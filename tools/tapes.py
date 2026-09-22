"""ImmortalFruitFliesTape tape encode/decode - vendored verbatim from bio-intelligent/brain/export.py."""
from pathlib import Path

import numpy as np

def write_tapes(path: Path, pi: np.ndarray, qi: np.ndarray, w: np.ndarray, n_slots: int, max_body: int = 65_535) -> list[Path]:
    """ImmortalFruitFliesTape tape payloads, byte-identical layout to the deployed ones."""
    assert pi.size == 0 or np.all(np.diff(pi) >= 0), "CSR-sorted by source required"
    # split neuron range into tapes; each tape body must fit the uint16 offsets
    worst_per_neuron = max(1, int(np.bincount(pi, minlength=n_slots).max())) if pi.size else 1
    # offsets are absolute file positions: 2*(n+1) header + 5*records body must fit uint16
    per_tape_cap = (max_body - 2) // (5 * worst_per_neuron + 2)
    per_tape = min(5_831, per_tape_cap)
    files: list[Path] = []
    path.mkdir(parents=True, exist_ok=True)
    base = 0
    bi = 0
    while base < n_slots:
        n = min(per_tape, n_slots - base)
        lo, hi = np.searchsorted(pi, base), np.searchsorted(pi, base + n)
        offs = [2 * (n + 1)]
        for j in range(n):
            offs.append(offs[-1] + 5 * int(np.searchsorted(pi, base + j + 1) - np.searchsorted(pi, base + j)))
        assert offs[-1] <= 65_535, f"bank {bi} body exceeds uint16 offsets ({offs[-1]})"
        buf = bytearray()
        # the first uint16 of the file IS offs[0] (= 2*(n+1)): it doubles as the
        # neuron-count header and the first offset, exactly like the deployed banks
        for j in range(n + 1):
            buf += int(offs[j]).to_bytes(2, "big")
        for k in range(lo, hi):
            buf += int(qi[k]).to_bytes(3, "big")
            buf += (int(w[k]) & 0xFFFF).to_bytes(2, "big")
        f = path / f"tape_{bi:05d}.bin"
        f.write_bytes(bytes(buf))
        files.append(f)
        base += n
        bi += 1
    return files

def decode_tapes(files: list[Path]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Independent re-parse of the written banks (same code path as the audit)."""
    src, tgt, w = [], [], []
    base = 0
    for f in files:
        raw = f.read_bytes()
        n = int.from_bytes(raw[0:2], "big") // 2 - 1
        offs = [int.from_bytes(raw[2 * j : 2 * j + 2], "big") for j in range(n + 1)]
        for j in range(n):
            a, b = offs[j], offs[j + 1]
            for p in range(a, b, 5):
                src.append(base + j)
                tgt.append((raw[p] << 16) | (raw[p + 1] << 8) | raw[p + 2])
                wt = (raw[p + 3] << 8) | raw[p + 4]
                w.append(wt - 65536 if wt >= 32768 else wt)
        base += n
    return np.asarray(src, dtype=np.int64), np.asarray(tgt, dtype=np.int64), np.asarray(w, dtype=np.int64)

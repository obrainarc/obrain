#!/usr/bin/env python3
"""The chain-exact twin of a Flybook brain: `Connectome.think`, in Python, to the bit.

A descendant's brain is a `Connectome` clone reading the species `Holotype` (the Ancestor's
85 tapes, the decay and gate tables, the dimensions) with a genome of 64 genes, one per
segment of the scan. This module replays it: the sensory injection into cells 0-255, the
gated scan of K = 3 segments chosen by the attention bucket, the lazy decay of each 16-cell
word by the Q16 table entry for the ticks since it was last visited (a product chain past
64), threshold and reset-on-fire, sequential clamped delivery of every tape record of a fired
cell under the segment's gene (`mutatedWeight`: keccak(gene, target, "m") mod 1000 < 50 bends
the weight by keccak(gene, target, "d") clamped to +/-25 %), and the `rootDirty` fold over
every storage word a thought writes, at the clone's slot numbers (potentials from slot 11,
last-active ticks from slot 11,011). `Clone.think(inputAgg)` returns exactly what the brain's
`Thought` log carries: synapses, spiked, the fired ids and the root.

    species = Species("research/<study>/data/holotype.bin", "tapes")
    brain = Clone(species, genome_words)          # the 8 words of the Eclosed log
    synapses, spiked, fired, root = brain.think(input_agg)

Needs numpy and pycryptodome. `python3 tools/vclone.py` replays founder 2's first thought and
checks its root against the chain's.
"""
import os
import sys
from pathlib import Path

import numpy as np
from Crypto.Hash import keccak

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tapes import decode_tapes  # noqa: E402

QMAX = 32_000
SPIKE_CAP = 2048
MU_RATE, MU_SWING, BPS = 50, 2500, 10_000
SLOT_POTENTIALS, SLOT_LAST = 11, 11_011
FOLD_SEED = int.from_bytes(keccak.new(digest_bits=256, data=b"Flybook Connectome v1").digest(), "big")
CONFIG_HASH = "baf5133151386f4d2fbad817c793b1fa39942b9876910132011b2be2b6a1bb91"


def k(data: bytes) -> bytes:
    return keccak.new(digest_bits=256, data=data).digest()


def fold(r: int, slot: int, value: int) -> int:
    return int.from_bytes(k(r.to_bytes(32, "big") + slot.to_bytes(32, "big") + value.to_bytes(32, "big")), "big")


class Species:
    """the Holotype blob (HolotypeCodec layout) and the 85 tapes as one CSR edge list"""

    def __init__(self, blob_path: str, tapes_dir: str):
        b = Path(blob_path).read_bytes()
        assert k(b).hex() == CONFIG_HASH, "this is not the pinned species"
        g = lambda o, w: int.from_bytes(b[o:o + w], "big")  # noqa: E731
        self.NN, self.NW, self.nExp, self.K, self.wpe, self.sensory, self.nTapes = (g(4 * i, 4) for i in range(7))
        th = g(28, 4)
        self.TH = th - (1 << 32) if th >= 1 << 31 else th
        self.lut = [g(32 + 4 * i, 4) for i in range(64)]
        self.gate = [g(288 + 8 * i, 8) for i in range(256)]
        self.tsn = [g(2336 + 4 * i, 4) for i in range(self.nTapes + 1)]
        src, self.tgt, self.w = decode_tapes(sorted(Path(tapes_dir).glob("tape_*.bin")))
        assert self.tsn[-1] == self.NN and len(src) == 325_292
        ids = np.arange(self.NN)
        self.starts, self.ends = np.searchsorted(src, ids), np.searchsorted(src, ids, side="right")
        self._mult = {}

    def mult(self, dt: int) -> int:
        """the Q16 decay multiplier for dt ticks of silence: one table entry to 64, a product chain beyond"""
        m = self._mult.get(dt)
        if m is None:
            if dt <= 64:
                m = self.lut[dt - 1]
            else:
                m, rem = self.lut[0], dt - 1
                while rem > 0:
                    step = min(rem, 64)
                    m = (m * self.lut[step - 1] + 32768) >> 16
                    rem -= step
            self._mult[dt] = m
        return m


def mutated(gene: int, tgt: int, wt: int) -> int:
    pre = gene.to_bytes(32, "big") + tgt.to_bytes(32, "big")
    if int.from_bytes(k(pre + b"m"), "big") % 1000 >= MU_RATE:
        return wt
    d = int.from_bytes(k(pre + b"d")[-2:], "big")
    d = d - 65536 if d >= 32768 else d
    lim = abs(wt) * MU_SWING // BPS
    return wt + max(-lim, min(lim, d))


class Clone:
    def __init__(self, species: Species, genome: list):
        self.s = species
        self.genes = [(genome[i >> 3] >> ((i & 7) * 32)) & 0xFFFFFFFF for i in range(64)]
        self.lanes = np.zeros(species.NW * 16, dtype=np.int64)  # int16 potentials, 16 per word
        self.last = np.zeros(species.NW, dtype=np.int64)  # the tick each word was last decayed
        self.tick = 0
        self.root = FOLD_SEED
        self._mcache = {}

    def packed(self, w: int) -> int:
        v = 0
        for L, x in enumerate(self.lanes[16 * w:16 * w + 16]):
            v |= (int(x) & 0xFFFF) << (16 * L)
        return v

    def packed_last(self, slot: int) -> int:
        v = 0
        for i in range(8):
            w = 8 * slot + i
            if w < self.s.NW:
                v |= int(self.last[w]) << (32 * i)
        return v

    def weight(self, gene: int, tgt: int, wt: int) -> int:
        key = (gene, tgt, wt)
        m = self._mcache.get(key)
        if m is None:
            m = self._mcache[key] = mutated(gene, tgt, wt)
        return m

    def think(self, input_agg: int):
        s, lanes = self.s, self.lanes
        self.tick = t = self.tick + 1
        r = self.root
        dirty = set()
        # ---- sensory injection: cell n reads the 8-bit window at bit 3 (n mod 60), times 64, clamped above
        for w in range((s.sensory + 15) >> 4):
            for L in range(16):
                n = 16 * w + L
                if n < s.sensory:
                    c = int(lanes[n]) + ((input_agg >> (3 * (n % 60))) & 0xFF) * 64
                    lanes[n] = min(c, QMAX)
            dirty.add(w)
            r = fold(r, SLOT_POTENTIALS + w, self.packed(w))
        # ---- the gated scan
        gate = s.gate[input_agg % s.nExp]
        synapses = spiked = 0
        fired = []
        for i in range(s.K):
            e = (gate >> (8 * i)) & 0xFF
            gene = self.genes[e]
            base, end = e * s.wpe, min((e + 1) * s.wpe, s.NW)
            cur = None
            for w in range(base, end):
                slot = w >> 3
                if slot != cur:
                    if cur is not None:
                        r = fold(r, SLOT_LAST + cur, self.packed_last(cur))
                    cur = slot
                dt = t - int(self.last[w])
                if dt:
                    m = s.mult(dt)
                    seg = lanes[16 * w:16 * w + 16]
                    seg[:] = (seg * m + 32768) >> 16
                    dirty.add(w)
                    snapshot = seg.copy()  # the threshold reads the word as decayed, not as delivered to
                    for L in range(16):
                        if snapshot[L] >= s.TH:
                            n = 16 * w + L
                            spiked += 1
                            if len(fired) < SPIKE_CAP:
                                fired.append(n)
                            for p in range(int(s.starts[n]), int(s.ends[n])):
                                tgt, wt = int(s.tgt[p]), int(s.w[p])
                                if wt == 0:
                                    continue
                                if gene:
                                    wt = self.weight(gene, tgt, wt)
                                if tgt < s.NN:
                                    synapses += 1
                                    lanes[tgt] = max(-QMAX, min(QMAX, int(lanes[tgt]) + wt))
                                    dirty.add(tgt >> 4)
                            lanes[n] = 0
                self.last[w] = t
            if cur is not None:
                r = fold(r, SLOT_LAST + cur, self.packed_last(cur))
        # ---- every dirty word, in order, folded with its final value
        for w in sorted(dirty):
            if w < s.NW:
                r = fold(r, SLOT_POTENTIALS + w, self.packed(w))
        self.root = r
        return synapses, spiked, fired, r


if __name__ == "__main__":  # founder 2's first thought: input 0x7f803c, root 0xc91e...760d (CS-002, CS-003)
    import csv
    here = Path(__file__).resolve().parent.parent
    species = Species(here / "research/2026-10-07-flybook-clone-twin/data/holotype.bin", here / "tapes")
    founders = {int(r["fly"]): r for r in csv.DictReader(open(here / "research/2026-09-27-flybook-generation-zero/data/founder_census.csv"))}
    genome = [int(x, 16) for x in founders[2]["genome"].split()]
    words = [sum(genome[8 * i + j] << (32 * j) for j in range(8)) for i in range(8)]
    thoughts = [r for r in csv.DictReader(open(here / "research/2026-09-27-flybook-generation-zero/data/thought_census.csv")) if r["fly"] == "2"]
    brain = Clone(species, words)
    for r in sorted(thoughts, key=lambda r: int(r["tick"])):
        syn, sp, fired, root = brain.think(int(r["input_agg"], 16))
        ok = f"{root:064x}" == r["root"][2:] and " ".join(map(str, fired)) == r["fired"] and syn == int(r["synapses"])
        print(f"fly 2 tick {r['tick']}: synapses {syn} spiked {sp} root 0x{root:064x} {'== chain' if ok else '!= chain ' + r['root']}")
        assert ok
    print("twin ok")

"""VBrain: vectorized chain-exact LIF twin of the on-chain kernel (v3.1).

Vendored verbatim (AST-extracted) from the superseded brain/bench_vs_original.py,
removed together with the old source-pruned brain. Validated against ChainBrain
in that file's own harness; see flybrainv2/bench_chain.py header for usage.

Semantics: squared decay LUT, sensory write-through into slots 0..255 with
shifts (n%60)*3, 3 gated segments per tick (0, b+21, b+42), per-record clamp,
reset-on-fire, word-at-a-time decay, strict sequential per-lane delivery.
"""
import numpy as np

SCALE = 64
THRESH = 200 * SCALE
LEAK = 0.98
QMAX = 32000
N_EXPERTS = 64
K = 3
SENSORY = 256
WORDS = 10568
N0 = 169078
N = 169088
WPE = (WORDS + N_EXPERTS - 1) // N_EXPERTS
SPIKE_CAP = 2048
GATE_OFFSETS = (21, 42)
HUNT_PATS = [0xFFFFFFFF, 0x00000000, 0xFFFFFFF0, 0x0F0F0F0F, 0xAAAAAAAA,
             0x55555555, 0x80000001, 0x7FFFFFFE]

class VBrain:
    """Vectorized chain-exact LIF. Same semantics as ChainBrain/ImmortalFruitFlies kernel v3.1
    (squared decay LUT, sensory (n%60)*3, gates 0/b+21/b+42, per-record clamp,
    reset-on-fire, word-at-a-time decay) but handles full-width uint256 inputs,
    which the on-chain think(uint256) accepts and the exported calibration
    never exercised."""

    def __init__(self, src, tgt, w, float_mode=False):
        self.src = np.asarray(src, dtype=np.int64)
        self.tgt = np.asarray(tgt, dtype=np.int64)
        self.w = np.asarray(w, dtype=np.int64 if not float_mode else np.float64)
        assert np.all(np.diff(self.src) >= 0), 'src must be CSR-sorted'
        self.starts = np.searchsorted(self.src, np.arange(N0))
        self.ends = np.searchsorted(self.src, np.arange(N0), side='right')
        lut = [64225]
        m = 64225
        for _ in range(63):
            m = (m * m) // 65536
            lut.append(m)
        self.lut = np.array(lut, dtype=np.int64)
        self.mult_cache = {}
        self.sh = ((np.arange(SENSORY) % 60) * 3)
        self.float_mode = float_mode
        self.lanes = np.zeros(N, dtype=np.float64 if float_mode else np.int64)
        self.last = np.zeros(WORDS, dtype=np.int64)
        self.tick = 0
        # segment word masks
        self.we = np.minimum(np.arange(WORDS) // WPE, N_EXPERTS - 1)

    def _mult(self, dt):
        """Chain LUT multiplier in Q16 (exact same composition as the kernel)."""
        m = self.mult_cache.get(dt)
        if m is not None:
            return m
        if dt <= 64:
            m = int(self.lut[dt - 1])
        else:
            m = int(self.lut[0])
            rem = dt - 1
            while rem > 0:
                step = rem if rem < 64 else 64
                m = (m * int(self.lut[step - 1]) + 32768) >> 16
                rem -= step
        self.mult_cache[dt] = m
        return m

    def think(self, inp):
        """One tick, byte-exact with ChainBrain: word-at-a-time decay, then a
        strict sequential per-lane scan (deliveries from earlier lanes of the
        same pass are visible to later lanes)."""
        t = self.tick + 1
        self.tick = t
        lanes = self.lanes
        # sensory write-through
        addv = np.fromiter((((int(inp) >> int(s)) & 0xFF) for s in self.sh), dtype=np.int64,
                           count=SENSORY) * SCALE
        if self.float_mode:
            lanes[:SENSORY] = lanes[:SENSORY] + addv
        else:
            lanes[:SENSORY] = np.minimum(lanes[:SENSORY] + addv, QMAX)
        b = int(inp) % N_EXPERTS
        gate = (0, (b + GATE_OFFSETS[0]) % N_EXPERTS, (b + GATE_OFFSETS[1]) % N_EXPERTS)
        ops = 0
        spiked = 0
        fired_ids = []
        starts, ends, tgt, wt_all = self.starts, self.ends, self.tgt, self.w
        is_float = self.float_mode
        for e in gate:
            ws = np.nonzero(self.we == e)[0]
            if len(ws) == 0:
                continue
            for wi in range(int(ws[0]), int(ws[-1]) + 1):
                dt = t - int(self.last[wi])
                self.last[wi] = t
                n0 = wi * 16
                if dt:
                    m = self._mult(dt)
                    if m != 65536:
                        seg = lanes[n0:n0 + 16]
                        if is_float:
                            lanes[n0:n0 + 16] = seg * (m / 65536.0)
                        else:
                            nz = seg != 0
                            seg[nz] = (seg[nz] * m + 32768) >> 16
                for L in range(16):
                    n = n0 + L
                    if lanes[n] >= THRESH:
                        if spiked < SPIKE_CAP:
                            spiked += 1
                            fired_ids.append(n)
                            if n < N0:
                                a, z = int(starts[n]), int(ends[n])
                                if z > a:
                                    tg = tgt[a:z]
                                    wv = wt_all[a:z]
                                    keep = (wv != 0) & (tg < N)
                                    if not keep.all():
                                        tg, wv = tg[keep], wv[keep]
                                    if len(tg):
                                        ops += len(tg)
                                        if is_float:
                                            lanes[tg] += wv
                                        else:
                                            vals = lanes[tg] + wv
                                            np.clip(vals, -QMAX, QMAX, out=vals)
                                            lanes[tg] = vals
                        lanes[n] = 0
        return ops, spiked, np.asarray(fired_ids, dtype=np.int64)

    def state_root(self):
        from Crypto.Hash import keccak as _k

        def kk(b):
            h = _k.new(digest_bits=256, data=b)
            return int.from_bytes(h.digest(), 'big')

        h = kk(self.tick.to_bytes(32, 'big'))
        buf = bytearray(64)
        lanes = self.lanes
        for s in range(WORDS):
            word = 0
            for L in range(16):
                word |= (int(lanes[s * 16 + L]) & 0xFFFF) << (16 * L)
            buf[0:32] = h.to_bytes(32, 'big')
            buf[32:64] = word.to_bytes(32, 'big')
            h = kk(bytes(buf))
        return h

def prng_inputs(seed, n, width=64):
    x, out = seed, []
    mask = (1 << width) - 1
    for _ in range(n):
        x = (x * 6364136223846793005 + 1442695040888963407) % (1 << 64)
        out.append(x & mask)
    return out

def hunt_inputs(n, salt):
    x, out = salt, []
    for _ in range(n):
        x = (x * 1103515245 + 12345) % (1 << 31)
        out.append(HUNT_PATS[x % len(HUNT_PATS)] ^ (x & 0xFF))
    return out

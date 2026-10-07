#!/usr/bin/env python3
"""Register, before the fact, what every Flybook brain will do at its next thought.

At one block the twin (tools/vclone.py) is brought to each brain's state by replaying its
recorded input words (tools/verify_clones.py proves that state is the chain's). From that state
it thinks, hypothetically, each of the stimuli a keeper can give in one transaction, the input
word built as the hub builds it (attention = keccak(afferent, tick) mod 64, sensillum s at bit
6 + 9s): the 19 sensilla at tiers 0, 1 and 2, and the pheromone (sensillum 0 at tier 1, a
courtship). For each it records the attention bucket, the segments scanned, the spike count,
the courtship-region count (regions[0], the ruling's number), the cells fired outside the input
layer and the root the brain would commit. It also lists the cells outside the input layer the
brain holds at or above threshold, waiting for their segment.

A row is falsified by one transaction: the brain's next Thought log, if its input is one of the
57 stimuli, must carry that spike count and that root. Rows are only valid for the brain's
*next* thought; any thought spends them, and the file says at which tick each brain stood.

    python3 tools/predict_next.py --at BLOCK [--rpc URL] [--out DIR] [--check DIR] [--fresh]

Writes predictions.csv and waiting.csv; with --check regenerates them at the registered block
and diffs. Needs numpy and pycryptodome; the JSON-RPC client is tools/chain.py.
"""
import argparse
import copy
import csv
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vclone import Clone, Species, k  # noqa: E402
from verify_flybook import DEPLOY_BLOCK, HUB, Rpc  # noqa: E402
from verify_generation1 import T, words  # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHARGE = [31, 127, 255]
FIELDS = ["fly", "generation", "tick_before", "root_before", "sensillum", "tier", "input_agg", "attention", "segments", "spiked", "courtship_region", "out_of_layer", "root"]
WAITING = ["fly", "tick_before", "cell", "segment", "buckets", "potential", "fires_if_visited_within"]


def input_agg(afferent: int, tick: int) -> int:
    agg = int.from_bytes(k(afferent.to_bytes(32, "big") + tick.to_bytes(4, "big")), "big") % 64
    for s in range(20):
        agg |= ((afferent >> (8 * s)) & 0xFF) << (6 + 9 * s)
    return agg


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rpc", default="https://rpc.mainnet.arc.io")
    ap.add_argument("--at", type=int, help="the block the predictions are registered at (default: head)")
    ap.add_argument("--out")
    ap.add_argument("--check")
    ap.add_argument("--fresh", action="store_true")
    ap.add_argument("--blob", default=os.path.join(HERE, "research/2026-10-07-flybook-clone-twin/data/holotype.bin"))
    a = ap.parse_args()
    rpc = Rpc(a.rpc, cache=not a.fresh)
    at = a.at or rpc.head
    if a.check:
        with open(os.path.join(a.check, "REGISTERED_BLOCK")) as fh:
            at = int(fh.read().split()[0])
    species = Species(a.blob, os.path.join(HERE, "tapes"))
    wpe, TH = species.wpe, species.TH
    visitors = defaultdict(list)
    for b in range(64):
        g = species.gate[b]
        for i in range(1, 3):
            visitors[(g >> (8 * i)) & 255].append(b)

    hub = rpc.logs([[T[n] for n in ("Eclosed", "Courted", "Accepted", "Rejected", "Laid", "PupaHatched", "Thought", "Sensed")]], DEPLOY_BLOCK, at, HUB)
    genome, gen, inputs = {}, {}, defaultdict(dict)
    for x in hub:
        if x["topics"][0] == T["Eclosed"]:
            w = words(x["data"])
            genome[int(x["topics"][1], 16)], gen[int(x["topics"][1], 16)] = w[4:12], w[1]
        elif x["topics"][0] == T["Thought"]:
            w = words(x["data"])
            inputs[int(x["topics"][1], 16)][w[0]] = w[1]

    rows, waiting = [], []
    for f in sorted(genome):
        base = Clone(species, genome[f])
        for t in sorted(inputs[f]):
            base.think(inputs[f][t])
        root0 = f"0x{base.root:064x}"
        for c in (int(x) for x in (base.lanes[256:] >= TH).nonzero()[0] + 256):
            seg = (c >> 4) // wpe
            v = int(base.lanes[c])
            within = max([d for d in range(1, 65) if (v * species.mult(d) + 32768) >> 16 >= TH] or [0])
            waiting.append({"fly": f, "tick_before": base.tick, "cell": c, "segment": seg, "buckets": " ".join(map(str, visitors[seg])) if seg else "every", "potential": v, "fires_if_visited_within": within})
        stimuli = [(s, tier) for s in range(1, 20) for tier in range(3)] + ([(0, 1)] if gen[f] == 0 else [])
        for s, tier in stimuli:
            b = copy.deepcopy(base)
            agg = input_agg(CHARGE[tier] << (8 * s), b.tick)
            syn, sp, fired, root = b.think(agg)
            gate = species.gate[agg % species.nExp]
            rows.append({"fly": f, "generation": gen[f], "tick_before": base.tick, "root_before": root0, "sensillum": s, "tier": tier, "input_agg": hex(agg),
                         "attention": agg % 64, "segments": " ".join(str((gate >> (8 * i)) & 255) for i in range(3)), "spiked": sp,
                         "courtship_region": sum(1 for c in fired if ((c >> 4) // wpe) >> 3 == 0), "out_of_layer": " ".join(str(c) for c in fired if c >= species.sensory), "root": f"0x{root:064x}"})

    out = {"predictions.csv": (FIELDS, rows), "waiting.csv": (WAITING, waiting)}
    bad = []
    if a.check:
        for name, (fields, ours) in out.items():
            with open(os.path.join(a.check, name)) as fh:
                shipped = list(csv.DictReader(fh))
            ours_s = [{key: str(r[key]) for key in fields} for r in ours]
            diff = [i for i, (s, o) in enumerate(zip(shipped, ours_s)) if s != o] + (["row count"] if len(shipped) != len(ours_s) else [])
            print(f"{name}: {len(shipped)} rows, {'identical' if not diff else 'DIFFERS at ' + ', '.join(map(str, diff[:10]))}")
            bad += diff
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        for name, (fields, rs) in out.items():
            with open(os.path.join(a.out, name), "w", newline="") as fh:
                w = csv.DictWriter(fh, fields, lineterminator="\n")
                w.writeheader()
                w.writerows(rs)
        with open(os.path.join(a.out, "REGISTERED_BLOCK"), "w") as fh:
            fh.write(f"{at}\n")
        print("wrote", a.out, "registered at block", at)
    print(f"{len(genome)} brains at block {at}: {len(rows)} predicted next thoughts ({sum(1 for r in rows if r['out_of_layer'])} fire outside the input layer), "
          f"{len(waiting)} cells waiting above threshold in {len({w['fly'] for w in waiting})} brains; head {rpc.head}; {len(bad)} mismatches")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

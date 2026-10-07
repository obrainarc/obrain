#!/usr/bin/env python3
"""Replay every Flybook brain's whole life with the twin and diff it against the chain.

For each fly, from consensus alone: its genome (the `Eclosed` log), the input word of each of
its thoughts (the hub's `Thought` logs, in tick order) and what its own brain logged for each
(`Connectome.Thought`: synapses, spiked, the fired ids, the root). The twin (`tools/vclone.py`)
starts every brain from the empty fold and thinks the same words; a thought is reproduced when
synapses, spiked, the fired list and the root all agree. The root is a keccak fold over every
storage word the thought wrote, so agreement on it is agreement on the whole membrane field.

Writes replay.csv (one row per thought: fly, tick, block, input word, attention bucket, the
segments scanned, synapses, spiked, fired, root, the cells fired outside the input layer, and
whether the chain agrees) with --out DIR; with --check DIR replays to the census' last block
and diffs. Exits nonzero on any thought the twin does not reproduce.

    python3 tools/verify_clones.py [--rpc URL] [--to BLOCK] [--out DIR] [--check DIR] [--fresh]

Needs numpy and pycryptodome; the JSON-RPC client is tools/chain.py.
"""
import argparse
import csv
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vclone import Clone, Species  # noqa: E402
from verify_flybook import DEPLOY_BLOCK, HUB, THOUGHT, Rpc  # noqa: E402
from verify_generation1 import T, words  # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIELDS = ["fly", "tick", "block", "input_agg", "attention", "segments", "synapses", "spiked", "fired", "root", "out_of_layer", "reproduced"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rpc", default="https://rpc.mainnet.arc.io")
    ap.add_argument("--to", type=int)
    ap.add_argument("--out")
    ap.add_argument("--check")
    ap.add_argument("--fresh", action="store_true", help="ignore the local cache; read everything from the chain")
    ap.add_argument("--blob", default=os.path.join(HERE, "research/2026-10-07-flybook-clone-twin/data/holotype.bin"))
    a = ap.parse_args()
    rpc = Rpc(a.rpc, cache=not a.fresh)
    to = a.to or rpc.head
    if a.check:
        with open(os.path.join(a.check, "replay.csv")) as fh:
            to = max(int(r["block"]) for r in csv.DictReader(fh))
    species = Species(a.blob, os.path.join(HERE, "tapes"))

    hub = rpc.logs([[T[n] for n in ("Eclosed", "Courted", "Accepted", "Rejected", "Laid", "PupaHatched", "Thought", "Sensed")]], DEPLOY_BLOCK, to, HUB)
    genome, brain, inputs = {}, {}, defaultdict(dict)
    for x in hub:
        if x["topics"][0] == T["Eclosed"]:
            w = words(x["data"])
            genome[int(x["topics"][1], 16)], brain[int(x["topics"][1], 16)] = w[4:12], f"0x{w[0]:040x}"
        elif x["topics"][0] == T["Thought"]:
            w = words(x["data"])
            inputs[int(x["topics"][1], 16)][w[0]] = (w[1], int(x["blockNumber"], 16))
    flies = sorted(genome)
    soma = defaultdict(dict)
    for x in rpc.logs([THOUGHT], DEPLOY_BLOCK, to, [brain[f] for f in flies]):
        w = words(x["data"])
        raw = bytes.fromhex(x["data"][2:])[w[5] + 32:w[5] + 32 + w[6]]
        soma[x["address"].lower()][int(x["topics"][1], 16)] = (w[1], w[2], [int.from_bytes(raw[i:i + 3], "big") for i in range(0, len(raw), 3)], w[4])

    rows, bad = [], []
    for f in flies:
        twin = Clone(species, genome[f])
        mine = soma[brain[f]]
        for tick in sorted(inputs[f]):
            agg, block = inputs[f][tick]
            syn, sp, fired, root = twin.think(agg)
            chain = mine.get(tick)
            ok = chain is not None and (syn, sp, fired, root) == chain[:3] + (chain[3],)
            if not ok:
                bad.append(f"fly {f} tick {tick}: twin ({syn}, {sp}, {len(fired)} fired, 0x{root:064x}) vs chain {chain if chain is None else (chain[0], chain[1], len(chain[2]), hex(chain[3]))}")
            gate = species.gate[agg % species.nExp]
            rows.append({"fly": f, "tick": tick, "block": block, "input_agg": hex(agg), "attention": agg % 64,
                         "segments": " ".join(str((gate >> (8 * i)) & 0xFF) for i in range(species.K)), "synapses": syn, "spiked": sp,
                         "fired": " ".join(map(str, fired)), "root": f"0x{root:064x}", "out_of_layer": " ".join(str(c) for c in fired if c >= species.sensory),
                         "reproduced": int(ok)})
        if len(mine) != len(inputs[f]):
            bad.append(f"fly {f}: {len(mine)} brain Thoughts, {len(inputs[f])} hub Thoughts")

    if a.check:
        with open(os.path.join(a.check, "replay.csv")) as fh:
            shipped = list(csv.DictReader(fh))
        ours = [{k: str(v) for k, v in r.items()} for r in rows]
        diff = [i for i, (s, o) in enumerate(zip(shipped, ours)) if s != o] + (["row count"] if len(shipped) != len(ours) else [])
        print(f"replay.csv: {len(shipped)} rows, {'identical' if not diff else 'DIFFERS at ' + ', '.join(map(str, diff[:10]))}")
        bad += [f"replay.csv {d}" for d in diff]
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        with open(os.path.join(a.out, "replay.csv"), "w", newline="") as fh:
            w = csv.DictWriter(fh, FIELDS, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        print("wrote", os.path.join(a.out, "replay.csv"))
    for b in bad:
        print("MISMATCH", b)
    out = sum(1 for r in rows if r["out_of_layer"])
    print(f"{len(flies)} brains, {len(rows)} thoughts to block {to}: the twin reproduces synapses, spiked, fired and root for "
          f"{sum(r['reproduced'] for r in rows)}/{len(rows)}; {out} thoughts fired outside the input layer; {len(bad)} mismatches")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

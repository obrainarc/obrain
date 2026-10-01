#!/usr/bin/env python3
"""Verify the first Flybook offspring generation (G1) and the courtships that made it.

A child reaches the hub by one of two routes, and for each this re-derives from consensus
alone that its genome is `Meiosis.cross(mother, father, seed)` of its parents' Eclosed genomes:

  egg   Accepted(target, suitor, eggId, courter, seed, fired, selectivity) fixes the seed;
        Laid(eggId, flyId) names the child; child = cross(G[target], G[suitor], seed)
  pupa  PupaSettled(pupaId, seed) on Pupae fixes the seed; PupaHatched(pupaId, flyId, tier,
        pick, ...) names the child and the candidate; child = cross(G[m], G[f],
        keccak(abi.encode(seed, pick)))

cross: gene s from the mother when bit s of the seed is set, else from the father; then with
probability 20/1000 (keccak(seed, uint8(s), "mu") mod 1000 < 20) replaced by the low 32 bits
of keccak(seed, uint8(s), "new"). Every courtship ruling is checked against `fired >=
selectivity` (a ruling above threshold that was rejected must be a cooldown).

Writes pedigree.csv, courtship.csv and thought_census.csv (hub Thought joined by transaction
with its Sensed logs, or marked `pheromone` when the transaction is the Courted that wrote
sensillum 0) with --out DIR; with --check DIR re-derives to the census' last block
and diffs. Exits nonzero on any mismatch.

    python3 tools/verify_generation1.py [--rpc URL] [--to BLOCK] [--out DIR] [--check DIR]

Needs pycryptodome; shares verify_flybook.py's throttled JSON-RPC client.
"""
import argparse
import csv
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify_flybook import DEPLOY_BLOCK, HUB, Rpc, k  # noqa: E402

PUPAE = "0x83547b1d4b9ce8fc469bed87b22d525e5c64fb20"
CUT = 22_971_428  # CS-003 census close: the window opens at the next block


def topic(sig: str) -> str:
    return "0x" + k(sig.encode()).hex()


T = {n: topic(s) for n, s in {
    "Eclosed": "Eclosed(uint256,address,address,uint16,uint256,uint256,uint256[8],uint256,address)",
    "Courted": "Courted(uint256,uint256,address,uint256,uint256)",
    "Accepted": "Accepted(uint256,uint256,uint256,address,bytes32,uint256,uint256)",
    "Rejected": "Rejected(uint256,uint256,address,uint256,uint256)",
    "Laid": "Laid(uint256,uint256)",
    "PupaHatched": "PupaHatched(uint256,uint256,uint8,uint8,uint256,bool)",
    "Thought": "Thought(uint256,address,uint32,uint256,uint32,uint32,uint16[8],uint64)",
    "Sensed": "Sensed(uint256,address,uint8,uint8,uint256)",
    "PupaSettled": "PupaSettled(uint256,bytes32)",
}.items()}
NAME = {v: n for n, v in T.items()}

PEDIGREE = ["fly", "route", "egg_or_pupa", "block", "owner", "mother", "father", "seed", "pick",
            "maternal_loci", "mutated_loci", "genome"]
COURTSHIP = ["block", "tx", "target", "suitor", "courter", "outcome", "fired", "selectivity", "egg"]
THOUGHTS = ["fly", "tick", "block", "keeper", "senses", "fee_obrain", "input_agg", "synapses", "spiked", "regions", "death_at"]


def logs(rpc: Rpc, topics: list, frm: int, to: int, address=None) -> list:
    """one getLogs per request: a 20-chunk batch over the busiest days outruns the 60 s timeout"""
    f = dict({"topics": topics}, **({"address": address} if address else {}))
    return [x for a in range(frm, to + 1, 9_999)
            for x in rpc.batch([("eth_getLogs", [dict(f, fromBlock=hex(a), toBlock=hex(min(a + 9_998, to)))])])[0]]


def words(data: str) -> list:
    h = data[2:]
    return [int(h[i:i + 64], 16) for i in range(0, len(h), 64)]


def gene(g: list, s: int) -> int:
    return (g[s >> 3] >> ((s & 7) * 32)) & 0xFFFFFFFF


def mutated(seed: bytes, s: int) -> bool:
    return int.from_bytes(k(seed + bytes([s]) + b"mu"), "big") % 1000 < 20


def cross(mother: list, father: list, seed: bytes) -> list:
    bits = int.from_bytes(seed, "big")
    child = [0] * 8
    for s in range(64):
        v = gene(mother, s) if bits >> s & 1 else gene(father, s)
        if mutated(seed, s):
            v = int.from_bytes(k(seed + bytes([s]) + b"new")[-4:], "big")
        child[s >> 3] |= v << ((s & 7) * 32)
    return child


def hexgenome(g: list) -> str:
    return " ".join(f"{gene(g, s):08x}" for s in range(64))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rpc", default="https://rpc.mainnet.arc.io")
    ap.add_argument("--to", type=int)
    ap.add_argument("--out")
    ap.add_argument("--check")
    a = ap.parse_args()
    rpc = Rpc(a.rpc)
    head = int(rpc.batch([("eth_blockNumber", [])])[0], 16)
    to = a.to or head
    if a.check:
        with open(os.path.join(a.check, "pedigree.csv")) as fh:
            to = max(int(r["block"]) for r in csv.DictReader(fh))
        with open(os.path.join(a.check, "thought_census.csv")) as fh:
            to = max([to] + [int(r["block"]) for r in csv.DictReader(fh)])
        with open(os.path.join(a.check, "courtship.csv")) as fh:
            to = max([to] + [int(r["block"]) for r in csv.DictReader(fh)])

    hub = sorted(logs(rpc, [[T[n] for n in ("Eclosed", "Courted", "Accepted", "Rejected", "Laid", "PupaHatched", "Thought", "Sensed")]],
                               DEPLOY_BLOCK, to, HUB), key=lambda x: (int(x["blockNumber"], 16), int(x["logIndex"], 16)))
    settled = {int(x["topics"][1], 16): bytes.fromhex(x["data"][2:66]) for x in logs(rpc, [T["PupaSettled"]], DEPLOY_BLOCK, to, PUPAE)}
    by = defaultdict(list)
    for x in hub:
        by[NAME[x["topics"][0]]].append(x)

    G, gen, par, owner, born = {}, {}, {}, {}, {}
    for x in by["Eclosed"]:
        f, w = int(x["topics"][1], 16), words(x["data"])
        G[f], gen[f], par[f], owner[f], born[f] = w[4:12], w[1], (w[2], w[3]), "0x" + x["topics"][2][-40:], int(x["blockNumber"], 16)

    bad, eggs, courtship = [], {}, []
    for x in by["Accepted"] + by["Rejected"]:
        acc = NAME[x["topics"][0]] == "Accepted"
        t, s = int(x["topics"][1], 16), int(x["topics"][2], 16)
        w = words(x["data"])
        fired, sel = (w[2], w[3]) if acc else (w[1], w[2])
        egg = int(x["topics"][3], 16) if acc else ""
        if acc:
            eggs[egg] = (t, s, w[1].to_bytes(32, "big"))
            if fired < sel:
                bad.append(f"egg {egg}: accepted with fired {fired} < selectivity {sel}")
        courtship.append({"block": int(x["blockNumber"], 16), "tx": x["transactionHash"], "target": t, "suitor": s,
                          "courter": "0x" + x["data"][26:66],
                          "outcome": "accepted" if acc else "rejected", "fired": fired, "selectivity": sel, "egg": egg})
    courtship.sort(key=lambda r: (r["block"], r["outcome"]))
    cooldown = sum(r["outcome"] == "rejected" and r["fired"] >= r["selectivity"] for r in courtship)

    rows = []
    for x in by["Laid"]:
        egg, f = int(x["topics"][1], 16), int(x["topics"][2], 16)
        m, fa, seed = eggs[egg]
        rows.append((f, "egg", egg, m, fa, seed, ""))
    for x in by["PupaHatched"]:
        pupa, f = int(x["topics"][1], 16), int(x["topics"][2], 16)
        pick = words(x["data"])[1]
        m, fa = par[f]
        rows.append((f, "pupa", pupa, m, fa, k(settled[pupa] + pick.to_bytes(32, "big")), pick))
    pedigree = []
    for f, route, src, m, fa, seed, pick in sorted(rows):
        if par[f] != (m, fa) or gen[f] != 1:
            bad.append(f"fly {f}: Eclosed parents {par[f]} gen {gen[f]}, {route} {src} says ({m}, {fa})")
        if cross(G[m], G[fa], seed) != G[f]:
            bad.append(f"fly {f}: genome is not Meiosis.cross of {m} x {fa} under its {route} seed")
        bits = int.from_bytes(seed, "big")
        mu = [s for s in range(64) if mutated(seed, s)]
        pedigree.append({"fly": f, "route": route, "egg_or_pupa": src, "block": born[f], "owner": owner[f], "mother": m,
                         "father": fa, "seed": "0x" + seed.hex(), "pick": pick,
                         "maternal_loci": sum(bits >> s & 1 for s in range(64) if s not in mu),
                         "mutated_loci": " ".join(map(str, mu)), "genome": hexgenome(G[f])})
    orphans = [f for f in G if gen[f] and f not in {r["fly"] for r in pedigree}]
    bad += [f"fly {f}: generation {gen[f]} with no egg or pupa" for f in orphans]

    sensed = defaultdict(list)
    for x in by["Sensed"]:
        sensed[(x["transactionHash"], int(x["topics"][1], 16))].append(x)
    courted = {(x["transactionHash"], int(x["topics"][1], 16)) for x in by["Courted"]}  # the target thinks on sensillum 0
    thoughts = []
    for x in by["Thought"]:
        if int(x["blockNumber"], 16) <= CUT:
            continue
        f, w = int(x["topics"][1], 16), words(x["data"])
        ss = sensed.pop((x["transactionHash"], f), [])
        pheromone = not ss and (x["transactionHash"], f) in courted
        if not ss and not pheromone:
            bad.append(f"fly {f}: Thought in {x['transactionHash']} has neither Sensed nor Courted")
        thoughts.append({"fly": f, "tick": w[0], "block": int(x["blockNumber"], 16), "keeper": "0x" + x["topics"][2][-40:],
                         "senses": "pheromone" if pheromone else " ".join(f"{words(s['data'])[0]}:{words(s['data'])[1]}" for s in ss),
                         "fee_obrain": sum(words(s["data"])[2] for s in ss) // 10**18, "input_agg": hex(w[1]),
                         "synapses": w[2], "spiked": w[3], "regions": " ".join(map(str, w[4:12])), "death_at": w[12]})

    out = {"pedigree.csv": (PEDIGREE, pedigree), "courtship.csv": (COURTSHIP, courtship), "thought_census.csv": (THOUGHTS, thoughts)}
    if a.check:
        for name, (fields, ours) in out.items():
            with open(os.path.join(a.check, name)) as fh:
                shipped = list(csv.DictReader(fh))
            ours_s = [{f: str(r[f]) for f in fields} for r in ours]
            diff = [i for i, (s, o) in enumerate(zip(shipped, ours_s)) if s != o] + (["row count"] if len(shipped) != len(ours_s) else [])
            print(f"{name}: {len(shipped)} rows, {'identical' if not diff else 'DIFFERS at ' + ', '.join(map(str, diff[:10]))}")
            bad += [f"{name} {d}" for d in diff]
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        for name, (fields, rows_) in out.items():
            with open(os.path.join(a.out, name), "w", newline="") as fh:
                w = csv.DictWriter(fh, fields, lineterminator="\n")
                w.writeheader()
                w.writerows(rows_)
            print("wrote", os.path.join(a.out, name))

    for b in bad:
        print("MISMATCH", b)
    route = Counter(r["route"] for r in pedigree)
    mus = sum(len(r["mutated_loci"].split()) for r in pedigree)
    print(f"G1 to block {to}: {len(pedigree)} children ({route['egg']} by egg, {route['pupa']} by pupa), "
          f"Meiosis.cross reproduces {len(pedigree) - sum('Meiosis' in b for b in bad)}/{len(pedigree)}; "
          f"{mus} point mutations over {64 * len(pedigree)} loci (expected {0.02 * 64 * len(pedigree):.1f})")
    print(f"courtship: {len(by['Courted'])} courted, {len(eggs)} accepted, {len(courtship) - len(eggs)} rejected "
          f"({cooldown} at or above threshold, i.e. cooldown), {len(eggs) - len(by['Laid'])} eggs unlaid")
    print(f"thoughts after block {CUT}: {len(thoughts)} by {len({t['keeper'] for t in thoughts})} keepers on "
          f"{len({t['fly'] for t in thoughts})} flies; head {head}; {len(bad)} mismatches")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

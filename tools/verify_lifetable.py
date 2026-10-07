#!/usr/bin/env python3
"""Verify the life table of the Flybook population: every fly's clock, re-derived from its log.

A fly's stored record (`flyOf`: bornAt, deathAt, lastThoughtAt, lastBredAt, thoughts) is a fold
over its own events, and this replays that fold from consensus alone, at one pinned block:

  Eclosed         bornAt = the block's timestamp; deathAt = bornAt + baseLifespan (30 d) for a
                  founder, bornAt + broodLifespan (90 d) for a brood; lastThoughtAt = bornAt
  Thought         before the P2 upgrade (block 23,384,885): deathAt = min(effective + 6 h,
                  bornAt + 90 d), where `effective` takes off every second asleep past
                  diapauseAfter (72 h, 7 d from the EcologyChanged of block 23,384,728);
                  from P2 on: a brood's deathAt takes the diapause charge and nothing else, a
                  founder's is pushed by `Tended`
  Tended(fly, at) a founder's window: deathAt = max(deathAt, now + tendedFor (30 d)); emitted by
                  a thought, a parented egg, an accepted courtship and a wake
  Woke(fly, s)    expected at exactly the thoughts whose gap since the last exceeds diapauseAfter,
                  with s = gap - diapauseAfter
  Accepted        lastBredAt of target and suitor = the block's timestamp
  Transfer        the owner now is the last transfer's `to`

and then checks the pinned `deathAtOf` (Society.deathMoment: a founder's stored deathAt; a brood's
stored deathAt, or the midpoint (deathAt + lastThoughtAt + diapauseAfter + 1) / 2 where the
diapause charge would catch up with it) and `lifeOf` (dead or dormant past deathMoment, in
diapause when a brood has not thought for diapauseAfter, else alive) against the same rules.

Writes life_table.csv (one row per fly) with --out DIR; with --check DIR re-derives at the
census' pinned block and diffs. Exits nonzero on any mismatch.

    python3 tools/verify_lifetable.py [--rpc URL] [--to BLOCK] [--out DIR] [--check DIR]

Needs pycryptodome; shares verify_flybook.py's throttled JSON-RPC client. State reads are
pinned at --to (or at head), so the RPC must serve that block's state.
"""
import argparse
import csv
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify_flybook import DEPLOY_BLOCK, HUB, Rpc, k  # noqa: E402
from verify_generation1 import logs, words  # noqa: E402

AMBER = "0x82e820049cd4d1110f1560f2eed623305c704dee"
P2_BLOCK = 23_384_885  # hub Upgraded + NurseryChanged: tended windows and fixed brood lives from here
DIAPAUSE = [(DEPLOY_BLOCK, 72 * 3600), (23_384_728, 7 * 86400)]  # EcologyChanged: diapauseAfter by block
BASE_LIFE, MAX_LIFE, PER_THOUGHT = 30 * 86400, 90 * 86400, 6 * 3600
BROOD_LIFE, TENDED_FOR = 90 * 86400, 30 * 86400
LIFE = ["alive", "diapause", "dead", "dormant"]


def topic(sig: str) -> str:
    return "0x" + k(sig.encode()).hex()


T = {n: topic(s) for n, s in {
    "Eclosed": "Eclosed(uint256,address,address,uint16,uint256,uint256,uint256[8],uint256,address)",
    "Thought": "Thought(uint256,address,uint32,uint256,uint32,uint32,uint16[8],uint64)",
    "Tended": "Tended(uint256,uint64)",
    "Woke": "Woke(uint256,uint64)",
    "Woken": "Woken(uint256,address,uint256,uint64)",
    "Entombed": "Entombed(uint256,uint64,uint32)",
    "Accepted": "Accepted(uint256,uint256,uint256,address,bytes32,uint256,uint256)",
    "Transfer": "Transfer(address,address,uint256)",
    "Advertised": "Advertised(uint256,address,uint256)",
    "Interred": "Interred(uint256,uint16,uint64,uint64,uint32)",
}.items()}
NAME = {v: n for n, v in T.items()}
SEL = {"flyOf": "0x7904a302", "deathAtOf": "0xa0bf1696", "lifeOf": "0x827fa400", "ownerOf": "0x6352211e",
       "statusOf": "0xad35efd4", "studFeeOf": "0xe02838ec", "advertisedBy": "0xf058f318"}
FIELDS = ["fly", "generation", "mother", "father", "born_block", "born_at", "keeper", "owner", "transfers", "thoughts",
          "last_thought_at", "last_bred_at", "children", "wokes", "stud_fee", "death_at", "death_moment", "life", "status"]


def diapause_at(block: int) -> int:
    return [d for b, d in DIAPAUSE if block >= b][-1]


def death_moment(f: dict, block: int) -> int:
    if f["generation"] == 0 or f["entombed"]:
        return f["deathAt"]
    sleep = f["lastThoughtAt"] + diapause_at(block)
    return f["deathAt"] if f["deathAt"] <= sleep else (f["deathAt"] + sleep + 1) // 2


def life_of(f: dict, now: int, block: int) -> int:
    if now >= death_moment(f, block):
        return 3 if f["generation"] == 0 and not f["entombed"] else 2
    if f["generation"] != 0 and now - f["lastThoughtAt"] > diapause_at(block):
        return 1
    return 0


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
    shipped = None
    if a.check:
        with open(os.path.join(a.check, "life_table.csv")) as fh:
            shipped = list(csv.DictReader(fh))
        with open(os.path.join(a.check, "PINNED_BLOCK")) as fh:
            to = int(fh.read().split()[0])
    rpc.at = hex(to)
    now = int(rpc.batch([("eth_getBlockByNumber", [hex(to), False])])[0]["timestamp"], 16)

    hub = logs(rpc, [[T[n] for n in NAME.values() if n != "Interred"]], DEPLOY_BLOCK, to, HUB)
    interred = logs(rpc, [T["Interred"]], DEPLOY_BLOCK, to, AMBER)
    hub.sort(key=lambda x: (int(x["blockNumber"], 16), int(x["logIndex"], 16)))
    blocks = sorted({int(x["blockNumber"], 16) for x in hub})
    when = {b: int(r["timestamp"], 16) for b, r in zip(blocks, rpc.batch([("eth_getBlockByNumber", [hex(b), False]) for b in blocks]))}

    # the fold
    F, keeper, owner, transfers, children, wokes, expected_wokes, observed_wokes, bad = {}, {}, {}, Counter(), Counter(), Counter(), [], [], []
    stud = {}
    for x in hub:
        n, b = NAME[x["topics"][0]], int(x["blockNumber"], 16)
        ts, w = when[b], words(x["data"])
        if n == "Transfer":
            f = int(x["topics"][3], 16)
            owner[f] = "0x" + x["topics"][2][-40:]
            if int(x["topics"][1], 16):
                transfers[f] += 1
            continue
        f = int(x["topics"][1], 16)
        if n == "Eclosed":
            gen = w[1]
            F[f] = {"bornAt": ts, "deathAt": ts + (BASE_LIFE if gen == 0 else BROOD_LIFE), "lastThoughtAt": ts, "lastBredAt": 0,
                    "thoughts": 0, "generation": gen, "mother": w[2], "father": w[3], "entombed": False, "born_block": b}
            keeper[f] = "0x" + x["topics"][2][-40:]
            if gen:
                children[w[2]] += 1
                children[w[3]] += 1
        elif n == "Thought":
            s, d = F[f], diapause_at(b)
            gap = ts - s["lastThoughtAt"]
            if gap > d:
                expected_wokes.append((f, gap - d))
            charge = max(0, gap - d) if (b < P2_BLOCK or s["generation"]) else 0
            effective = max(0, s["deathAt"] - charge)
            s["deathAt"] = min(effective + PER_THOUGHT, s["bornAt"] + MAX_LIFE) if b < P2_BLOCK else effective
            s["lastThoughtAt"], s["thoughts"] = ts, s["thoughts"] + 1
            if w[12] != s["deathAt"]:
                bad.append(f"fly {f}: Thought {w[0]} reports deathAt {w[12]}, the fold says {s['deathAt']}")
        elif n == "Tended":
            s = F[f]
            s["deathAt"] = max(s["deathAt"], ts + TENDED_FOR)
            if w[0] != s["deathAt"]:
                bad.append(f"fly {f}: Tended {w[0]} at block {b}, the fold says {s['deathAt']}")
        elif n == "Woke":  # logged before the thought's own Thought: compared with the gaps at the end
            wokes[f] += 1
            observed_wokes.append((f, w[0]))
        elif n == "Accepted":
            F[f]["lastBredAt"] = F[int(x["topics"][2], 16)]["lastBredAt"] = ts
        elif n == "Advertised":
            stud[f] = (w[0], "0x" + x["topics"][2][-40:])
        elif n == "Entombed":
            F[f]["entombed"], F[f]["deathAt"] = True, w[0]
        elif n == "Woken":
            pass  # its Tended carries the window
    if sorted(observed_wokes) != sorted(expected_wokes):
        bad.append(f"Woke logs {sorted(observed_wokes)} are not the thought gaps past diapauseAfter {sorted(expected_wokes)}")

    # the pinned state
    ids = sorted(F)
    reads = rpc.batch([rpc.call(HUB, SEL[s] + f"{f:064x}") for f in ids for s in SEL])
    rows = []
    for i, f in enumerate(ids):
        r = dict(zip(SEL, reads[i * len(SEL):(i + 1) * len(SEL)]))
        fo = words(r["flyOf"])
        s = F[f]
        chain = {"bornAt": fo[0], "deathAt": fo[1], "lastThoughtAt": fo[2], "lastBredAt": fo[3], "thoughts": fo[4],
                 "generation": fo[5], "mother": fo[6], "father": fo[7], "entombed": bool(fo[8])}
        for key, v in chain.items():
            if s[key] != v:
                bad.append(f"fly {f}: {key} {v} on chain, {s[key]} from the log")
        dm, lf = int(r["deathAtOf"], 16), int(r["lifeOf"], 16)
        if dm != death_moment(chain, to):
            bad.append(f"fly {f}: deathAtOf {dm} is not deathMoment {death_moment(chain, to)}")
        if lf != life_of(chain, now, to):
            bad.append(f"fly {f}: lifeOf {lf} is not {life_of(chain, now, to)}")
        own = "0x" + r["ownerOf"][-40:]
        if own != owner.get(f):
            bad.append(f"fly {f}: ownerOf {own}, last Transfer to {owner.get(f)}")
        fee, by = int(r["studFeeOf"], 16), "0x" + r["advertisedBy"][-40:]
        want = stud.get(f, (0, "0x" + "0" * 40))
        if fee != want[0] or (fee and by != want[1]):
            bad.append(f"fly {f}: studFeeOf {fee} by {by}, last Advertised {want}")
        rows.append({"fly": f, "generation": s["generation"], "mother": s["mother"], "father": s["father"], "born_block": s["born_block"],
                     "born_at": s["bornAt"], "keeper": keeper[f], "owner": own, "transfers": transfers[f], "thoughts": s["thoughts"],
                     "last_thought_at": s["lastThoughtAt"], "last_bred_at": s["lastBredAt"], "children": children[f], "wokes": wokes[f],
                     "stud_fee": fee // 10**18 if by == own else 0, "death_at": s["deathAt"], "death_moment": dm, "life": LIFE[lf],
                     "status": int(r["statusOf"], 16)})

    if shipped is not None:
        ours = [{key: str(v) for key, v in r.items()} for r in rows]
        diff = [s["fly"] for s, o in zip(shipped, ours) if s != o] + (["row count"] if len(shipped) != len(ours) else [])
        print(f"life_table.csv: {len(shipped)} rows, {'identical' if not diff else 'DIFFERS at ' + ', '.join(map(str, diff[:10]))}")
        bad += diff
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        with open(os.path.join(a.out, "life_table.csv"), "w", newline="") as fh:
            w = csv.DictWriter(fh, FIELDS, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        with open(os.path.join(a.out, "PINNED_BLOCK"), "w") as fh:
            fh.write(f"{to} {now}\n")
        print("wrote", os.path.join(a.out, "life_table.csv"), "pinned at block", to)

    for b in bad:
        print("MISMATCH", b)
    life = Counter((r["generation"] > 0, r["life"]) for r in rows)
    print(f"{len(rows)} flies at block {to} ({now}): founders " + " ".join(f"{life[(False, l)]} {l}" for l in LIFE if life[(False, l)])
          + "; brood " + " ".join(f"{life[(True, l)]} {l}" for l in LIFE if life[(True, l)]))
    print(f"the fold reproduces flyOf, deathAtOf, lifeOf and ownerOf for {len(rows) - len({m.split()[1] for m in bad if m.startswith('fly')})}/{len(rows)}; "
          f"{sum(wokes.values())} Woke on {len(expected_wokes)} thought gaps past diapauseAfter; {sum(transfers.values())} transfers; "
          f"{len(interred)} Interred; head {head}; {len(bad)} mismatches")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

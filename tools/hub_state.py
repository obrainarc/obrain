#!/usr/bin/env python3
"""Read the hub's governance state and the code at every address in the Flybook record at a block.

Writes hub_state.txt (paused, upgradesRenounced, timelock and its getMinDelay, guardian and whether
it holds code, PupaRearmed count to the block) and addresses.csv (every keeper, courter and owner
address in the study's CSVs: roles, code size at the block, code prefix, and whether the code is an
EIP-7702 delegation `0xef0100…`, with its delegate), and footprint.csv (the population's load on the chain to the block:
for each kind of hub transaction, Eclosed / Thought / Courted / Transfer, the distinct transactions,
their gas used and the fees they paid in the chain's native unit, from the receipts; a `total_unique` row counts
each transaction once, since a courtship's thought and an eclosion's mint share their transaction). With --check DIR,
regenerates all three at DIR's PINNED_BLOCK and diffs.

    python3 tools/hub_state.py [--rpc URL] --data DIR [--out DIR] [--check DIR] [--fresh]
"""
import argparse
import csv
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chain import Rpc  # noqa: E402
from verify_flybook import DEPLOY_BLOCK, HUB  # noqa: E402
from verify_generation1 import PUPAE, T, topic  # noqa: E402

KINDS = {"Eclosed": T["Eclosed"], "Thought": T["Thought"], "Courted": T["Courted"], "Transfer": topic("Transfer(address,address,uint256)")}

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIELDS = ["address", "roles", "code_bytes", "code_prefix", "eip7702_delegation", "delegate"]
FOOT = ["kind", "logs", "transactions", "gas_used", "fee_native_wei"]


def selector(sig: str) -> str:
    return topic(sig)[:10]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rpc", default="https://rpc.mainnet.arc.io")
    ap.add_argument("--data", required=True, help="dir with thought_census.csv, courtship.csv, life_table.csv, PINNED_BLOCK")
    ap.add_argument("--out")
    ap.add_argument("--check")
    ap.add_argument("--fresh", action="store_true")
    a = ap.parse_args()
    rpc = Rpc(a.rpc, cache=not a.fresh)
    with open(os.path.join(a.data, "PINNED_BLOCK")) as fh:
        at = int(fh.read().split()[0])
    blk = hex(at)

    def load(p):
        with open(p) as fh:
            return list(csv.DictReader(fh))
    roles = defaultdict(set)
    for x in load(os.path.join(a.data, "thought_census.csv")):
        roles[x["keeper"].lower()].add("keeper")
    for x in load(os.path.join(HERE, "research/2026-09-27-flybook-generation-zero/data/thought_census.csv")):
        roles[x["keeper"].lower()].add("keeper")
    for x in load(os.path.join(a.data, "courtship.csv")):
        roles[x["courter"].lower()].add("courter")
    for x in load(os.path.join(a.data, "life_table.csv")):
        roles[x["keeper"].lower()].add("ecloser")
        roles[x["owner"].lower()].add("owner")
    addrs = sorted(roles)
    codes = rpc.batch([("eth_getCode", [ad, blk]) for ad in addrs])
    rows = [{"address": ad, "roles": " ".join(sorted(roles[ad])), "code_bytes": (len(c) - 2) // 2, "code_prefix": c[:12] if len(c) > 2 else "",
             "eip7702_delegation": int(c.lower().startswith("0xef0100")), "delegate": "0x" + c[8:48].lower() if c.lower().startswith("0xef0100") else ""} for ad, c in zip(addrs, codes)]

    paused, renounced, timelock, guardian = rpc.batch([("eth_call", [{"to": HUB, "data": selector(s)}, blk]) for s in ("paused()", "upgradesRenounced()", "timelock()", "guardian()")])
    timelock, guardian = "0x" + timelock[-40:], "0x" + guardian[-40:]
    delay, tcode, gcode = rpc.batch([("eth_call", [{"to": timelock, "data": selector("getMinDelay()")}, blk]), ("eth_getCode", [timelock, blk]), ("eth_getCode", [guardian, blk])])
    rearmed = rpc.logs([[topic("PupaRearmed(uint256,uint64,uint64,uint8)")]], DEPLOY_BLOCK, at, PUPAE)
    per_pupa = defaultdict(int)
    for x in rearmed:
        per_pupa[int(x["topics"][1], 16)] += 1
    state = (f"block {at}\npaused {int(paused, 16) != 0}\nupgradesRenounced {int(renounced, 16) != 0}\n"
             f"timelock {timelock} code_bytes {(len(tcode) - 2) // 2} minDelay_seconds {int(delay, 16)}\n"
             f"guardian {guardian} code_bytes {(len(gcode) - 2) // 2}\n"
             f"PupaRearmed_logs {len(rearmed)} pupae_rearmed {len(per_pupa)}\n"
             f"rearms_by_pupa {' '.join(f'{k}:{v}' for k, v in sorted(per_pupa.items()))}\n")
    foot, alltx, nlogs = [], set(), 0
    for kind, tp in KINDS.items():
        lg = rpc.logs([[tp]], DEPLOY_BLOCK, at, HUB)
        txs = sorted({x["transactionHash"] for x in lg})
        rc = rpc.receipts(txs)
        foot.append({"kind": kind, "logs": len(lg), "transactions": len(txs), "gas_used": sum(int(rc[t]["gasUsed"], 16) for t in txs),
                     "fee_native_wei": sum(int(rc[t]["gasUsed"], 16) * int(rc[t]["effectiveGasPrice"], 16) for t in txs)})
        alltx |= set(txs); nlogs += len(lg)
    rc = rpc.receipts(sorted(alltx))  # a courtship's thought and an eclosion's mint share their transaction: count each once
    foot.append({"kind": "total_unique", "logs": nlogs, "transactions": len(alltx), "gas_used": sum(int(r["gasUsed"], 16) for r in rc.values()),
                 "fee_native_wei": sum(int(r["gasUsed"], 16) * int(r["effectiveGasPrice"], 16) for r in rc.values())})
    with_code = sum(r["code_bytes"] > 0 for r in rows)
    print(f"{len(rows)} addresses, {with_code} hold code at block {at} ({sum(r['eip7702_delegation'] for r in rows)} EIP-7702 delegations, "
          f"{with_code - sum(r['eip7702_delegation'] for r in rows)} deployed contracts)")
    print(state, end="")
    for f in foot:
        print(f"{f['kind']}: {f['logs']} logs in {f['transactions']} transactions, {f['gas_used']:,} gas, {f['fee_native_wei'] / 1e18:.4f} native units in fees")
    bad = []
    if a.check:
        shipped = load(os.path.join(a.check, "addresses.csv"))
        ours = [{k: str(r[k]) for k in FIELDS} for r in rows]
        bad = [i for i, (s, o) in enumerate(zip(shipped, ours)) if s != o] + (["row count"] if len(shipped) != len(ours) else [])
        print(f"addresses.csv: {len(shipped)} rows, {'identical' if not bad else 'DIFFERS at ' + ', '.join(map(str, bad[:10]))}")
        with open(os.path.join(a.check, "hub_state.txt")) as fh:
            same = fh.read() == state
        print(f"hub_state.txt: {'identical' if same else 'DIFFERS'}")
        bad += [] if same else ["hub_state"]
        shipped = load(os.path.join(a.check, "footprint.csv"))
        ours = [{k: str(r[k]) for k in FOOT} for r in foot]
        d = [i for i, (sh, o) in enumerate(zip(shipped, ours)) if sh != o] + (["row count"] if len(shipped) != len(ours) else [])
        print(f"footprint.csv: {len(shipped)} rows, {'identical' if not d else 'DIFFERS at ' + ', '.join(map(str, d))}")
        bad += d
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        with open(os.path.join(a.out, "addresses.csv"), "w", newline="") as fh:
            w = csv.DictWriter(fh, FIELDS, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        with open(os.path.join(a.out, "hub_state.txt"), "w") as fh:
            fh.write(state)
        with open(os.path.join(a.out, "footprint.csv"), "w", newline="") as fh:
            w = csv.DictWriter(fh, FOOT, lineterminator="\n")
            w.writeheader()
            w.writerows(foot)
        print("wrote", a.out)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())

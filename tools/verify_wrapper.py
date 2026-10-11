#!/usr/bin/env python3
"""Re-derive what a custody contract did with the flies deposited into it over a block interval (CS-010).

For every hub `Transfer` of a fly to the contract in (FROM, TO], finds the contract's own `Transfer` logs
in the same transaction and writes wrapper_deposits.csv (fly, block, tx, depositor, the token the contract
minted and to whom) and wrapper_tokens.csv (every `Transfer` log the contract emitted in the interval:
mints, moves, with the fly deposited in the same transaction when there is one). With --check DIR, regenerates
both at DIR's PINNED_BLOCK from the previous census block given with --from and diffs.

    python3 tools/verify_wrapper.py --contract 0x… --from PREV_BLOCK [--to BLOCK] [--out DIR] [--check DIR] [--fresh]
"""
import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chain import Rpc  # noqa: E402
from verify_flybook import HUB  # noqa: E402
from verify_generation1 import topic  # noqa: E402

TRANSFER = topic("Transfer(address,address,uint256)")
DEPOSITS = ["fly", "block", "tx", "depositor", "wrapped_token", "minted_to"]
TOKENS = ["block", "tx", "token", "from", "to", "kind", "fly_deposited"]


def addr(t: str) -> str:
    return "0x" + t[-40:]


def derive(rpc: Rpc, contract: str, frm: int, to: int):
    contract = contract.lower()
    hub = [x for x in rpc.logs([TRANSFER], frm, to, HUB) if addr(x["topics"][2]) == contract]
    own = rpc.logs([TRANSFER], frm, to, contract)
    key = lambda x: (int(x["blockNumber"], 16), int(x["logIndex"], 16))
    hub.sort(key=key)
    own.sort(key=key)
    by_tx = {}
    for x in own:
        by_tx.setdefault(x["transactionHash"], []).append(x)
    fly_in_tx = {x["transactionHash"]: int(x["topics"][3], 16) for x in hub}
    deposits, tokens = [], []
    for x in hub:
        mints = [m for m in by_tx.get(x["transactionHash"], []) if int(m["topics"][1], 16) == 0]
        m = mints[0] if mints else None
        deposits.append({"fly": int(x["topics"][3], 16), "block": int(x["blockNumber"], 16), "tx": x["transactionHash"],
                         "depositor": addr(x["topics"][1]), "wrapped_token": int(m["topics"][3], 16) if m else "",
                         "minted_to": addr(m["topics"][2]) if m else ""})
    for x in own:
        f, t = int(x["topics"][1], 16), int(x["topics"][2], 16)
        tokens.append({"block": int(x["blockNumber"], 16), "tx": x["transactionHash"], "token": int(x["topics"][3], 16),
                       "from": addr(x["topics"][1]), "to": addr(x["topics"][2]),
                       "kind": "mint" if f == 0 else ("burn" if t == 0 else "move"), "fly_deposited": fly_in_tx.get(x["transactionHash"], "")})
    return deposits, tokens


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rpc", default="https://rpc.mainnet.arc.io")
    ap.add_argument("--contract", required=True)
    ap.add_argument("--from", dest="frm", type=int, required=True, help="the previous census block; the interval starts at the next block")
    ap.add_argument("--to", type=int)
    ap.add_argument("--out")
    ap.add_argument("--check")
    ap.add_argument("--fresh", action="store_true", help="ignore the local cache; read everything from the chain")
    a = ap.parse_args()
    rpc = Rpc(a.rpc, cache=not a.fresh)
    to = a.to or rpc.head
    if a.check:
        with open(os.path.join(a.check, "PINNED_BLOCK")) as fh:
            to = int(fh.read().split()[0])
    deposits, tokens = derive(rpc, a.contract, a.frm + 1, to)
    n_mint = sum(t["kind"] == "mint" for t in tokens)
    matched = sum(bool(d["wrapped_token"]) and d["minted_to"] == d["depositor"] for d in deposits)
    print(f"{len(deposits)} deposits into {a.contract} in blocks {a.frm + 1}-{to}: {matched} minted one token to the depositor in the same transaction; "
          f"the contract emitted {len(tokens)} Transfer logs ({n_mint} mints, {sum(t['kind'] == 'move' for t in tokens)} moves of "
          f"{len({t['token'] for t in tokens if t['kind'] == 'move'})} tokens to {len({t['to'] for t in tokens if t['kind'] == 'move'})} addresses, "
          f"{sum(t['kind'] == 'burn' for t in tokens)} burns); {len({d['depositor'] for d in deposits})} depositors")
    bad = 0
    for name, rows, fields in (("wrapper_deposits.csv", deposits, DEPOSITS), ("wrapper_tokens.csv", tokens, TOKENS)):
        if a.check:
            with open(os.path.join(a.check, name)) as fh:
                shipped = [{k: v for k, v in r.items()} for r in csv.DictReader(fh)]
            mine = [{k: str(r[k]) for k in fields} for r in rows]
            same = shipped == mine
            bad += not same
            print(f"{name}: {len(shipped)} rows, {'identical' if same else 'DIFFERENT (' + str(len(mine)) + ' re-derived)'}")
        if a.out:
            with open(os.path.join(a.out, name), "w", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
                w.writeheader()
                w.writerows(rows)
            print(f"wrote {os.path.join(a.out, name)}")
    print(f"{bad} mismatches")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

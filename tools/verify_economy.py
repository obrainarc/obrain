#!/usr/bin/env python3
"""The economy of the Flybook population, re-derived from consensus: what every fly earned and
cost in OBRAIN, what it sold for in USDC, and what OBRAIN was worth in USDC when it did.

From the hub (`Eclosed` prices, `Sensed` fees, `Courted`/`Accepted` stud fees, `PupaLaid` asks,
ERC-721 `Transfer`s), the ledgers (`Rewards.Claimed`, `Orchard.OrchardClaimed`,
`Orchard.SeasonClaimed`, `Orchard.Fed`), the OBRAIN/USDC pool (Uniswap v4 `Swap` logs of the
PoolManager for the pool id the Flybook web reads) and the transactions behind each secondary
transfer (native USDC value, or ERC-20 USDC/OBRAIN `Transfer` logs in the same receipt), it writes:

  cashflows.csv  one row per fly: generation, price paid at eclosion, care fees spent on it,
                 stud fees its owner received (90 % of the escrow), nursery asks received (60 %),
                 ledger claims by source, feed spent, and the same in USDC at the pool price of
                 each event's block
  sales.csv      one row per secondary transfer: block, fly, from, to, the contract it went
                 through, the USDC paid in that transaction (shared equally when one transaction
                 moved several flies), the OBRAIN price of a founder at that block
  price.csv      one row per pool swap: block, timestamp, USDC per OBRAIN

    python3 tools/verify_economy.py [--rpc URL] [--to BLOCK] [--out DIR] [--check DIR] [--fresh]

Needs pycryptodome; the JSON-RPC client is tools/chain.py.
"""
import argparse
import bisect
import csv
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify_flybook import DEPLOY_BLOCK, HUB, Rpc, k  # noqa: E402
from verify_generation1 import T, words  # noqa: E402

ORCHARD = "0x1cfe143b38dadd74db66770f5c0a83d5d5cb9f3a"
REWARDS = "0x7a525aa5daf37214a4cf7455a2ac84d6af4fe9ec"
OBRAIN = "0x28f986a61e078795639f239675582a12b4cf7f01"
USDC = "0x3600000000000000000000000000000000000000"
STATE_VIEW = "0xF3334192D15450CdD385c8B70e03f9A6bD9E673b"
POOL_ID = "0xcb884ecb09388944a1afd5e1b74c42a4dfb2f93ec38288ce20c966ec233a0d52"
SEAPORT = "0x0000000000000068f116a894984e2db1123eb395"


def topic(sig: str) -> str:
    return "0x" + k(sig.encode()).hex()


E = {n: topic(s) for n, s in {
    "PupaLaid": "PupaLaid(uint256,address,uint256,uint256,bytes32,uint256,uint256,address)",
    "Transfer": "Transfer(address,address,uint256)",
    "Claimed": "Claimed(uint256,uint256,uint8,uint256,address)",
    "OrchardClaimed": "OrchardClaimed(uint256,uint256,uint8,uint256,address)",
    "SeasonClaimed": "SeasonClaimed(uint256,uint256,uint256,address)",
    "Fed": "Fed(uint256,uint8,uint256)",
    "Swap": "Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24)",
    "Initialize": "Initialize(bytes32,address,address,uint24,int24,address,uint160,int24)",
}.items()}
SOURCES = ["price", "care", "stud", "egg_ask", "claimed", "orchard", "season", "feed"]
CASH = ["fly", "generation", "born_block"] + SOURCES + [s + "_usdc" for s in SOURCES]
SALES = ["block", "timestamp", "tx", "fly", "from", "to", "via", "usdc", "founder_price_usdc"]
PRICE = ["block", "timestamp", "usdc_per_obrain"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rpc", default="https://rpc.mainnet.arc.io")
    ap.add_argument("--to", type=int)
    ap.add_argument("--out")
    ap.add_argument("--check")
    ap.add_argument("--fresh", action="store_true")
    a = ap.parse_args()
    rpc = Rpc(a.rpc, cache=not a.fresh)
    to = a.to or rpc.head
    if a.check:
        with open(os.path.join(a.check, "CENSUS_BLOCK")) as fh:
            to = int(fh.read().split()[0])

    # ---- the pool: one price per swap, carried forward
    pm = "0x" + rpc.multicall([(STATE_VIEW, "0x" + k(b"poolManager()").hex()[:8])])[0][-40:]
    init = rpc.logs([E["Initialize"], POOL_ID], DEPLOY_BLOCK - 1_000_000, to, pm)
    swaps = rpc.logs([E["Swap"], POOL_ID], int(init[0]["blockNumber"], 16) if init else DEPLOY_BLOCK - 1_000_000, to, pm)
    sw_blocks = sorted({int(x["blockNumber"], 16) for x in swaps})
    when = {b: int(h["timestamp"], 16) for b, h in rpc.blocks(sw_blocks).items()}
    price_rows = []
    for x in swaps:
        sq = words(x["data"])[2]
        b = int(x["blockNumber"], 16)
        price_rows.append({"block": b, "timestamp": when[b], "usdc_per_obrain": (sq / 2 ** 96) ** 2 * 1e12})
    pb = [r["block"] for r in price_rows]

    def price_at(block: int) -> float:
        i = bisect.bisect_right(pb, block) - 1
        return price_rows[i]["usdc_per_obrain"] if i >= 0 else 0.0

    # ---- the hub and the ledgers
    hub = rpc.logs([[T[n] for n in ("Eclosed", "Courted", "Accepted", "Rejected", "Laid", "PupaHatched", "Thought", "Sensed")]], DEPLOY_BLOCK, to, HUB)
    pupa = rpc.logs([E["PupaLaid"]], DEPLOY_BLOCK, to, HUB)
    transfers = [x for x in rpc.logs([E["Transfer"]], DEPLOY_BLOCK, to, HUB) if int(x["topics"][1], 16)]
    ledger = rpc.logs([[E[n] for n in ("Claimed", "OrchardClaimed", "SeasonClaimed", "Fed")]], DEPLOY_BLOCK, to, [ORCHARD, REWARDS])
    cf = defaultdict(lambda: defaultdict(float))
    meta = {}
    courted = {}
    for x in hub:
        t, b, f = x["topics"][0], int(x["blockNumber"], 16), int(x["topics"][1], 16)
        if t == T["Eclosed"]:
            w = words(x["data"])
            meta[f] = (w[1], b)
            cf[f]["price"] += w[12] / 1e18
            cf[f]["price_usdc"] += w[12] / 1e18 * price_at(b)
        elif t == T["Sensed"]:
            fee = words(x["data"])[2] / 1e18
            cf[f]["care"] += fee
            cf[f]["care_usdc"] += fee * price_at(b)
        elif t == T["Courted"]:
            courted[(b, f)] = words(x["data"])[0] / 1e18
        elif t == T["Accepted"]:
            fee = courted[(b, f)] * 0.9
            cf[f]["stud"] += fee
            cf[f]["stud_usdc"] += fee * price_at(b)
    for x in pupa:
        w, b = words(x["data"]), int(x["blockNumber"], 16)
        for fly, ask in ((w[0], w[3]), (w[1], w[4])):
            cf[fly]["egg_ask"] += ask / 1e18 * 0.6
            cf[fly]["egg_ask_usdc"] += ask / 1e18 * 0.6 * price_at(b)
    for x in ledger:
        t, b = x["topics"][0], int(x["blockNumber"], 16)
        if t == E["Fed"]:
            f, amt, src = int(x["topics"][1], 16), words(x["data"])[1] / 1e18, "feed"
        else:
            f = int(x["topics"][2], 16)
            amt = words(x["data"])[0 if t == E["SeasonClaimed"] else 1] / 1e18
            src = {E["Claimed"]: "claimed", E["OrchardClaimed"]: "orchard", E["SeasonClaimed"]: "season"}[t]
        cf[f][src] += amt
        cf[f][src + "_usdc"] += amt * price_at(b)
    cash = [{"fly": f, "generation": meta[f][0], "born_block": meta[f][1], **{key: round(cf[f][key], 6) for key in CASH[3:]}} for f in sorted(meta)]

    # ---- the sales
    txs = sorted({x["transactionHash"] for x in transfers})
    receipts = rpc.receipts(txs)
    txdata = dict(zip(txs, rpc.batch([("eth_getTransactionByHash", [t]) for t in txs])))
    per_tx = defaultdict(list)
    for x in transfers:
        per_tx[x["transactionHash"]].append(x)
    tr_when = {b: int(h["timestamp"], 16) for b, h in rpc.blocks(sorted({int(x["blockNumber"], 16) for x in transfers})).items()}
    sales = []
    for tx in txs:
        rc, td = receipts[tx], txdata[tx]
        paid = int(td["value"], 16) / 1e18  # native USDC
        if not paid:  # ERC-20 USDC or OBRAIN moved in the same receipt
            usdc = sum(int(l["data"], 16) / 1e6 for l in rc["logs"] if l["topics"][0] == E["Transfer"] and len(l["topics"]) == 3 and l["address"].lower() == USDC)
            ob = sum(int(l["data"], 16) / 1e18 for l in rc["logs"] if l["topics"][0] == E["Transfer"] and len(l["topics"]) == 3 and l["address"].lower() == OBRAIN)
            paid = usdc + ob * price_at(int(rc["blockNumber"], 16))
        for x in per_tx[tx]:
            b = int(x["blockNumber"], 16)
            sales.append({"block": b, "timestamp": tr_when[b], "tx": tx, "fly": int(x["topics"][3], 16), "from": "0x" + x["topics"][1][-40:], "to": "0x" + x["topics"][2][-40:],
                          "via": rc["to"].lower(), "usdc": round(paid / len(per_tx[tx]), 6), "founder_price_usdc": round(200_000 * price_at(b), 6)})
    sales.sort(key=lambda r: (r["block"], r["fly"]))

    out = {"cashflows.csv": (CASH, cash), "sales.csv": (SALES, sales), "price.csv": (PRICE, [{**r, "usdc_per_obrain": f"{r['usdc_per_obrain']:.12g}"} for r in price_rows])}
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
        for name, (fields, rows) in out.items():
            with open(os.path.join(a.out, name), "w", newline="") as fh:
                w = csv.DictWriter(fh, fields, lineterminator="\n")
                w.writeheader()
                w.writerows(rows)
        with open(os.path.join(a.out, "CENSUS_BLOCK"), "w") as fh:
            fh.write(f"{to}\n")
        print("wrote", a.out, "to block", to)
    tot = {s: sum(r[s] for r in cash) for s in SOURCES}
    print(f"{len(cash)} flies to block {to}: " + ", ".join(f"{s} {v:,.0f}" for s, v in tot.items()) + " OBRAIN; "
          f"{len(sales)} secondary transfers in {len(txs)} transactions, {sum(1 for s in sales if s['usdc'])} priced in USDC; "
          f"{len(price_rows)} pool swaps, last {price_rows[-1]['usdc_per_obrain']:.3g} USDC/OBRAIN; head {rpc.head}; {len(bad)} mismatches")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

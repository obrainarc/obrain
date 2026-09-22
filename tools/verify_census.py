#!/usr/bin/env python3
"""Re-scan the brain's BrainState and Feed logs from Arc and verify the shipped census.

Compares every on-chain thought against research/2026-09-22-brainstate-census/data/
brainstate_census.csv (tick, block, feed, poke word, fired ids, synapses, spiked,
readout p0-p3), checks the poke law (poke = levels[tier] << channel*3), and
confirms the row count against the contract's own TICK(). Exits nonzero on any
mismatch, so the census can be re-audited by anyone at any time:

    python3 tools/verify_census.py [rpc_url] [brain_address] [from_block]

stdlib only; 9,999-block getLogs chunks with backoff (Arc throttles bursts).
"""
import csv
import json
import sys
import time
import urllib.request
from pathlib import Path

RPC = sys.argv[1] if len(sys.argv) > 1 else "https://rpc.mainnet.arc.io"
BRAIN = (sys.argv[2] if len(sys.argv) > 2 else "0xaef83c5b8742da5e3228930bc6084adcf0539ccd").lower()
FROM = int(sys.argv[3], 0) if len(sys.argv) > 3 else 21_181_651
HERE = Path(__file__).resolve().parent.parent
BS_TOPIC = "0xc08a3de3fd4d1048d0992ce0624e6d1287cb294188d6f70ee83a87baa5ec6375"
FEED_TOPIC = "0x22196226f70d916ec28deedcf1dfbee374b5eb7ad606b22044371f7e13be12c0"
LEVELS = {0: 31, 1: 127, 2: 255}


def rpc(method, params, tries=5):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    for attempt in range(tries):
        try:
            req = urllib.request.Request(RPC, data=body, headers={
                "Content-Type": "application/json", "User-Agent": "Mozilla/5.0 verify_census/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                out = json.loads(r.read())
            if "result" in out:
                return out["result"]
            msg = str(out.get("error", {}).get("message", ""))
            if any(s in msg for s in ("32005", "429", "not available", "rate")):
                time.sleep(3 * (attempt + 1))
                continue
            raise SystemExit(f"rpc error: {msg}")
        except urllib.error.HTTPError:
            if attempt == tries - 1:
                raise
            time.sleep(3 * (attempt + 1))


def scan(topic):
    head = int(rpc("eth_blockNumber", []), 16)
    logs, start = [], FROM
    while start <= head:
        end = min(start + 9_999 - 1, head)
        logs += rpc("eth_getLogs", [{"address": BRAIN, "topics": [topic],
                                     "fromBlock": hex(start), "toBlock": hex(end)}])
        start = end + 1
        time.sleep(0.35)
    return logs


def s16(w):  # int256 lane value
    v = int.from_bytes(w, "big")
    return v - (1 << 256) if v >> 255 else v


def decode_brainstate(log):
    d = log["data"][2:]
    word = lambda i: bytes.fromhex(d[64 * i:64 * (i + 1)])
    off = int.from_bytes(word(9), "big")           # `fired` head
    length = int.from_bytes(word(off // 32), "big")
    packed = bytes.fromhex(d[64 * (off // 32 + 1):64 * (off // 32 + 1) + length * 2])
    return {
        "tick": int(log["topics"][1], 16),
        "block": int(log["blockNumber"], 16),
        "p": [s16(word(i)) for i in range(4)],
        "synapses": int.from_bytes(word(4), "big") & 0xFFFFFFFF,
        "spiked": int.from_bytes(word(5), "big") & 0xFFFFFFFF,
        "capped": word(6)[-1] != 0,
        "state_root": "0x" + word(7).hex(),
        "poke": int.from_bytes(word(8), "big"),
        "fired_ids": [int.from_bytes(packed[i:i + 3], "big") for i in range(0, len(packed), 3)],
    }


def decode_feed(log):
    d = log["data"][2:]
    w0 = bytes.fromhex(d[:64]); w1 = bytes.fromhex(d[64:128])
    return {
        "block": int(log["blockNumber"], 16),
        "feeder": "0x" + log["topics"][1][26:],
        "channel": int(log["topics"][2], 16),
        "tier": int(log["topics"][3], 16),
        "amount": int.from_bytes(w0, "big") // 10**18,
    }


def main():
    census = list(csv.DictReader(open(HERE / "research/2026-09-22-brainstate-census/data/brainstate_census.csv")))
    print(f"census rows: {len(census)}; scanning blocks {FROM}..head for {BRAIN}")
    bs = sorted((decode_brainstate(l) for l in scan(BS_TOPIC)), key=lambda r: r["tick"])
    feeds = {f["block"]: f for f in (decode_feed(l) for l in scan(FEED_TOPIC))}
    tick_now = int.from_bytes(bytes.fromhex(rpc("eth_call", [{"to": BRAIN, "data": "0x3eaf5d9f"}, "latest"])[2:]), "big")

    errors = []
    if [r["tick"] for r in bs] != list(range(1, len(census) + 1)):
        errors.append(f"chain ticks {[r['tick'] for r in bs][:5]}... not contiguous 1..{len(census)}")
    if len(bs) != len(census):
        errors.append(f"chain has {len(bs)} BrainStates, census has {len(census)}")
    if len(bs) != tick_now:
        errors.append(f"TICK() = {tick_now} but {len(bs)} events scanned")

    for ev, row in zip(bs, census):
        t = row["tick"]
        f = feeds.get(ev["block"])
        if f is None:
            errors.append(f"tick {t}: no Feed event at block {ev['block']}")
            continue
        checks = [
            (int(row["block"]) == ev["block"], f"tick {t}: block {row['block']} != {ev['block']}"),
            (int(row["channel"]) == f["channel"] and int(row["tier"]) == f["tier"], f"tick {t}: feed mismatch"),
            (int(row["obrain_burned"]) == f["amount"], f"tick {t}: amount mismatch"),
            (row["feeder"].lower() == f["feeder"], f"tick {t}: feeder mismatch"),
            (int(row["poke_word"]) == ev["poke"], f"tick {t}: poke {row['poke_word']} != {ev['poke']}"),
            (ev["poke"] == LEVELS[f["tier"]] << (f["channel"] * 3), f"tick {t}: poke law violated"),
            (int(row["poked_cells"]) == len(ev["fired_ids"]), f"tick {t}: fired count"),
            ([int(x) for x in row["fired_ids"].split()] == ev["fired_ids"], f"tick {t}: fired ids"),
            (int(row["synapses"]) == ev["synapses"] and int(row["spiked"] or 0) == ev["spiked"], f"tick {t}: synapses/spiked"),
            (row["capped"] == str(ev["capped"]).lower(), f"tick {t}: capped"),
            ([int(row[k]) for k in ("p0", "p1", "p2", "p3")] == ev["p"], f"tick {t}: readout"),
        ]
        errors += [msg for ok, msg in checks if not ok]

    if errors:
        print(f"FAIL - {len(errors)} mismatches:")
        for e in errors[:20]:
            print(" ", e)
        raise SystemExit(1)
    print(f"PASS - {len(census)} thoughts verified against the chain: events, feeds, pokes, "
          f"spike lists, counts, readouts; poke law holds throughout; TICK() = {tick_now}")


if __name__ == "__main__":
    main()

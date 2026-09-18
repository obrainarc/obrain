#!/usr/bin/env python3
"""Prove the 85 on-chain ImmortalFruitFliesTape tapes are byte-identical to tapes/*.bin.

ImmortalFruitFliesTape's constructor returns the payload as its runtime code, so explorers
cannot source-verify tapes the usual way; this fetches eth_getCode for every tapes(i) and
byte-compares against the repository files. Exits nonzero on mismatch.

    python3 tools/verify_tapes.py [rpc_url] [brain_address]
"""
import json
import sys
import urllib.request
from pathlib import Path

RPC = sys.argv[1] if len(sys.argv) > 1 else "https://rpc.mainnet.arc.io"
BRAIN = sys.argv[2] if len(sys.argv) > 2 else "0xaef83c5b8742da5e3228930bc6084adcf0539ccd"
HERE = Path(__file__).resolve().parent.parent
SEL = "0x487a22d0"  # tapes(uint256)


def rpc_call(method: str, params: list) -> dict:
    req = urllib.request.Request(
        RPC,
        data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 verify_tapes/1.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["result"]


def main() -> None:
    files = sorted((HERE / "tapes").glob("tape_*.bin"))
    ok = 0
    for i, f in enumerate(files):
        addr = "0x" + rpc_call("eth_call", [{"to": BRAIN, "data": SEL + f"{i:064x}"}, "latest"])[-40:]
        code = rpc_call("eth_getCode", [addr, "latest"])
        if code == "0x" + f.read_bytes().hex():
            ok += 1
        else:
            print(f"MISMATCH tape {i} at {addr}")
    print(f"tapes byte-identical on-chain: {ok}/{len(files)} (brain {BRAIN})")
    sys.exit(0 if ok == len(files) else 1)


if __name__ == "__main__":
    main()

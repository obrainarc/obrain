#!/usr/bin/env python3
"""Verify the Flybook descendants of the organism: their brains, their wiring, their genes.

Flybook (hub 0x14b5…eb36 on Arc) ecloses flies whose brains are EIP-1167 clones of one
`Connectome`, all reading the species' `Holotype`, which points at the Ancestor's own 85
tapes. For every `Eclosed` log this re-derives from consensus alone:

  wiring    Holotype.tape(i) == Ancestor.tapes(i), i = 0..84 (the tapes verify_tapes.py
            proves byte-identical to tapes/), and Holotype.configHash()
  soma      brainOf(fly) is the 45-byte clone of the Connectome implementation and its
            holotype() is the Holotype
  genotype  founder: seed = keccak(blockhash(n - 1), flyId, owner), gene s present when
            bit s of seed is set, allele = low 32 bits of keccak(seed, uint8(s), "g")
            (Meiosis.founder); the brain's stored genome() equals the Eclosed genome
  physiology  a brain that has thought holds, in rootDirty(), the root of its last Thought

and writes the founder census (immutable fields only) with --out. Exits nonzero on any
mismatch. With --check CSV it re-derives up to that census' last block and diffs it.

    python3 tools/verify_flybook.py [--rpc URL] [--out CSV] [--check CSV]

Needs pycryptodome (as verify_twin.py does); batched JSON-RPC, 9,999-block getLogs chunks.
"""
import argparse
import csv
import json
import sys
import time
import urllib.request
from collections import Counter

from Crypto.Hash import keccak

HUB = "0x14b557957d378b56511785b408a21c93e79feb36"
HOLOTYPE = "0xb0725bf519786c8d2798e99d45c8c7fe886be73b"
CONNECTOME = "caa923d6dbe59e780e32914257cbbf8deae4c5d2"
ANCESTOR = "0xaef83c5b8742da5e3228930bc6084adcf0539ccd"
DEPLOY_BLOCK = 22_703_390
ECLOSED = "0x" + keccak.new(digest_bits=256, data=b"Eclosed(uint256,address,address,uint16,uint256,uint256,uint256[8],uint256,address)").hexdigest()
THOUGHT = "0x5a417a3ac1296589324f66f63001dc960243f226b6e4da15b03f271f185e39ac"  # Connectome.Thought
ACCEPTED = "0x1066add5337f2b25f517544b4b10627e28766a6adeac425240b246c3f930dbc9"
SEL = {"brainOf": "0x3d383602", "holotype": "0xd0b9b4e7", "genome": "0xd5ba0428", "rootDirty": "0x1f0817dc",
       "tick": "0x3eaf5d9f", "tape": "0xdcd953b3", "tapes": "0x487a22d0", "configHash": "0xe1f1176d"}
CLONE = "0x363d3d373d3d3d363d73" + CONNECTOME + "5af43d82803e903d91602b57fd5bf3"

# Phenotype.sol: gene groups and the classical mutant each hashes to; wild when the group is empty
TRAITS = {"eyes": (0, 8, "red", ["white", "sepia", "brown", "vermilion"]),
          "body": (8, 16, "wild", ["yellow", "ebony", "tan"]),
          "wings": (16, 24, "normal", ["curly", "vestigial", "dumpy"]),
          "size": (24, 32, "medium", ["small", "large"])}
FIELDS = ["fly", "block", "owner", "brain", "parent_blockhash", "seed", "alleles", "eyes", "body", "wings", "size", "genome"]


def k(data: bytes) -> bytes:
    return keccak.new(digest_bits=256, data=data).digest()


def founder(seed: bytes) -> list:
    s = int.from_bytes(seed, "big")
    return [int.from_bytes(k(seed + bytes([i]) + b"g")[-4:], "big") if s >> i & 1 else 0 for i in range(64)]


def phenotype(genes: list) -> dict:
    out = {}
    for name, (lo, hi, wild, variants) in TRAITS.items():
        g = genes[lo:hi]
        out[name] = variants[int.from_bytes(k(b"".join(x.to_bytes(4, "big") for x in g)), "big") % len(variants)] if any(g) else wild
    return out


def genes64(words: list) -> list:
    return [(words[s >> 3] >> ((s & 7) * 32)) & 0xFFFFFFFF for s in range(64)]


class Rpc:
    def __init__(self, url: str):
        self.url = url

    def batch(self, calls: list, tries: int = 12) -> list:
        """calls: [(method, params)] -> results in order. Arc throttles at about 20 requests a
        burst (-32005), so calls go 20 at a time and only the throttled ones are retried."""
        out = [None] * len(calls)
        todo = list(range(len(calls)))
        for attempt in range(tries):
            for i in range(0, len(todo), 20):
                ids = todo[i:i + 20]
                body = json.dumps([{"jsonrpc": "2.0", "id": j, "method": calls[j][0], "params": calls[j][1]} for j in ids]).encode()
                try:
                    req = urllib.request.Request(self.url, data=body, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 verify_flybook/1.0"})
                    with urllib.request.urlopen(req, timeout=60) as r:
                        for x in json.loads(r.read()):
                            if "result" in x:
                                out[x["id"]] = x["result"]
                            elif x.get("error", {}).get("code") != -32005:
                                raise SystemExit(f"rpc error {x['error']} on {calls[x['id']]}")
                except (urllib.error.URLError, TimeoutError):
                    pass
                time.sleep(1.0)
            todo = [j for j in todo if out[j] is None]
            if not todo:
                return out
            time.sleep(2 * (attempt + 1))
        raise SystemExit(f"rpc failed after {tries} tries: {calls[todo[0]]}")

    def call(self, to: str, data: str) -> tuple:
        return ("eth_call", [{"to": to, "data": data}, self.at])

    def logs(self, topics: list, frm: int, to: int, address=None) -> list:
        f = {"topics": topics}
        if address:
            f["address"] = address
        calls = [("eth_getLogs", [dict(f, fromBlock=hex(a), toBlock=hex(min(a + 9_998, to)))]) for a in range(frm, to + 1, 9_999)]
        return [log for chunk in self.batch(calls) for log in chunk]


def word(n: int) -> str:
    return f"{n:064x}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rpc", default="https://rpc.mainnet.arc.io")
    ap.add_argument("--out", help="write the founder census CSV here")
    ap.add_argument("--check", help="re-derive this census up to its last block and diff")
    a = ap.parse_args()
    rpc = Rpc(a.rpc)
    shipped = list(csv.DictReader(open(a.check))) if a.check else None
    head = int(rpc.batch([("eth_blockNumber", [])])[0], 16)
    rpc.at = hex(head)  # every read at one block, so a fly thinking mid-run cannot race the check
    to = max(int(r["block"]) for r in shipped) if shipped else head
    bad = []

    # wiring: the species reads the Ancestor's tapes
    got = rpc.batch([rpc.call(HOLOTYPE, SEL["tape"] + word(i)) for i in range(85)] +
                    [rpc.call(ANCESTOR, SEL["tapes"] + word(i)) for i in range(85)] +
                    [rpc.call(HOLOTYPE, SEL["configHash"])])
    same = sum(got[i] == got[85 + i] for i in range(85))
    bad += [f"tape {i}" for i in range(85) if got[i] != got[85 + i]]
    print(f"wiring: Holotype.tape(i) == Ancestor.tapes(i) {same}/85, configHash {got[170]}")

    logs = sorted(rpc.logs([ECLOSED], DEPLOY_BLOCK, to, HUB), key=lambda x: int(x["topics"][1], 16))
    flies = []
    for log in logs:
        d = bytes.fromhex(log["data"][2:])
        w = [int.from_bytes(d[i:i + 32], "big") for i in range(0, len(d), 32)]
        flies.append({"fly": int(log["topics"][1], 16), "owner": "0x" + log["topics"][2][-40:], "brain": "0x" + f"{w[0]:040x}",
                      "generation": w[1], "mother": w[2], "father": w[3], "genes": genes64(w[4:12]), "words": w[4:12],
                      "block": int(log["blockNumber"], 16)})
    blocks = sorted({f["block"] - 1 for f in flies})
    hashes = dict(zip(blocks, (b["hash"] for b in rpc.batch([("eth_getBlockByNumber", [hex(b), False]) for b in blocks]))))
    per = ["brainOf", "code", "holotype", "genome", "rootDirty", "tick"]
    reads = rpc.batch([c for f in flies for c in (
        rpc.call(HUB, SEL["brainOf"] + word(f["fly"])), ("eth_getCode", [f["brain"], rpc.at]),
        rpc.call(f["brain"], SEL["holotype"]), rpc.call(f["brain"], SEL["genome"]),
        rpc.call(f["brain"], SEL["rootDirty"]), rpc.call(f["brain"], SEL["tick"]))])
    thoughts = {}
    for log in rpc.logs([THOUGHT], DEPLOY_BLOCK, head):
        thoughts.setdefault(log["address"].lower(), []).append(log)

    rows, thinkers = [], 0
    for n, f in enumerate(flies):
        r = dict(zip(per, reads[n * len(per):(n + 1) * len(per)]))
        fly, brain = f["fly"], f["brain"]
        if r["brainOf"][-40:] != brain[2:]:
            bad.append(f"fly {fly}: brainOf {r['brainOf']} != Eclosed brain {brain}")
        if r["code"] != CLONE:
            bad.append(f"fly {fly}: brain code is not the Connectome clone")
        if r["holotype"][-40:] != HOLOTYPE[2:]:
            bad.append(f"fly {fly}: holotype {r['holotype']}")
        stored = r["genome"][2:]
        if [int(stored[i:i + 64], 16) for i in range(0, 512, 64)] != f["words"]:
            bad.append(f"fly {fly}: stored genome != Eclosed genome")
        if f["generation"] != 0:
            print(f"fly {fly}: generation {f['generation']} (mother {f['mother']}, father {f['father']}); inheritance is checked in the study, not here")
            continue
        ph = bytes.fromhex(hashes[f["block"] - 1][2:])
        seed = k(ph + fly.to_bytes(32, "big") + bytes.fromhex(f["owner"][2:]))
        if founder(seed) != f["genes"]:
            bad.append(f"fly {fly}: genome does not reproduce from its seed")
        mine = sorted(thoughts.get(brain, []), key=lambda x: (int(x["blockNumber"], 16), int(x["logIndex"], 16)))
        if mine:
            thinkers += 1
            last = mine[-1]
            root = "0x" + last["data"][2 + 64 * 4: 2 + 64 * 5]
            if int(last["topics"][1], 16) != int(r["tick"], 16) or root != r["rootDirty"]:
                bad.append(f"fly {fly}: last Thought (tick {int(last['topics'][1], 16)}) does not commit to storage")
        rows.append({"fly": fly, "block": f["block"], "owner": f["owner"], "brain": brain, "parent_blockhash": hashes[f["block"] - 1],
                     "seed": "0x" + seed.hex(), "alleles": sum(1 for g in f["genes"] if g), **phenotype(f["genes"]),
                     "genome": " ".join(f"{g:08x}" for g in f["genes"])})

    for b in bad:
        print("MISMATCH", b)
    if shipped is not None:
        ours = [{k2: str(v) for k2, v in r.items()} for r in rows]
        diff = [s["fly"] for s, o in zip(shipped, ours) if s != o] + (["row count"] if len(shipped) != len(ours) else [])
        print(f"census {a.check}: {len(shipped)} rows, {'identical' if not diff else 'DIFFERS at ' + ', '.join(diff)}")
        bad += diff
    if a.out:
        with open(a.out, "w", newline="") as fh:
            w = csv.DictWriter(fh, FIELDS, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        print("wrote", a.out)
    al = [r["alleles"] for r in rows]
    if al:
        mean = sum(al) / len(al)
        var = sum((x - mean) ** 2 for x in al) / (len(al) - 1) if len(al) > 1 else 0
        print(f"alleles per founder: mean {mean:.2f} var {var:.2f} min {min(al)} max {max(al)} (Binomial(64, 1/2): 32, 16)")
        for t in TRAITS:
            print(f"{t}: " + " · ".join(f"{v} {c}" for v, c in Counter(r[t] for r in rows).most_common()))
    accepted = rpc.logs([ACCEPTED], DEPLOY_BLOCK, head, HUB)
    print(f"{len(flies)} flies to block {to}: {len(rows)} founders reproduced from the chain, {thinkers} have thought, "
          f"{len(accepted)} matings accepted; head {head}; {len(bad)} mismatches")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

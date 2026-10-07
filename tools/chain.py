#!/usr/bin/env python3
"""The one JSON-RPC client the Flybook audits share: throttled batches, a cache of what the
chain can no longer change, and Multicall3 for state reads.

Arc's public RPC answers about 20 requests a burst (-32005 past that) and times out a 20-chunk
`eth_getLogs` batch over a busy day, so calls go 20 at a time with a pause and log chunks go one
request each. Logs, block headers and receipts below the head's finality margin are immutable,
so they are kept in an SQLite file (`~/.cache/obrain/chain.sqlite`, or $OBRAIN_CACHE) and an
audit fetches only the blocks it has not seen; `Rpc(url, cache=False)` (`--fresh` in the tools)
ignores the file and reads everything from the chain again, which is how a study's shipped
verification run is made. State reads go through Multicall3 (`tryAggregate`) in groups of 200,
one request instead of two hundred, and fall back to plain `eth_call`s when it is absent.
"""
import json
import os
import sqlite3
import time
import urllib.request

MULTICALL3 = "0xcA11bde05977b3631167028862bE2a173976CA11"
TRY_AGGREGATE = "0xbce38bd7"  # tryAggregate(bool,(address,bytes)[])
SPAN = 9_999  # blocks per eth_getLogs chunk; cached chunks start at DEPLOY-aligned multiples
FINAL = 256  # blocks under the head a chunk must be before it is cached
CACHE = os.environ.get("OBRAIN_CACHE", os.path.expanduser("~/.cache/obrain/chain.sqlite"))


def word(n: int) -> str:
    return f"{n:064x}"


class Rpc:
    def __init__(self, url: str, cache: bool = True):
        self.url = url
        self.at = "latest"
        self.head = int(self.batch([("eth_blockNumber", [])])[0], 16)
        self.db = None
        if cache:
            os.makedirs(os.path.dirname(CACHE), exist_ok=True)
            self.db = sqlite3.connect(CACHE)
            self.db.executescript("CREATE TABLE IF NOT EXISTS logs (key TEXT, start INTEGER, body TEXT, PRIMARY KEY (key, start));"
                                  "CREATE TABLE IF NOT EXISTS blocks (number INTEGER PRIMARY KEY, body TEXT);"
                                  "CREATE TABLE IF NOT EXISTS receipts (tx TEXT PRIMARY KEY, body TEXT);")

    # ------------------------------------------------------------------ transport
    def batch(self, calls: list, tries: int = 12) -> list:
        """calls: [(method, params)] -> results in order; only the throttled or timed-out ones are retried"""
        out = [None] * len(calls)
        todo = list(range(len(calls)))
        for attempt in range(tries):
            for i in range(0, len(todo), 20):
                ids = todo[i:i + 20]
                body = json.dumps([{"jsonrpc": "2.0", "id": j, "method": calls[j][0], "params": calls[j][1]} for j in ids]).encode()
                try:
                    req = urllib.request.Request(self.url, data=body, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 obrain-audit/2.0"})
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

    # ------------------------------------------------------------------ the immutable past, cached
    def logs(self, topics: list, frm: int, to: int, address=None) -> list:
        """every log matching `topics` (and `address`: one or a list) in [frm, to], one chunk per request;
        the RPC refuses a filter with more than a few addresses (-32012), so a long list is fetched
        by topic alone and filtered here (the cache then holds the topic's whole stream once)"""
        if isinstance(address, list) and len(address) > 8:
            want = {a.lower() for a in address}
            return [x for x in self.logs(topics, frm, to) if x["address"].lower() in want]
        f = {"topics": topics}
        if address:
            f["address"] = address
        key = json.dumps([address, topics], sort_keys=True)
        out = []
        for a in range(frm, to + 1, SPAN):
            b = min(a + SPAN - 1, to)
            row = self.db.execute("SELECT body FROM logs WHERE key = ? AND start = ?", (key, a)).fetchone() if self.db else None
            if row:
                out += [x for x in json.loads(row[0]) if int(x["blockNumber"], 16) <= b]
                continue
            chunk = self.batch([("eth_getLogs", [dict(f, fromBlock=hex(a), toBlock=hex(b))])])[0]
            out += chunk
            if self.db and b == a + SPAN - 1 and b <= self.head - FINAL:  # a whole chunk, final: keep it
                self.db.execute("INSERT OR REPLACE INTO logs VALUES (?, ?, ?)", (key, a, json.dumps(chunk)))
                self.db.commit()
        return out

    def blocks(self, numbers: list) -> dict:
        """number -> header (hash, timestamp, ...) for every block asked"""
        numbers = sorted(set(numbers))
        got = {}
        if self.db:
            for n in numbers:
                row = self.db.execute("SELECT body FROM blocks WHERE number = ?", (n,)).fetchone()
                if row:
                    got[n] = json.loads(row[0])
        need = [n for n in numbers if n not in got]
        for n, h in zip(need, self.batch([("eth_getBlockByNumber", [hex(n), False]) for n in need])):
            got[n] = h
            if self.db and n <= self.head - FINAL:
                self.db.execute("INSERT OR REPLACE INTO blocks VALUES (?, ?)", (n, json.dumps(h)))
        if self.db:
            self.db.commit()
        return got

    def receipts(self, txs: list) -> dict:
        got = {}
        if self.db:
            for t in txs:
                row = self.db.execute("SELECT body FROM receipts WHERE tx = ?", (t,)).fetchone()
                if row:
                    got[t] = json.loads(row[0])
        need = [t for t in txs if t not in got]
        for t, r in zip(need, self.batch([("eth_getTransactionReceipt", [t]) for t in need])):
            got[t] = r
            if self.db and int(r["blockNumber"], 16) <= self.head - FINAL:
                self.db.execute("INSERT OR REPLACE INTO receipts VALUES (?, ?)", (t, json.dumps(r)))
        if self.db:
            self.db.commit()
        return got

    # ------------------------------------------------------------------ state, two hundred reads a request
    def multicall(self, calls: list) -> list:
        """calls: [(to, data)] -> return data of each, at self.at; a reverted call returns '0x'"""
        if not calls:
            return []
        if not hasattr(self, "_mc"):
            self._mc = self.batch([("eth_getCode", [MULTICALL3, "latest"])])[0] not in (None, "0x")
        if not self._mc:
            return self.batch([self.call(to, data) for to, data in calls])
        groups = [calls[i:i + 200] for i in range(0, len(calls), 200)]
        out = []
        for g, res in zip(groups, self.batch([self.call(MULTICALL3, _encode_try_aggregate(g)) for g in groups])):
            out += _decode_results(res, len(g))
        return out


def _encode_try_aggregate(calls: list) -> str:
    """tryAggregate(false, calls): bool, then a dynamic array of (address, bytes) tuples"""
    heads, tails = [], []
    base = 32 * len(calls)
    for to, data in calls:
        raw = bytes.fromhex(data[2:])
        heads.append(word(base + sum(len(t) for t in tails)))
        tails.append(bytes.fromhex(word(int(to, 16)) + word(64) + word(len(raw))) + raw + b"\0" * (-len(raw) % 32))
    arr = word(len(calls)) + "".join(heads) + b"".join(tails).hex()
    return TRY_AGGREGATE + word(0) + word(64) + arr


def _decode_results(res: str, n: int) -> list:
    """(bool success, bytes returnData)[] -> ['0x...'] with '0x' for a failed call"""
    b = bytes.fromhex(res[2:])
    arr = int.from_bytes(b[:32], "big")
    count = int.from_bytes(b[arr:arr + 32], "big")
    assert count == n, (count, n)
    out = []
    for i in range(n):
        off = arr + 32 + int.from_bytes(b[arr + 32 + 32 * i:arr + 64 + 32 * i], "big")
        ok = int.from_bytes(b[off:off + 32], "big")
        doff = off + int.from_bytes(b[off + 32:off + 64], "big")
        ln = int.from_bytes(b[doff:doff + 32], "big")
        out.append("0x" + b[doff + 32:doff + 32 + ln].hex() if ok else "0x")
    return out


if __name__ == "__main__":  # self-check: multicall agrees with plain eth_call on two reads
    rpc = Rpc("https://rpc.mainnet.arc.io", cache=False)
    hub = "0x14b557957d378b56511785b408a21c93e79feb36"
    calls = [(hub, "0x9ae89478"), (hub, "0x3d383602" + word(1)), (hub, "0x7904a302" + word(10**9))]
    mc, plain = rpc.multicall(calls), rpc.batch([rpc.call(t, d) for t, d in calls[:2]])
    assert mc[:2] == plain and mc[2] == "0x", (mc, plain)
    print("multicall ok:", int(mc[0], 16), "flies; brainOf(1)", "0x" + mc[1][-40:])

#!/usr/bin/env python3
"""Score a register of predictions (tools/predict_next.py, CS-007) against what the brains did.

A register row names, for one brain at one tick, the Thought log it will write if its next
stimulus is one of 57 (19 sensilla at 3 tiers, the pheromone). The brain's next thought is its
replay.csv row at tick_before + 1 (tools/verify_clones.py, chain-exact); the row was *tested*
if that thought's input word is the row's, and *hit* if spike count, root and the cells fired
outside the input layer agree. A brain whose next input was none of the 57 (an expedition)
spent its rows untested. A pheromone row also predicts the ruling of the target's next
courtship (courtship.csv row at target_tick == tick_before + 1): accept iff the predicted
courtship-region count >= the target's selectivity. A waiting.csv charge is scored by whether
the brain's next thought visited its segment and whether the cell then fired; `live` marks the charges
the register could have fired at the next thought (the segment's last visit, read from the register's
own replay.csv, within `fires_if_visited_within` ticks of the next tick), the rest are stranded.

    python3 tools/score_register.py --register DIR --data DIR [--out DIR] [--check DIR]

Writes register_score.csv (one row per brain that thought after the registration block),
courtship_score.csv and waiting_score.csv; --check diffs them against shipped files.
No RPC: everything is read from the two studies' CSVs.
"""
import argparse
import csv
import os
from collections import defaultdict

SCORE = ["fly", "tick_before", "next_block", "next_tick", "next_input_agg", "sensillum", "tier", "tested", "predicted_spiked", "observed_spiked", "predicted_out_of_layer", "observed_out_of_layer", "predicted_root", "observed_root", "hit"]
COURT = ["block", "target", "suitor", "outcome", "target_tick", "tick_before", "predicted_count", "observed_fired", "selectivity", "predicted_ruling", "hit"]
WAIT = ["fly", "tick_before", "cell", "segment", "live", "next_block", "next_segments", "visited", "fired"]


def load(path):
    with open(path) as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--register", required=True, help="dir with predictions.csv, waiting.csv, REGISTERED_BLOCK")
    ap.add_argument("--data", required=True, help="dir with replay.csv and courtship.csv to a later block")
    ap.add_argument("--out")
    ap.add_argument("--check")
    a = ap.parse_args()
    with open(os.path.join(a.register, "REGISTERED_BLOCK")) as fh:
        reg_block = int(fh.read().split()[0])
    rows = load(os.path.join(a.register, "predictions.csv"))
    waiting = load(os.path.join(a.register, "waiting.csv"))
    replay = load(os.path.join(a.data, "replay.csv"))
    last = defaultdict(dict)  # fly -> segment -> its last visit before the registration block
    for r in load(os.path.join(a.register, "replay.csv")):
        for seg in r["segments"].split():
            last[r["fly"]][seg] = max(last[r["fly"]].get(seg, 0), int(r["tick"]))
    courtship = load(os.path.join(a.data, "courtship.csv"))

    nxt = {}  # fly -> its first thought after the registration block
    for r in sorted(replay, key=lambda r: (int(r["block"]), int(r["tick"]))):
        if int(r["block"]) > reg_block and r["fly"] not in nxt:
            nxt[r["fly"]] = r
    by_fly = defaultdict(list)
    for r in rows:
        by_fly[r["fly"]].append(r)

    score = []
    for f in sorted(nxt, key=int):
        n, regs = nxt[f], by_fly.get(f, [])
        if not regs:
            continue  # born after the register
        tb = regs[0]["tick_before"]
        assert int(n["tick"]) == int(tb) + 1, f"fly {f}: next thought at tick {n['tick']}, registered at {tb}"
        hit = [r for r in regs if int(r["input_agg"], 16) == int(n["input_agg"], 16)]
        s = {"fly": f, "tick_before": tb, "next_block": n["block"], "next_tick": n["tick"], "next_input_agg": n["input_agg"], "tested": int(bool(hit)),
             "observed_spiked": n["spiked"], "observed_out_of_layer": n["out_of_layer"], "observed_root": n["root"]}
        if hit:
            (r,) = hit
            s.update(sensillum=r["sensillum"], tier=r["tier"], predicted_spiked=r["spiked"], predicted_out_of_layer=r["out_of_layer"], predicted_root=r["root"],
                     hit=int(r["spiked"] == n["spiked"] and r["root"].lower() == n["root"].lower() and r["out_of_layer"] == n["out_of_layer"]))
        score.append({k: s.get(k, "") for k in SCORE})

    court = []
    pher = {r["fly"]: r for r in rows if r["sensillum"] == "0" and r["tier"] == "1"}
    for c in courtship:
        if int(c["block"]) <= reg_block or c["target"] not in pher:
            continue
        p = pher[c["target"]]
        if int(c["target_tick"]) != int(p["tick_before"]) + 1:
            continue  # another thought spent the row
        ruling = "accepted" if int(p["courtship_region"]) >= int(c["selectivity"]) else "rejected"
        court.append({"block": c["block"], "target": c["target"], "suitor": c["suitor"], "outcome": c["outcome"], "target_tick": c["target_tick"], "tick_before": p["tick_before"],
                      "predicted_count": p["courtship_region"], "observed_fired": c["fired"], "selectivity": c["selectivity"], "predicted_ruling": ruling, "hit": int(ruling == c["outcome"] and p["courtship_region"] == c["fired"])})

    wait, live_all = [], 0
    for w in waiting:
        live = int(w["tick_before"]) + 1 - last[w["fly"]].get(w["segment"], 0) <= int(w["fires_if_visited_within"])
        live_all += live
        n = nxt.get(w["fly"])
        if n is None:
            continue
        segs = n["segments"].split()
        visited = w["segment"] in segs or w["segment"] == "0"
        wait.append({"fly": w["fly"], "tick_before": w["tick_before"], "cell": w["cell"], "segment": w["segment"], "live": int(live), "next_block": n["block"], "next_segments": n["segments"],
                     "visited": int(visited), "fired": int(w["cell"] in n["fired"].split())})

    out = {"register_score.csv": (SCORE, score), "courtship_score.csv": (COURT, court), "waiting_score.csv": (WAIT, wait)}
    tested = [s for s in score if s["tested"]]
    print(f"register at block {reg_block}: {len(score)} brains thought after it, {len(tested)} with a registered stimulus, "
          f"{sum(s['hit'] for s in tested)}/{len(tested)} rows hit (spiked, out-of-layer cells and root)")
    print(f"courtships at the target's registered tick: {len(court)}, rulings and counts hit {sum(c['hit'] for c in court)}/{len(court)}")
    lv = [w for w in wait if w["live"]]
    print(f"waiting charges: {len(waiting)} ({live_all} live); in brains that thought {len(wait)} ({len(lv)} live, {sum(w['visited'] for w in lv)} of them visited); "
          f"segment visited {sum(w['visited'] for w in wait)}, cell fired {sum(w['fired'] for w in wait)}")
    bad = []
    if a.check:
        for name, (fields, ours) in out.items():
            shipped = load(os.path.join(a.check, name))
            ours_s = [{k: str(r[k]) for k in fields} for r in ours]
            diff = [i for i, (s, o) in enumerate(zip(shipped, ours_s)) if s != o] + (["row count"] if len(shipped) != len(ours_s) else [])
            print(f"{name}: {len(shipped)} rows, {'identical' if not diff else 'DIFFERS at ' + ', '.join(map(str, diff[:10]))}")
            bad += diff
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        for name, (fields, rs) in out.items():
            with open(os.path.join(a.out, name), "w", newline="") as fh:
                w = csv.DictWriter(fh, fields, lineterminator="\n")
                w.writeheader()
                w.writerows(rs)
        print("wrote", a.out)
    misses = [s for s in tested if not s["hit"]] + [c for c in court if not c["hit"]]
    print(f"{len(bad)} differences, {len(misses)} misses")
    return 1 if bad or misses else 0


if __name__ == "__main__":
    raise SystemExit(main())

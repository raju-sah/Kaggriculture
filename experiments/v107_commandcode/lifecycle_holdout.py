#!/usr/bin/env python3
"""Criterion-4 lifecycle evidence for V107 on the firing holdout seeds.

The holdout itself ran --replay-policy none.  These are the SAME frozen seeds and
the SAME frozen candidate, re-run with replays retained purely to observe the
day-6 chain and the cow's later product.  Deterministic, so the games are the
same games; this adds evidence, not new evaluation.  Replays are deleted after
the audit to keep disk use low.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SIM = ROOT / "simulation"
CAND = HERE / "candidate.py"
BASE = ROOT / "agents" / "v50_agent.py"
OPP = ROOT / "agents" / "v56_agent.py"
TMP = HERE / "runs" / "_lifecycle_probe"
STRUCT = ("PASTURE", "PASTURE_1", "COOP")

FIRING = [190005, 190008, 190010, 190011, 190012, 190013, 190015,
          190017, 190018, 190019, 190020, 190021, 190023, 190024]


def day_hour(step):
    return step // 24 + 1, step % 24


def tiles(farm):
    out = []
    for row in farm.get("tiles", []) if isinstance(farm, dict) else []:
        for t in row:
            if isinstance(t, dict):
                out.append(t)
    return out


def analyse(path):
    """Chain completion, retained cow, and cow-tile harvest evidence.

    HARVEST carries only {actor,x,y} and SELL carries no species, so the cow's own
    product is attributed by tile position: a HARVEST at a tile the cow ended on is
    a harvest of that cow's product.
    """
    rep = json.loads(path.read_text())
    frames = rep["frames"]

    # Cow tiles are stable once placed; take them from the final frame.
    final_farm = (frames[-1].get("state") or {}).get("farms", [])[0]
    cow_tiles = {(t.get("x"), t.get("y")) for t in tiles(final_farm)
                 if t.get("animal") == "COW" and {"x", "y"} <= t.keys()}
    sheep_end = sum(1 for t in tiles(final_farm) if t.get("animal") == "SHEEP")

    a = {"buy": None, "pickup": [], "place": [], "cow_harvests": 0,
         "cow_harvest_days": [], "milk_cash": 0.0, "wool_cash": 0.0}
    # action_history is CUMULATIVE: every settled action lives in the final frame,
    # so all tallies below read that frame exactly once (never per-frame, which
    # would multiply-count).
    final_acts = (frames[-1].get("state") or {}).get("status", {}).get("action_history", [])
    for x in final_acts:
        s = x.get("action_string", "")
        ar = x.get("args", {}) or {}
        d, h = day_hour(x.get("step", 0))
        if d == 6 and h == 6 and s.startswith("BUY_ANIMAL"):
            a["buy"] = s
        elif d == 6 and "PICKUP_ANIMAL" in s and "COW" in s:
            a["pickup"].append(h)
        elif d == 6 and "PLACE_ANIMAL" in s and "COW" in s:
            a["place"].append(h)
        elif s == "HARVEST" and (ar.get("x"), ar.get("y")) in cow_tiles:
            a["cow_harvests"] += 1
            a["cow_harvest_days"].append(d)
        elif "SELL" in s and x.get("player_id") == 0:
            ch = ar.get("cashChange") or 0
            if "MILK" in s:
                a["milk_cash"] += ch
            elif "WOOL" in s:
                a["wool_cash"] += ch
    a["cow_harvest_days"] = sorted(set(a["cow_harvest_days"]))
    a["cow_end"] = len(cow_tiles)
    a["sheep_end"] = sheep_end
    return a


def main():
    import shutil
    rows = []
    for seed in FIRING:
        work = TMP / str(seed)          # per-seed dir: no cross-seed replay bleed
        work.mkdir(parents=True, exist_ok=True)
        cmd = [sys.executable, str(SIM / "match_worker.py"), "--seed", str(seed),
               "--agents", str(CAND), str(OPP), "--seats", "0", "1",
               "--repeats", "1", "--repeat-mode", "independent",
               "--timeout-seconds", "120", "--replay-policy", "all",
               "--out", str(work / "games.jsonl")]
        subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=600)
        rp = work / "replays"
        files = sorted(rp.glob("*.json")) if rp.exists() else []
        if not files:
            rows.append({"seed": seed, "error": "no replay"})
            print(f"{seed} NO REPLAY", flush=True)
            shutil.rmtree(work, ignore_errors=True)
            continue
        a = analyse(files[0])
        games = [json.loads(l) for l in (work / "games.jsonl").read_text().splitlines() if l.strip()]
        shutil.rmtree(work, ignore_errors=True)
        rows.append({"seed": seed, "buy": a["buy"],
                     "pickup_h": a["pickup"], "place_h": a["place"],
                     "cow_end": a["cow_end"], "sheep_end": a["sheep_end"],
                     "cow_harvests": a["cow_harvests"],
                     "cow_harvest_days": a["cow_harvest_days"],
                     "milk_cash": round(a["milk_cash"]), "wool_cash": round(a["wool_cash"]),
                     "err": bool(games[0].get("candidate_error")) if games else True})
        r = rows[-1]
        chain = bool(r["buy"]) and len(r["pickup_h"]) >= 1 and len(r["place_h"]) >= 1
        print(f"{seed} buy={r['buy']} pick={r['pickup_h']} place={r['place_h']} "
              f"cow_end={r['cow_end']} sheep={r['sheep_end']} "
              f"cow_harvests={r['cow_harvests']} (days {r['cow_harvest_days']}) "
              f"milk=${r['milk_cash']:,} chain={'OK' if chain else 'BAD'}", flush=True)
    (HERE / "lifecycle_holdout.json").write_text(json.dumps(rows, indent=2))
    good = sum(1 for r in rows
               if r.get("buy") and len(r.get("pickup_h", [])) >= 1
               and len(r.get("place_h", [])) >= 1 and r.get("cow_end", 0) >= 1
               and r.get("cow_harvests", 0) >= 1 and not r.get("err") and not r.get("error"))
    print(f"\nchain + retained cow + cow harvests on {good}/{len(rows)} firing seeds")


if __name__ == "__main__":
    main()

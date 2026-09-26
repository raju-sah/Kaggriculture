"""Compare the DSM replay-derived route with frozen v57 on fresh seed blocks."""
from __future__ import annotations

import hashlib
import json
import os
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from simulation.tournament import MatchSpec, Opponent, _run_worker

BASE = ROOT / "experiments/v57_broad/v57_reset_candidate.py"
DSM = ROOT / "experiments/v58_expansion/elite_route/v58_dsm_replay_route.py"
ROUTE = ROOT / "experiments/v58_expansion/elite_route/dsm_episode_113508988_actions.json"
OPPONENTS = {
    "v48": ROOT / "experiments/v48_agent.py",
    "v50": ROOT / "experiments/v50_agent.py",
    "v51": ROOT / "experiments/v51_agent.py",
    "v52": ROOT / "experiments/v52_agent.py",
    "v53": ROOT / "experiments/v53_agent.py",
    "v54": ROOT / "agents/v54_agent.py",
    "v55": ROOT / "agents/v55_agent.py",
    "v56": ROOT / "agents/v56_agent.py",
}
SEEDS = list(range(94110, 94115))
OUT = ROOT / "experiments/v58_expansion/elite_route/all8_94110"
HASHES = {
    "baseline": "4173479fe1f80d031d570d1ea23b694dfe86e1d162317a4c9c7df0058a40208e",
    "dsm": "88e26b19baebbf7c547190560de374884acb940f20dc5085ffef7ccc51f24671",
    "route": "",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def shops(path: Path, seat: int):
    data = json.loads(path.read_text())
    longest = []
    for state in data.get("steps", []):
        obs = state[seat].get("observation") or {}
        row = (obs.get("town") or {}).get("unlocked_shops") or []
        if len(row) > len(longest): longest = list(row)
    return longest


def route_adaptation(path: Path, seat: int, route):
    data = json.loads(path.read_text())
    actual_steps = data.get("steps", [])[1:]
    n = min(len(actual_steps), len(route))
    diffs = []
    actor_changes = 0
    action_changes = 0
    expected_actors = 0
    actual_actors = 0
    weed_digs = 0
    for i in range(n):
        expected = route[i] or {}
        actual = actual_steps[i][seat].get("action") or {}
        exp_units = [expected.get("farmer", ["PASS"]), *(expected.get("hands") or [])]
        act_units = [actual.get("farmer", ["PASS"]), *(actual.get("hands") or [])]
        expected_actors += len(exp_units)
        actual_actors += len(act_units)
        if expected != actual:
            action_changes += 1
            changed = sum((exp_units[j] if j < len(exp_units) else ["PASS"]) !=
                          (act_units[j] if j < len(act_units) else ["PASS"])
                          for j in range(max(len(exp_units), len(act_units))))
            actor_changes += changed
            if any(j < len(act_units) and act_units[j] and act_units[j][0] == "DIG" and
                   j < len(exp_units) and exp_units[j] and exp_units[j][0] in ("PLANT", "BUILD_PASTURE")
                   for j in range(max(len(exp_units), len(act_units)))):
                weed_digs += 1
            if len(diffs) < 5:
                obs = actual_steps[i][seat].get("observation") or {}
                diffs.append({"route_index": i, "step": obs.get("step"), "day": obs.get("day"),
                              "hour": obs.get("hour"), "expected_farmer": exp_units[0],
                              "actual_farmer": act_units[0], "expected_hand_count": len(exp_units)-1,
                              "actual_hand_count": len(act_units)-1})
    return {"action_rows_different_from_public_trace": action_changes,
            "unit_actions_different_from_trace": actor_changes,
            "expected_unit_action_count": expected_actors,
            "actual_unit_action_count": actual_actors,
            "weed_dig_repair_steps": weed_digs,
            "first_differences": diffs}


def margin(row):
    coins = row.get("final_coins") or [None, None]
    seat = int(row.get("candidate_seat", 0))
    return None if coins[0] is None or coins[1] is None else float(coins[seat] - coins[1-seat])


def main():
    os.chdir(ROOT)
    if sha(BASE) != HASHES["baseline"] or sha(DSM) != HASHES["dsm"]:
        raise SystemExit("Frozen source hash mismatch")
    route = json.loads(ROUTE.read_text())
    if len(route) != 719: raise SystemExit("DSM route must be exactly 719 actions")
    HASHES["route"] = sha(ROUTE)
    OUT.mkdir(parents=True, exist_ok=True)
    paths = {"baseline": BASE, "dsm_route": DSM}
    plans = {arm: {"candidate": str(p.relative_to(ROOT)), "sha256": sha(p),
                   "opponents": {n: str(o.relative_to(ROOT)) for n,o in OPPONENTS.items()},
                   "opponent_sha256": {n: sha(o) for n,o in OPPONENTS.items()},
                   "seeds": SEEDS, "seats": [0,1], "route_source_sha256": HASHES["route"]}
             for arm,p in paths.items()}
    for arm,p in plans.items():
        folder=OUT/arm;folder.mkdir(parents=True,exist_ok=True)
        (folder/"plan.json").write_text(json.dumps(p,indent=2)+"\n")
    tasks=[]
    for arm,candidate in paths.items():
        for name,op in OPPONENTS.items():
            for seed in SEEDS:
                for seat in (0,1):
                    tasks.append((arm,candidate,MatchSpec(Opponent(name,op),seed,bool(seat),0)))
    records={arm:[] for arm in paths};start=time.monotonic()
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures={pool.submit(_run_worker,c,spec,OUT/arm,240,"all"):(arm,spec)
                 for arm,c,spec in tasks}
        for future in as_completed(futures):
            arm,spec=futures[future];row=future.result()
            replay=Path(row["replay_path"]) if row.get("replay_path") else None
            seat=int(bool(spec.swapped));row["candidate_seat"]=seat
            row["candidate_coin_margin"]=margin(row)
            row["shop_sequence"]=shops(replay,seat) if replay and replay.exists() else []
            row["route_adaptation"]=route_adaptation(replay,seat,route) if arm=="dsm_route" and replay and replay.exists() else None
            row["replay_path"]=str(replay) if replay else None
            records[arm].append(row)
            print(f"{arm} {row['opponent']} seed={row['seed']} seat={seat} coins={row.get('final_coins')} "
                  f"margin={row['candidate_coin_margin']} elapsed={time.monotonic()-start:.0f}s",flush=True)
    for arm,rows in records.items():
        rows.sort(key=lambda r:(r["opponent"],r["seed"],r["candidate_seat"]))
        (OUT/arm/"games.json").write_text(json.dumps(rows,indent=2)+"\n")
        summaries={}
        for name in OPPONENTS:
            group=[r for r in rows if r["opponent"]==name]
            vals=[r["candidate_coin_margin"] for r in group if r["candidate_coin_margin"] is not None]
            summaries[name]={"wins":sum(r.get("candidate_result")=="win" for r in group),
                             "losses":sum(r.get("candidate_result")=="loss" for r in group),
                             "errors":sum(not r.get("ok") for r in group),
                             "mean_margin":statistics.fmean(vals) if vals else None}
        (OUT/arm/"summary.json").write_text(json.dumps({"games":len(rows),"by_opponent":summaries},indent=2)+"\n")
    bmap={(r["opponent"],r["seed"],r["candidate_seat"]):r for r in records["baseline"]}
    dmap={(r["opponent"],r["seed"],r["candidate_seat"]):r for r in records["dsm_route"]}
    paired=[]
    for key,b in bmap.items():
        d=dmap[key];seat=key[2];bc=b["final_coins"];dc=d["final_coins"]
        bp=Path(b["replay_path"]) if b.get("replay_path") else None
        dp=Path(d["replay_path"]) if d.get("replay_path") else None
        paired.append({"opponent":key[0],"seed":key[1],"candidate_seat":seat,
                       "baseline_coins_candidate_opponent":[bc[seat],bc[1-seat]],
                       "dsm_coins_candidate_opponent":[dc[seat],dc[1-seat]],
                       "candidate_coin_delta":dc[seat]-bc[seat],"opponent_coin_delta":dc[1-seat]-bc[1-seat],
                       "baseline_margin":b["candidate_coin_margin"],"dsm_margin":d["candidate_coin_margin"],
                       "margin_delta":d["candidate_coin_margin"]-b["candidate_coin_margin"],
                       "same_shop_sequence":b["shop_sequence"]==d["shop_sequence"],
                       "baseline_shop_sequence":b["shop_sequence"],"dsm_shop_sequence":d["shop_sequence"],
                       "first_action_difference":_first_diff(bp,dp,seat) if bp and dp and bp.exists() and dp.exists() else None})
    (OUT/"paired_comparison.json").write_text(json.dumps(paired,indent=2)+"\n")
    for arm in records:
        for r in records[arm]:
            if r.get("replay_path"):Path(r["replay_path"]).unlink(missing_ok=True)
            r["replay_path"]=None
        (OUT/arm/"games.json").write_text(json.dumps(records[arm],indent=2)+"\n")
    return 0 if all(r.get("ok") for rows in records.values() for r in rows) else 1


def _first_diff(bp: Path, dp: Path, seat: int):
    b=json.loads(bp.read_text()).get("steps",[]);d=json.loads(dp.read_text()).get("steps",[])
    for i,(bs,ds) in enumerate(zip(b,d)):
        ba=bs[seat].get("action") or {};da=ds[seat].get("action") or {}
        if ba!=da:
            obs=ds[seat].get("observation") or {}
            return {"step_index":i,"step":obs.get("step"),"day":obs.get("day"),"hour":obs.get("hour"),
                    "baseline_action":ba,"dsm_action":da}
    return None


if __name__ == "__main__":
    raise SystemExit(main())

"""Paired expansion-vs-reset development screen; writes only this experiment folder."""
from __future__ import annotations

import json
import hashlib
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from simulation.tournament import MatchSpec, Opponent, _game_id, _run_worker

BASELINE = ROOT / "experiments/v57_broad/v57_reset_candidate.py"
EXPANSION = ROOT / "experiments/v58_expansion/v58_expansion_candidate.py"
OPPONENTS = {
    "v50": ROOT / "experiments/v50_agent.py",
    "v53": ROOT / "experiments/v53_agent.py",
}
SEEDS = [93400, 93401, 93402, 93403]
OUT = ROOT / "experiments/v58_expansion/paired"


def main() -> int:
    os.chdir(ROOT)
    tasks = []
    plans = {}
    for arm, candidate in (("baseline", BASELINE), ("expansion", EXPANSION)):
        plans[arm] = {
            "candidate": str(candidate.relative_to(ROOT)),
            "candidate_sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(),
            "opponents": {}, "opponent_sha256": {}, "seeds": SEEDS,
            "seats": [0, 1], "engine": "kaggle-environments 1.32.7",
        }
        for name, path in OPPONENTS.items():
            plans[arm]["opponents"][name] = str(path.relative_to(ROOT))
            plans[arm]["opponent_sha256"][name] = hashlib.sha256(path.read_bytes()).hexdigest()
            for seed in SEEDS:
                for seat in (0, 1):
                    spec = MatchSpec(Opponent(name, path), seed, bool(seat), 0)
                    tasks.append((arm, candidate, spec))

    for arm, plan in plans.items():
        out = OUT / arm
        out.mkdir(parents=True, exist_ok=True)
        (out / "plan.json").write_text(json.dumps(plan, indent=2) + "\n")

    started = time.monotonic()
    records = {arm: [] for arm in plans}
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {}
        for arm, candidate, spec in tasks:
            arm_out = OUT / arm
            replay_policy = "all" if arm == "expansion" else "none"
            future = pool.submit(_run_worker, candidate, spec, arm_out, 240, replay_policy)
            futures[future] = arm
        for future in as_completed(futures):
            arm = futures[future]
            record = future.result()
            records[arm].append(record)
            coins = record.get("final_coins") or [None, None]
            seat = record.get("candidate_seat", 0)
            margin = coins[seat] - coins[1 - seat] if coins[0] is not None and coins[1] is not None else None
            record["candidate_coin_margin"] = margin
            print(f"{arm} {record['opponent']} seed={record['seed']} seat={seat} "
                  f"result={record['candidate_result']} margin={margin} "
                  f"elapsed={time.monotonic()-started:.0f}s", flush=True)

    for arm, rows in records.items():
        rows.sort(key=lambda row: (row["opponent"], row["seed"], row["candidate_seat"]))
        out = OUT / arm
        (out / "games.json").write_text(json.dumps(rows, indent=2) + "\n")
        summary = {}
        for opponent in OPPONENTS:
            group = [row for row in rows if row["opponent"] == opponent]
            margins = [float(row["candidate_coin_margin"]) for row in group if row.get("candidate_coin_margin") is not None]
            summary[opponent] = {
                "wins": sum(row["candidate_result"] == "win" for row in group),
                "losses": sum(row["candidate_result"] == "loss" for row in group),
                "draws": sum(row["candidate_result"] == "draw" for row in group),
                "errors": sum(not row.get("ok") for row in group),
                "mean_margin": sum(margins) / len(margins) if margins else None,
                "margins": margins,
            }
        (out / "summary.json").write_text(json.dumps({"games": len(rows), "by_opponent": summary,
            "elapsed_seconds": round(time.monotonic() - started, 1)}, indent=2) + "\n")
    return 0 if all(row.get("ok") for rows in records.values() for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())

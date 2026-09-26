"""Run the predeclared tuning or one-time confirmation panel."""
from __future__ import annotations

import hashlib
import json
import os
import statistics
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

from simulation.tournament import MatchSpec, Opponent, _game_id, _run_worker
from experiments.v58_validation.search.build_agents import BASE, CONFIGS, ROOT, build_all, sha

OUT = ROOT / "experiments/runs/v58_policy_search"
BASELINE = ROOT / "experiments/v57_broad/v57_reset_candidate.py"
TUNE_SEEDS = [94200, 94201, 94202]
CONFIRM_SEEDS = [94210, 94211, 94212, 94213, 94214]
TUNE_OPPONENTS = {
    "v48": "experiments/v48_agent.py",
    "v50": "experiments/v50_agent.py",
    "v53": "experiments/v53_agent.py",
    "v54": "agents/v54_agent.py",
}
CONFIRM_OPPONENTS = {
    "v48": "experiments/v48_agent.py",
    "v50": "experiments/v50_agent.py",
    "v51": "experiments/v51_agent.py",
    "v52": "experiments/v52_agent.py",
    "v53": "experiments/v53_agent.py",
    "v54": "agents/v54_agent.py",
    "v55": "agents/v55_agent.py",
    "v56": "agents/v56_agent.py",
}


def margin(row: dict) -> float:
    seat = row["candidate_seat"]
    return float(row["final_coins"][seat] - row["final_coins"][row["opponent_seat"]])


def opponent_hashes(opponents: dict[str, str]) -> dict[str, str]:
    return {name: sha(ROOT / path) for name, path in opponents.items()}


def load_arm(run_dir: Path, arm: str, candidate: Path, opponents: dict[str, str],
             seeds: list[int]) -> list[dict]:
    arm_dir = run_dir / "arms" / arm
    arm_dir.mkdir(parents=True, exist_ok=True)
    agent_hash = sha(candidate)
    opp_hashes = opponent_hashes(opponents)
    plan = {"candidate": str(candidate.relative_to(ROOT)), "candidate_sha256": agent_hash,
            "opponents": opponents, "opponent_sha256": opp_hashes,
            "seeds": seeds, "seats": [0, 1], "repeats": 1,
            "replay_policy": "errors", "final_holdout_used": False}
    old_plan_path = arm_dir / "plan.json"
    resume_eligible = False
    if old_plan_path.exists():
        try:
            old_plan = json.loads(old_plan_path.read_text())
            resume_eligible = all(old_plan.get(k) == plan[k] for k in (
                "candidate_sha256", "opponent_sha256", "seeds", "seats", "repeats"))
        except (OSError, json.JSONDecodeError):
            resume_eligible = False
    (arm_dir / "plan.json").write_text(json.dumps(plan, indent=2) + "\n")

    specs = [MatchSpec(Opponent(name, ROOT / path), seed, bool(seat), 0)
             for seed in seeds for name, path in opponents.items() for seat in (0, 1)]
    records = []
    pending = []
    for spec in specs:
        game_id = _game_id(spec)
        result_path = arm_dir / "games" / f"{game_id}.json"
        if result_path.exists():
            old = json.loads(result_path.read_text())
            seat = 1 if spec.swapped else 0
            if (resume_eligible
                    and old.get("candidate_seat") == seat
                    and old.get("opponent_path") == str(spec.opponent.path)
                    and old.get("opponent") == spec.opponent.name
                    and old.get("seed") == spec.seed
                    and old.get("ok") is True):
                records.append(old)
                continue
        pending.append(spec)

    completed = 0
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(_run_worker, candidate, spec, arm_dir, 240, "errors"): spec
                   for spec in pending}
        for future in as_completed(futures):
            row = future.result()
            records.append(row)
            completed += 1
            print(f"{arm}: {completed}/{len(pending)} {row['game_id']} ok={row.get('ok')}", flush=True)
    if sha(candidate) != agent_hash or opponent_hashes(opponents) != opp_hashes:
        raise SystemExit(f"Frozen artifacts changed during arm {arm}")
    records.sort(key=lambda r: (r["opponent"], r["seed"], r["candidate_seat"]))
    (arm_dir / "games.json").write_text(json.dumps(records, separators=(",", ":")) + "\n")
    summary = {"games": len(records), "errors": sum(not r.get("ok") for r in records),
               "wins": sum(r.get("candidate_result") == "win" for r in records),
               "losses": sum(r.get("candidate_result") == "loss" for r in records),
               "draws": sum(r.get("candidate_result") == "draw" for r in records)}
    (arm_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return records


def arm_comparison(baseline: list[dict], candidate: list[dict]) -> dict:
    key = lambda r: (r["opponent"], r["seed"], r["candidate_seat"])
    base_by_key = {key(row): row for row in baseline}
    cand_by_key = {key(row): row for row in candidate}
    if set(base_by_key) != set(cand_by_key):
        raise RuntimeError("baseline and candidate match keys differ")
    paired = []
    by_opponent: dict[str, list[float]] = {}
    for pair_key in sorted(base_by_key):
        base_row, cand_row = base_by_key[pair_key], cand_by_key[pair_key]
        if not base_row.get("ok") or not cand_row.get("ok"):
            paired.append({"opponent": pair_key[0], "seed": pair_key[1],
                           "candidate_seat": pair_key[2], "paired_margin_delta": None,
                           "candidate_win": cand_row.get("candidate_result") == "win",
                           "baseline_win": base_row.get("candidate_result") == "win",
                           "errors": int(not base_row.get("ok")) + int(not cand_row.get("ok"))})
            continue
        delta = margin(cand_row) - margin(base_row)
        by_opponent.setdefault(pair_key[0], []).append(delta)
        paired.append({"opponent": pair_key[0], "seed": pair_key[1],
                       "candidate_seat": pair_key[2],
                       "baseline_margin": margin(base_row),
                       "candidate_margin": margin(cand_row), "paired_margin_delta": delta,
                       "candidate_win": cand_row.get("candidate_result") == "win",
                       "baseline_win": base_row.get("candidate_result") == "win",
                       "errors": int(not base_row.get("ok")) + int(not cand_row.get("ok"))})
    opponent_summary = {name: {"games": len(values), "mean_paired_margin_delta": statistics.mean(values),
                                "median_paired_margin_delta": statistics.median(values),
                                "positive_pairs": sum(v > 0 for v in values),
                                "negative_pairs": sum(v < 0 for v in values),
                                "zero_pairs": sum(v == 0 for v in values)}
                        for name, values in sorted(by_opponent.items())}
    means = [v["mean_paired_margin_delta"] for v in opponent_summary.values()]
    valid_deltas = [p["paired_margin_delta"] for p in paired if p["paired_margin_delta"] is not None]
    return {"games": len(paired), "errors": sum(p["errors"] for p in paired),
            "mean_paired_margin_delta": statistics.mean(valid_deltas) if valid_deltas else None,
            "worst_opponent_mean_delta": min(means) if means else None,
            "opponents": opponent_summary, "paired_games": paired}


def run_tune() -> None:
    built = build_all()
    run_dir = OUT / "tune"
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"stage": "tune", "created_at": datetime.now(UTC).isoformat(),
                "baseline": str(BASELINE.relative_to(ROOT)), "baseline_sha256": sha(BASELINE),
                "seeds": TUNE_SEEDS, "opponents": TUNE_OPPONENTS,
                "opponent_sha256": opponent_hashes(TUNE_OPPONENTS),
                "seats": [0, 1], "configs": CONFIGS, "generated": built,
                "confirm_seeds_reserved": CONFIRM_SEEDS,
                "holdout_93000_93049_used": False}
    (run_dir / "plan.json").write_text(json.dumps(manifest, indent=2) + "\n")

    arms: dict[str, list[dict]] = {}
    arms["baseline"] = load_arm(run_dir, "baseline", BASELINE, TUNE_OPPONENTS, TUNE_SEEDS)
    analyses = {}
    for config in CONFIGS:
        arm = config["id"]
        candidate = ROOT / built[arm]["path"]
        arms[arm] = load_arm(run_dir, arm, candidate, TUNE_OPPONENTS, TUNE_SEEDS)
        analyses[arm] = arm_comparison(arms["baseline"], arms[arm])

    # Maximize the weakest opponent-group paired gain; use overall mean as the
    # tie-breaker. The predeclared parameter grid has no post-hoc expansions.
    selection = max(CONFIGS, key=lambda c: (
        analyses[c["id"]]["worst_opponent_mean_delta"],
        analyses[c["id"]]["mean_paired_margin_delta"],
        c["id"],
    ))
    result = {"plan": manifest, "analyses": analyses,
              "selected_config_id": selection["id"],
              "selection_rule": "maximum worst-opponent mean paired margin delta, then overall mean delta, then config ID",
              "interpretation": "Tuning only. Do not call this confirmation or release evidence."}
    (run_dir / "analysis.json").write_text(json.dumps(result, indent=2) + "\n")
    (run_dir / "selection.json").write_text(json.dumps({"config": selection,
        "candidate": built[selection["id"]], "selected_at": datetime.now(UTC).isoformat(),
        "confirmation_seeds": CONFIRM_SEEDS}, indent=2) + "\n")
    print(json.dumps({"selected_config_id": selection["id"],
                      "tuning": {k: {"mean_delta": round(v["mean_paired_margin_delta"], 1),
                                     "worst_opponent_delta": round(v["worst_opponent_mean_delta"], 1),
                                     "errors": v["errors"]} for k, v in analyses.items()}}, indent=2))


def run_confirm() -> None:
    selection_path = OUT / "tune" / "selection.json"
    if not selection_path.exists():
        raise SystemExit("Run tune first; confirmation needs a frozen tuning selection")
    selection = json.loads(selection_path.read_text())
    config_id = selection["config"]["id"]
    built = build_all()
    candidate = ROOT / built[config_id]["path"]
    if sha(candidate) != selection["candidate"]["sha256"]:
        raise SystemExit("Selected candidate bytes changed after tuning freeze")
    run_dir = OUT / "confirm"
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"stage": "one_time_confirmation", "created_at": datetime.now(UTC).isoformat(),
                "selected_config_id": config_id, "config": selection["config"],
                "baseline": str(BASELINE.relative_to(ROOT)), "baseline_sha256": sha(BASELINE),
                "candidate": str(candidate.relative_to(ROOT)), "candidate_sha256": sha(candidate),
                "seeds": CONFIRM_SEEDS, "opponents": CONFIRM_OPPONENTS,
                "opponent_sha256": opponent_hashes(CONFIRM_OPPONENTS),
                "seats": [0, 1], "holdout_93000_93049_used": False,
                "selection_frozen_at": selection["selected_at"]}
    if (run_dir / "plan.json").exists():
        old = json.loads((run_dir / "plan.json").read_text())
        if old.get("candidate_sha256") != manifest["candidate_sha256"] or old.get("seeds") != CONFIRM_SEEDS:
            raise SystemExit("A different confirmation plan already exists; refusing seed reuse")
    (run_dir / "plan.json").write_text(json.dumps(manifest, indent=2) + "\n")
    base_records = load_arm(run_dir, "baseline", BASELINE, CONFIRM_OPPONENTS, CONFIRM_SEEDS)
    candidate_records = load_arm(run_dir, config_id, candidate, CONFIRM_OPPONENTS, CONFIRM_SEEDS)
    comparison = arm_comparison(base_records, candidate_records)
    summary = {"plan": manifest, "comparison": comparison,
               "recommendation_gate": {
                   "zero_errors": comparison["errors"] == 0,
                   "positive_overall_paired_margin_gain": comparison["mean_paired_margin_delta"] > 0,
                   "at_least_two_tuning_groups_positive": sum(
                       row["mean_paired_margin_delta"] > 0 for row in
                       json.loads((OUT / "tune" / "analysis.json").read_text())["analyses"][config_id]["opponents"].values()) >= 2,
                   "all_eight_opponents_reported": len(comparison["opponents"]) == 8,
               },
               "interpretation": "Development confirmation only; not the reserved final candidate holdout."}
    (run_dir / "analysis.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({"selected_config_id": config_id,
                      "mean_paired_margin_delta": round(comparison["mean_paired_margin_delta"], 1),
                      "errors": comparison["errors"],
                      "per_opponent": {k: round(v["mean_paired_margin_delta"], 1)
                                       for k, v in comparison["opponents"].items()},
                      "gate": summary["recommendation_gate"]}, indent=2))


def main() -> None:
    os.chdir(ROOT)
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    if stage == "tune":
        run_tune()
    elif stage == "confirm":
        run_confirm()
    else:
        raise SystemExit("Usage: python -m experiments.v58_validation.search.run_search {tune|confirm}")


if __name__ == "__main__":
    main()

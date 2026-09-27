"""Phase-gated, hash-pinned local V68 tournament. No phase is run implicitly."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import shutil
import sys
import random
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from simulation.tournament import MatchSpec, Opponent, _game_id, _run_worker, build_summary, _write_flat_files

PLAN_PATH = ROOT / "experiments/v68_validation/plan.json"
PHASES = ("spent_gate", "smoke", "historical_gate", "stronger_panel", "broader_paired_panel")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def uncertainty(records):
    wins = sum(r.get("candidate_result") == "win" for r in records)
    n = len(records)
    try:
        from scipy.stats import beta
        interval = [0.0 if wins == 0 else float(beta.ppf(0.025, wins, n - wins + 1)),
                    1.0 if wins == n else float(beta.ppf(0.975, wins + 1, n - wins))]
    except ImportError:
        interval = None
    blocks = {}
    for r in records:
        blocks.setdefault(r["seed"], []).append(r)
    rng = random.Random(68001)
    keys = sorted(blocks)
    estimates = []
    if len(keys) >= 2:
        for _ in range(20000):
            sample = [rng.choice(keys) for _ in keys]
            sample_rows = [r for key in sample for r in blocks[key]]
            estimates.append(sum(r["candidate_result"] == "win" for r in sample_rows) / len(sample_rows))
        estimates.sort()
        bootstrap = [estimates[int(.025 * (len(estimates) - 1))], estimates[int(.975 * (len(estimates) - 1))]]
    else:
        bootstrap = None
    return {"wins": wins, "games": n, "clopper_pearson_95": interval,
            "seed_block_bootstrap_95": bootstrap, "bootstrap_replicates": 20000,
            "bootstrap_rng_seed": 68001}


def shop_schedule(record, phase_dir):
    replay_path = Path(record.get("replay_path") or "")
    if not replay_path.is_absolute():
        replay_path = phase_dir / replay_path
    if not replay_path.exists():
        return None
    replay = load_json(replay_path)
    schedules = []
    for seat in (0, 1):
        previous = None
        events = []
        for step_index, step in enumerate(replay.get("steps", [])):
            if seat >= len(step):
                continue
            obs = step[seat].get("observation") or {}
            town = obs.get("town") or {}
            unlocked = town.get("unlocked_shops")
            if unlocked is not None and unlocked != previous:
                events.append({"step": step_index, "day": obs.get("day"), "unlocked_shops": unlocked})
                previous = unlocked
        schedules.append(events)
    return schedules


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--phase", required=True, choices=PHASES)
    parser.add_argument("--timeout", type=float, default=180.0)
    args = parser.parse_args()
    candidate = args.candidate.resolve()
    if not candidate.is_file():
        parser.error(f"candidate file missing: {candidate}")
    if importlib.metadata.version("kaggle-environments") != "1.32.7":
        parser.error("expected kaggle-environments==1.32.7")
    plan = load_json(PLAN_PATH)
    candidate_hash = sha(candidate)

    # Re-read exact source pins before any execution. This fails closed if the
    # intended benchmark source has moved since this plan was reviewed.
    opponents = {}
    for group in ("historical_opponents", "strong_local_opponents"):
        for name, entry in plan[group].items():
            path = (ROOT / entry["path"]).resolve()
            if not path.is_file() or sha(path) != entry["sha256"]:
                parser.error(f"pinned opponent source mismatch: {name} ({path})")
            opponents[name] = (entry, path)

    phase_index = PHASES.index(args.phase)
    candidate_root = ROOT / "experiments/v68_validation/runs" / candidate_hash
    identity_path = candidate_root / "identity.json"
    candidate_root.mkdir(parents=True, exist_ok=True)
    identity = {"candidate_sha256": candidate_hash, "source_path": str(candidate), "plan_sha256": sha(PLAN_PATH)}
    if identity_path.exists() and load_json(identity_path) != identity:
        parser.error("candidate identity or validation plan differs from the frozen run")
    if not identity_path.exists():
        identity_path.write_text(json.dumps(identity, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        shutil.copyfile(candidate, candidate_root / "candidate.py")
        if sha(candidate_root / "candidate.py") != candidate_hash:
            parser.error("candidate snapshot hash mismatch")
    if sha(candidate_root / "candidate.py") != candidate_hash:
        parser.error("frozen candidate snapshot was modified")

    # Enforce predecessor gates. A phase folder must contain a passing analysis
    # with this same frozen candidate and the exact current plan.
    for prior in PHASES[:phase_index]:
        gate_path = candidate_root / prior / "analysis.json"
        if not gate_path.exists():
            parser.error(f"prerequisite phase missing: {prior}")
        gate = load_json(gate_path)
        if not gate.get("gate_passed") or gate.get("candidate_sha256") != candidate_hash:
            parser.error(f"prerequisite phase did not pass for this candidate: {prior}")

    phase = plan["stages"][args.phase]
    names = phase["opponents"]
    phase_dir = candidate_root / args.phase
    phase_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "phase": args.phase,
        "candidate_sha256": candidate_hash,
        "plan_sha256": sha(PLAN_PATH),
        "engine_version": "1.32.7",
        "seeds": phase["seeds"],
        "opponents": {name: {"path": str(opponents[name][1]), "sha256": opponents[name][0]["sha256"]} for name in names},
        "seat_orders": ["candidate-seat-0", "candidate-seat-1"],
        "timeout_seconds": args.timeout,
    }
    manifest_path = phase_dir / "manifest.json"
    if manifest_path.exists() and load_json(manifest_path) != manifest:
        parser.error("existing phase manifest differs; refusing to mix runs")
    if not manifest_path.exists():
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    records = []
    for name in names:
        _, opponent_path = opponents[name]
        opponent = Opponent(name, opponent_path)
        for seed in phase["seeds"]:
            for swapped in (False, True):
                spec = MatchSpec(opponent, int(seed), swapped, 0)
                game_id = _game_id(spec)
                result_path = phase_dir / "games" / f"{game_id}.json"
                replay_path = phase_dir / "replays" / f"{game_id}.json"
                record = None
                if result_path.exists():
                    prior_record = load_json(result_path)
                    agent_hashes = [a.get("sha256") for a in prior_record.get("agents", [])]
                    expected_seats = [opponent_path, candidate_root / "candidate.py"] if swapped else [candidate_root / "candidate.py", opponent_path]
                    if agent_hashes == [sha(p) for p in expected_seats] and prior_record.get("seed") == seed:
                        record = prior_record
                if record is None:
                    record = _run_worker(candidate_root / "candidate.py", spec, phase_dir, args.timeout, "all")
                record["shop_unlock_schedule_by_seat"] = shop_schedule(record, phase_dir)
                records.append(record)
                # Persist after every completed game for crash-safe resumption.
                _write_flat_files(phase_dir, records)

    summary = build_summary(records)
    expected_games = phase["games"]
    clean = len(records) == expected_games and all(
        r.get("ok") and r.get("candidate_status") == "DONE" and r.get("opponent_status") == "DONE"
        and not r.get("candidate_error") and not r.get("opponent_error")
        and not r.get("infrastructure_error") and not r.get("timed_out")
        for r in records
    )
    by_opp = summary.get("by_opponent", {})
    by_seat = summary.get("by_candidate_seat", {})
    by_opp_seat = {}
    for row in records:
        key = (row["opponent"], str(row["candidate_seat"]))
        by_opp_seat.setdefault(key, []).append(row)
    opp_seat_rates = {f"{opp}/seat{seat}": sum(r["candidate_result"] == "win" for r in rows) / len(rows)
                      for (opp, seat), rows in sorted(by_opp_seat.items())}
    if args.phase == "spent_gate":
        passed = clean and all(by_opp.get(n, {}).get("wins") == 2 for n in names)
    elif args.phase == "smoke":
        passed = clean
    elif args.phase == "historical_gate":
        passed = clean and all(by_opp.get(n, {}).get("wins") == 10 for n in names)
    elif args.phase == "stronger_panel":
        interval = uncertainty(records)["seed_block_bootstrap_95"]
        passed = clean and summary["win_rate"] >= 0.95 and all(v["win_rate"] >= 0.90 for v in by_opp.values()) and all(v >= 0.90 for v in opp_seat_rates.values()) and interval is not None and interval[0] >= 0.90
    else:
        interval = uncertainty(records)["seed_block_bootstrap_95"]
        passed = clean and summary["win_rate"] > 0.95 and all(v["win_rate"] >= 0.90 for v in by_opp.values()) and all(v >= 0.90 for v in opp_seat_rates.values()) and interval is not None and interval[0] >= 0.90
    report = {"phase": args.phase, "candidate_sha256": candidate_hash, "plan_sha256": sha(PLAN_PATH), "expected_games": expected_games, "actual_games": len(records), "clean": clean, "gate_passed": bool(passed), "gate_text": phase["gate"], "uncertainty": uncertainty(records), "per_opponent_seat_win_rates": opp_seat_rates, "summary": summary, "games": records}
    (phase_dir / "analysis.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (phase_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("phase", "candidate_sha256", "actual_games", "clean", "gate_passed", "summary")}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())

"""Analyze a completed/resumed v59 phase with exact errors and clustered uncertainty."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "experiments/v59_validation/plan.json"
BOOTSTRAP_REPLICATES = 20_000
BOOTSTRAP_SEED = 59001


def cp_interval(wins: int, total: int) -> list[float] | None:
    if not total:
        return None
    from scipy.stats import beta
    alpha = 0.05
    return [0.0 if wins == 0 else float(beta.ppf(alpha / 2, wins, total - wins + 1)),
            1.0 if wins == total else float(beta.ppf(1 - alpha / 2, wins + 1, total - wins))]


def rate_stats(rows: list[dict]) -> dict:
    n = len(rows)
    wins = sum(row["candidate_result"] == "win" for row in rows)
    draws = sum(row["candidate_result"] == "draw" for row in rows)
    margins = [row["coin_difference_candidate"] for row in rows if row.get("coin_difference_candidate") is not None]
    return {"games": n, "wins": wins, "losses": sum(row["candidate_result"] == "loss" for row in rows),
            "draws": draws, "strict_win_rate": wins / n if n else None,
            "score_rate": (wins + 0.5 * draws) / n if n else None,
            "clopper_pearson_95": cp_interval(wins, n),
            "mean_margin": statistics.fmean(margins) if margins else None,
            "median_margin": statistics.median(margins) if margins else None}


def clustered_interval(rows: list[dict], key: str | None) -> list[float] | None:
    clusters = defaultdict(list)
    for row in rows:
        cluster = (row["seed"] if key is None else (row["seed"], row[key]))
        clusters[cluster].append(int(row["candidate_result"] == "win"))
    values = [statistics.fmean(items) for items in clusters.values()]
    if len(values) < 2:
        return None
    rng = random.Random(BOOTSTRAP_SEED)
    n = len(values)
    draws = sorted(statistics.fmean(rng.choice(values) for _ in range(n)) for _ in range(BOOTSTRAP_REPLICATES))
    return [draws[int(0.025 * BOOTSTRAP_REPLICATES)], draws[int(0.975 * BOOTSTRAP_REPLICATES) - 1]]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--phase", required=True, choices=("smoke", "historical_gate", "stronger_dev_gate", "paired_pre_final"))
    args = parser.parse_args()
    candidate_hash = hashlib.sha256(args.candidate.resolve().read_bytes()).hexdigest()
    out = ROOT / "experiments/v59_validation/runs" / candidate_hash / args.phase
    manifest = json.loads((out / "manifest.json").read_text())
    if manifest["candidate_sha256"] != candidate_hash:
        raise SystemExit("Candidate hash differs from run manifest")
    expected = len(manifest["seeds"]) * len(manifest["opponents"]) * 2
    rows = json.loads((out / "games.json").read_text())
    if len(rows) != expected:
        raise SystemExit(f"Incomplete phase: expected {expected} records, found {len(rows)}")
    for row in rows:
        if row.get("candidate_sha256") != candidate_hash or row.get("engine") != manifest["engine"]:
            raise SystemExit(f"Provenance mismatch in {row.get('game_id')}")
        if row.get("opponent_sha256") != manifest["opponents"][row["opponent"]]["sha256"]:
            raise SystemExit(f"Opponent provenance mismatch in {row.get('game_id')}")

    opponent_rows = defaultdict(list)
    seat_rows = defaultdict(list)
    shop_first_rows = defaultdict(list)
    shop_signature_rows = defaultdict(list)
    for row in rows:
        opponent_rows[row["opponent"]].append(row)
        seat_rows[str(row["candidate_seat"])].append(row)
        first = row.get("shop_unlock_sequence") or []
        shop_first_rows[first[0]["shop"] if first else "NO_SHOP"].append(row)
        sig = ",".join(sorted(set(row.get("shop_signature") or []))) or "NO_SHOP"
        shop_signature_rows[sig].append(row)

    errors = []
    for row in rows:
        incomplete = row.get("candidate_status") != "DONE" or row.get("opponent_status") != "DONE"
        row["incomplete_game"] = incomplete
        if row.get("candidate_error") or row.get("opponent_error") or row.get("infrastructure_error") or row.get("timed_out") or not row.get("ok") or incomplete:
            errors.append({"game_id": row["game_id"], "opponent": row["opponent"], "seed": row["seed"],
                           "candidate_seat": row["candidate_seat"], "candidate_status": row.get("candidate_status"),
                           "opponent_status": row.get("opponent_status"), "candidate_error": row.get("candidate_error"),
                           "opponent_error": row.get("opponent_error"), "infrastructure_error": row.get("infrastructure_error"),
                           "timed_out": row.get("timed_out"), "incomplete_game": incomplete,
                           "ok": row.get("ok"), "error": row.get("error")})

    overall = rate_stats(rows)
    overall["seed_block_bootstrap_95"] = clustered_interval(rows, None)
    by_opponent = {key: rate_stats(value) for key, value in sorted(opponent_rows.items())}
    by_seat = {key: rate_stats(value) for key, value in sorted(seat_rows.items())}
    for name, subset in opponent_rows.items():
        by_opponent[name]["seed_block_bootstrap_95"] = clustered_interval(subset, None)
    for seat, subset in seat_rows.items():
        by_seat[seat]["seed_block_bootstrap_95"] = clustered_interval(subset, "candidate_seat")

    zero_errors = not errors
    historical = {f"v{i}" for i in (48, 50, 51, 52, 53, 54, 55, 56)}
    if args.phase == "smoke":
        gate = zero_errors and all(r.get("candidate_status") == "DONE" and r.get("opponent_status") == "DONE" for r in rows)
        gate_name = "smoke_integrity"
    elif args.phase == "historical_gate":
        gate = zero_errors and historical.issubset(by_opponent) and all(by_opponent[n]["games"] == 10 and by_opponent[n]["wins"] == 10 for n in historical)
        gate_name = "10_of_10_against_each_historical_agent"
    else:
        threshold = 0.95
        gate = (zero_errors and overall["strict_win_rate"] >= threshold and
                all(item["strict_win_rate"] >= 0.90 for item in by_opponent.values()) and
                all(item["strict_win_rate"] >= 0.90 for item in by_seat.values()) and
                overall["seed_block_bootstrap_95"] is not None and overall["seed_block_bootstrap_95"][0] >= 0.90)
        if args.phase == "paired_pre_final":
            gate = gate and overall["strict_win_rate"] > threshold
        gate_name = "robust_stronger_panel"

    report = {
        "phase": args.phase, "candidate_sha256": candidate_hash, "engine": manifest["engine"],
        "games": len(rows), "expected_games": expected, "gate_name": gate_name, "gate_pass": bool(gate),
        "interpretation": "Local finite-panel evidence only. It does not establish future win probability or Kaggle leaderboard rank.",
        "uncertainty_method": {"exact": "two-sided 95% Clopper-Pearson", "bootstrap": "percentile bootstrap resampling whole seed blocks", "replicates": BOOTSTRAP_REPLICATES, "rng_seed": BOOTSTRAP_SEED},
        "overall": overall, "by_opponent": by_opponent, "by_candidate_seat": by_seat,
        "errors": {"count": len(errors), "incomplete_games": sum(row["incomplete_game"] for row in rows), "records": errors},
        "shop_first_unlock": {key: rate_stats(value) for key, value in sorted(shop_first_rows.items())},
        "shop_signature_exploratory": {key: rate_stats(value) for key, value in sorted(shop_signature_rows.items())},
        "shop_schedules": [{"game_id": row["game_id"], "opponent": row["opponent"], "seed": row["seed"],
                            "candidate_seat": row["candidate_seat"], "unlock_sequence": row.get("shop_unlock_sequence", []),
                            "signature": row.get("shop_signature", [])} for row in rows]
    }
    (out / "analysis.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"phase": args.phase, "candidate_sha256": candidate_hash, "gate_pass": gate,
                      "overall": overall, "by_opponent": by_opponent, "by_candidate_seat": by_seat,
                      "error_count": len(errors)}, indent=2))
    return 0 if gate else 1


if __name__ == "__main__":
    raise SystemExit(main())

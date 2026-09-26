"""Summarize the frozen v58 screen, including the requested 10-game sweep."""
from __future__ import annotations

import json
import random
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "experiments/runs/v58_validation_baseline"
PLAN = ROOT / "experiments/v58_validation/plan.json"


def main() -> None:
    plan = json.loads(PLAN.read_text())
    records = json.loads((RUN / "games.json").read_text())
    by_opp = defaultdict(list)
    by_seat = defaultdict(list)
    by_seed = defaultdict(list)
    for row in records:
        win = int(row.get("winner_seat") == row.get("candidate_seat"))
        draw = int(row.get("winner_seat") is None and row.get("ok"))
        error = not row.get("ok")
        item = {"win": win, "draw": draw, "error": error,
                "margin": ((row["final_coins"][row["candidate_seat"]] -
                            row["final_coins"][row["opponent_seat"]])
                           if row.get("final_coins") and all(x is not None for x in row["final_coins"]) else None)}
        by_opp[row["opponent"]].append(item)
        by_seat[row["candidate_seat"]].append(item)
        by_seed[row["seed"]].append(item)

    total_games = len(records)
    wins = sum(x["win"] for rows in by_opp.values() for x in rows)
    errors = sum(x["error"] for rows in by_opp.values() for x in rows)
    seed_ids = sorted(by_seed)
    rng = random.Random(58001)
    boot = []
    for _ in range(20000):
        draw_seeds = [rng.choice(seed_ids) for _ in seed_ids]
        values = [item["win"] for seed in draw_seeds for item in by_seed[seed]]
        boot.append(sum(values) / len(values))
    boot.sort()
    overall = wins / total_games if total_games else 0
    rows = {}
    for name, items in sorted(by_opp.items()):
        w = sum(x["win"] for x in items)
        rows[name] = {"wins": w, "losses": len(items)-w-sum(x["draw"] for x in items),
                      "draws": sum(x["draw"] for x in items), "errors": sum(x["error"] for x in items),
                      "win_rate": w/len(items) if items else None,
                      "mean_margin": statistics.mean([x["margin"] for x in items if x["margin"] is not None]) if items else None}
    historic = ["v48", "v50", "v51", "v52", "v53", "v54", "v55", "v56"]
    sweep = all(rows.get(name, {}).get("wins") == 10 and rows.get(name, {}).get("errors") == 0
                for name in historic)
    summary = {
        "games": total_games, "wins": wins, "strict_win_rate": overall,
        "errors": errors, "requested_100_percent_eight_agent_sweep_pass": sweep,
        "historical_sweep": {name: rows.get(name) for name in historic},
        "per_opponent": rows,
        "per_seat": {str(seat): {"games": len(items), "wins": sum(x["win"] for x in items),
                                 "win_rate": sum(x["win"] for x in items)/len(items)}
                     for seat, items in sorted(by_seat.items())},
        "seed_block_bootstrap_95_percent": {"lower": boot[int(0.025*len(boot))], "upper": boot[int(0.975*len(boot))],
                                            "seed_blocks": len(seed_ids), "replicates": len(boot), "rng_seed": 58001},
        "broader_95_percent_readiness_gate_pass": errors == 0 and overall >= .95 and
            all(v["win_rate"] >= .90 for v in rows.values()) and
            all(v["win_rate"] >= .90 for v in summary_seat_values(by_seat).values()) and boot[int(.025*len(boot))] >= .90,
        "interpretation": "Finite local panel only; not proof of universal 100% performance or top-ten rank."
    }
    (RUN / "analysis.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


def summary_seat_values(by_seat):
    return {seat: sum(x["win"] for x in rows)/len(rows) for seat, rows in by_seat.items()}


if __name__ == "__main__":
    main()

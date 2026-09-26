"""Derive seed/seat matchup strata and shop regimes from frozen v58 baseline records."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from kaggle_environments.envs.kaggriculture.kaggriculture import SHOPS

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "experiments/runs/v58_validation_baseline"
OPPONENTS = ["v48", "v50", "v51", "v52", "v53", "v55"]


def main() -> None:
    records = json.loads((RUN / "games.json").read_text())
    outcomes = {}
    for opponent in OPPONENTS:
        outcomes[opponent] = {}
        for seed in sorted({r["seed"] for r in records}):
            outcomes[opponent][str(seed)] = {}
            for row in sorted(
                (r for r in records if r["opponent"] == opponent and r["seed"] == seed),
                key=lambda r: r["candidate_seat"],
            ):
                seat = row["candidate_seat"]
                margin = row["final_coins"][seat] - row["final_coins"][row["opponent_seat"]]
                outcomes[opponent][str(seed)][str(seat)] = {
                    "result": row["candidate_result"],
                    "margin": margin,
                    "candidate_final_coins": row["final_coins"][seat],
                    "opponent_final_coins": row["final_coins"][row["opponent_seat"]],
                    "replay_sha256": row.get("replay_sha256"),
                }

    duplicate_replays = {}
    for left, right in (("v50", "v52"), ("v53", "v55")):
        pairs = []
        for seed in sorted({r["seed"] for r in records}):
            for seat in (0, 1):
                a = next(r for r in records if r["opponent"] == left and r["seed"] == seed and r["candidate_seat"] == seat)
                b = next(r for r in records if r["opponent"] == right and r["seed"] == seed and r["candidate_seat"] == seat)
                pairs.append({"seed": seed, "candidate_seat": seat,
                              "same_normalized_replay_sha256": a["replay_sha256"] == b["replay_sha256"]})
        duplicate_replays[f"{left}_vs_{right}"] = {
            "comparisons": len(pairs), "identical_replays": sum(p["same_normalized_replay_sha256"] for p in pairs),
            "pairs": pairs,
        }

    shops = {}
    for replay_path in sorted((RUN / "replays").glob("*.json")):
        replay = json.loads(replay_path.read_text())
        by_day = {}
        for step in replay["steps"]:
            obs = step[0].get("observation") or {}
            if "day" in obs:
                by_day.setdefault(obs["day"], obs.get("town", {}).get("unlocked_shops", []))
        days = sorted(by_day)
        unlocks = []
        previous: list[str] = []
        for day in days:
            current = by_day[day]
            if len(current) > len(previous):
                for index in range(len(previous), len(current)):
                    unlocks.append({"day_observed": day, "shop": current[index]})
            previous = current
        demand = Counter(product for event in unlocks for product in SHOPS[event["shop"]])
        shops[replay_path.stem] = {
            "seed": replay.get("configuration", {}).get("seed"),
            "unlocks": unlocks,
            "unlock_count": len(unlocks),
            "unique_shop_names": sorted({event["shop"] for event in unlocks}),
            "products_demanded_per_shop_instance_per_tick": dict(sorted(demand.items())),
            "final_unlocked_shops": by_day[days[-1]] if days else [],
            "observed_day_range": [days[0], days[-1]] if days else None,
            "normalized_replay_sha256": hashlib.sha256(
                json.dumps({k: v for k, v in replay.items() if k != "id"}, sort_keys=True,
                            separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
            ).hexdigest(),
        }

    result = {
        "source": "experiments/runs/v58_validation_baseline",
        "opponents": OPPONENTS,
        "seed_seat_outcomes": outcomes,
        "duplicate_behavior_checks": duplicate_replays,
        "shop_regimes": shops,
        "shop_replay_coverage_note": "Shop classifications are limited to retained replay files; no regime is imputed for missing replays.",
    }
    out = RUN / "stratification.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(out), "replays_classified": len(shops),
                      "duplicate_behavior": {k: f"{v['identical_replays']}/{v['comparisons']} identical"
                                             for k, v in duplicate_replays.items()}}, indent=2))


if __name__ == "__main__":
    main()

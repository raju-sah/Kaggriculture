"""Evaluate day-gate candidates on paired scan records, one row per game.

`analysis/pair_scan.py` collects compact per-day public signals. This module
turns those records into gate evidence at the granularity that actually
matters: one row per played game, not per seed, because an agent decides
inside a single game.

For every candidate predicate it reports the triggered subgroup (the games
where the gate would fire and the candidate program would run), the skipped
subgroup (where champion behaviour must be byte-identical, so the paired
difference is the candidate's own error), Wilson intervals, and the oracle
regret of the trigger decision.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Callable

from analysis.pair_scan import _signal_for, SHOP_PRODUCTS

MILK_SHOPS = ("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP")
STRAW_SHOPS = tuple(shop for shop, products in SHOP_PRODUCTS.items() if "STRAWBERRY" in products)
EGG_SHOPS = ("BAKERY", "BRUNCH_SPOT")


def wilson(wins: int, games: int, z: float = 1.96) -> list[float] | None:
    if games == 0:
        return None
    phat = wins / games
    denominator = 1 + z * z / games
    center = (phat + z * z / (2 * games)) / denominator
    margin = z * math.sqrt(phat * (1 - phat) / games + z * z / (4 * games * games)) / denominator
    return [max(0.0, center - margin), min(1.0, center + margin)]


GATES: tuple[tuple[str, Callable[[dict[str, Any]], bool]], ...] = (
    ("d3_milk", lambda s: s.get("d3_milk")),
    ("d3_straw", lambda s: s.get("d3_straw")),
    ("d3_wool", lambda s: s.get("d3_wool")),
    ("berry6>=1", lambda s: s["straw_shops6"] >= 1),
    ("berry6>=2", lambda s: s["straw_shops6"] >= 2),
    ("milk6>=1", lambda s: s["milk6"] >= 1),
    ("milk6>=2", lambda s: s["milk6"] >= 2),
    ("milk9>=1", lambda s: s["milk9"] >= 1),
    ("yarn6>=1", lambda s: s["yarn6"] >= 1),
    ("egg6>=1", lambda s: s["egg6"] >= 1),
    ("animal6>=2", lambda s: s["animal6"] >= 2),
    ("animal6>=3", lambda s: s["animal6"] >= 3),
    ("animal9>=3", lambda s: s["animal9"] >= 3),
    ("milk6_or_yarn6", lambda s: s["milk6"] >= 1 or s["yarn6"] >= 1),
    ("animal6>=1", lambda s: s["animal6"] >= 1),
    ("milk6_and_animal9>=2", lambda s: s["milk6"] >= 1 and s["animal9"] >= 2),
)

def load_games(directories: list[Path], view: str) -> list[dict[str, Any]]:
    rows = []
    for directory in directories:
        for path in sorted((directory / "games").glob("*.json")):
            record = json.loads(path.read_text(encoding="utf-8"))
            if not record.get("ok"):
                rows.append({"source": directory.name, "seed": record["seed"], "seat": None,
                             "diff": None, "signal": None, "failed": True})
                continue
            seat = record["candidate_seat"]
            candidate = record["final_coins"][seat]
            opponent = record["final_coins"][1 - seat]
            if candidate is None or opponent is None:
                continue
            signal = _signal_for(record, seat if view == "a" else 1 - seat)
            if not signal:
                continue
            rows.append(
                {
                    "source": directory.name,
                    "seed": record["seed"],
                    "seat": seat,
                    "diff": candidate - opponent,
                    "signal": signal,
                    "failed": False,
                }
            )
    return rows


def _stats(diffs: list[float]) -> dict[str, Any]:
    if not diffs:
        return {"games": 0, "mean": None, "median": None, "winner_rate": None,
                "winner_rate_wilson_95": None, "min": None, "max": None, "total": None}
    ordered = sorted(diffs)
    middle = len(ordered) // 2
    median = ordered[middle] if len(ordered) % 2 else (ordered[middle - 1] + ordered[middle]) / 2
    wins = sum(1 for value in diffs if value > 0)
    return {
        "games": len(diffs),
        "mean": sum(diffs) / len(diffs),
        "median": median,
        "winner_rate": wins / len(diffs),
        "winner_rate_wilson_95": wilson(wins, len(diffs)),
        "min": ordered[0],
        "max": ordered[-1],
        "total": sum(diffs),
    }


def evaluate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    usable = [row for row in rows if row["diff"] is not None]
    oracle = sum(max(0.0, row["diff"]) for row in usable)
    results = []
    for name, predicate in GATES:
        triggered = [row["diff"] for row in usable if predicate(row["signal"])]
        skipped = [row["diff"] for row in usable if not predicate(row["signal"])]
        results.append(
            {
                "gate": name,
                "triggered": _stats(triggered),
                "skipped": _stats(skipped),
                "gate_value": sum(triggered),
                "regret_vs_oracle": oracle - sum(triggered),
            }
        )
    return {
        "games": len(usable),
        "failures": sum(1 for row in rows if row["failed"]),
        "oracle_value": oracle,
        "candidate_null_value": sum(row["diff"] for row in usable),
        "gates": results,
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directories", nargs="+", type=Path)
    parser.add_argument("--view", choices=("a", "b"), default="b",
                        help="whose day-6 view the gate reads (b = the champion's own view)")
    parser.add_argument("--rows", action="store_true", help="print one row per game")
    args = parser.parse_args()

    rows = load_games(args.directories, args.view)
    if args.rows:
        for row in sorted(rows, key=lambda item: (item["seed"], str(item["seat"]))):
            signal = row["signal"] or {}
            print(
                f"{row['seed']:>6} seat{row['seat']} diff={row['diff']:+9.0f} "
                f"milk6={signal.get('milk6')} milk9={signal.get('milk9')} "
                f"yarn6={signal.get('yarn6')} egg6={signal.get('egg6')} "
                f"animal9={signal.get('animal9')} pM6={signal.get('price_milk6')}"
            )
    report = evaluate(rows)
    print(json.dumps(report, indent=2, sort_keys=True))
    print(
        "\nnull (candidate never gated) value: {:+.0f} over {} games; oracle {:.0f}".format(
            report["candidate_null_value"], report["games"], report["oracle_value"]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Print compact strategy profiles from Kaggle simulation replay JSON files.

The profiler intentionally records public actions and each agent's own observed
farm/private state only. It is a development-time analysis tool; it is not part
of the submitted agent.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import Any


SNAPSHOT_DAYS = (0, 3, 5, 6, 9, 12, 15, 20, 29)


def _farm_counts(farm: dict[str, Any]) -> tuple[Counter[str], Counter[str]]:
    animals: Counter[str] = Counter()
    crops: Counter[str] = Counter()
    for row in farm["tiles"]:
        for tile in row:
            if not isinstance(tile, dict):
                continue
            if animal := tile.get("animal"):
                animals[animal] += 1
            if crop := tile.get("crop"):
                crops[crop] += 1
    return animals, crops


def _market_totals(steps: list[list[dict[str, Any]]], seat: int) -> Counter[tuple[str, str]]:
    totals: Counter[tuple[str, str]] = Counter()
    for step in steps:
        action = step[seat].get("action") or {}
        for order in action.get("market") or []:
            if not order:
                continue
            quantity = order[2] if len(order) > 2 and isinstance(order[2], (int, float)) else 1
            totals[(str(order[0]), str(order[1]) if len(order) > 1 else "")] += int(quantity)
    return totals


def profile(path: Path) -> dict[str, Any]:
    replay = json.loads(path.read_text())
    steps = replay["steps"]
    result: dict[str, Any] = {
        "episode_id": replay.get("info", {}).get("EpisodeId"),
        "seed": replay.get("info", {}).get("seed"),
        "module_version": replay.get("module_version"),
        "agents": [],
    }
    names = replay.get("info", {}).get("TeamNames", [])
    for seat in range(len(steps[0])):
        totals = _market_totals(steps, seat)
        snapshots = []
        for day in SNAPSHOT_DAYS:
            index = min(day * 24 + 23, len(steps) - 1)
            observation = steps[index][seat]["observation"]
            farm = observation["farms"][seat]
            animals, crops = _farm_counts(farm)
            snapshots.append(
                {
                    "day": day,
                    "money": round(float(farm["money"]), 2),
                    "hands": len(farm["hands"]),
                    "land_quadrants": len(farm["unlocked_quadrants"]),
                    "animals": dict(sorted(animals.items())),
                    "crops": dict(sorted(crops.items())),
                }
            )
        result["agents"].append(
            {
                "seat": seat,
                "name": names[seat] if seat < len(names) else f"seat-{seat}",
                "reward": replay.get("rewards", [None] * len(steps[0]))[seat],
                "snapshots": snapshots,
                "animal_buys": {
                    item: quantity
                    for (operation, item), quantity in sorted(totals.items())
                    if operation == "BUY_ANIMAL"
                },
                "feed_bought": totals[("BUY_PRODUCT", "WHEAT")],
                "land_orders": totals[("BUY_LAND", "")],
                "sales": {
                    item: quantity
                    for (operation, item), quantity in sorted(totals.items())
                    if operation == "SELL"
                },
                "seed_buys": {
                    item: quantity
                    for (operation, item), quantity in sorted(totals.items())
                    if operation == "BUY_SEED"
                },
            }
        )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("replays", nargs="+", type=Path)
    parser.add_argument("--indent", type=int, default=2)
    args = parser.parse_args()
    print(json.dumps([profile(path) for path in args.replays], indent=args.indent, sort_keys=True))


if __name__ == "__main__":
    main()

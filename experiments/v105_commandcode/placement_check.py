"""V105 Phase 0: does the day-6 route supply TWO sheep placements?

V105 wants to convert BOTH bought sheep into cows. That needs two cow pickups
and two cow placements on the same existing day-6 route, with no extra worker
time. The V104 feasibility run showed seed 160001's day-6 route carries only
ONE sheep pickup and ONE sheep place for a cohort of TWO -- which would leave a
second cow unplaced.

This counts, from ALREADY-SAVED replays only, how many sheep pickups and places
each day-6 route actually supplies, and whether free pastures exist. No matches
are run.

    .venv/bin/python experiments/v105_commandcode/placement_check.py
"""

from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def day6_counts(game: dict, seat: int) -> dict:
    steps = game["steps"]
    buy_qty = 0
    pickups: list[int] = []
    places: list[int] = []
    cow_pickups = 0
    cow_places = 0
    for frame in range(1, len(steps)):
        obs = steps[frame - 1][seat]["observation"]
        act = steps[frame][seat].get("action") or {}
        if int(obs.get("day", 0)) != 6:
            continue
        for order in (act.get("market") or []):
            if (isinstance(order, list) and len(order) >= 3 and order[0] == "BUY_ANIMAL"
                    and order[1] == "SHEEP"):
                buy_qty += int(order[2])
        units = [act.get("farmer", ["PASS"]), *(act.get("hands") or [])]
        for a in units:
            if not isinstance(a, list) or len(a) < 2:
                continue
            if a[0] == "PICKUP" and a[1] == "SHEEP":
                pickups.append(int(obs.get("hour", 0)))
            if a[0] == "PLACE" and a[1] == "SHEEP":
                places.append(int(obs.get("hour", 0)))
            if a[0] == "PICKUP" and a[1] == "COW":
                cow_pickups += 1
            if a[0] == "PLACE" and a[1] == "COW":
                cow_places += 1
    return {"buy_qty": buy_qty, "pickups": pickups, "places": places,
            "cow_pickups": cow_pickups, "cow_places": cow_places}


def main() -> int:
    pats = [
        ROOT / "experiments/v101_commandcode/lifecycle_replays/seed_*.json",
        ROOT / "experiments/v101_commandcode/micro_replays/candidate_seed_*.json",
    ]
    files: list[Path] = []
    for p in pats:
        files += sorted(Path(x) for x in glob.glob(str(p)))
    if not files:
        print("no spent replays found", file=sys.stderr)
        return 2

    print(f"reading {len(files)} spent replays (no matches run)\n")
    print(f"{'file':>16} {'buy':>4} {'#pick':>6} {'#place':>7} {'#cowP':>6} {'#cowPl':>7}  verdict")
    two_ok = 0
    total = 0
    for f in files:
        try:
            game = json.loads(f.read_text())
        except Exception:
            continue
        # the V101 files already rewrote one sheep->cow, so look at the raw tape
        c = day6_counts(game, 0)
        if c["buy_qty"] == 0:
            continue
        total += 1
        # V105 needs >=2 pickups AND >=2 places on day 6
        enough = len(c["pickups"]) >= 2 and len(c["places"]) >= 2
        two_ok += enough
        name = f.name.split("seed_")[-1].replace(".json", "")
        print(f"{name:>16} {c['buy_qty']:>4} {len(c['pickups']):>6} {len(c['places']):>7} "
              f"{c['cow_pickups']:>6} {c['cow_places']:>7}  "
              f"{'OK' if enough else 'INSUFFICIENT'}")

    print(f"\n{two_ok}/{total} spent replays supply two sheep pickups AND two places on day 6.")
    if two_ok == 0:
        print("=> V105 (replace BOTH sheep) is INFEASIBLE on the existing day-6 route:")
        print("   the second cow would be unplaced on every seed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

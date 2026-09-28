"""V105 pre-match gate: are BOTH cows placed, and are they later collected/sold?

Run on ONE spent seed first. Reports, per seat:
  * how many day-6 COW buys / pickups / places actually happened,
  * whether two DISTINCT pasture tiles ended the episode holding the two new
    cows (i.e. the second cow was not left in the shed),
  * whether the second cow was later collected and sold (HARVEST / shed pickup),
  * whether the base one-cow candidate does the same thing with exactly one cow,
    so the two are directly comparable.

Exits non-zero if the second cow is unplaced on either seat, because an unplaced
cow is the exact failure mode this experiment exists to avoid.

    .venv/bin/python experiments/v105_commandcode/verify_pair.py --seed 160001
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

CAND = HERE / "candidate.py"
BASE = ROOT / "experiments/v101_adaptive_swap/candidate_milk_sink_no_yarn.py"


def analyse(game: dict, seat: int) -> dict:
    steps = game["steps"]
    buys = pickups = places = 0
    cow_tiles: set[tuple[int, int]] = set()
    harvested = 0
    for frame in range(1, len(steps)):
        obs = steps[frame - 1][seat]["observation"]
        act = steps[frame][seat].get("action") or {}
        day = int(obs.get("day", 0))
        farm = obs["farms"][seat]
        units = [act.get("farmer", ["PASS"]), *(act.get("hands") or [])]
        positions = [farm.get("farmer"), *list(farm.get("hands") or [])]
        for order in (act.get("market") or []):
            if (isinstance(order, list) and len(order) >= 3 and order[0] == "BUY_ANIMAL"
                    and order[1] == "COW" and day == 6):
                buys += int(order[2])
        for ui, a in enumerate(units):
            if not isinstance(a, list) or len(a) < 2:
                continue
            if day == 6 and a[0] == "PICKUP" and a[1] == "COW":
                pickups += 1
            if day == 6 and a[0] == "PLACE" and a[1] == "COW":
                places += 1
                pos = positions[ui] if ui < len(positions) and positions[ui] else None
                if pos:
                    cow_tiles.add(tuple(pos))
            if a[0] == "HARVEST" and cow_tiles:
                pos = tuple(positions[ui]) if ui < len(positions) and positions[ui] else None
                if pos in cow_tiles:
                    harvested += 1

    final = steps[-1][seat]["observation"]["farms"][seat]
    live = []
    for y, row in enumerate(final["tiles"]):
        for x, t in enumerate(row):
            if isinstance(t, dict) and t.get("animal") == "COW":
                live.append((x, y))
    return {"buys": buys, "pickups": pickups, "places": places,
            "placed_tiles": sorted(cow_tiles), "live_cows": len(live),
            "new_cows_live": len([c for c in cow_tiles if c in live]),
            "harvests": harvested}


def run(agent: Path, seed: int):
    from kaggle_environments import make
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=True)
    env.run([str(agent), str(BASE)])
    return env.toJSON(), env.steps[-1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=160001)
    args = ap.parse_args()

    g, final = run(CAND, args.seed)
    gb, finalb = run(BASE, args.seed)
    ok = True
    for seat in (0, 1):
        c = analyse(g, seat)
        b = analyse(gb, seat)
        print(f"seed {args.seed} seat {seat}")
        print(f"  V105 : buys {c['buys']} pickups {c['pickups']} places {c['places']} "
              f"placed_tiles {c['placed_tiles']} new_cows_live {c['new_cows_live']} "
              f"harvests {c['harvests']}")
        print(f"  base : buys {b['buys']} pickups {b['pickups']} places {b['places']} "
              f"placed_tiles {b['placed_tiles']} new_cows_live {b['new_cows_live']} "
              f"harvests {b['harvests']}")
        if c["buys"] >= 2:
            if c["places"] < 2:
                print(f"  FAIL second cow unplaced on seat {seat}")
                ok = False
            if c["new_cows_live"] < 2:
                print(f"  FAIL second cow not alive at end on seat {seat}")
                ok = False
    print("\nVERDICT:", "both cows placed and retained" if ok else "STOP - second cow unplaced")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

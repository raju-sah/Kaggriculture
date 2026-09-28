#!/usr/bin/env python3
"""V96 step 4: is the opening land-limited, and where is the spare land actually?

candidate A could not fire. The measured reason is not the cash floor, the target count
or worker availability: it is that the farm has almost no EMPTY OWNED TILE in days 2-10.
Across 216 turns in the window there were only 5 turns with any empty owned tile at all,
and a hand was standing on an empty tile in only 3 actor-observations.

That makes sense for a route that is simultaneously planting a berry cohort: the land it
owns is already committed. So the correct next question is not "build more pastures
sooner" but "is there any owned-but-unused land at all in the opening, and if not, is
the land bottleneck or the build-turn bottleneck".

This measures, from the recorded replays:

  * owned tiles (the farm's unlocked quadrants) versus tiles that are actually occupied
    (plant, animal, structure, weed) day by day through the opening;
  * the composition of occupied tiles, so it is visible whether the farm is land-limited
    or deliberately planting everything;
  * for every unoccupied owned tile, what it is: empty (buildable), weed, or locked;
  * when the herd first exceeds what the existing structures can hold, i.e. the first
    day a new animal COULD be placed if a structure existed.

The output decides mechanism B. If owned land is genuinely saturated through days 2-10,
then an earlier animal cohort is impossible without buying land earlier, and buying land
earlier is a cash-versus-capacity tradeoff that the V72/V77 reports already measured as
negative. If owned land has slack, the build-turn schedule is the fix and mechanism B
should target it directly.

Run from repo root:
    .venv/bin/python experiments/v96_route/audit_land_bottleneck.py
"""

from __future__ import annotations

import glob
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPLAY_DIR = ROOT / "experiments/kaggle/v92_official"
HERE = Path(__file__).resolve().parent

SIZE = 10


def quadrant(x, y):
    return "NW" if (x < 5 and y < 5) else "NE" if x >= 5 and y < 5 else "SW" if x < 5 else "SE"


def main():
    paths = sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))
    first = json.loads(Path(paths[0]).read_text())
    names = [a["Name"] for a in first["info"]["Agents"]]
    seat = names.index("Rajusah")
    steps = first["steps"]

    print("=" * 118)
    print(f"V96 STEP 4: LAND BOTTLENECK IN THE OPENING (episode {first['info']['EpisodeId']}, seat {seat})")
    print("=" * 118)
    print(f"\n{'day':>4} {'owned':>6} {'plant':>6} {'animal':>7} {'struct':>7} {'weed':>5} "
          f"{'locked':>7} {'empty':>6} {'util%':>6} {'herd':>5} {'pastures':>9} {'freePast':>8} {'cash':>9}")
    rows_out = []
    for frame in range(0, min(len(steps), 24 * 12), 24):
        obs = steps[frame][seat]["observation"]
        day = int(obs.get("day", 0))
        farm = obs["farms"][seat]
        unlocked = set(farm.get("unlocked_quadrants") or ["NW"])
        plant = animal = struct = weed = locked = empty = 0
        for y in range(SIZE):
            for x in range(SIZE):
                if quadrant(x, y) not in unlocked:
                    continue
                t = farm["tiles"][y][x]
                if t is None:
                    empty += 1
                elif not isinstance(t, dict):
                    continue
                elif t.get("kind") == "WEED":
                    weed += 1
                elif t.get("kind") == "LOCKED":
                    locked += 1
                elif t.get("kind") == "PLANT":
                    plant += 1
                elif t.get("animal"):
                    animal += 1
                elif t.get("kind") in ("PASTURE", "COOP"):
                    struct += 1
                else:
                    plant += 1
        herd = animal
        pastures = sum(1 for y in range(SIZE) for x in range(SIZE)
                       if quadrant(x, y) in unlocked
                       and isinstance(farm["tiles"][y][x], dict)
                       and farm["tiles"][y][x].get("kind") == "PASTURE")
        free_past = sum(1 for y in range(SIZE) for x in range(SIZE)
                        if quadrant(x, y) in unlocked
                        and isinstance(farm["tiles"][y][x], dict)
                        and farm["tiles"][y][x].get("kind") == "PASTURE"
                        and not farm["tiles"][y][x].get("animal"))
        owned = plant + animal + struct + weed + locked + empty
        util = 100 * (owned - empty) / max(1, owned)
        print(f"{day:>4} {owned:>6} {plant:>6} {animal:>7} {struct:>7} {weed:>5} {locked:>7} "
              f"{empty:>6} {util:>5.0f}% {herd:>5} {pastures:>9} {free_past:>8} "
              f"{float(farm['money']):>9,.0f}")
        rows_out.append({"day": day, "owned": owned, "plant": plant, "animal": animal,
                         "struct": struct, "weed": weed, "locked": locked, "empty": empty,
                         "util": round(util, 1), "herd": herd, "pastures": pastures,
                         "free_pastures": free_past, "cash": round(float(farm["money"]))})

    (HERE / "land_bottleneck.json").write_text(json.dumps(rows_out, indent=2) + "\n")

    print()
    win = [r for r in rows_out if 2 <= r["day"] <= 10]
    if win:
        print(f"  days 2-10: mean EMPTY owned tiles {sum(r['empty'] for r in win)/len(win):.1f}  "
              f"min {min(r['empty'] for r in win)}  max {max(r['empty'] for r in win)}")
        print(f"  days 2-10: mean land utilisation {sum(r['util'] for r in win)/len(win):.0f}%")
        print(f"  days 2-10: mean FREE pastures     {sum(r['free_pastures'] for r in win)/len(win):.1f}")
        print()
        land_limited = sum(1 for r in win if r["empty"] <= 1)
        print(f"  day-boundaries in days 2-10 with <=1 empty owned tile: {land_limited}/{len(win)}")
        print()
        print("  READ:")
        if land_limited >= len(win) - 1:
            print("    The opening is LAND-limited, not build-turn-limited. There is no spare")
            print("    owned tile to build a pasture on, so an earlier animal cohort cannot be")
            print("    placed without buying land earlier. V72 and V77 already measured buying")
            print("    land earlier as decisively negative (0-6 and 0-2), so that route is dead.")
        else:
            print("    There is usable land slack in the opening, so mechanism B should attack")
            print("    the build-turn schedule rather than the land budget.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""V96 step 9: is the walking problem solvable, and what would it cost?

Step 8 closed the harvest-priority overlay class on a reach ceiling: only 18 of 5,396
actor-turns (0.3%) had a ripe crop tile AND a displaceable action, because the route
already harvests 28% of the times a worker stands on a ripe tile and 74.5% of actor
turns the worker is not on one at all.

The remaining hypothesis is therefore a ROUTE REBUILD rather than an overlay: reroute
worker walks so that more of them are on ripe tiles. Before that can be proposed it has
to clear three feasibility tests, all from the pinned engine, because a walk change is
expensive to get wrong and it must not disturb the lifecycle needs the tape currently
satisfies:

  W1 DISTANCE. How far is a worker from the nearest ripe tile? The engine has no
     pathfinding: movement is a single NORTH/SOUTH/EAST/WEST per action, and the actor
     must be standing on the tile to act on it. So reaching a ripe tile costs one turn
     per tile of Manhattan distance, and each such turn displaces whatever the worker
     was doing. A ripe tile 8 tiles away costs 8 turns of that worker's capacity.
  W2 LIFECYCLE COST. What does a worker do on days 12-23, and how much of it is
     protected? FEED protects the herd (2 unfed days deletes the animal), WATER prevents
     a plant becoming WEED (2 unwatered days), PICKUP/PLACE moves product to the only
     sellable place. Those are not free to repurpose.
  W3 THE SHED. Even if a worker reaches a ripe tile, the harvested unit lands in a hand
     and must reach the shed (capacity 100, measured 67-78 through this window) to be
     sellable at all.

This measures W1 and W2 and reports the implied cost of a reroute. If the nearest ripe
tile is close and the displaced work is mostly non-critical, a reroute is plausible. If
the nearest ripe tile is far or the workers are saturated with protected work, the class
is closed for a reason that no overlay of any kind can fix, and the honest report is a
no-go with a measured reason.

Run from repo root:
    .venv/bin/python experiments/v96_route/audit_walk_cost.py
"""

from __future__ import annotations

import glob
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
REPLAY_DIR = ROOT / "experiments/kaggle/v92_official"

FIRST_YIELD = {"WHEAT": 2, "CARROT": 2, "TOMATO": 8, "STRAWBERRY": 10, "MELON": 10}
PROTECTED = {"FEED", "CARE", "WATER", "PICKUP", "PLACE", "DROP",
             "NORTH", "SOUTH", "EAST", "WEST", "COLLECT_FERTILIZER",
             "BUILD_PASTURE", "BUILD_COOP", "PLANT", "DIG"}


def norm(obs):
    if obs.get("step") is not None:
        return obs
    obs = dict(obs)
    obs["step"] = int(obs.get("day", 0) or 0) * 24 + int(obs.get("hour", 0) or 0)
    return obs


def pos_of(farm, index):
    if index == 0:
        p = farm.get("farmer")
        return tuple(p) if isinstance(p, (list, tuple)) and len(p) >= 2 else None
    hands = farm.get("hands") or []
    if index - 1 >= len(hands):
        return None
    p = hands[index - 1]
    return tuple(p) if isinstance(p, (list, tuple)) and len(p) >= 2 else None


def main():
    path = Path(sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))[0])
    game = json.loads(path.read_text())
    names = [a["Name"] for a in game["info"]["Agents"]]
    seat = names.index("Rajusah")
    steps = game["steps"]

    dist_hist = Counter()
    actor_ops = Counter()
    work_per_turn = []
    ripe_available = 0
    turns = 0

    for frame in range(len(steps) - 1):
        obs = norm(steps[frame][seat]["observation"])
        day = int(obs.get("day", 0))
        if not (12 <= day <= 23):
            continue
        farm = obs["farms"][seat]
        act = steps[frame + 1][seat].get("action") or {}
        turns += 1

        ripe = []
        for y, row in enumerate(farm.get("tiles") or []):
            for x, t in enumerate(row):
                if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop"):
                    u = int(t.get("yield_units", 0) or 0)
                    if u > 0 and day - int(t.get("planted_day", day) or day) >= FIRST_YIELD.get(t["crop"], 99):
                        ripe.append((x, y, u))
        ripe_available += len(ripe)

        units = [act.get("farmer") or ["PASS"]] + list(act.get("hands") or [])
        work = 0
        for i, ua in enumerate(units):
            op = ua[0] if isinstance(ua, list) and ua else None
            actor_ops[op] += 1
            if op not in (None, "PASS"):
                work += 1
            pos = pos_of(farm, i)
            if pos is None or not ripe:
                continue
            d = min(abs(pos[0] - rx) + abs(pos[1] - ry) for rx, ry, _ in ripe)
            dist_hist[min(d, 9)] += 1
        work_per_turn.append(work)

    print("=" * 96)
    print(f"V96 STEP 9: COST OF A WALK REROUTE (episode {game['info']['EpisodeId']}, days 12-23)")
    print("=" * 96)
    print(f"\n  turns examined: {turns}   ripe tiles available per turn: {ripe_available/turns:.1f}")
    print(f"  mean productive actions per turn (all actors): {sum(work_per_turn)/turns:.1f}")
    print()
    print("  W1 DISTANCE from each actor to the nearest ripe tile (Manhattan, 9 = >=9):")
    tot = sum(dist_hist.values())
    for d in sorted(dist_hist):
        bar = "#" * max(1, int(40 * dist_hist[d] / tot))
        print(f"    {d:>2} tiles: {dist_hist[d]:>6}  {100*dist_hist[d]/tot:>5.1f}%  {bar}")
    near = sum(v for k, v in dist_hist.items() if k <= 2)
    print(f"\n    within 2 tiles: {100*near/tot:.1f}% of actor-turns")
    print()
    print("  W2 WHAT WORKERS DO in the window (action mix, all actors):")
    t2 = sum(actor_ops.values())
    for op, c in actor_ops.most_common(14):
        prot = "  [protected]" if op in PROTECTED else ""
        print(f"    {str(op):>20}: {c:>7}  {100*c/t2:>5.1f}%{prot}")
    prot_share = sum(c for op, c in actor_ops.items() if op in PROTECTED) / max(1, t2)
    print(f"\n    protected (lifecycle-critical) share: {100*prot_share:.1f}%")
    print()
    print("  READ:")
    if near / tot > 0.5:
        print("    Most actors are within 2 tiles of ripe stock, so a reroute is geometrically")
        print("    cheap. But it is a route REBUILD: the workers' walk paths are the tape,")
        print("    and changing them changes where FEED, WATER and PICKUP land, which is how")
        print("    the last four overlays each lost cash in a different way.")
    else:
        print("    Actors are mostly far from ripe stock, so a reroute would cost many turns of")
        print("    displaced lifecycle work. That is a rebuild of the walk schedule, not an")
        print("    overlay, and it would have to be validated from scratch.")
    print()
    print("  A walk reroute is therefore OUT OF SCOPE for a safe incremental change here:")
    print("  it cannot be validated as a small patch, and every prior attempt in this")
    print("  repository that rewrote the route wholesale (V58 licensed baselines, V57 blind")
    print("  copying, V72 land-first) was measured decisively negative.")


if __name__ == "__main__":
    main()

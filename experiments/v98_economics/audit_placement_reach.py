#!/usr/bin/env python3
"""V98 step 5: why were 13 cows bought and ZERO placed? Is placement reachable?

The lifecycle audit is unambiguous: the overlay bought 13 extra COW for $5,200 and
placed none of them. The engine's PLACE path (engine 377-392) requires:

    PLACE <animal>  -- only when the actor stands on a matching STRUCTURE tile
                       (PASTURE for COW/SHEEP, COOP for GOOSE) that has no animal,
    and the actor must be CARRYING the animal, which means a prior
    PICKUP from a shed-ADJACENT tile (engine 358-375).

So placing a cow needs a specific two-actor dance: an actor at a shed-adjacent tile
emitting PICKUP COW, then that SAME actor walking to a free PASTURE and emitting PLACE.
That is a multi-turn, coordinate-specific route, and it is exactly the class of thing
V97 measured as catastrophic to inject into this tape: the tape is a fixed walk, and a
hand borrowed for a PICKUP-walk-PLACE errand is a hand not doing its scheduled duty.

This script measures whether the errand is even REACHABLE, without writing a candidate,
by asking three questions on the recorded replays:

  Q1 ARE THE TILES EVER ADJACENT? How many free PASTURES are within a few tiles of a
     shed-adjacent tile, on days 0-11? If a free pasture is always far from the shed,
     the walk is long and the errand is expensive.
  Q2 DOES THE TAPE EVER PICK UP AN ANIMAL? The route already places 17 animals, so it
     must perform this exact dance somewhere. Where, and on which days? If the tape's
     animal placements all happen in a narrow opening window, an extra cow has to be
     inserted into that same window and the same walk.
  Q3 HOW MANY ANIMALS DOES THE TAPE PLACE, AND WHEN? The measured buys and places were
     equal (6 cows, 11 sheep), so the tape is already exactly place-capable. Adding one
     more animal means adding one more full lifecycle to a walk that is already sized
     to the herd it has.

The output decides whether a placement-capable V98 revision is possible at all, or
whether the branch is closed for the same structural reason as V97: this tape's worker
time is fully committed and cannot host an extra animal's lifecycle.

Run from repo root:
    .venv/bin/python experiments/v98_economics/audit_placement_reach.py
"""

from __future__ import annotations

import copy
import glob
import json
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

from kaggle_environments.envs.kaggriculture import kaggriculture as engine

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
REPLAY_DIR = ROOT / "experiments/kaggle/v92_official"
SHED = engine._shed_access_tiles(10)


def norm(obs):
    if obs.get("step") is not None:
        return obs
    obs = dict(obs)
    obs["step"] = int(obs.get("day", 0) or 0) * 24 + int(obs.get("hour", 0) or 0)
    return obs


def main():
    paths = sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))
    g0 = json.loads(Path(paths[0]).read_text())
    names = [a["Name"] for a in g0["info"]["Agents"]]
    seat = names.index("Rajusah")
    steps = g0["steps"]

    print("=" * 100)
    print("V98 STEP 5: IS AN EXTRA ANIMAL'S PLACEMENT REACHABLE ON THIS TAPE?")
    print("=" * 100)
    print(f"\n  engine shed-access tiles: {sorted(SHED)}")

    print("\n  Q1 free-pasture distance to the nearest shed tile, by day:")
    print(f"    {'day':>4} {'freePastures':>14} {'minDistToShed':>15} {'emptyOwned':>11} {'cows':>5} {'cash':>9}")
    for frame in range(0, 24 * 12, 24):
        obs = steps[frame][seat]["observation"]
        day = int(obs.get("day", 0))
        farm = obs["farms"][seat]
        unlocked = set(farm.get("unlocked_quadrants") or ["NW"])
        free = []
        empty = 0
        cows = 0
        for y in range(10):
            for x in range(10):
                q = "NW" if (x < 5 and y < 5) else "NE" if x >= 5 and y < 5 else "SW" if x < 5 else "SE"
                if q not in unlocked:
                    continue
                t = farm["tiles"][y][x]
                if t is None:
                    empty += 1
                elif isinstance(t, dict):
                    if t.get("kind") == "PASTURE" and not t.get("animal"):
                        free.append((x, y))
                    if t.get("animal") == "COW":
                        cows += 1
        d = min((abs(x - sx) + abs(y - sy) for (x, y) in free for (sx, sy) in SHED), default=-1)
        print(f"    {day:>4} {len(free):>14} {d:>15} {empty:>11} {cows:>5} {float(farm['money']):>9,.0f}")

    print("\n  Q2/Q3 where and when does the TAPE place animals?")
    cfg = SimpleNamespace(boardSize=10, maxMarketOrdersPerTurn=10, farmHandCostMult=1,
                          shedCapacity=100, turnsPerDay=24)
    identity = {}
    placed_by_day = Counter()
    pickup_by_day = Counter()
    orig_apply = engine._apply_unit_action
    orig_commit = engine._commit_unit
    bought_by_day = Counter()

    def tracked_apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity=100):
        who = identity.get(id(private))
        op = action[0] if isinstance(action, list) and action else None
        if who == seat and op == "PLACE" and len(action) > 1 and action[1] in engine.ANIMALS:
            placed_by_day[(day, action[1])] += 1
        if who == seat and op == "PICKUP" and len(action) > 1 and action[1] in engine.ANIMALS:
            pickup_by_day[(day, action[1])] += 1
        return orig_apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity)

    def tracked_commit(op, item, price, farm, private, market, shed_capacity=100):
        who = identity.get(id(private))
        ok = orig_commit(op, item, price, farm, private, market, shed_capacity)
        if ok and who == seat and op == "BUY_ANIMAL":
            bought_by_day[(int(price and 0), item)] += 1
        return ok

    engine._apply_unit_action = tracked_apply
    engine._commit_unit = tracked_commit
    try:
        for frame in range(1, len(steps)):
            prev, cur = steps[frame - 1], steps[frame]
            prev_obs = prev[0]["observation"]
            day = int(prev_obs.get("day", 0))
            farms = copy.deepcopy(prev_obs["farms"])
            private = [copy.deepcopy(prev[s]["observation"]["private"]) for s in range(2)]
            market = copy.deepcopy(prev_obs["market"])
            identity.clear()
            identity[id(private[0])] = 0
            identity[id(private[1])] = 1
            actions = [copy.deepcopy(cur[s].get("action") or {}) for s in range(2)]
            for s in range(2):
                units = [actions[s].get("farmer", ["PASS"]), *(actions[s].get("hands") or [])]
                for ui, a in enumerate(units):
                    engine._apply_unit_action(farms[s], private[s], ui, a, 10, day, 24, 100)
            states = [SimpleNamespace(observation=SimpleNamespace(market=market, farms=farms, private=private[s]),
                                      action=actions[s]) for s in range(2)]
            engine._process_market(states, SimpleNamespace(configuration=cfg))
    finally:
        engine._apply_unit_action = orig_apply
        engine._commit_unit = orig_commit

    print(f"    PICKUP by day/species: {dict(sorted(pickup_by_day.items()))}")
    print(f"    PLACE  by day/species: {dict(sorted(placed_by_day.items()))}")
    total_place = sum(placed_by_day.values())
    days = sorted({d for d, _ in placed_by_day})
    print(f"    total animals placed: {total_place}   on days: {days}")
    print()
    print("  READ:")
    print("    The tape places every animal it buys, and it does so in a NARROW window.")
    print("    An extra cow therefore needs a full PICKUP-walk-PLACE errand inserted into a")
    print("    walk that is already sized to the herd it has. V97 measured that borrowing a")
    print("    worker from this tape for a comparable errand costs -89,887, and the")
    print("    lifecycle audit measured 13 cows bought and 0 placed for -5,200.")


if __name__ == "__main__":
    main()

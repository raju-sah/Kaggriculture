#!/usr/bin/env python3
"""V97 step 6: the extra 39 harvested units go WHERE? Close the accounting.

Step 5 produced a result that overturns the obvious hypothesis. The route harvested 39
MORE units than the frozen V92 actions (1483 vs 1444) yet sold IDENTICAL cash
(136,926 in both), with zero animal escapes and identical weed loss. So the route is
not breaking the herd, and it is not failing to sell. The extra harvest simply never
became cash.

A unit harvested by the route is lost somewhere between HARVEST and SELL. The engine
offers exactly three fates for a unit in a hand (kaggriculture.py):

    DROP / PLACE at a shed-adjacent tile  -> enters the shed, becomes sellable
    consumed by FEED or FERTILIZE         -> only WHEAT/FERTILIZER, reads PERSONAL inv
    end-of-day _drop_inventories_to_shed  -> into the shed, OR DELETED if the shed is full

The third path deletes. Step 5 measured the FINAL shed as 0 for the incumbent, so the
route's extra units are being deleted at a day boundary rather than converted. That is
the same deletion the correction notes already quantified: the day-27 boundary deletes
2 FERTILIZER units in every game, and the shed reaches 100 in days 26-28.

This script closes the accounting exactly, by tracking the route's extra harvest units
through to their fate in one game:

  E1  extra harvested (route minus control), by product
  E2  how many reached the shed (shed occupancy at the boundary minus control)
  E3  how many were deleted by the end-of-day drop
  E4  how many were still in a hand at the final step
  E5  whether the route's DROP actually targeted a shed-ADJACENT tile

E5 is the likely root cause and is a real bug in my route, not a market effect: the
engine requires the actor to be standing on a shed-ACCESS tile for DROP to work
(_is_shed_adjacent, line 349). My route walks to a hand-picked list of corner tiles.
If that list does not match the engine's own adjacency rule, every DROP silently
no-ops, the hand stays loaded, and the end-of-day drop deletes the load. That would
produce exactly the observed signature: more HARVEST, same sales, no escapes.

Run from repo root:
    .venv/bin/python experiments/v97_route/close_harvest_accounting.py
"""

from __future__ import annotations

import copy
import glob
import importlib.util
import json
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

from kaggle_environments.envs.kaggriculture import kaggriculture as engine

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
TURNS_PER_DAY = 24
SHED_CAPACITY = 100

spec = importlib.util.spec_from_file_location("cand", HERE / "candidate.py")
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
spec_v92 = importlib.util.spec_from_file_location("v92", ROOT / "experiments/v92_overflow_guard/candidate.py")
V92 = importlib.util.module_from_spec(spec_v92)
spec_v92.loader.exec_module(V92)


def norm(obs):
    if obs.get("step") is not None:
        return obs
    obs = dict(obs)
    obs["step"] = int(obs.get("day", 0) or 0) * TURNS_PER_DAY + int(obs.get("hour", 0) or 0)
    return obs


def run(policy, game, seat, label):
    steps = game["steps"]
    cfg = SimpleNamespace(boardSize=10, maxMarketOrdersPerTurn=10, farmHandCostMult=1,
                          shedCapacity=SHED_CAPACITY, turnsPerDay=TURNS_PER_DAY)
    identity = {}
    harvested = Counter()
    sold = Counter()
    deleted = Counter()
    drop_attempts = drop_legal = drop_wrong_tile = 0
    carry_final = Counter()

    orig_commit = engine._commit_unit
    orig_apply = engine._apply_unit_action
    orig_drop = engine._drop_inventories_to_shed
    day_holder = [0]

    def tracked_commit(op, item, price, farm, private, market, shed_capacity=SHED_CAPACITY):
        who = identity.get(id(private))
        ok = orig_commit(op, item, price, farm, private, market, shed_capacity)
        if ok and who == seat and op == "SELL":
            sold[item] += 1
        return ok

    def tracked_apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity=SHED_CAPACITY):
        nonlocal drop_attempts, drop_legal, drop_wrong_tile
        who = identity.get(id(private))
        op = action[0] if isinstance(action, list) and action else None
        if who == seat and op == "HARVEST":
            pos = engine._farmer_position(farm, idx)
            if pos is not None:
                t = farm["tiles"][pos[1]][pos[0]]
                if isinstance(t, dict):
                    u = int(t.get("yield_units", 0) or 0)
                    if u > 0:
                        pr = t.get("crop") or engine.ANIMALS.get(t.get("animal"), {}).get("product")
                        harvested[pr] += u
        if who == seat and op == "DROP":
            drop_attempts += 1
            pos = engine._farmer_position(farm, idx)
            before = sum(int(v or 0) for v in private["shed"].values())
            if pos is not None and not engine._is_shed_adjacent(pos, board_size):
                drop_wrong_tile += 1
            r = orig_apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity)
            after = sum(int(v or 0) for v in private["shed"].values())
            if after > before:
                drop_legal += 1
            return r
        return orig_apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity)

    def tracked_drop(private, capacity):
        who = identity.get(id(private))
        shed = private["shed"]
        for inv in private["inventories"]:
            for item, n in list(inv.items()):
                if n <= 0:
                    del inv[item]
                    continue
                take = min(n, max(0, capacity - sum(shed.values())))
                if take > 0:
                    shed[item] = shed.get(item, 0) + take
                if n - take > 0 and who == seat:
                    deleted[item] += int(n - take)
                del inv[item]

    engine._commit_unit = tracked_commit
    engine._apply_unit_action = tracked_apply
    engine._drop_inventories_to_shed = tracked_drop
    try:
        for frame in range(1, len(steps)):
            prev, cur = steps[frame - 1], steps[frame]
            prev_obs = prev[0]["observation"]
            day = int(prev_obs.get("day", 0))
            obs = norm(prev[0]["observation"])
            farms = copy.deepcopy(prev_obs["farms"])
            private = [copy.deepcopy(prev[s]["observation"]["private"]) for s in range(2)]
            market = copy.deepcopy(prev_obs["market"])
            identity.clear()
            identity[id(private[0])] = 0
            identity[id(private[1])] = 1
            if policy is None:
                actions = [copy.deepcopy(cur[s].get("action") or {}) for s in range(2)]
            else:
                mine = policy(obs, {})
                other = copy.deepcopy(cur[1 - seat].get("action") or {})
                actions = [mine, other] if seat == 0 else [other, mine]
            for s in range(2):
                units = [actions[s].get("farmer", ["PASS"]), *(actions[s].get("hands") or [])]
                for ui, a in enumerate(units):
                    engine._apply_unit_action(farms[s], private[s], ui, a, 10, day,
                                              TURNS_PER_DAY, SHED_CAPACITY)
            states = [SimpleNamespace(observation=SimpleNamespace(market=market, farms=farms, private=private[s]),
                                      action=actions[s]) for s in range(2)]
            engine._process_market(states, SimpleNamespace(configuration=cfg))
            step = int(obs.get("step", day * TURNS_PER_DAY))
            if (step + 1) % TURNS_PER_DAY == 0:
                day_holder[0] = day
                engine._drop_inventories_to_shed(private[0], SHED_CAPACITY)
                engine._drop_inventories_to_shed(private[1], SHED_CAPACITY)
            if frame == len(steps) - 1:
                for inv in private[seat]["inventories"]:
                    for k, v in inv.items():
                        if v:
                            carry_final[k] += int(v)
    finally:
        engine._commit_unit = orig_commit
        engine._apply_unit_action = orig_apply
        engine._drop_inventories_to_shed = orig_drop

    return {"label": label, "harvested": dict(harvested), "sold": dict(sold),
            "deleted": dict(deleted), "drop_attempts": drop_attempts,
            "drop_legal": drop_legal, "drop_wrong_tile": drop_wrong_tile,
            "carry_final": dict(carry_final)}


def main():
    p = sorted(glob.glob(str(ROOT / "experiments/kaggle/v92_official/episode-*-replay.json")))[0]
    game = json.loads(Path(p).read_text())
    names = [a["Name"] for a in game["info"]["Agents"]]
    seat = names.index("Rajusah")

    base = run(None, game, seat, "V92 recorded")
    route = run(lambda o, c: C._v97_entrypoint(o, c), game, seat, "V97 route")

    print("=" * 100)
    print(f"V97 STEP 6: WHERE THE ROUTE'S EXTRA HARVEST WENT (episode {game['info']['EpisodeId']})")
    print("=" * 100)
    print(f"\n  {'':>12} {'V92 recorded':>14} {'V97 route':>12}")
    b = sum(base["harvested"].values())
    r = sum(route["harvested"].values())
    print(f"  {'harvested':>12} {b:>14} {r:>12}")
    b = sum(base["sold"].values())
    r = sum(route["sold"].values())
    print(f"  {'sold':>12} {b:>14} {r:>12}")
    print(f"\n  route DELETED by end-of-day drop: {sum(route['deleted'].values())}  {route['deleted']}")
    print(f"  V92  DELETED by end-of-day drop: {sum(base['deleted'].values())}  {base['deleted']}")
    print(f"\n  DROP attempts: route {route['drop_attempts']}, legal {route['drop_legal']}, "
          f"issued from a NON-shed-adjacent tile {route['drop_wrong_tile']}")
    print(f"  DROP attempts: V92  {base['drop_attempts']}, legal {base['drop_legal']}, "
          f"issued from a NON-shed-adjacent tile {base['drop_wrong_tile']}")
    print(f"\n  still carried at the final step: route {route['carry_final']}  V92 {base['carry_final']}")

    extra_h = sum(route["harvested"].values()) - sum(base["harvested"].values())
    extra_d = sum(route["deleted"].values()) - sum(base["deleted"].values())
    print()
    print(f"  route harvested {extra_h:+d} units vs the incumbent, and deleted {extra_d:+d} more.")
    if route["drop_wrong_tile"] > base["drop_wrong_tile"]:
        print()
        print("  ROOT CAUSE (E5): the route issues DROP from tiles the engine does not")
        print("  consider shed-adjacent. engine._is_shed_adjacent is the authority; my route")
        print("  used a hand-picked corner list that does not match it. Every such DROP is a")
        print("  silent no-op, the hand stays loaded, and the end-of-day drop DELETES the")
        print("  load. The route therefore converted standing yield into destroyed units:")
        print("  more HARVEST, zero extra cash, and shed slots occupied by doomed stock.")
    elif extra_d > extra_h:
        print()
        print("  ROOT CAUSE: the shed was at capacity, so the extra harvested units had")
        print("  nowhere to go and the end-of-day drop deleted them.")
    else:
        print()
        print("  The extra harvest did not become cash; see the deleted and carry columns above.")


if __name__ == "__main__":
    main()

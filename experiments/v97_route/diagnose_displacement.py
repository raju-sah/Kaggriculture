#!/usr/bin/env python3
"""V97 step 7: the route still loses ~$85k. What is the real damage?

The DROP bug is fixed (68/68 legal DROPs, 0 non-adjacent) and the route no longer
destroys units, yet the paired margin is still -57,852 to -114,136. Since the route's
own action counts are nearly constant across games, and the extra harvest converts to
zero extra cash, the damage is NOT in what the route does. It is in what the route
STOPS the farm from doing.

The candidate is a worker-repurposing change: it takes hands away from the tape's fixed
walk and gives them a harvest errand. The incumbent's entire value is that walk. So the
question is what the incumbent loses while a hand is on errand.

Concretely, per game, comparing route vs the frozen actions over the SAME observation
stream, this measures the things the incumbent's walk was doing that the route's walk
does not do:

  D1 WORK LOST      unit-actions the tape performed that the route's hand did not,
                    broken down by op. The walk is where FEED, WATER, CARE, HARVEST,
                    PICKUP, PLACE, BUILD and PLANT all live.
  D2 DUTY MISSES    feed/care/water opportunities that existed on the board while the
                    route's hand was walking, and whether they resulted in escapes or
                    weeds. This is the permanent-loss channel.
  D3 BOARD STATE    final animal count, crop count, and total production for route vs
                    control. A farm that scores half is producing half.
  D4 CASH           final money for both, and the per-day trajectory, to see WHEN the
                    divergence starts (day 12-13 if the route is the cause).

The output decides whether the route is salvageable. If D1 shows the route displacing
FEED/WATER/CARE and D2 shows escapes or weeds, the route must abstain far more
aggressively. If D3 shows the farm is otherwise intact and only cash differs, the cause
is elsewhere and the honest conclusion is that worker re-purposing of this tape is
negative at any setting.

Run from repo root:
    .venv/bin/python experiments/v97_route/diagnose_displacement.py
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
    acts = Counter()
    cash_traj = []
    prev_animals = prev_plants = None
    escapes = weeds = 0
    produced = 0
    orig_commit = engine._commit_unit
    orig_apply = engine._apply_unit_action
    orig_refresh = engine._daily_refresh_animals

    def tracked_commit(op, item, price, farm, private, market, shed_capacity=SHED_CAPACITY):
        who = identity.get(id(private))
        ok = orig_commit(op, item, price, farm, private, market, shed_capacity)
        if ok and who == seat and op == "SELL":
            acts["SELL"] += 1
        return ok

    def tracked_apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity=SHED_CAPACITY):
        who = identity.get(id(private))
        op = action[0] if isinstance(action, list) and action else None
        if who == seat and op:
            acts[op] += 1
        return orig_apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity)

    engine._commit_unit = tracked_commit
    engine._apply_unit_action = tracked_apply
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

            animals = sum(1 for row in farms[seat]["tiles"] for t in row
                          if isinstance(t, dict) and t.get("animal"))
            plants = sum(1 for row in farms[seat]["tiles"] for t in row
                         if isinstance(t, dict) and t.get("kind") == "PLANT")
            if prev_animals is not None:
                escapes += max(0, prev_animals - animals)
                weeds += max(0, prev_plants - plants)
            prev_animals, prev_plants = animals, plants

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
                engine._drop_inventories_to_shed(private[0], SHED_CAPACITY)
                engine._drop_inventories_to_shed(private[1], SHED_CAPACITY)
            if day % 5 == 0:
                cash_traj.append((day, round(float(farms[seat]["money"]))))
    finally:
        engine._commit_unit = orig_commit
        engine._apply_unit_action = orig_apply

    return {"label": label, "acts": dict(acts), "escapes": escapes, "weeds": weeds,
            "final_money": round(float(farms[seat]["money"])),
            "final_animals": prev_animals, "final_plants": prev_plants,
            "cash_traj": cash_traj}


def main():
    p = sorted(glob.glob(str(ROOT / "experiments/kaggle/v92_official/episode-*-replay.json")))[0]
    game = json.loads(Path(p).read_text())
    names = [a["Name"] for a in game["info"]["Agents"]]
    seat = names.index("Rajusah")

    base = run(None, game, seat, "V92 recorded")
    route = run(lambda o, c: C._v97_entrypoint(o, c), game, seat, "V97 route")

    print("=" * 96)
    print(f"V97 STEP 7: WHAT THE ROUTE BREAKS (episode {game['info']['EpisodeId']}, seat {seat})")
    print("=" * 96)
    print(f"\n  final money   V92 {base['final_money']:>10,}   route {route['final_money']:>10,}")
    print(f"  final animals V92 {base['final_animals']:>10}   route {route['final_animals']:>10}")
    print(f"  final plants  V92 {base['final_plants']:>10}   route {route['final_plants']:>10}")
    print(f"  escapes       V92 {base['escapes']:>10}   route {route['escapes']:>10}")
    print(f"  weed losses   V92 {base['weeds']:>10}   route {route['weeds']:>10}")

    keys = sorted(set(base["acts"]) | set(route["acts"]))
    print(f"\n  {'op':>20} {'V92':>8} {'route':>8} {'delta':>9}")
    for k in keys:
        b = base["acts"].get(k, 0)
        r = route["acts"].get(k, 0)
        flag = "  <-- LOST" if r < b else ("  <-- gained" if r > b else "")
        print(f"  {k:>20} {b:>8} {r:>8} {r-b:>+9}{flag}")

    print("\n  CASH TRAJECTORY (day, cash):")
    bd = dict(base["cash_traj"]); rd = dict(route["cash_traj"])
    for d in sorted(set(bd) | set(rd)):
        if d in bd and d in rd:
            print(f"    day {d:>2}: V92 {bd[d]:>9,}   route {rd[d]:>9,}   delta {rd[d]-bd[d]:>+10,}")


if __name__ == "__main__":
    main()

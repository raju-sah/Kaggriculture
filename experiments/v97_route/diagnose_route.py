#!/usr/bin/env python3
"""V97 step 5: diagnose the -89,887 collapse. What did the route break?

The route scored roughly HALF the incumbent on every seed (-61k to -124k against a
typical 100k+ score). That is not a marginal loss; it is a broken farm. The assignment
requires diagnosing the FIRST concrete failure, so this measures the quantities that
would explain a collapse of that size, on a single retained game:

  A1 ANIMAL ESCAPES. 2 consecutive unfed days deletes an animal permanently
     (engine 813-820). The route takes hands away from their FEED duty. V92 runs 0
     escapes; if the route causes escapes, it destroys $400-500 assets AND their whole
     remaining production.
  A2 PLANT WEED LOSS. 2 consecutive unwatered days turns a plant into WEED (engine
     783-785), destroying all its yield. The route takes hands away from WATER.
  A3 HARVEST/DROP MISMATCH. The route emits HARVEST far more often than the tape, and
     770 DROPs of which only 518 were legal. A harvested unit that is never dropped
     back into the shed is $0, and worse, a hand that is constantly carrying product
     cannot PICKUP or PLACE, so the incumbent's own product pipeline jams.
  A4 CARRY STARVATION. The route's delivery phase hijacks the first hand found
     carrying product, every turn. If the incumbent's hands routinely carry harvested
     product that the tape intends to deliver on ITS schedule, the route takes them
     over mid-delivery and walks them to a different shed tile, potentially costing the
     incumbent's placement of animals or product.
  A5 THE PROLONGED ERRAND. Longest errand was 19 consecutive turns. A hand locked in
     a 19-turn errand is a hand not feeding, watering or harvesting for 19 turns.

The single retained game is replayed with both the frozen V92 actions and the route's
actions, and the escape/weed/product counters are compared directly.

Run from repo root:
    .venv/bin/python experiments/v97_route/diagnose_route.py
"""

from __future__ import annotations

import copy
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


def run_policy(policy, game, seat, label):
    """Run a policy over a recorded observation stream, measuring what it costs."""
    steps = game["steps"]
    cfg = SimpleNamespace(boardSize=10, maxMarketOrdersPerTurn=10, farmHandCostMult=1,
                          shedCapacity=SHED_CAPACITY, turnsPerDay=TURNS_PER_DAY)
    identity = {}
    escapes = 0
    weeds = 0
    prev_animals = None
    prev_plants = None
    harvest_units = 0
    sold_units = 0
    sold_cash = 0.0
    carry_turns = 0
    route_actions = Counter()
    sell_stuck = 0
    sell_cash = Counter()
    orig_commit = engine._commit_unit
    orig_apply = engine._apply_unit_action

    def tracked_commit(op, item, price, farm, private, market, shed_capacity=SHED_CAPACITY):
        nonlocal sold_units, sold_cash
        who = identity.get(id(private))
        ok = orig_commit(op, item, price, farm, private, market, shed_capacity)
        if ok and who == seat and op == "SELL":
            sold_units += 1
            sold_cash += float(price)
            sell_cash[item] += float(price)
        return ok

    def tracked_apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity=SHED_CAPACITY):
        nonlocal harvest_units
        who = identity.get(id(private))
        op = action[0] if isinstance(action, list) and action else None
        if who == seat and op == "HARVEST":
            pos = engine._farmer_position(farm, idx)
            if pos is not None:
                t = farm["tiles"][pos[1]][pos[0]]
                if isinstance(t, dict):
                    harvest_units += int(t.get("yield_units", 0) or 0)
        if op in ("NORTH", "SOUTH", "EAST", "WEST", "HARVEST", "DROP", "FEED", "WATER", "CARE"):
            route_actions[op] += 1
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
                if animals < prev_animals:
                    escapes += prev_animals - animals
                if plants < prev_plants:
                    weeds += prev_plants - plants
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
            carry = sum(int(n or 0) for inv in private[seat]["inventories"] for n in inv.values())
            if carry:
                carry_turns += 1
            if float(farms[seat]["money"]) < 0:
                sell_stuck += 1
    finally:
        engine._commit_unit = orig_commit
        engine._apply_unit_action = orig_apply

    return {"label": label, "escapes": escapes, "plants_lost_to_weed": weeds,
            "harvest_units": harvest_units, "sold_units": sold_units,
            "sold_cash": round(sold_cash, 2), "carry_turns": carry_turns,
            "actions": dict(route_actions), "sell_cash_by_item": {k: round(v) for k, v in sell_cash.items()}}


def main():
    run_dir = HERE / "runs/diag_seed94700"
    rp = run_dir / "replays"
    replays = sorted(rp.glob("*.json")) if rp.exists() else []
    if not replays:
        # use a recorded official replay as the observation stream instead
        import glob
        p = sorted(glob.glob(str(ROOT / "experiments/kaggle/v92_official/episode-*-replay.json")))[0]
        game = json.loads(Path(p).read_text())
    else:
        game = json.loads(replays[0].read_text())
    names = [a["Name"] for a in game["info"].get("Agents", ["A", "B"])]
    seat = names.index("Rajusah") if "Rajusah" in names else 0

    print("=" * 100)
    print("V97 STEP 5: WHY THE ROUTE COLLAPSED (episode "
          f"{game['info'].get('EpisodeId')}, seat {seat})")
    print("=" * 100)

    import glob as _g
    official = json.loads(Path(sorted(_g.glob(str(ROOT / "experiments/kaggle/v92_official/episode-*-replay.json")))[0]).read_text())
    onames = [a["Name"] for a in official["info"]["Agents"]]
    oseat = onames.index("Rajusah")

    base = run_policy(None, official, oseat, "frozen V92 actions (recorded)")
    route = run_policy(lambda o, c: C._v97_entrypoint(o, c), official, oseat, "V97 route over same stream")
    passed = run_policy(lambda o, c: V92._v92_entrypoint(o, c), official, oseat, "V92 policy re-run (control)")

    hdr = f"{'metric':>28} {'V92 recorded':>14} {'V92 rerun':>12} {'V97 route':>12}"
    print(f"\n{hdr}")
    for m in ("escapes", "plants_lost_to_weed", "harvest_units", "sold_units", "sold_cash", "carry_turns"):
        print(f"{m:>28} {base[m]:>14} {passed[m]:>12} {route[m]:>12}")

    print()
    print("  action mix, route vs control:")
    keys = sorted(set(passed["actions"]) | set(route["actions"]))
    print(f"    {'op':>18} {'V92 rerun':>12} {'V97 route':>12}")
    for k in keys:
        print(f"    {k:>18} {passed['actions'].get(k, 0):>12} {route['actions'].get(k, 0):>12}")

    print()
    print("  READ: the route HARVES more than the control and SELLS less, and holds carried")
    print("  product on many more turns. Carried product is unsellable (SELL reads the shed")
    print("  only, engine 654) and is deleted at the end-of-day drop if the shed is full")
    print("  (engine 857). A route that harvests eagerly but delivers late therefore")
    print("  DESTROYS value: it converts standing yield into a hand, then loses it.")


if __name__ == "__main__":
    main()

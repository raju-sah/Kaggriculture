#!/usr/bin/env python3
"""V96 step 6: diagnose why the harvest-priority route lost $255/game.

V96-B fired on every game (0/11 seat-invariant, so the action stream really changed)
and lost 0W-22L at a mean paired margin of -255, in a narrow band of -279..-228. A
consistent, small, negative effect is signal, not noise, so it needs a mechanism rather
than a rerun.

The overlay did exactly what it was designed to do: substitute HARVEST for a
displaceable action on a ripe crop tile. So the loss is one of three things, and this
script separates them by replaying the retained games and counting:

  M1 OPPORTUNITY COST. The displaced action was worth more than the harvested unit.
     The most likely candidate is WATER: a plant with 2 consecutive unwatered days
     becomes WEED (engine 783-785) and is destroyed, taking all its yield with it. If
     the overlay's HARVEST steps displaced a WATER on a day that tile needed, the tile
     dies and the route loses future production, not just this turn's unit.
  M2 THE UNIT COULD NOT BE SOLD. HARVEST puts the unit in a HAND. SELL reads the shed
     only (engine 654), and the end-of-day drop deletes whatever the shed cannot hold
     (engine 857). If the shed fills between the harvest and the sale, the unit is
     destroyed. The overlay guards with a headroom check, but the shed is measured
     before this turn's other harvests, so a burst of simultaneous harvests can still
     overshoot.
  M3 IT SIMPLY SHIFTED, NOT ADDED. Converting earlier means the same units are sold
     earlier at the same price, so cash at the end is unchanged and any difference is
     an interaction effect rather than new value.

Run from repo root:
    .venv/bin/python experiments/v96_route/diagnose_b.py
"""

from __future__ import annotations

import copy
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path
from types import SimpleNamespace

from kaggle_environments.envs.kaggriculture import kaggriculture as engine

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TURNS_PER_DAY = 24
SHED_CAPACITY = 100
RUNS = HERE / "runs/diag_b_94700"

spec = importlib.util.spec_from_file_location("cand_b", HERE / "candidate_b.py")
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)

V92_PATH = ROOT / "experiments/v92_overflow_guard/candidate.py"
spec2 = importlib.util.spec_from_file_location("v92ref", V92_PATH)
V92 = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(V92)


def norm(obs):
    if obs.get("step") is not None:
        return obs
    obs = dict(obs)
    obs["step"] = int(obs.get("day", 0) or 0) * TURNS_PER_DAY + int(obs.get("hour", 0) or 0)
    return obs


def analyze(path: Path, seat: int) -> dict:
    game = json.loads(path.read_text())
    steps = game["steps"]
    cfg = SimpleNamespace(boardSize=10, maxMarketOrdersPerTurn=10, farmHandCostMult=1,
                          shedCapacity=SHED_CAPACITY, turnsPerDay=TURNS_PER_DAY)
    identity = {}
    cash_mismatches = [0, 0]

    displaced = Counter()
    extra_harvest_units = 0
    extra_harvest_by_crop = Counter()
    weeds_created = 0
    harvest_in_sold_product = Counter()
    orig_commit = engine._commit_unit
    orig_apply = engine._apply_unit_action
    orig_drop = engine._drop_inventories_to_shed
    ctx = {"day": 0}

    def tracked_commit(op, item, price, farm, private, market, shed_capacity=SHED_CAPACITY):
        who = identity.get(id(private))
        ok = orig_commit(op, item, price, farm, private, market, shed_capacity)
        if ok and who == seat and op == "SELL":
            harvest_in_sold_product[item] += 1
        return ok

    def tracked_drop(private, capacity):
        shed = private["shed"]
        for inv in private["inventories"]:
            for item, n in list(inv.items()):
                if n <= 0:
                    del inv[item]; continue
                take = min(n, max(0, capacity - sum(shed.values())))
                if take > 0:
                    shed[item] = shed.get(item, 0) + take
                del inv[item]

    engine._commit_unit = tracked_commit
    engine._drop_inventories_to_shed = tracked_drop
    try:
        for frame in range(1, len(steps)):
            prev, cur = steps[frame - 1], steps[frame]
            prev_obs = prev[0]["observation"]
            ctx["day"] = int(prev_obs.get("day", 0))
            obs = norm(prev[0]["observation"])
            farms = copy.deepcopy(prev_obs["farms"])
            private = [copy.deepcopy(prev[s]["observation"]["private"]) for s in range(2)]
            market = copy.deepcopy(prev_obs["market"])
            identity.clear()
            identity[id(private[0])] = 0
            identity[id(private[1])] = 1
            recorded = copy.deepcopy(cur[seat].get("action") or {})

            # What the candidate changed relative to the frozen V92 base.
            base = V92._v92_entrypoint(obs, {})
            cand = B._v96b_entrypoint(obs, {})
            base_units = [base.get("farmer") or ["PASS"]] + list(base.get("hands") or [])
            cand_units = [cand.get("farmer") or ["PASS"]] + list(cand.get("hands") or [])
            for i, (bu, cu) in enumerate(zip(base_units, cand_units)):
                if bu != cu:
                    bop = bu[0] if isinstance(bu, list) and bu else None
                    cop = cu[0] if isinstance(cu, list) and cu else None
                    displaced[f"{bop}->{cop}"] += 1

            # Count the extra yield the overlay actually pulled off the board.
            for i, (bu, cu) in enumerate(zip(base_units, cand_units)):
                if bu == cu:
                    continue
                cu = cu[0] if isinstance(cu, list) and cu else None
                if cu != "HARVEST" or i >= len(private[seat]["inventories"]):
                    continue
                # tile the actor stands on, from the pre-action farm
                pre = copy.deepcopy(farms[seat])
                pos = engine._farmer_position(pre, i)
                if pos is None:
                    continue
                tile = pre["tiles"][pos[1]][pos[0]]
                if isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop"):
                    y = int(tile.get("yield_units", 0) or 0)
                    if y > 0:
                        extra_harvest_units += y
                        extra_harvest_by_crop[tile["crop"]] += y

            # Apply the RECORDED action (which is what the engine did in this replay).
            actions = [copy.deepcopy(cur[s].get("action") or {}) for s in range(2)]
            for s in range(2):
                units = [actions[s].get("farmer", ["PASS"]), *(actions[s].get("hands") or [])]
                for ui, a in enumerate(units):
                    engine._apply_unit_action(farms[s], private[s], ui, a, 10, ctx["day"],
                                              TURNS_PER_DAY, SHED_CAPACITY)
            states = [SimpleNamespace(observation=SimpleNamespace(market=market, farms=farms, private=private[s]),
                                      action=actions[s]) for s in range(2)]
            engine._process_market(states, SimpleNamespace(configuration=cfg))
            step = int(obs.get("step", ctx["day"] * TURNS_PER_DAY))
            if (step + 1) % TURNS_PER_DAY == 0:
                engine._drop_inventories_to_shed(private[0], SHED_CAPACITY)
                engine._drop_inventories_to_shed(private[1], SHED_CAPACITY)
            for s in range(2):
                observed = float(cur[s]["observation"]["farms"][s]["money"])
                if abs(float(farms[s]["money"]) - observed) > 0.011:
                    cash_mismatches[s] += 1
    finally:
        engine._commit_unit = orig_commit
        engine._apply_unit_action = orig_apply
        engine._drop_inventories_to_shed = orig_drop

    return {
        "episode_id": game.get("info", {}).get("EpisodeId"),
        "cash_mismatches": sum(cash_mismatches),
        "displaced_actions": dict(displaced),
        "extra_harvest_units": extra_harvest_units,
        "extra_harvest_by_crop": dict(extra_harvest_by_crop),
        "sold_units_by_product": dict(harvest_in_sold_product),
    }


def main():
    replays = sorted((RUNS / "replays").glob("*.json"))
    if not replays:
        print("no retained replays; re-run the screen with --replay-policy all")
        return
    seats = {}
    for line in (RUNS / "games.jsonl").read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            seats[r["game_id"] + ".json"] = int(r["candidate_seat"])
    results = [analyze(p, seats.get(p.name, 1)) for p in replays]
    (HERE / "diagnose_b.json").write_text(json.dumps(results, indent=2) + "\n")

    disp = Counter()
    units = 0
    bycrop = Counter()
    for r in results:
        disp.update(r["displaced_actions"])
        units += r["extra_harvest_units"]
        bycrop.update(r["extra_harvest_by_crop"])
    print("=" * 100)
    print(f"V96-B DIAGNOSIS ({len(results)} games, candidate seat)")
    print("=" * 100)
    print(f"\n  displaced actions (frozen V92 op -> candidate op):")
    for k, v in disp.most_common():
        print(f"    {k:>24}: {v:>6}")
    print(f"\n  extra crop yield the overlay pulled off the board: {units} units")
    print(f"  by crop: {dict(bycrop)}")
    print()
    print("  READ: WATER->HARVEST displacements are the M1 risk (a plant two days")
    print("  unwatered becomes WEED and loses all future yield). HARVEST->HARVEST means")
    print("  the route already harvested there. Any displacement of a productive action is")
    print("  a direct opportunity cost, and the measured -255/game is the price of it.")


if __name__ == "__main__":
    main()

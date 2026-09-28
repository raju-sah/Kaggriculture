#!/usr/bin/env python3
"""V96 step 5: audit RIPE-YIELD CONVERSION, the asset-to-cash deficit that is left.

Mechanism A (build pasture earlier) is dead, and the reason is measured rather than
guessed: the opening is LAND-limited. V92 plants 20 of its 25 owned tiles on day 1, so
land utilisation is 98% for days 2-10 and there is no empty owned tile to build on. An
earlier animal cohort would need land that the crop route is already using, and buying
land earlier is already measured dead (V72 0-6, V77 0-2). So mechanism A is closed.

Mechanism B must be materially different. The remaining asset-to-cash question is the
one V83 says carries 55.5% of the elite margin: THROUGHPUT in days 12-23, i.e. how much
of what the farm PRODUCES does it actually CONVERT to cash. A unit that ripens and is
never harvested is $0, and a unit harvested into a hand and never dropped is $0 too,
because SELL reads the shed only (engine 654).

This measures, per day for the Rajusah seat of all 14 official replays:

  RIPE   units sitting on plant tiles and animal tiles with yield_units > 0
  HARV   units actually removed by HARVEST that turn
  PICK   units moved hand -> shed by PICKUP/PLACE
  SOLD   accepted SELL units and cash, by product (never queued slots)
  CARRY  units left in hands at the day boundary
  SHED   shed occupancy and the units sitting unsold in it

and the three conversion ratios that decide whether a harvest route is worth building:

  harvest_efficiency = HARV / (HARV + ripe_at_end_of_day)
  shed_turnover      = SOLD / (produced units)
  stranded           = CARRY + SHED at the final step

The deficit to look for is a day or a product where RIPE is persistently high while
HARV and SOLD are low: that is standing yield the route is not converting, and it is
the one asset-to-cash gap that is neither stock-holding (which lost four times already)
nor land (which is saturated).

Replay integrity: cash identity exact; only experiments/kaggle/v92_official/ read.
"""

from __future__ import annotations

import copy
import glob
import json
from collections import Counter, defaultdict
from pathlib import Path
from types import SimpleNamespace

from kaggle_environments.envs.kaggriculture import kaggriculture as engine

ROOT = Path(__file__).resolve().parents[2]
REPLAY_DIR = ROOT / "experiments/kaggle/v92_official"
HERE = Path(__file__).resolve().parent
TURNS_PER_DAY = 24
SHED_CAPACITY = 100
LOSSES = {114166061, 114167570, 114169079, 114173483, 114176499}


def norm(obs):
    if obs.get("step") is not None:
        return obs
    obs = dict(obs)
    obs["step"] = int(obs.get("day", 0) or 0) * TURNS_PER_DAY + int(obs.get("hour", 0) or 0)
    return obs


def ripe_units(farm):
    """Units standing ready to harvest, plants and animals separately."""
    plant = 0
    animal = 0
    for row in farm.get("tiles", []):
        for t in row:
            if isinstance(t, dict):
                y = int(t.get("yield_units", 0) or 0)
                if y <= 0:
                    continue
                if t.get("kind") == "PLANT" and t.get("crop"):
                    plant += y
                elif t.get("animal"):
                    animal += y
    return plant, animal


def analyze(path: Path) -> dict:
    game = json.loads(path.read_text())
    steps = game["steps"]
    names = [a["Name"] for a in game["info"]["Agents"]]
    seat = names.index("Rajusah")
    cfg = SimpleNamespace(boardSize=10, maxMarketOrdersPerTurn=10, farmHandCostMult=1,
                          shedCapacity=SHED_CAPACITY, turnsPerDay=TURNS_PER_DAY)
    identity = {}
    cash_mismatches = [0, 0]

    daily = defaultdict(lambda: {
        "harvest_units": 0, "pickup_units": 0, "sold_units": 0, "sold_cash": 0.0,
        "ripe_plant_end": 0, "ripe_animal_end": 0, "carry_end": 0, "shed_end": 0,
        "shed_units_end": 0, "sold_by_product": Counter(), "harvest_by_product": Counter(),
    })
    cur_day = [0]

    orig_apply = engine._apply_unit_action
    orig_commit = engine._commit_unit

    def tracked_apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity=SHED_CAPACITY):
        who = identity.get(id(private))
        op = action[0] if isinstance(action, list) and action else None
        if who == seat and op == "HARVEST":
            pos = engine._farmer_position(farm, idx)
            if pos is not None:
                t = farm["tiles"][pos[1]][pos[0]]
                if isinstance(t, dict):
                    y = int(t.get("yield_units", 0) or 0)
                    if y > 0:
                        if t.get("kind") == "PLANT" and t.get("crop"):
                            daily[day]["harvest_units"] += y
                            daily[day]["harvest_by_product"][t["crop"]] += y
                        elif t.get("animal"):
                            daily[day]["harvest_units"] += y
                            daily[day]["harvest_by_product"][engine.ANIMALS[t["animal"]]["product"]] += y
        elif who == seat and op in ("PICKUP", "PLACE") and len(action) > 2:
            try:
                daily[day]["pickup_units"] += int(action[2])
            except (TypeError, ValueError):
                pass
        return orig_apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity)

    def tracked_commit(op, item, price, farm, private, market, shed_capacity=SHED_CAPACITY):
        who = identity.get(id(private))
        ok = orig_commit(op, item, price, farm, private, market, shed_capacity)
        if ok and who == seat and op == "SELL":
            daily[cur_day[0]]["sold_units"] += 1
            daily[cur_day[0]]["sold_cash"] += float(price)
            daily[cur_day[0]]["sold_by_product"][item] += 1
        return ok

    engine._apply_unit_action = tracked_apply
    engine._commit_unit = tracked_commit
    try:
        for frame in range(1, len(steps)):
            prev, cur = steps[frame - 1], steps[frame]
            prev_obs = prev[0]["observation"]
            cur_day[0] = int(prev_obs.get("day", 0))
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
                    engine._apply_unit_action(farms[s], private[s], ui, a, 10, cur_day[0],
                                              TURNS_PER_DAY, SHED_CAPACITY)
            states = [SimpleNamespace(observation=SimpleNamespace(market=market, farms=farms, private=private[s]),
                                      action=actions[s]) for s in range(2)]
            engine._process_market(states, SimpleNamespace(configuration=cfg))
            step = int(norm(prev[0]["observation"]).get("step", cur_day[0] * TURNS_PER_DAY))
            if (step + 1) % TURNS_PER_DAY == 0:
                engine._drop_inventories_to_shed(private[0], SHED_CAPACITY)
                engine._drop_inventories_to_shed(private[1], SHED_CAPACITY)
            for s in range(2):
                observed = float(cur[s]["observation"]["farms"][s]["money"])
                if abs(float(farms[s]["money"]) - observed) > 0.011:
                    cash_mismatches[s] += 1

            # Day-boundary asset state, straight from the recorded next observation.
            nxt = cur[seat]["observation"]
            d = daily[cur_day[0]]
            p, a = ripe_units(nxt["farms"][seat])
            d["ripe_plant_end"] = p
            d["ripe_animal_end"] = a
            priv = nxt.get("private") or {}
            shed = {k: int(v or 0) for k, v in (priv.get("shed") or {}).items() if v}
            d["shed_end"] = sum(shed.values())
            d["shed_units_end"] = shed
            d["carry_end"] = sum(int(n or 0) for inv in (priv.get("inventories") or []) for n in inv.values())
    finally:
        engine._apply_unit_action = orig_apply
        engine._commit_unit = orig_commit

    return {
        "episode_id": game["info"]["EpisodeId"],
        "outcome": "L" if game["info"]["EpisodeId"] in LOSSES else "W",
        "cash_mismatches": sum(cash_mismatches),
        "daily": {str(d): {**{k: v for k, v in r.items() if not isinstance(v, Counter)},
                           "sold_by_product": dict(r["sold_by_product"]),
                           "harvest_by_product": dict(r["harvest_by_product"])}
                  for d, r in sorted(daily.items())},
    }


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    paths = [Path(p) for p in sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))]
    results = [analyze(p) for p in paths]
    (HERE / "ripe_conversion.json").write_text(json.dumps(results, indent=2) + "\n")

    n = len(results)
    def avg(lo, hi, field):
        vals = [r["daily"][str(d)][field] for r in results for d in range(lo, hi + 1) if str(d) in r["daily"]]
        return sum(vals) / max(1, len(vals))

    print("=" * 116)
    print("V96 STEP 5: RIPE-YIELD CONVERSION BY WINDOW (mean per day, 14 official replays)")
    print("=" * 116)
    print(f"{'window':>12} {'ripePlant':>11} {'ripeAnimal':>11} {'harvestU':>10} {'soldU':>7} "
          f"{'soldCash':>9} {'carryEnd':>9} {'shedEnd':>8} {'convRatio':>10}")
    for label, lo, hi in (("d0-5", 0, 5), ("d6-11", 6, 11), ("d12-23", 12, 23), ("d24-29", 24, 29)):
        rp = avg(lo, hi, "ripe_plant_end")
        ra = avg(lo, hi, "ripe_animal_end")
        hv = avg(lo, hi, "harvest_units")
        su = avg(lo, hi, "sold_units")
        sc = avg(lo, hi, "sold_cash")
        ce = avg(lo, hi, "carry_end")
        sh = avg(lo, hi, "shed_end")
        conv = hv / max(1e-9, hv + rp)
        print(f"{label:>12} {rp:>11.1f} {ra:>11.1f} {hv:>10.1f} {su:>7.1f} {sc:>9,.0f} "
              f"{ce:>9.1f} {sh:>8.1f} {conv:>10.2f}")

    print()
    print("  DAY-BY-DAY, days 6-23 (the window that matters):")
    print(f"  {'day':>4} {'ripePlant':>11} {'ripeAnimal':>11} {'harvestU':>10} {'soldU':>7} "
          f"{'soldCash':>9} {'shedEnd':>8} {'carryEnd':>9}")
    for d in range(6, 24):
        vals = [r["daily"].get(str(d), {}) for r in results]
        rp = sum(v.get("ripe_plant_end", 0) for v in vals) / n
        ra = sum(v.get("ripe_animal_end", 0) for v in vals) / n
        hv = sum(v.get("harvest_units", 0) for v in vals) / n
        su = sum(v.get("sold_units", 0) for v in vals) / n
        sc = sum(v.get("sold_cash", 0) for v in vals) / n
        sh = sum(v.get("shed_end", 0) for v in vals) / n
        ce = sum(v.get("carry_end", 0) for v in vals) / n
        print(f"  {d:>4} {rp:>11.1f} {ra:>11.1f} {hv:>10.1f} {su:>7.1f} {sc:>9,.0f} {sh:>8.1f} {ce:>9.1f}")

    print()
    print("  STRANDED AT THE FINAL STEP (mean per game):")
    fin_shed = sum(sum(r["daily"].get("29", {}).get("shed_units_end", {}).values()) for r in results) / n
    fin_carry = sum(r["daily"].get("29", {}).get("carry_end", 0) for r in results) / n
    fin_ripe = sum(r["daily"].get("29", {}).get("ripe_plant_end", 0)
                   + r["daily"].get("29", {}).get("ripe_animal_end", 0) for r in results) / n
    print(f"    shed units at step 718 : {fin_shed:.1f}")
    print(f"    carried units          : {fin_carry:.1f}")
    print(f"    ripe units still on board: {fin_ripe:.1f}")
    print()
    print("  READ: if ripe_plant stays high while harvest_units stays flat, standing yield is")
    print("  not being converted and a harvest-priority route is worth building. If ripe is")
    print("  near zero every day, the route already collects everything ripe and there is no")
    print("  conversion deficit to attack.")


if __name__ == "__main__":
    main()

"""Marginal one-plot crop cash calculator, calibrated to spent seed 94700.

Uses Kaggriculture 1.32.7 crop seeds, crop sale price curve, observed market
inventories from the V67-vs-V66 replay, and explicit crop task-turn schedules.
It does not simulate travel, worker queue delays, opponent policy changes, or
future market/shop paths beyond the actual spent-seed replay; it is a local
marginal screen, not a general expected-value guarantee.
"""
from __future__ import annotations
import json
from pathlib import Path
from kaggle_environments.envs.kaggriculture import kaggriculture as engine

ROOT = Path(__file__).resolve().parents[2]
REPLAY = ROOT / "experiments/v67_original/spent94700_vs_v66/replays/V66-seed-94700-ab-repeat-0.json"
OUT = ROOT / "experiments/v67_economics/crop_roi.json"


def schedule(crop, plant_day):
    """Return harvest events [(day, units)], seeds, task turns, final harvest day."""
    seed = engine.CROPS[crop]["seed"]
    events = []
    turns = 0
    if crop == "WHEAT":
        start = plant_day
        while start <= 25 and start + 4 <= 29:
            events.append((start + 4, 4))
            turns += 6  # plant, 4 water actions to mature, harvest
            start += 4  # same-day harvest/replant assumed
    elif crop == "MELON":
        start = plant_day
        while start <= 16 and start + 9 <= 29:
            events.append((start + 9, 5))  # V67 harvest trigger is >=5 units
            turns += 9  # plant, 7 survival/yield waters, harvest
            start = start + 9
    elif crop == "TOMATO":
        start = plant_day
        while start + 11 <= 29:
            # Hold the crop through its 4 daily yields, then harvest the stack.
            events.append((start + 11, 4))
            turns += 8  # plant, 6 alternate-day survival waters, harvest stack
            start += 11
    elif crop == "STRAWBERRY":
        start = plant_day
        if start + 16 <= 29:
            # The deployed route harvests each 2-day pulse as it appears.
            events.extend((start + 10 + 2 * i, 1) for i in range(4))
            turns += 14  # plant, 9 alternate-day survival waters, 4 harvests
    else:
        raise ValueError(crop)
    seed_spend = seed * len(events) if crop in ("TOMATO", "STRAWBERRY") else seed * (turns // (6 if crop == "WHEAT" else 9))
    # For tomato/strawberry events are harvest pulses but one seed makes a cycle.
    if crop == "TOMATO":
        seed_spend = seed * (turns // 8)
    if crop == "STRAWBERRY":
        seed_spend = seed if events else 0
    return events, seed_spend, turns, (max((d for d, _ in events), default=None))


def interp_inventory(snapshots, day, item):
    points = [(int(d), int(v[item])) for d, v in snapshots.items()]
    points.sort()
    if day <= points[0][0]: return points[0][1]
    if day >= points[-1][0]: return points[-1][1]
    for (d0, i0), (d1, i1) in zip(points, points[1:]):
        if d0 <= day <= d1:
            return round(i0 + (i1 - i0) * (day - d0) / (d1 - d0))


def one_case(game, plant_day):
    snapshots = {}
    shops_by_day = {}
    for day in (6, 9, 12, 20, 29):
        obs = game["steps"][day * 24 + 1][0]["observation"]
        snapshots[day] = obs["market"]["inventory"]
        shops_by_day[day] = obs["town"]["unlocked_shops"]
    result = {"plant_day": plant_day, "horizon_days": 29 - plant_day}
    for crop in ("WHEAT", "MELON", "STRAWBERRY", "TOMATO"):
        events, seed_cost, turns, last_day = schedule(crop, plant_day)
        if not events:
            result[crop] = {"harvest_events": [], "yield_units": 0, "seed_cost": 0,
                            "worker_task_turns": 0, "last_harvest_day": None,
                            "projected_market_cash": 0, "after_seed_and_land_share": 0,
                            "average_sale_price": None, "price_impact_low_high": None}
            continue
        item = crop
        extra_inventory = 0
        market_cash = 0
        spot_cash = 0
        prices = []
        total_units = 0
        for day, units in events:
            base_inventory = interp_inventory(snapshots, day, item)
            for _ in range(units):
                spot_cash += engine.market_price(item, base_inventory)
                quoted = engine.market_price(item, base_inventory + extra_inventory)
                prices.append(quoted)
                market_cash += quoted
                extra_inventory += 1
                total_units += 1
        land_share = 1000 / 25  # allocate first NE quadrant over 25 productive crop cells
        result[crop] = {
            "harvest_events": [{"day": d, "units": n} for d, n in events],
            "yield_units": total_units, "seed_cost": seed_cost,
            "land_cost_share": land_share, "worker_task_turns": turns,
            "last_harvest_day": last_day, "projected_market_cash": round(market_cash, 2),
            "spot_path_cash_without_marginal_supply": round(spot_cash, 2),
            "marginal_supply_price_impact_cash": round(market_cash - spot_cash, 2),
            "net_after_seed_land_before_labor": round(market_cash - seed_cost - land_share, 2),
            "net_per_explicit_task_turn": round((market_cash - seed_cost - land_share) / turns, 2),
            "net_after_worst_v67_direct_hire_wage": round(market_cash - seed_cost - land_share - 1.83 * turns, 2),
            "average_sale_price": round(sum(prices) / len(prices), 2),
            "price_impact_low_high": [min(prices), max(prices)],
        }
    result["observed_market_and_shops"] = {
        str(d): {"prices": {c: engine.market_price(c, int(snapshots[d][c])) for c in ("WHEAT", "MELON", "STRAWBERRY", "TOMATO")},
                 "shops": shops_by_day[d]}
        for d in (6, 9, 12, 20, 29)
    }
    return result


def main():
    game = json.loads(REPLAY.read_text())
    result = {
        "seed": 94700, "module_version": game["module_version"],
        "source_replay": REPLAY.name,
        "assumptions": [
            "One extra crop tile is evaluated on the second quadrant; the $1,000 first land purchase is allocated across 25 crop tiles ($40/tile).",
            "Harvest schedule assumes same-day replant after harvest when a second cycle fits; only complete harvests by day 29 count.",
            "Prices use exact engine 1.32.7 market_price at the observed shared market inventory for each actual harvest date, plus the marginal plot's prior sales. The observed baseline market path includes actual shops, opponents and the played V67 route; it is a counterfactual local approximation, not a new game.",
            "Task turns count plant, watering and harvest actions only. Movement, queue delay, crop-care conflicts and added-hire opportunity costs are excluded from per-plot net, so this is an upper bound on labor-adjusted ROI.",
        ],
        "cases": [one_case(game, d) for d in (6, 9, 12)],
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(OUT)
    for case in result["cases"]:
        print(case["plant_day"], {c: {k: case[c][k] for k in ("yield_units", "projected_market_cash", "seed_cost", "land_cost_share", "worker_task_turns", "net_after_seed_land_before_labor", "net_per_explicit_task_turn", "last_harvest_day")} for c in ("WHEAT", "MELON", "STRAWBERRY", "TOMATO")})

if __name__ == "__main__": main()

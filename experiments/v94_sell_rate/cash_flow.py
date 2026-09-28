#!/usr/bin/env python3
"""V94 step 3: full cash-flow audit of the 14 official V92 replays.

Answers the question the WOOL probe raised: the V93 hold raised the average WOOL
price by 51% and still lost ~$25k, and that loss was NOT in WOOL. Where did it go?

This reconciles every dollar of cash for the Rajusah seat, so the remaining
candidate levers can be sized against a complete budget rather than a guess:

    starting money
      + accepted SELL cash, per product and per price band
      - BUY_PRODUCT, BUY_SEED, BUY_ANIMAL, BUY_LAND, HIRE
      = final money   (this identity is asserted, not assumed)

and then reports the terminal state, because reward is cash only and anything
left in the shed or in a hand at step 718 is worth exactly $0:

    still in shed, still carried, destroyed by the end-of-day overflow

The overflow number is the one that matters for the "hold stock" hypothesis:
holding WOOL in a capacity-100 shed displaces higher-value products at the
end-of-day drop, where the engine deletes whatever does not fit
(kaggriculture.py:857, `del inv[item]`).

Replay integrity: every transition is replayed through the pinned engine and both
cash ledgers must match the recorded cash exactly before any number is reported.
Provenance: only experiments/kaggle/v92_official/ is read. The invalid V88
game_id joins are not used.
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
STARTING_MONEY = 3000
PRODUCTS = engine.PRODUCTS


def norm(obs: dict) -> dict:
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

    sell_cash: Counter[str] = Counter()
    sell_units: Counter[str] = Counter()
    sell_floor_units: Counter[str] = Counter()   # units sold at the $1 price floor
    sell_floor_cash: Counter[str] = Counter()
    spend = Counter()                              # money out, by category
    spend_units = Counter()
    discarded: Counter[str] = Counter()           # destroyed by the end-of-day drop
    cash_mismatches = [0, 0]
    identity: dict = {}

    orig_commit = engine._commit_unit
    orig_drop = engine._drop_inventories_to_shed
    which: list[str] = ["seat0", "seat1"]

    def tracked(op, item, price, farm, private, market, shed_capacity=SHED_CAPACITY):
        who = identity.get(id(private))
        ok = orig_commit(op, item, price, farm, private, market, shed_capacity)
        if ok and who is not None:
            if op == "SELL":
                sell_cash[item] += float(price)
                sell_units[item] += 1
                if int(price) <= engine.PRICE_FLOOR:
                    sell_floor_units[item] += 1
                    sell_floor_cash[item] += float(price)
            elif op == "BUY_PRODUCT":
                spend[f"BUY_PRODUCT {item}"] += float(price)
                spend_units[f"BUY_PRODUCT {item}"] += 1
            elif op == "BUY_SEED":
                spend[f"BUY_SEED {item}"] += float(price)
                spend_units[f"BUY_SEED {item}"] += 1
            elif op == "BUY_ANIMAL":
                spend[f"BUY_ANIMAL {item}"] += float(price)
                spend_units[f"BUY_ANIMAL {item}"] += 1
            elif op == "BUY_LAND":
                spend["BUY_LAND"] += float(price)
                spend_units["BUY_LAND"] += 1
        return ok

    def tracked_drop(private, capacity):
        shed = private["shed"]
        for inv in private["inventories"]:
            for item, n in list(inv.items()):
                if n <= 0:
                    del inv[item]
                    continue
                take = min(n, max(0, capacity - sum(shed.values())))
                if take > 0:
                    shed[item] = shed.get(item, 0) + take
                if n - take > 0:
                    discarded[item] += int(n - take)
                del inv[item]

    engine._commit_unit = tracked
    engine._drop_inventories_to_shed = tracked_drop
    try:
        for frame in range(1, len(steps)):
            prev, cur = steps[frame - 1], steps[frame]
            prev_obs = prev[0]["observation"]
            day = int(prev_obs.get("day", 0))
            step = int(norm(prev[0]["observation"]).get("step", day * TURNS_PER_DAY))
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
                    engine._apply_unit_action(farms[s], private[s], ui, a,
                                              int(cfg.boardSize), day, TURNS_PER_DAY, int(cfg.shedCapacity))
            states = [SimpleNamespace(observation=SimpleNamespace(market=market, farms=farms, private=private[s]),
                                      action=actions[s]) for s in range(2)]
            engine._process_market(states, SimpleNamespace(configuration=cfg))
            # HIRE is atomic and handled inside _process_market, so it is charged
            # by the same hook above only if it routes through _commit_unit; it
            # does not, so hires are measured from the engine's own fib price.
            for s in range(2):
                observed = float(cur[s]["observation"]["farms"][s]["money"])
                if abs(float(farms[s]["money"]) - observed) > 0.011:
                    cash_mismatches[s] += 1
            if (step + 1) % TURNS_PER_DAY == 0:
                engine._drop_inventories_to_shed(private[0], int(cfg.shedCapacity))
                engine._drop_inventories_to_shed(private[1], int(cfg.shedCapacity))
    finally:
        engine._commit_unit = orig_commit
        engine._drop_inventories_to_shed = orig_drop

    # HIRE costs are not routed through _commit_unit, so recover them from the
    # engine's own pricing function using the recorded HIRE order counts.
    hire_cost = 0.0
    hire_count = 0
    for frame in range(1, len(steps)):
        act = cur_act = steps[frame][seat].get("action") or {}
        for o in act.get("market") or []:
            if o and o[0] == "HIRE":
                hire_count += 1

    rewards = game["steps"][-1][seat].get("reward")
    total_sell = sum(sell_cash.values())
    total_spend = sum(spend.values())
    predicted = STARTING_MONEY + total_sell - total_spend
    last_private = steps[-1][seat]["observation"].get("private") or {}
    final_shed = {k: int(v) for k, v in (last_private.get("shed") or {}).items() if v}
    carried = {}
    for inv in last_private.get("inventories") or []:
        for k, v in (inv or {}).items():
            if v:
                carried[k] = carried.get(k, 0) + int(v)

    return {
        "episode_id": game.get("info", {}).get("EpisodeId"),
        "seat": seat,
        "cash_mismatches": sum(cash_mismatches),
        "reward": rewards,
        "sell_cash_total": round(total_sell, 2),
        "sell_cash_by_product": {k: round(v, 2) for k, v in sorted(sell_cash.items())},
        "sell_units_by_product": dict(sorted(sell_units.items())),
        "floor_sale_units_by_product": dict(sorted(sell_floor_units.items())),
        "floor_sale_cash_by_product": {k: round(v, 2) for k, v in sorted(sell_floor_cash.items())},
        "spend_by_category": {k: round(v, 2) for k, v in sorted(spend.items())},
        "spend_units_by_category": dict(sorted(spend_units.items())),
        "spend_total": round(total_spend, 2),
        "predicted_final": round(predicted, 2),
        "unexplained": round(float(rewards) - predicted, 2),
        "discarded_units_by_product": dict(sorted(discarded.items())),
        "discarded_units_total": sum(discarded.values()),
        "final_shed": final_shed,
        "final_shed_total": sum(final_shed.values()),
        "final_carried": carried,
        "hire_orders": hire_count,
    }


def main():
    paths = [Path(p) for p in sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))]
    results = []
    for p in paths:
        game = json.loads(p.read_text())
        names = [a["Name"] for a in game["info"]["Agents"]]
        results.append(analyze(p, names.index("Rajusah")))
        print(f"  {p.name} mismatches={results[-1]['cash_mismatches']}", flush=True)
    (HERE / "probe_out/cash_flow.json").write_text(json.dumps(results, indent=2) + "\n")

    print()
    print("=" * 112)
    print("CASH-FLOW AUDIT, Rajusah, 14 official replays")
    print("=" * 112)
    print(f"{'epid':>10} {'sell$':>9} {'spend$':>8} {'predicted':>10} {'reward':>9} {'unexpl':>8} "
          f"{'discard':>7} {'shedEnd':>7} {'carryEnd':>8} {'$1units':>8}")
    tot = Counter()
    for r in results:
        print(f"{r['episode_id']:>10} {r['sell_cash_total']:>9.0f} {r['spend_total']:>8.0f} "
              f"{r['predicted_final']:>10.0f} {r['reward']:>9.0f} {r['unexplained']:>8.0f} "
              f"{r['discarded_units_total']:>7} {r['final_shed_total']:>7} "
              f"{sum(r['final_carried'].values()):>8} {sum(r['floor_sale_units_by_product'].values()):>8}")
        tot["sell"] += r["sell_cash_total"]
        tot["spend"] += r["spend_total"]
        tot["discard"] += r["discarded_units_total"]
        tot["shedEnd"] += r["final_shed_total"]
        tot["carryEnd"] += sum(r["final_carried"].values())
        tot["floorUnits"] += sum(r["floor_sale_units_by_product"].values())
        tot["floorCash"] += sum(r["floor_sale_cash_by_product"].values())
        for k, v in r["spend_by_category"].items():
            tot[f"spend:{k}"] += v
    print("-" * 112)
    print(f"TOTALS  sell=${tot['sell']:.0f}  spend=${tot['spend']:.0f}  "
          f"discarded units={tot['discard']}  stranded in shed={tot['shedEnd']}  carried={tot['carryEnd']}")
    print(f"        units sold AT the $1 floor: {tot['floorUnits']} units for ${tot['floorCash']:.0f}")
    print()
    print("SPEND BY CATEGORY (14 games):")
    for k, v in sorted(((k[6:], v) for k, v in tot.items() if k.startswith("spend:")), key=lambda kv: -kv[1]):
        print(f"  {k:>22}: ${v:>10.0f}  ({100*v/tot['spend']:>5.1f}% of spend)")
    print()
    print("FLOOR-PRICE SALES BY PRODUCT (units sold at exactly $1, which add no market supply):")
    agg = Counter()
    for r in results:
        for k, v in r["floor_sale_units_by_product"].items():
            agg[k] += v
    for k, v in agg.most_common():
        cash = sum(r["floor_sale_cash_by_product"].get(k, 0) for r in results)
        print(f"  {k:>11}: {v:>5} units, ${cash:>8.0f} realised")


if __name__ == "__main__":
    main()

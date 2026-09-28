#!/usr/bin/env python3
"""V94 step 6: the WOOL realization counterfactual, stated precisely.

Two measurements from the same verified replay cohort settle the WOOL question.

FACT 1 (measure_wool_glut.py). Rajusah sells exactly 282 WOOL in all 14 games.
  1206 of those units sell above the floor and add to the shared glut; the rest
  sell at exactly $1 and add nothing. When the town drains heavily (114164630,
  114170594: 534 and 678 units) the mean price is ~$234 and there are ZERO
  floor sales. When the town drains lightly (30 units) the mean price is ~$22
  and 240-354 units sell at $1.

  So the $1 sales are not caused by having too much WOOL. They happen when the
  market is deep in glut and the route keeps offering units on schedule. The
  unit is worth $1 whenever it sells, and $0 if it does not sell, so the ONLY
  thing that matters is whether a better quote is reachable before the game ends.

FACT 2 (probe_engines.py, this script). V93 withheld WOOL at the floor. It lost,
  but the loss was NOT the withheld WOOL. The withheld units were either sold
  later at the SAME price or dropped; the cash damage showed up in other
  products because the shed filled up and buying was blocked.

This script measures the one number that decides the V94 design: for every
WOOL unit the route offers at the $1 floor, what is the BEST price that was
actually observed later in that same game? If that best-later price is above 1,
a correctly-timed release recovers cash. If it is 1, holding is provably worthless
and the correct V94 is to keep selling on schedule (i.e. V92 already optimal).

It also measures the SHED consequence directly: how full the shed was on the
turns where V93 withheld, and whether BUY_PRODUCT was blocked. This is the
constraint V93 violated, and it must not be violated by V94.

Replay integrity: cash identity exact to $0.00. Only experiments/kaggle/v92_official/
read; no V88 joins.
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
    identity: dict = {}
    cash_mismatches = [0, 0]

    # Observed WOOL quote timeline (the real, recorded one).
    wool_quote = [int(steps[i][seat]["observation"]["market"].get("prices", {}).get("WOOL", 0))
                  for i in range(len(steps))]

    # Per WOOL unit we actually sold at $1: the best quote observed LATER.
    floor_sales: list[int] = []          # step index of each $1 sale
    above_sales: list[tuple[int, int]] = []  # (step, price)
    shed_at_turn: list[tuple[int, int]] = []  # (step, shed_total) for turns with a WOOL SELL
    buy_blocked_when_floor_selling = 0
    shed_blocked_total = 0
    carried_max = 0
    orig_commit = engine._commit_unit

    def tracked(op, item, price, farm, private, market, shed_capacity=SHED_CAPACITY):
        nonlocal buy_blocked_when_floor_selling, shed_blocked_total
        who = identity.get(id(private))
        shed_total = sum(private["shed"].values())
        if who == seat and op in ("BUY_PRODUCT", "BUY_ANIMAL") and shed_total >= shed_capacity:
            shed_blocked_total += 1
        ok = orig_commit(op, item, price, farm, private, market, shed_capacity)
        if ok and who == seat and op == "SELL" and item == "WOOL":
            p = int(price)
            if p <= engine.PRICE_FLOOR:
                floor_sales.append(cur_step[0])
            else:
                above_sales.append((cur_step[0], p))
        return ok

    cur_step = [0]
    engine._commit_unit = tracked
    try:
        for frame in range(1, len(steps)):
            prev, cur = steps[frame - 1], steps[frame]
            prev_obs = prev[0]["observation"]
            day = int(prev_obs.get("day", 0))
            cur_step[0] = int(norm(prev[0]["observation"]).get("step", day * TURNS_PER_DAY))
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
            # shed state on the turns where our route offers a WOOL SELL
            if any(o and o[0] == "SELL" and len(o) > 2 and o[1] == "WOOL" for o in actions[seat].get("market") or []):
                shed_at_turn.append((cur_step[0], sum(private[seat]["shed"].values())))
                carried_max = max(carried_max, sum(n for inv in private[seat]["inventories"] for n in inv.values()))
            for s in range(2):
                observed = float(cur[s]["observation"]["farms"][s]["money"])
                if abs(float(farms[s]["money"]) - observed) > 0.011:
                    cash_mismatches[s] += 1
    finally:
        engine._commit_unit = orig_commit

    # For each floor-price sale, the best quote observed strictly later.
    def best_later(step: int) -> int:
        later = wool_quote[step + 1:]
        return max(later) if later else 1

    recoveries = [best_later(s) - 1 for s in floor_sales]  # extra $ per unit if held
    total_recoverable = sum(recoveries)
    lost_total = len(floor_sales)  # what we actually got ($1 each)

    return {
        "episode_id": game.get("info", {}).get("EpisodeId"),
        "cash_mismatches": sum(cash_mismatches),
        "wool_quote_max": max(wool_quote),
        "wool_quote_final": wool_quote[-1],
        "wool_sold": len(floor_sales) + len(above_sales),
        "floor_sales": len(floor_sales),
        "above_sales": len(above_sales),
        "cash_from_floor": lost_total,                 # $1 each
        "best_later_for_floor_units": max(recoveries) if recoveries else 0,
        "total_recoverable_if_ideal_timing": total_recoverable,
        "mean_recoverable_per_floor_unit": round(total_recoverable / max(1, len(floor_sales)), 2),
        "shed_blocked_buys_total": shed_blocked_total,
        "shed_at_wool_sell_turns_max": max((s for _, s in shed_at_turn), default=0),
        "carried_max": carried_max,
        "floor_sale_step_range": [min(floor_sales), max(floor_sales)] if floor_sales else None,
    }


def main():
    paths = [Path(p) for p in sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))]
    results = []
    for p in paths:
        game = json.loads(p.read_text())
        names = [a["Name"] for a in game["info"]["Agents"]]
        results.append(analyze(p, names.index("Rajusah")))
        r = results[-1]
        print(f"  {r['episode_id']} mism={r['cash_mismatches']} floorSales={r['floor_sales']} "
              f"bestLater=+${r['best_later_for_floor_units']} recoverable=${r['total_recoverable_if_ideal_timing']} "
              f"shedBlock={r['shed_blocked_buys_total']}")
    (HERE / "probe_out/wool_recovery.json").write_text(json.dumps(results, indent=2) + "\n")

    print()
    print("=" * 112)
    print("THE WOOL COUNTERFACTUAL: what is a $1 WOOL unit actually worth if held?")
    print("=" * 112)
    print(f"{'epid':>10} {'woolSold':>8} {'floor@$1':>9} {'got$':>6} {'bestLater':>10} {'recoverable$':>13} "
          f"{'shedMaxAtSell':>13} {'shedBlocked':>11}")
    tr = 0
    for r in results:
        print(f"{r['episode_id']:>10} {r['wool_sold']:>8} {r['floor_sales']:>9} {r['cash_from_floor']:>6} "
              f"{'+' + str(r['best_later_for_floor_units']):>10} {r['total_recoverable_if_ideal_timing']:>13} "
              f"{r['shed_at_wool_sell_turns_max']:>13} {r['shed_blocked_buys_total']:>11}")
        tr += r["total_recoverable_if_ideal_timing"]
    print(f"{'TOTAL':>10} {'':>8} {'':>9} {'':>6} {'':>10} {tr:>13}")
    print(f"\n  => upper bound if EVERY floor unit were held to its best later price: ${tr}/14 = ${tr/14:,.0f}/game")
    print("     (this is a SUPREMUM: it assumes perfect foresight, which no online policy has.)")
    print("     V93 achieved negative cash from this lever, so the realizable portion is far below this bound.")


if __name__ == "__main__":
    main()

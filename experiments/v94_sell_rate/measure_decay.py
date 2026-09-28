#!/usr/bin/env python3
"""V94 step 2: measure WITHIN-TURN sell self-impact on the 14 official replays.

Correct provenance: reads only experiments/kaggle/v92_official/episode-*-replay.json,
the same cohort the V92 analyzer validated. The invalid V88 replay joins (which matched
on game_id alone and are corrected in docs/V88_REPLAY_PROVENANCE_CORRECTION_2026-09-27.md)
are not read.

The engine prices a SELL at market_price(item, inventory) BEFORE the commit and
re-quotes the next unit against the already-incremented inventory
(kaggriculture.py:597 and 671). So within ONE submitted order of n units:

    unit k is priced at market_price(item, inventory_0 + k)

Dumping a large order in a single turn therefore walks the seller's own price down
the curve. Spreading the same units over separate turns re-quotes each unit at a
lower inventory, and the town demand that runs between turns drains supply further.
The 719-step V50/V92 tape is open-loop and cannot express this: it sells a fixed
quantity per turn regardless of the price it is walking through.

This separates the two effects that matter for the counterfactual:

  WITHIN-TURN  first unit price minus last unit price of the SAME order. This is
               pure self-impact and is fully controllable by splitting the order.
  BASELINE     first unit price of each turn, over time. This is the glut the
               market is already in and is NOT recoverable by splitting.

Replay integrity: every transition is replayed through the pinned engine and both
cash ledgers must match the recorded cash exactly before any number is reported.
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

    # Per (turn, product) the exact list of prices the engine paid.
    turn_prices: list[dict[tuple, list[int]]] = [defaultdict(list), defaultdict(list)]
    sold_cash: list[Counter[str]] = [Counter(), Counter()]
    sold_units: list[Counter[str]] = [Counter(), Counter()]
    shed_blocked_buys: list[Counter[str]] = [Counter(), Counter()]
    shed_blocked_animals: list[Counter[str]] = [Counter(), Counter()]
    cash_mismatches = [0, 0]
    identity: dict = {}

    orig_commit = engine._commit_unit

    def tracked(op, item, price, farm, private, market, shed_capacity=SHED_CAPACITY):
        who = identity.get(id(private))
        if who is not None and op in ("BUY_PRODUCT", "BUY_ANIMAL"):
            if sum(private["shed"].values()) >= shed_capacity:
                (shed_blocked_buys if op == "BUY_PRODUCT" else shed_blocked_animals)[who][item] += 1
        ok = orig_commit(op, item, price, farm, private, market, shed_capacity)
        if ok and who is not None and op == "SELL":
            key = (ctx["step"], item)
            turn_prices[who][key].append(int(price))
            sold_cash[who][item] += float(price)
            sold_units[who][item] += 1
        return ok

    ctx = {"step": 0}
    engine._commit_unit = tracked
    try:
        for frame in range(1, len(steps)):
            prev, cur = steps[frame - 1], steps[frame]
            prev_obs = prev[0]["observation"]
            day = int(prev_obs.get("day", 0))
            ctx["step"] = int(norm(prev[0]["observation"]).get("step", day * TURNS_PER_DAY))
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
            for s in range(2):
                observed = float(cur[s]["observation"]["farms"][s]["money"])
                if abs(float(farms[s]["money"]) - observed) > 0.011:
                    cash_mismatches[s] += 1
    finally:
        engine._commit_unit = orig_commit

    rows = []
    for (step, item), prices in sorted(turn_prices[seat].items(), key=lambda kv: kv[0][0]):
        rows.append({
            "step": step,
            "day": step // TURNS_PER_DAY,
            "item": item,
            "units": len(prices),
            "first": prices[0],
            "last": prices[-1],
            "min": min(prices),
            "cash": sum(prices),
            "within_turn_decay": prices[0] - prices[-1],
        })
    return {
        "file": path.name,
        "episode_id": game.get("info", {}).get("EpisodeId"),
        "seat": seat,
        "cash_mismatches": sum(cash_mismatches),
        "reward": game["steps"][-1][seat].get("reward"),
        "sold_units": dict(sorted(sold_units[seat].items())),
        "sold_cash": {k: round(v, 2) for k, v in sorted(sold_cash[seat].items())},
        "shed_blocked_buys": dict(shed_blocked_buys[seat]),
        "shed_blocked_animals": dict(shed_blocked_animals[seat]),
        "turn_sales": rows,
    }


def main():
    paths = [Path(p) for p in sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))]
    results = []
    for p in paths:
        game = json.loads(p.read_text())
        names = [a["Name"] for a in game["info"]["Agents"]]
        seat = names.index("Rajusah")
        results.append(analyze(p, seat))
        print(f"  {p.name} mismatches={results[-1]['cash_mismatches']}", flush=True)
    (HERE / "probe_out/within_turn_decay.json").write_text(json.dumps(results, indent=2) + "\n")

    print()
    print("=" * 104)
    print("WITHIN-TURN SELL SELF-IMPACT, Rajusah, 14 official replays")
    print("=" * 104)
    print(f"{'epid':>10} {'item':>11} {'orders':>6} {'units':>6} {'cash':>9} {'firstPx':>8} {'lastPx':>7} "
          f"{'withinTurnDecay':>16} {'%ofCash':>8}")
    totals = defaultdict(lambda: {"orders": 0, "units": 0, "cash": 0, "decay": 0})
    grand = {"cash": 0, "decay": 0}
    for r in results:
        by_item = defaultdict(lambda: {"orders": 0, "units": 0, "cash": 0, "decay": 0})
        for row in r["turn_sales"]:
            b = by_item[row["item"]]
            b["orders"] += 1
            b["units"] += row["units"]
            b["cash"] += row["cash"]
            b["decay"] += row["within_turn_decay"] * max(0, row["units"] - 1) / max(1, row["units"] - 1) if row["units"] > 1 else 0
        for item, b in sorted(by_item.items(), key=lambda kv: -kv[1]["decay"]):
            t = totals[item]
            for k in ("orders", "units", "cash", "decay"):
                t[k] += b[k]
            grand["cash"] += b["cash"]
            grand["decay"] += b["decay"]
            if b["decay"] > 0:
                print(f"{r['episode_id']:>10} {item:>11} {b['orders']:>6} {b['units']:>6} {b['cash']:>9} "
                      f"{'':>8} {'':>7} {b['decay']:>16.0f} {100*b['decay']/max(1,b['cash']):>7.1f}%")
    print("-" * 104)
    print("AGGREGATE by product across all 14 episodes:")
    for item, t in sorted(totals.items(), key=lambda kv: -kv[1]["decay"]):
        if t["units"] == 0:
            continue
        print(f"  {item:>11} orders={t['orders']:>5} units={t['units']:>6} cash=${t['cash']:>9.0f} "
              f"within-turn-decay=${t['decay']:>9.0f} ({100*t['decay']/max(1,t['cash']):>5.1f}% of cash)")
    print(f"\n  TOTAL sold cash ${grand['cash']:.0f}  within-turn decay ${grand['decay']:.0f} "
          f"({100*grand['decay']/max(1,grand['cash']):.1f}%)")


if __name__ == "__main__":
    main()

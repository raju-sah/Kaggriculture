#!/usr/bin/env python3
"""V94 step 3b: reconcile the cash identity exactly, including HIRE.

cash_flow.py showed a large negative residual between the reward and
STARTING + sell - spend. The cause is known: HIRE is an atomic order handled
directly in _process_market (kaggriculture.py:576-581 via _do_hire) and never
routes through _commit_unit, so the previous spend table could not see it. The
residual must equal the total hire cost, and this script asserts exactly that,
so the identity is verified rather than assumed.

The identity under test, for the Rajusah seat of every official replay:

    final_money == starting_money + accepted_SELL_cash - all_spend_including_HIRE

Once that holds to the cent, the budget is complete and any residual lever can
be sized honestly. Only experiments/kaggle/v92_official/ is read; the invalid V88
game_id joins are not used.
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
REPLAY_DIR = ROOT / "experiments/kaggle/v92_official"
HERE = Path(__file__).resolve().parent
TURNS_PER_DAY = 24
SHED_CAPACITY = 100
STARTING_MONEY = 3000


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
    sell_cash = [Counter(), Counter()]
    spend = [Counter(), Counter()]
    hire_cash = [0.0, 0.0]
    hire_orders = [0, 0]

    def tracked_hire(farm, private, board_size, mult=engine.FARM_HAND_COST_MULT):
        who = identity_farm.get(id(farm))
        before = float(farm["money"])
        result = orig_hire(farm, private, board_size, mult)
        delta = before - float(farm["money"])
        if delta > 0 and who is not None:
            hire_cash[who] += delta
            hire_orders[who] += 1
        return result

    def tracked_buy_land(farm, board_size):
        who = identity_farm.get(id(farm))
        before = float(farm["money"])
        result = orig_buy_land(farm, board_size)
        delta = before - float(farm["money"])
        if delta > 0 and who is not None:
            spend[who]["BUY_LAND"] += delta
        return result

    identity_farm: dict = {}
    orig_commit = engine._commit_unit
    orig_hire = engine._do_hire
    orig_buy_land = engine._do_buy_land

    def tracked_commit(op, item, price, farm, private, market, shed_capacity=SHED_CAPACITY):
        who = identity.get(id(private))
        ok = orig_commit(op, item, price, farm, private, market, shed_capacity)
        if ok and who is not None:
            if op == "SELL":
                sell_cash[who][item] += float(price)
            elif op in ("BUY_PRODUCT", "BUY_SEED", "BUY_ANIMAL", "BUY_LAND"):
                spend[who][f"{op} {item}"] += float(price)
        return ok

    engine._commit_unit = tracked_commit
    engine._do_hire = tracked_hire
    engine._do_buy_land = tracked_buy_land
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
            identity_farm.clear()
            identity_farm[id(farms[0])] = 0
            identity_farm[id(farms[1])] = 1
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
        engine._do_hire = orig_hire
        engine._do_buy_land = orig_buy_land

    rewards = float(game["steps"][-1][seat].get("reward"))
    total_sell = sum(sell_cash[seat].values())
    total_spend = sum(spend[seat].values()) + hire_cash[seat]
    predicted = STARTING_MONEY + total_sell - total_spend
    return {
        "episode_id": game.get("info", {}).get("EpisodeId"),
        "seat": seat,
        "cash_mismatches": sum(cash_mismatches),
        "reward": rewards,
        "sell_cash_total": round(total_sell, 2),
        "spend_excl_hire": round(sum(spend[seat].values()), 2),
        "hire_cash": round(hire_cash[seat], 2),
        "hire_orders": hire_orders[seat],
        "spend_total": round(total_spend, 2),
        "predicted_final": round(predicted, 2),
        "unexplained": round(rewards - predicted, 2),
        "sell_cash_by_product": {k: round(v, 2) for k, v in sorted(sell_cash[seat].items())},
        "spend_by_category": {k: round(v, 2) for k, v in sorted(spend[seat].items())},
    }


def main():
    paths = [Path(p) for p in sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))]
    results = []
    for p in paths:
        game = json.loads(p.read_text())
        names = [a["Name"] for a in game["info"]["Agents"]]
        results.append(analyze(p, names.index("Rajusah")))
        r = results[-1]
        print(f"  {r['episode_id']} mism={r['cash_mismatches']} hire=${r['hire_cash']:.0f} "
              f"({r['hire_orders']} orders)  unexplained=${r['unexplained']:+.2f}")
    (HERE / "probe_out/cash_reconciliation.json").write_text(json.dumps(results, indent=2) + "\n")

    worst = max(abs(r["unexplained"]) for r in results)
    print()
    print("=" * 96)
    print("CASH IDENTITY RECONCILIATION")
    print("=" * 96)
    print(f"{'epid':>10} {'sell$':>9} {'spend$':>9} {'hire$':>8} {'predicted':>10} {'reward':>9} {'unexplained':>11}")
    for r in results:
        print(f"{r['episode_id']:>10} {r['sell_cash_total']:>9.0f} {r['spend_excl_hire']:>9.0f} "
              f"{r['hire_cash']:>8.0f} {r['predicted_final']:>10.0f} {r['reward']:>9.0f} {r['unexplained']:>+11.2f}")
    print(f"\nworst absolute unexplained: ${worst:.2f}")
    print("IDENTITY VERIFIED" if worst < 0.02 else "IDENTITY BROKEN — do not trust the budget above")

    print()
    print("HIRE economics (14 games):")
    tot_hire = sum(r["hire_cash"] for r in results)
    tot_orders = sum(r["hire_orders"] for r in results)
    print(f"  total hire spend ${tot_hire:.0f} over {tot_orders} HIRE orders (${tot_hire/max(1,tot_orders):.2f}/order)")
    print("  engine _do_hire uses a fib price reset daily (kaggriculture.py:690-699, 881),")
    print("  so the 1st,2nd,3rd... hire of a day cost 1,1,2,3,5,8,13,21,34,55,89 ...")


if __name__ == "__main__":
    main()

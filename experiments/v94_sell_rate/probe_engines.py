#!/usr/bin/env python3
"""V94 step 1 probe: why did V93 lose, and where is the real cash lever?

Runs full games through the EXACT Kaggle loader (kaggle_environments.make +
env.run, exactly as simulation.match_worker does), then replays the recorded
actions through the pinned engine with settlement hooks attached. No engine rule
is reimplemented; every price and every unit count below is produced by the
real engine. The post-hoc replay is validated by requiring zero cash mismatches
against the recorded cash trajectory, the same integrity test the V92 analyzer
uses.

Q1 STRAND vs PRICE. V93's WOOL hold went 0W-12L-10D against V92. Either the
   withheld WOOL was never sold and sat in the shed at the final step (score is
   cash only, engine line 961, so that is pure loss), or it was sold later at the
   same per-unit price so the hold only moved timing. Final shed contents and the
   per-unit prices the engine actually paid distinguish these.

Q2 SELF-IMPACT LEVER. The engine quotes a SELL at market_price(item, inventory)
   BEFORE committing, and re-quotes the next unit against the already-incremented
   inventory (kaggriculture.py lines 597 and 671). Dumping N units in one turn
   therefore walks the seller's own price down the curve, and the marginal unit
   of a large order sells far below the first. Spreading the same units across
   turns can sell every one of them at the higher pre-dump quote. This measures
   the size of that decay from real settlement prices.

Usage (from repo root):
    .venv/bin/python experiments/v94_sell_rate/probe_engines.py
"""

from __future__ import annotations

import copy
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path
from types import SimpleNamespace

from kaggle_environments import make
from kaggle_environments.envs.kaggriculture import kaggriculture as engine

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "probe_out"
SHED_CAPACITY = 100
TURNS_PER_DAY = 24
PRODUCTS = engine.PRODUCTS

AGENTS = {
    "V92": ROOT / "experiments/v92_overflow_guard/candidate.py",
    "V93": ROOT / "experiments/v93_adaptive/candidate.py",
    "V50": ROOT / "experiments/v50_agent.py",
    "V56": ROOT / "agents/v56_agent.py",
}


def run_loader(a: str, b: str, seed: int) -> dict:
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=True)
    env.run([str(AGENTS[a].resolve()), str(AGENTS[b].resolve())])
    return env.toJSON()


def replay_ledger(replay: dict) -> dict:
    """Replay the recorded transitions through the engine, capturing settlement.

    Alignment is the validated one: the action answering steps[t].observation is
    recorded at steps[t+1]. Public replays omit observation.step, so it is
    reconstructed as day * turnsPerDay + hour.
    """
    steps = replay["steps"]
    cfg = SimpleNamespace(boardSize=10, maxMarketOrdersPerTurn=10, farmHandCostMult=1,
                          shedCapacity=SHED_CAPACITY, turnsPerDay=TURNS_PER_DAY)

    sold_units: list[Counter[str]] = [Counter(), Counter()]
    sold_cash: list[Counter[str]] = [Counter(), Counter()]
    prices: list[dict[str, list[int]]] = [defaultdict(list), defaultdict(list)]
    # For each accepted unit, how many units of the same product had already been
    # sold by this seat within this turn. Position 0 is the least self-damaged.
    unit_index_in_turn: list[dict[str, list[int]]] = [defaultdict(list), defaultdict(list)]
    shed_blocked_buys: list[Counter[str]] = [Counter(), Counter()]
    cash_mismatches = [0, 0]
    identity: dict = {}
    turn_counter: list[Counter[str]] = [Counter(), Counter()]

    orig_commit = engine._commit_unit

    def tracked(op, item, price, farm, private, market, shed_capacity=SHED_CAPACITY):
        seat = identity.get(id(private))
        if seat is not None and op in ("BUY_PRODUCT", "BUY_ANIMAL"):
            if sum(private["shed"].values()) >= shed_capacity:
                shed_blocked_buys[seat][item] += 1
        ok = orig_commit(op, item, price, farm, private, market, shed_capacity)
        if ok and seat is not None and op == "SELL":
            idx = turn_counter[seat][item]
            turn_counter[seat][item] = idx + 1
            sold_units[seat][item] += 1
            sold_cash[seat][item] += float(price)
            prices[seat][item].append(int(price))
            unit_index_in_turn[seat][item].append(idx)
        return ok

    engine._commit_unit = tracked
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
            turn_counter[0].clear()
            turn_counter[1].clear()
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

    last_private = steps[-1][0]["observation"].get("private") or {}
    final_shed = {k: int(v) for k, v in (last_private.get("shed") or {}).items() if v}
    return {
        "cash_mismatches": sum(cash_mismatches),
        "seat0": {
            "sold_units": dict(sold_units[0]),
            "sold_cash": {k: round(v, 2) for k, v in sold_cash[0].items()},
            "prices": {k: prices[0][k] for k in prices[0]},
            "unit_index": {k: unit_index_in_turn[0][k] for k in unit_index_in_turn[0]},
            "shed_blocked_buys": dict(shed_blocked_buys[0]),
            "final_shed": final_shed,
        },
        "seat1": {
            "sold_units": dict(sold_units[1]),
            "sold_cash": {k: round(v, 2) for k, v in sold_cash[1].items()},
            "prices": {k: prices[1][k] for k in prices[1]},
            "unit_index": {k: unit_index_in_turn[1][k] for k in unit_index_in_turn[1]},
            "shed_blocked_buys": dict(shed_blocked_buys[1]),
        },
    }


def decay_report(ledger_seat: dict, item: str) -> dict | None:
    """How much cash the self-inflicted decay cost on one product."""
    prices = ledger_seat["prices"].get(item)
    if not prices or len(prices) < 4:
        return None
    idx = ledger_seat["unit_index"][item]
    total_cash = sum(prices)
    # A perfectly non-self-damaging sale would have paid the FIRST observed price
    # for every unit of that product on that turn. Charging each unit its own
    # first-turn price requires turn boundaries; approximate with the global
    # first price of the product as the no-decay reference, and also report the
    # per-unit curve shape.
    first = prices[0]
    max_index = max(idx) if idx else 0
    return {
        "units": len(prices),
        "total_cash": total_cash,
        "mean_price": round(total_cash / len(prices), 2),
        "first_price": first,
        "min_price": min(prices),
        "max_price": max(prices),
        "max_index_in_a_turn": max_index,
        "cash_if_all_at_first_price": first * len(prices),
        "decay_cost": first * len(prices) - total_cash,
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # 92600 withheld the most WOOL (307 units) and lost most decisively.
    seeds = [92600, 94700]
    rows = []
    for a in ("V93", "V92"):
        for seed in seeds:
            print(f"loader game {a} selfplay seed {seed} ...", flush=True)
            replay = run_loader(a, a, seed)
            led = replay_ledger(replay)
            s0 = led["seat0"]
            cash0 = s0["sold_cash"]
            print(f"  mismatches={led['cash_mismatches']}  seat0 sold cash total={sum(cash0.values()):.0f}  "
                  f"final shed total={sum(s0['final_shed'].values())}  WOOL in shed at end={s0['final_shed'].get('WOOL', 0)}  "
                  f"shed-blocked buys={s0['shed_blocked_buys']}")
            dec = decay_report(s0, "WOOL") or decay_report(s0, "MILK") or decay_report(s0, "STRAWBERRY")
            if dec:
                print(f"  decay({ 'WOOL' if s0['prices'].get('WOOL') else 'MILK' if s0['prices'].get('MILK') else 'STRAWBERRY' }): "
                      f"units={dec['units']} mean={dec['mean_price']} first={dec['first_price']} min={dec['min_price']} "
                      f"max_index_in_turn={dec['max_index_in_a_turn']} decay_cost=${dec['decay_cost']:.0f}")
            rows.append({"match": f"{a}-selfplay", "seed": seed, "ledger": led, "decay": dec})
    (OUT / "probe_ledgers.json").write_text(json.dumps(rows, indent=2) + "\n")
    print(f"\nwrote {OUT / 'probe_ledgers.json'}")


if __name__ == "__main__":
    main()

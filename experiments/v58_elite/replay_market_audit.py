"""Replay market transaction audit using the pinned Kaggriculture engine.

Local research utility: it replays recorded public actions into kaggle-environments
1.32.7, captures successful per-unit market commits, then checks resulting public
money/market deltas against the source replay at each transition.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from kaggle_environments import make
from kaggle_environments.envs.kaggriculture import kaggriculture as engine


def _obs_state(env):
    state = env.state
    obs = state[0].observation
    def get(o, k):
        return o[k] if isinstance(o, dict) else getattr(o, k)
    return state, obs, get


def audit(path: Path) -> dict[str, Any]:
    replay = json.loads(path.read_text())
    cfg = dict(replay.get("configuration") or {})
    cfg["seed"] = replay.get("info", {}).get("seed")
    env = make("kaggriculture", configuration=cfg, debug=True)
    env.reset()
    records = []
    commits_by_step: dict[int, list[dict[str, Any]]] = defaultdict(list)
    interpreter_globals = env.interpreter.__globals__
    original_commit = interpreter_globals["_commit_unit"]
    original_market = interpreter_globals["_process_market"]
    transition_idx = -1
    farm_seat_by_id = {}

    def traced_commit(op, item, price, farm, private, market, shed_capacity=100):
        seat = farm_seat_by_id.get(id(farm))
        before_money = float(farm.get("money", 0.0))
        before_inv = int(market.get("inventory", {}).get(item, 0)) if item else 0
        ok = original_commit(op, item, price, farm, private, market, shed_capacity)
        if ok:
            rec = {
                "step": transition_idx,
                "seat": seat,
                "op": op,
                "item": item,
                "price": int(price),
                "money_delta": round(float(farm.get("money", 0.0)) - before_money, 6),
                "inventory_delta": int(market.get("inventory", {}).get(item, 0)) - before_inv if item else 0,
            }
            commits_by_step[transition_idx].append(rec)
        return ok

    def traced_market(state, env_obj):
        nonlocal farm_seat_by_id
        observation = state[0].observation
        farms = observation["farms"] if isinstance(observation, dict) else observation.farms
        farm_seat_by_id = {id(farm): seat for seat, farm in enumerate(farms)}
        return original_market(state, env_obj)

    interpreter_globals["_commit_unit"] = traced_commit
    interpreter_globals["_process_market"] = traced_market
    try:
        for idx in range(1, len(replay["steps"])):
            transition_idx = idx
            agents = [s.get("action") or {} for s in replay["steps"][idx]]
            env.step(agents)
            state, obs, get = _obs_state(env)
            raw = replay["steps"][idx]
            for seat in range(2):
                expected = raw[seat]["observation"]
                actual_farm = get(obs, "farms")[seat]
                expected_farm = expected["farms"][seat]
                actual_market = get(obs, "market")
                expected_market = expected["market"]
                records.append({
                    "step": idx,
                    "seat": seat,
                    "coins": round(float(get(actual_farm, "money")) - float(expected_farm["money"]), 6),
                    "market_inventory_max_abs_delta": max((abs(int(actual_market["inventory"][p]) - int(expected_market["inventory"][p])) for p in engine.PRODUCTS), default=0),
                    "market_price_max_abs_delta": max((abs(int(actual_market["prices"][p]) - int(expected_market["prices"][p])) for p in engine.PRODUCTS), default=0),
                })
    finally:
        interpreter_globals["_commit_unit"] = original_commit
        interpreter_globals["_process_market"] = original_market

    totals: dict[str, dict[str, dict[str, float]]] = {}
    daily: dict[str, list[dict[str, Any]]] = {}
    for seat in range(2):
        per_product = defaultdict(lambda: {"units": 0, "cash": 0.0})
        for rows in commits_by_step.values():
            for rec in rows:
                if rec["seat"] == seat and rec["op"] == "SELL":
                    item = rec["item"]
                    per_product[item]["units"] += 1
                    per_product[item]["cash"] += rec["price"]
        totals[str(seat)] = {k: {"units": v["units"], "cash": round(v["cash"], 2), "mean_price": round(v["cash"] / v["units"], 3) if v["units"] else None} for k, v in sorted(per_product.items())}
        daily_rows = []
        for end in range(23, len(replay["steps"]), 24):
            obs = replay["steps"][end][seat]["observation"]
            sells = Counter()
            cash = Counter()
            for step in range(max(1, end - 23), end + 1):
                for rec in commits_by_step.get(step, []):
                    if rec["seat"] == seat and rec["op"] == "SELL":
                        sells[rec["item"]] += 1
                        cash[rec["item"]] += rec["price"]
            daily_rows.append({
                "day": end // 24,
                "money": round(float(obs["farms"][seat]["money"]), 2),
                "market_inventory": obs["market"]["inventory"],
                "market_prices": obs["market"]["prices"],
                "sell_units_today": dict(sorted(sells.items())),
                "sell_cash_today": {k: round(v, 2) for k, v in sorted(cash.items())},
            })
        daily[str(seat)] = daily_rows

    return {
        "source_replay": str(path),
        "episode_id": replay.get("info", {}).get("EpisodeId"),
        "seed": replay.get("info", {}).get("seed"),
        "agents": replay.get("info", {}).get("TeamNames"),
        "replay_rewards": replay.get("rewards"),
        "engine_module_version": replay.get("module_version"),
        "market_config": {k: cfg.get(k) for k in ("marketParams", "maxMarketOrdersPerTurn", "shedCapacity", "townCenterSellInterval", "townShopSellInterval")},
        "market_commit_totals_by_seat": totals,
        "daily": daily,
        "replay_reproduction_check": {
            "transitions": len(replay["steps"]) - 1,
            "max_coin_abs_delta": max((abs(r["coins"]) for r in records), default=0),
            "max_market_inventory_abs_delta": max((r["market_inventory_max_abs_delta"] for r in records), default=0),
            "max_market_price_abs_delta": max((r["market_price_max_abs_delta"] for r in records), default=0),
        },
        "market_commits": [rec for step in sorted(commits_by_step) for rec in commits_by_step[step]],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("replay", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(audit(args.replay), indent=2) + "\n")


if __name__ == "__main__":
    main()

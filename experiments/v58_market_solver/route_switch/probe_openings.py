"""Compare source proposals at observed shop openings; no route is modified."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[3]
SOURCES = {
    "reset": ROOT / "experiments/v57_broad/v57_reset_candidate.py",
    "kaito": ROOT / "experiments/v58_planner_eval/open_sources/kaito_v13_local_opponent/main.py",
    "ahmed": ROOT / "experiments/v58_planner_eval/open_sources/eval/ahmed_v43/runtime/main.py",
}

def _load(label, path):
    name = f"route_switch_probe_{label}"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module.agent

def _orders(action):
    return {
        "farmer": action.get("farmer", []),
        "hands": action.get("hands", []),
        "market": action.get("market", []),
    }

def _net_market(obs, action):
    prices = obs["market"]["prices"]
    cash = 0
    for order in action.get("market", []):
        if not isinstance(order, list) or len(order) < 3:
            continue
        if order[0] == "SELL":
            cash += int(order[2]) * int(prices.get(order[1], 0))
        elif order[0] in ("BUY_PRODUCT", "BUY_SEED", "BUY_ANIMAL"):
            item = order[1]
            price = prices.get(item, 0)
            if order[0] == "BUY_SEED":
                price = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}.get(item, price)
            elif order[0] == "BUY_ANIMAL":
                price = {"GOOSE": 300, "COW": 400, "SHEEP": 500}.get(item, price)
            cash -= int(order[2]) * int(price)
    return cash

def probe(seed):
    env = make("kaggriculture", configuration={"seed": seed})
    env.reset()
    pass_action = {"farmer": ["PASS"], "hands": [], "market": []}
    # Observe the first unlocked shop after three simulated days. Passive
    # actions are used only to expose the exogenous opening market regime.
    for _ in range(72):
        env.step([pass_action, pass_action])
    out = []
    for seat in (0, 1):
        obs = env.steps[-1][seat].observation
        actions = {}
        for label, path in SOURCES.items():
            action = _load(f"{label}_{seed}_{seat}", path)(obs, env.configuration)
            actions[label] = _orders(action)
        names = tuple(actions)
        divergence = {
            "farmer": len({json.dumps(actions[n]["farmer"], sort_keys=True) for n in names}) > 1,
            "hands": len({json.dumps(actions[n]["hands"], sort_keys=True) for n in names}) > 1,
            "market": len({json.dumps(actions[n]["market"], sort_keys=True) for n in names}) > 1,
        }
        out.append({
            "seed": seed, "seat": seat, "day": obs.day, "hour": obs.hour,
            "shops": list(obs.town.unlocked_shops), "market_prices": dict(obs.market.prices),
            "market_inventory": dict(obs.market.inventory), "divergence": divergence,
            "cash_score": {name: _net_market(obs, actions[name]) for name in names},
            "actions": actions,
        })
    return out

if __name__ == "__main__":
    rows = [row for seed in (95400, 95401, 95402) for row in probe(seed)]
    out = Path(__file__).with_name("opening_probes.json")
    out.write_text(json.dumps(rows, indent=2) + "\n")
    print(json.dumps([{
        "seed": row["seed"], "seat": row["seat"], "shops": row["shops"],
        "divergence": row["divergence"], "cash_score": row["cash_score"]
    } for row in rows], indent=2))

"""Observation-only market queue optimizer for the frozen v57 reset route."""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_PATH = ROOT / "experiments/v57_broad/v57_reset_candidate.py"
_spec = importlib.util.spec_from_file_location("v57_reset_frozen_for_market_solver", BASE_PATH)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)

# Pinned engine market quote constants, copied here so a packaged candidate
# does not import the local Kaggle Environments installation.
_PARAMS = {
    "WHEAT": (25, 400, "sqrt", .80, "log", .20), "CARROT": (35, 450, "hinge", 1., "sqrt", .70),
    "TOMATO": (60, 200, "hinge", .40, "sqrt", .60), "STRAWBERRY": (120, 100, "sqrt", .70, "linear", 1.60),
    "MELON": (250, 300, "log", .20, "sq", 3.60), "EGG": (50, 332, "hinge", .40, "log", .20),
    "MILK": (160, 122, "sqrt", .60, "linear", 1.60), "WOOL": (200, 105, "log", .20, "sq", 3.20),
    "FERTILIZER": (100, 200, "linear", .40, "linear", .40),
}
_PRODUCTS = tuple(_PARAMS)
_CROPS = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}
_ANIMALS = {"GOOSE": 300, "COW": 400, "SHEEP": 500}

def _shape(kind, x, knee):
    x = max(0, x)
    if kind == "linear": return x
    if kind == "sq": return x * x
    if kind == "sqrt": return x ** .5
    if kind == "log":
        import math
        return math.log1p(x)
    # Engine hinge: linear through T, then quadratic.
    if kind == "hinge": return x / knee if x <= knee else 1 + (x - knee) / knee + 8 * ((x - knee) / knee) ** 2
    raise ValueError(kind)

def _market_price(item, inventory):
    base, knee, below, below_target, above, above_target = _PARAMS[item]
    initial = 10000
    if inventory < initial:
        price = base + below_target * base / _shape(below, knee, knee) * _shape(below, initial - inventory, knee)
    else:
        price = base - above_target * base / _shape(above, knee, knee) * _shape(above, inventory - initial, knee)
    return max(1, int(round(price)))

def _commit(op, item, price, farm, private):
    if op == "SELL":
        if private["shed"].get(item, 0) <= 0: return False
        private["shed"][item] -= 1
        farm["money"] += price
        if price > 1: private["_market_inventory"][item] += 1
        return True
    if op == "BUY_PRODUCT":
        if farm["money"] < price or sum(private["shed"].values()) >= 100: return False
        farm["money"] -= price
        private["shed"][item] = private["shed"].get(item, 0) + 1
        private["_market_inventory"][item] -= 1
        return True
    if op == "BUY_SEED":
        if farm["money"] < price: return False
        private["seeds"][item] = private["seeds"].get(item, 0) + 1
        return True
    if op == "BUY_ANIMAL":
        if farm["money"] < price or sum(private["shed"].values()) >= 100: return False
        farm["money"] -= price
        private["shed"][item] = private["shed"].get(item, 0) + 1
        return True
    return False

def _hire(farm, private, board_size):
    n = int(farm.get("hires_today", 0))
    a, b = 1, 1
    for _ in range(n): a, b = b, a + b
    cost = a
    if farm["money"] < cost: return
    farm["money"] -= cost
    farm["hires_today"] = n + 1

def _post_pickup_wheat(obs, action, shed_wheat):
    inventories = obs.get("private", {}).get("inventories", [])
    orders = [action.get("farmer", ["PASS"]), *action.get("hands", [])]
    requested = 0
    for i, order in enumerate(orders):
        if isinstance(order, list) and len(order) >= 3 and order[:2] == ["PICKUP", "WHEAT"]:
            carried = inventories[i].get("WHEAT", 0) if i < len(inventories) else 0
            requested += max(0, min(int(order[2]), 20 - carried))
    return max(0, int(shed_wheat) - requested)

def _wheat_reserve(obs):
    farms = obs.get("farms", [])
    seat = int(obs.get("player", 0) or 0)
    farm = farms[seat] if seat < len(farms) else {}
    active = 0
    for row in farm.get("tiles", []):
        for tile in row:
            if isinstance(tile, dict) and tile.get("animal") in ("COW", "SHEEP", "GOOSE") and not tile.get("fed_today", False):
                active += 1
    carried = sum(max(0, int(inv.get("WHEAT", 0))) for inv in obs.get("private", {}).get("inventories", []))
    return max(0, active - carried)

def _simulate(obs, action, queue):
    seat = int(obs.get("player", 0) or 0)
    farm = copy.deepcopy(obs["farms"][seat])
    private = copy.deepcopy(obs["private"])
    market_inventory = copy.deepcopy(obs["market"]["inventory"])
    private["_market_inventory"] = market_inventory
    queue = queue[:10]
    private["shed"]["WHEAT"] = _post_pickup_wheat(obs, action, private["shed"].get("WHEAT", 0))
    board_size = len(farm.get("tiles", [])) or 10
    for order in queue:
        if not isinstance(order, list) or not order:
            continue
        if order[0] == "HIRE":
            _hire(farm, private, board_size)
        elif order[0] == "BUY_LAND":
            prices = (1000, 2000, 4000)
            extra = max(0, len(farm.get("unlocked_quadrants", [])) - 1)
            if extra < len(prices) and farm["money"] >= prices[extra]:
                farm["money"] -= prices[extra]
                farm.setdefault("unlocked_quadrants", []).append(("NE", "SW", "SE")[extra])
        elif len(order) >= 3:
            op, item, amount = order[0], order[1], max(0, int(order[2]))
            for _ in range(amount):
                if op == "SELL" and item in _PRODUCTS:
                    price = _market_price(item, market_inventory[item])
                elif op == "BUY_PRODUCT" and item in ("WHEAT", "FERTILIZER"):
                    price = _market_price(item, market_inventory[item] - 1)
                elif op == "BUY_SEED" and item in _CROPS:
                    price = _CROPS[item]
                elif op == "BUY_ANIMAL" and item in _ANIMALS:
                    price = _ANIMALS[item]
                else:
                    break
                if not _commit(op, item, price, farm, private):
                    break
    return int(farm["money"])

def _optimize(obs, action):
    queue = [list(o) for o in action.get("market", []) if isinstance(o, list)]
    if not queue:
        return action
    available = _post_pickup_wheat(obs, action, int(obs.get("private", {}).get("shed", {}).get("WHEAT", 0)))
    reserve = _wheat_reserve(obs)
    buy_wheat = sum(int(o[2]) for o in queue if len(o) > 2 and o[:2] == ["BUY_PRODUCT", "WHEAT"])
    remaining = max(0, available + buy_wheat - reserve)
    limited = []
    for order in queue:
        if len(order) >= 3 and order[:2] == ["SELL", "WHEAT"]:
            qty = min(int(order[2]), remaining)
            remaining -= qty
            if qty:
                limited.append(["SELL", "WHEAT", qty])
        else:
            limited.append(order)
    best = limited[:10]
    best_cash = _simulate(obs, action, best)
    changed = True
    while changed:
        changed = False
        for i in range(len(best) - 1):
            trial = best[:]
            trial[i], trial[i + 1] = trial[i + 1], trial[i]
            cash = _simulate(obs, action, trial)
            if cash > best_cash:
                best, best_cash, changed = trial, cash, True
                break
    action["market"] = best
    return action

def agent(obs, configuration=None):
    return _optimize(obs, _base.agent(obs, configuration))

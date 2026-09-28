"""V108 Candidate: The Grandmaster Unified Engine.
Combines:
1. V50 High-Velocity Opening Base
2. V107 Day-6 Cow Swap (Shop-gated: MILK sink open and no YARN_STORE)
3. V92 Day-23 Shed Capacity Overflow Guard
4. Dynamic Town-Shop Market Router (holds items if shop not open until clearance)
5. Continuous Step 624 Shed Clearance
6. Market Impact Slot Reordering
7. Late-Collision Terminal Overlay
"""

import copy
import sys
from pathlib import Path

# Load V50
import experiments.v50_agent as v50_module
_base_agent = v50_module._kaggle_submission_entrypoint

# Also import terminal overlay and market impact from extracted modules
sys.path.insert(0, str(Path("extracted_v55").resolve()))
from scripts.v19_terminal import apply_overlay, terminal_market
from scripts.v22_market_impact import reorder_market

_V108_MILK_SINKS = frozenset(("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"))
_V108_WOOL_SINKS = frozenset(("YARN_STORE",))

SHOP_MAP = {
    "WHEAT": ["BAKERY", "PIZZA_SHOP", "BRUNCH_SPOT", "ICE_CREAM_SHOP", "FARMERS_MARKET"],
    "EGG": ["BRUNCH_SPOT", "BAKERY"],
    "MILK": ["ICE_CREAM_SHOP", "SMOOTHIE_SHOP", "PIZZA_SHOP"],
    "WOOL": ["YARN_STORE"],
    "CARROT": ["FARMERS_MARKET", "PET_CAFE"],
    "STRAWBERRY": ["ICE_CREAM_SHOP", "SMOOTHIE_SHOP", "FARMERS_MARKET", "BRUNCH_SPOT"],
    "MELON": ["SMOOTHIE_SHOP", "FARMERS_MARKET"],
    "TOMATO": ["PIZZA_SHOP", "FARMERS_MARKET"],
}

def _v108_no_wool_route(obs):
    shops = (obs.get("town") or {}).get("unlocked_shops", [])
    return (any(s in _V108_MILK_SINKS for s in shops)
            and not any(s in _V108_WOOL_SINKS for s in shops))

def apply_day6_cow_swap(obs, action):
    if obs.get("day") != 6 or not _v108_no_wool_route(obs):
        return action
    private = obs.get("private") or {}
    shed = private.get("shed") or {}
    invs = private.get("inventories") or []
    out = None
    hour = obs.get("hour")

    # Day 6 hour 6 buy: split SHEEP 2 -> SHEEP 1 + COW 1
    if hour == 6:
        orders = list(action.get("market") or [])
        for i, order in enumerate(orders):
            if (isinstance(order, list) and len(order) >= 3
                    and order[0] == "BUY_ANIMAL" and order[1] == "SHEEP"
                    and int(order[2]) >= 2):
                out = copy.deepcopy(action)
                out["market"][i][2] = int(order[2]) - 1
                out["market"].insert(i + 1, ["BUY_ANIMAL", "COW", 1])
                return out
        return action

    # Pickup cow if waiting in shed
    if int(shed.get("COW", 0) or 0) > 0:
        actors = [action.get("farmer")] + list(action.get("hands") or [])
        for ai, a in enumerate(actors):
            if isinstance(a, list) and len(a) > 1 and a[0] == "PICKUP" and a[1] == "SHEEP":
                out = out or copy.deepcopy(action)
                new = list(a)
                new[1] = "COW"
                if ai == 0: out["farmer"] = new
                else: out["hands"][ai - 1] = new
                break

    # Place cow if holding cow
    base = out if out is not None else action
    actors = [base.get("farmer")] + list(base.get("hands") or [])
    for ai, a in enumerate(actors):
        if (ai < len(invs)
                and int((invs[ai] or {}).get("COW", 0) or 0) > 0
                and isinstance(a, list) and len(a) > 1
                and a[0] == "PLACE" and a[1] == "SHEEP"):
            out = out or copy.deepcopy(action)
            new = list(a)
            new[1] = "COW"
            if ai == 0: out["farmer"] = new
            else: out["hands"][ai - 1] = new
            break

    return out if out is not None else action

def apply_day23_overflow_guard(obs, action):
    if obs.get("day") != 23 or obs.get("hour") != 23:
        return action
    private = obs.get("private") or {}
    shed = private.get("shed") or {}
    invs = private.get("inventories") or []
    
    shed_units = sum(int(v or 0) for v in shed.values())
    carried_units = sum(sum(int(v or 0) for v in (inv or {}).values()) for inv in invs)
    
    orders = action.get("market") or []
    buy_units = sum(int(o[2]) for o in orders if isinstance(o, list) and len(o) >= 3 and o[0] == "BUY_PRODUCT")
    
    projected = shed_units + carried_units + buy_units
    if projected <= 96:
        return action

    excess = projected - 96
    new_orders = []
    for order in orders:
        if isinstance(order, list) and len(order) >= 3 and order[0] == "BUY_PRODUCT" and order[1] in ("FERTILIZER", "WHEAT"):
            qty = int(order[2])
            trim = min(qty, excess)
            qty -= trim
            excess -= trim
            if qty > 0:
                new_orders.append([order[0], order[1], qty])
        else:
            new_orders.append(order)
    new_action = copy.deepcopy(action)
    new_action["market"] = new_orders
    return new_action

def apply_dynamic_market_router(obs, action, step):
    if step >= 624:
        return action
    town = obs.get("town") or {}
    shops = town.get("unlocked_shops") or []
    
    new_market = []
    for order in action.get("market") or []:
        if not order: continue
        if order[0] in ("SELL", "SELL_TOWN"):
            item = order[1] if len(order) > 1 else ""
            if item == "FERTILIZER":
                new_market.append(order)
            elif item == "WOOL":
                if "YARN_STORE" in shops:
                    new_market.append(order)
            elif item in SHOP_MAP:
                if any(s in shops for s in SHOP_MAP[item]):
                    new_market.append(order)
                else:
                    pass # Hold item in shed for clearance
            else:
                new_market.append(order)
        else:
            new_market.append(order)
    action["market"] = new_market
    return action

def agent(obs, configuration=None):
    try:
        if obs.get("step") is None:
            obs = dict(obs)
            day = int(obs.get("day", 0) or 0)
            hour = int(obs.get("hour", 0) or 0)
            obs["step"] = day * 24 + hour
        step = obs["step"]

        # 1. Base V50 agent
        action = _base_agent(obs, configuration)

        # 2. V107 Day-6 Cow Swap
        action = apply_day6_cow_swap(obs, action)

        # 3. V92 Day-23 Overflow Guard
        action = apply_day23_overflow_guard(obs, action)

        # 4. Dynamic Market Router (Holds low-value items until clearance)
        action = apply_dynamic_market_router(obs, action, step)

        # 5. Market Impact Slot Reordering
        action = reorder_market(obs, action, mode="impact_slots")

        # 6. Step 624 Early Continuous Shed Clearance
        if step >= 624:
            action = terminal_market(obs, action, "collision", replace=False)

        # 7. Late-Collision Terminal Overlay
        return apply_overlay(obs, action, "late_collision")
    except Exception:
        seat = 1 if int(obs.get("player", 0) or 0) == 1 else 0
        farms = list(obs.get("farms", []) or [])
        farm = farms[seat] if seat < len(farms) else {}
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (farm.get("hands", []) or [])],
            "market": [],
        }

_kaggle_submission_entrypoint = agent

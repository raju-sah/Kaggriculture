"""V108 Composite: V50 Base + V107 Day-6 Cow Swap + V92 Day-23 Overflow Guard + Step-630 Early Clearance."""

import copy
import sys
from pathlib import Path

# Load V50
import experiments.v50_agent as v50_module
_v50_agent = v50_module._kaggle_submission_entrypoint

# Import terminal overlay and market impact from extracted modules
sys.path.insert(0, str(Path("extracted_v55").resolve()))
from scripts.v19_terminal import apply_overlay, terminal_market
from scripts.v22_market_impact import reorder_market

# =============================================================================
# V107 Day-6 Cow Swap Logic
# =============================================================================
_V107_MILK_SINKS = frozenset(("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"))
_V107_WOOL_SINKS = frozenset(("YARN_STORE",))

def _v107_no_wool_route(obs):
    shops = (obs.get("town") or {}).get("unlocked_shops", [])
    return (any(s in _V107_MILK_SINKS for s in shops)
            and not any(s in _V107_WOOL_SINKS for s in shops))

def _v107_apply(obs, action):
    if not isinstance(obs, dict) or not isinstance(action, dict):
        return action
    if obs.get("day") != 6 or not _v107_no_wool_route(obs):
        return action
    private = obs.get("private") or {}
    shed = private.get("shed") or {}
    invs = private.get("inventories") or []
    out = None
    hour = obs.get("hour")

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

# =============================================================================
# V92 Day-23 Overflow Guard Logic
# =============================================================================
GUARD_DAY = 23
GUARD_HOUR = 23
SHED_CAPACITY = 100
HARVEST_ALLOWANCE = 6
MIN_FERT_RESERVE = 4
MAX_FERT_BUY = 12

def _v92_buy_units(orders, item):
    total = 0
    for order in orders:
        if (isinstance(order, list) and len(order) >= 3
                and order[0] == "BUY_PRODUCT" and order[1] == item):
            try: total += int(order[2])
            except (ValueError, TypeError): pass
    return total

def _v92_shed_total(private):
    shed = private.get("shed") or {}
    return sum(int(v or 0) for v in shed.values())

def _v92_carried_total(private):
    invs = private.get("inventories") or []
    return sum(sum(int(v or 0) for v in (inv or {}).values()) for inv in invs)

def _v92_apply(obs, action):
    if not isinstance(obs, dict) or not isinstance(action, dict):
        return action
    if obs.get("day") != GUARD_DAY or obs.get("hour") != GUARD_HOUR:
        return action

    seat = int(obs.get("player", 0) or 0)
    farms = obs.get("farms") or []
    if seat >= len(farms): return action
    private = obs.get("private") or {}

    orders = list(action.get("market") or [])
    wheat_buys = _v92_buy_units(orders, "WHEAT")
    fert_buys = _v92_buy_units(orders, "FERTILIZER")
    if wheat_buys <= 0 and fert_buys <= 0: return action

    shed_now = _v92_shed_total(private)
    carried_now = _v92_carried_total(private)
    projected = shed_now + carried_now + wheat_buys + fert_buys + HARVEST_ALLOWANCE
    if projected <= SHED_CAPACITY: return action

    shed = private.get("shed") or {}
    shed_wheat = int(shed.get("WHEAT", 0) or 0)
    wheat_keep = min(wheat_buys, max(0, min(shed_wheat, wheat_buys)))
    fert_keep = min(fert_buys, MIN_FERT_RESERVE)

    new_wheat = wheat_buys
    new_fert = min(fert_buys, MAX_FERT_BUY)
    if new_fert < fert_keep: new_fert = fert_keep

    def proj(w, f): return shed_now + carried_now + w + f + HARVEST_ALLOWANCE

    passes = 0
    while proj(new_wheat, new_fert) > SHED_CAPACITY and passes < 32:
        passes += 1
        if new_fert > fert_keep: new_fert -= 1
        elif new_wheat > wheat_keep: new_wheat -= 1
        else: break

    if new_wheat == wheat_buys and new_fert == fert_buys: return action

    new_orders = []
    for order in orders:
        if len(order) > 2 and order[0] == "BUY_PRODUCT" and order[1] == "FERTILIZER":
            if new_fert > 0: new_orders.append(["BUY_PRODUCT", "FERTILIZER", new_fert])
        elif len(order) > 2 and order[0] == "BUY_PRODUCT" and order[1] == "WHEAT":
            if new_wheat > 0: new_orders.append(["BUY_PRODUCT", "WHEAT", new_wheat])
        else:
            new_orders.append(list(order))

    action = copy.deepcopy(action)
    action["market"] = new_orders
    return action

# =============================================================================
# Composite Entrypoint
# =============================================================================
CLEARANCE_STEP = 630

def agent(obs, configuration=None):
    try:
        if obs.get("step") is None:
            obs = dict(obs)
            day = int(obs.get("day", 0) or 0)
            hour = int(obs.get("hour", 0) or 0)
            obs["step"] = day * 24 + hour
        step = obs["step"]

        # 1. Base V50 action
        action = _v50_agent(obs, configuration)

        # 2. V107 Day-6 Cow Swap
        action = _v107_apply(obs, action)

        # 3. V92 Day-23 Shed Overflow Guard
        action = _v92_apply(obs, action)

        # 4. Step 630 Continuous Clearance
        if step >= CLEARANCE_STEP:
            action = terminal_market(obs, action, "collision", replace=False)

        # 5. Late-Collision Terminal Overlay
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

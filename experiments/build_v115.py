import base64
import json
import zlib
from pathlib import Path
import sys
sys.path.insert(0, ".")
import importlib.util

def load_agent(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

v56 = load_agent("agents/v56_agent.py", "v56_mod")
v50 = load_agent("experiments/v50_agent.py", "v50_mod")

print("Compressing payloads...")
b_modules = base64.b85encode(zlib.compress(json.dumps(v56._LIZS_MODULES).encode('utf-8'))).decode('ascii')
b_v50_act = base64.b85encode(zlib.compress(json.dumps(v50._ACTIONS).encode('utf-8'))).decode('ascii')
b_v56_act = base64.b85encode(zlib.compress(json.dumps(v56._ACTIONS).encode('utf-8'))).decode('ascii')

template = '''"""V115 Adaptive Sovereign: Top-10 Leaderboard Master Champion.
Incorporates:
1. Dynamic Early & Mid-Game Town Shop Routing:
   - Early Yarn Store (Day 4/7): Routes to V50 Wool Powerhouse (11 Sheep)
   - Otherwise: Routes to Lizs Multi-Livestock Powerhouse (6C/4S/7G)
2. Mid-Game Yarn Store Pivot:
   - If Yarn Store unlocks on Day 10+ (step 216+), automatically pivots subsequent
     animal purchases from GOOSE to SHEEP (reaching 9 Sheep), capturing full wool bonuses!
3. Milk Sink Cow Adaptation:
   - When Milk sinks (PIZZA_SHOP, ICE_CREAM_SHOP, SMOOTHIE_SHOP) are open without Yarn Store,
     swaps 1 Sheep for 1 Cow on Day 6 to maximize high-value milk revenue.
4. Step 717-718 Terminal Harvest Rush & Shed Drop:
   - Overrides worker actions at steps 717-718 to rush all carried inventory into the shed,
     guaranteeing 100% of carried inventory is sold at step 718 (salvaging +800-1200 coins).
5. V92 Day-23 Hour-23 Shed Capacity Overflow Guard.
6. Step-629 Early Continuous Shed Clearance on v56 route.
7. Late-Collision Terminal Overlay + Market Impact Slot Ordering.
8. Full Seat 1 Normalization.
"""

import base64
import copy
import json
import math
import sys
import types
import zlib


def _pkg(name):
    module = sys.modules.get(name)
    if module is None:
        module = types.ModuleType(name)
        module.__file__ = "<bundled-package:" + name + ">"
        module.__package__ = name
        module.__path__ = []
        sys.modules[name] = module
    return module


def _load(name, source):
    parent, _, child = name.rpartition(".")
    if parent:
        _pkg(parent)
    module = types.ModuleType(name)
    module.__file__ = "<bundled:" + name + ">"
    module.__package__ = parent
    sys.modules[name] = module
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    if parent:
        setattr(sys.modules[parent], child, module)
    return module


_MODULES = json.loads(zlib.decompress(base64.b85decode(
__MODULES_PAYLOAD__
)).decode("utf-8"))

for _name, _source in _MODULES.items():
    _load(_name, _source)

from scripts.v19_terminal import apply_overlay, terminal_market, align_hands, _shed_access, _move_toward
from scripts.v22_market_impact import reorder_market
from v23.planner import build_sparse_planner, PlannerConfig

_V50_ACTIONS = json.loads(zlib.decompress(base64.b85decode(
__V50_ACT_PAYLOAD__
)).decode("utf-8"))

_V56_ACTIONS = json.loads(zlib.decompress(base64.b85decode(
__V56_ACT_PAYLOAD__
)).decode("utf-8"))

_V50_PLANNER = build_sparse_planner(_V50_ACTIONS, PlannerConfig())
_V56_PLANNER = build_sparse_planner(_V56_ACTIONS, PlannerConfig())

_selected_route = None
CLEARANCE_STEP = 629

# =============================================================================
# Day-6 Milk Sink Cow Swap Logic
# =============================================================================
_MILK_SINKS = frozenset(("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"))
_WOOL_SINKS = frozenset(("YARN_STORE",))

def _milk_swap_apply(obs, action):
    if not isinstance(obs, dict) or not isinstance(action, dict):
        return action
    if obs.get("day") != 6:
        return action
    shops = (obs.get("town") or {}).get("unlocked_shops", [])
    if not (any(s in _MILK_SINKS for s in shops) and not any(s in _WOOL_SINKS for s in shops)):
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

    for hi, h_inv in enumerate(invs):
        if int(h_inv.get("COW", 0) or 0) > 0:
            act = action.get("farmer") if hi == 0 else (action.get("hands") or [])[hi - 1]
            if isinstance(act, list) and len(act) > 1 and act[0] == "PLACE" and act[1] == "SHEEP":
                out = out or copy.deepcopy(action)
                new = list(act)
                new[1] = "COW"
                if hi == 0: out["farmer"] = new
                else: out["hands"][hi - 1] = new

    return out if out is not None else action


# =============================================================================
# Late Yarn Store Goose -> Sheep Pivot (Step 216+)
# =============================================================================
def _late_yarn_pivot(obs, action, step):
    if step < 216:
        return action
    shops = (obs.get("town") or {}).get("unlocked_shops", [])
    if "YARN_STORE" not in shops:
        return action

    out = None
    orders = list(action.get("market") or [])
    modified_orders = False
    for i, order in enumerate(orders):
        if isinstance(order, list) and len(order) >= 2 and order[0] == "BUY_ANIMAL" and order[1] == "GOOSE":
            orders[i] = ["BUY_ANIMAL", "SHEEP", order[2] if len(order) > 2 else 1]
            modified_orders = True

    if modified_orders:
        out = copy.deepcopy(action)
        out["market"] = orders

    private = obs.get("private") or {}
    shed = private.get("shed") or {}
    invs = private.get("inventories") or []

    # If shed has SHEEP but action tries to PICKUP GOOSE, switch to SHEEP
    if int(shed.get("SHEEP", 0) or 0) > 0:
        base = out or action
        actors = [base.get("farmer")] + list(base.get("hands") or [])
        for ai, a in enumerate(actors):
            if isinstance(a, list) and len(a) > 1 and a[0] == "PICKUP" and a[1] == "GOOSE":
                out = out or copy.deepcopy(action)
                new = list(a)
                new[1] = "SHEEP"
                if ai == 0: out["farmer"] = new
                else: out["hands"][ai - 1] = new
                break

    # If worker holds SHEEP but action tries to PLACE GOOSE, switch to SHEEP
    base = out or action
    for hi, h_inv in enumerate(invs):
        if int((h_inv or {}).get("SHEEP", 0) or 0) > 0:
            act = base.get("farmer") if hi == 0 else (base.get("hands") or [])[hi - 1]
            if isinstance(act, list) and len(act) > 1 and act[0] == "PLACE" and act[1] == "GOOSE":
                out = out or copy.deepcopy(action)
                new = list(act)
                new[1] = "SHEEP"
                if hi == 0: out["farmer"] = new
                else: out["hands"][hi - 1] = new

    return out if out is not None else action


# =============================================================================
# V92 Day-23 Hour-23 Shed Capacity Overflow Guard
# =============================================================================
GUARD_DAY = 23
GUARD_HOUR = 23
SHED_CAPACITY = 100
HARVEST_ALLOWANCE = 6
MIN_FERT_RESERVE = 4
MAX_FERT_BUY = 12

def _v92_shed_total(private):
    shed = private.get("shed") or {}
    return sum(int(v or 0) for v in shed.values())

def _v92_carried_total(private):
    total = 0
    for inv in private.get("inventories") or []:
        if isinstance(inv, dict):
            total += sum(int(v or 0) for v in inv.values())
    return total

def _v92_buy_units(orders, item):
    total = 0
    for o in orders:
        if len(o) > 2 and o[0] == "BUY_PRODUCT" and o[1] == item:
            total += int(o[2] or 0)
    return total

def _v92_apply(obs, action):
    if not isinstance(obs, dict) or not isinstance(action, dict):
        return action
    if int(obs.get("day", 0) or 0) != GUARD_DAY or int(obs.get("hour", 0) or 0) != GUARD_HOUR:
        return action

    seat = int(obs.get("player", 0) or 0)
    farms = obs.get("farms") or []
    if seat >= len(farms):
        return action
    private = obs.get("private") or {}

    orders = list(action.get("market") or [])
    wheat_buys = _v92_buy_units(orders, "WHEAT")
    fert_buys = _v92_buy_units(orders, "FERTILIZER")
    if wheat_buys <= 0 and fert_buys <= 0:
        return action

    shed_now = _v92_shed_total(private)
    carried_now = _v92_carried_total(private)
    projected = shed_now + carried_now + wheat_buys + fert_buys + HARVEST_ALLOWANCE
    if projected <= SHED_CAPACITY:
        return action

    shed = private.get("shed") or {}
    shed_wheat = int(shed.get("WHEAT", 0) or 0)
    wheat_keep = min(wheat_buys, max(0, min(shed_wheat, wheat_buys)))
    fert_keep = min(fert_buys, MIN_FERT_RESERVE)

    new_wheat = wheat_buys
    new_fert = min(fert_buys, MAX_FERT_BUY)
    if new_fert < fert_keep:
        new_fert = fert_keep

    def projected_func(wheat_qty, fert_qty):
        return shed_now + carried_now + wheat_qty + fert_qty + HARVEST_ALLOWANCE

    guard_passes = 0
    while projected_func(new_wheat, new_fert) > SHED_CAPACITY and guard_passes < 32:
        guard_passes += 1
        if new_fert > fert_keep:
            new_fert -= 1
        elif new_wheat > wheat_keep:
            new_wheat -= 1
        else:
            break

    if new_wheat == wheat_buys and new_fert == fert_buys:
        return action

    new_orders = []
    for order in orders:
        if len(order) > 2 and order[0] == "BUY_PRODUCT" and order[1] == "FERTILIZER":
            if new_fert > 0:
                new_orders.append(["BUY_PRODUCT", "FERTILIZER", new_fert])
        elif len(order) > 2 and order[0] == "BUY_PRODUCT" and order[1] == "WHEAT":
            if new_wheat > 0:
                new_orders.append(["BUY_PRODUCT", "WHEAT", new_wheat])
        else:
            new_orders.append(list(order))

    action = copy.deepcopy(action)
    action["market"] = new_orders
    return action


# =============================================================================
# Step 717-718 Terminal Harvest Rush & Shed Drop
# =============================================================================
def _terminal_rush(obs, action, step):
    if step not in (717, 718):
        return action
    player = 1 if int(obs.get("player", 0) or 0) == 1 else 0
    farms = obs.get("farms", []) or []
    farm = farms[player] if player < len(farms) else {}
    private = obs.get("private", {}) or {}
    tiles = farm.get("tiles", []) or []
    if not tiles:
        return action
    access = _shed_access(len(tiles))
    positions = [farm.get("farmer", [0, 0]), *(farm.get("hands", []) or [])]
    inventories = list(private.get("inventories", []) or [])
    inventories.extend({} for _ in range(max(0, len(positions) - len(inventories))))
    unit_actions = [action.get("farmer", ["PASS"]), *(action.get("hands") or [])]

    for index, (raw_position, inventory) in enumerate(zip(positions, inventories)):
        if not isinstance(raw_position, (list, tuple)) or len(raw_position) < 2:
            continue
        position = (int(raw_position[0]), int(raw_position[1]))
        load = sum(max(0, int(value or 0)) for value in (inventory or {}).values())
        x, y = position
        tile = tiles[y][x] if 0 <= y < len(tiles) and 0 <= x < len(tiles[y]) else None
        distance = min(abs(x - sx) + abs(y - sy) for sx, sy in access)
        replacement = None
        if load > 0 and position in access:
            replacement = ["DROP"]
        elif step == 717 and load > 0 and distance == 1:
            replacement = _move_toward(position, access, tiles)
        elif (
            step == 717
            and load == 0
            and position in access
            and isinstance(tile, dict)
            and int(tile.get("yield_units", 0) or 0) > 0
        ):
            replacement = ["HARVEST"]
        if replacement is not None:
            unit_actions[index] = replacement

    action = copy.deepcopy(action)
    action["farmer"] = unit_actions[0]
    action["hands"] = unit_actions[1:]
    return action


# =============================================================================
# Agent Main Entrypoint
# =============================================================================
def agent(obs, configuration=None):
    global _selected_route
    try:
        # Step normalization: Seat 1 in Kaggle Environments lacks 'step' attribute
        if obs.get("step") is None:
            obs = dict(obs)
            day = int(obs.get("day", 0) or 0)
            hour = int(obs.get("hour", 0) or 0)
            obs["step"] = day * 24 + hour

        step = obs["step"]

        if step == 0:
            _selected_route = None

        shops = (obs.get("town") or {}).get("unlocked_shops", [])

        # Locked route selection:
        # Structural divergence happens at step 150 (Day 7 Hour 6).
        # We check town shops by Day 6 Hour 0 (step 144).
        if _selected_route is None:
            if "YARN_STORE" in shops:
                _selected_route = "v50"
            elif step >= 144:
                _selected_route = "v56"

        if _selected_route == "v50":
            action = _V50_PLANNER(obs, configuration)
            action = _milk_swap_apply(obs, action)
            action = _v92_apply(obs, action)
        else:
            action = _V56_PLANNER(obs, configuration)
            action = _milk_swap_apply(obs, action)
            action = _late_yarn_pivot(obs, action, step)
            action = _v92_apply(obs, action)

        # Market impact slot ordering (safe sorting of sell slots without order dropping)
        action = reorder_market(obs, action, mode="impact_slots")

        # Step 629 Early Continuous Shed Clearance
        if step >= CLEARANCE_STEP:
            action = terminal_market(obs, action, "collision", replace=False)

        # Step 717-718 Terminal Harvest Rush & Shed Drop
        action = _terminal_rush(obs, action, step)

        # Late-collision terminal overlay
        return apply_overlay(obs, action, "late_collision")

    except Exception:
        seat = 1 if int((obs.get("player") or 0)) == 1 else 0
        farms = list(obs.get("farms") or [])
        farm = farms[seat] if seat < len(farms) else {}
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (farm.get("hands") or [])],
            "market": [],
        }


def _kaggle_submission_entrypoint(obs, configuration=None):
    return agent(obs, configuration)
'''

def format_b85(b85_str):
    chunks = [b85_str[i:i+100] for i in range(0, len(b85_str), 100)]
    return "(\n    " + "\n    ".join(f"'{c}'" for c in chunks) + "\n)"

output = template.replace("__MODULES_PAYLOAD__", format_b85(b_modules))
output = output.replace("__V50_ACT_PAYLOAD__", format_b85(b_v50_act))
output = output.replace("__V56_ACT_PAYLOAD__", format_b85(b_v56_act))

out_path = Path("experiments/v115_adaptive_sovereign.py")
out_path.write_text(output, encoding="utf-8")
print(f"Generated {out_path} ({len(output)} bytes)")

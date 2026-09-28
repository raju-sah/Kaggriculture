import base64
import json
import zlib
from pathlib import Path

# Load extracted modules and action tables
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
v51 = load_agent("experiments/v51_agent.py", "v51_mod")

print("Compressing payloads...")
b_modules = base64.b85encode(zlib.compress(json.dumps(v56._LIZS_MODULES).encode('utf-8'))).decode('ascii')
b_v50_act = base64.b85encode(zlib.compress(json.dumps(v50._ACTIONS).encode('utf-8'))).decode('ascii')
b_v51_act = base64.b85encode(zlib.compress(json.dumps(v51._ACTIONS).encode('utf-8'))).decode('ascii')
b_v56_act = base64.b85encode(zlib.compress(json.dumps(v56._ACTIONS).encode('utf-8'))).decode('ascii')

template = '''"""V111 Adaptive Grandmaster: Intelligent Tri-Route Town-Shop Engine.
Dynamic 3-way routing between:
- V50 Wool Powerhouse (11 Sheep) when Yarn Store is open
- V51 Milk & Multi-Livestock Powerhouse (9C/5S/3G) when Milk sinks are present or general market
- V56 Egg & Balanced Powerhouse (6C/4S/7G) when pure Egg sinks are present
Plus:
- V92 Day-23 Hour-23 Shed Capacity Overflow Guard
- Step-629 Early Continuous Shed Clearance
- Late-Collision Terminal Overlay + Market Impact Slot Ordering
- Full Seat 1 Normalization
"""

import base64
import copy
import json
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

from scripts.v19_terminal import apply_overlay, terminal_market
from scripts.v22_market_impact import reorder_market
from v23.planner import build_sparse_planner, PlannerConfig

_V50_ACTIONS = json.loads(zlib.decompress(base64.b85decode(
__V50_ACT_PAYLOAD__
)).decode("utf-8"))

_V51_ACTIONS = json.loads(zlib.decompress(base64.b85decode(
__V51_ACT_PAYLOAD__
)).decode("utf-8"))

_V56_ACTIONS = json.loads(zlib.decompress(base64.b85decode(
__V56_ACT_PAYLOAD__
)).decode("utf-8"))

_V50_PLANNER = build_sparse_planner(_V50_ACTIONS, PlannerConfig())
_V51_PLANNER = build_sparse_planner(_V51_ACTIONS, PlannerConfig())
_V56_PLANNER = build_sparse_planner(_V56_ACTIONS, PlannerConfig())

_selected_route = None
CLEARANCE_STEP = 629

# V92 Day-23 Overflow Guard
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


_MILK_SHOPS = frozenset(("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"))
_EGG_SHOPS = frozenset(("BAKERY", "BRUNCH_SPOT"))


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

        # Intelligent locked route selection at Day 6/7 boundary (step 144)
        # Structural livestock divergence happens at step 150 (Day 7 Hour 6).
        # We examine the town shop matrix:
        if _selected_route is None:
            if "YARN_STORE" in shops:
                _selected_route = "v50"  # 11-Sheep Wool King
            elif step >= 144:
                has_milk = any(s in _MILK_SHOPS for s in shops)
                has_egg = any(s in _EGG_SHOPS for s in shops)
                if has_egg and not has_milk:
                    _selected_route = "v56"  # 6C/4S/7G Egg Specialist
                else:
                    _selected_route = "v51"  # 9C/5S/3G Heavy Milk & Balanced King

        if _selected_route == "v50":
            action = _V50_PLANNER(obs, configuration)
        elif _selected_route == "v56":
            action = _V56_PLANNER(obs, configuration)
        else:
            action = _V51_PLANNER(obs, configuration)

        action = _v92_apply(obs, action)

        # Market impact slot ordering (safe sorting of sell slots without order dropping)
        action = reorder_market(obs, action, mode="impact_slots")

        # Step 629 Early Continuous Shed Clearance
        if step >= CLEARANCE_STEP:
            action = terminal_market(obs, action, "collision", replace=False)

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
output = output.replace("__V51_ACT_PAYLOAD__", format_b85(b_v51_act))
output = output.replace("__V56_ACT_PAYLOAD__", format_b85(b_v56_act))

out_path = Path("experiments/v111_adaptive_grandmaster.py")
out_path.write_text(output, encoding="utf-8")
print(f"Generated {out_path} ({len(output)} bytes)")

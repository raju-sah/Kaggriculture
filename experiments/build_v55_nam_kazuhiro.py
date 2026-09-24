"""Builder script for self-contained v55 Dynamic Adaptive Champion:
Nam 9C/5S/3G (Primary Elo 1233 Engine) + Kazuhiro 11-Sheep (Yarn Store Specialist).
"""

import base64
import json
import zlib
from pathlib import Path

import experiments.v48_agent as v48
from experiments.kazuhiro_agent import ACTIONS as K_ACTIONS
import experiments.v52_agent as v52

NAM_ACTIONS = v52._ACTIONS

NEEDED_MODULES = [
    "scripts.v21_route_memory_search",
    "v19_terminal",
    "scripts.v19_terminal",
    "scripts.v22_market_impact",
    "scripts.v22_weed_repair",
    "v23.state_encoder",
    "v23.simulator",
    "v23.policy_library",
    "v23.planner",
    "v24.market_maker",
]

sub_modules = {k: v48._V48_MODULES[k] for k in NEEDED_MODULES}
modules_compressed = base64.b85encode(
    zlib.compress(json.dumps(sub_modules).encode("utf-8"), 9)
).decode("ascii")

kazuhiro_compressed = base64.b85encode(
    zlib.compress(json.dumps(K_ACTIONS).encode("utf-8"), 9)
).decode("ascii")

nam_compressed = base64.b85encode(
    zlib.compress(json.dumps(NAM_ACTIONS).encode("utf-8"), 9)
).decode("ascii")


def chunk_str(s, n=100):
    lines = [s[i:i+n] for i in range(0, len(s), n)]
    return "\n".join(f"    '{line}'" for line in lines)


modules_b85_formatted = chunk_str(modules_compressed)
kazuhiro_b85_formatted = chunk_str(kazuhiro_compressed)
nam_b85_formatted = chunk_str(nam_compressed)

code = f'''"""v55: Dynamic Shop-Adaptive Champion Agent (Adaptive Town-Shop Routing: Nam 9C/5S/3G Primary Backbone vs Kazuhiro 11-Sheep Yarn Store Specialist + Closed-Loop Weed Repair + Market Impact Slot Ordering + Step 630 Clearance + Late-Collision Terminal Overlay + Full Seat 1 Normalization)."""

import base64
import json
import sys
import types
import zlib


def _v55_package(name):
    module = sys.modules.get(name)
    if module is None:
        module = types.ModuleType(name)
        module.__file__ = "<bundled-package:" + name + ">"
        module.__package__ = name
        module.__path__ = []
        sys.modules[name] = module
    return module


def _v55_load(name, source):
    parent, _, child = name.rpartition(".")
    if parent:
        _v55_package(parent)
    module = types.ModuleType(name)
    module.__file__ = "<bundled:" + name + ">"
    module.__package__ = parent
    sys.modules[name] = module
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    if parent:
        setattr(sys.modules[parent], child, module)
    return module


_V55_MODULES = json.loads(zlib.decompress(base64.b85decode(
(
{modules_b85_formatted}
)
)).decode("utf-8"))

for _name, _source in _V55_MODULES.items():
    _v55_load(_name, _source)

from scripts.v19_terminal import apply_overlay, terminal_market
from scripts.v22_market_impact import reorder_market
from v23.planner import build_sparse_planner, PlannerConfig
from v23.state_encoder import get as _v55_get

_KAZUHIRO_ACTIONS = json.loads(zlib.decompress(base64.b85decode(
(
{kazuhiro_b85_formatted}
)
)).decode("utf-8"))

_NAM_ACTIONS = json.loads(zlib.decompress(base64.b85decode(
(
{nam_b85_formatted}
)
)).decode("utf-8"))

_KAZUHIRO_PLANNER = build_sparse_planner(_KAZUHIRO_ACTIONS, PlannerConfig())
_NAM_PLANNER = build_sparse_planner(_NAM_ACTIONS, PlannerConfig())
CLEARANCE_STEP = 630


def agent(obs, configuration=None):
    try:
        # Step normalization: Seat 1 in Kaggle Environments lacks 'step' attribute
        if obs.get("step") is None:
            obs = dict(obs)
            day = int(obs.get("day", 0) or 0)
            hour = int(obs.get("hour", 0) or 0)
            obs["step"] = day * 24 + hour

        step = obs["step"]
        shops = obs.get("town", {{}}).get("unlocked_shops", []) or []

        # Dynamic town-shop routing:
        # If YARN_STORE is unlocked, route to Kazuhiro (11 sheep) wool powerhouse!
        # Otherwise, route to Nam (9C/5S/3G) high-milk / multi-livestock powerhouse!
        if "YARN_STORE" in shops:
            action = _KAZUHIRO_PLANNER(obs, configuration)
        else:
            action = _NAM_PLANNER(obs, configuration)
        
        # Market impact slot ordering (safe sorting of sell slots without order dropping)
        action = reorder_market(obs, action, mode="impact_slots")

        # Step 630 Early Continuous Shed Clearance (monetizes 50 hours earlier before late crashes)
        if step >= CLEARANCE_STEP:
            action = terminal_market(obs, action, "collision", replace=False)

        # Late-collision terminal overlay (monetization and terminal 718 full replacement)
        return apply_overlay(obs, action, "late_collision")
    except Exception:
        seat = 1 if int(_v55_get(obs, "player", 0) or 0) == 1 else 0
        farms = list(_v55_get(obs, "farms", []) or [])
        farm = farms[seat] if seat < len(farms) else {{}}
        return {{
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (_v55_get(farm, "hands", []) or [])],
            "market": [],
        }}


def _kaggle_submission_entrypoint(obs, configuration=None):
    return agent(obs, configuration)
'''

# Build candidate
candidate_path = Path("experiments/v55_nam_kazuhiro.py")
candidate_path.write_text(code, encoding="utf-8")
print(f"Wrote {len(code)} characters to {candidate_path}")

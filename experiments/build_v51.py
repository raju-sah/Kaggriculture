"""Builder script for self-contained v51 agent."""

import base64
import json
import zlib
from pathlib import Path

import experiments.v48_agent as v48
from experiments.nam_agent import ACTIONS

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

actions_compressed = base64.b85encode(
    zlib.compress(json.dumps(ACTIONS).encode("utf-8"), 9)
).decode("ascii")

def chunk_str(s, n=100):
    lines = [s[i:i+n] for i in range(0, len(s), n)]
    return "\n".join(f"    '{line}'" for line in lines)

modules_b85_formatted = chunk_str(modules_compressed)
actions_b85_formatted = chunk_str(actions_compressed)

code = f'''"""v51: Nam 122k Multi-Product Engine (9 Cows + 3 Geese + 5 Sheep) + Closed-Loop Weed Repair + Market Impact Ordering + Late-Collision Terminal Overlay."""

import base64
import json
import sys
import types
import zlib


def _v51_package(name):
    module = sys.modules.get(name)
    if module is None:
        module = types.ModuleType(name)
        module.__file__ = "<bundled-package:" + name + ">"
        module.__package__ = name
        module.__path__ = []
        sys.modules[name] = module
    return module


def _v51_load(name, source):
    parent, _, child = name.rpartition(".")
    if parent:
        _v51_package(parent)
    module = types.ModuleType(name)
    module.__file__ = "<bundled:" + name + ">"
    module.__package__ = parent
    sys.modules[name] = module
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    if parent:
        setattr(sys.modules[parent], child, module)
    return module


_V51_MODULES = json.loads(zlib.decompress(base64.b85decode(
(
{modules_b85_formatted}
)
)).decode("utf-8"))

for _name, _source in _V51_MODULES.items():
    _v51_load(_name, _source)

from scripts.v19_terminal import apply_overlay
from v23.planner import build_sparse_planner, PlannerConfig
from v23.state_encoder import get as _v51_get

_ACTIONS = json.loads(zlib.decompress(base64.b85decode(
(
{actions_b85_formatted}
)
)).decode("utf-8"))

_PLANNER = build_sparse_planner(_ACTIONS, PlannerConfig())


def agent(obs, configuration=None):
    try:
        action = _PLANNER(obs, configuration)
        return apply_overlay(obs, action, "late_collision")
    except Exception:
        seat = 1 if int(_v51_get(obs, "player", 0) or 0) == 1 else 0
        farms = list(_v51_get(obs, "farms", []) or [])
        farm = farms[seat] if seat < len(farms) else {{}}
        return {{
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (_v51_get(farm, "hands", []) or [])],
            "market": [],
        }}


def _kaggle_submission_entrypoint(obs, configuration=None):
    return agent(obs, configuration)
'''

target_path = Path("experiments/v51_agent.py")
target_path.write_text(code, encoding="utf-8")
print(f"Wrote {len(code)} characters to {target_path}")

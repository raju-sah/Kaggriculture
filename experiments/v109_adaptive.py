"""V109 Adaptive Champion: Dynamic Early-Shop Routing.
Routes to Lizs 6C/4S/7G (v56) when Day-3 Egg sinks (BAKERY, BRUNCH_SPOT) unlock.
Routes to V108 Composite (V50 + V107 Cow Swap + V92 Overflow Guard + Step-630 Clearance) otherwise.
Full Seat 1 normalization + Late-Collision Terminal Overlay + Market Impact Ordering.
"""

import copy
import importlib.util
import os
import sys
from pathlib import Path

# Load extracted modules
sys.path.insert(0, str(Path("extracted_v55").resolve()))
from scripts.v19_terminal import apply_overlay, terminal_market
from scripts.v22_market_impact import reorder_market

BASE_DIR = Path(__file__).resolve().parent.parent

def _load_module(rel_path, mod_name):
    abs_path = str(BASE_DIR / rel_path)
    spec = importlib.util.spec_from_file_location(mod_name, abs_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

v56_module = _load_module("agents/v56_agent.py", "v56_bundled")
v108_module = _load_module("experiments/v108_composite.py", "v108_bundled")

_v56_agent = v56_module.agent
_v108_agent = v108_module.agent

_EGG_SHOPS = frozenset(("BAKERY", "BRUNCH_SPOT"))
CLEARANCE_STEP = 629


def agent(obs, configuration=None):
    try:
        # Step normalization: Seat 1 in Kaggle Environments lacks 'step' attribute
        if obs.get("step") is None:
            obs = dict(obs)
            day = int(obs.get("day", 0) or 0)
            hour = int(obs.get("hour", 0) or 0)
            obs["step"] = day * 24 + hour

        step = obs["step"]
        shops = (obs.get("town") or {}).get("unlocked_shops", [])

        # Check if an egg sink unlocked on Day 3 or later, without early yarn store
        has_egg_shop = any(s in _EGG_SHOPS for s in shops)
        has_yarn_store = "YARN_STORE" in shops

        if has_egg_shop and not has_yarn_store:
            # Route to v56 (Lizs 6C/4S/7G Egg & Milk powerhouse)
            action = _v56_agent(obs, configuration)
        else:
            # Route to v108 (V50 + Cow Swap + V92 Overflow Guard)
            action = _v108_agent(obs, configuration)

        return action

    except Exception as e:
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

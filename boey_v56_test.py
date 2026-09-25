import sys
import copy
from experiments.boey_agent import BOEY_ACTIONS, PlannerConfig, build_sparse_planner
from scripts.v19_terminal import apply_overlay, terminal_market
from scripts.v22_market_impact import reorder_market
from v23.state_encoder import get as _v55_get

_BOEY_PLANNER = build_sparse_planner(BOEY_ACTIONS, PlannerConfig())
CLEARANCE_STEP = 630

def agent(obs, configuration=None):
    try:
        if obs.get("step") is None:
            obs = dict(obs)
            day = int(obs.get("day", 0) or 0)
            hour = int(obs.get("hour", 0) or 0)
            obs["step"] = day * 24 + hour
        step = obs["step"]
        
        action = _BOEY_PLANNER(obs, configuration)
        action = reorder_market(obs, action, mode="impact_slots")
        if step >= CLEARANCE_STEP:
            action = terminal_market(obs, action, "collision", replace=False)
        return apply_overlay(obs, action, "late_collision")
    except Exception:
        seat = 1 if int(_v55_get(obs, "player", 0) or 0) == 1 else 0
        farms = list(_v55_get(obs, "farms", []) or [])
        farm = farms[seat] if seat < len(farms) else {}
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (_v55_get(farm, "hands", []) or [])],
            "market": [],
        }

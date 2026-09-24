"""v54: Adaptive Dual-Strategy Agent.

Dynamically switches between two pre-computed sparse planners:
- v53 (sheep/wool backbone) when YARN_STORE is present (wool stays profitable)  
- boey (diversified: carrots/eggs/wheat/wool/milk/strawberry/fertilizer) otherwise

Both strategies use the same sparse planner infrastructure with v53's market overlays.
"""

import sys
import os
import importlib.util
import copy

_workspace_root = os.getcwd()
if _workspace_root not in sys.path:
    sys.path.append(_workspace_root)

# Load v53 agent (sheep/wool specialist)
_v53_spec = importlib.util.spec_from_file_location(
    "v53_agent_mod", os.path.join(_workspace_root, "agents", "v53_agent.py"))
_v53_mod = importlib.util.module_from_spec(_v53_spec)
sys.modules["v53_agent_mod"] = _v53_mod
_v53_spec.loader.exec_module(_v53_mod)

# Load boey agent (diversified specialist)
_boey_spec = importlib.util.spec_from_file_location(
    "boey_agent_mod", os.path.join(_workspace_root, "experiments", "boey_agent.py"))
_boey_mod = importlib.util.module_from_spec(_boey_spec)
sys.modules["boey_agent_mod"] = _boey_mod
_boey_spec.loader.exec_module(_boey_mod)

# Per-player strategy lock
_PLAYER_STRATEGY = {}
_STRATEGY_LOCKED_DAY = 3  # Lock strategy by day 3 when shops are known


def _detect_strategy(obs):
    """Detect optimal strategy based on town shop configuration."""
    town = obs.get("town", {})
    if not town:
        return "v53"  # Default to proven strategy
    
    shops = town.get("unlocked_shops", [])
    if not shops:
        # No shops info yet - check if we can infer from other data
        return "v53"
    
    # YARN_STORE consumes 2 wool every 4 steps = keeps wool prices high
    # Without it, 11 sheep dump 379 wool → price crashes to $1-$17
    if "YARN_STORE" in shops:
        return "v53"  # Wool stays profitable
    
    # Check for dairy-friendly shops
    dairy_shops = {"ICE_CREAM_SHOP", "PET_CAFE"}
    crop_shops = {"FARMERS_MARKET", "BRUNCH_SPOT", "BAKERY", "PIZZA_SHOP"}
    
    has_dairy = bool(dairy_shops & set(shops))
    has_crop = bool(crop_shops & set(shops))
    
    # Boey's diversified strategy handles non-wool seeds better
    # It sells carrots, eggs, wheat, milk, strawberries, fertilizer
    if has_dairy or has_crop:
        return "boey"
    
    # Unknown shop config - boey is safer for non-wool
    return "boey"


def agent(obs, configuration=None):
    # Step normalization for Seat 1
    if obs.get("step") is None:
        obs = dict(obs)
        day = int(obs.get("day", 0) or 0)
        hour = int(obs.get("hour", 0) or 0)
        obs["step"] = day * 24 + hour

    player = obs.get("player", 0)
    day = obs.get("day", 0)
    step = obs.get("step", 0)
    
    # Lock strategy once we have shop information
    if player not in _PLAYER_STRATEGY:
        if day >= _STRATEGY_LOCKED_DAY:
            strategy = _detect_strategy(obs)
            _PLAYER_STRATEGY[player] = strategy
            print(f"P{player} Strategy: {strategy} (Day {day}, Shops: {obs.get('town', {}).get('unlocked_shops', [])})")
    
    strategy = _PLAYER_STRATEGY.get(player, "v53")
    
    # Dispatch to the selected strategy's agent
    try:
        if strategy == "boey":
            return _boey_mod.agent(obs, configuration)
        else:
            return _v53_mod.agent(obs, configuration)
    except Exception as e:
        print(f"P{player} Strategy {strategy} error: {e}, falling back to v53")
        try:
            return _v53_mod.agent(obs, configuration)
        except Exception:
            return {
                "farmer": ["PASS"],
                "hands": [],
                "market": [],
            }

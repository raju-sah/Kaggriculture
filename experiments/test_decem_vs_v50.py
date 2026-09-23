import json
import sys
from pathlib import Path
from kaggle_environments import make
sys.path.insert(0, str(Path("extracted_v55").resolve()))
from v23.planner import build_sparse_planner, PlannerConfig
from scripts.v19_terminal import apply_overlay, terminal_market
from scripts.v22_market_impact import reorder_market

with open("experiments/decem_actions.json") as f:
    decem_actions = json.load(f)

decem_planner = build_sparse_planner(decem_actions, PlannerConfig())

def decem_agent(obs, configuration=None):
    if obs.get("step") is None:
        obs = dict(obs)
        day = int(obs.get("day", 0) or 0)
        hour = int(obs.get("hour", 0) or 0)
        obs["step"] = day * 24 + hour
    step = obs["step"]
    action = decem_planner(obs, configuration)
    action = reorder_market(obs, action, mode="impact_slots")
    if step >= 630:
        action = terminal_market(obs, action, "collision", replace=False)
    return apply_overlay(obs, action, "late_collision")

if __name__ == "__main__":
    env = make("kaggriculture", configuration={"seed": 190001, "episodeSteps": 720})
    env.reset()
    # Test decem_agent vs experiments/v50_agent.py
    env.run([decem_agent, "experiments/v50_agent.py"])
    rewards = [env.state[0].reward, env.state[1].reward]
    print("Seed 190001 [DECEM vs V50]:", rewards)
    
    # Swapped seat
    env = make("kaggriculture", configuration={"seed": 190001, "episodeSteps": 720})
    env.reset()
    env.run(["experiments/v50_agent.py", decem_agent])
    rewards = [env.state[0].reward, env.state[1].reward]
    print("Seed 190001 [V50 vs DECEM]:", rewards)

import kaggle_environments
from collections import Counter
import sys
sys.path.insert(0, ".")

import importlib.util

def load_agent(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

v50 = load_agent("experiments/v50_agent.py", "v50_mod")
v51 = load_agent("experiments/v51_agent.py", "v51_mod")
v56 = load_agent("agents/v56_agent.py", "v56_mod")

seeds = [190001, 190002, 190003, 190004, 190005, 190006, 190007, 190008, 190009, 190010]

def eval_seed(seed, p0, p1):
    env = kaggle_environments.make("kaggriculture", configuration={"seed": seed})
    env.reset()
    state = env.run([p0.agent, p1.agent])
    r0 = state[-1][0]["reward"]
    r1 = state[-1][1]["reward"]
    return r0, r1

print(f"{'Seed':<8} | {'Shops at Day 7 (Step 144)':<35} | {'v50 vs v51':<20} | {'v51 vs v56':<20} | {'v50 vs v56':<20}")
print("-" * 110)

for s in seeds:
    # get shops at step 144
    env = kaggle_environments.make("kaggriculture", configuration={"seed": s})
    env.reset()
    for st in range(145):
        state = env.step([{}, {}])
    shops = state[0].observation.get("town", {}).get("unlocked_shops", [])
    
    r50_51_0, r50_51_1 = eval_seed(s, v50, v51)
    r51_56_0, r51_56_1 = eval_seed(s, v51, v56)
    r50_56_0, r50_56_1 = eval_seed(s, v50, v56)
    
    res1 = f"v50 +{r50_51_0 - r50_51_1:.0f}" if r50_51_0 > r50_51_1 else f"v51 +{r50_51_1 - r50_51_0:.0f}"
    res2 = f"v51 +{r51_56_0 - r51_56_1:.0f}" if r51_56_0 > r51_56_1 else f"v56 +{r51_56_1 - r51_56_0:.0f}"
    res3 = f"v50 +{r50_56_0 - r50_56_1:.0f}" if r50_56_0 > r50_56_1 else f"v56 +{r50_56_1 - r50_56_0:.0f}"
    
    print(f"{s:<8} | {str(shops):<35} | {res1:<20} | {res2:<20} | {res3:<20}")

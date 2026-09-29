from experiments.kazuhiro_agent import ACTIONS as k_actions
from experiments.lizs_agent import _ACTIONS as l_actions

diff_step = -1
for i, (k, l) in enumerate(zip(k_actions, l_actions)):
    if k != l:
        diff_step = i
        break
print(f"First difference at step: {diff_step}")

from experiments.kazuhiro_agent import ACTIONS as k_actions
from experiments.v53_agent import _ACTIONS as v53_actions
from experiments.v52_agent import _ACTIONS as v52_actions
print(k_actions == v53_actions)
print(k_actions == v52_actions)

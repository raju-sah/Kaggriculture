import json
from main import _ACTIONS

with open("actions_dump.json", "w") as f:
    json.dump(_ACTIONS, f, indent=2)

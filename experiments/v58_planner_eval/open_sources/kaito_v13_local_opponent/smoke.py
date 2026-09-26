"""One-game local loader/runtime smoke; this file is not a submission wrapper."""
from pathlib import Path
import hashlib
import importlib.util
import sys
from kaggle_environments import make
from kaggle_environments.agent import get_last_callable

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[3]
sys.path.insert(0, str(PROJECT))
main_path = HERE / "main.py"
assert hashlib.sha256(main_path.read_bytes()).hexdigest() == "69f06a802b62aa08f28705dab5728eb924bb6a7c23ffe0164f65b104cc3dadf3"
kaito = get_last_callable(main_path.read_text(), path=str(main_path))
from experiments.v57_broad.v57_reset_candidate import agent as frozen_reset

env = make("kaggriculture", configuration={"seed": 94900})
state = env.run([kaito, frozen_reset])
assert len(state) == 720, len(state)
assert all(s[0].get("status") != "ERROR" and s[1].get("status") != "ERROR" for s in state)
print({"seed": 94900, "seat": 0, "steps": len(state), "kaito_reward": state[-1][0]["reward"], "frozen_reset_reward": state[-1][1]["reward"], "kaito_sha256": hashlib.sha256(main_path.read_bytes()).hexdigest()})

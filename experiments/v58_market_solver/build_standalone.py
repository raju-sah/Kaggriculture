"""Assemble the reset route plus the self-contained observation-only solver."""

from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
base = (ROOT / "experiments/v57_broad/v57_reset_candidate.py").read_text()
solver = (HERE / "market_solver_agent.py").read_text()
helper_start = solver.index("# Pinned engine market quote constants")
agent_start = solver.rindex("def agent(obs, configuration=None):")
helpers = solver[helper_start:agent_start]
tail = "\n_v58_base_agent = agent\n" + helpers + "\ndef _market_solver_entrypoint(obs, configuration=None):\n    return _optimize(obs, _v58_base_agent(obs, configuration))\n"
output = base + "\n\n# v58 exact observation-only market optimizer.\nimport copy\n" + tail
dest = HERE / "market_solver_standalone.py"
dest.write_text(output)
print(f"wrote {dest} ({len(output)} bytes)")

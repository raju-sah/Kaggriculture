"""Compare exact market queue outcomes on retained v57 replay observations."""

import importlib.util
import json
import time
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("market_solver_agent", Path(__file__).with_name("market_solver_agent.py"))
solver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(solver)

replays = [
    ROOT / "experiments/v58_elite/v57reset_vs_boeyproxy_511533100/replays/BoeyProxy-seed-511533100-ab-repeat-0.json",
    ROOT / "experiments/v58_elite/v57reset_vs_boeyproxy_511533100/replays/BoeyProxy-seed-511533100-ba-repeat-0.json",
    *sorted((ROOT / "experiments/v58_elite/v57_vs_elite_proxies/replays").glob("*.json")),
]
totals = {"frames": 0, "action_divergences": 0, "oracle_gain": 0, "positive_frames": 0, "wheat_sale_frames": 0, "wheat_sales_suppressed": 0, "active_animal_wheat_sells_after": 0, "actor_action_mutations": 0}
durations = []
per_replay = []
for path in replays:
    data = json.loads(path.read_text())
    # Candidate seat is recorded on the match summary when available. Replay
    # filenames encode ba (candidate seat 1) or ab (candidate seat 0).
    seat = 1 if "-ba-" in path.name else 0
    changes = gains = frames = suppressed = wheat = active_wheat_after = 0
    for i in range(1, len(data["steps"])):
        obs = data["steps"][i - 1][seat].get("observation") or {}
        action = data["steps"][i][seat].get("action") or {}
        if not obs or not action:
            continue
        baseline = [list(o) for o in action.get("market", []) if isinstance(o, list)]
        if not baseline:
            continue
        candidate_action = {**action, "market": [list(o) for o in baseline]}
        before_actors = (candidate_action.get("farmer"), candidate_action.get("hands"))
        started = time.perf_counter()
        optimized = solver._optimize(obs, candidate_action)
        durations.append(time.perf_counter() - started)
        if before_actors != (optimized.get("farmer"), optimized.get("hands")):
            totals["actor_action_mutations"] += 1
        after = optimized.get("market", [])
        frames += 1
        if baseline != after:
            changes += 1
        gain = solver._simulate(obs, action, after) - solver._simulate(obs, action, baseline)
        gains += gain
        if gain > 0:
            totals["positive_frames"] += 1
        before_wheat = sum(o[2] for o in baseline if len(o) > 2 and o[:2] == ["SELL", "WHEAT"])
        after_wheat = sum(o[2] for o in after if len(o) > 2 and o[:2] == ["SELL", "WHEAT"])
        if before_wheat:
            wheat += 1
        if after_wheat < before_wheat:
            suppressed += 1
        if after_wheat and solver._wheat_reserve(obs):
            active_wheat_after += 1
    per_replay.append({"replay": path.name, "seat": seat, "market_frames": frames, "changed_frames": changes, "oracle_cash_delta": gains, "wheat_sell_frames": wheat, "wheat_suppressed_frames": suppressed, "active_animal_wheat_sell_frames_after": active_wheat_after})
    totals["frames"] += frames
    totals["action_divergences"] += changes
    totals["oracle_gain"] += gains
    totals["wheat_sale_frames"] += wheat
    totals["wheat_sales_suppressed"] += suppressed
    totals["active_animal_wheat_sells_after"] += active_wheat_after

durations.sort()
p95 = durations[int(.95 * (len(durations) - 1))] if durations else None
out = {"method": "saved v57 market actions; copied pinned engine market quote and commit rules; current shared inventory only; opponent same-turn market response excluded", "totals": totals, "optimizer_runtime_seconds_p95": p95, "optimizer_runtime_seconds_median": statistics.median(durations) if durations else None, "replays": per_replay}
dest = Path(__file__).with_name("retained_oracle.json")
dest.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))

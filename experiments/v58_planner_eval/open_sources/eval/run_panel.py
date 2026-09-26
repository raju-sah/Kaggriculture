"""Fresh internal opponent screen; records final rewards/errors only, no replays."""
from __future__ import annotations
import hashlib, importlib.util, json, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from kaggle_environments import make
from kaggle_environments.agent import get_last_callable
def load_local_agent(name, path):
    spec = importlib.util.spec_from_file_location(f"panel_{name}", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.agent

BASELINES = {
    "v50": load_local_agent("v50", ROOT / "experiments/v50_agent.py"),
    "v53": load_local_agent("v53", ROOT / "agents/v53_agent.py"),
    "v54": load_local_agent("v54", ROOT / "agents/v54_agent.py"),
    "v56": load_local_agent("v56", ROOT / "agents/v56_agent.py"),
}
SOURCES = {
    "ahmed_v43": ROOT / "experiments/v58_planner_eval/open_sources/eval/ahmed_v43/runtime/main.py",
    "yhay_three_day": ROOT / "experiments/v58_planner_eval/open_sources/eval/yhay_three_day/runtime/main.py",
}
EXPECTED = {
    "ahmed_v43": "919fc1d61050cd96f799979e49177ae3ac7bce98ec9835724238bea73f4a08ed",
    "yhay_three_day": "23b0d0c93bcf3dfecaabfecd950ec4ab3b4c46000c0c481bddcf0a63ce019f02",
}
SEEDS = list(range(95000, 95005))

agents = {}
for name, path in SOURCES.items():
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    assert digest == EXPECTED[name], (name, digest)
    agents[name] = get_last_callable(data.decode("utf-8"), path=str(path))

out = ROOT / "experiments/v58_planner_eval/open_sources/eval/results"
out.mkdir(parents=True, exist_ok=True)
rows = []
start = time.time()
for candidate_name, candidate in agents.items():
    for baseline_name, baseline in BASELINES.items():
        for seed in SEEDS:
            for candidate_seat in (0, 1):
                players = [candidate, baseline] if candidate_seat == 0 else [baseline, candidate]
                try:
                    env = make("kaggriculture", configuration={"seed": seed})
                    state = env.run(players)
                    final = state[-1]
                    own, other = final[candidate_seat], final[1-candidate_seat]
                    err = [int((s or {}).get("status") in {"ERROR", "INVALID"} or (s or {}).get("reward") is None) for s in final]
                    game = {
                        "candidate": candidate_name, "baseline": baseline_name,
                        "seed": seed, "candidate_seat": candidate_seat,
                        "steps": len(state), "candidate_reward": own.get("reward"),
                        "baseline_reward": other.get("reward"), "error_players": sum(err),
                        "candidate_sha256": EXPECTED[candidate_name],
                    }
                except Exception as e:
                    game = {"candidate": candidate_name, "baseline": baseline_name,
                            "seed": seed, "candidate_seat": candidate_seat,
                            "steps": 0, "candidate_reward": None,
                            "baseline_reward": None, "error_players": 2,
                            "exception": f"{type(e).__name__}: {e}",
                            "candidate_sha256": EXPECTED[candidate_name]}
                rows.append(game)
                print(json.dumps(game), flush=True)
                (out / "games.jsonl").open("a").write(json.dumps(game)+"\n")
summary = {"seeds": SEEDS, "seat_orders": [0,1], "baseline_names": list(BASELINES),
           "candidate_names": list(agents), "games": len(rows), "elapsed_seconds": round(time.time()-start,2),
           "all_games_complete": all(r["steps"] == 720 for r in rows),
           "zero_error_games": sum(r["error_players"] == 0 for r in rows), "rows": rows}
(out / "summary.json").write_text(json.dumps(summary, indent=2)+"\n")
print("SUMMARY", json.dumps({k:v for k,v in summary.items() if k!="rows"}))

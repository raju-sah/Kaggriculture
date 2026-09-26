"""Exercise the frozen policy and new controller through Kaggle's exact loader."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from kaggle_environments.agent import get_last_callable

ROOT = Path(__file__).resolve().parents[3]
POLICY = ROOT / "experiments/v58_validation/original_route/agent.py"
BASELINE = ROOT / "experiments/v57_broad/v57_reset_candidate.py"
PUBLIC_REPLAY = ROOT / "experiments/v58_elite/replays/episode-113508988-replay.json"


def main() -> int:
    policy_source = POLICY.read_text()
    policy = get_last_callable(policy_source, path=str(POLICY))
    baseline = get_last_callable(BASELINE.read_text(), path=str(BASELINE))
    replay = json.loads(PUBLIC_REPLAY.read_text())
    probes = []
    indexes = sorted({1, 24, 24 * 6, 24 * 12, 24 * 20, min(700, len(replay["steps"]) - 1)})
    for i in indexes:
        frame = replay["steps"][i]
        for seat in (0, 1):
            obs = frame[seat].get("observation") or {}
            candidate_action = policy(obs, None)
            baseline_action = baseline(obs, None)
            farm = (obs.get("farms") or [{}])[seat]
            hands = list(farm.get("hands") or [])
            shape_ok = (isinstance(candidate_action, dict)
                        and isinstance(candidate_action.get("farmer"), list)
                        and len(candidate_action.get("hands", [])) == len(hands)
                        and isinstance(candidate_action.get("market"), list)
                        and all(isinstance(x, list) and x for x in candidate_action["market"]))
            probes.append({"frame": i, "seat": seat, "step": obs.get("step"),
                           "shape_ok": shape_ok, "different_from_reset": candidate_action != baseline_action,
                           "actions": candidate_action})
    result = {"policy_sha256": hashlib.sha256(policy_source.encode()).hexdigest(),
              "entrypoint": policy.__name__, "replay_episode_id": replay.get("id"),
              "probes": probes, "all_action_shapes_ok": all(p["shape_ok"] for p in probes),
              "different_probe_count": sum(p["different_from_reset"] for p in probes)}
    out = ROOT / "experiments/runs/v58_validation_original_route/loader_check.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "probes"}, indent=2))
    return 0 if result["all_action_shapes_ok"] and result["different_probe_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

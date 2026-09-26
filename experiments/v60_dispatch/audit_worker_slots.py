"""Read-only comparison of saved v57 worker actions on wins and losses."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPLAYS = {
    "loss_92802_v48": ("experiments/v58_diagnostics/replays/v48-seed-92802-ab-repeat-0.json", 0),
    "loss_92804_v51": ("experiments/v58_diagnostics/replays/v51-seed-92804-ab-repeat-0.json", 0),
    "win_92900_v48": ("experiments/v58_policy/baseline_vs_v48/replays/v48-seed-92900-ab-repeat-0.json", 0),
    "win_92901_v48": ("experiments/v58_policy/baseline_vs_v48/replays/v48-seed-92901-ab-repeat-0.json", 0),
    "loss_92902_v52": ("experiments/runs/v58_validation_baseline/replays/v52-seed-92902-ab-repeat-0.json", 0),
    "loss_92902_v53": ("experiments/runs/v58_validation_baseline/replays/v53-seed-92902-ab-repeat-0.json", 0),
    "win_92902_v54": ("experiments/runs/v58_validation_baseline/replays/v54-seed-92902-ab-repeat-0.json", 0),
}


def unit_stream_and_audit(path: Path, seat: int):
    replay = json.loads(path.read_text())
    steps = replay["steps"]
    counters = {"actions": Counter(), "no_effect": Counter(), "passes": Counter(),
                "attempts": Counter(), "successes": Counter()}
    stream = []
    feed_attempts = feed_successes = 0
    for frame in range(1, len(steps)):
        prev = steps[frame - 1][seat].get("observation") or {}
        curr = steps[frame][seat].get("observation") or {}
        action = steps[frame][seat].get("action") or {}
        farm0 = (prev.get("farms") or [{}] * 2)[seat]
        farm1 = (curr.get("farms") or [{}] * 2)[seat]
        positions0 = [farm0.get("farmer"), *(farm0.get("hands") or [])]
        positions1 = [farm1.get("farmer"), *(farm1.get("hands") or [])]
        actor_actions = [action.get("farmer") or ["PASS"], *(action.get("hands") or [])]
        stream.append({"farmer": actor_actions[0], "hands": actor_actions[1:]})
        inv0 = (prev.get("private") or {}).get("inventories") or []
        inv1 = (curr.get("private") or {}).get("inventories") or []
        tiles0 = farm0.get("tiles") or []
        tiles1 = farm1.get("tiles") or []
        for idx, order in enumerate(actor_actions):
            verb = order[0] if order else "PASS"
            counters["actions"][verb] += 1
            if verb in ("PASS", "WAIT"):
                counters["passes"][verb] += 1
                continue
            counters["attempts"][verb] += 1
            pos0 = positions0[idx] if idx < len(positions0) else None
            pos1 = positions1[idx] if idx < len(positions1) else pos0
            moved = pos0 != pos1
            tile0 = tiles0[pos0[1]][pos0[0]] if pos0 and 0 <= pos0[1] < len(tiles0) and 0 <= pos0[0] < len(tiles0[pos0[1]]) else None
            tile1 = tiles1[pos1[1]][pos1[0]] if pos1 and 0 <= pos1[1] < len(tiles1) and 0 <= pos1[0] < len(tiles1[pos1[1]]) else None
            before = inv0[idx] if idx < len(inv0) else {}
            after = inv1[idx] if idx < len(inv1) else {}
            effect = moved or tile0 != tile1 or before != after
            if verb == "FEED":
                animal_live = isinstance(tile0, dict) and tile0.get("animal") and not tile0.get("fed_today")
                has_wheat = idx < len(inv0) and (inv0[idx] or {}).get("WHEAT", 0) > 0
                feed_success = bool(animal_live and has_wheat)
                feed_attempts += 1
                feed_successes += int(feed_success)
                effect |= feed_success
            if effect:
                counters["successes"][verb] += 1
            else:
                counters["no_effect"][verb] += 1
    payload = json.dumps(stream, sort_keys=True, separators=(",", ":")).encode()
    return {
        "source": str(path.relative_to(ROOT)),
        "episode_seed": (replay.get("info") or {}).get("seed"),
        "rewards": replay.get("rewards"),
        "seat": seat,
        "actor_action_sha256": hashlib.sha256(payload).hexdigest(),
        "transition_action_frames": len(stream),
        "actor_action_counts": dict(counters["actions"]),
        "pass_slots": dict(counters["passes"]),
        "no_effect_by_command": dict(counters["no_effect"]),
        "command_attempts": dict(counters["attempts"]),
        "observed_effects_by_command": dict(counters["successes"]),
        "feed_attempts": feed_attempts,
        "feed_successes": feed_successes,
    }


def main():
    out = {}
    for label, (relpath, seat) in REPLAYS.items():
        path = ROOT / relpath
        out[label] = unit_stream_and_audit(path, seat)
        print(label, out[label]["rewards"], out[label]["actor_action_sha256"],
              out[label]["pass_slots"], out[label]["no_effect_by_command"], flush=True)
    seed92902 = [out[k]["actor_action_sha256"] for k in ("loss_92902_v52", "loss_92902_v53", "win_92902_v54")]
    out["same_seed92902_actor_stream_identical"] = len(set(seed92902)) == 1
    out["limitations"] = [
        "No game seeds were run; this is a read-only audit of saved replays.",
        "An observed state change is a proxy for successful worker action, not a full engine acceptance record.",
        "Market demand and opponent actions differ, so reward differences are not attributed to dispatch.",
    ]
    target = ROOT / "experiments/v60_dispatch/saved_replay_audit.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(out, indent=2) + "\n")


if __name__ == "__main__":
    main()

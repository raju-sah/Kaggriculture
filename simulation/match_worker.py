"""Run one isolated Kaggriculture match and emit a machine-readable record."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import sys
import time
import traceback
from collections import Counter
from pathlib import Path
from typing import Any

from kaggle_environments import make
from kaggle_environments.envs.kaggriculture import kaggriculture as kaggriculture_engine


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _normalized_replay(replay: dict[str, Any]) -> dict[str, Any]:
    """Remove the framework's per-run UUID while preserving game state."""
    return {key: value for key, value in replay.items() if key != "id"}


def _action_counts(replay: dict[str, Any], seat: int) -> dict[str, dict[str, int]]:
    farmer = Counter()
    hands = Counter()
    market = Counter()
    for step in replay.get("steps", [])[1:]:
        action = step[seat].get("action") or {}
        farmer_action = action.get("farmer") or ["PASS"]
        farmer[str(farmer_action[0])] += 1
        for hand_action in action.get("hands") or []:
            if hand_action:
                hands[str(hand_action[0])] += 1
        for market_action in action.get("market") or []:
            if market_action:
                market[str(market_action[0])] += 1
    return {
        "farmer": dict(sorted(farmer.items())),
        "hands": dict(sorted(hands.items())),
        "market": dict(sorted(market.items())),
    }


def _reward(value: Any) -> float | None:
    return float(value) if isinstance(value, (int, float)) else None


def run_match(agent_paths: list[Path], seed: int, replay_path: Path) -> dict[str, Any]:
    started = time.perf_counter()
    absolute_agents = [path.resolve() for path in agent_paths]
    engine_path = Path(kaggriculture_engine.__file__).resolve()
    specification_path = engine_path.with_name("kaggriculture.json")
    base = {
        "seed": seed,
        "agents": [
            {"path": str(path), "sha256": _sha256_file(path)}
            for path in absolute_agents
        ],
        "environment": {
            "name": "kaggriculture",
            "package": "kaggle-environments",
            "package_version": importlib.metadata.version("kaggle-environments"),
            "python_version": platform.python_version(),
            "episode_steps": 720,
            "engine_path": str(engine_path),
            "engine_sha256": _sha256_file(engine_path),
            "specification_path": str(specification_path),
            "specification_sha256": _sha256_file(specification_path),
        },
    }

    try:
        environment = make(
            "kaggriculture",
            configuration={"episodeSteps": 720, "seed": seed},
            debug=True,
        )
        environment.run([str(path) for path in absolute_agents])
        replay = environment.toJSON()
        replay_bytes = _canonical_json(replay)
        normalized_replay_bytes = _canonical_json(_normalized_replay(replay))
        replay_path.parent.mkdir(parents=True, exist_ok=True)
        replay_path.write_bytes(replay_bytes + b"\n")

        final_states = environment.steps[-1]
        rewards = [_reward(state.reward) for state in final_states]
        statuses = [str(state.status) for state in final_states]
        if rewards[0] is not None and rewards[1] is not None and rewards[0] > rewards[1]:
            winner = 0
        elif rewards[0] is not None and rewards[1] is not None and rewards[1] > rewards[0]:
            winner = 1
        else:
            winner = None

        completed = all(status == "DONE" for status in statuses)
        status_error = None
        if not completed:
            status_error = {
                "type": "AgentStatusError",
                "message": f"final statuses were {statuses}",
            }

        return {
            **base,
            "ok": completed,
            "resolved_seed": environment.info.get("seed"),
            "final_coins": rewards,
            "statuses": statuses,
            "winner_seat": winner,
            "coin_difference_seat_0": (
                rewards[0] - rewards[1]
                if rewards[0] is not None and rewards[1] is not None
                else None
            ),
            "action_counts": [_action_counts(replay, 0), _action_counts(replay, 1)],
            "runtime_seconds": time.perf_counter() - started,
            "replay_path": str(replay_path.resolve()),
            "replay_sha256": hashlib.sha256(normalized_replay_bytes).hexdigest(),
            "raw_replay_sha256": hashlib.sha256(replay_bytes).hexdigest(),
            "replay_normalization": {"removed_top_level_fields": ["id"]},
            "error": status_error,
        }
    except Exception as exc:  # A worker must preserve diagnostics for the parent.
        formatted_traceback = traceback.format_exc()
        failed_seats = [
            seat for seat, path in enumerate(absolute_agents) if str(path) in formatted_traceback
        ]
        return {
            **base,
            "ok": False,
            "resolved_seed": None,
            "final_coins": [None, None],
            "statuses": ["ERROR", "ERROR"],
            "winner_seat": None,
            "coin_difference_seat_0": None,
            "action_counts": [None, None],
            "failed_agent_seat": failed_seats[0] if len(failed_seats) == 1 else None,
            "runtime_seconds": time.perf_counter() - started,
            "replay_path": None,
            "replay_sha256": None,
            "raw_replay_sha256": None,
            "error": {
                "type": type(exc).__name__,
                "message": str(exc),
                "traceback": formatted_traceback,
            },
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-0", required=True, type=Path)
    parser.add_argument("--agent-1", required=True, type=Path)
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--replay", required=True, type=Path)
    parser.add_argument("--result", required=True, type=Path)
    args = parser.parse_args()

    result = run_match([args.agent_0, args.agent_1], args.seed, args.replay)
    args.result.parent.mkdir(parents=True, exist_ok=True)
    args.result.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

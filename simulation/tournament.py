"""Run reproducible, seat-swapped Kaggriculture tournaments."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import re
import statistics
import subprocess
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class Opponent:
    name: str
    path: Path


@dataclass(frozen=True)
class MatchSpec:
    opponent: Opponent
    seed: int
    swapped: bool
    repeat: int


def parse_seeds(value: str) -> list[int]:
    """Parse comma-separated integers and inclusive ranges such as 1-5,20."""
    seeds: list[int] = []
    seen: set[int] = set()
    for part in value.split(","):
        token = part.strip()
        if not token:
            continue
        range_match = re.fullmatch(r"(-?\d+)-(-?\d+)", token)
        if range_match:
            start, end = map(int, range_match.groups())
            if end < start:
                raise ValueError(f"descending seed range is not allowed: {token}")
            values: Iterable[int] = range(start, end + 1)
        else:
            values = [int(token)]
        for seed in values:
            if seed not in seen:
                seen.add(seed)
                seeds.append(seed)
    if not seeds:
        raise ValueError("at least one seed is required")
    return seeds


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_.-]+", "-", value).strip("-")
    return slug or "opponent"


def _parse_opponent(value: str) -> Opponent:
    if "=" not in value:
        raise ValueError("opponents must use NAME=PATH")
    name, raw_path = value.split("=", 1)
    if not name.strip() or not raw_path.strip():
        raise ValueError("opponents must use non-empty NAME=PATH")
    path = Path(raw_path).resolve()
    if not path.is_file():
        raise ValueError(f"opponent file does not exist: {path}")
    return Opponent(name=name.strip(), path=path)


def _game_id(spec: MatchSpec) -> str:
    seat_order = "ba" if spec.swapped else "ab"
    return f"{_slug(spec.opponent.name)}-seed-{spec.seed}-{seat_order}-repeat-{spec.repeat}"


def _run_worker(
    candidate: Path,
    spec: MatchSpec,
    output_dir: Path,
    timeout_seconds: float,
    replay_policy: str,
) -> dict[str, Any]:
    game_id = _game_id(spec)
    result_path = output_dir / "games" / f"{game_id}.json"
    replay_path = output_dir / "replays" / f"{game_id}.json"
    log_path = output_dir / "logs" / f"{game_id}.log"
    seats = [spec.opponent.path, candidate] if spec.swapped else [candidate, spec.opponent.path]
    candidate_seat = 1 if spec.swapped else 0
    command = [
        sys.executable,
        "-m",
        "simulation.match_worker",
        "--agent-0",
        str(seats[0]),
        "--agent-1",
        str(seats[1]),
        "--seed",
        str(spec.seed),
        "--replay",
        str(replay_path),
        "--result",
        str(result_path),
    ]

    started = time.perf_counter()
    infrastructure_error = False
    timed_out = False
    try:
        completed = subprocess.run(
            command,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(
            f"exit_code={completed.returncode}\n\nSTDOUT\n{completed.stdout}\nSTDERR\n{completed.stderr}",
            encoding="utf-8",
        )
        if result_path.exists():
            record = json.loads(result_path.read_text(encoding="utf-8"))
        else:
            infrastructure_error = True
            record = {
                "ok": False,
                "seed": spec.seed,
                "final_coins": [None, None],
                "statuses": ["ERROR", "ERROR"],
                "winner_seat": None,
                "coin_difference_seat_0": None,
                "replay_sha256": None,
                "runtime_seconds": time.perf_counter() - started,
                "error": {
                    "type": "WorkerFailure",
                    "message": f"worker exited {completed.returncode} without a result",
                },
            }
        record["worker_exit_code"] = completed.returncode
    except subprocess.TimeoutExpired as exc:
        infrastructure_error = True
        timed_out = True
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(
            f"TIMEOUT after {timeout_seconds}s\nSTDOUT\n{exc.stdout or ''}\nSTDERR\n{exc.stderr or ''}",
            encoding="utf-8",
        )
        record = {
            "ok": False,
            "seed": spec.seed,
            "final_coins": [None, None],
            "statuses": ["TIMEOUT", "TIMEOUT"],
            "winner_seat": None,
            "coin_difference_seat_0": None,
            "replay_sha256": None,
            "worker_exit_code": None,
            "error": {
                "type": "TimeoutExpired",
                "message": f"match exceeded {timeout_seconds} seconds",
            },
            "runtime_seconds": time.perf_counter() - started,
        }

    statuses = record.get("statuses") or ["ERROR", "ERROR"]
    candidate_status = statuses[candidate_seat]
    opponent_status = statuses[1 - candidate_seat]
    failed_agent_seat = record.get("failed_agent_seat")
    if not record.get("ok") and failed_agent_seat is None and not infrastructure_error:
        infrastructure_error = True
    candidate_error = infrastructure_error or failed_agent_seat == candidate_seat
    opponent_error = not infrastructure_error and failed_agent_seat == 1 - candidate_seat
    if failed_agent_seat is None and not infrastructure_error:
        candidate_error = candidate_status != "DONE" and opponent_status == "DONE"
        opponent_error = opponent_status != "DONE" and candidate_status == "DONE"
    winner = record.get("winner_seat")
    if candidate_error:
        candidate_result = "loss"
    elif opponent_error:
        candidate_result = "win"
    elif winner is None:
        candidate_result = "draw"
    elif winner == candidate_seat:
        candidate_result = "win"
    else:
        candidate_result = "loss"

    record.update(
        {
            "game_id": game_id,
            "opponent": spec.opponent.name,
            "opponent_path": str(spec.opponent.path),
            "repeat": spec.repeat,
            "swapped": spec.swapped,
            "candidate_seat": candidate_seat,
            "opponent_seat": 1 - candidate_seat,
            "candidate_status": candidate_status,
            "opponent_status": opponent_status,
            "candidate_error": candidate_error,
            "opponent_error": opponent_error,
            "infrastructure_error": infrastructure_error,
            "timed_out": timed_out,
            "candidate_result": candidate_result,
            "log_path": str(log_path.resolve()),
        }
    )
    retain_replay = (
        replay_policy == "all"
        or (replay_policy == "losses" and candidate_result == "loss")
        or (replay_policy == "errors" and (candidate_error or opponent_error or infrastructure_error))
    )
    record["replay_retained"] = retain_replay and replay_path.exists()
    if not retain_replay and replay_path.exists():
        replay_path.unlink()
        record["replay_path"] = None
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record


def _determinism_checks(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, int, bool], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[(record["opponent"], record["seed"], record["swapped"])].append(record)

    checks = []
    for (opponent, seed, swapped), group in sorted(grouped.items()):
        if len(group) < 2:
            continue
        signatures = {
            (
                tuple(record.get("final_coins", [])),
                tuple(record.get("statuses", [])),
                record.get("replay_sha256"),
            )
            for record in group
        }
        checks.append(
            {
                "opponent": opponent,
                "seed": seed,
                "swapped": swapped,
                "repeats": len(group),
                "identical": len(signatures) == 1,
            }
        )
    return checks


def _wilson_interval(successes: int, trials: int, z: float = 1.959963984540054) -> list[float] | None:
    if trials == 0:
        return None
    proportion = successes / trials
    denominator = 1 + z * z / trials
    center = (proportion + z * z / (2 * trials)) / denominator
    margin = z * math.sqrt(
        proportion * (1 - proportion) / trials + z * z / (4 * trials * trials)
    ) / denominator
    return [max(0.0, center - margin), min(1.0, center + margin)]


def _cluster_bootstrap_win_rate(
    records: list[dict[str, Any]], samples: int = 5000
) -> list[float] | None:
    clusters: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        clusters[(record["opponent"], record["seed"])].append(record)
    values = [
        sum(record["candidate_result"] == "win" for record in group) / len(group)
        for group in clusters.values()
    ]
    if len(values) < 2:
        return None
    generator = random.Random(20260919)
    estimates = sorted(
        statistics.fmean(generator.choice(values) for _ in values) for _ in range(samples)
    )
    return [
        estimates[round(0.025 * (samples - 1))],
        estimates[round(0.975 * (samples - 1))],
    ]


def _group_by(records: list[dict[str, Any]], key: str) -> dict[Any, list[dict[str, Any]]]:
    grouped: dict[Any, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[record[key]].append(record)
    return grouped


def _summarize(records: list[dict[str, Any]], include_strata: bool) -> dict[str, Any]:
    wins = sum(record["candidate_result"] == "win" for record in records)
    losses = sum(record["candidate_result"] == "loss" for record in records)
    draws = sum(record["candidate_result"] == "draw" for record in records)
    total = len(records)
    candidate_coins = [
        record["final_coins"][record["candidate_seat"]]
        for record in records
        if record.get("final_coins")
        and record["final_coins"][record["candidate_seat"]] is not None
    ]
    differences = [
        record["final_coins"][record["candidate_seat"]]
        - record["final_coins"][record["opponent_seat"]]
        for record in records
        if record.get("final_coins")
        and record["final_coins"][record["candidate_seat"]] is not None
        and record["final_coins"][record["opponent_seat"]] is not None
    ]
    decisive = wins + losses
    summary: dict[str, Any] = {
        "games": total,
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "candidate_errors": sum(bool(r["candidate_error"]) for r in records),
        "opponent_errors": sum(bool(r["opponent_error"]) for r in records),
        "infrastructure_errors": sum(bool(r["infrastructure_error"]) for r in records),
        "timeouts": sum(bool(r["timed_out"]) for r in records),
        "win_rate": wins / total if total else None,
        "win_rate_wilson_95": _wilson_interval(wins, total),
        "score_rate": (wins + 0.5 * draws) / total if total else None,
        "decisive_win_rate": wins / decisive if decisive else None,
        "decisive_win_rate_wilson_95": _wilson_interval(wins, decisive),
        "paired_seed_bootstrap_win_rate_95": _cluster_bootstrap_win_rate(records),
        "mean_final_coins_candidate": statistics.fmean(candidate_coins) if candidate_coins else None,
        "median_coin_difference_candidate": statistics.median(differences) if differences else None,
        "mean_runtime_seconds": statistics.fmean(r["runtime_seconds"] for r in records),
    }
    if include_strata:
        summary["by_opponent"] = {
            opponent: _summarize(group, include_strata=False)
            for opponent, group in sorted(_group_by(records, "opponent").items())
        }
        summary["by_candidate_seat"] = {
            str(seat): _summarize(group, include_strata=False)
            for seat, group in sorted(_group_by(records, "candidate_seat").items())
        }
    return summary


def build_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    summary = _summarize(records, include_strata=True)
    checks = _determinism_checks(records)
    summary["determinism_checks"] = checks
    summary["deterministic"] = all(check["identical"] for check in checks) if checks else None
    return summary


def _write_flat_files(output_dir: Path, records: list[dict[str, Any]]) -> None:
    with (output_dir / "games.jsonl").open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    fields = [
        "game_id",
        "opponent",
        "seed",
        "repeat",
        "candidate_seat",
        "candidate_result",
        "candidate_status",
        "opponent_status",
        "candidate_error",
        "opponent_error",
        "infrastructure_error",
        "timed_out",
        "candidate_final_coins",
        "opponent_final_coins",
        "coin_difference_candidate",
        "runtime_seconds",
        "replay_sha256",
        "log_path",
    ]
    with (output_dir / "games.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for record in records:
            coins = record.get("final_coins") or [None, None]
            candidate_coin = coins[record["candidate_seat"]]
            opponent_coin = coins[record["opponent_seat"]]
            writer.writerow(
                {
                    **{field: record.get(field) for field in fields},
                    "candidate_final_coins": candidate_coin,
                    "opponent_final_coins": opponent_coin,
                    "coin_difference_candidate": (
                        candidate_coin - opponent_coin
                        if candidate_coin is not None and opponent_coin is not None
                        else None
                    ),
                }
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", "--agent-a", dest="candidate", required=True, type=Path)
    parser.add_argument("--agent-b", type=Path, help="single opponent path (compatibility form)")
    parser.add_argument(
        "--opponent",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help="named opponent; may be repeated",
    )
    seed_group = parser.add_mutually_exclusive_group()
    seed_group.add_argument("--seed", type=int)
    seed_group.add_argument("--seeds", help="integers/ranges, for example 1-50,100")
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument(
        "--replay-policy",
        choices=("all", "losses", "errors", "none"),
        default="errors",
        help="which full replays to retain; hashes and action counts are always recorded",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("experiments/runs/tournament"))
    args = parser.parse_args()

    candidate = args.candidate.resolve()
    if not candidate.is_file():
        parser.error(f"candidate file does not exist: {candidate}")
    if args.repeats < 1:
        parser.error("--repeats must be positive")
    if not 1 <= args.workers <= 8:
        parser.error("--workers must be between 1 and 8")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")

    try:
        opponents = [_parse_opponent(value) for value in args.opponent]
        if args.agent_b:
            opponent_path = args.agent_b.resolve()
            if not opponent_path.is_file():
                raise ValueError(f"opponent file does not exist: {opponent_path}")
            opponents.append(Opponent(name=opponent_path.stem, path=opponent_path))
        if not opponents:
            raise ValueError("provide --agent-b PATH or at least one --opponent NAME=PATH")
        if len({opponent.name for opponent in opponents}) != len(opponents):
            raise ValueError("opponent names must be unique")
        if len({_slug(opponent.name) for opponent in opponents}) != len(opponents):
            raise ValueError("opponent names must also be unique after filename normalization")
        seeds = parse_seeds(args.seeds) if args.seeds else [args.seed or 20260919]
    except ValueError as exc:
        parser.error(str(exc))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    specs = [
        MatchSpec(opponent=opponent, seed=seed, swapped=swapped, repeat=repeat)
        for opponent in opponents
        for seed in seeds
        for swapped in (False, True)
        for repeat in range(args.repeats)
    ]
    started_at = datetime.now(UTC)
    records = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(
                _run_worker,
                candidate,
                spec,
                args.output_dir,
                args.timeout,
                args.replay_policy,
            ): spec
            for spec in specs
        }
        for future in as_completed(futures):
            records.append(future.result())
    records.sort(key=lambda r: (r["opponent"], r["seed"], r["swapped"], r["repeat"]))

    summary = build_summary(records)
    finished_at = datetime.now(UTC)
    report = {
        "schema_version": 2,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "wall_seconds": (finished_at - started_at).total_seconds(),
        "candidate": str(candidate),
        "opponents": [{"name": opponent.name, "path": str(opponent.path)} for opponent in opponents],
        "seeds": seeds,
        "repeats": args.repeats,
        "workers": args.workers,
        "replay_policy": args.replay_policy,
        "summary": summary,
        "games": records,
    }
    _write_flat_files(args.output_dir, records)
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    report_path = args.output_dir / "report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(report_path.resolve()), **summary}, indent=2))

    failed_determinism = summary["deterministic"] is False
    return 1 if summary["infrastructure_errors"] or failed_determinism else 0


if __name__ == "__main__":
    sys.exit(main())

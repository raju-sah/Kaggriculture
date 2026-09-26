"""Hash-frozen, resumable v59 local validation. Does not submit or touch main.py."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from simulation.tournament import MatchSpec, Opponent, _game_id, _run_worker

ROOT = Path(__file__).resolve().parents[2]
PLAN_PATH = ROOT / "experiments/v59_validation/plan.json"
OUT_ROOT = ROOT / "experiments/v59_validation/runs"
PHASES = ("smoke", "historical_gate", "stronger_dev_gate", "paired_pre_final")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def engine_version() -> str:
    try:
        from importlib.metadata import version
        return version("kaggle-environments")
    except Exception as exc:  # pragma: no cover - environment diagnostic
        raise SystemExit(f"Cannot determine kaggle-environments version: {exc}")


def stage_passed(candidate_hash: str, stage: str) -> bool:
    report = OUT_ROOT / candidate_hash / stage / "analysis.json"
    if not report.is_file():
        return False
    return bool(json.loads(report.read_text()).get("gate_pass"))


def shop_schedule(path: Path) -> tuple[list[dict], list[str]]:
    if not path.is_file():
        return [], []
    replay = json.loads(path.read_text())
    sequence: list[dict] = []
    previous: list[str] = []
    signature: list[str] = []
    for step, states in enumerate(replay.get("steps", [])):
        if not states:
            continue
        obs = states[0].get("observation") or {}
        shops = (obs.get("town") or {}).get("unlocked_shops") or []
        if len(shops) > len(previous):
            for shop in shops[len(previous):]:
                sequence.append({"step": step, "day": obs.get("day"), "shop": shop})
        previous = list(shops)
        signature = list(shops)
    return sequence, signature


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--phase", required=True, choices=PHASES)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=float, default=240)
    args = parser.parse_args()
    os.chdir(ROOT)
    if not 1 <= args.workers <= 8 or args.timeout <= 0:
        parser.error("workers must be 1..8 and timeout must be positive")

    plan = json.loads(PLAN_PATH.read_text())
    candidate = args.candidate.resolve()
    if not candidate.is_file():
        parser.error(f"candidate does not exist: {candidate}")
    candidate_hash = sha(candidate)
    if args.phase != "smoke":
        prior = {
            "historical_gate": ("smoke",),
            "stronger_dev_gate": ("smoke", "historical_gate"),
            "paired_pre_final": ("smoke", "historical_gate", "stronger_dev_gate"),
        }[args.phase]
        missing = [name for name in prior if not stage_passed(candidate_hash, name)]
        if missing:
            raise SystemExit(f"Refusing {args.phase}: same candidate hash has not passed {missing}")

    stage = plan["stages"][args.phase]
    names = stage["opponents"]
    opponent_catalog = {**plan["historical_opponents"], **plan["pinned_local_opponents"]}
    opponents = {}
    for name in names:
        spec = opponent_catalog[name]
        path = ROOT / spec["path"]
        actual = sha(path)
        if actual != spec["sha256"]:
            raise SystemExit(f"Pinned opponent hash mismatch for {name}: {actual}")
        opponents[name] = {"path": spec["path"], "sha256": actual}

    installed_engine = engine_version()
    if installed_engine != "1.32.7":
        raise SystemExit(f"Engine mismatch: plan pins 1.32.7, installed {installed_engine}")
    manifest = {
        "schema_version": 1,
        "phase": args.phase,
        "candidate_path": str(candidate),
        "candidate_sha256": candidate_hash,
        "engine": installed_engine,
        "seeds": stage["seeds"],
        "seats": [0, 1],
        "opponents": opponents,
        "timeout_seconds": args.timeout,
        "replay_policy": "all",
    }
    out = OUT_ROOT / candidate_hash / args.phase
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / "manifest.json"
    if manifest_path.exists() and canonical(json.loads(manifest_path.read_text())) != canonical(manifest):
        raise SystemExit("Existing run manifest differs; use a new frozen candidate hash or phase")
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    frozen_candidate = out / "candidate.py"
    if frozen_candidate.exists():
        if sha(frozen_candidate) != candidate_hash:
            raise SystemExit("Saved candidate snapshot hash mismatch")
    else:
        shutil.copyfile(candidate, frozen_candidate)
        if sha(frozen_candidate) != candidate_hash:
            frozen_candidate.unlink(missing_ok=True)
            raise SystemExit("Could not create a byte-identical candidate snapshot")

    tasks = [(name, seed, seat) for seed in stage["seeds"] for name in names for seat in (0, 1)]
    pending = []
    records = []
    for name, seed, seat in tasks:
        swapped = bool(seat)
        spec = MatchSpec(Opponent(name, ROOT / opponents[name]["path"]), seed, swapped, 0)
        game_id = _game_id(spec)
        result = out / "games" / f"{game_id}.json"
        if result.is_file():
            row = json.loads(result.read_text())
            if (row.get("candidate_sha256") == candidate_hash and
                    row.get("opponent_sha256") == opponents[name]["sha256"] and
                    row.get("seed") == seed and row.get("candidate_seat") == seat and row.get("engine") == installed_engine):
                replay = out / "replays" / f"{game_id}.json"
                row["shop_unlock_sequence"], row["shop_signature"] = shop_schedule(replay)
                records.append(row)
                continue
            raise SystemExit(f"Existing result has mismatched provenance: {result}")
        pending.append((name, seed, seat, spec))

    print(f"phase={args.phase} candidate={candidate_hash} scheduled={len(pending)} resumed={len(records)} total={len(tasks)}", flush=True)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(_run_worker, frozen_candidate, spec, out, args.timeout, "all"): (name, seed, seat)
            for name, seed, seat, spec in pending
        }
        for future in as_completed(futures):
            name, seed, seat = futures[future]
            row = future.result()
            row["candidate_sha256"] = candidate_hash
            row["opponent_sha256"] = opponents[name]["sha256"]
            row["engine"] = installed_engine
            row["shop_unlock_sequence"], row["shop_signature"] = shop_schedule(out / "replays" / f"{row['game_id']}.json")
            result_path = out / "games" / f"{row['game_id']}.json"
            result_path.write_text(json.dumps(row, indent=2, sort_keys=True) + "\n")
            records.append(row)
            print(f"completed={len(records)}/{len(tasks)} errors={sum(not r.get('ok') for r in records)}", flush=True)

    if sha(candidate) != candidate_hash:
        raise SystemExit("Candidate changed during evaluation; results retained but phase is invalid")
    for name, details in opponents.items():
        if sha(ROOT / details["path"]) != details["sha256"]:
            raise SystemExit(f"Opponent changed during evaluation: {name}")
    records.sort(key=lambda r: (r["opponent"], r["seed"], r["candidate_seat"]))
    (out / "games.json").write_text(json.dumps(records, separators=(",", ":")) + "\n")
    print(f"Saved {len(records)} game rows under {out.relative_to(ROOT)}. Run analyze.py with the same --candidate and --phase.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

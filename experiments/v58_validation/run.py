"""Run the frozen v58 baseline screen. Results are isolated under experiments/runs."""
from __future__ import annotations

import hashlib
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

from simulation.tournament import MatchSpec, Opponent, _game_id, _run_worker

ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "experiments/v58_validation/plan.json"
OUT = ROOT / "experiments/runs/v58_validation_baseline"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    os.chdir(ROOT)
    plan = json.loads(PLAN.read_text())
    candidate = ROOT / plan["candidate"]
    if sha(candidate) != plan["candidate_sha256"]:
        raise SystemExit("Frozen baseline candidate hash mismatch")
    hashes = {name: sha(ROOT / path) for name, path in plan["opponents"].items()}
    tasks = [(name, seed, seat) for seed in plan["seeds"]
             for name in plan["opponents"] for seat in plan["seats"]]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "plan.json").write_text(json.dumps({**plan, "opponent_sha256": hashes}, indent=2) + "\n")
    pending = []
    records = []
    for name, seed, seat in tasks:
        spec = MatchSpec(Opponent(name, ROOT / plan["opponents"][name]), seed, bool(seat), 0)
        result = OUT / "games" / f"{_game_id(spec)}.json"
        if result.exists():
            row = json.loads(result.read_text())
            if row.get("agents", [{}])[row.get("candidate_seat", 0)].get("sha256") == plan["candidate_sha256"]:
                records.append(row)
                continue
        pending.append((name, seed, seat, spec))
    started = time.monotonic()
    print(f"scheduled={len(pending)} resumed={len(records)} total={len(tasks)}", flush=True)
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {}
        for name, seed, seat, spec in pending:
            futures[pool.submit(_run_worker, candidate, spec, OUT, 240, "errors")] = (name, seed, seat)
        for future in as_completed(futures):
            row = future.result()
            records.append(row)
            print(f"completed={len(records)}/{len(tasks)} errors={sum(not r.get('ok') for r in records)} elapsed={time.monotonic()-started:.0f}s", flush=True)
    plan_hashes_ok = sha(candidate) == plan["candidate_sha256"] and all(
        sha(ROOT / plan["opponents"][name]) == digest for name, digest in hashes.items())
    if not plan_hashes_ok:
        raise SystemExit("A frozen artifact changed during the screen")
    records.sort(key=lambda r: (r["opponent"], r["seed"], r["candidate_seat"]))
    (OUT / "games.json").write_text(json.dumps(records, separators=(",", ":")) + "\n")
    summary = {"finished_at": datetime.now(UTC).isoformat(), "plan_hashes_verified": True,
               "games": len(records), "errors": sum(not r.get("ok") for r in records),
               "wins": sum(r.get("winner_seat") == r.get("candidate_seat") for r in records),
               "losses": sum(r.get("winner_seat") is not None and r.get("winner_seat") != r.get("candidate_seat") for r in records),
               "draws": sum(r.get("winner_seat") is None and r.get("ok") for r in records),
               "elapsed_seconds": round(time.monotonic()-started, 1)}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return int(summary["errors"] > 0)


if __name__ == "__main__":
    raise SystemExit(main())

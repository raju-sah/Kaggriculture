"""Same-seed two-seat cashflow preflight for source revisions."""
from __future__ import annotations

import hashlib
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from simulation.tournament import MatchSpec, Opponent, _run_worker

ROOT = Path(__file__).resolve().parents[3]
POLICY = ROOT / "experiments/v58_validation/original_route/agent.py"
OPPONENT = ROOT / "experiments/v48_agent.py"
SEED = 94403
OUT = ROOT / "experiments/runs/v58_validation_original_route/preflight_guarded"
OLD = ROOT / "experiments/runs/v58_validation_original_route/preflight_94403/games.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    os.chdir(ROOT)
    policy_hash, opponent_hash = sha(POLICY), sha(OPPONENT)
    OUT.mkdir(parents=True, exist_ok=True)
    old_rows = json.loads(OLD.read_text()) if OLD.exists() else []
    old_by_seat = {r["candidate_seat"]: r for r in old_rows}
    specs = [MatchSpec(Opponent("v48", OPPONENT), SEED, bool(swapped), 0) for swapped in (0, 1)]
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {pool.submit(_run_worker, POLICY, spec, OUT / "original", 240, "all"): spec
                   for spec in specs}
        rows = [future.result() for future in as_completed(futures)]
    rows.sort(key=lambda r: r["candidate_seat"])
    (OUT / "games.json").write_text(json.dumps(rows, indent=2) + "\n")
    result = {"seed": SEED, "policy_sha256": policy_hash, "opponent_sha256": opponent_hash,
              "errors": sum(not r.get("ok") for r in rows),
              "current": [{"candidate_seat": r["candidate_seat"], "final_coins": r.get("final_coins"),
                           "result": r.get("candidate_result")} for r in rows],
              "previous_same_seed": [{"candidate_seat": r["candidate_seat"], "final_coins": r.get("final_coins"),
                                      "result": r.get("candidate_result")} for r in old_rows],
              "reused_previous_seeds": False, "purpose": "development cashflow preflight only"}
    (OUT / "analysis.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if sha(POLICY) != policy_hash or sha(OPPONENT) != opponent_hash:
        raise SystemExit("Source changed during preflight")
    return 0 if result["errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

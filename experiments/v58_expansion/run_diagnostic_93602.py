"""Rerun seed 93602 with full replays to locate v54/v56 regressions."""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from simulation.tournament import MatchSpec, Opponent, _run_worker

BASELINE = ROOT / "experiments/v57_broad/v57_reset_candidate.py"
EXPANSION = ROOT / "experiments/v58_expansion/v58_expansion_candidate.py"
OPPONENTS = {name: ROOT / f"agents/{name}_agent.py" for name in ("v54",)}
OUT = ROOT / "experiments/v58_expansion/diagnostic_93602"


def main() -> int:
    os.chdir(ROOT)
    expected = {
        "baseline": "4173479fe1f80d031d570d1ea23b694dfe86e1d162317a4c9c7df0058a40208e",
        "expansion": "20c5a4a2e0d96d39cdd9e26de9daff0e685b66b5ec7f943f1e85ae38330e09fc",
    }
    arms = {"baseline": BASELINE, "expansion": EXPANSION}
    tasks = []
    for arm, candidate in arms.items():
        actual = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if actual != expected[arm]:
            raise SystemExit(f"{arm} candidate hash mismatch: {actual}")
        arm_out = OUT / arm
        arm_out.mkdir(parents=True, exist_ok=True)
        plan = {"candidate": str(candidate.relative_to(ROOT)), "candidate_sha256": actual,
                "opponents": {k: str(v.relative_to(ROOT)) for k,v in OPPONENTS.items()},
                "seed": 93602, "seats": [0,1], "replay_policy": "all"}
        (arm_out / "plan.json").write_text(json.dumps(plan,indent=2)+"\n")
        for name, path in OPPONENTS.items():
            for seat in (0,1):
                tasks.append((arm,candidate,MatchSpec(Opponent(name,path),93602,bool(seat),0)))
    rows={k:[] for k in arms};started=time.monotonic()
    with ThreadPoolExecutor(max_workers=4) as pool:
        future_map={pool.submit(_run_worker,candidate,spec,OUT/arm,240,"all"):(arm,spec)
                    for arm,candidate,spec in tasks}
        for future in as_completed(future_map):
            arm,spec=future_map[future];row=future.result();rows[arm].append(row)
            print(arm,spec.opponent.name,spec.seed,"candidate_seat",1 if spec.swapped else 0,
                  row.get("final_coins"),"elapsed",round(time.monotonic()-started),flush=True)
    for arm,items in rows.items():
        items.sort(key=lambda r:(r["opponent"],r["candidate_seat"]))
        (OUT/arm/"games.json").write_text(json.dumps(items,indent=2)+"\n")
    return 0 if all(r.get("ok") for v in rows.values() for r in v) else 1


if __name__=="__main__":
    raise SystemExit(main())

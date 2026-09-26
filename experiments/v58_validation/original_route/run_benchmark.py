"""Paired fresh-seed benchmark for the independent route prototype."""
from __future__ import annotations

import hashlib
import json
import os
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from simulation.tournament import MatchSpec, Opponent, _game_id, _run_worker

ROOT = Path(__file__).resolve().parents[3]
BASELINE = ROOT / "experiments/v57_broad/v57_reset_candidate.py"
ORIGINAL = ROOT / "experiments/v58_validation/original_route/agent.py"
OUT = ROOT / "experiments/runs/v58_validation_original_route"
SEEDS = [94400, 94401, 94402]
OPPONENTS = {
    "v48": "experiments/v48_agent.py",
    "v50": "experiments/v50_agent.py",
    "v53": "experiments/v53_agent.py",
    "v54": "agents/v54_agent.py",
    "v56": "agents/v56_agent.py",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def play_arm(arm: str, candidate: Path) -> list[dict]:
    folder = OUT / arm
    folder.mkdir(parents=True, exist_ok=True)
    opp_paths = {name: ROOT / rel for name, rel in OPPONENTS.items()}
    plan = {"arm": arm, "candidate": str(candidate.relative_to(ROOT)), "candidate_sha256": sha(candidate),
            "opponents": OPPONENTS, "opponent_sha256": {n: sha(p) for n, p in opp_paths.items()},
            "seeds": SEEDS, "seats": [0, 1], "repeats": 1, "replay_policy": "all",
            "final_93000_93049_used": False}
    plan_path = folder / "plan.json"
    if plan_path.exists():
        old = json.loads(plan_path.read_text())
        if old != plan:
            raise SystemExit(f"Refusing to reuse {arm} output for changed hashes or plan")
    plan_path.write_text(json.dumps(plan, indent=2) + "\n")
    specs = [MatchSpec(Opponent(n, p), seed, bool(swapped), 0)
             for seed in SEEDS for n, p in opp_paths.items() for swapped in (0, 1)]
    rows = []
    pending = []
    for spec in specs:
        game_id = _game_id(spec)
        p = folder / "games" / f"{game_id}.json"
        if p.exists():
            old = json.loads(p.read_text())
            if old.get("ok") is True and old.get("seed") == spec.seed and old.get("opponent") == spec.opponent.name:
                rows.append(old)
                continue
        pending.append(spec)
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(_run_worker, candidate, spec, folder, 240, "all"): spec for spec in pending}
        for future in as_completed(futures):
            row = future.result()
            rows.append(row)
            print(f"{arm} {row['opponent']} {row['seed']} seat={row['candidate_seat']} "
                  f"coins={row.get('final_coins')} ok={row.get('ok')}", flush=True)
    rows.sort(key=lambda r: (r["opponent"], r["seed"], r["candidate_seat"]))
    (folder / "games.json").write_text(json.dumps(rows, indent=2) + "\n")
    return rows


def margin(row: dict) -> float:
    s = row["candidate_seat"]
    return float(row["final_coins"][s] - row["final_coins"][1-s])


def main() -> int:
    os.chdir(ROOT)
    base_hash = sha(BASELINE)
    original_hash = sha(ORIGINAL)
    preflight = OUT / "preflight_94403"
    preflight.mkdir(parents=True, exist_ok=True)
    first_opponent = Opponent("v48", ROOT / OPPONENTS["v48"])
    with ThreadPoolExecutor(max_workers=2) as pool:
        fs = {pool.submit(_run_worker, ORIGINAL, MatchSpec(first_opponent, 94403, bool(swapped), 0),
                          preflight / "original", 240, "all"): swapped for swapped in (0, 1)}
        preflight_rows = [f.result() for f in as_completed(fs)]
    (preflight / "games.json").write_text(json.dumps(preflight_rows, indent=2) + "\n")
    print("preflight_94403", json.dumps({"games": len(preflight_rows),
          "errors": sum(not r.get("ok") for r in preflight_rows),
          "results": [r.get("candidate_result") for r in preflight_rows]}), flush=True)
    if any(not r.get("ok") for r in preflight_rows):
        raise SystemExit("Original agent failed the two-seat preflight; do not start panel")
    base = play_arm("baseline", BASELINE)
    original = play_arm("original", ORIGINAL)
    if sha(BASELINE) != base_hash or sha(ORIGINAL) != original_hash:
        raise SystemExit("Candidate bytes changed during benchmark")
    bmap = {(r["opponent"], r["seed"], r["candidate_seat"]): r for r in base}
    omap = {(r["opponent"], r["seed"], r["candidate_seat"]): r for r in original}
    paired = []
    for key in sorted(bmap):
        b, o = bmap[key], omap[key]
        if not b.get("ok") or not o.get("ok"):
            delta = None
        else:
            delta = margin(o) - margin(b)
        paired.append({"opponent": key[0], "seed": key[1], "candidate_seat": key[2],
                       "baseline_margin": margin(b) if b.get("ok") else None,
                       "original_margin": margin(o) if o.get("ok") else None,
                       "paired_margin_delta": delta,
                       "baseline_result": b.get("candidate_result"),
                       "original_result": o.get("candidate_result"),
                       "baseline_error": not b.get("ok"), "original_error": not o.get("ok")})
    (OUT / "paired.json").write_text(json.dumps(paired, indent=2) + "\n")
    by_opponent = {}
    for name in OPPONENTS:
        group = [r for r in paired if r["opponent"] == name]
        valid = [r["paired_margin_delta"] for r in group if r["paired_margin_delta"] is not None]
        by_opponent[name] = {"games": len(group), "errors": sum(r["baseline_error"] or r["original_error"] for r in group),
                             "baseline_wins": sum(r["baseline_result"] == "win" for r in group),
                             "original_wins": sum(r["original_result"] == "win" for r in group),
                             "mean_paired_margin_delta": statistics.fmean(valid) if valid else None}
    valid = [r["paired_margin_delta"] for r in paired if r["paired_margin_delta"] is not None]
    result = {"baseline_sha256": base_hash, "original_sha256": original_hash, "seeds": SEEDS,
              "games": len(paired), "errors": sum(r["baseline_error"] or r["original_error"] for r in paired),
              "mean_paired_margin_delta": statistics.fmean(valid) if valid else None,
              "opponents": by_opponent, "paired": paired}
    (OUT / "analysis.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("paired",)}, indent=2))
    return 0 if result["errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

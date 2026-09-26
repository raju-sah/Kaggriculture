"""Pair a candidate against the same opponent on fresh seeds, both seats."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from simulation.tournament import MatchSpec, Opponent, _game_id, _run_worker

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OPPONENT = ROOT / "experiments/v48_agent.py"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--seeds", required=True, help="comma-separated seed integers")
    parser.add_argument("--opponent", type=Path, default=DEFAULT_OPPONENT)
    parser.add_argument("--name", default="early-sale-probe")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    os.chdir(ROOT)
    candidate = args.candidate.resolve()
    opponent = args.opponent.resolve()
    out = args.out if args.out.is_absolute() else ROOT / args.out
    seeds = [int(x.strip()) for x in args.seeds.split(",") if x.strip()]
    out.mkdir(parents=True, exist_ok=True)
    candidate_hash = digest(candidate)
    opponent_hash = digest(opponent)
    manifest = {"candidate": str(candidate.relative_to(ROOT)),
                "candidate_sha256": candidate_hash,
                "opponent": str(opponent.relative_to(ROOT)),
                "opponent_sha256": opponent_hash,
                "seeds": seeds, "seats": [0, 1], "name": args.name}
    (out / "plan.json").write_text(json.dumps(manifest, indent=2) + "\n")

    specs = [MatchSpec(Opponent(args.name, opponent), seed, bool(seat), 0)
             for seed in seeds for seat in (0, 1)]
    records = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(_run_worker, candidate, spec, out, 240, "all"): spec
                   for spec in specs}
        for future in as_completed(futures):
            row = future.result()
            records.append(row)
            print(f"done {row['game_id']} ok={row.get('ok')} result={row.get('candidate_result')}", flush=True)
    if digest(candidate) != candidate_hash or digest(opponent) != opponent_hash:
        raise SystemExit("An agent file changed during the paired probe")
    records.sort(key=lambda r: (r["seed"], r["candidate_seat"]))
    (out / "games.json").write_text(json.dumps(records, separators=(",", ":")) + "\n")
    summary = {"games": len(records),
               "errors": sum(not r.get("ok") for r in records),
               "wins": sum(r.get("candidate_result") == "win" for r in records),
               "losses": sum(r.get("candidate_result") == "loss" for r in records),
               "draws": sum(r.get("candidate_result") == "draw" for r in records),
               "mean_margin": round(sum((r["final_coins"][r["candidate_seat"]]
                                          - r["final_coins"][r["opponent_seat"]])
                                         for r in records if r.get("final_coins"))
                                    / max(1, sum(bool(r.get("final_coins")) for r in records)), 2),
               "margins_by_seed": {str(seed): [r["final_coins"][r["candidate_seat"]]
                                               - r["final_coins"][r["opponent_seat"]]
                                               for r in records if r["seed"] == seed and r.get("final_coins")]
                                   for seed in seeds}}
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

"""V101 development panel: candidate vs frozen V92 and V50, both seats.

Exact Kaggle loader (simulation.tournament / match_worker), pinned kaggriculture
1.32.7, engine sha256 bc8a5487...653e. Development seeds 160001-160060, which
belong to this worker only; the other agent's 150001-150080 range and the spent
V99 holdouts (137501-137524, 93000-93011) are untouched.

    .venv/bin/python experiments/v101_commandcode/screen.py --workers 2
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CAND = HERE / "candidate.py"
DEV_SEEDS = list(range(160001, 160061))
OPPONENTS = {
    "v92": ROOT / "experiments/v92_overflow_guard/candidate.py",
    "v50": ROOT / "experiments/v50_agent.py",
    "v56": ROOT / "agents/v56_agent.py",
}


def run(tag: str, outdir: Path, workers: int) -> int:
    cmd = [sys.executable, "-m", "simulation.tournament",
           "--candidate", str(CAND), "--opponent", f"{tag}={OPPONENTS[tag]}",
           "--seeds", ",".join(str(s) for s in DEV_SEEDS),
           "--workers", str(workers), "--timeout", "900",
           "--replay-policy", "errors", "--output-dir", str(outdir)]
    print(f"  $ V101 vs {tag} ({len(DEV_SEEDS)} seeds x 2 seats, {workers} workers)", flush=True)
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=86400)
    (outdir / "runner.log").write_text(proc.stdout + "\n" + proc.stderr, encoding="utf-8")
    return proc.returncode


def summarize(outdir: Path, label: str) -> dict:
    rows = [json.loads(l) for l in (outdir / "games.jsonl").read_text().splitlines() if l.strip()]
    wins = sum(r["candidate_result"] == "win" for r in rows)
    losses = sum(r["candidate_result"] == "loss" for r in rows)
    draws = sum(r["candidate_result"] == "draw" for r in rows)
    errs = (sum(bool(r["candidate_error"]) for r in rows)
            + sum(bool(r["opponent_error"]) for r in rows)
            + sum(bool(r["infrastructure_error"]) for r in rows)
            + sum(bool(r["timed_out"]) for r in rows))
    margins = [r["final_coins"][r["candidate_seat"]] - r["final_coins"][r["opponent_seat"]]
               for r in rows if r.get("final_coins")]
    runtime = [r["runtime_seconds"] for r in rows]

    # Effective sample = distinct seeds with a decisive result. Both seat orders
    # of a seed are the same deterministic game, so games are not independent.
    decisive: dict[int, float] = {}
    for r in rows:
        d = r["final_coins"][r["candidate_seat"]] - r["final_coins"][r["opponent_seat"]]
        decisive.setdefault(r["seed"], d)
    decisive_seeds = [d for d in decisive.values() if d != 0]
    ties = sum(1 for d in decisive.values() if d == 0)

    # seat-swap identity
    by_key: dict[tuple, list[float]] = {}
    for r in rows:
        d = r["final_coins"][r["candidate_seat"]] - r["final_coins"][r["opponent_seat"]]
        by_key.setdefault((r["seed"], r["repeat"]), []).append(d)
    swaps_identical = all(len(set(v)) == 1 for v in by_key.values())

    print(f"\n--- {label} ---")
    print(f"  {len(rows)} games  {wins}W-{losses}L-{draws}D  errors/timeouts {errs}")
    print(f"  score rate {(wins + 0.5*draws)/max(1,len(rows)):.3f}  "
          f"decisive win rate {wins/(wins+losses) if wins+losses else 0:.3f}")
    if margins:
        print(f"  paired margin: mean {statistics.fmean(margins):+,.0f}  "
              f"median {statistics.median(margins):+,.0f}  "
              f"range {min(margins):+,.0f}..{max(margins):+,.0f}")
    print(f"  distinct seeds {len(decisive)}  decisive seeds {len(decisive_seeds)}  "
          f"ties {ties}  (effective n = {len(decisive_seeds)})")
    print(f"  seat-swap identical margins: {swaps_identical}")
    if runtime:
        print(f"  runtime mean {statistics.fmean(runtime):.0f}s max {max(runtime):.0f}s")
    for seed in sorted(decisive):
        d = decisive[seed]
        tagline = "tie " if d == 0 else ("WIN " if d > 0 else "LOSS")
        print(f"    {seed} {tagline} {d:>+10,.0f}")

    return {"games": len(rows), "wins": wins, "losses": losses, "draws": draws,
            "errors": errs, "effective_n": len(decisive_seeds), "ties": ties,
            "seat_swap_identical": swaps_identical,
            "mean_margin": statistics.fmean(margins) if margins else None,
            "median_margin": statistics.median(margins) if margins else None,
            "per_seed": {str(k): v for k, v in sorted(decisive.items())}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--opponents", default="v92,v50")
    ap.add_argument("--workers", type=int, default=2)
    args = ap.parse_args()
    if not 1 <= args.workers <= 2:
        print("workers must be 1 or 2 (another worker is on this machine)", file=sys.stderr)
        return 2

    res = {}
    for tag in args.opponents.split(","):
        outdir = HERE / "runs" / f"dev_vs_{tag}"
        rc = run(tag, outdir, args.workers)
        print(f"    runner exit={rc}")
        res[tag] = summarize(outdir, f"V101 vs {tag.upper()} (dev 160001-160060, both seats)")
    (HERE / "dev_results.json").write_text(json.dumps(res, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

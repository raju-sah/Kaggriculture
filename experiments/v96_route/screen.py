#!/usr/bin/env python3
"""V96 cheap screen: run a route candidate against V50 and V92 on spent seeds.

This is the feasibility screen required before any promotion gate is frozen. It
answers, on already-spent seeds and in both seats, through the exact Kaggle loader:

  * does the candidate's action stream actually DIFFER from the incumbent (a candidate
    that never changes an action is an invalid test, not a win);
  * are there zero errors, and what is the runtime;
  * what is the paired cash margin, per seed and per seat.

Seeds are ALREADY-SPENT and reused from the V93/V95 dev panel (each has >=22 prior
saved games in experiments/**/games.jsonl). Spending them again costs no new evidence.
Seeds 93000-93011 are excluded entirely (consumed by the V92 holdout).

Run from repo root:
    .venv/bin/python experiments/v96_route/screen.py --candidate candidate_a.py
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

DEV_SEEDS = [92600, 92601, 92602, 92603, 92604, 92802, 93700, 94700, 95100, 95200, 95300]
OPPONENTS = {
    "v92": ROOT / "experiments/v92_overflow_guard/candidate.py",
    "v50": ROOT / "experiments/v50_agent.py",
    "v56": ROOT / "agents/v56_agent.py",
}


def run(candidate: Path, tag: str, opp: Path, seeds, outdir: Path, replay="errors"):
    cmd = [sys.executable, "-m", "simulation.tournament",
           "--candidate", str(candidate), "--opponent", f"{tag}={opp}",
           "--seeds", ",".join(str(s) for s in seeds),
           "--workers", "8", "--timeout", "900",
           "--replay-policy", replay, "--output-dir", str(outdir)]
    print(f"  $ ... {candidate.name} vs {tag}  ({len(seeds)} seeds x 2 seats)", flush=True)
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=14400)
    (outdir / "runner.log").write_text(proc.stdout + "\n" + proc.stderr, encoding="utf-8")
    return proc.returncode


def summarize(outdir: Path, label: str):
    rows = [json.loads(l) for l in (outdir / "games.jsonl").read_text().splitlines() if l.strip()]
    wins = sum(r["candidate_result"] == "win" for r in rows)
    losses = sum(r["candidate_result"] == "loss" for r in rows)
    draws = sum(r["candidate_result"] == "draw" for r in rows)
    errs = (sum(bool(r["candidate_error"]) for r in rows)
            + sum(bool(r["opponent_error"]) for r in rows)
            + sum(bool(r["infrastructure_error"]) for r in rows)
            + sum(bool(r["timed_out"]) for r in rows))
    margins = [r["final_coins"][r["candidate_seat"]] - r["final_coins"][r["opponent_seat"]]
               for r in rows
               if r.get("final_coins") and r["final_coins"][r["candidate_seat"]] is not None
               and r["final_coins"][r["opponent_seat"]] is not None]
    runtime = [r["runtime_seconds"] for r in rows]
    # Distinct replay hashes per seed tells us whether the action stream really changed:
    # identical policies on a seed give an identical hash for both seat orders.
    hashes = {}
    for r in rows:
        hashes.setdefault(r["seed"], set()).add(r["replay_sha256"])
    identical = sum(1 for v in hashes.values() if len(v) == 1)
    print(f"\n--- {label} ---")
    print(f"  {len(rows)} games  {wins}W-{losses}L-{draws}D  score_rate {(wins+0.5*draws)/max(1,len(rows)):.3f}  errors {errs}")
    if margins:
        print(f"  paired margin: mean {statistics.fmean(margins):+,.0f}  median {statistics.median(margins):+,.0f}  "
              f"range {min(margins):+,.0f}..{max(margins):+,.0f}")
        print(f"  positive {sum(1 for m in margins if m > 0)}/{len(margins)}  "
              f"negative {sum(1 for m in margins if m < 0)}  zero {sum(1 for m in margins if m == 0)}")
    if runtime:
        print(f"  runtime mean {statistics.fmean(runtime):.0f}s max {max(runtime):.0f}s")
    print(f"  seat-invariant (identical result in both seats) on {identical}/{len(hashes)} seeds")
    return {"games": len(rows), "wins": wins, "losses": losses, "draws": draws, "errors": errs,
            "score_rate": (wins + 0.5 * draws) / max(1, len(rows)),
            "margins": margins,
            "mean_margin": statistics.fmean(margins) if margins else None,
            "median_margin": statistics.median(margins) if margins else None,
            "positive": sum(1 for m in margins if m > 0) if margins else 0,
            "seat_invariant_seeds": identical, "n_seeds": len(hashes)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--opponents", default="v92,v50")
    args = ap.parse_args()
    cand = HERE / args.candidate
    stem = cand.stem
    results = {}
    for tag in args.opponents.split(","):
        outdir = HERE / "runs" / f"screen_{stem}_vs_{tag}"
        rc = run(cand, tag, OPPONENTS[tag], DEV_SEEDS, outdir)
        print(f"    runner exit={rc}")
        results[tag] = summarize(outdir, f"{stem} vs {tag.upper()} (dev seeds, both seats)")
    (HERE / f"screen_{stem}.json").write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    main()

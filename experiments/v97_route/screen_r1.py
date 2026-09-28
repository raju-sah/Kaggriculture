#!/usr/bin/env python3
"""V97 step 4: spent-seed screen for the multi-turn route, both seats, vs V50 and V92.

Exact Kaggle loader (simulation.tournament / match_worker), pinned kaggriculture 1.32.7.
11 already-spent seeds (each >=22 prior saved games in experiments/**/games.jsonl), both
seat orders. Seeds 93000-93011 are excluded (consumed by the V92 holdout).

Reported per arm: wins/losses/draws, paired cash margin per seed and per seat, error
counts, runtime, and whether the action stream actually differed from the incumbent
(seat-invariant seeds mean identical outcomes in both seats, which for this candidate
should be near zero because the route is deterministic and seed-dependent).

Run from repo root:
    .venv/bin/python experiments/v97_route/screen.py
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
CAND = HERE / "candidate_r1.py"
DEV_SEEDS = [92600, 92601, 92602, 92603, 92604, 92802, 93700, 94700, 95100, 95200, 95300]
OPPONENTS = {
    "v92": ROOT / "experiments/v92_overflow_guard/candidate.py",
    "v50": ROOT / "experiments/v50_agent.py",
    "v56": ROOT / "agents/v56_agent.py",
}


def run(tag, opp, outdir, replay="errors"):
    cmd = [sys.executable, "-m", "simulation.tournament",
           "--candidate", str(CAND), "--opponent", f"{tag}={opp}",
           "--seeds", ",".join(str(s) for s in DEV_SEEDS),
           "--workers", "8", "--timeout", "900",
           "--replay-policy", replay, "--output-dir", str(outdir)]
    print(f"  $ route vs {tag} ({len(DEV_SEEDS)} seeds x 2 seats)", flush=True)
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=14400)
    (outdir / "runner.log").write_text(proc.stdout + "\n" + proc.stderr, encoding="utf-8")
    return proc.returncode


def summarize(outdir, label):
    rows = [json.loads(l) for l in (outdir / "games.jsonl").read_text().splitlines() if l.strip()]
    wins = sum(r["candidate_result"] == "win" for r in rows)
    losses = sum(r["candidate_result"] == "loss" for r in rows)
    draws = sum(r["candidate_result"] == "draw" for r in rows)
    errs = (sum(bool(r["candidate_error"]) for r in rows) + sum(bool(r["opponent_error"]) for r in rows)
            + sum(bool(r["infrastructure_error"]) for r in rows) + sum(bool(r["timed_out"]) for r in rows))
    margins = [r["final_coins"][r["candidate_seat"]] - r["final_coins"][r["opponent_seat"]] for r in rows]
    runtime = [r["runtime_seconds"] for r in rows]
    hashes = {}
    for r in rows:
        hashes.setdefault(r["seed"], set()).add(r["replay_sha256"])
    invariant = sum(1 for v in hashes.values() if len(v) == 1)
    print(f"\n--- {label} ---")
    print(f"  {len(rows)} games  {wins}W-{losses}L-{draws}D  score_rate {(wins+0.5*draws)/max(1,len(rows)):.3f}  errors {errs}")
    if margins:
        print(f"  paired margin: mean {statistics.fmean(margins):+,.0f}  median {statistics.median(margins):+,.0f}  "
              f"range {min(margins):+,.0f}..{max(margins):+,.0f}")
        print(f"  positive {sum(1 for m in margins if m>0)}/{len(margins)}  negative {sum(1 for m in margins if m<0)}  zero {sum(1 for m in margins if m==0)}")
    if runtime:
        print(f"  runtime mean {statistics.fmean(runtime):.0f}s max {max(runtime):.0f}s")
    print(f"  seeds where both seats gave an identical result: {invariant}/{len(hashes)}")
    for r in rows:
        d = r["final_coins"][r["candidate_seat"]] - r["final_coins"][r["opponent_seat"]]
        print(f"    {r['game_id']:<42} {r['candidate_result']:<5} {d:>+9,.0f}")
    return {"games": len(rows), "wins": wins, "losses": losses, "draws": draws, "errors": errs,
            "score_rate": (wins + 0.5 * draws) / max(1, len(rows)), "margins": margins,
            "mean_margin": statistics.fmean(margins) if margins else None,
            "median_margin": statistics.median(margins) if margins else None,
            "positive": sum(1 for m in margins if m > 0) if margins else 0,
            "seat_invariant": invariant, "n_seeds": len(hashes)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--opponents", default="v92,v50")
    args = ap.parse_args()
    res = {}
    for tag in args.opponents.split(","):
        outdir = HERE / "runs" / f"screen_r1_vs_{tag}"
        rc = run(tag, OPPONENTS[tag], outdir)
        print(f"    runner exit={rc}")
        res[tag] = summarize(outdir, f"V97-R1 vs {tag.upper()} (dev seeds, both seats)")
    (HERE / "screen_r1_results.json").write_text(json.dumps(res, indent=2) + "\n")


if __name__ == "__main__":
    main()

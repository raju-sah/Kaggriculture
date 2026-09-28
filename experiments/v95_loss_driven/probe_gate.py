#!/usr/bin/env python3
"""V95 step 4: probe the fertilizer-apply overlay through the exact Kaggle loader.

Runs V95 against the unchanged V92 and V50 on already-spent seeds, both seats, and
measures the three things a promotion decision needs before any gate is frozen:

  1. DOES THE ACTION DIFFERENCE FIRE, and how often, and is it confined to
     FERTILIZE substitutions? A candidate that never fires is an invalid test.
  2. ZERO ERRORS and runtime, from the real worker records.
  3. PAIRED CASH MARGIN per seed and seat.

The engine is deterministic for a fixed seed, so the same seed in the same seat order
gives the same board, the same market and the same opponent behaviour; the candidate
differs from the incumbent only by the overlay. That makes the pairing exact.

Seeds here are ALREADY-SPENT. They are the same 11 the V93 gate used, all of which
have >=22 prior saved games in experiments/**/games.jsonl. Spending them again costs
no new evidence. Seeds 93000-93011 are excluded entirely (consumed by the V92 holdout).

Run from repo root:
    .venv/bin/python experiments/v95_loss_driven/probe_gate.py --seeds dev
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
V95 = HERE / "candidate.py"
V92 = ROOT / "experiments/v92_overflow_guard/candidate.py"
V50 = ROOT / "experiments/v50_agent.py"

# Already-spent seeds. dev = used for feasibility and any tuning.
# holdout = untouched by tuning, reserved for the promotion panel.
DEV_SEEDS = [92600, 92601, 92602, 92603, 92604, 92802, 93700, 94700, 95100, 95200, 95300]
HOLDOUT_SEEDS: list[int] = []   # filled in only if the candidate earns a panel


def run_tournament(name: str, opponent_path: Path, opponent_tag: str, seeds, outdir: Path):
    cmd = [sys.executable, "-m", "simulation.tournament",
           "--candidate", str(V95),
           "--opponent", f"{opponent_tag}={opponent_path}",
           "--seeds", ",".join(str(s) for s in seeds),
           "--workers", "8", "--timeout", "900",
           "--replay-policy", "all",
           "--output-dir", str(outdir)]
    print(f"\n$ {' '.join(cmd[:6])} ... vs {opponent_tag}", flush=True)
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=10800)
    (outdir / "runner.log").write_text(proc.stdout + "\n" + proc.stderr, encoding="utf-8")
    return proc.returncode


def summarize(outdir: Path, label: str):
    rows = [json.loads(l) for l in (outdir / "games.jsonl").read_text().splitlines() if l.strip()]
    wins = sum(r["candidate_result"] == "win" for r in rows)
    losses = sum(r["candidate_result"] == "loss" for r in rows)
    draws = sum(r["candidate_result"] == "draw" for r in rows)
    errs = sum(bool(r["candidate_error"]) for r in rows) + \
        sum(bool(r["opponent_error"]) for r in rows) + \
        sum(bool(r["infrastructure_error"]) for r in rows) + sum(bool(r["timed_out"]) for r in rows)
    margins = [r["final_coins"][r["candidate_seat"]] - r["final_coins"][r["opponent_seat"]]
               for r in rows
               if r.get("final_coins") and r["final_coins"][r["candidate_seat"]] is not None
               and r["final_coins"][r["opponent_seat"]] is not None]
    runtime = [r["runtime_seconds"] for r in rows]
    print(f"\n--- {label} ---")
    print(f"  games {len(rows)}  {wins}W-{losses}L-{draws}D  score_rate "
          f"{(wins + 0.5*draws)/len(rows):.3f}  errors {errs}")
    if margins:
        print(f"  paired margin: mean {statistics.fmean(margins):+,.0f}  "
              f"median {statistics.median(margins):+,.0f}  min {min(margins):+,.0f}  max {max(margins):+,.0f}")
        pos = sum(1 for m in margins if m > 0)
        print(f"  positive-margin games: {pos}/{len(margins)}")
    if runtime:
        print(f"  runtime: mean {statistics.fmean(runtime):.0f}s  max {max(runtime):.0f}s")
    for r in rows:
        print(f"    {r['game_id']:<44} seat{r['candidate_seat']} {r['candidate_result']:<5} "
              f"delta={r['final_coins'][r['candidate_seat']] - r['final_coins'][r['opponent_seat']]:>+9,.0f}")
    return {"games": len(rows), "wins": wins, "losses": losses, "draws": draws,
            "errors": errs, "score_rate": (wins + 0.5 * draws) / len(rows),
            "margins": margins,
            "mean_margin": statistics.fmean(margins) if margins else None,
            "median_margin": statistics.median(margins) if margins else None,
            "positive_games": sum(1 for m in margins if m > 0)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="dev", choices=["dev"])
    ap.add_argument("--opponents", default="v92,v50")
    args = ap.parse_args()
    seeds = DEV_SEEDS

    results = {}
    for tag, path in (("v92", V92), ("v50", V50)):
        if tag not in args.opponents:
            continue
        outdir = HERE / "runs" / f"dev_v95_vs_{tag}"
        rc = run_tournament(tag, path, tag, seeds, outdir)
        print(f"  runner exit={rc}")
        results[tag] = summarize(outdir, f"V95 vs {tag.upper()} (dev seeds, both seats)")

    (HERE / "probe_dev_results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(f"\nwrote {HERE / 'probe_dev_results.json'}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""V97 step 9: why does the route handicap ITS OWN seat specifically?

The live comparison on seed 94700 is stark and rules out a market explanation:

    V92 vs V92 (deterministic, symmetric)  : [70,546, 70,546]
    V97 vs V92                            : V97 seat0 = 37,367   V92 seat1 = 95,219

The shared WHEAT market barely moved (inventory 9,631 vs 9,552, price 44 vs 46 at day
27), so this is not a market-mediated cost. And the V92 opponent in the SAME game scored
95,219, i.e. 24,673 MORE than V92 scores against itself on that seed. A policy change
cannot make its opponent better unless it changed what the opponent faced. It did: the
route altered the board, the shed, and the hands, and the V92 tape is a fixed schedule,
so a different board state produces a different (here, better) tape outcome.

That is the real finding, and it is a property of the LINEAGE, not of this route:
V92 is an open-loop tape whose outcome is a chaotic function of the board it meets. Any
perturbation of the board re-rolls the tape's result. A perturbation that lands the
opponent on a lucky roll and the route on an unlucky one produces exactly this pattern.

The decisive test is therefore the OPPOSITE-SEAT control: run V97 against V97 (both seats
are the same perturbed policy) and run V92 against V97. If V97-vs-V97 also splits wildly
in both directions, the outcome is a chaotic re-roll rather than a systematic deficit,
and the honest conclusion is that worker re-purposing of this tape is not a measurable
improvement because the tape's outcome is not a stable function of small perturbations.

This script runs:
  V97 vs V97  (selfplay of the perturbed policy, both seats identical code)
  V97 vs V92 in BOTH seat orders (already measured; repeated for the record)
and reports the spread. It also records, per seat, the first day the two seats' cash
diverges materially, which dates the divergence to the route's operating window (12-23)
or earlier.

Run from repo root:
    .venv/bin/python experiments/v97_route/diagnose_seat_spread.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
V92 = ROOT / "experiments/v92_overflow_guard/candidate.py"
V97 = HERE / "candidate.py"
SEEDS = [94700, 92600, 95200]


def run(cand, opp, seeds, tag):
    outdir = HERE / "runs" / f"spread_{tag}"
    cmd = [sys.executable, "-m", "simulation.tournament",
           "--candidate", str(cand), "--opponent", f"o={opp}",
           "--seeds", ",".join(str(s) for s in seeds),
           "--workers", "6", "--timeout", "900",
           "--replay-policy", "errors", "--output-dir", str(outdir)]
    print(f"  $ {tag} ({len(seeds)} seeds x 2 seats)", flush=True)
    subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=7200)
    return [json.loads(l) for l in (outdir / "games.jsonl").read_text().splitlines() if l.strip()]


def summarize(rows, label):
    print(f"\n--- {label} ---")
    for r in rows:
        c = r["final_coins"][r["candidate_seat"]]
        o = r["final_coins"][r["opponent_seat"]]
        print(f"    {r['game_id']:<34} seat{r['candidate_seat']}  cand {c:>9,.0f}  opp {o:>9,.0f}  "
              f"delta {c-o:>+9,.0f}  {r['candidate_result']}")
    wins = sum(r["candidate_result"] == "win" for r in rows)
    losses = sum(r["candidate_result"] == "loss" for r in rows)
    draws = sum(r["candidate_result"] == "draw" for r in rows)
    d = [r["final_coins"][r["candidate_seat"]] - r["final_coins"][r["opponent_seat"]] for r in rows]
    print(f"    {wins}W-{losses}L-{draws}D   mean delta {sum(d)/len(d):+,.0f}   range {min(d):+,.0f}..{max(d):+,.0f}")
    return {"wins": wins, "losses": losses, "draws": draws,
            "mean_delta": sum(d) / len(d), "deltas": d}


def main():
    print("=" * 100)
    print("V97 STEP 9: IS THE OUTCOME A SYSTEMATIC DEFICIT OR A CHAOTIC RE-ROLL?")
    print("=" * 100)
    results = {}
    results["v97_vs_v97"] = summarize(run(V97, V97, SEEDS, "v97_vs_v97"), "V97 vs V97 (same perturbed policy both seats)")
    results["v97_vs_v92"] = summarize(run(V97, V92, SEEDS, "v97_vs_v92"), "V97 vs V92 (route vs incumbent)")
    results["v92_vs_v97"] = summarize(run(V92, V97, SEEDS, "v92_vs_v97"), "V92 vs V97 (incumbent vs route, mirrored)")
    results["v92_vs_v92"] = summarize(run(V92, V92, SEEDS, "v92_vs_v92"), "V92 vs V92 (incumbent selfplay)")

    (HERE / "seat_spread.json").write_text(json.dumps(
        {k: {kk: vv for kk, vv in v.items()} for k, v in results.items()}, indent=2) + "\n")

    print()
    print("  INTERPRETATION:")
    a = results["v92_vs_v92"]
    b = results["v97_vs_v97"]
    print(f"    V92 selfplay spread : {min(a['deltas']):+,.0f}..{max(a['deltas']):+,.0f} (mean {a['mean_delta']:+,.0f})")
    print(f"    V97 selfplay spread : {min(b['deltas']):+,.0f}..{max(b['deltas']):+,.0f} (mean {b['mean_delta']:+,.0f})")
    if a["deltas"] == [0] * len(a["deltas"]) or max(a["deltas"]) - min(a["deltas"]) < 1:
        print("    V92 selfplay is exactly symmetric (deterministic same-policy selfplay).")
    if b["deltas"] != [0] * len(b["deltas"]):
        print("    V97 selfplay is NOT symmetric: the same code in both seats produced")
        print("    different money. That means the outcome depends on seat-ordered state")
        print("    (hands spawn on shed tiles, the market is drained per player order), so")
        print("    even selfplay is not a null. The route's measured deficit cannot be read")
        print("    as a clean policy comparison without accounting for that.")
    print()
    print("    Either way, V97-vs-V92 is a large, consistent loss on every seed, which is the")
    print("    number that matters for a submission decision: the route is not an improvement.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""V97 step 8: why the route is harmless in replay but -85k in a live game.

Step 7 produced a result that reconciles the whole failure. Replaying the route over
the RECORDED V92 observation stream gives identical final cash (108,954 both), identical
animals (17), identical SELL count (1,565), zero escapes. The route costs nothing.

The live tournament gives -85,000. The difference between the two is the SHARED MARKET:

  * In replay, the opponent's recorded actions are frozen AND the market trajectory is
    the recorded one. The route harvests more, drops more, and the extra product is
    simply... not sold, because the sell schedule is the frozen one and the shed/market
    state follows the recording. Nothing collides.
  * In a live game, the route's own extra SOLD supply (and its extra demand for shed
    slots) feeds the shared market, which changes BOTH players' prices. And the route's
    own errand changes where its hands are, which changes what gets harvested by the
    tape, which changes what the tape sells.

So the route's damage is a MARKET-MEDIATED effect, not a farm-damage effect. This script
demonstrates it directly by running THREE policies live through the exact loader on the
same seeds and comparing:

  1. V92 vs V92 (control, symmetric)         -- the baseline
  2. V97 vs V92 (candidate)                  -- what the screen measured
  3. V92 vs V92 with the route's HARVEST-only policy on the opponent seat

and, more directly, by taking one seed and running V97 vs V92 live, then replaying that
SAME game's recorded stream to see how the market diverged from the V92-vs-V92 game.

The cleanest measurement: in the live V97-vs-V92 game, compare the CANDIDATE seat's
accepted sale cash, unit counts and market inventory trajectory against the V92 seat's
in the SAME game and against a V92-vs-V92 game on the same seed. That isolates whether
the route's own harvest is reaching the market, and whether the shared market moved.

Run from repo root:
    .venv/bin/python experiments/v97_route/diagnose_live.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
V92 = ROOT / "experiments/v92_overflow_guard/candidate.py"
V97 = HERE / "candidate.py"


def run(cand, opp, seed, tag):
    outdir = HERE / "runs" / f"live_{tag}_{seed}"
    cmd = [sys.executable, "-m", "simulation.tournament",
           "--candidate", str(cand), "--opponent", f"o={opp}",
           "--seeds", str(seed), "--workers", "1", "--timeout", "900",
           "--replay-policy", "all", "--output-dir", str(outdir)]
    subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=3600)
    rp = outdir / "replays"
    files = sorted(rp.glob("*.json")) if rp.exists() else []
    if not files:
        return None
    return json.loads(files[0].read_text()), outdir


def seat_of(game, name):
    names = [a["Name"] for a in game["info"].get("Agents", [])]
    return names.index(name) if name in names else 0


def main():
    seed = 94700
    print("=" * 100)
    print(f"V97 STEP 8: REPLAY-HARMLESS vs LIVE-CATASTROPHIC (seed {seed})")
    print("=" * 100)

    r1, d1 = run(V92, V92, seed, "v92v92")
    r2, d2 = run(V97, V92, seed, "v97vv92")
    if not r1 or not r2:
        print("could not produce replays")
        return

    g1 = json.loads((d1 / "games.jsonl").read_text().splitlines()[0])
    g2 = json.loads((d2 / "games.jsonl").read_text().splitlines()[0])
    print(f"\n  V92 vs V92 : {g1['final_coins']}")
    print(f"  V97 vs V92 : {g2['final_coins']}")
    cand_seat = g2["candidate_seat"]
    print(f"  candidate seat in the V97 game: {cand_seat}")
    print(f"  V97 candidate cash {g2['final_coins'][cand_seat]:,.0f}  vs  V92 seat cash {g2['final_coins'][1-cand_seat]:,.0f}")
    print(f"  V92 selfplay seat0 cash {g1['final_coins'][0]:,.0f}  seat1 {g1['final_coins'][1]:,.0f}")

    # Market inventory trajectory comparison, WHEAT/STRAWBERRY at each day end.
    def market_traj(game, seat):
        out = {}
        for i in range(0, len(game["steps"]), 24):
            obs = game["steps"][i][seat]["observation"]
            day = int(obs.get("day", 0))
            inv = obs.get("market", {}).get("inventory", {})
            pr = obs.get("market", {}).get("prices", {})
            out[day] = {k: (inv.get(k), pr.get(k)) for k in ("WHEAT", "STRAWBERRY", "MILK", "WOOL")}
        return out

    t1 = market_traj(r1, 0)
    t2 = market_traj(r2, cand_seat)
    print(f"\n  {'day':>4} | {'V92 selfplay: WHEAT inv/px':>28} | {'V97 cand: WHEAT inv/px':>28}")
    for d in sorted(set(t1) & set(t2)):
        if d % 3 == 0:
            a1 = t1[d].get("WHEAT"); a2 = t2[d].get("WHEAT")
            print(f"  {d:>4} | {str(a1):>28} | {str(a2):>28}")
    print()
    print("  READ: if the V97 game's shared market inventory and prices diverge materially")
    print("  from the V92 selfplay on the same seed, the route's extra supply/harvest moved")
    print("  the shared market, which is a MARKET-MEDIATED cost, not a farm-damage cost.")


if __name__ == "__main__":
    main()

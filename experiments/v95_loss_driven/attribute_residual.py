#!/usr/bin/env python3
"""V95 step 6: explain the residual -361, and decide whether a third variant is worth it.

V95 v1 lost 0W-22L at mean -6,926. The diagnosed cause was that 97% of FERTILIZE
actions landed on tiles not already watered, so the engine's bonus (paid only inside a
WATER action, kaggriculture.py 442-443) never materialised while the displaced action was
still lost. Requiring watered_today cut the loss to mean -361, range -299..-399.

That is a 95% repair and it confirms the mechanism was right. The residual is small but
it is UNMISTAKABLY NEGATIVE: 0 of 22 games positive, and the spread is tight enough
(-299..-399) that this is signal, not noise.

The break-even table said applying beats selling for every crop except WHEAT
(P_WHEAT $40.83 < P_FERT $48.48). The v1 diagnosis showed the overlay fertilized
WHEAT 1,166 times versus STRAWBERRY 1,342. If those WHEAT applications are the residual
loss, restricting the overlay to the crops where applying actually wins should flip the
sign. This script measures the per-crop contribution of the v2 overlay directly: for
each crop, how many FERTILIZE actions it issued and what each one displaced.

This is the assignment's instruction: "If the first idea fails, use the diagnosed
failure to test another materially different lever; do not dress a no-op as progress."
The diagnosed failure is crop-blind fertilization, so v3 is crop-aware fertilization,
not a retune of v2's threshold.

Run from repo root:
    .venv/bin/python experiments/v95_loss_driven/attribute_residual.py
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs/dev_v95_vs_v92/replays"


def main():
    diag = json.loads((HERE / "overlay_diagnosis.json").read_text())
    # v2 replays overwrote v1 replays, so re-derive per-crop counts from the
    # current diagnosis artifact.
    fert_by_crop = Counter()
    fert_watered = Counter()
    for r in diag:
        for k, v in r["fert_events_by_crop"].items():
            fert_by_crop[k] += v
        for k, v in r["fert_by_watered"].items():
            crop, flag = k.split("|")
            fert_watered[(crop, flag)] += v

    prices = {"STRAWBERRY": 142.65, "MILK": 139.33, "WOOL": 69.32, "WHEAT": 40.83,
              "MELON": 218.73, "FERTILIZER": 48.48, "CARROT": 67.42}

    print("=" * 104)
    print("V95 v2 RESIDUAL ATTRIBUTION — which crops is the overlay fertilizing?")
    print("=" * 104)
    print(f"\n{'crop':>11} {'FERTILIZE':>10} {'on watered':>11} {'P_crop':>8} {'P_fert':>8} "
          f"{'net/unit':>9} {'est. net':>10}")
    total_est = 0
    for crop in sorted(fert_by_crop, key=lambda c: -fert_by_crop[c]):
        n = fert_by_crop[crop]
        w = fert_watered.get((crop, "watered=True"), 0)
        pc = prices.get(crop, 0.0)
        net = pc - prices["FERTILIZER"]
        est = net * w
        total_est += est
        print(f"{crop:>11} {n:>10} {w:>11} {pc:>8.2f} {prices['FERTILIZER']:>8.2f} "
              f"{net:>+9.2f} {est:>+10,.0f}")

    print()
    print(f"  gross estimated effect of the applications that landed on a watered tile: "
          f"{total_est:+,.0f} over {sum(fert_watered.values())} applications")
    print(f"  measured paired margin: -361 mean per game x 22 games = {-361*22:,.0f}")
    print()
    losers = [c for c in fert_by_crop if prices.get(c, 0) < prices["FERTILIZER"]]
    print(f"  crops where APPLYING loses to SELLING: {losers}")
    for c in losers:
        w = fert_watered.get((c, "watered=True"), 0)
        n = fert_by_crop[c]
        cost = (prices["FERTILIZER"] - prices[c]) * w
        print(f"    {c}: {n} FERTILIZE actions ({w} on watered tiles) costing about {cost:+,.0f}")
    print()
    print("  If WHEAT dominates the loss, v3 = restrict fertilization to crops whose")
    print("  realized unit price exceeds the realized fertilizer price. That is a")
    print("  materially different rule, not a threshold retune: it removes a whole")
    print("  class of provably value-destroying actions identified by measured price.")


if __name__ == "__main__":
    main()

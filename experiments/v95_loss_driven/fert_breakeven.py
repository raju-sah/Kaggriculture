#!/usr/bin/env python3
"""V95 step 3b: is the fertilizer margin actually wrong? A break-even test.

Step 3 nearly produced a false positive and caught it. The naive reading was "V92
collects 5,222 fertilizer and applies only 1,400, so 3,822 units of yield are being
thrown away". That is wrong. V92 SELLS 4,438 of them for $215,146, which is 11.7% of
all sale cash. The collected fertilizer is not idle, it is monetized. Only 35 units
are discarded unused.

So the real question is a MARGIN question, and it has a clean break-even answer:

    V92 currently sells a collected FERTILIZER unit for price P_fert.
    If instead it APPLIED that unit to an in-window crop tile, engine 442-443 gives
    the tile +2 yield instead of +1, i.e. ONE EXTRA UNIT of that crop, which then
    sells for P_crop.

    Applying is better than selling only when  P_crop > P_fert.

Both prices must be MEASURED, not peak. The V93 and V94 candidates both died pricing
extra units at peak quotes; this measures the realized average price the farm
actually received for each product across the 14 verified games.

It also has to be checked against inventory reality: applying fertilizer requires
COLLECT_FERTILIZER and FERTILIZE to happen on the same actor walk to a plant tile,
so the realizable fraction is bounded by reach. And the shed is already saturated at
102/100, so converting a shed FERTILIZER into a crop unit changes WHEN the shed
frees up, which is the mechanism that killed the hold family. That interaction is
exactly what has to be measured rather than assumed.

Run from repo root:
    .venv/bin/python experiments/v95_loss_driven/fert_breakeven.py
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
V94_OUT = ROOT / "experiments/v94_sell_rate/probe_out"


def main():
    print("=" * 100)
    print("V95 STEP 3b: FERTILIZER BREAK-EVEN — sell the unit, or apply it to a tile?")
    print("=" * 100)

    # Realized per-unit sale prices, from the V94 engine-measured ledger.
    rec = json.loads((V94_OUT / "cash_reconciliation.json").read_text())
    sell_cash = Counter()
    for r in rec:
        for k, v in r["sell_cash_by_product"].items():
            sell_cash[k] += v

    # Per-unit realized price = cash / units, and units come from the V94
    # realization ledger (accepted units, never order slots).
    led = json.loads((ROOT / "experiments/v93_adaptive/realization_ledger.json").read_text())
    units = Counter()
    for r in led:
        for item, u in (r["ledger"][item]["sold_units"] for item in []):
            pass
    # realization_ledger stores sold_units per product inside ledger[item]
    for r in led:
        for item, row in r["ledger"].items():
            units[item] += int(row.get("sold_units", 0) or 0)

    print(f"\n{'product':>11} {'units sold':>11} {'cash':>12} {'realized $/unit':>16}")
    price = {}
    for item in sorted(sell_cash, key=lambda k: -sell_cash[k]):
        u = units.get(item, 0)
        p = sell_cash[item] / u if u else 0.0
        price[item] = p
        print(f"{item:>11} {u:>11,} {sell_cash[item]:>12,.0f} {p:>16.2f}")

    pf = price.get("FERTILIZER", 0.0)
    print()
    print("  Break-even rule: APPLY a collected fertilizer unit to an in-window tile")
    print("  instead of SELLING it, only when  P_crop > P_fert  (it buys +1 extra yield unit).")
    print(f"  P_fert (realized) = ${pf:.2f}")
    print()
    print(f"  {'crop':>11} {'P_crop':>9} {'beats fert?':>12} {'margin/unit':>12}")
    for item in ("STRAWBERRY", "MILK", "WOOL", "MELON", "CARROT", "WHEAT"):
        pc = price.get(item, 0.0)
        if pc <= 0:
            continue
        wins = pc > pf
        print(f"  {item:>11} {pc:>9.2f} {'YES' if wins else 'no':>12} {pc - pf:>+12.2f}")

    print()
    print("  Read this carefully before proposing anything:")
    print("   - FERTILIZER is bought at market (engine 598) but also collected FREE")
    print("     from animals (engine 515-522). The collected ones are the ones in question.")
    print("   - If P_crop < P_fert, V92 is already making the CORRECT choice by selling,")
    print("     and there is no lever here at all.")
    print("   - If P_crop > P_fert, there is a real margin, but it is capped by worker")
    print("     reach and by shed saturation (measured at 102/100), which is the exact")
    print("     mechanism that made the hold-family overlays lose.")


if __name__ == "__main__":
    main()

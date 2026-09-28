#!/usr/bin/env python3
"""V95 step 0: recompute every V94 aggregate from the verified raw evidence.

The V94 report quoted sale cash of $3,448,243 and total spend of $338,688. Those
numbers came from probe_out/cash_flow.json, which summed the market hooks across
BOTH seats. The correct denominator for the Rajusah cash identity is
probe_out/cash_reconciliation.json, which holds the 14 Rajusah rows and reconciles
to $0.00 unexplained on every one.

  cash_reconciliation.json : 14 rows, sell 1,832,002  spend 415,898  |unexplained| = 0.00
  cash_flow.json           : sums both seats       sell 3,448,243  spend 672,162

This script recomputes every number the V94 report states, from the Rajusah rows
only, so the correction is verifiable rather than asserted. It does not modify
the raw evidence files; it only reads them and writes a correction artifact.

Run from repo root:
    .venv/bin/python experiments/v95_loss_driven/recompute_v94_aggregates.py
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V94 = ROOT / "experiments/v94_sell_rate/probe_out"
HERE = Path(__file__).resolve().parent


def main() -> None:
    rec = json.loads((V94 / "cash_reconciliation.json").read_text())
    assert len(rec) == 14, f"expected 14 Rajusah rows, got {len(rec)}"

    sell = sum(r["sell_cash_total"] for r in rec)
    spend = sum(r["spend_total"] for r in rec)
    spend_excl_hire = sum(r["spend_excl_hire"] for r in rec)
    hire = sum(r["hire_cash"] for r in rec)
    hire_orders = sum(r["hire_orders"] for r in rec)
    predicted = sum(r["predicted_final"] for r in rec)
    reward = sum(r["reward"] for r in rec)
    worst = max(abs(r["unexplained"]) for r in rec)
    mism = sum(r["cash_mismatches"] for r in rec)

    sell_by = Counter()
    spend_by = Counter()
    for r in rec:
        for k, v in r["sell_cash_by_product"].items():
            sell_by[k] += v
        for k, v in r["spend_by_category"].items():
            spend_by[k] += v

    out = {
        "source": "experiments/v94_sell_rate/probe_out/cash_reconciliation.json",
        "rows": len(rec),
        "identity_holds": worst == 0.0,
        "max_abs_unexplained": worst,
        "total_cash_mismatches": mism,
        "sell_cash_total": sell,
        "spend_total": spend,
        "spend_excl_hire": spend_excl_hire,
        "hire_cash": hire,
        "hire_orders": hire_orders,
        "hire_per_game": round(hire / 14, 2),
        "hire_avg_per_order": round(hire / hire_orders, 2),
        "predicted_final_total": predicted,
        "reward_total": reward,
        "sell_cash_by_product": {k: round(v, 2) for k, v in sell_by.most_common()},
        "sell_cash_share": {k: round(100 * v / sell, 2) for k, v in sell_by.most_common()},
        "spend_by_category": {k: round(v, 2) for k, v in spend_by.most_common()},
        "spend_share": {k: round(100 * v / spend, 2) for k, v in spend_by.most_common()},
        "corrections_vs_v94_report": {
            "sell_cash_total": {"v94_report": 3448243, "correct": sell},
            "spend_total": {"v94_report": 338688, "correct": spend},
            "note": (
                "V94 quoted the BOTH-SEAT sum from cash_flow.json. The Rajusah cash "
                "identity denominator is cash_reconciliation.json, which is one row per "
                "episode. The $0.00 reconciliation result itself still holds on all 14."
            ),
        },
    }
    HERE.mkdir(parents=True, exist_ok=True)
    (HERE / "v94_aggregate_correction.json").write_text(json.dumps(out, indent=2) + "\n")

    print("=" * 92)
    print("V94 AGGREGATE RECOMPUTATION (Rajusah rows only, 14 official replays)")
    print("=" * 92)
    print(f"  sell_cash_total        {sell:>14,.0f}     (V94 report said 3,448,243 = both-seat sum)")
    print(f"  spend_total            {spend:>14,.0f}     (V94 report said 338,688)")
    print(f"  spend_excl_hire        {spend_excl_hire:>14,.0f}")
    print(f"  hire_cash              {hire:>14,.0f}     ({hire_orders} orders, {hire/14:,.0f}/game, {hire/hire_orders:.2f}/order)")
    print(f"  predicted_final_total  {predicted:>14,.0f}")
    print(f"  reward_total           {reward:>14,.0f}")
    print(f"  max |unexplained|      {worst:>14.2f}     identity holds: {out['identity_holds']}")
    print(f"  total cash mismatches  {mism:>14}")
    print()
    print("  SALE CASH by product (share of 1,832,002):")
    for k, v in sell_by.most_common():
        print(f"    {k:>11} {v:>12,.0f}  {100*v/sell:>5.1f}%")
    print()
    print("  SPEND by category (share of 415,898):")
    for k, v in spend_by.most_common():
        print(f"    {k:>22} {v:>10,.0f}  {100*v/spend:>5.1f}%")
    print(f"\n  wrote {HERE / 'v94_aggregate_correction.json'}")


if __name__ == "__main__":
    main()

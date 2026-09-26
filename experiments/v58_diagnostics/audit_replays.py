"""Summarize sale prices and market-order slot use in captured v57-loss replays."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPLAYS = ROOT / "experiments/v58_diagnostics/replays"
OUTPUT = ROOT / "experiments/v58_diagnostics/replay_audit.json"
CAP = 10  # kaggriculture maxMarketOrdersPerTurn in the standard config
FOCUS = {"MILK", "WOOL", "STRAWBERRY"}


def main() -> None:
    audits = []
    for path in sorted(REPLAYS.glob("*.json")):
        replay = json.loads(path.read_text())
        lengths = Counter()
        saturated = []
        low_sales = []
        first_low = {}
        for index, players in enumerate(replay["steps"]):
            frame = players[0]  # captured matches put the candidate in seat 0
            action = frame.get("action") or {}
            orders = action.get("market") or []
            lengths[len(orders)] += 1
            observation = frame.get("observation") or {}
            prices = (observation.get("market") or {}).get("prices") or {}
            if len(orders) == CAP:
                saturated.append({
                    "step": index,
                    "orders": Counter(o[0] for o in orders if o),
                    "focus_sales": [
                        {"item": o[1], "units": o[2], "observed_price": prices.get(o[1])}
                        for o in orders if o and o[0] == "SELL" and o[1] in FOCUS
                    ],
                })
            for order in orders:
                if not order or order[0] != "SELL" or order[1] not in FOCUS:
                    continue
                item, units = order[1], order[2]
                price = prices.get(item)
                if price is not None and price <= 5:
                    first_low.setdefault(item, index)
                    low_sales.append({
                        "step": index, "item": item, "units": units,
                        "observed_price": price, "order_count": len(orders),
                    })

        low_unconstrained = [r for r in low_sales if r["order_count"] < CAP]
        audits.append({
            "replay": path.name,
            "candidate_seat": 0,
            "turns": sum(lengths.values()),
            "order_count_histogram": dict(sorted(lengths.items())),
            "saturated_turn_count": len(saturated),
            "saturated_turns": saturated,
            "first_sale_at_observed_price_le_5": first_low,
            "focus_low_price_sale_order_count": len(low_sales),
            "focus_low_price_sales_with_spare_slots": len(low_unconstrained),
            "focus_low_price_sales": low_sales,
        })
    OUTPUT.write_text(json.dumps(audits, indent=2, default=dict) + "\n")
    print(f"wrote {OUTPUT.relative_to(ROOT)} ({len(audits)} replays)")


if __name__ == "__main__":
    main()

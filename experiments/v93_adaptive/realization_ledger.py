#!/usr/bin/env python3
"""V93 step 1d: production-vs-realization audit of the 14 official V92 replays.

Read-only. Reads experiments/kaggle/v92_official/episode-*-replay.json only.
No V88 artifact is read; the V88 replay joins were invalidated on provenance
grounds (docs/V88_REPLAY_PROVENANCE_CORRECTION_2026-09-27.md) and are not reused.

Why this exists
---------------
reward = final money (engine line 961). Shed contents, tiles, herds and seeds
are all worth exactly $0 at the end. So every unit that is produced but never
converted to cash is a unit of work thrown away, and every unit converted at a
price below its own peak quote is cash left on the table.

This replays each episode through the pinned engine (obs at steps[t], action at
steps[t+1], same alignment as experiments/v92_official/analyze_replays.py) and
requires zero cash mismatches on both ledgers before any number is believed.
On top of that it hooks the engine's own inventory and settlement primitives to
build a per-product ledger:

    harvested -> shed/carried -> SOLD at price p  => realised cash
                                     DISCARDED at the end-of-day drop => $0
                                     consumed by FEED / FERTILIZE  => $0
                                     still in shed at step 718     => $0

and records the quote trajectory so "sold cheap" can be separated from
"only ever cheap".
"""

from __future__ import annotations

import copy
import glob
import json
from collections import Counter, defaultdict
from pathlib import Path
from types import SimpleNamespace

from kaggle_environments.envs.kaggriculture import kaggriculture as engine

ROOT = Path(__file__).resolve().parents[2]
REPLAY_DIR = ROOT / "experiments/kaggle/v92_official"
HERE = Path(__file__).resolve().parent
TURNS_PER_DAY = 24
SHED_CAPACITY = 100
PRODUCTS = engine.PRODUCTS


def replay(path: Path) -> dict:
    game = json.loads(path.read_text())
    names = [a["Name"] for a in game["info"].get("Agents", [])]
    seat = names.index("Rajusah")
    rewards = game["rewards"]
    configuration = game.get("configuration", {})
    cfg = SimpleNamespace(
        **{
            key: configuration.get(key, default)
            for key, default in {
                "boardSize": 10, "maxMarketOrdersPerTurn": 10, "farmHandCostMult": 1,
                "shedCapacity": SHED_CAPACITY, "turnsPerDay": TURNS_PER_DAY,
            }.items()
        }
    )

    # Per-seat ledgers, indexed by the same 0/1 order the engine uses.
    sold_units: list[Counter[str]] = [Counter(), Counter()]
    sold_cash: list[Counter[str]] = [Counter(), Counter()]
    sold_prices: list[dict[str, list[float]]] = [defaultdict(list), defaultdict(list)]
    harvested: list[Counter[str]] = [Counter(), Counter()]
    bought: list[Counter[str]] = [Counter(), Counter()]
    spent_cash: list[float] = [0.0, 0.0]
    fed_wheat: list[int] = [0, 0]
    fert_used: list[int] = [0, 0]
    discarded: list[Counter[str]] = [Counter(), Counter()]
    quote_hi: list[dict[str, int]] = [defaultdict(int), defaultdict(int)]
    quote_lo: list[dict[str, int]] = [defaultdict(int), defaultdict(int)]
    daily_sold_units: list[dict[int, Counter[str]]] = [defaultdict(Counter), defaultdict(Counter)]
    daily_sold_cash: list[dict[int, float]] = [defaultdict(float), defaultdict(float)]
    final_shed: list[dict] = [{}, {}]
    final_carried: list[Counter[str]] = [Counter(), Counter()]
    cash_mismatches = [0, 0]

    orig_inv_add = engine._inv_add
    orig_inv_take = engine._inv_take
    orig_commit = engine._commit_unit
    orig_drop = engine._drop_inventories_to_shed
    ctx: dict = {"seat": 0, "day": 0, "market": None, "op": None, "private_to_seat": {}}

    def tracking_inv_add(inv, item, n):
        result = orig_inv_add(inv, item, n)
        # Only a HARVEST creates product. PICKUP merely moves shed stock into a
        # hand, and DROP/PLACE move it back, so counting those as production
        # would triple-count the same units.
        if ctx.get("op") == "HARVEST":
            harvested[ctx["seat"]][item] += int(n)
        return result

    def tracking_inv_take(inv, item, n):
        # Only record a real consumption when the take succeeds.
        if int(inv.get(item, 0) or 0) >= n:
            s = ctx["seat"]
            if item == "WHEAT":
                fed_wheat[s] += int(n)
            if item == "FERTILIZER":
                fert_used[s] += int(n)
        return orig_inv_take(inv, item, n)

    def tracking_commit(op, item, price, farm, private, market, shed_capacity=SHED_CAPACITY):
        ok = orig_commit(op, item, price, farm, private, market, shed_capacity)
        if ok:
            # Attribute by the identity of the private dict being settled, not by
            # a mutable context seat: _process_market drives both players inside
            # one lockstep loop, so a context seat cannot distinguish them.
            s = ctx["private_to_seat"].get(id(private))
            if s is None:
                return ok
            if op == "SELL":
                sold_units[s][item] += 1
                sold_cash[s][item] += float(price)
                sold_prices[s][item].append(float(price))
                daily_sold_units[s][ctx["day"]][item] += 1
                daily_sold_cash[s][ctx["day"]] += float(price)
            elif op == "BUY_PRODUCT":
                bought[s][item] += 1
                spent_cash[s] += float(price)
        return ok

    def tracking_drop(private, capacity):
        shed = private["shed"]
        for inv in private["inventories"]:
            for item, n in list(inv.items()):
                if n <= 0:
                    del inv[item]
                    continue
                current = sum(shed.values())
                take = min(n, max(0, capacity - current))
                if take > 0:
                    shed[item] = shed.get(item, 0) + take
                if n - take > 0:
                    discarded[ctx["seat"]][item] += int(n - take)
                del inv[item]

    engine._inv_add = tracking_inv_add
    engine._inv_take = tracking_inv_take
    engine._commit_unit = tracking_commit
    engine._drop_inventories_to_shed = tracking_drop
    try:
        for frame in range(1, len(game["steps"])):
            previous, current = game["steps"][frame - 1], game["steps"][frame]
            prev_obs = previous[0]["observation"]
            day = int(prev_obs.get("day", 0))
            step = int(prev_obs.get("step", day * TURNS_PER_DAY))
            farms = copy.deepcopy(prev_obs["farms"])
            private = [copy.deepcopy(previous[s]["observation"]["private"]) for s in range(2)]
            market = copy.deepcopy(prev_obs["market"])
            ctx["market"] = market
            ctx["day"] = day
            ctx["private_to_seat"] = {id(private[0]): 0, id(private[1]): 1}
            for s in range(2):
                for item, price in (market.get("prices", {}) or {}).items():
                    p = int(price)
                    if p > quote_hi[s][item]:
                        quote_hi[s][item] = p
                    if p < quote_lo[s][item] or quote_lo[s][item] == 0:
                        quote_lo[s][item] = p
            actions = [copy.deepcopy(current[s].get("action") or {}) for s in range(2)]

            for s in range(2):
                units = [actions[s].get("farmer", ["PASS"]), *(actions[s].get("hands") or [])]
                for unit_index, action in enumerate(units):
                    ctx["seat"] = s
                    ctx["op"] = action[0] if isinstance(action, list) and action else None
                    engine._apply_unit_action(
                        farms[s], private[s], unit_index, action,
                        int(cfg.boardSize), day, TURNS_PER_DAY, int(cfg.shedCapacity),
                    )
            ctx["op"] = None
            states = [
                SimpleNamespace(observation=SimpleNamespace(market=market, farms=farms, private=private[s]), action=actions[s])
                for s in range(2)
            ]
            engine._process_market(states, SimpleNamespace(configuration=cfg))

            for s in range(2):
                observed = float(current[s]["observation"]["farms"][s]["money"])
                if abs(float(farms[s]["money"]) - observed) > 0.011:
                    cash_mismatches[s] += 1

            if (step + 1) % TURNS_PER_DAY == 0:
                # _end_of_day drops seat 0's inventories first, then seat 1's,
                # exactly as the engine does, so the discard attribution is right.
                engine._drop_inventories_to_shed(private[0], int(cfg.shedCapacity))
                engine._drop_inventories_to_shed(private[1], int(cfg.shedCapacity))
    finally:
        engine._inv_add = orig_inv_add
        engine._inv_take = orig_inv_take
        engine._commit_unit = orig_commit
        engine._drop_inventories_to_shed = orig_drop

    # Final inventory state, read straight from the last recorded observation.
    last_private = game["steps"][-1][seat]["observation"].get("private") or {}
    final_shed[seat] = {k: int(v) for k, v in (last_private.get("shed") or {}).items() if v}
    for inv in last_private.get("inventories") or []:
        for item, n in (inv or {}).items():
            if n:
                final_carried[seat][item] += int(n)

    ledger = {}
    for item in PRODUCTS:
        units_sold = sold_units[seat][item]
        cash = sold_cash[seat][item]
        prices = sold_prices[seat][item]
        prod = harvested[seat][item] + bought[seat][item]
        ledger[item] = {
            "harvested": harvested[seat][item],
            "bought": bought[seat][item],
            "sold_units": units_sold,
            "sold_cash": round(cash, 2),
            "avg_price": round(cash / units_sold, 2) if units_sold else None,
            "quote_high": quote_hi[seat][item],
            "quote_low": quote_lo[seat][item],
            "fed_or_fertilized": fed_wheat[seat] if item == "WHEAT" else (fert_used[seat] if item == "FERTILIZER" else 0),
            "discarded": discarded[seat][item],
            "in_shed_at_end": final_shed[seat].get(item, 0),
            "carried_at_end": final_carried[seat].get(item, 0),
        }

    return {
        "file": path.name,
        "episode_id": game.get("info", {}).get("EpisodeId"),
        "opponent": names[1 - seat],
        "outcome": "W" if rewards[seat] > rewards[1 - seat] else "L",
        "margin": round(float(rewards[seat]) - float(rewards[1 - seat])),
        "rajusah_score": rewards[seat],
        "cash_mismatches": sum(cash_mismatches),
        "ledger": ledger,
        "total_sold_cash": round(sum(sold_cash[seat].values()), 2),
        "buy_product_cash_spent": round(spent_cash[seat], 2),
        "daily_sold_cash": {str(d): round(v, 2) for d, v in sorted(daily_sold_cash[seat].items())},
        "daily_sold_units": {str(d): dict(c) for d, c in sorted(daily_sold_units[seat].items())},
    }


def main() -> None:
    paths = [Path(p) for p in sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))]
    results = []
    for p in paths:
        results.append(replay(p))
        print(f"  replayed {p.name}", flush=True)
    out = HERE / "realization_ledger.json"
    out.write_text(json.dumps(results, indent=2) + "\n")
    print(f"\nwrote {out}\n")
    print(f"{'epid':>10} {'out':>3} {'margin':>8} {'mism':>5} {'soldCash':>10} {'buyCash':>9}")
    for r in results:
        print(
            f"{r['episode_id']:>10} {r['outcome']:>3} {r['margin']:>+8} {r['cash_mismatches']:>5} "
            f"{r['total_sold_cash']:>10.0f} {r['buy_product_cash_spent']:>9.0f}"
        )

    print("\n--- per-product ledger, first loss (114166061) ---")
    loss = next(r for r in results if r["episode_id"] == 114166061)
    hdr = f"{'item':>11} {'harv':>5} {'bought':>6} {'sold':>5} {'cash':>9} {'avgP':>7} {'qHi':>5} {'qLo':>5} {'discard':>7} {'shedEnd':>7}"
    print(hdr)
    for item, row in loss["ledger"].items():
        if not any(row[k] for k in ("harvested", "bought", "sold_units", "discarded", "in_shed_at_end")):
            continue
        print(
            f"{item:>11} {row['harvested']:>5} {row['bought']:>6} {row['sold_units']:>5} {row['sold_cash']:>9.0f} "
            f"{(row['avg_price'] or 0):>7.1f} {row['quote_high']:>5} {row['quote_low']:>5} {row['discarded']:>7} {row['in_shed_at_end']:>7}"
        )


if __name__ == "__main__":
    main()

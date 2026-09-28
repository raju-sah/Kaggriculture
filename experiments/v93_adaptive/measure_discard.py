#!/usr/bin/env python3
"""V93 step 1c: measure the EXACT end-of-day discard in all 14 official replays.

Read-only. Reads experiments/kaggle/v92_official/episode-*-replay.json only.
No V88 artifact is read; the V88 replay joins were invalidated on provenance
grounds (docs/V88_REPLAY_PROVENANCE_CORRECTION_2026-09-27.md) and are not reused.

Method
------
Replays each recorded transition through the pinned installed engine exactly as
experiments/v92_official/analyze_replays.py does (observation at steps[t] pairs
with the action at steps[t+1]), and requires ZERO cash mismatches on both
ledgers before any number here is believed. On top of that replay it wraps
engine._drop_inventories_to_shed so that the exact units destroyed at every
end-of-day boundary are captured, together with the market quote for each one.

This is the measurement that decides whether V92's single-boundary guard
(day 23 hour 23) leaves other boundaries unhandled, and what those unhandled
units are actually worth. reward = money (engine line 961), so a discarded unit
is worth exactly $0 and a retained unit is worth its eventual sale price.
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


def _quote(item: str, inventory: int, params: dict | None) -> int:
    return engine.market_price(item, inventory, params)


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
                "boardSize": 10,
                "maxMarketOrdersPerTurn": 10,
                "farmHandCostMult": 1,
                "shedCapacity": SHED_CAPACITY,
                "turnsPerDay": TURNS_PER_DAY,
            }.items()
        }
    )

    discards: list[dict] = []
    cash_mismatches = [0, 0]
    accepted_sales: Counter[str] = Counter()
    accepted_cash: Counter[str] = Counter()

    original_drop = engine._drop_inventories_to_shed
    original_commit = engine._commit_unit
    state_holder: dict = {}

    def record_drop(private, capacity):
        shed = private["shed"]
        for inv in private["inventories"]:
            for item, n in list(inv.items()):
                if n <= 0:
                    del inv[item]
                    continue
                current = sum(shed.values())
                room = max(0, capacity - current)
                take = min(n, room)
                if take > 0:
                    shed[item] = shed.get(item, 0) + take
                lost = n - take
                if lost > 0:
                    market = state_holder.get("market") or {}
                    params = market.get("params")
                    inv_level = int((market.get("inventory") or {}).get(item, engine.MARKET_I0))
                    price = _quote(item, inv_level, params)
                    discards.append(
                        {
                            "step": state_holder.get("step", -1),
                            "day": (state_holder.get("step", 0)) // TURNS_PER_DAY,
                            "item": item,
                            "lost_units": int(lost),
                            "quote": int(price),
                            "quote_value": int(lost) * int(price),
                            "shed_after": int(sum(shed.values())),
                        }
                    )
                del inv[item]

    def record_commit(op, item, price, farm, private, market, shed_capacity=SHED_CAPACITY):
        ok = original_commit(op, item, price, farm, private, market, shed_capacity)
        if ok and op == "SELL" and state_holder.get("seat") is not None:
            who = state_holder["seat"]
            if who == 0:
                accepted_sales[item] += 1
                accepted_cash[item] += float(price)
        return ok

    engine._drop_inventories_to_shed = record_drop
    engine._commit_unit = record_commit
    try:
        for frame in range(1, len(game["steps"])):
            previous, current = game["steps"][frame - 1], game["steps"][frame]
            prev_obs = previous[0]["observation"]
            day = int(prev_obs.get("day", 0))
            step = int(prev_obs.get("step", day * TURNS_PER_DAY))
            farms = copy.deepcopy(prev_obs["farms"])
            private = [copy.deepcopy(previous[s]["observation"]["private"]) for s in range(2)]
            market = copy.deepcopy(prev_obs["market"])
            state_holder["market"] = market
            state_holder["step"] = step
            actions = [copy.deepcopy(current[s].get("action") or {}) for s in range(2)]

            state_holder["seat"] = None
            for who in range(2):
                units = [actions[who].get("farmer", ["PASS"]), *(actions[who].get("hands") or [])]
                for unit_index, action in enumerate(units):
                    state_holder["seat"] = 0 if who == seat else 1
                    engine._apply_unit_action(
                        farms[who], private[who], unit_index, action,
                        int(cfg.boardSize), day, TURNS_PER_DAY, int(cfg.shedCapacity),
                    )

            states = [
                SimpleNamespace(
                    observation=SimpleNamespace(market=market, farms=farms, private=private[s]),
                    action=actions[s],
                )
                for s in range(2)
            ]
            # Market: the recorded actions are applied in player order, and the
            # commit hook attributes to seat 0 = Rajusah.
            for _ in range(1):
                state_holder["seat"] = 0 if seat == 0 else 1
                engine._process_market(states, SimpleNamespace(configuration=cfg))

            for who in range(2):
                observed = float(current[who]["observation"]["farms"][who]["money"])
                if abs(float(farms[who]["money"]) - observed) > 0.011:
                    cash_mismatches[who] += 1

            # The recorded observation already contains the end-of-day effect,
            # so the drop is replayed only to MEASURE it, not to advance state.
            if (step + 1) % TURNS_PER_DAY == 0:
                state_holder["seat"] = 0 if seat == 0 else 1
                engine._drop_inventories_to_shed(private[seat], int(cfg.shedCapacity))
    finally:
        engine._drop_inventories_to_shed = original_drop
        engine._commit_unit = original_commit

    by_day: dict[str, dict] = defaultdict(lambda: {"lost_units": 0, "quote_value": 0.0, "items": Counter()})
    for d in discards:
        bucket = by_day[str(d["day"])]
        bucket["lost_units"] += d["lost_units"]
        bucket["quote_value"] += d["quote_value"]
        bucket["items"][d["item"]] += d["lost_units"]

    total_lost = sum(d["lost_units"] for d in discards)
    total_value = sum(d["quote_value"] for d in discards)
    return {
        "file": path.name,
        "episode_id": game.get("info", {}).get("EpisodeId"),
        "opponent": names[1 - seat],
        "outcome": "W" if rewards[seat] > rewards[1 - seat] else "L",
        "margin": round(float(rewards[seat]) - float(rewards[1 - seat])),
        "cash_mismatches_rajusah": cash_mismatches[0],
        "cash_mismatches_total": sum(cash_mismatches),
        "total_lost_units": total_lost,
        "total_quote_value": round(total_value, 2),
        "discard_by_day": {
            day: {
                "lost_units": b["lost_units"],
                "quote_value": round(b["quote_value"], 2),
                "items": dict(b["items"]),
            }
            for day, b in sorted(by_day.items(), key=lambda kv: int(kv[0]))
        },
        "discard_detail": discards,
        "accepted_sale_units_by_item": dict(sorted(accepted_sales.items())),
        "accepted_sale_cash_by_item": {k: round(v, 2) for k, v in sorted(accepted_cash.items())},
        "accepted_sale_cash_total": round(sum(accepted_cash.values()), 2),
    }


def main() -> None:
    paths = [Path(p) for p in sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))]
    results = []
    for p in paths:
        results.append(replay(p))
        print(f"  replayed {p.name}", flush=True)
    out = HERE / "discard_measurement.json"
    out.write_text(json.dumps(results, indent=2) + "\n")

    print(f"\nwrote {out}\n")
    print(f"{'epid':>10} {'out':>3} {'margin':>8} {'mismatch':>8} {'lostUnits':>9} {'quoteValue':>10} {'W':>3} {'L':>3} {'margin/val':>10}")
    for r in results:
        loss = r["outcome"] == "L"
        print(
            f"{r['episode_id']:>10} {r['outcome']:>3} {r['margin']:>+8} {r['cash_mismatches_total']:>8} "
            f"{r['total_lost_units']:>9} {r['total_quote_value']:>10.0f} "
            f"{r['margin'] if not loss else 0:>+3} {r['margin'] if loss else 0:>+3} "
            f"{r['margin'] / max(1.0, r['total_quote_value']):>10.2f}"
        )

    print("\n--- discard by day (episode 114166061, a loss) ---")
    sample = next(r for r in results if r["episode_id"] == 114166061)
    for day, b in sample["discard_by_day"].items():
        print(f"  day {day:>2}: {b['lost_units']:>3} units  ${b['quote_value']:>8.0f}  {b['items']}")

    print("\n--- is the discard pattern identical across episodes? ---")
    patterns = {json.dumps(r["discard_by_day"], sort_keys=True) for r in results}
    print(f"  distinct discard_by_day patterns across 14 episodes: {len(patterns)}")


if __name__ == "__main__":
    main()

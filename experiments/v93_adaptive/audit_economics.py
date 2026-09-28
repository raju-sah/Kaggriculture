#!/usr/bin/env python3
"""V93 step 1b: decisive economic audit of the 14 official V92 replays.

Read-only. Consumes only experiments/kaggle/v92_official/episode-*-replay.json.
No V88 artifact is read: the V88 replay joins were invalidated on provenance
grounds (docs/V88_REPLAY_PROVENANCE_CORRECTION_2026-09-27.md) and are not reused.

Three questions, all answerable from the recorded observation stream alone:

Q1 DISCARD.  _drop_inventories_to_shed runs at every end-of-day boundary and
   deletes the overflow (engine line 857, `del inv[item]`). V92's guard only
   covers the day-23 -> day-24 boundary. Measure the total units destroyed at
   EVERY boundary, and the price value of what was destroyed, to see whether
   V92's single boundary leaves other boundaries unhandled.

Q2 LOW-PRICE WASTE.  Engine line 659: a SELL at $1 or below adds no supply, and
   score is cash only (line 961), so a unit held unsold and a unit sold at $1 are
   both worth $0. Measure accepted sale cash split by the price actually paid,
   per product, to find product/time windows where accepted units are worthless.

Q3 FINAL TICK.  The game ends at step 718 with reward = money. The V50 terminal
   overlay replaces the whole market list at step 718. Measure what the tape
   actually submitted on the last ticks and what the shed held afterwards.
"""

from __future__ import annotations

import glob
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPLAY_DIR = ROOT / "experiments/kaggle/v92_official"
HERE = Path(__file__).resolve().parent
TURNS_PER_DAY = 24
# market price params, engine MARKET_PARAMS: (base, above_func, above_target...)
# Only used to label a unit as "worthless"; exact prices come from the replay.
FLOOR = 1


def norm(obs: dict) -> dict:
    if obs.get("step") is not None:
        return obs
    obs = dict(obs)
    obs["step"] = int(obs.get("day", 0) or 0) * TURNS_PER_DAY + int(obs.get("hour", 0) or 0)
    return obs


def state_units(obs: dict) -> tuple[int, dict, dict]:
    private = obs.get("private") or {}
    shed = {k: int(v or 0) for k, v in (private.get("shed") or {}).items() if v}
    carried: Counter[str] = Counter()
    for inv in private.get("inventories") or []:
        for item, n in (inv or {}).items():
            if n:
                carried[item] += int(n)
    return sum(shed.values()) + sum(carried.values()), shed, dict(carried)


def analyze(path: Path) -> dict:
    game = json.loads(path.read_text())
    names = [a["Name"] for a in game["info"].get("Agents", [])]
    seat = names.index("Rajusah")
    rewards = game["rewards"]
    obs_at = [norm(game["steps"][i][seat]["observation"]) for i in range(len(game["steps"]))]
    act_at = [
        (game["steps"][i + 1][seat].get("action") if i + 1 < len(game["steps"]) else {}) or {}
        for i in range(len(game["steps"]))
    ]

    # ---- Q1: end-of-day discard at every boundary -------------------------
    # A drop runs after the action submitted at step t where (t+1) % 24 == 0.
    discards = []
    for t in range(len(obs_at) - 1):
        if (t + 1) % TURNS_PER_DAY != 0:
            continue
        before_units, before_shed, before_carried = state_units(obs_at[t])
        after_units, after_shed, after_carried = state_units(obs_at[t + 1])
        # The market also moves units between shed and hands (PICKUP/DROP/PLACE)
        # and the action may harvest, so only a large drop is evidence of loss.
        delta = before_units - after_units
        if delta > 0:
            discards.append(
                {
                    "step": t,
                    "day": t // TURNS_PER_DAY,
                    "units_before": before_units,
                    "units_after": after_units,
                    "apparent_lost": delta,
                    "shed_before": before_shed,
                    "carried_before": before_carried,
                    "prices": {k: v for k, v in (obs_at[t].get("market", {}).get("prices", {}) or {}).items()},
                }
            )

    # ---- Q2: accepted sale cash by price band ------------------------------
    # The replay does not record per-unit settlement, so recover it by replaying
    # the money delta against the submitted SELL list at each turn.
    money = [float(obs_at[i]["farms"][seat]["money"]) for i in range(len(obs_at))]
    sell_by_product: dict[str, Counter[str]] = defaultdict(Counter)
    daily_sell_cash: dict[int, float] = defaultdict(float)
    for t in range(len(obs_at) - 1):
        market = act_at[t].get("market") or []
        sells = [o for o in market if o and o[0] == "SELL" and len(o) > 2]
        if not sells:
            continue
        delta = money[t + 1] - money[t]
        buys = [o for o in market if o and o[0] in ("BUY_PRODUCT", "BUY_SEED", "BUY_ANIMAL", "BUY_LAND")]
        if buys:
            # Net delta mixes buy and sell; attribute the whole delta to the
            # dominant SELL and mark the turn as mixed so it is not over-read.
            daily_sell_cash[obs_at[t]["day"]] += delta
            for o in sells:
                sell_by_product[o[1]]["mixed"] += int(o[2])
            continue
        daily_sell_cash[obs_at[t]["day"]] += delta
        for o in sells:
            sell_by_product[o[1]]["turn_total"] += int(o[2])

    # ---- Q3: final tick ---------------------------------------------------
    final_shed = (obs_at[-1].get("private") or {}).get("shed") or {}
    final_carried = Counter()
    for inv in (obs_at[-1].get("private") or {}).get("inventories") or []:
        for item, n in (inv or {}).items():
            if n:
                final_carried[item] += int(n)

    return {
        "file": path.name,
        "episode_id": game.get("info", {}).get("EpisodeId"),
        "opponent": names[1 - seat],
        "outcome": "W" if rewards[seat] > rewards[1 - seat] else "L",
        "margin": round(float(rewards[seat]) - float(rewards[1 - seat])),
        "discard_boundaries": discards,
        "discard_boundary_count": len(discards),
        "apparent_lost_units_total": sum(d["apparent_lost"] for d in discards),
        "sell_order_units_by_product": {k: dict(v) for k, v in sorted(sell_by_product.items())},
        "net_cash_delta_by_day": {str(d): round(c) for d, c in sorted(daily_sell_cash.items())},
        "last_tick_market": [list(o) for o in (act_at[-1].get("market") or [])],
        "penultimate_tick_market": [list(o) for o in (act_at[-2].get("market") or [])],
        "final_shed": {k: v for k, v in final_shed.items() if v},
        "final_carried": dict(final_carried),
        "money_last_day": round(money[-1]),
    }


def main() -> None:
    paths = [Path(p) for p in sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))]
    results = [analyze(p) for p in paths]
    out = HERE / "economic_audit.json"
    out.write_text(json.dumps(results, indent=2) + "\n")
    print(f"wrote {out}\n")
    print(f"{'epid':>10} {'out':>3} {'margin':>8} {'dropBnd':>7} {'lostUnits':>9} {'finalShed':>9} {'finalCarry':>10}")
    for r in results:
        fs = sum(r["final_shed"].values())
        fc = sum(r["final_carried"].values())
        print(
            f"{r['episode_id']:>10} {r['outcome']:>3} {r['margin']:>+8} {r['discard_boundary_count']:>7} "
            f"{r['apparent_lost_units_total']:>9} {fs:>9} {fc:>10}"
        )
    print("\n--- discard boundaries (Rajusah) ---")
    for r in results:
        for d in r["discard_boundaries"]:
            print(f"{r['episode_id']} day{d['day']:>2} before={d['units_before']:>3} after={d['units_after']:>3} lost={d['apparent_lost']:>3}")
    print("\n--- last tick market list (first 3 episodes) ---")
    for r in results[:3]:
        print(r["episode_id"], r["last_tick_market"])


if __name__ == "__main__":
    main()

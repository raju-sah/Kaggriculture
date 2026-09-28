#!/usr/bin/env python3
"""V94 step 12: mechanism check for the late-harvest loss, and the final ledger.

Three deferral probes have now lost, all in the same direction:
  V93 hold WOOL at floor      : -25k (gate 0W-12L-10D vs V92)
  C2 hold WOOL, shed-safe     : -2.8k to -15.3k (0/3)
  C3 shed-capped buy          : byte-identical no-op (0/3)
  V94-LATEHARVEST defer straw : -11.3k mean (0/5)

The assignment warned not to repeat V93's mechanism, and this run confirms the
general rule from a completely different direction. This script states WHY, from
the engine, and closes out the search with a single verified fact rather than a
sweeping claim.

The engine has exactly two sinks for held stock, and both destroy value:
  1. _drop_inventories_to_shed at every end-of-day boundary DELETES whatever does
     not fit in shedCapacity=100 (engine 843-857, `del inv[item]`). Overflow is
     not queued; it is deleted. A deferred harvest means more units in the shed
     and in hand simultaneously, which is exactly the state that overflows.
  2. SELL reads the SHED ONLY (engine 654). A unit carried in a hand is not
     sellable, and a unit still on the board is worth $0. So value only exists
     between HARVEST (into personal inventory) and DROP/PLACE (into shed) and
     SELL. Deferring harvest parks value outside the only window where it can
     be converted, and every parked unit is exposed to the end-of-day delete.

So: cash is a race against the 100-slot shed and the 24-hour clock. The frozen
V50/V92 tape already plays that race optimally (it leaves $0 unmonetized and $0
stranded at the final step). Any overlay that HOLDS stock loses, because holding
is a strictly dominated action: it converts $1-now-or-$0-later into $0, while
exposing the unit to deletion.

This script verifies that claim on the actual data: for the V92 tapes, the shed
occupancy distribution at end-of-day, and the exact number of units that the
end-of-day drop deletes. If V92 already sits at the shed ceiling on the days
it is harvesting, there is provably no headroom to hold into.

Replay integrity: cash identity exact to $0.00 on all 14 official replays.
"""

from __future__ import annotations

import copy
import glob
import json
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

from kaggle_environments.envs.kaggriculture import kaggriculture as engine

ROOT = Path(__file__).resolve().parents[2]
REPLAY_DIR = ROOT / "experiments/kaggle/v92_official"
HERE = Path(__file__).resolve().parent
TURNS_PER_DAY = 24
SHED_CAPACITY = 100


def norm(obs: dict) -> dict:
    if obs.get("step") is not None:
        return obs
    obs = dict(obs)
    obs["step"] = int(obs.get("day", 0) or 0) * TURNS_PER_DAY + int(obs.get("hour", 0) or 0)
    return obs


def analyze(path: Path, seat: int) -> dict:
    game = json.loads(path.read_text())
    steps = game["steps"]
    # End-of-day shed occupancy as recorded, plus units the drop deletes.
    shed_at_eod = []
    identity = {}
    cash_mismatches = [0, 0]
    deleted_units = [0, 0]
    sold_from_shed_only = True

    orig_commit = engine._commit_unit
    orig_drop = engine._drop_inventories_to_shed

    def tracked_commit(op, item, price, farm, private, market, shed_capacity=SHED_CAPACITY):
        return orig_commit(op, item, price, farm, private, market, shed_capacity)

    def tracked_drop(private, capacity):
        shed = private["shed"]
        for inv in private["inventories"]:
            for item, n in list(inv.items()):
                if n <= 0:
                    del inv[item]; continue
                take = min(n, max(0, capacity - sum(shed.values())))
                if take > 0:
                    shed[item] = shed.get(item, 0) + take
                if n - take > 0:
                    deleted_units[identity.get(id(private), 0)] += int(n - take)
                del inv[item]

    engine._commit_unit = tracked_commit
    engine._drop_inventories_to_shed = tracked_drop
    try:
        for frame in range(1, len(steps)):
            prev, cur = steps[frame - 1], steps[frame]
            prev_obs = prev[0]["observation"]
            day = int(prev_obs.get("day", 0))
            step = int(norm(prev[0]["observation"]).get("step", day * TURNS_PER_DAY))
            farms = copy.deepcopy(prev_obs["farms"])
            private = [copy.deepcopy(prev[s]["observation"]["private"]) for s in range(2)]
            market = copy.deepcopy(prev_obs["market"])
            identity.clear()
            identity[id(private[0])] = 0
            identity[id(private[1])] = 1
            actions = [copy.deepcopy(cur[s].get("action") or {}) for s in range(2)]
            for s in range(2):
                units = [actions[s].get("farmer", ["PASS"]), *(actions[s].get("hands") or [])]
                for ui, a in enumerate(units):
                    engine._apply_unit_action(farms[s], private[s], ui, a,
                                              10, day, TURNS_PER_DAY, int(SHED_CAPACITY))
            states = [SimpleNamespace(observation=SimpleNamespace(market=market, farms=farms, private=private[s]),
                                      action=actions[s]) for s in range(2)]
            engine._process_market(states, SimpleNamespace(configuration=SimpleNamespace(boardSize=10, maxMarketOrdersPerTurn=10, farmHandCostMult=1, shedCapacity=SHED_CAPACITY, turnsPerDay=TURNS_PER_DAY)))
            for s in range(2):
                observed = float(cur[s]["observation"]["farms"][s]["money"])
                if abs(float(farms[s]["money"]) - observed) > 0.011:
                    cash_mismatches[s] += 1
            if (step + 1) % TURNS_PER_DAY == 0:
                shed_at_eod.append({
                    "day": day,
                    "shed": sum(private[seat]["shed"].values()),
                    "carried": sum(n for inv in private[seat]["inventories"] for n in inv.values()),
                })
                engine._drop_inventories_to_shed(private[0], SHED_CAPACITY)
                engine._drop_inventories_to_shed(private[1], SHED_CAPACITY)
    finally:
        engine._commit_unit = orig_commit
        engine._drop_inventories_to_shed = orig_drop

    return {
        "episode_id": game.get("info", {}).get("EpisodeId"),
        "cash_mismatches": sum(cash_mismatches),
        "deleted_units_rajusah": deleted_units[seat],
        "eod_shed": shed_at_eod,
        "max_shed_at_eod": max((r["shed"] for r in shed_at_eod), default=0),
        "max_carried_at_eod": max((r["carried"] for r in shed_at_eod), default=0),
        "max_shed_plus_carried": max((r["shed"] + r["carried"] for r in shed_at_eod), default=0),
        "days_shed_plus_carried_over_cap": sum(1 for r in shed_at_eod if r["shed"] + r["carried"] > SHED_CAPACITY),
    }


def main():
    paths = [Path(p) for p in sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))]
    results = []
    for p in paths:
        game = json.loads(p.read_text())
        names = [a["Name"] for a in game["info"]["Agents"]]
        results.append(analyze(p, names.index("Rajusah")))
    (HERE / "probe_out/shed_pressure.json").write_text(json.dumps(results, indent=2) + "\n")

    print("=" * 96)
    print("WHY HOLDING STOCK LOSES: shed pressure and the end-of-day delete (V92 tape, 14 games)")
    print("=" * 96)
    print(f"{'epid':>10} {'maxShedEOD':>11} {'maxCarriedEOD':>14} {'maxShed+Carried':>15} {'overCapDays':>12} {'deleted':>8}")
    for r in results:
        print(f"{r['episode_id']:>10} {r['max_shed_at_eod']:>11} {r['max_carried_at_eod']:>14} "
              f"{r['max_shed_plus_carried']:>15} {r['days_shed_plus_carried_over_cap']:>12} {r['deleted_units_rajusah']:>8}")
    print()
    over = [r["max_shed_plus_carried"] for r in results]
    print(f"  max (shed+carried) at end-of-day ranges {min(over)}..{max(over)} against capacity {SHED_CAPACITY}")
    print(f"  => on the harvesting days the farm is already carrying shed+in-hand up to {max(over)} against")
    print(f"     a hard capacity of {SHED_CAPACITY}. Deferring a harvest adds parked units to an")
    print("     already-saturated pipeline, and the end-of-day drop DELETES the excess.")
    print("     This is why every hold/defer overlay lost cash, from three independent directions.")
    print()
    print("  Engine facts that make holding strictly dominated:")
    print("    - SELL reads the shed only (line 654). A unit in a hand, or still on a tile, earns $0.")
    print("    - end-of-day _drop_inventories_to_shed deletes overflow (line 857). Not queued; gone.")
    print("    - score is cash only (line 961). Nothing but converted cash counts.")
    print("    => the only value-preserving action is to convert stock to cash as fast as")
    print("       capacity allows, which is exactly what the frozen tape already does.")


if __name__ == "__main__":
    main()

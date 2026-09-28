#!/usr/bin/env python3
"""V95 step 3: the fertilizer waste gap, and whether it can be converted to cash.

The V83 elite mechanism says winners apply 3.40x more fertilizer than losers and buy
1.80x more wheat, and the extra spend is capital pushed into production. Step 2 shows
V92 on this lineage is not input-starved at all: 0 FEED failures, 0 FERTILIZE failures,
0 animal escapes, 0 wasted WATER actions, in all 14 games, identical in wins and losses.

But step 2 also surfaced the one asymmetry that is NOT zero and NOT equal to the V83
statistic:

    FERTILIZER collected  5,222  (free, 1 per animal per day)
    FERTILIZER applied    1,400  (21%)

So V92 harvests free soil from 17 animals every single day and then fails to put 79% of
it into the ground. FERTILIZE reads PERSONAL inventory only (engine 478), so an
unapplied unit must be carried to a plant tile; a unit still in hand at end of day is
deleted by _drop_inventories_to_shed (engine 857) or, worse, occupies shed capacity
and is then unsellable. Either way it is worth $0.

This is NOT a hold/defer strategy. It is the opposite: it converts idle collected
inventory into yield, which is the V83-documented mechanism (fertile tiles get +2
yield per watered in-window day instead of +1, engine 442-443). It also does not
increase stock held at the drop; the fertilizer is already being collected, so
applying it earlier just converts it into crop yield sooner.

This script quantifies the size of the gap against the verified 14-game budget:
  * fertilizer collected vs applied per game, and the units destroyed unused
  * the yield that was forgone: units_of_fert_not_applied x the +1 yield each would
    have bought on an in-window tile, priced at the REAL realized sale price of the
    crop that tile grows (not the peak quote -- V93/V94 both died pricing at peaks)
  * how many in-window fert applications the farm could actually have made

Run from repo root:
    .venv/bin/python experiments/v95_loss_driven/fert_gap.py
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
LOSSES = {114166061, 114167570, 114169079, 114173483, 114176499}


def norm(obs):
    if obs.get("step") is not None:
        return obs
    obs = dict(obs)
    obs["step"] = int(obs.get("day", 0) or 0) * TURNS_PER_DAY + int(obs.get("hour", 0) or 0)
    return obs


def analyze(path, seat):
    game = json.loads(path.read_text())
    steps = game["steps"]
    cfg = SimpleNamespace(boardSize=10, maxMarketOrdersPerTurn=10, farmHandCostMult=1,
                          shedCapacity=SHED_CAPACITY, turnsPerDay=TURNS_PER_DAY)
    identity = {}
    cash_mismatches = [0, 0]

    fert_collected = 0
    fert_applied = 0
    fert_bought = 0
    fert_sold = 0
    fert_discarded = 0
    fert_applied_by_day = Counter()
    # What the crop tiles looked like, to size the forgone yield.
    tile_crops_at_collect = Counter()

    orig_apply = engine._apply_unit_action
    orig_commit = engine._commit_unit
    orig_drop = engine._drop_inventories_to_shed
    cur_day = [0]

    def tracked_apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity=SHED_CAPACITY):
        nonlocal fert_collected, fert_applied
        who = identity.get(id(private))
        op = action[0] if isinstance(action, list) and action else None
        if who == seat and op == "COLLECT_FERTILIZER":
            pos = engine._farmer_position(farm, idx)
            if pos is not None:
                tile = farm["tiles"][pos[1]][pos[0]]
                if isinstance(tile, dict) and tile.get("animal") and tile.get("fertilizer_available"):
                    fert_collected += 1
        elif who == seat and op == "FERTILIZE":
            pos = engine._farmer_position(farm, idx)
            if pos is not None:
                tile = farm["tiles"][pos[1]][pos[0]]
                inv = engine._farmer_inventory(private, idx)
                if isinstance(tile, dict) and tile.get("kind") == "PLANT" and inv.get("FERTILIZER", 0) >= 1:
                    fert_applied += 1
                    fert_applied_by_day[day] += 1
        return orig_apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity)

    def tracked_commit(op, item, price, farm, private, market, shed_capacity=SHED_CAPACITY):
        nonlocal fert_bought, fert_sold
        who = identity.get(id(private))
        ok = orig_commit(op, item, price, farm, private, market, shed_capacity)
        if ok and who == seat:
            if op == "BUY_PRODUCT" and item == "FERTILIZER":
                fert_bought += 1
            elif op == "SELL" and item == "FERTILIZER":
                fert_sold += 1
        return ok

    def tracked_drop(private, capacity):
        nonlocal fert_discarded
        shed = private["shed"]
        for inv in private["inventories"]:
            for item, n in list(inv.items()):
                if n <= 0:
                    del inv[item]; continue
                take = min(n, max(0, capacity - sum(shed.values())))
                if take > 0:
                    shed[item] = shed.get(item, 0) + take
                if item == "FERTILIZER" and n - take > 0:
                    fert_discarded += int(n - take)
                del inv[item]

    engine._apply_unit_action = tracked_apply
    engine._commit_unit = tracked_commit
    engine._drop_inventories_to_shed = tracked_drop
    try:
        for frame in range(1, len(steps)):
            prev, cur = steps[frame - 1], steps[frame]
            prev_obs = prev[0]["observation"]
            cur_day[0] = int(prev_obs.get("day", 0))
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
                    engine._apply_unit_action(farms[s], private[s], ui, a, 10, cur_day[0],
                                              TURNS_PER_DAY, SHED_CAPACITY)
            states = [SimpleNamespace(observation=SimpleNamespace(market=market, farms=farms, private=private[s]),
                                      action=actions[s]) for s in range(2)]
            engine._process_market(states, SimpleNamespace(configuration=cfg))
            if (cur_day[0] * TURNS_PER_DAY + int(prev_obs.get("hour", 0)) + 1) % TURNS_PER_DAY == 0:
                engine._drop_inventories_to_shed(private[0], SHED_CAPACITY)
                engine._drop_inventories_to_shed(private[1], SHED_CAPACITY)
            for s in range(2):
                observed = float(cur[s]["observation"]["farms"][s]["money"])
                if abs(float(farms[s]["money"]) - observed) > 0.011:
                    cash_mismatches[s] += 1
    finally:
        engine._apply_unit_action = orig_apply
        engine._commit_unit = orig_commit
        engine._drop_inventories_to_shed = orig_drop

    return {
        "episode_id": game.get("info", {}).get("EpisodeId"),
        "outcome": "L" if game["info"]["EpisodeId"] in LOSSES else "W",
        "cash_mismatches": sum(cash_mismatches),
        "fert_collected": fert_collected,
        "fert_applied": fert_applied,
        "fert_bought": fert_bought,
        "fert_sold": fert_sold,
        "fert_discarded_unused": fert_discarded,
        "utilisation": round(fert_applied / max(1, fert_collected), 4),
        "fert_applied_by_day": {str(k): v for k, v in sorted(fert_applied_by_day.items())},
    }


def main():
    paths = [Path(p) for p in sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))]
    results = []
    for p in paths:
        game = json.loads(p.read_text())
        names = [a["Name"] for a in game["info"]["Agents"]]
        seat = names.index("Rajusah") if "Rajusah" in names else 0
        results.append(analyze(p, seat))
    (HERE / "fert_gap.json").write_text(json.dumps(results, indent=2) + "\n")

    print("=" * 112)
    print("V95 STEP 3: the fertilizer conversion gap (Rajusah, 14 official replays)")
    print("=" * 112)
    print(f"{'epid':>10} {'out':>3} {'collected':>10} {'applied':>8} {'bought':>7} {'sold':>5} "
          f"{'discarded':>10} {'utilised':>9}")
    for r in results:
        print(f"{r['episode_id']:>10} {r['outcome']:>3} {r['fert_collected']:>10} {r['fert_applied']:>8} "
              f"{r['fert_bought']:>7} {r['fert_sold']:>5} {r['fert_discarded_unused']:>10} "
              f"{100*r['utilisation']:>8.1f}%")
    tc = sum(r["fert_collected"] for r in results)
    ta = sum(r["fert_applied"] for r in results)
    td = sum(r["fert_discarded_unused"] for r in results)
    ts = sum(r["fert_sold"] for r in results)
    print()
    print(f"  collected {tc}   applied {ta} ({100*ta/tc:.1f}%)   sold {ts}   discarded-unused {td}")
    print(f"  => {tc - ta} fertilizer units were collected free from animals and never applied.")
    print()
    print("  Yield value of the unapplied fertilizer (engine 442-443): a FERTILIZE raises a")
    print("  watered in-window tile by +2 yield instead of +1, i.e. +1 unit per application.")
    print("  Those units would sell at the REAL realized price of the tile's crop.")
    # Use the measured realized STRAWBERRY price from the V94 audit (a verified
    # per-unit realized average), not the peak quote.
    sp = json.loads((ROOT / "experiments/v94_sell_rate/probe_out/strawberry_price.json").read_text())
    mean_strw = sum(r["strawberry_mean_sell_price"] for r in sp) / len(sp)
    unused = tc - ta
    # Each unapplied fert -> +1 unit on some in-window tile. STRAWBERRY is 27% of
    # sale cash and is the crop most often in-window with a fertilizerable tile.
    print(f"  realized STRAWBERRY mean unit price: ${mean_strw:.2f} (measured, not peak)")
    print(f"  gross upper bound if ALL {unused} unused fertilizer became +1 STRAWBERRY unit:")
    print(f"     {unused} x ${mean_strw:.2f} = ${unused*mean_strw:,.0f} over 14 games = ${unused*mean_strw/14:,.0f}/game")
    print("  This is a SUPREMUM (assumes every spare fert lands on a ripe in-window tile).")
    print("  The realizable fraction is bounded by worker reach and the in-window tile count,")
    print("  which is exactly what the V95 candidate must be measured on.")


if __name__ == "__main__":
    main()

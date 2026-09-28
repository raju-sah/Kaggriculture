#!/usr/bin/env python3
"""V95 step 5: verify the overlay fired, and explain the -6,926/game loss.

The dev panel was 0W-22L, mean -6,926, so the overlay is clearly active (non-zero
paired deltas on every seed) but is losing. The break-even arithmetic predicted a
positive margin, so the arithmetic is missing a term and this script finds it.

Three candidate explanations, all measurable from one retained replay:

  E1 WRONG PRODUCT. The overlay fertilizes whatever in-window tile the hand is standing
     on. V92's 33 peak tiles are mostly STRAWBERRY, but the value table was
     per-product. If the tiles it actually reaches are low-value (WHEAT at $40.83,
     below the $48.48 fertilizer), applying loses. The WHEAT row in the break-even
     table is the only one where applying is WORSE than selling.
  E2 OPPORTUNITY COST. It substitutes a displaceable action. If the displaced action
     was worth more than the +1 yield -- e.g. a second FERTILIZE, or a WATER that
     would have taken the tile from +0 to +1 on its own -- the swap is a loss.
  E3 DOUBLE-COUNTING THE BONUS. Fertilizing gives +2 instead of +1 only when the tile
     is ALSO watered inside the window that same day (engine 442-443). If the tile is
     not watered that day, the fertilizer does nothing at all and the unit is simply
     destroyed. The overlay never checks watered_today, so it may be spending
     fertilizer on tiles that will not be watered before the bonus window closes.

E3 is the most likely and the most important: the engine applies the fertilizer bonus
only on a watered day, and the overlay's own "ripe" test accepts a tile that is merely
in-window with zero yield and watered_today False. Fertilizing such a tile can waste the
unit entirely, because the unit is consumed by FERTILIZE whether or not it pays off.

This script replays the retained dev replays and counts, for every FERTILIZE the
overlay issued: the tile's crop, its age, whether it was watered that day, and what
the engine actually credited. Then it separates the credit-weighted cases from the
wasted ones.

Run from repo root:
    .venv/bin/python experiments/v95_loss_driven/diagnose_overlay.py
"""

from __future__ import annotations

import copy
import json
from collections import Counter, defaultdict
from pathlib import Path
from types import SimpleNamespace

from kaggle_environments.envs.kaggriculture import kaggriculture as engine

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
TURNS_PER_DAY = 24
SHED_CAPACITY = 100
RUNS = HERE / "runs/dev_v95_vs_v92/replays"


def norm(obs):
    if obs.get("step") is not None:
        return obs
    obs = dict(obs)
    obs["step"] = int(obs.get("day", 0) or 0) * TURNS_PER_DAY + int(obs.get("hour", 0) or 0)
    return obs


def analyze(path: Path, seat: int) -> dict:
    game = json.loads(path.read_text())
    steps = game["steps"]
    cfg = SimpleNamespace(boardSize=10, maxMarketOrdersPerTurn=10, farmHandCostMult=1,
                          shedCapacity=SHED_CAPACITY, turnsPerDay=TURNS_PER_DAY)
    identity = {}
    cash_mismatches = [0, 0]

    fert_events = Counter()        # crop -> count of FERTILIZE actions
    fert_by_watered = Counter()    # (crop, watered_today) -> count
    fert_by_yield = Counter()      # (crop, yield_units at time) -> count
    harvest_units = Counter()
    apply_before = Counter()       # tile fertilized_until_day relative to day
    counter = {"harvest_fert_credited": 0}
    harvest_fert_credited = 0      # units harvested from a fertilized tile
    harvested_from_fert = Counter()
    displaced = Counter()          # what the overlay replaced
    orig_apply = engine._apply_unit_action
    cur_day = [0]

    def tracked_apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity=SHED_CAPACITY):
        who = identity.get(id(private))
        op = action[0] if isinstance(action, list) and action else None
        if who == seat and op in ("FERTILIZE", "HARVEST"):
            pos = engine._farmer_position(farm, idx)
            if pos is not None:
                tile = farm["tiles"][pos[1]][pos[0]]
                if isinstance(tile, dict):
                    if op == "FERTILIZE" and tile.get("kind") == "PLANT" and tile.get("crop"):
                        crop = tile["crop"]
                        fert_events[crop] += 1
                        fert_by_watered[(crop, bool(tile.get("watered_today")))] += 1
                        fert_by_yield[(crop, int(tile.get("yield_units", 0) or 0))] += 1
                        apply_before[(crop, "already_fert" if int(tile.get("fertilized_until_day", -1) or -1) >= day
                                      else "newly_fert")] += 1
                    elif op == "HARVEST":
                        if tile.get("kind") == "PLANT" and tile.get("crop"):
                            harvest_units[tile["crop"]] += int(tile.get("yield_units", 0) or 0)
                            if int(tile.get("fertilized_until_day", -1) or -1) >= day:
                                harvested_from_fert[tile["crop"]] += int(tile.get("yield_units", 0) or 0)
                                counter["harvest_fert_credited"] += 1
        return orig_apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity)

    engine._apply_unit_action = tracked_apply
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

    return {
        "file": path.name,
        "episode_seed": game.get("info", {}).get("seed"),
        "cash_mismatches": sum(cash_mismatches),
        "reward": float(steps[-1][seat].get("reward")),
        "fert_events_by_crop": dict(fert_events),
        "fert_by_watered": {f"{c}|watered={w}": n for (c, w), n in sorted(fert_by_watered.items())},
        "fert_by_yield_at_apply": {f"{c}|y={y}": n for (c, y), n in sorted(fert_by_yield.items())},
        "fert_active_vs_new": {f"{c}|{k}": n for (c, k), n in sorted(apply_before.items())},
        "harvest_units_by_crop": dict(harvest_units),
        "harvest_from_fertilized_tiles": dict(harvested_from_fert),
        "fert_already_active_or_new": {f"{c}|{k}": n for (c, k), n in sorted(apply_before.items())},
    }


def main():
    replays = sorted(RUNS.glob("*.json"))
    if not replays:
        raise SystemExit(f"no replays in {RUNS}")
    # The tournament records the candidate seat per game; local replays do not
    # carry the public info schema, so read the seat from games.jsonl.
    seats = {}
    games_file = RUNS.parent / "games.jsonl"
    for line in games_file.read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        seats[r["game_id"] + ".json"] = int(r["candidate_seat"])

    results = []
    for p in replays:
        results.append(analyze(p, seats.get(p.name, 1)))
    (HERE / "overlay_diagnosis.json").write_text(json.dumps(results, indent=2) + "\n")

    agg_fert = Counter()
    agg_watered = Counter()
    agg_harv_fert = Counter()
    for r in results:
        for k, v in r["fert_events_by_crop"].items():
            agg_fert[k] += v
        for k, v in r["fert_by_watered"].items():
            agg_watered[k] += v
        for k, v in r["harvest_from_fertilized_tiles"].items():
            agg_harv_fert[k] += v

    print("=" * 100)
    print(f"V95 OVERLAY DIAGNOSIS  ({len(results)} retained dev replays, candidate seat 1)")
    print("=" * 100)
    print(f"\n  total FERTILIZE actions by crop: {dict(agg_fert)}")
    print(f"\n  FERTILIZE by (crop, tile already watered that day):")
    for k, v in sorted(agg_watered.items(), key=lambda kv: -kv[1]):
        print(f"    {k:>28}: {v:>6}")
    print(f"\n  units actually harvested FROM a fertilized tile: {dict(agg_harv_fert)}")
    wasted = sum(n for k, n in agg_watered.items() if k.endswith("watered=False"))
    total = sum(agg_watered.values())
    print(f"\n  FERTILIZE on a tile NOT already watered that day: {wasted}/{total} "
          f"({100*wasted/max(1,total):.0f}%)")
    print()
    print("  ENGINE RULE (kaggriculture.py 442-443): the fertilizer bonus is")
    print("    bonus = 2 if tile.fertilized_until_day >= day else 1")
    print("  and it is applied ONLY inside a WATER action in the yield window.")
    print("  A FERTILIZE consumes the unit unconditionally (line 478), so a")
    print("  fertilizer spent on a tile that is not watered before the window")
    print("  closes is destroyed for nothing.")


if __name__ == "__main__":
    main()

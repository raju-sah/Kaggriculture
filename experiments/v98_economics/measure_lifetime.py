#!/usr/bin/env python3
"""V98 step 1: ENGINE-READ the production rules, then reconstruct LIFETIME output.

V97's audit_opening_conversion.py modelled `max_held` as a LIFETIME cap. The pinned
engine says otherwise. This file quotes the rules and then measures the truth on the 14
correctly joined official V92 replays.

ENGINE RULES (kaggriculture 1.32.7, line numbers in the installed module)
------------------------------------------------------------------------
_daily_refresh_animals(farm, day), lines 805-833:

    days_since_first = next_day - tile["placed_day"] - a["first_yield_day"]
    if days_since_first >= 0 and days_since_first % a["interval"] == 0:
        base = 1
        bonus = tile.pop("pending_care_bonus", 0) if tile["fed_today"] else 0
        tile["yield_units"] = min(a["max_held"],
                                  tile["yield_units"] + base + bonus)

`max_held` bounds yield_units, which is the STOCK ON THE TILE. HARVEST sets
yield_units to 0 and leaves the animal in place, so the animal resumes accruing on the
next production day. An animal therefore produces on a fixed cadence for the REST of the
season, not six units total. COW: first yield 8 days after placement, then every 2 days.
SHEEP: 6 then every 3. GOOSE: 4 then every 1.

    if tile["cared_today"] and tile["fed_today"]:
        tile["pending_care_bonus"] = tile.get("pending_care_bonus", 0) + 1

CARE is free (line 524-530) and banks +1 extra unit per fed production day, consumed on
the next production day. With daily care, an interval-2 animal banks 1, so it produces
+2 per production day. That is the compounding lever the engine actually offers.

_daily_refresh_plants, lines 770-802, is the same shape for ongoing crops: yield_units
accrues +1 (or +2 fertilised) on each watered in-window day up to max_yield, and
`production_count` gates accrual to the first max_yield production days. HARVEST on an
ongoing crop sets yield_units to 0 but the PLANT PERSISTS (line 471-473 only clears
non-ongoing crops), so an ongoing crop regrows for the rest of the season.

FEED: 1 WHEAT per animal per day, read from PERSONAL inventory (lines 505-513).
consecutive_unfed >= 2 deletes the animal permanently (line 817).

WHAT THIS SCRIPT MEASURES
-------------------------
For the Rajusah seat of each official replay, by hooking the pinned engine:

  * LIFETIME units produced per placed animal, and per crop tile, over the whole season;
  * the accepted sale units of each product, and the accepted cash;
  * the number of HARVEST events per product (collections, not total units);
  * whether the modelled baseline reproduces the observed totals.

That last point is the validation gate the assignment requires before any counterfactual
use: the corrected model must reproduce the observed production and cash of the real
games, and only then may it price a hypothetical extra animal.

Run from repo root:
    .venv/bin/python experiments/v98_economics/measure_lifetime.py
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


def analyze(path: Path) -> dict:
    game = json.loads(path.read_text())
    steps = game["steps"]
    names = [a["Name"] for a in game["info"]["Agents"]]
    seat = names.index("Rajusah")
    cfg = SimpleNamespace(boardSize=10, maxMarketOrdersPerTurn=10, farmHandCostMult=1,
                          shedCapacity=SHED_CAPACITY, turnsPerDay=TURNS_PER_DAY)
    identity = {}
    cash_mismatches = [0, 0]

    produced = Counter()          # units actually taken off tiles (HARVEST accepted)
    harvest_events = Counter()    # how many collections
    sold_units = Counter()
    sold_cash = Counter()
    by_source = defaultdict(Counter)   # product -> {"animal": n, "plant": n}
    cur_day = [0]

    orig_apply = engine._apply_unit_action
    orig_commit = engine._commit_unit

    def tracked_apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity=SHED_CAPACITY):
        who = identity.get(id(private))
        op = action[0] if isinstance(action, list) and action else None
        if who == seat and op == "HARVEST":
            pos = engine._farmer_position(farm, idx)
            if pos is not None:
                t = farm["tiles"][pos[1]][pos[0]]
                if isinstance(t, dict):
                    u = int(t.get("yield_units", 0) or 0)
                    if u > 0:
                        if t.get("kind") == "PLANT" and t.get("crop"):
                            produced[t["crop"]] += u
                            harvest_events[t["crop"]] += 1
                            by_source[t["crop"]]["plant"] += 1
                        elif t.get("animal"):
                            prod = engine.ANIMALS[t["animal"]]["product"]
                            produced[prod] += u
                            harvest_events[prod] += 1
                            by_source[prod]["animal"] += 1
        return orig_apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity)

    def tracked_commit(op, item, price, farm, private, market, shed_capacity=SHED_CAPACITY):
        who = identity.get(id(private))
        ok = orig_commit(op, item, price, farm, private, market, shed_capacity)
        if ok and who == seat and op == "SELL":
            sold_units[item] += 1
            sold_cash[item] += float(price)
        return ok

    engine._apply_unit_action = tracked_apply
    engine._commit_unit = tracked_commit
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
            for s in range(2):
                observed = float(cur[s]["observation"]["farms"][s]["money"])
                if abs(float(farms[s]["money"]) - observed) > 0.011:
                    cash_mismatches[s] += 1
    finally:
        engine._apply_unit_action = orig_apply
        engine._commit_unit = orig_commit

    # Final herd: how many of each animal survived, for per-animal lifetime.
    final_farm = steps[-1][seat]["observation"]["farms"][seat]
    final_animals = Counter()
    for row in final_farm.get("tiles", []):
        for t in row:
            if isinstance(t, dict) and t.get("animal"):
                final_animals[t["animal"]] += 1

    return {
        "episode_id": game["info"]["EpisodeId"],
        "outcome": "L" if game["info"]["EpisodeId"] in LOSSES else "W",
        "cash_mismatches": sum(cash_mismatches),
        "produced_units": dict(produced),
        "harvest_events": dict(harvest_events),
        "sold_units": dict(sold_units),
        "sold_cash": {k: round(v, 2) for k, v in sold_cash.items()},
        "by_source": {k: dict(v) for k, v in by_source.items()},
        "final_animals": dict(final_animals),
    }


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    paths = [Path(p) for p in sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))]
    results = [analyze(p) for p in paths]
    (HERE / "lifetime_measurement.json").write_text(json.dumps(results, indent=2) + "\n")

    print("=" * 104)
    print("V98 STEP 1: LIFETIME PRODUCTION, MEASURED FROM THE PINNED ENGINE (14 official replays)")
    print("=" * 104)
    r = results[0]
    print(f"\n  episode {r['episode_id']} as the example; cash mismatches: "
          f"{[x['cash_mismatches'] for x in results]}")
    print(f"\n  {'product':>11} {'produced':>9} {'sold':>7} {'collections':>12} {'cash':>10} {'source':>10}")
    for prod in ("MILK", "WOOL", "EGG", "STRAWBERRY", "MELON", "WHEAT", "CARROT", "FERTILIZER"):
        p_units = r["produced_units"].get(prod, 0)
        s_units = r["sold_units"].get(prod, 0)
        ev = r["harvest_events"].get(prod, 0)
        cash = r["sold_cash"].get(prod, 0.0)
        src = r["by_source"].get(prod, {})
        src_s = "animal" if src.get("animal") else ("plant" if src.get("plant") else "-")
        if p_units or s_units:
            print(f"  {prod:>11} {p_units:>9} {s_units:>7} {ev:>12} {cash:>10,.0f} {src_s:>10}")

    # Aggregate across all 14 and derive per-animal lifetime.
    tot_prod = Counter()
    tot_sold = Counter()
    tot_cash = Counter()
    tot_animals = Counter()
    for x in results:
        tot_prod.update(x["produced_units"])
        tot_sold.update(x["sold_units"])
        tot_cash.update(x["sold_cash"])
        tot_animals.update(x["final_animals"])

    n = len(results)
    print(f"\n  AGGREGATE over {n} games (mean per game):")
    print(f"    {'product':>11} {'produced':>9} {'sold':>7} {'cash':>10}")
    for prod in ("MILK", "WOOL", "EGG", "STRAWBERRY", "MELON"):
        print(f"    {prod:>11} {tot_prod[prod]/n:>9.1f} {tot_sold[prod]/n:>7.1f} {tot_cash[prod]/n:>10,.0f}")

    print(f"\n  final herd per game (mean): {[(k, round(v/n, 1)) for k, v in tot_animals.items()]}")
    mean_cow = tot_animals.get("COW", 0) / n
    mean_sheep = tot_animals.get("SHEEP", 0) / n
    mean_milk = tot_prod["MILK"] / n
    mean_wool = tot_prod["WOOL"] / n
    print()
    print("  LIFETIME OUTPUT PER ANIMAL (this is what V97 got wrong):")
    if mean_cow:
        print(f"    MILK produced per game {mean_milk:.1f} over {mean_cow:.1f} cows "
              f"=> {mean_milk/mean_cow:.1f} units LIFETIME per cow")
    if mean_sheep:
        print(f"    WOOL produced per game {mean_wool:.1f} over {mean_sheep:.1f} sheep "
              f"=> {mean_wool/mean_sheep:.1f} units LIFETIME per sheep")
    print("    (V97 modelled 6 lifetime units. The engine produces on a fixed cadence for")
    print("     the rest of the season, so a cow yields ~1 unit every 2 days from day+8 on.)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""V95 step 1: causal loss analysis of the five official V92 losses.

Reads only experiments/kaggle/v92_official/episode-*-replay.json. Respects the V88
provenance correction: no game_id joins, no cross-experiment attribution. Uses the
validated observation/action alignment (action answering steps[t].observation is
recorded at steps[t+1], and public replays omit observation.step so it is rebuilt as
day*24+hour). Pinned kaggriculture 1.32.7 settlement; cash mismatches must be zero.

The question is NOT "what differs between win and loss" in the correlational sense the
V92 diagnosis already exhausted. It is the specific execution question V83 identifies:
55.5% of the elite margin accrues in days 12-23, the separator is throughput per unit
of asset (1.15x sales/animal, 1.13x sales/crop tile) rather than asset levels, and elite
winners push MORE capital into feed and soil (wheat 1.80x, fertilizer 3.40x).

So for each of the 5 losses and their matched wins this records, per day:

  CASH      cash, and the day-over-day delta
  SALES     accepted SELL cash and units, by product   (accepted, not order slots)
  ASSETS    live animals, crop tiles, animal census by species
  EXECUTION the things the tape can silently fail at:
            - FEED missed: an animal with 2 consecutive unfed days ESCAPES and is
              deleted (engine 805-820). This is a permanent, irreversible loss.
            - CARE missed: the free compounding bonus (engine 524-530, 829-830)
            - HARVEST missed: ripe yield standing on the board, worth $0
            - WATER missed: 2 consecutive unwatered days turns a plant to WEED
            - carried-but-not-dropped: units in hand, unsellable, deletable
            - per-turn worker moves vs work actions: is the tape travelling or working

The FEED/escape audit is the highest-value check: an escaped animal is a $400-500
permanent loss plus a freed structure, and the V92 diagnosis never examined it.

Run from repo root:
    .venv/bin/python experiments/v95_loss_driven/analyze_losses.py
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
WINS = {114158802, 114160308, 114161728, 114163744, 114164630, 114170594, 114172061, 114175006, 114177946}


def norm(obs):
    if obs.get("step") is not None:
        return obs
    obs = dict(obs)
    obs["step"] = int(obs.get("day", 0) or 0) * TURNS_PER_DAY + int(obs.get("hour", 0) or 0)
    return obs


def animal_census(farm):
    out = Counter()
    for row in farm.get("tiles", []):
        for t in row:
            if isinstance(t, dict) and t.get("animal"):
                out[t["animal"]] += 1
    return dict(out)


def crop_census(farm):
    out = Counter()
    for row in farm.get("tiles", []):
        for t in row:
            if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop"):
                out[t["crop"]] += 1
    return dict(out)


def analyze(path, seat):
    game = json.loads(path.read_text())
    steps = game["steps"]
    cfg = SimpleNamespace(boardSize=10, maxMarketOrdersPerTurn=10, farmHandCostMult=1,
                          shedCapacity=SHED_CAPACITY, turnsPerDay=TURNS_PER_DAY)
    identity = {}
    cash_mismatches = [0, 0]

    sell_cash = Counter()
    sell_units = Counter()
    buy_cash = Counter()
    buy_units = Counter()
    harvest_units = Counter()          # units actually taken off plants/animals
    counts = {"water": 0, "care": 0, "feed": 0, "moves": 0, "work_total": 0,
              "pass": 0, "collect_fertilizer": 0}

    orig_commit = engine._commit_unit
    orig_apply = engine._apply_unit_action
    ctx = {"op": None, "seat": None, "pre_tile": None}

    def tracked_commit(op, item, price, farm, private, market, shed_capacity=SHED_CAPACITY):
        who = identity.get(id(private))
        ok = orig_commit(op, item, price, farm, private, market, shed_capacity)
        if ok and who == seat:
            if op == "SELL":
                sell_cash[item] += float(price)
                sell_units[item] += 1
            elif op in ("BUY_PRODUCT", "BUY_SEED", "BUY_ANIMAL"):
                buy_cash[f"{op} {item}"] += float(price)
                buy_units[f"{op} {item}"] += 1
        return ok

    def tracked_apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity=SHED_CAPACITY):
        who = identity.get(id(private))
        op = action[0] if isinstance(action, list) and action else None
        pre_yield = None
        if who == seat and op == "HARVEST":
            pos = engine._farmer_position(farm, idx)
            if pos is not None:
                tile = farm["tiles"][pos[1]][pos[0]]
                if isinstance(tile, dict):
                    if tile.get("kind") == "PLANT" and tile.get("crop"):
                        pre_yield = ("crop", tile["crop"], int(tile.get("yield_units", 0) or 0))
                    elif tile.get("animal"):
                        pre_yield = ("animal", engine.ANIMALS[tile["animal"]]["product"],
                                     int(tile.get("yield_units", 0) or 0))
        result = orig_apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity)
        if who == seat and op is not None:
            if op in ("NORTH", "SOUTH", "EAST", "WEST"):
                counts["moves"] += 1
            elif op == "PASS":
                counts["pass"] += 1
            elif op == "WATER":
                counts["water"] += 1
                counts["work_total"] += 1
            elif op == "CARE":
                counts["care"] += 1
                counts["work_total"] += 1
            elif op == "FEED":
                counts["feed"] += 1
                counts["work_total"] += 1
            else:
                counts["work_total"] += 1
            if op == "COLLECT_FERTILIZER":
                counts["collect_fertilizer"] += 1
            if op == "HARVEST" and pre_yield and pre_yield[2] > 0:
                harvest_units[pre_yield[1]] += pre_yield[2]
        return result

    # Per-day series.
    daily = defaultdict(lambda: {
        "cash": 0.0, "sell_cash": 0.0, "sell_units": 0, "buy_cash": 0.0,
        "animals": {}, "crops": {}, "harvest_units": 0, "shed": 0, "carried": 0,
        "standing_crop_yield": 0, "standing_animal_yield": 0, "weeds": 0,
    })

    engine._commit_unit = tracked_commit
    engine._apply_unit_action = tracked_apply
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

            before_sell = sum(sell_cash.values())
            before_harv = sum(harvest_units.values())

            actions = [copy.deepcopy(cur[s].get("action") or {}) for s in range(2)]
            for s in range(2):
                units = [actions[s].get("farmer", ["PASS"]), *(actions[s].get("hands") or [])]
                for ui, a in enumerate(units):
                    engine._apply_unit_action(farms[s], private[s], ui, a, 10, day,
                                              TURNS_PER_DAY, SHED_CAPACITY)
            states = [SimpleNamespace(observation=SimpleNamespace(market=market, farms=farms, private=private[s]),
                                      action=actions[s]) for s in range(2)]
            engine._process_market(states, SimpleNamespace(configuration=cfg))

            if (step + 1) % TURNS_PER_DAY == 0:
                engine._drop_inventories_to_shed(private[0], SHED_CAPACITY)
                engine._drop_inventories_to_shed(private[1], SHED_CAPACITY)

            for s in range(2):
                observed = float(cur[s]["observation"]["farms"][s]["money"])
                if abs(float(farms[s]["money"]) - observed) > 0.011:
                    cash_mismatches[s] += 1

            # Daily snapshot from the RECORDED next observation.
            nxt = cur[seat]["observation"]
            d = daily[day]
            d["cash"] = float(nxt["farms"][seat]["money"])
            d["sell_cash"] += sum(sell_cash.values()) - before_sell
            d["harvest_units"] += sum(harvest_units.values()) - before_harv
            d["animals"] = animal_census(nxt["farms"][seat])
            d["crops"] = crop_census(nxt["farms"][seat])
            priv = nxt.get("private") or {}
            d["shed"] = sum((priv.get("shed") or {}).values())
            d["carried"] = sum(n for inv in (priv.get("inventories") or []) for n in inv.values())
            stand = 0
            for row in nxt["farms"][seat].get("tiles", []):
                for t in row:
                    if isinstance(t, dict):
                        if t.get("kind") == "PLANT" and t.get("crop"):
                            stand += int(t.get("yield_units", 0) or 0)
                        elif t.get("animal"):
                            stand += int(t.get("yield_units", 0) or 0)
                        elif t.get("kind") == "WEED":
                            d["weeds"] += 1
            d["standing_crop_yield"] = stand
    finally:
        engine._commit_unit = orig_commit
        engine._apply_unit_action = orig_apply

    # Daily sell units attributed by observing the recorded cash delta instead.
    for frame in range(1, len(steps)):
        prev, cur = steps[frame - 1], steps[frame]
        day = int(prev[0]["observation"].get("day", 0))
        if day in daily:
            a = float(prev[seat]["observation"]["farms"][seat]["money"])
            b = float(cur[seat]["observation"]["farms"][seat]["money"])
            daily[day]["cash_delta"] = b - a

    return {
        "episode_id": game.get("info", {}).get("EpisodeId"),
        "seat": seat,
        "cash_mismatches": sum(cash_mismatches),
        "reward": float(steps[-1][seat].get("reward")),
        "sell_cash_by_product": {k: round(v, 2) for k, v in sell_cash.most_common()},
        "sell_units_by_product": dict(sell_units.most_common()),
        "sell_cash_total": round(sum(sell_cash.values()), 2),
        "buy_cash_by_category": {k: round(v, 2) for k, v in buy_cash.most_common()},
        "buy_cash_total": round(sum(buy_cash.values()), 2),
        "harvest_units_by_product": dict(harvest_units.most_common()),
        "exec_counts": counts,
        "daily": {str(d): v for d, v in sorted(daily.items())},
    }


def main():
    paths = [Path(p) for p in sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))]
    results = []
    for p in paths:
        game = json.loads(p.read_text())
        names = [a["Name"] for a in game["info"]["Agents"]]
        r = analyze(p, names.index("Rajusah"))
        r["outcome"] = "L" if r["episode_id"] in LOSSES else "W"
        results.append(r)
        print(f"  {r['episode_id']} {r['outcome']} mism={r['cash_mismatches']} "
              f"sell=${r['sell_cash_total']:,.0f} reward=${r['reward']:,.0f}", flush=True)
    HERE.mkdir(parents=True, exist_ok=True)
    (HERE / "loss_analysis.json").write_text(json.dumps(results, indent=2) + "\n")

    # V83 framing: throughput per unit of asset during days 12-23.
    print()
    print("=" * 118)
    print("V95 STEP 1: throughput per unit of asset, days 12-23 (V83 elite separator)")
    print("=" * 118)
    print(f"{'epid':>10} {'out':>3} {'d12-23 sell$':>13} {'d12-23 harvestU':>16} {'d12 animals':>12} "
          f"{'d12 crops':>10} {'sell/animal':>12} {'harvestU/crop':>14} {'reward':>9}")
    agg = {"L": [], "W": []}
    for r in results:
        d = r["daily"]
        sell1223 = sum(d[str(x)]["sell_cash"] for x in range(12, 24) if str(x) in d)
        harv1223 = sum(d[str(x)]["harvest_units"] for x in range(12, 24) if str(x) in d)
        d12 = d.get("12", {})
        animals = sum(d12.get("animals", {}).values())
        crops = sum(d12.get("crops", {}).values())
        spa = sell1223 / max(1, animals)
        huc = harv1223 / max(1, crops)
        print(f"{r['episode_id']:>10} {r['outcome']:>3} {sell1223:>13,.0f} {harv1223:>16} "
              f"{animals:>12} {crops:>10} {spa:>12,.0f} {huc:>14.1f} {r['reward']:>9,.0f}")
        agg[r["outcome"]].append((sell1223, harv1223, animals, crops, spa, huc))
    for k in ("W", "L"):
        if agg[k]:
            n = len(agg[k])
            print(f"  {k} mean: sell=${sum(x[0] for x in agg[k])/n:,.0f} "
                  f"harvestU={sum(x[1] for x in agg[k])/n:.0f} "
                  f"sell/animal={sum(x[4] for x in agg[k])/n:,.0f} "
                  f"harvestU/crop={sum(x[5] for x in agg[k])/n:.1f}")

    print()
    print("=" * 118)
    print("EXECUTION COUNTS (whole game, Rajusah)")
    print("=" * 118)
    print(f"{'epid':>10} {'out':>3} {'water':>7} {'care':>7} {'feed':>6} {'moves':>7} {'work':>7} "
          f"{'pass':>7} {'colFert':>8}")
    for r in results:
        e = r["exec_counts"]
        print(f"{r['episode_id']:>10} {r['outcome']:>3} {e['water']:>7} {e['care']:>7} {e['feed']:>6} "
              f"{e['moves']:>7} {e['work_total']:>7} {e['pass']:>7} {e['collect_fertilizer']:>8}")


if __name__ == "__main__":
    main()

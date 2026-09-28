#!/usr/bin/env python3
"""V96 step 1: audit the days 0-11 asset-to-cash deficit of the V92 lineage.

Step 0 rederived the shed constraint and overturned V94's premise: carried is 0 at
every daily snapshot, and the shed is only saturated LATE (mean occupancy 12.8 of 100
in days 0-11, 67.5 in days 12-23, 94.3 in days 24-29). So the opening window has ~87
units of shed headroom, and the binding constraint there is NOT storage.

docs/V75_ELITE_CASHFLOW.md is a settlement-exact audit (0 mismatches, max cash error
$0.00) of 6 public elite winners against 4 saved V70 trajectories, and V70 is this
same V50 lineage. It reports a large opening deficit. It is a purposive,
outcome-conditioned sample and is treated here as a HYPOTHESIS to test, not as causal
proof. The question this script answers is narrower and measurable: what does the V92
lineage ACTUALLY do in days 0-11, day by day, and where does it diverge from those
elite medians?

For each of the 14 official replays it records, at every day boundary, the Rajusah
seat's: cash, land count, animal census by species, crop census by species, and the
accepted sale cash by product for that day. Accepted cash comes from replaying the
recorded actions through the pinned engine and counting committed SELL units, never
queued market slots.

The deficit that matters is TIMING, not totals: a product that sells in days 6-11
compounds through the whole season (cash funds feed, seeds, animals), while the same
product sold in days 24-29 is a terminal liquidation. So the audit reports the day
distribution of accepted sale cash by product, and compares the opening window
against the elite medians V75 reports.

Run from repo root:
    .venv/bin/python experiments/v96_route/audit_opening.py
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

# Elite medians from docs/V75_ELITE_CASHFLOW.md (6 public winners). Hypothesis only.
ELITE = {
    "day3_animals": 7, "day6_animals": 12.5, "day9_animals": 18,
    "day6_strawberry_tiles": 24, "day9_strawberry_tiles": 31.5,
    "day3_cash": 28, "day6_cash": 33, "day9_lands": 3,
    "melon_sales_d6_11": 11236, "product_sales_d6_11": 26430,
    "animal_buy_d0_5": 3900,
}


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
    identity: dict = {}
    cash_mismatches = [0, 0]

    daily_sell_cash = defaultdict(lambda: Counter())
    daily_sell_units = defaultdict(lambda: Counter())
    daily_buy_cash = defaultdict(lambda: Counter())
    cur_day = [0]

    orig_commit = engine._commit_unit

    def tracked_commit(op, item, price, farm, private, market, shed_capacity=SHED_CAPACITY):
        who = identity.get(id(private))
        ok = orig_commit(op, item, price, farm, private, market, shed_capacity)
        if ok and who == seat:
            if op == "SELL":
                daily_sell_cash[cur_day[0]][item] += float(price)
                daily_sell_units[cur_day[0]][item] += 1
            elif op in ("BUY_PRODUCT", "BUY_SEED", "BUY_ANIMAL", "BUY_LAND"):
                daily_buy_cash[cur_day[0]][f"{op} {item}"] += float(price)
        return ok

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
        engine._commit_unit = orig_commit

    # Day-boundary asset census straight from the recorded observations.
    timeline = []
    for frame in range(0, len(steps), TURNS_PER_DAY):
        obs = steps[frame][seat]["observation"]
        day = int(obs.get("day", 0))
        farm = obs["farms"][seat]
        animals = Counter()
        crops = Counter()
        for row in farm.get("tiles", []):
            for t in row:
                if not isinstance(t, dict):
                    continue
                if t.get("animal"):
                    animals[t["animal"]] += 1
                elif t.get("kind") == "PLANT" and t.get("crop"):
                    crops[t["crop"]] += 1
        priv = obs.get("private") or {}
        timeline.append({
            "day": day,
            "cash": float(farm["money"]),
            "lands": len(farm.get("unlocked_quadrants", [])),
            "animals": dict(animals),
            "animal_total": sum(animals.values()),
            "crops": dict(crops),
            "shed": sum(int(v or 0) for v in (priv.get("shed") or {}).values()),
        })

    return {
        "episode_id": game["info"]["EpisodeId"],
        "outcome": "L" if game["info"]["EpisodeId"] in LOSSES else "W",
        "cash_mismatches": sum(cash_mismatches),
        "timeline": timeline,
        "daily_sell_cash": {str(d): {k: round(v, 2) for k, v in c.items()} for d, c in sorted(daily_sell_cash.items())},
        "daily_sell_units": {str(d): dict(c) for d, c in sorted(daily_sell_units.items())},
        "daily_buy_cash": {str(d): {k: round(v, 2) for k, v in c.items()} for d, c in sorted(daily_buy_cash.items())},
    }


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    paths = [Path(p) for p in sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))]
    results = [analyze(p) for p in paths]
    (HERE / "opening_audit.json").write_text(json.dumps(results, indent=2) + "\n")

    def at(r, day):
        for x in r["timeline"]:
            if x["day"] == day:
                return x
        return {}

    print("=" * 116)
    print("V96 STEP 1: V92 LINEAGE OPENING AUDIT (14 official replays, Rajusah)")
    print("=" * 116)
    print(f"{'epid':>10} {'out':>3} {'d3 cash':>8} {'d6 cash':>8} {'d9 cash':>8} {'d3 anim':>8} "
          f"{'d6 anim':>8} {'d9 anim':>8} {'d6 straw':>9} {'d9 lands':>9}")
    for r in results:
        d3, d6, d9 = at(r, 3), at(r, 6), at(r, 9)
        print(f"{r['episode_id']:>10} {r['outcome']:>3} {d3.get('cash', 0):>8,.0f} {d6.get('cash', 0):>8,.0f} "
              f"{d9.get('cash', 0):>8,.0f} {d3.get('animal_total', 0):>8} {d6.get('animal_total', 0):>8} "
              f"{d9.get('animal_total', 0):>8} {d6.get('crops', {}).get('STRAWBERRY', 0):>9} "
              f"{d9.get('lands', 0):>9}")

    n = len(results)
    avg = lambda f: sum(f(r) for r in results) / n
    print()
    print("  MEAN OF THE 14 GAMES  vs  V75 ELITE MEDIANS (hypothesis, purposive sample of 6)")
    rows = [
        ("day 3 animals", avg(lambda r: at(r, 3).get("animal_total", 0)), ELITE["day3_animals"]),
        ("day 6 animals", avg(lambda r: at(r, 6).get("animal_total", 0)), ELITE["day6_animals"]),
        ("day 9 animals", avg(lambda r: at(r, 9).get("animal_total", 0)), ELITE["day9_animals"]),
        ("day 6 strawberry tiles", avg(lambda r: at(r, 6).get("crops", {}).get("STRAWBERRY", 0)), ELITE["day6_strawberry_tiles"]),
        ("day 9 strawberry tiles", avg(lambda r: at(r, 9).get("crops", {}).get("STRAWBERRY", 0)), ELITE["day9_strawberry_tiles"]),
        ("day 3 cash", avg(lambda r: at(r, 3).get("cash", 0)), ELITE["day3_cash"]),
        ("day 6 cash", avg(lambda r: at(r, 6).get("cash", 0)), ELITE["day6_cash"]),
        ("day 9 lands", avg(lambda r: at(r, 9).get("lands", 0)), ELITE["day9_lands"]),
    ]
    print(f"    {'metric':>24} {'V92 mean':>10} {'elite med':>10} {'gap':>10}")
    for name, ours, elite in rows:
        print(f"    {name:>24} {ours:>10.1f} {elite:>10.1f} {ours - elite:>+10.1f}")

    # Sale cash by product across the two windows that matter.
    def window(r, lo, hi, key="daily_sell_cash"):
        tot = Counter()
        for d, c in r[key].items():
            if lo <= int(d) <= hi:
                for k, v in c.items():
                    tot[k] += v
        return tot

    print()
    print("  ACCEPTED SALE CASH BY PRODUCT AND WINDOW (mean per game)")
    print(f"    {'product':>12} {'d0-5':>10} {'d6-11':>10} {'d12-23':>10} {'d24-29':>10} {'total':>10}")
    for item in ("MELON", "STRAWBERRY", "WOOL", "MILK", "WHEAT", "FERTILIZER", "EGG", "CARROT"):
        a = sum(window(r, 0, 5).get(item, 0) for r in results) / n
        b = sum(window(r, 6, 11).get(item, 0) for r in results) / n
        c = sum(window(r, 12, 23).get(item, 0) for r in results) / n
        d = sum(window(r, 24, 29).get(item, 0) for r in results) / n
        if a + b + c + d == 0:
            continue
        print(f"    {item:>12} {a:>10,.0f} {b:>10,.0f} {c:>10,.0f} {d:>10,.0f} {a+b+c+d:>10,.0f}")

    print()
    print("  THE HEADLINE GAP CHECK (V75 elite medians, days 6-11):")
    melon611 = sum(window(r, 6, 11).get("MELON", 0) for r in results) / n
    prod611 = sum(sum(v for k, v in window(r, 6, 11).items() if not k.startswith("BUY")) for r in results) / n
    print(f"    melon accepted sale cash d6-11 : V92 {melon611:>9,.0f}   elite {ELITE['melon_sales_d6_11']:>9,.0f}")
    print(f"    all product sale cash d6-11    : V92 {prod611:>9,.0f}   elite {ELITE['product_sales_d6_11']:>9,.0f}")

    print()
    print("  BUY CASH in the opening (mean per game), days 0-5:")
    buys = Counter()
    for r in results:
        for k, v in window(r, 0, 5, "daily_buy_cash").items():
            buys[k] += v
    for k, v in sorted(buys.items(), key=lambda kv: -kv[1]):
        print(f"    {k:>22}: {v/n:>9,.0f}")
    print(f"    {'ANIMAL TOTAL d0-5':>22}: "
          f"{sum(v for k, v in buys.items() if k.startswith('BUY_ANIMAL'))/n:>9,.0f}   "
          f"elite {ELITE['animal_buy_d0_5']:>9,.0f}")


if __name__ == "__main__":
    main()

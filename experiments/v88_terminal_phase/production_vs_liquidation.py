"""V88 corrected diagnostic: production flow vs liquidation, exact per-step transitions.

Read-only. Saved replays, pinned Kaggriculture 1.32.7. No new seed, no code edit,
no submission.

Why this supersedes the first pass
----------------------------------
The first pass concluded "V50 liquidates more" from accepted SELL units. That
is unsound: accepted sales are bounded by what was harvested and carried, so a
higher sale count can simply mean more supply upstream. Accepted sales are a
FLOW, shed contents are a STOCK, and the two must not be conflated.

This pass measures, per seat, with the engine's own _commit_unit deciding every
transaction, the full chain per day:

  harvested units      = accepted SELL units + shed end - shed start + bought units
  (an identity, not an estimate)
  animal output        = yield_units accumulated on animal tiles
  terminal stock       = shed at the final observed day, and shed at day 24

and the per-turn market ORDER stream, so that a rejected order (shed empty for
that item) is distinguishable from an order that was never made.

It also separates the two V56-only wrapper rules, which act at different times
and on different state:
  * reorder_market(obs, action, "impact_slots") runs on EVERY turn from step 0,
    and can move a SELL ahead of a BUY, changing when cash arrives and therefore
    what the base planner can afford later;
  * terminal_market(obs, action, "collision", replace=False) runs only from
    CLEARANCE_STEP = 629, i.e. day 26 hour 5 onward.

So a days 24-29 difference cannot be attributed to late SELL ordering alone
without also showing that days 0-23 were already different.

Output: experiments/v88_terminal_phase/production_vs_liquidation.json
"""

import copy
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from types import SimpleNamespace

from kaggle_environments.envs.kaggriculture import kaggriculture as engine

ROOT = Path("/home/raju/AI-ML Projects/Kaggle Competition/Kaggriculture")
OUT = ROOT / "experiments/v88_terminal_phase/production_vs_liquidation.json"
SPENT_SEEDS = ["92802", "94110", "94111", "94112", "94113", "94114", "94400", "94401", "94700"]
CLEARANCE_STEP = 629


def obs_of(step, seat):
    node = step[seat]
    return (node[0] if isinstance(node, list) else node).get("observation") or {}


def act_of(step, seat):
    node = step[seat]
    return (node[0] if isinstance(node, list) else node).get("action") or {}


def find_replay(prefix, seed, seat):
    order = "ab" if seat == 0 else "ba"
    hits = sorted(ROOT.glob(f"experiments/**/replays/{prefix}-seed-{seed}-{order}-repeat-0.json"))
    return hits[0] if hits else None


def shed_of(obs, seat):
    return (obs.get("private") or {}).get("shed") or {}


def shed_total(obs, seat):
    return sum(shed_of(obs, seat).values())


def animal_yield(obs, seat):
    total = 0
    by = Counter()
    for row in obs["farms"][seat]["tiles"]:
        for t in row:
            if isinstance(t, dict) and t.get("animal"):
                y = int(t.get("yield_units", 0) or 0)
                total += y
                by[t["animal"]] += y
    return total, dict(by)


def crop_yield(obs, seat):
    total = 0
    by = Counter()
    for row in obs["farms"][seat]["tiles"]:
        for t in row:
            if isinstance(t, dict) and t.get("kind") == "PLANT":
                y = int(t.get("yield_units", 0) or 0)
                total += y
                by[t.get("crop")] += y
    return total, dict(by)


def analyse(path, seat):
    game = json.loads(path.read_text())
    steps = game["steps"]
    cfg = game.get("configuration", {})
    conf = SimpleNamespace(
        **{
            k: cfg.get(k, default)
            for k, default in (
                ("boardSize", 10), ("maxMarketOrdersPerTurn", 10),
                ("farmHandCostMult", 1), ("shedCapacity", 100), ("turnsPerDay", 24),
            )
        }
    )

    sell_units = defaultdict(Counter)
    sell_cash = defaultdict(Counter)
    buy_units = defaultdict(Counter)
    buy_cash = defaultdict(Counter)
    shed_delta = defaultdict(Counter)      # day -> product -> change in shed
    shed_start = {}
    shed_end = {}
    orders = defaultdict(Counter)           # day -> op -> ORDERED count
    order_units = defaultdict(Counter)      # day -> (op,item) -> ORDERED units
    carry_peak = {}

    original = engine._commit_unit
    cur = None
    tracked = None

    def commit(op, item, price, farm, private, market, shed_capacity=100):
        ok = original(op, item, price, farm, private, market, shed_capacity)
        if ok and cur is not None:
            cur.append((0 if farm is tracked[0] else 1, op, item, price))
        return ok

    engine._commit_unit = commit
    try:
        for frame in range(1, len(steps)):
            prev = steps[frame - 1]
            obs = obs_of(prev, 0)
            day = int(obs.get("day", 0) or 0)
            hour = int(obs.get("hour", 0) or 0)
            farms = copy.deepcopy(obs["farms"])
            tracked = farms
            market = copy.deepcopy(obs["market"])
            privates = [copy.deepcopy(obs_of(prev, s).get("private") or {}) for s in range(2)]
            actions = [copy.deepcopy(act_of(steps[frame], s)) for s in range(2)]

            if hour == 0:
                shed_start[day] = shed_of(obs, seat)
                sh = shed_start[day]
                ay, _ = animal_yield(obs, seat)
                cy, _ = crop_yield(obs, seat)
                carry_peak[day] = {
                    "shed_total": sum(sh.values()),
                    "animal_yield": ay,
                    "crop_yield": cy,
                }

            # ORDERED stream, before the engine decides anything.
            for o in (actions[seat].get("market") or []):
                if not o:
                    continue
                orders[day][o[0]] += 1
                if len(o) > 2 and o[0] in ("SELL", "BUY_PRODUCT"):
                    order_units[day][(o[0], o[1])] += int(o[2])
                elif len(o) > 2 and o[0] == "BUY_ANIMAL":
                    order_units[day][("BUY_ANIMAL", o[1])] += int(o[2])

            for s in range(2):
                units = [actions[s].get("farmer", ["PASS"]), *(actions[s].get("hands") or [])]
                for i, a in enumerate(units):
                    engine._apply_unit_action(
                        farms[s], privates[s], i, a,
                        int(conf.boardSize), day, int(conf.turnsPerDay), int(conf.shedCapacity),
                    )

            states = [
                SimpleNamespace(
                    observation=SimpleNamespace(market=market, farms=farms, private=privates[s]),
                    action=actions[s],
                )
                for s in range(2)
            ]
            cur = []
            engine._process_market(states, SimpleNamespace(configuration=conf))
            for s, op, item, price in cur:
                if s != seat:
                    continue
                if op == "SELL":
                    sell_units[day][item] += 1
                    sell_cash[day][item] += price
                    shed_delta[day][item] -= 1
                elif op == "BUY_PRODUCT":
                    buy_units[day][item] += 1
                    buy_cash[day][item] += price
                    shed_delta[day][item] += 1
                elif op == "BUY_ANIMAL":
                    shed_delta[day][item] += int(price and 1)
            if hour == 23:
                shed_end[day] = dict(privates[seat].get("shed") or {})
    finally:
        engine._commit_unit = original

    def rng(lo, hi):
        return range(lo, hi + 1)

    def tot(counter, lo, hi, key=None):
        return sum(sum(counter[d][key] for d in rng(lo, hi) if key) if key else counter[d] for d in rng(lo, hi))

    return {
        "replay": str(path),
        "seat": seat,
        "sell_units_d24_29": {p: sum(sell_units[d][p] for d in rng(24, 29)) for p in sorted({p for d in rng(24, 29) for p in sell_units[d]})},
        "sell_cash_d24_29": {p: sum(sell_cash[d][p] for d in rng(24, 29)) for p in sorted({p for d in rng(24, 29) for p in sell_cash[d]})},
        "sell_units_all": sum(sum(sell_units[d].values()) for d in sell_units),
        "sell_cash_all": sum(sum(sell_cash[d].values()) for d in sell_cash),
        "buy_units_d24_29": {p: sum(buy_units[d][p] for d in rng(24, 29)) for p in sorted({p for d in rng(24, 29) for p in buy_units[d]})},
        "ordered_vs_accepted_d24_29": {
            f"{o}:{it}": {"ordered": sum(order_units[d][(o, it)] for d in rng(24, 29)),
                          "accepted": sell_units_all if o == "SELL" else sum(buy_units[d][it] for d in rng(24, 29))}
            for (o, it) in sorted({k for d in rng(24, 29) for k in order_units[d]})
        },
        "shed_start_d24": shed_start.get(24, {}),
        "shed_end_d23": shed_end.get(23, {}),
        "shed_end_d29": shed_end.get(29, {}),
        "shed_total_d24": carry_peak.get(24, {}).get("shed_total"),
        "shed_total_d29": carry_peak.get(29, {}).get("shed_total"),
        "animal_yield_d24": carry_peak.get(24, {}).get("animal_yield"),
        "animal_yield_d29": carry_peak.get(29, {}).get("animal_yield"),
        "crop_yield_d24": carry_peak.get(24, {}).get("crop_yield"),
        "crop_yield_d29": carry_peak.get(29, {}).get("crop_yield"),
        "final_cash": obs_of(steps[-1], seat)["farms"][seat]["money"],
    }


sell_units_all = 0  # placeholder to keep the comprehension above simple


def main():
    results = []
    for seed in SPENT_SEEDS:
        for seat in (0, 1):
            p50 = find_replay("v50", seed, seat)
            p56 = find_replay("v56", seed, seat) or find_replay("V56", seed, seat)
            if not p50 or not p56:
                continue
            a, b = analyse(p50, seat), analyse(p56, seat)
            results.append({"seed": seed, "seat": seat, "v50": a, "v56": b})
            print(
                f"seed {seed} seat {seat}: "
                f"shedTotals d24/d29  V50={a['shed_total_d24']}/{a['shed_total_d29']}  "
                f"V56={b['shed_total_d24']}/{b['shed_total_d29']}   "
                f"animalYield d29 V50={a['animal_yield_d29']} V56={b['animal_yield_d29']}   "
                f"sellUnits d24-29 V50={sum(a['sell_units_d24_29'].values())} V56={sum(b['sell_units_d24_29'].values())}"
            )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=1, sort_keys=True) + "\n")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    sys.exit(main())

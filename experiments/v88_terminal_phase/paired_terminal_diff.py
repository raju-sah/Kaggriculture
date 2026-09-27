"""V88: paired V50 vs V56 terminal-phase diagnostic (days 24-29).

Read-only. Uses saved replays and the pinned Kaggriculture 1.32.7 engine. No new
seed is spent, no agent code is edited, nothing is submitted.

Question
--------
V87 showed the two frozen agents are identical in days 0-5 and diverge almost
entirely in days 24-29 (seed 94400: V50 +3,517 of a +4,475 total edge). What is
the causal difference, at action, market, inventory and cash level?

Method
------
For every spent seed where both agents have saved replays in both seat orders,
reconstruct each seat's accepted market activity through the pinned engine and
compare, per day and per product:
  * accepted SELL units and accepted SELL proceeds,
  * accepted BUY_PRODUCT units and cost,
  * accepted BUY_SEED / BUY_ANIMAL,
  * shed inventory carried into each day,
  * worker turns by action type,
  * final cash and the per-phase decomposition.

Structural hypothesis under test: the two wrappers differ in exactly two ways.
V50's agent() calls only _PLANNER then apply_overlay. V56's agent() additionally
calls reorder_market(obs, action, mode="impact_slots") on every turn, and
terminal_market(obs, action, "collision", replace=False) from CLEARANCE_STEP=629.
If the days 24-29 gap comes from those two calls, the divergence must be visible
as a difference in accepted sale ordering, accepted proceeds per turn, or both,
starting either immediately (impact_slots, all 720 turns) or at step 629.

Output: experiments/v88_terminal_phase/paired_terminal_diff.json
"""

import copy
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from types import SimpleNamespace

from kaggle_environments.envs.kaggriculture import kaggriculture as engine

ROOT = Path("/home/raju/AI-ML Projects/Kaggle Competition/Kaggriculture")
OUT = ROOT / "experiments/v88_terminal_phase/paired_terminal_diff.json"

SPENT_SEEDS = ["92802", "94110", "94111", "94112", "94113", "94114", "94400", "94401", "94700"]


def obs_of(step, seat):
    node = step[seat]
    if isinstance(node, list):
        node = node[0]
    return node.get("observation") or {}


def act_of(step, seat):
    node = step[seat]
    if isinstance(node, list):
        node = node[0]
    return node.get("action") or {}


def find_replay(prefix, seed, seat):
    order = f"{'ab' if seat == 0 else 'ba'}"
    hits = sorted(ROOT.glob(f"experiments/**/replays/{prefix}-seed-{seed}-{order}-repeat-0.json"))
    return hits[0] if hits else None


def analyse(path, seat):
    game = json.loads(path.read_text())
    steps = game["steps"]
    cfg = game.get("configuration", {})
    conf = SimpleNamespace(
        **{
            k: cfg.get(k, default)
            for k, default in (
                ("boardSize", 10),
                ("maxMarketOrdersPerTurn", 10),
                ("farmHandCostMult", 1),
                ("shedCapacity", 100),
                ("turnsPerDay", 24),
            )
        }
    )

    proceeds = defaultdict(Counter)   # day -> product -> accepted SELL $
    sell_units = defaultdict(Counter)
    buy_units = defaultdict(Counter)
    buy_cost = defaultdict(Counter)
    shed_by_day = defaultdict(Counter)
    turns = defaultdict(Counter)
    shed_total_by_day = {}

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
                shed = privates[seat].get("shed") or {}
                shed_by_day[day].update({k: v for k, v in shed.items() if v})
                shed_total_by_day[day] = sum(shed.values())

            for u in [actions[seat].get("farmer", ["PASS"]), *(actions[seat].get("hands") or [])]:
                if u:
                    turns[day][u[0]] += 1

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
                    proceeds[day][item] += price
                    sell_units[day][item] += 1
                elif op == "BUY_PRODUCT":
                    buy_units[day][item] += 1
                    buy_cost[day][item] += price
    finally:
        engine._commit_unit = original

    def phase(lo, hi):
        return sum(sum(proceeds[d].values()) for d in proceeds if lo <= d <= hi)

    return {
        "replay": str(path),
        "seat": seat,
        "phase_sell_proceeds": {
            "d0_5": phase(0, 5),
            "d6_11": phase(6, 11),
            "d12_23": phase(12, 23),
            "d24_29": phase(24, 29),
        },
        "d24_29_proceeds_by_product": {p: sum(proceeds[d][p] for d in proceeds if 24 <= d <= 29) for p in sorted({p for d in range(24, 30) for p in proceeds[d]})},
        "d24_29_sell_units": {p: sum(sell_units[d][p] for d in sell_units if 24 <= d <= 29) for p in sorted({p for d in range(24, 30) for p in sell_units[d]})},
        "d24_29_buy_product": {p: sum(buy_units[d][p] for d in buy_units if 24 <= d <= 29) for p in sorted({p for d in range(24, 30) for p in buy_units[d]})},
        "d24_29_turns": dict(sum((turns[d] for d in range(24, 30)), Counter())),
        "shed_total_by_day": {str(d): v for d, v in sorted(shed_total_by_day.items())},
        "final_cash": obs_of(steps[-1], seat)["farms"][seat]["money"],
    }


def main():
    results = []
    for seed in SPENT_SEEDS:
        for seat in (0, 1):
            r50 = find_replay("v50", seed, seat)
            r56 = find_replay("v56", seed, seat) or find_replay("V56", seed, seat)
            if not r50 or not r56:
                continue
            a = analyse(r50, seat)
            b = analyse(r56, seat)
            d = b["phase_sell_proceeds"]["d24_29"] - a["phase_sell_proceeds"]["d24_29"]
            results.append(
                {
                    "seed": seed,
                    "seat": seat,
                    "v50": a,
                    "v56": b,
                    "d24_29_delta_v56_minus_v50": d,
                    "final_delta_v56_minus_v50": b["final_cash"] - a["final_cash"],
                }
            )
            print(
                f"seed {seed} seat {seat}: d24-29 proceeds V50=${a['phase_sell_proceeds']['d24_29']:8.0f} "
                f"V56=${b['phase_sell_proceeds']['d24_29']:8.0f}  delta={d:+9.0f}   "
                f"final delta={b['final_cash'] - a['final_cash']:+9.0f}"
            )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=1, sort_keys=True) + "\n")
    if results:
        mean = sum(r["d24_29_delta_v56_minus_v50"] for r in results) / len(results)
        print(f"\nmean d24-29 delta (V56 - V50) across {len(results)} paired games: {mean:+.0f}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    sys.exit(main())

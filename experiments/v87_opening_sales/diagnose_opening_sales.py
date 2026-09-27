"""V87 opening-sale diagnostic: production shortfall vs failed SELL orders.

Read-only. Replays recorded actions through the pinned Kaggriculture 1.32.7
engine and separates, for every SELL order, whether the unit was actually
available to sell. Nothing is re-simulated or invented: the engine's own
_commit_unit decides each unit, and this script only records the outcome.

Question: V56 accepts 3,035 in accepted sales over days 0-5 while elite winners
accept 5,319 and elite losers 3,695. Is the deficit because V56 produces less,
or because V56 tries to sell and fails?

Method, per seat:
  * replay every frame's recorded action through engine._process_market with the
    engine's own _commit_unit, exactly as experiments/v75_elite_cashflow/
    reconstruct.py does, and record (seat, op, item, price) for each *accepted*
    unit commit;
  * separately count the SELL units the agent *ordered* per product per day;
  * ordered minus accepted is the rejection count, which is production or
    inventory shortage, not a failed order;
  * a SELL that is accepted but late (after day 5) is a timing effect, not a
    production effect.

Output: experiments/v87_opening_sales/opening_sale_diagnostic.json
"""

import copy
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from types import SimpleNamespace

from kaggle_environments.envs.kaggriculture import kaggriculture as engine

ROOT = Path("/home/raju/AI-ML Projects/Kaggle Competition/Kaggriculture")
OUT = ROOT / "experiments/v87_opening_sales/opening_sale_diagnostic.json"

# Same-seed V50 / V56 pairs, seat 0, from the frozen saved replays.
PAIRS = [
    ("94400", ROOT / "experiments/runs/v58_validation_original_route/baseline/replays/v56-seed-94400-ab-repeat-0.json", 0),
    ("94401", ROOT / "experiments/runs/v58_validation_original_route/baseline/replays/v56-seed-94401-ab-repeat-0.json", 0),
    ("94110", None, 0),
    ("94111", None, 0),
    ("94112", None, 0),
    ("94113", None, 0),
    ("94114", None, 0),
]


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


def analyse(replay_path, seat):
    """Return ordered vs accepted sales by product and day for one seat."""
    game = json.loads(replay_path.read_text())
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

    ordered = defaultdict(Counter)      # day -> product -> units ordered
    accepted = defaultdict(Counter)     # day -> product -> proceeds accepted
    accepted_units = defaultdict(Counter)
    shed_snapshot = defaultdict(Counter)  # day -> product -> shed stock at day start
    unfed = Counter()

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
            farms = copy.deepcopy(obs["farms"])
            tracked = farms
            market = copy.deepcopy(obs["market"])
            privates = []
            for s in range(2):
                pv = obs_of(prev, s).get("private") or {}
                privates.append(copy.deepcopy(pv))
            actions = [copy.deepcopy(act_of(steps[frame], s)) for s in range(2)]

            # Record what the candidate seat ORDERED, and the shed it had.
            if day == 0 or obs.get("hour") == 0:
                shed_snapshot[day][":".join(f"{k}={v}" for k, v in sorted(privates[seat].get("shed", {}).items()) if v)] += 1
            for order in (actions[seat].get("market") or []):
                if order and order[0] == "SELL" and len(order) > 2:
                    ordered[day][order[1]] += int(order[2])

            for s in range(2):
                units = [actions[s].get("farmer", ["PASS"]), *(actions[s].get("hands") or [])]
                for i, a in enumerate(units):
                    engine._apply_unit_action(
                        farms[s], privates[s], i, a,
                        int(conf.boardSize), day, int(conf.turnsPerDay), int(conf.shedCapacity),
                    )
            for s in range(2):
                for row in farms[s]["tiles"]:
                    for t in row:
                        if isinstance(t, dict) and t.get("animal") and t.get("consecutive_unfed", 0) >= 1:
                            unfed[(s, day)] += 1

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
                if s != seat or op != "SELL":
                    continue
                accepted[day][item] += price
                accepted_units[day][item] += 1
    finally:
        engine._commit_unit = original

    early_ordered = sum(sum(ordered[d].values()) for d in ordered if d <= 5)
    early_accepted_units = sum(sum(accepted_units[d].values()) for d in accepted_units if d <= 5)
    early_proceeds = sum(sum(accepted[d].values()) for d in accepted if d <= 5)
    return {
        "replay": str(replay_path),
        "seat": seat,
        "ordered_by_day": {str(d): dict(ordered[d]) for d in sorted(ordered)},
        "accepted_by_day": {str(d): dict(accepted[d]) for d in sorted(accepted)},
        "accepted_units_by_day": {str(d): dict(accepted_units[d]) for d in sorted(accepted_units)},
        "early_0_5_ordered_units": early_ordered,
        "early_0_5_accepted_units": early_accepted_units,
        "early_0_5_rejected_units": early_ordered - early_accepted_units,
        "early_0_5_proceeds": early_proceeds,
        "early_0_5_rejection_rate": (
            (early_ordered - early_accepted_units) / early_ordered if early_ordered else 0.0
        ),
        "total_proceeds": sum(sum(accepted[d].values()) for d in accepted),
        "final_cash": obs_of(steps[-1], seat)["farms"][seat]["money"],
    }


def main():
    results = []
    for seed, path, seat in PAIRS:
        if path is None or not path.exists():
            continue
        r = analyse(path, seat)
        r["seed"] = seed
        results.append(r)
        print(
            f"seed {seed} seat {seat}: ordered(d0-5)={r['early_0_5_ordered_units']} "
            f"accepted={r['early_0_5_accepted_units']} "
            f"rejected={r['early_0_5_rejected_units']} "
            f"({100 * r['early_0_5_rejection_rate']:.1f}%) "
            f"proceeds=${r['early_0_5_proceeds']:.0f} final=${r['final_cash']:.0f}"
        )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=1, sort_keys=True) + "\n")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    sys.exit(main())

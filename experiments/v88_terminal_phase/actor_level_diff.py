"""V88 actor-level diagnostic: V50 versus V56 in the SAME games, by agent SHA.

Read-only. Reconstructs provenance from game records and agent SHA-256 values,
never from filename prefixes. Saved replays, pinned Kaggriculture 1.32.7. No new
seed, no agent code edit, no submission.

Correction being applied
------------------------
The first V88 pass compared files matched by filename prefix and produced a
"days 24-29" delta. That was invalid: in this project a replay is named for the
OPPOSITION, so `v50-seed-X-ab.json` under a v57/v80/v81 run is that candidate
playing AGAINST v50. The delta paired a v50 opponent seat against a v56 opponent
seat from different games with different opponents. All of it is discarded.

This pass uses only games whose two recorded agent SHA-256 values are exactly
{experiments/v50_agent.py, agents/v56_agent.py}. In those games seat 0 and seat 1
are the two agents, so the same seed, the same market and the same opponent
conditions apply to both, and any difference is attributable to the agent.

Measured per seat, per phase, with the engine's own _commit_unit deciding every
transaction:
  accepted SELL units and proceeds, accepted buys, ordered-vs-accepted,
  shed stock entering each day (a stock, not a flow), harvest/carry/animal output
  (yield_units accumulated on tiles), and worker turns by action type.

Output: experiments/v88_terminal_phase/actor_level_diff.json
"""

import copy
import glob
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from types import SimpleNamespace

from kaggle_environments.envs.kaggriculture import kaggriculture as engine

ROOT = Path("/home/raju/AI-ML Projects/Kaggle Competition/Kaggriculture")
OUT = ROOT / "experiments/v88_terminal_phase/actor_level_diff.json"
V50 = hashlib.sha256((ROOT / "experiments/v50_agent.py").read_bytes()).hexdigest()
V56 = hashlib.sha256((ROOT / "agents/v56_agent.py").read_bytes()).hexdigest()


def obs_of(step, seat):
    n = step[seat]
    return (n[0] if isinstance(n, list) else n).get("observation") or {}


def act_of(step, seat):
    n = step[seat]
    return (n[0] if isinstance(n, list) else n).get("action") or {}


def head_to_head():
    """Direct V50-vs-V56 games that have a saved replay on disk."""
    found = {}
    for path in glob.glob(str(ROOT / "experiments/**/games.jsonl"), recursive=True):
        for line in open(path):
            try:
                rec = json.loads(line)
            except Exception:
                continue
            ags = rec.get("agents")
            if not isinstance(ags, list) or len(ags) != 2:
                continue
            seats = [a.get("sha256") for a in ags if isinstance(a, dict)]
            if len(seats) != 2 or V50 not in seats or V56 not in seats:
                continue
            gid = rec.get("game_id")
            hits = glob.glob(str(ROOT / f"experiments/**/replays/{gid}.json"), recursive=True)
            if not hits:
                continue
            found[gid] = {
                "seed": rec.get("seed"),
                "v50_seat": seats.index(V50),
                "coins": rec.get("final_coins"),
                "replay": hits[0],
            }
    return found


def shed(obs, seat):
    return (obs.get("private") or {}).get("shed") or {}


def yields(obs, seat):
    animal = Counter()
    crop = Counter()
    for row in obs["farms"][seat]["tiles"]:
        for t in row:
            if not isinstance(t, dict):
                continue
            y = int(t.get("yield_units", 0) or 0)
            if t.get("animal"):
                animal[t["animal"]] += y
            elif t.get("kind") == "PLANT":
                crop[t.get("crop")] += y
    return sum(animal.values()), sum(crop.values())


def analyse(path, seat):
    game = json.loads(Path(path).read_text())
    steps = game["steps"]
    cfg = game.get("configuration", {})
    conf = SimpleNamespace(**{k: cfg.get(k, d) for k, d in (
        ("boardSize", 10), ("maxMarketOrdersPerTurn", 10), ("farmHandCostMult", 1),
        ("shedCapacity", 100), ("turnsPerDay", 24))})

    sell_u = defaultdict(Counter)
    sell_c = defaultdict(Counter)
    buy_u = defaultdict(Counter)
    buy_c = defaultdict(Counter)
    ordered_u = defaultdict(Counter)
    shed_enter = defaultdict(int)
    animal_yield = defaultdict(int)
    crop_yield = defaultdict(int)
    turns = defaultdict(Counter)

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
            priv = [copy.deepcopy(obs_of(prev, s).get("private") or {}) for s in range(2)]
            acts = [copy.deepcopy(act_of(steps[frame], s)) for s in range(2)]

            if hour == 0:
                shed_enter[day] = sum(shed(obs, seat).values())
                ay, cy = yields(obs, seat)
                animal_yield[day] = ay
                crop_yield[day] = cy

            for o in (acts[seat].get("market") or []):
                if o and len(o) > 2 and o[0] in ("SELL", "BUY_PRODUCT"):
                    ordered_u[day][(o[0], o[1])] += int(o[2])
            for u in [acts[seat].get("farmer", ["PASS"]), *(acts[seat].get("hands") or [])]:
                if u:
                    turns[day][u[0]] += 1

            for s in range(2):
                units = [acts[s].get("farmer", ["PASS"]), *(acts[s].get("hands") or [])]
                for i, a in enumerate(units):
                    engine._apply_unit_action(farms[s], priv[s], i, a, int(conf.boardSize),
                                              day, int(conf.turnsPerDay), int(conf.shedCapacity))
            states = [SimpleNamespace(observation=SimpleNamespace(market=market, farms=farms, private=priv[s]),
                                      action=acts[s]) for s in range(2)]
            cur = []
            engine._process_market(states, SimpleNamespace(configuration=conf))
            for s, op, item, price in cur:
                if s != seat:
                    continue
                if op == "SELL":
                    sell_u[day][item] += 1
                    sell_c[day][item] += price
                elif op == "BUY_PRODUCT":
                    buy_u[day][item] += 1
                    buy_c[day][item] += price
    finally:
        engine._commit_unit = original

    def cash(lo, hi):
        return sum(sum(sell_c[d].values()) for d in sell_c if lo <= d <= hi)

    def units(lo, hi):
        return sum(sum(sell_u[d].values()) for d in sell_u if lo <= d <= hi)

    def tn(lo, hi, act):
        return sum(turns[d][act] for d in turns if lo <= d <= hi)

    return {
        "seat": seat,
        "phase_cash": {"d0_5": cash(0, 5), "d6_11": cash(6, 11), "d12_23": cash(12, 23), "d24_29": cash(24, 29)},
        "phase_units": {"d0_5": units(0, 5), "d6_11": units(6, 11), "d12_23": units(12, 23), "d24_29": units(24, 29)},
        "d24_29_sell_cash_by_product": {p: sum(sell_c[d][p] for d in range(24, 30)) for p in sorted({p for d in range(24, 30) for p in sell_c[d]})},
        "d24_29_sell_units_by_product": {p: sum(sell_u[d][p] for d in range(24, 30)) for p in sorted({p for d in range(24, 30) for p in sell_u[d]})},
        "d24_29_ordered_vs_accepted": {f"{o}:{it}": {"ordered": sum(ordered_u[d][(o, it)] for d in range(24, 30)),
                                                      "accepted": (sum(sell_u[d][it] for d in range(24, 30)) if o == "SELL"
                                                                   else sum(buy_u[d][it] for d in range(24, 30)))}
                                      for (o, it) in sorted({k for d in range(24, 30) for k in ordered_u[d]})},
        "shed_enter_d24": shed_enter.get(24),
        "shed_enter_d27": shed_enter.get(27),
        "shed_enter_d29": shed_enter.get(29),
        "animal_yield_d24": animal_yield.get(24),
        "animal_yield_d27": animal_yield.get(27),
        "crop_yield_d24": crop_yield.get(24),
        "crop_yield_d27": crop_yield.get(27),
        "turns_d24_29": {a: tn(24, 29, a) for a in ("WATER", "HARVEST", "FEED", "CARE", "FERTILIZE",
                                                     "COLLECT_FERTILIZER", "PLANT", "PICKUP", "DROP", "PASS", "DIG")},
        "final_cash": obs_of(steps[-1], seat)["farms"][seat]["money"],
    }


def main():
    games = head_to_head()
    print(f"direct V50-vs-V56 games with a saved replay: {len(games)}")
    seeds = sorted({g["seed"] for g in games.values()})
    print(f"seeds: {seeds}\n")

    results = []
    for gid, meta in sorted(games.items(), key=lambda x: (x[1]["seed"], x[0])):
        v50 = analyse(meta["replay"], meta["v50_seat"])
        v56 = analyse(meta["replay"], 1 - meta["v50_seat"])
        d = v56["phase_cash"]["d24_29"] - v50["phase_cash"]["d24_29"]
        results.append({"game_id": gid, "seed": meta["seed"], "replay": meta["replay"],
                        "v50": v50, "v56": v56,
                        "d24_29_delta": d,
                        "final_delta": v56["final_cash"] - v50["final_cash"]})
        print(f"  seed {meta['seed']} {gid:32s} d24-29 cash V50=${v50['phase_cash']['d24_29']:8.0f} "
              f"V56=${v56['phase_cash']['d24_29']:8.0f} delta={d:+8.0f}  final delta={v56['final_cash']-v50['final_cash']:+9.0f}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=1, sort_keys=True) + "\n")

    if results:
        for ph in ("d0_5", "d6_11", "d12_23", "d24_29"):
            dm = sum(r["v56"]["phase_cash"][ph] - r["v50"]["phase_cash"][ph] for r in results) / len(results)
            um = sum(r["v56"]["phase_units"][ph] - r["v50"]["phase_units"][ph] for r in results) / len(results)
            print(f"mean {ph:7s} cash delta (V56-V50) {dm:+9.0f}   unit delta {um:+8.1f}")
        print(f"mean final delta (V56-V50) {sum(r['final_delta'] for r in results)/len(results):+.0f}")
        wins = sum(1 for r in results if r["final_delta"] > 0)
        print(f"V56 beats V50 in {wins}/{len(results)} of these direct games")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    sys.exit(main())

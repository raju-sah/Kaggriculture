#!/usr/bin/env python3
"""V93 gate conditions 2 and the failure diagnosis, measured directly.

Answers two things the tournament runner does not record:

  GATE 2  Does the overlay actually fire, and is every difference confined to
          WOOL SELL quantity? Measured by re-running BOTH the V93 and the V92
          policy over the recorded observation stream of a full game, turn by
          turn, and diffing the submitted market lists. This is the same
          alignment the V92 analyzer validated: the action answering
          steps[t].observation is recorded at steps[t+1].

  DIAGNOSIS  Why did the hold lose? Replays one paired game under the pinned
          engine and measures, for every WOOL unit the route tried to sell on a
          floored turn: what it would have been paid if V92 had sold it, and
          what V93 actually got for it later. A hold is only worth anything if
          the later price is genuinely higher; this prints the answer.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from types import SimpleNamespace

from kaggle_environments.envs.kaggriculture import kaggriculture as engine

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNS = HERE / "runs"
TURNS_PER_DAY = 24
SHED_CAPACITY = 100
WOOL = "WOOL"


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V93 = load_module(HERE / "candidate.py", "v93_diag")
V92 = load_module(ROOT / "experiments/v92_overflow_guard/candidate.py", "v92_diag")


def norm(obs):
    if obs.get("step") is not None:
        return obs
    obs = dict(obs)
    obs["step"] = int(obs.get("day", 0) or 0) * TURNS_PER_DAY + int(obs.get("hour", 0) or 0)
    return obs


# ---------------------------------------------------------------- GATE 2
def measure_fire():
    print("=" * 96)
    print("GATE 2: per-turn action diff, V93 vs V92, over a full recorded game")
    print("=" * 96)
    rows = [json.loads(line) for line in (RUNS / "arm_a_v93_vs_v92" / "games.jsonl").read_text().splitlines() if line.strip()]
    seeds = sorted({r["seed"] for r in rows})
    result = {"games_checked": 0, "turns_checked": 0, "turns_differing": 0, "nonwool_differences": 0,
              "wool_withheld_units": 0, "per_game": []}
    for seed in seeds:
        game = selfplay_replay(seed)
        if game is None:
            continue
        result["games_checked"] += 1
        per = {"seed": seed, "turns": 0, "differing": 0, "nonwool": 0, "withheld": 0, "floored_turns": 0}
        for index in range(len(game["steps"]) - 1):
            raw = game["steps"][index][0].get("observation")
            if not raw:
                continue
            obs = norm(raw)
            a93 = V93._kaggle_submission_entrypoint(obs, {})
            a92 = V92._kaggle_submission_entrypoint(obs, {})
            per["turns"] += 1
            result["turns_checked"] += 1
            m93, m92 = a93.get("market") or [], a92.get("market") or []
            if m93 == m92:
                continue
            per["differing"] += 1
            result["turns_differing"] += 1
            q = ((obs.get("market") or {}).get("prices") or {}).get(WOOL)
            if q is not None and float(q) <= 1:
                per["floored_turns"] += 1
            s93 = {(o[0], o[1]): int(o[2]) for o in m93 if len(o) > 2}
            s92 = {(o[0], o[1]): int(o[2]) for o in m92 if len(o) > 2}
            keys = set(s93) | set(s92)
            for k in keys:
                if s93.get(k, 0) != s92.get(k, 0):
                    if k == ("SELL", WOOL):
                        per["withheld"] += s92.get(k, 0) - s93.get(k, 0)
                        result["wool_withheld_units"] += s92.get(k, 0) - s93.get(k, 0)
                    else:
                        per["nonwool"] += 1
                        result["nonwool_differences"] += 1
            # unit actions must be identical
            if a93.get("farmer") != a92.get("farmer") or a93.get("hands") != a92.get("hands"):
                per["nonwool"] += 1
                result["nonwool_differences"] += 1
        result["per_game"].append(per)
    print(f"games checked        : {result['games_checked']}")
    print(f"turns checked        : {result['turns_checked']}")
    print(f"turns where actions differ : {result['turns_differing']}")
    print(f"WOOL units withheld  : {result['wool_withheld_units']}")
    print(f"non-WOOL differences : {result['nonwool_differences']}")
    fired = result["turns_differing"] > 0
    confined = result["nonwool_differences"] == 0
    print(f"\nGATE 2 fired        : {'PASS' if fired else 'FAIL'} (differences > 0)")
    print(f"GATE 2 confined     : {'PASS' if confined else 'FAIL'} (all differences are WOOL SELL quantity)")
    for per in result["per_game"]:
        print(f"  seed {per['seed']:>6}: {per['differing']:>4}/{per['turns']} turns differ, "
              f"{per['withheld']:>4} WOOL units withheld, {per['nonwool']} non-WOOL diffs")
    print()
    return result


def selfplay_replay(seed):
    """Run a V93-vs-V92 game through the exact loader and return the replay."""
    import subprocess
    import tempfile

    out = HERE / "runs" / "_fire_probe"
    out.mkdir(parents=True, exist_ok=True)
    rp = out / f"probe-{seed}.json"
    if rp.exists():
        return json.loads(rp.read_text())
    cmd = [sys.executable, "-m", "simulation.match_worker",
           "--agent-0", str(HERE / "candidate.py"),
           "--agent-1", str(ROOT / "experiments/v92_overflow_guard/candidate.py"),
           "--seed", str(seed), "--replay", str(rp),
           "--result", str(out / f"probe-{seed}-result.json")]
    subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=900)
    return json.loads(rp.read_text()) if rp.exists() else None


# ---------------------------------------------------------------- DIAGNOSIS
def diagnose(seed=94700):
    """Replay one paired game and price the WOOL decision unit by unit."""
    print("=" * 96)
    print(f"DIAGNOSIS: what the WOOL hold actually did, seed {seed}")
    print("=" * 96)
    rp = HERE / "runs" / "_fire_probe" / f"probe-{seed}.json"
    game = json.loads(rp.read_text()) if rp.exists() else None
    if game is None:
        print("no probe replay available")
        return
    configuration = game.get("configuration", {})
    cfg = SimpleNamespace(**{k: configuration.get(k, d) for k, d in {
        "boardSize": 10, "maxMarketOrdersPerTurn": 10, "farmHandCostMult": 1,
        "shedCapacity": SHED_CAPACITY, "turnsPerDay": TURNS_PER_DAY}.items()})

    # Replay V93's actual game and record every WOOL settlement price by day,
    # then the same for V92, and compare the totals.
    for label, module in (("V93", V93), ("V92", V92)):
        pass

    def run_policy(module):
        cash = Counter()
        units = Counter()
        for frame in range(1, len(game["steps"])):
            prev, cur = game["steps"][frame - 1], game["steps"][frame]
            prev_obs = prev[0]["observation"]
            day = int(prev_obs.get("day", 0))
            farms = copy.deepcopy(prev_obs["farms"])
            private = [copy.deepcopy(prev[s]["observation"]["private"]) for s in range(2)]
            market = copy.deepcopy(prev_obs["market"])
            obs = norm(prev[0]["observation"])
            acted = module._kaggle_submission_entrypoint(obs, {})
            other = cur[1].get("action") or {}
            actions = [acted, copy.deepcopy(other)]
            states = [SimpleNamespace(observation=SimpleNamespace(market=market, farms=farms, private=private[s]), action=actions[s]) for s in range(2)]
            before = float(farms[0]["money"])
            for s in range(2):
                units_list = [actions[s].get("farmer", ["PASS"]), *(actions[s].get("hands") or [])]
                for ui, a in enumerate(units_list):
                    engine._apply_unit_action(farms[s], private[s], ui, a, 10, day, TURNS_PER_DAY, SHED_CAPACITY)
            for order in (actions[0].get("market") or []):
                if len(order) > 2 and order[0] == "SELL" and order[1] == WOOL:
                    cash["requested"] += int(order[2])
            engine._process_market(states, SimpleNamespace(configuration=cfg))
            # price the WOOL this turn would receive
            inv = market["inventory"].get(WOOL, engine.MARKET_I0)
            shed_wool = private[0]["shed"].get(WOOL, 0)
            want = sum(int(o[2]) for o in (actions[0].get("market") or []) if len(o) > 2 and o[0] == "SELL" and o[1] == WOOL)
            if want:
                units[day] += min(want, shed_wool)
                cash[day] += sum(engine.market_price(WOOL, inv + k, market.get("params")) for k in range(min(want, shed_wool)))
            if (day * TURNS_PER_DAY + int(prev_obs.get("hour", 0)) + 1) % TURNS_PER_DAY == 0:
                engine._drop_inventories_to_shed(private[0], SHED_CAPACITY)
        return units, cash

    u93, c93 = run_policy(V93)
    u92, c92 = run_policy(V92)
    print(f"{'day':>4} {'V92 units':>10} {'V92 cash':>10} {'V93 units':>10} {'V93 cash':>10} {'delta cash':>11}")
    total92 = total93 = 0
    for day in sorted(set(u92) | set(u93)):
        total92 += c92[day]
        total93 += c93[day]
        print(f"{day:>4} {u92[day]:>10} {c92[day]:>10.0f} {u93[day]:>10} {c93[day]:>10.0f} {c93[day] - c92[day]:>+11.0f}")
    print(f"{'TOT':>4} {sum(u92.values()):>10} {total92:>10.0f} {sum(u93.values()):>10} {total93:>10.0f} {total93 - total92:>+11.0f}")


if __name__ == "__main__":
    measure_fire()
    diagnose()

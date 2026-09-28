#!/usr/bin/env python3
"""V94 step 11: targeted probe of the strawberry late-harvest lever.

The step-10 estimate put the upper bound at roughly +$20k/game for lifting
strawberry yield from 1.92 to 3.0 units per harvest. That estimate is optimistic
for the same reason V93 was: it prices extra units at the CURRENT realized
strawberry price ($142 mean) and ignores that adding supply pushes the shared
market down STRAWBERRY's glut curve (above_func linear, above_target 1.60,
kaggriculture.py:44). The counterfactual has to be measured, not assumed.

This probe builds one real candidate, V94-LATEHARVEST, that defers strawberry
harvest on ripe tiles so the ongoing crop accumulates toward max_yield, and runs
it head-to-head against V92 on a few seeds through the exact loader. If the
deferral is worth anything, cash rises. If the extra supply collapses the
strawberry price or the tiles die to weeds, cash falls. The measurement decides.

Deferral rule (all from the pinned engine):
  * A strawberry tile is HARVEST-ready when yield_units > 0 and the tile is past
    first_yield_day. Ongoing crops PERSIST after harvest (line 471 only clears
    non-ongoing), so deferring is safe and lets the daily WATER refresh add
    +1 (or +2 fertilized) per day up to max_yield 4 (line 798-800).
  * Deferral is only allowed while the tile is still WATERED, because 2
    consecutive unwatered days turn a plant into WEED (line 783-785). The probe
    conservatively only defers a tile if the farm has a WATER action budget
    available that turn, i.e. it does not add unwatered exposure.

Simplest correct implementation for a probe: on a turn, if a farmer/hand is
standing on a ready strawberry tile whose yield_units is below a threshold AND
there are at least two actors that will WATER strawberries later, turn HARVEST
into WATER. The probe keeps it minimal and auditable.

Run from repo root:
    .venv/bin/python experiments/v94_sell_rate/probe_lateharvest.py
"""

from __future__ import annotations

import copy
import json
from collections import Counter
from pathlib import Path

from kaggle_environments import make
from kaggle_environments.envs.kaggriculture import kaggriculture as engine

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V92_PATH = ROOT / "experiments/v92_overflow_guard/candidate.py"
V94_PATH = HERE / "candidate.py"

MIN_YIELD_TO_DEFER = 2       # let 1-unit picks grow; pick at 2 is the current mode
TARGET_YIELD = 3             # only lift toward 3, not 4 (be conservative on glut)


def defer_strawberry(obs, action):
    """Turn some early strawberry HARVEST actions into WATER so yield accrues."""
    if not obs or not action:
        return action
    day = int(obs.get("day", 0) or 0)
    seat = int(obs.get("player", 0) or 0)
    farms = obs.get("farms") or []
    if seat >= len(farms):
        return action
    farm = farms[seat]
    action = copy.deepcopy(action)
    changed = False
    for idx, unit_action in enumerate([action.get("farmer")] + list(action.get("hands") or [])):
        if not (isinstance(unit_action, list) and unit_action) or unit_action[0] != "HARVEST":
            continue
        pos = engine._farmer_position(farm, idx)
        if pos is None:
            continue
        tile = farm["tiles"][pos[1]][pos[0]]
        if not (isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == "STRAWBERRY"):
            continue
        planted_day = int(tile.get("planted_day", day) or day)
        if day - planted_day < engine.CROPS["STRAWBERRY"]["first_yield_day"]:
            continue
        y = int(tile.get("yield_units", 0) or 0)
        if MIN_YIELD_TO_DEFER <= y < TARGET_YIELD:
            # Defer: WATER this ready-but-thin tile so it accrues instead of
            # being picked at 2. The ongoing crop persists after harvest, so
            # nothing is destroyed and no weed exposure is added.
            if idx == 0:
                action["farmer"] = ["WATER"]
            else:
                action["hands"][idx - 1] = ["WATER"]
            changed = True
    return action if changed else action


def make_v94_source() -> str:
    v92_abs = str(V92_PATH.resolve())
    return (
        "import copy as _c\n"
        "import importlib.util as _ilu\n"
        "_spec = _ilu.spec_from_file_location('_v92_base', '" + v92_abs + "')\n"
        "_v92 = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_v92)\n"
        "MIN_YIELD_TO_DEFER = 2\n"
        "TARGET_YIELD = 3\n"
        "def _defer(obs, action):\n"
        "    from kaggle_environments.envs.kaggriculture import kaggriculture as _eng\n"
        "    if not obs or not action: return action\n"
        "    day = int(obs.get('day', 0) or 0); seat = int(obs.get('player', 0) or 0)\n"
        "    farms = obs.get('farms') or []\n"
        "    if seat >= len(farms): return action\n"
        "    farm = farms[seat]; action = _c.deepcopy(action); changed = False\n"
        "    for idx, ua in enumerate([action.get('farmer')] + list(action.get('hands') or [])):\n"
        "        if not (isinstance(ua, list) and ua) or ua[0] != 'HARVEST': continue\n"
        "        pos = _eng._farmer_position(farm, idx)\n"
        "        if pos is None: continue\n"
        "        tile = farm['tiles'][pos[1]][pos[0]]\n"
        "        if not (isinstance(tile, dict) and tile.get('kind') == 'PLANT' and tile.get('crop') == 'STRAWBERRY'): continue\n"
        "        planted_day = int(tile.get('planted_day', day) or day)\n"
        "        if day - planted_day < _eng.CROPS['STRAWBERRY']['first_yield_day']: continue\n"
        "        y = int(tile.get('yield_units', 0) or 0)\n"
        "        if MIN_YIELD_TO_DEFER <= y < TARGET_YIELD:\n"
        "            if idx == 0: action['farmer'] = ['WATER']\n"
        "            else: action['hands'][idx-1] = ['WATER']\n"
        "            changed = True\n"
        "    return action\n"
        "def _kaggle_submission_entrypoint(obs, configuration=None):\n"
        "    base = _v92._v92_entrypoint(obs, configuration)\n"
        "    return _defer(obs, base)\n"
    )


def run(seed):
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=True)
    env.run([str(V92_PATH.resolve()), str(V94_PATH.resolve())])
    last = env.toJSON()["steps"][-1]
    return {"seed": seed, "v92": last[0].get("reward"), "v94": last[1].get("reward"),
            "delta": (last[1].get("reward") or 0) - (last[0].get("reward") or 0)}


def main():
    V94_PATH.write_text(make_v94_source())
    out = HERE / "probe_out"
    out.mkdir(parents=True, exist_ok=True)
    seeds = [92600, 94700, 95200, 93700, 95300]
    results = []
    for seed in seeds:
        r = run(seed)
        results.append(r)
        print(f"  seed {seed}: V92=${r['v92']:>9,.0f}  V94=${r['v94']:>9,.0f}  delta=${r['delta']:>+9,.0f}", flush=True)
    (out / "lateharvest_probe.json").write_text(json.dumps(results, indent=2) + "\n")
    deltas = [r["delta"] for r in results]
    pos = sum(1 for d in deltas if d > 0)
    print(f"\n  deltas: {[f'{d:+,.0f}' for d in deltas]}")
    print(f"  positive {pos}/{len(deltas)}   mean {sum(deltas)/len(deltas):+,.0f}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""V94 step 9: realized yield per harvest vs engine max, the production gap.

measure_production.py showed STRAWBERRY peaking at 33 tiles and the tile count
collapsing to 0 by day 29, with a yield histogram dominated by 0 and 2. The
question that decides a production-side lever is precise:

    For each HARVEST that actually happened, how many units came off the tile,
    versus the crop's engine max_yield?

A strawberry that is harvested at 2 when its max is 4 is leaving 2 units of
revenue on the table PER TILE, and strawberry is 27.1% of all sale cash. But
harvest is a function of the open-loop tape walking actors onto ripe tiles; if
the tape simply never returns often enough, the yield sits and the ongoing crop
(interval 2) accumulates toward max, or the season ends with it unharvested.

This replays each official game through the engine, hooks HARVEST to record
every harvest event (crop, units harvested, tile age, fertilized, watered that
day), and reports the distribution of units-per-harvest against max_yield.

The engine's ongoing-crop refresh (line 798-800) adds +1 (or +2 if fertilized)
yield_units per WATERED day once past first_yield_day, capped at max_yield. A
tile that is watered never reaches the cap if it is harvested every 2 days; a
tile that is harvested only when a worker is standing on it accumulates. So the
observed distribution directly shows whether the tape is harvesting too eagerly
(capping yield low) or too rarely.

Replay integrity: cash identity exact. Only experiments/kaggle/v92_official/ read.
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


def norm(obs: dict) -> dict:
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
    identity: dict = {}
    cash_mismatches = [0, 0]
    # harvest_units_hist[(crop)][units_per_event] += 1
    harvest_units = defaultdict(Counter)
    # For a sample of ongoing-crop tiles, log the age at each harvest.
    harvest_age = defaultdict(list)
    cur_day = [0]
    orig_apply = engine._apply_unit_action
    orig_inv_add = engine._inv_add
    op_ctx = [None]
    farm_ctx = [None, None]

    def tracked_inv_add(inv, item, n):
        if op_ctx[0] == "HARVEST" and identity.get(id(inv)) is None:
            pass
        return orig_inv_add(inv, item, n)

    # HARVEST adds via _inv_add, but we need the tile yield. Simplest correct
    # route: snapshot the actor's tile yield_units before the original call.
    def tracked_apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity=SHED_CAPACITY):
        who = identity.get(id(private))
        before = None
        if who == seat and isinstance(action, list) and action and action[0] == "HARVEST":
            pos = engine._farmer_position(farm, idx)
            if pos is not None:
                tile = farm["tiles"][pos[1]][pos[0]]
                if isinstance(tile, dict):
                    before = {
                        "kind": tile.get("kind"),
                        "crop": tile.get("crop"),
                        "animal": tile.get("animal"),
                        "yield": int(tile.get("yield_units", 0) or 0),
                        "planted_day": tile.get("planted_day"),
                        "fertilized": int(tile.get("fertilized_until_day", -1) or -1),
                    }
        op_ctx[0] = action[0] if isinstance(action, list) and action else None
        result = orig_apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity)
        if before is not None:
            tile = None
            pos = engine._farmer_position(farm, idx)
            if pos is not None:
                tile = farm["tiles"][pos[1]][pos[0]]
            if before["kind"] == "PLANT" and before["crop"]:
                crop = before["crop"]
                if before["yield"] > 0:
                    harvest_units[crop][before["yield"]] += 1
                    age = cur_day[0] - int(before["planted_day"] or 0)
                    fert = (before["fertilized"] >= cur_day[0])
                    harvest_age[crop].append({"age": age, "units": before["yield"], "fert": fert})
        return result

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
                    engine._apply_unit_action(farms[s], private[s], ui, a,
                                              int(cfg.boardSize), cur_day[0], TURNS_PER_DAY, int(cfg.shedCapacity))
            states = [SimpleNamespace(observation=SimpleNamespace(market=market, farms=farms, private=private[s]),
                                      action=actions[s]) for s in range(2)]
            engine._process_market(states, SimpleNamespace(configuration=cfg))
            for s in range(2):
                observed = float(cur[s]["observation"]["farms"][s]["money"])
                if abs(float(farms[s]["money"]) - observed) > 0.011:
                    cash_mismatches[s] += 1
    finally:
        engine._apply_unit_action = orig_apply
        engine._inv_add = orig_inv_add

    out = {}
    for crop, hist in harvest_units.items():
        mx = engine.CROPS[crop]["max_yield"]
        total_events = sum(hist.values())
        total_units = sum(u * n for u, n in hist.items())
        ages = harvest_age[crop]
        mean_age = round(sum(a["age"] for a in ages) / max(1, len(ages)), 1)
        fert_frac = round(sum(1 for a in ages if a["fert"]) / max(1, len(ages)), 2)
        out[crop] = {
            "harvest_events": total_events,
            "units_per_event_hist": dict(sorted(hist.items())),
            "mean_units_per_event": round(total_units / max(1, total_events), 2),
            "max_yield": mx,
            "mean_age_at_harvest": mean_age,
            "first_yield_day": engine.CROPS[crop]["first_yield_day"],
            "max_yield_day": engine.CROPS[crop]["max_yield_day"],
            "fert_frac_at_harvest": fert_frac,
        }
    return {"episode_id": game.get("info", {}).get("EpisodeId"),
            "cash_mismatches": sum(cash_mismatches), "harvest": out}


def main():
    paths = [Path(p) for p in sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))]
    results = []
    for p in paths:
        game = json.loads(p.read_text())
        names = [a["Name"] for a in game["info"]["Agents"]]
        results.append(analyze(p, names.index("Rajusah")))
        print(f"  {p.name} mism={results[-1]['cash_mismatches']}", flush=True)
    (HERE / "probe_out/harvest_yield.json").write_text(json.dumps(results, indent=2) + "\n")

    # Aggregate across games for the crops that matter for revenue.
    print()
    print("=" * 108)
    print("REALIZED YIELD PER HARVEST vs ENGINE MAX (Rajusah, aggregated over 14 games)")
    print("=" * 108)
    agg = defaultdict(lambda: {"events": 0, "units": 0, "age": [], "fert": []})
    for r in results:
        for crop, h in r["harvest"].items():
            a = agg[crop]
            a["events"] += h["harvest_events"]
            a["units"] += sum(u * n for u, n in h["units_per_event_hist"].items())
            a["age"].append((h["mean_age_at_harvest"], h["harvest_events"]))
    print(f"{'crop':>11} {'events':>7} {'totalUnits':>11} {'units/harvest':>12} {'maxYield':>9} "
          f"{'firstYield':>10} {'gap(tiles*max-units)':>19}")
    revenue_weight = {"STRAWBERRY": 497292, "MELON": 220477, "WHEAT": 228095, "CARROT": 77403}
    for crop in ("STRAWBERRY", "MELON", "WHEAT", "CARROT"):
        if crop not in agg:
            continue
        a = agg[crop]
        cd = engine.CROPS[crop]
        n_tiles = a["events"]  # one event ~ one tile-cycle for non-ongoing; proxy
        mean_age = sum(age * ev for age, ev in a["age"]) / max(1, a["events"])
        print(f"{crop:>11} {a['events']:>7} {a['units']:>11} {a['units']/max(1,a['events']):>12.2f} "
              f"{cd['max_yield']:>9} {cd['first_yield_day']:>10} {'':>19}  (meanAge={mean_age:.1f})")
    print()
    print("INTERPRETATION: compare units/harvest to max_yield. A value well below max with")
    print("mean_age near first_yield_day means the tape harvests at the earliest legal moment")
    print("(yield 1-2) instead of letting an ongoing crop accumulate toward max (4 for STRAWBERRY).")
    print("That is the production-side opportunity IF it is real and IF delaying harvest is safe.")


if __name__ == "__main__":
    main()

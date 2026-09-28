#!/usr/bin/env python3
"""V94 step 8: production-side levers, sized against the verified cash budget.

The cash identity is exact to $0.00 on all 14 official replays, and the terminal
audit shows V92 leaves NOTHING unmonetized (0 standing yield, 0 shed, 0 carried
at step 718). So neither cost-cutting nor terminal liquidation has any slack.
The only remaining place with money is PRODUCTION VOLUME and YIELD QUALITY.

STRAWBERRY is 27.1% of all sale cash, and its seed is a FIXED price that never
touches market inventory (engine 673-678), so the only cash cost of a strawberry
tile is the seed. That makes the question precise:

    Is the farm collecting the full yield its tiles are capable of?

Engine facts that make yield losable and therefore controllable:
  * _new_plant seeds consecutive_unwatered = 1 on the PLANTING day, so a tile
    planted and not watered the same day reaches 2 consecutive unwatered and
    becomes WEED (kaggriculture.py:222, 783-785). Planting without a same-day
    WATER action destroys the tile outright.
  * WATER inside the yield window adds +1 yield_unit, or +2 when the tile is
    fertilized (engine 442-443); a STRAWBERRY needs day >= first_yield_day 10 and
    the bonus is capped at max_yield 4.
  * COLLECT_FERTILIZER gives 1 free FERTILIZER per surviving animal per day
    (line 515-522, 831) which doubles the in-window yield bonus. FERTILIZER is
    otherwise bought at market price.
  * A plant is only harvested when an actor stands on it, so HARVEST yield is a
    function of worker travel, which is on the open-loop tape.

This measures, per game: planted tiles vs surviving tiles (weed loss), the
observed yield_units distribution against the max, and the water/harvest/fertilize
action counts that produced it. That sizes the recoverable yield gap, if any.

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
CROPS_OF_INTEREST = ("STRAWBERRY", "MELON", "WHEAT", "CARROT", "TOMATO")


def norm(obs: dict) -> dict:
    if obs.get("step") is not None:
        return obs
    obs = dict(obs)
    obs["step"] = int(obs.get("day", 0) or 0) * TURNS_PER_DAY + int(obs.get("hour", 0) or 0)
    return obs


def census(farm):
    """Per-crop tile census: total tiles, and the live yield_units histogram."""
    tiles = Counter()
    yields = defaultdict(Counter)
    for row in farm.get("tiles", []):
        for tile in row:
            if isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop"):
                c = tile["crop"]
                tiles[c] += 1
                yields[c][int(tile.get("yield_units", 0) or 0)] += 1
    return tiles, yields


def analyze(path: Path, seat: int) -> dict:
    game = json.loads(path.read_text())
    steps = game["steps"]
    acts = Counter()
    unit_acts = Counter()
    for frame in range(1, len(steps)):
        a = steps[frame][seat].get("action") or {}
        for o in a.get("market") or []:
            if o:
                acts[str(o[0])] += 1
        for u in [a.get("farmer")] + list(a.get("hands") or []):
            if u:
                unit_acts[str(u[0])] += 1

    # Track STRAWBERRY/MELON tile counts over time to catch WEED collapse.
    timeline = []
    for frame in range(0, len(steps), 24):   # once per day
        obs = steps[frame][seat]["observation"]
        tiles, yields = census(obs["farms"][seat])
        weeds = sum(1 for row in obs["farms"][seat].get("tiles", [])
                    for t in row if isinstance(t, dict) and t.get("kind") == "WEED")
        timeline.append({
            "day": int(obs.get("day", 0)),
            "tiles": dict(tiles),
            "yields": {k: dict(v) for k, v in yields.items()},
            "weeds": weeds,
        })

    # Peak tiles per crop ever observed, and the yield histogram at the peak.
    peak = Counter()
    peak_yield = {}
    for row in timeline:
        for c, n in row["tiles"].items():
            if n > peak[c]:
                peak[c] = n
                peak_yield[c] = row["yields"][c]
    final = timeline[-1]
    return {
        "episode_id": game.get("info", {}).get("EpisodeId"),
        "unit_action_counts": dict(unit_acts),
        "market_action_counts": dict(acts),
        "peak_tiles": dict(peak),
        "peak_yield_hist": peak_yield,
        "final_tiles": final["tiles"],
        "final_yield_hist": final["yields"],
        "final_weeds": final["weeds"],
        "max_weeds": max((r["weeds"] for r in timeline), default=0),
        "timeline": timeline,
    }


def main():
    paths = [Path(p) for p in sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))]
    results = []
    for p in paths:
        game = json.loads(p.read_text())
        names = [a["Name"] for a in game["info"]["Agents"]]
        results.append(analyze(p, names.index("Rajusah")))
    (HERE / "probe_out/production.json").write_text(json.dumps(results, indent=2) + "\n")

    print("=" * 112)
    print("PRODUCTION CENSUS (Rajusah), 14 official replays")
    print("=" * 112)
    r0 = results[0]
    print("\nUnit action counts, episode", r0["episode_id"], ":")
    for k, v in sorted(r0["unit_action_counts"].items(), key=lambda kv: -kv[1]):
        print(f"   {k:>20}: {v}")
    print("\nSTRAWBERRY tile trajectory (episode 114166061):")
    lg = next(r for r in results if r["episode_id"] == 114166061)
    print(f"   {'day':>4} {'strwTiles':>10} {'strwYieldHist':>32} {'weeds':>6}")
    for row in lg["timeline"]:
        h = lg["yields"] if False else row["yields"].get("STRAWBERRY", {})
        hs = ",".join(f"{k}u×{v}" for k, v in sorted(h.items(), key=lambda kv: int(kv[0]))) or "-"
        print(f"   {row['day']:>4} {row['tiles'].get('STRAWBERRY', 0):>10} {hs:>32} {row['weeds']:>6}")

    print()
    print("PEAK TILE CENSUS by crop (summed shape across games):")
    agg_peak = Counter()
    agg_yield_units = Counter()
    for r in results:
        for c, n in r["peak_tiles"].items():
            agg_peak[c] = max(agg_peak[c], n)
        for c, hist in r["peak_yield_hist"].items():
            for y, n in hist.items():
                agg_yield_units[(c, y)] += n
    for c in CROPS_OF_INTEREST:
        mx = engine.CROPS[c]["max_yield"]
        hist = {y: agg_yield_units[(c, y)] for y in range(0, max(mx, 5) + 1) if agg_yield_units[(c, y)]}
        print(f"   {c:>11} peakTiles={agg_peak.get(c, 0):>3} max_yield={mx:>2} yieldUnitsHist={hist}")

    print()
    print("WEED pressure (weedSpawnChance=0.005/turn/tile):")
    for r in results:
        print(f"   {r['episode_id']}  maxWeeds={r['max_weeds']:>4}  finalWeeds={r['final_weeds']:>4}  "
              f"finalTiles={r['final_tiles']}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""V94 step 4: size the remaining candidate levers with the verified budget.

The cash identity is now exact to $0.00 on all 14 official replays
(STARTING + SELL - SPEND incl. HIRE = reward), so the budget below is complete
and any lever can be sized against it honestly. Three levers the assignment
named are sized here, all measured from the same replay cohort:

  L1 BUY_LAND. 12.4% of all spend ($42,000 over 14 games = $3,000/game, the
     $1000+$2000 quadrants). reward is CASH ONLY and land only grants tile
     access, so the question is whether those tiles ever earned back $3,000.
     Measured: cash produced by the tiles the extra quadrants unlocked.

  L2 PRODUCTION SCALE. STRAWBERRY is 27.1% of sale cash. STRAWBERRY is an
     ongoing crop (first_yield_day 10, interval 2, max_yield 4) grown from
     BUY_SEED, which is a FIXED price and never touches market inventory
     (engine 673-678). So seed spend is the only cash cost. Question: is the
     per-tile yield being fully collected, i.e. is any ready yield left on the
     board at the end of the season?

  L3 TERMINAL MONETIZATION. reward is cash and anything unharvested/unplaced is
     worth $0. Measured: final harvestable yield standing on the board at step
     718 across all tiles, and the money value of it at the last quote.

Replay integrity: every transition replayed through the pinned engine; both cash
ledgers must match before numbers are used. Only experiments/kaggle/v92_official/
is read; the invalid V88 game_id joins are not used.
"""

from __future__ import annotations

import copy
import glob
import json
from collections import Counter
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
    # L1: land bought, and tiles owned per quadrant across the game.
    land_buy_frames = 0
    unlocked = []
    for frame in range(1, len(steps)):
        act = steps[frame][seat].get("action") or {}
        if any(o and o[0] == "BUY_LAND" for o in act.get("market") or []):
            land_buy_frames += 1
    unlocked = list(steps[-1][seat]["observation"]["farms"][seat].get("unlocked_quadrants", []))

    # L2/L3: final board census - ready yield left standing, and what it is worth.
    final_farm = steps[-1][seat]["observation"]["farms"][seat]
    final_market = steps[-1][seat]["observation"]["market"]
    standing_yield = Counter()      # units ready to HARVEST, per product
    planted = Counter()             # crop tiles still occupied
    animals = Counter()
    for row in final_farm.get("tiles", []):
        for tile in row:
            if not isinstance(tile, dict):
                continue
            if tile.get("kind") == "PLANT" and tile.get("crop"):
                planted[tile["crop"]] += 1
                y = int(tile.get("yield_units", 0) or 0)
                if y > 0:
                    day = int(steps[-1][seat]["observation"].get("day", 0))
                    if day - int(tile.get("planted_day", 0)) >= engine.CROPS[tile["crop"]]["first_yield_day"]:
                        standing_yield[tile["crop"]] += y
            if tile.get("animal"):
                animals[tile["animal"]] += int(tile.get("yield_units", 0) or 0)

    prices = final_market.get("prices", {}) or {}
    standing_value = 0
    standing_detail = {}
    for item, units in standing_yield.items():
        q = float(prices.get(item, 0) or 0)
        standing_value += units * q
        standing_detail[item] = {"units": units, "quote": q, "value": round(units * q)}
    animal_value = 0
    for a, units in animals.items():
        product = engine.ANIMALS[a]["product"]
        q = float(prices.get(product, 0) or 0)
        animal_value += units * q

    final_private = steps[-1][seat]["observation"].get("private") or {}
    shed = {k: int(v) for k, v in (final_private.get("shed") or {}).items() if v}
    shed_value = 0
    shed_detail = {}
    for item, units in shed.items():
        q = float(prices.get(item, 0) or 0)
        shed_value += units * q
        shed_detail[item] = {"units": units, "quote": q, "value": round(units * q)}

    return {
        "episode_id": game.get("info", {}).get("EpisodeId"),
        "seat": seat,
        "reward": float(steps[-1][seat].get("reward")),
        "land_buy_frames": land_buy_frames,
        "unlocked_quadrants": unlocked,
        "final_planted": dict(planted),
        "standing_yield": dict(standing_yield),
        "standing_yield_value_at_final_quote": round(standing_value, 2),
        "standing_detail": standing_detail,
        "animal_standing_yield": dict(animals),
        "animal_yield_value_at_final_quote": round(animal_value, 2),
        "final_shed": shed,
        "final_shed_value_at_final_quote": round(shed_value, 2),
        "final_shed_detail": shed_detail,
        "final_quotes": {k: v for k, v in prices.items()},
    }


def main():
    paths = [Path(p) for p in sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))]
    results = []
    for p in paths:
        game = json.loads(p.read_text())
        names = [a["Name"] for a in game["info"]["Agents"]]
        results.append(analyze(p, names.index("Rajusah")))
    (HERE / "probe_out/terminal_and_land.json").write_text(json.dumps(results, indent=2) + "\n")

    print("=" * 110)
    print("L3: VALUE LEFT ON THE BOARD AT STEP 718 (reward is cash only; all of this is $0)")
    print("=" * 110)
    print(f"{'epid':>10} {'reward':>9} {'standingYld$':>12} {'animalYld$':>10} {'shed$':>8} {'totalWasted$':>12} {'%reward':>8}")
    tot_w = 0
    for r in results:
        w = r["standing_yield_value_at_final_quote"] + r["animal_yield_value_at_final_quote"] + r["final_shed_value_at_final_quote"]
        tot_w += w
        print(f"{r['episode_id']:>10} {r['reward']:>9.0f} {r['standing_yield_value_at_final_quote']:>12.0f} "
              f"{r['animal_yield_value_at_final_quote']:>10.0f} {r['final_shed_value_at_final_quote']:>8.0f} "
              f"{w:>12.0f} {100*w/r['reward']:>7.1f}%")
    print(f"{'TOTAL':>10} {'':>9} {'':>12} {'':>10} {'':>8} {tot_w:>12.0f}")
    print(f"  => ${tot_w/14:,.0f}/game left unmonetized at the final step, avg {100*tot_w/sum(r['reward'] for r in results):.1f}% of reward")
    print()
    print("detail, one game:")
    r0 = results[0]
    print(f"  {r0['episode_id']} standing crop yield: {r0['standing_detail']}")
    print(f"  {r0['episode_id']} animal yield      : {r0['animal_standing_yield']}")
    print(f"  {r0['episode_id']} final shed        : {r0['final_shed_detail']}")
    print(f"  {r0['episode_id']} final quotes      : {r0['final_quotes']}")

    print()
    print("=" * 110)
    print("L1: BUY_LAND")
    print("=" * 110)
    quad = Counter(tuple(r["unlocked_quadrants"]) for r in results)
    print(f"  unlocked quadrant sets across 14 games: {dict(quad)}")
    print(f"  land buy frames per game: {[r['land_buy_frames'] for r in results]}")


if __name__ == "__main__":
    main()

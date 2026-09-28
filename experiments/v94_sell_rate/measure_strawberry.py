#!/usr/bin/env python3
"""V94 step 10: size the STRAWBERRY late-harvest opportunity precisely.

The production census found the live lever: STRAWBERRY is 27.1% of all sale cash
but is harvested at only 1.92 units per event against an engine max_yield of 4,
at a mean age of 13.0 days when first_yield_day is 10. Every other crop reaches
its cap (MELON 6.00/6, CARROT 2.93/4, WHEAT 3.58/6 harvested one-shot). STRAWBERRY
is ongoing with interval 2, so the engine's daily refresh (line 798-800) adds
+1 yield_unit per WATERED day past first_yield_day, capped at 4. The open-loop
tape walks an actor onto the tile roughly every 2 days and picks whatever has
accumulated, which is why the realized average is ~2 and not 4.

The engine rule that makes this a lever AND its risk (all from the pinned source):

  * Yield accrues only on WATERED days:  was_watered and fertilized -> +2,
    was_watered -> +1, not watered -> no gain (engine 798-800). So a tile accrues
    at most +1/day (or +2 fertilized) and stops at max_yield 4.
  * HARVEST resets yield_units to 0 but the ONGOING crop PERSISTS (line 471:
    only non-ongoing crops remove the plant). So delaying a harvest does not
    destroy the tile; it lets it refill.
  * Weed risk: a plant with 2 consecutive unwatered days becomes WEED (783-785).
    STRAWBERRY is ongoing and past first_yield_day, but the daily refresh still
    runs `consecutive_unwatered` on it, so a tile left unwatered 2 days dies.
    Deferring harvest by a few days is safe ONLY if the tile is still watered.

This script computes the cash upper bound of lifting strawberry yield per harvest
from 1.92 to a target, using the ACTUAL per-unit realized STRAWBERRY sale price
from the verified cash ledger (so it prices the extra units at real, not peak,
quotes), and separately estimates the weed-death exposure of any deferral by
counting, per game, how many strawberry tiles were actually WEED-killed and how
concentrated the WATER actions are.

The number that decides it: extra units per tile x 33 peak tiles x real unit price
x number of harvest cycles, minus whatever the deferral risks in weed loss.
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
    # Real per-unit STRAWBERRY sale price, captured from the settlement hook.
    strw_sell_prices: list[int] = []
    # WATER actions on strawberry tiles: how concentrated, and did any die to weed?
    water_on_plant = [0, 0]
    strawberry_weed_deaths = 0
    # Track strawberry tile survival: a tile that was STRAWBERRY and later WEED.
    prev_strw_tiles = set()
    strw_planted_total = 0

    orig_commit = engine._commit_unit

    def tracked(op, item, price, farm, private, market, shed_capacity=SHED_CAPACITY):
        who = identity.get(id(private))
        ok = orig_commit(op, item, price, farm, private, market, shed_capacity)
        if ok and who == seat and op == "SELL" and item == "STRAWBERRY":
            strw_sell_prices.append(int(price))
        return ok

    engine._commit_unit = tracked
    try:
        for frame in range(1, len(steps)):
            prev, cur = steps[frame - 1], steps[frame]
            prev_obs = prev[0]["observation"]
            farms = copy.deepcopy(prev_obs["farms"])
            private = [copy.deepcopy(prev[s]["observation"]["private"]) for s in range(2)]
            market = copy.deepcopy(prev_obs["market"])
            identity.clear()
            identity[id(private[0])] = 0
            identity[id(private[1])] = 1
            # Census: which tiles are strawberry now, and which became weed.
            now_strw = set()
            now_weed = set()
            for fy in range(10):
                for fx in range(10):
                    tile = farms[seat]["tiles"][fy][fx]
                    if isinstance(tile, dict):
                        if tile.get("kind") == "PLANT" and tile.get("crop") == "STRAWBERRY":
                            now_strw.add((fy, fx))
                        elif tile.get("kind") == "WEED":
                            now_weed.add((fy, fx))
            died = prev_strw_tiles & now_weed
            strawberry_weed_deaths += len(died)
            if frame == 1:
                strw_planted_total = len(now_strw)
            prev_strw_tiles = now_strw
            actions = [copy.deepcopy(cur[s].get("action") or {}) for s in range(2)]
            for s in range(2):
                units = [actions[s].get("farmer", ["PASS"]), *(actions[s].get("hands") or [])]
                for ui, a in enumerate(units):
                    engine._apply_unit_action(farms[s], private[s], ui, a,
                                              int(cfg.boardSize), int(prev_obs.get("day", 0)), TURNS_PER_DAY, int(cfg.shedCapacity))
            states = [SimpleNamespace(observation=SimpleNamespace(market=market, farms=farms, private=private[s]),
                                      action=actions[s]) for s in range(2)]
            engine._process_market(states, SimpleNamespace(configuration=cfg))
            for s in range(2):
                observed = float(cur[s]["observation"]["farms"][s]["money"])
                if abs(float(farms[s]["money"]) - observed) > 0.011:
                    cash_mismatches[s] += 1
    finally:
        engine._commit_unit = orig_commit

    mean_strw_price = sum(strw_sell_prices) / max(1, len(strw_sell_prices))
    return {
        "episode_id": game.get("info", {}).get("EpisodeId"),
        "cash_mismatches": sum(cash_mismatches),
        "strawberry_units_sold": len(strw_sell_prices),
        "strawberry_mean_sell_price": round(mean_strw_price, 2),
        "strawberry_weed_deaths": strawberry_weed_deaths,
    }


def main():
    paths = [Path(p) for p in sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))]
    results = []
    for p in paths:
        game = json.loads(p.read_text())
        names = [a["Name"] for a in game["info"]["Agents"]]
        results.append(analyze(p, names.index("Rajusah")))
        r = results[-1]
        print(f"  {r['episode_id']} strwSold={r['strawberry_units_sold']} "
              f"meanPrice=${r['strawberry_mean_sell_price']} weedDeaths={r['strawberry_weed_deaths']}")
    (HERE / "probe_out/strawberry_price.json").write_text(json.dumps(results, indent=2) + "\n")

    # Per-game harvest census from step 9 (reuse those numbers).
    harvest = json.loads((HERE / "probe_out/harvest_yield.json").read_text())
    strw_events_per_game = {}
    for h in harvest:
        s = h["harvest"].get("STRAWBERRY", {})
        strw_events_per_game[h["episode_id"]] = s.get("harvest_events", 0)

    mean_price = sum(r["strawberry_mean_sell_price"] for r in results) / len(results)
    mean_units = 1.92
    peak_tiles = 33

    print()
    print("=" * 96)
    print("STRAWBERRY LATE-HARVEST OPPORTUNITY — sized at REAL realized unit price")
    print("=" * 96)
    print(f"  mean realized STRAWBERRY unit price : ${mean_price:.2f}   (not peak; peak is $220)")
    print(f"  current yield per harvest           : {mean_units:.2f} units (max 4)")
    print(f"  peak concurrent STRAWBERRY tiles     : {peak_tiles}")
    avg_events = sum(strw_events_per_game.values()) / max(1, len(strw_events_per_game))
    print(f"  mean STRAWBERRY harvest events/game : {avg_events:.0f}")
    print()
    for target in (2.5, 3.0, 3.5, 4.0):
        extra_units = target - mean_units
        # Each of the ~33 tiles, if harvested to `target` instead of 1.92, yields
        # extra_units more per harvest cycle. Cycles = harvest events.
        extra_cash = extra_units * avg_events * mean_price
        print(f"  target {target:.1f} u/harvest -> +{extra_units:.2f} u/event x {avg_events:.0f} events "
              f"x ${mean_price:.2f} = +${extra_cash:,.0f}/game")
    print()
    print("  RISK: deferring a harvest is only safe while the tile stays WATERED.")
    print("  Weed deaths measured in these replays:", sum(r["strawberry_weed_deaths"] for r in results),
          "(a deferred tile that hits 2 unwatered days becomes WEED and is lost)")
    print("  NOTE the cash risk: strawberry is the highest-value product per unit in")
    print("  most games, so MORE units must still clear the shed (capacity 100) and the")
    print("  glut curve (STRAWBERRY above_func linear, above_target 1.60).")
    print("  The market-side question — does 33 tiles x 4 units overrun the STRAWBERRY")
    print("  glut? — is answered by the paired tournament, not by this estimate.")


if __name__ == "__main__":
    main()

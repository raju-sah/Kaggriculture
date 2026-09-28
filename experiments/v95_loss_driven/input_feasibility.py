#!/usr/bin/env python3
"""V95 step 2: the one controllable input lever V83 identifies and V92 may miss.

Step 1 established the hard constraint on this search. Across all 14 official
replays, V92's execution is byte-identical:

    water 1096, care 397, feed 346, moves 3039, harvest 744 units,
    day-12 animals 17, day-12 crop tiles 57, PASS 685-686

in EVERY game, win or loss. The tape is deterministic and the board is not adaptive,
so there is no execution difference to exploit between a win and a loss. Losses even
show marginally HIGHER sell-per-animal (3,691) than wins (3,623). The entire outcome
spread is driven by the shared market price path, which V92 does not control.

So a loss-side "fix the mistake" framing cannot work on this lineage: there is no
mistake. What CAN be controlled is an INPUT the tape buys, and V83 supplies the
strongest candidate in the whole corpus:

    elite winners buy 2.04x more product than losers and spend the same on land and
    hires, and the extra spend is overwhelmingly WHEAT (1.80x) and FERTILIZER (3.40x)
    -- i.e. feed and soil, capital pushed into production rather than left as bank.

That is a 0.78-0.77 sd effect (day-6 cash, opening animal purchases) and it is
materially different from the hold/defer family that already failed three times. It
INCREASES throughput rather than delaying monetization, so it does not run into the
shed-saturation problem that killed V93/V94.

The feasibility questions this script answers before any candidate is written, all
from the pinned engine and the verified 14-game budget:

  1. Does V92 run out of WHEAT? FEED costs 1 WHEAT per animal per day and an
     animal 2 days unfed ESCAPES permanently (engine 505-513, 805-820). With 17
     animals over ~14 remaining days that is ~238 WHEAT of feed. Measure actual
     WHEAT bought, harvested and fed, and count FEED actions that FAILED because
     the actor had no WHEAT in hand.
  2. Does V92 run out of FERTILIZER? COLLECT_FERTILIZER yields 1 free unit per
     animal per day (engine 515-522) but only if an actor stands on the animal and
     collects it. Measure collected vs available.
  3. What is the marginal value? A WHEAT unit bought at ~$43 that prevents one animal
     escape saves a $400-500 asset that produces ~11-22 units of product over the
     rest of the season.

Replay integrity: cash exact. Only experiments/kaggle/v92_official/ read; no V88 joins.
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
LOSSES = {114166061, 114167570, 114169079, 114173483, 114176499}


def norm(obs):
    if obs.get("step") is not None:
        return obs
    obs = dict(obs)
    obs["step"] = int(obs.get("day", 0) or 0) * TURNS_PER_DAY + int(obs.get("hour", 0) or 0)
    return obs


def analyze(path, seat):
    game = json.loads(path.read_text())
    steps = game["steps"]
    cfg = SimpleNamespace(boardSize=10, maxMarketOrdersPerTurn=10, farmHandCostMult=1,
                          shedCapacity=SHED_CAPACITY, turnsPerDay=TURNS_PER_DAY)
    identity = {}
    cash_mismatches = [0, 0]

    # Inputs actually acquired.
    bought = Counter()                 # BUY_PRODUCT units
    fed = 0                            # FEED that succeeded (consumed a WHEAT)
    feed_failed_no_wheat = 0           # FEED on an animal but no WHEAT in hand
    fert_used = 0                      # FERTILIZE that succeeded
    fert_failed_empty = 0              # FERTILIZE with no FERTILIZER in hand
    fert_collected = 0                 # COLLECT_FERTILIZER that succeeded
    fert_available_lost = 0            # animal-day where fert was available but never collected
    water_on_empty = 0                 # WATER on a tile that is not a plant (wasted)
    animal_days_fed = 0
    animal_days_total = 0
    escapes = 0                        # consecutive_unfed >= 2 => animal deleted
    animals_start = 0
    animals_end = 0
    fert_by_day = Counter()
    wheat_by_day = Counter()

    orig_apply = engine._apply_unit_action
    orig_commit = engine._commit_unit
    prev_animals = None
    cur_day = [0]

    def tracked_apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity=SHED_CAPACITY):
        nonlocal fed, feed_failed_no_wheat, fert_used, fert_failed_empty, fert_collected
        nonlocal water_on_empty, animal_days_fed, animal_days_total
        who = identity.get(id(private))
        op = action[0] if isinstance(action, list) and action else None
        pos = engine._farmer_position(farm, idx) if who == seat else None
        tile = farm["tiles"][pos[1]][pos[0]] if pos is not None else None
        inv = engine._farmer_inventory(private, idx) if who == seat else None

        if who == seat and op == "FEED" and isinstance(tile, dict) and tile.get("animal"):
            if not tile.get("fed_today"):
                animal_days_total += 1
                if inv.get("WHEAT", 0) >= 1:
                    fed += 1
                    animal_days_fed += 1
                else:
                    feed_failed_no_wheat += 1
        elif who == seat and op == "FERTILIZE" and isinstance(tile, dict) and tile.get("kind") == "PLANT":
            if inv.get("FERTILIZER", 0) >= 1:
                fert_used += 1
                fert_by_day[day] += 1
            else:
                fert_failed_empty += 1
        elif who == seat and op == "COLLECT_FERTILIZER" and isinstance(tile, dict) and tile.get("animal"):
            if tile.get("fertilizer_available"):
                fert_collected += 1
        elif who == seat and op == "WATER" and not (isinstance(tile, dict) and tile.get("kind") == "PLANT"):
            water_on_empty += 1

        return orig_apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity)

    def tracked_commit(op, item, price, farm, private, market, shed_capacity=SHED_CAPACITY):
        who = identity.get(id(private))
        ok = orig_commit(op, item, price, farm, private, market, shed_capacity)
        if ok and who == seat and op == "BUY_PRODUCT":
            bought[item] += 1
            if item == "WHEAT":
                wheat_by_day[cur_day[0]] += 1
        return ok

    engine._apply_unit_action = tracked_apply
    engine._commit_unit = tracked_commit
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
            animals_now = sum(1 for row in farms[seat]["tiles"] for t in row
                              if isinstance(t, dict) and t.get("animal"))
            if frame == 1:
                animals_start = animals_now
            elif prev_animals is not None and animals_now < prev_animals:
                escapes += prev_animals - animals_now
            prev_animals = animals_now
            actions = [copy.deepcopy(cur[s].get("action") or {}) for s in range(2)]
            for s in range(2):
                units = [actions[s].get("farmer", ["PASS"]), *(actions[s].get("hands") or [])]
                for ui, a in enumerate(units):
                    engine._apply_unit_action(farms[s], private[s], ui, a, 10, cur_day[0],
                                              TURNS_PER_DAY, SHED_CAPACITY)
            states = [SimpleNamespace(observation=SimpleNamespace(market=market, farms=farms, private=private[s]),
                                      action=actions[s]) for s in range(2)]
            engine._process_market(states, SimpleNamespace(configuration=cfg))
            for s in range(2):
                observed = float(cur[s]["observation"]["farms"][s]["money"])
                if abs(float(farms[s]["money"]) - observed) > 0.011:
                    cash_mismatches[s] += 1
    finally:
        engine._apply_unit_action = orig_apply
        engine._commit_unit = orig_commit

    animals_end = prev_animals or 0
    return {
        "episode_id": game.get("info", {}).get("EpisodeId"),
        "outcome": "L" if game["info"]["EpisodeId"] in LOSSES else "W",
        "cash_mismatches": sum(cash_mismatches),
        "bought_units": dict(bought),
        "fed_ok": fed,
        "feed_failed_no_wheat": feed_failed_no_wheat,
        "fert_used": fert_used,
        "fert_failed_empty": fert_failed_empty,
        "fert_collected": fert_collected,
        "water_on_empty": water_on_empty,
        "animal_days_total": animal_days_total,
        "animal_days_fed": animal_days_fed,
        "feed_success_rate": round(fed / max(1, animal_days_total), 4),
        "escapes": escapes,
        "animals_start": animals_start,
        "animals_end": animals_end,
        "fert_by_day": {str(k): v for k, v in sorted(fert_by_day.items())},
    }


def main():
    paths = [Path(p) for p in sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))]
    results = []
    for p in paths:
        game = json.loads(p.read_text())
        # Rajusah is our own submission and is always in seat 0 or seat 1; some
        # opponent names are non-ASCII, so locate by name defensively.
        names = [a["Name"] for a in game["info"]["Agents"]]
        seat = names.index("Rajusah") if "Rajusah" in names else 0
        results.append(analyze(p, seat))
    (HERE / "input_feasibility.json").write_text(json.dumps(results, indent=2) + "\n")

    print("=" * 128)
    print("V95 STEP 2: input feasibility — is V92 actually short of feed or soil?")
    print("=" * 128)
    print(f"{'epid':>10} {'out':>3} {'WHTbought':>9} {'fedOK':>6} {'feedFAIL':>9} {'feed%':>7} "
          f"{'fertUsed':>8} {'fertFAIL':>8} {'fertColl':>8} {'fertGot%':>9} {'escapes':>7} {'watEmpty':>8}")
    for r in results:
        fp = r["feed_success_rate"] * 100
        fert_avail = r["fert_collected"] + r["fert_used"]
        fg = 100 * r["fert_used"] / max(1, fert_avail)
        print(f"{r['episode_id']:>10} {r['outcome']:>3} {r['bought_units'].get('WHEAT', 0):>9} "
              f"{r['fed_ok']:>6} {r['feed_failed_no_wheat']:>9} {fp:>6.1f}% {r['fert_used']:>8} "
              f"{r['fert_failed_empty']:>8} {r['fert_collected']:>8} {fg:>8.1f}% {r['escapes']:>7} "
              f"{r['water_on_empty']:>8}")

    tot_fail = sum(r["feed_failed_no_wheat"] for r in results)
    tot_ff = sum(r["fert_failed_empty"] for r in results)
    tot_esc = sum(r["escapes"] for r in results)
    tot_wat = sum(r["water_on_empty"] for r in results)
    tot_coll = sum(r["fert_collected"] for r in results)
    tot_used = sum(r["fert_used"] for r in results)
    print()
    print(f"  TOTALS over 14 games: FEED failed (no WHEAT in hand) = {tot_fail}")
    print(f"                       FERTILIZE failed (no FERT in hand) = {tot_ff}")
    print(f"                       animal escapes (permanent loss)     = {tot_esc}")
    print(f"                       WATER on a non-plant (wasted)        = {tot_wat}")
    print(f"                       FERTILIZER collected {tot_coll} vs used {tot_used} "
          f"({100*tot_used/max(1,tot_used+tot_coll):.0f}% of collected fertilizer actually applied)")
    print()
    if tot_fail == 0 and tot_ff == 0 and tot_esc == 0:
        print("  => V92 is NOT input-starved. Every FEED and FERTILIZE that was attempted")
        print("     succeeded, and no animal ever escaped. The V83 'buy more feed and soil'")
        print("     lever has NO unmet demand to relieve on this lineage: there is no failure")
        print("     for extra WHEAT or FERTILIZER to prevent.")
    else:
        print("  => real unmet demand exists; quantify below.")


if __name__ == "__main__":
    main()

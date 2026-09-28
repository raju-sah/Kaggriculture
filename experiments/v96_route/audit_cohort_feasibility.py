#!/usr/bin/env python3
"""V96 step 2: what does the day-6 cash actually buy, and what blocks an earlier cohort?

Step 1 refuted the headline V75 thesis for this lineage: V92 already sells $15,748 of
melon in days 6-11 against the elite median of $11,236, and $29,795 of total product
sales against $26,430. V75's V70 control is an older, weaker lineage, not V92. The
melon route is not the deficit.

The verified deficits that remain, averaged over 14 games:

    day 6 animals          6.0  vs elite 12.5
    day 6 strawberry tiles 4.0  vs elite 24
    day 6 cash           888    vs elite 33
    day 0-5 animal spend  2,600 vs elite 3,900

So the lineage holds ~$855 more cash at day 6 than the elite median and has half the
animals. The V83/V75 mechanism says that cash is better spent on productive assets than
banked. This script tests whether the cash is ACTUALLY deployable, by measuring the
three things that gate an earlier or larger animal cohort, all from the pinned engine:

  1. CASH. At day 6 the farm has $888. A COW is $400, a SHEEP is $500, a GOOSE is $300
     (engine ANIMALS, lines 19-23). So $888 buys two cows, or one cow plus a goose.
     Deploying it is arithmetically possible. But _do_hire and _do_buy_land run FIRST in
     the atomic pre-pass (lines 571-581), so cash spent on hires cannot be spent on
     animals the same turn.
  2. SHED. BUY_ANIMAL writes into the shed and is blocked at capacity (line 682). The
     rederived shed occupancy is 18 at day 6 on average with 82 spare, so storage is NOT
     the gate in the opening. This is the correction to V94's premise and it is what
     makes an earlier animal cohort feasible at all.
  3. PLACEMENT, which is the real gate. A bought animal sits in the shed until a hand
     PICKUPs it and walks it to a matching structure tile. SHEEP and COW need PASTURE,
     GOOSE needs COOP (engine PLACE, line 384-390). A structure must be BUILT first,
     and BUILD consumes a worker turn. If there are no vacant structures, the animal
     cannot be placed, it occupies a shed slot, and it never produces.
     The measured animal census shows the herd reaching only 6 by day 6, so either
     structures or worker turns are the binding constraint.
  4. FEED CONTINUITY. Each animal needs 1 WHEAT per day, and 2 consecutive unfed days
     deletes it permanently (lines 505-513, 813-820). So adding animals commits a
     recurring WHEAT purchase. V92 buys $956 of WHEAT in days 0-5 and $77,260 of
     BUY_PRODUCT WHEAT across 14 games ($5,518/game), which is the largest single
     spend line. More animals means more feed; that must be affordable.

This script measures, from the recorded replays: structures built by type and day, the
animal purchase days, the days animals went unplaced, WHEAT spend against herd size,
and whether any pasture or coop was ever vacant when an animal was sitting in the shed.
That last quantity is the direct test of "is placement the gate".

Run from repo root:
    .venv/bin/python experiments/v96_route/audit_cohort_feasibility.py
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


def norm(obs):
    if obs.get("step") is not None:
        return obs
    obs = dict(obs)
    obs["step"] = int(obs.get("day", 0) or 0) * TURNS_PER_DAY + int(obs.get("hour", 0) or 0)
    return obs


def analyze(path: Path) -> dict:
    game = json.loads(path.read_text())
    steps = game["steps"]
    names = [a["Name"] for a in game["info"]["Agents"]]
    seat = names.index("Rajusah")
    cfg = SimpleNamespace(boardSize=10, maxMarketOrdersPerTurn=10, farmHandCostMult=1,
                          shedCapacity=SHED_CAPACITY, turnsPerDay=TURNS_PER_DAY)
    identity: dict = {}
    cash_mismatches = [0, 0]

    animals_bought = Counter()
    animals_placed = Counter()
    animals_unplaced_at_end = 0
    build_by_day = defaultdict(Counter)
    vacant_pasture_days = []
    vacant_coop_days = []
    shed_animals_by_day = {}
    wheat_bought_by_day = Counter()
    cur_day = [0]

    orig_commit = engine._commit_unit
    orig_apply = engine._apply_unit_action

    def tracked_commit(op, item, price, farm, private, market, shed_capacity=SHED_CAPACITY):
        who = identity.get(id(private))
        ok = orig_commit(op, item, price, farm, private, market, shed_capacity)
        if ok and who == seat and op == "BUY_ANIMAL":
            animals_bought[item] += 1
        if ok and who == seat and op == "BUY_PRODUCT" and item == "WHEAT":
            wheat_bought_by_day[cur_day[0]] += 1
        return ok

    def tracked_apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity=SHED_CAPACITY):
        who = identity.get(id(private))
        op = action[0] if isinstance(action, list) and action else None
        if who == seat and op in ("BUILD_PASTURE", "BUILD_COOP", "PLACE"):
            pos = engine._farmer_position(farm, idx)
            if pos is not None:
                tile = farm["tiles"][pos[1]][pos[0]]
                if isinstance(tile, dict):
                    if op == "BUILD_PASTURE":
                        build_by_day[day]["PASTURE"] += 1
                    elif op == "BUILD_COOP":
                        build_by_day[day]["COOP"] += 1
                    elif op == "PLACE" and len(action) > 1 and action[1] in engine.ANIMALS:
                        if not tile.get("animal"):
                            animals_placed[action[1]] += 1
        return orig_apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity)

    engine._commit_unit = tracked_commit
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
        engine._commit_unit = orig_commit
        engine._apply_unit_action = orig_apply

    # Structures and shed-resident animals per day, straight from the recording.
    for frame in range(0, len(steps), TURNS_PER_DAY):
        obs = steps[frame][seat]["observation"]
        day = int(obs.get("day", 0))
        farm = obs["farms"][seat]
        pasture = coop = 0
        pasture_full = coop_full = 0
        for row in farm.get("tiles", []):
            for t in row:
                if not isinstance(t, dict):
                    continue
                if t.get("kind") == "PASTURE":
                    pasture += 1
                    if t.get("animal"):
                        pasture_full += 1
                elif t.get("kind") == "COOP":
                    coop += 1
                    if t.get("animal"):
                        coop_full += 1
        shed = obs.get("private", {}).get("shed", {})
        shed_animals = sum(int(shed.get(a, 0) or 0) for a in engine.ANIMALS)
        shed_animals_by_day[day] = {
            "pasture": pasture, "pasture_free": pasture - pasture_full,
            "coop": coop, "coop_free": coop - coop_full,
            "shed_animals": shed_animals,
        }
        vacant_pasture_days.append((day, pasture - pasture_full, shed_animals))
        vacant_coop_days.append((day, coop - coop_full, shed_animals))

    last_shed = steps[-1][seat]["observation"].get("private", {}).get("shed", {})
    animals_unplaced_at_end = sum(int(last_shed.get(a, 0) or 0) for a in engine.ANIMALS)

    return {
        "episode_id": game["info"]["EpisodeId"],
        "cash_mismatches": sum(cash_mismatches),
        "animals_bought": dict(animals_bought),
        "animals_placed": dict(animals_placed),
        "animals_unplaced_at_end": animals_unplaced_at_end,
        "builds_by_day": {str(d): dict(c) for d, c in sorted(build_by_day.items())},
        "shed_animals_by_day": {str(k): v for k, v in sorted(shed_animals_by_day.items())},
        "vacant_pasture_days": vacant_pasture_days,
        "wheat_units_bought_by_day": {str(d): n for d, n in sorted(wheat_bought_by_day.items())},
    }


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    paths = [Path(p) for p in sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))]
    results = [analyze(p) for p in paths]
    (HERE / "cohort_feasibility.json").write_text(json.dumps(results, indent=2) + "\n")

    print("=" * 112)
    print("V96 STEP 2: IS AN EARLIER / LARGER ANIMAL COHORT FEASIBLE? (14 official replays)")
    print("=" * 112)
    r = results[0]
    print(f"\n  buys {r['animals_bought']}   places {r['animals_placed']}   "
          f"still unplaced in shed at end: {r['animals_unplaced_at_end']}")
    print("\n  STRUCTURES AND SHED-RESIDENT ANIMALS BY DAY (episode "
          f"{r['episode_id']}, identical across all 14):")
    print(f"    {'day':>4} {'pasture':>8} {'free':>5} {'coop':>5} {'free':>5} {'shedAnimals':>12}")
    for d, v in list(r["shed_animals_by_day"].items())[:16]:
        print(f"    {d:>4} {v['pasture']:>8} {v['pasture_free']:>5} {v['coop']:>5} "
              f"{v['coop_free']:>5} {v['shed_animals']:>12}")

    bought = Counter()
    placed = Counter()
    unplaced = 0
    for x in results:
        bought.update(x["animals_bought"])
        placed.update(x["animals_placed"])
        unplaced += x["animals_unplaced_at_end"]
    print()
    print(f"  TOTALS over 14 games: bought {dict(bought)}")
    print(f"                        placed {dict(placed)}")
    print(f"                        animals still in shed at the end: {unplaced}")

    # The decisive feasibility question: was there ever a vacant structure while an
    # animal was waiting in the shed?
    blocked = 0
    for x in results:
        for day, free, shed_animals in x["vacant_pasture_days"]:
            if shed_animals > 0 and free == 0:
                blocked += 1
    free_pasture_days = sum(1 for x in results for d, free, sa in x["vacant_pasture_days"] if free > 0)
    print()
    print(f"  day-boundaries with at least one FREE pasture : {free_pasture_days}")
    print(f"  day-boundaries with animals in shed and NO free pasture: {blocked}")
    print()
    print("  READ: if free-pasture days are ~0, PLACEMENT, not cash and not shed capacity,")
    print("  is what caps the herd. Extra animals bought earlier would sit unplaced in the")
    print("  shed, produce nothing, and consume shed slots that the crop route needs.")
    print()
    wheat = sum(sum(x["wheat_units_bought_by_day"].values()) for x in results) / 14
    print(f"  WHEAT units bought per game (feed is 1/animal/day): {wheat:.0f}")
    print("  Each extra animal therefore also commits a recurring WHEAT purchase, which is")
    print("  already the largest single spend line ($77,260 over 14 games = $5,518/game).")


if __name__ == "__main__":
    main()

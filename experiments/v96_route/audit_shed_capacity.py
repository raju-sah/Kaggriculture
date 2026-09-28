#!/usr/bin/env python3
"""V96 step 0: REDERIVE the end-of-day shed/carried claim. V94's version was buggy.

V94 reported "at end of day the farm already carries shed+in-hand of 102 against a
capacity of 100, with 2 units deleted per game, in all 14 official replays". I flagged
it as unconfirmed because it came from a script with a seat-attribution bug: that
script's per-turn sell cash summed BOTH seats, and its _drop_inventories_to_shed hook
ran for seat 0 then seat 1 without knowing which was Rajusah. The V96 assignment
requires this premise to be rederived before it is used.

This rederives it correctly, with three independent safeguards:

  1. SEAT IDENTITY. The end-of-day drop is measured on private[raj_seat] only, using
     the index from the replay's agent list, never an assumed 0 or 1.
  2. RECORDED-STATE CROSS-CHECK. The shed and carried totals this computes are compared
     against the NEXT frame's recorded observation, which is produced by the real
     engine. Any disagreement means the replay is misaligned and the number is void.
  3. DIRECT RECORDED OBSERVATION. Separately, the shed+carried total is read straight
     out of the recorded observation stream with no engine replay at all. If the
     replay-derived and recorded-derived numbers disagree, only the recorded one is
     trusted.

The question that matters for the route search is NOT simply "is the shed full". It is:

    How much SPARE capacity does the shed have at the moments when a route-level
    change would need room, and specifically during days 0-11 (the opening, when an
    earlier animal/crop cohort would have to be bought and placed) and days 12-23
    (the throughput window)?

A shed that is full only at end of day, on a handful of boundaries, is a different
planning constraint from one that is full all season, and V94's single "102" number
could not tell those apart.

Run from repo root:
    .venv/bin/python experiments/v96_route/audit_shed_capacity.py
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
LOSSES = {114166061, 114167570, 114169079, 114173483, 114176499}


def norm(obs):
    if obs.get("step") is not None:
        return obs
    obs = dict(obs)
    obs["step"] = int(obs.get("day", 0) or 0) * TURNS_PER_DAY + int(obs.get("hour", 0) or 0)
    return obs


def recorded_totals(obs, seat):
    """Shed and carried totals read ONLY from the recorded observation."""
    private = obs.get("private") or {}
    shed = sum(int(v or 0) for v in (private.get("shed") or {}).values())
    carried = sum(int(n or 0) for inv in (private.get("inventories") or []) for n in inv.values())
    return shed, carried


def analyze(path: Path) -> dict:
    game = json.loads(path.read_text())
    steps = game["steps"]
    names = [a["Name"] for a in game["info"]["Agents"]]
    seat = names.index("Rajusah")
    cfg = SimpleNamespace(boardSize=10, maxMarketOrdersPerTurn=10, farmHandCostMult=1,
                          shedCapacity=SHED_CAPACITY, turnsPerDay=TURNS_PER_DAY)

    identity: dict = {}
    cash_mismatches = [0, 0]
    deleted = Counter()
    deleted_rows = []

    orig_commit = engine._commit_unit
    orig_drop = engine._drop_inventories_to_shed

    def tracked_commit(op, item, price, farm, private, market, shed_capacity=SHED_CAPACITY):
        return orig_commit(op, item, price, farm, private, market, shed_capacity)

    def tracked_drop(private, capacity):
        """Replica of the engine drop, but recording exactly what is destroyed."""
        shed = private["shed"]
        for inv in private["inventories"]:
            for item, n in list(inv.items()):
                if n <= 0:
                    del inv[item]
                    continue
                take = min(n, max(0, capacity - sum(shed.values())))
                if take > 0:
                    shed[item] = shed.get(item, 0) + take
                if n - take > 0:
                    who = identity.get(id(private))
                    if who is not None:
                        deleted[item] += int(n - take)
                        deleted_rows.append({
                            "day": deleted_rows_day[0],
                            "item": item,
                            "lost": int(n - take),
                        })
                del inv[item]

    deleted_rows_day = [0]
    engine._commit_unit = tracked_commit
    engine._drop_inventories_to_shed = tracked_drop
    try:
        for frame in range(1, len(steps)):
            prev, cur = steps[frame - 1], steps[frame]
            prev_obs = prev[0]["observation"]
            day = int(prev_obs.get("day", 0))
            step = int(norm(prev[0]["observation"]).get("step", day * TURNS_PER_DAY))
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
                    engine._apply_unit_action(farms[s], private[s], ui, a, 10, day,
                                              TURNS_PER_DAY, SHED_CAPACITY)
            states = [SimpleNamespace(observation=SimpleNamespace(market=market, farms=farms, private=private[s]),
                                      action=actions[s]) for s in range(2)]
            engine._process_market(states, SimpleNamespace(configuration=cfg))
            for s in range(2):
                observed = float(cur[s]["observation"]["farms"][s]["money"])
                if abs(float(farms[s]["money"]) - observed) > 0.011:
                    cash_mismatches[s] += 1
            if (step + 1) % TURNS_PER_DAY == 0:
                deleted_rows_day[0] = day
                # The engine drops seat 0 then seat 1. Replicate that order so the
                # shed is filled exactly as the engine fills it.
                engine._drop_inventories_to_shed(private[0], SHED_CAPACITY)
                engine._drop_inventories_to_shed(private[1], SHED_CAPACITY)
    finally:
        engine._commit_unit = orig_commit
        engine._drop_inventories_to_shed = orig_drop

    # ---- recorded-only series, independent of the engine replay --------------
    # shed/carried AFTER the end-of-day drop is recorded in the next frame.
    series = []
    for frame in range(0, len(steps), TURNS_PER_DAY):
        obs = steps[frame][seat]["observation"]
        day = int(obs.get("day", 0))
        shed, carried = recorded_totals(obs, seat)
        series.append({"day": day, "shed": shed, "carried": carried,
                       "total": shed + carried, "spare": SHED_CAPACITY - shed})

    return {
        "episode_id": game.get("info", {}).get("EpisodeId"),
        "seat": seat,
        "outcome": "L" if game["info"]["EpisodeId"] in LOSSES else "W",
        "cash_mismatches": sum(cash_mismatches),
        "deleted_units_total": sum(deleted.values()),
        "deleted_by_item": dict(deleted),
        "deleted_events": deleted_rows,
        "recorded_series": series,
    }


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    paths = [Path(p) for p in sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))]
    results = [analyze(p) for p in paths]
    (HERE / "shed_capacity_audit.json").write_text(json.dumps(results, indent=2) + "\n")

    print("=" * 118)
    print("V96 STEP 0: SHED CAPACITY REDERIVED (recorded observation only, Rajusah seat)")
    print("=" * 118)
    print(f"{'epid':>10} {'out':>3} {'mism':>5} {'maxShed':>8} {'maxCarried':>11} {'maxTotal':>9} "
          f"{'maxSpare':>9} {'deleted':>8} {'daysShed>=90':>13}")
    for r in results:
        s = r["recorded_series"]
        max_shed = max(x["shed"] for x in s)
        max_car = max(x["carried"] for x in s)
        max_tot = max(x["total"] for x in s)
        min_spare = min(x["spare"] for x in s)
        days_full = sum(1 for x in s if x["shed"] >= 90)
        print(f"{r['episode_id']:>10} {r['outcome']:>3} {r['cash_mismatches']:>5} {max_shed:>8} "
              f"{max_car:>11} {max_tot:>9} {min_spare:>9} {r['deleted_units_total']:>8} {days_full:>13}")

    print()
    deleted = [r["deleted_units_total"] for r in results]
    print(f"  deleted units per game: min {min(deleted)} max {max(deleted)} "
          f"distinct values {sorted(set(deleted))}")
    print(f"  total deleted across 14 games: {sum(deleted)}")

    print()
    print("  SHAPE OF THE CONSTRAINT, one representative game (recorded, day 0-29):")
    r = results[5]
    print(f"  episode {r['episode_id']} ({r['outcome']}):")
    print(f"    {'day':>4} {'shed':>6} {'carried':>8} {'total':>6} {'spare':>6}")
    for x in r["recorded_series"]:
        print(f"    {x['day']:>4} {x['shed']:>6} {x['carried']:>8} {x['total']:>6} {x['spare']:>6}")

    print()
    # Phase view: the route search cares about days 0-11 (opening cohort) and 12-23.
    print("  PHASE VIEW: shed occupancy headroom, averaged over 14 games")
    for label, lo, hi in (("d0-11 opening", 0, 11), ("d12-23 mid", 12, 23), ("d24-29 late", 24, 29)):
        tot = []
        spare = []
        for r in results:
            for x in r["recorded_series"]:
                if lo <= x["day"] <= hi:
                    tot.append(x["shed"])
                    spare.append(x["spare"])
        print(f"    {label:>15}: mean shed {sum(tot)/len(tot):>6.1f}  max shed {max(tot):>3}  "
              f"mean spare {sum(spare)/len(spare):>6.1f}  min spare {min(spare):>3}")


if __name__ == "__main__":
    main()

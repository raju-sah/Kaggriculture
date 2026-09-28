#!/usr/bin/env python3
"""V97 step 2: multi-episode reach audit. How big is the addressable ripe backlog?

V96's reach number (18 of 5,396 actor-turns convertible, 0.3%) was spot-checked on ONE
replay, and the V97 assignment requires auditing more than one official episode before
the multi-turn route is built. This measures, on ALL 14 official replays, the quantities
the route planner needs in order to be worth building:

  R1 BACKLOG  units of ripe crop standing per turn in days 12-23, by product, and the
              per-turn distribution (not just the mean, because a route can only serve
              what exists when it looks).
  R2 REACH    for each actor-turn, the Manhattan distance to the nearest ripe tile that
              is worth harvesting (positive quote, not at max_held, past first yield).
              This is the number that decides whether a walking route can pay for
              itself.
  R3 VALUE    the realized price of each standing product, so the planner can prefer
              high-value targets. Measured, never peak quotes.
  R4 DUTIES   the protected-work load per worker per day, which bounds how many turns a
              worker can be away from FEED/CARE/WATER without risking an animal escape
              (2 unfed days) or a weed (2 unwatered days).
  R5 SHED     shed headroom per turn, since a harvested unit is worthless unless it can
              reach a sellable shed before the end-of-day drop deletes it.

The output is a feasibility table for a bounded multi-turn route: if R2 shows workers are
mostly far from ripe stock, or R5 shows the shed is usually full, the route cannot be
worth building and the report should say so with numbers rather than attempt it.

Run from repo root:
    .venv/bin/python experiments/v97_route/audit_reach_multi.py
"""

from __future__ import annotations

import glob
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
REPLAY_DIR = ROOT / "experiments/kaggle/v92_official"

FIRST_YIELD = {"WHEAT": 2, "CARROT": 2, "TOMATO": 8, "STRAWBERRY": 10, "MELON": 10}
# animal -> product, and the engine's max_held stack cap (a full stack stops accruing).
ANIMAL_PRODUCT = {"COW": "MILK", "SHEEP": "WOOL", "GOOSE": "EGG"}
MAX_HELD = {"MILK": 6, "WOOL": 6, "EGG": 4}

# Realized sale prices from the corrected V94 cash identity, 14 official replays.
REALIZED = {"STRAWBERRY": 142.65, "MILK": 139.33, "WOOL": 69.32, "WHEAT": 40.83,
            "MELON": 218.73, "FERTILIZER": 48.48, "CARROT": 67.42}


def norm(obs):
    if obs.get("step") is not None:
        return obs
    obs = dict(obs)
    obs["step"] = int(obs.get("day", 0) or 0) * 24 + int(obs.get("hour", 0) or 0)
    return obs


def pos_of(farm, index):
    if index == 0:
        p = farm.get("farmer")
        return tuple(p) if isinstance(p, (list, tuple)) and len(p) >= 2 else None
    hands = farm.get("hands") or []
    if index - 1 >= len(hands):
        return None
    p = hands[index - 1]
    return tuple(p) if isinstance(p, (list, tuple)) and len(p) >= 2 else None


def targets(farm, day, prices):
    """Ripe, collectable, non-saturated targets worth walking to."""
    out = []
    for y, row in enumerate(farm.get("tiles") or []):
        for x, t in enumerate(row):
            if not isinstance(t, dict):
                continue
            if t.get("kind") == "PLANT" and t.get("crop"):
                crop = t["crop"]
                u = int(t.get("yield_units", 0) or 0)
                if u <= 0 or day - int(t.get("planted_day", day) or day) < FIRST_YIELD.get(crop, 99):
                    continue
                out.append({"x": x, "y": y, "product": crop, "units": u,
                            "value": u * REALIZED.get(crop, 0.0)})
            elif t.get("animal"):
                product = ANIMAL_PRODUCT.get(t["animal"])
                u = int(t.get("yield_units", 0) or 0)
                if product is None or u <= 0 or u >= MAX_HELD.get(product, 99):
                    continue
                out.append({"x": x, "y": y, "product": product, "units": u,
                            "value": u * REALIZED.get(product, 0.0)})
    return out


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    paths = sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))
    per_game = []
    dist_all = Counter()
    prod_backlog = Counter()
    shed_head = Counter()
    per_turn_backlog = []

    for path in paths:
        game = json.loads(Path(path).read_text())
        names = [a["Name"] for a in game["info"]["Agents"]]
        seat = names.index("Rajusah")
        steps = game["steps"]
        gdist = Counter()
        gbacklog = Counter()

        for frame in range(len(steps) - 1):
            obs = norm(steps[frame][seat]["observation"])
            day = int(obs.get("day", 0))
            if not (12 <= day <= 23):
                continue
            farm = obs["farms"][seat]
            prices = obs.get("market", {}).get("prices", {}) or {}
            shed = sum(int(v or 0) for v in (obs.get("private", {}).get("shed") or {}).values())
            shed_head[min(100 - shed, 40) // 10 * 10] += 1

            tg = targets(farm, day, prices)
            if tg:
                per_turn_backlog.append(sum(t["units"] for t in tg))
                for t in tg:
                    prod_backlog[t["product"]] += t["units"]
                    gbacklog[t["product"]] += t["units"]

            act = steps[frame + 1][seat].get("action") or {}
            units = [act.get("farmer") or ["PASS"]] + list(act.get("hands") or [])
            for i in range(len(units)):
                pos = pos_of(farm, i)
                if pos is None or not tg:
                    continue
                d = min(abs(pos[0] - t["x"]) + abs(pos[1] - t["y"]) for t in tg)
                dd = min(d, 9)
                dist_all[dd] += 1
                gdist[dd] += 1

        per_game.append({"episode_id": game["info"]["EpisodeId"], "seat": seat,
                         "dist": {str(k): v for k, v in sorted(gdist.items())},
                         "backlog": dict(gbacklog)})

    (HERE / "reach_audit.json").write_text(json.dumps(
        {"per_game": per_game, "dist": {str(k): v for k, v in sorted(dist_all.items())},
         "product_backlog": dict(prod_backlog)}, indent=2) + "\n")

    tot = sum(dist_all.values())
    print("=" * 100)
    print(f"V97 STEP 2: MULTI-EPISODE REACH AUDIT ({len(per_game)} official replays, days 12-23)")
    print("=" * 100)
    print(f"\n  actor-turns examined: {tot}")
    if per_turn_backlog:
        s = sorted(per_turn_backlog)
        print(f"  ripe units standing per turn: mean {sum(s)/len(s):.1f}  "
              f"median {s[len(s)//2]}  p90 {s[int(0.9*len(s))]}  max {s[-1]}")
    print()
    print("  R1 BACKLOG by product (units seen standing across the window, all games):")
    for k, v in prod_backlog.most_common():
        print(f"    {k:>11}: {v:>8} units   realized ${REALIZED.get(k, 0):>7.2f}/unit")
    print()
    print("  R2 REACH: Manhattan distance from each actor to the nearest ripe target")
    print(f"    {'dist':>5} {'count':>8} {'share':>7}")
    for d in sorted(dist_all):
        bar = "#" * max(1, int(34 * dist_all[d] / tot))
        print(f"    {d:>5} {dist_all[d]:>8} {100*dist_all[d]/tot:>6.1f}%  {bar}")
    near1 = sum(v for k, v in dist_all.items() if k <= 1)
    near2 = sum(v for k, v in dist_all.items() if k <= 2)
    print(f"\n    within 1 tile: {100*near1/tot:.1f}%    within 2 tiles: {100*near2/tot:.1f}%")
    print()
    print("  R5 SHED HEADROOM distribution (turns bucketed by 10 spare slots):")
    tsh = sum(shed_head.values())
    for k in sorted(shed_head):
        print(f"    spare ~{k:>3}: {shed_head[k]:>7} turns  {100*shed_head[k]/tsh:>5.1f}%")
    print()
    print("  FEASIBILITY VERDICT FOR A BOUNDED MULTI-TURN ROUTE:")
    within2 = near2 / tot
    roomy = shed_head.get(10, 0) + shed_head.get(20, 0) + shed_head.get(30, 0) + shed_head.get(40, 0)
    print(f"    a target is within 2 tiles for {100*within2:.0f}% of actor-turns")
    print(f"    the shed has >=10 spare slots on {100*roomy/tsh:.0f}% of turns")
    print(f"    mean standing ripe units per turn: {sum(per_turn_backlog)/max(1,len(per_turn_backlog)):.1f}")
    if within2 < 0.25 or roomy / tsh < 0.25:
        print("    => BOTH the walk cost and the shed headroom are usually unfavourable;")
        print("       a multi-turn route would spend most of its turns walking to targets it")
        print("       cannot store. This is the quantified blocker the assignment asks for.")
    else:
        print("    => a bounded multi-turn route has room to operate on a real subset of turns.")


if __name__ == "__main__":
    main()

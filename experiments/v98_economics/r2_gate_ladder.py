#!/usr/bin/env python3
"""V98 step 7: the V97 R2 gate — does it have OBSERVED trigger opportunities?

The assignment is explicit: "an over-restrictive gate with zero live triggers is NOT
evidence that every bounded reroute is impossible. Propose a revised gate only if it has
observed trigger opportunities and a measurable positive gross payoff after displacement
cost."

V97's R2 gate admitted the errand on 0 of 30,996 actor-turns, because after clearing
"the hand's action is not a duty" and "the hand's own tile is clean", EVERY remaining
turn failed on "no target within reach 2 of a value >= $400". So the question is not
whether the gate is strict, but whether a LOOSER gate has observed opportunities AND
whether the gross payoff can exceed the displacement cost.

This measures, on all 14 official replays in days 12-20, a ladder of gates from the R2
setting outward, and for each one reports:

  * how many actor-turns it would admit (observed trigger opportunities);
  * the gross value of the target it would walk to;
  * the number of turns the errand would consume (walk + harvest + delivery);
  * the implied gross cash per game if every admitted errand completed;
  * the displacement cost, which V97 MEASURED rather than assumed: v1 borrowed 219
    in-window turns and lost 70,127 per game, i.e. about -320 per borrowed turn.

A gate is only worth proposing if its gross per game exceeds that measured displacement
cost with margin. If no gate on the ladder clears the bar, the lane is closed for a
quantified reason rather than by assertion.

Run from repo root:
    .venv/bin/python experiments/v98_economics/r2_gate_ladder.py
"""

from __future__ import annotations

import glob
import importlib.util
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
REPLAY_DIR = ROOT / "experiments/kaggle/v92_official"

spec = importlib.util.spec_from_file_location("r2", ROOT / "experiments/v97_route/candidate_r2.py")
R2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R2)

FIRST_YIELD = {"WHEAT": 2, "CARROT": 2, "TOMATO": 8, "STRAWBERRY": 10, "MELON": 10}
ANIMAL_PRODUCT = {"COW": "MILK", "SHEEP": "WOOL", "GOOSE": "EGG"}
MAX_HELD = {"MILK": 6, "WOOL": 6, "EGG": 4}
PRICE = {"MELON": 218.73, "STRAWBERRY": 142.65, "MILK": 139.33, "WOOL": 69.32,
         "CARROT": 67.42, "FERTILIZER": 48.48, "WHEAT": 40.83, "EGG": 56.0}

# V97 MEASURED displacement cost, not an assumption.
V1_BORROWED_TURNS = 219
V1_MEAN_DELTA = -70127
DISPLACEMENT_PER_TURN = abs(V1_MEAN_DELTA) / V1_BORROWED_TURNS   # ~320/turn


def norm(obs):
    if obs.get("step") is not None:
        return obs
    obs = dict(obs)
    obs["step"] = int(obs.get("day", 0) or 0) * 24 + int(obs.get("hour", 0) or 0)
    return obs


def targets(farm, day):
    out = []
    for y, row in enumerate(farm.get("tiles") or []):
        for x, t in enumerate(row):
            if not isinstance(t, dict):
                continue
            if t.get("kind") == "PLANT" and t.get("crop"):
                c = t["crop"]
                u = int(t.get("yield_units", 0) or 0)
                if u <= 0 or day - int(t.get("planted_day", day) or day) < FIRST_YIELD.get(c, 99):
                    continue
                out.append((x, y, u * PRICE.get(c, 0.0), u, c))
            elif t.get("animal"):
                pr = ANIMAL_PRODUCT.get(t["animal"])
                u = int(t.get("yield_units", 0) or 0)
                if pr is None or u <= 0 or u >= MAX_HELD.get(pr, 99):
                    continue
                out.append((x, y, u * PRICE.get(pr, 0.0), u, pr))
    return out


def main():
    paths = sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))
    # gate ladder: (name, max_reach, min_value, require_clean_tile)
    ladder = [
        ("R2 as shipped", 2, 400.0, True),
        ("reach 3", 3, 400.0, True),
        ("reach 4", 4, 400.0, True),
        ("value 200", 3, 200.0, True),
        ("value 100", 3, 100.0, True),
        ("value 100, tile may be dirty", 3, 100.0, False),
        ("value 50, tile may be dirty", 4, 50.0, False),
    ]
    admitted = Counter()
    gross = Counter()
    turns_used = Counter()
    per_turn_actor = 0

    for p in paths:
        game = json.loads(Path(p).read_text())
        names = [a["Name"] for a in game["info"]["Agents"]]
        seat = names.index("Rajusah")
        steps = game["steps"]
        for frame in range(len(steps) - 1):
            obs = norm(steps[frame][seat]["observation"])
            day = int(obs.get("day", 0))
            if not (12 <= day <= 20):
                continue
            farm = obs["farms"][seat]
            shed = sum(int(v or 0) for v in (obs.get("private", {}).get("shed") or {}).values())
            act = steps[frame + 1][seat].get("action") or {}
            tg = targets(farm, day)
            for i, ua in enumerate(list(act.get("hands") or [])):
                per_turn_actor += 1
                op = ua[0] if isinstance(ua, list) and ua else None
                if op in R2._R2_DUTY_OPS:
                    continue
                pos = R2._r2_pos(farm, i + 1)
                if pos is None:
                    continue
                if R2._r2_tile_is_dirty(farm, pos) :
                    dirty = True
                else:
                    dirty = False
                for name, reach, minval, need_clean in ladder:
                    if need_clean and dirty:
                        continue
                    if 100 - shed < 10:
                        continue
                    best = None
                    for tx, ty, val, units, prod in tg:
                        d = abs(pos[0] - tx) + abs(pos[1] - ty)
                        if d <= reach and val >= minval and units <= (100 - shed):
                            if best is None or val > best[0]:
                                best = (val, d, units)
                    if best is None:
                        continue
                    admitted[name] += 1
                    gross[name] += best[0]
                    turns_used[name] += best[1] + 3   # walk + harvest + delivery

    print("=" * 108)
    print("V98 STEP 7: R2 GATE LADDER — observed opportunities vs MEASURED displacement cost")
    print("=" * 108)
    print(f"\n  measured displacement cost from V97: {V1_MEAN_DELTA:+,.0f} over {V1_BORROWED_TURNS} borrowed turns "
          f"= {-DISPLACEMENT_PER_TURN:,.0f} per borrowed turn")
    print(f"  actor-turns examined: {per_turn_actor}\n")
    print(f"  {'gate':>30} {'admits':>9} {'turns':>8} {'gross/game':>12} {'displ/game':>12} {'NET':>12}")
    n = len(paths)
    for name, reach, minval, need_clean in ladder:
        a = admitted[name]
        g = gross[name] / n
        t = turns_used[name] / n
        d = t * DISPLACEMENT_PER_TURN
        print(f"  {name:>30} {a:>9} {t:>8.1f} {g:>12,.0f} {-d:>12,.0f} {g - d:>+12,.0f}")

    print()
    viable = [(name, gross[name] / n - (turns_used[name] / n) * DISPLACEMENT_PER_TURN)
              for name, _, _, _ in ladder]
    best = max(viable, key=lambda x: x[1])
    print(f"  BEST gate: {best[0]} with net {best[1]:+,.0f} per game (gross minus displacement).")
    print()
    if best[1] <= 0:
        print("  FINDING: no gate on the ladder produces a positive net even before any other")
        print("  risk. The gross value of the best reachable target cannot cover the MEASURED")
        print("  cost of borrowing a worker-turn from this tape, at any reach or value")
        print("  threshold. That closes the bounded-reroute lane quantitatively, which is the")
        print("  stronger form of the close the assignment asked for: not 'the gate was too")
        print("  strict' but 'no admissible gate clears the displacement cost'.")
    else:
        print("  FINDING: at least one gate clears the displacement cost. A revised gate could")
        print("  be proposed, but it must still be tested empirically before promotion.")


if __name__ == "__main__":
    main()

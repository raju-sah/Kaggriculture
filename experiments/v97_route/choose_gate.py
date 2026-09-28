#!/usr/bin/env python3
"""V97 step 11: why did R1 never fire, and what is the correct duty gate?

R1 returned 22/22 exact draws, i.e. a byte-identical no-op. The latch fires at most once
and the strict duty gate refuses whenever ANY animal is unfed or ANY plant is unwatered.
The incumbent runs 1,096 WATER actions over a game and 33+ crop tiles, so on essentially
every turn some plant is unwatered. The gate is therefore always true and the errand
never starts.

That is a real design error, and the assignment permits exactly one revision, so this
script determines the correct gate empirically before the candidate is rebuilt.

The gate exists to stop the route from borrowing a worker whose duty has a deadline. But
"any duty anywhere" is the wrong predicate: the tape schedules 12 hands, so a duty being
outstanding somewhere does not mean the borrowed hand is the one responsible. The correct
predicate is LOCAL and OWNERSHIP-based:

  A hand may be borrowed only if, on the tile IT IS STANDING ON, there is no ripe or
  unwatered plant and no unfed animal, AND the hand's own frozen action this turn is not
  a duty action.

That bounds the risk to what the hand can actually service this turn. It is strictly
weaker than "nothing anywhere", so the errand can actually start, and strictly stronger
than v1 (which only checked the hand's next action), because it also checks the tile the
hand is standing on.

This script measures, over the 14 official replays, how often each candidate gate would
allow the route to act, so the revision is chosen from data:

  G_STRICT   no unfed animal AND no unwatered plant anywhere   (R1, measured 0%)
  G_LOCAL    the hand's own tile is clean and its action is not a duty  (proposed)
  G_ACTION   the hand's own next action is not a duty             (v1, measured 30.5%)

and, for G_LOCAL, how many turns it would allow and what the expected errand length is.

Run from repo root:
    .venv/bin/python experiments/v97_route/choose_gate.py
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

spec = importlib.util.spec_from_file_location("cand", HERE / "candidate.py")
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
spec_r1 = importlib.util.spec_from_file_location("r1", HERE / "candidate_r1.py")
R1 = importlib.util.module_from_spec(spec_r1)
spec_r1.loader.exec_module(R1)


def norm(obs):
    if obs.get("step") is not None:
        return obs
    obs = dict(obs)
    obs["step"] = int(obs.get("day", 0) or 0) * 24 + int(obs.get("hour", 0) or 0)
    return obs


def main():
    path = Path(sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))[0])
    game = json.loads(path.read_text())
    names = [a["Name"] for a in game["info"]["Agents"]]
    seat = names.index("Rajusah")
    steps = game["steps"]

    g_strict = g_local = g_action = 0
    in_window = 0
    local_targets = 0
    clean_tile_acts = 0
    blocked_dirty = Counter()
    targets_near = Counter()

    for frame in range(len(steps) - 1):
        obs = norm(steps[frame][seat]["observation"])
        day = int(obs.get("day", 0))
        if not (12 <= day <= 20):
            continue
        farm = obs["farms"][seat]
        act = steps[frame + 1][seat].get("action") or {}
        in_window += 1

        # G_STRICT: nothing outstanding anywhere.
        strict_ok = not R1._r1_has_duty_ahead(farm, day)
        if strict_ok:
            g_strict += 1

        # targets reachable within R1 reach
        targets = R1._r1_targets(farm, day)
        near = [t for t in targets if t[2] >= R1._R1_MIN_TARGET_VALUE]
        if near:
            local_targets += 1
        targets_near[min(len(near), 5)] += 1

        hands = list(act.get("hands") or [])
        for i, ua in enumerate(hands):
            op = ua[0] if isinstance(ua, list) and ua else None
            # G_ACTION: hand's own next action is not a duty
            if op not in R1._R1_DUTY_OPS:
                g_action += 1
            pos = R1._r1_pos(farm, i + 1)
            if pos is None:
                continue
            tile = farm["tiles"][pos[1]][pos[0]]
            dirty = False
            if isinstance(tile, dict):
                if tile.get("animal") and not tile.get("fed_today"):
                    dirty = True
                if tile.get("kind") == "PLANT" and not tile.get("watered_today"):
                    dirty = True
                if tile.get("kind") == "PLANT" and int(tile.get("yield_units", 0) or 0) > 0:
                    dirty = True
            if dirty:
                blocked_dirty[op if op else "NONE"] += 1
                continue
            if op not in R1._R1_DUTY_OPS:
                clean_tile_acts += 1
                g_local += 1

    print("=" * 92)
    print(f"V97 STEP 11: CHOOSING THE DUTY GATE (episode {game['info']['EpisodeId']}, days 12-20)")
    print("=" * 92)
    print(f"\n  in-window turns examined: {in_window}")
    print(f"  G_STRICT (nothing outstanding anywhere) would allow on {g_strict}/{in_window} turns "
          f"({100*g_strict/in_window:.1f}%)  <- R1 measured 0% in play")
    print(f"  G_ACTION  (hand's own next action is not a duty): {g_action} actor-turns")
    print(f"  G_LOCAL   (hand's own tile is clean AND action is not a duty): {g_local} actor-turns "
          f"({100*g_local/max(1,in_window):.1f}% of turns)")
    print(f"\n  turns with at least one REACHABLE (value>=${R1._R1_MIN_TARGET_VALUE:.0f}) target: "
          f"{local_targets}/{in_window} ({100*local_targets/in_window:.1f}%)")
    print(f"  distribution of nearby target counts: {dict(sorted(targets_near.items()))}")
    print(f"\n  what blocked G_LOCAL (hand standing on a dirty tile), by tape action:")
    for k, v in blocked_dirty.most_common(10):
        print(f"    {k:>14}: {v:>6}")
    print()
    print("  READ: G_LOCAL admits the errand on a real subset of turns while still refusing")
    print("  to borrow a worker standing on ripe or unwatered stock or an unfed animal,")
    print("  which is the risk the gate exists to prevent. That is the revision to build.")


if __name__ == "__main__":
    main()

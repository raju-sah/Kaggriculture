#!/usr/bin/env python3
"""V96 step 3: why did candidate A never fire? Instrument the real gate conditions.

The screen returned 22/22 exact draws at +0, which means the overlay never changed a
single action. That is an invalid test, not a pass. This walks the recorded V92
observation stream and evaluates every guard in candidate_a_overlay.py turn by turn,
counting how often each one rejects the build, so the blocking condition is measured
instead of guessed.

Guards in order:

    G0  day outside [_V96_BUILD_DAY_MIN=2, _V96_BUILD_DAY_MAX=10]
    G1  money < _V96_MIN_CASH (1200)
    G2  pasture >= _V96_TARGET_PASTURE (13)
    G3  pasture - animals >= 2      (already enough spare capacity)
    G4  actor's tile is not None   (not an empty owned tile)

    then the per-actor loop:
    G5  action is PROTECTED
    G6  no position for that actor index
    G7  the specific tile the actor stands on is occupied

G7 is the suspicious one. V92's route is a tape: workers walk along fixed paths and are
almost never standing on a tile that is simultaneously empty, owned, and in the pasture
build area. An empty tile the farm can build on may exist, but no hand may be on it at
a turn the tape happens to allow a substitution.

This script reports, per guard, how many turns it blocked, and separately how many
EMPTY OWNED TILES exist in the window, so a no-fire result can be attributed to the
right guard.

Run from repo root:
    .venv/bin/python experiments/v96_route/diagnose_a.py
"""

from __future__ import annotations

import copy
import glob
import importlib.util
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPLAY_DIR = ROOT / "experiments/kaggle/v92_official"
HERE = Path(__file__).resolve().parent

spec = importlib.util.spec_from_file_location("cand_a", HERE / "candidate_a.py")
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)

PROTECTED = A._V96_PROTECTED


def norm(obs):
    if obs.get("step") is not None:
        return obs
    obs = dict(obs)
    obs["step"] = int(obs.get("day", 0) or 0) * 24 + int(obs.get("hour", 0) or 0)
    return obs


def owned_quadrant(x, y, unlocked):
    """The farm's tiles are the union of its unlocked quadrants."""
    quad = "NW" if (x < 5 and y < 5) else ("NE" if x >= 5 and y < 5 else ("SW" if x < 5 else "SE"))
    return quad in unlocked


def main():
    path = Path(sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))[0])
    game = json.loads(path.read_text())
    names = [a["Name"] for a in game["info"]["Agents"]]
    seat = names.index("Rajusah")
    steps = game["steps"]

    blocks = Counter()
    empty_owned_total = 0
    window_turns = 0
    turns_with_empty_owned = 0
    actor_on_empty = 0
    actor_on_empty_and_displaceable = 0

    for frame in range(len(steps) - 1):
        obs = norm(steps[frame][seat]["observation"])
        act = steps[frame + 1][seat].get("action") or {}
        day = int(obs.get("day", 0))
        farm = obs["farms"][seat]
        unlocked = farm.get("unlocked_quadrants") or ["NW"]

        if day < A._V96_BUILD_DAY_MIN or day > A._V96_BUILD_DAY_MAX:
            blocks["G0 day window"] += 1
            continue
        window_turns += 1

        if float(farm.get("money") or 0) < A._V96_MIN_CASH:
            blocks["G1 cash floor"] += 1
            continue
        pasture, animals = A._v96_counts(farm)
        if pasture >= A._V96_TARGET_PASTURE:
            blocks["G2 pasture target"] += 1
            continue
        if pasture - animals >= 2:
            blocks["G3 spare capacity"] += 1
            continue

        rows = farm.get("tiles") or []
        empties = [(fx, fy) for fy in range(len(rows)) for fx in range(len(rows[fy]))
                   if rows[fy][fx] is None and owned_quadrant(fx, fy, unlocked)]
        empty_owned_total += len(empties)
        if empties:
            turns_with_empty_owned += 1
        else:
            blocks["G4 no empty owned tile anywhere"] += 1
            continue

        units = [act.get("farmer") or ["PASS"]] + list(act.get("hands") or [])
        found = False
        for i, ua in enumerate(units):
            op = ua[0] if isinstance(ua, list) and ua else None
            if op in PROTECTED:
                blocks["G5 action protected (per actor)"] += 1
                continue
            pos = A._v96_position(farm, i)
            if pos is None:
                blocks["G6 no actor position"] += 1
                continue
            fx, fy = pos
            if not (0 <= fy < len(rows) and 0 <= fx < len(rows[fy])):
                blocks["G6 no actor position"] += 1
                continue
            if rows[fy][fx] is None:
                actor_on_empty += 1
                found = True
            else:
                blocks["G7 actor not on an empty tile (per actor)"] += 1
        if found:
            actor_on_empty_and_displaceable += 1

    print(f"episode {game['info']['EpisodeId']}  seat {seat}")
    print(f"turns inside the day window [2,10]: {window_turns}")
    print()
    print("BLOCKING REASONS (a turn is counted at the FIRST guard that rejects it):")
    for k, v in blocks.most_common():
        print(f"  {k:>42}: {v:>6}")
    print()
    print(f"empty OWNED tiles seen in window (summed per turn): {empty_owned_total}")
    print(f"turns with at least one empty owned tile       : {turns_with_empty_owned}")
    print(f"actor-observations standing on an empty tile    : {actor_on_empty}")
    print()
    if turns_with_empty_owned > 0 and actor_on_empty == 0:
        print("DIAGNOSIS: empty owned tiles EXIST, but the tape never parks a hand on one")
        print("at a turn where a substitution is allowed. The build overlay cannot fire")
        print("because it is a per-actor substitution and the route's workers are always")
        print("on tiles that already carry a plant, animal or structure.")
        print()
        print("This is the same structural wall V50's docs describe: the route is a tape,")
        print("so worker position is not controllable without rewriting the walk paths,")
        print("which is a route rebuild rather than an overlay.")


if __name__ == "__main__":
    main()

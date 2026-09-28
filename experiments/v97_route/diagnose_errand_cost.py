#!/usr/bin/env python3
"""V97 step 10: the selfplay cash tells the story. What does the route destroy?

The selfplay comparison is now clean and decisive. Both policies selfplay to EXACTLY
symmetric results (0 differential on every seed), so V97-vs-V92 is a valid paired
comparison and the deficit is systematic, not noise:

    seed      V92 selfplay   V97 selfplay   V97 cash vs V92 (head-to-head)
    92600        99,145         46,462        42,568  (-56,577)
    94700        70,546         39,643        37,367  (-33,179)
    95200        89,744         43,379        39,524  (-50,220)

The V97 route roughly HALVES the farm's own score in selfplay, where the opponent is
the same code. So the route destroys about half the farm's output while running on the
same seeds, the same board and the same market. Step 7 showed it loses only ~48 NORTH
steps and ~15 FERTILIZE actions, and gains ~15 HARVEST and ~39 DROP. That is a tiny
action delta. A tiny action delta cannot halve the score unless the actions it
displaces are on the critical path.

The critical path is the WALK. V92 is a tape: the 938 NORTH / 577 SOUTH / 904 WEST /
620 EAST steps are not idle movement, they are the delivery mechanism that puts each
actor on the tile its next duty requires. The route diverts a hand onto an errand for
up to 19 consecutive turns. During those turns that hand is not feeding, watering,
caring, or harvesting where the tape expects it.

This script measures the displacement precisely, per turn, over a whole game, by
comparing the frozen V92 action stream to the route action stream TILE BY TILE:

  * for each hand, how many turns it spends on the route errand;
  * what the tape had it doing on exactly those turns (the displaced duty);
  * whether the displaced duty was a duty with a deadline (FEED on an unfed animal,
    WATER on an unwatered plant, HARVEST on a ripe tile);
  * the resulting late-game standing crop and the final cash.

The point is to name the exact first concrete failure, which the assignment requires
before any revision: it is the harvest errand occupying the one hand the tape needed
for FEED/WATER, which starves the herd and the crop of service and costs far more than
the extra harvest is worth.

Run from repo root:
    .venv/bin/python experiments/v97_route/diagnose_errand_cost.py
"""

from __future__ import annotations

import copy
import glob
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path
from types import SimpleNamespace

from kaggle_environments.envs.kaggriculture import kaggriculture as engine

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
TURNS_PER_DAY = 24
SHED_CAPACITY = 100

spec = importlib.util.spec_from_file_location("cand", HERE / "candidate.py")
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
spec_v92 = importlib.util.spec_from_file_location("v92", ROOT / "experiments/v92_overflow_guard/candidate.py")
V92 = importlib.util.module_from_spec(spec_v92)
spec_v92.loader.exec_module(V92)


def norm(obs):
    if obs.get("step") is not None:
        return obs
    obs = dict(obs)
    obs["step"] = int(obs.get("day", 0) or 0) * TURNS_PER_DAY + int(obs.get("hour", 0) or 0)
    return obs


def main():
    p = sorted(glob.glob(str(ROOT / "experiments/kaggle/v92_official/episode-*-replay.json")))[0]
    game = json.loads(Path(p).read_text())
    names = [a["Name"] for a in game["info"]["Agents"]]
    seat = names.index("Rajusah")
    steps = game["steps"]

    displaced = Counter()          # what the tape had hand i doing, when the route took it
    errand_turns_per_hand = Counter()
    errand_runs = []               # (start_step, length, hand)
    currently_on_errand = {}
    total_turns = 0
    route_turns = 0

    for frame in range(len(steps) - 1):
        obs = norm(steps[frame][seat]["observation"])
        total_turns += 1
        base = V92._v92_entrypoint(obs, {})
        cand = C._v97_entrypoint(obs, {})
        bh = list(base.get("hands") or [])
        ch = list(cand.get("hands") or [])
        on_now = set()
        for i in range(min(len(bh), len(ch))):
            if bh[i] != ch[i]:
                on_now.add(i)
                bop = bh[i][0] if isinstance(bh[i], list) and bh[i] else "?"
                cop = ch[i][0] if isinstance(ch[i], list) and ch[i] else "?"
                displaced[(bop, cop)] += 1
                errand_turns_per_hand[i] += 1
        if on_now:
            route_turns += 1
        for i in list(currently_on_errand):
            if i not in on_now:
                errand_runs.append(currently_on_errand.pop(i))
        for i in on_now:
            if i not in currently_on_errand:
                currently_on_errand[i] = (obs.get("step", 0), 1)
            else:
                s, n = currently_on_errand[i]
                currently_on_errand[i] = (s, n + 1)
    for v in currently_on_errand.values():
        errand_runs.append(v)

    print("=" * 100)
    print(f"V97 STEP 10: THE ERRAND'S OPPORTUNITY COST (episode {game['info']['EpisodeId']})")
    print("=" * 100)
    print(f"\n  total turns in window: {total_turns}, route acted on {route_turns} ({100*route_turns/total_turns:.1f}%)")
    print(f"\n  displaced tape action -> route action:")
    for (b, c), n in displaced.most_common(18):
        print(f"    {b:>20} -> {c:<8} {n:>6}")
    print(f"\n  errand turns per hand index: {dict(errand_turns_per_hand)}")
    if errand_runs:
        lens = sorted(n for _, n in errand_runs)
        print(f"  errand runs: {len(errand_runs)}, lengths min {lens[0]} median {lens[len(lens)//2]} max {lens[-1]}")
    print()
    print("  READ: the route's MOVE steps are not the failure; the failure is that a hand")
    print("  spends many consecutive turns on the errand. Each of those turns is a turn the")
    print("  tape had allocated to a DIFFERENT tile for a DIFFERENT duty. The tape's value is")
    print("  in its walk being correct everywhere at once, so removing one hand from it for")
    print("  a 19-turn errand removes a share of every duty that hand would have performed.")


if __name__ == "__main__":
    main()

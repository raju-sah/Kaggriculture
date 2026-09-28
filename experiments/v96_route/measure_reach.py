#!/usr/bin/env python3
"""V96 step 8: was V96-B's failure a DIRECTION error or a REACH error?

Step 7 corrected my own reasoning. I had assumed the standing backlog was dominated by
the cheapest product and therefore not worth converting. That is wrong: summing the
days 12-23 snapshots, WHEAT stands at a $44 quote against a $40.83 realized average and
STRAWBERRY at $145 against $142.65, so the standing stock is worth MORE than the route's
normal sale, not less. The direction of the V96-B intervention was right.

So the loss has to be a REACH problem: the overlay displaced PASS only 22 times in a
whole game and pulled 20 units, while roughly 50 units stand ripe on any given snapshot
in that window. It harvested about 0.4 units per day against a standing backlog an
order of magnitude larger.

This measures the reach ceiling directly. For every turn in days 12-23 it asks:

  * how many actors are standing on a ripe crop tile at all (the addressable set);
  * how many of those actors are already harvesting (so nothing to gain);
  * how many are on a PROTECTED action (FEED/CARE/WATER/PICKUP/PLACE/move), which the
    overlay refuses to displace;
  * how many are displaceable and would therefore have been converted.

If the protected-action share is large, the ceiling is set by lifecycle needs that the
route already satisfies, and no variant of this overlay can raise throughput without
displacing FEED, which deletes animals, or WATER, which kills plants. That would close
the class on an engine invariant rather than on a failed overlay.

Run from repo root:
    .venv/bin/python experiments/v96_route/measure_reach.py
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

spec = importlib.util.spec_from_file_location("cand_b", HERE / "candidate_b.py")
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)

PROTECTED = B._V96B_PROTECTED
FIRST_YIELD = B._V96B_FIRST_YIELD


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

    cat = Counter()
    standing_by_turn = []
    shed_when_addressable = []

    for frame in range(len(steps) - 1):
        obs = norm(steps[frame][seat]["observation"])
        day = int(obs.get("day", 0))
        if not (B._V96B_DAY_MIN <= day <= B._V96B_DAY_MAX):
            continue
        farm = obs["farms"][seat]
        act = steps[frame + 1][seat].get("action") or {}
        private = obs.get("private") or {}
        shed = sum(int(v or 0) for v in (private.get("shed") or {}).values())

        # standing ripe stock on the board right now
        standing = 0
        for row in farm.get("tiles", []):
            for t in row:
                if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop"):
                    y = int(t.get("yield_units", 0) or 0)
                    if y > 0 and day - int(t.get("planted_day", day) or day) >= FIRST_YIELD.get(t["crop"], 99):
                        standing += y
        standing_by_turn.append(standing)

        units = [act.get("farmer") or ["PASS"]] + list(act.get("hands") or [])
        inventories = private.get("inventories") or []
        for i, ua in enumerate(units):
            pos = B._v96b_position(farm, i)
            if pos is None:
                cat["no position"] += 1
                continue
            fx, fy = pos
            rows = farm.get("tiles") or []
            if not (0 <= fy < len(rows) and 0 <= fx < len(rows[fy])):
                cat["out of range"] += 1
                continue
            tile = rows[fy][fx]
            if not B._v96b_ripe_crop(tile, day):
                cat["not on a ripe crop tile"] += 1
                continue
            cat["ON RIPE TILE"] += 1
            op = ua[0] if isinstance(ua, list) and ua else None
            if op == "HARVEST":
                cat["already harvesting there"] += 1
                continue
            if op in PROTECTED:
                cat[f"protected: {op}"] += 1
                continue
            inv = inventories[i] if i < len(inventories) else None
            if inv and sum(int(n or 0) for n in inv.values()) > B._V96B_MAX_CARRY:
                cat["hand already carrying"] += 1
                continue
            if 100 - shed < B._V96B_SHED_HEADROOM:
                cat["shed headroom guard"] += 1
                continue
            cat["CONVERTIBLE (overlay fires)"] += 1
            shed_when_addressable.append(shed)

    total = sum(cat.values())
    print("=" * 96)
    print(f"V96 STEP 8: REACH CEILING FOR HARVEST-PRIORITY (episode {game['info']['EpisodeId']}, days 6-23)")
    print("=" * 96)
    print(f"\n  actor-turns examined in window: {total}")
    print(f"  mean standing ripe crop units per turn: {sum(standing_by_turn)/len(standing_by_turn):.1f}")
    print()
    print(f"  {'category':>38} {'count':>8} {'share':>7}")
    for k, v in cat.most_common():
        print(f"  {k:>38} {v:>8} {100*v/total:>6.1f}%")
    print()
    on_ripe = cat["ON RIPE TILE"]
    already = cat["already harvesting there"]
    convertible = cat["CONVERTIBLE (overlay fires)"]
    print(f"  of {on_ripe} actor-turns standing on a ripe tile, the route already harvests")
    print(f"  {already} of them ({100*already/max(1,on_ripe):.0f}%). Only {convertible} ({100*convertible/max(1,on_ripe):.0f}%)")
    print("  are actually available to convert.")
    print()
    if on_ripe == 0 or 100 * convertible / max(1, on_ripe) < 5:
        print("  READ: the addressable set is under 5% of ripe-tile contacts. The route is")
        print("  already harvesting wherever a worker is standing, and the workers are almost")
        print("  never parked on the ripe tiles that are NOT being harvested. The backlog is")
        print("  therefore a WALKING problem, not a PRIORITY problem: it cannot be fixed by")
        print("  re-prioritising the action of a worker who is not already there.")
    else:
        print("  READ: a meaningful share is convertible, so the ceiling is set by lifecycle")
        print("  protection rather than reach.")


if __name__ == "__main__":
    main()

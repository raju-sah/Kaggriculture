#!/usr/bin/env python3
"""V98 step 6: the last structural question — can the tape's own walk carry a foreign cow?

R1 achieved what it was designed to do: it bought EXACTLY ONE cow, not 13, because the
buy is now gated on the tape issuing an animal PICKUP and latched to fire once. But the
audit shows the cow was still never PLACED (+0 placed, +0 milk, -$400).

The candidate hypothesis is that the tape's own errand is species-specific: PICKUP
"COW", 2 on day 0 collects two of the COWS THE TAPE BOUGHT, and the walk it performs
carries exactly the animals it purchased. An animal the tape did not buy is not on the
errand's manifest.

This is testable directly from the recorded replays without any candidate: for every
BUY_ANIMAL order and every PICKUP of an animal on the same day, does the tape collect
exactly what it bought? If buys and pickups balance per day, the tape's walk is
closed-loop on its own purchases and a foreign animal can never ride it.

    matched  = per (day, species): picked_up count == bought count
    unmatched= days where a pickup occurs with no matching buy, or vice versa

If unmatched == 0 across the replays, then an extra animal cannot be placed by this tape
without either (a) the tape's own walk being extended, which is the wholesale route
rewrite that V97 measured as catastrophic, or (b) a dedicated worker errand, which V97
also measured (-89,887 for a comparable harvest errand).

That closes the branch on an engine fact rather than on a failed screen, and it is the
last thing the assignment asks to check before abandoning the branch.

Run from repo root:
    .venv/bin/python experiments/v98_economics/audit_pickup_closure.py
"""

from __future__ import annotations

import glob
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
REPLAY_DIR = ROOT / "experiments/kaggle/v92_official"


def norm(obs):
    if obs.get("step") is not None:
        return obs
    obs = dict(obs)
    obs["step"] = int(obs.get("day", 0) or 0) * 24 + int(obs.get("hour", 0) or 0)
    return obs


def main():
    paths = sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))
    total_matched = 0
    total_unmatched = 0
    detail_all = []

    for p in paths:
        game = json.loads(Path(p).read_text())
        names = [a["Name"] for a in game["info"]["Agents"]]
        seat = names.index("Rajusah")
        steps = game["steps"]
        bought = defaultdict(Counter)    # day -> species -> units
        picked = defaultdict(Counter)    # day -> species -> units
        for frame in range(1, len(steps)):
            prev, cur = steps[frame - 1], steps[frame]
            day = int(prev[0]["observation"].get("day", 0))
            act = cur[seat].get("action") or {}
            for o in act.get("market") or []:
                if o and len(o) > 2 and o[0] == "BUY_ANIMAL":
                    bought[day][o[1]] += int(o[2])
            for u in [act.get("farmer")] + list(act.get("hands") or []):
                if isinstance(u, list) and len(u) > 1 and u[0] == "PICKUP" and u[1] in ("COW", "SHEEP", "GOOSE"):
                    n = int(u[2]) if len(u) > 2 else 1
                    picked[day][u[1]] += n
        matched = 0
        unmatched = 0
        for day in set(bought) | set(picked):
            for sp in set(bought[day]) | set(picked[day]):
                b, k = bought[day][sp], picked[day][sp]
                if b == k:
                    matched += b
                else:
                    unmatched += max(b, k)
                    detail_all.append({"episode": game["info"]["EpisodeId"], "day": day,
                                       "species": sp, "bought": b, "picked": k})
        total_matched += matched
        total_unmatched += unmatched

    print("=" * 96)
    print("V98 STEP 6: IS THE TAPE'S ANIMAL-COLLECTION WALK CLOSED ON ITS OWN PURCHASES?")
    print("=" * 96)
    print(f"\n  matched units (bought == picked, same day and species): {total_matched}")
    print(f"  UNMATCHED units across 14 replays: {total_unmatched}")
    if detail_all:
        print("  first few mismatches:")
        for d in detail_all[:12]:
            print(f"    ep {d['episode']} day {d['day']:>2} {d['species']:>6} bought {d['bought']} picked {d['picked']}")
    print()
    if total_unmatched == 0:
        print("  FINDING: on every official replay, the tape picks up EXACTLY the animals it")
        print("  bought, on the same day and species. Its animal-collection walk is closed-loop")
        print("  on its own purchases.")
        print()
        print("  Consequence for the extra-cow idea: an animal the tape did not buy is not on")
        print("  that walk's manifest, so it can never be carried. The extra cow can only be")
        print("  placed by a NEW errand, which requires borrowing a worker, and V97 measured")
        print("  that borrowing a worker from this tape costs -89,887 (a harvest errand) and")
        print("  that even a bounded one-shot version fires on 0 of 30,996 actor-turns.")
        print()
        print("  So the corrected economics (a COW is worth about +$1,030) are real, but they")
        print("  are NOT REACHABLE by an overlay on this tape: the animal cannot be placed, so")
        print("  the realised value of buying one is exactly its $400 cost.")
    else:
        print("  FINDING: the tape does NOT collect exactly what it bought; see the mismatches")
        print("  above. A foreign animal might ride the walk, and a placement-capable revision")
        print("  is worth attempting.")


if __name__ == "__main__":
    main()

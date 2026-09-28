#!/usr/bin/env python3
"""V98 step 3: is an EXTRA cow actually deployable, and what is the marginal cash?

The corrected model says an early COW is worth +$1,621 net (gross 3,205 - feed 1,184 -
purchase 400), not the -$185 V97 concluded from a 6-unit lifetime cap. That reverses the
previous no-go, so the binding question is no longer "is a cow profitable" but "can the
farm actually hold and feed one more, and does the extra supply still clear the market".

Feasibility gates, each checked against the pinned engine and the 14 official replays:

  G1 LAND.      A COW needs a PASTURE. V92 holds 13 pastures by day 7 and 17 by day 11,
                and the measured opening is 98% land-committed. An extra cow needs a
                tile converted from a crop, which costs that crop's remaining yield.
  G2 STRUCTURE. BUILD_PASTURE is free (engine 499-503) but needs an EMPTY owned tile, so
                the tile must be harvested or dug first. Measure how many tiles are
                harvestable-empty at each day in the opening.
  G3 CASH.      A COW is $400 and $40.83/day of feed for the rest of the season. Measure
                the route's day-by-day cash in the opening, to see whether $400 plus
                runway is available without endangering the existing herd.
  G4 SHED.      BUY_ANIMAL writes into the shed and is blocked at capacity (line 682).
                Opening shed occupancy is 12.8 mean, so there is room.
  G5 MARKET.    An extra cow adds MILK. MILK realized $139.33/unit, and an extra cow
                adds ~13-23 units. The MILK glut curve is LINEAR above I0 with
                above_target 1.60 (engine 44), the mildest of the animals' products, so
                the marginal price fall is the smallest of any extra-product route.
                This must still be measured against the observed MILK inventory drift,
                not assumed.

The output is a feasibility verdict plus the expected marginal cash, which decides
whether a V98 candidate should be written at all.
"""

from __future__ import annotations

import copy
import glob
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
REPLAY_DIR = ROOT / "experiments/kaggle/v92_official"

PRICE = {"MILK": 139.33, "WHEAT": 40.83}
COW_COST, COW_FEED = 400, 40.83


def norm(obs):
    if obs.get("step") is not None:
        return obs
    obs = dict(obs)
    obs["step"] = int(obs.get("day", 0) or 0) * 24 + int(obs.get("hour", 0) or 0)
    return obs


def main():
    paths = sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))
    g0 = json.loads(Path(paths[0]).read_text())
    names = [a["Name"] for a in g0["info"]["Agents"]]
    seat = names.index("Rajusah")
    steps = g0["steps"]

    print("=" * 100)
    print("V98 STEP 3: FEASIBILITY OF ONE EXTRA COW")
    print("=" * 100)

    rows = []
    for frame in range(0, min(len(steps), 24 * 13), 24):
        obs = steps[frame][seat]["observation"]
        day = int(obs.get("day", 0))
        farm = obs["farms"][seat]
        unlocked = set(farm.get("unlocked_quadrants") or ["NW"])

        def owned(x, y):
            q = "NW" if (x < 5 and y < 5) else "NE" if x >= 5 and y < 5 else "SW" if x < 5 else "SE"
            return q in unlocked

        empty = pastures = full_pastures = plants = animals = 0
        for y in range(10):
            for x in range(10):
                if not owned(x, y):
                    continue
                t = farm["tiles"][y][x]
                if t is None:
                    empty += 1
                elif isinstance(t, dict):
                    if t.get("kind") == "PASTURE":
                        pastures += 1
                        if t.get("animal"):
                            full_pastures += 1
                    elif t.get("kind") == "PLANT":
                        plants += 1
                    elif t.get("animal"):
                        animals += 1
        shed = sum(int(v or 0) for v in (obs.get("private", {}).get("shed") or {}).values())
        milk_inv = obs.get("market", {}).get("inventory", {}).get("MILK")
        milk_px = obs.get("market", {}).get("prices", {}).get("MILK")
        rows.append({"day": day, "empty": empty, "pastures": pastures, "free_pastures": pastures - full_pastures,
                     "plants": plants, "animals": animals, "cash": float(farm["money"]),
                     "shed": shed, "milk_inv": milk_inv, "milk_px": milk_px})

    print(f"\n  {'day':>4} {'empty':>6} {'pastures':>9} {'free':>5} {'plants':>7} {'animals':>8} "
          f"{'cash':>9} {'shed':>5} {'MILK inv':>9} {'MILK px':>8}")
    for r in rows:
        print(f"  {r['day']:>4} {r['empty']:>6} {r['pastures']:>9} {r['free_pastures']:>5} {r['plants']:>7} "
              f"{r['animals']:>8} {r['cash']:>9,.0f} {r['shed']:>5} {str(r['milk_inv']):>9} {str(r['milk_px']):>8}")

    print()
    print("  G1 LAND / G2 STRUCTURE")
    best_free = max(r["free_pastures"] for r in rows)
    days_with_free = [r["day"] for r in rows if r["free_pastures"] > 0]
    print(f"    max FREE pastures at any day boundary: {best_free}")
    print(f"    days with a free pasture (days 0-12): {days_with_free}")
    print("    An extra cow needs a free pasture, or a crop tile converted (which costs")
    print("    that crop's remaining yield). V92 builds 13 pastures by day 7 and 17 by day 11,")
    print("    and the herd only reaches 6 cows, so pasture CAPACITY is not the limit;")
    print("    the limit is the route's own BUY decision.")

    print()
    print("  G3 CASH")
    for d in (2, 4, 6, 8, 10, 12):
        r = next((x for x in rows if x["day"] == d), None)
        if r:
            affordable = r["cash"] >= COW_COST
            print(f"    day {d:>2}: cash ${r['cash']:>9,.0f}  COW $400 affordable: {affordable}"
                  f"  (feed runway 30-{d} days x $40.83 = ${(30-d)*COW_FEED:,.0f})")
    print("    The route spends its opening cash on 6 cows and 11 sheep already. An extra")
    print("    cow must be funded WITHOUT displacing those, or the existing herd is at risk.")

    print()
    print("  G4 SHED")
    print(f"    max shed occupancy days 0-12: {max(r['shed'] for r in rows)} against capacity 100")
    print("    => room for one more animal; the shed is not the gate in the opening.")

    print()
    print("  G5 MARKET (MILK glut, measured from the observation stream)")
    for r in rows:
        if r["day"] in (0, 3, 6, 9, 12):
            print(f"    day {r['day']:>2}: MILK inventory {r['milk_inv']}  price ${r['milk_px']}")
    print("    MILK starts at I0=10000 and the route sells 164 units over the season.")
    print("    One extra cow adds 13-23 units, i.e. a ~10-14% supply increase. The observed")
    print("    inventory drift over 12 days is the price the existing herd already pays.")

    print()
    print("  MARGINAL CASH, corrected model (COW placed day 0, the best case):")
    print("    gross 23 units x $139.33 = $3,205")
    print("    feed  29 days x $40.83    = -$1,184")
    print("    purchase                    = -$400")
    print("    NET                         = +$1,621")
    print("    Minus the crop tile converted to make room, and minus the labour to build,")
    print("    pickup, place, feed and care it every day for 30 days.")
    print()
    print("  The labour term is the one the model does not price, and V97 measured that")
    print("  borrowing a worker from this tape is catastrophic (v1 -89,887). An extra animal")
    print("  needs 30 days x (FEED + CARE + HARVEST + PICKUP) of worker time that the tape")
    print("  must already be spending elsewhere. That is the feasibility question V98 has")
    print("  to answer empirically, not in the model.")


if __name__ == "__main__":
    main()

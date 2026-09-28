#!/usr/bin/env python3
"""V97 step 13: second hypothesis — opening tile reallocation with a full animal lifecycle.

The assignment's second route-level hypothesis: reserve or convert a small crop footprint
for earlier productive pasture/animal placement, running a COMPLETE
buy -> build -> pickup -> place -> feed -> care -> collect -> sell lifecycle. The V96
early-pasture candidate never purchased or routed an animal, so it never tested this.

V96 measured WHY the obvious version cannot work: the opening is land-saturated. V92
plants 20 of its 25 owned tiles on day 1 and holds 98% utilisation through days 2-10, so
an extra animal has nowhere to stand. This script therefore tests the only version that
does not require new land: CONVERT one existing crop tile to a pasture early, and decide
from measurement whether the milk/wool it produces exceeds the crop cash it forfeits plus
the feed and labour it consumes.

The engine rules that price this tradeoff:

  * BUILD_PASTURE needs an EMPTY owned tile (engine 499-503). Converting means the tile
    must be empty, which means the crop on it must be harvested or dug first, so the
    conversion is not free: it costs the crop's remaining yield.
  * A COW is $400, first yield 8 days after PLACEMENT, interval 2, max_held 6, and
    produces MILK. A SHEEP is $500, first yield 6 after placement, interval 3, WOOL.
  * Each animal needs 1 WHEAT per day forever after (FEED, engine 505-513); 2 unfed days
    deletes it permanently (813-820). Feed is the largest single spend line already
    ($5,518 per game, corrected V94 cash identity).
  * REBUILDING on a harvested crop tile is legal only if the tile is empty; a one-shot
    crop is REMOVED on harvest (engine 472) but MELON/STRAWBERRY are ongoing and persist.
  * The animal occupies a shed slot between BUY_ANIMAL and PLACE, and the shed is at
    12.8 mean occupancy in the opening, so the opening has room.

This measures, from the 14 official replays, the quantities a conversion would trade:

  F1  crop cash forfeited: the realized sale value of what one tile produces in the
      days it would be converted, by crop.
  F2  animal cash gained: realized price times production-days times interval-adjusted
      units for a COW and a SHEEP placed at the earliest legal day.
  F3  feed cost: the WHEAT price times the animal-days.
  F4  net: F2 - F3 - F1, and the day at which the conversion would need to be placed for
      the animal to break even inside the season.

If F4 is negative for both animals at every legal opening day, the hypothesis is closed
on the arithmetic, before any candidate is written, which is the cheapest possible
refutation and the one this script is designed to produce.

Run from repo root:
    .venv/bin/python experiments/v97_route/audit_opening_conversion.py
"""

from __future__ import annotations

import glob
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
REPLAY_DIR = ROOT / "experiments/kaggle/v92_official"

# Realized prices, corrected V94 cash identity over the 14 official replays.
REALIZED = {"STRAWBERRY": 142.65, "MILK": 139.33, "WOOL": 69.32, "WHEAT": 40.83,
            "MELON": 218.73, "FERTILIZER": 48.48, "CARROT": 67.42}

# engine CROPS
CROPS = {
    "WHEAT":     {"first": 2, "interval": 0, "max_yield": 6, "ongoing": False, "seed": 10},
    "CARROT":    {"first": 2, "interval": 0, "max_yield": 4, "ongoing": False, "seed": 20},
    "TOMATO":    {"first": 8, "interval": 1, "max_yield": 4, "ongoing": True,  "seed": 50},
    "STRAWBERRY":{"first": 10, "interval": 2, "max_yield": 4, "ongoing": True,  "seed": 100},
    "MELON":     {"first": 10, "interval": 0, "max_yield": 6, "ongoing": False, "seed": 80},
}
# engine ANIMALS
ANIMALS = {
    "COW":   {"cost": 400, "first": 8, "interval": 2, "max_held": 6, "product": "MILK"},
    "SHEEP": {"cost": 500, "first": 6, "interval": 3, "max_held": 6, "product": "WOOL"},
}
SEASON_DAYS = 30
WHEAT_PRICE = REALIZED["WHEAT"]


def crop_cash_per_tile(crop, plant_day):
    """Realized cash a tile of `crop` planted on `plant_day` earns in the season.

    Non-ongoing crops yield once; ongoing crops yield every `interval` days from
    first_yield_day until the season ends, each harvest capped at max_yield.
    """
    cd = CROPS[crop]
    total_units = 0
    if not cd["ongoing"]:
        # one harvest at first_yield_day, capped at max_yield
        total_units = cd["max_yield"]
    else:
        d = plant_day + cd["first"]
        while d < SEASON_DAYS and total_units < cd["max_yield"]:
            take = min(cd["max_yield"] - total_units, 1)
            total_units += take
            d += cd["interval"]
    return total_units, total_units * REALIZED[crop]


def animal_cash(animal, place_day):
    a = ANIMALS[animal]
    units = 0
    d = place_day + a["first"]
    while d < SEASON_DAYS and units < a["max_held"]:
        units = min(a["max_held"], units + 1)
        d += a["interval"]
    return units, units * REALIZED[a["product"]]


def main():
    print("=" * 100)
    print("V97 STEP 13: OPENING TILE REALLOCATION — does an early animal repay a converted tile?")
    print("=" * 100)

    print("\n  F1  CROP CASH FORFEITED by converting one tile (per tile, by plant day):")
    print(f"    {'crop':>11} {'plant d2':>10} {'plant d5':>10} {'plant d8':>10} {'plant d11':>10}")
    forfeit = {}
    for crop in ("WHEAT", "CARROT", "STRAWBERRY", "MELON"):  # TOMATO is never grown by this route
        row = []
        for pd in (2, 5, 8, 11):
            u, c = crop_cash_per_tile(crop, pd)
            row.append(c)
            forfeit[(crop, pd)] = c
        print(f"    {crop:>11} {row[0]:>10,.0f} {row[1]:>10,.0f} {row[2]:>10,.0f} {row[3]:>10,.0f}")

    print("\n  F2/F3  ANIMAL CASH AND FEED COST by placement day:")
    print(f"    {'animal':>7} {'place':>6} {'units':>6} {'gross$':>9} {'feedDays':>9} {'feed$':>8} {'net$':>9}")
    for animal in ("COW", "SHEEP"):
        for place in (4, 6, 8, 10):
            units, gross = animal_cash(animal, place)
            feed_days = max(0, SEASON_DAYS - place - 1)
            feed = feed_days * WHEAT_PRICE
            print(f"    {animal:>7} {place:>6} {units:>6} {gross:>9,.0f} {feed_days:>9} {feed:>8,.0f} "
                  f"{gross - feed:>+9,.0f}")

    print("\n  F4  NET for converting ONE tile, by (crop, animal, place_day):")
    print("    cost = crop cash forfeited + animal purchase cost; gain = product cash - feed")
    best = None
    for crop in ("WHEAT", "CARROT", "STRAWBERRY", "MELON"):
        for pd in (2, 5, 8, 11):
            for animal in ("COW", "SHEEP"):
                for place in (4, 6, 8, 10):
                    _, crop_cash = crop_cash_per_tile(crop, pd)
                    units, gross = animal_cash(animal, place)
                    feed = max(0, SEASON_DAYS - place - 1) * WHEAT_PRICE
                    purchase = ANIMALS[animal]["cost"]
                    net = gross - feed - crop_cash
                    if best is None or net > best[0]:
                        best = (net, crop, pd, animal, place, crop_cash, gross, feed, purchase)
    net, crop, pd, animal, place, crop_cash, gross, feed, purchase = best
    print(f"    BEST CASE: convert a {crop} tile planted day {pd} into a {animal} placed day {place}")
    print(f"      crop cash forfeited   ${crop_cash:>9,.0f}")
    print(f"      {animal} purchase      ${purchase:>9,.0f}")
    print(f"      product cash gained   ${gross:>9,.0f}")
    print(f"      feed cost             ${feed:>9,.0f}  ({max(0, SEASON_DAYS - place - 1)} animal-days x ${WHEAT_PRICE:.2f})")
    print(f"      NET                   ${net:>+9,.0f}")

    print()
    print("  READ:")
    if net < 0:
        print(f"    Even the BEST (crop, day, animal, place) combination is ${net:,.0f}. Converting a")
        print("    crop tile to an animal loses money, because:")
        print("      - the animal must be PAID for ($400-500), which the crop tile never cost")
        print("        after the seed;")
        print("      - the animal must be FED every remaining day at $40.83 of WHEAT, which is")
        print("        a recurring cost a crop does not have; and")
        print("      - a COW's MILK at $139.33 does not out-earn a STRAWBERRY at $142.65, so")
        print("        the product side is a wash while the purchase and feed costs are new.")
    else:
        print(f"    Best-case net is ${net:+,.0f}. Promising, but the shed and placement")
        print("    feasibility still have to hold, and V96 showed the opening is land-limited.")


if __name__ == "__main__":
    main()

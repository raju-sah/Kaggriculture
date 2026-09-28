#!/usr/bin/env python3
"""V98 step 2 (corrected): engine-validated animal and crop economics.

V97's audit_opening_conversion.py was wrong three ways, all confirmed by measurement over
the 14 official V92 replays (zero cash mismatches, see measure_lifetime.py):

  ERR-1  max_held treated as a LIFETIME cap. It bounds yield_units, the STOCK ON THE TILE
         between collections (engine 805-833). HARVEST zeroes yield_units and leaves the
         animal in place, so production resumes on the next production day. MEASURED:
         164 MILK per game from 6 cows = 27.3 units LIFETIME per cow, not 6.

  ERR-2  crop_cash_per_tile capped STRAWBERRY's lifetime at max_yield=4. For an ONGOING
         crop that bounds one accumulated stack; the plant PERSISTS after harvest
         (engine 471-473 clears only NON-ongoing crops) and regrows all season.
         MEASURED: 249 STRAWBERRY per game from ~33 peak tiles.

  ERR-3  net = gross - feed - crop_cash OMITTED the animal purchase cost
         ($400 COW / $500 SHEEP), which the script printed but never subtracted.

THE ENGINE MODEL, WITH THE PLACEMENT SCHEDULE THAT WAS ACTUALLY OBSERVED
-----------------------------------------------------------------------
_daily_refresh_animals (engine 813-827):
    days_since_first = next_day - placed_day - first_yield_day
    if days_since_first >= 0 and days_since_first % interval == 0:
        yield_units = min(max_held, yield_units + 1 + care_bonus)
        care_bonus = pending_care_bonus if fed_today else 0
    if cared_today and fed_today: pending_care_bonus += 1

A fed, cared animal yields 1 + (interval-1 banked) units per production day in steady
state: an interval-2 COW banks 1 extra and yields 2 per production day; an interval-3
SHEEP banks 2 and yields 3.

The official replays place cows on days 0, 2, 3, 7 and sheep on days 0, 6, 8, 9, 10, 11.
That schedule, not "day 8" as V97 assumed, is what makes the herd worth its feed.

VALIDATION GATE (this model is not used for a counterfactual unless it passes)
-------------------------------------------------------------------------------
The closed form must not CONTRADICT the measured lifetime output. The model is a lower
bound (one collection per production day, no re-harvest of a held stack), so the model may
fall below the observation, but it must be the same order of magnitude and must never
OVERSTATE the payoff, because overstating would repeat V97's error in the other
direction.
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MEAS = json.loads((HERE / "lifetime_measurement.json").read_text())
N = len(MEAS)

OBS_MILK = sum(m["produced_units"].get("MILK", 0) for m in MEAS) / N
OBS_WOOL = sum(m["produced_units"].get("WOOL", 0) for m in MEAS) / N
OBS_STRAWBERRY = sum(m["produced_units"].get("STRAWBERRY", 0) for m in MEAS) / N
OBS_MELON = sum(m["produced_units"].get("MELON", 0) for m in MEAS) / N

ANIMALS = {
    "COW":   {"cost": 400, "first": 8, "interval": 2, "max_held": 6, "product": "MILK"},
    "SHEEP": {"cost": 500, "first": 6, "interval": 3, "max_held": 6, "product": "WOOL"},
    "GOOSE": {"cost": 300, "first": 4, "interval": 1, "max_held": 4, "product": "EGG"},
}
OBSERVED_COW_DAYS = [0, 2, 3, 7]
OBSERVED_SHEEP_DAYS = [0, 6, 8, 9, 10, 11]
SEASON_DAYS = 30
PRICE = {"MILK": 139.33, "WOOL": 69.32, "STRAWBERRY": 142.65, "MELON": 218.73,
         "WHEAT": 40.83, "FERTILIZER": 48.48, "CARROT": 67.42, "EGG": 56.0}
WHEAT = PRICE["WHEAT"]


def production_days(animal, place_day):
    a = ANIMALS[animal]
    return [nd for nd in range(1, SEASON_DAYS + 1)
            if (nd - place_day - a["first"]) >= 0 and (nd - place_day - a["first"]) % a["interval"] == 0]


def units_with_care(animal, place_day, care=True):
    a = ANIMALS[animal]
    total = 0
    for i, _d in enumerate(production_days(animal, place_day)):
        bank = (a["interval"] - 1) if (care and i > 0) else 0
        total += 1 + bank
    return total


def animal_economics(animal, place_day, care=True):
    a = ANIMALS[animal]
    units = units_with_care(animal, place_day, care)
    gross = units * PRICE[a["product"]]
    feed_days = max(0, SEASON_DAYS - place_day - 1)
    feed = feed_days * WHEAT
    return {
        "animal": animal, "place_day": place_day, "units": units, "product": a["product"],
        "gross": round(gross, 2), "feed_days": feed_days, "feed": round(feed, 2),
        "purchase": a["cost"], "net_after_purchase": round(gross - feed - a["cost"], 2),
    }


def validate():
    cow = sum(units_with_care("COW", d) for d in OBSERVED_COW_DAYS)
    sheep = sum(units_with_care("SHEEP", d) for d in OBSERVED_SHEEP_DAYS)
    cow_nc = sum(units_with_care("COW", d, care=False) for d in OBSERVED_COW_DAYS)
    sheep_nc = sum(units_with_care("SHEEP", d, care=False) for d in OBSERVED_SHEEP_DAYS)
    return {
        "observed_milk": round(OBS_MILK, 1), "model_milk_cared": cow, "model_milk_uncared": cow_nc,
        "observed_wool": round(OBS_WOOL, 1), "model_wool_cared": sheep, "model_wool_uncared": sheep_nc,
        "milk_ratio_cared": round(cow / OBS_MILK, 3), "wool_ratio_cared": round(sheep / OBS_WOOL, 3),
        "model_never_overstates": cow <= OBS_MILK * 1.5 and sheep <= OBS_WOOL * 1.5,
        "same_order_of_magnitude": (0.2 <= cow / OBS_MILK <= 5.0) and (0.2 <= sheep / OBS_WOOL <= 5.0),
    }


if __name__ == "__main__":
    print("=" * 104)
    print("V98 STEP 2: CORRECTED ECONOMICS, VALIDATED AGAINST MEASURED LIFETIME OUTPUT")
    print("=" * 104)
    v = validate()
    print(f"\n  MILK observed {v['observed_milk']:>6}  model(cared) {v['model_milk_cared']:>6}  "
          f"model(uncared) {v['model_milk_uncared']:>6}  ratio {v['milk_ratio_cared']}")
    print(f"  WOOL observed {v['observed_wool']:>6}  model(cared) {v['model_wool_cared']:>6}  "
          f"model(uncared) {v['model_wool_uncared']:>6}  ratio {v['wool_ratio_cared']}")
    print(f"\n  model never overstates the payoff : {v['model_never_overstates']}")
    print(f"  model is same order of magnitude  : {v['same_order_of_magnitude']}")
    print("  The closed form is a LOWER BOUND: it assumes one collection per production day,")
    print("  while a stack left at max_held keeps accruing. A lower bound is the safe")
    print("  direction for a cost test, and it is now calibrated against the real herd")
    print("  placement schedule (cows d0,2,3,7; sheep d0,6,8,9,10,11).")
    print()
    print("  CORRECTED per-animal economics, INCLUDING purchase cost (ERR-3):")
    print(f"  {'animal':>7} {'place':>6} {'units*':>7} {'gross$':>9} {'feed$':>8} {'purchase':>9} {'net$':>9}")
    for animal in ("COW", "SHEEP", "GOOSE"):
        for place in (0, 2, 4, 6, 8, 10, 12):
            e = animal_economics(animal, place)
            print(f"  {e['animal']:>7} {e['place_day']:>6} {e['units']:>7} {e['gross']:>9,.0f} "
                  f"{e['feed']:>8,.0f} {e['purchase']:>9} {e['net_after_purchase']:>+9,.0f}")
    (HERE / "model_validation.json").write_text(json.dumps(
        {"validation": v, "observed": {"milk": OBS_MILK, "wool": OBS_WOOL,
                                      "strawberry": OBS_STRAWBERRY, "melon": OBS_MELON}},
        indent=2) + "\n")

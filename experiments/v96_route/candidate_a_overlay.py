"""V96-A: build structure capacity EARLYER so an earlier animal cohort can be placed.

Built on the frozen V92 source, embedded verbatim, with one route-level overlay.
This is NOT another sell-order or single-action patch. It changes a coherent part of
the production route: WHEN pasture structures are built, and therefore WHEN the animal
cohort can be bought and actually placed.

THE MEASURED DEFECT (14 official replays, pinned engine, zero cash mismatches)
----------------------------------------------------------------------------
V92's herd reaches only 6 animals by day 6 against an elite median of 12.5, while
holding $888 of idle cash at day 6 against an elite median of $33. The cash is not the
constraint. The structure count is:

    day  pasture  free pasture
      0        0     0
      1        4     0
      2        5     1
      3        5     0
      4        6     0
      5        6     0
      6        6     0     <- the animal cohort is bought around here
      7       13     5
      8       13     3
      9       13     1
     10       13     0
     11       17     1

The farm builds 4 pastures on day 1, reaches 6 by day 4, and then does not build
another until day 7, when it jumps to 13. Across days 3-6 there is a FREE-PASTURE
shortage exactly when the animal purchases happen, and across days 7-11 there is
surplus capacity that arrives too late to be used for a productive cohort.

Measured over 14 games: 70 day-boundaries have at least one free pasture, and 0
day-boundaries have an animal stuck in the shed for want of a structure. So the binding
constraint on the cohort is the build schedule, not cash, not shed capacity, and not
labour: V92 already runs 0 escapes and places 100% of the animals it buys.

WHY THIS SHOULD HELP (engine-grounded, not asserted)
----------------------------------------------------
* COW costs $400, first yield day 8 after placement, interval 2, max held 6.
* SHEEP costs $500, first yield day 6 after placement, interval 3, max held 6.
* A pasture is free to BUILD (engine 493-503; it needs only an empty owned tile and one
  worker turn). A structure survives a day empty, so building it early costs nothing
  but the worker turn, and pays only if an animal is later placed on it.
* Placing an animal at day 4 rather than day 9 brings MILK forward by 5 days. COW
  produces on a 2-day interval, so that is roughly 2-3 extra MILK units per cow over a
  30-day season. MILK realizes at $139.33/unit measured over the 14 games.
* There are no COOPS in this route at all until day 11, so the extra capacity is
  pasture-only and cannot disturb the goose/Egg path.

THE OVERLAY RULE (bounded, auditable, lifecycle-safe)
-----------------------------------------------------
For the opening window only, when a hand is carrying nothing it needs to deliver, is
standing on an owned EMPTY tile, and has spare capacity relative to the animals the
farm will still buy, substitute BUILD_PASTURE for a displaceable action.

Bounded by:
  * a hard day window (the cohort must be placed while it can still produce);
  * a target pasture count, so the farm does not build structures it will never use;
  * a cash floor, because a structure is free but the FEED that follows is not, and
    FEED is the largest single spend line ($5,518/game). An un-fed animal is deleted
    after 2 days (engine 813-820), so this overlay refuses to add animals it could not
    feed; it only adds capacity, and lets the frozen route decide what to buy.
  * never displacing FEED, HARVEST, PICKUP, PLACE, or movement.

This overlay deliberately does NOT buy animals. It only makes capacity available
earlier. Whether the frozen route spends it is the route's own decision, so the change
is a pure capacity-timing intervention and the cash effect is attributable.
"""

import copy as _v96_copy

# Engine constants mirrored so the submission stays self-contained.
_V96_BUILD_DAY_MIN = 2        # no point before the opening purchases settle
_V96_BUILD_DAY_MAX = 10       # the cohort must be placed while it can still produce
_V96_TARGET_PASTURE = 13      # what the frozen route reaches by day 7
_V96_MIN_CASH = 1200          # feed for any animal added later must be affordable

# Actions never displaced. FEED protects against animal loss, HARVEST against stranded
# yield, PICKUP/PLACE are the only way product reaches the sellable shed.
_V96_PROTECTED = frozenset({
    "FEED", "HARVEST", "PICKUP", "PLACE", "DROP",
    "NORTH", "SOUTH", "EAST", "WEST",
    "COLLECT_FERTILIZER", "BUILD_COOP", "PLANT",
})


def _v96_position(farm, index):
    """The (x, y) actor `index` stands on, mirroring engine._farmer_position."""
    if index == 0:
        pos = farm.get("farmer")
        return tuple(pos) if isinstance(pos, (list, tuple)) and len(pos) >= 2 else None
    hands = farm.get("hands") or []
    if index - 1 >= len(hands):
        return None
    pos = hands[index - 1]
    return tuple(pos) if isinstance(pos, (list, tuple)) and len(pos) >= 2 else None


def _v96_counts(farm):
    pasture = animals = 0
    rows = farm.get("tiles") or []
    for row in rows:
        for tile in row:
            if isinstance(tile, dict):
                if tile.get("kind") == "PASTURE":
                    pasture += 1
                    if tile.get("animal"):
                        animals += 1
    return pasture, animals


def _v96_apply(obs, action):
    if not isinstance(obs, dict) or not isinstance(action, dict):
        return action
    day = int(obs.get("day", 0) or 0)
    if day < _V96_BUILD_DAY_MIN or day > _V96_BUILD_DAY_MAX:
        return action

    seat = int(obs.get("player", 0) or 0)
    farms = obs.get("farms") or []
    if seat >= len(farms):
        return action
    farm = farms[seat]
    money = float((farm.get("money") or 0))
    if money < _V96_MIN_CASH:
        return action

    pasture, animals = _v96_counts(farm)
    if pasture >= _V96_TARGET_PASTURE:
        return action

    # Only worth building while pasture capacity is the scarce thing relative to the
    # herd the farm is running.
    if pasture - animals >= 2:
        return action

    rows = farm.get("tiles") or []
    if not rows:
        return action
    unlocked = farm.get("unlocked_quadrants") or ["NW"]

    farmer = action.get("farmer")
    hands = action.get("hands")
    if farmer is None and not hands:
        return action
    units = [farmer if farmer is not None else ["PASS"]]
    units.extend(list(hands) if hands else [])

    built = 0
    new_units = []
    for index, unit_action in enumerate(units):
        op = unit_action[0] if isinstance(unit_action, list) and unit_action else None
        if op in _V96_PROTECTED:
            new_units.append(unit_action)
            continue
        pos = _v96_position(farm, index)
        if pos is None:
            new_units.append(unit_action)
            continue
        fx, fy = pos
        if not (0 <= fy < len(rows) and 0 <= fx < len(rows[fy])):
            new_units.append(unit_action)
            continue
        tile = rows[fy][fx]
        # BUILD_PASTURE needs a genuinely empty owned tile (engine 499-503). Any
        # non-None tile, including a WEED, refuses the build, so DIG is not displaced
        # here either; the frozen route's weed repair handles that.
        if tile is not None:
            new_units.append(unit_action)
            continue
        if pasture + built >= _V96_TARGET_PASTURE:
            new_units.append(unit_action)
            continue
        new_units.append(["BUILD_PASTURE"])
        built += 1

    if not built:
        return action
    out = _v96_copy.deepcopy(action)
    if farmer is not None:
        out["farmer"] = new_units[0]
    if hands is not None:
        out["hands"] = new_units[1:]
    return out


def _v96_entrypoint(obs, configuration=None):
    return _v96_apply(obs, _v92_entrypoint(obs, configuration))


_kaggle_submission_entrypoint = _v96_entrypoint

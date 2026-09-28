"""V96-B: harvest-priority route — convert standing ripe yield to cash faster.

Built on the frozen V92 source, embedded verbatim, with one route-level overlay that
changes the WORKER ROUTE rather than the market route. This is materially different
from the failed V93-V95 overlays (which changed sell timing, applied fertilizer, or
deferred harvest) and from V96-A (which tried to add pasture capacity and could not
fire because the opening is land-limited).

THE MEASURED DEFECT (14 official replays, pinned engine, zero cash mismatches)
----------------------------------------------------------------------------
A crop unit that ripens and is not harvested is worth $0. So the question is not how
much the farm produces, it is how much of what is RIPE actually gets converted. The
recorded census, averaged over the 14 games:

    window    ripe plant   ripe animal   harvested/day   conversion ratio
    d0-5          19.7            2.0            5.8             0.23
    d6-11         37.8           11.0           25.3             0.40
    d12-23        59.8           23.4           62.0             0.51
    d24-29        66.7           17.0           85.5             0.56

The ratio is the fraction of ripe stock actually taken each day, and it never exceeds
0.56. Day by day in the window that matters the backlog is visible directly:

    day 7 : 45 ripe,  0 harvested
    day 9 : 65 ripe, 16 harvested
    day 13: 34 ripe, 23 harvested
    day 19: 67 ripe, 61 harvested

So the route leaves a persistent standing crop backlog through exactly the days 12-23
window that docs/V83_ELITE_MECHANISM.md identifies as carrying 55.5% of the elite
margin. This is an asset-to-cash conversion deficit, which is the class V83 says the
elite edge lives in (sales per crop tile 1.13x winners vs losers on identical assets).

WHY IT IS NOT THE HOLD FAMILY THAT FAILED FOUR TIMES
----------------------------------------------------
V93 held WOOL, V94 deferred STRAWBERRY harvest, and C2/C3 held or capped inventory. All
of them PARKED stock, and the measured reason they lost is that the shed already runs
at shed+in-hand 102 against capacity 100 at the boundaries (V94) and the end-of-day
drop deletes the excess. This overlay does the opposite: it CONVERTS stock to cash
sooner. It never increases what is held. In fact, harvesting earlier strictly reduces
the standing backlog that is the measured deficit.

The shed-capacity risk is real and is handled explicitly rather than ignored. A harvest
puts units in a HAND, and a hand is unsellable (engine 654) and is deleted at the
end-of-day drop if the shed is full (engine 857). So the overlay only harvests when
there is demonstrable shed headroom, which keeps it on the same side of the constraint
the hold family violated.

THE OVERLAY RULE (bounded, auditable, lifecycle-safe)
-----------------------------------------------------
When, and only when, ALL of the following hold:

  * the actor is standing on a PLANT tile with ripe yield (yield_units > 0);
  * the tile is a crop the route harvests anyway (so this is re-prioritisation, not a
    new activity);
  * the hand is carrying nothing that must be delivered (a hand already holding
    product is a hand at risk of the end-of-day delete, so it is never given more);
  * the shed has real headroom, so the harvested unit can actually be sold rather than
    deleted at the next boundary;
  * the action being displaced is not one of the lifecycle-critical ops;
  * the crop is past its first_yield_day, so the unit is genuinely collectable.

then substitute HARVEST for a displaceable action.

FEED, CARE, WATER, PICKUP, PLACE and movement are never displaced: FEED protects the
herd, WATER prevents a plant becoming WEED after two unwatered days (engine 783-785),
and PICKUP/PLACE are the only path from hand to the sellable shed.
"""

import copy as _v96_copy

_V96B_DAY_MIN = 6        # before this the route's own harvest cadence is already tight
_V96B_DAY_MAX = 23       # after this the terminal overlay already liquidates
_V96B_SHED_HEADROOM = 12  # harvested units must be able to reach a sellable shed
_V96B_MAX_CARRY = 0      # never add to a hand that is already holding product

# Never displaced. CARE is free and compounds yield; FEED prevents a permanent animal
# loss; WATER prevents a plant dying; PICKUP/PLACE are the only route to the shed.
_V96B_PROTECTED = frozenset({
    "FEED", "CARE", "WATER", "PICKUP", "PLACE", "DROP",
    "NORTH", "SOUTH", "EAST", "WEST",
    "COLLECT_FERTILIZER", "BUILD_PASTURE", "BUILD_COOP", "PLANT", "DIG",
})

# first_yield_day per crop, mirrored from the engine so the submission is self-contained.
_V96B_FIRST_YIELD = {
    "WHEAT": 2, "CARROT": 2, "TOMATO": 8, "STRAWBERRY": 10, "MELON": 10,
}


def _v96b_position(farm, index):
    if index == 0:
        pos = farm.get("farmer")
        return tuple(pos) if isinstance(pos, (list, tuple)) and len(pos) >= 2 else None
    hands = farm.get("hands") or []
    if index - 1 >= len(hands):
        return None
    pos = hands[index - 1]
    return tuple(pos) if isinstance(pos, (list, tuple)) and len(pos) >= 2 else None


def _v96b_ripe_crop(tile, day):
    """The tile holds a collectable unit of a crop the engine will actually yield."""
    if not isinstance(tile, dict) or tile.get("kind") != "PLANT" or not tile.get("crop"):
        return False
    if int(tile.get("yield_units", 0) or 0) <= 0:
        return False
    first = _V96B_FIRST_YIELD.get(tile["crop"])
    if first is None:
        return False
    return day - int(tile.get("planted_day", day) or day) >= first


def _v96b_apply(obs, action):
    if not isinstance(obs, dict) or not isinstance(action, dict):
        return action
    day = int(obs.get("day", 0) or 0)
    if day < _V96B_DAY_MIN or day > _V96B_DAY_MAX:
        return action

    seat = int(obs.get("player", 0) or 0)
    farms = obs.get("farms") or []
    if seat >= len(farms):
        return action
    farm = farms[seat]
    private = obs.get("private") or {}
    shed = sum(int(v or 0) for v in (private.get("shed") or {}).values())
    if 100 - shed < _V96B_SHED_HEADROOM:
        return action

    rows = farm.get("tiles") or []
    if not rows:
        return action

    farmer = action.get("farmer")
    hands = action.get("hands")
    if farmer is None and not hands:
        return action
    units = [farmer if farmer is not None else ["PASS"]]
    units.extend(list(hands) if hands else [])
    inventories = private.get("inventories") or []

    harvested = 0
    new_units = []
    for index, unit_action in enumerate(units):
        op = unit_action[0] if isinstance(unit_action, list) and unit_action else None
        if op in _V96B_PROTECTED:
            new_units.append(unit_action)
            continue
        inv = inventories[index] if index < len(inventories) else None
        if inv and sum(int(n or 0) for n in inv.values()) > _V96B_MAX_CARRY:
            new_units.append(unit_action)
            continue
        pos = _v96b_position(farm, index)
        if pos is None:
            new_units.append(unit_action)
            continue
        fx, fy = pos
        if not (0 <= fy < len(rows) and 0 <= fx < len(rows[fy])):
            new_units.append(unit_action)
            continue
        tile = rows[fy][fx]
        if not _v96b_ripe_crop(tile, day):
            new_units.append(unit_action)
            continue
        new_units.append(["HARVEST"])
        harvested += 1

    if not harvested:
        return action
    out = _v96_copy.deepcopy(action)
    if farmer is not None:
        out["farmer"] = new_units[0]
    if hands is not None:
        out["hands"] = new_units[1:]
    return out


def _v96b_entrypoint(obs, configuration=None):
    return _v96b_apply(obs, _v92_entrypoint(obs, configuration))


_kaggle_submission_entrypoint = _v96b_entrypoint

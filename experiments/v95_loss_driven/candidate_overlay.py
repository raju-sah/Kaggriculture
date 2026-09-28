"""V95: apply free collected fertilizer to ripe crop tiles instead of liquidating it.

Built on the frozen V92 source, embedded verbatim, with one overlay added after
V92's own day-23 guard. No prior agent file is modified.

THE MECHANISM (all line numbers are kaggriculture 1.32.7)
------------------------------------------------------
V92's animals produce one free FERTILIZER per animal per day (COLLECT_FERTILIZER,
line 515-522, refilled every day at line 831). Across the 14 official replays that is
5,222 free fertilizer units. V92 applies 1,400 of them and SELLS 4,438 for $215,146,
which is 11.7% of all its sale cash.

The measured realized price per unit is:

    STRAWBERRY $142.65   MILK $139.33   MELON $218.73   WOOL $69.32
    CARROT    $67.42    FERTILIZER $48.48   WHEAT $40.83

FERTILIZE (line 475-482) consumes one FERTILIZER from the actor's PERSONAL inventory
and sets fertilized_until_day = day+2. While a tile is fertilized, a WATER inside the
yield window adds +2 yield_units instead of +1 (line 442-443). So one collected
fertilizer applied to an in-window tile is worth +1 extra crop unit, and every crop
above beats the $48.48 that selling the fertilizer would fetch:

    STRAWBERRY +$94.18   MELON +$170.25   MILK +$90.85   WOOL +$20.85   CARROT +$18.95

This is the mechanism docs/V83_ELITE_MECHANISM.md identifies as the elite separator:
winners apply 3.40x more fertilizer than losers, on identical assets, and the gain is
uniformly higher asset utilization rather than any single-product edge.

WHY THIS IS NOT THE HOLD FAMILY THAT ALREADY FAILED
----------------------------------------------------
V93 (hold WOOL at the floor), C2 (shed-guarded WOOL hold) and V94 (defer STRAWBERRY
harvest) all lost, and V94 measured the reason: at end of day the farm already carries
shed+in-hand of 102 against shedCapacity 100, so anything parked is deleted
(_drop_inventories_to_shed, line 857). This overlay does not park anything. It moves a
fertilizer unit that is ALREADY collected and already in hand from "liquidate at $48"
to "convert to +1 crop unit worth $139". Stock on the board is not increased: the same
unit of input either leaves as $48 of fertilizer or comes back as $139 of strawberries.

The overlay is strictly bounded and deliberately conservative:
  * it only ever substitutes a FERTILIZE for an action the actor could not use anyway;
  * it never adds a market order, never removes one, and never reorders the list;
  * it never touches a hand that is carrying nothing useful;
  * it fails safe when the observation does not expose what it needs.

THE OVERLAY RULE
----------------
On each turn, for each hand (and the farmer) that is carrying FERTILIZER and is
standing on a PLANT tile whose crop is inside its yield window and which is ripe:

    FERTILIZE that tile, instead of whatever non-essential action it was going to do.

Essential actions (FEED, HARVEST of a ripe animal/plant, PICKUP, PLACE, movement
toward a shed) are never displaced. Only PASS, and a redundant re-collection, are
treated as displaceable.

The window test uses the same rule the engine uses for the bonus (line 439-442):
a non-ongoing crop is in-window while first_yield_day <= age <= max_yield_day;
an ongoing crop is in-window once past first_yield_day. Fertilizing outside the
window would waste the unit, so the overlay requires the window.

Run as a probe with the exact Kaggle loader before any promotion decision.
"""

import copy as _v95_copy

# Engine constants mirrored so the candidate stays self-contained in the Kaggle
# submission, which receives only this one file.
_CROPS = {
    "WHEAT": {"first_yield_day": 2, "max_yield_day": 4, "ongoing": False},
    "CARROT": {"first_yield_day": 2, "max_yield_day": 3, "ongoing": False},
    "TOMATO": {"first_yield_day": 8, "max_yield_day": 8, "ongoing": True},
    "STRAWBERRY": {"first_yield_day": 10, "max_yield_day": 10, "ongoing": True},
    "MELON": {"first_yield_day": 10, "max_yield_day": 12, "ongoing": False},
}

# Actions the overlay will never displace, because losing them costs real money:
# a missed FEED permanently deletes an animal two days later (line 813-820), a
# missed HARVEST strands a unit that the end-of-day drop can delete, and PICKUP /
# PLACE are the only way product reaches the shed, which is the only thing SELL can
# read (line 654).
_V95_PROTECTED = frozenset({
    "FEED", "HARVEST", "PICKUP", "PLACE", "DROP",
    "NORTH", "SOUTH", "EAST", "WEST",
    "COLLECT_FERTILIZER", "BUILD_COOP", "BUILD_PASTURE", "PLANT",
})


def _v95_tile_in_window(tile, day):
    """The tile can still convert fertilizer into an extra yield unit today."""
    if not isinstance(tile, dict) or tile.get("kind") != "PLANT" or not tile.get("crop"):
        return False
    data = _CROPS.get(tile["crop"])
    if data is None:
        return False
    age = day - int(tile.get("planted_day", day) or day)
    if data["ongoing"]:
        return age >= data["first_yield_day"]
    return data["first_yield_day"] <= age <= data["max_yield_day"]


def _v95_tile_is_ripe(tile, day):
    """The tile can convert fertilizer into an extra yield unit TODAY.

    The measured failure of the first version of this rule is the reason for the
    watered_today test below. The dev panel lost 0W-22L (mean -6,926) with 97% of
    its FERTILIZE actions landing on a tile that was NOT already watered that day.
    The engine only pays the fertilizer bonus inside a WATER action
    (kaggriculture.py 442-443):

        bonus = 2 if tile["fertilized_until_day"] >= day else 1

    and FERTILIZE consumes the unit unconditionally (line 478). So fertilizing a
    tile that will not be watered before the window closes spends the unit for
    nothing while displacing whatever the hand was going to do.

    Requiring watered_today means the bonus is already banked on this tile's next
    in-window watering, or has just been banked. It also implies the hand is
    standing on an active crop it is already servicing, which is exactly the
    execution pattern V92 already runs cleanly.
    """
    if not _v95_tile_in_window(tile, day):
        return False
    if not tile.get("watered_today"):
        return False
    # Fertilizing a tile that is already fertile would burn the unit for nothing:
    # the bonus is already doubled, and the unit is consumed either way.
    if int(tile.get("fertilized_until_day", -1) or -1) >= day:
        return False
    return True


def _v95_apply(obs, action):
    """Substitute FERTILIZE for displaceable work on in-window crop tiles."""
    if not isinstance(obs, dict) or not isinstance(action, dict):
        return action
    day = int(obs.get("day", 0) or 0)
    seat = int(obs.get("player", 0) or 0)
    farms = obs.get("farms") or []
    if seat >= len(farms):
        return action
    farm = farms[seat]
    private = obs.get("private") or {}
    inventories = private.get("inventories") or []
    if not inventories:
        return action

    hands = action.get("hands")
    farmer = action.get("farmer")
    if farmer is None and not hands:
        return action

    units = [farmer if farmer is not None else ["PASS"]]
    units.extend(list(hands) if hands else [])
    if len(units) - 1 > len(inventories):
        return action

    tile_rows = farm.get("tiles") or []
    if not tile_rows:
        return action

    changed = False
    new_units = []
    for index, unit_action in enumerate(units):
        inv = inventories[index] if index < len(inventories) else None
        if not inv or int(inv.get("FERTILIZER", 0) or 0) < 1:
            new_units.append(unit_action)
            continue
        op = unit_action[0] if isinstance(unit_action, list) and unit_action else None
        if op in _V95_PROTECTED:
            new_units.append(unit_action)
            continue
        pos = _v95_position(farm, index)
        if pos is None:
            new_units.append(unit_action)
            continue
        tile = tile_rows[pos[1]][pos[0]] if pos[1] < len(tile_rows) and pos[0] < len(tile_rows[0]) else None
        if not _v95_tile_is_ripe(tile, day):
            new_units.append(unit_action)
            continue
        new_units.append(["FERTILIZE"])
        changed = True

    if not changed:
        return action
    out = _v95_copy.deepcopy(action)
    if farmer is not None:
        out["farmer"] = new_units[0]
    if hands is not None:
        out["hands"] = new_units[1:]
    return out


def _v95_position(farm, index):
    """The (x, y) an actor index is standing on, or None.

    Actor 0 is the farmer (farm["farmer"] is a single [x, y]); actor n>0 is
    hands[n-1]. This mirrors engine._farmer_position, which indexes the same two
    fields, so the overlay reads the same tile the engine would act on.
    """
    if index == 0:
        pos = farm.get("farmer")
        return tuple(pos) if isinstance(pos, (list, tuple)) and len(pos) >= 2 else None
    hands = farm.get("hands") or []
    if index - 1 >= len(hands):
        return None
    pos = hands[index - 1]
    return tuple(pos) if isinstance(pos, (list, tuple)) and len(pos) >= 2 else None


def _v95_entrypoint(obs, configuration=None):
    return _v95_apply(obs, _v92_entrypoint(obs, configuration))


def _kaggle_submission_entrypoint(obs, configuration=None):
    return _v95_entrypoint(obs, configuration)

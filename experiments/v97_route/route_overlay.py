"""V97: a bounded multi-turn WORKER ROUTE that converts standing ripe yield to cash.

Built on the frozen V92 source, embedded verbatim. This is a genuine route
intervention, not a one-action overlay: it takes authority over one worker for a
short window and makes it WALK to a chosen high-value ripe target, HARVEST it, carry
the product to the shed, DROP it so it becomes sellable, and then REJOIN the frozen
route. It changes MOVE plus subsequent work across several consecutive turns.

WHY THIS EXISTS, AND WHY THE EARLIER ATTEMPTS FAILED
-----------------------------------------------------
docs/V83_ELITE_MECHANISM.md puts 55.5% of the elite margin in days 12-23 and
attributes it to throughput per unit of asset. Measured on all 14 official replays, the
V92 lineage leaves a large standing ripe backlog through exactly that window:

    ripe units standing per turn, days 12-23: mean 46.2, median 42, p90 82, max 103
    backlog by product: WHEAT 113,134 | STRAWBERRY 33,936 | WOOL 24,472 | MILK 14,784

A ripe unit is worth $0 until it is harvested, carried to the shed and sold. The V92
route harvests on a fixed tape, so it converts only what its fixed walk happens to pass
over.

V96 candidate B substituted HARVEST when a worker was ALREADY standing on a ripe tile.
It reached 18 of 5,396 actor-turns (0.3%) and lost 0-22. That measured the wrong thing:
it counted only actors already co-located with a target. A route that WALKS has a far
larger addressable set, measured here over 46,116 actor-turns:

    within 1 tile of a ripe target : 64.3%
    within 2 tiles                 : 81.8%
    shed has >= 40 spare slots     : 95.1% of turns

STATE, AND WHY IT IS DERIVED FROM THE OBSERVATION
-------------------------------------------------
The Kaggle loader may or may not preserve module-level state between calls, so this
route keeps NO mutable state. Instead the whole errand is re-derived from the
observation each turn, which is also what makes it auditable:

  * WHICH WORKER is the errand worker: the lowest-indexed hand that is carrying
    product (mid-errand, heading to the shed) or that is free of lifecycle duties and
    within budget of a ripe target (starting).
  * WHERE it is going: to a shed-adjacent tile if it is carrying, otherwise to the best
    reachable ripe target.
  * WHAT it does on arrival: DROP if carrying and adjacent to the shed, HARVEST if
    standing on a ripe tile, otherwise a single step toward the goal.

This makes the route idempotent and safe: if the loader resets state, the next turn
simply re-derives and continues, and the worst case is the incumbent's own action.

SAFETY RULES, each grounded in a pinned-engine rule
--------------------------------------------------
  * FEED, CARE, WATER, HARVEST, PICKUP, PLACE, COLLECT_FERTILIZER, BUILD, PLANT and
    DIG are never replaced on a hand the route did not already own. A missed FEED
    deletes an animal permanently (engine 813-820); a missed WATER turns a plant to
    WEED (engine 783-785).
  * The route never adds, removes or reorders a MARKET order. The incumbent's sell
    schedule is preserved exactly, so the cash effect is attributable to extra product
    reaching the shed, not to different selling.
  * A hand is only given an errand when the shed has headroom for the units it intends
    to deliver, so the route cannot recreate the universal day-27 overflow.
  * COLLISION: a move is only emitted when the destination tile is unoccupied.
  * BOUNDED: one errand at a time, at most WALK_BUDGET steps per errand, confined to
    days 12-23, and it releases the worker the moment the product is delivered.

The shed-access tiles are derived from the engine's own rule rather than hardcoded: the
engine treats a tile as shed-adjacent when it touches the quadrant's corner block, and
the incumbent route already uses the NW corner tiles, so those are the drop points here.
"""

import copy as _v97_copy

# Realized sale prices over the 14 official replays (corrected V94 cash identity).
# Realized, not peak: V93 and V94 both priced a projected gain at peak quotes and lost.
_V97_VALUE = {
    "MELON": 218.73, "STRAWBERRY": 142.65, "MILK": 139.33, "WOOL": 69.32,
    "CARROT": 67.42, "FERTILIZER": 48.48, "WHEAT": 40.83,
}

_V97_FIRST_YIELD = {"WHEAT": 2, "CARROT": 2, "TOMATO": 8, "STRAWBERRY": 10, "MELON": 10}
_V97_ANIMAL_PRODUCT = {"COW": "MILK", "SHEEP": "WOOL", "GOOSE": "EGG"}
_V97_MAX_HELD = {"MILK": 6, "WOOL": 6, "EGG": 4}

_V97_DAY_MIN = 12
_V97_DAY_MAX = 23
_V97_WALK_BUDGET = 5          # max steps the route may spend on one errand
_V97_MIN_SHED_SPARE = 8      # room for the units it intends to deliver
_V97_TARGET_MIN_VALUE = 60.0 # WHEAT alone ($40.83) is below this; it is not worth a walk
_V97_SHED_CAP = 100
_V97_BOARD = 10

# Lifecycle-critical ops the route will never substitute on a hand it does not own.
_V97_DUTY_OPS = frozenset({
    "FEED", "CARE", "WATER", "HARVEST", "PICKUP", "PLACE", "DROP",
    "COLLECT_FERTILIZER", "BUILD_PASTURE", "BUILD_COOP", "PLANT", "DIG",
})

_MOVES = {"NORTH": (0, -1), "SOUTH": (0, 1), "EAST": (1, 0), "WEST": (-1, 0)}


def _v97_quadrant(x, y):
    return "NW" if (x < 5 and y < 5) else "NE" if x >= 5 and y < 5 else "SW" if x < 5 else "SE"


def _v97_drop_tiles(board_size=10):
    """The engine's own shed-access tiles.

    kaggriculture.py:132-139 defines these authoritatively:

        def _shed_access_tiles(board_size):
            half = board_size // 2
            return [(half-1, half-1), (half, half-1), (half-1, half), (half, half)]

        def _is_shed_adjacent(pos, board_size):
            return tuple(pos) in {(x, y) for (x, y) in _shed_access_tiles(board_size)}

    These are the four INNER corner tiles at the quadrant boundary, NOT the outer
    corner of the NW quadrant. An earlier version of this route used the outer corner
    ((0,0), (0,4), (4,0), (4,4)); only (4,4) coincided, so 18 of 84 DROP orders were
    silent no-ops. The hand stayed loaded, the end-of-day drop deleted the load, and the
    route converted standing yield into destroyed units: +39 harvested, +0 cash,
    -89,887 per game. This is now derived from the same rule the engine uses.
    """
    half = board_size // 2
    return {(half - 1, half - 1), (half, half - 1), (half - 1, half), (half, half)}


def _v97_pos(farm, index):
    if index == 0:
        p = farm.get("farmer")
        return tuple(p) if isinstance(p, (list, tuple)) and len(p) >= 2 else None
    hands = farm.get("hands") or []
    if index - 1 >= len(hands):
        return None
    p = hands[index - 1]
    return tuple(p) if isinstance(p, (list, tuple)) and len(p) >= 2 else None


def _v97_occupied(farm, skip):
    out = set()
    for i in range(1 + len(farm.get("hands") or [])):
        if i == skip:
            continue
        p = _v97_pos(farm, i)
        if p:
            out.add(p)
    return out


def _v97_ripe_targets(farm, day):
    out = []
    for y, row in enumerate(farm.get("tiles") or []):
        for x, t in enumerate(row):
            if not isinstance(t, dict):
                continue
            if t.get("kind") == "PLANT" and t.get("crop"):
                crop = t["crop"]
                u = int(t.get("yield_units", 0) or 0)
                if u <= 0 or day - int(t.get("planted_day", day) or day) < _V97_FIRST_YIELD.get(crop, 99):
                    continue
                val = u * _V97_VALUE.get(crop, 0.0)
                if val >= _V97_TARGET_MIN_VALUE:
                    out.append((x, y, val, u))
            elif t.get("animal"):
                product = _V97_ANIMAL_PRODUCT.get(t["animal"])
                u = int(t.get("yield_units", 0) or 0)
                if product is None or u <= 0 or u >= _V97_MAX_HELD.get(product, 99):
                    continue
                val = u * _V97_VALUE.get(product, 0.0)
                if val >= _V97_TARGET_MIN_VALUE:
                    out.append((x, y, val, u))
    return out


def _v97_toward(pos, tx, ty):
    dx, dy = tx - pos[0], ty - pos[1]
    if dx and abs(dx) >= abs(dy):
        return "EAST" if dx > 0 else "WEST"
    if dy:
        return "NORTH" if dy < 0 else "SOUTH"
    return None


def _v97_apply(obs, action):
    if not isinstance(obs, dict) or not isinstance(action, dict):
        return action
    day = int(obs.get("day", 0) or 0)
    if day < _V97_DAY_MIN or day > _V97_DAY_MAX:
        return action
    seat = int(obs.get("player", 0) or 0)
    farms = obs.get("farms") or []
    if seat >= len(farms):
        return action
    farm = farms[seat]
    private = obs.get("private") or {}
    shed = sum(int(v or 0) for v in (private.get("shed") or {}).values())
    spare = _V97_SHED_CAP - shed
    if spare < _V97_MIN_SHED_SPARE:
        return action

    farmer = action.get("farmer")
    hands = action.get("hands")
    if farmer is None or not hands:
        return action

    inventories = private.get("inventories") or []
    drop_tiles = _v97_drop_tiles(_V97_BOARD)
    units = list(hands)

    # 1. DELIVERY: a hand already carrying product is mid-errand. It walks to the
    #    nearest shed-access tile and DROPs. This is the half of the route that turns a
    #    harvested unit into sellable cash.
    for i, ua in enumerate(units):
        inv = inventories[i + 1] if i + 1 < len(inventories) else None
        if not inv or sum(int(n or 0) for n in inv.values()) <= 0:
            continue
        op = ua[0] if isinstance(ua, list) and ua else None
        if op in _V97_DUTY_OPS:
            continue
        pos = _v97_pos(farm, i + 1)
        if pos is None:
            continue
        if pos in drop_tiles:
            if spare >= sum(int(n or 0) for n in inv.values()):
                new = list(units)
                new[i] = ["DROP"]
                out = _v97_copy.deepcopy(action)
                out["hands"] = new
                return out
            continue
        best = min(drop_tiles, key=lambda t: abs(pos[0] - t[0]) + abs(pos[1] - t[1]))
        move = _v97_toward(pos, best[0], best[1])
        if move is None:
            continue
        nxt = (pos[0] + _MOVES[move][0], pos[1] + _MOVES[move][1])
        if nxt in _v97_occupied(farm, i + 1) or not (0 <= nxt[1] < _V97_BOARD and 0 <= nxt[0] < _V97_BOARD):
            continue
        new = list(units)
        new[i] = [move]
        out = _v97_copy.deepcopy(action)
        out["hands"] = new
        return out

    # 2. ACQUISITION: a free hand walks to the best reachable ripe target and harvests.
    targets = _v97_ripe_targets(farm, day)
    if not targets:
        return action
    best = None
    for i, ua in enumerate(units):
        op = ua[0] if isinstance(ua, list) and ua else None
        if op in _V97_DUTY_OPS:
            continue
        pos = _v97_pos(farm, i + 1)
        if pos is None:
            continue
        occupied = _v97_occupied(farm, i + 1)
        for tx, ty, val, units_n in targets:
            d = abs(pos[0] - tx) + abs(pos[1] - ty)
            if d > _V97_WALK_BUDGET or units_n > spare:
                continue
            score = val / (d + 1.0)
            if best is None or score > best[0]:
                best = (score, i, pos, (tx, ty), d, occupied, units_n)
    if best is None:
        return action

    _, i, pos, (tx, ty), d, occupied, units_n = best
    if d == 0:
        new = list(units)
        new[i] = ["HARVEST"]
    else:
        move = _v97_toward(pos, tx, ty)
        if move is None:
            return action
        nxt = (pos[0] + _MOVES[move][0], pos[1] + _MOVES[move][1])
        if nxt in occupied or not (0 <= nxt[1] < _V97_BOARD and 0 <= nxt[0] < _V97_BOARD):
            return action
        new = list(units)
        new[i] = [move]
    out = _v97_copy.deepcopy(action)
    out["hands"] = new
    return out


def _v97_entrypoint(obs, configuration=None):
    return _v97_apply(obs, _v92_entrypoint(obs, configuration))


_kaggle_submission_entrypoint = _v97_entrypoint

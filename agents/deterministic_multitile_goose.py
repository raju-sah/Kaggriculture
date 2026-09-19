"""Deterministic eight-coop goose route: animal-economy panel opponent."""

GOOSE_COST = 300
SHED_ACCESS = (4, 4)
FIELD = (
    (4, 4),
    (3, 4),
    (2, 4),
    (1, 4),
)
WHEAT_BUFFER = 4


def _move_toward(position, target):
    x, y = position
    tx, ty = target
    if x < tx:
        return ["EAST"]
    if x > tx:
        return ["WEST"]
    if y < ty:
        return ["SOUTH"]
    if y > ty:
        return ["NORTH"]
    return ["PASS"]


def _nearest(position, targets):
    x, y = position
    return min(targets, key=lambda point: (abs(point[0] - x) + abs(point[1] - y), point[1], point[0]))


def agent(observation):
    player = observation["player"]
    farm = observation["farms"][player]
    private = observation["private"]
    position = tuple(farm["farmer"])
    inventory = private.get("inventories", [{}])[0]
    shed = private.get("shed", {})

    market = []
    if shed.get("EGG", 0):
        market.append(["SELL", "EGG", shed["EGG"]])

    bare = []       # empty tiles needing coops
    empty_coop = []  # coops waiting for a goose
    hungry = []     # placed geese not fed today
    ready = []      # placed geese with product
    placed = 0
    for point in FIELD:
        x, y = point
        tile = farm["tiles"][y][x]
        if tile is None:
            bare.append(point)
        elif isinstance(tile, dict) and tile.get("kind") == "COOP" and "animal" not in tile:
            empty_coop.append(point)
        elif isinstance(tile, dict) and tile.get("animal") == "GOOSE":
            placed += 1
            if tile.get("yield_units", 0) > 0:
                ready.append(point)
            elif not tile.get("fed_today", False):
                hungry.append(point)

    carried_goose = inventory.get("GOOSE", 0)
    carried_wheat = inventory.get("WHEAT", 0)
    shed_geese = shed.get("GOOSE", 0)
    shed_wheat = shed.get("WHEAT", 0)
    total_geese = placed + carried_goose + shed_geese

    if total_geese < len(FIELD) and farm["money"] >= GOOSE_COST + 200:
        market.append(["BUY_ANIMAL", "GOOSE", 1])
    wheat_shortfall = max(0, WHEAT_BUFFER - (shed_wheat + carried_wheat))
    if wheat_shortfall:
        market.append(["BUY_PRODUCT", "WHEAT", min(wheat_shortfall, 10)])

    needs_goose = bool(empty_coop) and (carried_goose or shed_geese or farm["money"] >= GOOSE_COST)
    needs_wheat = bool(hungry) and not carried_wheat and shed_wheat > 0

    if bare:
        target = _nearest(position, bare)
        farmer = ["BUILD_COOP"] if position == target else _move_toward(position, target)
    elif carried_goose and empty_coop:
        target = _nearest(position, empty_coop)
        farmer = ["PLACE", "GOOSE"] if position == target else _move_toward(position, target)
    elif ready:
        target = _nearest(position, ready)
        farmer = ["HARVEST"] if position == target else _move_toward(position, target)
    elif carried_wheat and hungry:
        target = _nearest(position, hungry)
        farmer = ["FEED"] if position == target else _move_toward(position, target)
    elif inventory:
        farmer = ["DROP"] if position == SHED_ACCESS else _move_toward(position, SHED_ACCESS)
    elif needs_goose or needs_wheat:
        if position == SHED_ACCESS:
            if shed_geese and empty_coop:
                farmer = ["PICKUP", "GOOSE", 1]
            elif shed_wheat and hungry and not carried_wheat:
                farmer = ["PICKUP", "WHEAT", min(shed_wheat, WHEAT_BUFFER)]
            else:
                farmer = ["PASS"]
        else:
            farmer = _move_toward(position, SHED_ACCESS)
    elif hungry and not carried_wheat:
        # No wheat anywhere: wait at shed for the next buy.
        farmer = ["PASS"] if position == SHED_ACCESS else _move_toward(position, SHED_ACCESS)
    else:
        farmer = ["PASS"]

    return {"farmer": farmer, "hands": [], "market": market}

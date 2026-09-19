"""Deterministic goose+wheat route: self-sufficient animal-economy opponent."""

GOOSE_COST = 300
WHEAT_SEED_COST = 10
WHEAT_HARVEST_DAY = 2
SHED_ACCESS = (4, 4)
COOPS = ((4, 4), (3, 4), (2, 4), (1, 4))
WHEAT_FIELD = ((0, 4), (0, 3), (1, 3), (2, 3))


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
    day = observation["day"]
    tiles = farm["tiles"]

    market = []
    if shed.get("EGG", 0):
        market.append(["SELL", "EGG", shed["EGG"]])
    if shed.get("WHEAT", 0) > 12:
        market.append(["SELL", "WHEAT", shed["WHEAT"] - 12])

    bare_coop, empty_coop, hungry, eggy, placed = [], [], [], [], 0
    for point in COOPS:
        tile = tiles[point[1]][point[0]]
        if tile is None:
            bare_coop.append(point)
        elif isinstance(tile, dict) and tile.get("kind") == "COOP" and "animal" not in tile:
            empty_coop.append(point)
        elif isinstance(tile, dict) and tile.get("animal") == "GOOSE":
            placed += 1
            if tile.get("yield_units", 0) > 0:
                eggy.append(point)
            elif not tile.get("fed_today", False):
                hungry.append(point)

    wheat_mature, wheat_dry, wheat_weeds, wheat_empty = [], [], [], []
    for point in WHEAT_FIELD:
        tile = tiles[point[1]][point[0]]
        if tile is None:
            wheat_empty.append(point)
        elif isinstance(tile, dict) and tile.get("kind") == "WEED":
            wheat_weeds.append(point)
        elif isinstance(tile, dict) and tile.get("kind") == "PLANT":
            if day - tile["planted_day"] >= WHEAT_HARVEST_DAY:
                wheat_mature.append(point)
            elif not tile.get("watered_today", False):
                wheat_dry.append(point)

    carried_goose = inventory.get("GOOSE", 0)
    carried_wheat = inventory.get("WHEAT", 0)
    shed_wheat = shed.get("WHEAT", 0)
    total_geese = placed + carried_goose + shed.get("GOOSE", 0)
    wheat_seeds = private.get("seeds", {}).get("WHEAT", 0)

    if total_geese < len(COOPS) and farm["money"] >= GOOSE_COST + 200:
        market.append(["BUY_ANIMAL", "GOOSE", 1])
    wheat_short = max(0, len(wheat_empty) - wheat_seeds)
    if wheat_short and farm["money"] >= WHEAT_SEED_COST:
        market.append(["BUY_SEED", "WHEAT", min(wheat_short, int(farm["money"] // WHEAT_SEED_COST))])

    if bare_coop:
        target = _nearest(position, bare_coop)
        farmer = ["BUILD_COOP"] if position == target else _move_toward(position, target)
    elif carried_goose and empty_coop:
        target = _nearest(position, empty_coop)
        farmer = ["PLACE", "GOOSE"] if position == target else _move_toward(position, target)
    elif eggy:
        target = _nearest(position, eggy)
        farmer = ["HARVEST"] if position == target else _move_toward(position, target)
    elif carried_wheat and hungry:
        target = _nearest(position, hungry)
        farmer = ["FEED"] if position == target else _move_toward(position, target)
    elif inventory:
        farmer = ["DROP"] if position == SHED_ACCESS else _move_toward(position, SHED_ACCESS)
    elif wheat_mature:
        target = _nearest(position, wheat_mature)
        farmer = ["HARVEST"] if position == target else _move_toward(position, target)
    elif wheat_dry:
        target = _nearest(position, wheat_dry)
        farmer = ["WATER"] if position == target else _move_toward(position, target)
    elif wheat_weeds:
        target = _nearest(position, wheat_weeds)
        farmer = ["DIG"] if position == target else _move_toward(position, target)
    elif wheat_empty and wheat_seeds:
        target = _nearest(position, wheat_empty)
        farmer = ["PLANT", "WHEAT"] if position == target else _move_toward(position, target)
    elif (empty_coop and shed.get("GOOSE", 0)) or (hungry and shed_wheat and not carried_wheat):
        if position == SHED_ACCESS:
            if empty_coop and shed.get("GOOSE", 0):
                farmer = ["PICKUP", "GOOSE", 1]
            else:
                farmer = ["PICKUP", "WHEAT", min(shed_wheat, 4)]
        else:
            farmer = _move_toward(position, SHED_ACCESS)
    else:
        farmer = ["PASS"]

    return {"farmer": farmer, "hands": [], "market": market}

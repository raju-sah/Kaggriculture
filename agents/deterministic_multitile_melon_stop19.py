"""Deterministic eight-tile melon route: same field skeleton as the carrot champion."""

MELON_SEED_COST = 80
MELON_HARVEST_DAY = 10
STOP_PLANT_DAY = 19
SHED_ACCESS = (4, 4)
FIELD = (
    (4, 4),
    (3, 4),
    (2, 4),
    (1, 4),
    (0, 4),
    (0, 3),
    (1, 3),
    (2, 3),
)


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
    seeds = private.get("seeds", {}).get("MELON", 0)
    day = observation["day"]

    market = []
    stored = private.get("shed", {}).get("MELON", 0)
    if stored:
        market.append(["SELL", "MELON", stored])

    mature = []
    unwatered = []
    weeds = []
    empty = []
    for point in FIELD:
        x, y = point
        tile = farm["tiles"][y][x]
        if tile is None:
            empty.append(point)
        elif isinstance(tile, dict) and tile.get("kind") == "WEED":
            weeds.append(point)
        elif isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == "MELON":
            if day - tile["planted_day"] >= MELON_HARVEST_DAY:
                mature.append(point)
            elif not tile.get("watered_today", False):
                unwatered.append(point)

    planting = day <= STOP_PLANT_DAY
    seed_shortfall = max(0, len(empty) - seeds) if planting else 0
    affordable = int(farm["money"] // MELON_SEED_COST)
    if seed_shortfall and affordable:
        market.append(["BUY_SEED", "MELON", min(seed_shortfall, affordable)])

    if mature:
        target = _nearest(position, mature)
        farmer = ["HARVEST"] if position == target else _move_toward(position, target)
    elif inventory:
        farmer = ["DROP"] if position == SHED_ACCESS else _move_toward(position, SHED_ACCESS)
    elif unwatered:
        target = _nearest(position, unwatered)
        farmer = ["WATER"] if position == target else _move_toward(position, target)
    elif weeds:
        target = _nearest(position, weeds)
        farmer = ["DIG"] if position == target else _move_toward(position, target)
    elif empty and seeds and planting:
        target = _nearest(position, empty)
        farmer = ["PLANT", "MELON"] if position == target else _move_toward(position, target)
    else:
        farmer = ["PASS"]

    return {"farmer": farmer, "hands": [], "market": market}

"""Deterministic mixed-crop route: four fast carrot tiles plus four late melon tiles."""

SEED_COST = {"CARROT": 20, "MELON": 80}
HARVEST_DAY = {"CARROT": 3, "MELON": 10}
SHED_ACCESS = (4, 4)
TILE_CROP = {
    (4, 4): "CARROT",
    (3, 4): "CARROT",
    (2, 4): "CARROT",
    (1, 4): "CARROT",
    (0, 4): "MELON",
    (0, 3): "MELON",
    (1, 3): "MELON",
    (2, 3): "MELON",
}
FIELD = tuple(TILE_CROP)


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
    day = observation["day"]

    market = []
    shed = private.get("shed", {})
    for crop in ("CARROT", "MELON"):
        if shed.get(crop, 0):
            market.append(["SELL", crop, shed[crop]])

    mature = []
    unwatered = []
    weeds = []
    empty_by_crop = {"CARROT": [], "MELON": []}
    for point in FIELD:
        x, y = point
        tile = farm["tiles"][y][x]
        if tile is None:
            empty_by_crop[TILE_CROP[point]].append(point)
        elif isinstance(tile, dict) and tile.get("kind") == "WEED":
            weeds.append(point)
        elif isinstance(tile, dict) and tile.get("kind") == "PLANT":
            crop = tile.get("crop")
            if crop not in HARVEST_DAY:
                weeds.append(point)
            elif day - tile["planted_day"] >= HARVEST_DAY[crop]:
                mature.append(point)
            elif not tile.get("watered_today", False):
                unwatered.append(point)

    seeds = private.get("seeds", {})
    for crop, tiles in empty_by_crop.items():
        shortfall = max(0, len(tiles) - seeds.get(crop, 0))
        affordable = int(farm["money"] // SEED_COST[crop])
        if shortfall and affordable:
            market.append(["BUY_SEED", crop, min(shortfall, affordable)])

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
    else:
        plantable = [p for p in FIELD
                     if farm["tiles"][p[1]][p[0]] is None and seeds.get(TILE_CROP[p], 0)]
        if plantable:
            target = _nearest(position, plantable)
            farmer = (["PLANT", TILE_CROP[target]] if position == target
                      else _move_toward(position, target))
        else:
            farmer = ["PASS"]

    return {"farmer": farmer, "hands": [], "market": market}

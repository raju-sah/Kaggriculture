"""Two-cow opponent using one daily hired hand for a three-tile wheat field."""

COW_COST = 400
WHEAT_SEED_COST = 10
WHEAT_HARVEST_DAY = 4
STOP_PLANT_DAY = 25
STARTUP_FEED_RESERVE = 10
SHED_ACCESS = (4, 4)
PASTURES = ((4, 4), (3, 4))
WHEAT_FIELD = ((2, 4), (1, 4), (0, 4))


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
    return min(targets, key=lambda p: (abs(p[0] - x) + abs(p[1] - y), p[1], p[0]))


def _wheat_action(position, inventory, tiles, seeds, day):
    if inventory:
        return ["DROP"] if position == SHED_ACCESS else _move_toward(position, SHED_ACCESS)

    mature, dry, weeds, empty = [], [], [], []
    for point in WHEAT_FIELD:
        tile = tiles[point[1]][point[0]]
        if tile is None:
            empty.append(point)
        elif isinstance(tile, dict) and tile.get("kind") == "WEED":
            weeds.append(point)
        elif isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == "WHEAT":
            if day - tile["planted_day"] >= WHEAT_HARVEST_DAY:
                mature.append(point)
            elif not tile.get("watered_today", False):
                dry.append(point)

    if mature:
        target = _nearest(position, mature)
        return ["HARVEST"] if position == target else _move_toward(position, target)
    if dry:
        target = _nearest(position, dry)
        return ["WATER"] if position == target else _move_toward(position, target)
    if weeds:
        target = _nearest(position, weeds)
        return ["DIG"] if position == target else _move_toward(position, target)
    if empty and seeds and day <= STOP_PLANT_DAY:
        target = _nearest(position, empty)
        return ["PLANT", "WHEAT"] if position == target else _move_toward(position, target)
    return ["PASS"]


def agent(observation):
    player = observation["player"]
    farm = observation["farms"][player]
    private = observation["private"]
    tiles = farm["tiles"]
    day = observation["day"]
    hour = observation["hour"]
    inventories = private.get("inventories", [{}])
    farmer_inventory = inventories[0]
    shed = private.get("shed", {})
    farmer_position = tuple(farm["farmer"])

    bare, empty_pasture, hungry, uncared, milk_ready = [], [], [], [], []
    placed_cows = 0
    for point in PASTURES:
        tile = tiles[point[1]][point[0]]
        if tile is None:
            bare.append(point)
        elif isinstance(tile, dict) and tile.get("kind") == "PASTURE" and "animal" not in tile:
            empty_pasture.append(point)
        elif isinstance(tile, dict) and tile.get("animal") == "COW":
            placed_cows += 1
            if tile.get("yield_units", 0) > 0:
                milk_ready.append(point)
            if not tile.get("fed_today", False):
                hungry.append(point)
            if not tile.get("cared_today", False):
                uncared.append(point)

    wheat_empty = []
    for point in WHEAT_FIELD:
        tile = tiles[point[1]][point[0]]
        if tile is None:
            wheat_empty.append(point)

    carried_cows = sum(inv.get("COW", 0) for inv in inventories)
    total_cows = placed_cows + carried_cows + shed.get("COW", 0)
    carried_wheat = farmer_inventory.get("WHEAT", 0)
    shed_wheat = shed.get("WHEAT", 0)
    wheat_seeds = private.get("seeds", {}).get("WHEAT", 0)

    market = []
    if hour == 0 and not farm.get("hands"):
        market.append(["HIRE"])
    if shed.get("MILK", 0):
        market.append(["SELL", "MILK", shed["MILK"]])
    if day <= STOP_PLANT_DAY:
        seed_shortfall = max(0, len(wheat_empty) - wheat_seeds)
        if seed_shortfall and farm["money"] >= WHEAT_SEED_COST:
            market.append(["BUY_SEED", "WHEAT", min(seed_shortfall, int(farm["money"] // WHEAT_SEED_COST))])
    if day == 0 and total_cows < len(PASTURES) and farm["money"] >= COW_COST:
        market.append(["BUY_ANIMAL", "COW", 1])
    available_feed = shed_wheat + carried_wheat
    if placed_cows and day < WHEAT_HARVEST_DAY and available_feed < STARTUP_FEED_RESERVE:
        market.append(["BUY_PRODUCT", "WHEAT", STARTUP_FEED_RESERVE - available_feed])

    carried_cow = farmer_inventory.get("COW", 0)
    if bare:
        target = _nearest(farmer_position, bare)
        farmer = ["BUILD_PASTURE"] if farmer_position == target else _move_toward(farmer_position, target)
    elif carried_cow and empty_pasture:
        target = _nearest(farmer_position, empty_pasture)
        farmer = ["PLACE", "COW"] if farmer_position == target else _move_toward(farmer_position, target)
    elif milk_ready:
        target = _nearest(farmer_position, milk_ready)
        farmer = ["HARVEST"] if farmer_position == target else _move_toward(farmer_position, target)
    elif hungry and carried_wheat:
        target = _nearest(farmer_position, hungry)
        farmer = ["FEED"] if farmer_position == target else _move_toward(farmer_position, target)
    elif hungry and shed_wheat:
        farmer = (
            ["PICKUP", "WHEAT", min(shed_wheat, len(hungry))]
            if farmer_position == SHED_ACCESS
            else _move_toward(farmer_position, SHED_ACCESS)
        )
    elif uncared:
        target = _nearest(farmer_position, uncared)
        farmer = ["CARE"] if farmer_position == target else _move_toward(farmer_position, target)
    elif farmer_inventory:
        farmer = ["DROP"] if farmer_position == SHED_ACCESS else _move_toward(farmer_position, SHED_ACCESS)
    elif empty_pasture and shed.get("COW", 0):
        farmer = (
            ["PICKUP", "COW", 1]
            if farmer_position == SHED_ACCESS
            else _move_toward(farmer_position, SHED_ACCESS)
        )
    else:
        farmer = ["PASS"]

    hand_actions = []
    for index, position in enumerate(farm.get("hands", []), start=1):
        hand_inventory = inventories[index] if index < len(inventories) else {}
        hand_actions.append(_wheat_action(tuple(position), hand_inventory, tiles, wheat_seeds, day))

    return {"farmer": farmer, "hands": hand_actions, "market": market}

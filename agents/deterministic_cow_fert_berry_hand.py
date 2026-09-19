"""Two-cow champion with wheat feed, one daily hired hand, fertilizer collection, and a conditional second hand for strawberries.

This clones the main.py two-cow/wheat-hand/fertilizer champion exactly and adds
only one conditional behavior: when milk-demanding shops are absent early and the
farm can afford the investment, a second hired hand is recruited to plant, water,
harvest, and sell a 4-tile strawberry plot.
"""

COW_COST = 400
WHEAT_SEED_COST = 10
WHEAT_HARVEST_DAY = 4
STOP_PLANT_DAY = 25
STARTUP_FEED_RESERVE = 10
SHED_ACCESS = (4, 4)
PASTURES = ((4, 4), (3, 4))
WHEAT_FIELD = ((2, 4), (1, 4), (0, 4))

STRAW_SEED_COST = 100
STRAW_FIRST_YIELD_DAY = 10
STRAW_PLANT_BY_DAY = 8
STRAW_FIELD = ((1, 3), (2, 3), (3, 3), (4, 3))
MILK_SHOPS = ("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP")


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


def _straw_action(position, inventory, tiles, seeds, day):
    if inventory:
        return ["DROP"] if position == SHED_ACCESS else _move_toward(position, SHED_ACCESS)

    mature, dry, weeds, empty = [], [], [], []
    for point in STRAW_FIELD:
        tile = tiles[point[1]][point[0]]
        if tile is None:
            empty.append(point)
        elif isinstance(tile, dict) and tile.get("kind") == "WEED":
            weeds.append(point)
        elif isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == "STRAWBERRY":
            if day - tile["planted_day"] >= STRAW_FIRST_YIELD_DAY and tile.get("yield_units", 0) > 0:
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
    if empty and seeds and day <= STRAW_PLANT_BY_DAY:
        target = _nearest(position, empty)
        return ["PLANT", "STRAWBERRY"] if position == target else _move_toward(position, target)
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

    shops = observation.get("town", {}).get("unlocked_shops", [])
    milk_shops = sum(1 for s in shops if s in MILK_SHOPS)
    straw_seeds = private.get("seeds", {}).get("STRAWBERRY", 0)
    straw_tiles_live = any(
        isinstance(tiles[point[1]][point[0]], dict)
        and tiles[point[1]][point[0]].get("kind") == "PLANT"
        and tiles[point[1]][point[0]].get("crop") == "STRAWBERRY"
        for point in STRAW_FIELD
    )
    straw_active = (
        straw_tiles_live
        or straw_seeds > 0
        or (day >= 6 and day <= STRAW_PLANT_BY_DAY and milk_shops == 0)
    )

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

    straw_empty = []
    if straw_active:
        for point in STRAW_FIELD:
            tile = tiles[point[1]][point[0]]
            if tile is None:
                straw_empty.append(point)

    carried_cows = sum(inv.get("COW", 0) for inv in inventories)
    total_cows = placed_cows + carried_cows + shed.get("COW", 0)
    carried_wheat = farmer_inventory.get("WHEAT", 0)
    shed_wheat = shed.get("WHEAT", 0)
    wheat_seeds = private.get("seeds", {}).get("WHEAT", 0)

    market = []
    if hour == 0 and not farm.get("hands"):
        market.append(["HIRE"])
    # Hands reset daily, so at hour 0 the list is always empty: queue both hires
    # together (1 coin each). First hire serves wheat, second serves strawberries.
    if straw_active and hour == 0 and not farm.get("hands"):
        market.append(["HIRE"])
    if shed.get("MILK", 0):
        market.append(["SELL", "MILK", shed["MILK"]])
    if shed.get("FERTILIZER", 0):
        market.append(["SELL", "FERTILIZER", shed["FERTILIZER"]])
    if shed.get("STRAWBERRY", 0):
        market.append(["SELL", "STRAWBERRY", shed["STRAWBERRY"]])
    if day <= STOP_PLANT_DAY:
        seed_shortfall = max(0, len(wheat_empty) - wheat_seeds)
        if seed_shortfall and farm["money"] >= WHEAT_SEED_COST:
            market.append(["BUY_SEED", "WHEAT", min(seed_shortfall, int(farm["money"] // WHEAT_SEED_COST))])
    if straw_active and day <= STRAW_PLANT_BY_DAY:
        straw_shortfall = max(0, len(straw_empty) - straw_seeds)
        if straw_shortfall and farm["money"] >= STRAW_SEED_COST:
            market.append(["BUY_SEED", "STRAWBERRY", min(straw_shortfall, int(farm["money"] // STRAW_SEED_COST))])
    if day == 0 and total_cows < len(PASTURES) and farm["money"] >= COW_COST:
        market.append(["BUY_ANIMAL", "COW", 1])
    available_feed = shed_wheat + carried_wheat
    if placed_cows and day < WHEAT_HARVEST_DAY and available_feed < STARTUP_FEED_RESERVE:
        market.append(["BUY_PRODUCT", "WHEAT", STARTUP_FEED_RESERVE - available_feed])

    fert_ready = [
        point
        for point in PASTURES
        if isinstance(tiles[point[1]][point[0]], dict)
        and "animal" in tiles[point[1]][point[0]]
        and tiles[point[1]][point[0]].get("fertilizer_available") is True
    ]
    fert_price_ok = observation.get("market", {}).get("prices", {}).get("FERTILIZER", 0) >= 40

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
    elif fert_ready and fert_price_ok and not carried_cow:
        target = _nearest(farmer_position, fert_ready)
        farmer = ["COLLECT_FERTILIZER"] if farmer_position == target else _move_toward(farmer_position, target)
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
        if index == 1:
            hand_actions.append(_wheat_action(tuple(position), hand_inventory, tiles, wheat_seeds, day))
        else:
            hand_actions.append(_straw_action(tuple(position), hand_inventory, tiles, straw_seeds, day))

    return {"farmer": farmer, "hands": hand_actions, "market": market}

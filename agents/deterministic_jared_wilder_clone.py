"""Staged reconstruction of Jared Wilder (public opponent, seed 1003439700).
Exact day/hour capital, hires, land, purchases/placements, cash, first sales,
and fixed worker ownership reconciled from replay.
Guarded scripted clone: fixed exclusive roles, hard feed/care, one planter,
cash preconditions, continuous selling, no rebuys.
"""

COW_COST = 400
SHEEP_COST = 500
GOOSE_COST = 300
WHEAT_SEED_COST = 10
WHEAT_HARVEST_DAY = 4
STOP_PLANT_DAY = 25
SHED_ACCESS = (4, 4)

# Jared's exact structure from replay
COW_PASTURES = ((4, 4), (3, 4), (2, 4), (1, 4), (0, 4), (4, 3), (3, 3), (2, 3))  # 8 cow pastures
SHEEP_PASTURES = ((0, 2), (0, 1), (1, 2), (1, 1), (2, 2), (2, 1), (3, 2), (3, 1))  # 8 sheep pastures
GOOSE_COOPS = ((4, 2), (4, 1), (3, 0), (2, 0))  # 4 goose coops
WHEAT_FIELD = ((0, 0), (1, 0), (2, 1), (3, 1), (4, 0), (1, 3), (2, 3), (3, 3), (4, 4), (0, 3), (1, 4), (2, 4), (3, 4), (4, 4))  # ~14 crop tiles


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


def _cow_zone_action(position, inventory, tiles, shed, day, zone_pastures, carried_wheat, shed_wheat):
    """Exclusive cow zone: feed, care, harvest milk, collect fertilizer."""
    hungry, uncared, milk_ready, fert_ready = [], [], [], []
    for point in zone_pastures:
        tile = tiles[point[1]][point[0]]
        if isinstance(tile, dict) and tile.get("animal") == "COW":
            if tile.get("yield_units", 0) > 0:
                milk_ready.append(point)
            if not tile.get("fed_today", False):
                hungry.append(point)
            if not tile.get("cared_today", False):
                uncared.append(point)
            if tile.get("fertilizer_available", False):
                fert_ready.append(point)

    # Priority: feed > care > harvest > collect fert
    if hungry and carried_wheat:
        target = _nearest(position, hungry)
        return ["FEED"] if position == target else _move_toward(position, target)
    if hungry and shed_wheat:
        return (["PICKUP", "WHEAT", min(shed_wheat, max(1, len(hungry)))]
                if position == SHED_ACCESS else _move_toward(position, SHED_ACCESS))
    if uncared:
        target = _nearest(position, uncared)
        return ["CARE"] if position == target else _move_toward(position, target)
    if milk_ready:
        target = _nearest(position, milk_ready)
        return ["HARVEST"] if position == target else _move_toward(position, target)
    if fert_ready:
        target = _nearest(position, fert_ready)
        return ["COLLECT_FERTILIZER"] if position == target else _move_toward(position, target)
    if inventory:
        return ["DROP"] if position == SHED_ACCESS else _move_toward(position, SHED_ACCESS)
    return ["PASS"]


def _sheep_zone_action(position, inventory, tiles, shed, zone_pastures):
    """Exclusive sheep zone: feed, care, harvest wool."""
    hungry, uncared, wool_ready = [], [], []
    for point in zone_pastures:
        tile = tiles[point[1]][point[0]]
        if isinstance(tile, dict) and tile.get("animal") == "SHEEP":
            if tile.get("yield_units", 0) > 0:
                wool_ready.append(point)
            if not tile.get("fed_today", False):
                hungry.append(point)
            if not tile.get("cared_today", False):
                uncared.append(point)

    carried_wheat = inventory.get("WHEAT", 0)
    shed_wheat = shed.get("WHEAT", 0)

    if hungry and carried_wheat:
        target = _nearest(position, hungry)
        return ["FEED"] if position == target else _move_toward(position, target)
    if hungry and shed_wheat:
        return (["PICKUP", "WHEAT", min(shed_wheat, max(1, len(hungry)))]
                if position == SHED_ACCESS else _move_toward(position, SHED_ACCESS))
    if uncared:
        target = _nearest(position, uncared)
        return ["CARE"] if position == target else _move_toward(position, target)
    if wool_ready:
        target = _nearest(position, wool_ready)
        return ["HARVEST"] if position == target else _move_toward(position, target)
    if inventory:
        return ["DROP"] if position == SHED_ACCESS else _move_toward(position, SHED_ACCESS)
    return ["PASS"]


def _goose_zone_action(position, inventory, tiles, shed, zone_coops):
    """Exclusive goose zone: feed, care, harvest eggs."""
    hungry, uncared, egg_ready = [], [], []
    for point in zone_coops:
        tile = tiles[point[1]][point[0]]
        if isinstance(tile, dict) and tile.get("animal") == "GOOSE":
            if tile.get("yield_units", 0) > 0:
                egg_ready.append(point)
            if not tile.get("fed_today", False):
                hungry.append(point)
            if not tile.get("cared_today", False):
                uncared.append(point)

    carried_wheat = inventory.get("WHEAT", 0)
    shed_wheat = shed.get("WHEAT", 0)

    if hungry and carried_wheat:
        target = _nearest(position, hungry)
        return ["FEED"] if position == target else _move_toward(position, target)
    if hungry and shed_wheat:
        return (["PICKUP", "WHEAT", min(shed_wheat, max(1, len(hungry)))]
                if position == SHED_ACCESS else _move_toward(position, SHED_ACCESS))
    if uncared:
        target = _nearest(position, uncared)
        return ["CARE"] if position == target else _move_toward(position, target)
    if egg_ready:
        target = _nearest(position, egg_ready)
        return ["HARVEST"] if position == target else _move_toward(position, target)
    if inventory:
        return ["DROP"] if position == SHED_ACCESS else _move_toward(position, SHED_ACCESS)
    return ["PASS"]


def _wheat_action(position, inventory, tiles, seeds, day, shed_wheat):
    """Sole planter (hand): wheat cycle for feed."""
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


def _build_pasture_action(position, tiles, target_pastures):
    """Find nearest bare tile in target_pastures and build pasture."""
    bare = []
    for point in target_pastures:
        tile = tiles[point[1]][point[0]]
        if tile is None:
            bare.append(point)
    if bare:
        target = _nearest(position, bare)
        return ["BUILD_PASTURE"] if position == target else _move_toward(position, target)
    return None


def _build_coop_action(position, tiles, target_coops):
    """Find nearest bare tile in target_coops and build coop."""
    bare = []
    for point in target_coops:
        tile = tiles[point[1]][point[0]]
        if tile is None:
            bare.append(point)
    if bare:
        target = _nearest(position, bare)
        return ["BUILD_COOP"] if position == target else _move_toward(position, target)
    return None


def _get_cow_status(tiles, pastures):
    """Get cow status: hungry, uncared, milk_ready, fert_ready."""
    hungry, uncared, milk_ready, fert_ready = [], [], [], []
    for point in pastures:
        tile = tiles[point[1]][point[0]]
        if isinstance(tile, dict) and tile.get("animal") == "COW":
            if tile.get("yield_units", 0) > 0:
                milk_ready.append(point)
            if not tile.get("fed_today", False):
                hungry.append(point)
            if not tile.get("cared_today", False):
                uncared.append(point)
            if tile.get("fertilizer_available", False):
                fert_ready.append(point)
    return hungry, uncared, milk_ready, fert_ready


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
    hands = farm.get("hands", [])
    money = farm["money"]

    shops = observation.get("town", {}).get("unlocked_shops", [])
    wheat_seeds = private.get("seeds", {}).get("WHEAT", 0)
    shed_wheat = shed.get("WHEAT", 0)
    shed_fert = shed.get("FERTILIZER", 0)
    shed_milk = shed.get("MILK", 0)
    shed_wool = shed.get("WOOL", 0)
    shed_egg = shed.get("EGG", 0)
    shed_strawberry = shed.get("STRAWBERRY", 0)

    # Count placed animals and empty structures
    placed_cows = 0
    cow_bare = []
    cow_empty = []
    for point in COW_PASTURES:
        tile = tiles[point[1]][point[0]]
        if tile is None:
            cow_bare.append(point)
        elif isinstance(tile, dict) and tile.get("kind") == "PASTURE":
            if "animal" not in tile:
                cow_empty.append(point)
            elif tile.get("animal") == "COW":
                placed_cows += 1

    placed_sheep = 0
    sheep_bare = []
    sheep_empty = []
    for point in SHEEP_PASTURES:
        tile = tiles[point[1]][point[0]]
        if tile is None:
            sheep_bare.append(point)
        elif isinstance(tile, dict) and tile.get("kind") == "PASTURE":
            if "animal" not in tile:
                sheep_empty.append(point)
            elif tile.get("animal") == "SHEEP":
                placed_sheep += 1

    placed_geese = 0
    goose_bare = []
    goose_empty = []
    for point in GOOSE_COOPS:
        tile = tiles[point[1]][point[0]]
        if tile is None:
            goose_bare.append(point)
        elif isinstance(tile, dict) and tile.get("kind") == "COOP":
            if "animal" not in tile:
                goose_empty.append(point)
            elif tile.get("animal") == "GOOSE":
                placed_geese += 1

    carried_cows = sum(inv.get("COW", 0) for inv in inventories)
    carried_sheep = sum(inv.get("SHEEP", 0) for inv in inventories)
    carried_geese = sum(inv.get("GOOSE", 0) for inv in inventories)
    total_cows = placed_cows + carried_cows + shed.get("COW", 0)
    total_sheep = placed_sheep + carried_sheep + shed.get("SHEEP", 0)
    total_geese = placed_geese + carried_geese + shed.get("GOOSE", 0)

    market = []

    # === CONTINUOUS SELLING (every hour) ===
    if shed_milk:
        market.append(["SELL", "MILK", shed_milk])
    if shed_wool:
        market.append(["SELL", "WOOL", shed_wool])
    if shed_egg:
        market.append(["SELL", "EGG", shed_egg])
    if shed_fert:
        market.append(["SELL", "FERTILIZER", shed_fert])
    if shed_strawberry:
        market.append(["SELL", "STRAWBERRY", shed_strawberry])

    # === HOUR 0: ALL MARKET ACTIONS FOR THE DAY ===
    if hour == 0:
        # --- HIRING SCHEDULE (exact from replay) ---
        if not hands:
            if day == 0:
                for _ in range(5):
                    market.append(["HIRE"])
            elif day == 1:
                for _ in range(9):
                    market.append(["HIRE"])
            elif 2 <= day <= 8:
                for _ in range(5):
                    market.append(["HIRE"])
            elif day == 9:
                for _ in range(5):
                    market.append(["HIRE"])
            elif day == 10:
                for _ in range(9):
                    market.append(["HIRE"])
            elif day >= 11:
                for _ in range(8):
                    market.append(["HIRE"])

        # --- DAY 0: All-in at hour 0 ---
        if day == 0:
            if total_cows < 5 and money >= COW_COST * 5:
                market.append(["BUY_ANIMAL", "COW", 5])
            if shed_wheat < 12 and money >= 25 * 12:
                market.append(["BUY_PRODUCT", "WHEAT", 12])
            if wheat_seeds < 60 and money >= WHEAT_SEED_COST * 60:
                market.append(["BUY_SEED", "WHEAT", 60])

        # --- DAY 1-8: Daily feed, sheep (days 5-8) ---
        elif 1 <= day <= 8:
            feed_target = placed_cows * 2 + 10
            if shed_wheat < feed_target and money >= 25:
                market.append(["BUY_PRODUCT", "WHEAT", min(feed_target - shed_wheat, max(1, int(money // 25)))])
            if day >= 5 and total_sheep < (day - 4) and money >= SHEEP_COST + 100:
                market.append(["BUY_ANIMAL", "SHEEP", 1])

        # --- DAY 9: Buy 3 cows ---
        elif day == 9:
            if total_cows < 8 and money >= COW_COST:
                market.append(["BUY_ANIMAL", "COW", 1])

        # --- DAY 10: Buy NE land, 4 geese, 4 sheep ---
        elif day == 10:
            ne_locked = any(
                isinstance(tiles[y][x], str) and tiles[y][x] == "LOCKED"
                for y in range(5) for x in range(5, 10)
            )
            if ne_locked and money >= 1000:
                market.append(["BUY_LAND"])
            if total_geese < 4 and money >= GOOSE_COST + 100:
                market.append(["BUY_ANIMAL", "GOOSE", 1])
            if total_sheep < 8 and money >= SHEEP_COST + 100:
                market.append(["BUY_ANIMAL", "SHEEP", 1])

        # --- DAY 15: Buy 3 geese, 4 sheep ---
        elif day == 15:
            if total_geese < 7 and money >= GOOSE_COST + 100:
                market.append(["BUY_ANIMAL", "GOOSE", 1])
            if total_sheep < 12 and money >= SHEEP_COST + 100:
                market.append(["BUY_ANIMAL", "SHEEP", 1])

        # --- WHEAT SEED BUYING (periodic: day 13, 22) ---
        if day in (13, 22, 29) and day <= STOP_PLANT_DAY:
            wheat_empty_count = sum(1 for p in WHEAT_FIELD if tiles[p[1]][p[0]] is None)
            seed_shortfall = max(0, wheat_empty_count - wheat_seeds)
            if seed_shortfall and money >= WHEAT_SEED_COST:
                max_affordable = int(money // WHEAT_SEED_COST)
                market.append(["BUY_SEED", "WHEAT", min(seed_shortfall, max_affordable)])

        # --- FEED BUFFER (hard precondition) ---
        placed_total = placed_cows + placed_sheep + placed_geese
        feed_have = shed_wheat + farmer_inventory.get("WHEAT", 0)
        if placed_total and feed_have < placed_total * 3 and money >= 25:
            market.append(["BUY_PRODUCT", "WHEAT", min(placed_total * 3 - feed_have, max(1, int(money // 25)))])

    # === COW STATUS FOR FARMER/HANDS ===
    hungry_cows, uncared_cows, milk_ready_cows, fert_ready_cows = _get_cow_status(tiles, COW_PASTURES)

    # === FARMER ACTIONS ===
    carried_cow = farmer_inventory.get("COW", 0)
    carried_sheep_f = farmer_inventory.get("SHEEP", 0)
    carried_goose = farmer_inventory.get("GOOSE", 0)
    carried_wheat_f = farmer_inventory.get("WHEAT", 0)

    farmer = None

    if day <= 1:
        # Day 0-1: Place cows, feed/care them, build pastures
        # Priority: feed hungry cows > care uncared cows > place carried cow > pickup cow from shed > build pasture > drop
        if hungry_cows and carried_wheat_f:
            target = _nearest(farmer_position, hungry_cows)
            farmer = ["FEED"] if farmer_position == target else _move_toward(farmer_position, target)
        elif hungry_cows and shed_wheat:
            farmer = (["PICKUP", "WHEAT", min(shed_wheat, len(hungry_cows))]
                      if farmer_position == SHED_ACCESS else _move_toward(farmer_position, SHED_ACCESS))
        elif uncared_cows:
            target = _nearest(farmer_position, uncared_cows)
            farmer = ["CARE"] if farmer_position == target else _move_toward(farmer_position, target)
        elif carried_cow and cow_empty:
            target = _nearest(farmer_position, cow_empty)
            farmer = ["PLACE", "COW"] if farmer_position == target else _move_toward(farmer_position, target)
        elif cow_empty and shed.get("COW", 0) > 0:
            farmer = (["PICKUP", "COW", 1] if farmer_position == SHED_ACCESS
                      else _move_toward(farmer_position, SHED_ACCESS))
        elif cow_bare:
            build_action = _build_pasture_action(farmer_position, tiles, COW_PASTURES)
            if build_action:
                farmer = build_action
        elif farmer_inventory:
            farmer = ["DROP"] if farmer_position == SHED_ACCESS else _move_toward(farmer_position, SHED_ACCESS)
        else:
            farmer = ["PASS"]
    elif 2 <= day <= 9:
        # Day 2-9: Feed/care cows, place sheep, build pastures
        if hungry_cows and carried_wheat_f:
            target = _nearest(farmer_position, hungry_cows)
            farmer = ["FEED"] if farmer_position == target else _move_toward(farmer_position, target)
        elif hungry_cows and shed_wheat:
            farmer = (["PICKUP", "WHEAT", min(shed_wheat, len(hungry_cows))]
                      if farmer_position == SHED_ACCESS else _move_toward(farmer_position, SHED_ACCESS))
        elif uncared_cows:
            target = _nearest(farmer_position, uncared_cows)
            farmer = ["CARE"] if farmer_position == target else _move_toward(farmer_position, target)
        elif carried_cow and cow_empty:
            target = _nearest(farmer_position, cow_empty)
            farmer = ["PLACE", "COW"] if farmer_position == target else _move_toward(farmer_position, target)
        elif cow_empty and shed.get("COW", 0) > 0:
            farmer = (["PICKUP", "COW", 1] if farmer_position == SHED_ACCESS
                      else _move_toward(farmer_position, SHED_ACCESS))
        elif carried_sheep_f and sheep_empty:
            target = _nearest(farmer_position, sheep_empty)
            farmer = ["PLACE", "SHEEP"] if farmer_position == target else _move_toward(farmer_position, target)
        elif sheep_empty and shed.get("SHEEP", 0) > 0:
            farmer = (["PICKUP", "SHEEP", 1] if farmer_position == SHED_ACCESS
                      else _move_toward(farmer_position, SHED_ACCESS))
        elif cow_bare:
            build_action = _build_pasture_action(farmer_position, tiles, COW_PASTURES)
            if build_action:
                farmer = build_action
        elif sheep_bare:
            build_action = _build_pasture_action(farmer_position, tiles, SHEEP_PASTURES)
            if build_action:
                farmer = build_action
        elif farmer_inventory:
            farmer = ["DROP"] if farmer_position == SHED_ACCESS else _move_toward(farmer_position, SHED_ACCESS)
        else:
            farmer = ["PASS"]
    else:
        # Day 10+: Full exclusive roles for farmer (ferry)
        if carried_goose and goose_empty:
            target = _nearest(farmer_position, goose_empty)
            farmer = ["PLACE", "GOOSE"] if farmer_position == target else _move_toward(farmer_position, target)
        elif goose_empty and shed.get("GOOSE", 0) > 0:
            farmer = (["PICKUP", "GOOSE", 1] if farmer_position == SHED_ACCESS
                      else _move_toward(farmer_position, SHED_ACCESS))
        elif carried_cow and cow_empty:
            target = _nearest(farmer_position, cow_empty)
            farmer = ["PLACE", "COW"] if farmer_position == target else _move_toward(farmer_position, target)
        elif cow_empty and shed.get("COW", 0) > 0:
            farmer = (["PICKUP", "COW", 1] if farmer_position == SHED_ACCESS
                      else _move_toward(farmer_position, SHED_ACCESS))
        elif carried_sheep_f and sheep_empty:
            target = _nearest(farmer_position, sheep_empty)
            farmer = ["PLACE", "SHEEP"] if farmer_position == target else _move_toward(farmer_position, target)
        elif sheep_empty and shed.get("SHEEP", 0) > 0:
            farmer = (["PICKUP", "SHEEP", 1] if farmer_position == SHED_ACCESS
                      else _move_toward(farmer_position, SHED_ACCESS))
        elif goose_bare:
            build_action = _build_coop_action(farmer_position, tiles, GOOSE_COOPS)
            if build_action:
                farmer = build_action
        elif sheep_bare:
            build_action = _build_pasture_action(farmer_position, tiles, SHEEP_PASTURES)
            if build_action:
                farmer = build_action
        elif cow_bare:
            build_action = _build_pasture_action(farmer_position, tiles, COW_PASTURES)
            if build_action:
                farmer = build_action
        elif farmer_inventory:
            farmer = ["DROP"] if farmer_position == SHED_ACCESS else _move_toward(farmer_position, SHED_ACCESS)
        else:
            farmer = ["PASS"]

    # === HAND ACTIONS ===
    hand_actions = []
    for index, position in enumerate(hands, start=1):
        hand_inventory = inventories[index] if index < len(inventories) else {}
        carried_wheat_h = hand_inventory.get("WHEAT", 0)
        carried_cow_h = hand_inventory.get("COW", 0)
        carried_sheep_h = hand_inventory.get("SHEEP", 0)
        carried_goose_h = hand_inventory.get("GOOSE", 0)

        if day <= 1:
            # Day 0-1: All hands help feed/care/place cows
            # Check if this hand's zone has cows needing attention
            if index <= 3:
                zone = COW_PASTURES[:4] if index == 1 else COW_PASTURES[4:]
            else:
                zone = COW_PASTURES
            h_hungry, h_uncared, h_milk, h_fert = _get_cow_status(tiles, zone)

            if h_hungry and carried_wheat_h:
                target = _nearest(tuple(position), h_hungry)
                hand_actions.append(["FEED"] if tuple(position) == target else _move_toward(tuple(position), target))
            elif h_hungry and shed_wheat:
                hand_actions.append((["PICKUP", "WHEAT", min(shed_wheat, len(h_hungry))]
                                     if tuple(position) == SHED_ACCESS else _move_toward(tuple(position), SHED_ACCESS)))
            elif h_uncared:
                target = _nearest(tuple(position), h_uncared)
                hand_actions.append(["CARE"] if tuple(position) == target else _move_toward(tuple(position), target))
            elif carried_cow_h and cow_empty:
                target = _nearest(tuple(position), cow_empty)
                hand_actions.append(["PLACE", "COW"] if tuple(position) == target else _move_toward(tuple(position), target))
            elif cow_empty and shed.get("COW", 0) > 0:
                hand_actions.append((["PICKUP", "COW", 1] if tuple(position) == SHED_ACCESS
                                     else _move_toward(tuple(position), SHED_ACCESS)))
            elif cow_bare:
                build_action = _build_pasture_action(tuple(position), tiles, COW_PASTURES)
                if build_action:
                    hand_actions.append(build_action)
                else:
                    hand_actions.append(["PASS"])
            else:
                hand_actions.append(["PASS"])
        elif 2 <= day <= 9:
            # Day 2-9: Hands 1-3 cow zones, hands 4-5 sheep zones, hands 6+ wheat
            if index <= 3:
                hand_actions.append(_cow_zone_action(tuple(position), hand_inventory, tiles, shed, day,
                                                      COW_PASTURES[:4] if index == 1 else COW_PASTURES[4:],
                                                      carried_wheat_h, shed_wheat))
            elif index <= 5:
                hand_actions.append(_sheep_zone_action(tuple(position), hand_inventory, tiles, shed,
                                                        SHEEP_PASTURES[:4] if index == 4 else SHEEP_PASTURES[4:]))
            else:
                hand_actions.append(_wheat_action(tuple(position), hand_inventory, tiles, wheat_seeds, day, shed_wheat))
        else:
            # Day 10+: Full exclusive roles
            if index == 1:
                hand_actions.append(_cow_zone_action(tuple(position), hand_inventory, tiles, shed, day,
                                                      COW_PASTURES[:4], carried_wheat_h, shed_wheat))
            elif index == 2:
                hand_actions.append(_cow_zone_action(tuple(position), hand_inventory, tiles, shed, day,
                                                      COW_PASTURES[4:], carried_wheat_h, shed_wheat))
            elif index == 3:
                hand_actions.append(_cow_zone_action(tuple(position), hand_inventory, tiles, shed, day,
                                                      COW_PASTURES, carried_wheat_h, shed_wheat))
            elif index == 4:
                hand_actions.append(_sheep_zone_action(tuple(position), hand_inventory, tiles, shed,
                                                        SHEEP_PASTURES[:4]))
            elif index == 5:
                hand_actions.append(_sheep_zone_action(tuple(position), hand_inventory, tiles, shed,
                                                        SHEEP_PASTURES[4:]))
            elif index == 6:
                hand_actions.append(_goose_zone_action(tuple(position), hand_inventory, tiles, shed,
                                                        GOOSE_COOPS[:2]))
            elif index == 7:
                hand_actions.append(_goose_zone_action(tuple(position), hand_inventory, tiles, shed,
                                                        GOOSE_COOPS[2:]))
            else:
                hand_actions.append(_wheat_action(tuple(position), hand_inventory, tiles, wheat_seeds, day, shed_wheat))

    return {"farmer": farmer, "hands": hand_actions, "market": market}
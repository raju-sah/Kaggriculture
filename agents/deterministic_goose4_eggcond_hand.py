"""Two-cow/four-sheep/two-goose champion: YARN-triggered second sheep pair with a fifth exclusive hand, zone-locked labor, and a conditional fertilized strawberry plot.

Clones the fertilized-strawberry champion and adds exactly one conservative scale
step: two sheep on two new west pastures, serviced by a dedicated third hand.
Zones never overlap (farmer: cow pastures + build/place; hand-1: wheat, sole
planter; hand-2: strawberries; hand-3: sheep). Role order is index-stable: the
straw placeholder is always hired second when sheep are active. Exactly one
planter per crop (demand-cap rule). Feed buffer is maintained, never gated by day.
"""

COW_COST = 400
SHEEP_COST = 500
GOOSE_COST = 300
GOOSE_COOPS = ((2, 2), (3, 2))
GOOSE2_COOPS = ((0, 0), (1, 0))
EGG_SHOPS = ("BAKERY", "BRUNCH_SPOT")
WHEAT_SEED_COST = 10
WHEAT_HARVEST_DAY = 4
STOP_PLANT_DAY = 25
SHED_ACCESS = (4, 4)
COW_PASTURES = ((4, 4), (3, 4))
SHEEP_PASTURES = ((0, 3), (0, 2))
SHEEP2_PASTURES = ((3, 2), (4, 2))
WHEAT_FIELD = ((2, 4), (1, 4), (0, 4))

STRAW_SEED_COST = 100
STRAW_FIRST_YIELD_DAY = 10
STRAW_PLANT_BY_DAY = 8
STRAW_FIELD = ((1, 3), (2, 3), (3, 3), (4, 3))
STRAW2_FIELD = ((1, 1), (2, 1), (3, 1), (4, 1))
STRAW_SHOPS = ("BRUNCH_SPOT", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP", "FARMERS_MARKET")
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


def _straw_fert_due(tiles, day, field=STRAW_FIELD):
    """Return field points with a strawberry production tomorrow that is not yet fertilized for today."""
    due = []
    for point in field:
        tile = tiles[point[1]][point[0]]
        if isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == "STRAWBERRY":
            planted_day = tile["planted_day"]
            offset = day + 1 - planted_day - 10
            if 0 <= offset and offset % 2 == 0 and (offset // 2 + 1) <= 4:
                if tile.get("fertilized_until_day", -1) < day:
                    due.append(point)
    return due


def _straw_action(position, inventory, tiles, seeds, day, carried_fert, shed_fert, field=STRAW_FIELD):
    mature, dry, weeds, empty = [], [], [], []
    for point in field:
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

    due = _straw_fert_due(tiles, day, field)

    if mature:
        target = _nearest(position, mature)
        return ["HARVEST"] if position == target else _move_toward(position, target)

    # Drop non-fertilizer items at the shed. Carry FERTILIZER when a field tile is due.
    if inventory:
        carrying_only_fert = set(inventory.keys()) == {"FERTILIZER"}
        if not carrying_only_fert or not due:
            return ["DROP"] if position == SHED_ACCESS else _move_toward(position, SHED_ACCESS)

    if dry:
        target = _nearest(position, dry)
        return ["WATER"] if position == target else _move_toward(position, target)

    if due and carried_fert > 0:
        target = _nearest(position, due)
        return ["FERTILIZE"] if position == target else _move_toward(position, target)
    if due and carried_fert == 0 and shed_fert > 0:
        return ["PICKUP", "FERTILIZER", min(shed_fert, max(1, len(due)))] if position == SHED_ACCESS else _move_toward(position, SHED_ACCESS)

    if weeds:
        target = _nearest(position, weeds)
        return ["DIG"] if position == target else _move_toward(position, target)
    if empty and seeds and day <= STRAW_PLANT_BY_DAY:
        target = _nearest(position, empty)
        return ["PLANT", "STRAWBERRY"] if position == target else _move_toward(position, target)
    return ["PASS"]


def _flock_action(position, inventory, tiles, shed, day, fert_price_ok, zones=None):
    """Flock generalist (feed/care/harvest/collect) over exclusive zone tiles.

    zones pins tile ownership: hand-3 gets SHEEP_PASTURES, hand-4+ gets
    GOOSE_COOPS. Exclusive ownership keeps daily service load inside one
    worker's capacity so care bonuses are actually earned.
    """
    if zones is None:
        zones = SHEEP_PASTURES + GOOSE_COOPS
    hungry, uncared, wool_ready, fert_ready = [], [], [], []
    for point in zones:
        tile = tiles[point[1]][point[0]]
        if isinstance(tile, dict) and tile.get("animal") in ("SHEEP", "GOOSE"):
            if tile.get("yield_units", 0) > 0:
                wool_ready.append(point)
            if not tile.get("fed_today", False):
                hungry.append(point)
            if not tile.get("cared_today", False):
                uncared.append(point)
            if tile.get("fertilizer_available", False):
                fert_ready.append(point)

    carried_wheat = inventory.get("WHEAT", 0)
    shed_wheat = shed.get("WHEAT", 0)

    if hungry and carried_wheat:
        target = _nearest(position, hungry)
        return ["FEED"] if position == target else _move_toward(position, target)
    if hungry and shed_wheat:
        return (
            ["PICKUP", "WHEAT", min(shed_wheat, max(1, len(hungry)))]
            if position == SHED_ACCESS
            else _move_toward(position, SHED_ACCESS)
        )
    if uncared:
        target = _nearest(position, uncared)
        return ["CARE"] if position == target else _move_toward(position, target)
    if wool_ready:
        target = _nearest(position, wool_ready)
        return ["HARVEST"] if position == target else _move_toward(position, target)
    if fert_ready and fert_price_ok:
        target = _nearest(position, fert_ready)
        return ["COLLECT_FERTILIZER"] if position == target else _move_toward(position, target)
    if inventory:
        return ["DROP"] if position == SHED_ACCESS else _move_toward(position, SHED_ACCESS)
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
    # Second 4-tile strawberry plot (exp-0043a): disjoint NW row y=1 with its
    # own dedicated hand (hand-6). exp-0023 proved one hand cannot clear/water
    # 8 tiles, so capacity doubles only with doubled plot labor. One planter
    # per crop/plot is preserved: hand-2 plants STRAW_FIELD only, hand-6
    # plants STRAW2_FIELD only. Single causal trigger from engine economics
    # and public shop demand: the first town unlock is public from day 3 and
    # reads the season demand mix. A strawberry consumer
    # (BRUNCH/ICE_CREAM/SMOOTHIE/FARMERS) means the drain side we sell into
    # is deep, so +32 units stay on the scarcity branch (~269/unit, +8.6k
    # gross for ~400 seed + fib-8 hire). Otherwise the plot never activates
    # and the policy is byte-identical to the champion. The trigger is read
    # from day 3 on (first unlock exists from day 3; later unlocks only add
    # shops) but planting still respects the champion's day<=8 deadline and
    # the same animal-care-first capital order, so days 0-2 commitment is
    # untouched.
    d3_straw = any(s in STRAW_SHOPS for s in shops) and day >= 3
    straw2_tiles_live = any(
        isinstance(tiles[point[1]][point[0]], dict)
        and tiles[point[1]][point[0]].get("kind") == "PLANT"
        and tiles[point[1]][point[0]].get("crop") == "STRAWBERRY"
        for point in STRAW2_FIELD
    )
    straw2_active = bool(straw2_tiles_live or (d3_straw and (straw_seeds > 0 or (6 <= day <= STRAW_PLANT_BY_DAY))))
    # Keep STRAW2 strictly staged behind days 0-2 commitment: no hires/seeds
    # before day 3 even if shops arrive early in edge configs. Hires/seed
    # buys additionally stage to day 6+ (see hire ladder + seed queue) so
    # days 3-5 cash funds the sheep pair first.
    if day < 3:
        straw2_active = bool(straw2_tiles_live)

    # Cow zone (farmer): original two pastures only.
    bare, empty_pasture, hungry, uncared, milk_ready = [], [], [], [], []
    placed_cows = 0
    for point in COW_PASTURES:
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

    # Sheep zone (third hand): two west pastures.
    sheep_bare = []
    sheep_placed = 0
    for point in SHEEP_PASTURES:
        tile = tiles[point[1]][point[0]]
        if tile is None:
            sheep_bare.append(point)
            bare.append(point)
        elif isinstance(tile, dict) and tile.get("animal") == "SHEEP":
            sheep_placed += 1
    sheep_carried = sum(inv.get("SHEEP", 0) for inv in inventories)
    sheep_total = sheep_placed + sheep_carried + shed.get("SHEEP", 0)
    sheep_active = sheep_total >= 1 or (3 <= day <= 6)
    # Second sheep pair (fifth hand): only on early YARN draw. Wool break-even
    # needs yarn-driven drain: 2 sheep x ~6 events x ~2.5u x ~230 = ~7k gross
    # for ~1.1k capital+hire. Placed by ~day 8 for 6 productions (P+6..P+21).
    yarn_seen = "YARN_STORE" in shops
    sheep2_bare = []
    sheep2_placed = 0
    for point in SHEEP2_PASTURES:
        tile = tiles[point[1]][point[0]]
        if tile is None:
            sheep2_bare.append(point)
            bare.append(point)
        elif isinstance(tile, dict) and tile.get("animal") == "SHEEP":
            sheep2_placed += 1
    sheep2_total = sheep2_placed + sheep_carried + shed.get("SHEEP", 0)
    sheep2_active = sheep2_total >= 1 or (yarn_seen and 3 <= day <= 8)
    # Goose coops: built days 9+, stocked days 10-12.
    goose_bare = []
    goose_placed = 0
    for point in GOOSE_COOPS:
        tile = tiles[point[1]][point[0]]
        if tile is None:
            goose_bare.append(point)
            bare.append(point)
        elif isinstance(tile, dict) and tile.get("animal") == "GOOSE":
            goose_placed += 1
    goose_carried = sum(inv.get("GOOSE", 0) for inv in inventories)
    goose_total = goose_placed + goose_carried + shed.get("GOOSE", 0)
    # Second goose pair (exp-0043b): two extra coops on disjoint free NW
    # tiles ((0,0),(1,0)) with their own dedicated labor. GOOSE is the
    # cheapest flood-robust unit (300 capital, first yield day 4, interval 1,
    # EGG on a log curve that never floors: observed 50 -> 55-64 through day
    # 29). exp-0029 failed on the hand-3 care ceiling; exp-0030 solved that
    # with exclusive zones, so the killing mechanism is gone — but the second
    # pair must still ship with its own zone-locked hand, exactly as the
    # second strawberry plot shipped with hand-6. Single causal trigger from
    # engine economics + public shop demand: an EGG consumer (BAKERY or
    # BRUNCH_SPOT) visible from day 9. EGG drains through BAKERY/BRUNCH; no
    # egg consumer by day 9 means the drain side is thin and the pair stays
    # unbuilt (policy byte-identical to the champion there). Days 9-12 window
    # matches the champion's goose build/stock rhythm so the farmer's
    # build/place sequence is undisturbed; capital staged AFTER sheep+straw
    # (GOOSE+100 floor, same as the first pair) so early cash stays safe.
    egg_seen = any(s in EGG_SHOPS for s in shops)
    goose2_bare = []
    goose2_placed = 0
    for point in GOOSE2_COOPS:
        tile = tiles[point[1]][point[0]]
        if tile is None:
            goose2_bare.append(point)
            bare.append(point)
        elif isinstance(tile, dict) and tile.get("animal") == "GOOSE":
            goose2_placed += 1
    goose2_total = goose2_placed + goose_carried + shed.get("GOOSE", 0)
    goose2_active = bool(
        goose2_placed >= 1 or (egg_seen and 9 <= day <= 12 and goose_total >= 2)
    )
    if day < 9:
        goose2_active = bool(goose2_placed >= 1)

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

    straw2_empty = []
    if straw2_active:
        for point in STRAW2_FIELD:
            tile = tiles[point[1]][point[0]]
            if tile is None:
                straw2_empty.append(point)

    carried_cows = sum(inv.get("COW", 0) for inv in inventories)
    total_cows = placed_cows + carried_cows + shed.get("COW", 0)
    carried_wheat = farmer_inventory.get("WHEAT", 0)
    shed_wheat = shed.get("WHEAT", 0)
    wheat_seeds = private.get("seeds", {}).get("WHEAT", 0)
    shed_fert = shed.get("FERTILIZER", 0)

    market = []
    if hour == 0 and not farm.get("hands"):
        market.append(["HIRE"])
    # Hands reset daily: queue together for index-stable roles (1 wheat,
    # 2 straw, 3 sheep, 4 geese, 5 sheep2, 6 straw2/goose2, 7 goose2).
    # Placeholders keep roles stable: each earlier role is hired whenever any
    # later role is active. Hand-6 doubles as goose2 keeper when straw2 is off
    # (see dispatch); hand-7 exists only when BOTH straw2 and goose2 fire.
    # Seventh hire costs fib-13 coins/day; it is ordered only on the egg_seen
    # trigger from day 9+ AND straw2 active, so all other games keep the
    # champion's exact hire ladder.
    _straw2_hire = straw2_active and day >= 6
    _goose2_hire = goose2_active and day >= 9
    _goose2_seventh = _goose2_hire and _straw2_hire
    geese_active = goose_total >= 1 or (10 <= day <= 12)
    if (straw_active or sheep_active or geese_active or sheep2_active or _straw2_hire or _goose2_hire) and hour == 0 and not farm.get("hands"):
        market.append(["HIRE"])
    if (sheep_active or geese_active or sheep2_active or _straw2_hire or _goose2_hire) and hour == 0 and not farm.get("hands"):
        market.append(["HIRE"])
    if (geese_active or sheep2_active or _straw2_hire or _goose2_hire) and hour == 0 and not farm.get("hands"):
        market.append(["HIRE"])
    if (sheep2_active or _straw2_hire or _goose2_hire) and hour == 0 and not farm.get("hands"):
        market.append(["HIRE"])
    if (_straw2_hire or _goose2_hire) and hour == 0 and not farm.get("hands"):
        market.append(["HIRE"])
    if _straw2_hire and hour == 0 and not farm.get("hands"):
        market.append(["HIRE"])
    # Goose2 seventh hire: only when straw2 is ALSO active (hand-7 exists).
    # When straw2 is off, hand-6 already serves as the goose2 hand (see
    # dispatch), so no seventh hire is ordered and the ladder stays minimal.
    if _goose2_seventh and hour == 0 and not farm.get("hands"):
        market.append(["HIRE"])
    if shed.get("MILK", 0):
        market.append(["SELL", "MILK", shed["MILK"]])
    if shed.get("WOOL", 0):
        market.append(["SELL", "WOOL", shed["WOOL"]])
    if shed.get("EGG", 0):
        market.append(["SELL", "EGG", shed["EGG"]])

    straw_open = any(
        isinstance(tiles[point[1]][point[0]], dict)
        and tiles[point[1]][point[0]].get("kind") == "PLANT"
        and tiles[point[1]][point[0]].get("crop") == "STRAWBERRY"
        and tiles[point[1]][point[0]].get("planted_day", 0) + 16 >= day
        for point in STRAW_FIELD + STRAW2_FIELD
    )
    if straw_open and day <= 24:
        # Reserve 16/process: 8 waves x 2 plots. The deeper reserve applies
        # only when the second plot actually exists; non-trigger games keep
        # the champion's exact 16 so behavior is identical there.
        _reserve = 24 if straw2_active else 16
        sell_fert = max(0, shed_fert - _reserve)
    else:
        sell_fert = shed_fert
    if sell_fert > 0:
        market.append(["SELL", "FERTILIZER", sell_fert])

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
    if day == 0 and total_cows < len(COW_PASTURES) and farm["money"] >= COW_COST:
        market.append(["BUY_ANIMAL", "COW", 1])
    all_sheep = sheep_placed + sheep2_placed + sheep_carried + shed.get("SHEEP", 0)
    if 3 <= day <= 6 and all_sheep < 2 and farm["money"] >= SHEEP_COST + 100:
        market.append(["BUY_ANIMAL", "SHEEP", 1])
    if yarn_seen and 3 <= day <= 10 and all_sheep < 4 and farm["money"] >= SHEEP_COST + 100:
        market.append(["BUY_ANIMAL", "SHEEP", 1])
    if 10 <= day <= 12 and goose_total < 2 and farm["money"] >= GOOSE_COST + 100:
        market.append(["BUY_ANIMAL", "GOOSE", 1])
    if goose2_active and 9 <= day <= 12 and farm["money"] >= GOOSE_COST + 100:
        # Queued AFTER the first pair + sheep + straw so core capital is never
        # crowded out. Same GOOSE+100 floor as the champion's pair; day-9+
        # staging keeps sheep days 3-6 and straw days 6-8 ahead of it. The
        # goose_total>=2 precondition (see trigger) means the first pair is
        # already funded before a single coin commits to the second.
        _goose2_need = max(0, 2 - goose2_placed - goose_carried - shed.get("GOOSE", 0))
        if _goose2_need:
            market.append(["BUY_ANIMAL", "GOOSE", 1])
    if straw2_active and day >= 6 and day <= STRAW_PLANT_BY_DAY:
        # Queued AFTER animals so sheep/goose capital is never crowded out.
        # Covers only the second plot net of seeds already held/queued for
        # plot 1; plot 1 keeps its champion priority. Staged to day 6+:
        # days 3-5 cash is reserved for the sheep pair (SHEEP_COST+100
        # floor) and the feed buffer, so plot-2 seed commits only after the
        # core opening is funded. Same day<=8 deadline as plot 1.
        straw2_net = max(0, len(straw2_empty) - max(0, straw_seeds - len(straw_empty)))
        if straw2_net and farm["money"] >= STRAW_SEED_COST + 100:
            market.append(["BUY_SEED", "STRAWBERRY", min(straw2_net, int((farm["money"] - 100) // STRAW_SEED_COST))])
    # Capital schedule (animal care + early cash stay safe): animals first,
    # then plot-1 seeds, then plot-2 seeds. Plot-2 seed buys require the
    # d3_straw trigger AND a +100 reserve above the animal floor so sheep
    # days 3-6 are never crowded out. No late low-yield plants: both plots
    # share the champion day<=8 deadline.
    # Feed buffer maintained all season: ~4 days cover for every placed animal.
    placed_total = placed_cows + sheep_placed + goose_placed + sheep2_placed + goose2_placed
    feed_have = shed_wheat + carried_wheat
    # Day-0 reserve buys once: stock-gated so it cannot repeat every turn.
    # (Unconditional day-gated orders repeat 24x and bankrupt the farm.)
    if day == 0 and feed_have < 12 and farm["money"] >= 300:
        market.append(["BUY_PRODUCT", "WHEAT", min(12 - feed_have, max(1, int(farm["money"] // 25)))])
    if placed_total and feed_have < placed_total * 4 and farm["money"] >= 25:
        market.append(["BUY_PRODUCT", "WHEAT", min(placed_total * 4 - feed_have, max(1, int(farm["money"] // 25)))])

    fert_ready = [
        point
        for point in COW_PASTURES
        if isinstance(tiles[point[1]][point[0]], dict)
        and "animal" in tiles[point[1]][point[0]]
        and tiles[point[1]][point[0]].get("fertilizer_available") is True
    ]
    fert_price_ok = observation.get("market", {}).get("prices", {}).get("FERTILIZER", 0) >= 40

    carried_cow = farmer_inventory.get("COW", 0)
    carried_sheep = farmer_inventory.get("SHEEP", 0)
    carried_goose = farmer_inventory.get("GOOSE", 0)
    goose_empty = [
        point for point in GOOSE_COOPS + GOOSE2_COOPS
        if isinstance(tiles[point[1]][point[0]], dict)
        and tiles[point[1]][point[0]].get("kind") == "COOP"
        and "animal" not in tiles[point[1]][point[0]]
    ]
    goose2_empty = [
        point for point in GOOSE2_COOPS
        if isinstance(tiles[point[1]][point[0]], dict)
        and tiles[point[1]][point[0]].get("kind") == "COOP"
        and "animal" not in tiles[point[1]][point[0]]
    ]
    if bare:
        target = _nearest(farmer_position, bare)
        build_op = "BUILD_COOP" if target in GOOSE_COOPS + GOOSE2_COOPS else "BUILD_PASTURE"
        farmer = [build_op] if farmer_position == target else _move_toward(farmer_position, target)
    elif carried_cow and empty_pasture:
        target = _nearest(farmer_position, empty_pasture)
        farmer = ["PLACE", "COW"] if farmer_position == target else _move_toward(farmer_position, target)
    elif carried_sheep:
        sheep_empty = [
            point for point in SHEEP_PASTURES + SHEEP2_PASTURES
            if isinstance(tiles[point[1]][point[0]], dict)
            and tiles[point[1]][point[0]].get("kind") == "PASTURE"
            and "animal" not in tiles[point[1]][point[0]]
        ]
        if sheep_empty:
            target = _nearest(farmer_position, sheep_empty)
            farmer = ["PLACE", "SHEEP"] if farmer_position == target else _move_toward(farmer_position, target)
        else:
            farmer = ["DROP"] if farmer_position == SHED_ACCESS else _move_toward(farmer_position, SHED_ACCESS)
    elif carried_goose and goose_empty:
        # First-pair coops keep placement priority; second-pair empties are
        # filled from the same queue once pair-1 coops are stocked, so the
        # champion's day 10-12 stocking order is undisturbed.
        _g1_empty = [p for p in goose_empty if p in GOOSE_COOPS]
        target = _nearest(farmer_position, _g1_empty or goose_empty)
        farmer = ["PLACE", "GOOSE"] if farmer_position == target else _move_toward(farmer_position, target)
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
    elif shed.get("GOOSE", 0) and goose_empty:
        # Ferry shed geese to built empty coops (either pair; pair-1 first).
        farmer = (
            ["PICKUP", "GOOSE", 1]
            if farmer_position == SHED_ACCESS
            else _move_toward(farmer_position, SHED_ACCESS)
        )
    elif shed.get("SHEEP", 0):
        # Ferry shed sheep to built empty sheep pastures (either pair).
        sheep_empty = [
            point for point in SHEEP_PASTURES + SHEEP2_PASTURES
            if isinstance(tiles[point[1]][point[0]], dict)
            and tiles[point[1]][point[0]].get("kind") == "PASTURE"
            and "animal" not in tiles[point[1]][point[0]]
        ]
        if sheep_empty:
            farmer = (
                ["PICKUP", "SHEEP", 1]
                if farmer_position == SHED_ACCESS
                else _move_toward(farmer_position, SHED_ACCESS)
            )
        else:
            farmer = ["DROP"] if farmer_position == SHED_ACCESS else _move_toward(farmer_position, SHED_ACCESS)
    else:
        farmer = ["PASS"]

    hand_actions = []
    for index, position in enumerate(farm.get("hands", []), start=1):
        hand_inventory = inventories[index] if index < len(inventories) else {}
        if index == 1:
            hand_actions.append(_wheat_action(tuple(position), hand_inventory, tiles, wheat_seeds, day))
        elif index == 2:
            hand_actions.append(_straw_action(tuple(position), hand_inventory, tiles, straw_seeds, day, hand_inventory.get("FERTILIZER", 0), shed_fert))
        elif index == 3:
            hand_actions.append(_flock_action(tuple(position), hand_inventory, tiles, shed, day, fert_price_ok, SHEEP_PASTURES))
        elif index == 4:
            hand_actions.append(_flock_action(tuple(position), hand_inventory, tiles, shed, day, fert_price_ok, GOOSE_COOPS))
        elif index == 5:
            hand_actions.append(_flock_action(tuple(position), hand_inventory, tiles, shed, day, fert_price_ok, SHEEP2_PASTURES))
        elif index == 6 and _goose2_hire and not _straw2_hire:
            # No straw2 this game: hand-6 serves as the goose2 hand instead of
            # a straw placeholder. Keeps the hire count minimal on egg-only
            # games (no fib-8 straw placeholder + fib-13 goose hire stacked).
            hand_actions.append(_flock_action(tuple(position), hand_inventory, tiles, shed, day, fert_price_ok, GOOSE2_COOPS))
        elif index == 6:
            # Hand-6: sole planter of STRAW2_FIELD. Fixed tile ownership:
            # hand-2 never enters STRAW2_FIELD and hand-6 never enters
            # STRAW_FIELD, so full watering/fertilizing holds on both plots.
            # Plant serialization: the engine drops ALL same-crop PLANTs on a
            # turn when demand exceeds seeds, so hand-6 plants only after
            # plot 1 is full (seeds=0 keeps it on water/weed/fertilize duty).
            # This keeps one effective planter per crop per turn.
            _s6_seeds = 0 if straw_empty else straw_seeds
            hand_actions.append(_straw_action(tuple(position), hand_inventory, tiles, _s6_seeds, day, hand_inventory.get("FERTILIZER", 0), shed_fert, STRAW2_FIELD))
        else:
            # Hand-7: sole keeper of GOOSE2_COOPS. Fixed zone ownership:
            # hand-4 never enters GOOSE2_COOPS and hand-7 never enters
            # GOOSE_COOPS, so daily feed/care load stays inside one worker's
            # capacity (the exp-0029 killer) and care bonuses are earned.
            hand_actions.append(_flock_action(tuple(position), hand_inventory, tiles, shed, day, fert_price_ok, GOOSE2_COOPS))

    return {"farmer": farmer, "hands": hand_actions, "market": market}

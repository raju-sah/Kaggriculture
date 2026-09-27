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
WHEAT_SEED_COST = 10
WHEAT_HARVEST_DAY = 4
STOP_PLANT_DAY = 25
SHED_ACCESS = (4, 4)
COW_PASTURES = ((4, 4), (3, 4))
SHEEP_PASTURES = ((0, 3), (0, 2))
SHEEP2_PASTURES = ((3, 2), (4, 2))
WHEAT_FIELD = ((2, 4), (1, 4), (0, 4))

# --- State-derived opener + day-2 bridge ---
# The opening footprint is generated from the first unlocked quadrant and
# Manhattan travel costs. Duties are derived from live tile state every turn.
# Engine-verified mechanics baked into the planner:
#   - a fresh plant counts 1 unwatered day at creation, so EVERY plant must
#     be watered on its planting day or it dies that night;
#   - animals escape after 2 consecutive unfed days; care bonuses need
#     fed+cared on the same day; each animal yields 1 fertilizer/day;
#   - one-shot crops die to decay after max_yield_day+1 (wheat day 5,
#     melon day 13), so harvests are deadline tasks;
#   - aggregate PLANT orders for a crop exceeding held seeds are ALL
#     rejected that turn, so plant tasks are guarded by seed stock.
MELON_SEED_COST = 80  # engine CROPS["MELON"]["seed"]
MELON_MAX_YIELD_DAY = 12
OPENING_HANDS_TARGET = 4
BRIDGE_HANDS_TARGET = 5   # extra hand funds the mid-season watering load
WHEAT_MAX_YIELD_DAY = 4
MELON_WATER_WINDOW_LAST = 10  # 5 waters saturate the 6-unit yield
WHEAT_REPLANT_BY_DAY = 25
MELON_REPLANT_BY_DAY = 16
GOOSE_BUILD_FIRST_DAY = 4
GOOSE_BUILD_LAST_DAY = 14  # the (3,2) melon tile only frees on day 13
GOOSE_BUY_FIRST_DAY = 10
GOOSE_BUY_LAST_DAY = 14
SHED_TILES = ((4, 4), (5, 4), (4, 5), (5, 5))  # engine _shed_access_tiles(10)

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


_OPENING_LAYOUT_CACHE = {}


def _fib(n):
    """Daily hire cost at order index n (engine's 1, 1, 2, 3, ... ladder)."""
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def _opening_layout(tiles, unlocked):
    """Derive a compact 5-pasture/10+10 crop layout from available land.

    Pastures occupy the five cells closest to the shed-facing quadrant corner.
    Crop cells are split into two ten-cell clusters by testing every pair of
    candidate centers and minimizing aggregate Manhattan worker travel.
    The first unlocked quadrant retains the original animal/crop opener;
    additional unlocked quadrants become state-derived crop capacity.
    """
    height = len(tiles)
    width = len(tiles[0]) if height else 0
    labels = tuple(unlocked or ["NW"])
    label = labels[0]
    cache_key = (width, height, labels)
    if cache_key in _OPENING_LAYOUT_CACHE:
        return _OPENING_LAYOUT_CACHE[cache_key]
    west = "W" in label
    north = "N" in label
    x0, x1 = (0, width // 2) if west else (width // 2, width)
    y0, y1 = (0, height // 2) if north else (height // 2, height)
    cells = [(x, y) for y in range(y0, y1) for x in range(x0, x1)]
    home = (x1 - 1 if west else x0, y1 - 1 if north else y0)
    md = lambda a, b: abs(a[0] - b[0]) + abs(a[1] - b[1])
    pasture = sorted(cells, key=lambda p: (md(p, home), p[1], p[0]))[:5]
    plots = [p for p in cells if p not in set(pasture)]
    best = None
    for i, a in enumerate(plots):
        for b in plots[i + 1:]:
            # Assign exactly ten plots to each field by relative center cost.
            ranked = sorted(plots, key=lambda p: (md(p, a) - md(p, b), p[1], p[0]))
            field_a, field_b = ranked[:10], ranked[10:]
            cost = sum(md(p, a) for p in field_a) + sum(md(p, b) for p in field_b)
            cost += md(home, a) + md(home, b)
            key = (cost, a[1], a[0], b[1], b[0])
            if best is None or key < best[0]:
                best = (key, field_a, field_b)
    if best is None:
        result = ((), (), (), (), ())
        _OPENING_LAYOUT_CACHE[cache_key] = result
        return result
    # Stable identity assignment removes any dependence on iteration order.
    f0, f1 = best[1], best[2]
    if (min((p[1], p[0]) for p in f1)) < (min((p[1], p[0]) for p in f0)):
        f0, f1 = f1, f0
    melon = sorted(f1, key=lambda p: (md(p, home), p[1], p[0]))
    wheat = sorted(f0, key=lambda p: (md(p, home), p[1], p[0]))
    cows = tuple(pasture[:2])
    sheep = tuple(pasture[2:])
    # Every later unlocked quadrant becomes additional, state-derived crop
    # capacity.  Keep its cells out of the initial pasture footprint; the
    # first quadrant's animal service load remains fixed while the worker
    # planner can service the new fields anywhere on the board.
    extra_wheat, extra_melon = [], []
    for extra_label in labels[1:]:
        extra_west = "W" in extra_label
        extra_north = "N" in extra_label
        ex0, ex1 = (0, width // 2) if extra_west else (width // 2, width)
        ey0, ey1 = (0, height // 2) if extra_north else (height // 2, height)
        quadrant_cells = [(x, y) for y in range(ey0, ey1) for x in range(ex0, ex1)]
        quadrant_home = (ex0 if extra_west else ex1 - 1, ey0 if extra_north else ey1 - 1)
        quadrant_cells.sort(key=lambda p: (md(p, SHED_ACCESS), md(p, quadrant_home), p[1], p[0]))
        split = (len(quadrant_cells) + 1) // 2
        extra_wheat.extend(quadrant_cells[:8])
        extra_melon.extend(quadrant_cells[split:split + 12])
    wheat.extend(extra_wheat)
    melon_extra = tuple(extra_melon)
    result = (tuple(wheat), tuple(melon[:6]), tuple(melon[6:]), cows, sheep, melon_extra)
    _OPENING_LAYOUT_CACHE[cache_key] = result
    return result


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


def _champion_agent(observation):
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

    # exp-0044: care for ALL placed animals, not just COW_PASTURES. The
    # scripted top-opener places cows/sheep at tiles outside the champion's
    # zones (e.g. cow2 at (3,1), sheep at (3,3)/(2,3)/(3,4)); animals escape
    # after 2 consecutive unfed days, so off-zone livestock must be covered
    # or the opener's roster bleeds away on days 2-3.
    for _y in range(len(tiles)):
        for _x in range(len(tiles[_y])):
            if (_x, _y) in COW_PASTURES:
                continue
            _tile = tiles[_y][_x]
            if isinstance(_tile, dict) and "animal" in _tile:
                if not _tile.get("fed_today", False):
                    hungry.append((_x, _y))
                if not _tile.get("cared_today", False):
                    uncared.append((_x, _y))

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
    # 2 straw, 3 sheep, 4 geese, 5 sheep2, 6 straw2). Placeholders keep roles
    # stable: each earlier role is hired whenever any later role is active, so
    # the sheep2 hand is always index 5 and the straw2 hand is always index 6.
    # Sixth hire costs fib=8 coins/day; it is ordered only on the d3_straw
    # trigger AND from day 6+ so days 3-5 hires match the champion exactly
    # (non-trigger days keep the champion's hire ladder every day).
    _straw2_hire = straw2_active and day >= 6
    geese_active = goose_total >= 1 or (10 <= day <= 12)
    if (straw_active or sheep_active or geese_active or sheep2_active or _straw2_hire) and hour == 0 and not farm.get("hands"):
        market.append(["HIRE"])
    if (sheep_active or geese_active or sheep2_active or _straw2_hire) and hour == 0 and not farm.get("hands"):
        market.append(["HIRE"])
    if (geese_active or sheep2_active or _straw2_hire) and hour == 0 and not farm.get("hands"):
        market.append(["HIRE"])
    if (sheep2_active or _straw2_hire) and hour == 0 and not farm.get("hands"):
        market.append(["HIRE"])
    if _straw2_hire and hour == 0 and not farm.get("hands"):
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
    placed_total = placed_cows + sheep_placed + goose_placed + sheep2_placed
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
        point for point in GOOSE_COOPS
        if isinstance(tiles[point[1]][point[0]], dict)
        and tiles[point[1]][point[0]].get("kind") == "COOP"
        and "animal" not in tiles[point[1]][point[0]]
    ]
    if bare:
        target = _nearest(farmer_position, bare)
        build_op = "BUILD_COOP" if target in GOOSE_COOPS else "BUILD_PASTURE"
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
        target = _nearest(farmer_position, goose_empty)
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
        # Ferry shed geese to built empty coops.
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
        else:
            # Hand-6: sole planter of STRAW2_FIELD. Fixed tile ownership:
            # hand-2 never enters STRAW2_FIELD and hand-6 never enters
            # STRAW_FIELD, so full watering/fertilizing holds on both plots.
            # Plant serialization: the engine drops ALL same-crop PLANTs on a
            # turn when demand exceeds seeds, so hand-6 plants only after
            # plot 1 is full (seeds=0 keeps it on water/weed/fertilize duty).
            # This keeps one effective planter per crop per turn.
            _s6_seeds = 0 if straw_empty else straw_seeds
            hand_actions.append(_straw_action(tuple(position), hand_inventory, tiles, _s6_seeds, day, hand_inventory.get("FERTILIZER", 0), shed_fert, STRAW2_FIELD))

    return {"farmer": farmer, "hands": hand_actions, "market": market}


def _dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _nearest_shed(pos):
    return min(SHED_TILES, key=lambda p: (_dist(pos, p), p))


def _go(pos, target, op):
    return list(op) if pos == target else _move_toward(pos, target)


def _empty_structures(tiles, kind):
    out = []
    for y in range(5):
        for x in range(5):
            tile = tiles[y][x]
            if isinstance(tile, dict) and tile.get("kind") == kind and "animal" not in tile:
                out.append((x, y))
    return out


def _bridge_state(observation):
    player = observation["player"]
    farm = observation["farms"][player]
    private = observation.get("private", None) or {}
    inventories = private.get("inventories", None) or [{}]
    units = [["farmer", tuple(farm["farmer"]), dict(inventories[0] if inventories else {})]]
    for i, pos in enumerate(farm.get("hands", None) or []):
        inv = inventories[i + 1] if i + 1 < len(inventories) else {}
        units.append([f"hand{i + 1}", tuple(pos), dict(inv)])
    return {
        "tiles": farm["tiles"],
        "unlocked": list(farm.get("unlocked_quadrants", None) or ["NW"]),
        "day": observation["day"],
        "hour": observation.get("hour", 0),
        "units": units,
        "shed": dict(private.get("shed", None) or {}),
        "seeds": dict(private.get("seeds", None) or {}),
        "money": float(farm["money"]),
        "prices": ((observation.get("market", None) or {}).get("prices", None) or {}),
        "shops": list((observation.get("town", None) or {}).get("unlocked_shops", None) or []),
    }


def _emit_task(task, unit, shed):
    _pri, _seq, pos, kind, payload, _bound = task
    _name, upos, uinv = unit
    if kind == "place":
        return _go(upos, pos, ["PLACE", payload])
    if kind == "build":
        return _go(upos, pos, ["BUILD_COOP" if payload["structure"] == "COOP" else "BUILD_PASTURE"])
    if kind == "fetch":
        target = _nearest_shed(upos)
        if upos == target:
            return ["PICKUP", payload, 1]
        return _move_toward(upos, target)
    if kind == "feed":
        if uinv.get("WHEAT"):
            return _go(upos, pos, ["FEED"])
        target = _nearest_shed(upos)
        if upos == target:
            if shed.get("WHEAT", 0) > 0:
                return ["PICKUP", "WHEAT", min(3, shed["WHEAT"])]
            return ["PASS"]
        return _move_toward(upos, target)
    if kind == "care":
        return _go(upos, pos, ["CARE"])
    if kind == "harvest":
        return _go(upos, pos, ["HARVEST"])
    if kind == "water":
        return _go(upos, pos, ["WATER"])
    if kind == "fertilize":
        if uinv.get("FERTILIZER", 0) > 0:
            return _go(upos, pos, ["FERTILIZE"])
        target = _nearest_shed(upos)
        if upos == target and shed.get("FERTILIZER", 0) > 0:
            return ["PICKUP", "FERTILIZER", 1]
        if upos != target:
            return _move_toward(upos, target)
        return ["PASS"]
    if kind == "collect":
        return _go(upos, pos, ["COLLECT_FERTILIZER"])
    if kind == "drop":
        target = _nearest_shed(upos)
        if upos == target:
            return ["DROP"]
        return _move_toward(upos, target)
    if kind == "plant":
        return _go(upos, pos, ["PLANT", payload])
    if kind == "dig":
        return _go(upos, pos, ["DIG"])
    return ["PASS"]


def _bridge_market(s, stats, day):
    shed = s["shed"]
    seeds = s["seeds"]
    money = s["money"]
    prices = s["prices"]
    market = []

    # Sells first (orders execute in order): continuous cash flow.
    for item in ("MILK", "WOOL", "EGG", "MELON", "STRAWBERRY"):
        if shed.get(item, 0) > 0:
            market.append(["SELL", item, shed[item]])
    fertilizer_keep = min(shed.get("FERTILIZER", 0), stats.get("straw_fert_due", 0))
    sell_fert = max(0, shed.get("FERTILIZER", 0) - fertilizer_keep)
    if sell_fert:
        market.append(["SELL", "FERTILIZER", sell_fert])
    if stats.get("straw_fert_due", 0) > 0:
        available_fert = shed.get("FERTILIZER", 0) + stats.get("carried_fertilizer", 0)
        shortfall = max(0, stats["straw_fert_due"] - available_fert)
        fert_price = prices.get("FERTILIZER", 100)
        if shortfall and fert_price <= 100 and money >= 1000 + shortfall * fert_price:
            market.append(["BUY_PRODUCT", "FERTILIZER", shortfall])
    shed_wheat = shed.get("WHEAT", 0)
    wheat_buffer = stats["animals_placed"] + 2
    if day >= 2 and shed_wheat - wheat_buffer >= 5:
        market.append(["SELL", "WHEAT", shed_wheat - wheat_buffer])
    # Day-0 cash bridge: the capital ladder needs the last wheat seeds, which
    # current stock can bridge the final seed purchase.
    if day == 0 and money < 100 and shed_wheat > 2:
        market.append(["SELL", "WHEAT", 1])

    # The submitted V66 policy never bought land, leaving its planner confined
    # to one 25-cell quadrant.  Unlock one additional quadrant at a time as
    # cash permits; _opening_layout turns each unlock into wheat/melon fields.
    unlocked = len(s["unlocked"])
    desired_unlocked = 1 + int(day >= 6) + int(day >= 12)
    land_prices = (1000, 2000, 4000)
    if unlocked < min(desired_unlocked, 4):
        land_cost = land_prices[unlocked - 1]
        expansion_seed_budget = 12 * STRAW_SEED_COST + (12 - 12) * MELON_SEED_COST + 8 * WHEAT_SEED_COST
        land_reserve = 1000
        strawberry_demand = any(shop in STRAW_SHOPS for shop in s["shops"])
        strawberry_price = prices.get("STRAWBERRY", 0)
        if strawberry_demand and strawberry_price >= 100 and money >= land_cost + expansion_seed_budget + land_reserve:
            market.append(["BUY_LAND"])

    # Expand worker capacity with the planned farm.  These daily targets are
    # affordable only when the full Fibonacci hire ladder leaves operating
    # cash for feed and seed; otherwise retain the proven five-hand core.
    if day <= 1:
        target = OPENING_HANDS_TARGET
    elif day <= 5:
        target = BRIDGE_HANDS_TARGET
    elif day <= 8:
        target = 7
    else:
        target = 8
    # V70 capacity overlay: buy same-day labor only when the live, reachable
    # queue has profitable work beyond the baseline crew's one-day capacity.
    # `marginal_work_value` is already haircut for uncertain market acceptance.
    if s.get("hour", 0) <= 1:
        backlog = max(0.0, stats.get("estimated_work", 0.0) - 24 * (len(s["units"])))
        marginal_value = stats.get("marginal_work_value", 0.0)
        while target < 14 and backlog > 0:
            next_cost = _fib(len(s["units"]) - 1)
            if marginal_value < next_cost * 1.25:
                break
            target += 1
            backlog = max(0.0, backlog - 20.0)
            marginal_value *= 0.72
    n_hands = len(s["units"]) - 1
    target_cost = sum(_fib(i) for i in range(n_hands, target))
    operating_reserve = 1000 if day < 12 else 1400
    if money < target_cost + operating_reserve:
        target = BRIDGE_HANDS_TARGET if day > 1 else OPENING_HANDS_TARGET
    if n_hands < target and money >= 15:
        market.extend([["HIRE"]] * (target - n_hands))

    # Day-0 all-in capital ladder, guarded by current cash.
    if day == 0:
        cow_want = 2 - stats["cow_total"]
        if cow_want > 0 and money >= COW_COST * cow_want:
            market.append(["BUY_ANIMAL", "COW", cow_want])
        sheep_want = 3 - stats["sheep_total"]
        if sheep_want > 0 and money >= SHEEP_COST * sheep_want:
            market.append(["BUY_ANIMAL", "SHEEP", sheep_want])

    # Geese once coop slots exist (coops are built by the duty planner).
    slots = len(_empty_structures(s["tiles"], "COOP"))
    slots += sum(1 for p in GOOSE_COOPS if s["tiles"][p[1]][p[0]] is None)
    if (
        GOOSE_BUY_FIRST_DAY <= day <= GOOSE_BUY_LAST_DAY
        and stats["goose_total"] < 2
        and slots > 0
        and money >= GOOSE_COST + 50
    ):
        market.append(["BUY_ANIMAL", "GOOSE", min(2 - stats["goose_total"], slots)])

    # Feed buffer before seed money (survival first): one day of cover per
    # placed animal. Day 0 buys nothing — animals can wait a day without
    # escaping and fertilizer income funds day-1 feeding. The day-1 reserve
    # is low on purpose: the first wheat must be bought at h0 because the
    # animals' two-day escape clock started during the day-0 build rush.
    if day >= 1 and stats["animals_placed"] > 0:
        feed_have = shed_wheat + stats["carried_wheat"]
        feed_need = stats["animals_placed"] - feed_have
        reserve = 25 if day == 1 else 60
        if feed_need > 0 and money >= reserve + 1:
            price = max(1, int(prices.get("WHEAT", 25)))
            n = min(feed_need, 3, int((money - reserve) // price))
            if n > 0:
                market.append(["BUY_PRODUCT", "WHEAT", n])

    # Seeds. Melon pairs on the opener days with
    # a single-seed fallback when cash is tight, then continuous replenishment
    # for replant cycles; reserves protect feed cash.
    melon_target = stats["melon_slots"]
    melon_want = melon_target - stats["melon_planted"] - seeds.get("MELON", 0)
    if day <= MELON_REPLANT_BY_DAY and melon_want > 0:
        n = min(2, melon_want)
        reserve = 20 if day <= 1 else 120
        if money >= n * MELON_SEED_COST + reserve:
            market.append(["BUY_SEED", "MELON", n])
        elif money >= MELON_SEED_COST + reserve:
            market.append(["BUY_SEED", "MELON", 1])
    wheat_want = (
        stats["wheat_slots"] + (6 if day == 0 else 0)
        - stats["wheat_planted"] - seeds.get("WHEAT", 0)
    )
    if day <= WHEAT_REPLANT_BY_DAY and wheat_want > 0:
        reserve = 20 if day <= 1 else 60
        n = min(wheat_want, int((money - reserve) // WHEAT_SEED_COST))
        if n > 0:
            market.append(["BUY_SEED", "WHEAT", n])
    strawberry_want = (
        stats.get("strawberry_slots", 0) - stats.get("strawberry_planted", 0)
        - seeds.get("STRAWBERRY", 0)
    )
    if day <= 11 and strawberry_want > 0:
        reserve = 1000 if day < 12 else 1400
        n = min(strawberry_want, max(0, int((money - reserve) // STRAW_SEED_COST)))
        if n > 0:
            market.append(["BUY_SEED", "STRAWBERRY", n])
    return market


# Sticky per-unit goals (per player): carriers keep their build/place spot
# across turns and open tasks keep their unit, so re-deriving the same plan
# each turn does not make units oscillate between equally-distant targets.
_UNIT_GOALS = {}


def _bridge_agent(observation):
    """exp-0044: state-derived top opener (days 0-1) + monotone day-2 bridge.

    Every turn derives duties from live tile state: place/fetch/build the
    five-pasture roster, feed/care all animals, harvest before crop decay,
    water every unwatered plant (planting-day watering is mandatory), plant
    the fixed wheat/melon footprints from seed stock, collect and sell the
    daily fertilizer flow. The opening capital ladder targets the fixed
    starting herd, worker count, and crop portfolio from live farm state.
    """
    s = _bridge_state(observation)
    tiles = s["tiles"]
    day = s["day"]
    shed = s["shed"]
    seeds = s["seeds"]
    prices = s["prices"]
    units = s["units"]

    wheat_tiles, melon_day0, melon_day1, cow_spots, sheep_spots, expansion_cells = _opening_layout(tiles, s["unlocked"])
    melon_tiles = melon_day0 if day == 0 else melon_day0 + melon_day1
    strawberry_demand = any(shop in STRAW_SHOPS for shop in s["shops"])
    strawberry_tiles = expansion_cells if len(s["unlocked"]) > 1 and strawberry_demand and prices.get("STRAWBERRY", 0) >= 100 else ()
    if strawberry_tiles:
        melon_tiles = tuple(p for p in melon_tiles if p not in strawberry_tiles)
    pasture_spots = cow_spots + sheep_spots

    animal_tiles = {}
    for y in range(len(tiles)):
        for x in range(len(tiles[y])):
            tile = tiles[y][x]
            if isinstance(tile, dict) and "animal" in tile:
                animal_tiles[(x, y)] = tile

    cows_placed = sum(1 for t in animal_tiles.values() if t["animal"] == "COW")
    sheep_placed = sum(1 for t in animal_tiles.values() if t["animal"] == "SHEEP")
    goose_placed = sum(1 for t in animal_tiles.values() if t["animal"] == "GOOSE")
    animals_placed = cows_placed + sheep_placed + goose_placed
    carried = {"COW": 0, "SHEEP": 0, "GOOSE": 0}
    carried_wheat = 0
    carried_fertilizer = 0
    for _name, _pos, inv in units:
        for animal in carried:
            carried[animal] += inv.get(animal, 0)
        carried_wheat += inv.get("WHEAT", 0)
        carried_fertilizer += inv.get("FERTILIZER", 0)
    melon_planted = sum(
        1
        for p in melon_tiles
        if isinstance(tiles[p[1]][p[0]], dict)
        and tiles[p[1]][p[0]].get("kind") == "PLANT"
        and tiles[p[1]][p[0]].get("crop") == "MELON"
    )
    wheat_planted = sum(
        1
        for p in wheat_tiles
        if isinstance(tiles[p[1]][p[0]], dict)
        and tiles[p[1]][p[0]].get("kind") == "PLANT"
        and tiles[p[1]][p[0]].get("crop") == "WHEAT"
    )
    straw_planted = sum(
        1 for p in strawberry_tiles
        if isinstance(tiles[p[1]][p[0]], dict)
        and tiles[p[1]][p[0]].get("kind") == "PLANT"
        and tiles[p[1]][p[0]].get("crop") == "STRAWBERRY"
    )
    straw_fert_due = _straw_fert_due(tiles, day, strawberry_tiles)
    stats = {
        "cow_total": cows_placed + carried["COW"] + shed.get("COW", 0),
        "sheep_total": sheep_placed + carried["SHEEP"] + shed.get("SHEEP", 0),
        "goose_total": goose_placed + carried["GOOSE"] + shed.get("GOOSE", 0),
        "goose_placed": goose_placed,
        "animals_placed": animals_placed,
        "melon_planted": melon_planted,
        "wheat_planted": wheat_planted,
        "carried_wheat": carried_wheat,
        "wheat_slots": len(wheat_tiles),
        "melon_slots": len(melon_tiles),
        "strawberry_planted": straw_planted,
        "strawberry_slots": len(strawberry_tiles),
        "straw_fert_due": len(straw_fert_due),
        "carried_fertilizer": carried_fertilizer,
    }

    # Priorities (lower = first). Day 0: builds, animal placement and the
    # plant/water pair own the whole day — feeding/care slip to day 1 (one
    # unfed day is recoverable; a missed planting-day watering kills the
    # plant that night). Day 1+: feeding and care are escape/bonus-critical
    # and outrank the watering wave, which has until nightfall anyway;
    # fertilizer collection follows right behind (it funds feed and seeds).
    plant_pri = 1 if day <= 1 else 4
    water_pri = 1 if day == 0 else 3
    fresh_water_pri = 0.5  # a plant with no water buffer dies tonight
    collect_pri = 0.45 if day <= 1 else 4
    feed_pri = 6 if day == 0 else 0.4
    care_pri = 7 if day == 0 else 2
    harvest_animal_pri = 2 if day <= 1 else 2.5

    tasks = []

    def add(pri, pos, kind, payload=None, bound=None):
        tasks.append([pri, len(tasks), pos, kind, payload, bound])

    # Per-turn target claims: bound tasks pick distinct structures/spots so
    # two carriers never converge on the same tile (the second PLACE/BUILD
    # would no-op and strand the animal or waste the hand).
    claimed = set()

    # 0: carried animals -> place on an empty structure or build their spot.
    # Carriers keep their chosen spot across turns (sticky goal) so a build
    # target never switches mid-walk.
    goals = _UNIT_GOALS.setdefault(observation["player"], {})
    for ui, (_name, pos, inv) in enumerate(units):
        for animal in ("COW", "SHEEP", "GOOSE"):
            if not inv.get(animal):
                goals.pop(ui, None)
                continue
            structure = "COOP" if animal == "GOOSE" else "PASTURE"
            spots = (
                GOOSE_COOPS
                if animal == "GOOSE"
                else (cow_spots if animal == "COW" else sheep_spots)
            )
            goal = goals.get(ui)
            tile = tiles[goal[1]][goal[0]] if goal else None
            goal_valid = (
                goal in spots
                and (
                    (isinstance(tile, dict) and tile.get("kind") == structure and "animal" not in tile)
                    or tile is None
                )
            )
            if not goal_valid:
                empty = [p for p in _empty_structures(tiles, structure) if p not in claimed]
                buildable = [p for p in spots if tiles[p[1]][p[0]] is None and p not in claimed]
                if empty:
                    goal = min(empty, key=lambda p: (_dist(pos, p), p))
                    claimed.add(goal)
                    add(0, goal, "place", animal, ui)
                    goals[ui] = goal
                    continue
                if buildable:
                    goal = min(buildable, key=lambda p: (_dist(pos, p), p))
                    claimed.add(goal)
                    goals[ui] = goal
                    add(0, goal, "build", {"structure": structure}, ui)
                    continue
                continue  # no slot this turn; keep carrying
            claimed.add(goal)
            if isinstance(tile, dict):
                add(0, goal, "place", animal, ui)
            else:
                add(0, goal, "build", {"structure": structure}, ui)

    # 1: fetch shed animals while placement slots exist. Geese are fetched on
    # any day a free coop exists (their buy window is days 10-14; an unfetched
    # goose strands in the shed and produces nothing).
    if day <= 2:
        for animal in ("COW", "SHEEP"):
            n_shed = shed.get(animal, 0)
            if n_shed <= 0:
                continue
            spots = cow_spots if animal == "COW" else sheep_spots
            slots = len([p for p in _empty_structures(tiles, "PASTURE") if p not in claimed])
            slots += sum(1 for p in spots if tiles[p[1]][p[0]] is None and p not in claimed)
            slots -= carried[animal]
            for _ in range(min(n_shed, max(0, slots))):
                add(1, (4, 4), "fetch", animal)
    goose_shed = shed.get("GOOSE", 0)
    if goose_shed > 0:
        free_coops = len([p for p in _empty_structures(tiles, "COOP") if p not in claimed])
        for _ in range(min(goose_shed, max(0, free_coops - carried["GOOSE"]))):
            add(1, (4, 4), "fetch", "GOOSE")

    # 1: day-0 pastures (the farmer builds its own spawn corner while the
    # market buys the first cow).
    if day == 0:
        for p in pasture_spots:
            if tiles[p[1]][p[0]] is None and p not in claimed:
                claimed.add(p)
                add(1, p, "build", {"structure": "PASTURE"})

    # 2: feed hungry animals (escape needs 2 consecutive unfed days). Only as
    # many tasks as there is wheat to actually deliver, and skipped entirely
    # when no wheat exists anywhere — a pickup shuttle with an empty shed
    # must not occupy units.
    feed_have = stats["carried_wheat"] + shed.get("WHEAT", 0)
    if feed_have > 0:
        for p, t in sorted(animal_tiles.items()):
            if not t.get("fed_today", False) and feed_have > 0:
                feed_have -= 1
                add(feed_pri, p, "feed")

    # 2: deadline harvests (decay kills one-shot crops after max_yield_day+1).
    for p in wheat_tiles:
        tile = tiles[p[1]][p[0]]
        if (
            isinstance(tile, dict)
            and tile.get("kind") == "PLANT"
            and tile.get("crop") == "WHEAT"
            and tile.get("yield_units", 0) > 0
            and (day - tile["planted_day"] >= WHEAT_MAX_YIELD_DAY or tile["yield_units"] >= 4)
        ):
            add(2, p, "harvest")
    for p in melon_tiles:
        tile = tiles[p[1]][p[0]]
        if (
            isinstance(tile, dict)
            and tile.get("kind") == "PLANT"
            and tile.get("crop") == "MELON"
            and tile.get("yield_units", 0) > 0
            and (tile["yield_units"] >= 5 or day - tile["planted_day"] >= MELON_MAX_YIELD_DAY)
        ):
            add(2, p, "harvest")

    # 3: care (fed+cared same day accrues the production bonus).
    for p, t in sorted(animal_tiles.items()):
        if not t.get("cared_today", False):
            add(care_pri, p, "care")

    # 4: harvest animal products (milk day 8+, wool day 6+, eggs).
    for p, t in sorted(animal_tiles.items()):
        if t.get("yield_units", 0) > 0:
            add(harvest_animal_pri, p, "harvest")

    # 3: goose coops (day 4+; outranks replanting so the coop spots are not
    # recropped). Window extends to day 14: the (3,2) melon tile only frees
    # on day 13 (its day-1 planting reaches age 12 then).
    if GOOSE_BUILD_FIRST_DAY <= day <= GOOSE_BUILD_LAST_DAY and stats["goose_placed"] < 2:
        for p in GOOSE_COOPS:
            if tiles[p[1]][p[0]] is None:
                add(3, p, "build", {"structure": "COOP"})

    # 3: water every unwatered plant while its window is open. A plant from
    # TODAY gets the fresh-water priority: it counts 1 unwatered day at
    # creation, so missing tonight kills it regardless of the yield window.
    for p in wheat_tiles:
        tile = tiles[p[1]][p[0]]
        if (
            isinstance(tile, dict)
            and tile.get("kind") == "PLANT"
            and tile.get("crop") == "WHEAT"
            and not tile.get("watered_today", False)
            and (tile.get("planted_day") == day or tile.get("consecutive_unwatered", 0) >= 1)
            and day - tile["planted_day"] <= WHEAT_MAX_YIELD_DAY
        ):
            add(fresh_water_pri, p, "water")

    for p in strawberry_tiles:
        tile = tiles[p[1]][p[0]]
        if not (isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == "STRAWBERRY"):
            continue
        if (
            not tile.get("watered_today", False)
            and (
                tile.get("planted_day") == day
                or tile.get("consecutive_unwatered", 0) >= 1
                or p in straw_fert_due
            )
        ):
            add(fresh_water_pri, p, "water")
        if tile.get("yield_units", 0) > 0:
            add(harvest_animal_pri, p, "harvest")
    for p in straw_fert_due:
        add(2.7, p, "fertilize")
    for p in melon_tiles:
        tile = tiles[p[1]][p[0]]
        if (
            isinstance(tile, dict)
            and tile.get("kind") == "PLANT"
            and tile.get("crop") == "MELON"
            and not tile.get("watered_today", False)
            and (tile.get("planted_day") == day or tile.get("consecutive_unwatered", 0) >= 1)
            and day - tile["planted_day"] <= MELON_WATER_WINDOW_LAST
        ):
            add(fresh_water_pri, p, "water")

    # 6: collect fertilizer (1/animal/day) and ship products to the shed so
    # same-turn sells can see them.
    if prices.get("FERTILIZER", 0) >= 40:
        for p, t in sorted(animal_tiles.items()):
            if t.get("fertilizer_available", False):
                add(collect_pri, p, "collect")
    for ui, (_name, pos, inv) in enumerate(units):
        if any(v for k, v in inv.items() if k not in ("WHEAT", "COW", "SHEEP", "GOOSE")):
            add(6, _nearest_shed(pos), "drop", None, ui)

    # Plant the fixed footprints from seed stock (aggregate-PLANT safe).
    # Per-tile deadline: a plant only pays if it can still be watered today
    # (plant + water + travel must fit before hour 23); as that slack closes
    # the task's priority is boosted so it jumps the watering queue.
    def _plant_task(p, crop, stock):
        if stock <= 0 or not (tiles[p[1]][p[0]] is None):
            return stock
        mind = min(_dist(u[1], p) for u in units)
        slack = 21 - s["hour"] - mind
        if slack < -1:
            return stock
        # Urgency: as the plant+water window closes, jump the normal watering
        # queue — but never ahead of a fresh-plant water (floor 0.5).
        add(max(0.5, plant_pri - max(0, 6 - slack)), p, "plant", crop)
        return stock - 1

    # While the coop build window is open with geese still owed, reserve the
    # coop spots from replanting: the same-turn harvest->replant pipeline
    # otherwise never leaves those tiles None, so BUILD_COOP can never fire
    # (this stranded two bought geese in the shed in the regression audit).
    reserve_coop_spots = (
        GOOSE_BUILD_FIRST_DAY <= day <= GOOSE_BUILD_LAST_DAY and stats["goose_placed"] < 2
    )
    melon_stock = seeds.get("MELON", 0)
    if day <= MELON_REPLANT_BY_DAY:
        for p in melon_tiles:
            if reserve_coop_spots and p in GOOSE_COOPS:
                continue
            melon_stock = _plant_task(p, "MELON", melon_stock)
    wheat_stock = seeds.get("WHEAT", 0)
    if day <= WHEAT_REPLANT_BY_DAY:
        for p in wheat_tiles:
            if reserve_coop_spots and p in GOOSE_COOPS:
                continue
            wheat_stock = _plant_task(p, "WHEAT", wheat_stock)

    strawberry_stock = seeds.get("STRAWBERRY", 0)
    if day <= 11 and strawberry_demand and prices.get("STRAWBERRY", 0) >= 100:
        for p in strawberry_tiles:
            strawberry_stock = _plant_task(p, "STRAWBERRY", strawberry_stock)

    # 7: weeds block planting on the planned footprints.
    for p in melon_tiles + wheat_tiles:
        tile = tiles[p[1]][p[0]]
        if isinstance(tile, dict) and tile.get("kind") == "WEED":
            add(7, p, "dig")

    # Batch assignment by strict urgency bands. Bound work (for example, a
    # carrier placing its own animal) remains actor-specific, but no longer
    # jumps ahead of more urgent open work merely because it is bound. Within
    # each priority band, repeatedly choose the globally cheapest unit/task
    # pair; this avoids the task-first greedy assignment sending the nearest
    # worker away when another worker can cover that task cheaply.
    goals = _UNIT_GOALS.setdefault(observation["player"], {})
    last_task = goals.setdefault("_last", {})
    plan = {}
    free = set(range(len(units)))

    def _pair_cost(ui, task):
        _name, upos, uinv = units[ui]
        kind, pos = task[3], task[2]
        cost = _dist(upos, pos)
        if kind == "feed" and not uinv.get("WHEAT"):
            cost += _dist(upos, _nearest_shed(upos)) + 3
        if kind == "build" and ui == 0 and pos != (4, 4):
            cost += 4
        if last_task.get(ui) == pos:
            cost -= 2.5
        return cost

    priorities = sorted({task[0] for task in tasks})
    for pri in priorities:
        band = [task for task in tasks if task[0] == pri]
        # Actor-specific tasks are mandatory for that actor, but obey this
        # band’s urgency instead of preempting every lower-priority number.
        for task in sorted((t for t in band if t[5] is not None), key=lambda t: t[1]):
            ui = task[5]
            if ui in free:
                plan[ui] = _emit_task(task, units[ui], shed)
                free.discard(ui)
        open_tasks = [task for task in band if task[5] is None]
        while free and open_tasks:
            best = min(
                ((_pair_cost(ui, task), ui, task[1], idx)
                 for idx, task in enumerate(open_tasks)
                 for ui in free),
                key=lambda row: (row[0], row[1], row[2]),
            )
            _cost, ui, _tid, idx = best
            task = open_tasks.pop(idx)
            plan[ui] = _emit_task(task, units[ui], shed)
            last_task[ui] = task[2]
            free.discard(ui)

    # Estimate a conservative one-day action route: one operation plus the
    # nearest crew's distance for every live task. Value only jobs with an
    # observable price or a clear preservation payoff, then haircut gross
    # quotes because town acceptance is not guaranteed.
    estimated_work = 0.0
    gross_value = 0.0
    for task in sorted(tasks, key=lambda row: (row[0], row[1])):
        pos, kind = task[2], task[3]
        travel = min(_dist(unit[1], pos) for unit in units)
        estimated_work += 1.0 + travel
        tile = tiles[pos[1]][pos[0]]
        value = 0.0
        if kind == "collect":
            value = prices.get("FERTILIZER", 0)
        elif kind == "harvest":
            if isinstance(tile, dict) and tile.get("kind") == "PLANT":
                item = tile.get("crop", "")
                value = prices.get(item, 0) * max(1, tile.get("yield_units", 1))
            elif isinstance(tile, dict):
                animal = tile.get("animal")
                item = {"COW": "MILK", "SHEEP": "WOOL", "GOOSE": "EGG"}.get(animal, "")
                value = prices.get(item, 0) * max(1, tile.get("yield_units", 1))
        elif kind in ("water", "fertilize") and isinstance(tile, dict):
            crop = tile.get("crop", "")
            value = prices.get(crop, 0) * max(1, tile.get("yield_units", 1)) * 0.35
        elif kind in ("feed", "care"):
            # Protecting an animal preserves future output and fertilizer.
            value = 12.0
        gross_value += value
    stats["estimated_work"] = estimated_work * 0.85
    stats["marginal_work_value"] = gross_value * 0.40
    actions = [plan.get(ui, ["PASS"]) for ui in range(len(units))]
    return {
        "farmer": actions[0],
        "hands": actions[1:],
        "market": _bridge_market(s, stats, day),
    }



def agent(observation):
    # exp-0044: the state-derived top opener + day-2 bridge drives every
    # turn; the champion body remains only as an anomaly fallback.
    try:
        return _bridge_agent(observation)
    except Exception:
        return _champion_agent(observation)

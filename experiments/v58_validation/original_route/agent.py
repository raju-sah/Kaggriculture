"""Independent observation-conditioned Kaggriculture controller.

This is a small task allocator built from the public engine's action/state
contract. It does not encode a replay's step sequence or import another agent.
"""
from __future__ import annotations

from collections import Counter


SHOP_GOODS = {
    "BAKERY": ("EGG", "WHEAT"), "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"), "YARN_STORE": ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"), "PET_CAFE": ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}
CROPS = {
    "WHEAT": {"seed": 10, "first": 2, "interval": 0, "yield": 6, "repeat": 1},
    "CARROT": {"seed": 20, "first": 2, "interval": 0, "yield": 4, "repeat": 1},
    "MELON": {"seed": 80, "first": 10, "interval": 0, "yield": 6, "repeat": 1},
    "TOMATO": {"seed": 50, "first": 8, "interval": 1, "yield": 4, "repeat": 4},
    "STRAWBERRY": {"seed": 100, "first": 10, "interval": 2, "yield": 4, "repeat": 4},
}
ANIMALS = {"GOOSE", "COW", "SHEEP"}
ANIMAL_GOODS = {"GOOSE": "EGG", "COW": "MILK", "SHEEP": "WOOL"}


def _step(obs):
    return int(obs.get("step", int(obs.get("day", 0)) * 24 + int(obs.get("hour", 0))))


def _shed_tiles(size):
    h = size // 2
    return [(h - 1, h - 1), (h, h - 1), (h - 1, h), (h, h)]


def _move(src, dst):
    x, y = src
    tx, ty = dst
    if x < tx: return ["EAST"]
    if x > tx: return ["WEST"]
    if y < ty: return ["SOUTH"]
    if y > ty: return ["NORTH"]
    return ["PASS"]


def _distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _crop_value(crop, obs, step, expected_supply):
    spec = CROPS[crop]
    day = step // 24
    day_left = max(0, 29 - day)
    if spec["first"] > day_left:
        return -1e9
    events = 1 if spec["repeat"] == 1 else min(spec["repeat"], 1 + (day_left - spec["first"]) // spec["interval"])
    output = events * spec["yield"]
    shops = (obs.get("town") or {}).get("unlocked_shops", [])
    shop_rate = sum(1 for name in shops if crop in SHOP_GOODS.get(name, ())) * 6
    # Demand counts one unit/day from the town center and six/shop-instance/day.
    demand = (30 - day) * (1 + shop_rate)
    available_demand = max(0, demand - expected_supply.get(crop, 0))
    price = float(((obs.get("market") or {}).get("prices") or {}).get(crop, 0))
    units = min(output, available_demand)
    delay = max(1, spec["first"])
    return (units * price - spec["seed"]) / delay


def _choose_crop(obs, step, expected_supply):
    prices = (obs.get("market") or {}).get("prices") or {}
    pool = [crop for crop in CROPS if prices.get(crop, 0) > 1]
    return max(pool, key=lambda c: (_crop_value(c, obs, step, expected_supply), c == "WHEAT")) if pool else "WHEAT"


def agent(obs, configuration=None):
    farms = obs.get("farms") or []
    player = int(obs.get("player", 0) or 0)
    if player >= len(farms):
        return {"farmer": ["PASS"], "hands": [], "market": []}
    farm = farms[player]
    private = obs.get("private") or {}
    day = int(obs.get("day", 0) or 0)
    step = _step(obs)
    board = farm.get("tiles") or []
    size = len(board) or 10
    pos = [farm.get("farmer", [0, 0]), *(farm.get("hands") or [])]
    invs = list(private.get("inventories") or [])
    invs.extend({} for _ in range(len(pos) - len(invs)))
    shed = private.get("shed") or {}
    seeds = private.get("seeds") or {}
    prices = (obs.get("market") or {}).get("prices") or {}
    shops = (obs.get("town") or {}).get("unlocked_shops") or []

    near_term_value = 0.0
    for item, quantity in shed.items():
        if item in CROPS or item in ("EGG", "MILK", "WOOL", "FERTILIZER"):
            near_term_value += max(0, int(quantity or 0)) * float(prices.get(item, 0))
    ready_value = 0.0
    for row in board:
        for tile in row:
            if not isinstance(tile, dict):
                continue
            item = tile.get("crop") if tile.get("kind") == "PLANT" else ANIMAL_GOODS.get(tile.get("animal"))
            if item:
                ready_value += max(0, int(tile.get("yield_units", 0) or 0)) * float(prices.get(item, 0))
    # Discount inventory and yields because simultaneous demand and market
    # price movement make their full quoted value unavailable as cash.
    cashflow = float(farm.get("money", 0) or 0) + 0.55 * (near_term_value + ready_value)
    reserve = 500 + 100 * sum(1 for row in board for tile in row
                              if isinstance(tile, dict) and tile.get("animal") in ANIMALS
                              and not tile.get("fed_today"))

    market = []
    # Sell existing inventory in value order, keeping one day of visible wheat
    # demand in reserve if livestock need feed.
    hungry = sum(1 for row in board for tile in row
                 if isinstance(tile, dict) and tile.get("animal") in ANIMALS and not tile.get("fed_today"))
    wheat_in_hands = sum(int(inv.get("WHEAT", 0) or 0) for inv in invs)
    wheat_reserve = max(0, hungry - wheat_in_hands)
    for item, quantity in sorted(shed.items(), key=lambda kv: prices.get(kv[0], 0), reverse=True):
        if item in ANIMALS or quantity <= 0:
            continue
        sale = max(0, int(quantity) - (wheat_reserve if item == "WHEAT" else 0))
        if sale and len(market) < 10:
            market.append(["SELL", item, sale])

    # Cash gates tie labor to realized or immediately saleable output. Hires
    # disappear at day end, so the controller re-forms a daily crew only while
    # liquid value comfortably exceeds feed/seed reserves and labor cost.
    target_hands = 0 if cashflow < reserve + 150 else 4 if cashflow < reserve + 1500 else 7 if cashflow < reserve + 3500 else 10
    if len(pos) - 1 < target_hands and float(farm.get("money", 0) or 0) > reserve + 20:
        market.insert(0, ["HIRE"])
    quadrants = len(farm.get("unlocked_quadrants") or ["NW"])
    occupied = sum(1 for row in board for tile in row if tile is not None and tile != "LOCKED")
    land_cost = 1000 if quadrants == 1 else 2000 if quadrants == 2 else 4000
    if (5 <= day <= 10 and quadrants < 3 and occupied >= 20 * quadrants
            and float(farm.get("money", 0) or 0) > land_cost + reserve + 1200
            and cashflow > land_cost + reserve + 2500):
        market.insert(1 if market and market[0][0] == "HIRE" else 0, ["BUY_LAND"])

    owned_empty = [(x, y) for y, row in enumerate(board) for x, tile in enumerate(row) if tile is None]
    expected_supply = Counter(shed)
    for row in board:
        for tile in row:
            if isinstance(tile, dict) and tile.get("kind") == "PLANT":
                spec = CROPS.get(tile.get("crop"), {})
                total_cycle = int(spec.get("yield", 0)) * int(spec.get("repeat", 1))
                expected_supply[tile.get("crop")] += max(0, total_cycle - int(tile.get("yield_units", 0) or 0))
    crop = _choose_crop(obs, step, expected_supply)
    empty_count = len(owned_empty)
    needed_seed = max(0, min(6, empty_count, (len(pos) + 1) // 2) - int(seeds.get(crop, 0) or 0))
    if (needed_seed and farm.get("money", 0) >= CROPS[crop]["seed"] * needed_seed + reserve + 100
            and cashflow >= CROPS[crop]["seed"] * needed_seed + reserve + 100 and len(market) < 10):
        market.append(["BUY_SEED", crop, needed_seed])

    # Select small herds from visible shop demand. Buildings, animals and feed
    # are distinct investments; each animal purchase must have an empty
    # matching structure and enough cash left for one hundred feed-reserve
    # coins per prospective animal.
    shop_counts = Counter(item for name in shops for item in SHOP_GOODS.get(name, ()))
    desired = Counter()
    # Start with one animal chosen by conservative net production per day;
    # expand the herd only after a separate feed-throughput test, not because
    # a high shop count alone makes a larger herd look attractive.
    animal_daily_net = {
        "COW": 0.5 * float(prices.get("MILK", 160)) - float(prices.get("WHEAT", 25)),
        "SHEEP": (1 / 3) * float(prices.get("WOOL", 200)) - float(prices.get("WHEAT", 25)),
        "GOOSE": float(prices.get("EGG", 50)) - float(prices.get("WHEAT", 25)),
    }
    shop_gate = {"COW": shop_counts["MILK"], "SHEEP": shop_counts["WOOL"], "GOOSE": shop_counts["EGG"]}
    eligible_animals = [a for a in ANIMALS if shop_gate[a] > 0 and day < 24]
    if eligible_animals:
        preferred = max(eligible_animals, key=lambda a: (animal_daily_net[a], a == "COW"))
        desired[preferred] = 1
    animal_counts = Counter()
    empty_structures = Counter()
    for row in board:
        for tile in row:
            if not isinstance(tile, dict):
                continue
            if tile.get("animal") in ANIMALS:
                animal_counts[tile["animal"]] += 1
            elif tile.get("kind") in ("PASTURE", "COOP"):
                empty_structures[tile["kind"]] += 1
    for inv in invs:
        for animal in ANIMALS:
            animal_counts[animal] += int(inv.get(animal, 0) or 0)
    for animal in ANIMALS:
        animal_counts[animal] += int(shed.get(animal, 0) or 0)
    pasture_goal = max(0, desired["COW"] + desired["SHEEP"] - animal_counts["COW"] - animal_counts["SHEEP"] - empty_structures["PASTURE"])
    coop_goal = max(0, desired["GOOSE"] - animal_counts["GOOSE"] - empty_structures["COOP"])
    if len(market) < 10:
        for animal in ("COW", "SHEEP", "GOOSE"):
            structure = "COOP" if animal == "GOOSE" else "PASTURE"
            open_spot = empty_structures[structure] > int(shed.get(animal, 0) or 0)
            cost = {"COW": 400, "SHEEP": 500, "GOOSE": 300}[animal]
            if (open_spot and animal_counts[animal] < desired[animal]
                    and float(farm.get("money", 0) or 0) > reserve + cost + 600
                    and cashflow > reserve + cost + 1000):
                market.append(["BUY_ANIMAL", animal, 1])
                animal_counts[animal] += 1
                empty_structures[structure] -= 1
                break

    total_wheat = int(shed.get("WHEAT", 0) or 0) + wheat_in_hands
    if hungry > total_wheat and len(market) < 10:
        feed_order = min(hungry - total_wheat, 3)
        wheat_price = float(prices.get("WHEAT", 25))
        if float(farm.get("money", 0) or 0) > reserve + feed_order * wheat_price + 100:
            market.append(["BUY_PRODUCT", "WHEAT", feed_order])

    # Build a fresh task list from visible tiles each turn. Each target has one
    # owner for this turn, preventing collisions among the farmer and hands.
    tasks = []
    if pasture_goal or coop_goal:
        for y, row in enumerate(board):
            for x, tile in enumerate(row):
                if tile is None:
                    if pasture_goal:
                        tasks.append((91.0, (x, y), ["BUILD_PASTURE"], "build_pasture"))
                        pasture_goal -= 1
                    elif coop_goal:
                        tasks.append((90.0, (x, y), ["BUILD_COOP"], "build_coop"))
                        coop_goal -= 1
                    if not pasture_goal and not coop_goal:
                        break
            if not pasture_goal and not coop_goal:
                break
    for y, row in enumerate(board):
        for x, tile in enumerate(row):
            if tile == "LOCKED":
                continue
            xy = (x, y)
            if tile is None:
                if int(seeds.get(crop, 0) or 0) > 0:
                    tasks.append((70.0, xy, ["PLANT", crop], "plant"))
                continue
            if not isinstance(tile, dict):
                continue
            if tile.get("kind") in ("PASTURE", "COOP"):
                compatible = ("GOOSE",) if tile.get("kind") == "COOP" else ("COW", "SHEEP")
                for animal in compatible:
                    if any(int(inv.get(animal, 0) or 0) > 0 for inv in invs):
                        tasks.append((122.0, xy, ["PLACE", animal, 1], "place_animal"))
            kind = tile.get("kind")
            if kind == "WEED":
                tasks.append((65.0, xy, ["DIG"], "weed"))
            elif kind == "PLANT":
                c = tile.get("crop")
                yield_n = int(tile.get("yield_units", 0) or 0)
                if yield_n > 0:
                    tasks.append((105 + min(20, yield_n * prices.get(c, 1) / 100), xy, ["HARVEST"], "harvest"))
                elif not tile.get("watered_today"):
                    # Every crop turns into a weed after two consecutive
                    # unwatered days; one-shot crops also gain yield in their
                    # watering window.
                    first = CROPS.get(c, {}).get("first", 99)
                    age = day - int(tile.get("planted_day", day))
                    bonus_window = max(1, first // 2) <= age <= first + 2
                    tasks.append((84.0 if c in ("TOMATO", "STRAWBERRY") or bonus_window else 74.0,
                                  xy, ["WATER"], "water"))
            elif tile.get("animal") in ANIMALS:
                animal = tile["animal"]
                yielded = int(tile.get("yield_units", 0) or 0)
                if yielded:
                    tasks.append((110 + min(15, yielded * prices.get(ANIMAL_GOODS[animal], 1) / 100), xy, ["HARVEST"], "harvest"))
                if tile.get("fertilizer_available"):
                    tasks.append((58.0, xy, ["COLLECT_FERTILIZER"], "fert"))
                if not tile.get("fed_today") and wheat_in_hands:
                    tasks.append((96.0, xy, ["FEED"], "feed"))
                if not tile.get("cared_today"):
                    tasks.append((45.0, xy, ["CARE"], "care"))

    # A purchased animal waits in the shed. Assign one carrier to the nearest
    # access tile only if a compatible empty structure exists; the following
    # turn the unit's visible inventory pins it to a matching PLACE task.
    for structure, compatible in (("PASTURE", ("COW", "SHEEP")), ("COOP", ("GOOSE",))):
        has_slot = any(isinstance(tile, dict) and tile.get("kind") == structure
                       and "animal" not in tile for row in board for tile in row)
        if has_slot:
            for animal in compatible:
                carried = sum(int(inv.get(animal, 0) or 0) for inv in invs)
                stored = int(shed.get(animal, 0) or 0)
                if stored > carried:
                    goal = min(_shed_tiles(size), key=lambda t: min(_distance(tuple(p), t) for p in pos))
                    tasks.append((119.0, goal, ["PICKUP", animal, 1], "pickup_animal"))
                    break

    actions = [["PASS"] for _ in pos]
    used = set()
    # Existing cargo is delivered before new work, except wheat reserved for a
    # visible feeding job. Carrying capacity is therefore reclaimed quickly.
    shed_goals = _shed_tiles(size)
    for idx, p in enumerate(pos):
        inventory = invs[idx]
        cargo = sum(int(v or 0) for v in inventory.values())
        carrying_animal = any(int(inventory.get(animal, 0) or 0) > 0 for animal in ANIMALS)
        if cargo and not carrying_animal:
            has_nonfeed = any(item != "WHEAT" or not hungry for item in inventory)
            if has_nonfeed:
                goal = min(shed_goals, key=lambda t: _distance(tuple(p), t))
                actions[idx] = ["DROP"] if tuple(p) == goal else _move(tuple(p), goal)
                used.add(("actor", idx))

    # If feed is due and wheat is in the shed, route one unoccupied actor to
    # fetch a batch; subsequent turns route that carrier to animals.
    if hungry > wheat_in_hands and int(shed.get("WHEAT", 0) or 0) > 0:
        free = [i for i in range(len(pos)) if ("actor", i) not in used
                and not any(int(invs[i].get(a, 0) or 0) > 0 for a in ANIMALS)]
        if free:
            i = min(free, key=lambda j: min(_distance(tuple(pos[j]), t) for t in shed_goals))
            goal = min(shed_goals, key=lambda t: _distance(tuple(pos[i]), t))
            actions[i] = ["PICKUP", "WHEAT", min(hungry - wheat_in_hands, int(shed.get("WHEAT", 0) or 0))] if tuple(pos[i]) == goal else _move(tuple(pos[i]), goal)
            used.add(("actor", i))

    plants_assigned = 0
    for priority, target, operation, label in sorted(tasks, key=lambda t: (-t[0], t[3], t[1])):
        if target in used:
            continue
        eligible = [i for i in range(len(pos)) if ("actor", i) not in used]
        if not eligible:
            break
        if label == "feed":
            eligible = [i for i in eligible if int(invs[i].get("WHEAT", 0) or 0) > 0]
            if not eligible:
                continue
        if label == "place_animal":
            animal = operation[1]
            eligible = [i for i in eligible if int(invs[i].get(animal, 0) or 0) > 0]
            if not eligible:
                continue
        if label == "pickup_animal":
            animal = operation[1]
            eligible = [i for i in eligible if not any(int(invs[i].get(a, 0) or 0) > 0 for a in ANIMALS)]
            if not eligible:
                continue
        if label == "plant" and plants_assigned >= int(seeds.get(crop, 0) or 0):
            continue
        i = min(eligible, key=lambda j: (_distance(tuple(pos[j]), target), j))
        actions[i] = operation if tuple(pos[i]) == target else _move(tuple(pos[i]), target)
        if label == "plant":
            plants_assigned += 1
        used.add(target)
        used.add(("actor", i))

    return {"farmer": actions[0], "hands": actions[1:], "market": market[:10]}


def _kaggle_submission_entrypoint(obs, configuration=None):
    return agent(obs, configuration)

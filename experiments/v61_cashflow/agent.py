"""Original, observation-conditioned Kaggriculture economy manager.

Only the current observation drives targets and routes. No replay, episode,
seed, or opponent-family lookup is used.
"""
from __future__ import annotations

from collections import Counter
from math import ceil

DIRS = ((0, -1, "NORTH"), (1, 0, "EAST"), (0, 1, "SOUTH"), (-1, 0, "WEST"))
SHED_GOOD = ((4, 4), (5, 4), (4, 5), (5, 5))
CROP = {
    "WHEAT": {"seed": 10, "yield": 4, "days": 4, "last": 26, "cap": 10},
    "CARROT": {"seed": 20, "yield": 3, "days": 3, "last": 27, "cap": 6},
    "TOMATO": {"seed": 50, "yield": 4, "days": 11, "last": 18, "cap": 5},
    "STRAWBERRY": {"seed": 100, "yield": 4, "days": 16, "last": 19, "cap": 7},
    "MELON": {"seed": 80, "yield": 6, "days": 10, "last": 20, "cap": 5},
}
ANIMALS = {"COW": {"structure": "PASTURE", "cost": 400, "item": "MILK", "rate": .5, "cap": 6},
           "SHEEP": {"structure": "PASTURE", "cost": 500, "item": "WOOL", "rate": 1/3, "cap": 5},
           "GOOSE": {"structure": "COOP", "cost": 300, "item": "EGG", "rate": 1., "cap": 6}}
BASE_PRICE = {"WHEAT": 25, "CARROT": 35, "TOMATO": 60, "STRAWBERRY": 120, "MELON": 250,
              "MILK": 160, "WOOL": 200, "EGG": 50, "FERTILIZER": 100}
SHOP_GOODS = {
    "BAKERY": ("EGG", "WHEAT"), "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"), "YARN_STORE": ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"), "PET_CAFE": ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}


def _tile(farm, p):
    x, y = p
    tiles = farm.get("tiles", [])
    return tiles[y][x] if 0 <= y < len(tiles) and 0 <= x < len(tiles[y]) else "LOCKED"


def _positions(farm):
    return [list(farm.get("farmer", [4, 4])), *[list(p) for p in farm.get("hands", [])]]


def _farm_counts(farm):
    counts = Counter()
    animals = Counter()
    structures = Counter()
    empty = []
    for y, row in enumerate(farm.get("tiles", [])):
        for x, tile in enumerate(row):
            if tile == "LOCKED":
                continue
            if tile is None:
                empty.append((x, y))
            elif isinstance(tile, dict):
                kind = tile.get("kind")
                if kind == "PLANT":
                    counts[tile.get("crop", "")] += 1
                if kind in ("PASTURE", "COOP"):
                    structures[kind] += 1
                    if tile.get("animal"):
                        animals[tile["animal"]] += 1
    return counts, animals, structures, empty


def _shop_demand(obs):
    shops = (obs.get("town") or {}).get("unlocked_shops") or []
    demand = Counter()
    for shop in shops:
        for item in SHOP_GOODS.get(shop, ()):
            # Each shop instance consumes six units per day (12 for single-good
            # shops, handled below); this is an observable pressure estimate.
            demand[item] += 12 if shop == "YARN_STORE" else 6
    for item in ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
                 "EGG", "MILK", "WOOL"):
        demand[item] += 1  # town center
    return demand


def _crop_scores(obs, counts, day):
    prices = (obs.get("market") or {}).get("prices") or {}
    demand = _shop_demand(obs)
    scores = {}
    for name, data in CROP.items():
        remaining = 29 - day
        if remaining < data["days"] or day > data["last"]:
            continue
        price = max(1, float(prices.get(name, BASE_PRICE[name])))
        # A repeated crop loses marginal value as supply grows; live prices and
        # shop use adapt this each invocation without relying on a future quote.
        demand_factor = 1.0 + min(.35, demand[name] / 30.0)
        gross = data["yield"] * price * demand_factor
        value = max(0.0, gross - data["seed"])
        scores[name] = value / (data["days"] + 1.5) / (1.0 + .24 * counts[name])
    return scores


def _plant_targets(obs, farm, counts, empty):
    day = int(obs.get("day", 0))
    goals = min(24, 6 + day)
    scores = _crop_scores(obs, counts, day)
    targets = Counter(counts)
    while sum(targets.values()) < goals and scores:
        choices = [(score, name) for name, score in scores.items()
                   if targets.get(name, 0) < CROP[name]["cap"]]
        if not choices:
            break
        _, crop = max(choices, key=lambda pair: (pair[0], pair[1]))
        targets[crop] += 1
        # Diminishing return makes a portfolio emerge rather than filling one
        # crop to its cap before considering every alternative.
        scores[crop] *= .73
    free_slots = max(0, len(empty) - 3)
    while sum(targets.values()) > sum(counts.values()) + free_slots:
        eligible = [crop for crop in targets if targets[crop] > counts[crop]]
        if not eligible:
            break
        crop = min(eligible, key=lambda c: scores.get(c, 0))
        targets[crop] -= 1
        if targets[crop] <= counts[crop]:
            del targets[crop]
    return targets


def _animal_targets(obs):
    day = int(obs.get("day", 0))
    prices = (obs.get("market") or {}).get("prices") or {}
    demand = _shop_demand(obs)
    shops = (obs.get("town") or {}).get("unlocked_shops") or []
    # Herd targets respond to current demand/price and season left; low-demand
    # herds stay small to protect feed reserves.
    target = {}
    for species, spec in ANIMALS.items():
        if day > 23:
            target[species] = 0
            continue
        item = spec["item"]
        price = float(prices.get(item, BASE_PRICE[item]))
        if species == "COW":
            visible = sum(s in shops for s in ("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"))
            desired = 1 + visible * 2
        elif species == "SHEEP":
            visible = shops.count("YARN_STORE")
            desired = 0 if visible == 0 else 2 + min(3, visible * 2)
        else:
            visible = sum(s in shops for s in ("BAKERY", "BRUNCH_SPOT"))
            desired = 0 if visible == 0 else 1 + visible * 2
        if price < BASE_PRICE[item] * .45:
            desired = max(0, desired // 2)
        remaining = 29 - day
        if remaining < 5:
            desired = 0
        target[species] = min(spec["cap"], desired)
    return target


def _dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _next_step(pos, target, size):
    x, y = pos
    tx, ty = target
    # Stable shortest-path tie break; locked land is traversable.
    for dx, dy, action in DIRS:
        nx, ny = x + dx, y + dy
        if 0 <= nx < size and 0 <= ny < size and _dist((nx, ny), target) < _dist(pos, target):
            return [action]
    return ["PASS"]


def _add_task(tasks, priority, target, action, requires=None, label=""):
    tasks.append({"priority": float(priority), "target": tuple(target), "action": action,
                  "requires": requires, "label": label})


def _tasks(obs, farm, priv, counts, animals, structures, empty, targets):
    day = int(obs.get("day", 0))
    positions = _positions(farm)
    inventories = priv.get("inventories") or [{} for _ in positions]
    shed = priv.get("shed") or {}
    seeds = priv.get("seeds") or {}
    tasks = []
    size = len(farm.get("tiles", []))
    tile_rows = farm.get("tiles", [])
    animal_goal = _animal_targets(obs)
    held_animals = Counter(shed)
    for inv in inventories:
        held_animals.update(inv)
    desired_structure = Counter()
    target_structures = Counter()
    for species, goal in animal_goal.items():
        target_structures[ANIMALS[species]["structure"]] += goal
    for structure, goal in target_structures.items():
        desired_structure[structure] = max(0, goal - structures[structure])

    # Daily service tasks are unique by tile and only actionable if current
    # inventory/preconditions permit the action.
    for y, row in enumerate(tile_rows):
        for x, tile in enumerate(row):
            if not isinstance(tile, dict):
                continue
            pos = (x, y)
            kind = tile.get("kind")
            if kind == "PLANT":
                crop = tile.get("crop", "")
                age = day - int(tile.get("planted_day", day))
                if not tile.get("watered_today", False):
                    urgency = 125 if int(tile.get("consecutive_unwatered", 0)) >= 1 else 88
                    _add_task(tasks, urgency, pos, ["WATER"], label="water")
                ripe_age = {"WHEAT": 4, "CARROT": 3, "MELON": 10}.get(crop, 0)
                should_harvest = tile.get("yield_units", 0) > 0 and (
                    age >= ripe_age if ripe_age else tile.get("yield_units", 0) >= 3
                )
                if should_harvest:
                    _add_task(tasks, 92 + min(12, tile.get("yield_units", 0) * 2), pos,
                              ["HARVEST"], label="harvest")
            if kind in ("PASTURE", "COOP") and tile.get("animal"):
                animal = tile["animal"]
                if not tile.get("fed_today", False):
                    _add_task(tasks, 145, pos, ["FEED"], requires="WHEAT", label="feed")
                elif not tile.get("cared_today", False):
                    _add_task(tasks, 105, pos, ["CARE"], label="care")
                if tile.get("yield_units", 0) > 0:
                    _add_task(tasks, 100 + min(12, tile["yield_units"] * 2), pos,
                              ["HARVEST"], label="animal_harvest")
                if tile.get("fertilizer_available"):
                    _add_task(tasks, 66, pos, ["COLLECT_FERTILIZER"], label="fertilizer")

    # Reserve distinct empty tiles for any missing target structures before
    # assigning crop work; simultaneous BUILD and PLANT on one tile conflicts.
    build_positions = []
    reserved = set()
    for structure, count in desired_structure.items():
        for pos in empty:
            if len([x for x in build_positions if x[1] == structure]) >= count:
                break
            if pos in reserved:
                continue
            build_positions.append((pos, structure))
            reserved.add(pos)
    for pos, structure in build_positions:
        _add_task(tasks, 73, pos, ["BUILD_" + structure], label="build")

    # Plant only as many same-crop actions as currently held seeds. Engine
    # validates same-turn PLANT requests atomically per crop.
    crop_need = Counter()
    for crop, target in targets.items():
        crop_need[crop] = max(0, target - counts[crop])
    crop_scores = _crop_scores(obs, counts, day)
    candidates = []
    for p in empty:
        if _tile(farm, p) is not None or p in reserved:
            continue
        for crop, need in crop_need.items():
            if need > 0 and seeds.get(crop, 0) > 0:
                candidates.append((crop_scores.get(crop, 0), crop, p))
    candidates.sort(reverse=True)
    for score, crop, pos in candidates:
        if crop_need[crop] <= 0 or seeds.get(crop, 0) <= 0:
            continue
        _add_task(tasks, 55 + min(15, score / 8), pos, ["PLANT", crop], label="plant")
        crop_need[crop] -= 1
        seeds[crop] -= 1

    # Deliver purchased livestock into an unoccupied compatible structure.
    held_livestock = Counter()
    for inv in inventories:
        held_livestock.update({species: int(inv.get(species, 0)) for species in ANIMALS})
    empty_structures = []
    for y, row in enumerate(tile_rows):
        for x, tile in enumerate(row):
            if isinstance(tile, dict) and tile.get("kind") in ("PASTURE", "COOP") and not tile.get("animal"):
                empty_structures.append(((x, y), tile["kind"]))
    claimed = set()
    for species, spec in ANIMALS.items():
        candidates = [(p, kind) for p, kind in empty_structures
                      if kind == spec["structure"] and p not in claimed]
        for _ in range(min(held_livestock[species], len(candidates))):
            p, _kind = candidates.pop(0)
            claimed.add(p)
            _add_task(tasks, 83, p, ["PLACE", species, 1],
                      requires=species, label="place_animal")

    # Fetch livestock from the shed when placement space is ready.
    shed_totals = Counter(shed)
    for inv in inventories:
        shed_totals.subtract(inv)
    vacant = Counter()
    for row in tile_rows:
        for tile in row:
            if isinstance(tile, dict) and tile.get("kind") in ("PASTURE", "COOP") and not tile.get("animal"):
                for species, spec in ANIMALS.items():
                    if spec["structure"] == tile["kind"]:
                        vacant[species] += 1
    access = [p for p in SHED_GOOD if p[0] < size and p[1] < size]
    pickup_tile = min(access, key=lambda p: min((_dist(p, pos) for pos in positions), default=0)) if access else (4, 4)
    for species in ANIMALS:
        pickups = min(max(0, int(shed_totals[species])), vacant[species])
        for _ in range(pickups):
            _add_task(tasks, 79, pickup_tile, ["PICKUP", species, 1], label="pickup_animal")

    # Carry feed to any hungry animal. If no worker carries wheat, pick up a
    # small batch from the shed; market replenishment happens at hour zero.
    hungry = 0
    for row in tile_rows:
        for tile in row:
            if isinstance(tile, dict) and tile.get("animal") and not tile.get("fed_today"):
                hungry += 1
    carried_wheat = sum(int(inv.get("WHEAT", 0)) for inv in inventories)
    to_pick = min(max(0, hungry - carried_wheat), int(shed.get("WHEAT", 0)))
    for _ in range(to_pick):
        _add_task(tasks, 120, pickup_tile, ["PICKUP", "WHEAT", 1], label="pickup_feed")

    return tasks


def _assign(obs, farm, inventories, tasks):
    positions = _positions(farm)
    size = len(farm.get("tiles", []))
    pairs = []
    for actor, pos in enumerate(positions):
        inv = inventories[actor] if actor < len(inventories) else {}
        for ti, task in enumerate(tasks):
            req = task["requires"]
            if req and int(inv.get(req, 0)) <= 0:
                continue
            if task["action"][0] == "PLANT" and int((obs.get("private", {}).get("seeds") or {}).get(task["action"][1], 0)) <= 0:
                continue
            distance = _dist(pos, task["target"])
            utility = task["priority"] - 1.6 * distance
            pairs.append((-utility, distance, actor, ti))
    pairs.sort()
    chosen_actor = set()
    chosen_task = set()
    actions = [["PASS"] for _ in positions]
    for _, _, actor, ti in pairs:
        if actor in chosen_actor or ti in chosen_task:
            continue
        chosen_actor.add(actor)
        chosen_task.add(ti)
        task = tasks[ti]
        if tuple(positions[actor]) == task["target"]:
            actions[actor] = task["action"]
        else:
            actions[actor] = _next_step(positions[actor], task["target"], size)
    return actions


def _fib_cost(count):
    a, b, total = 1, 1, 0
    for _ in range(count):
        total += a
        a, b = b, a + b
    return total


def _market_plan(obs, farm, priv, counts, animals, structures, targets):
    if int(obs.get("hour", -1)) != 0:
        return []
    day = int(obs.get("day", 0))
    money = float(farm.get("money", 0))
    hires_today = int(farm.get("hires_today", 0))
    prices = (obs.get("market") or {}).get("prices") or {}
    seeds = priv.get("seeds") or {}
    shed = priv.get("shed") or {}
    inventories = priv.get("inventories") or []
    tile_counts = Counter()
    for inv in inventories:
        tile_counts.update(inv)
    cash_from_stock = sum(float(prices.get(k, BASE_PRICE.get(k, 20))) * int(v)
                          for k, v in shed.items() if k not in ANIMALS)
    feed_cost = float(prices.get("WHEAT", 25))
    active_herd = sum(animals.values())
    feed_reserve = active_herd * 2 * feed_cost
    orders = []

    # Liquidate visible stock to keep the shed clear, retaining two days of
    # feed wheat in storage and excluding any held livestock.
    sell_orders = []
    for item, qty in sorted(shed.items()):
        if item in ANIMALS or int(qty) <= 0:
            continue
        retain = int(feed_reserve / max(1, feed_cost)) if item == "WHEAT" else 0
        sell_qty = max(0, int(qty) - retain)
        if sell_qty:
            unit = float(prices.get(item, BASE_PRICE.get(item, 20)))
            sell_orders.append((sell_qty * unit, ["SELL", item, sell_qty]))

    # Replenish feed to a two-day target plus one emergency day. This reserves
    # current cash before discretionary herd/land investment.
    feed_stock = int(shed.get("WHEAT", 0)) + sum(int(inv.get("WHEAT", 0)) for inv in inventories)
    feed_target = active_herd * 3
    feed_buy = max(0, feed_target - feed_stock)
    if feed_buy and money - feed_buy * feed_cost >= 300:
        orders.append(["BUY_PRODUCT", "WHEAT", min(feed_buy, 30)])
        money -= min(feed_buy, 30) * feed_cost

    # Buy seeds only for open planting tasks, capped by the remaining acreage.
    plantable = max(0, sum(targets.values()) - sum(counts.values()))
    seed_budget = max(0, money - max(450, active_herd * 3 * feed_cost))
    crop_scores = _crop_scores(obs, counts, day)
    seed_orders = 0
    for crop, _score in sorted(crop_scores.items(), key=lambda kv: -kv[1]):
        if seed_orders >= 4:
            break
        unit = CROP[crop]["seed"]
        # Seeds are crop-specific. Surplus stock for one crop cannot satisfy
        # another crop's target and must not suppress its purchase.
        crop_need = max(0, int(targets.get(crop, 0)) - int(counts.get(crop, 0))
                        - int(seeds.get(crop, 0)))
        qty = min(crop_need, 4, int(seed_budget // unit))
        # Avoid replenishing seeds for crops already at their target count.
        if qty <= 0 or counts[crop] >= CROP[crop]["cap"]:
            continue
        orders.append(["BUY_SEED", crop, qty])
        seed_budget -= qty * unit
        seed_orders += 1
        money -= qty * unit

    # Adaptive herd portfolio from live shop demand and prices.
    goals = _animal_targets(obs)
    held = Counter(shed)
    for inv in inventories:
        held.update(inv)
    empty_by_structure = Counter()
    for row in farm.get("tiles", []):
        for tile in row:
            if isinstance(tile, dict) and tile.get("kind") in ("PASTURE", "COOP") and not tile.get("animal"):
                for species, spec in ANIMALS.items():
                    if spec["structure"] == tile["kind"]:
                        empty_by_structure[species] += 1
    structural_need = Counter()
    for species, goal in goals.items():
        needed = max(0, min(goal - animals[species] - held[species],
                            empty_by_structure[species] + max(0, 1 - empty_by_structure[species])))
        if needed:
            price = ANIMALS[species]["cost"]
            if money - price >= max(650, active_herd * 3 * feed_cost):
                orders.append(["BUY_ANIMAL", species, min(needed, 2)])
                money -= price * min(needed, 2)
                structural_need[ANIMALS[species]["structure"]] += min(needed, 2)

    # Expand only when the target crop/structure workload is approaching the
    # current unlocked area, with liquid cash left for feed and inputs.
    unlocked = sum(1 for row in farm.get("tiles", []) for tile in row if tile != "LOCKED")
    occupied = sum(1 for row in farm.get("tiles", []) for tile in row if isinstance(tile, dict))
    free = unlocked - occupied
    if day <= 15 and free < 5 and money >= 2300 and len(farm.get("unlocked_quadrants", [])) < 4:
        orders.append(["BUY_LAND"])
        money -= 2000

    # Productive capacity ramps from current funded-work backlog. The schedule
    # aims near 9–10 total units by day 6–9, then hires only when crops/herd can
    # use the capacity. HIRE Fibonacci cost is budgeted before appending.
    projected_work = sum(counts.values()) + sum(animals.values()) * 2 + max(0, plantable)
    if day <= 13 and projected_work > 0:
        target_units = min(11, 5 + (day + 1) // 2)
        if projected_work < 12:
            target_units = min(target_units, max(2, 1 + ceil(projected_work / 2)))
        # Hired hands are temporary: they disappear at the day boundary.
        # Plan this day's staffing from the farmer baseline every morning.
        want = max(0, target_units - 1)
        hire_count = 0
        hire_cost = 0
        for n in range(hires_today, hires_today + want):
            cost = _fib_cost(n + 1) - _fib_cost(n)
            if money - hire_cost - cost < max(400, active_herd * 3 * feed_cost):
                break
            hire_cost += cost
            hire_count += 1
        orders.extend([["HIRE"] for _ in range(hire_count)])

    # Keep the feed reserve first, then fund the planned temporary workforce.
    # Fill remaining slots with investment orders and observed stock sales.
    feed_orders = [o for o in orders if o[0] == "BUY_PRODUCT" and o[1] == "WHEAT"]
    hire_orders = [o for o in orders if o[0] == "HIRE"]
    optional_orders = [o for o in orders if o not in feed_orders and o[0] != "HIRE"]
    budgeted = feed_orders[:1] + hire_orders[:9]
    budgeted += optional_orders[:max(0, 9 - len(budgeted))]
    slots = max(0, 10 - len(budgeted))
    selected_sales = [x[1] for x in sorted(sell_orders, reverse=True)[:slots]]
    return (selected_sales + budgeted)[:10]


def agent(obs, configuration=None):
    seat = int(obs.get("player", 0))
    farms = obs.get("farms") or []
    if seat >= len(farms):
        return {"farmer": ["PASS"], "hands": [], "market": []}
    farm = farms[seat]
    priv = obs.get("private") or {}
    counts, animals, structures, empty = _farm_counts(farm)
    targets = _plant_targets(obs, farm, counts, empty)
    tasks = _tasks(obs, farm, priv, counts, animals, structures, empty, targets)
    inventories = priv.get("inventories") or [{} for _ in _positions(farm)]
    actions = _assign(obs, farm, inventories, tasks)
    market = _market_plan(obs, farm, priv, counts, animals, structures, targets)
    return {"farmer": actions[0] if actions else ["PASS"],
            "hands": actions[1:], "market": market}

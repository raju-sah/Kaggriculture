"""Observation-grounded short-horizon cash/feed/seed allocator.

This module is intentionally a seam: a route planner proposes actor work and
optional market orders; allocate_market() protects daily feed and committed
planting work, then spends only remaining cash on discretionary buys.
"""
from collections import Counter

SEED_COST = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}


def _farm_and_seat(obs):
    seat = int(obs.get("player", 0) or 0)
    farms = obs.get("farms", [])
    return (farms[seat] if seat < len(farms) else {}), seat


def _units(action):
    return [action.get("farmer") or ["PASS"], *(action.get("hands") or [])]


def _live_animals(farm):
    return sum(1 for row in farm.get("tiles", []) for tile in row
               if isinstance(tile, dict) and tile.get("animal"))


def reserve_plan(obs, proposed_action):
    """Return a transparent one-day liability ledger from visible state/actions."""
    farm, seat = _farm_and_seat(obs)
    private = obs.get("private", {}) or {}
    inventory = private.get("inventories", [])
    carried = Counter()
    for row in inventory: carried.update(row or {})
    shed = Counter(private.get("shed", {}) or {})
    animals = _live_animals(farm)
    unassigned_feed = 0
    planting = Counter()
    for unit, order in enumerate(_units(proposed_action)):
        if not order: continue
        if order[0] == "PLANT" and len(order) > 1: planting[order[1]] += 1
        if order[0] == "FEED": unassigned_feed += 1
    seeds = Counter(private.get("seeds", {}) or {})
    seed_shortfall = {crop: max(0, count-seeds[crop]) for crop,count in planting.items()}
    wheat_price = float((obs.get("market", {}).get("prices", {}) or {}).get("WHEAT", 25))
    # One day of feed is a liquid reserve liability, reduced by all visible wheat
    # already held in hands or shed. Planned FEED actions do not reduce the herd's
    # next-day reserve requirement.
    feed_reserve_units = max(0, animals - carried['WHEAT'] - shed['WHEAT'])
    seed_reserve_cash = sum(n * SEED_COST.get(c, 999999) for c,n in seed_shortfall.items())
    feed_reserve_cash = feed_reserve_units * wheat_price
    return {
        "seat": seat, "day": int(obs.get("day", 0) or 0),
        "cash": float(farm.get("money", 0)), "animals": animals,
        "wheat_carried": carried['WHEAT'], "wheat_shed": shed['WHEAT'],
        "feed_reserve_units": feed_reserve_units,
        "feed_reserve_cash": feed_reserve_cash,
        "planting_commitments": dict(planting), "seed_shortfall": seed_shortfall,
        "seed_reserve_cash": seed_reserve_cash,
        "protected_cash": feed_reserve_cash + seed_reserve_cash,
        "discretionary_cash": max(0.0, float(farm.get("money", 0))-feed_reserve_cash-seed_reserve_cash),
    }


def allocate_market(obs, proposed_action, *, max_orders=10):
    """Reserve one-day feed and committed seeds before funding the route's buys.

    The planner retains control of route and order choice. This controller
    trims planned purchases only when they would consume the visible feed/seed
    liability reserve, and never counts hoped-for sale proceeds as cash.
    """
    import copy
    action = copy.deepcopy(proposed_action)
    ledger = reserve_plan(obs, action)
    farm, _ = _farm_and_seat(obs)
    private = obs.get("private", {}) or {}
    prices = obs.get("market", {}).get("prices", {}) or {}
    money = ledger["cash"]
    reserve = ledger["protected_cash"]
    need_seed = dict(ledger["seed_shortfall"])
    market = []
    hires = int(farm.get("hires_today", 0) or 0)
    extra_land = max(0, len(farm.get("unlocked_quadrants", []))-1)
    fib = [1,1,2,3,5,8,13,21,34,55,89,144,233]
    land_costs = [1000,2000,4000]
    animal_cost = {"GOOSE":300,"COW":400,"SHEEP":500}
    for order in action.get("market", []) or []:
        if not isinstance(order, list) or not order: continue
        op = order[0]
        item = order[1] if len(order)>1 else ""
        requested = int(order[2]) if len(order)>2 and isinstance(order[2], (int,float)) else 1
        if op == "SELL":
            market.append(order)
            continue
        if op == "HIRE":
            cost = fib[min(hires, len(fib)-1)]; hires += 1; qty = 1
        elif op == "BUY_LAND":
            cost = land_costs[extra_land] if extra_land < len(land_costs) else float("inf"); extra_land += 1; qty = 1
        elif op == "BUY_ANIMAL":
            cost = animal_cost.get(item, float("inf")); qty = max(0, requested)
        elif op == "BUY_PRODUCT":
            cost = float(prices.get(item, 25)); qty = max(0, requested)
        elif op == "BUY_SEED":
            cost = float(SEED_COST.get(item, 999999)); qty = max(0, requested)
        else:
            market.append(order); continue

        # A committed planting or explicit FEED action may spend its matching
        # reserve. All other purchases must leave those liabilities liquid.
        liability = 0.0
        if op == "BUY_PRODUCT" and item == "WHEAT":
            liability = min(qty, ledger["feed_reserve_units"]) * cost
            ledger["feed_reserve_units"] -= min(qty, ledger["feed_reserve_units"])
        elif op == "BUY_SEED" and item in need_seed:
            use = min(qty, need_seed[item]); need_seed[item] -= use
            liability = use * cost
        use_reserve = min(reserve, liability)
        affordable = max(0, int((money - max(0.0, reserve-use_reserve)) // max(1.0,cost)))
        take = min(qty, affordable)
        if take <= 0: continue
        spent = take*cost
        money -= spent
        reserve = max(0.0, reserve-min(use_reserve, spent))
        if op in ("BUY_PRODUCT", "BUY_SEED"):
            market.append([op,item,take])
        else:
            market.append(order)
    action["market"] = market[:max_orders]
    return action

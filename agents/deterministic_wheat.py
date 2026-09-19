"""Deterministic single-tile wheat loop used as the initial local baseline."""

WHEAT_SEED_COST = 10
WHEAT_HARVEST_DAY = 2


def agent(observation):
    player = observation["player"]
    farm = observation["farms"][player]
    private = observation["private"]
    farmer_inventory = private.get("inventories", [{}])[0]
    x, y = farm["farmer"]
    tile = farm["tiles"][y][x]

    market = []
    stored_wheat = private.get("shed", {}).get("WHEAT", 0)
    if stored_wheat:
        market.append(["SELL", "WHEAT", stored_wheat])

    seeds = private.get("seeds", {}).get("WHEAT", 0)
    if tile is None and seeds == 0 and farm["money"] >= WHEAT_SEED_COST:
        market.append(["BUY_SEED", "WHEAT", 1])

    if farmer_inventory:
        farmer_action = ["DROP"]
    elif tile is None and seeds:
        farmer_action = ["PLANT", "WHEAT"]
    elif isinstance(tile, dict) and tile.get("kind") == "PLANT":
        age = observation["day"] - tile["planted_day"]
        if age >= WHEAT_HARVEST_DAY:
            farmer_action = ["HARVEST"]
        elif not tile.get("watered_today", False):
            farmer_action = ["WATER"]
        else:
            farmer_action = ["PASS"]
    else:
        farmer_action = ["PASS"]

    return {"farmer": farmer_action, "hands": [], "market": market}

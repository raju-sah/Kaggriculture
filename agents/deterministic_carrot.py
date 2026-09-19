"""Deterministic single-tile carrot loop used as a second smoke opponent."""

CARROT_SEED_COST = 20
CARROT_HARVEST_DAY = 3


def agent(observation):
    player = observation["player"]
    farm = observation["farms"][player]
    private = observation["private"]
    farmer_inventory = private.get("inventories", [{}])[0]
    x, y = farm["farmer"]
    tile = farm["tiles"][y][x]

    market = []
    stored = private.get("shed", {}).get("CARROT", 0)
    if stored:
        market.append(["SELL", "CARROT", stored])

    seeds = private.get("seeds", {}).get("CARROT", 0)
    if tile is None and seeds == 0 and farm["money"] >= CARROT_SEED_COST:
        market.append(["BUY_SEED", "CARROT", 1])

    if farmer_inventory:
        farmer_action = ["DROP"]
    elif tile is None and seeds:
        farmer_action = ["PLANT", "CARROT"]
    elif isinstance(tile, dict) and tile.get("kind") == "PLANT":
        age = observation["day"] - tile["planted_day"]
        if age >= CARROT_HARVEST_DAY:
            farmer_action = ["HARVEST"]
        elif not tile.get("watered_today", False):
            farmer_action = ["WATER"]
        else:
            farmer_action = ["PASS"]
    else:
        farmer_action = ["PASS"]

    return {"farmer": farmer_action, "hands": [], "market": market}


import json
import os
from collections import Counter

file_path = "episode-113165315-replay.json"
with open(file_path) as f:
    data = json.load(f)

info = data.get("info", {})
names = info.get("TeamNames", ["Player 0", "Player 1"])
rewards = data.get("rewards", [0, 0])
print("Names:", names)
print("Rewards:", rewards)

def get_stats(seat):
    steps = data["steps"]
    buys = Counter()
    sales = Counter()
    town_shops_seen = set()

    for step in steps:
        obs0 = step[0].get("observation", {})
        town = obs0.get("town", {})
        if isinstance(town, dict):
            shops = town.get("unlocked_shops", []) or []
            for s in shops:
                town_shops_seen.add(s)

        action = step[seat].get("action", {}) or {}
        mkt = action.get("market", []) or []
        for order in mkt:
            if not order: continue
            cmd = order[0]
            item = order[1] if len(order) > 1 else ""
            qty = order[2] if len(order) > 2 and isinstance(order[2], (int, float)) else 1
            if cmd == "BUY_ANIMAL":
                buys[item] += qty
            elif cmd in ("SELL", "SELL_TOWN"):
                sales[item] += qty
    return buys, sales, town_shops_seen

b0, s0, ts0 = get_stats(0)
b1, s1, ts1 = get_stats(1)

print(f"{names[0]} (Seat 0):")
print(f"  Buys: {dict(b0)}")
print(f"  Sales: {dict(s0)}")
print(f"{names[1]} (Seat 1):")
print(f"  Buys: {dict(b1)}")
print(f"  Sales: {dict(s1)}")
print(f"Town Shops seen: {ts0}")

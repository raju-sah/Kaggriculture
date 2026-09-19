import json
from collections import Counter, defaultdict
from pathlib import Path

def analyze_episode(filepath):
    with open(filepath) as f:
        data = json.load(f)

    info = data.get("info", {})
    teams = info.get("TeamNames", ["Player 0", "Player 1"])
    rewards = data.get("rewards", [0, 0])
    seed = info.get("seed")

    steps = data["steps"]
    num_steps = len(steps)

    def player_analysis(seat):
        buys = Counter()
        sales_qty = Counter()
        order_types = Counter()
        snapshots = {}

        for step_idx, step in enumerate(steps):
            obs = step[0].get("observation", {})
            farms = obs.get("farms", [])
            farm = farms[seat] if len(farms) > seat else {}
            action = step[seat].get("action", {}) or {}

            cash = farm.get("money", 0)
            day = obs.get("day", step_idx // 24)
            hour = obs.get("hour", step_idx % 24)

            if hour == 23 and day in (5, 9, 14, 19, 24, 29):
                livestock = Counter()
                crops = Counter()
                tiles = farm.get("tiles", [])
                for row in tiles:
                    if not isinstance(row, list): continue
                    for cell in row:
                        if isinstance(cell, dict):
                            kind = cell.get("kind")
                            if kind == "PASTURE":
                                livestock[cell.get("animal", "UNKNOWN")] += 1
                            elif kind == "COOP":
                                livestock["COOP_" + str(cell.get("animal", "GOOSE"))] += 1
                            elif kind == "PLANT":
                                crops[cell.get("crop", "UNKNOWN")] += 1

                hands = len(farm.get("hands", []))
                quads = farm.get("unlocked_quadrants", [])
                snapshots[day] = {
                    "cash": cash,
                    "hands": hands,
                    "quadrants": len(quads),
                    "livestock": dict(livestock),
                    "crops": dict(crops),
                }

            mkt = action.get("market", []) or []
            for order in mkt:
                if not order: continue
                cmd = order[0]
                order_types[cmd] += 1
                item = order[1] if len(order) > 1 else ""
                qty = order[2] if len(order) > 2 and isinstance(order[2], (int, float)) else 1
                if cmd == "BUY_ANIMAL":
                    buys[f"ANIMAL_{item}"] += qty
                elif cmd == "BUY":
                    buys[item] += qty
                elif cmd in ("SELL", "SELL_TOWN"):
                    sales_qty[item] += qty

        final_farm = steps[-1][0].get("observation", {}).get("farms", [])[seat]
        final_livestock = Counter()
        final_crops = Counter()
        for row in final_farm.get("tiles", []):
            if isinstance(row, list):
                for cell in row:
                    if isinstance(cell, dict):
                        if cell.get("kind") in ("PASTURE", "COOP"):
                            final_livestock[cell.get("animal")] += 1
                        elif cell.get("kind") == "PLANT":
                            final_crops[cell.get("crop")] += 1

        return {
            "team": teams[seat],
            "reward": rewards[seat],
            "buys": dict(buys),
            "requested_sales": dict(sales_qty),
            "final_hands": len(final_farm.get("hands", [])),
            "final_quadrants": len(final_farm.get("unlocked_quadrants", [])),
            "final_livestock": dict(final_livestock),
            "final_crops": dict(final_crops),
            "snapshots": snapshots
        }

    p0 = player_analysis(0)
    p1 = player_analysis(1)

    town_shops = []
    for step in steps:
        t = step[0].get("observation", {}).get("town", {})
        if isinstance(t, dict):
            shops = t.get("unlocked_shops", [])
            if shops and len(shops) > len(town_shops):
                town_shops = list(shops)

    return {
        "teams": teams,
        "rewards": rewards,
        "seed": seed,
        "town_shops": town_shops,
        "p0": p0,
        "p1": p1
    }

if __name__ == "__main__":
    import sys
    files = sys.argv[1:]
    for f in files:
        res = analyze_episode(f)
        winner = res["teams"][0] if res["rewards"][0] > res["rewards"][1] else res["teams"][1]
        margin = abs(res["rewards"][0] - res["rewards"][1])
        print(f"=== {Path(f).name} ===")
        print(f"Winner: {winner} (Margin: +{margin:,.0f}) | Seed: {res['seed']}")
        print(f"Town shops: {res['town_shops']}")
        for p in [res["p0"], res["p1"]]:
            print(f"\n--- {p['team']} (Reward: {p['reward']:,.0f}) ---")
            print(f"  Final Hands: {p['final_hands']} | Final Quadrants: {p['final_quadrants']}")
            print(f"  Final Livestock: {p['final_livestock']}")
            print(f"  Final Crops: {p['final_crops']}")
            print(f"  Key Animal Buys: {[k for k, v in p['buys'].items() if 'ANIMAL' in k]}")
            print(f"  Requested Sales: {p['requested_sales']}")
            print("  Snapshots:")
            for day, snap in sorted(p["snapshots"].items()):
                print(f"    Day {day:2d}: Cash ${snap['cash']:,.0f} | Hands: {snap['hands']} | Quads: {snap['quadrants']} | Animals: {snap['livestock']} | Crops: {snap['crops']}")
        print("\n" + "="*60 + "\n")

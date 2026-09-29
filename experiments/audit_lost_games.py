import json
import os
from collections import Counter

LOST_EPISODES = ["114764045", "114765602", "114770056", "114773097"]
FOLDER = "experiments/v110_kaggle_episodes"

def audit_game(ep_id):
    fpath = os.path.join(FOLDER, f"episode-{ep_id}-replay.json")
    with open(fpath, "r") as f:
        data = json.load(f)

    info = data.get("info", {})
    names = info.get("TeamNames", ["Agent0", "Agent1"])
    rewards = data.get("rewards", [0, 0])
    steps = data.get("steps", [])

    our_seat = 1 if "Rajusah" in names[1] else 0
    opp_seat = 1 - our_seat

    print("=" * 80)
    print(f"AUDIT EPISODE {ep_id}: Rajusah (Seat {our_seat}) vs {names[opp_seat]} (Seat {opp_seat})")
    print(f"Scores: Rajusah = {rewards[our_seat]}, {names[opp_seat]} = {rewards[opp_seat]} (Diff: {rewards[our_seat] - rewards[opp_seat]})")

    # Environment configuration & seed
    config = data.get("configuration", {})
    seed = config.get("seed", "unknown")
    print(f"Seed: {seed}")

    # Track town shops unlocking
    unlocked_shops_timeline = {}
    for s_idx, step in enumerate(steps):
        obs = step[0].get("observation", {})
        step_num = obs.get("step", s_idx)
        day = (step_num // 24) + 1
        town = obs.get("town", {})
        if isinstance(town, dict):
            shops = town.get("unlocked_shops", []) or []
            if day not in unlocked_shops_timeline:
                unlocked_shops_timeline[day] = list(shops)

    print("\nTown Shop Unlocks:")
    prev_shops = []
    for day in sorted(unlocked_shops_timeline.keys()):
        current = unlocked_shops_timeline[day]
        new_shops = [s for s in current if s not in prev_shops]
        if new_shops:
            print(f"  Day {day:2d} (step {(day-1)*24:3d}): New shops -> {new_shops}")
            prev_shops = list(current)

    # Analyze both players' actions & economy
    def analyze_player(seat, label):
        buys = Counter()
        sales_general = Counter()
        sales_town = Counter()
        animals_owned = Counter() # track alive / bought
        crops_planted = Counter()
        money_spent_animals = 0
        revenue_town = 0
        revenue_general = 0
        coins_timeline = {}

        for s_idx, step in enumerate(steps):
            obs = step[seat].get("observation", {})
            step_num = obs.get("step", s_idx)
            day = (step_num // 24) + 1
            coins = obs.get("coins", 0)
            if step_num % 24 == 0 or s_idx == len(steps) - 1:
                coins_timeline[day] = coins

            action = step[seat].get("action", {}) or {}
            mkt = action.get("market", []) or []
            for order in mkt:
                if not order: continue
                cmd = order[0]
                item = order[1] if len(order) > 1 else ""
                qty = order[2] if len(order) > 2 and isinstance(order[2], (int, float)) else 1
                if cmd == "BUY_ANIMAL":
                    buys[item] += qty
                elif cmd == "SELL":
                    sales_general[item] += qty
                elif cmd == "SELL_TOWN":
                    sales_town[item] += qty

        final_obs = steps[-1][seat].get("observation", {})
        final_inv = final_obs.get("inventory", {})
        final_animals = final_obs.get("animals", {})
        animal_counts = Counter()
        if isinstance(final_animals, list):
            for a in final_animals:
                animal_counts[a.get("type", "unknown")] += 1
        elif isinstance(final_animals, dict):
            for a_id, a_data in final_animals.items():
                animal_counts[a_data.get("type", "unknown")] += 1

        print(f"\n--- {label} ---")
        print(f"  Animals Bought: {dict(buys)}")
        print(f"  Final Animals Alive: {dict(animal_counts)}")
        print(f"  Sales General: {dict(sales_general)}")
        print(f"  Sales Town: {dict(sales_town)}")
        print(f"  Final Leftover Inventory: {final_inv}")
        print(f"  Coins Progression (selected days):")
        days_to_show = [1, 5, 10, 15, 20, 25, 27]
        prog = {d: coins_timeline.get(d, "N/A") for d in days_to_show if d in coins_timeline}
        print(f"    {prog}")

    analyze_player(our_seat, f"OUR AGENT (Rajusah, Seat {our_seat})")
    analyze_player(opp_seat, f"OPPONENT ({names[opp_seat]}, Seat {opp_seat})")

if __name__ == "__main__":
    for ep in LOST_EPISODES:
        audit_game(ep)

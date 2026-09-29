import json
import glob
import os
from collections import Counter

def analyze_replays(folder="experiments/v110_kaggle_episodes"):
    replay_files = sorted(glob.glob(os.path.join(folder, "episode-*-replay.json")))
    if not replay_files:
        print("No replay files found.")
        return

    print(f"Found {len(replay_files)} replays.\n" + "="*80)

    summary = []
    lost_games = []

    for fpath in replay_files:
        ep_id = os.path.basename(fpath).split("-")[1]
        try:
            with open(fpath, "r") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error loading {fpath}: {e}")
            continue

        info = data.get("info", {})
        names = info.get("TeamNames", ["Agent0", "Agent1"])
        rewards = data.get("rewards", [0, 0])
        steps = data.get("steps", [])
        if not steps:
            continue

        # Determine which seat is our agent vs opponent
        # Check team names or inspect agent logic
        # Usually names[0] or names[1]
        # Let's inspect final reward
        r0 = rewards[0] if rewards and len(rewards) > 0 else 0
        r1 = rewards[1] if rewards and len(rewards) > 1 else 0

        # Extract town shops progression
        town_shops_by_day = {}
        for s_idx, step in enumerate(steps):
            obs0 = step[0].get("observation", {})
            step_num = obs0.get("step", s_idx)
            day = (step_num // 24) + 1
            town = obs0.get("town", {})
            if isinstance(town, dict):
                shops = town.get("unlocked_shops", []) or []
                if day not in town_shops_by_day:
                    town_shops_by_day[day] = list(shops)

        # Helper to get seat stats
        def get_seat_data(seat):
            buys = Counter()
            sales = Counter()
            final_coins = 0
            final_inv = {}
            for s_idx, step in enumerate(steps):
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
                obs = step[seat].get("observation", {})
                if obs:
                    final_coins = obs.get("coins", final_coins)
                    final_inv = obs.get("inventory", final_inv)
            return buys, sales, final_coins, final_inv

        b0, s0, c0, inv0 = get_seat_data(0)
        b1, s1, c1, inv1 = get_seat_data(1)

        # Check who won
        win0 = r0 > r1
        win1 = r1 > r0
        draw = r0 == r1

        summary.append({
            "ep_id": ep_id,
            "names": names,
            "rewards": (r0, r1),
            "coins": (c0, c1),
            "b0": b0,
            "b1": b1,
            "s0": s0,
            "s1": s1,
            "shops": town_shops_by_day.get(27, town_shops_by_day.get(len(town_shops_by_day), [])),
            "all_shops": town_shops_by_day
        })

    print(f"{'Ep ID':<12} | {'Seat 0 Team':<20} | {'R0 / C0':<15} | {'Seat 1 Team':<20} | {'R1 / C1':<15} | {'Outcome'}")
    print("-" * 95)
    for s in summary:
        n0 = s['names'][0][:18]
        n1 = s['names'][1][:18]
        r0, r1 = s['rewards']
        c0, c1 = s['coins']
        outcome = "Draw"
        if r0 > r1: outcome = f"Seat 0 Won (+{r0-r1:.1f})"
        elif r1 > r0: outcome = f"Seat 1 Won (+{r1-r0:.1f})"
        print(f"{s['ep_id']:<12} | {n0:<20} | {r0:.0f} ({c0}){'':<6} | {n1:<20} | {r1:.0f} ({c1}){'':<6} | {outcome}")

if __name__ == "__main__":
    analyze_replays()

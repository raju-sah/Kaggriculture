"""Deep Analyzer for v52 Kaggle Ladder Matches."""

import glob
import json
from collections import Counter
from pathlib import Path


def analyze_replay(file_path):
    data = json.loads(Path(file_path).read_text())
    info = data.get("info", {})
    ep_id = info.get("EpisodeId")
    seed = info.get("seed")
    names = info.get("TeamNames", ["Player 0", "Player 1"])
    rewards = data.get("rewards", [0, 0])

    # Find Rajusah's seat
    if "Rajusah" in names[0]:
        our_seat = 0
        opp_seat = 1
    elif "Rajusah" in names[1]:
        our_seat = 1
        opp_seat = 0
    else:
        # Default assume seat 0 or 1
        our_seat = 0
        opp_seat = 1

    our_name = names[our_seat]
    opp_name = names[opp_seat]
    our_score = rewards[our_seat]
    opp_score = rewards[opp_seat]
    won = our_score > opp_score
    diff = our_score - opp_score

    # Analyze actions and town shops
    steps = data["steps"]
    our_buys = Counter()
    opp_buys = Counter()
    our_sales = Counter()
    opp_sales = Counter()
    our_town_sales = Counter()
    opp_town_sales = Counter()

    town_shops_seen = set()

    for step in steps:
        # Check town shops in obs
        obs0 = step[0].get("observation", {})
        town = obs0.get("town", {})
        if isinstance(town, dict):
            shops = town.get("unlocked_shops", []) or []
            for s in shops:
                town_shops_seen.add(s)

        for seat, (bc, sc, tc) in [
            (our_seat, (our_buys, our_sales, our_town_sales)),
            (opp_seat, (opp_buys, opp_sales, opp_town_sales)),
        ]:
            action = step[seat].get("action", {}) or {}
            mkt = action.get("market", []) or []
            for order in mkt:
                if not order:
                    continue
                cmd = order[0]
                item = order[1] if len(order) > 1 else ""
                qty = order[2] if len(order) > 2 and isinstance(order[2], (int, float)) else 1
                if cmd == "BUY_ANIMAL":
                    bc[item] += qty
                elif cmd == "SELL":
                    sc[item] += qty
                elif cmd == "SELL_TOWN":
                    tc[item] += qty

    return {
        "ep_id": ep_id,
        "seed": seed,
        "our_name": our_name,
        "opp_name": opp_name,
        "our_seat": our_seat,
        "our_score": our_score,
        "opp_score": opp_score,
        "won": won,
        "diff": diff,
        "our_buys": dict(our_buys),
        "opp_buys": dict(opp_buys),
        "our_sales": our_sales.most_common(5),
        "opp_sales": opp_sales.most_common(5),
        "our_town_sales": our_town_sales.most_common(5),
        "opp_town_sales": opp_town_sales.most_common(5),
        "town_shops": sorted(list(town_shops_seen)),
    }


def main():
    replay_files = sorted(glob.glob("experiments/v52_replays/*.json"))
    if not replay_files:
        print("No replays found in experiments/v52_replays/")
        return

    print(f"Analyzing {len(replay_files)} downloaded replays for v52...\n")

    wins = 0
    losses = 0
    ties = 0

    results = []
    for f in replay_files:
        res = analyze_replay(f)
        results.append(res)
        if res["won"]:
            wins += 1
        elif res["our_score"] < res["opp_score"]:
            losses += 1
        else:
            ties += 1

    print("=" * 80)
    print(f"LADDER SUMMARY: Total: {len(results)} | Wins: {wins} | Losses: {losses} | Ties: {ties} | WinRate: {wins/len(results)*100:.1f}%")
    print("=" * 80)

    print("\n--- MATCH BREAKDOWN ---")
    for r in results:
        status = "WIN " if r["won"] else "LOSS"
        print(f"[{status}] Ep {r['ep_id']} (Seed {r['seed']}) Seat {r['our_seat']} vs {r['opp_name']}")
        print(f"       Score: Rajusah {r['our_score']:,.0f} vs Opp {r['opp_score']:,.0f} (Margin: {r['diff']:+,.0f})")
        print(f"       Rajusah Buys: {r['our_buys']} | Opp Buys: {r['opp_buys']}")
        print(f"       Town Shops: {r['town_shops']}")
        if not r["won"]:
            print(f"       >>> LOSS ANALYSIS: Opponent top sales: {r['opp_sales']}")
            print(f"       >>> LOSS ANALYSIS: Opponent town sales: {r['opp_town_sales']}")
            print(f"       >>> LOSS ANALYSIS: Rajusah top sales: {r['our_sales']}")
        print("-" * 80)


if __name__ == "__main__":
    main()

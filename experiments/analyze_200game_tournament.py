import json
import glob
import os
from collections import defaultdict

def analyze_tournament(run_dir="experiments/runs/v115_20game_tournament"):
    game_files = glob.glob(os.path.join(run_dir, "games", "*.json"))
    print(f"Total completed games found: {len(game_files)}")

    opp_stats = defaultdict(lambda: {"wins": 0, "losses": 0, "draws": 0, "margins": []})

    for fpath in game_files:
        try:
            with open(fpath, "r") as f:
                data = json.load(f)
        except Exception:
            continue

        opp = data.get("opponent", "unknown")
        # Candidate seat: 0 if ab, 1 if ba
        game_id = data.get("game_id", "")
        swapped = "-ba-" in game_id
        cand_seat = 1 if swapped else 0
        opp_seat = 0 if swapped else 1

        coins = data.get("final_coins", [0, 0])
        cand_coins = coins[cand_seat]
        opp_coins = coins[opp_seat]
        margin = cand_coins - opp_coins

        res = data.get("candidate_result")
        opp_stats[opp]["margins"].append(margin)
        if res == "win":
            opp_stats[opp]["wins"] += 1
        elif res == "loss":
            opp_stats[opp]["losses"] += 1
        else:
            opp_stats[opp]["draws"] += 1

    print("\n" + "="*85)
    print(f"{'Opponent':<12} | {'Games':<6} | {'Wins':<6} | {'Draws':<6} | {'Losses':<6} | {'Win Rate':<10} | {'Mean Margin'}")
    print("="*85)

    total_games = 0
    total_wins = 0
    total_draws = 0
    total_losses = 0

    for opp in sorted(opp_stats.keys()):
        stats = opp_stats[opp]
        g = stats["wins"] + stats["draws"] + stats["losses"]
        w = stats["wins"]
        d = stats["draws"]
        l = stats["losses"]
        wr = (w + 0.5 * d) / g * 100 if g > 0 else 0
        mean_margin = sum(stats["margins"]) / len(stats["margins"]) if stats["margins"] else 0

        total_games += g
        total_wins += w
        total_draws += d
        total_losses += l

        print(f"{opp:<12} | {g:<6} | {w:<6} | {d:<6} | {l:<6} | {wr:>6.1f}%    | {mean_margin:>+8.1f}")

    total_wr = (total_wins + 0.5 * total_draws) / total_games * 100 if total_games > 0 else 0
    print("-" * 85)
    print(f"{'TOTAL':<12} | {total_games:<6} | {total_wins:<6} | {total_draws:<6} | {total_losses:<6} | {total_wr:>6.1f}%    |")
    print("="*85)

if __name__ == "__main__":
    analyze_tournament()

"""Complete verification tournament for candidate v55 vs all prior agents."""

from kaggle_environments import make

opponents = [
    ("v54 (Lizs 6C/4S/7G)", "agents/v54_agent.py"),
    ("v53 (Kazuhiro 11S)", "agents/v53_agent.py"),
    ("v52 (Nam 9C/5S/3G)", "experiments/v52_agent.py"),
    ("v51 (Nam Clearance)", "experiments/v51_agent.py"),
    ("v50 (Nam Base)", "experiments/v50_agent.py"),
    ("v48 (Boey 10C/2S)", "experiments/v48_agent.py"),
]

seeds = [1001, 1017, 2001, 2002]

print("=" * 80, flush=True)
print("TOURNAMENT: v55 Dynamic Adaptive Champion vs ALL Previous Versions", flush=True)
print(f"Seeds: {seeds} across both seats (Seat 0 and Seat 1, 8 matches per opponent)", flush=True)
print("=" * 80, flush=True)

total_wins, total_losses, total_ties = 0, 0, 0

for opp_name, opp_path in opponents:
    wins, losses, ties = 0, 0, 0
    scores_55, scores_opp = [], []
    for s in seeds:
        for seat in [0, 1]:
            agents = ["agents/v55_agent.py", opp_path] if seat == 0 else [opp_path, "agents/v55_agent.py"]
            env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s})
            env.run(agents)
            r55 = env.state[0]["reward"] if seat == 0 else env.state[1]["reward"]
            ropp = env.state[1]["reward"] if seat == 0 else env.state[0]["reward"]
            scores_55.append(r55)
            scores_opp.append(ropp)
            if r55 > ropp:
                wins += 1
            elif r55 < ropp:
                losses += 1
            else:
                ties += 1
    total_wins += wins
    total_losses += losses
    total_ties += ties
    avg55 = sum(scores_55) / len(scores_55)
    avgopp = sum(scores_opp) / len(scores_opp)
    net = avg55 - avgopp
    print(f"v55 vs {opp_name:<22}: {wins}W - {losses}L - {ties}T | Avg $: {avg55:,.0f} vs {avgopp:,.0f} (Net: {net:+,.0f})", flush=True)

print("=" * 80, flush=True)
print(f"OVERALL TOURNAMENT RECORD: {total_wins}W - {total_losses}L - {total_ties}T ({total_wins/(total_wins+total_losses)*100:.1f}% Win Rate)", flush=True)
print("=" * 80, flush=True)

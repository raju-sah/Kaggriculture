"""Fast multi-core parallel tournament for candidate v55 (Nam + Kazuhiro) vs all prior agents."""

import concurrent.futures
import time
from kaggle_environments import make

CANDIDATE = "experiments/v55_nam_kazuhiro.py"

OPPONENTS = [
    ("v54 (Lizs 6C/4S/7G)", "agents/v54_agent.py"),
    ("v53 (Kazuhiro 11S)", "agents/v53_agent.py"),
    ("v52 (Nam 9C/5S/3G)", "experiments/v52_agent.py"),
    ("v51 (Nam Clearance)", "experiments/v51_agent.py"),
    ("v50 (Nam Base)", "experiments/v50_agent.py"),
    ("v48 (Boey 10C/2S)", "experiments/v48_agent.py"),
]

SEEDS = [1001, 1017, 2001, 2002]


def run_single_match(args):
    candidate_path, opp_path, seed, seat = args
    agents = [candidate_path, opp_path] if seat == 0 else [opp_path, candidate_path]
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
    env.run(agents)
    rcand = env.state[0]["reward"] if seat == 0 else env.state[1]["reward"]
    ropp = env.state[1]["reward"] if seat == 0 else env.state[0]["reward"]
    return seed, seat, rcand, ropp


def run_tournament():
    print("=" * 80, flush=True)
    print("FAST MULTI-CORE TOURNAMENT: Candidate v55 (Nam 9C/5S/3G + Kazuhiro 11S)", flush=True)
    print(f"Seeds: {SEEDS} across both seats (Seat 0 & 1, 8 matches per opponent in parallel)", flush=True)
    print("=" * 80, flush=True)

    total_wins, total_losses, total_ties = 0, 0, 0
    t0 = time.time()

    for opp_name, opp_path in OPPONENTS:
        tasks = []
        for s in SEEDS:
            for seat in [0, 1]:
                tasks.append((CANDIDATE, opp_path, s, seat))

        wins, losses, ties = 0, 0, 0
        scores_cand, scores_opp = [], []

        with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(run_single_match, tasks))

        for s, seat, rcand, ropp in results:
            scores_cand.append(rcand)
            scores_opp.append(ropp)
            if rcand > ropp:
                wins += 1
            elif rcand < ropp:
                losses += 1
            else:
                ties += 1

        total_wins += wins
        total_losses += losses
        total_ties += ties
        avg_cand = sum(scores_cand) / len(scores_cand)
        avg_opp = sum(scores_opp) / len(scores_opp)
        net = avg_cand - avg_opp
        pct = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
        print(f"v55 vs {opp_name:<22}: {wins}W - {losses}L - {ties}T ({pct:4.1f}%) | Avg $: {avg_cand:,.0f} vs {avg_opp:,.0f} (Net: {net:+,.0f})", flush=True)

    elapsed = time.time() - t0
    print("=" * 80, flush=True)
    total_matches = total_wins + total_losses + total_ties
    win_rate = (total_wins / (total_wins + total_losses) * 100) if (total_wins + total_losses) > 0 else 0
    print(f"OVERALL TOURNAMENT RECORD: {total_wins}W - {total_losses}L - {total_ties}T ({win_rate:.1f}% Win Rate) in {elapsed:.1f}s", flush=True)
    print("=" * 80, flush=True)


if __name__ == "__main__":
    run_tournament()

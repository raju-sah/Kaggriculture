"""Tournament Validation Suite for Candidate v53 vs Prior Versions & Reference League."""

from __future__ import annotations

import copy
from experiments.v50_agent import agent as v50_agent
from experiments.v52_agent import agent as v52_agent
from experiments.kazuhiro_agent import ACTIONS as K_ACTIONS
from kaggle_environments import make
from scripts.v19_terminal import apply_overlay, terminal_market
from scripts.v22_market_impact import reorder_market
from v23.planner import build_sparse_planner, PlannerConfig

# Build Candidate v53
_PLANNER = build_sparse_planner(K_ACTIONS, PlannerConfig())
CLEARANCE_STEP = 630


def v53_agent(obs, configuration=None):
    try:
        # 1. Full Seat 1 Normalization: Kaggle container drops 'step' for Player 1
        if obs.get("step") is None:
            obs = dict(obs)
            day = int(obs.get("day", 0) or 0)
            hour = int(obs.get("hour", 0) or 0)
            obs["step"] = day * 24 + hour

        step = obs["step"]

        # 2. Base planner with closed-loop weed repair
        action = _PLANNER(obs, configuration)

        # 3. Market impact slot ordering (safe sorting of sell slots without order dropping)
        action = reorder_market(obs, action, mode="impact_slots")

        # 4. Step 630 Early Continuous Shed Clearance (captures peak prices 50 hours earlier)
        if step >= CLEARANCE_STEP:
            action = terminal_market(obs, action, "collision", replace=False)

        # 5. Late-collision terminal overlay (monetization & terminal 718 full replacement)
        return apply_overlay(obs, action, "late_collision")
    except Exception:
        seat = 1 if int(obs.get("player", 0) or 0) == 1 else 0
        farms = list(obs.get("farms", []) or [])
        farm = farms[seat] if seat < len(farms) else {}
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (farm.get("hands", []) or [])],
            "market": [],
        }


def run_tournament(agent_a, agent_b, name_a, name_b, seeds):
    print(f"\n{'='*75}")
    print(f"TOURNAMENT: {name_a} vs {name_b} ({len(seeds)*2} Matches across {len(seeds)} Seeds, Both Seats)")
    print(f"{'='*75}")
    wins = 0
    losses = 0
    ties = 0
    margins = []

    for seed in seeds:
        for seat in [0, 1]:
            env = make("kaggriculture", configuration={"seed": seed})
            agents = [agent_a, agent_b] if seat == 0 else [agent_b, agent_a]
            state = env.run(agents)
            r0 = state[-1][0]["reward"]
            r1 = state[-1][1]["reward"]
            our_r = r0 if seat == 0 else r1
            opp_r = r1 if seat == 0 else r0
            diff = our_r - opp_r
            margins.append(diff)
            if diff > 0:
                wins += 1
                status = "WIN "
            elif diff < 0:
                losses += 1
                status = "LOSS"
            else:
                ties += 1
                status = "TIE "
            print(f"[{status}] Seed {seed} Seat {seat}: {name_a} {our_r:,.0f} vs {name_b} {opp_r:,.0f} (Margin: {diff:+,.0f})")

    win_rate = wins / (wins + losses + ties) * 100
    avg_margin = sum(margins) / len(margins)
    print(f"{'-'*75}")
    print(f"RESULT {name_a} vs {name_b}: Wins: {wins} | Losses: {losses} | Ties: {ties} | WinRate: {win_rate:.1f}% | Avg Margin: {avg_margin:+,.0f}")
    print(f"{'='*75}\n")
    return wins, losses, ties, win_rate, avg_margin


def main():
    holdout_seeds = [4400, 4401, 4402, 4403, 4404, 4405, 4406, 4407, 4408, 4409]

    # Tournament 1: v53 vs v52 (Current S12 Champion)
    w1, l1, t1, wr1, m1 = run_tournament(v53_agent, v52_agent, "v53_candidate", "v52_champion", holdout_seeds)

    # Tournament 2: v53 vs v50 (S10 Champion)
    w2, l2, t2, wr2, m2 = run_tournament(v53_agent, v50_agent, "v53_candidate", "v50_champion", holdout_seeds)

    print("\n" + "#" * 75)
    print("AGGREGATE CHAMPIONSHIP TOURNAMENT SUMMARY:")
    print(f"vs v52 (S12 Champion): {w1}W - {l1}L - {t1}T ({wr1:.1f}% Win Rate, Avg Margin: {m1:+,.0f})")
    print(f"vs v50 (S10 Champion): {w2}W - {l2}L - {t2}T ({wr2:.1f}% Win Rate, Avg Margin: {m2:+,.0f})")
    print("#" * 75 + "\n")


if __name__ == "__main__":
    main()

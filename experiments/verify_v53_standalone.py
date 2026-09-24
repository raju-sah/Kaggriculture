"""Verification script for standalone v53 agent."""

from kaggle_environments import make
import importlib.util

def load_agent(path):
    spec = importlib.util.spec_from_file_location("agent_mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, "agent", getattr(mod, "_kaggle_submission_entrypoint", None))

closer_cleo = load_agent("experiments/kag-corpus/refagents/closer_cleo.py")
broker_bea = load_agent("experiments/kag-corpus/refagents/broker_bea.py")
v53_agent = load_agent("experiments/v53_agent.py")

v52_agent = load_agent("experiments/v52_agent.py")

def main():
    print("Testing standalone v53_agent...")
    for seed in [4400, 4401]:
        for opp_name, opp_agent in [("closer_cleo", closer_cleo), ("broker_bea", broker_bea), ("v52", v52_agent)]:
            for seat in [0, 1]:
                env = make("kaggriculture", configuration={"seed": seed})
                agents = [v53_agent, opp_agent] if seat == 0 else [opp_agent, v53_agent]
                state = env.run(agents)
                r0 = state[-1][0]["reward"]
                r1 = state[-1][1]["reward"]
                our_r = r0 if seat == 0 else r1
                opp_r = r1 if seat == 0 else r0
                diff = our_r - opp_r
                print(f"[Seed {seed} Seat {seat}] v53: {our_r:,.0f} vs {opp_name}: {opp_r:,.0f} (Margin: {diff:+,.0f})")
                assert diff > 0, f"Lost or tied game: margin is {diff}"
    print("All standalone checks PASSED successfully!")

if __name__ == "__main__":
    main()

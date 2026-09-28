"""Record the exact day-6 h6 decision state for a set of seeds.

The swap rule must fire from observable quantities only. This driver runs real
games with `probe_agent.py` (frozen V92 + a recorder) in one seat and an
opponent in the other, and captures, at the day-6 h6 decision turn, everything
the rule is allowed to look at:

  market inventory + prices for MILK and WOOL
  town unlocked_shops (the stable day-6 set)
  our own shed MILK/WOOL balances and shed total
  our own pasture slots and live animals
  the incumbent tape's own market orders on that turn

The probe writes JSONL itself (Kaggle's loader execs the agent file in a fresh
namespace, so its module state is not reachable from here).

Seeds are processed one at a time in-process; that keeps peak CPU at one worker
so this can run alongside another worker's tournament.

Usage (from repo root):
    .venv/bin/python experiments/v101_commandcode/observe_seeds.py \
        --seeds 160001-160060 --opponent v92
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

HERE = Path(__file__).resolve().parent
PROBE = HERE / "probe_agent.py"
OPPONENTS = {
    "v92": ROOT / "experiments/v92_overflow_guard/candidate.py",
    "v50": ROOT / "experiments/v50_agent.py",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="160001-160060")
    ap.add_argument("--opponent", default="v92", choices=("v92", "v50"))
    ap.add_argument("--out", default=str(HERE / "decision_states.jsonl"))
    args = ap.parse_args()

    from kaggle_environments import make
    from simulation.tournament import parse_seeds

    seeds = parse_seeds(args.seeds)
    out = Path(args.out)
    opp = OPPONENTS[args.opponent]
    os.environ["V101_PROBE_OUT"] = str(out)
    os.environ["V101_PROBE_META"] = str(out.with_suffix(".meta.jsonl"))

    for seed in seeds:
        os.environ["V101_PROBE_SEED"] = str(seed)
        os.environ["V101_PROBE_OPPONENT"] = args.opponent
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=True)
        env.run([str(PROBE), str(opp)])
        rewards = [s.reward for s in env.steps[-1]]
        print(f"seed {seed}: final {rewards}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

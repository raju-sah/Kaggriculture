"""Replay-faithful terminal SELL ordering counterfactuals."""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[2]


def _value_order(action, observation, mode):
    result = copy.deepcopy(action or {})
    market = list(result.get("market") or [])
    prices = (observation.get("market") or {}).get("prices") or {}
    slots = []
    for i, order in enumerate(market):
        if isinstance(order, list) and len(order) >= 3 and order[0] == "SELL":
            item, qty = order[1], max(0, int(order[2] or 0))
            price = float(prices.get(item, 0) or 0)
            if mode == "value":
                score = price * qty
            elif mode == "price":
                score = price
            else:
                score = math.log1p(qty)
            slots.append((score, -i, copy.deepcopy(order)))
    if len(slots) >= 2:
        slots.sort(reverse=True)
        iterator = iter(x[2] for x in slots)
        result["market"] = [next(iterator) if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL" else o for o in market]
    return result


def replay(path: Path, candidate_seat: int, mode: str | None, start_step: int = 630):
    data = json.loads(path.read_text())
    step_index = [0, 0]

    def make_agent(seat):
        def agent(obs):
            idx = step_index[seat] + 1  # replay row 0 is the initial, unapplied state
            step_index[seat] += 1
            state = data["steps"][idx][seat]
            action = copy.deepcopy(state.get("action") or {})
            if mode and seat == candidate_seat and idx >= start_step:
                action = _value_order(action, obs, mode)
            return action
        return agent

    config = dict(data["configuration"])
    config["seed"] = data.get("info", {}).get("seed")
    env = make("kaggriculture", configuration=config, debug=True)
    env.run([make_agent(0), make_agent(1)])
    return [float(state.reward) for state in env.steps[-1]], step_index


def main():
    rows = []
    paths = sorted((ROOT / "experiments/v58_expansion/diagnostic_93602/baseline/replays").glob("v54-*.json"))
    for path in paths:
        # Candidate seat is encoded in the ab/ba filename.
        candidate_seat = 0 if "-ab-" in path.name else 1
        for mode in (None, "value", "price", "quantity"):
            rewards, calls = replay(path, candidate_seat, mode)
            rows.append({"replay": path.name, "candidate_seat": candidate_seat,
                         "mode": mode or "control", "rewards": rewards,
                         "candidate_margin": rewards[candidate_seat] - rewards[1-candidate_seat],
                         "calls": calls})
            print(rows[-1], flush=True)
    out = ROOT / "experiments/v58_expansion/terminal_order_probe_93602.json"
    out.write_text(json.dumps(rows, indent=2) + "\n")


if __name__ == "__main__":
    main()

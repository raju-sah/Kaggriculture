"""Reconstruct accepted unit sales in the three saved seed-92902 matches."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
REPLAYS = ROOT / "experiments/runs/v58_validation_baseline/replays"
GAMES = ROOT / "experiments/runs/v58_validation_baseline/games"
ENGINE_PATH = ROOT / ".venv/lib/python3.12/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py"
OPPONENTS = ("v52", "v53", "v54")


def load_engine():
    spec = importlib.util.spec_from_file_location("v60_kaggriculture_engine", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load engine at {ENGINE_PATH}")
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    return engine


def reconstruct(engine, replay):
    config = replay["configuration"]
    sales = [dict(), dict()]
    balance_mismatches = 0
    for tick in range(1, len(replay["steps"])):
        previous, current = replay["steps"][tick - 1], replay["steps"][tick]
        source = previous[0]["observation"]
        farms = copy.deepcopy(source["farms"])
        market = copy.deepcopy(source["market"])
        town = copy.deepcopy(source["town"])
        private = [copy.deepcopy(previous[seat]["observation"]["private"]) for seat in (0, 1)]
        actions = [(frame.get("action") or {}) for frame in current]
        day = int(source.get("day", 0) or 0)

        for seat in (0, 1):
            commands = [actions[seat].get("farmer", ["PASS"]),
                        *(actions[seat].get("hands") or [])]
            demand = {}
            for command in commands:
                if isinstance(command, list) and len(command) >= 2 and command[0] == "PLANT":
                    demand[command[1]] = demand.get(command[1], 0) + 1
            blocked = {crop for crop, count in demand.items()
                       if count > private[seat].get("seeds", {}).get(crop, 0)}
            for actor, command in enumerate(commands):
                if actor > len(farms[seat].get("hands", [])):
                    break
                if (isinstance(command, list) and len(command) >= 2
                        and command[0] == "PLANT" and command[1] in blocked):
                    command = ["PASS"]
                engine._apply_unit_action(
                    farms[seat], private[seat], actor, command,
                    int(config.get("boardSize", 10)), day,
                    int(config.get("turnsPerDay", 24)),
                    int(config.get("shedCapacity", 100)),
                )

        original_commit = engine._commit_unit

        def record_commit(op, item, price, farm, private_state, market_state,
                          shed_capacity=100):
            seat = 0 if farm is farms[0] else 1
            accepted = original_commit(op, item, price, farm, private_state,
                                       market_state, shed_capacity)
            if accepted and op == "SELL":
                row = sales[seat].setdefault(item, {"accepted_units": 0, "gross_revenue": 0})
                row["accepted_units"] += 1
                row["gross_revenue"] += price
            return accepted

        engine._commit_unit = record_commit
        states = [SimpleNamespace(
            observation=SimpleNamespace(farms=farms, market=market, town=town,
                                        private=private[seat]),
            action=actions[seat],
        ) for seat in (0, 1)]
        try:
            engine._process_market(states, SimpleNamespace(configuration=config))
        finally:
            engine._commit_unit = original_commit

        # Farm actions and town consumption have no cash effect. Exact equality
        # verifies that the engine market replay aligned with this saved frame.
        for seat in (0, 1):
            saved = current[0]["observation"]["farms"][seat]["money"]
            if abs(saved - farms[seat]["money"]) > 0.01:
                balance_mismatches += 1
    return sales, balance_mismatches


def first_market_divergences(replays, field):
    reference = replays[OPPONENTS[0]]
    items = reference["steps"][0][0]["observation"]["market"][field]
    result = {}
    for item in items:
        for tick in range(len(reference["steps"])):
            values = {opponent: replay["steps"][tick][0]["observation"]["market"][field].get(item)
                      for opponent, replay in replays.items()}
            if len(set(values.values())) > 1:
                obs = replays["v54"]["steps"][tick][0]["observation"]
                result[item] = {"frame": tick, "day": obs["day"], "hour": obs["hour"],
                                "values": values}
                break
    return result


def main():
    engine = load_engine()
    replays = {opponent: json.loads((REPLAYS / f"{opponent}-seed-92902-ab-repeat-0.json").read_text())
               for opponent in OPPONENTS}
    result = {"seed": 92902, "candidate_seat": 0, "matches": {},
              "first_price_divergence": first_market_divergences(replays, "prices"),
              "first_inventory_divergence": first_market_divergences(replays, "inventory")}
    for opponent, replay in replays.items():
        sales, mismatches = reconstruct(engine, replay)
        game = json.loads((GAMES / f"{opponent}-seed-92902-ab-repeat-0.json").read_text())
        candidate_revenue = sum(row["gross_revenue"] for row in sales[0].values())
        result["matches"][opponent] = {
            "final_coins": game["final_coins"],
            "candidate_margin": game["final_coins"][0] - game["final_coins"][1],
            "market_balance_mismatches": mismatches,
            "candidate_gross_sales": sales[0],
            "candidate_total_gross_sales": candidate_revenue,
            "opponent_gross_sales": sales[1],
        }
    out = ROOT / "experiments/v60_dispatch/market_interaction_92902.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(out.relative_to(ROOT))


if __name__ == "__main__":
    main()

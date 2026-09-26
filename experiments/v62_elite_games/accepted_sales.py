#!/usr/bin/env python3
"""Settle recorded action[t] from observation[t-1] with the matching Kaggle engine."""
import copy
import json
from collections import Counter, defaultdict
from pathlib import Path
from types import SimpleNamespace

from kaggle_environments.envs.kaggriculture import kaggriculture as engine

ROOT = Path(__file__).resolve().parent


def settle(path):
    game = json.loads(path.read_text())
    steps = game["steps"]
    config = game.get("configuration", {})
    cfg = SimpleNamespace(**{k: config.get(k, v) for k, v in {
        "boardSize": 10, "maxMarketOrdersPerTurn": 10, "farmHandCostMult": 1,
        "shedCapacity": 100, "turnsPerDay": 24}.items()})
    names = game.get("info", {}).get("TeamNames", [])
    totals = [Counter(), Counter()]
    sale_value = [Counter(), Counter()]
    transaction_value = [Counter(), Counter()]
    phase_totals = [defaultdict(Counter), defaultdict(Counter)]
    phase_value = [defaultdict(Counter), defaultdict(Counter)]
    atomic_cost_totals = [Counter(), Counter()]
    sale_value_by_phase = [defaultdict(Counter), defaultdict(Counter)]
    detail = []
    audit = {"aligned_transitions": 0, "cash_mismatches": 0, "max_cash_error": 0.0,
             "max_action_row": len(steps) - 1}
    original_commit = engine._commit_unit
    current_tx = None
    tracked_farms = None

    def record_commit(op, item, price, farm, private, market, shed_capacity=100):
        ok = original_commit(op, item, price, farm, private, market, shed_capacity)
        if ok and current_tx is not None:
            seat = 0 if farm is tracked_farms[0] else 1
            current_tx.append({"seat": seat, "op": op, "item": item, "price": price})
        return ok

    engine._commit_unit = record_commit
    try:
        for frame in range(1, len(steps)):
            previous, current = steps[frame - 1], steps[frame]
            obs = previous[0]["observation"]
            farms = copy.deepcopy(obs["farms"])
            tracked_farms = farms
            market = copy.deepcopy(obs["market"])
            privates = [copy.deepcopy(previous[s]["observation"]["private"]) for s in range(2)]
            actions = [current[s].get("action") or {} for s in range(2)]
            before_cash = [float(farms[s]["money"]) for s in range(2)]
            before_hands = [len(farms[s].get("hands", [])) for s in range(2)]
            before_land = [len(farms[s].get("unlocked_quadrants", [])) for s in range(2)]
            day = int(obs.get("day", (frame - 1) // int(getattr(cfg, "turnsPerDay", 24))))
            phase = "opening_0_5" if day <= 5 else "day6_11" if day <= 11 else "day12_23" if day <= 23 else "late_24_29"
            turns_per_day = int(getattr(cfg, "turnsPerDay", 24))

            blocked = []
            for s in range(2):
                unit_acts = [actions[s].get("farmer", ["PASS"]), *(actions[s].get("hands") or [])]
                demand = Counter(a[1] for a in unit_acts if isinstance(a, list) and len(a) >= 2 and a[0] == "PLANT")
                blocked.append({crop for crop, count in demand.items() if count > privates[s].get("seeds", {}).get(crop, 0)})
            for s in range(2):
                unit_acts = [actions[s].get("farmer", ["PASS"]), *(actions[s].get("hands") or [])]
                for idx, action in enumerate(unit_acts):
                    if isinstance(action, list) and len(action) >= 2 and action[0] == "PLANT" and action[1] in blocked[s]:
                        action = ["PASS"]
                    engine._apply_unit_action(farms[s], privates[s], idx, action,
                        int(getattr(cfg, "boardSize", 10)), day, turns_per_day,
                        int(getattr(cfg, "shedCapacity", 100)))

            class Obs:
                pass
            states = []
            for s in range(2):
                o = Obs(); o.market = market; o.farms = farms; o.private = privates[s]
                states.append(SimpleNamespace(observation=o, action=actions[s]))
            current_tx = []
            engine._process_market(states, SimpleNamespace(configuration=cfg))

            grouped = defaultdict(Counter)
            values = defaultdict(Counter)
            for tx in current_tx:
                s, op, item, price = tx["seat"], tx["op"], tx["item"], tx["price"]
                totals[s][(op, item)] += 1
                grouped[s][(op, item)] += 1
                values[s][(op, item)] += price
                transaction_value[s][(op, item)] += price
                phase_totals[s][phase][(op, item)] += 1
                phase_value[s][phase][(op, item)] += price
                if op == "SELL":
                    sale_value[s][item] += price
                    sale_value_by_phase[s][phase][item] += price

            frame_players = []
            for s in range(2):
                observed_cash = float(current[s]["observation"]["farms"][s]["money"])
                error = abs(observed_cash - float(farms[s]["money"]))
                audit["aligned_transitions"] += 1
                audit["max_cash_error"] = max(audit["max_cash_error"], error)
                if error > .011: audit["cash_mismatches"] += 1
                sell_value = sum(v for (op, item), v in values[s].items() if op == "SELL")
                buy_cost = sum(v for (op, item), v in values[s].items() if op in ("BUY_PRODUCT", "BUY_SEED", "BUY_ANIMAL"))
                atomic_cost = round(before_cash[s] - float(farms[s]["money"]) - buy_cost + sell_value, 2)
                atomic_cost_totals[s][phase] += atomic_cost
                frame_players.append({
                    "seat": s, "name": names[s] if s < len(names) else str(s),
                    "accepted_units": {op: {item: n for (kind, item), n in grouped[s].items() if kind == op}
                                       for op in ("SELL", "BUY_PRODUCT", "BUY_SEED", "BUY_ANIMAL")
                                       if any(kind == op for kind, _ in grouped[s])},
                    "accepted_value_by_operation": {op: sum(v for (kind, item), v in values[s].items() if kind == op)
                                                     for op in ("SELL", "BUY_PRODUCT", "BUY_SEED", "BUY_ANIMAL")},
                    "accepted_value_by_product": {op: {item: v for (kind, item), v in values[s].items() if kind == op}
                                                  for op in ("SELL", "BUY_PRODUCT", "BUY_SEED", "BUY_ANIMAL")
                                                  if any(kind == op for kind, _ in values[s])},
                    "accepted_land_orders": len(farms[s].get("unlocked_quadrants", [])) - before_land[s],
                    "accepted_hires": len(farms[s].get("hands", [])) - before_hands[s],
                    "atomic_net_cost_land_hire": atomic_cost,
                    "direct_cash_delta": round(observed_cash - before_cash[s], 2),
                    "cash_reconstruction_error": round(error, 2),
                })
            if current_tx or any(p["accepted_land_orders"] or p["accepted_hires"] for p in frame_players):
                detail.append({"action_frame": frame, "day": day, "hour": (frame - 1) % turns_per_day,
                               "players": frame_players})
    finally:
        engine._commit_unit = original_commit

    player_summary = []
    for s in range(2):
        player_summary.append({
            "seat": s, "name": names[s] if s < len(names) else str(s),
            "accepted_units": {op: {item: n for (kind, item), n in totals[s].items() if kind == op}
                               for op in ("SELL", "BUY_PRODUCT", "BUY_SEED", "BUY_ANIMAL")
                               if any(kind == op for kind, _ in totals[s])},
            "accepted_value_by_operation": {op: sum(v for (kind, item), v in transaction_value[s].items() if kind == op)
                                             for op in ("SELL", "BUY_PRODUCT", "BUY_SEED", "BUY_ANIMAL")},
            "accepted_value_by_product": {op: {item: v for (kind, item), v in transaction_value[s].items() if kind == op}
                                          for op in ("SELL", "BUY_PRODUCT", "BUY_SEED", "BUY_ANIMAL")
                                          if any(kind == op for kind, _ in transaction_value[s])},
            "accepted_sale_value_by_product": dict(sale_value[s]),
            "accepted_sale_value_by_phase": {phase: dict(items) for phase, items in sale_value_by_phase[s].items()},
            "accepted_units_by_phase": {phase: {op: {item: n for (kind, item), n in items.items() if kind == op}
                                                   for op in ("SELL", "BUY_PRODUCT", "BUY_SEED", "BUY_ANIMAL")
                                                   if any(kind == op for kind, _ in items)}
                                         for phase, items in phase_totals[s].items()},
            "accepted_value_by_phase": {phase: {op: sum(v for (kind, item), v in items.items() if kind == op)
                                                  for op in ("SELL", "BUY_PRODUCT", "BUY_SEED", "BUY_ANIMAL")}
                                        for phase, items in phase_value[s].items()},
            "land_and_hire_net_cost_by_phase": dict(atomic_cost_totals[s]),
        })
    return {"episode_id": game.get("info", {}).get("EpisodeId"), "module_version": game.get("module_version"),
            "replay_sha256": __import__("hashlib").sha256(path.read_bytes()).hexdigest(),
            "alignment": "action[t] is paired with observation[t-1] and produces observation[t]",
            "players": player_summary, "audit": audit,
            "transactions_by_step": detail if game.get("info", {}).get("EpisodeId") == 113718271 else []}


if __name__ == "__main__":
    results = [settle(p) for p in sorted((ROOT / "replays").glob("episode-*-replay.json"))]
    (ROOT / "accepted_sales.json").write_text(json.dumps(results, separators=(",", ":"), sort_keys=True) + "\n")
    print(f"wrote {ROOT / 'accepted_sales.json'}")

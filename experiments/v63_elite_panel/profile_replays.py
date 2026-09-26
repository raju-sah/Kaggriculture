#!/usr/bin/env python3
"""Compact analysis of public Kaggriculture game replays."""
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPLAYS = ROOT / "replays"
OUT = ROOT / "profiles.json"
PHASES = {"opening_0_5": (0, 5), "day6_11": (6, 11), "day12_23": (12, 23), "late_24_29": (24, 29)}
SNAPSHOT_DAYS = (0, 6, 12, 20, 29)


def farm_counts(farm):
    crops, animals, structures = Counter(), Counter(), Counter()
    for row in farm["tiles"]:
        for tile in row:
            if not isinstance(tile, dict):
                continue
            if tile.get("kind") == "PLANT": crops[tile.get("crop", "?")] += 1
            if tile.get("animal"): animals[tile["animal"]] += 1
            elif tile.get("kind") in ("COOP", "PASTURE"): structures[tile["kind"]] += 1
    return dict(sorted(crops.items())), dict(sorted(animals.items())), dict(sorted(structures.items()))


def parse(path):
    raw = path.read_bytes()
    game = json.loads(raw)
    steps = game["steps"]
    names = game["info"].get("TeamNames", [])
    eid = game.get("info", {}).get("EpisodeId")
    players = []
    for seat in range(2):
        by_phase = {p: {"ops": Counter(), "market": Counter(), "market_qty": Counter(), "orders": 0} for p in PHASES}
        all_ops, all_market, day_market = Counter(), Counter(), defaultdict(Counter)
        nonpass = effective_orders = 0
        movement_attempts = movement_success = 0
        day_actions = defaultdict(Counter)
        for i, step in enumerate(steps):
            agent = step[seat]
            obs = agent.get("observation") or {}
            day = int(obs.get("day", i // 24))
            phase = next((key for key, (lo, hi) in PHASES.items() if lo <= day <= hi), "other")
            action = agent.get("action") or {}
            farmer = action.get("farmer") or ["PASS"]
            hands = action.get("hands") or []
            units = [("farmer", 0, farmer)] + [("hand", h_idx, h or ["PASS"]) for h_idx, h in enumerate(hands)]
            for unit, unit_idx, op in units:
                opname = str(op[0]) if op else "PASS"
                all_ops[opname] += 1
                by_phase[phase]["ops"][opname] += 1
                day_actions[day][opname] += 1
                if opname != "PASS": nonpass += 1
                if opname in {"NORTH", "SOUTH", "EAST", "WEST"}:
                    movement_attempts += 1
                    if i + 1 < len(steps):
                        before = obs.get("farms", [{}])[seat]
                        after = (steps[i + 1][seat].get("observation") or {}).get("farms", [{}])[seat]
                        if unit == "farmer":
                            bp, ap = before.get("farmer"), after.get("farmer")
                        else:
                            bp, ap = before.get("hands", []), after.get("hands", [])
                            bp = bp[unit_idx] if unit_idx < len(bp) else None
                            ap = ap[unit_idx] if unit_idx < len(ap) else None
                        if bp is not None and ap is not None and bp != ap:
                            movement_success += 1
            for order in action.get("market") or []:
                if not order: continue
                op = str(order[0]); item = str(order[1]) if len(order) > 1 else ""
                qty = int(order[2]) if len(order) > 2 and isinstance(order[2], (int, float)) else 1
                label = f"{op}:{item}" if item else op
                all_market[label] += qty
                by_phase[phase]["market"][label] += 1
                by_phase[phase]["market_qty"][label] += qty
                by_phase[phase]["orders"] += 1
                day_market[day][label] += qty
                if op in {"SELL", "SELL_TOWN"}: effective_orders += qty
        snapshots = []
        for day in SNAPSHOT_DAYS:
            idx = min((day * 24 if day == 0 else day * 24 + 1), len(steps) - 1)
            obs = steps[idx][seat].get("observation") or {}
            farm = obs.get("farms", [{}, {}])[seat]
            private = obs.get("private") or {}
            crops, animals, structures = farm_counts(farm)
            snapshots.append({"day": day, "observation_step": idx, "money": farm.get("money"),
                "hands": len(farm.get("hands", [])), "unlocked_quadrants": farm.get("unlocked_quadrants", []),
                "crops": crops, "animals": animals, "structures": structures,
                "shed": {k: int(v) for k, v in sorted((private.get("shed") or {}).items()) if v},
                "seeds": {k: int(v) for k, v in sorted((private.get("seeds") or {}).items()) if v},
                "inventories": private.get("inventories", []),
                "shops": obs.get("town", {}).get("unlocked_shops", []),
                "tiles_total": sum(1 for row in farm.get("tiles", []) for tile in row if isinstance(tile, dict)),
                "market_prices": obs.get("market", {}).get("prices", {})})
        phase_result = {}
        for phase, counts in by_phase.items():
            phase_result[phase] = {"unit_actions": sum(counts["ops"].values()), "nonpass_actions": sum(v for k,v in counts["ops"].items() if k != "PASS"),
                "op_counts": dict(sorted(counts["ops"].items())), "market_order_counts": dict(sorted(counts["market"].items())),
                "market_quantity": dict(sorted(counts["market_qty"].items()))}
        final_obs = steps[-1][seat].get("observation") or {}
        final_farm = final_obs.get("farms", [{}, {}])[seat]
        final_private = final_obs.get("private") or {}
        final_crops, final_animals, final_structures = farm_counts(final_farm)
        closing = {"observation_step": len(steps) - 1, "day": final_obs.get("day"), "hour": final_obs.get("hour"),
            "money": final_farm.get("money"), "hands": len(final_farm.get("hands", [])),
            "unlocked_quadrants": final_farm.get("unlocked_quadrants", []), "crops": final_crops,
            "animals": final_animals, "structures": final_structures,
            "shed": {k: int(v) for k, v in sorted((final_private.get("shed") or {}).items()) if v},
            "seeds": {k: int(v) for k, v in sorted((final_private.get("seeds") or {}).items()) if v},
            "inventories": final_private.get("inventories", []),
            "shops": final_obs.get("town", {}).get("unlocked_shops", []),
            "market_prices": final_obs.get("market", {}).get("prices", {})}
        players.append({"seat": seat, "name": names[seat] if seat < len(names) else f"seat{seat}",
            "reward": (game.get("rewards") or [None,None])[seat], "phases": phase_result,
            "snapshots": snapshots, "closing": closing, "market_quantity_all_game": dict(sorted(all_market.items())),
            "action_counts_all_game": dict(sorted(all_ops.items())),
            "daily_sales_and_buys": {str(d): dict(sorted(c.items())) for d,c in day_market.items()},
            "movement_attempts": movement_attempts, "movement_success_from_next_obs": movement_success,
            "nonpass_actions": nonpass, "sell_quantity_declared": effective_orders})
    return {"episode_id": eid, "seed": game.get("info", {}).get("seed"), "file": path.name,
        "sha256": hashlib.sha256(raw).hexdigest(), "module_version": game.get("module_version"),
        "steps": len(steps), "create_source": "kaggle competitions replay <episode_id>",
        "players": players, "rewards": game.get("rewards")}


if __name__ == "__main__":
    OUT.write_text(json.dumps([parse(p) for p in sorted(REPLAYS.glob("episode-*-replay.json"))], indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT}")

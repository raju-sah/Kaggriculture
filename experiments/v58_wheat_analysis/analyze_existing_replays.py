#!/usr/bin/env python3
"""Read-only audit of retained v58 wheat-overlay artifacts; runs no games."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCREEN = ROOT / "experiments/v58_policy/wheat_fert_screen"


def read_json(path: Path):
    return json.loads(path.read_text())


def active_animals(obs: dict, seat: int) -> tuple[Counter, int]:
    counts: Counter = Counter()
    max_unfed = 0
    for row in obs["farms"][seat]["tiles"]:
        for tile in row:
            if isinstance(tile, dict) and "animal" in tile:
                counts[tile["animal"]] += 1
                max_unfed = max(max_unfed, tile.get("consecutive_unfed", 0))
    return counts, max_unfed


def replay_audit():
    name = "v50-seed-93700-ab-repeat-0"
    replay = read_json(SCREEN / f"throughput/replays/{name}.json")
    audit = read_json(SCREEN / "throughput/audit-v50-93700-ab.json")
    seat = 0

    commits_by_step = defaultdict(list)
    totals = defaultdict(Counter)
    for commit in audit["market_commits"]:
        commits_by_step[commit["step"]].append(commit)
        if commit["seat"] == seat and commit["op"] == "SELL":
            totals[commit["item"]]["units"] += commit["inventory_delta"]
            totals[commit["item"]]["cash"] += commit["money_delta"]

    # The serialized action at row i is the action chosen from row i-1's
    # observation. Validate FEED against that pre-action state and the engine's
    # _apply_unit_action semantics, without executing the environment.
    feed_by_day = defaultdict(Counter)
    feed_events = []
    for frame in range(1, len(replay["steps"])):
        pre = replay["steps"][frame - 1][seat]["observation"]
        action = replay["steps"][frame][seat]["action"] or {}
        farm = pre["farms"][seat]
        inventories = [dict(inv) for inv in pre["private"].get("inventories", [])]
        positions = [farm.get("farmer")] + list(farm.get("hands", []))
        unit_actions = [action.get("farmer", [])] + list(action.get("hands", []))
        for unit, unit_action in enumerate(unit_actions):
            if not unit_action or unit_action[0] != "FEED":
                continue
            pos = positions[unit] if unit < len(positions) else None
            tile = farm["tiles"][pos[1]][pos[0]] if pos else None
            has_animal = isinstance(tile, dict) and "animal" in tile
            available_wheat = inventories[unit].get("WHEAT", 0) if unit < len(inventories) else 0
            if has_animal and not tile.get("fed_today") and available_wheat > 0:
                feed_by_day[pre["day"]]["success"] += 1
                inventories[unit]["WHEAT"] -= 1
                tile["fed_today"] = True
                result = "success"
            elif has_animal and not tile.get("fed_today") and available_wheat == 0:
                feed_by_day[pre["day"]]["no_wheat_on_animal"] += 1
                result = "no_wheat_on_animal"
            else:
                feed_by_day[pre["day"]]["wrong_tile_or_already_fed"] += 1
                result = "wrong_tile_or_already_fed"
            feed_events.append({
                "frame": frame,
                "day": pre["day"],
                "hour": pre["hour"],
                "unit": unit,
                "result": result,
                "animal": tile.get("animal") if isinstance(tile, dict) else None,
                "carried_wheat": available_wheat,
                "shed_wheat": pre["private"]["shed"].get("WHEAT", 0),
            })

    sale_frames = []
    for frame in range(1, len(replay["steps"])):
        pre = replay["steps"][frame - 1][seat]["observation"]
        action = replay["steps"][frame][seat]["action"] or {}
        wheat_orders = [o for o in action.get("market", []) if o and o[0] == "SELL" and o[1] == "WHEAT"]
        if not wheat_orders or frame < 73:
            continue
        sold = sum(c["inventory_delta"] for c in commits_by_step[frame]
                   if c["seat"] == seat and c["op"] == "SELL" and c["item"] == "WHEAT")
        bought = -sum(c["inventory_delta"] for c in commits_by_step[frame]
                      if c["seat"] == seat and c["op"] == "BUY_PRODUCT" and c["item"] == "WHEAT")
        sale_frames.append({
            "frame": frame,
            "input_day": pre["day"],
            "input_hour": pre["hour"],
            "input_shed_wheat": pre["private"]["shed"].get("WHEAT", 0),
            "input_carried_wheat": sum(inv.get("WHEAT", 0) for inv in pre["private"].get("inventories", [])),
            "submitted_units": sum(o[2] for o in wheat_orders if len(o) > 2),
            "accepted_units": sold,
            "same_turn_buys": bought,
            "market_orders": action.get("market", []),
            "farmer_action": action.get("farmer", []),
        })

    day5_pickups = []
    shed_access = {(4, 4), (5, 4), (4, 5), (5, 5)}
    for frame in range(1, len(replay["steps"])):
        pre = replay["steps"][frame - 1][seat]["observation"]
        if pre["day"] != 5:
            continue
        action = replay["steps"][frame][seat]["action"] or {}
        farm = pre["farms"][seat]
        positions = [farm.get("farmer")] + list(farm.get("hands", []))
        unit_actions = [action.get("farmer", [])] + list(action.get("hands", []))
        for unit, unit_action in enumerate(unit_actions):
            if not unit_action or unit_action[:2] != ["PICKUP", "WHEAT"]:
                continue
            pos = positions[unit] if unit < len(positions) else None
            requested = int(unit_action[2]) if len(unit_action) > 2 else 1
            available = pre["private"]["shed"].get("WHEAT", 0) if tuple(pos or []) in shed_access else 0
            day5_pickups.append({
                "frame": frame,
                "input_hour": pre["hour"],
                "unit": unit,
                "position": pos,
                "requested": requested,
                "shed_before": pre["private"]["shed"].get("WHEAT", 0),
                "pickup_feasible_units": min(requested, available),
            })

    herd_by_day = {}
    for state in replay["steps"]:
        obs = state[seat]["observation"]
        if obs["hour"] == 0:
            counts, max_unfed = active_animals(obs, seat)
            herd_by_day[str(obs["day"])] = {"animals": dict(counts), "max_consecutive_unfed": max_unfed}

    market_totals = {
        item: dict(values) for item, values in totals.items()
    }
    return {
        "replay": f"experiments/v58_policy/wheat_fert_screen/throughput/replays/{name}.json",
        "seed": 93700,
        "candidate_seat": seat,
        "candidate_reward": replay["rewards"][seat],
        "opponent_reward": replay["rewards"][1 - seat],
        "candidate_accepted_sales": market_totals,
        "wheat_sale_frames_from_day3": sale_frames,
        "day5_wheat_pickup_attempts": day5_pickups,
        "feed_results_by_input_day": {str(d): dict(c) for d, c in sorted(feed_by_day.items())},
        "first_feed_events_on_day5": [e for e in feed_events if e["day"] == 5],
        "herd_at_day_boundaries": herd_by_day,
    }


def paired_screen():
    control = {g["game_id"]: g for g in read_json(SCREEN / "control/games.json")}
    overlay = {g["game_id"]: g for g in read_json(SCREEN / "throughput/games.json")}
    pairs = []
    for game_id, trial in sorted(overlay.items()):
        baseline = control.get(game_id)
        if baseline is None:
            continue
        if (trial["final_coins"][trial["candidate_seat"]] is None
                or baseline["final_coins"][baseline["candidate_seat"]] is None):
            continue
        seat = trial["candidate_seat"]
        trial_margin = trial["final_coins"][seat] - trial["final_coins"][1 - seat]
        baseline_margin = baseline["final_coins"][seat] - baseline["final_coins"][1 - seat]
        pairs.append({
            "game_id": game_id,
            "seed": trial["seed"],
            "candidate_seat": seat,
            "control_margin": baseline_margin,
            "overlay_margin": trial_margin,
            "change": trial_margin - baseline_margin,
        })
    return pairs


if __name__ == "__main__":
    print(json.dumps({"replay_audit": replay_audit(), "paired_screen": paired_screen()}, indent=2))

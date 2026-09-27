#!/usr/bin/env python3
"""Audit downloaded official V92 replays with the pinned Kaggriculture engine.

Run from the repository root with:
    .venv/bin/python experiments/v92_official/analyze_replays.py

The source replays are read from experiments/kaggle/v92_official/. The tool
writes compact CSV and JSON summaries beside this file. It recomputes the V50
base action at the V92 guard observation and replays every recorded transition
through engine unit and market settlement; zero cash mismatches are required
for the sales totals to be considered exact.
"""

from __future__ import annotations

import copy
import csv
import glob
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path
from types import SimpleNamespace

from kaggle_environments.envs.kaggriculture import kaggriculture as engine


ROOT = Path(__file__).resolve().parents[2]
REPLAY_DIR = ROOT / "experiments/kaggle/v92_official"
HERE = Path(__file__).resolve().parent
PHASE_DAYS = (5, 10, 15, 20, 23, 25, 27, 29)
SNAPSHOT_DAYS = (10, 15, 20, 23, 27, 29)
QUOTE_ITEMS = ("MILK", "WOOL", "EGG", "STRAWBERRY", "WHEAT", "FERTILIZER")
ORIGINAL_TEN_IDS = {
    114158802, 114160308, 114161728, 114163744, 114164630,
    114166061, 114167570, 114169079, 114170594, 114172061,
}


def load_candidate():
    path = ROOT / "experiments/v92_overflow_guard/candidate.py"
    spec = importlib.util.spec_from_file_location("v92_official_audit_candidate", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalized_observation(observation: dict, configuration: dict) -> tuple[dict, bool]:
    """Public episode replays omit observation.step; restore the specified clock field."""
    obs = copy.deepcopy(observation)
    if obs.get("step") is not None:
        return obs, False
    turns_per_day = int(configuration.get("turnsPerDay", 24) or 24)
    obs["step"] = int(obs.get("day", 0) or 0) * turns_per_day + int(obs.get("hour", 0) or 0)
    return obs, True


def snapshot(game, day: int, seat: int) -> dict:
    frame = min(day * 24 + 23, len(game["steps"]) - 1)
    obs = game["steps"][frame][seat]["observation"]
    farm = obs["farms"][seat]
    tiles = [tile for row in farm.get("tiles", []) for tile in row if isinstance(tile, dict)]
    crops = Counter(tile["crop"] for tile in tiles if tile.get("kind") == "PLANT" and tile.get("crop"))
    animals = Counter(tile["animal"] for tile in tiles if tile.get("animal"))
    return {
        "cash": round(float(farm.get("money", 0))),
        "hands": len(farm.get("hands", [])),
        "crops": dict(sorted(crops.items())),
        "animals": dict(sorted(animals.items())),
        "shops": list((obs.get("town") or {}).get("unlocked_shops", [])),
        "quotes": {item: (obs.get("market", {}).get("prices", {}) or {}).get(item) for item in QUOTE_ITEMS},
    }


def replay_ledger(game, configuration) -> tuple[list[dict], list[int]]:
    """Replay actions through the installed 1.32.7 engine and record accepted cash."""
    cfg = SimpleNamespace(
        **{
            key: configuration.get(key, default)
            for key, default in {
                "boardSize": 10,
                "maxMarketOrdersPerTurn": 10,
                "farmHandCostMult": 1,
                "shedCapacity": 100,
                "turnsPerDay": 24,
            }.items()
        }
    )
    totals = [defaultdict(Counter) for _ in range(2)]
    cash_mismatches = [0, 0]
    original_commit = engine._commit_unit
    active_farms: list[dict] = []
    committed: list[tuple[int, str, str, float]] = []

    def record_commit(op, item, price, farm, private, market, shed_capacity=100):
        ok = original_commit(op, item, price, farm, private, market, shed_capacity)
        if ok:
            seat = next((i for i, current in enumerate(active_farms) if farm is current), -1)
            committed.append((seat, op, item, float(price)))
        return ok

    engine._commit_unit = record_commit
    try:
        for frame in range(1, len(game["steps"])):
            previous, current = game["steps"][frame - 1], game["steps"][frame]
            previous_obs = previous[0]["observation"]
            day = int(previous_obs.get("day", 0))
            farms = copy.deepcopy(previous_obs["farms"])
            active_farms = farms
            private = [copy.deepcopy(previous[seat]["observation"]["private"]) for seat in range(2)]
            market = copy.deepcopy(previous_obs["market"])
            actions = [copy.deepcopy(current[seat].get("action") or {}) for seat in range(2)]

            for seat in range(2):
                units = [actions[seat].get("farmer", ["PASS"]), *(actions[seat].get("hands") or [])]
                for unit_index, action in enumerate(units):
                    engine._apply_unit_action(
                        farms[seat], private[seat], unit_index, action,
                        int(cfg.boardSize), day, int(cfg.turnsPerDay), int(cfg.shedCapacity),
                    )

            states = [
                SimpleNamespace(
                    observation=SimpleNamespace(market=market, farms=farms, private=private[seat]),
                    action=actions[seat],
                )
                for seat in range(2)
            ]
            committed.clear()
            engine._process_market(states, SimpleNamespace(configuration=cfg))
            for seat, op, item, price in committed:
                totals[seat][op][item] += price

            for seat in range(2):
                observed_cash = float(current[seat]["observation"]["farms"][seat]["money"])
                if abs(float(farms[seat]["money"]) - observed_cash) > 0.011:
                    cash_mismatches[seat] += 1
    finally:
        engine._commit_unit = original_commit

    result = []
    for seat in range(2):
        result.append({op: dict(sorted(items.items())) for op, items in totals[seat].items()})
    return result, cash_mismatches


def analyze(path: Path, candidate) -> dict:
    game = json.loads(path.read_text())
    names = [agent["Name"] for agent in game["info"].get("Agents", [])]
    raj_seat = names.index("Rajusah")
    opponent_seat = 1 - raj_seat
    rewards = game["rewards"]
    configuration = game.get("configuration", {})

    checkpoints = {str(day): [snapshot(game, day, seat) for seat in (raj_seat, opponent_seat)] for day in SNAPSHOT_DAYS}
    # Cash samples are always recorded in player order [Rajusah, opponent].
    phase_cash = {
        str(day): [snapshot(game, day, raj_seat)["cash"], snapshot(game, day, opponent_seat)["cash"]]
        for day in PHASE_DAYS
    }

    guard_frame = 23 * 24 + 23
    guard_obs, _ = normalized_observation(game["steps"][guard_frame][raj_seat]["observation"], configuration)
    # Replay actions settle against the previous frame's observation; the
    # decision for the guard observation is recorded on the following frame.
    logged_action = game["steps"][guard_frame + 1][raj_seat].get("action") or {}
    base_action = None
    wrapped_action = None
    loader_matches = 0
    loader_mismatches = []
    missing_step_observations = 0
    # Run the real embedded V50/V92 call sequentially through this replay. The
    # current official replay writer omits observation.step, so reconstruct it
    # from day/hour before each policy call, as the runtime observation includes it.
    for frame_index in range(len(game["steps"]) - 1):
        raw_obs = game["steps"][frame_index][raj_seat]["observation"]
        obs, step_was_missing = normalized_observation(raw_obs, configuration)
        missing_step_observations += int(step_was_missing)
        if frame_index == guard_frame:
            base_action = candidate._v50_agent(obs, configuration)
            predicted = candidate._v92_apply(obs, copy.deepcopy(base_action))
            wrapped_action = predicted
        else:
            predicted = candidate._v92_entrypoint(obs, configuration)
        recorded = game["steps"][frame_index + 1][raj_seat].get("action") or {}
        if predicted == recorded:
            loader_matches += 1
        else:
            loader_mismatches.append(frame_index)
    if base_action is None or wrapped_action is None:
        raise RuntimeError(f"guard observation missing in {path}")
    private = guard_obs.get("private") or {}
    shed = candidate._v92_shed_total(private)
    carried = candidate._v92_carried_total(private)
    buys = candidate._v92_buy_units(base_action.get("market") or [], "WHEAT") + candidate._v92_buy_units(base_action.get("market") or [], "FERTILIZER")
    projection = shed + carried + buys + candidate.HARVEST_ALLOWANCE
    guard_fired = (wrapped_action.get("market") or []) != (base_action.get("market") or [])

    settlements, cash_mismatches = replay_ledger(game, configuration)
    sale_totals = []
    for seat in (raj_seat, opponent_seat):
        sale_totals.append(sum(settlements[seat].get("SELL", {}).values()))

    purchases = []
    for action_frame in range(1, len(game["steps"])):
        frame = game["steps"][action_frame]
        action = frame[raj_seat].get("action") or {}
        animals = [order for order in action.get("market", []) if len(order) >= 3 and order[0] == "BUY_ANIMAL"]
        if animals:
            obs = game["steps"][action_frame - 1][raj_seat]["observation"]
            purchases.append({"step": action_frame - 1, "day": obs.get("day"), "hour": obs.get("hour"), "orders": animals})

    actual_action_matches = wrapped_action == logged_action
    return {
        "file": path.name,
        "episode_id": game.get("info", {}).get("EpisodeId"),
        "cohort": "original_10" if game.get("info", {}).get("EpisodeId") in ORIGINAL_TEN_IDS else "out_of_sample",
        "seed": game.get("info", {}).get("seed"),
        "rajusah_seat": raj_seat,
        "opponent": names[opponent_seat],
        "rajusah_score": rewards[raj_seat],
        "opponent_score": rewards[opponent_seat],
        "margin": round(float(rewards[raj_seat]) - float(rewards[opponent_seat])),
        "outcome": "W" if rewards[raj_seat] > rewards[opponent_seat] else "L" if rewards[raj_seat] < rewards[opponent_seat] else "D",
        "phase_cash_raj_opponent": phase_cash,
        "snapshots": checkpoints,
        "guard": {
            "base_market": base_action.get("market", []),
            "wrapped_market": wrapped_action.get("market", []),
            "logged_market": logged_action.get("market", []),
            "shed_units": shed,
            "carried_units": carried,
            "base_wheat_fertilizer_buys": buys,
            "projection_with_harvest_allowance": projection,
            "fired": guard_fired,
            "logged_action_matches_recomputed_v92": actual_action_matches,
            "base_call_matches_logged_next_frame": base_action == logged_action,
        },
        "loader_reproduction": {
            "matched_actions": loader_matches,
            "checked_actions": len(game["steps"]) - 1,
            "mismatch_steps": loader_mismatches,
            "missing_step_observations_reconstructed": missing_step_observations,
            "step_reconstruction": "step = day * turnsPerDay + hour",
        },
        "animal_purchases_rajusah": purchases,
        "settlement": {
            "accepted_sales_cash_raj_opponent": sale_totals,
            "accepted_sales_by_item_raj": settlements[raj_seat].get("SELL", {}),
            "accepted_sales_by_item_opponent": settlements[opponent_seat].get("SELL", {}),
            "product_buys_raj": settlements[raj_seat].get("BUY_PRODUCT", {}),
            "animal_buys_raj": settlements[raj_seat].get("BUY_ANIMAL", {}),
            "cash_mismatches_by_seat": cash_mismatches,
        },
    }


def main() -> None:
    paths = [Path(p) for p in sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))]
    if not paths:
        raise SystemExit(f"no replay JSONs found in {REPLAY_DIR}")
    # A fresh policy module per replay mirrors the Kaggle process lifetime.
    results = [analyze(path, load_candidate()) for path in paths]
    json_path = HERE / "replay_summary.json"
    csv_path = HERE / "replay_summary.csv"
    json_path.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")

    columns = [
        "cohort", "episode_id", "seed", "outcome", "rajusah_seat", "opponent", "rajusah_score", "opponent_score", "margin",
        "guard_fired", "guard_projection", "base_market", "logged_guard_market", "loader_matches", "loader_checked", "loader_mismatches",
        "cash_d5", "cash_d10", "cash_d15", "cash_d20", "cash_d23", "cash_d25", "cash_d27", "cash_d29",
        "raj_sales_cash", "opponent_sales_cash", "raj_milk_sales", "opponent_milk_sales", "raj_wool_sales", "opponent_wool_sales",
        "raj_egg_sales", "opponent_egg_sales", "raj_strawberry_sales", "opponent_strawberry_sales", "raj_wheat_sales", "opponent_wheat_sales",
        "raj_cows_d15", "opponent_cows_d15", "raj_sheep_d15", "opponent_sheep_d15", "cash_mismatches",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=columns)
        writer.writeheader()
        for game in results:
            phases = game["phase_cash_raj_opponent"]
            snaps = game["snapshots"]
            raj_settlement = game["settlement"]
            row = {
                "cohort": game["cohort"], "episode_id": game["episode_id"], "seed": game["seed"], "outcome": game["outcome"],
                "rajusah_seat": game["rajusah_seat"], "opponent": game["opponent"],
                "rajusah_score": game["rajusah_score"], "opponent_score": game["opponent_score"], "margin": game["margin"],
                "guard_fired": game["guard"]["fired"], "guard_projection": game["guard"]["projection_with_harvest_allowance"],
                "base_market": json.dumps(game["guard"]["base_market"], ensure_ascii=False, separators=(",", ":")),
                "logged_guard_market": json.dumps(game["guard"]["logged_market"], ensure_ascii=False, separators=(",", ":")),
                "loader_matches": game["loader_reproduction"]["matched_actions"],
                "loader_checked": game["loader_reproduction"]["checked_actions"],
                "loader_mismatches": len(game["loader_reproduction"]["mismatch_steps"]),
                **{f"cash_d{d}": phases[str(d)][0] - phases[str(d)][1] for d in PHASE_DAYS},
                "raj_sales_cash": raj_settlement["accepted_sales_cash_raj_opponent"][0],
                "opponent_sales_cash": raj_settlement["accepted_sales_cash_raj_opponent"][1],
                "raj_milk_sales": raj_settlement["accepted_sales_by_item_raj"].get("MILK", 0),
                "opponent_milk_sales": raj_settlement["accepted_sales_by_item_opponent"].get("MILK", 0),
                "raj_wool_sales": raj_settlement["accepted_sales_by_item_raj"].get("WOOL", 0),
                "opponent_wool_sales": raj_settlement["accepted_sales_by_item_opponent"].get("WOOL", 0),
                "raj_egg_sales": raj_settlement["accepted_sales_by_item_raj"].get("EGG", 0),
                "opponent_egg_sales": raj_settlement["accepted_sales_by_item_opponent"].get("EGG", 0),
                "raj_strawberry_sales": raj_settlement["accepted_sales_by_item_raj"].get("STRAWBERRY", 0),
                "opponent_strawberry_sales": raj_settlement["accepted_sales_by_item_opponent"].get("STRAWBERRY", 0),
                "raj_wheat_sales": raj_settlement["accepted_sales_by_item_raj"].get("WHEAT", 0),
                "opponent_wheat_sales": raj_settlement["accepted_sales_by_item_opponent"].get("WHEAT", 0),
                "raj_cows_d15": snaps["15"][0]["animals"].get("COW", 0),
                "opponent_cows_d15": snaps["15"][1]["animals"].get("COW", 0),
                "raj_sheep_d15": snaps["15"][0]["animals"].get("SHEEP", 0),
                "opponent_sheep_d15": snaps["15"][1]["animals"].get("SHEEP", 0),
                "cash_mismatches": sum(raj_settlement["cash_mismatches_by_seat"]),
            }
            writer.writerow(row)
    print(f"Analyzed {len(results)} replays; wrote {csv_path} and {json_path}")
    for game in results:
        print(
            f"{game['episode_id']} {game['outcome']} margin={game['margin']:+} "
            f"guard_fired={game['guard']['fired']} cash_audit_mismatches="
            f"{sum(game['settlement']['cash_mismatches_by_seat'])} loader="
            f"{game['loader_reproduction']['matched_actions']}/{game['loader_reproduction']['checked_actions']}"
        )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Replay audit for the frozen V77 spent-seed first screen."""
import ast
import csv
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

from kaggle_environments.envs.kaggriculture import kaggriculture as engine

ROOT = Path(__file__).resolve().parents[2]
RUN = Path(__file__).resolve().parent / "runs" / (sys.argv[1] if len(sys.argv) > 1 else "v77_runway_corrected_94700")
SOURCE = Path(__file__).resolve().parent / (sys.argv[2] if len(sys.argv) > 2 else "agent_v77.py")
SPEC = importlib.util.spec_from_file_location("v77_agent_audit", SOURCE)
agent = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(agent)

# Reuse the established exact-settlement reconstruction without executing its
# top-level elite-panel batch or changing its output artifact.
source = (ROOT / "experiments/v75_elite_cashflow/reconstruct.py").read_text()
tree = ast.parse(source)
nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in ("checkpoint", "reconstruct")]
namespace = {"__file__": str(ROOT / "experiments/v75_elite_cashflow/reconstruct.py"), "engine": engine}
exec("import copy, csv, json, hashlib\nfrom collections import Counter, defaultdict\nfrom pathlib import Path\nfrom types import SimpleNamespace", namespace)
exec(compile(ast.Module(body=nodes, type_ignores=[]), "reconstruct.py", "exec"), namespace)

rows = list(csv.DictReader((RUN / "games.csv").open()))
results = []
for row in rows:
    seat = int(row["candidate_seat"])
    path = RUN / "replays" / (row["game_id"] + ".json")
    exact = namespace["reconstruct"](path, seat, row["game_id"])
    game = json.loads(path.read_text())
    steps = game["steps"]
    land_events = []
    day_snapshots = {}
    first_three_land = None
    stranded = []
    missed_harvest_deadlines = Counter()
    gate_checks = []
    original_gate = agent._third_land_runway
    gate_value = None
    def capture_gate(state, stats):
        nonlocal_gate = original_gate(state, stats)
        gate_checks.append({"day": state["day"], "hour": state["hour"], **nonlocal_gate})
        return nonlocal_gate
    agent._third_land_runway = capture_gate
    agent._UNIT_GOALS.clear()
    for frame in range(1, len(steps)):
        prev = steps[frame - 1][seat]["observation"]
        now = steps[frame][seat]["observation"]
        action = steps[frame][seat].get("action") or {}
        before_tiles = prev["farms"][seat]["tiles"]
        after_tiles = now["farms"][seat]["tiles"]
        for y, line in enumerate(before_tiles):
            for x, tile in enumerate(line):
                if not isinstance(tile, dict) or tile.get("kind") != "PLANT" or tile.get("crop") not in ("WHEAT", "MELON"):
                    continue
                after = after_tiles[y][x]
                if (isinstance(after, dict) and after.get("kind") == "WEED"
                        and tile.get("yield_units", 0) > 0
                        and tile.get("max_lifespan_step", -1) >= 0
                        and frame >= tile["max_lifespan_step"]):
                    missed_harvest_deadlines[tile["crop"]] += 1
        if len(prev["farms"][seat].get("unlocked_quadrants", [])) == 2 and prev["day"] <= 18:
            agent._bridge_agent(prev)
        if any(order == ["BUY_LAND"] for order in action.get("market", [])):
            land_events.append({"day": prev["day"], "hour": prev["hour"], "cash_before": prev["farms"][seat]["money"],
                                "cash_after": now["farms"][seat]["money"], "hands_after": len(now["farms"][seat]["hands"]),
                                "lands_after": len(now["farms"][seat]["unlocked_quadrants"])})
        # The engine removes daily hires during the rollover. The last
        # in-day observation (hour 23) is the paid-hand checkpoint.
        if now["day"] == prev["day"] or frame == len(steps) - 1:
            farm = now["farms"][seat]
            day = now["day"]
            tiles = [t for line in farm["tiles"] for t in line if isinstance(t, dict)]
            shed = now["private"].get("shed", {})
            carried = Counter()
            for inventory in now["private"].get("inventories", []):
                for animal in ("COW", "SHEEP", "GOOSE"):
                    carried[animal] += inventory.get(animal, 0)
            live = Counter(t.get("animal") for t in tiles if "animal" in t)
            day_snapshots[str(day)] = {"cash": farm["money"], "hands": len(farm["hands"]), "lands": len(farm["unlocked_quadrants"]),
                                      "plants": dict(Counter(t.get("crop") for t in tiles if t.get("kind") == "PLANT")),
                                      "animals_placed": dict(live),
                                      "animals_shed": {key: shed.get(key, 0) for key in ("COW", "SHEEP", "GOOSE")},
                                      "animals_carried": dict(carried)}
            if first_three_land is None and len(farm["unlocked_quadrants"]) >= 3:
                first_three_land = day
            if any(shed.get(key, 0) + carried[key] for key in ("COW", "SHEEP", "GOOSE")):
                stranded.append(day)
    agent._third_land_runway = original_gate
    daily_sales = {int(day): sum(items["sales"].values()) for day, items in exact["daily"].items()}
    streak = longest = 0
    for day in range(10, 17):
        streak = streak + 1 if daily_sales.get(day, 0) == 0 else 0
        longest = max(longest, streak)
    three_land_days = [day for day in range(10, 17) if day_snapshots[str(day)]["lands"] >= 3]
    paid_hands_ok = (all(day_snapshots[str(day)]["hands"] >= 8 for day in three_land_days)
                     if three_land_days else None)
    first_gate = next((g for g in gate_checks if g["eligible"]), None)
    plant_window = [g for g in gate_checks if g["day"] <= 11]
    best_window_gate = max(plant_window, key=lambda g: g["cash_after"], default=None)
    result = {"game_id": row["game_id"], "seat": seat, "opponent": row["opponent"],
              "cash": float(row["candidate_final_coins"]), "opponent_cash": float(row["opponent_final_coins"]),
              "accepted_sales": sum(daily_sales.values()), "daily_sales_d10_16": {str(d): daily_sales.get(d, 0) for d in range(10, 17)},
              "zero_sales_streak_d10_16": longest, "paid_hands_ok": paid_hands_ok,
              "land_events": land_events, "first_three_land_day": first_three_land,
              "first_eligible_gate": first_gate, "best_plant_window_gate": best_window_gate,
              "three_land_days_d10_16": three_land_days, "day_snapshots": day_snapshots,
              "animal_shed_days": sorted(set(stranded)), "exact_settlement": exact["audit"],
              "missed_harvest_deadlines": dict(missed_harvest_deadlines),
              "replay_sha256": exact["replay_sha256"]}
    results.append(result)

out = RUN / "v77_audit.json"
out.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
for r in results:
    print(r["game_id"], "cash", r["cash"], "sales", r["accepted_sales"], "land", r["land_events"],
          "zero streak", r["zero_sales_streak_d10_16"], "hands ok", r["paid_hands_ok"],
          "settlement", r["exact_settlement"])
print(out)

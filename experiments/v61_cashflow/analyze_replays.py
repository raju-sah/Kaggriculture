"""Read-only economic/task audit for retained Kaggriculture replays."""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from kaggle_environments.envs.kaggriculture.kaggriculture import (
    ANIMALS, CROPS, LAND_PRICES, market_price,
)

MOVE = {"NORTH", "SOUTH", "EAST", "WEST"}
TASK = {"PLANT", "WATER", "HARVEST", "FEED", "CARE", "COLLECT_FERTILIZER",
        "FERTILIZE", "BUILD_COOP", "BUILD_PASTURE", "PLACE", "PICKUP", "DIG", "DROP"}


def _tile_counts(farm):
    crops, animals = Counter(), Counter()
    for row in farm.get("tiles", []):
        for tile in row:
            if isinstance(tile, dict):
                if tile.get("kind") == "PLANT": crops[tile.get("crop")] += 1
                if tile.get("animal"): animals[tile["animal"]] += 1
    return crops, animals


def _requested_cost(order, obs, hire_n):
    if not order: return 0.0, hire_n
    op = order[0]
    if op == "HIRE":
        from kaggle_environments.envs.kaggriculture.kaggriculture import _hire_cost
        mult = obs.get("configuration", {}).get("farmHandCostMult", 1)
        cost = _hire_cost(hire_n, mult)
        return float(cost), hire_n + 1
    if op == "BUY_LAND":
        i = max(0, len(obs["farms"][obs["player"]].get("unlocked_quadrants", [])) - 1)
        return float(LAND_PRICES[i]) if i < len(LAND_PRICES) else 0.0, hire_n
    if len(order) < 3: return 0.0, hire_n
    item, qty = order[1], max(0, int(order[2]))
    if op == "BUY_SEED": return float(CROPS.get(item, {}).get("seed", 0) * qty), hire_n
    if op == "BUY_ANIMAL": return float(ANIMALS.get(item, {}).get("cost", 0) * qty), hire_n
    if op == "BUY_PRODUCT":
        market = obs.get("market", {})
        inv = market.get("inventory", {}).get(item, 0)
        params = market.get("params")
        return float(sum(market_price(item, int(inv) - j - 1, params) for j in range(qty))), hire_n
    return 0.0, hire_n


def audit(path: Path, seat: int, max_day: int = 12):
    replay = json.loads(path.read_text())
    steps = replay["steps"]
    purchase_cost = defaultdict(Counter)
    action_counts = defaultdict(Counter)
    worker_stats = Counter()
    open_days = {}
    snapshots = {}
    first_market = None

    for i in range(len(steps)):
        obs = (steps[i][seat].get("observation") or {})
        day, hour = obs.get("day"), obs.get("hour")
        if day is None or day > max_day: continue
        farm = obs.get("farms", [{}] * (seat + 1))[seat]
        if hour == 23:
            crops, animals = _tile_counts(farm)
            snapshots[day] = {"cash": farm.get("money"), "hands": len(farm.get("hands", [])),
                              "quadrants": len(farm.get("unlocked_quadrants", [])),
                              "crops": dict(crops), "animals": dict(animals)}
        if i == 0: continue
        # Kaggle replay action at frame i is the response to frame i-1's observation.
        prev_state = steps[i - 1][seat]
        pre = prev_state.get("observation") or {}
        pre_day = pre.get("day")
        if pre_day is None or pre_day > max_day: continue
        action = steps[i][seat].get("action") or {}
        market_orders = action.get("market") or []
        farm_pre = pre.get("farms", [{}] * (seat + 1))[seat]
        hire_n = int(farm_pre.get("hires_today", 0))
        for order in market_orders:
            if not order: continue
            op = order[0]
            if first_market is None and pre_day == 0:
                first_market = market_orders
            cost, hire_n = _requested_cost(order, pre, hire_n)
            category = {"BUY_SEED": "seed", "BUY_PRODUCT": "feed/product",
                        "BUY_ANIMAL": "animal", "BUY_LAND": "land", "HIRE": "hire"}.get(op)
            if category: purchase_cost[pre_day][category] += cost

        next_obs = obs
        farm_post = farm
        positions = [farm_pre.get("farmer")] + list(farm_pre.get("hands", []))
        next_positions = [farm_post.get("farmer")] + list(farm_post.get("hands", []))
        unit_actions = [action.get("farmer") or ["PASS"]] + list(action.get("hands") or [])
        inventories_pre = (pre.get("private", {}).get("inventories") or [])
        inventories_post = (next_obs.get("private", {}).get("inventories") or [])
        tiles_pre = farm_pre.get("tiles", [])
        tiles_post = farm_post.get("tiles", [])
        for u, command in enumerate(unit_actions):
            verb = command[0] if command else "PASS"
            if u: worker_stats["turns"] += 1
            action_counts[pre_day][verb] += 1
            if u and verb in MOVE: worker_stats["move"] += 1
            elif u and verb in ("PASS", "WAIT"): worker_stats["pass"] += 1
            elif u and verb in TASK: worker_stats["task_attempts"] += 1
            if verb not in TASK or u >= len(positions) or positions[u] is None: continue
            pos = positions[u]
            x, y = pos
            before_tile = tiles_pre[y][x] if 0 <= y < len(tiles_pre) and 0 <= x < len(tiles_pre[y]) else None
            after_pos = next_positions[u] if u < len(next_positions) else pos
            ax, ay = after_pos
            after_tile = tiles_post[ay][ax] if 0 <= ay < len(tiles_post) and 0 <= ax < len(tiles_post[ay]) else None
            before_inv = inventories_pre[u] if u < len(inventories_pre) else {}
            after_inv = inventories_post[u] if u < len(inventories_post) else {}
            if u and (before_tile != after_tile or before_inv != after_inv):
                worker_stats["task_effects"] += 1

    return {"path": str(path), "seat": seat, "seed": (replay.get("info") or {}).get("seed"),
            "reward": (replay.get("rewards") or [None, None])[seat],
            "snapshots_day0_12": snapshots,
            "requested_purchase_cost_day0_12": {str(k): dict(v) for k, v in purchase_cost.items()},
            "action_counts_day0_12": {str(k): dict(v) for k, v in action_counts.items()},
            "first_day_market_orders": first_market,
            "hand_utilization": {"task_effects": worker_stats["task_effects"],
                                 "task_attempts": worker_stats["task_attempts"],
                                 "moves": worker_stats["move"], "passes": worker_stats["pass"],
                                 "hand_turns": worker_stats["turns"]}}


if __name__ == "__main__":
    out = []
    for arg in sys.argv[1:]:
        path, seat = arg.rsplit(":", 1)
        out.append(audit(Path(path), int(seat)))
    print(json.dumps(out, indent=2))

"""Original economy-manager prototype for simulator-based search.

The day-level manager sets a small portfolio target; a state-derived option
scheduler routes actors to current work. This file is research-only.
"""
from __future__ import annotations

from collections import Counter

# Compact CEM vector (all choices are observation-conditioned by feasibility).
PARAMS = {
    "crop_target": 8,
    "herd_target": 1,
    "staff_target": 3,
    "cash_reserve": 700,
    "wheat_reserve": 2
}
CROP = "WHEAT"
ANIMAL = "SHEEP"
ANIMAL_GOOD = "WOOL"


def _adjacent_shed_tiles(size):
    h = size // 2
    return [(h - 1, h - 1), (h, h - 1), (h - 1, h), (h, h)]


def _near_shed(pos, size):
    return tuple(pos) in set(_adjacent_shed_tiles(size))


def _move(src, dst):
    x, y = src
    tx, ty = dst
    dx, dy = tx - x, ty - y
    if dx or dy:
        if abs(dx) >= abs(dy) and dx:
            return ["EAST" if dx > 0 else "WEST"]
        return ["SOUTH" if dy > 0 else "NORTH"]
    return ["PASS"]


def _dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _owned_empty(board):
    return [(x, y) for y, row in enumerate(board) for x, tile in enumerate(row)
            if tile is None]


def _animal_tiles(board):
    return [(x, y, tile) for y, row in enumerate(board) for x, tile in enumerate(row)
            if isinstance(tile, dict) and "animal" in tile]


def _pastures(board):
    return [(x, y, tile) for y, row in enumerate(board) for x, tile in enumerate(row)
            if isinstance(tile, dict) and tile.get("kind") == "PASTURE"]


def _tasks(obs, farm, private, actors, board, params):
    day = int(obs.get("day", 0) or 0)
    size = len(board) or 10
    shed = private.get("shed") or {}
    invs = list(private.get("inventories") or [])
    invs.extend({} for _ in range(max(0, len(actors) - len(invs))))
    tasks = []
    animal_tiles = _animal_tiles(board)
    pasture_tiles = _pastures(board)
    sheep_held = sum(max(0, int(inv.get(ANIMAL, 0) or 0)) for inv in invs)
    sheep_stored = max(0, int(shed.get(ANIMAL, 0) or 0))
    sheep_live = sum(1 for _x, _y, tile in animal_tiles if tile.get("animal") == ANIMAL)
    empty = _owned_empty(board)

    # Per-day feed/production service outranks crop investment.
    for x, y, tile in animal_tiles:
        if tile.get("animal") == ANIMAL:
            if not tile.get("fed_today"):
                tasks.append((0, "FEED", (x, y), "WHEAT"))
            if int(tile.get("yield_units", 0) or 0) > 0:
                tasks.append((1, "HARVEST", (x, y), None))
            if tile.get("fertilizer_available"):
                tasks.append((5, "COLLECT_FERTILIZER", (x, y), None))
            if not tile.get("cared_today") and day < 26:
                tasks.append((6, "CARE", (x, y), None))

    # Place a purchased sheep before buying more. One matching pasture is enough
    # for the initial manager; the setpoint supports later population search.
    empty_pastures = [(x, y, tile) for x, y, tile in pasture_tiles if "animal" not in tile]
    if sheep_held:
        for x, y, _tile in empty_pastures:
            tasks.append((2, "PLACE", (x, y), ANIMAL))
            break
    elif sheep_stored and empty_pastures:
        tasks.append((2, "PICKUP", _adjacent_shed_tiles(size), ANIMAL))

    live_count = sum(1 for _x, _y, tile in animal_tiles if tile.get("animal") == ANIMAL)
    unmet = max(0, int(params["herd_target"]) - live_count - len(empty_pastures)
                - sheep_stored - sheep_held)
    if unmet and empty and day < 20:
        # Add at most one matching structure per step, keeping construction
        # scalable with the optimized herd setpoint without duplicating targets.
        occupied_targets = {target for _p, name, target, _arg in tasks if name == "BUILD_PASTURE"}
        available = [p for p in empty if p not in occupied_targets]
        if available:
            target = min(available, key=lambda p: (min(_dist(p, s) for s in _adjacent_shed_tiles(size)), p[1], p[0]))
            tasks.append((2, "BUILD_PASTURE", target, None))

    # Water every live plot daily; harvest only after a useful fraction of yield
    # is ready, preserving more simultaneous output and avoiding immature picks.
    crops = []
    for y, row in enumerate(board):
        for x, tile in enumerate(row):
            if not isinstance(tile, dict) or tile.get("kind") != "PLANT":
                continue
            crops.append(tile.get("crop"))
            if not tile.get("watered_today"):
                tasks.append((0, "WATER", (x, y), None))
            yield_n = int(tile.get("yield_units", 0) or 0)
            if yield_n >= 4 or (yield_n > 0 and day - int(tile.get("planted_day", day)) >= 4):
                tasks.append((1, "HARVEST", (x, y), None))
    crop_n = sum(c == CROP for c in crops)
    free_targets = [p for p in empty if not any(p == target for _prio, _name, target, _arg in tasks)]
    if day < 24 and crop_n < int(params["crop_target"]) and int((private.get("seeds") or {}).get(CROP, 0)) > 0:
        for p in free_targets[:max(0, int(params["crop_target"]) - crop_n)]:
            tasks.append((3, "PLANT", p, CROP))

    # Convert feed work to a shed pickup stage when the assigned actor lacks
    # wheat. PICKUP requires a shed-adjacent tile; movement onto LOCKED tiles is
    # legal, so shortest Manhattan movement is sufficient.
    feed_need = sum(1 for _x, _y, tile in animal_tiles
                    if tile.get("animal") == ANIMAL and not tile.get("fed_today"))
    feed_supply = max(0, int(shed.get("WHEAT", 0) or 0))
    for idx, inv in enumerate(invs):
        feed_supply += max(0, int(inv.get("WHEAT", 0) or 0))
    if feed_need and feed_supply < feed_need:
        pass  # market manager replenishes wheat; feed task waits for delivery.
    return sorted(tasks, key=lambda t: (t[0], t[1], t[2]))


def _task_action(task, pos, inv, private, farm, board, size):
    _priority, name, target, arg = task
    shed = private.get("shed") or {}
    if name in ("FEED", "PICKUP"):
        if name == "PICKUP":
            if not _near_shed(pos, size):
                target_tile = min(target, key=lambda p: (_dist(pos, p), p[1], p[0]))
                return _move(pos, target_tile)
            if int(shed.get(arg, 0) or 0) > 0:
                return ["PICKUP", arg, 1]
            return ["PASS"]
        if int(inv.get("WHEAT", 0) or 0) <= 0:
            if not _near_shed(pos, size):
                shed_pos = min(_adjacent_shed_tiles(size), key=lambda p: (_dist(pos, p), p[1], p[0]))
                return _move(pos, shed_pos)
            if int(shed.get("WHEAT", 0) or 0) > 0:
                return ["PICKUP", "WHEAT", 1]
            return ["PASS"]
        if tuple(pos) != tuple(target):
            return _move(pos, target)
        return ["FEED"]
    if name == "PLACE":
        if tuple(pos) != tuple(target):
            return _move(pos, target)
        return ["PLACE", arg]
    if tuple(pos) != tuple(target):
        return _move(pos, target)
    if name == "PLANT":
        if board[pos[1]][pos[0]] is None and int((private.get("seeds") or {}).get(arg, 0) or 0) > 0:
            return ["PLANT", arg]
        return ["PASS"]
    if name == "BUILD_PASTURE":
        return ["BUILD_PASTURE"] if board[pos[1]][pos[0]] is None else ["PASS"]
    if name == "WATER":
        tile = board[pos[1]][pos[0]]
        return ["WATER"] if isinstance(tile, dict) and tile.get("kind") == "PLANT" and not tile.get("watered_today") else ["PASS"]
    if name == "HARVEST":
        tile = board[pos[1]][pos[0]]
        return ["HARVEST"] if isinstance(tile, dict) and int(tile.get("yield_units", 0) or 0) > 0 else ["PASS"]
    if name == "CARE":
        tile = board[pos[1]][pos[0]]
        return ["CARE"] if isinstance(tile, dict) and "animal" in tile and not tile.get("cared_today") else ["PASS"]
    if name == "COLLECT_FERTILIZER":
        tile = board[pos[1]][pos[0]]
        return ["COLLECT_FERTILIZER"] if isinstance(tile, dict) and "animal" in tile and tile.get("fertilizer_available") else ["PASS"]
    return ["PASS"]


def _legal_fallback(action, obs, seat, actor, config):
    """Conservative engine precondition mask for emitted actor commands."""
    farms = obs.get("farms") or []
    if seat >= len(farms):
        return ["PASS"]
    farm = farms[seat]
    board = farm.get("tiles") or []
    pos_list = [farm.get("farmer", [0, 0]), *(farm.get("hands") or [])]
    pos = pos_list[actor] if actor < len(pos_list) else [0, 0]
    x, y = int(pos[0]), int(pos[1])
    size = len(board)
    private = obs.get("private") or {}
    invs = list(private.get("inventories") or [])
    inv = invs[actor] if actor < len(invs) else {}
    if not action or not isinstance(action, list):
        return ["PASS"]
    op = action[0]
    if op in ("NORTH", "SOUTH", "EAST", "WEST"):
        dxdy = {"NORTH": (0, -1), "SOUTH": (0, 1), "EAST": (1, 0), "WEST": (-1, 0)}[op]
        nx, ny = x + dxdy[0], y + dxdy[1]
        return action if 0 <= nx < size and 0 <= ny < size else ["PASS"]
    if not (0 <= y < size and 0 <= x < size):
        return ["PASS"]
    tile = board[y][x]
    if op == "PASS": return action
    if op == "WATER": return action if isinstance(tile, dict) and tile.get("kind") == "PLANT" and not tile.get("watered_today") else ["PASS"]
    if op == "HARVEST": return action if isinstance(tile, dict) and int(tile.get("yield_units", 0) or 0) > 0 else ["PASS"]
    if op == "FEED": return action if isinstance(tile, dict) and "animal" in tile and not tile.get("fed_today") and int(inv.get("WHEAT", 0) or 0) > 0 else ["PASS"]
    if op == "CARE": return action if isinstance(tile, dict) and "animal" in tile and not tile.get("cared_today") else ["PASS"]
    if op == "COLLECT_FERTILIZER": return action if isinstance(tile, dict) and "animal" in tile and tile.get("fertilizer_available") else ["PASS"]
    if op == "PLANT": return action if tile is None and int((private.get("seeds") or {}).get(action[1], 0) or 0) > 0 else ["PASS"]
    if op == "BUILD_PASTURE": return action if tile is None else ["PASS"]
    if op == "PICKUP":
        if not _near_shed(pos, size) or len(action) < 2: return ["PASS"]
        return action if int((private.get("shed") or {}).get(action[1], 0) or 0) > 0 else ["PASS"]
    if op == "PLACE":
        if len(action) < 2: return ["PASS"]
        if action[1] == ANIMAL:
            return action if isinstance(tile, dict) and tile.get("kind") == "PASTURE" and "animal" not in tile and int(inv.get(ANIMAL, 0) or 0) > 0 else ["PASS"]
    return ["PASS"]


def _manager_market(obs, farm, private, board, actors, params):
    day = int(obs.get("day", 0) or 0)
    hour = int(obs.get("hour", 0) or 0)
    money = float(farm.get("money", 0) or 0)
    shed = private.get("shed") or {}
    seeds = private.get("seeds") or {}
    size = len(board) or 10
    animals = _animal_tiles(board)
    live_sheep = sum(1 for _, _, tile in animals if tile.get("animal") == ANIMAL)
    sheep_stored = max(0, int(shed.get(ANIMAL, 0) or 0))
    sheep_carried = sum(max(0, int((inv or {}).get(ANIMAL, 0) or 0)) for inv in private.get("inventories", []))
    live_crop = sum(1 for row in board for tile in row if isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == CROP)
    empty_count = len(_owned_empty(board))
    planned_crop = min(int(params["crop_target"]), live_crop + int(seeds.get(CROP, 0) or 0))
    orders = []

    # Liquidate production but leave feed and seed capital reserves.
    feed_buffer = int(params["wheat_reserve"]) if live_sheep else 0
    wheat_in_hands = sum(max(0, int((inv or {}).get("WHEAT", 0) or 0)) for inv in private.get("inventories", []))
    for item, quantity in sorted(shed.items(), key=lambda kv: float((obs.get("market", {}).get("prices") or {}).get(kv[0], 0)), reverse=True):
        if item in ("SHEEP", "COW", "GOOSE") or int(quantity or 0) <= 0:
            continue
        reserve = max(0, feed_buffer - wheat_in_hands) if item == "WHEAT" else 0
        sale_n = max(0, int(quantity) - reserve)
        if sale_n:
            orders.append(["SELL", item, sale_n])

    # Re-form a small crew daily; hires are ephemeral and cost little initially.
    if hour == 0:
        active = len(actors) - 1
        target_staff = min(int(params["staff_target"]), max(0, empty_count // 3))
        if active < target_staff and money > int(params["cash_reserve"]) + 300:
            orders.extend([["HIRE"] for _ in range(min(target_staff - active, 7))])
        # Buy livestock once only after a pasture is ready or can be built, and
        # protect a real cash reserve. Current trial targets one sheep.
        if (live_sheep + sheep_stored + sheep_carried < int(params["herd_target"])
                and day >= 2 and day <= 18 and money > int(params["cash_reserve"]) + 1200
                and len(orders) < 8):
            orders.append(["BUY_ANIMAL", ANIMAL, 1])
        # Buy enough crop seeds to approach the acreage target without filling
        # the shed; planting consumes these directly from private seed storage.
        desired_seed = max(0, min(3, int(params["crop_target"]) - live_crop - int(seeds.get(CROP, 0) or 0)))
        if desired_seed and money > int(params["cash_reserve"]) + 200 and len(orders) < 8:
            orders.append(["BUY_SEED", CROP, desired_seed])
        # Wheat bought as product is feed, distinct from the private seed slot.
        if live_sheep and int(shed.get("WHEAT", 0) or 0) < 1 and money > int(params["cash_reserve"]) + 100 and len(orders) < 9:
            orders.append(["BUY_PRODUCT", "WHEAT", live_sheep + max(0, int(params["wheat_reserve"]) - int(shed.get("WHEAT", 0) or 0))])
    return orders[:10]


def agent(obs, configuration=None):
    farms = obs.get("farms") or []
    seat = int(obs.get("player", 0) or 0)
    if seat >= len(farms):
        return {"farmer": ["PASS"], "hands": [], "market": []}
    farm = farms[seat]
    private = obs.get("private") or {}
    board = farm.get("tiles") or []
    size = len(board) or 10
    positions = [farm.get("farmer", [0, 0]), *(farm.get("hands") or [])]
    invs = list(private.get("inventories") or [])
    invs.extend({} for _ in range(len(positions) - len(invs)))
    tasks = _tasks(obs, farm, private, positions, board, PARAMS)

    # Greedy one-task-per-unit matching keeps target work distinct and stable
    # by actor index; actor/item targets are reconstructed from current state.
    assigned = {}
    available = set(range(len(positions)))
    for task in tasks:
        prio, name, target, arg = task
        if not available:
            break
        if name in ("FEED", "WATER", "HARVEST"):
            eligible = []
            for actor in available:
                inv = invs[actor]
                if name == "FEED" and int(inv.get("WHEAT", 0) or 0) <= 0 and not int((private.get("shed") or {}).get("WHEAT", 0) or 0):
                    continue
                eligible.append(actor)
            if not eligible and name == "FEED":
                eligible = list(available)
        else:
            eligible = list(available)
        actor = min(eligible or list(available), key=lambda i: (_dist(positions[i], target[0]) if isinstance(target, list) and target and isinstance(target[0], tuple) else _dist(positions[i], target), i))
        assigned[actor] = task
        available.remove(actor)
    actions = []
    for actor, pos in enumerate(positions):
        task = assigned.get(actor)
        if task is None:
            action = ["PASS"]
        else:
            action = _task_action(task, pos, invs[actor], private, farm, board, size)
        actions.append(_legal_fallback(action, obs, seat, actor, configuration))

    return {
        "farmer": actions[0],
        "hands": actions[1:],
        "market": _manager_market(obs, farm, private, board, positions, PARAMS),
    }

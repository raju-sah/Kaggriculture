"""Audit worker throughput and crop outcomes in the frozen V69 paired panel."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PANELS = {
    "V67": [
        ROOT / "experiments/v69_dispatch/seed94700_vs_v67/replays",
        ROOT / "experiments/v69_dispatch/seeds92802_92804_vs_v67/replays",
    ],
    "V56": [ROOT / "experiments/v69_dispatch/panel_vs_v56/replays"],
}
MOVES = {"NORTH", "SOUTH", "EAST", "WEST"}


def _crop_count(farm: dict, crop: str) -> int:
    return sum(
        1
        for row in farm.get("tiles", [])
        for tile in row
        if isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == crop
    )


def analyze(path: Path, candidate_seat: int) -> dict:
    replay = json.loads(path.read_text())
    steps = replay["steps"]
    hand_prod = hand_moves = 0
    care_done: dict[int, set[tuple[int, int]]] = defaultdict(set)
    feed_done: dict[int, set[tuple[int, int]]] = defaultdict(set)
    care_due: dict[int, set[tuple[int, int]]] = defaultdict(set)
    feed_due: dict[int, set[tuple[int, int]]] = defaultdict(set)
    escape_count = 0
    crop_harvest_units = Counter()
    crop_harvest_actions = Counter()
    crop_decay_units = Counter()
    accepted_sales_units = Counter()
    attempted_sales_units = Counter()
    strawberry_water = strawberry_harvests = 0
    strawberry_samples: dict[int, dict[int, int]] = defaultdict(dict)
    strawberry_alive_hours = 0
    ripe_crop_tile_days: dict[str, set[tuple[int, int, int]]] = defaultdict(set)
    harvested_crop_tiles_by_day: dict[str, set[tuple[int, int, int]]] = defaultdict(set)
    productive_by_op = Counter()

    # Replay action i follows observation i-1; observation i contains its effects.
    for i in range(1, len(steps)):
        prior = steps[i - 1][candidate_seat]["observation"]
        post = steps[i][candidate_seat]["observation"]
        action = steps[i][candidate_seat].get("action") or {}
        day = int(prior.get("day", 0))
        farm = prior["farms"][candidate_seat]
        after_farm = post["farms"][candidate_seat]
        positions = [farm.get("farmer", [0, 0]), *farm.get("hands", [])]
        unit_actions = [action.get("farmer") or ["PASS"], *(action.get("hands") or [])]
        pre_inv = (prior.get("private") or {}).get("inventories") or []
        post_inv = (post.get("private") or {}).get("inventories") or []

        # Count animal days due for basic care/feed and task completions.
        for y, row in enumerate(farm.get("tiles", [])):
            for x, tile in enumerate(row):
                if isinstance(tile, dict) and "animal" in tile:
                    p = (x, y)
                    if not tile.get("fed_today", False):
                        feed_due[day].add(p)
                    if not tile.get("cared_today", False):
                        care_due[day].add(p)

        for ui, unit_action in enumerate(unit_actions):
            if not unit_action:
                continue
            op = str(unit_action[0])
            if ui > 0:
                if op in MOVES:
                    hand_moves += 1
                elif op != "PASS":
                    hand_prod += 1
                    productive_by_op[op] += 1
            if ui >= len(positions):
                continue
            x, y = map(int, positions[ui])
            prior_tile = farm["tiles"][y][x]
            post_tile = after_farm["tiles"][y][x]
            if isinstance(prior_tile, dict) and prior_tile.get("kind") == "PLANT":
                crop = str(prior_tile.get("crop", ""))
                if crop == "STRAWBERRY" and op == "WATER" and isinstance(post_tile, dict) and post_tile.get("watered_today"):
                    strawberry_water += 1
                if crop == "STRAWBERRY" and op == "HARVEST" and prior_tile.get("yield_units", 0) > 0:
                    strawberry_harvests += 1
                if op == "HARVEST" and prior_tile.get("yield_units", 0) > 0:
                    crop_harvest_actions[crop] += 1
                    # HARVEST transfers the whole tile yield to the carrier.
                    # Use the engine's pre-action tile quantity; inventory
                    # deltas can be masked by an automatic inventory cap.
                    crop_harvest_units[crop] += int(prior_tile.get("yield_units", 0))
                    harvested_crop_tiles_by_day[crop].add((day, x, y))
                if (
                    isinstance(post_tile, dict)
                    and post_tile.get("kind") == "WEED"
                    and prior_tile.get("yield_units", 0) > 0
                ):
                    crop_decay_units[crop] += int(prior_tile.get("yield_units", 0))
            elif isinstance(prior_tile, dict) and "animal" in prior_tile:
                p = (x, y)
                if op == "FEED" and isinstance(post_tile, dict) and post_tile.get("fed_today"):
                    feed_done[day].add(p)
                if op == "CARE" and isinstance(post_tile, dict) and post_tile.get("cared_today"):
                    care_done[day].add(p)
                if op == "HARVEST" and prior_tile.get("yield_units", 0) > 0:
                    product = {"COW": "MILK", "SHEEP": "WOOL", "GOOSE": "EGG"}.get(prior_tile.get("animal"))
                    if product:
                        crop_harvest_units[product] += int(prior_tile.get("yield_units", 0))
                        crop_harvest_actions[product] += 1

        # Approximate accepted strawberry sale units exactly from shed stock
        # plus same-turn DROP deposits; SELL is order-index limited to ten.
        market_orders = action.get("market") or []
        if candidate_seat < 2 and (prior.get("private") or {}).get("shed"):
            private = prior["private"]
            shed = private.get("shed", {}) or {}
            dropped = Counter()
            for ui, unit_action in enumerate(unit_actions):
                if unit_action and unit_action[0] == "DROP" and ui < len(pre_inv):
                    dropped.update({item: int(qty) for item, qty in pre_inv[ui].items() if int(qty) > 0})
            available = Counter({item: int(qty) for item, qty in shed.items() if int(qty) > 0})
            available.update(dropped)
            for order_index, order in enumerate(market_orders[:10]):
                if order and len(order) >= 3 and order[0] == "SELL":
                    item = str(order[1])
                    requested = max(0, int(order[2]))
                    attempted_sales_units[item] += requested
                    accepted = min(available[item], requested)
                    accepted_sales_units[item] += accepted
                    available[item] -= accepted

        # Measure animal escapes from their public board transition.
        for y, row in enumerate(farm.get("tiles", [])):
            for x, tile in enumerate(row):
                if isinstance(tile, dict) and "animal" in tile:
                    after = after_farm["tiles"][y][x]
                    if not (isinstance(after, dict) and "animal" in after):
                        escape_count += 1

        # Day-level snapshots and ripe tile-days, deduplicated by position.
        for crop in ("STRAWBERRY", "WHEAT", "MELON"):
            for y, row in enumerate(farm.get("tiles", [])):
                for x, tile in enumerate(row):
                    if not isinstance(tile, dict) or tile.get("kind") != "PLANT" or tile.get("crop") != crop:
                        continue
                    if tile.get("yield_units", 0) > 0:
                        ripe_crop_tile_days[crop].add((day, x, y))
        if post.get("hour", 0) == 0:
            strawberry_samples[day] = {
                "strawberry": _crop_count(after_farm, "STRAWBERRY"),
                "wheat": _crop_count(after_farm, "WHEAT"),
                "melon": _crop_count(after_farm, "MELON"),
            }
        strawberry_alive_hours += _crop_count(farm, "STRAWBERRY")

    ripe_missed = {}
    for crop in ripe_crop_tile_days:
        ripe_missed[crop] = len(ripe_crop_tile_days[crop] - harvested_crop_tiles_by_day[crop])

    care_due_total = sum(len(v) for v in care_due.values())
    feed_due_total = sum(len(v) for v in feed_due.values())
    care_done_total = sum(len(v) for v in care_done.values())
    feed_done_total = sum(len(v) for v in feed_done.values())
    return {
        "hands_productive_actions": hand_prod,
        "hands_move_actions": hand_moves,
        "productive_share_of_nonpass_actions": round(hand_prod / max(1, hand_prod + hand_moves), 4),
        "productive_by_op": dict(productive_by_op),
        "care_due_animal_days": care_due_total,
        "care_served_animal_days": care_done_total,
        "feed_due_animal_days": feed_due_total,
        "feed_served_animal_days": feed_done_total,
        "animal_escapes": escape_count,
        "crop_harvest_actions": dict(crop_harvest_actions),
        "harvested_units": dict(crop_harvest_units),
        "crop_decay_yield_units": dict(crop_decay_units),
        "ripe_crop_tile_days": {k: len(v) for k, v in ripe_crop_tile_days.items()},
        "unharvested_ripe_crop_tile_days": ripe_missed,
        "strawberry_water_actions": strawberry_water,
        "strawberry_harvest_actions": strawberry_harvests,
        "accepted_sales_units": dict(accepted_sales_units),
        "attempted_sales_units": dict(attempted_sales_units),
        "accepted_strawberry_sales_units": accepted_sales_units["STRAWBERRY"],
        "attempted_strawberry_sales_units": attempted_sales_units["STRAWBERRY"],
        "strawberry_live_hours": strawberry_alive_hours,
        "strawberry_counts_by_day": dict(sorted(strawberry_samples.items())),
    }


def main() -> None:
    output = {"panels": {}}
    for opponent, folders in PANELS.items():
        for folder in folders:
            if not folder.exists():
                continue
            for replay_path in sorted(folder.glob("*.json")):
                game_path = folder.parent / "games" / replay_path.name
                if not game_path.exists():
                    continue
                game = json.loads(game_path.read_text())
                seat = int(game["candidate_seat"])
                key = f"{opponent}/{game['seed']}/{seat}"
                output["panels"][key] = {
                    "opponent": opponent,
                    "seed": game["seed"],
                    "candidate_seat": seat,
                    "final_candidate_cash": game["final_coins"][seat],
                    "final_opponent_cash": game["final_coins"][1 - seat],
                    "margin": game["final_coins"][seat] - game["final_coins"][1 - seat],
                    "candidate_metrics": analyze(replay_path, seat),
                    "opponent_metrics": analyze(replay_path, 1 - seat),
                }
    target = ROOT / "experiments/v69_dispatch/panel_metrics.json"
    target.write_text(json.dumps(output, indent=2) + "\n")
    print(target)


if __name__ == "__main__":
    main()

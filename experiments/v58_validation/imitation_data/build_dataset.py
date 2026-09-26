#!/usr/bin/env python3
"""Build grouped observation-only actor/market imitation rows from replay JSON.

Raw replay files are read in place and are not copied into this directory.
Episode IDs/seeds and provenance go only in the sidecar manifest, never features.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ELITE_NAMES = {"Boey", "DSM", "DECEM", "M & M & P & Q", "Unknown Mother-Goose", "Vadim Vasilenko"}
ELITE_DIR = ROOT / "experiments/v58_elite/replays"
PUBLIC_REPLAY_DIR = ROOT / "experiments/v58_imitation/replays"
PUBLIC_MANIFEST = ROOT / "experiments/v58_imitation/public_episode_manifest.json"
RESET_DIRS = [
    ROOT / "experiments/runs/v58_validation_baseline/replays",
    ROOT / "experiments/v57_broad/diagnostics/reset/replays",
]
SHOP_GOODS = {
    "BAKERY": ("EGG", "WHEAT"), "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"), "YARN_STORE": ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"), "PET_CAFE": ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}
CROPS = ("WHEAT", "CARROT", "MELON", "TOMATO", "STRAWBERRY")
ANIMALS = ("COW", "SHEEP", "GOOSE")
FEATURE_PRICE_BASES = {"WHEAT": 25, "CARROT": 35, "MELON": 250, "TOMATO": 100,
                       "STRAWBERRY": 120, "MILK": 160, "WOOL": 200, "EGG": 50,
                       "FERTILIZER": 100}


def _bin(n: float, edges: tuple[int, ...]) -> str:
    for i, edge in enumerate(edges):
        if n < edge:
            return str(i)
    return str(len(edges))


def features(obs: dict, seat: int, actor: int | None) -> dict:
    farms = obs.get("farms") or []
    farm = farms[seat] if seat < len(farms) else {}
    priv = obs.get("private") or {}
    tiles = farm.get("tiles") or []
    hands = farm.get("hands") or []
    actor_positions = [farm.get("farmer", [0, 0]), *hands]
    invs = priv.get("inventories") or []
    board_n = max(1, len(tiles))
    counts = Counter()
    crops = Counter()
    animals = Counter()
    for row in tiles:
        for tile in row:
            if isinstance(tile, dict):
                counts[tile.get("kind", "UNKNOWN")] += 1
                crops[tile.get("crop", "")] += 1
                animals[tile.get("animal", "")] += 1
    money = float(farm.get("money", 0) or 0)
    day = int(obs.get("day", 0) or 0)
    hour = int(obs.get("hour", 0) or 0)
    shops = (obs.get("town") or {}).get("unlocked_shops") or []
    shop_need = Counter(g for shop in shops for g in SHOP_GOODS.get(shop, ()))
    market_prices = (obs.get("market") or {}).get("prices") or {}
    shed = priv.get("shed") or {}
    seedbag = priv.get("seeds") or {}
    x, y = actor_positions[actor] if actor is not None and actor < len(actor_positions) else (0, 0)
    tile = tiles[y][x] if y < len(tiles) and x < len(tiles[y]) else None
    inv = invs[actor] if actor is not None and actor < len(invs) else {}
    h = board_n // 2
    shed_tiles = [(h - 1, h - 1), (h, h - 1), (h - 1, h), (h, h)]
    d_shed = min((abs(x - sx) + abs(y - sy) for sx, sy in shed_tiles), default=0)
    targets = {"ripe_crop": [], "thirsty_crop": [], "unfed_animal": [], "open_pasture": []}
    for ty, row in enumerate(tiles):
        for tx, candidate in enumerate(row):
            if not isinstance(candidate, dict):
                continue
            if candidate.get("kind") == "PLANT":
                if int(candidate.get("yield_units", 0) or 0) > 0:
                    targets["ripe_crop"].append((tx, ty))
                if not candidate.get("watered_today", False):
                    targets["thirsty_crop"].append((tx, ty))
            if candidate.get("animal") and not candidate.get("fed_today", False):
                targets["unfed_animal"].append((tx, ty))
            if candidate.get("kind") == "PASTURE" and not candidate.get("animal"):
                targets["open_pasture"].append((tx, ty))
    def target_distance(points):
        if not points:
            return "none"
        dist = min(abs(x - tx) + abs(y - ty) for tx, ty in points)
        return _bin(dist, (0, 1, 2, 3, 5, 8, 12))
    def target_delta(points, axis):
        if not points:
            return "none"
        tx, ty = min(points, key=lambda p: (abs(x - p[0]) + abs(y - p[1]), p[1], p[0]))
        delta = (tx - x) if axis == "x" else (ty - y)
        sign = "w" if delta < 0 and axis == "x" else "n" if delta < 0 else "e" if axis == "x" and delta > 0 else "s" if delta > 0 else "here"
        return sign + _bin(abs(delta), (1, 2, 4, 8))
    neighbor_tiles = []
    for ny in range(max(0, y - 1), min(len(tiles), y + 2)):
        for nx in range(max(0, x - 1), min(len(tiles[ny]), x + 2)):
            if (nx, ny) != (x, y):
                neighbor_tiles.append(tiles[ny][nx])
    neighbor_counts = Counter(t.get("kind", "UNKNOWN") for t in neighbor_tiles if isinstance(t, dict))
    neighbor_crops = Counter(t.get("crop", "UNKNOWN") for t in neighbor_tiles if isinstance(t, dict) and t.get("kind") == "PLANT")
    neighbor_animals = Counter(t.get("animal", "UNKNOWN") for t in neighbor_tiles if isinstance(t, dict) and t.get("animal"))
    # No seed, episode id, exact step, or exact day/hour is included.
    out = {
        "decision": "actor" if actor is not None else "market",
        "phase": "early" if day < 5 else "growth" if day < 12 else "production" if day < 22 else "late",
        "daypart": "dawn" if hour < 6 else "day" if hour < 16 else "evening",
        "current_day": str(day),
        "current_hour": str(hour),
        "money_bin": _bin(money, (500, 1500, 3500, 7000, 15000, 40000)),
        "hand_count": _bin(len(hands), (1, 3, 5, 8, 12)),
        "land_count": str(min(4, len(farm.get("unlocked_quadrants") or []))),
        "plant_count": _bin(counts["PLANT"], (1, 4, 8, 16, 30)),
        "pasture_count": _bin(counts["PASTURE"], (1, 3, 6)),
        "coop_count": _bin(counts["COOP"], (1, 3, 6)),
        "cow_count": _bin(animals["COW"], (1, 3, 6, 10)),
        "sheep_count": _bin(animals["SHEEP"], (1, 3, 6, 10)),
        "goose_count": _bin(animals["GOOSE"], (1, 3, 6, 10)),
        "shop_count": _bin(len(shops), (1, 3, 6, 10)),
        "shed_wheat": _bin(float(shed.get("WHEAT", 0) or 0), (1, 4, 10, 20, 40)),
        "wheat_seed": _bin(float(seedbag.get("WHEAT", 0) or 0), (1, 3, 6, 12)),
    }
    for crop in CROPS:
        out[f"crop_{crop.lower()}_count"] = _bin(crops[crop], (1, 3, 6, 12))
        out[f"demand_{crop.lower()}_shops"] = _bin(shop_need[crop], (1, 3, 6))
        base = FEATURE_PRICE_BASES[crop]
        out[f"price_{crop.lower()}"] = _bin(float(market_prices.get(crop, base) or base) / base, (0.6, 0.9, 1.2, 1.6, 2.5))
        out[f"seed_{crop.lower()}_count"] = _bin(float(seedbag.get(crop, 0) or 0), (1, 3, 6, 12))
    for animal, item in (("COW", "MILK"), ("SHEEP", "WOOL"), ("GOOSE", "EGG")):
        base = FEATURE_PRICE_BASES[item]
        out[f"price_{item.lower()}"] = _bin(float(market_prices.get(item, base) or base) / base, (0.6, 0.9, 1.2, 1.6, 2.5))
        out[f"demand_{item.lower()}_shops"] = _bin(shop_need[item], (1, 3, 6))
    base = FEATURE_PRICE_BASES["FERTILIZER"]
    out["price_fertilizer"] = _bin(float(market_prices.get("FERTILIZER", base) or base) / base, (0.6, 0.9, 1.2, 1.6, 2.5))
    if actor is not None:
        out.update({
            "actor_role": "farmer" if actor == 0 else "hand",
            "pos_x": str(x),
            "pos_y": str(y),
            "hands_distance_bin": _bin(d_shed, (1, 3, 6, 10, 16)),
            "dist_ripe_crop": target_distance(targets["ripe_crop"]),
            "rel_ripe_crop_dx": target_delta(targets["ripe_crop"], "x"),
            "rel_ripe_crop_dy": target_delta(targets["ripe_crop"], "y"),
            "dist_thirsty_crop": target_distance(targets["thirsty_crop"]),
            "rel_thirsty_crop_dx": target_delta(targets["thirsty_crop"], "x"),
            "rel_thirsty_crop_dy": target_delta(targets["thirsty_crop"], "y"),
            "dist_shed": target_distance(shed_tiles),
            "rel_shed_dx": target_delta(shed_tiles, "x"),
            "rel_shed_dy": target_delta(shed_tiles, "y"),
            "dist_unfed_animal": target_distance(targets["unfed_animal"]),
            "rel_unfed_animal_dx": target_delta(targets["unfed_animal"], "x"),
            "rel_unfed_animal_dy": target_delta(targets["unfed_animal"], "y"),
            "dist_open_pasture": target_distance(targets["open_pasture"]),
            "rel_open_pasture_dx": target_delta(targets["open_pasture"], "x"),
            "rel_open_pasture_dy": target_delta(targets["open_pasture"], "y"),
            "ripe_crop_count": _bin(len(targets["ripe_crop"]), (1, 3, 6, 12, 24)),
            "thirsty_crop_count": _bin(len(targets["thirsty_crop"]), (1, 3, 6, 12, 24)),
            "unfed_animal_count": _bin(len(targets["unfed_animal"]), (1, 3, 6, 12)),
            "open_pasture_count": _bin(len(targets["open_pasture"]), (1, 3, 6)),
            "board_zone": f"{int(x >= h)}{int(y >= h)}",
            "neighbor_plant_count": _bin(neighbor_counts["PLANT"], (1, 3, 5)),
            "neighbor_pasture_count": _bin(neighbor_counts["PASTURE"], (1, 3, 5)),
            "neighbor_coop_count": _bin(neighbor_counts["COOP"], (1, 3, 5)),
            "neighbor_cow_count": _bin(neighbor_animals["COW"], (1, 3, 5)),
            "neighbor_sheep_count": _bin(neighbor_animals["SHEEP"], (1, 3, 5)),
            "neighbor_goose_count": _bin(neighbor_animals["GOOSE"], (1, 3, 5)),
            "neighbor_wheat_count": _bin(neighbor_crops["WHEAT"], (1, 3, 5)),
            "neighbor_strawberry_count": _bin(neighbor_crops["STRAWBERRY"], (1, 3, 5)),
            "move_n_blocked": str(y == 0 or tiles[y - 1][x] == "LOCKED"),
            "move_s_blocked": str(y + 1 >= len(tiles) or tiles[y + 1][x] == "LOCKED"),
            "move_w_blocked": str(x == 0 or tiles[y][x - 1] == "LOCKED"),
            "move_e_blocked": str(x + 1 >= len(tiles[y]) or tiles[y][x + 1] == "LOCKED"),
            "tile_kind": tile.get("kind", "NONE") if isinstance(tile, dict) else "NONE",
            "tile_crop": tile.get("crop", "NONE") if isinstance(tile, dict) else "NONE",
            "tile_animal": tile.get("animal", "NONE") if isinstance(tile, dict) else "NONE",
            "tile_wet": str(bool(tile.get("watered_today", tile.get("watered", tile.get("wet", False))))) if isinstance(tile, dict) else "false",
            "tile_ready": str(bool(tile.get("harvestable", tile.get("ready", False)))) if isinstance(tile, dict) else "false",
            "tile_fed": str(bool(tile.get("fed_today", False))) if isinstance(tile, dict) and tile.get("animal") else "na",
            "tile_yield_bin": _bin(int(tile.get("yield_units", 0) or 0), (1, 2, 4, 8)) if isinstance(tile, dict) else "0",
            "tile_fertilizer_available": str(bool(tile.get("fertilizer_available", False))) if isinstance(tile, dict) else "false",
            "tile_cared_today": str(bool(tile.get("cared_today", False))) if isinstance(tile, dict) and tile.get("animal") else "na",
            "at_shed": str((x, y) in shed_tiles),
            "inventory_primary": max(inv, key=lambda k: int(inv.get(k, 0) or 0)) if inv else "NONE",
            "inventory_load_bin": _bin(sum(int(v or 0) for v in inv.values()), (1, 2, 4, 8)),
            "inventory_wheat_bin": _bin(int(inv.get("WHEAT", 0) or 0), (1, 2, 4)),
            "inventory_fertilizer_bin": _bin(int(inv.get("FERTILIZER", 0) or 0), (1, 2, 4)),
            "inventory_animal": next((a for a in ANIMALS if int(inv.get(a, 0) or 0) > 0), "NONE"),
            "shed_load_bin": _bin(sum(int(v or 0) for v in shed.values()), (1, 10, 30, 60)),
        })
    return out


def _action_group(action: dict, seat: int) -> list[list]:
    group = action.get("farmer") if seat == 0 else action.get("hands")
    if seat == 0:
        return [group] if isinstance(group, list) else []
    return group if isinstance(group, list) else []


def task_label(op: str, args: list, obs: dict, seat: int, actor: int) -> str:
    farm = (obs.get("farms") or [{}] * (seat + 1))[seat]
    pos = [farm.get("farmer", [0, 0]), *(farm.get("hands") or [])]
    x, y = pos[actor] if actor < len(pos) else (0, 0)
    tiles = farm.get("tiles") or []
    tile = tiles[y][x] if y < len(tiles) and x < len(tiles[y]) else None
    if op in ("PASS", "WAIT"): return "IDLE"
    if op in ("NORTH", "SOUTH", "EAST", "WEST"): return "MOVE"
    if op == "HARVEST": return "HARVEST_ANIMAL" if isinstance(tile, dict) and tile.get("animal") else "HARVEST_CROP"
    if op == "PLANT": return "PLANT_" + (str(args[0]) if args else "UNKNOWN")
    if op == "WATER": return "WATER_CROP"
    if op == "DIG": return "CLEAR_WEED" if isinstance(tile, dict) and tile.get("kind") == "WEED" else "DIG"
    if op == "FEED": return "FEED_ANIMAL"
    if op == "CARE": return "CARE_ANIMAL"
    if op == "PICKUP": return "PICKUP_" + (str(args[0]) if args else "ITEM")
    if op == "PLACE": return "PLACE_" + (str(args[0]) if args else "ANIMAL")
    if op == "DROP": return "DROP_INVENTORY"
    if op == "COLLECT_FERTILIZER": return "COLLECT_FERTILIZER"
    if op.startswith("BUILD_"): return op
    return op


def _sources() -> list[tuple[Path, str, int | None]]:
    src: list[tuple[Path, str, int | None]] = []
    for path in sorted(ELITE_DIR.glob("*replay*.json")):
        src.append((path, "public_elite", None))
    manifest_rows = {}
    if PUBLIC_MANIFEST.exists():
        manifest_rows = {str(row["episode_id"]): row
                         for row in json.loads(PUBLIC_MANIFEST.read_text()).get("selected", [])}
    for path in sorted(PUBLIC_REPLAY_DIR.glob("*replay*.json")):
        try:
            episode_id = path.name.split("episode-", 1)[1].split("-replay", 1)[0]
            record = manifest_rows.get(episode_id, {})
            seats = record.get("elite_seats") or ([record["elite_seat"]] if "elite_seat" in record else [None])
        except (IndexError, ValueError):
            seats = [None]
        for seat in seats:
            src.append((path, "public_elite", seat))
    for directory in RESET_DIRS:
        for path in sorted(directory.glob("*.json")):
            # Tournament artifact suffix says candidate was A (seat 0) or B (seat 1).
            seat = 0 if "-ab-" in path.name else 1 if "-ba-" in path.name else None
            if seat is not None:
                src.append((path, "reset_candidate", seat))
    return src


def _read_source(path: Path, family: str, preset_seat: int | None) -> tuple[dict, int, str]:
    replay = json.loads(path.read_text())
    source_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    names = (replay.get("info") or {}).get("TeamNames") or (replay.get("info") or {}).get("Agents") or []
    if family == "public_elite":
        episode_id = str((replay.get("info") or {}).get("EpisodeId") or replay.get("id") or path.stem)
        if PUBLIC_MANIFEST.exists():
            manifest = json.loads(PUBLIC_MANIFEST.read_text())
            selected = {str(item["episode_id"]): item for item in manifest.get("selected", [])}
        else:
            selected = {}
        record = selected.get(episode_id)
        if record:
            if source_hash != record.get("replay_sha256"):
                raise ValueError(f"public replay hash disagrees with episode manifest: {path}")
            seat = int(preset_seat if preset_seat is not None else record["elite_seat"])
            if seat not in (record.get("elite_seats") or [record["elite_seat"]]):
                raise ValueError(f"requested seat is not elite according to manifest: {path}, seat={seat}")
            participant = names[seat]
            label = participant.get("Name") if isinstance(participant, dict) else participant
            return replay, seat, str(label)
        if not isinstance(names, list): raise ValueError(f"missing participants in {path}")
        seat = next((i for i, name in enumerate(names)
                     if (name.get("Name") if isinstance(name, dict) else name) in ELITE_NAMES), None)
        if seat is None: raise ValueError(f"no recognized public elite seat in {path}: {names!r}")
        label = names[seat].get("Name") if isinstance(names[seat], dict) else names[seat]
    else:
        seat = int(preset_seat)
        label = "v57_reset_candidate"
    return replay, seat, str(label)


def _assign_splits(manifests: list[dict]) -> None:
    # Episode-grouped 20% holdout within source family. This does not use seed,
    # score, action rows, or episode order to choose a held-out example.
    by_family = {}
    for m in manifests:
        by_family.setdefault(m["source_family"], []).append(m)
    for family, items in by_family.items():
        items.sort(key=lambda m: hashlib.sha256((family + ":" + m["episode_id"]).encode()).hexdigest())
        n_hold = max(1, round(len(items) * 0.2)) if len(items) > 1 else 0
        held = {m["episode_id"] for m in items[-n_hold:]} if n_hold else set()
        for m in items:
            m["split"] = "heldout" if m["episode_id"] in held else "train"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    sources = _sources()
    manifest_rows = []
    seen = set()
    for path, family, preset in sources:
        replay, seat, player = _read_source(path, family, preset)
        info = replay.get("info") or {}
        episode_id = str(info.get("EpisodeId") or replay.get("id") or path.stem)
        group_key = (episode_id, seat)
        if group_key in seen:
            continue
        seen.add(group_key)
        source_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest_rows.append({"episode_id": episode_id, "source_family": family,
            "source_path": str(path.relative_to(ROOT)), "source_sha256": source_hash,
            "selected_player": str(player), "selected_seat": seat,
            "episode_seed": info.get("seed"),
            "terminal_reward": (replay.get("rewards") or [None, None])[seat],
            "_path": path})
        del replay
    if len(manifest_rows) < 3:
        raise SystemExit(f"only {len(manifest_rows)} unique replay episodes found")
    _assign_splits(manifest_rows)
    split_by_group = {(m["episode_id"], m["selected_seat"]): m["split"] for m in manifest_rows}
    # Keep only one episode-level manifest entry per source/player, and drop private paths from output.
    manifests = [{k: v for k, v in m.items() if not k.startswith("_")} for m in manifest_rows]
    open_files = {}
    open_groups = {}
    for split in ("train", "heldout"):
        open_files[split] = gzip.open(args.out_dir / f"{split}.jsonl.gz", "wt", encoding="utf-8")
        open_groups[split] = gzip.open(args.out_dir / f"{split}_row_groups.jsonl.gz", "wt", encoding="utf-8")
    row_count = Counter()
    group_count = Counter()
    actor_classes = {"train": Counter(), "heldout": Counter()}
    task_classes = {"train": Counter(), "heldout": Counter()}
    market_classes = {"train": Counter(), "heldout": Counter()}
    for manifest in manifest_rows:
        replay, seat, player = _read_source(manifest["_path"], manifest["source_family"], manifest["selected_seat"])
        eid = manifest["episode_id"]
        split = split_by_group[(eid, seat)]
        steps = replay.get("steps") or []
        for t in range(1, len(steps)):
            before = steps[t - 1][seat]
            after = steps[t][seat]
            obs = before.get("observation") or {}
            action = after.get("action") or {}
            if not obs:
                continue
            actor_actions = [action.get("farmer") or ["PASS"], *(action.get("hands") or [])]
            for actor, actor_action in enumerate(actor_actions):
                if not isinstance(actor_action, list) or not actor_action:
                    continue
                op = str(actor_action[0])
                args_label = str(actor_action[1]) if len(actor_action) > 1 and op in ("PLANT", "PICKUP", "PLACE") else ""
                row = {"features": features(obs, seat, actor), "action_verb": op,
                       "action_arg": args_label, "task_label": task_label(op, actor_action[1:], obs, seat, actor)}
                open_files[split].write(json.dumps(row, separators=(",", ":"), sort_keys=True) + "\n")
                open_groups[split].write(json.dumps({"row": row_count[split], "episode_id": eid,
                    "source_family": manifest["source_family"], "player": player,
                    "actor_role": "farmer" if actor == 0 else "hand"}, separators=(",", ":"), sort_keys=True) + "\n")
                row_count[split] += 1; group_count[split] += 1
                actor_classes[split][op] += 1
                task_classes[split][row["task_label"]] += 1
            # Independent per-order labels; no order amount/target coordinate.
            for order in action.get("market") or []:
                if not isinstance(order, list) or not order: continue
                op = str(order[0])
                arg = str(order[1]) if len(order) > 1 else ""
                label = op + (":" + arg if arg else "")
                row = {"features": features(obs, seat, None), "market_intent": label}
                open_files[split].write(json.dumps(row, separators=(",", ":"), sort_keys=True) + "\n")
                open_groups[split].write(json.dumps({"row": row_count[split], "episode_id": eid,
                    "source_family": manifest["source_family"], "player": player,
                    "actor_role": "market"}, separators=(",", ":"), sort_keys=True) + "\n")
                row_count[split] += 1; group_count[split] += 1
                market_classes[split][label] += 1
        del replay
    for split in ("train", "heldout"):
        open_files[split].close()
        open_groups[split].close()
    manifest_path = args.out_dir / "episodes.json"
    manifest_path.write_text(json.dumps({"schema_version": 1, "episodes": manifests,
        "feature_excludes": ["episode_id", "seed", "exact_step", "future_observation", "opponent_action"],
        "label_note": "Actor labels are immediate action verb plus current-state task classification; market labels omit quantities. Rows are not an executable action tape."}, indent=2) + "\n")
    summary = {"episode_count": len({m["episode_id"] for m in manifests}), "episode_player_source_count": len(manifests), "episode_splits": {
        split: sorted({m["episode_id"] for m in manifests if m["split"] == split}) for split in ("train", "heldout")},
        "rows": dict(row_count),
        "actor_action_counts": {s: dict(c) for s, c in actor_classes.items()},
        "actor_task_counts": {s: dict(c) for s, c in task_classes.items()},
        "market_intent_counts": {s: dict(c) for s, c in market_classes.items()},
        "row_group_sidecar": "*_row_groups.jsonl.gz keeps episode/player grouping outside features"}
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Offline legal-action ranker trained only from our own V69 rollout actions."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".venv/lib/python3.12/site-packages"))
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier

OUT = Path(__file__).resolve().parent
TRAIN_REPORT = ROOT / "experiments/v69_macro/spent94700_vs_v56/report.json"
TEST_REPORT = ROOT / "experiments/v69_macro/late_wheat94700_vs_v56/report.json"
ENGINE = ROOT / ".venv/lib/python3.12/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py"
PRODUCTS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER", "COW", "SHEEP", "GOOSE")
CROPS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON")
ANIMALS = ("COW", "SHEEP", "GOOSE")
SHOPS = ("BAKERY", "PIZZA_SHOP", "BRUNCH_SPOT", "YARN_STORE", "ICE_CREAM_SHOP", "PET_CAFE", "SMOOTHIE_SHOP", "FARMERS_MARKET")
MOVES = ("NORTH", "SOUTH", "EAST", "WEST")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def action_key(action):
    return json.dumps(action or ["PASS"], separators=(",", ":"), ensure_ascii=False)


def state_features(observation, seat: int, unit_index: int):
    farm = observation["farms"][seat]
    private = observation.get("private") or {}
    invs = private.get("inventories") or [{}]
    unit_count = 1 + len(farm.get("hands") or [])
    pos = farm["farmer"] if unit_index == 0 else farm["hands"][unit_index - 1]
    inv = invs[unit_index] if unit_index < len(invs) else {}
    feats = {
        "day": observation.get("day", 0), "hour": observation.get("hour", 0),
        "unit_index": unit_index, "unit_count": unit_count,
        "x": pos[0], "y": pos[1], "money": float(farm.get("money", 0)),
        "unlocked_quadrants": len(farm.get("unlocked_quadrants") or []),
        "shed_load": sum((private.get("shed") or {}).values()),
    }
    for item in PRODUCTS:
        feats[f"inv_{item}"] = int(inv.get(item, 0))
        feats[f"shed_{item}"] = int((private.get("shed") or {}).get(item, 0))
        feats[f"seed_{item}"] = int((private.get("seeds") or {}).get(item, 0))
        feats[f"price_{item}"] = float((observation.get("market") or {}).get("prices", {}).get(item, 0))
    counts = Counter()
    dry = 0
    mature = 0
    hungry = 0
    uncared = 0
    for row in farm.get("tiles") or []:
        for tile in row:
            if not isinstance(tile, dict):
                continue
            if tile.get("kind") == "PLANT":
                crop = tile.get("crop", "OTHER")
                counts[f"plant_{crop}"] += 1
                dry += not bool(tile.get("watered_today"))
                mature += int(tile.get("yield_units", 0) > 0)
            elif tile.get("kind") == "WEED":
                counts["weed"] += 1
            elif "animal" in tile:
                animal = tile.get("animal", "OTHER")
                counts[f"animal_{animal}"] += 1
                hungry += int(not tile.get("fed_today", False))
                uncared += int(not tile.get("cared_today", False))
            elif tile.get("kind") in ("PASTURE", "COOP"):
                counts[f"empty_{tile['kind']}"] += 1
    for crop in CROPS:
        feats[f"plant_{crop}"] = counts[f"plant_{crop}"]
    for animal in ANIMALS:
        feats[f"animal_{animal}"] = counts[f"animal_{animal}"]
    feats.update({
        "weeds": counts["weed"], "dry_plants": dry, "yielding_plants": mature,
        "hungry_animals": hungry, "uncared_animals": uncared,
        "empty_pastures": counts["empty_PASTURE"], "empty_coops": counts["empty_COOP"],
    })
    shops = (observation.get("town") or {}).get("unlocked_shops") or []
    for shop in SHOPS:
        feats[f"shop_{shop}"] = int(shop in shops)
    return feats


def rows_from_report(path: Path):
    report = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for game in report["games"]:
        seat = game["candidate_seat"]
        replay_path = Path(game["replay_path"])
        replay = json.loads(replay_path.read_text(encoding="utf-8"))
        steps = replay.get("steps") or []
        for step_no in range(1, len(steps)):
            before = steps[step_no - 1][seat].get("observation") or {}
            actions = steps[step_no][seat].get("action") or {}
            per_unit = [actions.get("farmer") or ["PASS"]] + (actions.get("hands") or [])
            for unit_index, action in enumerate(per_unit):
                rows.append({
                    "features": state_features(before, seat, unit_index),
                    "label": action_key(action), "verb": (action or ["PASS"])[0],
                    "seat": seat, "step": step_no,
                    "source_report": path.name,
                    "candidate_sha256": (game.get("agents") or [])[seat].get("sha256"),
                    "replay_sha256": game.get("replay_sha256"),
                    "observation": before, "unit_index": unit_index, "action": action or ["PASS"],
                })
    return rows


def engine_effectively_applies(observation, seat: int, unit_index: int, action) -> bool:
    """Ask the pinned engine whether this unit action mutates a copied state."""
    import sys
    sys.path.insert(0, str(ROOT / ".venv/lib/python3.12/site-packages"))
    from kaggle_environments.envs.kaggriculture import kaggriculture as engine
    farm = copy.deepcopy(observation["farms"][seat])
    private = copy.deepcopy(observation.get("private") or {})
    private.setdefault("inventories", [{}])
    before = json.dumps([farm, private], sort_keys=True, separators=(",", ":"))
    engine._apply_unit_action(farm, private, unit_index, action, len(farm["tiles"]),
                              int(observation.get("day", 0)), 24, 100)
    after = json.dumps([farm, private], sort_keys=True, separators=(",", ":"))
    return action and action[0] == "PASS" or before != after


def main():
    train = rows_from_report(TRAIN_REPORT)
    test = rows_from_report(TEST_REPORT)
    names = sorted({k for row in train + test for k in row["features"]})
    x_train = [[row["features"].get(k, 0) for k in names] for row in train]
    x_test = [[row["features"].get(k, 0) for k in names] for row in test]
    y_train = [row["label"] for row in train]
    y_test = [row["label"] for row in test]
    model = DecisionTreeClassifier(max_depth=7, min_samples_leaf=30, class_weight="balanced", random_state=69001)
    model.fit(x_train, y_train)
    predicted = model.predict(x_test).tolist()
    family = lambda key: (json.loads(key) or ["PASS"])[0]
    legal_top1 = []
    legal_masked_correct = []
    masked_verbs = []
    fallback_count = 0
    t = model.tree_
    classes = model.classes_.tolist()
    for row, raw in zip(test, predicted):
        try:
            is_legal = engine_effectively_applies(row["observation"], row["seat"], row["unit_index"], json.loads(raw))
        except Exception:
            is_legal = False
        legal_top1.append(is_legal)
        # Return leaf class counts in descending order, then choose the first
        # engine-applicable observed action. This is the minimal legality mask.
        node = 0
        values = [row["features"].get(k, 0) for k in names]
        while t.children_left[node] != t.children_right[node]:
            idx = t.feature[node]
            node = t.children_left[node] if values[idx] <= t.threshold[node] else t.children_right[node]
        class_counts = t.value[node][0]
        ranked = sorted(range(len(classes)), key=lambda i: (-class_counts[i], classes[i]))
        chosen = ["PASS"]
        for class_index in ranked:
            candidate_action = json.loads(classes[class_index])
            try:
                if engine_effectively_applies(row["observation"], row["seat"], row["unit_index"], candidate_action):
                    chosen = candidate_action
                    break
            except Exception:
                continue
        else:
            fallback_count += 1
        chosen_key = action_key(chosen)
        legal_masked_correct.append(chosen_key == row["label"])
        masked_verbs.append(family(chosen_key))

    model_report = {
        "candidate_sha256s": sorted({row["candidate_sha256"] for row in train + test}),
        "source_replay_sha256s": sorted({row["replay_sha256"] for row in train + test if row.get("replay_sha256")}),
        "train_games": str(TRAIN_REPORT.relative_to(ROOT)),
        "test_games": str(TEST_REPORT.relative_to(ROOT)),
        "seed_scope": "94700 spent seed only; train/test separated by V69 source variant, not independent seed",
        "train_unit_decisions": len(train), "test_unit_decisions": len(test),
        "tree_depth_max": 7, "min_samples_leaf": 30,
        "exact_action_top1_accuracy": accuracy_score(y_test, predicted),
        "action_family_top1_accuracy": accuracy_score([family(x) for x in y_test], [family(x) for x in predicted]),
        "majority_action_baseline_accuracy": Counter(y_train).most_common(1)[0][1] / len(y_train),
        "raw_top1_engine_applicability": sum(legal_top1) / len(legal_top1),
        "masked_action_exact_accuracy": sum(legal_masked_correct) / len(legal_masked_correct),
        "masked_engine_applicability": 1.0,
        "pass_fallback_count": fallback_count,
        "masked_action_family_counts": dict(Counter(masked_verbs)),
        "note": "Offline action-ranking diagnostic only; no policy replacement or game evaluation. Labels are V69 authored actions, not public competitor actions.",
    }
    tree = {
        "feature_names": names, "classes": classes,
        "children_left": t.children_left.tolist(), "children_right": t.children_right.tolist(),
        "feature": t.feature.tolist(), "threshold": t.threshold.tolist(), "value": t.value[:, 0, :].tolist(),
    }
    (OUT / "task_ranker_tree.json").write_text(json.dumps(tree, separators=(",", ":")) + "\n", encoding="utf-8")
    (OUT / "task_ranker_report.json").write_text(json.dumps(model_report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(model_report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

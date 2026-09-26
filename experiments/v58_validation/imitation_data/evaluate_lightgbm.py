#!/usr/bin/env python3
"""Fit LightGBM action/task classifiers on the grouped observation dataset."""
from __future__ import annotations
import gzip
import json
import time
from collections import defaultdict
from pathlib import Path

import lightgbm as lgb
import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score


ROOT = Path(__file__).resolve().parent
LEGALITY_KEYS = ("move_n_blocked", "move_s_blocked", "move_e_blocked", "move_w_blocked",
    "tile_kind", "tile_wet", "tile_animal", "tile_fed", "tile_cared_today", "tile_yield_bin",
    "tile_fertilizer_available", "inventory_wheat_bin", "inventory_fertilizer_bin", "inventory_load_bin",
    "inventory_animal", "at_shed", "shed_load_bin", "seed_wheat_count", "seed_carrot_count",
    "seed_melon_count", "seed_tomato_count", "seed_strawberry_count")


def load_arrays(split: str, keys: list[str] | None = None, category_maps=None):
    rows_path = ROOT / f"{split}.jsonl.gz"
    groups_path = ROOT / f"{split}_row_groups.jsonl.gz"
    if split == "train":
        actor_n = sum(json.loads((ROOT / "summary.json").read_text())["actor_action_counts"]["train"].values())
        category_maps = defaultdict(dict)
    else:
        actor_n = sum(json.loads((ROOT / "summary.json").read_text())["actor_action_counts"]["heldout"].values())
        assert keys is not None and category_maps is not None
    X = np.empty((actor_n, len(keys) if keys else 1), dtype=np.int16) if keys else None
    verbs = []
    tasks = []
    metadata = []
    k = 0
    with gzip.open(rows_path, "rt", encoding="utf-8") as rows, gzip.open(groups_path, "rt", encoding="utf-8") as groups:
        for line, meta_line in zip(rows, groups):
            row = json.loads(line)
            meta = json.loads(meta_line)
            features = row["features"]
            if features["decision"] != "actor":
                continue
            if keys is None:
                keys = sorted(features)
                X = np.empty((actor_n, len(keys)), dtype=np.int16)
            vals = []
            for key in keys:
                value = str(features[key])
                mapping = category_maps[key]
                if split == "train":
                    mapping.setdefault(value, len(mapping) + 1)
                vals.append(mapping.get(value, 0))
            X[k, :] = vals
            verbs.append(row["action_verb"])
            tasks.append(row["task_label"])
            if split == "heldout":
                metadata.append({"episode_id": meta["episode_id"],
                                 "features": {key: features.get(key, "") for key in LEGALITY_KEYS}})
            k += 1
    return X[:k], np.asarray(verbs), np.asarray(tasks), metadata, keys, category_maps


def metrics(y_true, y_pred):
    return {"n": len(y_true), "accuracy": float(accuracy_score(y_true, y_pred)),
            "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
            "classes": int(len(set(y_true))),
            "class_counts": {str(k): int(v) for k, v in sorted(__import__("collections").Counter(y_true).items())}}


def legal_proxy(action: str, f: dict):
    """Necessary-precondition proxy only; this is not engine-level validation."""
    if action == "PASS": return True
    x, y = int(f.get("pos_x", 0)), int(f.get("pos_y", 0))
    if action == "NORTH": return y > 0
    if action == "SOUTH": return y < 9
    if action == "WEST": return x > 0
    if action == "EAST": return x < 9
    if action == "WATER": return f.get("tile_kind") == "PLANT" and f.get("tile_wet") == "False"
    if action == "HARVEST": return f.get("tile_yield_bin") != "0"
    if action == "FEED": return f.get("tile_animal") != "NONE" and f.get("tile_fed") == "False" and f.get("inventory_wheat_bin") != "0"
    if action == "CARE": return f.get("tile_animal") != "NONE" and f.get("tile_cared_today") == "False"
    if action == "DIG": return f.get("tile_kind") == "WEED"
    if action == "DROP": return f.get("inventory_load_bin") != "0"
    if action == "COLLECT_FERTILIZER": return f.get("tile_fertilizer_available") == "True"
    if action == "FERTILIZE": return f.get("tile_kind") == "PLANT" and f.get("inventory_fertilizer_bin") != "0"
    if action == "PLANT":
        return f.get("tile_kind") == "NONE" and any(f.get(f"seed_{c.lower()}_count") != "0" for c in ("WHEAT", "CARROT", "MELON", "TOMATO", "STRAWBERRY"))
    if action == "PICKUP": return f.get("at_shed") == "True" and f.get("shed_load_bin") != "0"
    if action == "PLACE":
        species = f.get("inventory_animal")
        return (species in ("COW", "SHEEP") and f.get("tile_kind") == "PASTURE" and f.get("tile_animal") == "NONE") or (species == "GOOSE" and f.get("tile_kind") == "COOP" and f.get("tile_animal") == "NONE")
    return None


def main():
    start = time.perf_counter()
    X_train, yverb, ytask, _, keys, catmaps = load_arrays("train")
    X_test, tverb, ttask, metadata, _, _ = load_arrays("heldout", keys, catmaps)
    split_seconds = time.perf_counter() - start
    train_ids = {m["episode_id"] for m in json.loads((ROOT / "episodes.json").read_text())["episodes"] if m["split"] == "train"}
    held_ids = {m["episode_id"] for m in json.loads((ROOT / "episodes.json").read_text())["episodes"] if m["split"] == "heldout"}
    report = {"train_n": len(X_train), "heldout_n": len(X_test), "feature_count": len(keys),
              "categorical_features": len(keys), "episode_overlap": sorted(train_ids & held_ids), "split_load_seconds": round(split_seconds, 2), "models": {}}
    if report["episode_overlap"]:
        raise RuntimeError("episode leakage across train/heldout")
    for label_name, y_train, y_test in (("action_verb", yverb, tverb), ("task_label", ytask, ttask)):
        fit_start = time.perf_counter()
        model = lgb.LGBMClassifier(objective="multiclass", n_estimators=70, num_leaves=31,
            learning_rate=0.08, max_depth=-1, min_child_samples=40, reg_lambda=1.0,
            max_bin=63, n_jobs=2, verbosity=-1, random_state=17, deterministic=True,
            force_col_wise=True)
        model.fit(X_train, y_train, categorical_feature=list(range(len(keys))))
        y_pred = model.predict(X_test)
        known = [legal_proxy(str(p), m["features"]) for p, m in zip(y_pred, metadata)] if label_name == "action_verb" else []
        known_rates = [x for x in known if x is not None]
        train_counts = __import__("collections").Counter(y_train)
        majority = max(train_counts, key=train_counts.get)
        classes = sorted(set(y_test) | set(y_pred))
        cm = confusion_matrix(y_test, y_pred, labels=classes)
        confusions = sorted(((int(cm[i, j]), str(classes[i]), str(classes[j]))
            for i in range(len(classes)) for j in range(len(classes)) if i != j and cm[i, j] > 0), reverse=True)[:30]
        model.booster_.save_model(str(ROOT / f"{label_name}_model.txt"))
        report["models"][label_name] = {
            "metrics": metrics(y_test, y_pred),
            "majority_baseline": metrics(y_test, np.full(len(y_test), majority)),
            "largest_confusions_true_to_pred_count": [{"count": n, "true": a, "predicted": b} for n, a, b in confusions],
            "training_seconds": round(time.perf_counter() - fit_start, 2),
            "necessary_precondition_proxy": ({"coverage": len(known_rates) / max(1, len(known)),
                "predicted_feasible_rate_on_covered": sum(known_rates) / max(1, len(known_rates)),
                "covered_rows": len(known_rates),
                "warning": "Current-observation necessary-precondition proxy; not engine action acceptance."}
                if label_name == "action_verb" else {"applicable": False}),
            "top_features_by_gain": sorted(zip(keys, model.booster_.feature_importance(importance_type="gain")),
                key=lambda pair: -pair[1])[:20],
        }
    report["total_runtime_seconds"] = round(time.perf_counter() - start, 2)
    (ROOT / "feature_categories.json").write_text(json.dumps({"feature_keys": keys,
        "category_to_code": {key: values for key, values in catmaps.items()},
        "unknown_code": 0}, sort_keys=True, separators=(",", ":")) + "\n")
    (ROOT / "lightgbm_evaluation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

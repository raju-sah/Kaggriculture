#!/usr/bin/env python3
"""Measure exported booster inference and corrected necessary-precondition proxy."""
import gzip
import json
import time
from pathlib import Path

import lightgbm as lgb
import numpy as np

ROOT = Path(__file__).resolve().parent


def legal_proxy(action, f):
    if action == "PASS": return True
    x, y = int(f["pos_x"]), int(f["pos_y"])
    if action == "NORTH": return y > 0
    if action == "SOUTH": return y < 9
    if action == "WEST": return x > 0
    if action == "EAST": return x < 9
    if action == "WATER": return f["tile_kind"] == "PLANT" and f["tile_wet"] == "False"
    if action == "HARVEST": return f["tile_yield_bin"] != "0"
    if action == "FEED": return f["tile_animal"] != "NONE" and f["tile_fed"] == "False" and f["inventory_wheat_bin"] != "0"
    if action == "CARE": return f["tile_animal"] != "NONE" and f["tile_cared_today"] == "False"
    if action == "DIG": return f["tile_kind"] == "WEED"
    if action == "DROP": return f["inventory_load_bin"] != "0"
    if action == "COLLECT_FERTILIZER": return f["tile_fertilizer_available"] == "True"
    if action == "FERTILIZE": return f["tile_kind"] == "PLANT" and f["inventory_fertilizer_bin"] != "0"
    if action == "PLANT":
        return f["tile_kind"] == "NONE" and any(f[f"seed_{c}_count"] != "0" for c in ("wheat", "carrot", "melon", "tomato", "strawberry"))
    if action == "PICKUP": return f["at_shed"] == "True" and f["shed_load_bin"] != "0"
    if action == "PLACE":
        animal = f["inventory_animal"]
        return (animal in ("COW", "SHEEP") and f["tile_kind"] == "PASTURE" and f["tile_animal"] == "NONE") or (animal == "GOOSE" and f["tile_kind"] == "COOP" and f["tile_animal"] == "NONE")
    return None


def main():
    start = time.perf_counter()
    cat = json.loads((ROOT / "feature_categories.json").read_text())
    keys = cat["feature_keys"]
    maps = cat["category_to_code"]
    load_start = time.perf_counter()
    verb_model = lgb.Booster(model_file=str(ROOT / "action_verb_model.txt"))
    task_model = lgb.Booster(model_file=str(ROOT / "task_label_model.txt"))
    model_load_seconds = time.perf_counter() - load_start
    X = []
    rows = []
    with gzip.open(ROOT / "heldout.jsonl.gz", "rt", encoding="utf-8") as src:
        for line in src:
            row = json.loads(line)
            f = row["features"]
            if f["decision"] != "actor": continue
            X.append([maps[key].get(str(f[key]), 0) for key in keys])
            rows.append((f, row["action_verb"], row["task_label"]))
    X = np.asarray(X, dtype=np.int16)
    pred_start = time.perf_counter()
    verb_probs = verb_model.predict(X, num_threads=2)
    task_probs = task_model.predict(X, num_threads=2)
    inference_seconds = time.perf_counter() - pred_start
    classes = json.loads((ROOT / "model_classes.json").read_text())
    verbs = classes["action_verb_classes"]
    tasks = classes["task_label_classes"]
    verb_predictions = [verbs[int(i)] for i in np.argmax(verb_probs, axis=1)]
    task_predictions = [tasks[int(i)] for i in np.argmax(task_probs, axis=1)]
    covered = []
    for pred, (f, _, _) in zip(verb_predictions, rows):
        feasible = legal_proxy(pred, f)
        if feasible is not None: covered.append(bool(feasible))
    report = {
        "heldout_actor_rows": len(rows), "feature_count": len(keys),
        "booster_sizes_bytes": {"action_verb": (ROOT / "action_verb_model.txt").stat().st_size,
                                "task_label": (ROOT / "task_label_model.txt").stat().st_size},
        "model_load_seconds": round(model_load_seconds, 4),
        "two_model_inference_seconds": round(inference_seconds, 4),
        "milliseconds_per_actor_for_two_models": round(1000 * inference_seconds / max(1, len(rows)), 5),
        "models_each_invoked_once_for_all_actors": True,
        "predicted_action_precondition_proxy": {"coverage": len(covered) / max(1, len(rows)),
            "feasible_fraction_when_covered": sum(covered) / max(1, len(covered)),
            "coverage_n": len(covered),
            "warning": "Necessary preconditions from binned observations only; not exact engine legality. Runtime resolver must inspect raw observation and mask per-unit commands."},
        "action_prediction_counts": {name: verb_predictions.count(name) for name in sorted(set(verb_predictions))},
        "task_prediction_counts": {name: task_predictions.count(name) for name in sorted(set(task_predictions))},
        "total_runtime_seconds": round(time.perf_counter() - start, 4),
    }
    (ROOT / "inference_benchmark.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__": main()

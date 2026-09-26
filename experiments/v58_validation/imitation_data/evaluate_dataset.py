#!/usr/bin/env python3
"""Held-out categorical baselines for actor action/task and market labels."""
from __future__ import annotations
import gzip
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


def load(path: Path) -> list[dict]:
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return [json.loads(line) for line in f]


class CategoricalNB:
    def fit(self, examples: list[tuple[dict, str]]) -> None:
        self.n = len(examples)
        self.classes = Counter(y for _, y in examples)
        self.feature_counts = {c: defaultdict(Counter) for c in self.classes}
        self.vocab = defaultdict(set)
        for features, label in examples:
            for key, value in features.items():
                value = str(value)
                self.feature_counts[label][key][value] += 1
                self.vocab[key].add(value)

    def predict(self, features: dict) -> str:
        best_label, best_score = None, -float("inf")
        for label, n_label in self.classes.items():
            score = math.log((n_label + 1) / (self.n + len(self.classes)))
            for key, value in features.items():
                counts = self.feature_counts[label][key]
                vocab_size = max(2, len(self.vocab[key]))
                score += math.log((counts[str(value)] + 1) / (n_label + vocab_size))
            if score > best_score:
                best_label, best_score = label, score
        return str(best_label)


def metrics(y_true: list[str], y_pred: list[str]) -> dict:
    support = Counter(y_true)
    tp = Counter(a for a, b in zip(y_true, y_pred) if a == b)
    labels = set(y_true) | set(y_pred)
    f1s = []
    for label in labels:
        fp = sum(1 for a, b in zip(y_true, y_pred) if b == label and a != label)
        fn = sum(1 for a, b in zip(y_true, y_pred) if a == label and b != label)
        denom = 2 * tp[label] + fp + fn
        f1s.append(2 * tp[label] / denom if denom else 0.0)
    return {"n": len(y_true), "accuracy": sum(a == b for a, b in zip(y_true, y_pred)) / max(1, len(y_true)),
            "macro_f1": sum(f1s) / max(1, len(f1s)), "classes": len(support),
            "class_counts": dict(sorted(support.items()))}


def evaluate(train_rows: list[dict], held_rows: list[dict], label_key: str) -> dict:
    train = [(row["features"], row[label_key]) for row in train_rows if label_key in row]
    held = [(row["features"], row[label_key]) for row in held_rows if label_key in row]
    model = CategoricalNB()
    model.fit(train)
    y = [label for _, label in held]
    nb = [model.predict(features) for features, _ in held]
    majority = max(Counter(label for _, label in train), key=Counter(label for _, label in train).get)
    return {"train_n": len(train), "heldout": metrics(y, nb),
            "majority_baseline": metrics(y, [majority] * len(y)),
            "train_class_counts": dict(sorted(Counter(label for _, label in train).items()))}


def main() -> int:
    root = Path(__file__).resolve().parent
    train = load(root / "train.jsonl.gz")
    held = load(root / "heldout.jsonl.gz")
    train_groups = load(root / "train_row_groups.jsonl.gz")
    held_groups = load(root / "heldout_row_groups.jsonl.gz")
    train_episodes = {x["episode_id"] for x in train_groups}
    held_episodes = {x["episode_id"] for x in held_groups}
    overlap = sorted(train_episodes & held_episodes)
    actor_train = [row for row in train if row["features"]["decision"] == "actor"]
    actor_held = [row for row in held if row["features"]["decision"] == "actor"]
    market_train = [row for row in train if row["features"]["decision"] == "market"]
    market_held = [row for row in held if row["features"]["decision"] == "market"]
    report = {
        "train_episodes": len(train_episodes), "heldout_episodes": len(held_episodes),
        "episode_overlap": overlap,
        "feature_keys": sorted(train[0]["features"]),
        "actor_action_verb": evaluate(actor_train, actor_held, "action_verb"),
        "actor_task": evaluate(actor_train, actor_held, "task_label"),
        "market_intent": evaluate(market_train, market_held, "market_intent"),
        "caveat": "CategoricalNB and majority are diagnostics, not a route controller; action labels are behavior imitation and held-out episodes only measure replay-distribution generalization."
    }
    (root / "evaluation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 1 if overlap else 0


if __name__ == "__main__":
    raise SystemExit(main())

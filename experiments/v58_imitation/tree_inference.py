"""Pure-stdlib inference for the categorical multiclass LightGBM exports.

This supports only the decision types found in the fitted artifacts (categorical
equality). It is research tooling, not the standalone Kaggle callable.
"""
import gzip
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent

class TreeModel:
    def __init__(self, path):
        with gzip.open(path, "rt") as f:
            self.model = json.load(f)
        self.nclass = int(self.model["num_class"])
        self.ntree = int(self.model["num_tree_per_iteration"])
        self.trees = self.model["tree_info"]

    @staticmethod
    def _tree_value(node, features):
        while "split_index" in node:
            if node["decision_type"] != "==":
                raise ValueError(f"unsupported split: {node['decision_type']}")
            value = int(features[node["split_feature"]])
            categories = node["threshold"].split("||")
            match = str(value) in categories
            node = node["left_child"] if match else node["right_child"]
        return float(node["leaf_value"])

    def predict_one(self, features):
        scores = [0.0] * self.nclass
        for i, tree in enumerate(self.trees):
            scores[i % self.nclass] += self._tree_value(tree["tree_structure"], features)
        peak = max(scores)
        values = [math.exp(x - peak) for x in scores]
        total = sum(values)
        return [x / total for x in values]


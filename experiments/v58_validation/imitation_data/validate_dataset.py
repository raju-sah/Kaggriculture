#!/usr/bin/env python3
"""Check split boundaries, row-group alignment, and feature leakage contract."""
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FORBIDDEN = {"seed", "episode_id", "replay_id", "exact_step", "step", "future", "opponent_action"}


def rows(name):
    with gzip.open(ROOT / f"{name}.jsonl.gz", "rt", encoding="utf-8") as f:
        yield from f


def groups(name):
    with gzip.open(ROOT / f"{name}_row_groups.jsonl.gz", "rt", encoding="utf-8") as f:
        yield from f


def main():
    manifest = json.loads((ROOT / "episodes.json").read_text())["episodes"]
    by_split = {split: {x["episode_id"] for x in manifest if x["split"] == split}
                for split in ("train", "heldout")}
    overlap = sorted(by_split["train"] & by_split["heldout"])
    summary = {}
    bad_features = []
    for split in ("train", "heldout"):
        count = 0
        for line, meta_line in zip(rows(split), groups(split)):
            row = json.loads(line); meta = json.loads(meta_line)
            features = row["features"]
            if meta["episode_id"] not in by_split[split]:
                raise ValueError(f"row {count} appears in the wrong group: {meta['episode_id']}")
            bad = FORBIDDEN & {k.lower() for k in features}
            if bad: bad_features.append({"split": split, "row": count, "keys": sorted(bad)})
            if features["decision"] == "actor" and not {"action_verb", "task_label"} <= set(row):
                raise ValueError(f"actor labels missing at {split}:{count}")
            if features["decision"] == "market" and "market_intent" not in row:
                raise ValueError(f"market label missing at {split}:{count}")
            count += 1
        expected = json.loads((ROOT / "summary.json").read_text())["rows"][split]
        if count != expected:
            raise ValueError(f"row/group count mismatch for {split}: {count} != {expected}")
        summary[split] = count
    if overlap or bad_features:
        raise ValueError(f"leakage check failed: overlap={overlap}, bad_features={bad_features[:2]}")
    result = {"ok": True, "episode_overlap": overlap, "split_row_counts": summary,
              "forbidden_feature_keys_present": False}
    (ROOT / "validation.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__": main()

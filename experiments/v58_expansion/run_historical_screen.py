"""Frozen paired screen against the requested eight historical opponents."""
from __future__ import annotations

import hashlib
import json
import os
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from simulation.tournament import MatchSpec, Opponent, _game_id, _run_worker

BASELINE = ROOT / "experiments/v57_broad/v57_reset_candidate.py"
EXPANSION = ROOT / "experiments/v58_expansion/v58_expansion_candidate.py"
FROZEN_EXPANSION_SHA = "20c5a4a2e0d96d39cdd9e26de9daff0e685b66b5ec7f943f1e85ae38330e09fc"
FROZEN_BASELINE_SHA = "4173479fe1f80d031d570d1ea23b694dfe86e1d162317a4c9c7df0058a40208e"
OPPONENTS = {
    "v48": ROOT / "experiments/v48_agent.py",
    "v50": ROOT / "experiments/v50_agent.py",
    "v51": ROOT / "experiments/v51_agent.py",
    "v52": ROOT / "experiments/v52_agent.py",
    "v53": ROOT / "experiments/v53_agent.py",
    "v54": ROOT / "agents/v54_agent.py",
    "v55": ROOT / "agents/v55_agent.py",
    "v56": ROOT / "agents/v56_agent.py",
}
SEEDS = [93600, 93601, 93602, 93603, 93604]
OUT = ROOT / "experiments/v58_expansion/historical_93600"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def shops_from_replay(path: Path, seat: int) -> list[str]:
    replay = json.loads(path.read_text())
    longest: list[str] = []
    for step in replay.get("steps", []):
        if seat >= len(step):
            continue
        observation = step[seat].get("observation") or {}
        shops = ((observation.get("town") or {}).get("unlocked_shops") or [])
        if len(shops) > len(longest):
            longest = list(shops)
    return longest


def margin(row: dict) -> float | None:
    coins = row.get("final_coins") or [None, None]
    seat = row.get("candidate_seat", 0)
    if coins[0] is None or coins[1] is None:
        return None
    return float(coins[seat] - coins[1 - seat])


def main() -> int:
    os.chdir(ROOT)
    if sha(EXPANSION) != FROZEN_EXPANSION_SHA or sha(BASELINE) != FROZEN_BASELINE_SHA:
        raise SystemExit("Frozen candidate hash mismatch; refusing to run")
    arms = {"baseline": BASELINE, "expansion": EXPANSION}
    plans = {}
    tasks = []
    for arm, candidate in arms.items():
        plans[arm] = {
            "candidate": str(candidate.relative_to(ROOT)),
            "candidate_sha256": sha(candidate),
            "opponents": {name: str(path.relative_to(ROOT)) for name, path in OPPONENTS.items()},
            "opponent_sha256": {name: sha(path) for name, path in OPPONENTS.items()},
            "seeds": SEEDS,
            "seats": [0, 1],
            "engine": {
                "package": "kaggle-environments", "version": "1.32.7",
                "engine_sha256": "bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e",
            },
            "replay_handling": "Extract longest observed town.unlocked_shops list, then delete full replay.",
        }
        out = OUT / arm
        out.mkdir(parents=True, exist_ok=True)
        (out / "plan.json").write_text(json.dumps(plans[arm], indent=2) + "\n")
        for name, path in OPPONENTS.items():
            for seed in SEEDS:
                for seat in (0, 1):
                    tasks.append((arm, candidate, MatchSpec(Opponent(name, path), seed, bool(seat), 0)))

    records: dict[str, list[dict]] = {arm: [] for arm in arms}
    started = time.monotonic()
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {}
        for arm, candidate, spec in tasks:
            out = OUT / arm
            future = pool.submit(_run_worker, candidate, spec, out, 240, "all")
            futures[future] = arm
        for future in as_completed(futures):
            arm = futures[future]
            row = future.result()
            replay_path = Path(row["replay_path"]) if row.get("replay_path") else None
            if replay_path and replay_path.exists():
                row["shop_sequence"] = shops_from_replay(replay_path, row["candidate_seat"])
                replay_path.unlink()
            else:
                row["shop_sequence"] = []
            row["candidate_coin_margin"] = margin(row)
            row["replay_path"] = None
            row["replay_retained"] = False
            records[arm].append(row)
            print(f"{arm} {row['opponent']} seed={row['seed']} seat={row['candidate_seat']} "
                  f"result={row['candidate_result']} margin={row['candidate_coin_margin']} "
                  f"shops={row['shop_sequence']} elapsed={time.monotonic()-started:.0f}s", flush=True)

    for arm, rows in records.items():
        rows.sort(key=lambda row: (row["opponent"], row["seed"], row["candidate_seat"]))
        out = OUT / arm
        (out / "games.json").write_text(json.dumps(rows, indent=2) + "\n")
        by_opponent = {}
        for opponent in OPPONENTS:
            group = [row for row in rows if row["opponent"] == opponent]
            values = [row["candidate_coin_margin"] for row in group if row["candidate_coin_margin"] is not None]
            by_opponent[opponent] = {
                "wins": sum(row["candidate_result"] == "win" for row in group),
                "losses": sum(row["candidate_result"] == "loss" for row in group),
                "draws": sum(row["candidate_result"] == "draw" for row in group),
                "errors": sum(not row.get("ok") for row in group),
                "mean_margin": statistics.fmean(values) if values else None,
                "margins": values,
            }
        (out / "summary.json").write_text(json.dumps({
            "games": len(rows), "by_opponent": by_opponent,
            "elapsed_seconds": round(time.monotonic() - started, 1),
        }, indent=2) + "\n")

    bmap = {(r["opponent"], r["seed"], r["candidate_seat"]): r for r in records["baseline"]}
    emap = {(r["opponent"], r["seed"], r["candidate_seat"]): r for r in records["expansion"]}
    paired = []
    for key, baseline in bmap.items():
        expansion = emap[key]
        paired.append({
            "opponent": key[0], "seed": key[1], "candidate_seat": key[2],
            "baseline_margin": baseline["candidate_coin_margin"],
            "expansion_margin": expansion["candidate_coin_margin"],
            "margin_delta": expansion["candidate_coin_margin"] - baseline["candidate_coin_margin"],
            "same_shop_sequence": baseline["shop_sequence"] == expansion["shop_sequence"],
            "shop_sequence_baseline": baseline["shop_sequence"],
            "shop_sequence_expansion": expansion["shop_sequence"],
        })
    (OUT / "paired_comparison.json").write_text(json.dumps(paired, indent=2) + "\n")
    return 0 if all(row.get("ok") for rows in records.values() for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())

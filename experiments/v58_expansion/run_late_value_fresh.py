"""Paired fresh test of the frozen late-only SELL ordering overlay."""
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
from simulation.tournament import MatchSpec, Opponent, _run_worker

BASELINE = ROOT / "experiments/v57_broad/v57_reset_candidate.py"
LATE = ROOT / "experiments/v58_expansion/v58_late_value_candidate.py"
OPPONENTS = {name: ROOT / f"agents/{name}_agent.py" for name in ("v54", "v56")}
SEEDS = list(range(93800, 93805))
OUT = ROOT / "experiments/v58_expansion/late_value_93800"
EXPECTED = {
    "baseline": "4173479fe1f80d031d570d1ea23b694dfe86e1d162317a4c9c7df0058a40208e",
    "late_value": "ec0e983d6ba2db269c2382e0c923ff6260a33a4ba3e94fa4103074279fdb0527",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _shops(replay_path: Path, seat: int):
    data = json.loads(replay_path.read_text())
    longest = []
    for state in data.get("steps", []):
        obs = state[seat].get("observation") or {}
        shops = (obs.get("town") or {}).get("unlocked_shops") or []
        if len(shops) > len(longest):
            longest = list(shops)
    return longest


def _first_action_difference(base_path: Path, late_path: Path, seat: int):
    base = json.loads(base_path.read_text())["steps"]
    late = json.loads(late_path.read_text())["steps"]
    for index, (brow, lrow) in enumerate(zip(base, late)):
        ba = brow[seat].get("action") or {}
        la = lrow[seat].get("action") or {}
        if ba != la:
            obs = (lrow[seat].get("observation") or {})
            return {"step_index": index, "step": obs.get("step"), "day": obs.get("day"),
                    "hour": obs.get("hour"), "baseline_market": ba.get("market"),
                    "late_market": la.get("market"), "farmer_same": ba.get("farmer") == la.get("farmer"),
                    "hands_same": ba.get("hands") == la.get("hands")}
    return None


def _margin(row):
    coins = row.get("final_coins") or [None, None]
    seat = int(row["candidate_seat"])
    if coins[0] is None or coins[1] is None:
        return None
    return float(coins[seat] - coins[1-seat])


def main():
    os.chdir(ROOT)
    paths = {"baseline": BASELINE, "late_value": LATE}
    for arm, path in paths.items():
        actual = sha(path)
        if actual != EXPECTED[arm]:
            raise SystemExit(f"{arm} hash mismatch: {actual}")
    OUT.mkdir(parents=True, exist_ok=True)
    plan = {"arms": {arm: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for arm, path in paths.items()},
            "opponents": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in OPPONENTS.items()},
            "seeds": SEEDS, "seats": [0, 1], "games": 40,
            "change": "from step 630, rank existing SELL slots by current quote times requested quantity",
            "engine": {"package": "kaggle-environments", "version": "1.32.7",
                       "sha256": "bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e"}}
    (OUT / "plan.json").write_text(json.dumps(plan, indent=2) + "\n")
    tasks = []
    for arm, candidate in paths.items():
        for name, opath in OPPONENTS.items():
            for seed in SEEDS:
                for seat in (0, 1):
                    tasks.append((arm, candidate, MatchSpec(Opponent(name, opath), seed, bool(seat), 0)))
    records = {arm: [] for arm in paths}
    start = time.monotonic()
    with ThreadPoolExecutor(max_workers=6) as pool:
        future_map = {pool.submit(_run_worker, candidate, spec, OUT / arm, 240, "all"): (arm, spec)
                      for arm, candidate, spec in tasks}
        for fut in as_completed(future_map):
            arm, spec = future_map[fut]
            row = fut.result()
            replay = Path(row["replay_path"]) if row.get("replay_path") else None
            row["candidate_seat"] = int(bool(spec.swapped))
            row["candidate_coin_margin"] = _margin(row)
            row["shop_sequence"] = _shops(replay, row["candidate_seat"]) if replay and replay.exists() else []
            row["replay_path"] = str(replay) if replay else None
            records[arm].append(row)
            print(f"{arm} {row['opponent']} seed={row['seed']} seat={row['candidate_seat']} "
                  f"coins={row.get('final_coins')} margin={row['candidate_coin_margin']} "
                  f"shops={row['shop_sequence']} elapsed={time.monotonic()-start:.0f}s", flush=True)

    for arm in records:
        records[arm].sort(key=lambda r: (r["opponent"], r["seed"], r["candidate_seat"]))
        (OUT / arm / "games.json").write_text(json.dumps(records[arm], indent=2) + "\n")
        groups = {}
        for name in OPPONENTS:
            subset = [r for r in records[arm] if r["opponent"] == name]
            margins = [r["candidate_coin_margin"] for r in subset if r["candidate_coin_margin"] is not None]
            groups[name] = {"wins": sum(r.get("candidate_result") == "win" for r in subset),
                            "losses": sum(r.get("candidate_result") == "loss" for r in subset),
                            "errors": sum(not r.get("ok") for r in subset),
                            "mean_margin": statistics.fmean(margins) if margins else None}
        (OUT / arm / "summary.json").write_text(json.dumps({"games": len(records[arm]), "by_opponent": groups}, indent=2)+"\n")

    baseline_map = {(r["opponent"], r["seed"], r["candidate_seat"]): r for r in records["baseline"]}
    late_map = {(r["opponent"], r["seed"], r["candidate_seat"]): r for r in records["late_value"]}
    paired = []
    for key, b in baseline_map.items():
        e = late_map[key]
        bp, ep = Path(b["replay_path"]), Path(e["replay_path"])
        bcoins, ecoins = b["final_coins"], e["final_coins"]
        seat = int(b["candidate_seat"])
        paired.append({"opponent": key[0], "seed": key[1], "candidate_seat": seat,
                       "baseline_coins_candidate_opponent": [bcoins[seat], bcoins[1-seat]],
                       "late_coins_candidate_opponent": [ecoins[seat], ecoins[1-seat]],
                       "candidate_coin_delta": ecoins[seat]-bcoins[seat],
                       "opponent_coin_delta": ecoins[1-seat]-bcoins[1-seat],
                       "baseline_margin": b["candidate_coin_margin"],
                       "late_margin": e["candidate_coin_margin"],
                       "margin_delta": e["candidate_coin_margin"]-b["candidate_coin_margin"],
                       "same_shop_sequence": b["shop_sequence"] == e["shop_sequence"],
                       "shop_sequence_baseline": b["shop_sequence"],
                       "shop_sequence_late": e["shop_sequence"],
                       "first_action_difference": _first_action_difference(bp, ep, seat) if bp.exists() and ep.exists() else None,
                       "baseline_replay_sha256": b.get("replay_sha256"), "late_replay_sha256": e.get("replay_sha256")})
    (OUT / "paired_comparison.json").write_text(json.dumps(paired, indent=2)+"\n")
    for row in paired:
        for arm in ("baseline", "late_value"):
            rec = baseline_map[(row["opponent"], row["seed"], row["candidate_seat"])] if arm == "baseline" else late_map[(row["opponent"], row["seed"], row["candidate_seat"])]
            if rec.get("replay_path"):
                Path(rec["replay_path"]).unlink(missing_ok=True)
            rec["replay_path"] = None
    for arm in records:
        (OUT / arm / "games.json").write_text(json.dumps(records[arm], indent=2)+"\n")
    errors = sum(not r.get("ok") for rows in records.values() for r in rows)
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

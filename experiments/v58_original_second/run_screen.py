"""Fresh paired smoke screen for the observation-derived second route."""
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from simulation.tournament import MatchSpec, Opponent, _run_worker

CANDIDATE = Path(__file__).with_name("original_second_candidate.py")
OPPONENTS = {n: ROOT / f"experiments/{n}_agent.py" for n in ("v50", "v53", "v54")}
SEEDS = [94513, 94514, 94515]
OUT = Path(__file__).with_name("screen_fast_fetch")

def main():
    os.chdir(ROOT)
    plan = {"candidate": str(CANDIDATE.relative_to(ROOT)),
            "candidate_sha256": hashlib.sha256(CANDIDATE.read_bytes()).hexdigest(),
            "opponents": {n: str(p.relative_to(ROOT)) for n, p in OPPONENTS.items()},
            "opponent_sha256": {n: hashlib.sha256(p.read_bytes()).hexdigest() for n, p in OPPONENTS.items()},
            "seeds": SEEDS, "seats": [0, 1], "replay_policy": "candidate runs all, opponent agent uses loader",
            "engine": "kaggle-environments 1.32.7"}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "plan.json").write_text(json.dumps(plan, indent=2) + "\n")
    jobs = [(n, p, MatchSpec(Opponent(n, p), seed, bool(seat), 0))
            for n, p in OPPONENTS.items() for seed in SEEDS for seat in (0, 1)]
    rows, start = [], time.monotonic()
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(_run_worker, CANDIDATE, spec, OUT, 240, "all"): (n, spec)
                   for n, _, spec in jobs}
        for future in as_completed(futures):
            n, spec = futures[future]
            row = future.result()
            rows.append(row)
            coins = row.get("final_coins") or [None, None]
            seat = row.get("candidate_seat", 0)
            row["candidate_coin_margin"] = coins[seat] - coins[1-seat] if coins[0] is not None and coins[1] is not None else None
            print(n, spec.seed, seat, row.get("candidate_result"), row.get("candidate_coin_margin"), flush=True)
    rows.sort(key=lambda r: (r["opponent"], r["seed"], r["candidate_seat"]))
    (OUT / "games.json").write_text(json.dumps(rows, indent=2) + "\n")
    summary = {}
    for n in OPPONENTS:
        group = [r for r in rows if r["opponent"] == n]
        margins = [r["candidate_coin_margin"] for r in group if r.get("candidate_coin_margin") is not None]
        summary[n] = {"wins": sum(r["candidate_result"] == "win" for r in group),
                      "losses": sum(r["candidate_result"] == "loss" for r in group),
                      "draws": sum(r["candidate_result"] == "draw" for r in group),
                      "errors": sum(not r.get("ok") for r in group),
                      "mean_margin": sum(margins) / len(margins) if margins else None,
                      "margins": margins}
    (OUT / "summary.json").write_text(json.dumps({"games": len(rows), "by_opponent": summary,
         "elapsed_seconds": round(time.monotonic()-start, 1)}, indent=2) + "\n")

if __name__ == "__main__":
    raise SystemExit(main())

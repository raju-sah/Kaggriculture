"""V101 precommitted fresh holdout: 170001-170024, both seats, three opponents.

Runs the frozen candidate (sha256 8c572b90...) against frozen V92 (primary),
V50 and V56 (controls) on the precommitted fresh seed range. Nothing here tunes,
filters, retries or re-ranks a seed: every seed runs in both seats against every
opponent, and the raw per-game records are the output. The gate thresholds are
NOT read by this file; the audit is a separate step that scores the finished run
against the criteria already written in GATE.md.

    .venv/bin/python experiments/v101_commandcode/holdout.py --workers 8
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CAND = HERE / "candidate.py"

FROZEN_CANDIDATE_SHA = "8c572b9027ca4f5a0d656d1b1dd6fb74b4b121bd67c69b97aef16d66e21052e7"
FROZEN_OPPONENT_SHA = {
    "v92": "0d5d356baa25703f1a7b753527d1b39e1c7d63478985913be5b3c2550261b806",
    "v50": "e6b50128e023e3b9fafa1841e4cd520c5e581acb48e8628657585c18272eab2b",
    "v56": "d9e9670921b62afedfa8cbc7086d2a2ec19e153ee26006cef477eadd462bd19c",
}
OPPOSITION_PATHS = {
    "v92": ROOT / "experiments/v92_overflow_guard/candidate.py",
    "v50": ROOT / "experiments/v50_agent.py",
    "v56": ROOT / "agents/v56_agent.py",
}
HOLDOUT_SEEDS = list(range(170001, 170025))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def preflight() -> None:
    """Refuse to run unless every file still matches the precommitted hash."""
    problems = []
    got = sha(CAND)
    if got != FROZEN_CANDIDATE_SHA:
        problems.append(f"candidate drifted: {got} != {FROZEN_CANDIDATE_SHA}")
    for tag, path in OPPOSITION_PATHS.items():
        got = sha(path)
        if got != FROZEN_OPPONENT_SHA[tag]:
            problems.append(f"{tag} drifted: {got} != {FROZEN_OPPONENT_SHA[tag]}")
    if problems:
        print("PREFLIGHT FAILED:", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        raise SystemExit(2)
    print("preflight ok: candidate and all three opponents match the frozen hashes")


def run(tag: str, workers: int) -> None:
    outdir = HERE / "runs" / f"holdout_vs_{tag}"
    cmd = [sys.executable, "-m", "simulation.tournament",
           "--candidate", str(CAND), "--opponent", f"{tag}={OPPOSITION_PATHS[tag]}",
           "--seeds", ",".join(str(s) for s in HOLDOUT_SEEDS),
           "--workers", str(workers), "--timeout", "1800",
           "--replay-policy", "errors", "--output-dir", str(outdir)]
    print(f"  $ holdout vs {tag}: {len(HOLDOUT_SEEDS)} seeds x 2 seats, {workers} workers",
          flush=True)
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=172800)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "runner.log").write_text(proc.stdout + "\n" + proc.stderr, encoding="utf-8")
    if proc.returncode != 0:
        print(f"    runner exit={proc.returncode} (tournament returns 1 on infrastructure"
              " error or determinism failure; the audit reads games.jsonl directly)")


def summarize(tag: str) -> dict:
    outdir = HERE / "runs" / f"holdout_vs_{tag}"
    rows = [json.loads(l) for l in (outdir / "games.jsonl").read_text().splitlines() if l.strip()]
    dec: dict[int, float] = {}
    for r in rows:
        dec[r["seed"]] = r["final_coins"][r["candidate_seat"]] - r["final_coins"][r["opponent_seat"]]
    by_key: dict[tuple, list[float]] = {}
    for r in rows:
        d = r["final_coins"][r["candidate_seat"]] - r["final_coins"][r["opponent_seat"]]
        by_key.setdefault((r["seed"], r["repeat"]), []).append(d)
    identical = all(len(set(v)) == 1 for v in by_key.values())
    wins = sum(1 for d in dec.values() if d > 0)
    losses = sum(1 for d in dec.values() if d < 0)
    ties = sum(1 for d in dec.values() if d == 0)
    errs = sum(bool(r["candidate_error"]) or bool(r["opponent_error"])
               or bool(r["infrastructure_error"]) or bool(r["timed_out"]) for r in rows)
    print(f"\n--- holdout vs {tag.upper()} ---")
    print(f"  {len(rows)} games, {len(dec)} seeds, errors/timeouts {errs}, "
          f"seat-swap identical {identical}")
    print(f"  {wins}W-{losses}L-{ties}D  score rate {(wins + 0.5*ties)/max(1,len(dec)):.3f}")
    ms = list(dec.values())
    print(f"  mean margin {statistics.fmean(ms):+,.0f}  median {statistics.median(ms):+,.0f}  "
          f"range {min(ms):+,.0f}..{max(ms):+,.0f}")
    worst = min(dec.items(), key=lambda kv: kv[1])
    print(f"  worst single seed: {worst[0]} {worst[1]:+,.0f}")
    return {"games": len(rows), "seeds": len(dec), "wins": wins, "losses": losses,
            "ties": ties, "errors": errs, "seat_swap_identical": identical,
            "mean_margin": statistics.fmean(ms), "median_margin": statistics.median(ms),
            "worst_seed": worst[0], "worst_margin": worst[1], "per_seed": dec}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--opponents", default="v92,v50,v56")
    args = ap.parse_args()
    preflight()
    tags = args.opponents.split(",")
    for tag in tags:
        run(tag, args.workers)
    out = {}
    for tag in tags:
        out[tag] = summarize(tag)
    (HERE / "holdout_results.json").write_text(
        json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "per_seed"}
                    for k, v in out.items()}, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

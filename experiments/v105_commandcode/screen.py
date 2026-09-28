"""V105 paired screen on SPENT seeds: V105 vs the one-cow no-Yarn base, and both
vs V56 / V92 / V50.

Design. The experiment is paired, because the question is "what does the SECOND
cow add?". So every opponent is run twice:

  * V105  (two-cow candidate)  vs opponent
  * base  (one-cow no-Yarn)   vs opponent   <- matched control, same seeds, seats

and the reported effect is the per-(seed, opponent) difference
    delta = margin(V105 vs opp) - margin(base vs opp)
which cancels the opponent's own strength and isolates the second cow.

Seeds are SPENT only: 160001-160012 plus the 1500xx V56-loss seeds named in the
assignment. No protected fresh holdout (137501 / 170001 / 180001) is used, and
nothing here tunes on results -- the candidate hash is checked before the run and
replay-policy is `none` to keep disk usage low.

    .venv/bin/python experiments/v105_commandcode/screen.py --workers 2
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
BASE = ROOT / "experiments/v101_adaptive_swap/candidate_milk_sink_no_yarn.py"
CAND_SHA = "4488b26392b69fe416fceffc6325b3b4df94fa1897a6fe8f212cd9af162ed7e0"
BASE_SHA = "d166d2420440a0a96643c061b010c444f372a89e236e9c22a8417b4008b81763"

SPENT_SEEDS = sorted(set(
    list(range(160001, 160013)) +
    [150001, 150002, 150003, 150004, 150006, 150007,
     150009, 150010, 150011, 150013, 150014]
))
SPENT_SEED_SET = set(SPENT_SEEDS)
PROTECTED = set(range(137501, 137525)) | set(range(170001, 170025)) \
    | set(range(180001, 180025))
OPPONENTS = {
    "v92": ROOT / "experiments/v92_overflow_guard/candidate.py",
    "v50": ROOT / "experiments/v50_agent.py",
    "v56": ROOT / "agents/v56_agent.py",
}


def preflight(seeds: list[int]) -> None:
    """Refuse to run on hash drift or if any protected seed sneaks in."""
    bad = []
    clash = sorted(set(seeds) & PROTECTED)
    if clash:
        bad.append(f"PROTECTED SEED IN RANGE: {clash}")
    unknown = sorted(set(seeds) - SPENT_SEED_SET)
    if unknown:
        bad.append(f"seed outside the declared SPENT set: {unknown}")
    for path, want, name in ((CAND, CAND_SHA, "V105"), (BASE, BASE_SHA, "base")):
        got = hashlib.sha256(path.read_bytes()).hexdigest()
        if got != want:
            bad.append(f"{name} drifted: {got} != {want}")
    if bad:
        print("PREFLIGHT FAILED:", file=sys.stderr)
        for b in bad:
            print("  " + b, file=sys.stderr)
        raise SystemExit(2)
    print(f"preflight ok: V105 {CAND_SHA[:12]}  base {BASE_SHA[:12]}  "
          f"{len(seeds)} spent seeds, no protected seeds")


def run(agent: Path, opponent: str, outdir: Path, seeds: list[int], workers: int) -> None:
    """Run one arm sequentially. Raises on a nonzero exit or a short record count.

    Arms are run one after another on purpose: at a fixed total of 2 game workers
    there is no wall-time difference between running them concurrently at 1 each
    and sequentially at 2, so the simpler sequential form is kept.
    """
    cmd = [sys.executable, "-m", "simulation.tournament",
           "--candidate", str(agent), "--opponent", f"{opponent}={OPPONENTS[opponent]}",
           "--seeds", ",".join(str(s) for s in seeds),
           "--workers", str(workers), "--timeout", "1800",
           "--replay-policy", "none", "--output-dir", str(outdir)]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=86400)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "runner.log").write_text(proc.stdout + "\n" + proc.stderr, encoding="utf-8")
    if proc.returncode != 0:
        raise SystemExit(
            f"tournament failed for {agent.name} vs {opponent}: exit {proc.returncode}\n"
            f"{(outdir / 'runner.log').read_text()[-2000:]}")
    expected = 2 * len(seeds)
    got = len([l for l in (outdir / "games.jsonl").read_text().splitlines() if l.strip()])
    if got != expected:
        raise SystemExit(
            f"short record count for {agent.name} vs {opponent}: "
            f"expected {expected} (2 seats x {len(seeds)} seeds), got {got}")


def margins(outdir: Path) -> tuple[dict[int, float], int, int, bool]:
    rows = [json.loads(l) for l in (outdir / "games.jsonl").read_text().splitlines() if l.strip()]
    per: dict[int, float] = {}
    errors = 0
    pairs: dict[tuple, list[float]] = {}
    for r in rows:
        d = r["final_coins"][r["candidate_seat"]] - r["final_coins"][r["opponent_seat"]]
        per.setdefault(r["seed"], 0.0)
        per[r["seed"]] += d / 2.0
        pairs.setdefault((r["seed"], r["repeat"]), []).append(d)
        errors += bool(r["candidate_error"]) or bool(r["opponent_error"]) \
            or bool(r["infrastructure_error"]) or bool(r["timed_out"])
    stable = all(len(set(v)) == 1 for v in pairs.values())
    return per, len(rows), errors, stable


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--opponents", default="v56,v92,v50")
    ap.add_argument("--seeds", default=",".join(str(s) for s in SPENT_SEEDS),
                    help="subset of the declared SPENT seeds; preflight rejects "
                         "anything protected or undeclared")
    ap.add_argument("--stage", default="", help="suffix for the output dir")
    args = ap.parse_args()

    seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
    preflight(seeds)
    sfx = args.stage

    report: dict = {"candidate_sha": CAND_SHA, "base_sha": BASE_SHA,
                    "seeds": seeds, "opponents": {}}
    for opponent in args.opponents.split(","):
        run(CAND, opponent, HERE / "runs" / f"v105_vs_{opponent}{sfx}", seeds, args.workers)
        run(BASE, opponent, HERE / "runs" / f"base_vs_{opponent}{sfx}", seeds, args.workers)
        a, ag, aerr, astable = margins(HERE / "runs" / f"v105_vs_{opponent}{sfx}")
        b, bg, berr, bstable = margins(HERE / "runs" / f"base_vs_{opponent}{sfx}")
        common = sorted(set(a) & set(b))
        delta = {s: a[s] - b[s] for s in common}
        dvals = [delta[s] for s in common]
        pos = [d for d in dvals if d > 0]
        neg = [d for d in dvals if d < 0]
        worst_seed, worst = min(delta.items(), key=lambda kv: kv[1])
        print(f"\n=== vs {opponent.upper()} ({len(common)} spent seeds) ===")
        print(f"  V105 {ag} games err {aerr} seat-stable {astable}  "
              f"mean {statistics.fmean(a.values()):+,.0f}")
        print(f"  base {bg} games err {berr} seat-stable {bstable}  "
              f"mean {statistics.fmean(b.values()):+,.0f}")
        print(f"  PAIRED DELTA (V105 - base): mean {statistics.fmean(dvals):+,.0f}  "
              f"median {statistics.median(dvals):+,.0f}  "
              f"better {len(pos)} worse {len(neg)} tie {len(common)-len(pos)-len(neg)}")
        print(f"  worst delta: seed {worst_seed} {worst:+,.0f}")
        for s in common:
            print(f"    {s}  V105 {a[s]:+10,.0f}  base {b[s]:+10,.0f}  delta {delta[s]:+10,.0f}")
        report["opponents"][opponent] = {
            "v105_mean": statistics.fmean(a.values()), "base_mean": statistics.fmean(b.values()),
            "delta_mean": statistics.fmean(dvals), "delta_median": statistics.median(dvals),
            "delta_better": len(pos), "delta_worse": len(neg),
            "delta_worst_seed": worst_seed, "delta_worst": worst,
            "errors": aerr + berr,
            "per_seed": {str(s): {"v105": a[s], "base": b[s], "delta": delta[s]} for s in common},
        }
    out_name = f"screen_results{sfx}.json" if sfx else "screen_results.json"
    (HERE / out_name).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

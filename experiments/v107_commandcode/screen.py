"""V107 paired screen on SPENT seeds vs frozen V50 and V56, with matched control.

Design. V107 is compared to its own base, V50, on identical seeds and seats.
The opponent is fixed within each comparison, so the paired delta
    delta = margin(V107 vs OPP) - margin(V50 vs OPP)
cancels the opponent's own strength and isolates the one-cow no-Yarn swap.

Opponents:
  * V50 - the base. V107 vs V50 and V50 vs V50 self-play measure the swap's raw
    effect in a mirror.
  * V56 - the strongest known opponent, and the one the one-cow swap was
    previously shown (V101) to help on paired margin.

SPENT seeds only (160001-160012). No protected range (137501/170001/180001).
replay-policy none. Preflight re-checks the V50 and V107 hashes and refuses any
protected or undeclared seed. Nothing here tunes a threshold.

    .venv/bin/python experiments/v107_commandcode/screen.py --workers 4
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
V50 = ROOT / "experiments/v50_agent.py"
CAND_SHA = "7623988b6a1b2dff66759951f4843b5fd546ed1ded115597998817dc45953d0e"
V50_SHA = "e6b50128e023e3b9fafa1841e4cd520c5e581acb48e8628657585c18272eab2b"
V56 = ROOT / "agents/v56_agent.py"
V56_SHA = "d9e9670921b62afedfa8cbc7086d2a2ec19e153ee26006cef477eadd462bd19c"

SPENT_SEEDS = list(range(160001, 160013))
PROTECTED = set(range(137501, 137525)) | set(range(170001, 170025)) \
    | set(range(180001, 180025))


def preflight(seeds: list[int]) -> None:
    bad = []
    clash = sorted(set(seeds) & PROTECTED)
    if clash:
        bad.append(f"PROTECTED SEED: {clash}")
    for path, want, name in ((CAND, CAND_SHA, "V107"), (V50, V50_SHA, "V50"),
                             (V56, V56_SHA, "V56")):
        got = hashlib.sha256(path.read_bytes()).hexdigest()
        if got != want:
            bad.append(f"{name} drifted: {got} != {want}")
    if bad:
        print("PREFLIGHT FAILED:", file=sys.stderr)
        for b in bad:
            print("  " + b, file=sys.stderr)
        raise SystemExit(2)
    print(f"preflight ok: V107 {CAND_SHA[:12]}  V50 {V50_SHA[:12]}  V56 {V56_SHA[:12]}  "
          f"{len(seeds)} spent seeds, no protected")


def run(candidate: Path, opponent: Path, outdir: Path, seeds: list[int], workers: int) -> None:
    cmd = [sys.executable, "-m", "simulation.tournament",
           "--candidate", str(candidate), "--opponent", f"opp={opponent}",
           "--seeds", ",".join(str(s) for s in seeds),
           "--workers", str(workers), "--timeout", "1800",
           "--replay-policy", "none", "--output-dir", str(outdir)]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=86400)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "runner.log").write_text(proc.stdout + "\n" + proc.stderr, encoding="utf-8")
    if proc.returncode != 0:
        raise SystemExit(f"tournament failed {candidate.name} vs {opponent.name}: "
                         f"exit {proc.returncode}\n{(outdir / 'runner.log').read_text()[-2000:]}")
    got = len([l for l in (outdir / "games.jsonl").read_text().splitlines() if l.strip()])
    expect = 2 * len(seeds)
    if got != expect:
        raise SystemExit(f"short record count {candidate.name} vs {opponent.name}: "
                         f"expected {expect} got {got}")


def load(outdir: Path):
    rows = [json.loads(l) for l in (outdir / "games.jsonl").read_text().splitlines() if l.strip()]
    per: dict[int, float] = {}
    errs = 0
    pairs: dict[tuple, list[float]] = {}
    for r in rows:
        d = r["final_coins"][r["candidate_seat"]] - r["final_coins"][r["opponent_seat"]]
        per[r["seed"]] = per.get(r["seed"], 0.0) + d / 2.0
        pairs.setdefault((r["seed"], r["repeat"]), []).append(d)
        errs += bool(r["candidate_error"]) or bool(r["opponent_error"]) \
            or bool(r["infrastructure_error"]) or bool(r["timed_out"])
    stable = all(len(set(v)) == 1 for v in pairs.values())
    return per, len(rows), errs, stable


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--seeds", default=",".join(str(s) for s in SPENT_SEEDS))
    args = ap.parse_args()
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
    preflight(seeds)

    # V107 vs V50 and V56; V50 self (control) and V50 vs V56 (matched control).
    jobs = [
        ("v107_vs_v50", CAND, V50),
        ("v107_vs_v56", CAND, V56),
        ("v50_self", V50, V50),
        ("v50_vs_v56", V50, V56),
    ]
    for name, cand, opp in jobs:
        run(cand, opp, HERE / "runs" / name, seeds, args.workers)
        print(f"  done {name}", flush=True)

    res = {}
    for name, _, _ in jobs:
        per, ng, errs, stable = load(HERE / "runs" / name)
        res[name] = {"per_seed": per, "games": ng, "errors": errs, "seat_stable": stable}

    def show(label, a, b):
        common = sorted(set(a) & set(b))
        delta = {s: a[s] - b[s] for s in common}
        dv = [delta[s] for s in common]
        pos = [d for d in dv if d > 0]
        neg = [d for d in dv if d < 0]
        ws, ls = min(delta.items(), key=lambda kv: kv[1])
        print(f"\n=== {label} ({len(common)} seeds) ===")
        print(f"  mean A {statistics.fmean(a[s] for s in common):+,.0f}   "
              f"mean B {statistics.fmean(b[s] for s in common):+,.0f}")
        print(f"  PAIRED DELTA (A-B): mean {statistics.fmean(dv):+,.0f}  "
              f"median {statistics.median(dv):+,.0f}  better {len(pos)} worse {len(neg)} "
              f"tie {len(common)-len(pos)-len(neg)}  worst seed {ws} {delta[ws]:+,.0f}")
        return {"delta_mean": statistics.fmean(dv), "delta_median": statistics.median(dv),
                "better": len(pos), "worse": len(neg),
                "worst_seed": ws, "worst": delta[ws]}

    out = {
        "v107_vs_v50_delta": show("V107 - V50control  (vs V50 opponent)",
                                  res["v107_vs_v50"]["per_seed"], res["v50_self"]["per_seed"]),
        "v107_vs_v56_delta": show("V107 - V50control  (vs V56 opponent)",
                                  res["v107_vs_v56"]["per_seed"], res["v50_vs_v56"]["per_seed"]),
    }
    for name in res:
        print(f"  {name}: errors {res[name]['errors']} seat-stable {res[name]['seat_stable']} "
              f"games {res[name]['games']}")
    (HERE / "screen_results.json").write_text(json.dumps(
        {"candidate_sha": CAND_SHA, "seeds": seeds,
         **{k: {kk: vv for kk, vv in v.items() if kk != 'per_seed'} for k, v in res.items()},
         "deltas": out}, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

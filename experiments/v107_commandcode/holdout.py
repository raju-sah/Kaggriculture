"""Run the V107 precommitted fresh holdout (190001-190024) exactly once.

Preflight refuses to start unless the candidate, V50 and V56 hashes still match
GATE.md and no seed outside 190001-190024 is requested. Six arms: V107 and the
V50 control against each of V92 (primary), V56 and V50. replay-policy none.

    .venv/bin/python experiments/v107_commandcode/holdout.py --workers 4
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
V92 = ROOT / "experiments/v92_overflow_guard/candidate.py"
V56 = ROOT / "agents/v56_agent.py"

HASHES = {
    "V107": (CAND, "7623988b6a1b2dff66759951f4843b5fd546ed1ded115597998817dc45953d0e"),
    "V50": (V50, "e6b50128e023e3b9fafa1841e4cd520c5e581acb48e8628657585c18272eab2b"),
    "V56": (V56, "d9e9670921b62afedfa8cbc7086d2a2ec19e153ee26006cef477eadd462bd19c"),
}
SEEDS = list(range(190001, 190025))
ALLOWED = set(SEEDS)


def preflight() -> None:
    bad = []
    for name, (path, want) in HASHES.items():
        got = hashlib.sha256(path.read_bytes()).hexdigest()
        if got != want:
            bad.append(f"{name} drifted: {got} != {want}")
    if set(SEEDS) - ALLOWED:
        bad.append("seed outside the frozen range")
    if bad:
        print("PREFLIGHT FAILED:", file=sys.stderr)
        for b in bad:
            print("  " + b, file=sys.stderr)
        raise SystemExit(2)
    print(f"preflight ok: hashes match GATE.md, seeds {SEEDS[0]}-{SEEDS[-1]} frozen")


def run(cand: Path, opp: Path, out: Path, workers: int) -> None:
    cmd = [sys.executable, "-m", "simulation.tournament",
           "--candidate", str(cand), "--opponent", f"opp={opp}",
           "--seeds", ",".join(str(s) for s in SEEDS),
           "--workers", str(workers), "--timeout", "1800",
           "--replay-policy", "none", "--output-dir", str(out)]
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=172800)
    out.mkdir(parents=True, exist_ok=True)
    (out / "runner.log").write_text(p.stdout + "\n" + p.stderr)
    if p.returncode != 0:
        raise SystemExit(f"fail {cand.name} vs {opp.name}: {(out / 'runner.log').read_text()[-2000:]}")
    got = len([l for l in (out / "games.jsonl").read_text().splitlines() if l.strip()])
    if got != 2 * len(SEEDS):
        raise SystemExit(f"short record count {cand.name} vs {opp.name}: expected "
                         f"{2 * len(SEEDS)} got {got}")


def load(name: str):
    rows = [json.loads(l) for l in (HERE / "runs" / name / "games.jsonl").read_text().splitlines() if l.strip()]
    per: dict[int, float] = {}
    res: dict[int, str] = {}
    pairs: dict[tuple, list[float]] = {}
    errs = 0
    for r in rows:
        d = r["final_coins"][r["candidate_seat"]] - r["final_coins"][r["opponent_seat"]]
        per[r["seed"]] = per.get(r["seed"], 0.0) + d / 2.0
        res.setdefault(r["seed"], r["candidate_result"])
        pairs.setdefault((r["seed"], r["repeat"]), []).append(d)
        errs += bool(r["candidate_error"]) or bool(r["opponent_error"]) \
            or bool(r["infrastructure_error"]) or bool(r["timed_out"])
    stable = all(len(set(v)) == 1 for v in pairs.values())
    return per, res, errs, stable, len(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    preflight()
    arms = [("v107_vs_v92", CAND, V92), ("v50_vs_v92", V50, V92),
            ("v107_vs_v56", CAND, V56), ("v50_vs_v56", V50, V56),
            ("v107_vs_v50", CAND, V50), ("v50_self", V50, V50)]
    for name, c, o in arms:
        run(c, o, HERE / "runs" / name, args.workers)
        print(f"  done {name}", flush=True)

    out: dict = {"candidate_sha": HASHES["V107"][1], "seeds": SEEDS}
    for opp, (a, b) in (("v92", ("v107_vs_v92", "v50_vs_v92")),
                        ("v56", ("v107_vs_v56", "v50_vs_v56")),
                        ("v50", ("v107_vs_v50", "v50_self"))):
        pa, ra, ea, sa, ga = load(a)
        pb, rb, eb, sb, gb = load(b)
        com = sorted(set(pa) & set(pb))
        delta = {s: pa[s] - pb[s] for s in com}
        dv = [delta[s] for s in com]
        pos = [d for d in dv if d > 0]
        neg = [d for d in dv if d < 0]
        flips = [s for s in com if rb.get(s) == "win" and ra.get(s) == "loss"]
        wsv, wv = min(delta.items(), key=lambda kv: kv[1])
        out[opp] = {
            "v107_mean": statistics.fmean(pa[s] for s in com),
            "v50_mean": statistics.fmean(pb[s] for s in com),
            "delta_mean": statistics.fmean(dv), "delta_median": statistics.median(dv),
            "better": len(pos), "worse": len(neg), "tie": len(com) - len(pos) - len(neg),
            "worst_seed": wsv, "worst": delta[wsv],
            "win_to_loss_flips": flips, "errors": ea + eb,
            "seat_stable_v107": sa, "seat_stable_v50": sb,
            "games": ga + gb,
        }
    (HERE / "holdout_results.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    for opp in ("v92", "v56", "v50"):
        d = out[opp]
        print(f"\n=== {opp.upper()} ===")
        print(f"  V107 mean {d['v107_mean']:+,.0f}   V50 control mean {d['v50_mean']:+,.0f}")
        print(f"  PAIRED delta mean {d['delta_mean']:+,.0f} median {d['delta_median']:+,.0f} "
              f"better {d['better']} worse {d['worse']} tie {d['tie']}  "
              f"worst {d['worst_seed']} {d['worst']:+,.0f}")
        print(f"  win->loss flips {d['win_to_loss_flips']}  errors {d['errors']}  "
              f"seat-stable v107 {d['seat_stable_v107']} v50 {d['seat_stable_v50']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

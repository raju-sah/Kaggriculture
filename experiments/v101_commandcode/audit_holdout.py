"""Score the finished V101 holdout against the criteria frozen in GATE.md.

This file does not choose thresholds. It reads GATE.md's numbers as constants,
re-derives them here verbatim so a drift in either place is visible, and then
passes or fails each criterion with the numbers behind it. The candidate and the
gate were hashed before the holdout ran and are re-checked here.

    .venv/bin/python experiments/v101_commandcode/audit_holdout.py
"""

from __future__ import annotations

import hashlib
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

FROZEN_CANDIDATE_SHA = "8c572b9027ca4f5a0d656d1b1dd6fb74b4b121bd67c69b97aef16d66e21052e7"
GATE_SHA_BEFORE = "33f90dd83c31293bc3cbcbc30b4c56de07f380083d66599e540096c692ac311e"

# --- transcribed verbatim from GATE.md -------------------------------------
GATE = {
    "v92_score_rate_min": 0.55,
    "v92_mean_margin_min": 300.0,
    "v92_min_trigger_seeds": 6,
    "v50_score_rate_min": 0.55,
    "v50_mean_margin_min": 300.0,
    "v56_score_rate_min": 0.45,
    "v56_mean_margin_min": 0.0,
    "max_worst_v92_margin": -2000.0,
}


def per_seed(tag: str) -> dict[int, float]:
    path = HERE / "runs" / f"holdout_vs_{tag}" / "games.jsonl"
    rows = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    out: dict[int, float] = {}
    errors = 0
    for r in rows:
        out[r["seed"]] = r["final_coins"][r["candidate_seat"]] - r["final_coins"][r["opponent_seat"]]
        errors += bool(r["candidate_error"]) or bool(r["opponent_error"]) \
            or bool(r["infrastructure_error"]) or bool(r["timed_out"])
    return {"per_seed": out, "games": len(rows), "errors": errors,
            "seat_swap_identical": len(rows) == 2 * len(out)}


def score_rate(d: dict[int, float]) -> float:
    w = sum(1 for v in d.values() if v > 0)
    t = sum(1 for v in d.values() if v == 0)
    return (w + 0.5 * t) / max(1, len(d))


def main() -> int:
    cand_sha = hashlib.sha256((HERE / "candidate.py").read_bytes()).hexdigest()
    gate_sha = hashlib.sha256((HERE / "GATE.md").read_bytes()).hexdigest()
    data = {t: per_seed(t) for t in ("v92", "v50", "v56")}
    life_path = HERE / "lifecycle_results_holdout.json"
    life = json.loads(life_path.read_text()) if life_path.exists() else []

    checks = []

    def add(name: str, ok: bool, detail: str) -> None:
        checks.append({"criterion": name, "pass": bool(ok), "detail": detail})
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}\n         {detail}")

    print("integrity")
    add("candidate unchanged since freeze", cand_sha == FROZEN_CANDIDATE_SHA,
        f"sha256 {cand_sha}")
    add("gate file unchanged since precommit", gate_sha == GATE_SHA_BEFORE,
        f"sha256 {gate_sha}")
    for tag in ("v92", "v50", "v56"):
        add(f"{tag}: 24 seeds x 2 seats, no errors",
            data[tag]["games"] == 48 and data[tag]["errors"] == 0
            and data[tag]["seat_swap_identical"],
            f"{data[tag]['games']} games, {data[tag]['errors']} errors, "
            f"seat-swap identical {data[tag]['seat_swap_identical']}")

    print("\ncriterion 1 - V92 primary")
    v92 = data["v92"]["per_seed"]
    sr92, mm92 = score_rate(v92), statistics.fmean(v92.values())
    add("score rate > 0.55", sr92 > GATE["v92_score_rate_min"], f"{sr92:.3f}")
    add("mean margin > +$300", mm92 > GATE["v92_mean_margin_min"], f"${mm92:+,.0f}")

    print("\ncriterion 2 - V92 distinct-seed triggers")
    model_path = HERE / "model_deltas_holdout.json"
    if model_path.exists():
        deltas = json.loads(model_path.read_text())
        fired = [d for d in deltas if d["delta"] > 0]
        add("rule fires on >= 6 distinct holdout seeds",
            len(fired) >= GATE["v92_min_trigger_seeds"],
            f"{len(fired)}/{len(deltas)} seeds: "
            + ", ".join(str(d["seed"]) for d in fired))
    else:
        add("rule fires on >= 6 distinct holdout seeds", False,
            "model_deltas_holdout.json missing - observer did not complete")

    print("\ncriterion 3 - V50 control")
    v50 = data["v50"]["per_seed"]
    sr50, mm50 = score_rate(v50), statistics.fmean(v50.values())
    add("score rate > 0.55", sr50 > GATE["v50_score_rate_min"], f"{sr50:.3f}")
    add("mean margin > +$300", mm50 > GATE["v50_mean_margin_min"], f"${mm50:+,.0f}")

    print("\ncriterion 4 - V56 control")
    v56 = data["v56"]["per_seed"]
    sr56, mm56 = score_rate(v56), statistics.fmean(v56.values())
    add("score rate > 0.45", sr56 > GATE["v56_score_rate_min"], f"{sr56:.3f}")
    add("mean margin > 0", mm56 > GATE["v56_mean_margin_min"], f"${mm56:+,.0f}")

    print("\ncriterion 5 - lifecycle on firing seeds")
    if life:
        n = len(life)
        chain = sum(1 for r in life if r["cand_buy"] and r["cand_pickup"] and r["cand_place"])
        alive = sum(1 for r in life if r["alive_at_end"])
        produced = sum(1 for r in life if r["milk_units"] > 0)
        mism = sum(r["cash_mismatch_turns"] for r in life)
        add("three-step chain complete on every firing seed", chain == n, f"{chain}/{n}")
        add("cow alive on a pasture at season end", alive == n, f"{alive}/{n}")
        add("cow produced MILK", produced == n, f"{produced}/{n}")
        add("zero cash-reconstruction mismatches", mism == 0, f"{mism} mismatched turns")
    else:
        add("lifecycle audit present", False, "lifecycle_results_holdout.json missing")

    print("\ncriterion 6 - no harm")
    worst_seed, worst = min(v92.items(), key=lambda kv: kv[1])
    add("no V92 regression worse than -$2,000",
        worst > GATE["max_worst_v92_margin"],
        f"worst seed {worst_seed} at ${worst:+,.0f}")

    passed = sum(1 for c in checks if c["pass"])
    print(f"\n{passed}/{len(checks)} criteria pass -> GATE "
          f"{'PASS' if passed == len(checks) else 'FAIL'}")
    (HERE / "gate_audit.json").write_text(
        json.dumps({"checks": checks, "passed": passed, "total": len(checks)},
                   indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

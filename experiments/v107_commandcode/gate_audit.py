#!/usr/bin/env python3
"""Score the frozen V107 gate against the fresh 190001-190024 holdout data.

Criterion 4 (lifecycle) needs replays, which the holdout ran with
--replay-policy none; it is reported as needing a separate evidence path rather
than silently marked met.
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"
EXPECTED = list(range(190001, 190025))


def load(name):
    p = RUNS / name / "games.jsonl"
    if not p.exists():
        return None
    rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    marg, res, pair, errs = {}, {}, {}, 0
    for i, r in enumerate(rows):
        marg[r["seed"]] = marg.get(r["seed"], 0.0) + (
            r["final_coins"][r["candidate_seat"]] - r["final_coins"][r["opponent_seat"]]
        ) / 2
        # Official W/L is per GAME (2 games per seed), not per seed.  Key by game
        # index so the second seat's result is not silently dropped.
        res[i] = r["candidate_result"]
        pair.setdefault(r["seed"], []).append(r["candidate_result"])
        errs += bool(r.get("candidate_error") or r.get("opponent_error")
                     or r.get("infrastructure_error") or r.get("timed_out"))
    return {"marg": marg, "res": res, "pair": pair, "games": len(rows), "errors": errs}


def paired(a, b):
    seeds = sorted(set(a["marg"]) & set(b["marg"]))
    return {s: a["marg"][s] - b["marg"][s] for s in seeds}


def wl(res):
    """Official W/L/D over every GAME in a run (2 games per seed)."""
    vals = list(res.values())
    w = sum(1 for v in vals if v == "win")
    l_ = sum(1 for v in vals if v == "loss")
    return w, l_, len(vals) - w - l_


def score_rate(res):
    w, l_, d = wl(res)
    return (w + 0.5 * d) / len(res)


def seed_results(per_seed_pair):
    """Reduce the two games of a seed to one verdict: win / loss / mixed."""
    out = {}
    for s, outcomes in per_seed_pair.items():
        if all(o == "win" for o in outcomes):
            out[s] = "win"
        elif all(o == "loss" for o in outcomes):
            out[s] = "loss"
        else:
            out[s] = "mixed"
    return out


A92, B92 = load("v107_vs_v92"), load("v50_vs_v92")
A56, B56 = load("v107_vs_v56"), load("v50_vs_v56")
A50 = load("v107_vs_v50")

checks = []

# 1 primary
d92 = paired(A92, B92)
m92 = statistics.fmean(d92.values())
pos92 = sum(1 for v in d92.values() if v > 0)
checks.append(("1  V92 paired mean > +300", m92 > 300, f"{m92:+,.0f}"))
checks.append(("1b >=13/24 seeds positive", pos92 >= 13, f"{pos92}/24"))

# 2 no harm (seed-level verdicts: both seats must agree to call win/loss)
sa92, sb92 = seed_results(A92["pair"]), seed_results(B92["pair"])
flips = [s for s in d92 if sb92[s] == "win" and sa92[s] == "loss"]
w_a, l_a, _ = wl(A92["res"])
w_b, l_b, _ = wl(B92["res"])
checks.append(("2  zero V92 win->loss flips", not flips, str(flips or "none")))
checks.append(("2b V107 W/L not worse vs V92", w_a >= w_b and l_a <= l_b,
               f"V107 {w_a}W-{l_a}L vs V50 {w_b}W-{l_b}L (games)"))

# 3 V56 control
d56 = paired(A56, B56)
m56 = statistics.fmean(d56.values())
abs56 = statistics.fmean(A56["marg"].values())
score56 = score_rate(A56["res"])
w56, l56, t56 = wl(A56["res"])
cw56, cl56, _ = wl(B56["res"])
checks.append(("3a V56 paired mean not < -100", m56 >= -100, f"{m56:+,.0f}"))
checks.append(("3b V56 score >= 0.50", score56 >= 0.50,
               f"{score56:.3f} ({w56}W-{l56}L-{t56}D; V50 control {score_rate(B56['res']):.3f} {cw56}W-{cl56}L)"))
checks.append(("3c V56 abs mean not < -1500", abs56 >= -1500, f"{abs56:+,.0f}"))

# 4 lifecycle: no replays retained in this holdout
checks.append(("4  lifecycle on firing seeds", None,
               "not audited (replay-policy none); see evidence note"))

# 5 trigger breadth.  In the V107-vs-V50 self-mirror both seats play the same
# world, so a non-firing seed is an exact tie (V107 literally *is* V50 there).
# A non-zero margin therefore means the swap fired.
mirror = A50["marg"]
fired = sum(1 for v in mirror.values() if abs(v) >= 1.0)
checks.append(("5  >=8/24 seeds triggered", fired >= 8, f"{fired}/24"))

# 6 seat stability
unstable = []
for nm in ("v107_vs_v92", "v107_vs_v56", "v107_vs_v50"):
    rows = [json.loads(l) for l in (RUNS / nm / "games.jsonl").read_text().splitlines() if l.strip()]
    per = {}
    for r in rows:
        per.setdefault(r["seed"], {})[r["candidate_seat"]] = (
            r["final_coins"][r["candidate_seat"]] - r["final_coins"][r["opponent_seat"]])
    for s, m in per.items():
        if len(m) == 2 and abs(m[0] - m[1]) > 1.0:
            unstable.append((nm, s, round(m[0]), round(m[1])))
checks.append(("6  seat-stability recorded", len(unstable) <= 6, f"{len(unstable)} unstable seeds"))

# 7 tail
worst = min(d92.items(), key=lambda kv: kv[1])
tail = min(min(d92.values()), min(d56.values()))
checks.append(("7  no paired delta < -2000", tail > -2000, f"worst {tail:+,.0f} (seed {worst[0]} vs V92)"))

# 8 errors
tot_err = sum(x["errors"] for x in (A92, B92, A56, B56, A50) if x)
checks.append(("8  zero errors/timeouts", tot_err == 0, str(tot_err)))

print(f"V107 fresh holdout 190001-190024 vs frozen GATE.md\n")
for label, ok, detail in checks:
    mark = "PASS" if ok else ("N/A " if ok is None else "FAIL")
    print(f"  [{mark}] {label:34s} {detail}")
mandatory = [c for c in checks if c[0][0] in "12378" and c[0][1] != "b"]
print(f"\nmandatory (1,2,3,7,8): "
      f"{'ALL PASS' if all(c[1] for c in mandatory) else 'FAIL'}")
print(f"games: " + ", ".join(f"{n}={load(n)['games']}" for n in
      ("v107_vs_v92", "v50_vs_v92", "v107_vs_v56", "v50_vs_v56", "v107_vs_v50")))
if unstable:
    print("\nseat-unstable (opponent-side; both arms share the pair):")
    for u in unstable[:8]:
        print("   ", u)
print("\nV92 paired per seed:")
for s in sorted(d92):
    print(f"   {s}: {d92[s]:+8,.0f}   (V107 {A92['marg'][s]:+8,.0f} | V50 {B92['marg'][s]:+8,.0f})")

out = HERE / "holdout_results.json"
out.write_text(json.dumps({
    "seeds": EXPECTED,
    "checks": [{"label": l, "ok": o, "detail": d} for l, o, d in checks],
    "v92_paired": {str(k): round(v) for k, v in d92.items()},
    "v56_paired": {str(k): round(v) for k, v in d56.items()},
    "summary": {
        "v92_paired_mean": round(m92), "v92_positive": pos92,
        "v56_paired_mean": round(m56), "v56_abs_mean": round(abs56),
        "v56_score_rate": round(score56, 3),
        "seat_unstable": len(unstable), "errors": tot_err,
    },
}, indent=2))
print(f"\nwrote {out}")

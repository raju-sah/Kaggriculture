"""Run V72 macro screen on spent seeds and gated confirmation."""
from __future__ import annotations
import concurrent.futures
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
manifest = json.loads((HERE / "manifest.json").read_text())
py = sys.executable
all_variants = manifest["variants"]
excluded = set(manifest["excluded_from_finalist_selection"])
variants = [v for v in all_variants if v["name"] not in excluded]

def tournament(variant, opponent, seeds, phase):
    out = HERE / "runs" / f"{phase}_{variant['name']}"
    cmd = [py, "-m", "simulation.tournament", "--candidate", str(ROOT / variant["path"]),
           "--opponent", f"{opponent}={ROOT / manifest['opponents'][opponent]}",
           "--seeds", ",".join(map(str, seeds)), "--workers", "2", "--timeout", "120",
           "--replay-policy", "none", "--output-dir", str(out)]
    started = time.perf_counter()
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    out.mkdir(parents=True, exist_ok=True)
    (out / "stdout.json.txt").write_text(p.stdout)
    (out / "stderr.log").write_text(p.stderr)
    if p.returncode:
        raise RuntimeError(f"{variant['name']} vs {opponent} failed rc={p.returncode}; see {out}")
    report = json.loads((out / "report.json").read_text())
    games = report["games"]
    cash, margins, production = [], [], []
    production_ops = ("PLANT", "WATER", "HARVEST", "FERTILIZE", "FEED", "CARE", "COLLECT_FERTILIZER")
    by_seed = {}
    for g in games:
        cs = g["candidate_seat"]
        coins = g["final_coins"]
        actions = g["action_counts"][cs]
        direct = sum(actions[actor].get(op, 0) for actor in ("farmer", "hands") for op in production_ops)
        c = coins[cs]
        margin = c - coins[1-cs]
        cash.append(c); margins.append(margin); production.append(direct)
        by_seed.setdefault(str(g["seed"]), {"cash": [], "margin": [], "production": []})
        by_seed[str(g["seed"])]["cash"].append(c)
        by_seed[str(g["seed"])]["margin"].append(margin)
        by_seed[str(g["seed"])]["production"].append(direct)
    row = {
        "variant": variant["name"], "opponent": opponent, "phase": phase,
        "games": len(games), "wins": report["summary"]["wins"],
        "errors": report["summary"]["candidate_errors"] + report["summary"]["infrastructure_errors"],
        "mean_candidate_cash": sum(cash)/len(cash), "mean_margin": sum(margins)/len(margins),
        "mean_direct_production_actions": sum(production)/len(production),
        "per_seed": {k:{m:sum(vals)/len(vals) for m,vals in v.items()} for k,v in by_seed.items()},
        "mean_game_runtime_seconds": report["summary"]["mean_runtime_seconds"],
        "wall_seconds": time.perf_counter()-started,
        "candidate_sha256": variant["sha256"],
        "report": str((out / "report.json").relative_to(ROOT)),
    }
    print(json.dumps(row), flush=True)
    return row

started = time.perf_counter()
rows = []
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
    fs = [ex.submit(tournament, v, "V56", manifest["screen_seeds"], "screen_v56") for v in variants]
    for f in concurrent.futures.as_completed(fs): rows.append(f.result())
rows.sort(key=lambda r: r["variant"])
# On the exact same two spent seeds, V70 averaged $58,394 cash and -$80,216.5
# margin versus V56, with 1,393.5 direct production actions/match.
base_cash, base_margin, base_prod = 58394.0, -80216.5, 1393.5
for r in rows:
    r["cash_lift_vs_v70_same_seeds"] = r["mean_candidate_cash"] - base_cash
    r["margin_lift_vs_v70_same_seeds"] = r["mean_margin"] - base_margin
    r["production_lift_vs_v70_same_seeds"] = r["mean_direct_production_actions"] - base_prod
screen_path = HERE / "screen_results.json"
screen_path.write_text(json.dumps({"screen_wall_seconds":time.perf_counter()-started,"rows":rows},indent=2)+"\n")
shortlist = [r for r in rows if r["errors"] == 0 and r["cash_lift_vs_v70_same_seeds"] >= 2000 and r["margin_lift_vs_v70_same_seeds"] >= 0 and r["production_lift_vs_v70_same_seeds"] >= 0]
shortlist.sort(key=lambda r:r["cash_lift_vs_v70_same_seeds"]+r["margin_lift_vs_v70_same_seeds"],reverse=True)
control = []
if shortlist:
    best = shortlist[0]
    variant = next(v for v in variants if v["name"] == best["variant"])
    # The first and only untouched-by-this-variant screen seed, 92804, confirms
    # both cash/margin vs V56 and paired local behavior vs frozen V70.
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        fs = [ex.submit(tournament, variant, opponent, [manifest["confirm_seed"]], "confirm_"+opponent.lower()) for opponent in ("V56", "V70")]
        for f in concurrent.futures.as_completed(fs): control.append(f.result())
(HERE / "control_results.json").write_text(json.dumps({"rows":control},indent=2)+"\n")
print(json.dumps({"screen_wall_seconds":time.perf_counter()-started,"shortlist":shortlist,"confirm":control},indent=2))

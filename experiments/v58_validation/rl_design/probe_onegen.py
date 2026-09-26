"""One cheap CEM-style population probe on a single development seed."""
from __future__ import annotations
import concurrent.futures
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).with_name("candidate.py")
OUT = Path(__file__).with_name("probe95100")
V50 = ROOT / "experiments/v50_agent.py"
CONFIGS = [
    {"crop_target": 8, "herd_target": 1, "staff_target": 3, "cash_reserve": 700, "wheat_reserve": 2},
    {"crop_target": 8, "herd_target": 3, "staff_target": 6, "cash_reserve": 700, "wheat_reserve": 3},
    {"crop_target": 14, "herd_target": 2, "staff_target": 7, "cash_reserve": 700, "wheat_reserve": 3},
    {"crop_target": 14, "herd_target": 4, "staff_target": 7, "cash_reserve": 300, "wheat_reserve": 4},
]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def materialize(i, params):
    target = OUT / "candidates" / f"probe{i}.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    src = BASE.read_text()
    block = "PARAMS = {\n" + ",\n".join(f'    "{k}": {v}' for k, v in params.items()) + "\n}"
    src, n = re.subn(r"PARAMS = \{.*?\n\}", block, src, count=1, flags=re.S)
    if n != 1:
        raise RuntimeError("could not replace parameter block")
    target.write_text(src)
    return target

def run_one(i, params, candidate):
    out = OUT / f"candidate{i}"
    command = [sys.executable, "simulation/tournament.py", "--candidate", str(candidate),
               "--opponent", f"v50={V50}", "--seed", "95100", "--workers", "1",
               "--timeout", "120", "--replay-policy", "all", "--output-dir", str(out)]
    proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    report_path = out / "report.json"
    result = json.loads(report_path.read_text()) if report_path.exists() else None
    if proc.returncode and result is None:
        raise RuntimeError(f"config {i} failed: {proc.stdout}\n{proc.stderr}")
    records = result.get("games", []) if result else []
    candidate_rows=[]
    for game in records:
        seat=int(game["candidate_seat"])
        coins=game["final_coins"] or [None,None]
        candidate_rows.append({"seat":seat,"coins":coins[seat],"opponent_coins":coins[1-seat],"margin":coins[seat]-coins[1-seat],"ok":game.get("ok"),"error":game.get("candidate_error"),"runtime":game.get("runtime_seconds")})
    return {"id":f"probe{i}","params":params,"candidate_path":str(candidate),"candidate_sha256":sha(candidate),"exit_code":proc.returncode,"stdout_tail":proc.stdout[-500:],"games":candidate_rows,"mean_coins":sum(x["coins"] for x in candidate_rows if x["coins"] is not None)/max(1,len(candidate_rows)),"mean_margin":sum(x["margin"] for x in candidate_rows)/max(1,len(candidate_rows)),"no_errors":all(x["ok"] and not x["error"] for x in candidate_rows)}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    manifest={"seeds":[95100],"opponents":{"v50":str(V50),"v50_sha256":sha(V50)},"seat_orders":[0,1],"workers_cap":4,"purpose":"one-generation structure/throughput screening; no confirmation selection","configs":[]}
    inputs=[]
    for i,p in enumerate(CONFIGS):
        c=materialize(i,p);inputs.append((i,p,c))
        manifest["configs"].append({"id":f"probe{i}","params":p,"path":str(c),"sha256":sha(c)})
    (OUT/"plan.json").write_text(json.dumps(manifest,indent=2)+"\n")
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(lambda x:run_one(*x),inputs))
    results.sort(key=lambda r:r["id"])
    selection=max(results,key=lambda r:(r["no_errors"],r["mean_margin"],r["mean_coins"],r["id"]))
    report={"plan":manifest,"results":results,"selected_for_structure_review":selection["id"],"selection_rule":"no errors, then mean coin margin, then own coins; one seed only and not confirmation","holdout_93000_93049_used":False}
    (OUT/"results.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"results":[{"id":r["id"],"params":r["params"],"mean_coins":r["mean_coins"],"mean_margin":r["mean_margin"],"no_errors":r["no_errors"]} for r in results],"selected":selection["id"]},indent=2))

if __name__=="__main__":main()

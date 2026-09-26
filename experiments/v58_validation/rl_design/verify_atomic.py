"""Spent-seed verification of aggregate atomic seed planning repair."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
BASE=HERE/'candidate.py'; OUT=HERE/'verify95100';PARAMS={'crop_target':14,'herd_target':2,'staff_target':7,'cash_reserve':700,'wheat_reserve':3}
source=BASE.read_text();old=re.search(r'PARAMS = \{.*?\n\}',source,re.S)
if not old:raise SystemExit('parameter block not found')
block='PARAMS = {\n'+',\n'.join(f'    "{k}": {v}' for k,v in PARAMS.items())+'\n}'
source=source[:old.start()]+block+source[old.end():]
OUT.mkdir(parents=True,exist_ok=True);cand=OUT/'candidate.py';cand.write_text(source)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
plan={'purpose':'One spent-seed verification of aggregate simultaneous PLANT seed-demand mask on the prior crop14/herd2/staff7 vector.','seed':95100,'seats':[0,1],'opponent':str(ROOT/'experiments/v50_agent.py'),'opponent_sha256':sha(ROOT/'experiments/v50_agent.py'),'candidate':str(cand),'candidate_sha256':sha(cand),'base_source_sha256':sha(BASE),'params':PARAMS,'change':'aggregate PLANT request cap prevents all-per-crop atomic engine rejection','fresh_seeds_used':0,'final_holdout_used':False}
(OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
cmd=[sys.executable,'simulation/tournament.py','--candidate',str(cand),'--opponent',f'v50={ROOT/"experiments/v50_agent.py"}','--seed','95100','--workers','2','--timeout','120','--replay-policy','all','--output-dir',str(OUT/'games')]
p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
(OUT/'stdout.log').write_text(p.stdout+'\nSTDERR\n'+p.stderr)
print(p.stdout)
if p.returncode:raise SystemExit(p.returncode)

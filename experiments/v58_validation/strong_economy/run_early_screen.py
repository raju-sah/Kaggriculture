"""Execute the frozen, 2-seed early-futility screen once (max 3 workers)."""
from __future__ import annotations
import csv,hashlib,json,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
PLAN_PATH=HERE/'early_futility_plan.json'
PLAN=json.loads(PLAN_PATH.read_text())
OUT=HERE/'early_screen';
OPPS={name:ROOT/f'experiments/{name}_agent.py' for name in ('v50','v53','v54')}
OPPS['v53']=ROOT/'agents/v53_agent.py' if not OPPS['v53'].exists() else OPPS['v53']

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 if OUT.exists() and any(OUT.iterdir()): raise SystemExit(f'refusing to overwrite existing run: {OUT}')
 OUT.mkdir(parents=True,exist_ok=True)
 manifest={'plan_sha256':sha(PLAN_PATH),'baseline_sha256':sha(ROOT/'experiments/v57_broad/v57_reset_candidate.py'),
           'opponents':{k:{'path':str(v),'sha256':sha(v)} for k,v in OPPS.items()},
           'candidates':{},'seeds':PLAN['early_futility_seeds'],'started_at':time.time()}
 for x in PLAN['candidate_population']:
  p=HERE/'candidates'/f"{x['name']}.py"; assert sha(p)==x['sha256'],x['name']
  manifest['candidates'][x['name']]={'path':str(p),'sha256':sha(p)}
 manifest['candidates']['frozen_reset']={'path':str(ROOT/'experiments/v57_broad/v57_reset_candidate.py'),'sha256':sha(ROOT/'experiments/v57_broad/v57_reset_candidate.py')}
 (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 arms=[(x['name'],HERE/'candidates'/f"{x['name']}.py") for x in PLAN['candidate_population']]
 arms.append(('frozen_reset',ROOT/'experiments/v57_broad/v57_reset_candidate.py'))
 for name,candidate in arms:
  out=OUT/name
  cmd=[sys.executable,str(ROOT/'simulation/tournament.py'),'--candidate',str(candidate),
       '--seeds',','.join(map(str,PLAN['early_futility_seeds'])),'--workers',str(PLAN['workers_cap']),
       '--timeout','180','--replay-policy','errors','--output-dir',str(out)]
  for opp,path in OPPS.items():cmd.extend(['--opponent',f'{opp}={path}'])
  print('RUN',name,flush=True)
  start=time.monotonic();proc=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
  (OUT/f'{name}.stdout.log').write_text(proc.stdout+'\nSTDERR\n'+proc.stderr)
  if proc.returncode:raise SystemExit(f'{name} tournament failed ({proc.returncode})')
  print(proc.stdout.strip(),flush=True)
  rows=list(csv.DictReader((out/'games.csv').open()))
  if len(rows)!=12:raise SystemExit(f'{name} expected12 games got{len(rows)}')
  print('ARM_DONE',name,'games',len(rows),'errors',sum(r['candidate_error']!='False' or r['opponent_error']!='False' for r in rows),'timeouts',sum(r['timed_out']!='False' for r in rows),'elapsed_s',round(time.monotonic()-start,1),flush=True)
 manifest['finished_at']=time.time();(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print('SCREEN COMPLETE',OUT)
if __name__=='__main__':main()

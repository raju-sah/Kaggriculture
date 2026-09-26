"""Fresh, frozen 80-game validation of the overnight repair fix."""
import concurrent.futures as cf
import hashlib,json,time
from pathlib import Path
from simulation.tournament import MatchSpec,Opponent,_run_worker
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'experiments/runs/v57_reset_validation'
CANDIDATE=ROOT/'experiments/v57_broad/v57_reset_candidate.py'
VERSIONS=[48,50,51,52,53,54,55,56]
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 opponents=[]
 for v in VERSIONS:
  p=ROOT/f'agents/v{v}_agent.py'
  if not p.exists():p=ROOT/f'experiments/v{v}_agent.py'
  assert p.exists(),p
  opponents.append(Opponent(f'v{v}',p))
 digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 plan={'candidate':str(CANDIDATE.relative_to(ROOT)),'sha256':digest(CANDIDATE),'seeds':list(range(92800,92805)),'seats':[0,1],'opponents':{o.name:digest(o.path) for o in opponents},'selection':'Single overnight reset fix; no strategy tuning on these seeds','games':80}
 plan_path=OUT/'plan.json'
 if plan_path.exists():assert json.loads(plan_path.read_text())==plan
 else:plan_path.write_text(json.dumps(plan,indent=2)+'\n')
 results=[];start=time.monotonic()
 with cf.ThreadPoolExecutor(max_workers=6) as pool:
  futures=[pool.submit(_run_worker,CANDIDATE,MatchSpec(o,s,b,0),OUT,240,'errors') for s in plan['seeds'] for o in opponents for b in (False,True)]
  for future in cf.as_completed(futures):
   results.append(future.result())
   (OUT/'results.json').write_text(json.dumps(results,indent=2)+'\n')
   print(f'{len(results)}/80 {results[-1]["opponent"]} {results[-1]["candidate_result"]} elapsed={time.monotonic()-start:.0f}s',flush=True)
 for o in opponents:
  group=[r for r in results if r['opponent']==o.name]
  print(o.name,{k:sum(r['candidate_result']==k for r in group) for k in ('win','loss','draw','error')},flush=True)
if __name__=='__main__':main()

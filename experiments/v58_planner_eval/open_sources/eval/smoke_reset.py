"""Two-seat internal smoke vs the frozen reset, with no replay output retained."""
import hashlib, importlib.util, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]; sys.path.insert(0,str(ROOT))
from kaggle_environments import make
from kaggle_environments.agent import get_last_callable

def load_file(name, path):
    spec=importlib.util.spec_from_file_location('smoke_'+name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    return module.agent

sources={
 'ahmed_v43': ROOT/'experiments/v58_planner_eval/open_sources/eval/ahmed_v43/runtime/main.py',
 'yhay_three_day': ROOT/'experiments/v58_planner_eval/open_sources/eval/yhay_three_day/runtime/main.py',
}
reset=load_file('frozen_reset',ROOT/'experiments/v57_broad/v57_reset_candidate.py')
rows=[]
for name,path in sources.items():
 raw=path.read_bytes(); agent=get_last_callable(raw.decode(),path=str(path)); digest=hashlib.sha256(raw).hexdigest()
 for seed in (95000,95001):
  for seat in (0,1):
   players=[agent,reset] if seat==0 else [reset,agent]
   env=make('kaggriculture',configuration={'seed':seed}); state=env.run(players)
   a,b=state[-1][seat],state[-1][1-seat]
   err=sum((s or {}).get('status') in {'ERROR','INVALID'} or (s or {}).get('reward') is None for s in state[-1])
   row={'candidate':name,'seed':seed,'candidate_seat':seat,'steps':len(state),'candidate_reward':a.get('reward'),'reset_reward':b.get('reward'),'margin':a.get('reward')-b.get('reward'),'error_players':int(err),'candidate_sha256':digest}
   rows.append(row); print(json.dumps(row),flush=True)
out=ROOT/'experiments/v58_planner_eval/open_sources/eval/results'
out.mkdir(exist_ok=True,parents=True)
(out/'reset_smoke.json').write_text(json.dumps({'status':'completed_smoke_not_panel','rows':rows},indent=2)+'\n')

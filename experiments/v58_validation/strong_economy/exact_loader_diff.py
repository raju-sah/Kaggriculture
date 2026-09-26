"""Exact Kaggle loader action-difference proof on all frames of retained replay."""
import hashlib,json
from pathlib import Path
from kaggle_environments.agent import get_last_callable
ROOT=Path(__file__).resolve().parents[3]
REPLAY=ROOT/'experiments/v58_original_second/reset_probe/replays/v50-seed-94500-ab-repeat-0.json'

def load_source(path):
 raw=path.read_bytes();return get_last_callable(raw.decode(),path=str(path)),hashlib.sha256(raw).hexdigest()

def main():
 frames=json.loads(REPLAY.read_text())['steps']
 results=[]
 base,_=load_source(ROOT/'experiments/v57_broad/v57_reset_candidate.py')
 candidates=[(p,*load_source(p)) for p in sorted((ROOT/'experiments/v58_validation/strong_economy/candidates').glob('*.py'))]
 for t,step in enumerate(frames):
  for seat,agent_state in enumerate(step):
   obs=agent_state.get('observation')
   if not obs: continue
   base_action=base(obs)
   for config,fn,digest in candidates:
    actual=fn(obs)
    if actual!=base_action:
     results.append({'step':t,'seat':seat,'config':config.stem,'candidate_sha256':digest,
       'base_market':base_action.get('market',[]),'candidate_market':actual.get('market',[]),
       'actor_actions_changed':(actual.get('farmer'),actual.get('hands'))!=(base_action.get('farmer'),base_action.get('hands'))})
 out=ROOT/'experiments/v58_validation/strong_economy/exact_loader_diff.json'
 out.write_text(json.dumps({'source_replay':str(REPLAY),'source_replay_sha256':hashlib.sha256(REPLAY.read_bytes()).hexdigest(),'frames_checked':len(frames),'seat_observations_checked':2*len(frames),'changed_rows':results},indent=2)+'\n')
 print(json.dumps({'frames':len(frames),'seat_observations_checked':2*len(frames),'changed_rows':len(results),'by_config':{p.stem:sum(r['config']==p.stem for r in results) for p in sorted((ROOT/'experiments/v58_validation/strong_economy/candidates').glob('*.py'))},'samples':results[:8]},indent=2))
if __name__=='__main__':main()

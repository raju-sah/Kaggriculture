"""Prove preserved base orders and locate appended orders through Kaggle loader."""
import hashlib,json
from pathlib import Path
from kaggle_environments.agent import get_last_callable
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'experiments/v57_broad/v57_reset_candidate.py'
CAND=ROOT/'experiments/v58_validation/strong_economy/append_seed_refill.py'
REPLAY=ROOT/'experiments/v58_original_second/reset_probe/replays/v50-seed-94500-ab-repeat-0.json'
base_fn=get_last_callable(BASE.read_text(),path=str(BASE))
cand_fn=get_last_callable(CAND.read_text(),path=str(CAND))
assert cand_fn.__name__=='zzz_economy_policy_entrypoint',cand_fn.__name__
steps=json.loads(REPLAY.read_text())['steps']; additions=[]; mismatches=[]; fixtures={}
for t,step in enumerate(steps):
 for seat,row in enumerate(step):
  obs=row.get('observation')
  if not obs:continue
  b=base_fn(obs); c=cand_fn(obs)
  if (b.get('farmer'),b.get('hands'))!=(c.get('farmer'),c.get('hands')):mismatches.append({'step':t,'seat':seat,'kind':'actor'})
  bm=b.get('market',[]) or [];cm=c.get('market',[]) or []
  if cm[:len(bm)]!=bm:mismatches.append({'step':t,'seat':seat,'kind':'market_prefix','base':bm,'candidate':cm})
  if len(cm)>len(bm):
   o={'step':t,'seat':seat,'day':obs.get('day'),'hour':obs.get('hour'),'money':obs['farms'][int(obs.get('player',seat) or 0)].get('money'),
      'seeds':(obs.get('private',{}).get('seeds') or {}),'base_market':bm,'candidate_market':cm,
      'farmer':b.get('farmer'),'hands':b.get('hands'),'new_orders':cm[len(bm):]}
   additions.append(o)
  if t in (11,24,30) and seat==0:
   fixtures[str(t)]={'day':obs.get('day'),'hour':obs.get('hour'),'money':obs['farms'][int(obs.get('player',seat) or 0)].get('money'),'base_market':bm,'candidate_market':cm,'equal':bm==cm}
report={'loader':'kaggle_environments.agent.get_last_callable','candidate_entrypoint':cand_fn.__name__,'baseline_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(CAND.read_bytes()).hexdigest(),'replay_sha256':hashlib.sha256(REPLAY.read_bytes()).hexdigest(),'observations_checked':len(steps)*2,'base_order_prefix_mismatches':mismatches,'appended_action_rows':additions,'fixtures_steps11_24_30':fixtures}
out=ROOT/'experiments/v58_validation/strong_economy/append_preflight.json';out.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'entrypoint':report['candidate_entrypoint'],'observations':report['observations_checked'],'prefix_mismatches':len(mismatches),'added_rows':len(additions),'first_additions':additions[:8],'fixtures':fixtures},indent=2))

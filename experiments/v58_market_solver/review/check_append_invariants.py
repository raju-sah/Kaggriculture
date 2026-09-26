"""Independent read-only audit of the frozen strong-economy append overlay."""
from __future__ import annotations
import copy, hashlib, json
from pathlib import Path
from types import SimpleNamespace
from kaggle_environments.agent import get_last_callable
from kaggle_environments.utils import structify
from kaggle_environments import make
from kaggle_environments.envs.kaggriculture import kaggriculture as engine

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'experiments/v57_broad/v57_reset_candidate.py'
CAND=ROOT/'experiments/v58_validation/strong_economy/append_seed_refill.py'
REPLAY=ROOT/'experiments/v58_original_second/reset_probe/replays/v50-seed-94500-ab-repeat-0.json'
EXPECTED=''

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def productive(q): return [o for o in q if isinstance(o,list) and o and o[0] in {'BUY_SEED','HIRE','BUY_PRODUCT','BUY_ANIMAL'}]
def market_sim(obs_pair, actions, cfg):
    # Share the public market/farm state exactly as _process_market expects;
    # retain each seat's private observation separately.
    raw0, raw1=copy.deepcopy(obs_pair)
    raw0['market']=raw1['market']=copy.deepcopy(raw0['market'])
    raw0['farms']=raw1['farms']=copy.deepcopy(raw0['farms'])
    states=[]
    for raw,action in zip((raw0,raw1),actions):
        states.append(SimpleNamespace(observation=structify(raw),action=copy.deepcopy(action)))
    env=SimpleNamespace(configuration=cfg)
    engine._process_market(states,env)
    return states

def main():
    base_fn=get_last_callable(BASE.read_text(),path=str(BASE)); cand_fn=get_last_callable(CAND.read_text(),path=str(CAND))
    rep=json.loads(REPLAY.read_text()); steps=rep['steps']; cfg=dict(rep.get('configuration') or {})
    cfg.setdefault('boardSize',10); cfg.setdefault('farmHandCostMult',1); cfg.setdefault('maxMarketOrdersPerTurn',10); cfg.setdefault('shedCapacity',100)
    issues=[]; adds=[]; checked=actor=0; prefix=prod=slot=0; committed=failed=0; max_slots=0
    for t in range(1,len(steps)):
      for seat in range(2):
        obs=steps[t-1][seat].get('observation')
        if not obs: continue
        b=base_fn(obs); c=cand_fn(obs); checked+=1
        if (b.get('farmer'),b.get('hands')) != (c.get('farmer'),c.get('hands')):
          actor+=1; issues.append({'step':t,'seat':seat,'issue':'actor_mutation'})
        bm=b.get('market',[]) or []; cm=c.get('market',[]) or []; max_slots=max(max_slots,len(cm))
        if cm[:len(bm)] != bm:
          prefix+=1; issues.append({'step':t,'seat':seat,'issue':'base_queue_not_prefix'})
        if productive(cm)[:len(productive(bm))] != productive(bm):
          prod+=1; issues.append({'step':t,'seat':seat,'issue':'productive_subsequence_changed'})
        if len(cm)>10 or len(cm)>len(bm)+1 or (len(cm)>len(bm) and len(bm)>=10):
          slot+=1; issues.append({'step':t,'seat':seat,'issue':'slot_overflow','base_slots':len(bm),'candidate_slots':len(cm)})
        if len(cm)>len(bm):
          entry={'step':t,'seat':seat,'day':obs.get('day'),'hour':obs.get('hour'),'base_slots':len(bm),'market':cm,'seed_before':(obs.get('private',{}).get('seeds') or {}).get('WHEAT',0)}
          # Exact engine oracle with retained opponent order. Only appended BUY_SEED rows expected.
          actions=[None,None]; actions[seat]=c; actions[1-seat]=steps[t][1-seat].get('action') or {}
          rawpair=[steps[t-1][i]['observation'] for i in range(2)]
          sim=market_sim(rawpair,actions,cfg)
          after=sim[seat].observation.private.seeds.get('WHEAT',0)
          entry['seed_after_engine_market']=after; entry['seed_order_committed']=after>entry['seed_before']
          entry['money_after_engine_market']=sim[seat].observation.farms[seat].money
          if after>entry['seed_before']: committed+=1
          else: failed+=1
          adds.append(entry)
    result={'candidate_sha256':sha(CAND),'baseline_sha256':sha(BASE),'replay_sha256':sha(REPLAY),'observations_checked':checked,'actor_mutations':actor,'base_prefix_mismatches':prefix,'productive_subsequence_mismatches':prod,'slot_violations':slot,'max_candidate_queue_slots':max_slots,'append_rows':len(adds),'append_seed_commits':committed,'append_seed_not_committed_under_retained_opponent_action':failed,'append_details':adds,'issues':issues}
    out=ROOT/'experiments/v58_market_solver/review/append_invariant_report.json'; out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in {'append_details','issues'}},indent=2))
    if issues: raise SystemExit(1)
if __name__=='__main__': main()

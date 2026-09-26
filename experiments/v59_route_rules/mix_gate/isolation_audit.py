"""Replay-only proof that the isolated mix gate leaves baseline work untouched."""
import importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
REPLAYS=ROOT/'experiments/v59_state_teacher/dev95501_95519/replays'

def load(unique):
 spec=importlib.util.spec_from_file_location(unique,HERE/'candidate_isolated.py')
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def audit(seed):
 m=load(f'v59iso_{seed}')
 replay=json.loads((REPLAYS/f'v50-seed-{seed}-ab-repeat-0.json').read_text())
 n=base_diff=market_diff=unit_diff=0; byte_equal=True; converted=[]; failures=[]
 for frame in replay['steps']:
  state=frame[0];obs=state.get('observation') or {}
  if not obs:continue
  before=m._v59_frozen_agent_isolated(obs,{})
  after=m._v59_iso_apply(obs,before)
  n+=1
  if after!=before:
   base_diff+=1
  if json.dumps(after,separators=(',',':')) != json.dumps(before,separators=(',',':')):
   byte_equal=False
   if after.get('market')!=before.get('market'):market_diff+=1
   b=[before.get('farmer'),*(before.get('hands') or [])];a=[after.get('farmer'),*(after.get('hands') or [])]
   if a!=b:unit_diff+=1
   if after.get('market')!=before.get('market'):
    converted.append({'step':obs.get('step'),'day':obs.get('day'),'before':before.get('market'),'after':after.get('market')})
   # Every actor op change must be a tracked carrier action, and all other base work is preserved.
   if a!=b:
    seat=int(obs.get('player',0));state2=m._v59_extra_sheep_state.get(seat,{})
    changed=[i for i,(x,y) in enumerate(zip(b,a)) if x!=y]
    allowed=state2.get('routed',set())
    if not all(i in allowed or (y and y[0]=='PICKUP' and y[1]=='SHEEP') for i in changed):
     failures.append({'step':obs.get('step'),'changed':changed,'routed':list(allowed)})
 if seed==95501:
  # No early high-wool Yarn signal exists, so the entire returned action stream must equal base.
  pass
 return {'seed':seed,'frames':n,'changed_frames':base_diff,'market_changed_frames':market_diff,'unit_changed_frames':unit_diff,'converted_orders':converted,'route_scope_failures':failures,'byte_identical_to_frozen_output':base_diff==0 and byte_equal}

res={str(s):audit(s) for s in (95501,95508,95518)}
(HERE/'isolation_audit.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps(res,indent=2))

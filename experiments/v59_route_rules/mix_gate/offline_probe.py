"""Show the frozen action queue and candidate intervention on spent observations only."""
import importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
spec=importlib.util.spec_from_file_location('mixgate',HERE/'candidate.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
base=ROOT/'experiments/v59_state_teacher/dev95501_95519/replays'
out={}
for seed in (95501,95508,95518):
 r=json.loads((base/f'v50-seed-{seed}-ab-repeat-0.json').read_text())
 first_yarn=None;first_trigger=None;first_eligible=None
 for frame in r['steps']:
  st=frame[0];o=st.get('observation') or {};a=st.get('action') or {}
  if not o:continue
  shops=(o.get('town') or {}).get('unlocked_shops',[]); day=int(o.get('day',0)); wool=int((o.get('market') or {}).get('prices',{}).get('WOOL',0) or 0)
  goose=sum(int(x[2]) for x in a.get('market',[]) if len(x)>2 and x[:2]==['BUY_ANIMAL','GOOSE'])
  sheep=sum(int(x[2]) for x in a.get('market',[]) if len(x)>2 and x[:2]==['BUY_ANIMAL','SHEEP'])
  rec={'step':int(o.get('step',-1)),'day':day,'wool':wool,'market':a.get('market',[]),'goose_buy':goose,'sheep_buy':sheep}
  if 'YARN_STORE' in shops and first_yarn is None:first_yarn=rec
  if day<=11 and 'YARN_STORE' in shops and wool>=180 and first_trigger is None:first_trigger=rec
  if day<=11 and 'YARN_STORE' in shops and wool>=180 and goose>0 and first_eligible is None:
   farm=o['farms'][0]; private=o['private']; action={'farmer':a.get('farmer',['PASS']),'hands':a.get('hands',[]),'market':a.get('market',[])}
   before=list(action['market']); changed=m._v59_mix_gate(o,action)
   counts,vacant=m._v59_livestock_counts(o,farm,private)
   first_eligible={**rec,'pre_sheep_count':counts['SHEEP'],'vacant_pastures':len(vacant),'before_market':before,'after_market':changed['market']}
 out[str(seed)]={'first_yarn':first_yarn,'first_early_high_wool_trigger':first_trigger,'first_triggered_goose_order':first_eligible}
(HERE/'offline_probe.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))

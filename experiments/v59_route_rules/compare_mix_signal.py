"""Offline spent-replay comparison for the early-yarn sheep mix gate."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'experiments/v59_state_teacher/dev95501_95519/replays'

def stats(seed):
    path=BASE/f'v50-seed-{seed}-ab-repeat-0.json'
    replay=json.loads(path.read_text())
    rows=[]
    for frame in replay['steps']:
        state=frame[0]; obs=state.get('observation') or {}; action=state.get('action') or {}
        if not obs: continue
        day=int(obs.get('day',0)); shops=(obs.get('town') or {}).get('unlocked_shops',[])
        wool=int((obs.get('market') or {}).get('prices',{}).get('WOOL',0) or 0)
        gate=day<=11 and 'YARN_STORE' in shops and wool>=180
        buys=[a for a in action.get('market',[]) if len(a)>=3 and a[0]=='BUY_ANIMAL']
        geese=sum(int(a[2]) for a in buys if a[1]=='GOOSE')
        sheep=sum(int(a[2]) for a in buys if a[1]=='SHEEP')
        if gate or geese or (day<=11 and 'YARN_STORE' in shops):
            rows.append({'step':int(obs.get('step',-1)),'day':day,'yarn':('YARN_STORE' in shops),'wool_price':wool,'gate':gate,'goose_order':geese,'sheep_order':sheep})
    first_gate=next((r for r in rows if r['gate']),None)
    eligible=next((r for r in rows if r['gate'] and r['goose_order']),None)
    return {'seed':seed,'first_gate':first_gate,'first_gate_with_goose_buy':eligible,'first_early_yarn':next((r for r in rows if r['day']<=11 and r['yarn']),None),'samples':rows}

result={str(s):stats(s) for s in (95501,95508,95518)}
(ROOT/'experiments/v59_route_rules/mix_signal_offline.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:{'first_gate':v['first_gate'],'first_gate_with_goose_buy':v['first_gate_with_goose_buy'],'first_early_yarn':v['first_early_yarn']} for k,v in result.items()},indent=2))

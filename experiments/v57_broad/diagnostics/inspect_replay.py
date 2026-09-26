import json
from collections import Counter
from pathlib import Path
P=Path('experiments/v57_broad/diagnostics/direct/replays/v56-seed-92718-ba-repeat-0.json')
r=json.loads(P.read_text());steps=r['steps']
print('first observations keys', [list(x['observation']) for x in steps[0]])
print('day, coins, herd0, herd1, crops0,crops1,workers,shops')
for step in steps:
    obs=step[0]['observation']
    if obs.get('hour')!=0:continue
    farms=obs['farms'];herds=[];crops=[]
    for f in farms:
        herds.append(dict(Counter(t.get('animal') for row in f['tiles'] for t in row if isinstance(t,dict) and t.get('animal'))))
        crops.append(dict(Counter(t.get('crop') for row in f['tiles'] for t in row if isinstance(t,dict) and t.get('crop'))))
    print(obs['day'],[f['money'] for f in farms],herds,crops,[len(f['hands']) for f in farms],obs['town']['unlocked_shops'])
for i,step in enumerate(steps[1:],1):
    a,b=[x.get('action') or {} for x in step]
    if (a.get('farmer'),a.get('hands'))!=(b.get('farmer'),b.get('hands')):
        print('FIRST ACTOR DIVERGENCE',i,a,b)
        print('PREVIOUS OBS',json.dumps(steps[i-1][0]['observation'])[:300])
        break

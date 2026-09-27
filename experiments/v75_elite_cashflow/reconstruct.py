#!/usr/bin/env python3
"""Reconstruct checkpoints and accepted cash flows from saved official/local replays.

The policy is never run or copied: actions are replayed through Kaggriculture
1.32.7 settlement to audit realized sales and purchases.
"""
import copy, csv, json, hashlib
from collections import Counter, defaultdict
from pathlib import Path
from types import SimpleNamespace
from kaggle_environments.envs.kaggriculture import kaggriculture as engine

ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / 'experiments/v63_elite_panel'
OUT = Path(__file__).with_name('reconstructed.json')
ELITE_IDS = ['113423918','113537919','113664666','113681377','113685931','113696381']
V70_REPLAYS = [
 ('V70 seed94700 seat0','experiments/v70_capacity/spent94700_vs_v56/replays/v56_agent-seed-94700-ab-repeat-0.json',0),
 ('V70 seed94700 seat1','experiments/v70_capacity/spent94700_vs_v56/replays/v56_agent-seed-94700-ba-repeat-0.json',1),
 ('V70 seed92802 seat0','experiments/v70_capacity/spent92802_92804_vs_v56/replays/v56_agent-seed-92802-ab-repeat-0.json',0),
 ('V70 seed92804 seat0','experiments/v70_capacity/spent92802_92804_vs_v56/replays/v56_agent-seed-92804-ab-repeat-0.json',0),
]

def checkpoint(game, seat):
    steps=game['steps']; out={}
    for day in [0,3,6,9,12]:
        frame = 0 if day == 0 else min(day*24+23,len(steps)-1)
        obs=steps[frame][seat]['observation']
        f=obs['farms'][seat]; tiles=[t for row in f['tiles'] for t in row if isinstance(t,dict)]
        crops=Counter(t.get('crop') for t in tiles if t.get('kind')=='PLANT')
        animals=Counter(t.get('animal') for t in tiles if 'animal' in t)
        out[str(day)]={'cash':f['money'],'hands':len(f.get('hands',[])),
          'land':len(f.get('unlocked_quadrants',[])),'crops':dict(crops),'animals':dict(animals),
          'unlocked':f.get('unlocked_quadrants',[])}
    return out

def reconstruct(path, seat, label, meta=None):
    game=json.loads(Path(path).read_text()); steps=game['steps']; config=game.get('configuration',{})
    cfg=SimpleNamespace(**{k:config.get(k,v) for k,v in {'boardSize':10,'maxMarketOrdersPerTurn':10,'farmHandCostMult':1,'shedCapacity':100,'turnsPerDay':24}.items()})
    daily=defaultdict(lambda:{'sales':Counter(),'products':Counter(),'seeds':Counter(),'animals':Counter(),'land_hire_cost':0.0,'cash_delta':0.0})
    audit={'max_cash_error':0.0,'mismatches':0}
    original=engine._commit_unit; cur=None; tracked=None
    def commit(op,item,price,farm,private,market,shed_capacity=100):
        ok=original(op,item,price,farm,private,market,shed_capacity)
        if ok and cur is not None:
            s=0 if farm is tracked[0] else 1
            cur.append((s,op,item,price))
        return ok
    engine._commit_unit=commit
    try:
      for frame in range(1,len(steps)):
        prev,now=steps[frame-1],steps[frame]; obs=prev[seat]['observation']; day=int(obs['day'])
        farms=copy.deepcopy(obs['farms']); tracked=farms; market=copy.deepcopy(obs['market'])
        priv=[copy.deepcopy(prev[s]['observation']['private']) for s in range(2)]
        acts=[copy.deepcopy(now[s].get('action') or {}) for s in range(2)]
        before=[float(farms[s]['money']) for s in range(2)]
        blocked=[]
        for s in range(2):
          units=[acts[s].get('farmer',['PASS']),*(acts[s].get('hands') or [])]
          d=Counter(a[1] for a in units if isinstance(a,list) and len(a)>=2 and a[0]=='PLANT')
          blocked.append({c for c,n in d.items() if n>priv[s].get('seeds',{}).get(c,0)})
        for s in range(2):
          units=[acts[s].get('farmer',['PASS']),*(acts[s].get('hands') or [])]
          for i,a in enumerate(units):
            if isinstance(a,list) and len(a)>=2 and a[0]=='PLANT' and a[1] in blocked[s]: a=['PASS']
            engine._apply_unit_action(farms[s],priv[s],i,a,int(cfg.boardSize),day,int(cfg.turnsPerDay),int(cfg.shedCapacity))
        states=[]
        for s in range(2):
          o=SimpleNamespace(market=market,farms=farms,private=priv[s])
          states.append(SimpleNamespace(observation=o,action=acts[s]))
        cur=[]; engine._process_market(states,SimpleNamespace(configuration=cfg))
        drow=daily[day]
        sale=buy=0
        for s,op,item,price in cur:
          if s!=seat: continue
          if op=='SELL': drow['sales'][item]+=price; sale+=price
          elif op=='BUY_PRODUCT': drow['products'][item]+=price; buy+=price
          elif op=='BUY_SEED': drow['seeds'][item]+=price
          elif op=='BUY_ANIMAL': drow['animals'][item]+=price
        end=float(farms[seat]['money']); observed=float(now[seat]['observation']['farms'][seat]['money'])
        err=abs(end-observed); audit['max_cash_error']=max(audit['max_cash_error'],err); audit['mismatches']+=int(err>.011)
        # Remaining direct cash delta after explicit market transactions is land/hire/other atomic cost.
        explicit=sum(price for s,op,item,price in cur if s==seat and op in ('BUY_PRODUCT','BUY_SEED','BUY_ANIMAL'))-sale
        drow['land_hire_cost'] += before[seat]-end-explicit
        drow['cash_delta'] += observed-before[seat]
    finally: engine._commit_unit=original
    result={'label':label,'seat':seat,'replay_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),
            'checkpoints':checkpoint(game,seat),'daily':{str(d):{'sales':dict(x['sales']),'product_buys':dict(x['products']),'seed_buys':dict(x['seeds']),'animal_buys':dict(x['animals']),'land_hire_cost':round(x['land_hire_cost'],2),'cash_delta':round(x['cash_delta'],2)} for d,x in sorted(daily.items())},'audit':audit}
    if meta: result.update(meta)
    return result

players=list(csv.DictReader((PANEL/'players.csv').open()))
results=[]
for eid in ELITE_IDS:
  row=next(r for r in players if r['episode_id']==eid and r['winner']=='True')
  path=PANEL/'replays'/f'episode-{eid}-replay.json'
  results.append(reconstruct(path,int(row['seat']),f"Elite {row['team_name']} episode {eid}",{'team':row['team_name'],'episode_id':eid,'seed':row['seed']}))
for label,rel,seat in V70_REPLAYS:
  results.append(reconstruct(ROOT/rel,seat,label,{'episode_id':None,'seed':rel.split('seed-')[-1].split('-')[0]}))
OUT.write_text(json.dumps(results,separators=(',',':'),sort_keys=True)+'\n')
print(OUT)
for r in results:
  print(r['label'],r['audit'],'d0-5 sales',sum(sum(v.values()) for d,v in ((int(k),x['sales']) for k,x in r['daily'].items()) if d<=5),'d6-11 sales',sum(sum(v.values()) for d,v in ((int(k),x['sales']) for k,x in r['daily'].items()) if 6<=d<=11))

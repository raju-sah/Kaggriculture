"""Read-only replay audit for the isolated day-6 sheep-to-cow probe."""
from __future__ import annotations
import copy, json
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from kaggle_environments.envs.kaggriculture import kaggriculture as engine

HERE=Path(__file__).resolve().parent

def settle(game):
    steps=game['steps']; cfg=game.get('configuration',{})
    config=SimpleNamespace(**{k:cfg.get(k,v) for k,v in {'boardSize':10,'turnsPerDay':24,'maxMarketOrdersPerTurn':10,'farmHandCostMult':1,'shedCapacity':100}.items()})
    totals=[Counter(),Counter()]; mismatches=[0,0]
    original=engine._commit_unit; current_farms=[]; committed=[]
    def hook(op,item,price,farm,private,market,shed_capacity=100):
        ok=original(op,item,price,farm,private,market,shed_capacity)
        if ok:
            s=next((i for i,x in enumerate(current_farms) if x is farm),-1)
            committed.append((s,op,item,float(price)))
        return ok
    engine._commit_unit=hook
    try:
      for frame in range(1,len(steps)):
        prev,now=steps[frame-1],steps[frame]; obs=prev[0]['observation']; day=int(obs.get('day',0))
        farms=copy.deepcopy(obs['farms']); current_farms=farms
        private=[copy.deepcopy(prev[s]['observation']['private']) for s in (0,1)]
        market=copy.deepcopy(obs['market']); acts=[copy.deepcopy(now[s].get('action') or {}) for s in (0,1)]
        for s in (0,1):
          units=[acts[s].get('farmer',['PASS']),*(acts[s].get('hands') or [])]
          demand=Counter(a[1] for a in units if isinstance(a,list) and len(a)>=2 and a[0]=='PLANT')
          blocked={crop for crop,n in demand.items() if n>private[s].get('seeds',{}).get(crop,0)}
          for ui,a in enumerate(units):
            if isinstance(a,list) and len(a)>=2 and a[0]=='PLANT' and a[1] in blocked:a=['PASS']
            engine._apply_unit_action(farms[s],private[s],ui,a,int(config.boardSize),day,int(config.turnsPerDay),int(config.shedCapacity))
        states=[SimpleNamespace(observation=SimpleNamespace(market=market,farms=farms,private=private[s]),action=acts[s]) for s in (0,1)]
        committed.clear(); engine._process_market(states,SimpleNamespace(configuration=config))
        for s,op,item,price in committed: totals[s][(op,item)]+=price
        for s in (0,1):
          if abs(float(farms[s]['money'])-float(now[s]['observation']['farms'][s]['money']))>.011:mismatches[s]+=1
    finally: engine._commit_unit=original
    return totals,mismatches

def audit_lifecycle(path,seat):
    game=json.loads(Path(path).read_text()); steps=game['steps']; result={'buy':[],'pickup':[],'place':[],'feed_days':[],'care_days':[],'harvest':[]}
    cow_pos=None
    for frame in range(1,len(steps)):
      prev,now=steps[frame-1],steps[frame]; obs=prev[seat]['observation']; act=now[seat].get('action') or {}; day=int(obs.get('day',0)); hour=int(obs.get('hour',0)); farm=obs['farms'][seat]
      units=[act.get('farmer',['PASS']),*(act.get('hands') or [])]; positions=[farm.get('farmer')]+list(farm.get('hands') or [])
      if day==6 and hour==6:
        result['buy']=[o for o in act.get('market') or [] if o and o[0]=='BUY_ANIMAL']
      for ui,a in enumerate(units):
        if not isinstance(a,list) or not a:continue
        if day==6 and a[0]=='PICKUP' and len(a)>1 and a[1]=='COW':result['pickup'].append({'step':frame-1,'hour':hour,'actor':ui,'pos':positions[ui]})
        if day==6 and a[0]=='PLACE' and len(a)>1 and a[1]=='COW':
          cow_pos=tuple(positions[ui]); result['place'].append({'step':frame-1,'hour':hour,'actor':ui,'pos':list(cow_pos)})
        if cow_pos and tuple(positions[ui])==cow_pos and a[0] in ('FEED','CARE','HARVEST'):
          tile=farm['tiles'][cow_pos[1]][cow_pos[0]]
          if a[0]=='FEED':result['feed_days'].append(day)
          if a[0]=='CARE':result['care_days'].append(day)
          if a[0]=='HARVEST' and tile.get('animal')=='COW' and tile.get('yield_units',0)>0:
            result['harvest'].append({'step':frame-1,'day':day,'units':tile['yield_units']})
    if cow_pos:
      # Confirm the tile remains a cow, rather than a placement no-op or escape.
      last=steps[-1][seat]['observation']['farms'][seat]['tiles'][cow_pos[1]][cow_pos[0]]
      result['final_tile']=last
      result['position']=list(cow_pos)
    return result

if __name__ == '__main__':
    rows=[json.loads(x) for x in (HERE/'runs/seed92600_both_seats/games.jsonl').read_text().splitlines()]
    for path in sorted((HERE/'runs/seed92600_both_seats/replays').glob('*.json')):
      row=next(r for r in rows if Path(r['replay_path']).name==path.name); seat=row['candidate_seat']; game=json.loads(path.read_text())
      totals,mismatches=settle(game); life=audit_lifecycle(path,seat)
      print(path.name,'candidate seat',seat,'final',row['final_coins'][seat],'opponent',row['final_coins'][1-seat],'margin',row['final_coins'][seat]-row['final_coins'][1-seat])
      print('lifecycle',json.dumps(life,sort_keys=True))
      print('accepted cash milk',totals[seat][('SELL','MILK')],'wool',totals[seat][('SELL','WOOL')],'animal spend cow',totals[seat][('BUY_ANIMAL','COW')],'sheep',totals[seat][('BUY_ANIMAL','SHEEP')],'cash mismatches',mismatches)

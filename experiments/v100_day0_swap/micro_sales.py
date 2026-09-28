#!/usr/bin/env python3
"""Accepted-sale cash by seat for the V100 exact-loader micro pair."""
import copy,json
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from kaggle_environments.envs.kaggriculture import kaggriculture as engine
root=Path(__file__).resolve().parents[2]; run=root/'experiments/v100_day0_swap/runs/micro_92600_vs_v92'
orig=engine._commit_unit
for rec in [json.loads(x) for x in (run/'games.jsonl').read_text().splitlines()]:
 g=json.loads(Path(rec['replay_path']).read_text()); seat=rec['candidate_seat']; sums=[Counter(),Counter()]; errs=0
 cfg=SimpleNamespace(boardSize=10,turnsPerDay=24,maxMarketOrdersPerTurn=10,farmHandCostMult=1,shedCapacity=100)
 ids={}
 def hook(op,item,price,farm,private,market,shed_capacity=100):
  ok=orig(op,item,price,farm,private,market,shed_capacity)
  if ok and op=='SELL': sums[ids[id(farm)]][item]+=float(price)
  return ok
 engine._commit_unit=hook
 try:
  for frame in range(len(g['steps'])-1):
   prev,now=g['steps'][frame],g['steps'][frame+1]; obs=prev[0]['observation']; day=int(obs.get('day',0)); farms=copy.deepcopy(obs['farms']); ids={id(farms[i]):i for i in (0,1)}; private=[copy.deepcopy(prev[i]['observation']['private']) for i in (0,1)]; market=copy.deepcopy(obs['market']); acts=[copy.deepcopy(now[i].get('action') or {}) for i in (0,1)]
   for s in (0,1):
    for ui,a in enumerate([acts[s].get('farmer',['PASS']),*(acts[s].get('hands') or [])]):engine._apply_unit_action(farms[s],private[s],ui,a,10,day,24,100)
   states=[SimpleNamespace(observation=SimpleNamespace(market=market,farms=farms,private=private[s]),action=acts[s]) for s in (0,1)]
   engine._process_market(states,SimpleNamespace(configuration=cfg))
   for s in (0,1):
    if abs(farms[s]['money']-now[s]['observation']['farms'][s]['money'])>.011:errs+=1
 finally:engine._commit_unit=orig
 print(json.dumps({'game':rec['game_id'],'candidate_seat':seat,'cash':rec['final_coins'][seat],'opp_cash':rec['final_coins'][1-seat],'candidate_sell_cash':dict(sums[seat]),'opponent_sell_cash':dict(sums[1-seat]),'cash_mismatches':errs},sort_keys=True))

#!/usr/bin/env python3
"""Audit V100 day-zero swap lifecycle and accepted market cash in saved replays."""
from __future__ import annotations
import copy, json
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from kaggle_environments.envs.kaggriculture import kaggriculture as engine

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'experiments/v100_day0_swap/runs/micro_92600_vs_v92'
records=[json.loads(x) for x in (RUN/'games.jsonl').read_text().splitlines()]
orig=engine._commit_unit
for row in records:
    path=Path(row['replay_path']); game=json.loads(path.read_text()); seat=int(row['candidate_seat']); steps=game['steps']
    events=[]; cow_pos=None; lifecycle=Counter(); sales=Counter(); spend=Counter(); cash_mismatch=0
    cfg=SimpleNamespace(boardSize=10,turnsPerDay=24,maxMarketOrdersPerTurn=10,farmHandCostMult=1,shedCapacity=100)
    identities={}; cur_step=[0]
    def tracked(op,item,price,farm,private,market,shed_capacity=100):
        ok=orig(op,item,price,farm,private,market,shed_capacity)
        if ok:
            who=identities.get(id(farm))
            if who==seat:
                if op=='SELL': sales[item]+=float(price)
                elif op.startswith('BUY'): spend[f'{op}:{item}']+=float(price)
        return ok
    engine._commit_unit=tracked
    try:
      for frame in range(len(steps)-1):
        prev,now=steps[frame],steps[frame+1]; obs=prev[0]['observation']; day=int(obs.get('day',0)); hour=int(obs.get('hour',0))
        farm0=obs['farms'][seat]
        action=now[seat].get('action') or {}
        if (day,hour) in ((0,1),(0,3),(0,8)):
            events.append({'day':day,'hour':hour,'market':copy.deepcopy(action.get('market') or []),'farmer':action.get('farmer'),'hands':copy.deepcopy(action.get('hands') or [])})
        if day==0 and hour==8:
            units=[action.get('farmer',['PASS']),*(action.get('hands') or [])]
            poss=[farm0.get('farmer')]+list(farm0.get('hands') or [])
            for ui,a in enumerate(units):
                if isinstance(a,list) and len(a)>1 and a[0]=='PLACE' and a[1]=='COW': cow_pos=tuple(poss[ui]); break
        if cow_pos is not None:
            units=[action.get('farmer',['PASS']),*(action.get('hands') or [])]
            poss=[farm0.get('farmer')]+list(farm0.get('hands') or [])
            for ui,a in enumerate(units):
                if ui<len(poss) and tuple(poss[ui])==cow_pos and isinstance(a,list) and a and a[0] in ('FEED','CARE','HARVEST'):
                    tile=farm0['tiles'][cow_pos[1]][cow_pos[0]]
                    if isinstance(tile,dict) and tile.get('animal')=='COW': lifecycle[a[0]]+=1
        # Engine cash transition audit, including the pinned market commit point.
        farms=copy.deepcopy(obs['farms']); priv=[copy.deepcopy(prev[s]['observation']['private']) for s in (0,1)]; market=copy.deepcopy(obs['market'])
        identities={id(farms[s]):s for s in (0,1)}; acts=[copy.deepcopy(now[s].get('action') or {}) for s in (0,1)]
        for s in (0,1):
            units=[acts[s].get('farmer',['PASS']),*(acts[s].get('hands') or [])]
            for ui,a in enumerate(units): engine._apply_unit_action(farms[s],priv[s],ui,a,10,day,24,100)
        states=[SimpleNamespace(observation=SimpleNamespace(market=market,farms=farms,private=priv[s]),action=acts[s]) for s in (0,1)]
        engine._process_market(states,SimpleNamespace(configuration=cfg))
        for s in (0,1):
            seen=float(now[s]['observation']['farms'][s]['money'])
            if abs(float(farms[s]['money'])-seen)>.011: cash_mismatch+=1
    finally: engine._commit_unit=orig
    final=steps[-1][seat]['observation']['farms'][seat]
    final_tile=final['tiles'][cow_pos[1]][cow_pos[0]] if cow_pos else None
    print(json.dumps({'game':row['game_id'],'seat':seat,'cash':row['final_coins'][seat], 'opponent_cash':row['final_coins'][1-seat], 'candidate_margin':row['final_coins'][seat]-row['final_coins'][1-seat], 'day0_events':events,'cow_position':cow_pos,'cow_final_tile':final_tile,'cow_lifecycle_actions':dict(lifecycle),'accepted_sales_cash':dict(sales),'market_purchase_spend':dict(spend),'cash_mismatches':cash_mismatch},sort_keys=True))

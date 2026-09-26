#!/usr/bin/env python3
"""Compact, read-only diagnostics for Kaggriculture replay JSON files.

Usage: python3 experiments/v58_planner_eval/evaluate_replays.py replay.json [replay.json ...]
Actions at frame i were chosen from frame i-1's observation. The evaluator
reports observable productivity proxies; it does not claim hidden engine
acceptance when a replay lacks market commit logs.
"""
from __future__ import annotations
import argparse, json
from collections import Counter, defaultdict
from pathlib import Path


def farm_snapshot(obs, seat):
    farm = obs['farms'][seat]
    tiles = [t for row in farm.get('tiles', []) for t in row]
    animals = Counter(t['animal'] for t in tiles if isinstance(t, dict) and t.get('animal'))
    return farm, animals


def stocks(obs, seat):
    p = obs.get('private', {})
    out = Counter(p.get('shed', {}))
    for inv in p.get('inventories', []): out.update(inv)
    return out


def evaluate(path, seat):
    replay=json.loads(path.read_text()); steps=replay['steps']; cash_by_day={}; action_counts=Counter()
    hand_turns=productive_hands=valid_units=unit_turns=0; feeds=Counter(); sales=Counter(); sale_observed=Counter()
    day_cash=defaultdict(dict); attrition=[]
    for i, states in enumerate(steps):
        obs=states[seat].get('observation') or {}; day=obs.get('day'); hour=obs.get('hour')
        if day is not None and hour == 23:
            farm,_=farm_snapshot(obs,seat); day_cash[day]['close']=round(farm.get('money',0),2)
        if i == 0: continue
        prev=steps[i-1][seat].get('observation') or {}; action=states[seat].get('action') or {}
        pf,pa=farm_snapshot(prev,seat); nf,na=farm_snapshot(obs,seat)
        pre_stock,post_stock=stocks(prev,seat),stocks(obs,seat)
        positions=[pf.get('farmer')]+list(pf.get('hands',[])); next_positions=[nf.get('farmer')]+list(nf.get('hands',[]))
        unit_actions=[action.get('farmer') or ['PASS']]+list(action.get('hands') or [])
        unit_turns += len(unit_actions)
        for u,a in enumerate(unit_actions):
            verb=a[0] if a else 'PASS'; action_counts[verb]+=1
            if u: hand_turns+=1
            moved=u<len(next_positions) and u<len(positions) and next_positions[u]!=positions[u]
            pos=positions[u] if u<len(positions) else None
            before_tile=pf['tiles'][pos[1]][pos[0]] if pos else None
            after_pos=next_positions[u] if u<len(next_positions) else pos
            after_tile=nf['tiles'][after_pos[1]][after_pos[0]] if after_pos else None
            before_inv=(prev.get('private',{}).get('inventories',[])[u] if u<len(prev.get('private',{}).get('inventories',[])) else {})
            after_inv=(obs.get('private',{}).get('inventories',[])[u] if u<len(obs.get('private',{}).get('inventories',[])) else {})
            changed=(moved or before_tile!=after_tile or before_inv!=after_inv)
            if verb=='FEED':
                pos=positions[u] if u<len(positions) else None
                tile=pf['tiles'][pos[1]][pos[0]] if pos else None
                ok=bool(isinstance(tile,dict) and tile.get('animal') and not tile.get('fed_today') and (u<len(prev.get('private',{}).get('inventories',[])) and prev['private']['inventories'][u].get('WHEAT',0)>0))
                feeds['attempts']+=1; feeds['successes']+=int(ok); changed |= ok
            if verb not in ('PASS','WAIT') and changed: valid_units+=1
            if u and verb not in ('PASS','WAIT') and changed: productive_hands+=1
        for order in action.get('market') or []:
            if not order: continue
            op=order[0]; item=order[1] if len(order)>1 else ''
            qty=int(order[2]) if len(order)>2 and isinstance(order[2],(int,float)) else 1
            if op=='SELL':
                # Observable lower bound: only count across-frame inventory drawdown, capped by request.
                accepted=min(qty,max(0,pre_stock[item]-post_stock[item])); sales[item]+=accepted
                price=(prev.get('market') or {}).get('prices',{}).get(item)
                sale_observed[item]+=accepted*(price or 0)
        if day is not None and hour == 0:
            day_cash[day]['open']=round(nf.get('money',0),2)
            if i>1:
                prior=steps[i-1][seat].get('observation') or {}; _,old_animals=farm_snapshot(prior,seat)
                for animal,n in old_animals.items():
                    lost=max(0,n-na[animal])
                    if lost: attrition.append({'day':day,'animal':animal,'count':lost})
    cash=[]
    for d,v in sorted(day_cash.items()):
        if 'open' in v or 'close' in v: cash.append({'day':d,'open':v.get('open'),'close':v.get('close'),'delta':round(v['close']-v['open'],2) if 'open' in v and 'close' in v else None})
    n_hands=hand_turns
    return {'replay':str(path),'seed':(replay.get('info') or {}).get('seed'),'seat':seat,'reward':(replay.get('rewards') or [None]*2)[seat],
      'valid_actor_actions_observed':valid_units,'actor_action_slots':unit_turns,'valid_action_rate':round(valid_units/unit_turns,4) if unit_turns else None,
      'hand_productive_turns':productive_hands,'hand_turns':n_hands,'hand_productive_rate':round(productive_hands/n_hands,4) if n_hands else None,
      'feed_attempts':feeds['attempts'],'feed_successes':feeds['successes'],'feed_success_rate':round(feeds['successes']/feeds['attempts'],4) if feeds['attempts'] else None,
      'accepted_sales_lower_bound_units':dict(sales),'accepted_sales_observed_price_value_lower_bound':dict(sale_observed),
      'animal_attrition_events':attrition,'daily_cash':cash,'action_counts':dict(action_counts)}


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('replays',nargs='+',type=Path); p.add_argument('--seat',type=int,default=0)
    a=p.parse_args(); print(json.dumps([evaluate(x,a.seat) for x in a.replays],indent=2,sort_keys=True))
if __name__=='__main__': main()

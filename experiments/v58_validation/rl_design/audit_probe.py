"""Replay audit for population probe; observation/private-state only."""
from __future__ import annotations
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).with_name('probe95100')
FIRST={'WHEAT':2,'CARROT':2,'TOMATO':8,'STRAWBERRY':10,'MELON':10}
PRICE={'WHEAT':10,'CARROT':20,'TOMATO':50,'STRAWBERRY':100,'MELON':80}
PROD={'WHEAT':25,'CARROT':35,'TOMATO':60,'STRAWBERRY':120,'MELON':250,'EGG':50,'MILK':160,'WOOL':200,'FERTILIZER':100}

def fib_cost(n):
    a=b=1
    for _ in range(n): a,b=b,a+b
    return a

def audit_replay(path,seat):
    replay=json.loads(Path(path).read_text());steps=replay['steps']; op=Counter();effect=Counter();prevalid=Counter(); sales=Counter(); sale_value=Counter(); harvest=Counter();plants=Counter();animals_by_day={};crops_by_day={};hires=Counter();hire_spend=Counter();cash_day={};
    for i,states in enumerate(steps):
        obs=states[seat].get('observation') or {}; day=int(obs.get('day',0) or 0);hour=int(obs.get('hour',0) or 0)
        if hour==23:
            farm=obs['farms'][seat];tiles=[t for row in farm['tiles'] for t in row]
            animals_by_day[day]=dict(Counter(t.get('animal') for t in tiles if isinstance(t,dict) and t.get('animal')))
            crops_by_day[day]=dict(Counter(t.get('crop') for t in tiles if isinstance(t,dict) and t.get('kind')=='PLANT'))
            cash_day[day]=float(farm.get('money',0))
        if i==0:continue
        prev=steps[i-1][seat].get('observation') or {}; action=states[seat].get('action') or {}; pf=prev['farms'][seat]; nf=obs['farms'][seat];board=pf['tiles'];positions=[pf['farmer'],*pf.get('hands',[])]; invs=prev.get('private',{}).get('inventories',[])
        acts=[action.get('farmer') or ['PASS'],*(action.get('hands') or [])]
        plant_req=Counter(a[1] for a in acts if a and a[0]=='PLANT' and len(a)>1)
        seeds=prev.get('private',{}).get('seeds',{})
        for u,a in enumerate(acts):
            if not a:continue
            verb=a[0];op[verb]+=1; x,y=positions[u] if u<len(positions) else (0,0);tile=board[y][x]; inv=invs[u] if u<len(invs) else {}
            valid=False
            if verb in ('NORTH','SOUTH','EAST','WEST'):
                d={'NORTH':(0,-1),'SOUTH':(0,1),'EAST':(1,0),'WEST':(-1,0)}[verb];valid=0<=x+d[0]<len(board) and 0<=y+d[1]<len(board)
            elif verb=='WATER': valid=isinstance(tile,dict) and tile.get('kind')=='PLANT' and not tile.get('watered_today')
            elif verb=='HARVEST':
                if isinstance(tile,dict) and tile.get('yield_units',0)>0:
                    crop=tile.get('crop');animal=tile.get('animal'); obj=animal or crop; age=day-int(tile.get('planted_day',day))
                    valid=animal is not None or (obj and age>=FIRST.get(obj,0))
                    if valid: harvest[obj]+=int(tile.get('yield_units',0) or 0)
            elif verb=='PLANT': valid=len(a)>1 and tile is None and seeds.get(a[1],0)>0 and plant_req[a[1]]<=seeds.get(a[1],0)
            elif verb=='FEED': valid=isinstance(tile,dict) and tile.get('animal') and not tile.get('fed_today') and int(inv.get('WHEAT',0) or 0)>0
            elif verb=='CARE': valid=isinstance(tile,dict) and tile.get('animal') and not tile.get('cared_today')
            elif verb=='COLLECT_FERTILIZER': valid=isinstance(tile,dict) and tile.get('animal') and tile.get('fertilizer_available')
            elif verb=='BUILD_PASTURE': valid=tile is None
            elif verb=='PICKUP': valid=len(a)>1 and tuple((x,y)) in {(4,4),(5,4),(4,5),(5,5)} and int(prev.get('private',{}).get('shed',{}).get(a[1],0) or 0)>0
            elif verb=='PLACE': valid=len(a)>1 and isinstance(tile,dict) and tile.get('kind')=='PASTURE' and 'animal' not in tile and int(inv.get(a[1],0) or 0)>0
            prevalid[verb]+=int(valid)
            if valid:
                after= nf['tiles'][y][x]
                old_inv=inv
                new_inv=(obs.get('private',{}).get('inventories',[])[u] if u<len(obs.get('private',{}).get('inventories',[])) else {})
                next_positions=[nf.get('farmer')]+nf.get('hands',[])
                moved=u<len(next_positions) and [x,y] != next_positions[u]
                if moved or after!=tile or new_inv!=old_inv:effect[verb]+=1
            if verb=='PLANT' and valid:plants[a[1]]+=1
        market=action.get('market') or []
        today=int(prev.get('day',day) or 0)
        n_today=0
        for order in market:
            if not order:continue
            if order[0]=='HIRE':
                cost=fib_cost(n_today);n_today+=1;hires[today]+=1;hire_spend[today]+=cost
            if order[0]=='SELL' and len(order)>1:
                item=order[1];qty=int(order[2]) if len(order)>2 else 1
                before=Counter(prev.get('private',{}).get('shed',{}));after=Counter(obs.get('private',{}).get('shed',{}))
                for inv in prev.get('private',{}).get('inventories',[]):before.update(inv)
                for inv in obs.get('private',{}).get('inventories',[]):after.update(inv)
                n=min(qty,max(0,before[item]-after[item]));sales[item]+=n;sale_value[item]+=n*float((prev.get('market') or {}).get('prices',{}).get(item,0))
    losses=[]
    for day in sorted(animals_by_day):
        if day+1 not in animals_by_day and str(day+1) not in animals_by_day:
            continue  # episode terminal snapshot is not an in-season refresh
        nxt=animals_by_day.get(day+1, animals_by_day.get(str(day+1), {}))
        current=animals_by_day.get(day, animals_by_day.get(str(day), {}))
        for species,count in current.items():
            lost=max(0,count-nxt.get(species,0))
            if lost:losses.append({'day':day+1,'species':species,'count':lost})
    agent= {'seat':seat,'final_coins':(replay.get('rewards') or [None,None])[seat], 'accepted_sales_lb':dict(sales),'sales_value_at_prev_frame_prices_lb':dict(sale_value),'harvested_units_if_valid':dict(harvest),'planted_tile_actions_valid':dict(plants),'actor_ops':dict(op),'action_effects':dict(effect),'engine_precondition_valid':dict(prevalid),'valid_nonmovement_rate':sum(prevalid[k] for k in prevalid if k not in {'NORTH','SOUTH','EAST','WEST'})/max(1,sum(op[k] for k in op if k not in {'NORTH','SOUTH','EAST','WEST','PASS'})), 'hires_by_day':dict(hires),'hire_spend_by_day':dict(hire_spend),'total_hires':sum(hires.values()),'total_hire_cost_estimate':sum(hire_spend.values()),'animals_by_day':animals_by_day,'crop_tiles_by_day':crops_by_day,'cash_day29':cash_day.get(29),'feed_attempts':op.get('FEED',0),'feed_precondition_successes':prevalid.get('FEED',0),'animal_attrition_events':losses}
    return agent

def main():
    results=[]
    for i in (1,2):
        report=json.loads((OUT/f'candidate{i}'/'report.json').read_text())
        for game in report['games']:
            candidate_seat=int(game['candidate_seat']); replay=game['replay_path']
            cand=audit_replay(replay,candidate_seat);opp=audit_replay(replay,1-candidate_seat)
            results.append({'config':i,'candidate':cand,'v50_same_seed_and_market':opp,'runtime_seconds':game['runtime_seconds'],'candidate_sha256':game['agents'][candidate_seat]['sha256'],'v50_sha256':game['agents'][1-candidate_seat]['sha256']})
    out={'purpose':'same-seed replay audit of best-own-cash probe1 and best-margin probe2; market is shared, so baseline outcome is candidate-conditioned.','results':results}
    (OUT/'audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()

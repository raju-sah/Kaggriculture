"""Build an internal research copy with an observation-only economy postprocessor.

The v57 reset route is retained solely as a local development backbone; the
copy is not a submission candidate because its route has public replay lineage.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE=ROOT/'experiments/v57_broad/v57_reset_candidate.py'
PARAMS={
    'cow_ratio':0.90,
    'max_seed_acres':14,
    'max_sheep':8,
    'max_cows':5,
    'max_hires':7,
    'land_cap':4,
    'cash_reserve':500,
}
WRAPPER=r'''
# Local study only: source route copied from frozen v57 reset candidate
# (SHA-256 4173479fe1f80d031d570d1ea23b694dfe86e1d162317a4c9c7df0058a40208e).
ECON_PARAMS = __PARAMS__
_ANIMAL_COST = {"SHEEP": 500, "COW": 400, "GOOSE": 300}
_SEED_COST = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}
_LAND_COST = (0, 1000, 2000, 4000)


def _econ_live_counts(obs, farm):
    counts={"SHEEP":0,"COW":0,"GOOSE":0}
    for row in farm.get("tiles",[]) or []:
        for tile in row:
            if isinstance(tile,dict) and tile.get("animal") in counts:
                counts[tile["animal"]]+=1
    private=obs.get("private",{}) or {}
    for inv in private.get("inventories",[]) or []:
        for item in counts: counts[item]+=max(0,int((inv or {}).get(item,0) or 0))
    shed=private.get("shed",{}) or {}
    for item in counts: counts[item]+=max(0,int(shed.get(item,0) or 0))
    return counts


def economy_postprocess(obs, action, p=None):
    """Apply state-conditioned caps/reserve to current visible order intents."""
    p=ECON_PARAMS if p is None else p
    action=dict(action)
    market=[list(o) for o in (action.get("market",[]) or []) if isinstance(o,list) and o]
    farm=(obs.get("farms",[]) or [])[int(obs.get("player",0) or 0)]
    private=obs.get("private",{}) or {}
    counts=_econ_live_counts(obs,farm)
    crop_counts={k:0 for k in _SEED_COST}
    for row in farm.get("tiles",[]) or []:
        for tile in row:
            if isinstance(tile,dict) and tile.get("kind")=="PLANT" and tile.get("crop") in crop_counts:
                crop_counts[tile["crop"]]+=1
    seed_stock=private.get("seeds",{}) or {}
    money=float(farm.get("money",0) or 0)
    orders=[]; hires=0
    hire_index=max(0,int(farm.get("hires_today",0) or 0))
    land_unlocked=len(farm.get("unlocked_quadrants",[]) or [])
    land_cost_index=max(0,min(3,land_unlocked-1))
    seed_budget=max(0,int(p["max_seed_acres"])-crop_counts.get("WHEAT",0)-int(seed_stock.get("WHEAT",0) or 0))
    prices=(obs.get("market",{}) or {}).get("prices",{}) or {}
    shops=(obs.get("town",{}) or {}).get("unlocked_shops",[]) or []
    ratio=float(p["cow_ratio"])
    cow_preferred=(3<=int(obs.get("day",0) or 0)<=17 and 'YARN_STORE' not in shops
                   and any(s in shops for s in ('PIZZA_SHOP','ICE_CREAM_SHOP','SMOOTHIE_SHOP'))
                   and float(prices.get('MILK',0) or 0)>ratio*float(prices.get('WOOL',200) or 200))
    for order in market:
        op=order[0]
        item=order[1] if len(order)>1 else None
        qty=max(0,int(order[2] or 0)) if len(order)>2 else 1
        if op=='HIRE':
            if hires>=int(p['max_hires']): continue
            hires+=1
            a,b=0,1
            for _ in range(hire_index+1): a,b=b,a+b
            cost=a
        elif op=='BUY_LAND':
            if land_unlocked>=int(p['land_cap']): continue
            cost=_LAND_COST[land_cost_index]
            land_unlocked+=1;land_cost_index=min(3,land_cost_index+1)
        elif op=='BUY_SEED' and item in _SEED_COST:
            if item=='WHEAT': qty=min(qty,seed_budget)
            if qty<=0: continue
            cost=_SEED_COST[item]*qty
            if item=='WHEAT': seed_budget-=qty
        elif op=='BUY_ANIMAL' and item in _ANIMAL_COST:
            if item=='SHEEP' and cow_preferred and counts['COW']<int(p['max_cows']):
                order=['BUY_ANIMAL','COW',qty];item='COW'
            cap=int(p['max_sheep'] if item=='SHEEP' else p['max_cows'] if item=='COW' else 4)
            qty=min(qty,max(0,cap-counts[item]))
            if qty<=0: continue
            order[2]=qty;counts[item]+=qty
            cost=_ANIMAL_COST[item]*qty
        elif op=='BUY_PRODUCT' and item:
            cost=max(0,float(prices.get(item,0) or 0))*qty
        else:
            cost=0
        # Atomic hires and land are charged before market sales in the engine.
        # This conservative cash gate never relies on speculative sale proceeds.
        if op in ('HIRE','BUY_LAND') and money-cost<float(p['cash_reserve']):
            if op=='HIRE': hires-=1
            continue
        if op.startswith('BUY_') and money-cost<float(p['cash_reserve']):
            continue
        if op in ('BUY_LAND','HIRE'):
            money-=cost
            if op=='HIRE': hire_index+=1
        elif op.startswith('BUY_'):
            # Model market transactions in list order; BUY_PRODUCT uses the
            # visible quote as a conservative unit estimate.
            money-=cost
        orders.append(order)
    action['market']=orders
    return action

_base_economy_agent=agent
def agent(obs, configuration=None):
    return economy_postprocess(obs,_base_economy_agent(obs,configuration))

def zzz_economy_policy_entrypoint(obs, configuration=None):
    return agent(obs, configuration)
'''

def build(out:Path, params:dict):
    raw=BASE.read_bytes(); source=raw.decode()
    old="0.9*prices.get('WOOL',200)"
    if source.count(old)!=1: raise SystemExit('unexpected frozen reset source: cow threshold expression not unique')
    source=source.replace(old,"ECON_PARAMS['cow_ratio']*prices.get('WOOL',200)",1)
    # The final economy wrapper is the unique callable entry point used by Kaggle.
    source+='\n'+WRAPPER.replace('__PARAMS__',repr(params))
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(source)
    return hashlib.sha256(out.read_bytes()).hexdigest()

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--params',type=Path)
    ns=ap.parse_args();params=PARAMS if ns.params is None else json.loads(ns.params.read_text())
    print(json.dumps({'candidate':str(ns.out),'sha256':build(ns.out,params),'params':params},indent=2))

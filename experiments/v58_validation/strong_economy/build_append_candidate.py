"""Build an append-only optional WHEAT seed refill around the frozen reset."""
from __future__ import annotations
import hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'experiments/v57_broad/v57_reset_candidate.py'
WRAPPER=r'''
# Internal-only option: preserve the frozen public-replay-derived actor/economy
# route and every base order; append at most one observation-justified seed.
APPEND_PARAMS={"max_extra_wheat_seeds":1,"cash_reserve_after_base":500}
_ANIMAL_COST={"SHEEP":500,"COW":400,"GOOSE":300}
_SEED_COST={"WHEAT":10,"CARROT":20,"TOMATO":50,"STRAWBERRY":100,"MELON":80}
_LAND_COST=(1000,2000,4000)

def _conservative_base_spend(obs,action):
    farm=(obs.get("farms",[]) or [])[int(obs.get("player",0) or 0)]
    money=float(farm.get("money",0) or 0)
    private=obs.get("private",{}) or {}
    prices=(obs.get("market",{}) or {}).get("prices",{}) or {}
    hires_today=max(0,int(farm.get("hires_today",0) or 0));lands=max(0,len(farm.get("unlocked_quadrants",[]) or [])-1)
    spent=0.0
    for order in (action.get("market",[]) or []):
        if not isinstance(order,list) or not order: continue
        op=order[0];item=order[1] if len(order)>1 else None
        qty=max(0,int(order[2] or 0)) if len(order)>2 else 1
        if op=="HIRE":
            a,b=0,1
            for _ in range(hires_today+1):a,b=b,a+b
            spent+=a;hires_today+=1
        elif op=="BUY_LAND":
            if lands<len(_LAND_COST):spent+=_LAND_COST[lands];lands+=1
        elif op=="BUY_SEED":spent+=_SEED_COST.get(item,0)*qty
        elif op=="BUY_ANIMAL":spent+=_ANIMAL_COST.get(item,0)*qty
        elif op=="BUY_PRODUCT":
            # Ignore all SELL proceeds. Double the current visible quote to
            # cover price movement and avoid borrowing from expected sales.
            spent+=2.0*max(1.0,float(prices.get(item,0) or 0))*qty
    return money-spent

def append_optional_seed(obs,action,params=None):
    p=APPEND_PARAMS if params is None else params
    result=dict(action)
    base_market=[list(order) for order in (action.get("market",[]) or [])]
    # The unchanged base intent is always an exact prefix; no removal, rewrite,
    # sorting, or order changes are allowed in this branch.
    result["market"]=base_market
    day=int(obs.get("day",0) or 0)
    if day>25 or len(base_market)>=10:return result
    if any(len(o)>1 and o[:2]==["BUY_SEED","WHEAT"] for o in base_market):return result
    planned=sum(1 for a in [action.get("farmer",["PASS"]),*(action.get("hands",[]) or [])]
                if isinstance(a,list) and len(a)>1 and a[:2]==["PLANT","WHEAT"])
    if planned<=0:return result
    seeds=max(0,int(((obs.get("private",{}) or {}).get("seeds",{}) or {}).get("WHEAT",0) or 0))
    target=max(0,int(p["max_extra_wheat_seeds"]))
    refill=min(target,max(0,target-(seeds-planned)))
    if refill<=0:return result
    available=_conservative_base_spend(obs,action)
    unit_cost=_SEED_COST["WHEAT"]
    if available-unit_cost*refill<float(p["cash_reserve_after_base"]):return result
    result["market"].append(["BUY_SEED","WHEAT",refill])
    return result

_ORIGINAL_ROUTE_AGENT=agent
def zzz_economy_policy_entrypoint(obs,configuration=None):
    action=_ORIGINAL_ROUTE_AGENT(obs,configuration)
    return append_optional_seed(obs,action)
'''

def build(out:Path):
    source=BASE.read_text()+"\n"+WRAPPER
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(source)
    return hashlib.sha256(out.read_bytes()).hexdigest()
if __name__=='__main__':
    out=Path(__file__).resolve().parent/'append_seed_refill.py'
    print(build(out),out)

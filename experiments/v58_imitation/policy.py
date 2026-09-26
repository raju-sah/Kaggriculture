"""Observation-conditioned policy distilled from repeated public elite behavior patterns.
No episode IDs, replay action lookup, or seed-specific state is used at runtime.
"""
from collections import Counter

CROPS = ("WHEAT", "STRAWBERRY", "MELON", "CARROT", "TOMATO")
PRODUCTS = ("WHEAT", "FERTILIZER", "EGGS", "MILK", "WOOL", "STRAWBERRY", "MELON", "CARROT", "TOMATO")
DIRS = ((0,-1,"NORTH"),(0,1,"SOUTH"),(-1,0,"WEST"),(1,0,"EAST"))

def _dist(a,b): return abs(a[0]-b[0])+abs(a[1]-b[1])
def _tile(tiles,p): return tiles[p[1]][p[0]]
def _neighbors(p):
    for dx,dy,d in DIRS:
        q=(p[0]+dx,p[1]+dy)
        if 0<=q[0]<10 and 0<=q[1]<10: yield q,d

def _market(obs, farm, priv):
    day=int(obs.get('day',0)); hour=int(obs.get('hour',0)); cash=farm.get('money',0)
    shed=priv.get('shed',{}); seeds=priv.get('seeds',{}); prices=obs.get('market',{}).get('prices',{})
    town=obs.get('town',{}); demand=Counter()
    for shop in town.get('shops',[]):
        for p in shop.get('demand',[]): demand[p]+=1
    out=[]
    # Elite traces agree on rapid labor/land growth and large throughput, while product mix follows demand.
    if hour==0:
        hires=int(farm.get('hires_today',0))
        if hires<min(9,2+day//2) and cash>1200: out.extend([['HIRE']]*min(3,min(9,2+day//2)-hires))
        q=farm.get('unlocked_quadrants',[])
        if day in (2,5,8) and len(q)<min(4,1+(day+1)//3) and cash>7000: out.append(['BUY_LAND'])
        # Buy seeds in batches only when current seed stock is low; diversify toward observed town demand.
        for crop in sorted(CROPS,key=lambda c:(-demand[c], ('WHEAT','STRAWBERRY','MELON','CARROT','TOMATO').index(c))):
            threshold={'WHEAT':12,'STRAWBERRY':8,'MELON':5,'CARROT':5,'TOMATO':4}[crop]
            if seeds.get(crop,0)<threshold and cash>1800:
                n=min(threshold-seeds.get(crop,0), 8 if crop=='WHEAT' else 4)
                out.append(['BUY_SEED',crop,n]); cash-=n*prices.get(crop,100)
    # Sales use live inventory and market price: preserve wheat feed reserve and pace high-volume staples.
    if hour in (0,1,2,3,4,5,6,7,8,9,10,11):
        wheat_reserve=max(12, sum(1 for trow in farm['tiles'] for t in trow if isinstance(t,dict) and t.get('kind')=='PASTURE' and t.get('animal'))*3)
        for item in PRODUCTS:
            n=int(shed.get(item,0))
            if item=='WHEAT': n=max(0,n-wheat_reserve)
            if item=='FERTILIZER' and prices.get(item,0)<25: continue
            if item in ('STRAWBERRY','MELON','MILK','WOOL') and prices.get(item,0)<40: continue
            if n>0: out.append(['SELL',item,n])
    return out[:10]

def _task_action(obs, farm, pos, priv):
    tiles=farm['tiles']; day=int(obs.get('day',0)); x,y=pos; here=_tile(tiles,pos)
    if here is None and priv.get('seeds',{}).get('WHEAT',0)>0 and day<27: return ['PLANT','WHEAT']
    if isinstance(here,dict):
        k=here.get('kind')
        if k=='PLANT':
            crop=here.get('crop'); age=day-int(here.get('planted_day',day))
            # Harvest one-time crops when ripe; maintain ongoing plants daily.
            ripe={'WHEAT':2,'CARROT':3,'TOMATO':4,'STRAWBERRY':4,'MELON':4}.get(crop,4)
            if age>=ripe and (crop in ('WHEAT','CARROT','MELON') or here.get('yield_units',0)>=2): return ['HARVEST']
            if not here.get('watered_today',False): return ['WATER']
        if k in ('PASTURE','COOP') and here.get('animal'):
            if not here.get('fed_today',False): return ['FEED']
            if not here.get('cared_today',False): return ['CARE']
            if here.get('fertilizer_available'): return ['COLLECT_FERTILIZER']
    tasks=[]
    for yy,row in enumerate(tiles):
      for xx,t in enumerate(row):
        p=(xx,yy)
        if t=='LOCKED': continue
        if t is None:
            # Walk toward a sowing tile only while matching seed stock is available.
            if day<27 and priv.get('seeds',{}).get('WHEAT',0)>0: tasks.append((3+_dist(pos,p),p,['PLANT','WHEAT']))
        elif isinstance(t,dict):
            kind=t.get('kind')
            if kind=='PLANT':
                if not t.get('watered_today',False): tasks.append((0+_dist(pos,p),p,['WATER']))
                elif day-int(t.get('planted_day',day))>=2: tasks.append((4+_dist(pos,p),p,['HARVEST']))
            elif kind in ('PASTURE','COOP') and t.get('animal'):
                if not t.get('fed_today',False): tasks.append((_dist(pos,p),p,['FEED']))
                elif not t.get('cared_today',False): tasks.append((1+_dist(pos,p),p,['CARE']))
                elif t.get('fertilizer_available'): tasks.append((6+_dist(pos,p),p,['COLLECT_FERTILIZER']))
    if not tasks: return ['PASS']
    tasks.sort(key=lambda q:q[0]); _,target,act=tasks[0]
    if target==pos: return act
    options=[]
    for q,d in _neighbors(pos): options.append((_dist(q,target),d))
    options.sort(key=lambda z:z[0])
    return [options[0][1]] if options else ['PASS']

def _is_shed_tile(pos, board_size):
    mid = board_size // 2
    return tuple(pos) in ((mid - 1, mid - 1), (mid, mid - 1), (mid - 1, mid), (mid, mid))

def _engine_action_legal(action, obs, seat, actor, configuration=None):
    """Check necessary actor-action preconditions against the raw current observation."""
    if not isinstance(action, list) or not action: return False
    farms=obs.get("farms",[]); priv=obs.get("private",{})
    if seat<0 or seat>=len(farms): return False
    farm=farms[seat]; tiles=farm.get("tiles",[]); size=int((configuration or {}).get("boardSize",len(tiles) or 10))
    positions=[farm.get("farmer",[0,0])]+list(farm.get("hands",[]))
    if actor<0 or actor>=len(positions): return False
    x,y=positions[actor]; op=action[0]
    if op in ("NORTH","SOUTH","EAST","WEST"):
        dx,dy={"NORTH":(0,-1),"SOUTH":(0,1),"EAST":(1,0),"WEST":(-1,0)}[op]
        # Engine allows crossing locked land; only board edges block movement.
        return 0<=x+dx<size and 0<=y+dy<size
    if op=="PASS": return True
    tile=tiles[y][x] if y<len(tiles) and x<len(tiles[y]) else "LOCKED"
    invs=priv.get("inventories",[]); inv=invs[actor] if actor<len(invs) else {}
    shed=priv.get("shed",{}); shed_adj=_is_shed_tile((x,y),size)
    if op=="PICKUP": return shed_adj and len(action)>1 and int(shed.get(action[1],0) or 0)>0
    if op=="DROP": return shed_adj and any(int(v or 0)>0 for v in inv.values())
    if op=="PLACE":
        if len(action)<2:return False
        item=action[1]
        structure={"COW":"PASTURE","SHEEP":"PASTURE","GOOSE":"COOP"}.get(item)
        if structure and isinstance(tile,dict) and tile.get("kind")==structure and "animal" not in tile:
            return int(inv.get(item,0) or 0)>0
        room=int((configuration or {}).get("shedCapacity",100))-sum(int(v or 0) for v in shed.values())
        return shed_adj and int(inv.get(item,0) or 0)>0 and room>0
    # Tile operations cannot execute on locked land.
    if tile=="LOCKED": return False
    if op=="PLANT": return len(action)>1 and tile is None and int(priv.get("seeds",{}).get(action[1],0) or 0)>0
    if op=="WATER": return isinstance(tile,dict) and tile.get("kind")=="PLANT" and not tile.get("watered_today",False)
    if op=="HARVEST": return isinstance(tile,dict) and int(tile.get("yield_units",0) or 0)>0
    if op=="FEED": return isinstance(tile,dict) and "animal" in tile and not tile.get("fed_today",False) and int(inv.get("WHEAT",0) or 0)>0
    if op=="CARE": return isinstance(tile,dict) and "animal" in tile and not tile.get("cared_today",False)
    if op=="COLLECT_FERTILIZER": return isinstance(tile,dict) and "animal" in tile and bool(tile.get("fertilizer_available",False))
    if op=="FERTILIZE": return isinstance(tile,dict) and tile.get("kind")=="PLANT" and int(inv.get("FERTILIZER",0) or 0)>0
    if op=="DIG": return tile is not None and not (isinstance(tile,dict) and "animal" in tile)
    if op in ("BUILD_COOP","BUILD_PASTURE"): return tile is None
    return False

def _task_action(task):
    """Map a coarse task label to the engine command whose preconditions will be masked."""
    task=str(task or "IDLE").upper()
    if task in ("IDLE","PASS"): return ["PASS"]
    if task=="MOVE": return None
    if task=="WATER_CROP": return ["WATER"]
    if task in ("HARVEST_CROP","HARVEST_ANIMAL"): return ["HARVEST"]
    if task=="FEED_ANIMAL": return ["FEED"]
    if task=="CARE_ANIMAL": return ["CARE"]
    if task in ("COLLECT_FERTILIZER","FERTILIZE","DIG","BUILD_COOP","BUILD_PASTURE","DROP_INVENTORY"):
        return [{"DROP_INVENTORY":"DROP"}.get(task,task)]
    if task=="CLEAR_WEED": return ["DIG"]
    if task.startswith("PLANT_"): return ["PLANT",task[len("PLANT_"):]]
    if task.startswith("PICKUP_"): return ["PICKUP",task[len("PICKUP_"):],1]
    if task.startswith("PLACE_"): return ["PLACE",task[len("PLACE_"):],1]
    return None

def resolve_prediction(obs, seat, actor, verb_scores, task_scores, configuration=None):
    """Resolve task/verb model scores to an engine action under live-state masks.

    Task labels select operation and item arguments. Directional verb scores only
    choose among in-bounds moves; engine-legal movement onto LOCKED tiles remains
    available. If every proposed task is infeasible, the resolver tries safe
    no-argument verb predictions and falls back to PASS.
    """
    farms=obs.get("farms",[])
    if seat<0 or seat>=len(farms): return ["PASS"]
    ranked=sorted(task_scores.items(),key=lambda kv:(-float(kv[1]),str(kv[0])))
    for label,_score in ranked:
        if str(label).upper()=="MOVE":
            for _value,direction in sorted(((float(verb_scores.get(d,-1e9)),d) for d in ("NORTH","SOUTH","EAST","WEST")),key=lambda z:(-z[0],z[1])):
                candidate=[direction]
                if _engine_action_legal(candidate,obs,seat,actor,configuration): return candidate
            continue
        action=_task_action(label)
        if action is not None and _engine_action_legal(action,obs,seat,actor,configuration): return action
    no_arg=("PASS","WATER","HARVEST","FEED","CARE","COLLECT_FERTILIZER","FERTILIZE","DIG","DROP","BUILD_COOP","BUILD_PASTURE")
    for verb in sorted(no_arg,key=lambda v:(-float(verb_scores.get(v,-1e9)),v)):
        action=[verb]
        if _engine_action_legal(action,obs,seat,actor,configuration): return action
    for _value,direction in sorted(((float(verb_scores.get(d,-1e9)),d) for d in ("NORTH","SOUTH","EAST","WEST")),key=lambda z:(-z[0],z[1])):
        action=[direction]
        if _engine_action_legal(action,obs,seat,actor,configuration): return action
    return ["PASS"]

def _opening_action(obs,farm,priv,pos,normal):
    day=int(obs.get('day',0)); tile=_tile(farm['tiles'],pos)
    if day<12 and tile is None:
        # Establish animal infrastructure where worker traffic and seed tasks are not available.
        if day<4 and pos[0]<5 and pos[1]<5:
            kinds=[t.get('kind') for row in farm['tiles'] for t in row if isinstance(t,dict)]
            if 'PASTURE' not in kinds and priv.get('shed',{}).get('COW',0)>0:return ['BUILD_PASTURE']
    return normal


def agent(obs, configuration=None):
    player=int(obs.get('player',0)); farm=obs['farms'][player]; priv=obs.get('private',{})
    positions=[farm.get('farmer',[4,4])]+list(farm.get('hands',[]))
    # Daily actions are recomputed from the live farm; each worker gets a distinct nearest urgent task.
    used=set(); actions=[]
    for pos in positions:
        a=_task_action(obs,farm,pos,priv)
        if a and a[0] in ('WATER','HARVEST','FEED','CARE','COLLECT_FERTILIZER','PLANT'):
            key=(tuple(pos),a[0]);
            if key in used: a=['PASS']
            used.add(key)
        actions.append(a)
    if actions: actions[0] = _opening_action(obs,farm,priv,positions[0], actions[0])
    return {'farmer':actions[0] if actions else ['PASS'],'hands':actions[1:],'market':_market(obs,farm,priv)}

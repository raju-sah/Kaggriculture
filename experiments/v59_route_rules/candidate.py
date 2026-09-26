"""V59 original observation-driven crop route planner.

Daily intent is represented as funded operation tokens and workers are assigned
local stations. No episode-indexed route or action tape is used.
"""
from __future__ import annotations

CROP_TARGET = {"WHEAT": 9, "STRAWBERRY": 3}
LAST_PLANT = {"WHEAT": 24, "STRAWBERRY": 18}


def dist(a,b): return abs(int(a[0])-int(b[0]))+abs(int(a[1])-int(b[1]))
def move(a,b):
    x,y=map(int,a); tx,ty=map(int,b)
    if abs(tx-x)>=abs(ty-y) and tx!=x: return ["EAST" if tx>x else "WEST"]
    if ty!=y: return ["SOUTH" if ty>y else "NORTH"]
    if tx!=x: return ["EAST" if tx>x else "WEST"]
    return ["PASS"]
def near_shed(p,n):
    c=n//2
    return (p[0],p[1]) in ((c-1,c-1),(c,c-1),(c-1,c),(c,c))
def owned_empty(b): return [(x,y) for y,row in enumerate(b) for x,t in enumerate(row) if t is None]
def plant_tiles(b): return [(x,y,t) for y,row in enumerate(b) for x,t in enumerate(row) if isinstance(t,dict) and t.get("kind")=="PLANT"]
def crops_tasks(obs,farm,private,positions,board):
    day=int(obs.get('day',0)); shed=private.get('shed') or {}; invs=list(private.get('inventories') or [])
    invs += [{} for _ in range(max(0,len(positions)-len(invs)))]
    tasks=[]; planted=plant_tiles(board); counts={c:sum(t.get('crop')==c for _,_,t in planted) for c in CROP_TARGET}
    # All current crop operations are explicit one-owner tokens.
    for x,y,t in planted:
        crop=t.get('crop'); yield_n=int(t.get('yield_units',0) or 0)
        if not t.get('watered_today'): tasks.append((0,'WATER',(x,y),crop,2 if crop=='WHEAT' else 1))
        if yield_n >= (3 if crop=='STRAWBERRY' else 4): tasks.append((1,'HARVEST',(x,y),crop,4))
    # Crop tokens exist only when privately funded now; market seed orders replenish later.
    empty=owned_empty(board); seeds=private.get('seeds') or {}
    for crop in ('WHEAT','STRAWBERRY'):
        if day>LAST_PLANT[crop]: continue
        n=min(max(0,CROP_TARGET[crop]-counts[crop]),max(0,int(seeds.get(crop,0) or 0)),len(empty))
        for p in empty[:n]: tasks.append((2,'PLANT',p,crop,2 if crop=='WHEAT' else 3))
        empty=empty[n:]
    # Haul carried goods back to the shed so market orders can liquidate them.
    for i,iv in enumerate(invs):
        goods=sum(max(0,int(v or 0)) for k,v in iv.items() if k not in ('WHEAT',))
        if goods:
            tasks.append((1,'HAUL',(4,4),None,4+goods))
    return tasks

def station(pos,n,actor,count):
    # Deterministic local anchors spread across the active quarter around the shed.
    c=n//2
    anchors=[(c-1,c-1),(c,c-1),(c-1,c),(c,c)]
    return anchors[(actor-1)%4] if actor else anchors[0]

def action(task,pos,inv,private,board,n):
    _,name,target,arg,_=task; x,y=map(int,pos); tile=board[y][x]; shed=private.get('shed') or {}
    if name=='HAUL':
        return ['DROP'] if near_shed((x,y),n) else move(pos,(n//2,n//2))
    if (x,y)!=target: return move(pos,target)
    if name=='WATER': return ['WATER'] if isinstance(tile,dict) and tile.get('kind')=='PLANT' and not tile.get('watered_today') else ['PASS']
    if name=='HARVEST': return ['HARVEST'] if isinstance(tile,dict) and int(tile.get('yield_units',0) or 0)>0 else ['PASS']
    if name=='PLANT': return ['PLANT',arg] if tile is None and int((private.get('seeds') or {}).get(arg,0) or 0)>0 else ['PASS']
    return ['PASS']

def legal(a,obs,seat,actor):
    f=(obs.get('farms') or [])[seat]; b=f.get('tiles') or []; p=[f.get('farmer',[0,0]),*(f.get('hands') or [])][actor]; x,y=map(int,p); n=len(b)
    if not a or not isinstance(a,list): return ['PASS']
    if a[0] in ('NORTH','SOUTH','EAST','WEST'):
        dx,dy={'NORTH':(0,-1),'SOUTH':(0,1),'EAST':(1,0),'WEST':(-1,0)}[a[0]]; return a if 0<=x+dx<n and 0<=y+dy<n else ['PASS']
    tile=b[y][x]
    if a[0]=='WATER': return a if isinstance(tile,dict) and tile.get('kind')=='PLANT' and not tile.get('watered_today') else ['PASS']
    if a[0]=='HARVEST': return a if isinstance(tile,dict) and int(tile.get('yield_units',0) or 0)>0 else ['PASS']
    if a[0]=='PLANT': return a if tile is None and int(((obs.get('private') or {}).get('seeds') or {}).get(a[1],0) or 0)>0 else ['PASS']
    if a[0]=='DROP': return a if near_shed((x,y),n) else ['PASS']
    return ['PASS']

def market(obs,farm,private,board,tasks,positions):
    day=int(obs.get('day',0)); hour=int(obs.get('hour',0)); money=float(farm.get('money',0) or 0); shed=private.get('shed') or {}; seeds=private.get('seeds') or {}; prices=(obs.get('market') or {}).get('prices') or {}; orders=[]
    # Liquidate all harvested stock each turn, except products needed as feed (none in this crop-only route).
    for item,q in sorted(shed.items(),key=lambda kv:float(prices.get(kv[0],0)),reverse=True):
        if item in ('WHEAT','CARROT','TOMATO','STRAWBERRY','MELON','FERTILIZER','EGG','MILK','WOOL') and int(q or 0)>0: orders.append(['SELL',item,int(q)])
    # Commission workers only when recurring crop stations can sustain their service load.
    if hour==0 and day<20:
        crops=plant_tiles(board); uncovered=sum(1 for _,_,t in crops if not t.get('watered_today')) + sum(1 for _,_,t in crops if int(t.get('yield_units',0) or 0)>=4)
        hands=len(positions)-1
        target=min(5,max(1,(uncovered+5)//6))
        if hands<target and money>1800+hands*450: orders.append(['HIRE'])
    # Fund sowing only when near-term actor tokens indicate demand; purchases mature next observation.
    if day<=24 and money>1100:
        for crop in ('WHEAT','STRAWBERRY'):
            present=sum(1 for _,_,t in plant_tiles(board) if t.get('crop')==crop)
            target=CROP_TARGET[crop]
            deficit=target-present-int(seeds.get(crop,0) or 0)
            if deficit>0:
                qty=min(3,deficit)
                cost={'WHEAT':10,'STRAWBERRY':100}[crop]
                if money>1100+qty*cost: orders.append(['BUY_SEED',crop,qty]); money-=qty*cost
    return orders[:10]

def agent(obs,configuration=None):
    farms=obs.get('farms') or []; seat=int(obs.get('player',0) or 0)
    if seat>=len(farms): return {'farmer':['PASS'],'hands':[],'market':[]}
    farm=farms[seat]; private=obs.get('private') or {}; board=farm.get('tiles') or []; n=len(board) or 10
    positions=[farm.get('farmer',[0,0]),*(farm.get('hands') or [])]; invs=list(private.get('inventories') or []); invs += [{} for _ in range(max(0,len(positions)-len(invs)))]
    tasks=crops_tasks(obs,farm,private,positions,board)
    assigned={}; available=set(range(len(positions)))
    # Each worker owns one nearest task per turn; station affinity breaks ties and discourages crossing.
    for task in sorted(tasks,key=lambda z:(z[0],z[2][1],z[2][0])):
        if not available: break
        _,name,target,_,value=task
        actor=min(available,key=lambda i:(dist(positions[i],target)+0.15*dist(station(positions[i],n,i,len(positions)),target),i))
        assigned[actor]=task; available.remove(actor)
    acts=[]
    for i,p in enumerate(positions): acts.append(legal(action(assigned[i],p,invs[i],private,board,n),obs,seat,i) if i in assigned else ['PASS'])
    # Engine plant checks are aggregate and all-or-nothing by crop.
    for crop in CROP_TARGET:
        ids=[i for i,a in enumerate(acts) if a and a[0]=='PLANT' and len(a)>1 and a[1]==crop]
        budget=max(0,int((private.get('seeds') or {}).get(crop,0) or 0))
        for i in ids[budget:]: acts[i]=['PASS']
    return {'farmer':acts[0],'hands':acts[1:],'market':market(obs,farm,private,board,tasks,positions)}

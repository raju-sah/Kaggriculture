# Observation-only controls: no opponent identity, replay seed, or future town data.
from scripts.v19_terminal import align_hands, projected_shed, _move_toward, _shed_access


def _recover_terminal(obs, action):
    """Return carried goods by the last market turn; harvest on the way home."""
    step = obs['step']
    if step < 696:
        return action
    seat = int(obs.get('player', 0))
    farm = obs['farms'][seat]
    tiles = farm['tiles']
    access = _shed_access(len(tiles))
    positions = [farm['farmer'], *farm['hands']]
    inventories = obs['private']['inventories']
    orders = [action['farmer'], *action['hands']]
    prices = obs['market']['prices']
    claimed = set()
    remaining = 718-step
    for i, pos in enumerate(positions):
        x,y=pos; dist=min(abs(x-a)+abs(y-b) for a,b in access)
        inv = inventories[i] if i < len(inventories) else {}
        value = sum(prices.get(k,0)*v for k,v in inv.items())
        if remaining <= dist+1 and value:
            orders[i] = ['DROP'] if dist==0 else _move_toward(pos,access,tiles)
            continue
        # Keep the productive schedule until its final return window.
        if step < 708:
            continue
        choices=[]
        for ty,row in enumerate(tiles):
            for tx,tile in enumerate(row):
                if not isinstance(tile,dict) or (tx,ty) in claimed:
                    continue
                travel=abs(tx-x)+abs(ty-y)
                home=min(abs(tx-a)+abs(ty-b) for a,b in access)
                if travel+home+2 > remaining:
                    continue
                item={'COW':'MILK','SHEEP':'WOOL','GOOSE':'EGG'}.get(tile.get('animal'),tile.get('crop'))
                gain=prices.get(item,0)*tile.get('yield_units',0)
                op='HARVEST'
                if tile.get('fertilizer_available') and prices.get('FERTILIZER',0)>gain:
                    gain=prices.get('FERTILIZER',0);op='COLLECT_FERTILIZER'
                if gain>0:
                    choices.append((gain/(travel+1),gain,-travel,tx,ty,op))
        if choices:
            _,_,_,tx,ty,op=max(choices)
            claimed.add((tx,ty))
            orders[i]=[op] if (x,y)==(tx,ty) else _move_toward(pos,{(tx,ty)},tiles)
        elif value:
            orders[i]=['DROP'] if dist==0 else _move_toward(pos,access,tiles)
        else:
            orders[i]=['PASS']
    action['farmer']=orders[0];action['hands']=orders[1:]
    return action


def agent(obs, configuration=None):
    obs=dict(obs)
    obs['step']=int(obs.get('day',0))*24+int(obs.get('hour',0))
    action=align_hands(_base_agent(obs,configuration),obs)
    action=_recover_terminal(obs,action)
    step=obs['step']
    if step>=696:
        action['market']=[o for o in action['market'] if o[0] not in ('BUY_SEED','BUY_ANIMAL','BUY_LAND','BUY_PRODUCT')]
    # Fertilizer has no town demand: sell surplus before opponent supply lowers prices.
    shed=projected_shed(obs,action)
    reserve=3 if step<696 else 0
    surplus=max(0,shed.get('FERTILIZER',0)-reserve)
    market=action['market']
    if surplus and len(market)<10:
        market.append(['SELL','FERTILIZER',surplus])
    if step>=708:
        action=terminal_market(obs,action,'collision',replace=step==718)
    return action

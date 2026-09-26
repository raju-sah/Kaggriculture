# Fast local feedback replaces only actions that are provably ineffective.
def _repair_noops(obs, action):
    farm=obs['farms'][int(obs.get('player',0))]
    positions=[farm['farmer'],*farm['hands']]
    inventories=obs['private']['inventories']
    orders=[action['farmer'],*action['hands']]
    claimed=set()
    for i,(x,y) in enumerate(positions):
        tile=farm['tiles'][y][x]
        if not isinstance(tile,dict) or (x,y) in claimed:
            continue
        inv=inventories[i] if i<len(inventories) else {}
        op=orders[i][0]
        noop=(op=='PASS' or
              op=='FEED' and (tile.get('fed_today') or not inv.get('WHEAT') or not tile.get('animal')) or
              op=='CARE' and (tile.get('cared_today') or not tile.get('animal')) or
              op=='WATER' and (tile.get('watered_today') or tile.get('kind')!='PLANT') or
              op=='HARVEST' and not tile.get('yield_units') or
              op=='COLLECT_FERTILIZER' and not tile.get('fertilizer_available'))
        if not noop:
            continue
        replacement=None
        if tile.get('animal'):
            if not tile.get('fed_today') and inv.get('WHEAT') and obs['day']<29:
                replacement=['FEED']
            elif not tile.get('cared_today') and obs['day']<29:
                replacement=['CARE']
            elif tile.get('yield_units',0)>0:
                replacement=['HARVEST']
            elif tile.get('fertilizer_available'):
                replacement=['COLLECT_FERTILIZER']
        elif tile.get('kind')=='PLANT' and not tile.get('watered_today'):
            replacement=['WATER']
        if replacement:
            orders[i]=replacement;claimed.add((x,y))
    action['farmer']=orders[0];action['hands']=orders[1:]
    return action


_before_feedback=agent

def agent(obs, configuration=None):
    action=_before_feedback(obs,configuration)
    return _repair_noops(obs,action)

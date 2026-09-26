_before_herd=agent

def agent(obs,configuration=None):
    action=_before_herd(obs,configuration)
    day=int(obs.get('day',0));shops=obs.get('town',{}).get('unlocked_shops',[])
    prices=obs.get('market',{}).get('prices',{})
    counts={'COW':0,'SHEEP':0}
    for farm in obs.get('farms',[]):
        for row in farm.get('tiles',[]):
            for tile in row:
                if isinstance(tile,dict) and tile.get('animal') in counts:
                    counts[tile['animal']]+=1
    milk_shops=sum(s in ('PIZZA_SHOP','ICE_CREAM_SHOP','SMOOTHIE_SHOP') for s in shops)
    wool_shops=shops.count('YARN_STORE')
    favor_cow=(3<=day<=17 and wool_shops==0 and milk_shops>0 and prices.get('MILK',0)>0.9*prices.get('WOOL',200))
    favor_sheep=(3<=day<=19 and wool_shops>0 and milk_shops==0 and counts['SHEEP']+2 < (12*wool_shops+1)/1.33 and prices.get('WOOL',0)>prices.get('MILK',160))
    conversion=('SHEEP','COW') if favor_cow else ('COW','SHEEP') if favor_sheep else None
    if conversion:
        old,new=conversion
        action['market']=[['BUY_ANIMAL',new,o[2]] if len(o)>2 and o[:2]==['BUY_ANIMAL',old] else o for o in action['market']]
    shed=obs['private']['shed'];invs=obs['private']['inventories']
    orders=[action['farmer'],*action['hands']]
    available={k:shed.get(k,0) for k in ('COW','SHEEP')}
    for i,o in enumerate(orders):
        if len(o)>1 and o[1] in available:
            intended=o[1];other='COW' if intended=='SHEEP' else 'SHEEP'
            if o[0]=='PICKUP':
                if available[intended]>0:
                    available[intended]-=1
                elif available[other]>0:
                    orders[i]=['PICKUP',other,1];available[other]-=1
            elif o[0]=='PLACE' and i<len(invs) and not invs[i].get(intended) and invs[i].get(other):
                orders[i]=['PLACE',other,1]
    action['farmer']=orders[0];action['hands']=orders[1:]
    return action

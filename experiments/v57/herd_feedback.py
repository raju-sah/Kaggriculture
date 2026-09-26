_before_herd=agent

def agent(obs, configuration=None):
    action=_before_herd(obs,configuration)
    day=int(obs.get('day',0));shops=obs.get('town',{}).get('unlocked_shops',[])
    prices=obs.get('market',{}).get('prices',{})
    favor_cow=(3<=day<=17 and 'YARN_STORE' not in shops and any(s in shops for s in ('PIZZA_SHOP','ICE_CREAM_SHOP','SMOOTHIE_SHOP')) and prices.get('MILK',0)>0.9*prices.get('WOOL',200))
    if favor_cow:
        action['market']=[['BUY_ANIMAL','COW',o[2]] if len(o)>2 and o[:2]==['BUY_ANIMAL','SHEEP'] else o for o in action['market']]
    # Deliver the animal actually purchased, preserving the pasture/worker route.
    shed=obs['private']['shed'];invs=obs['private']['inventories']
    orders=[action['farmer'],*action['hands']]
    cows_available=shed.get('COW',0)
    sheep_available=shed.get('SHEEP',0)
    for i,o in enumerate(orders):
        if len(o)>1 and o[:2]==['PICKUP','SHEEP']:
            if sheep_available>0:
                sheep_available-=1
            elif cows_available>0:
                orders[i]=['PICKUP','COW',1];cows_available-=1
        elif len(o)>1 and o[:2]==['PLACE','SHEEP'] and i<len(invs) and not invs[i].get('SHEEP') and invs[i].get('COW'):
            orders[i]=['PLACE','COW',1]
    action['farmer']=orders[0];action['hands']=orders[1:]
    return action

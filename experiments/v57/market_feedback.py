# Online exponential estimates of observed price drift, reset per episode/seat.
_v57_price_state={}
_before_market_learning=agent

def agent(obs, configuration=None):
    action=_before_market_learning(obs,configuration)
    seat=int(obs.get('player',0));step=int(obs.get('day',0))*24+int(obs.get('hour',0))
    prices=obs.get('market',{}).get('prices',{})
    old=_v57_price_state.get(seat)
    if old is None or step<=old['step']:
        old={'step':step,'prices':dict(prices),'drift':{}}
    drift={k:0.9*old['drift'].get(k,0)+0.1*(v-old['prices'].get(k,v)) for k,v in prices.items()}
    _v57_price_state[seat]={'step':step,'prices':dict(prices),'drift':drift}
    shed=projected_shed(obs,action)
    market=action['market']
    crowded=sum(shed.values())>75
    for item in sorted(prices,key=lambda k:drift.get(k,0)):
        if item in ('WHEAT','FERTILIZER') or len(market)>=10:
            continue
        quantity=shed.get(item,0)-sum(o[2] for o in market if len(o)>2 and o[0]=='SELL' and o[1]==item)
        if quantity>0 and (crowded or (step>96 and drift.get(item,0)<-0.15)):
            market.append(['SELL',item,min(quantity,10)])
    return action

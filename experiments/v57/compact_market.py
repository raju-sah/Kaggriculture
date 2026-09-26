_before_compaction=agent

def agent(obs,configuration=None):
    action=_before_compaction(obs,configuration)
    stock=projected_shed(obs,action)
    result=[]
    # Empty SELL orders still occupy a simultaneous market slot. Removing them
    # lets actual inventory compete earlier without moving a buy across a sale.
    for order in action.get('market',[]):
        if len(order)>2 and order[0]=='SELL':
            item=order[1];quantity=min(order[2],stock.get(item,0))
            if quantity<=0:
                continue
            stock[item]-=quantity
            if result and result[-1][:2]==order[:2]:
                result[-1][2]+=quantity
            else:
                result.append(['SELL',item,quantity])
        else:
            result.append(list(order))
            if len(order)>2 and order[0] in ('BUY_PRODUCT','BUY_ANIMAL'):
                stock[order[1]]=stock.get(order[1],0)+order[2]
    action['market']=result
    return action

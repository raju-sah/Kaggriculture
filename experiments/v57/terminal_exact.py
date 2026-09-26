from scripts.v19_terminal import monetizable_terminal_units, terminal_market, projected_shed

def agent(obs,configuration=None):
    obs=dict(obs)
    if obs.get('step') is None:
        obs['step']=int(obs.get('day',0))*24+int(obs.get('hour',0))
    action=_base_agent(obs,configuration)
    action=monetizable_terminal_units(obs,action,obs['step'])
    if obs['step']==718:
        action=terminal_market(obs,action,'collision',replace=True)
    return action

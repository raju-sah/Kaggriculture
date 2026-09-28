import copy as _c
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location('_v92_base', '/home/raju/AI-ML Projects/Kaggle Competition/Kaggriculture/experiments/v92_overflow_guard/candidate.py')
_v92 = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_v92)
MIN_YIELD_TO_DEFER = 2
TARGET_YIELD = 3
def _defer(obs, action):
    from kaggle_environments.envs.kaggriculture import kaggriculture as _eng
    if not obs or not action: return action
    day = int(obs.get('day', 0) or 0); seat = int(obs.get('player', 0) or 0)
    farms = obs.get('farms') or []
    if seat >= len(farms): return action
    farm = farms[seat]; action = _c.deepcopy(action); changed = False
    for idx, ua in enumerate([action.get('farmer')] + list(action.get('hands') or [])):
        if not (isinstance(ua, list) and ua) or ua[0] != 'HARVEST': continue
        pos = _eng._farmer_position(farm, idx)
        if pos is None: continue
        tile = farm['tiles'][pos[1]][pos[0]]
        if not (isinstance(tile, dict) and tile.get('kind') == 'PLANT' and tile.get('crop') == 'STRAWBERRY'): continue
        planted_day = int(tile.get('planted_day', day) or day)
        if day - planted_day < _eng.CROPS['STRAWBERRY']['first_yield_day']: continue
        y = int(tile.get('yield_units', 0) or 0)
        if MIN_YIELD_TO_DEFER <= y < TARGET_YIELD:
            if idx == 0: action['farmer'] = ['WATER']
            else: action['hands'][idx-1] = ['WATER']
            changed = True
    return action
def _kaggle_submission_entrypoint(obs, configuration=None):
    base = _v92._v92_entrypoint(obs, configuration)
    return _defer(obs, base)

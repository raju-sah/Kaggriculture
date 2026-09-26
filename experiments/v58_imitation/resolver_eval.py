"""Replay-state check of the legal action/argument resolver on held-out episodes.
Uses one-hot oracle task/verb labels to isolate mapping and legality masks; it does
not estimate learned-model accuracy or policy reward.
"""
import json
from collections import Counter
from pathlib import Path
from policy import resolve_prediction, _engine_action_legal

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'experiments/v58_validation/imitation_data/episodes.json'

def task_label(action, obs, seat, actor):
    if not isinstance(action,list) or not action:return 'IDLE'
    op=action[0]; args=action[1:]
    if op in ('PASS','WAIT'):return 'IDLE'
    if op in ('NORTH','SOUTH','EAST','WEST'):return 'MOVE'
    farm=obs['farms'][seat];positions=[farm.get('farmer',[0,0])]+list(farm.get('hands',[]));x,y=positions[actor]
    tile=farm['tiles'][y][x]
    if op=='HARVEST':return 'HARVEST_ANIMAL' if isinstance(tile,dict) and tile.get('animal') else 'HARVEST_CROP'
    if op=='PLANT':return 'PLANT_'+str(args[0]) if args else 'PLANT_UNKNOWN'
    if op=='WATER':return 'WATER_CROP'
    if op=='DIG':return 'CLEAR_WEED' if isinstance(tile,dict) and tile.get('kind')=='WEED' else 'DIG'
    if op=='FEED':return 'FEED_ANIMAL'
    if op=='CARE':return 'CARE_ANIMAL'
    if op=='COLLECT_FERTILIZER':return 'COLLECT_FERTILIZER'
    if op=='FERTILIZE':return 'FERTILIZE'
    if op in ('BUILD_COOP','BUILD_PASTURE'):return op
    if op=='PICKUP':return 'PICKUP_'+str(args[0]) if args else 'PICKUP_UNKNOWN'
    if op=='PLACE':return 'PLACE_'+str(args[0]) if args else 'PLACE_UNKNOWN'
    if op=='DROP':return 'DROP_INVENTORY'
    return 'IDLE'

def main():
    episodes=json.loads(DATA.read_text())['episodes']; held=[e for e in episodes if e['split']=='heldout']
    seen=set();counts=Counter();matched=Counter();invalid=Counter();safe=Counter();invalid_examples=[]
    for item in held:
        ep_id=str(item['episode_id'])
        if ep_id in seen:continue
        seen.add(ep_id); path=Path(item['source_path'])
        if not path.is_absolute():path=ROOT/path
        replay=json.loads(path.read_text());config=replay.get('configuration') or {}
        # The replay stores each transition action beside the resulting observation.
        # Pair action at t+1 with the pre-action observation at t.
        steps=replay['steps']
        for step_i in range(len(steps)-1):
            observations=steps[step_i]; action_states=steps[step_i+1]
            for seat in range(2):
                state=observations[seat];obs=state.get('observation') or {};farm=obs.get('farms',[{}]*2)[seat]
                if not obs:continue
                actions=action_states[seat].get('action') or {}
                actlist=[actions.get('farmer')] if seat==0 else list(actions.get('hands') or [])
                positions=[farm.get('farmer',[0,0])]+list(farm.get('hands',[]))
                for actor_slot,act in enumerate(actlist):
                    actor=0 if seat==0 else actor_slot+1
                    if actor>=len(positions) or not isinstance(act,list) or not act:continue
                    gold_legal=_engine_action_legal(act,obs,seat,actor,config)
                    counts['actors']+=1; counts['legal_gold']+=int(gold_legal)
                    if not gold_legal:
                        invalid[act[0]]+=1
                        if len(invalid_examples)<8:invalid_examples.append({'episode':ep_id,'step':step_i,'seat':seat,'actor':actor,'action':act})
                    ts=task_label(act,obs,seat,actor)
                    resolved=resolve_prediction(obs,seat,actor,{act[0]:1.0},{ts:1.0},config)
                    resolved_safe=_engine_action_legal(resolved,obs,seat,actor,config)
                    safe['total']+=1;safe['safe']+=int(resolved_safe)
                    same=(resolved[:2]==act[:2] and (act[0] not in ('PLACE','PICKUP') or int(resolved[2] if len(resolved)>2 else 1)>=1))
                    matched['all']+=int(same);matched['n']+=1
                    if gold_legal:matched['legal_gold']+=int(same);matched['legal_gold_n']+=1
                    else:matched['invalid_to_pass']+=int(resolved==['PASS'])
    report={'heldout_episode_groups':len(seen),'heldout_actor_decisions':counts['actors'],'gold_legal_precondition_rate':counts['legal_gold']/max(1,counts['actors']),'resolver_output_safe_rate':safe['safe']/max(1,safe['total']),'oracle_label_mapping_match_rate':matched['all']/max(1,matched['n']),'match_rate_given_gold_legal':matched['legal_gold']/max(1,matched['legal_gold_n']),'invalid_gold_actions_by_op':dict(invalid),'invalid_examples':invalid_examples,'limitation':'One-hot labels from each recorded held-out action isolate resolver mapping/masks; these are oracle labels, not classifier predictions, engine acceptance logs, or a policy score.'}
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()

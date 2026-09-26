"""Attribute per-hour actor actions and idle causes from retained probe replays."""
from __future__ import annotations
import importlib.util, json
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).with_name('probe95100')
MODULE=OUT/'candidates'/'probe1.py'  # crop8/herd3/staff6 first-generation winner
SPEC=importlib.util.spec_from_file_location('probe_policy',MODULE);m=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(m)
DIRS=('NORTH','SOUTH','EAST','WEST')

def pos_list(farm):return [farm.get('farmer',[0,0]),*(farm.get('hands') or [])]
def coords(a):return tuple(a or (0,0))
def assigned_plan(obs):
    farms=obs.get('farms') or [];seat=int(obs.get('player',0) or 0);farm=farms[seat];private=obs.get('private') or {};board=farm.get('tiles') or [];positions=pos_list(farm);invs=list(private.get('inventories') or []);invs.extend({} for _ in range(len(positions)-len(invs)));tasks=m._tasks(obs,farm,private,positions,board,m.PARAMS);assigned={};available=set(range(len(positions)))
    for task in tasks:
        _prio,name,target,arg=task
        if not available:break
        if name in ('FEED','WATER','HARVEST'):
            eligible=[]
            for actor in available:
                inv=invs[actor]
                if name=='FEED' and int(inv.get('WHEAT',0) or 0)<=0 and not int((private.get('shed') or {}).get('WHEAT',0) or 0):continue
                eligible.append(actor)
            if not eligible and name=='FEED':eligible=list(available)
        else:eligible=list(available)
        actor=min(eligible or list(available),key=lambda i:(m._dist(positions[i],target[0]) if isinstance(target,list) and target and isinstance(target[0],tuple) else m._dist(positions[i],target),i))
        assigned[actor]=task;available.remove(actor)
    expected=[]
    for actor,p in enumerate(positions):
        task=assigned.get(actor)
        a=['PASS'] if task is None else m._task_action(task,p,invs[actor],private,farm,board,len(board) or 10)
        expected.append(m._legal_fallback(a,obs,seat,actor,None))
    # Reproduce the aggregate seed reservation that will be the scheduler fix.
    seeds=private.get('seeds') or {};by_crop=defaultdict(list)
    for actor,a in enumerate(expected):
        if a and a[0]=='PLANT' and len(a)>1:by_crop[a[1]].append(actor)
    for crop,actors in by_crop.items():
        for actor in actors[max(0,int(seeds.get(crop,0) or 0)):]:expected[actor]=['PASS']
    return tasks,assigned,expected

def replay(path,seat):
    r=json.loads(Path(path).read_text());stats=Counter();by_hour=defaultdict(Counter);by_task=defaultdict(Counter);by_day=defaultdict(Counter);churn=Counter();last_goal={};matches=Counter();plant_audit=[]
    for i in range(1,len(r['steps'])):
        prev=r['steps'][i-1][seat].get('observation') or {};step=r['steps'][i][seat];nxt=step.get('observation') or {};recorded=step.get('action') or {};hour=int(prev.get('hour',0) or 0);day=int(prev.get('day',0) or 0);farm=prev['farms'][seat];positions=pos_list(farm);tasks,assigned,expected=assigned_plan(prev);actual=[recorded.get('farmer') or ['PASS'],*(recorded.get('hands') or [])];
        # Count per-crop atomic seed collisions from the exact issued action.
        req=Counter(a[1] for a in actual if a and a[0]=='PLANT' and len(a)>1);seeds=prev.get('private',{}).get('seeds',{})
        atomic={c:n for c,n in req.items() if n>int(seeds.get(c,0) or 0)}
        if atomic:plant_audit.append({'day':day,'hour':hour,'requested':dict(req),'available':dict(seeds),'atomic_rejected_crops':atomic})
        next_pos=pos_list((nxt.get('farms') or [farm,farm])[seat]);
        for actor,act in enumerate(actual):
            task=assigned.get(actor);name=task[1] if task else 'NO_TASK';target=task[2] if task else None; expected_a=expected[actor] if actor<len(expected) else ['PASS']; action=act[0] if act else 'PASS'; role='farmer' if actor==0 else 'hand'; key=(role,name)
            stats['actor_slots']+=1;by_hour[hour]['actor_slots']+=1;by_day[day]['actor_slots']+=1;stats[f'action:{action}']+=1;by_hour[hour][f'action:{action}']+=1;by_task[name][f'action:{action}']+=1;by_day[day][f'action:{action}']+=1
            if actor<len(expected) and act==expected_a:matches['same_action']+=1
            else:matches['different_action']+=1
            if task is None:
                stats['unassigned_no_task']+=1;by_hour[hour]['unassigned_no_task']+=1;by_day[day]['unassigned_no_task']+=1
                p=prev.get('private') or {};seed=int((p.get('seeds') or {}).get('WHEAT',0) or 0);farm_tiles=[t for row in farm.get('tiles',[]) for t in row];crop_n=sum(1 for t in farm_tiles if isinstance(t,dict) and t.get('kind')=='PLANT' and t.get('crop')=='WHEAT')
                if crop_n<int(m.PARAMS['crop_target']) and seed==0:reason='crop_target_waiting_seed'
                elif day>=24 and crop_n==0:reason='late_season_no_crop_target'
                else:reason='no_remaining_schedulable_task'
                stats[f'idle:{reason}']+=1;by_hour[hour][f'idle:{reason}']+=1;by_day[day][f'idle:{reason}']+=1
            else:
                by_task[name]['assigned']+=1
                if action in DIRS:
                    src=coords(positions[actor]);dst=coords(target[0] if isinstance(target,list) and target and isinstance(target[0],tuple) else target);after=coords(next_pos[actor] if actor<len(next_pos) else src);before_d=m._dist(src,dst);after_d=m._dist(after,dst);moved=after!=src;progress=moved and after_d<before_d
                    cat='travel_progress' if progress else 'travel_no_progress'
                    stats[cat]+=1;by_hour[hour][cat]+=1;by_task[name][cat]+=1;by_day[day][cat]+=1
                    ident=(actor,name,target)
                    old=last_goal.get(actor)
                    if old and old[0]!=day and day!=old[0]:last_goal[actor]=ident
                    elif old and old[1:]!=(name,target):churn['target_changes_midday']+=1;last_goal[actor]=ident
                    else:last_goal[actor]=ident
                else:
                    if expected_a==['PASS']:
                        reason='task_blocked_by_resource_or_stage';stats[reason]+=1;by_hour[hour][reason]+=1;by_task[name][reason]+=1;by_day[day][reason]+=1
                    else:
                        stats['assigned_operation_attempts']+=1;by_hour[hour]['assigned_operation_attempts']+=1;by_task[name]['assigned_operation_attempts']+=1;by_day[day]['assigned_operation_attempts']+=1
                        if action==expected_a[0]:stats['assigned_operation_match']+=1;by_hour[hour]['assigned_operation_match']+=1;by_task[name]['assigned_operation_match']+=1;by_day[day]['assigned_operation_match']+=1
            if action=='PLANT' and atomic:
                stats['engine_atomic_plant_conflict']+=1;by_hour[hour]['engine_atomic_plant_conflict']+=1;by_day[day]['engine_atomic_plant_conflict']+=1;by_task['PLANT']['engine_atomic_plant_conflict']+=1
    return {'replay':str(path),'seat':seat,'candidate_hash':None,'param_vector':m.PARAMS,'counts':dict(stats),'action_reproduction':dict(matches),'target_churn':dict(churn),'per_hour_of_day':{str(k):dict(v) for k,v in sorted(by_hour.items())},'by_task':{k:dict(v) for k,v in by_task.items()},'per_day':{str(k):dict(v) for k,v in sorted(by_day.items())},'atomic_seed_conflicts':plant_audit}

def main():
    results=[]
    for g in json.loads((OUT/'candidate1'/'report.json').read_text())['games']:
        results.append(replay(g['replay_path'],int(g['candidate_seat'])))
    out={'purpose':'offline replay-action attribution using the frozen pre-fix config1 agent; compares original issued actions to reconstructed tasks.','results':results}
    (OUT/'instrumentation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()

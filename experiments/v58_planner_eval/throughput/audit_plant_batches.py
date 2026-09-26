"""Read-only action-batch audit of probe1 and same-game v50 replays (seed 95100)."""
from __future__ import annotations
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
GAMES=ROOT/'experiments/v58_validation/rl_design/probe95100/candidate1/games'
OUT=Path(__file__).with_name('probe1_seed95100.json')
MOVES={'NORTH':(0,-1),'SOUTH':(0,1),'EAST':(1,0),'WEST':(-1,0)}

def pos_list(farm): return [farm.get('farmer',[0,0]), *farm.get('hands',[])]
def tile_at(board,pos):
    x,y=map(int,pos)
    return board[y][x] if 0<=y<len(board) and 0<=x<len(board[y]) else None

def stock(inv,actor):
    xs=inv.get('inventories') or []
    return xs[actor] if actor<len(xs) else {}

def analyze(path,seat,label):
    replay=json.loads(path.read_text());steps=replay['steps']
    plant=Counter(); day_crop=Counter(); batch_fail=Counter(); individual_fail=Counter(); applied=Counter()
    blocked_by_worker=Counter();blocked_by_pos=Counter();blocked_days=Counter();batch_rows=[]
    effects=Counter(); no_effect=Counter(); no_effect_day=Counter();no_effect_worker=Counter();no_effect_pos=Counter()
    invalid_move=Counter();water=Counter();water_day=Counter()
    plant_results_by_worker=Counter(); plant_results_by_pos=Counter()
    hand_slots=productive_hands=0
    for i in range(1,len(steps)):
        pre=(steps[i-1][seat].get('observation') or {})
        post=(steps[i][seat].get('observation') or {})
        action=steps[i][seat].get('action') or {}
        day=int(pre.get('day',0) or 0); hour=int(pre.get('hour',0) or 0)
        pf=(pre.get('farms') or [{}])[seat]; nf=(post.get('farms') or [{}])[seat]
        pboard=pf.get('tiles') or []; nboard=nf.get('tiles') or []
        positions=pos_list(pf); after_positions=pos_list(nf)
        acts=[action.get('farmer') or ['PASS'],*(action.get('hands') or [])]
        private=pre.get('private') or {}; seeds=private.get('seeds') or {}
        demand=Counter(a[1] for a in acts if a and a[0]=='PLANT' and len(a)>1)
        blocked={crop for crop,n in demand.items() if n>int(seeds.get(crop,0) or 0)}
        blocked_details=[]
        for actor,a in enumerate(acts):
            if not a: continue
            op=a[0]; pos=positions[actor] if actor<len(positions) else None
            before=tile_at(pboard,pos) if pos is not None else None
            moved=actor<len(after_positions) and actor<len(positions) and after_positions[actor]!=positions[actor]
            after=tile_at(nboard,after_positions[actor]) if actor<len(after_positions) else before
            oldinv=stock(private,actor); newinv=stock(post.get('private') or {},actor)
            changed=bool(moved or before!=after or oldinv!=newinv)
            effects[op]+=int(changed)
            if actor>0: hand_slots+=1
            if op=='PLANT' and len(a)>1:
                crop=a[1];plant[crop,'requested']+=1;day_crop[day,crop,'requested']+=1
                plant_results_by_worker[crop,actor,'requested']+=1
                plant_results_by_pos[crop,tuple(pos) if pos is not None else None,'requested']+=1
                if crop in blocked:
                    plant[crop,'atomic_cancelled']+=1;day_crop[day,crop,'atomic_cancelled']+=1
                    blocked_by_worker[crop,actor]+=1;blocked_by_pos[crop,tuple(pos) if pos is not None else None]+=1;blocked_days[day]+=1
                    blocked_details.append({'worker':actor,'pos':pos,'crop':crop})
                elif before is not None:
                    plant[crop,'occupied_tile']+=1;day_crop[day,crop,'occupied_tile']+=1
                elif int(seeds.get(crop,0) or 0)<=0:
                    plant[crop,'no_seed']+=1;day_crop[day,crop,'no_seed']+=1
                elif isinstance(after,dict) and after.get('kind')=='PLANT' and after.get('crop')==crop:
                    plant[crop,'applied']+=1;day_crop[day,crop,'applied']+=1
                    plant_results_by_worker[crop,actor,'applied']+=1;plant_results_by_pos[crop,tuple(pos) if pos is not None else None,'applied']+=1
                elif not changed:
                    plant[crop,'unexplained_no_change']+=1;day_crop[day,crop,'unexplained_no_change']+=1
            if op=='WATER':
                tile=before
                valid=isinstance(tile,dict) and tile.get('kind')=='PLANT' and not tile.get('watered_today')
                water['requested']+=1;water['precondition_valid']+=int(valid);water['effect']+=int(changed)
                water_day[day,'requested']+=1;water_day[day,'precondition_valid']+=int(valid);water_day[day,'effect']+=int(changed)
            if op in MOVES and not moved:
                dx,dy=MOVES[op];x,y=positions[actor]
                in_bounds=0<=x+dx<len(pboard[0]) and 0<=y+dy<len(pboard)
                invalid_move['boundary_noop' if not in_bounds else 'in_bounds_no_move']+=1
            if actor>0:
                if op not in ('PASS','WAIT') and changed:productive_hands+=1
                if op not in ('PASS','WAIT') and not changed:
                    no_effect[op]+=1;no_effect_day[day,op]+=1;no_effect_worker[actor,op]+=1;no_effect_pos[tuple(pos) if pos is not None else None,op]+=1
                elif op in ('PASS','WAIT'):
                    no_effect['PASS/no_task_or_fallback']+=1;no_effect_day[day,'PASS/no_task_or_fallback']+=1
        for crop in blocked:
            batch_fail[crop]+=1
            if len(batch_rows)<30:
                batch_rows.append({'day':day,'hour':hour,'crop':crop,'seeds_available':int(seeds.get(crop,0) or 0),'requests':demand[crop],'cancelled_requests':demand[crop],'workers_and_positions':[d for d in blocked_details if d['crop']==crop]})
    hand_rate=productive_hands/hand_slots if hand_slots else None
    return {'label':label,'path':str(path),'seed':(replay.get('info') or {}).get('seed'),'seat':seat,'final_coins':(replay.get('rewards') or [None,None])[seat],
            'hand_productive_turns':productive_hands,'hand_turn_slots':hand_slots,'hand_productive_rate':round(hand_rate,4) if hand_rate is not None else None,
            'plant_by_crop':{crop:{k:v for (c,k),v in plant.items() if c==crop} for crop in sorted({c for c,_ in plant})},
            'daily_wheat_plant':{str(d):{k:v for (dd,c,k),v in day_crop.items() if dd==d and c=='WHEAT'} for d in sorted({d for d,c,k in day_crop if c=='WHEAT'})},
            'wheat_atomic_block_turns':batch_fail.get('WHEAT',0),'sample_atomic_blocks':batch_rows,
            'water':dict(water),'water_by_day':{str(d):{k:v for (dd,k),v in water_day.items() if dd==d} for d in sorted({d for d,k in water_day})},
            'movement_no_effect':dict(invalid_move),'nonmovement_no_effect':dict(no_effect),
            'no_effect_by_day_op':{f'{d}:{op}':v for (d,op),v in no_effect_day.items()},
            'no_effect_by_worker_op':{f'{u}:{op}':v for (u,op),v in no_effect_worker.items()},
            'no_effect_by_position_op':{f'{p}:{op}':v for (p,op),v in no_effect_pos.items()},
            'atomic_cancelled_by_worker':{f'{c}:{u}':v for (c,u),v in blocked_by_worker.items()},
            'atomic_cancelled_by_position':{f'{c}:{p}':v for (c,p),v in blocked_by_pos.items()}}

def main():
    rows=[]
    for path in sorted(GAMES.glob('*.json')):
        meta=json.loads(path.read_text()); replay=Path(meta['replay_path']); cseat=int(meta['candidate_seat'])
        rows.append(analyze(replay,cseat,'probe1'))
        rows.append(analyze(replay,1-cseat,'v50_same_replay'))
    OUT.write_text(json.dumps({'purpose':'read-only action-batch audit; frame action compared with previous observation and resulting frame','rows':rows},indent=2)+'\n')
    print(json.dumps({'rows':[{k:r[k] for k in ('label','seat','final_coins','hand_productive_rate','plant_by_crop','water','movement_no_effect','nonmovement_no_effect','wheat_atomic_block_turns')} for r in rows]},indent=2))
if __name__=='__main__':main()

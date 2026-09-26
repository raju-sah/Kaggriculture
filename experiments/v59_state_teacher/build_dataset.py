"""Query frozen v57 on student-visited states; emit aggregate state/action rows."""
import argparse, hashlib, importlib.util, json, re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('v59_teacher',ROOT/'experiments/v57_broad/v57_reset_candidate.py')
teacher=importlib.util.module_from_spec(spec); spec.loader.exec_module(teacher)
def features(obs, seat, actor):
    farm=obs['farms'][seat]; coords=[farm.get('farmer',[0,0]),*farm.get('hands',[])]
    pos=coords[actor] if actor<len(coords) else [0,0]
    x,y=int(pos[0]),int(pos[1]); tiles=farm.get('tiles',[])
    tile=tiles[y][x] if y<len(tiles) and x<len(tiles[y]) and isinstance(tiles[y][x],dict) else {}
    inventories=obs.get('private',{}).get('inventories',[]); inv=inventories[actor] if actor<len(inventories) else {}
    targets={'yield':[],'crop':[],'animal':[],'unfed':[],'fertilizer':[]}
    for yy,row in enumerate(tiles):
        for xx,t in enumerate(row):
            if not isinstance(t,dict): continue
            if t.get('yield_units',0)>0: targets['yield'].append((xx,yy))
            if t.get('crop'): targets['crop'].append((xx,yy))
            if t.get('animal'): targets['animal'].append((xx,yy))
            if t.get('animal') and not t.get('fed_today'): targets['unfed'].append((xx,yy))
            if t.get('fertilizer_available'): targets['fertilizer'].append((xx,yy))
    f={'actor':actor,'x':x,'y':y,'tile_kind':tile.get('kind','EMPTY'),'crop':tile.get('crop','none'),
       'yield_here':int(tile.get('yield_units',0) or 0),'watered':int(bool(tile.get('watered'))),
       'animal_here':tile.get('animal','none'),'fed_today':int(bool(tile.get('fed_today'))),
       'carry':tuple(sorted((k,int(v)) for k,v in inv.items() if isinstance(v,(int,float)) and v)),
       'day':int(obs.get('day',0) or 0),'hour':int(obs.get('hour',0) or 0),
       'cash_bin':int(float(farm.get('money',0) or 0)//5000),
       'shops':len(obs.get('town',{}).get('unlocked_shops',[]))}
    for n,pts in targets.items(): f['near_'+n]=min((abs(x-a)+abs(y-b) for a,b in pts),default=99)
    return f
def label(cmd): return '|'.join(map(str,cmd[:2])) if isinstance(cmd,list) and cmd else 'PASS'
def main():
    p=argparse.ArgumentParser(); p.add_argument('replays',nargs='+',type=Path); p.add_argument('--seat',choices=('0','1','auto'),required=True); p.add_argument('--stride',type=int,default=4); p.add_argument('--out',type=Path,required=True); a=p.parse_args()
    rows=[]; counts=Counter(); sources=[]
    for path in a.replays:
        m=re.search(r'-seed-(\d+)-([ab]{2})-',path.name)
        seed=int(m.group(1)) if m else None
        seat=(1 if m.group(2)=='ba' else 0) if a.seat=='auto' and m else int(a.seat) if a.seat!='auto' else 0
        replay=json.loads(path.read_text()); sources.append({'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        for tick,frame in enumerate(replay.get('steps',[])):
            if tick % a.stride: continue
            if not frame or len(frame)<=seat: continue
            obs=frame[seat].get('observation') or {}
            if not obs.get('farms'): continue
            action=teacher.agent(obs)
            cmds=[action.get('farmer',['PASS']),*action.get('hands',[])]
            for actor,cmd in enumerate(cmds):
                f=features(obs,seat,actor); lab=label(cmd)
                rows.append({'seed':seed,'features':f,'label':lab,'day':f['day'],'tick':tick})
                counts[(f['day'],lab)]+=1
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows))
    a.out.with_suffix('.meta.json').write_text(json.dumps({'rows':len(rows),'sources':sources,'features':sorted(rows[0]['features']) if rows else [],'day_label_counts':{f'{d}:{l}':n for (d,l),n in counts.items()},'labels':'v57 re-queried on current student observation; step, seed, replay id excluded from feature set','rights':'research only; replay-derived route pending rights clarification'},indent=2)+'\n')
    print(json.dumps({'rows':len(rows),'classes':len({r['label'] for r in rows})}))
if __name__=='__main__': main()

"""Staged V74 exact-loader search: spent seed only, own cash primary."""
from __future__ import annotations
import concurrent.futures, json, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; HERE=Path(__file__).resolve().parent
m=json.loads((HERE/'manifest.json').read_text()); py=sys.executable

def run_one(t, opponent, seeds, phase):
 out=HERE/'runs'/f'{phase}_{t["name"]}'
 cmd=[py,'-m','simulation.tournament','--candidate',str(ROOT/t['path']),
      '--opponent',f'{opponent}={ROOT/m["opponents"][opponent]}',
      '--seeds',','.join(map(str,seeds)),'--workers','2','--timeout','120',
      '--replay-policy','errors','--output-dir',str(out)]
 started=time.perf_counter(); p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
 if p.returncode: raise RuntimeError(f'{t["name"]} vs {opponent} rc={p.returncode}: {p.stderr[-2000:]}')
 report=json.loads((out/'report.json').read_text()); games=report['games']
 cash=[]; margin=[]; prod=[]; by_seed={}
 ops=('PLANT','WATER','HARVEST','FERTILIZE','FEED','CARE','COLLECT_FERTILIZER')
 for g in games:
  cs=g['candidate_seat']; coins=g['final_coins']; a=g['action_counts'][cs]
  val=sum(a[k].get(op,0) for k in ('farmer','hands') for op in ops)
  c=coins[cs]; md=c-coins[1-cs]
  cash.append(c); margin.append(md); prod.append(val)
  q=by_seed.setdefault(str(g['seed']),{'cash':[],'margin':[],'direct_production_actions':[]})
  q['cash'].append(c);q['margin'].append(md);q['direct_production_actions'].append(val)
 row={'name':t['name'],'opponent':opponent,'phase':phase,'sha256':t['sha256'],
      'games':len(games),'wins':report['summary']['wins'],
      'candidate_errors':report['summary']['candidate_errors']+report['summary']['infrastructure_errors'],
      'mean_own_cash':sum(cash)/len(cash),'mean_margin':sum(margin)/len(margin),
      'mean_direct_production_actions':sum(prod)/len(prod),
      'by_seed':{k:{n:sum(v)/len(v) for n,v in q.items()} for k,q in by_seed.items()},
      'mean_match_runtime_seconds':report['summary']['mean_runtime_seconds'],
      'wall_seconds':time.perf_counter()-started,
      'report':str((out/'report.json').relative_to(ROOT))}
 print(json.dumps(row),flush=True); return row

started=time.perf_counter(); rows=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 fs=[pool.submit(run_one,t,'V56',m['screen_seeds'],'screen_v56') for t in m['templates']]
 for f in concurrent.futures.as_completed(fs): rows.append(f.result())
base=next(r for r in rows if r['name']=='v70_control')
for r in rows:
 r['own_cash_lift_vs_v70']=r['mean_own_cash']-base['mean_own_cash']
 r['margin_lift_vs_v70']=r['mean_margin']-base['mean_margin']
 r['production_lift_vs_v70']=r['mean_direct_production_actions']-base['mean_direct_production_actions']
rows.sort(key=lambda r:r['name'])
(HERE/'screen_results.json').write_text(json.dumps({'wall_seconds':time.perf_counter()-started,'screen_rows':rows},indent=2)+'\n')
# Expand only when a template beats V70 own cash on the training block.
expand=[r for r in rows if r['name']!='v70_control' and r['candidate_errors']==0 and r['own_cash_lift_vs_v70']>0]
expansion=[]
if expand:
 chosen=[next(t for t in m['templates'] if t['name']==r['name']) for r in expand]
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  fs=[pool.submit(run_one,t,'V56',[m['expansion_seed']],'expand_v56') for t in chosen]
  expansion=[f.result() for f in concurrent.futures.as_completed(fs)]
 by_name={r['name']:r for r in rows}
 confirmed=[]
 for r in expansion:
  parent=by_name[r['name']]
  lift947=parent['by_seed']['94700']['cash']-57066.0
  lift928=r['by_seed']['92802']['cash']-59722.0
  r['cash_lift_vs_v70_seed94700']=lift947;r['cash_lift_vs_v70_seed92802']=lift928
  if min(lift947,lift928)>=m['promotion_gate']['vs_v70_cash_lift_each_screen_seed'] and r['candidate_errors']==0:
   confirmed.append(r)
 # Only a strong two-block winner may touch the confirm seed.
 if confirmed:
  names={r['name'] for r in confirmed}
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
   fs=[pool.submit(run_one,next(t for t in m['templates'] if t['name']==n),'V56',[m['confirm_seed']],'confirm_v56') for n in sorted(names)]
   expansion.extend(f.result() for f in concurrent.futures.as_completed(fs))
(HERE/'staged_results.json').write_text(json.dumps({'expansion_rows':expansion},indent=2)+'\n')
print(json.dumps({'wall_seconds':time.perf_counter()-started,'base':base,'screen_rows':rows,'expansion_rows':expansion},indent=2))

"""Seed-paired V101 tournament summary and day-6 gate audit."""
import csv, json
from pathlib import Path
HERE=Path(__file__).resolve().parent

def read_report(path): return json.loads(path.read_text())

def paired(path):
 report=read_report(path); by={}
 for g in report['games']:
  s=int(g['seed']); seat=int(g['candidate_seat']); coins=g.get('final_coins') or [0,0]
  by.setdefault(s,[]).append({'margin':coins[seat]-coins[1-seat], 'own':coins[seat], 'result':g['candidate_result'], 'record':g})
 return report,by

r,by=paired(HERE/'runs/unconditional_vs_v92_retry/report.json')
rows=[]
for seed,rs in sorted(by.items()):
 rows.append({'seed':seed,'margin':rs[0]['margin'],'own_cash':sum(x['own'] for x in rs)/len(rs),'result':rs[0]['result']})
with (HERE/'unconditional_seed_margins.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
print('unconditional seeds',len(rows),'W/L/D',sum(x['result']=='win' for x in rows),sum(x['result']=='loss' for x in rows),sum(x['result']=='draw' for x in rows),'mean margin',sum(x['margin'] for x in rows)/len(rows),'median',sorted(x['margin'] for x in rows)[len(rows)//2])

p=HERE/'runs/milk_sink_gate_vs_v92_dev20/report.json'
if p.exists():
 rep,b=paired(p)
 grows=[]
 for seed,rs in sorted(b.items()):
  g=rs[0]['record']; replay=json.loads(Path(g['replay_path']).read_text())
  seat=int(g['candidate_seat']); obs=replay['steps'][150][seat]['observation']; shops=(obs.get('town') or {}).get('unlocked_shops',[])
  fires=any(s in {'PIZZA_SHOP','ICE_CREAM_SHOP','SMOOTHIE_SHOP'} for s in shops)
  market=obs.get('market') or {}
  actions=[]
  if fires:
   # Record the submitted action at the day-6 h6 turn to confirm the quantity split.
   actions=(replay['steps'][150][seat].get('action') or {})
  grows.append({'seed':seed,'margin':rs[0]['margin'],'own_cash':sum(x['own'] for x in rs)/len(rs),'result':rs[0]['result'],'gate':fires,'shops':';'.join(shops),'milk_price':(market.get('prices') or {}).get('MILK'),'wool_price':(market.get('prices') or {}).get('WOOL'),'milk_inventory':(market.get('inventory') or {}).get('MILK'),'wool_inventory':(market.get('inventory') or {}).get('WOOL')})
 with (HERE/'milk_sink_seed_margins.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=grows[0]);w.writeheader();w.writerows(grows)
 t=[x for x in grows if x['gate']];nt=[x for x in grows if not x['gate']]
 print('gate seeds',len(grows),'triggered',len(t),'margin triggered',sum(x['margin'] for x in t)/len(t) if t else None,'W/L',sum(x['result']=='win' for x in t),sum(x['result']=='loss' for x in t),'no-op mean margin',sum(x['margin'] for x in nt)/len(nt) if nt else None)

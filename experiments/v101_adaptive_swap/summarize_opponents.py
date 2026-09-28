"""Summarize paired candidate-vs-opponent margin at distinct-seed level."""
import csv, json, sys
from collections import defaultdict
from pathlib import Path
p=Path(sys.argv[1]); r=json.loads(p.read_text()); by=defaultdict(list)
for g in r['games']:
 seat=int(g['candidate_seat']); coins=g['final_coins']
 by[(g['opponent'],int(g['seed']))].append({'margin':coins[seat]-coins[1-seat], 'own':coins[seat], 'result':g['candidate_result']})
rows=[]
for (op,seed),xs in sorted(by.items()):
 rows.append({'opponent':op,'seed':seed,'mean_margin':sum(x['margin'] for x in xs)/len(xs), 'mean_own_cash':sum(x['own'] for x in xs)/len(xs), 'seat_results':';'.join(x['result'] for x in xs)})
out=p.parent/'seed_opponent_margins.csv'
with out.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
for op in sorted({x['opponent'] for x in rows}):
 xs=[x for x in rows if x['opponent']==op]; ms=[x['mean_margin'] for x in xs]
 w=sum(m>0 for m in ms);l=sum(m<0 for m in ms);d=sum(m==0 for m in ms)
 print(op, f'seeds={len(xs)} W/L/D={w}/{l}/{d}', f'mean_margin={sum(ms)/len(ms):.1f}',f'median_margin={sorted(ms)[len(ms)//2]:.1f}')
print('wrote',out)

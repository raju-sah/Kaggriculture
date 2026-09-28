"""Summarize paired V101 results and infer the one extra BUY_ANIMAL order."""
import csv, json, sys
from collections import defaultdict
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit('usage: summarize_panel.py PATH_TO_report.json')
report_path = Path(sys.argv[1])
report = json.loads(report_path.read_text())
by = defaultdict(list)
for g in report['games']:
    seat = int(g['candidate_seat'])
    coins = g['final_coins']
    ca = g['action_counts'][seat]['market'].get('BUY_ANIMAL', 0)
    oa = g['action_counts'][1-seat]['market'].get('BUY_ANIMAL', 0)
    by[int(g['seed'])].append({
        'margin': coins[seat] - coins[1-seat],
        'own_cash': coins[seat],
        'result': g['candidate_result'],
        'buy_animal_delta': ca - oa,
        'candidate_seat': seat,
        'opponent_seat': 1-seat,
    })
rows=[]
for seed, xs in sorted(by.items()):
    fires = {x['buy_animal_delta'] == 1 for x in xs}
    if len(fires) != 1 or {x['buy_animal_delta'] for x in xs} not in ({1}, {0}):
        raise SystemExit(f'non-symmetric or unexpected BUY_ANIMAL delta at seed {seed}: {xs}')
    x=xs[0]
    if any(y['margin'] != x['margin'] for y in xs):
        print('WARNING seat margins differ at seed', seed)
    rows.append({'seed':seed,'trigger':next(iter(fires)),'buy_animal_delta':x['buy_animal_delta'],
                 'margin':x['margin'],'own_cash_mean':sum(y['own_cash'] for y in xs)/len(xs),
                 'result':x['result']})
out=report_path.parent/'seed_margins.csv'
with out.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)

def stats(xs):
    if not xs: return 'n=0'
    ms=[x['margin'] for x in xs]
    return (f"n={len(xs)} mean_margin={sum(ms)/len(ms):.1f} "
            f"W/L/D={sum(x['result']=='win' for x in xs)}/"
            f"{sum(x['result']=='loss' for x in xs)}/"
            f"{sum(x['result']=='draw' for x in xs)}")
print(report_path)
print('all:',stats(rows))
print('triggered:',stats([x for x in rows if x['trigger']]))
print('no-op:',stats([x for x in rows if not x['trigger']]))
print('wrote',out)

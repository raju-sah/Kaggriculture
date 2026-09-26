#!/usr/bin/env python3
"""Seed-balanced summary and comparison with the V63 elite panel."""
import csv, json, statistics, collections
from pathlib import Path
R=Path(__file__).resolve().parent
ELITE=R.parent/'v63_elite_panel'
local_players=json.loads((R/'players.json').read_text())
local_games=json.loads((R/'games.json').read_text())
public=list(csv.DictReader((ELITE/'players.csv').open()))
reset=[p for p in local_players if p['is_reset_v57']]
opp=[p for p in local_players if not p['is_reset_v57']]

def median(v): return statistics.median(v) if v else None
def q(v,p):
 if not v:return None
 s=sorted(v); return s[round((len(s)-1)*p)]
def describe(rows,key):
 values=[float(r[key]) for r in rows if r.get(key) is not None]
 return {'n_rows':len(values),'median':median(values),'p25':q(values,.25),'p75':q(values,.75),'min':min(values) if values else None,'max':max(values) if values else None}

def seed_balanced(rows):
 groups=collections.defaultdict(list)
 for r in rows: groups[r['seed']].append(r)
 out=[]
 numeric=[k for k,v in rows[0].items() if isinstance(v,(int,float)) and not isinstance(v,bool)]
 for seed,rs in groups.items():
  x={'seed':seed}
  for k in numeric:x[k]=statistics.mean(float(r[k]) for r in rs if r.get(k) is not None)
  # state/shop composition is fixed by the environment seed for the day; use first row.
  x.update({k:rs[0][k] for k in rs[0] if k.startswith('state_day') or k.startswith('day') and k.endswith(('shops','crop_mix','animal_mix'))})
  for op in ('SELL','BUY_PRODUCT'):
   keys=set().union(*(r.get('net_product_by_kind',{}).get(op,{}) for r in rs))
   if op=='SELL': x.setdefault('net_product_by_kind',{})[op]={k:statistics.mean(float(r.get('net_product_by_kind',{}).get(op,{}).get(k,0)) for r in rs) for k in keys}
   else: x.setdefault('net_product_by_kind',{})[op]={k:statistics.mean(float(r.get('net_product_by_kind',{}).get(op,{}).get(k,0)) for r in rs) for k in keys}
  x['opponents']=sorted({r['opponent'] for r in rs})
  out.append(x)
 return out

reset_seed=seed_balanced(reset)
opp_by_seed=seed_balanced(opp)
phases=['opening_0_5','day6_11','day12_23','late_24_29']
macro=['cash','hands','quadrants','crop_tiles','animals','shed_items']
local_desc={}
public_desc={}
for day in (6,12,20,29):
 for metric in macro:
  key=f'day{day}_{metric}' if metric!='shed_items' else None
  lk=f'state_day{day}'
  local_field='animal_tiles' if metric=='animals' else metric
  vals=[float(r[lk][local_field]) for r in reset_seed if local_field in r[lk]]
  local_desc[f'day{day}_{metric}']={'n_seeds':len(vals),'median':median(vals),'p25':q(vals,.25),'p75':q(vals,.75),'min':min(vals) if vals else None,'max':max(vals) if vals else None}
  if metric!='shed_items': public_desc[f'day{day}_{metric}']=describe(public,key)
for phase in phases:
 for name in ('cash_delta','sales','product_purchases','seed_purchases','animal_purchases','land_hire_cost','market_net_product'):
  key=f'{phase}_{name}'
  local_desc[key]={'n_seeds':len(reset_seed),'median':median([float(r[key]) for r in reset_seed]),'p25':q([float(r[key]) for r in reset_seed],.25),'p75':q([float(r[key]) for r in reset_seed],.75)}
  public_desc[key]=describe(public,key)

# Product-level net accepted product flow: sell proceeds minus purchase cost.
def net_by_product(row):
 data=row.get('net_product_by_kind')
 if isinstance(data,str): data=json.loads(data)
 if not data:return {}
 sells=data.get('SELL',{}); buys=data.get('BUY_PRODUCT',{})
 return {k:float(sells.get(k,0))-float(buys.get(k,0)) for k in set(sells)|set(buys)}
local_product=collections.defaultdict(list)
for r in reset_seed:
 for item,val in net_by_product(r).items():local_product[item].append(val)
public_product=collections.defaultdict(list)
for r in public:
 for item,val in net_by_product(r).items():public_product[item].append(val)
product_desc={k:{'local_reset_n_seeds':len(local_product[k]),'local_reset_median':median(local_product[k]),'local_reset_p25':q(local_product[k],.25),'local_reset_p75':q(local_product[k],.75),
                'elite_n_participant_rows':len(public_product[k]),'elite_median':median(public_product[k]),'elite_p25':q(public_product[k],.25),'elite_p75':q(public_product[k],.75)} for k in sorted(set(local_product)|set(public_product))}

# By shop regime: retain seed-level rows so seat-swap replays do not count twice.
shop_summary={}
for day in (6,12):
 for label,predicate in [('YARN_STORE',lambda s:'YARN_STORE' in s['shops']),
                          ('MILK_SHOP',lambda s:any(x in s['shops'] for x in ('PIZZA_SHOP','ICE_CREAM_SHOP','SMOOTHIE_SHOP'))),
                          ('BOTH',lambda s:'YARN_STORE' in s['shops'] and any(x in s['shops'] for x in ('PIZZA_SHOP','ICE_CREAM_SHOP','SMOOTHIE_SHOP'))),
                          ('NEITHER',lambda s:'YARN_STORE' not in s['shops'] and not any(x in s['shops'] for x in ('PIZZA_SHOP','ICE_CREAM_SHOP','SMOOTHIE_SHOP')))]:
  rows=[r for r in reset_seed if predicate(r[f'state_day{day}'])]
  shop_summary[f'day{day}_{label}']={'n_seeds':len(rows),'median_cash':median([r[f'state_day{day}']['cash'] for r in rows]),
    'median_crops':median([r[f'state_day{day}']['crop_tiles'] for r in rows]),
    'median_animals':median([r[f'state_day{day}']['animal_tiles'] for r in rows]),
    'median_day12_23_net' : median([r['day12_23_market_net_product'] for r in rows]) if day==12 else None}
  shop_summary[f'day{day}_regimes']=collections.Counter(r[f'state_day{day}']['shop_regime'] for r in reset_seed).most_common()

# Paired reset-vs-opponent metric differences, reduced to one mean per seed.
paired=[]
bygame=collections.defaultdict(dict)
for r in local_players:
 bygame[(r['seed'],r['game_id'])][r['is_reset_v57']]=r
for key,values in bygame.items():
 if True in values and False in values:
  a,b=values[True],values[False]
  paired.append({'seed':key[0],'opponent':a['opponent'],'reward_diff':a['final_cash']-b['final_cash'],
   'product_net_diff':a['net_product_market']-b['net_product_market'],
   'wheat_fert_net_diff':a['wheat_fert_net']-b['wheat_fert_net'],
   'day6_cash_diff':a['day6_cash']-b['day6_cash'],'day12_cash_diff':a['day12_cash']-b['day12_cash'],
   'day12_23_net_diff':a['day12_23_market_net_product']-b['day12_23_market_net_product']})
byseed_pair=collections.defaultdict(list)
for r in paired:byseed_pair[r['seed']].append(r)
paired_seed=[]
for seed,rs in byseed_pair.items():
 x={'seed':seed}
 for k in ('reward_diff','product_net_diff','wheat_fert_net_diff','day6_cash_diff','day12_cash_diff','day12_23_net_diff'):
  x[k]=statistics.mean(r[k] for r in rs)
 x['opponents']=sorted({r['opponent'] for r in rs});paired_seed.append(x)
paired_desc={k:{'n_seeds':len(paired_seed),'median':median([x[k] for x in paired_seed]),'p25':q([x[k] for x in paired_seed],.25),'p75':q([x[k] for x in paired_seed],.75),
                'positive_rate':sum(x[k]>0 for x in paired_seed)/len(paired_seed)} for k in ('reward_diff','product_net_diff','wheat_fert_net_diff','day6_cash_diff','day12_cash_diff','day12_23_net_diff')}
opp_summary={}
for name in sorted({name for r in reset_seed for name in r['opponents']}):
 rows=[r for r in reset_seed if name in r['opponents']]
 raw=[r for r in reset if r['opponent']==name]
 opp_summary[name]={'n_seeds':len(rows),'n_games':len(raw),'reset_reward_margin_median':median([r['final_cash']-r['opponent_reward'] for r in raw]),'reset_product_net_median':median([r['net_product_market'] for r in raw])}

summary={'provenance':{'reset_sha256':'4173479fe1f80d031d570d1ea23b694dfe86e1d162317a4c9c7df0058a40208e','unique_seeds':len(reset_seed),'games':len(local_games),'reset_rows':len(reset),'opponent_lineages':sorted({name for r in reset_seed for name in r['opponents']}),'cash_mismatches':sum(g['settlement_audit']['cash_mismatches'] for g in local_games),'aligned_transitions':sum(g['settlement_audit']['aligned_transitions'] for g in local_games),'snapshot_index':'day0 step0; day6/12/20/29 at day*24+1'},
 'local_reset_seed_balanced':local_desc,'elite_all_player_rows':public_desc,'accepted_net_by_product':product_desc,'shop_regime':shop_summary,'paired_reset_minus_opponent':paired_desc,'by_opponent':opp_summary,
 'caveat':'Saved, purposively selected diagnostic games; one opponent match per distinct seed with available seat swaps. Repeated seat-swap replays are reduced to one mean per seed in paired summaries. Descriptive only; no causal effect or new games.'}
(R/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
print('local seeds/games',len(reset_seed),len(local_games),'mismatches',summary['provenance']['cash_mismatches'],'opponents',summary['provenance']['opponent_lineages'])
for k in ['accepted_sell_value','accepted_product_buy_value','accepted_product_net','wheat_fert_net','day6_cash','day6_hands','day6_crop_tiles','day6_animals','day12_cash','day12_hands','day12_crop_tiles','day12_animals','day12_23_market_net_product','late_24_29_market_net_product']:
 if k in ('day6_cash','day6_hands','day6_crop_tiles','day6_animals','day12_cash','day12_hands','day12_crop_tiles','day12_animals'):
  d=local_desc[k]; print(k,'local median/p25/p75',d['median'],d['p25'],d['p75'],'elite median',public_desc.get(k,{}).get('median'))
 elif k in local_desc:
  d=local_desc[k]; print(k,'local median',d['median'],'elite median',public_desc.get(k,{}).get('median'))
 else:
  ek={'accepted_sell_value':'total_sales','accepted_product_buy_value':'total_product_purchases','accepted_product_net':'net_product_market','wheat_fert_net':None}[k]
  pv=[float(r[ek]) for r in public] if ek else [sum(net_by_product(r).get(i,0) for i in ('WHEAT','FERTILIZER')) for r in public]
  print(k,'local median',median([float(r[k]) for r in reset]),'elite median',median(pv))
print('paired',paired_desc)

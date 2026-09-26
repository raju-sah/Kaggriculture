#!/usr/bin/env python3
"""Create compact participant/game tables and descriptive paired summaries."""
import csv,json,statistics,collections
from pathlib import Path
R=Path(__file__).resolve().parent
profiles=json.loads((R/'profiles.json').read_text())
settles={x['episode_id']:x for x in json.loads((R/'accepted_sales.json').read_text())}
manifest=json.loads((R/'episode_manifest.json').read_text())
meta={g['episode_id']:g for g in manifest['games']}
phases=['opening_0_5','day6_11','day12_23','late_24_29']
players=[]; games=[]
for game in profiles:
 eid=int(game['episode_id']); settle=settles[eid]; m=meta[eid]
 raw=json.loads((R/'replays'/f'episode-{eid}-replay.json').read_text())
 rews=game.get('rewards') or [0,0]; winner=max(range(2),key=lambda s:rews[s]) if rews[0]!=rews[1] else None
 pair=[]
 for seat,p in enumerate(game['players']):
  a=settle['players'][seat]
  snaps={int(z['day']):z for z in p['snapshots']}
  row={'episode_id':eid,'seed':game.get('seed'),'module_version':game.get('module_version'),
       'leaderboard_team':m['leaderboard_team'],'submission_id':m['submission_id'],'submission_score':m['submission_public_score'],
       'seat':seat,'team_name':p['name'],'reward':rews[seat],'winner':seat==winner if winner is not None else None,
       'opponent':game['players'][1-seat]['name'],'opponent_reward':rews[1-seat],
       'game_gap_coins':abs(rews[0]-rews[1]),'cash_mismatches':settle['audit']['cash_mismatches'],
       'aligned_transitions':settle['audit']['aligned_transitions'],'replay_sha256':m['replay_sha256']}
  # Results at standardized boundary snapshots. day0 is initial; other snapshots are one action step into the day to avoid zero-worker transition artifacts.
  for d,s in snaps.items():
   prefix=f'day{d}_'
   row[prefix+'cash']=s['money']; row[prefix+'hands']=s['hands']; row[prefix+'quadrants']=len(s['unlocked_quadrants'])
   row[prefix+'crop_tiles']=sum(s['crops'].values()); row[prefix+'animals']=sum(s['animals'].values())
   row[prefix+'crop_mix']=json.dumps(s['crops'],sort_keys=True,separators=(',',':'))
   row[prefix+'animal_mix']=json.dumps(s['animals'],sort_keys=True,separators=(',',':'))
   row[prefix+'shed']=json.dumps(s['shed'],sort_keys=True,separators=(',',':'))
   row[prefix+'shed_value_current_price']=sum(int(q)*float(s['market_prices'].get(k,0)) for k,q in s['shed'].items())
   row[prefix+'shops']=json.dumps(s['shops'],separators=(',',':'))
   row[prefix+'market_prices']=json.dumps(s['market_prices'],sort_keys=True,separators=(',',':'))
  close=p['closing']
  row['closing_step']=close['observation_step']; row['closing_day']=close['day']; row['closing_hour']=close['hour']
  row['closing_cash']=close['money']; row['closing_hands']=close['hands']; row['closing_quadrants']=len(close['unlocked_quadrants'])
  row['closing_crop_tiles']=sum(close['crops'].values()); row['closing_animals']=sum(close['animals'].values())
  row['closing_crop_mix']=json.dumps(close['crops'],sort_keys=True,separators=(',',':'))
  row['closing_animal_mix']=json.dumps(close['animals'],sort_keys=True,separators=(',',':'))
  row['closing_shed']=json.dumps(close['shed'],sort_keys=True,separators=(',',':'))
  row['closing_shed_value_current_price']=sum(int(q)*float(close['market_prices'].get(k,0)) for k,q in close['shed'].items())
  row['closing_shops']=json.dumps(close['shops'],separators=(',',':'))
  for phase in phases:
   cash_start_idx={'opening_0_5':0,'day6_11':6*24,'day12_23':12*24,'late_24_29':24*24}[phase]
   cash_end_idx={'opening_0_5':6*24,'day6_11':12*24,'day12_23':24*24,'late_24_29':len(raw['steps'])-1}[phase]
   # Load cash boundary observations exactly, independent of accepted transaction aggregation.
   c0=raw['steps'][cash_start_idx][seat]['observation']['farms'][seat]['money']
   c1=raw['steps'][cash_end_idx][seat]['observation']['farms'][seat]['money']
   row[f'{phase}_cash_delta']=round(float(c1)-float(c0),2)
   val=a['accepted_value_by_phase'].get(phase,{})
   row[f'{phase}_sales']=round(float(val.get('SELL',0)),2)
   row[f'{phase}_product_purchases']=round(float(val.get('BUY_PRODUCT',0)),2)
   row[f'{phase}_seed_purchases']=round(float(val.get('BUY_SEED',0)),2)
   row[f'{phase}_animal_purchases']=round(float(val.get('BUY_ANIMAL',0)),2)
   row[f'{phase}_land_hire_cost']=round(float(a['land_and_hire_net_cost_by_phase'].get(phase,0)),2)
   row[f'{phase}_market_net_product']=row[f'{phase}_sales']-row[f'{phase}_product_purchases']
   row[f'{phase}_accepted_product_by_kind']=json.dumps({op: val.get(op,{}) for op in ('SELL','BUY_PRODUCT')},sort_keys=True,separators=(',',':'))
  # Full-game totals
  row['total_sales']=a['accepted_value_by_operation'].get('SELL',0)
  row['total_product_purchases']=a['accepted_value_by_operation'].get('BUY_PRODUCT',0)
  row['net_product_market']=row['total_sales']-row['total_product_purchases']
  row['net_product_by_kind']=json.dumps({op:a['accepted_value_by_product'].get(op,{}) for op in ('SELL','BUY_PRODUCT')},sort_keys=True,separators=(',',':'))
  row['audit_max_cash_error']=settle['audit']['max_cash_error']
  players.append(row); pair.append(row)
 # aggregate market state at start day 6/12 from profile snapshots; winner seat metadata
 games.append({'episode_id':eid,'seed':game.get('seed'),'module_version':game.get('module_version'),
  'leaderboard_team':m['leaderboard_team'],'submission_id':m['submission_id'],'episode_created':m['episode_created'],
  'seat0_team':pair[0]['team_name'],'seat1_team':pair[1]['team_name'],'seat0_reward':rews[0],'seat1_reward':rews[1],
  'winner_team':None if winner is None else pair[winner]['team_name'],'winner_seat':winner,
  'winner_reward':None if winner is None else rews[winner],'loser_reward':None if winner is None else rews[1-winner],
  'winner_gap':abs(rews[0]-rews[1]),'winner_leaderboard_lineage':m['leaderboard_team'],
  'seat0_day6_cash':pair[0].get('day6_cash'),'seat1_day6_cash':pair[1].get('day6_cash'),
  'cash_mismatches':settle['audit']['cash_mismatches'],'aligned_transitions':settle['audit']['aligned_transitions'],
  'replay_sha256':m['replay_sha256']})

def write_csv(path,rows):
 keys=[]
 for x in rows:
  for k in x:
   if k not in keys:keys.append(k)
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
write_csv(R/'players.csv',players);write_csv(R/'games.csv',games)
# Descriptive paired comparison; no claim of randomized treatment or causal effect.
winners=[x for x in players if x['winner'] is True]; losers=[x for x in players if x['winner'] is False]
metrics=['day6_cash','day6_hands','day6_quadrants','day6_crop_tiles','day6_animals','day12_cash','day12_hands','day12_quadrants','day12_crop_tiles','day12_animals','day20_cash','day20_hands','day20_crop_tiles','day20_animals','day20_shed_value_current_price','day29_cash','day29_hands','day29_crop_tiles','day29_animals','closing_cash','closing_shed_value_current_price','closing_hands','net_product_market']
summary={}
for metric in metrics:
 vals=[float(x[metric]) for x in winners+losers if x.get(metric) not in ('',None)]
 w=[float(x[metric]) for x in winners if x.get(metric) not in ('',None)]
 l=[float(x[metric]) for x in losers if x.get(metric) not in ('',None)]
 summary[metric]={'n_winners':len(w),'n_losers':len(l),'winner_median':statistics.median(w) if w else None,'loser_median':statistics.median(l) if l else None,
  'median_winner_minus_loser':statistics.median(w)-statistics.median(l) if w and l else None,
  'pair_winner_advantage_rate':sum(1 for g in games if next(x[metric] for x in players if x['episode_id']==g['episode_id'] and x['winner'] is True)>next(x[metric] for x in players if x['episode_id']==g['episode_id'] and x['winner'] is False))/max(1,len(games))}
# Phase/product winner minus loser paired medians, with market products distinct.
for phase in phases:
 for metric in [phase+'_cash_delta',phase+'_sales',phase+'_product_purchases',phase+'_market_net_product',phase+'_seed_purchases',phase+'_animal_purchases',phase+'_land_hire_cost']:
  diffs=[]
  for g in games:
   win=next((x for x in players if x['episode_id']==g['episode_id'] and x['winner'] is True),None)
   los=next((x for x in players if x['episode_id']==g['episode_id'] and x['winner'] is False),None)
   if win and los: diffs.append(float(win[metric])-float(los[metric]))
  summary[metric]={'n_pairs':len(diffs),'median_winner_minus_loser':statistics.median(diffs) if diffs else None,'wins_over_games':sum(d>0 for d in diffs)}
unique_seed=len({g['seed'] for g in games})
cohort_lineages=collections.Counter(g['leaderboard_team'] for g in games)
report={'n_games':len(games),'n_participant_rows':len(players),'unique_seeds':unique_seed,'module_versions':sorted({g['module_version'] for g in games}),
 'cash_reconciliation':{'total_transitions':sum(x['audit']['aligned_transitions'] for x in settles.values()),'mismatches':sum(x['audit']['cash_mismatches'] for x in settles.values()),'max_error':max(x['audit']['max_cash_error'] for x in settles.values())},
 'games_per_leaderboard_lineage':dict(cohort_lineages),'metrics':summary,
 'caveat':'Purely descriptive public replay panel; episode selection is conditional on top-ten leaderboard submissions and contains repeated agent lineages/seeds/opponent pools. Pairing removes shared game conditions only partially. No causal conclusions.'}
(R/'summary.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print('games',len(games),'players',len(players),'unique seeds',unique_seed,'mismatch',report['cash_reconciliation']['mismatches'])
for k in ['day6_cash','day6_hands','day6_crop_tiles','day12_cash','day12_hands','day20_shed_value_current_price','net_product_market','day6_11_market_net_product','day12_23_cash_delta','late_24_29_cash_delta','closing_cash']:
 print(k,summary.get(k))

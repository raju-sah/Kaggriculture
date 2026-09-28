"""Summarize paired runs and replay-grounded sales/lifecycle for this probe."""
import json, csv
from pathlib import Path
from audit_replays import settle, audit_lifecycle

HERE=Path(__file__).resolve().parent
out=[]
for opponent in ('v92','v50'):
  folder=HERE/'runs'/f'panel_vs_{opponent}'
  games=[json.loads(x) for x in (folder/'games.jsonl').read_text().splitlines()]
  byseed={}
  for r in games:byseed.setdefault(r['seed'],[]).append(r)
  for seed,rs in sorted(byseed.items()):
    r=rs[0]; path=Path(r['replay_path']); seat=r['candidate_seat']; game=json.loads(path.read_text())
    totals,mismatches=settle(game); life=audit_lifecycle(path,seat)
    obs=game['steps'][150][seat]['observation']; market=obs['market']; town=obs.get('town') or {}
    margin=r['final_coins'][seat]-r['final_coins'][1-seat]
    out.append({'opponent':opponent,'seed':seed,'candidate_seat_0_margin':round(margin),'candidate_cash':r['final_coins'][seat],
      'opponent_cash':r['final_coins'][1-seat],'result':r['candidate_result'],'milk_cash':totals[seat][('SELL','MILK')],
      'wool_cash':totals[seat][('SELL','WOOL')],'cow_spend':totals[seat][('BUY_ANIMAL','COW')],
      'sheep_spend':totals[seat][('BUY_ANIMAL','SHEEP')], 'milk_quote_d6h6':market['prices'].get('MILK'),
      'wool_quote_d6h6':market['prices'].get('WOOL'),'milk_market_inventory_d6h6':market['inventory'].get('MILK'),
      'wool_market_inventory_d6h6':market['inventory'].get('WOOL'),'shops_d6h6':';'.join(town.get('unlocked_shops',[])),
      'cow_placed':bool(life.get('place')),'cow_finally_alive':life.get('final_tile',{}).get('animal')=='COW',
      'cow_feed_days':len(set(life['feed_days'])),'cow_care_days':len(set(life['care_days'])),'cow_milk_harvest_units':sum(x['units'] for x in life['harvest']),
      'cow_milking_days':';'.join(str(x['day']) for x in life['harvest']),'cash_mismatches':sum(mismatches)})
  print(opponent,'games',len(games),'wins',sum(r['candidate_result']=='win' for r in games),'losses',sum(r['candidate_result']=='loss' for r in games),'draws',sum(r['candidate_result']=='draw' for r in games), 'mean margin',sum(r['final_coins'][r['candidate_seat']]-r['final_coins'][1-r['candidate_seat']] for r in games)/len(games))
with (HERE/'panel_metrics.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
print('wrote',HERE/'panel_metrics.csv','rows',len(out))

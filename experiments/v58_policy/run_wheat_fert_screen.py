"""Paired screen of wheat/fertilizer sell overlay against frozen expansion control."""
from __future__ import annotations
import hashlib, json, os, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from simulation.tournament import MatchSpec, Opponent, _run_worker
VARIANT=ROOT/'experiments/v58_policy/v58_expansion_wheat_fert_candidate.py'
CONTROL=ROOT/'experiments/v58_expansion/v58_expansion_candidate.py'
OPPONENTS={'v50':ROOT/'experiments/v50_agent.py','v53':ROOT/'experiments/v53_agent.py'}
SEEDS=[93700,93701,93702,93703]
OUT=ROOT/'experiments/v58_policy/wheat_fert_screen'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 os.chdir(ROOT); tasks=[]; arms={'control':CONTROL,'throughput':VARIANT};
 for arm,candidate in arms.items():
  d=OUT/arm;d.mkdir(parents=True,exist_ok=True)
  (d/'plan.json').write_text(json.dumps({'candidate':str(candidate.relative_to(ROOT)),'candidate_sha256':sha(candidate),'opponents':{k:str(v.relative_to(ROOT)) for k,v in OPPONENTS.items()},'opponent_sha256':{k:sha(v) for k,v in OPPONENTS.items()},'seeds':SEEDS,'seats':[0,1],'engine':'kaggle-environments 1.32.7'},indent=2)+'\n')
  for name,path in OPPONENTS.items():
   for seed in SEEDS:
    for seat in (0,1):
     tasks.append((arm,candidate,MatchSpec(Opponent(name,path),seed,bool(seat),0)))
 records={a:[] for a in arms}; started=time.monotonic()
 with ThreadPoolExecutor(max_workers=6) as pool:
  futures={pool.submit(_run_worker,c,s,OUT/a,240,'all' if a=='throughput' else 'none'):(a,s) for a,c,s in tasks}
  for f in as_completed(futures):
   arm,spec=futures[f];row=f.result(); coins=row.get('final_coins') or [None,None]; seat=row.get('candidate_seat',0)
   row['candidate_coin_margin']=coins[seat]-coins[1-seat] if coins[0] is not None and coins[1] is not None else None
   records[arm].append(row)
   print(f"{arm} {row.get('opponent')} seed={row.get('seed')} seat={seat} result={row.get('candidate_result')} margin={row.get('candidate_coin_margin')} elapsed={time.monotonic()-started:.0f}s",flush=True)
 for arm,rows in records.items():
  rows.sort(key=lambda x:(x['opponent'],x['seed'],x['candidate_seat']))
  d=OUT/arm;(d/'games.json').write_text(json.dumps(rows,indent=2)+'\n')
  summary={}
  for opp in OPPONENTS:
   group=[r for r in rows if r.get('opponent')==opp]
   margins=[r['candidate_coin_margin'] for r in group if r.get('candidate_coin_margin') is not None]
   summary[opp]={'wins':sum(r.get('candidate_result')=='win' for r in group),'losses':sum(r.get('candidate_result')=='loss' for r in group),'draws':sum(r.get('candidate_result')=='draw' for r in group),'errors':sum(not r.get('ok') for r in group),'mean_margin':sum(margins)/len(margins) if margins else None,'margins':margins}
  (d/'summary.json').write_text(json.dumps({'games':len(rows),'by_opponent':summary,'elapsed_seconds':round(time.monotonic()-started,1)},indent=2)+'\n')
 return 0 if all(r.get('ok') for group in records.values() for r in group) else 1
if __name__=='__main__': raise SystemExit(main())

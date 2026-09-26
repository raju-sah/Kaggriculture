"""Development screen; never use these seeds as the final holdout."""
import argparse
import concurrent.futures
import contextlib
import hashlib
import io
import json
from pathlib import Path
import time

def game(task):
    candidate, opponent, seed, seat = task
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        from kaggle_environments import make
        env=make('kaggriculture', configuration={'seed':seed,'episodeSteps':720},debug=True)
        paths=[candidate,opponent] if seat==0 else [opponent,candidate]
        env.run(paths)
    rewards=[s.reward for s in env.state]; statuses=[s.status for s in env.state]
    return dict(candidate=candidate,opponent=opponent,seed=seed,seat=seat,coins=rewards[seat],other=rewards[1-seat],statuses=statuses,
                candidate_sha256=hashlib.sha256(Path(candidate).read_bytes()).hexdigest())

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--candidates',nargs='+',required=True);p.add_argument('--opponents',nargs='+',default=['agents/v54_agent.py','experiments/v48_agent.py']);p.add_argument('--seeds',nargs='+',type=int,default=[92500,92501,92502]);p.add_argument('--output',required=True);p.add_argument('--both',action='store_true');p.add_argument('--workers',type=int,default=4);a=p.parse_args()
    tasks=[(c,o,s,t) for c in a.candidates for o in a.opponents for s in a.seeds for t in ([0,1] if a.both else [0])]
    rows=[]; start=time.time()
    with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers,max_tasks_per_child=1) as pool:
        futures=[pool.submit(game,t) for t in tasks]
        for f in concurrent.futures.as_completed(futures):
            r=f.result();rows.append(r);Path(a.output).write_text(json.dumps(rows,indent=2));print(Path(r['candidate']).stem,Path(r['opponent']).stem,r['seed'],r['seat'],r['coins'],r['other'],r['statuses'],flush=True)
    print('seconds',time.time()-start)

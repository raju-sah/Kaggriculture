"""Resumable, isolated common-opponent comparison using the existing harness."""
import hashlib
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
import time

from simulation.tournament import MatchSpec, Opponent, _game_id, _run_worker, build_summary

ROOT=Path(__file__).resolve().parents[2]
PLAN=ROOT/'experiments/v57_broad/plan.json'
OUT=ROOT/'experiments/runs/v57_broad_validation'


def validate_files(plan):
    for category,key in [('candidate','candidates'),('opponent','opponents')]:
        for name,path in plan[key].items():
            actual=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
            assert actual==plan['sha256'][f'{category}:{name}'],f'Frozen file changed: {path}'


def main():
    os.chdir(ROOT)
    plan=json.loads(PLAN.read_text());validate_files(plan)
    tasks=[]
    for seed in plan['seeds']:
        for name,path in plan['opponents'].items():
            for seat in plan['seats']:
                for version in plan['candidates']:
                    tasks.append((version,ROOT/plan['candidates'][version],
                                  MatchSpec(Opponent(name,ROOT/path),seed,bool(seat),0)))
        for seat in plan['seats']:
            tasks.append(('direct',ROOT/plan['candidates']['v57'],
                          MatchSpec(Opponent('v56',ROOT/plan['candidates']['v56']),seed,bool(seat),0)))
    assert len(tasks)==plan['total_games']
    OUT.mkdir(parents=True,exist_ok=True)
    records={key:[] for key in ['v57','v56','direct']}
    pending=[]
    for group,candidate,spec in tasks:
        directory=OUT/group;directory.mkdir(exist_ok=True)
        path=directory/'games'/f'{_game_id(spec)}.json'
        if path.exists():
            r=json.loads(path.read_text())
            if 'candidate_result' in r and 'worker_exit_code' in r:
                expected='v57' if group=='direct' else group
                assert r['agents'][r['candidate_seat']]['sha256']==plan['sha256'][f'candidate:{expected}']
                records[group].append(r)
                continue
        pending.append((group,candidate,spec,directory))
    started=time.perf_counter();initial=sum(map(len,records.values()))
    print(f'{datetime.now(UTC).isoformat()} scheduled={len(pending)} resumed={initial}',flush=True)
    with ThreadPoolExecutor(max_workers=plan['workers']) as pool:
        futures={pool.submit(_run_worker,candidate,spec,directory,plan['timeout_seconds'],plan['replay_policy']):group
                 for group,candidate,spec,directory in pending}
        for future in as_completed(futures):
            group=futures[future];record=future.result();records[group].append(record)
            count=sum(map(len,records.values()))
            if count%6==0 or not record['ok'] or count==len(tasks):
                progress={'completed':count,'total':len(tasks),'elapsed_seconds':round(time.perf_counter()-started,1),
                          'by_group':{k:len(v) for k,v in records.items()},
                          'errors':sum(not r['ok'] for values in records.values() for r in values)}
                temp=OUT/'progress.tmp';temp.write_text(json.dumps(progress,indent=2)+'\n');temp.replace(OUT/'progress.json')
                print(json.dumps(progress),flush=True)
    validate_files(plan)
    for group,values in records.items():
        values.sort(key=lambda r:(r['opponent'],r['seed'],r['candidate_seat']))
        report={'plan':plan,'group':group,'finished_at':datetime.now(UTC).isoformat(),
                'summary':build_summary(values),'games':values}
        (OUT/group/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Complete: all reports written',flush=True)
    return int(any(not r['ok'] for values in records.values() for r in values))

if __name__=='__main__':raise SystemExit(main())

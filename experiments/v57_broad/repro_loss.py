"""Reproduce the severe direct-game score deficit; diagnostic, not a new trial."""
from pathlib import Path
from simulation.tournament import MatchSpec, Opponent, _run_worker

ROOT=Path(__file__).resolve().parents[2]
record=_run_worker(ROOT/'agents/v57_agent.py',
                   MatchSpec(Opponent('v56',ROOT/'agents/v56_agent.py'),92718,True,0),
                   ROOT/'experiments/v57_broad/diagnostics/direct',240,'all')
seat=record['candidate_seat']
margin=record['final_coins'][seat]-record['final_coins'][1-seat]
print({'seed':92718,'candidate_seat':seat,'coins':record['final_coins'],'margin':margin,'statuses':record['statuses']},flush=True)
assert margin > -10000, f'Severe score regression reproduced: v57 margin {margin}'

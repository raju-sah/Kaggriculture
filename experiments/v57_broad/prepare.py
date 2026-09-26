"""Freeze the agents, seed panel, and decision criteria before evaluation."""
import hashlib
import json
from datetime import datetime, UTC
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'experiments/v57_broad'
seeds=list(range(92700,92730))
# Check seed fields, not arbitrary scores that happen to contain the same digits.
spent=set()
for path in (ROOT/'experiments/runs').rglob('report.json'):
    try:
        report=json.loads(path.read_text())
        spent.update(report.get('seeds',[]))
    except (OSError,ValueError,TypeError):
        continue
assert not spent.intersection(seeds), f'Seeds already used: {spent.intersection(seeds)}'
reference=ROOT/'experiments/kag-corpus/refagents/ledger_lena.py'
source=reference.read_text()
source+='''\n\n# Evaluation adapter: normalize shared day/hour to a step for either seat.
_ledger_original_agent = agent

def _ledger_normalized_entrypoint(obs, configuration=None):
    obs = dict(obs)
    obs["step"] = int(obs.get("day", 0))*24 + int(obs.get("hour", 0))
    return _ledger_original_agent(obs, configuration)
'''
normalized=OUT/'ledger_lena_normalized.py'
normalized.write_text(source)
candidates={'v57':'agents/v57_agent.py','v56':'agents/v56_agent.py'}
opponents={'v48':'experiments/v48_agent.py','v51':'experiments/v51_agent.py',
           'v55':'agents/v55_agent.py','ledger_lena':'experiments/v57_broad/ledger_lena_normalized.py'}
paths={**{f'candidate:{k}':v for k,v in candidates.items()},**{f'opponent:{k}':v for k,v in opponents.items()}}
plan={'created_at':datetime.now(UTC).isoformat(),'seeds':seeds,'seats':[0,1],'repeats':1,
      'candidates':candidates,'opponents':opponents,'direct_matchup':['v57','v56'],
      'common_panel_games':480,'direct_games':60,'total_games':540,
      'sha256':{k:hashlib.sha256((ROOT/v).read_bytes()).hexdigest() for k,v in paths.items()},
      'reference_original_sha256':hashlib.sha256(reference.read_bytes()).hexdigest(),
      'workers':6,'timeout_seconds':240,'replay_policy':'errors',
      'primary_metric':'Paired change in strict win rate, v57 minus v56, on the common panel.',
      'uncertainty':'95% percentile bootstrap resampling complete seed blocks (all opponents and seats), 10000 resamples, RNG 57056.',
      'submission_gate':{'zero_execution_errors':True,'minimum_win_rate_gain_pp':5,
                         'paired_seed_bootstrap_lower_bound_pp_above':0,
                         'maximum_per_opponent_win_rate_regression_pp':5},
      'rules':['No agent tuning, seed replacement, or outcome-based early stopping.',
               'Report common-panel and direct-matchup results separately.',
               'Use these games only for validation of these frozen versions.',
               'Public reference agent is a local strategy control, not a claim to reproduce a current elite submission.',
               'No Kaggle submission is authorized by this evaluation plan.']}
p=OUT/'plan.json'
assert not p.exists(), 'Refusing to replace an existing frozen plan'
p.write_text(json.dumps(plan,indent=2)+'\n')
print(json.dumps({'total_games':plan['total_games'],'seeds':[seeds[0],seeds[-1]],'hashes':plan['sha256']},indent=2))

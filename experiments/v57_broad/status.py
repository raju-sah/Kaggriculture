"""Report only complete matched seed blocks while the comparison runs."""
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'experiments/runs/v57_broad_validation'
plan=json.loads((ROOT/'experiments/v57_broad/plan.json').read_text())
records={name:[] for name in ('v57','v56','direct')}
for name in records:
    for path in (OUT/name/'games').glob('*.json'):
        try:
            game=json.loads(path.read_text())
            if 'candidate_result' in game:
                records[name].append(game)
        except (OSError,ValueError):
            pass
counts={name:Counter(game['seed'] for game in games) for name,games in records.items()}
complete=[seed for seed in plan['seeds'] if counts['v57'][seed]==8 and counts['v56'][seed]==8 and counts['direct'][seed]==2]
summary={'completed':sum(map(len,records.values())),'total':540,'complete_seed_groups':len(complete),
         'errors':sum(not game['ok'] for games in records.values() for game in games)}
for name,games in records.items():
    chosen=[game for game in games if game['seed'] in complete]
    summary[name+'_complete_seeds']=dict(Counter(game['candidate_result'] for game in chosen))
print(json.dumps(summary,indent=2))

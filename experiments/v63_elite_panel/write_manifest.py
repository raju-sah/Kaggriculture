import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
selected=json.loads(Path('/tmp/v63_selected.json').read_text())
entries=[]
for src in selected:
 p=ROOT/'replays'/f"episode-{src['id']}-replay.json"
 raw=p.read_bytes(); game=json.loads(raw)
 entries.append({
  'episode_id':int(src['id']), 'submission_id':int(src['submission_id']), 'team_id':int(src['team_id']),
  'leaderboard_team':src['team'], 'submission_public_score':float(src['score']),
  'episode_created':src['createTime'], 'episode_state':src.get('state'),
  'replay_sha256':hashlib.sha256(raw).hexdigest(), 'module_version':game.get('module_version'),
  'seed':game.get('info',{}).get('seed'), 'players':game.get('info',{}).get('TeamNames'),
  'rewards':game.get('rewards'), 'steps':len(game.get('steps',[])), 'configuration':game.get('configuration'),
  'source_command':f"kaggle competitions replay {src['id']} -p experiments/v63_elite_panel/replays -q",
 })
manifest={'selection':{'description':'50 unique, public, completed, recent games; round-robin across the current top-10 leaderboard lineages, selecting each team’s highest-scoring entry among its latest two public submissions; sampled across available episodes dated 2026-09-24 through 2026-09-26.', 'submission_ids_command':'kaggle competitions team-submissions <team_id> --format json', 'episodes_command':'kaggle competitions episodes <submission_id> --format json', 'replay_command':'kaggle competitions replay <episode_id> -p experiments/v63_elite_panel/replays -q', 'episodes':len(entries)},'source':'Official Kaggle CLI public simulation replay endpoint; no private data.', 'games':entries}
(ROOT/'episode_manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
print('wrote',len(entries))

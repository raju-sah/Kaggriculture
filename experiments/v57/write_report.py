"""Summarize the fixed holdout without suppressing losses or failed checks."""
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
folder=ROOT/'experiments/v57'
report=json.loads((ROOT/'experiments/runs/v57_holdout/report.json').read_text())
summary=report['summary'];manifest=json.loads((folder/'manifest.json').read_text());profile=json.loads((folder/'profile.json').read_text())
assert hashlib.sha256((ROOT/manifest['agent']).read_bytes()).hexdigest()==manifest['sha256']
assert summary['games']==80
for game in report['games']:
    assert game['agents'][game['candidate_seat']]['sha256']==manifest['sha256']
    assert game['seed'] in manifest['evaluation_plan']['final_holdout_seeds']
assert len({game['environment']['engine_sha256'] for game in report['games']})==1
assert all(v['games']==10 for v in summary['by_opponent'].values())
rows=[]
for name in manifest['evaluation_plan']['opponents']:
    v=summary['by_opponent'][name]
    rows.append(f"| {name} | {v['wins']} | {v['losses']} | {v['draws']} | {100*v['win_rate']:.0f}% | {v['median_coin_difference_candidate']:+,.0f} |")
dev=[]
for p in sorted(folder.glob('screen_*.json')):
    groups=defaultdict(list)
    for r in json.loads(p.read_text()):groups[Path(r['candidate']).stem].append(r['coins']-r['other'])
    for name,values in groups.items():
        dev.append(f"| {name} | {len(values)} | {sum(v>0 for v in values)} | {sum(v<0 for v in values)} | {sum(values)/len(values):+,.0f} |")
text=f'''# v57 evaluation — 2026-09-25

## Outcome

Built `agents/v57_agent.py` and the standalone `experiments/v57/v57_submission.tar.gz` package. **{summary['wins']} wins, {summary['losses']} losses, {summary['draws']} draws out of 80 holdout games ({100*summary['win_rate']:.1f}% wins).** The requested 100% win rate and top-ten leaderboard position have **not** been established. No Kaggle submission was made, and the existing `main.py` was preserved.

Latest verified live team standing: **Rajusah / rajucode #3,464 of 10,012, score 1187.7**, from the official CSV snapshot **2026-09-25 17:39:40 UTC**. Tenth place, TheEggman, has **2916.2** (gap **1728.5** points). This is the existing team's live rating, not a v57 rating. [Official leaderboard](https://www.kaggle.com/competitions/kaggriculture/leaderboard). Evidence: `experiments/v57/research/final_snapshot/`; earlier research and source corrections: [V57_RESEARCH_2026-09-25.md](V57_RESEARCH_2026-09-25.md).

## Frozen holdout

The earlier `run_all_tests.sh` used `--repeats 5` without supplying varied seeds; the archived v56 reports confirm five identical repeats per seat on seed 20260919. Its 100% result does not establish performance across varied environments.

Five previously unused seeds **92600–92604**, both seats, one game per seat and seed: **exactly ten games against each requested agent**. Repeated games on one seed were not counted as varied environments. Agent SHA-256: `{manifest['sha256']}`. The agent was frozen before any holdout outcomes, and no losing seeds were replaced.

| Opponent | Wins | Losses | Draws | Win rate | Median coin margin |
|---|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

Candidate errors: **{summary['candidate_errors']}**; opponent errors: **{summary['opponent_errors']}**; infrastructure errors: **{summary['infrastructure_errors']}**; timeouts: **{summary['timeouts']}**. Raw hashes, per-game scores, statuses, engine version, and paired-seed summary: `experiments/runs/v57_holdout/report.json` and `games/`.

These games share five initial environment seeds across the opponent panel, so they are not eighty independent environment draws. Winning against old local agents cannot establish a live top-ten rating.

## What v57 changes

- **Online price estimates:** exponentially updates observed price drift during each game and sells available non-operational surplus during declining prices or storage pressure. The estimates reset between games; this is lightweight online estimation, not a trained neural policy.
- **Demand-aware livestock:** changes later sheep purchases to cows when unlocked milk shops and observed prices favor milk and no yarn store is open. Worker pickup/placement follows the animal actually available. It preserves the pasture layout instead of switching to an incompatible farm route midgame.
- **Market order compaction:** removes empty sells and merges adjacent sales of the same product while retaining buy/sell barriers, allowing real sales to execute earlier in the simultaneous market.
- **Terminal delivery:** redirects reachable carried goods to the shed for a final same-turn drop and sale.
- Retains the public Lizs farm route, existing weed repair, seat normalization, and bundled market helpers. Source files for the new controls are readable under `experiments/v57/`; the release bundles them into one Python file.

## Validation and speed

Seven release-control checks passed (`tests/test_v57_controls.py`). The existing full test suite was also run: six pre-existing failures/errors refer to old `main.py` opener constants and behavior; see `experiments/v57/existing_tests.log`. Those tests were not rewritten to conceal failures.

The tar archive ran a complete game from an empty temporary working directory against v54 on previously used development seed 92503. Both agents finished DONE; score **{profile['rewards'][0]:,.0f}–{profile['rewards'][1]:,.0f}**. Across **{profile['calls']} calls**, median decision time was **{profile['median_ms']:.2f} ms**, p95 **{profile['p95_ms']:.2f} ms**, and maximum **{profile['max_ms']:.2f} ms**, versus the configured 1000 ms action limit. This timing sample is one complete game, not a worst-case guarantee. Evidence: `experiments/v57/profile.json`.

## Development evidence and rejected approaches

All development seeds were 92500–92508. Development screens used seat zero and were for selection, not final evidence; the final holdout uses both seats. Results below are not directly comparable where panels differ; full per-game candidate hashes and opponents are retained in each `screen_*.json`.

| Candidate | Games | Wins | Losses | Mean coin margin |
|---|---:|---:|---:|---:|
{chr(10).join(dev)}

The final cow variant beat v54 4/4 and v48 2/4 on its final development panel (6/8 overall), versus 5/8 for the broader balanced variant. Aggressive fertilizer liquidation and broad actor substitutions were rejected after regressions. Blind copying of elite replay routes also performed poorly under changed town and cash conditions. The final agent contains neither the aggressive fertilizer seller nor the broad no-op actor replacement experiment.

## Remaining limits and next research direction

v57 still uses a fixed farm route and a narrow livestock adjustment. It does not learn a general farm policy, foresee future shop draws, or adapt to arbitrary game dimensions or horizons; validation covers the standard 10×10, 720-step environment. Price trends do not fully model opponents' future supply. These constraints remain barriers to the user's broader objective.

The next substantial improvement needs a live-state farm planner that schedules feeding, care, harvesting, expansion, and crop choices against demand, followed by a larger seed-separated evaluation against public elite strategies. Another narrow patch cannot responsibly be described as guaranteeing top ten or universal wins.

## Reproduce

```sh
.venv/bin/python -m experiments.v57.build_release --herd cow
.venv/bin/python -m unittest discover -s tests -p test_v57_controls.py -v
.venv/bin/python -m experiments.v57.profile_release
.venv/bin/python -m experiments.v57.run_holdout
.venv/bin/python -m experiments.v57.write_report
```

Do not overwrite the recorded holdout with a modified candidate. Preserve the manifest and use a new output directory and fresh seeds for subsequent development.
'''
(ROOT/'docs/V57_RESULTS.md').write_text(text)
(folder/'holdout_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(text[:2300])

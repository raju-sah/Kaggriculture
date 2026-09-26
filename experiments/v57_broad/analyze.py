"""Paired, seed-block analysis of the frozen v57/v56 validation panel."""
from __future__ import annotations

import hashlib
import json
import random
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'experiments/runs/v57_broad_validation'


def percentile(values, fraction):
    values = sorted(values)
    position = fraction * (len(values) - 1)
    low = int(position)
    high = min(low + 1, len(values) - 1)
    return values[low] + (values[high] - values[low]) * (position - low)


def seed_bootstrap(values, samples=10000, seed=57056):
    rng = random.Random(seed)
    means = [statistics.fmean(rng.choices(values, k=len(values))) for _ in range(samples)]
    return [percentile(means, .025), percentile(means, .975)]


def win(record):
    return int(record['candidate_result'] == 'win')


def margin(record):
    seat = record['candidate_seat']
    return record['final_coins'][seat] - record['final_coins'][1 - seat]


def pair_index(records):
    indexed = {}
    for record in records:
        key = (record['opponent'], record['seed'], record['candidate_seat'])
        if key in indexed:
            raise ValueError(f'Duplicate paired observation: {key}')
        indexed[key] = record
    return indexed


def compare(left, right, seeds):
    a, b = pair_index(left), pair_index(right)
    if a.keys() != b.keys():
        raise ValueError('Mismatched common-opponent panel')
    rows = []
    for key in sorted(a):
        rows.append({'opponent':key[0], 'seed':key[1], 'seat':key[2],
                     'v57_result':a[key]['candidate_result'], 'v56_result':b[key]['candidate_result'],
                     'win_delta':win(a[key])-win(b[key]),
                     'margin_delta':margin(a[key])-margin(b[key]),
                     'v57_margin':margin(a[key]), 'v56_margin':margin(b[key])})
    seed_means = [statistics.fmean(r['win_delta'] for r in rows if r['seed']==seed) for seed in seeds]
    return {'games_per_version':len(rows),
            'v57_wins':sum(win(r) for r in left), 'v56_wins':sum(win(r) for r in right),
            'win_rate_gain_pp':100*statistics.fmean(r['win_delta'] for r in rows),
            'paired_seed_bootstrap_95_pp':[100*x for x in seed_bootstrap(seed_means)],
            'mean_margin_gain':statistics.fmean(r['margin_delta'] for r in rows),
            'positive_win_flips':sum(r['win_delta']>0 for r in rows),
            'negative_win_flips':sum(r['win_delta']<0 for r in rows),
            'seed_win_rate_deltas':dict(zip(seeds,seed_means)), 'paired_games':rows}


def main():
    plan=json.loads((ROOT/'experiments/v57_broad/plan.json').read_text())
    reports={name:json.loads((OUT/name/'report.json').read_text()) for name in ('v57','v56','direct')}
    expected={(opponent,seed,seat) for opponent in plan['opponents'] for seed in plan['seeds'] for seat in plan['seats']}
    for version in ('v57','v56'):
        assert pair_index(reports[version]['games']).keys()==expected
    direct_expected={('v56',seed,seat) for seed in plan['seeds'] for seat in plan['seats']}
    assert pair_index(reports['direct']['games']).keys()==direct_expected
    engine_hashes=set()
    for group,report in reports.items():
        version='v57' if group=='direct' else group
        assert hashlib.sha256((ROOT/plan['candidates'][version]).read_bytes()).hexdigest()==plan['sha256'][f'candidate:{version}']
        for game in report['games']:
            seat=game['candidate_seat']
            assert game['agents'][seat]['sha256']==plan['sha256'][f'candidate:{version}']
            opp_key='candidate:v56' if group=='direct' else f"opponent:{game['opponent']}"
            assert game['agents'][1-seat]['sha256']==plan['sha256'][opp_key]
            assert game['resolved_seed']==game['seed']
            engine_hashes.add(game['environment']['engine_sha256'])
    assert len(engine_hashes)==1
    errors=sum(not game['ok'] for report in reports.values() for game in report['games'])
    result=compare(reports['v57']['games'],reports['v56']['games'],plan['seeds'])
    result['by_opponent']={name:compare([r for r in reports['v57']['games'] if r['opponent']==name],
                                       [r for r in reports['v56']['games'] if r['opponent']==name],plan['seeds'])
                           for name in plan['opponents']}
    result['errors']=errors
    result['direct']=reports['direct']['summary']
    gate=plan['submission_gate']
    checks={'zero_errors':errors==0,
            'minimum_gain':result['win_rate_gain_pp']>=gate['minimum_win_rate_gain_pp'],
            'positive_bootstrap_lower_bound':result['paired_seed_bootstrap_95_pp'][0]>gate['paired_seed_bootstrap_lower_bound_pp_above'],
            'no_large_opponent_regression':all(r['win_rate_gain_pp']>=-gate['maximum_per_opponent_win_rate_regression_pp'] for r in result['by_opponent'].values())}
    result['gate_checks']=checks;result['submission_gate_passed']=all(checks.values())
    (OUT/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
    rows=[]
    for name,comparison in result['by_opponent'].items():
        a=reports['v57']['summary']['by_opponent'][name]
        b=reports['v56']['summary']['by_opponent'][name]
        ci=comparison['paired_seed_bootstrap_95_pp']
        rows.append(f"| {name} | {a['wins']}–{a['losses']}–{a['draws']} | {b['wins']}–{b['losses']}–{b['draws']} | {comparison['win_rate_gain_pp']:+.1f} pp | [{ci[0]:+.1f}, {ci[1]:+.1f}] pp |")
    low,high=result['paired_seed_bootstrap_95_pp'];direct=result['direct']
    recommendation=('The predeclared local gate passed. A live evaluation submission is supported, with no promise of top-ten placement.'
                    if result['submission_gate_passed'] else
                    'The predeclared local gate did not pass. Keep v57 experimental and investigate paired regressions before further tuning or submission.')
    text=f'''# v57 versus v56: broad validation

## Decision

**{recommendation}** No submission was made.

On the common panel, v57 won **{result['v57_wins']}/240** and v56 won **{result['v56_wins']}/240**. The paired strict-win-rate change is **{result['win_rate_gain_pp']:+.2f} percentage points**, with a **95% seed-block bootstrap interval [{low:+.2f}, {high:+.2f}] pp**. Mean paired change in coin margin: **{result['mean_margin_gain']:+,.1f}**.

Direct v57–v56 matches: **{direct['wins']} wins, {direct['losses']} losses, {direct['draws']} draws in 60 games**. These direct games are separate from the common-opponent comparison.

## Opponent panel

Both versions played each opponent on the same thirty previously unused seeds, 92700–92729, in both seats: 60 games per version per opponent. The common panel contains 480 games; the direct comparison adds 60, totaling **540 games**. Recorded execution errors: **{errors}**.

| Opponent | v57 W–L–D | v56 W–L–D | Paired win-rate change | 95% seed-block interval |
|---|---:|---:|---:|---:|
{chr(10).join(rows)}

The public Ledger Lena reference has a documented day/hour-to-step adapter applied identically in both panels so that seat handling does not weaken the opponent. Its strategy code is otherwise unchanged. It is a local reference agent, not the current source of an elite Kaggle entrant.

## Predeclared decision gate

The plan was written before any outcomes. A pass requires no execution errors, at least +5 percentage points overall win-rate improvement, a positive 95% seed-block lower bound, and no per-opponent win-rate decline worse than 5 percentage points.

```json
{json.dumps(checks,indent=2)}
```

The bootstrap resamples entire seed blocks, keeping both seats and all opponents together (10,000 draws, RNG seed 57056). It does not treat 480 matches as 480 independent environment draws. This interval describes the selected local panel; it cannot prove performance against the full live leaderboard. Per-opponent intervals are exploratory, without multiple-comparison correction.

Paired outcomes: **{result['positive_win_flips']} favorable flips** and **{result['negative_win_flips']} unfavorable flips** for v57. Neither agent was tuned during this validation; no seeds or losses were removed.

## Provenance and reproduction

- Frozen plan and SHA-256 hashes: `experiments/v57_broad/plan.json`.
- v57 hash: `{plan['sha256']['candidate:v57']}`.
- Per-game scores, statuses, hashes, and logs: `experiments/runs/v57_broad_validation/`.
- Machine-readable comparison: `experiments/runs/v57_broad_validation/comparison.json`.
- Run: `.venv/bin/python -m experiments.v57_broad.run` (resumes only completed matching records).
- Analyze: `.venv/bin/python -m experiments.v57_broad.analyze`.

The seeds in this report are now spent. Subsequent policy changes need a new untouched validation panel. This work evaluates submission readiness; it does not establish a v57 leaderboard score or authorize submission.
'''
    (ROOT/'docs/V57_BROAD_VALIDATION.md').write_text(text)
    print(text[:3500])

if __name__=='__main__':main()

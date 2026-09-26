# v57 versus v56: broad validation

## Decision

**The predeclared local gate did not pass. Keep v57 experimental and investigate paired regressions before further tuning or submission.** No submission was made.

On the common panel, v57 won **186/240** and v56 won **177/240**. The paired strict-win-rate change is **+3.75 percentage points**, with a **95% seed-block bootstrap interval [+0.83, +7.50] pp**. Mean paired change in coin margin: **+1,324.4**.

Direct v57–v56 matches: **45 wins, 15 losses, 0 draws in 60 games**. These direct games are separate from the common-opponent comparison.

## Opponent panel

Both versions played each opponent on the same thirty previously unused seeds, 92700–92729, in both seats: 60 games per version per opponent. The common panel contains 480 games; the direct comparison adds 60, totaling **540 games**. Recorded execution errors: **0**.

| Opponent | v57 W–L–D | v56 W–L–D | Paired win-rate change | 95% seed-block interval |
|---|---:|---:|---:|---:|
| v48 | 42–18–0 | 36–24–0 | +10.0 pp | [+0.0, +23.3] pp |
| v51 | 43–17–0 | 40–20–0 | +5.0 pp | [+0.0, +13.3] pp |
| v55 | 41–19–0 | 41–19–0 | +0.0 pp | [+0.0, +0.0] pp |
| ledger_lena | 60–0–0 | 60–0–0 | +0.0 pp | [+0.0, +0.0] pp |

The public Ledger Lena reference has a documented day/hour-to-step adapter applied identically in both panels so that seat handling does not weaken the opponent. Its strategy code is otherwise unchanged. It is a local reference agent, not the current source of an elite Kaggle entrant.

## Predeclared decision gate

The plan was written before any outcomes. A pass requires no execution errors, at least +5 percentage points overall win-rate improvement, a positive 95% seed-block lower bound, and no per-opponent win-rate decline worse than 5 percentage points.

```json
{
  "zero_errors": true,
  "minimum_gain": false,
  "positive_bootstrap_lower_bound": true,
  "no_large_opponent_regression": true
}
```

The bootstrap resamples entire seed blocks, keeping both seats and all opponents together (10,000 draws, RNG seed 57056). It does not treat 480 matches as 480 independent environment draws. This interval describes the selected local panel; it cannot prove performance against the full live leaderboard. Per-opponent intervals are exploratory, without multiple-comparison correction.

Paired outcomes: **9 favorable flips** and **0 unfavorable flips** for v57. Neither agent was tuned during this validation; no seeds or losses were removed.

## Provenance and reproduction

- Frozen plan and SHA-256 hashes: `experiments/v57_broad/plan.json`.
- v57 hash: `6b2e3ace3b9d500047e9ae8f2da4fd7729cf65f2f29b16315a2b8aa1b476ba59`.
- Per-game scores, statuses, hashes, and logs: `experiments/runs/v57_broad_validation/`.
- Machine-readable comparison: `experiments/runs/v57_broad_validation/comparison.json`.
- Run: `.venv/bin/python -m experiments.v57_broad.run` (resumes only completed matching records).
- Analyze: `.venv/bin/python -m experiments.v57_broad.analyze`.

The seeds in this report are now spent. Subsequent policy changes need a new untouched validation panel. This work evaluates submission readiness; it does not establish a v57 leaderboard score or authorize submission.

## Follow-up diagnosis

The severe direct loss at seed 92718 was traced to weed-repair state surviving the overnight actor reset. A separate corrected candidate and targeted reproduction are documented in [V57_RESET_DIAGNOSIS.md](V57_RESET_DIAGNOSIS.md). Its fresh 80-game screen finished 54–26 with zero errors; see [V57_RESET_VALIDATION.md](V57_RESET_VALIDATION.md). Those results belong to a different artifact and seed panel and do not alter this frozen report.

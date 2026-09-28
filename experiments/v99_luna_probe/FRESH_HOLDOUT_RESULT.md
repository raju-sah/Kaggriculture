# Frozen V99 Pizza gate: fresh holdout result

The precommitted gate is in [`../V99_FRESH_HOLDOUT_GATE.md`](../V99_FRESH_HOLDOUT_GATE.md).
The candidate SHA-256 remained
`7e1cede46e4d6c8ad6ae81af66cc1c49d205e7c8c1a9a9cde24f548b383a85aa`.
Exact-loader results are under `runs/fresh_holdout_137501_137524/`: 24 previously
unused seeds (137501–137524), both seats, four unchanged opponents, 192 games,
zero agent errors, infrastructure errors, or timeouts. The two seat orders have
identical margins, so the effective sample is 24 seeds per opponent.

| Opponent | W–L–D | Mean margin | Score rate | Gate result |
|---|---:|---:|---:|---|
| V92 | 4–0–44 | +$187.75 | 0.542 | **Fail:** only two distinct seeds triggered (137501, 137520); required at least five, +$800 mean, and 0.60 score rate. |
| V50 | 48–0–0 | +$915.54 | 1.000 | Pass |
| V52 | 48–0–0 | +$915.54 | 1.000 | Pass |
| V56 | 20–28–0 | +$941.29 | 0.417 | **Fail:** required score rate above 0.55. Wide variance: −$59,429 to +$41,365. |

**Decision: NO-SUBMIT.** The rule made no V92 game worse, but it rarely fired in
the fresh panel and failed the predeclared primary and V56 control criteria.
The development 8W/12D against V92 was optimistic for these new maps. Keep the
four remaining Kaggle submission slots. The result is now known data; do not
retune this candidate on seeds 137501–137524 or reuse them as a fresh holdout.

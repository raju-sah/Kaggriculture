# v59 validation protocol

## Readiness status

This protocol and runner are prepared; **no v59 games have been run and no candidate is declared ready**. The candidate hash is supplied when the runner starts, and every run is isolated beneath its SHA-256. This report concerns local game evidence only. Even a full local pass cannot establish a top-ten Kaggle rating; that needs fresh official leaderboard evidence for an explicitly authorized submission. No submission is part of this protocol.

The requested historical target remains exact: **10/10 strict wins against each of v48 and v50–v56**, shown separately by opponent and seat. The pre-final broader target is **strictly more than 95% wins** over the stronger paired panel, with zero errors, at least 90% against every opponent and in each candidate seat, and a whole-seed-block bootstrap lower 95% bound of at least 90%. These are finite sampled results, not guarantees about future play.

## Opponents and rights boundary

The eight pinned historical artifacts are v48 and v50–v56. Their relative paths and SHA-256 digests are in [`plan.json`](../experiments/v59_validation/plan.json); every phase checks the exact bytes before and after play. The reset-fixed v57 artifact is included as a local reference. Kaito v13 is eligible only as an internal local opponent under the existing source audit: keep its attribution and Apache license beside the snapshot, and do not adapt its routes, submit it, publish it, or redistribute it. Ahmed v43 is excluded because the source audit found embedded action tapes attributed to third parties, and left execution untested; permission for this internal execution is unresolved. See [V58 open-agent source audit](V58_OPEN_AGENT_SOURCES.md) and [V58 replay-rights assessment](V58_REPLAY_RIGHTS.md).

## Stage order and gates

The runner requires all prior stages to pass for the same candidate hash before it will schedule the next stage. Each stage saves an immutable manifest and per-game result rows; reruns resume only rows whose candidate, opponent, seat, seed, and engine hashes match.

1. **Smoke:** seeds 95900–95901, both seats against v56 and frozen reset (8 games). Require zero errors, timeouts, or incomplete games. This checks loading and basic execution only.
2. **Historical gate:** seeds 95902–95906, both seats against each of v48 and v50–v56 (80 games). Require zero errors and exactly 10/10 strict wins against every historical opponent. Draws are non-wins. This directly tests the requested finite sweep.
3. **Stronger development screen:** seeds 95910–95914, both seats against frozen reset and Kaito v13 (20 games). Require zero errors, at least 95% strict wins, at least 90% for each opponent and seat, and seed-block bootstrap lower 95% bound at least 90%. This gate is a screen; five seed blocks yield coarse uncertainty.
4. **Pre-final paired panel:** seeds 95800–95829, both seats against all eight historical agents, frozen reset, and Kaito v13 (600 games). Require zero errors, **strictly greater than 95%** strict wins overall, at least 90% against every opponent and in each candidate seat, and whole-seed-block bootstrap lower 95% bound at least 90%. The historical 10/10 result remains a separate gate and is not hidden by the larger aggregate.
5. **Sealed final holdout:** seeds 93000–93049 remain sealed. Do not run or inspect them for development, diagnosis, or tuning. A final run is not implemented as a normal stage in this harness. It is only appropriate after the earlier gates pass, all artifacts and the engine are frozen, and final validation is explicitly requested.

The pre-final panel reserves the Kaito executable as the one approved open local opponent. Ahmed is not included unless a future rights review establishes clear permission. If an opponent is unavailable or its pinned hash changes, the run stops; do not silently substitute an opponent.

## Seed ledger

`experiments/v59_validation/plan.json` is the shared allocation ledger. The teacher branch has already spent seeds 95500–95519. Conservatively mark 95700–95799 occupied for rule-route work. The validation gates use audited fresh seeds 95900–95914; 95800–95829 remains reserved for the paired panel, and 93000–93049 remains sealed for final validation. Check all candidate-specific and older branch records before allocating any additional dev seed. Never report reused seeds as fresh evidence.

## Reports and uncertainty

Each phase retains complete replays, exact per-game seat assignments, agent statuses and error fields, final coin margins, and the ordered shop unlock sequence with day and step. Analysis reports wins/losses/draws, errors by candidate/opponent/infrastructure/timeout, results by opponent and candidate seat, and the exploratory shop first-unlock and shop-set strata. Shop groups are post-hoc descriptions and do not prove that a shop caused the outcome.

Report two-sided 95% Clopper-Pearson intervals and a 20,000-replicate percentile bootstrap that resamples whole seed blocks. The bootstrap RNG seed is recorded. Opponent and seat splits are descriptive and published alongside the overall interval; do not replace a weak matchup with the aggregate. Zero errors of every class are required, even when the other agent fails.

## Reproduction

Run from the repository root with the exact candidate file. Do not point to `main.py`; keep the experimental candidate in its own versioned artifact.

```bash
.venv/bin/python -m experiments.v59_validation.run --candidate PATH_TO_FROZEN_CANDIDATE --phase smoke
.venv/bin/python -m experiments.v59_validation.analyze --candidate PATH_TO_FROZEN_CANDIDATE --phase smoke
```

After reviewing a passing report, request the next phase by changing `--phase` to `historical_gate`, then `stronger_dev_gate`, then `paired_pre_final`. The runner blocks later phases unless earlier `analysis.json` files pass for the exact same candidate hash. Results are stored under `experiments/v59_validation/runs/<candidate_sha256>/<phase>/`. The runner verifies Kaggle Environments 1.32.7 and refuses hash drift. The `runs/` directory holds local validation data and should remain untracked/private.

The intended candidate gate is therefore reviewable at two levels: exact 10/10 per historical artifact on the declared 10-game screen, then >95% over the larger ten-opponent paired panel with explicit uncertainty and errors. A pass is “strong local panel performance,” not proof of future wins or leaderboard placement.

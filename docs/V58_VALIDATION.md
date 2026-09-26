# v58 validation protocol

## Scope and limits

This validation is local evidence for a frozen policy. It reports two distinct targets: the user's requested **100% observed sweep** (10/10 wins against each of the eight historical agents) and a broader **95% local robustness gate** over eleven opponents. The first is an exact finite-panel acceptance target; the second estimates wider performance. Neither proves a universal 100% win rate: both sample named opponents under the pinned local engine and seed distribution. A local result cannot establish a top-ten Kaggle rating. That claim requires official leaderboard evidence for an authorized submission; live opponents and the evaluator can change.

The local comparator panel includes the eight historical versions requested in the current project record (v48, v50–v56) and three available stronger references: the Boey replay policy proxy, Ernnnn backbone, and Lizs backbone. The latter are locally reconstructed/replay-derived policies and are useful stress opponents, but they are not the current live Kaggle submissions. Public replay action streams disclose behavior for observed episodes only; they do not recover an opponent's adaptive source policy.

## Frozen baseline screen

The first screen uses the reset-fixed v57 policy as a baseline, not as a v58 release candidate. Plan: [plan.json](../experiments/v58_validation/plan.json). It uses seeds 92900–92904, both candidate seats, and all eleven opponents (110 games). This also yields exactly ten games against each requested historical agent; the 100% target is 10/10 wins for **each** of v48 and v50–v56 and is reported independently of the robustness gate. The file hashes are checked before and after play. Outcomes are reported by opponent and candidate seat; a seed is a block because both seats and opponents share the same environment seed. These seeds are spent after the screen and must not be reused for tuning claims.

Run from the repository root with:

```bash
.venv/bin/python -m experiments.v58_validation.run
.venv/bin/python -m experiments.v58_validation.analyze
```

The runner resumes only results with a matching candidate hash and saves records under `experiments/runs/v58_validation_baseline/`.

## Final candidate holdout and release gate

Seeds 93000–93049 are reserved for the final, byte-frozen candidate. Run every seed against every opponent in both seats: 50 independent seed blocks and 1,100 games. The baseline screen above does not consume these seeds. Do not tune the candidate, change opponents, or replace seeds after observing this holdout. If a code change follows a failed gate, define a new untouched range and repeat the protocol.

The final report must first state whether the requested historical sweep achieved 10/10 strict wins against every one of v48 and v50–v56. This is a separate acceptance result. The predeclared broader local readiness gate requires all of the following:

1. Zero execution errors, timeouts, or incomplete games.
2. At least 95% strict wins overall (draws count as non-wins).
3. At least 90% wins against each opponent and in each candidate seat.
4. The lower end of a 95% percentile bootstrap interval for the overall win rate, resampling whole seed blocks, is at least 90%.
5. Publish per-opponent win/loss/draw records, score margins, and uncertainty; do not hide a weak matchup in the aggregate.

Even a pass is “strong local panel performance,” not proof of 100% future wins or top-ten readiness. Report the exact binomial interval too, but treat the seed-block bootstrap as primary because games on the same seed are clustered. With 50 blocks, intervals remain relatively wide; expanding the frozen holdout is appropriate if the result is near a threshold. A strict 100% observed win rate means only that no losses occurred in this finite panel.

## Live leaderboard evidence

The latest research snapshot in [V57 live research](V57_RESEARCH_2026-09-25.md) is timestamped 2026-09-25 and places the submitted v56 at #3,464 with 1,187.7 rating, far below the snapshot's tenth-place cutoff of 2,916.2. Those standings are time-dependent and do not describe a future artifact. Before making a top-ten claim, refresh the official leaderboard and submission status after an explicitly authorized submission, then report the observed rank and rating with its timestamp. No Kaggle submission is part of this protocol.

## Artifacts and preservation

The baseline screen is isolated in `experiments/v58_validation/`; its records go in the ignored run directory. Existing `agents/main.py` is not modified. The baseline policy hash is pinned in the plan. Do not amend a completed report when later code changes; create a new plan, artifact hash, and disjoint seed allocation.

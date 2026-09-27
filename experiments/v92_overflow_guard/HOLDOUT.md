# V92 fresh sealed holdout — PASS, 24-0 replicated on 12 never-used seeds

Authoritative unbiased result for the frozen V92 candidate. **No Kaggle submission made**; root
decides on that. Candidate was not edited and not retuned; the SHA below was re-verified at run time.

## Provenance

| File | SHA-256 |
|---|---|
| `experiments/v92_overflow_guard/candidate.py` (**frozen, unedited**) | `0d5d356baa25703f1a7b753527d1b39e1c7d63478985913be5b3c2550261b806` |
| `experiments/v50_agent.py` (opponent and control, unmodified) | `e6b50128e023e3b9fafa1841e4cd520c5e581acb48e8628657585c18272eab2b` |
| `agents/v56_agent.py` (unmodified) | `d9e9670921b62afedfa8cbc7086d2a2ec19e153ee26006cef477eadd462bd19c` |

The frozen SHA in `holdout_plan.json` was compared against the on-disk file immediately before the
run and matched.

## Seeds

93000–93011, both seat orders. Verified fresh before spending: **0 prior games each** across all
`experiments/**/games.jsonl` (6,206 games, 704 distinct seeds, range 42 – 1,060,984,117). These
twelve are now consumed and must not be reused for further tuning.

## Result: 72 games, zero errors

| Run | Opponent | W-L-D | Win rate | Score rate | Median margin | Mean coins |
|---|---|---|---:|---:|---:|---:|
| Candidate | V50 | **24-0-0** | **100.0%** | 100.0% | **+598** | 90,867 |
| Candidate | V56 | 10-14-0 | 41.7% | 41.7% | −8,974 | — |
| Control (frozen V50) | V56 | 10-14-0 | 41.7% | 41.7% | −9,325 | — |

Zero candidate errors, opponent errors, infrastructure errors and timeouts across all runs.

## Predeclared gate (frozen in `holdout_plan.json` before any seed was spent)

| Criterion | Threshold | Result |
|---|---|---|
| Zero errors | all counters zero | **PASS** (0) |
| Wins vs V50 | ≥ 20 of 24 (80%) | **PASS** — 24 |
| Median margin vs V50 | strictly positive | **PASS** — +598 |
| No score-rate regression vs V56 | within 5pp of matched control | **PASS** — 41.7% vs 41.7%, **+0.0pp** |

**VERDICT: PASS, 4 of 4.**

## Replication from the spent panel

| Panel | Seeds | vs V50 | Median margin |
|---|---|---|---|
| Spent | 12 previously used | 24-0-0 | +412 |
| **Fresh sealed** | **12 never used** | **24-0-0** | **+598** |

The sweep is **stronger on fresh seeds** than on the spent panel (+598 vs +412 median), which is the
opposite of the overfitting signature. Every individual seed won, in both seat orders, with a minimum
margin of +323 (seed 93002) and a maximum of +1,263 (seed 93009). There is no seed on which the
guard fails.

## Identity: the sweep is real

Two independent checks, both run before this holdout:

- **Null:** frozen V50 against **itself** on the spent panel seeds gave **0-0-24, median margin 0**.
  Identical policies draw every game, as V82 found for V56 (7-7-58) and V89 confirmed. A 24-0 is
  therefore not a self-play artifact.
- **Firing:** the guard changed the market order on **56 of 56** reachable day-23 hour-23 states.
  It is not an inert overlay that happened to survive.

## Honest reading, and what this does not show

- **The effect is a consistency effect, not a magnitude effect.** Median margin is +598 on a game
  that ends near 90,000 coins — well under 1%. The guard wins every game, but by a thin margin that
  would be easy to erase with a different opponent or a different portfolio.
- **Against V56 the guard is exactly neutral** — 41.7% candidate vs 41.7% control, **+0.0pp**. All of
  the measured benefit is against the V50 lineage. This is consistent with the mechanism: the guard
  prevents shed overflow, and V56 is the tomato/egg portfolio that (per V88) does not overflow.
- **The projected ladder gain is therefore not established.** V56 currently sits near 1,181 while the
  top-10 cutoff is ~2,892. A +598 median against one opponent does not bridge that gap, and nothing
  here measures a leaderboard score.
- The holdout confirms the guard **beats frozen V50 reliably on unseen seeds**. It does not confirm
  the candidate would beat the elite proxies, which is the measurement that would indicate real
  top-ten readiness.

## Artifacts

- `candidate.py` (frozen), `plan.json` (spent-panel gate), `holdout_plan.json` (holdout gate),
  `verify_embedded_source.py` (packaging and loader contract)
- `runs/holdout_candidate/` — 48 games, `runs/holdout_control/` — 24 games
- Prior evidence: `runs/candidate_panel/` (48), `runs/control_panel/` (24), `runs/null_selfplay/` (24)

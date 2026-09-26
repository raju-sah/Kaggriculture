# v57 evaluation — 2026-09-25

## Outcome

Built `agents/v57_agent.py` and the standalone `experiments/v57/v57_submission.tar.gz` package. **56 wins, 24 losses, 0 draws out of 80 holdout games (70.0% wins).** The requested 100% win rate and top-ten leaderboard position have **not** been established. No Kaggle submission was made, and the existing `main.py` was preserved.

Latest verified live team standing: **Rajusah / rajucode #3,464 of 10,012, score 1187.7**, from the official CSV snapshot **2026-09-25 17:39:40 UTC**. Tenth place, TheEggman, has **2916.2** (gap **1728.5** points). This is the existing team's live rating, not a v57 rating. [Official leaderboard](https://www.kaggle.com/competitions/kaggriculture/leaderboard). Evidence: `experiments/v57/research/final_snapshot/`; earlier research and source corrections: [V57_RESEARCH_2026-09-25.md](V57_RESEARCH_2026-09-25.md).

## Frozen holdout

The earlier `run_all_tests.sh` used `--repeats 5` without supplying varied seeds; the archived v56 reports confirm five identical repeats per seat on seed 20260919. Its 100% result does not establish performance across varied environments.

Five previously unused seeds **92600–92604**, both seats, one game per seat and seed: **exactly ten games against each requested agent**. Repeated games on one seed were not counted as varied environments. Agent SHA-256: `6b2e3ace3b9d500047e9ae8f2da4fd7729cf65f2f29b16315a2b8aa1b476ba59`. The agent was frozen before any holdout outcomes, and no losing seeds were replaced.

| Opponent | Wins | Losses | Draws | Win rate | Median coin margin |
|---|---:|---:|---:|---:|---:|
| v48 | 4 | 6 | 0 | 40% | -14,806 |
| v50 | 6 | 4 | 0 | 60% | +22,202 |
| v51 | 8 | 2 | 0 | 80% | +10,607 |
| v52 | 6 | 4 | 0 | 60% | +22,202 |
| v53 | 6 | 4 | 0 | 60% | +21,008 |
| v54 | 10 | 0 | 0 | 100% | +3,199 |
| v55 | 6 | 4 | 0 | 60% | +21,008 |
| v56 | 10 | 0 | 0 | 100% | +3,199 |

Candidate errors: **0**; opponent errors: **0**; infrastructure errors: **0**; timeouts: **0**. Raw hashes, per-game scores, statuses, engine version, and paired-seed summary: `experiments/runs/v57_holdout/report.json` and `games/`.

These games share five initial environment seeds across the opponent panel, so they are not eighty independent environment draws. Winning against old local agents cannot establish a live top-ten rating.

## What v57 changes

- **Online price estimates:** exponentially updates observed price drift during each game and sells available non-operational surplus during declining prices or storage pressure. The estimates reset between games; this is lightweight online estimation, not a trained neural policy.
- **Demand-aware livestock:** changes later sheep purchases to cows when unlocked milk shops and observed prices favor milk and no yarn store is open. Worker pickup/placement follows the animal actually available. It preserves the pasture layout instead of switching to an incompatible farm route midgame.
- **Market order compaction:** removes empty sells and merges adjacent sales of the same product while retaining buy/sell barriers, allowing real sales to execute earlier in the simultaneous market.
- **Terminal delivery:** redirects reachable carried goods to the shed for a final same-turn drop and sale.
- Retains the public Lizs farm route, existing weed repair, seat normalization, and bundled market helpers. Source files for the new controls are readable under `experiments/v57/`; the release bundles them into one Python file.

## Validation and speed

Seven release-control checks passed (`tests/test_v57_controls.py`). The existing full test suite was also run: six pre-existing failures/errors refer to old `main.py` opener constants and behavior; see `experiments/v57/existing_tests.log`. Those tests were not rewritten to conceal failures.

The tar archive ran a complete game from an empty temporary working directory against v54 on previously used development seed 92503. Both agents finished DONE; score **124,005–116,233**. Across **719 calls**, median decision time was **0.80 ms**, p95 **2.40 ms**, and maximum **7.27 ms**, versus the configured 1000 ms action limit. This timing sample is one complete game, not a worst-case guarantee. Evidence: `experiments/v57/profile.json`.

## Development evidence and rejected approaches

All development seeds were 92500–92508. Development screens used seat zero and were for selection, not final evidence; the final holdout uses both seats. Results below are not directly comparable where panels differ; full per-game candidate hashes and opponents are retained in each `screen_*.json`.

| Candidate | Games | Wins | Losses | Mean coin margin |
|---|---:|---:|---:|---:|
| lizs_adaptive | 6 | 2 | 4 | +6,469 |
| lizs_herd | 6 | 4 | 2 | +10,268 |
| dsm_base | 6 | 0 | 6 | -111,961 |
| boey_base | 6 | 1 | 5 | -34,098 |
| ernnn_base | 6 | 0 | 6 | -28,861 |
| lizs_base | 6 | 1 | 3 | -3,851 |
| lizs_exact_market | 4 | 3 | 1 | +10,394 |
| lizs_compact | 4 | 4 | 0 | +10,465 |
| lizs_feedback | 6 | 2 | 4 | +3,449 |
| v48_feedback | 6 | 5 | 1 | +950 |
| final_cow | 8 | 6 | 2 | +4,510 |
| final_balanced | 8 | 5 | 3 | +5,153 |
| lizs_market | 4 | 3 | 1 | +10,348 |
| lizs_plus | 9 | 2 | 7 | +909 |
| v48_plus | 9 | 3 | 6 | -12,376 |
| lizs_safe | 4 | 2 | 2 | +10,367 |
| v48_safe | 4 | 1 | 3 | -13,990 |

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

## Subsequent validation

The frozen candidate subsequently completed a 540-game paired evaluation: see [V57_BROAD_VALIDATION.md](V57_BROAD_VALIDATION.md). A separate experimental overnight-repair fix is documented in [V57_RESET_DIAGNOSIS.md](V57_RESET_DIAGNOSIS.md); its results must not be attributed to the original artifact reported here.

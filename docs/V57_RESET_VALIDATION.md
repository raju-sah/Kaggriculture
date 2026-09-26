# Overnight-repair candidate: fresh screening results

The separate candidate won **54/80 (67.5%)**, with **26 losses**, **0 draws**, and **0 execution errors**. All eight requested opponents received ten games: five fresh seeds, 92800–92804, in both seats.

| Opponent | Wins | Losses | Draws |
|---|---:|---:|---:|
| v48 | 8 | 2 | 0 |
| v50 | 6 | 4 | 0 |
| v51 | 6 | 4 | 0 |
| v52 | 6 | 4 | 0 |
| v53 | 6 | 4 | 0 |
| v54 | 8 | 2 | 0 |
| v55 | 6 | 4 | 0 |
| v56 | 8 | 2 | 0 |

## Interpretation

The overnight state fix is supported by a captured-observation regression and a full-game reproduction that flips the severe seed-92718 loss into a win. This new panel screens the corrected candidate; it does **not** measure its gain over original v57, because original v57 was not rerun on these five seeds. Do not compare this percentage directly with percentages on the earlier panels.

The requested 100% win rate was not achieved. Five initial seeds are too few to establish broad robustness or top-ten readiness. The corrected artifact is suitable for further experiments, but this evidence does not support a top-ten submission claim. A new paired, broader comparison and stronger external opponents remain appropriate before promotion.

## Artifacts

- Candidate: `experiments/v57_broad/v57_reset_candidate.py`.
- Standalone archive: `experiments/v57_broad/v57_reset_submission.tar.gz` (contains only `main.py`). Extracted archive passed the captured-observation regression from an empty working directory.
- Manifest: `experiments/v57_broad/reset_manifest.json`.
- Frozen plan, game outcomes, hashes, logs and summary: `experiments/runs/v57_reset_validation/`.
- Runner: `.venv/bin/python -m experiments.v57_broad.validate_reset` (reruns the screen; not a resume command).
- Report: `.venv/bin/python -m experiments.v57_broad.report_reset` (requires all 80 unique results and verifies hashes).
- Diagnosis: [V57_RESET_DIAGNOSIS.md](V57_RESET_DIAGNOSIS.md).
- Original frozen 540-game comparison: [V57_BROAD_VALIDATION.md](V57_BROAD_VALIDATION.md).

No Kaggle submission was made. Original `agents/v57_agent.py`, its archive, and existing `main.py` were preserved. These screening seeds are now spent.

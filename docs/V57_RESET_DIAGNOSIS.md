# v57 overnight weed-repair diagnosis

The frozen 540-game validation exposed a severe direct loss on seed 92718, candidate seat 1. Original v57 lost 72,734–131,880. This exact outcome reproduced in a separate diagnostic run; it is not an additional independent validation trial.

## Cause and controlled evidence

At day 7, hour 22 (step 190), the farmer encounters a weed at (0,1). The inherited weed-repair wrapper digs and retries planting on the following turn. At day 8, hour 0, the environment resets the farmer to the shed and dismisses hired hands. The wrapper nevertheless replays the previous day's WATER action instead of the new day's WEST movement. Its bounded replay then expires before the displaced route catches up: at step 201 the farmer feeds at (4,3) instead of (4,2). Subsequent livestock and crop production deteriorate.

A three-observation captured fixture reproduces the misplaced action through the standalone agent. Explicitly normalizing day/hour to step leaves the defect intact. Calling the base agent without v57's newer control layers also leaves it intact. This is an inherited repair-state lifetime defect, not evidence that market or herd feedback caused the initial divergence.

The experimental fix clears active weed transactions when the observed day changes. This applies to the standard 24-hour configuration, matching the existing route and agent timing assumptions. It leaves same-day transactions unchanged and prevents stale hand-index transactions from carrying into a new hiring cycle.

The frozen `agents/v57_agent.py` and original submission archive remain untouched. The separate candidate is `experiments/v57_broad/v57_reset_candidate.py`, SHA-256 `4173479fe1f80d031d570d1ea23b694dfe86e1d162317a4c9c7df0058a40208e`.

## Reproduction and regression

- Original full failure: `.venv/bin/python -m experiments.v57_broad.repro_loss` (intentional assertion failure).
- Minimal original failure: `.venv/bin/python -m experiments.v57_broad.diagnostics.check_day_reset` produces DIG, PLANT WHEAT, WATER; assertion requires the scheduled WEST after reset.
- Build separate variant: `.venv/bin/python -m experiments.v57_broad.diagnostics.build_reset_variant`.
- Minimal fixed replay: `.venv/bin/python -m experiments.v57_broad.diagnostics.check_day_reset experiments/v57_broad/v57_reset_candidate.py` produces DIG, PLANT WHEAT, WEST and passes.
- Regression: `.venv/bin/python -m unittest tests.test_v57_day_reset tests.test_v57_controls tests.test_v57_broad_analysis` — 11 checks pass.
- Full fixed replay of seed 92718, seat 1: **139,369–135,077**, a **4,292-coin win**; both agents DONE. Opponent coins also change because the market is shared. This confirms the fix affects the actual game, but one targeted replay does not establish general strength.

Raw original and fixed replays are under `experiments/v57_broad/diagnostics/{direct,reset}/`. The compact fixture and diagnostic scripts are intentionally retained there for reproduction. No temporary runtime logging was added to either agent.

## Prevention

Persistent action-repair state must respect environment lifecycle boundaries. Treat overnight actor reset and hand dismissal as invalidating old route transactions. The captured-observation regression exercises that boundary through the real bundled submission entrypoint.

## Fresh validation

The candidate was frozen before testing on seeds 92800–92804, both seats against v48, v50, v51, v52, v53, v54, v55, and v56: 80 games. The pre-run plan, hashes, raw results, and logs are in `experiments/runs/v57_reset_validation/`. This is a new five-seed screening panel, not a replacement for the original 30-seed paired comparison and not a leaderboard estimate. Completed: **54 wins, 26 losses, zero draws/errors (67.5%)**. Against v56: **8–2**. Full opponent table and limitations: [V57_RESET_VALIDATION.md](V57_RESET_VALIDATION.md). The requested perfect record was not achieved; continue development before promotion.

# V59 original route rules study

## Decision

**No-go; no fresh seed expansion.** The original observation-driven crop route generated positive harvest activity and finished above its initial cash, but it did not reach the required throughput or economics on the spent seed-95100 diagnostic. The frozen-reset reference is performance context only. No frozen-reset policy or action tape was used in this candidate, and no final holdout seed or submission was touched.

## Design

`experiments/v59_route_rules/candidate.py` is a standalone hierarchy. It derives funded sowing tokens from current seed inventory, caps simultaneous requests by aggregate crop seed balance, reconstructs crop service tasks from the live board, and assigns each task once to a nearest worker with a deterministic local station tie-break. A small hour-zero manager replenishes seeds only when cash allows and adds workers when observed crop service demand can support them. Market orders sell shed output. It has no episode-specific route or indexed action tape.

The local station rule spreads workers around shed-adjacent positions, then favors tasks near each worker's station. This was meant to reduce cross-field travel while retaining a state-derived plan. Seed purchases occur after the current unit actions, so only seeds visible in the observation fund current sowing.

## Verification and spent diagnostic

The candidate passed four checks in `experiments/v59_route_rules/test_candidate.py`, including a call through Kaggle's `get_last_callable`, output shape validation, funded aggregate planting, boundary movement masking, and deterministic station mapping. The tournament used the repository tournament worker and Kaggle's normal agent-loading path.

One paired two-seat screen against v50 used only spent diagnostic seed `95100`: **0–2**, no errors or timeouts, mean candidate final cash **$5,217**, and median candidate-minus-v50 margin **−$167,087**. Candidate source SHA-256: `a37a3b0338ad6c6953cd69b9a306c2f2a30d5a01fb1484edcc5e95434e2c7f45`; v50 reference SHA-256: `e6b50128e023e3b9fafa1841e4cd520c5e581acb48e8628657585c18272eab2b`.

A replay audit of either seat recorded 1,179 actor slots, 905 effectful actions (**76.8%**), 266 PASS slots, and 8 attempted no-ops. It observed 40 plants, 201 watering effects, and 19 harvests. This is positive crop production and the final balance exceeds the initial $3,000, but the route is far below the requested ~90% worker-effect target and the $70,000 gate. Seed `95700+` screens against v50/v53/v54 were therefore not run. Seeds `93000–93049` remain sealed.

## Structural finding

Task coverage is not sufficient by itself: this plan can keep producing legal water and planting work while the small portfolio yields too little saleable output. The day-level manager needs to estimate expected harvest value and worker-turn costs before hiring/reinvesting. Station affinity did not solve the dominant cash gap, so more routing tuning or broad seed allocation is not justified without a materially better production portfolio and sale pipeline.

Files and reproduction: candidate and tests in `experiments/v59_route_rules/`; exact tournament report and replay in `experiments/v59_route_rules/spent95100/`. Run the local checks with `.venv/bin/python experiments/v59_route_rules/test_candidate.py`.

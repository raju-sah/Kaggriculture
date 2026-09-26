# V59 state-conditioned teacher-query experiment

**Decision: no-go as a new policy.** A clock-free learned worker controller reproduced the reset-v57 worker policy with high held-out action accuracy, but it showed no paired score gain over reset-v57 on the one fresh confirmation seed. No Kaggle submission was made. The final 93000–93049 holdout remains sealed.

## What was tested

The data-generation candidate is `experiments/v59_state_teacher/student.py`. It is a self-contained copy of frozen `experiments/v57_broad/v57_reset_candidate.py` with an intended coordinate-conditioned hand dropout. The guard checks `isinstance(pos, dict)`, but Kaggriculture observations represent hand positions as `[x, y]` lists. The guard therefore never fires. Replay inspection confirmed that its farmer and hand actions match reset-v57 on all 720 turns in sampled games; only market lists differed. The candidate was effectively frozen reset-v57, and did **not** create student-visited off-policy states. The builder re-queried reset-v57 on its on-policy states. This experiment therefore did not achieve its DAgger objective.

The first development seed, 95500, produced 6/6 wins with no agent errors across both seats against v50, v53, and v54. The remaining development seeds 95501–95519 completed 114 seat-swapped games: 79 wins, 35 losses, zero draws, and zero candidate/opponent/infrastructure errors. Combined, these runs produced 85–35 across 120 games. These are frozen reset-v57 collection results, not perturbed-student or learned-policy performance.

The modeling corpus uses existing candidate-seat replays from v50 matches across seeds 95500–95519, both seats. It samples every fourth replay frame, then queries reset-v57 for the farmer and hand decisions. Because the dropout was inactive, these are on-policy reset-v57 states, not off-policy student states. The corpus contains 65,000 action rows; the worker model drops farmer rows, leaving 57,800 rows. Seeds 95500–95518 (54,910 worker rows) train the model, and seed 95519 (2,890 worker rows) is a disjoint development-seed behavior check. The model features use actor identity, coordinates, local tile/crop/animal state, carried inventory, current cash/shop state, and distances to visible crop, yield, animal, unfed-animal, and fertilizer work. Seed, replay name, and future observations are provenance only and never model features.

The full-feature model reached 100% on seed 95519, but a clock ablation revealed schedule leakage: `(day, hour, actor)` alone forms 1,625 keys across the 65,000 rows, and 1,624 keys map to a single action label. The final model therefore removes day and hour. Its held-out action accuracy is still 99.52%, but this is same-policy, on-policy action reconstruction. Spatial/task features may encode the scripted route; the metric does not demonstrate generalization to states visited by a different student or prove strategic learning.

## Learned full-game check

`experiments/v59_state_teacher/student_model_noclock.py` embeds the fitted clock-free LightGBM model and uses it to replace only the hand commands from reset-v57. The farmer and market remain reset-v57 scaffolding. If the classifier predicts an action label, the runtime reuses a matching command template from the current teacher action; if none exists, it falls back to that worker's teacher command. Therefore this is a learned worker-controller probe, not a standalone policy.

The exact Kaggle loader completed both seat-swapped games against frozen reset-v57 on fresh seed 95600, with zero reported agent errors. The learned candidate scored 95,489 to 91,304 in seat 0, and 91,304 to 95,489 in seat 1. The paired coin differences are +4,185 and −4,185, for a net paired difference of zero. Both games have the same normalized replay hash (`4e10c9e25ecfc0e280b79796c6e381ee4d8ff6f194c4fa0baa8794bb5ec2a77f`), confirming identical match outcomes across seat swaps. This is one-seed evidence and does not establish a score distribution. Since the collector never perturbed workers, the model was trained on reference-policy trajectories; this comparison does not test whether it can track a separately evolving student's state distribution.

Full-game runtimes were 40.78s and 32.76s. The local loader had LightGBM and pandas available; the embedded policy source is 2,514,347 bytes and embeds a compressed 5,438,917-byte model. The exact-loader check establishes that this environment can run the artifact. It does not establish portability to a competition runtime without those libraries, nor does match completion prove that the engine accepted every semantically possible command (the engine can ignore invalid actions).

The command resolver only emits a teacher-produced command template or retains the worker's teacher command, so its operation/argument shape comes from the reference output. No separate action-effect audit or cash/feed/seed invariant audit was completed. We therefore make no claim that those invariants have been proved by this experiment. The paired no-gain result is sufficient to stop this line before a broader tournament.

## Artifacts and provenance

- Builder and query logic: `experiments/v59_state_teacher/build_dataset.py`.
- Sampled state/action corpus and source hashes: `experiments/v59_state_teacher/dev_teacher_rows.jsonl` and `.meta.json`.
- Training code: `experiments/v59_state_teacher/train_model.py`.
- Clock-free model and held-out metrics: `worker_model_noclock.txt` and `worker_model_noclock.metrics.json`.
- Embedded exact-loader probe builder: `experiments/v59_state_teacher/make_agent.py`.
- Collector tournaments: `experiments/v59_state_teacher/smoke95500b/` and `dev95501_95519/`.
- Fresh paired teacher comparison: `experiments/v59_state_teacher/headtohead95600/`.

SHA-256: data corpus `3d7180cc25c3c40784f16ede1b4e74a5ecfce0e7df9b1ee121ccd06992af8dfe`; clock-free model `a3fac87c624c121891e9551972b308b34cc12f0528a937f796911bdfa7105ed3`; exact-loader candidate `e789afe1b281096ffa539d2fb9bd42dfddef1cca6f5f4d2fca3adcff653e93c1`. The embedded teacher implementation matches reset-v57 SHA-256 `4173479fe1f80d031d570d1ea23b694dfe86e1d162317a4c9c7df0058a40208e`.

## Seed ledger and rights

- Development collection: 95500–95519, spent.
- Paired learned-controller check: 95600, spent.
- No other 95600+ confirmation seeds were used. A wider confirmation screen was stopped after the learned policy tied the teacher exactly in paired coins.
- Final holdout seeds 93000–93049 remain sealed.

This route derives from public replay actions. Public replay analysis may inform general research, but whether a replay-derived route may be embedded in a competition submission remains unresolved. This experiment is research-only pending rights clarification; see [V58 replay rights](V58_REPLAY_RIGHTS.md). Raw generated match replays remain under the local experiment output and are not copied into the submission.

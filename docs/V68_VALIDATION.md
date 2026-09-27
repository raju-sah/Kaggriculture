# V68 candidate validation protocol

This is a prepared protocol, not a claim that a V68 candidate passed. No V68 validation games have been run by this protocol. The current V68 routing variant is ineligible: it went 0/2 against V67 on spent seed 94700, with mean margin −$18,233, and the milder routing ablation also lost both seats to V56. A future candidate must first win both seats against both V67 and V56 on that already-spent seed. That screen is a cheap eligibility filter, never fresh evidence. Until a candidate clears it, do not start smoke, historical, or panel phases.

## Frozen phases

`experiments/v68_validation/plan.json` is the seed and source ledger. `experiments/v68_validation/run.py` runs only the explicitly named phase, verifies pinned opponent source hashes and `kaggle-environments==1.32.7`, snapshots the candidate by SHA-256, retains each replay, writes a manifest and game records incrementally, and resumes only matching seed/seat/source records. Later phases require every earlier phase's passing `analysis.json` for the same candidate hash. There is no command for the final holdout.

| Phase | Seeds | Opponents | Games | Pass condition |
|---|---:|---|---:|---|
| Spent eligibility | 94700 (already spent) | V67 original, V56 | 4 | Strict 2/2 wins against each, no error, timeout, or incomplete game. Diagnostic only. |
| Smoke | 96200–96201 | V67, V56 | 8 | All games complete without errors/timeouts; both seats against both opponents. |
| Historical gate | 96202–96206 | v48, v50–v56 | 80 | Exactly 10/10 strict wins against each of the eight historical agents, zero errors. Draws are non-wins. |
| Stronger panel | 96210–96219 | V67, Kaito v13 local opponent, Boey/Ernnnn/Lizs local proxies | 100 | At least 95% strict wins overall, at least 90% against each opponent and in each opponent-seat cell, seed-block bootstrap lower 95% bound at least 90%, zero errors. |
| Broader paired panel | 96300–96329 | All eight historical opponents, V67, Kaito, and three local proxies | 780 | Strictly above 95% overall, at least 90% against each opponent and in each opponent-seat cell, seed-block bootstrap lower 95% bound at least 90%, zero errors. |

The historical target is intentionally a separate, exact 10/10-per-agent gate; the larger panels cannot wash out a historical loss. Results include every game, seat, final score/margin, engine and source hashes, runtime, status/error fields, replay hash, and per-seat shop-unlock schedule. The reports include two-sided 95% Clopper–Pearson intervals and a 20,000-replicate percentile bootstrap that resamples complete seed blocks with RNG seed 68001. The bootstrap is descriptive at the ten-seed stronger panel; its lower bound is still a declared gate.

## Seed ledger and source pins

The new development allocations 96200–96206, 96210–96219, and 96300–96329 were not found in existing plan/ledger documents during the audit. The runner is deliberately gated because those ranges become spent if invoked. Prior spent controls include 92802, 92804, and 94700. Preserve the V59 95800–95829 paired-panel reservation and 95900–95914 allocations. Keep the official final holdout 93000–93049 sealed and uninspected. Do not substitute seeds after seeing outcomes. Re-audit all candidate-specific ledgers immediately before a future run.

All eight historical agents and the local challengers have pinned file hashes in `plan.json`; the runner rejects a mismatch. Kaito v13 is only an internal benchmark. Attribute it in any internal report and do not adapt, submit, publish, or redistribute it. The other named elite agents are reconstructed local proxies, so clearing these panels is not evidence of beating live competition opponents.

The latest official leaderboard snapshot supplied on 2026-09-26 reports the team at rank 3448/10049 with score 1189.7; tenth place was 2880.3. The V66 submission scored 442.2 in the same snapshot, while v56 remains the best recorded submission at 1189.7. Refresh official results before making any readiness claim. Local win rates cannot establish top-ten readiness by themselves.

## Original learned-policy path to investigate

The gap is structural: V67 averaged about $40k against V56's $136k on spent seed 94700, with substantially fewer productive actions, hires, crop sales, and livestock. Copying elite actions is not enough to teach the missing investment and cashflow decisions. A bounded next research path is an **offline behavior-cloned macro-action proposal policy with a hand-written safety/economy shield**, trained only from public replay observations and actions, then tested against the deterministic in-house agent in the pinned simulator. Keep it as an experimental V68 candidate; do not treat replay score as a reward label or put a replay script into the deployed agent.

The existing public corpus is small: the V58 audit found 30 downloaded public games (38 episode groups when local traces are included). Frames are highly correlated and behavior-policy biased; even thousands of turn rows amount to only tens of independent seasons. Train/test splits must hold out entire episodes and ideally opponent/seat groups. A small model can learn legal local task preferences, but this corpus is not sufficient to learn reliable season-level expansion, feed economics, or opponent response. Generate additional on-policy rollouts from the in-house simulator for those decisions, using terminal cash and candidate-vs-control margin as the objective; do not label every observed action with its episode's final score.

Use a compact two-timescale architecture. At day boundaries, an interpretable manager sets crop/species/staffing targets from the current public and private observation. A small classifier (for example, a categorical LightGBM policy over explicitly enumerated legal task intents) ranks local intents for the current worker. A deterministic shield checks affordability, seed availability, feed coverage, engine preconditions, season/day horizon, and action legality, and falls back to V67's safe action when confidence is low. Derive all features from current observations; do not use episode IDs, replay-specific coordinates, stored action sequences, or lookup tables keyed to observed games. This keeps behavior responsive to randomized worlds and gives an auditable standalone source.

Before training, verify the permitted use and redistribution terms for each replay source, retain source/episode attribution in an internal manifest, and keep the raw replay cache private. Public availability is not itself a rights grant. Use replay data for internal policy research only until the source-specific rights audit approves any broader use. The original learned artifact should contain weights and feature code only, without replay rows, action arrays, or source code copied from opponents. If that boundary cannot be established for a source, exclude it.

Profile against the actual Kaggle agent protocol before scaling up: the model must load locally from the standalone bundle, stay within per-action runtime/memory limits, avoid heavy training-library imports at inference, and produce valid JSON for all 720 steps. Train locally on CPU first; Kaggle GPU quota does not speed up the Python environment simulations. Only after a candidate beats V67 and V56 on the spent gate, clears the smoke, and exceeds V67/V56 on the specified spent opponent panel should its frozen hash consume fresh seeds. No training or matches are authorized by this preparation document.

## Running a future authorized phase

From the repository root, after the candidate clears the spent screen and is frozen:

```bash
python3 experiments/v68_validation/run.py --candidate path/to/frozen_candidate.py --phase spent_gate
```

Use the same source path and hash for subsequent phases, advancing only when the prior `analysis.json` records a pass. The current failed routing artifact does not pass this first condition. Do not run the command for it, do not submit an artifact under this protocol, and do not unlock the sealed final range from local results.

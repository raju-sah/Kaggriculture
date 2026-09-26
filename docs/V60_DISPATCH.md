# V60 worker-dispatch audit

## Decision

No dispatch candidate was justified by the saved-replay audit, so this branch makes no policy change and runs no new games. The frozen v57 worker schedule did not show a recurring loss-specific slot or cash-waste signature. The clearest control is seed 92902: the candidate seat's farmer/hand action stream is byte-for-byte equivalent after canonical serialization against v52, v53, and v54, despite losses to v52/v53 and a win against v54. The likely difference lies outside worker dispatch.

## Evidence

`experiments/v60_dispatch/audit_worker_slots.py` reads seven saved v57 replays and writes the detailed results to `experiments/v60_dispatch/saved_replay_audit.json`. It inspects 719 transitions per replay and calculates an action-stream SHA-256 for the candidate seat, action counts, no-observed-effect counts, and a simple feed-success proxy.

| Replay | Outcome for candidate | Candidate reward | Action-stream SHA-256 prefix | PASS slots | FEED |
|---|---:|---:|---|---:|---:|
| 92802 vs v48 | loss | 70,037 | `b3246b9d…` | 453 | 332/333 |
| 92804 vs v51 | loss | 114,967 | `9777a569…` | 453 | 332/333 |
| 92900 vs v48 | win | 88,019 | `9777a569…` | 453 | 332/333 |
| 92901 vs v48 | win | 139,199 | `9777a569…` | 453 | 332/333 |
| 92902 vs v52 | loss | 105,947 | `9777a569…` | 453 | 332/333 |
| 92902 vs v53 | loss | 105,451 | `9777a569…` | 453 | 332/333 |
| 92902 vs v54 | win | 98,600 | `9777a569…` | 453 | 332/333 |

The 453 PASSes are farm-wide padded worker slots in the 719-frame action stream, not 453 opportunities for one worker that could simply be reassigned. The repeated stream also contains 1,184 WATER, 546 HARVEST, 399 CARE, and 383 COLLECT_FERTILIZER commands. On the common stream, state-change proxies flag 12 WATER, 15 HARVEST, 6 CARE, and 26 COLLECT_FERTILIZER attempts without a visible state change; these counts are identical on the seed-92902 loss and win replays. The separate 92802 stream has fewer visible no-effect attempts in some commands and is not evidence of a broad dispatch defect.

The same-seed comparison is especially useful because seed 92902 has identical candidate-side dispatch across three opponents while the result flips. Other saved wins and losses also share that action fingerprint. This rules against a dispatch overlay based on the replay-visible worker schedule alone; it does not prove every action is economically optimal.

## Limits

This was a read-only offline audit. It ran no new seeds and created no candidate. A visible state delta is only a proxy for action acceptance and value: it cannot establish whether a no-delta action was rejected, redundant, or strategically useful. Opponent actions and market outcomes can change reward while candidate dispatch remains identical. No full causal value model for worker actions was built.

Given those limits and the lack of a loss-specific signal, a state-conditioned replacement would be speculative. Reopen dispatch only with a concrete engine-derived opportunity (for example, a worker-action acceptance reason tied to a recurring losing state) and a paired replay intervention that changes the action in that loss state while preserving the corresponding win behavior.

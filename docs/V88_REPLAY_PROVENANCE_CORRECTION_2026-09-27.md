# V88 replay-provenance correction — 2026-09-27

**Correction:** V88's replay-derived direct-match and phase conclusions are not supported by the artifacts. The agent hashes identify direct V50–V56 game records, but the replay join then uses only `game_id`; replay filenames are opponent-based and the ID does not identify the candidate. The first matching replay can therefore be a different candidate playing one of those agents.

## Concrete mismatch

For `v50-seed-92802-ab-repeat-0`, the direct record in [`v56_panel_large/games.jsonl`](../experiments/v82_baseline/runs/v56_panel_large/games.jsonl) identifies V56 (frozen SHA `d9e96709…`) in seat 0 and V50 (frozen SHA `e6b50128…`) in seat 1. It records final coins `[78631, 112153]`: V56 loses by 33,522.

[`actor_level_diff.json`](../experiments/v88_terminal_phase/actor_level_diff.json) attributes to that same ID the replay [`v81_expert_switch/.../v50-seed-92802-ab-repeat-0.json`](../experiments/v81_expert_switch/runs/screen_92802/replays/v50-seed-92802-ab-repeat-0.json). That replay is the V81 hybrid against V50, with final cash `[65182, 88632]`. V88 treated the hybrid's seat as V56 and reported a −23,450 V56–V50 delta. Six replay files with this ID exist, from unrelated candidate-versus-V50 games.

The corrected [`provenance_audit.json`](../experiments/v88_terminal_phase/provenance_audit.json) reports zero direct V50–V56 games with a retained replay. The direct game records themselves have `replay_retained: false` and `replay_path: null`. Consequently, V88's reported 32/56 direct wins cannot be paired with its −$19,919 mean “direct” cash delta: the former comes from direct game records, while the latter and the phase measurements come from incorrectly joined replays.

## Claims to discard and provisional direct count

Discard V88's replay-derived win/margin pairing, phase sales deltas, product-composition attribution, and action-level explanation as direct V50–V56 evidence. The replay files do contain observations, but they are not the labeled direct games. They cannot establish a selector feature/outcome dataset. In particular, the README's 56 games/28 seeds with 56 saved direct replays is contradicted by the provenance audit; its listed seed range itself names 29 seeds.

As a limited cross-check, I scanned `experiments/**/games.jsonl` for records carrying the exact frozen V50 and V56 hashes, restricted to the seeds listed in the V88 README, and grouped by `(seed, V56 seat)`. This finds **29 seeds / 58 seed-seat cells**. Selecting the first matching record per cell gives V56 38 positive final-cash margins and 20 negative, mean margin **−$1,905**, median **+$8,381**; duplicate records for a cell agreed on margin in this scan. This is provisional only: the README's stated 28-seed panel and seed list disagree, and the scan's cell-level deduplication is not a predeclared sampling rule. Do not treat these figures as a validated performance estimate or compare them directly with V88's 56-game claims.

## Decision

**No-go for an early contextual selector using current V88 artifacts.** There is no verified direct-game observation stream, and the replay-derived phase signals are misattributed. First build and freeze a seed-blocked direct outcome table with explicit provenance and a consistent deduplication rule; verify any same-seed opening observations against one another before using them as features. Only then is a small grouped cross-validation feasibility check justified. No selector gain is established here.

# v58 public replay imitation study

## Decision

**No-go as a candidate strategy.** The observation-conditioned prototype is callable through the Kaggle file loader and completes a game, but its economic policy collapsed. On seed 94700 against v50, with the candidate in both seats, it scored $1,644 average against $149,978 for v50 before the sowing correction (0/2 wins, no runtime errors). After correcting the missing `PLANT` action when a worker stood on an empty tile with wheat seed in stock, the same paired seed scored $3,632 against $149,410 (0/2). I stopped there instead of running the requested broader v53/v54 panel: the one-seed result was decisive evidence that this task allocator is not worth a broad screen.

The replay explains the collapse. Workers repeatedly chose the same nearest empty or urgent tile, collided, and moved back and forth around the shed. The initial version never planted at the occupied worker position; after that was fixed, the workers still lacked distinct target allocation. It bought seed and hired workers but did not turn them into a farm economy. This is a useful failure record, not a competitive agent.

## Replay-derived model

The preliminary extraction run used four publicly downloadable episodes already present in the team-local research cache. After that initial held-out result, the official Kaggle CLI episode API yielded a broader set of 30 distinct public completed episodes from elite submission episode lists. Each downloaded replay was checked for at least one top-ten participant, and the manifest records the observed players, replay hashes, API listing source, and elite seat(s). It treats market actions as intent labels and actor commands as coarse operation labels. It drops quantities, action ordering, and absolute turn IDs. Feature bins come only from the acting elite player’s current observation: day and hour buckets, cash, hands, unlocked land, planted area, animal structures and counts, seed/shed wheat, current shop count, and observed prices. Neither seed nor future observations are features.

The split is by episode: train on Boey episode 113508987, DSM episode 113508988, and DECEM episode 113508989; hold out M & M & P & Q episode 113507961. The trainer outputs aggregate categorical counts per intent and feature value, not any episode-indexed action table. On the 720 held-out observations, the simple smoothed Bernoulli model reached 0.438 micro F1 overall, 0.528 actor-intent F1, and 0.193 market-intent F1. Exact per-turn intent-set accuracy was 0%. Market precision was only 0.115 at 0.599 recall. This does not support deploying the learned market decisions; the four matches also represent a small, heterogeneous sample rather than a representative elite policy population.

The preliminary four-episode model provenance and raw replay hashes are recorded in `experiments/v58_imitation/market_model.metrics.json`. The broader 30-episode acquisition manifest is `experiments/v58_imitation/public_episode_manifest.json`, with the CLI episode-list metadata in `experiments/v58_imitation/episode_lists/` and ignored local raw replays in `experiments/v58_imitation/replays/`. The broader set is being prepared for a separate unit-level, episode-held-out extraction; the preliminary metrics below are not from those 30 episodes. Episode IDs and elite seats: 113508987 / Boey / seat 0; 113508988 / DSM / seat 0; 113508989 / DECEM / seat 1; 113507961 / M & M & P & Q / seat 0. Source profiles and public replay availability are documented in [V58 elite research](V58_ELITE_RESEARCH.md). No raw replay is copied into this branch. The use follows the boundary in [replay rights](V58_REPLAY_RIGHTS.md): use traces for general analysis, do not embed or redistribute a literal action tape.

## Artifacts and reproducibility

- `experiments/v58_imitation/policy.py` is the standalone observation-conditioned but failed actor/market heuristic. It reads only the supplied observation and does not use a seed, episode ID, remembered route, or future observation.
- `experiments/v58_imitation/behavior_extract.py` extracts binned features and coarse intent labels from local replay paths and trains the aggregate intent model. Example invocation and exact split:

  ```sh
  .venv/bin/python experiments/v58_imitation/behavior_extract.py \
    experiments/v58_elite/replays/episode-113508987-replay.json \
    experiments/v58_elite/replays/episode-113508988-replay.json \
    experiments/v58_elite/replays/episode-113508989-replay.json \
    experiments/v58_elite/replays/episode-113507961-replay.json \
    --holdout 113507961 --out experiments/v58_imitation/market_model.json
  ```

- `market_model.json` contains only aggregated feature-category class counts; `market_model.metrics.json` contains episode IDs, source hashes, held-out metrics, and the model hash. Raw replays remain in the existing ignored local cache.

The exact tournament loader imported `agent` from `policy.py` and completed both seat-swapped games without candidate errors. The engine silently ignores invalid commands, so successful completion alone does not certify every action’s semantic legality. The replay shows observable inert/colliding behavior, which is the central failure. No replay-derived actor or market action tape is stored or queried by the runtime callable.

SHA-256 at this checkpoint:

- policy: `378e7a9b51a958528da7420fa918d56846a6affb41f93652a4470bbb808775c5`
- extractor: `64c7865799cc81a013e7a895770c819d46f3a61855e486ae23babf10395c2d86`
- aggregate model: `eabb20517c0bcf0559bd63e894f972174e5e3b878fc796bf13e00539514830b0`

This is research-only. It is not a submission recommendation or evidence of ladder strength. A stronger next experiment would need more independent episode-level samples and an explicit worker-to-task allocator before any broad match screen.

## Expanded unit-level holdout

A follow-up builder used 38 episode groups: the 30 new public elite episodes listed in `public_episode_manifest.json`, four earlier elite replays, and reset-candidate diagnostic traces. It extracted one row per actor decision and market turn; player/episode/seed/hash/split information stays in a separate provenance sidecar. Actor rows carry the actor's current-observation features, coarse action verb, crop/species argument where applicable, and an inferred task label from the current tile and inventory. Market rows carry observed state and market intent. The builder omitted replay ID, seed, coordinates, exact step/day/hour, and future observations from the model features. Both players from an elite-vs-elite episode remain in the same split group.

The episode split contains 29 training groups and 9 held-out groups, with zero group overlap. It produced 415,396 training rows and 123,590 held-out rows; the latter comprise 94,089 actor decisions and 29,501 market decisions. A categorical Naive Bayes diagnostic compared with a majority-label baseline gave:

| Held-out label | Naive Bayes accuracy / macro F1 | Majority accuracy / macro F1 |
|---|---:|---:|
| Actor action verb | 0.2495 / 0.2501 | 0.1620 / 0.0155 |
| Actor task | 0.2223 / 0.2586 | 0.4308 / 0.0167 |
| Market intent | 0.1349 / 0.1077 | 0.1297 / 0.0104 |

The task classifier loses on raw accuracy because movement (`MOVE`) is 43.1% of the held-out labels, but has better macro F1 because it spreads predictions across task classes. Market prediction barely improves accuracy over the baseline. These are behavior-label metrics, not expected game reward or a farm policy; they support the no-go decision for direct imitation at this stage. The full grouped dataset and evaluation live in `experiments/v58_validation/imitation_data/` and are owned by the validation study.

## Spatial LightGBM diagnostic

The observation schema was extended with current actor coordinates and day/hour, the local 3×3 tile context, movement-boundary flags, and binned Manhattan distance/count plus signed relative direction to visible task proxies (unwatered crops, crops with yield, unfed animals, shed, and empty pasture). These are computed from the current observation and contain no episode or seed identifiers. The same episode split was retained.

LightGBM on the 29/9 episode split trained from 334,264 actor rows and scored 94,089 held-out actor rows with 96 categorical observation features. The action-verb model reached 70.11% accuracy and 0.7406 macro F1; the task-label model reached 81.04% accuracy and 0.7375 macro F1. These are same-state behavior-label scores, not expected game reward. The learned resolver ranks task labels, chooses movement direction from the verb model, checks arguments against current tile/inventory state, and falls back through lower-ranked tasks to a legal verb or PASS. On held-out states it agreed with the recorded operation and categorical item on 69.29% of actor decisions; quantity is not represented by these labels, and for MOVE the resolved direction must match the recorded direction. It emitted shape-valid commands on 100% of rows and passed its conservative necessary-precondition checks on 100%; replay-recorded actions passed that same proxy on 99.82%. The resolver check does not establish engine acceptance or strategic quality. Full definitions and per-run measurements are in `experiments/v58_imitation/learned_resolver_eval.json`.

The native text boosters total 10.3 MB and score a 1,000-row batch in 0.22 seconds after load. To test portability, compressed JSON tree dumps total 6.58 MB; a stdlib-only categorical tree interpreter matched native class probabilities within 1e-15 on 1,000 held-out rows, but took 11.71 seconds versus 0.22 seconds for native inference. That is about 0.15 seconds for a thirteen-actor observation, 53 times slower than native inference, and the model bundle is too large to count as a self-contained submission source. The callable heuristic above remains a separate negative control; it is not the LightGBM resolver.

That portability gate did not prevent a local rollout: the exact Kaggle loader ran `learned_agent.py` with LightGBM and the local validation artifacts available. The candidate played seed 94700 from both seats against v50 and lost both games without errors or timeouts. It finished at $7,943 in each order against $153,103 for v50, a -$145,160 margin. Replay evaluation found an 86.31% actor changed-state proxy and 86.24% productive-hand rate, but the candidate ended with no animals and no feed attempts. Observable sale drawdown was 95 units worth about $10,741 at observed prices (12 melons, 24 strawberries, 59 wheat); sales were too small to sustain the farm. Candidate action calls averaged 3.78–4.04 ms, with p95 4.66–5.24 ms and one 62.8 ms initial/load spike; full games took about 14.2–14.6 seconds. These are local runtimes with LightGBM installed, not portable-submission measurements. The game confirms that high held-out label accuracy does not make a coherent economic policy. Results, replay hashes, and both full traces are under `experiments/v58_imitation/learned94700/`.

The hierarchy failure is visible in the candidate's market trace: it hired 88 times, bought seeds 33 times, sold 23 times, and never bought an animal or land. Crop activity produced some cash but no scalable livestock income; the learned actor model could not supply the missing multi-day economic plan. A future RL/self-play policy needs a coherent high-level investment and reserve plan (pasture/animal purchase, feed supply, and sales/reinvestment) before optimizing individual action imitation. This evidence is specific to this candidate and seed, not a universal engine strategy.

Reproduce the held-out model and rollout diagnostics from the repository root after the validation agent's model artifacts are present:

```sh
.venv/bin/python experiments/v58_imitation/learned_resolver_eval.py
.venv/bin/python experiments/v58_imitation/portable_eval.py
.venv/bin/python simulation/tournament.py --candidate experiments/v58_imitation/learned_agent.py \
  --agent-b experiments/v50_agent.py --seed 94700 \
  --output-dir experiments/v58_imitation/learned94700 --workers 1 --timeout 180 --replay-policy all
```

The learned resolver report is `experiments/v58_imitation/learned_resolver_eval.json`; the portable inference report is `experiments/v58_imitation/portable_eval.json`. The rollout JSON records the agent-source SHA-256 and normalized/raw replay hashes. SHA-256: `learned_agent.py` = `5b54fe137110cab4f05cbc59745132670a536bbe5ed7259e2d915e34c972b3d5`; validation verb booster = `3ad339baa8841ad8b13f9eb9475a2e096c0487e011da2630ce01bf2e412d0318`; validation task booster = `b95c25269572a7d958f951ca05463facc866dafb0435cbedce18d1e1cfee6b43`; compressed portable artifacts are recorded by `sha256sum experiments/v58_imitation/models/*.gz`.

The fit plus data load took 231 seconds on the local CPU (28 seconds to load, 71 seconds for the action-verb fit, and 132 seconds for the task fit). The Kaggle CLI 2.2.4 was authenticated through a read-only quota query: it reported 0/30 GPU hours and 0/20 TPU hours, refreshing 2026-10-03. The current CLI supports `kaggle kernels push --accelerator ...`; official docs say kernel accelerator starts may queue for several minutes. Only the processed data (~13–16 MB) would be uploaded, never the local 1.1 GB raw replay cache. Because the local workload is a few-minute tabular tree fit and remote GPU support for LightGBM/OpenCL is not verified, a private kernel run has no demonstrated end-to-end advantage. No kernel was pushed and no competition submission was made.

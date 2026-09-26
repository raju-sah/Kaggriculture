# V58 imitation dataset

`experiments/v58_validation/imitation_data/build_dataset.py` turns local public
elite replays and retained reset-candidate traces into compact supervised rows.
It reads source files in place; it does not copy raw replays into the dataset.
The downloaded public replay source list and elite seat mapping live in
`experiments/v58_imitation/public_episode_manifest.json`.

The dataset separates each episode into a train or held-out group before rows
are written. If both players in an episode are in the elite cohort, both seats
stay in the same split. Reset matches contribute only the candidate seat as
declared by the replay artifact's `ab` / `ba` seat suffix. The row-group
sidecars map rows to episode/player/source after training; those fields are not
model features.

The current build contains 38 distinct episodes (30 downloaded public episodes
plus locally retained elite/reset traces), 29 training episodes and 9 held-out
episodes. It has 415,396 training rows and 123,590 held-out rows. Episode IDs do
not overlap across the two splits. The same named players occur in both splits,
so this tests new episodes from the observed policy cohort rather than
generalization to an unseen player. The 94,089 held-out actor decisions cover
18 verbs and 36 task labels; 40,531 are movement (43.1%), 15,247 are water
(16.2%), 7,105 are harvest (7.6%), and 4,865 are feed (5.2%). The 29,501 market
rows cover 22 order-intent classes.

Actor rows use the prior observation and the action recorded at the next replay
state. Features contain only the current observation: current day/hour, actor
coordinates, local tile state, and relative distances to visible task targets,
alongside farm/economic aggregates. A “ripe crop” target is the observation-only
proxy `yield_units > 0`. They omit episode/replay IDs, seed, exact step, future
state, opponent action, action quantities, and target coordinates. Directional
destination flags are contextual features; LOCKED tiles are traversable in the
engine and those flags must not be used as legality masks. Labels preserve
immediate action verbs, crop/animal categories for relevant actions, and task
classes inferred from the action and the pre-action actor tile. Market order
labels are separate rows and omit quantities. Thus the data is not an
executable sequence or an action tape.

Run `python3 experiments/v58_validation/imitation_data/build_dataset.py` to
refresh the compressed train/held-out JSONL and episode sidecar. Run
`python3 experiments/v58_validation/imitation_data/validate_dataset.py` to
verify the group boundary and feature exclusions. `evaluate_dataset.py` holds
the earlier coarse categorical-naive-Bayes diagnostic. The reproducible
LightGBM fit and held-out evaluation is
`python3 experiments/v58_validation/imitation_data/evaluate_lightgbm.py`, and
`benchmark_inference.py` measures exported booster inference. Held-out episodes
are grouped at episode level and chosen by a deterministic hash within source
family. Accuracy is replay behavior imitation, not evidence of a profitable
closed-loop policy. Raw public replay blobs remain in their existing ignored
source directory; the official-rule provenance and originality constraints in
[V58_REPLAY_RIGHTS.md](V58_REPLAY_RIGHTS.md) still apply.

An earlier categorical-naive-Bayes diagnostic on coarse feature bins scored
24.95% action-verb accuracy (macro-F1 .250) and 22.23% task accuracy
(macro-F1 .259). The updated 96-feature categorical LightGBM models include
present-state spatial features and use 70 estimators, 31 leaves, learning rate
.08, and two CPU threads. On the same episode split, action-verb accuracy is
70.11% (macro-F1 .741) versus 16.20% / .015 for the majority baseline, and task
accuracy is 81.04% (macro-F1 .737) versus 43.08% / .017. The strongest
confusions include FERTILIZE→WATER (1,605), WEST→NORTH (1,401), NORTH→WEST
(1,256), and task MOVE→WATER_CROP (2,447). These scores measure held-out
episodes from known policy names, not generalization to unseen players.

Exported boosters are 10.3 MB combined. Loading both takes .065 seconds;
batched inference for 94,089 held-out actors took 16.98 seconds, or .181 ms per
actor for both models. A binned observation-only precondition proxy covers
99.67% of predicted action verbs and passes 98.87% of covered cases. This proxy
is not engine action acceptance: the runtime resolver must apply exact masks
from the raw observation. Model files, category codes, confusion metrics, and
inference measurements are recorded under
`experiments/v58_validation/imitation_data/`.

The raw-observation action resolver was also evaluated with learned model
predictions on all nine held-out episode groups (94,089 actor decisions). It
used observation at replay step t-1 and action at step t. Verb accuracy was
70.11%, task accuracy 81.04%, and resolved operation-plus-item agreement was
69.29% (movement requires the exact direction; only quantities are ignored).
The top task passed the current-state necessary-precondition mask on 99.947%
of rows, with fallback on 0.053%; the resolver emitted a trained-verb action
and passed its conservative necessary-precondition checks on 100%. Recorded
actions passed the same proxy on 99.816%. These checks are not engine action
acceptance, and replay imitation accuracy does not establish profitable
closed-loop play. Full counts and definitions are in
`experiments/v58_imitation/learned_resolver_eval.json`, produced by
`experiments/v58_imitation/learned_resolver_eval.py`; masks inspect raw current
observations. A pure-standard-library tree export matched native LightGBM to
within 1.0e-15 maximum probability error on 1,000 held-out rows, but took
4.19 seconds for verb inference and 7.52 seconds for task inference, versus
0.069 and 0.153 seconds natively. At 13 actors, that projects to roughly 0.15
seconds per observation for both models, so deployment latency remains a
concern. The parity sample and timings are in
`experiments/v58_imitation/portable_eval.json`.

# V58 scheduler throughput diagnosis

## Evidence from the spent seed-95100 replay

`experiments/v58_planner_eval/throughput/audit_plant_batches.py` is a read-only
replay audit. It compares each recorded action with the before/after
observation, grouping no-effect actions by operation, worker, position, and day,
and checking planting batches against private seed inventory. Its output is
`experiments/v58_planner_eval/throughput/probe1_seed95100.json`.

The original probe1 policy had 0.5142 productive hand turns in this audit. It
issued 638 wheat planting actions; the engine atomically cancelled 608 of them
across 116 overdrawn batches, leaving 30 applied. The engine validation at
`kaggriculture.py:920-931` counts all same-crop PLANT requests before applying
any unit actions. Per-worker seed masks therefore cannot make a planting batch
safe. The later aggregate seed reservation fix was reported to yield 68/68
valid PLANT actions, but only 0.681 productive turns, 340 watering effects,
and about $14k terminal cash. That follow-up is from the validation branch;
this note does not rerun it.

The remaining losses are predominantly missing work, not failed movement. The
validation instrumentation classifies 1,479 no-task PASS slots as 614
seed-starved crop opportunities, 369 turns after the day-24 planting cutoff,
and 496 turns with no remaining schedulable task. Another 353 attempted tasks
were blocked by resource or stage, including 42 feed attempts. Of 1,737
movement slots, 1,717 made progress and 20 did not; only 14 targets changed
midday. Thus route churn is measurable but secondary to work and input supply.

The historical v50 replay on the same seed requests 166 wheat plants and
applies all 166. Its wider crop mix and task coverage also yield more work.
Absolute hand-rate/effect counts in this local audit differ slightly from the
shared evaluator because the audit uses direct frame-to-frame state diffs;
use the validation instrumentation and `evaluate_replays.py` for official
cross-candidate metrics. No games or new seeds were used for this diagnosis.

## Scheduler invariant to test

Use a **feasible-work coverage invariant** across the daily manager and the
per-turn scheduler:

> Every hired hand must have a positive-value, input-ready task route in the
> day plan; every task token has one worker owner; do not hire beyond the
> number of profitable feasible routes.

At hour zero, construct task tokens from current observation only. A token is
eligible only when its operation preconditions and resource requirements hold,
and enough season remains to mature, harvest, and sell its output. Score crop
options by expected net sale value divided by seed/feed cost plus worker-turns
for travel, care, harvest, and hauling. Buy seeds for the next actor phase;
market purchases occur after unit actions, so they cannot authorize planting
in the same turn. Replace the fixed day-24 cutoff with a per-crop profitability
and maturity check. Assign each token to one worker by expected value per
worker-turn, including a distance penalty. Hire only if another feasible
positive-value route is uncovered. If a worker has no token, reserve that
worker as unstaffed instead of emitting PASS turns from an unnecessary hire.

Within the day, preserve a worker's local crop or animal service cluster while
it still has feasible work; send it elsewhere only when its current cluster is
exhausted or a higher-value urgent task (such as feed) dominates. This should
reduce crossing and long trips, but the 14 observed target changes do not
support making route persistence the first fix.

## Cheap validation checks before any new games

- Generate one action batch with seed inventory `n` and more than `n` planting
  targets; assert exactly `n` PLANT actions remain and the rest are PASS.
- For each planned actor, assert one unique task owner and verify current
  preconditions, inputs, and remaining-season profitability.
- Assert no hire is added when all available task tokens are already owned or
  have nonpositive expected net value.
- Assert purchases made at hour zero affect only later actor phases.
- Count no-task PASS slots, task-blocked operations, travel distance to owned
  targets, operations completed, crop sale revenue, seed purchases, feed
  shortfalls, and cash by day. Use these to distinguish a staffing/input gain
  from a routing gain.

The post-fix opportunity is therefore to improve the crop portfolio and align
staffing with executable, profitable work. Station-aware assignment is a
follow-on improvement once the policy supplies enough useful tasks.

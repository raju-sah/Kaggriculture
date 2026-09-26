# V58 simulator-based economy-policy search

## Recommendation

Train a coherent economy controller against the simulator with an evolutionary
search over a compact daily portfolio policy, while keeping the actor movement
and task executor as a separate legality-first option controller. Do not train
another next-action classifier. The seed-94700 learned-label rollout is a clear
counterexample: it had 70.1% verb accuracy and 81.0% task accuracy, yet ended at
$7,943 versus $153,103 for v50, hired 88 times, bought 33 seed orders, and never
bought livestock or land. The missing decisions span several days, so matching
individual elite actions cannot teach when to invest, provision feed, and sell.

The public elite replay corpus is also a weak offline-RL source: it contains
only 30 downloaded games (38 unique episode groups including local traces),
with no counterfactual actions or complete hidden farm state. Assigning each
observed action its episode's terminal score would give correlated, heavily
policy-biased labels, not a credible action-value estimate. Keep those replays
for descriptive analysis. Generate counterfactuals from the pinned simulator.

## Proposed policy hierarchy

Use three layers, each with a narrow contract:

1. **Economy manager, one decision at hour 0 each day (30 decisions per
   season).** Read current money, hands, land, crop stages/yields, animal counts
   and feed state, seed reserve, shed inventory, market prices/inventory, and
   unlocked shops. Emit setpoints for target animals by species, crop acreage
   by crop, staffing/expansion, cash/feed reserve, and liquidation/reinvestment
   intent. Recompute them from the current observation; do not depend on hidden
   episode ID or action history.
2. **Option scheduler, every turn.** Assign farmers/hands to persistent tasks
   such as fulfill feed deficit, water/harvest a chosen crop, build/place a
   planned animal, transport goods, or service an investment target. Tasks
   terminate when complete or invalidated. Per-unit targets must persist by
   `(unit, species/task)` until completion; the earlier route bug erased a cow
   target while checking absent sheep/goose inventory.
3. **Action executor, every turn.** Convert one task to a single legal move or
   operation using current observation and private inventory. Movement is
   bounded by board edges; LOCKED tiles are traversable. Mask task actions
   against the engine preconditions and pass rather than issue silent no-ops.

The search tunes only the manager at first. Keep its output small and
interpretable: e.g. crop portfolio weights, species herd caps, wheat/feed
coverage target, reserve cash, maximum daily investment fraction, hire target
by season phase, and an expansion trigger. Route the mid/low layers with
explicit state and legal-action tests before exposing these knobs to search.

## Learning signal

The competition objective is final bank coins. For every rollout retain the
actual terminal money and candidate-minus-opponent margin; use no imitation
accuracy as a policy objective. Preserve the exact reward for ranking
candidates. For critic/credit-assignment experiments, log day-boundary deltas
for cash, sold goods, productive crop inventory, fed/cared herd, unpaid feed
need, and wasted/overflow inventory. A potential-based shaping term
`lambda * (Phi(next_day) - Phi(day))`, with `Phi(terminal)=0` and undiscounted
returns, can redistribute reward toward investments without changing the
optimal terminal-cash policy. Make `lambda=0` the control. Do not add arbitrary
bonuses for herd size, hires, or harvest counts: these can reward bankrupt
expansion. Any inventory valuation must use current observable prices and
include shed capacity, time to sale, feed obligation, and future production
risk; calibrate it only as a potential, never as a substitute terminal score.

A day-level value learner is a later option: fit value on simulator-generated
states with terminal final coins as targets, split by complete seed block, and
use it only to rank the manager's legal macro-options. Do not use random
turn-level replay splits; neighboring frames share almost the same state and
outcome.

## Search and paired evaluation protocol

Use a compact, predeclared parameterized manager and Cross-Entropy Method
(CEM), rather than manually adding rules after each loss. At each generation,
score 20 candidate parameter vectors on the same training seeds against both
frozen v50 and v53 references, with candidate in both seats. Update the
parameter distribution from the top four candidates; run four generations,
then freeze the single best by mean paired coin-margin delta with worst
opponent mean as the first tie-breaker. The development objective is mean
paired margin; report strict wins, mean candidate coins, and per-opponent/per-
seat outcomes separately. The fixed references and common seeds reduce
market/shop randomness in comparisons. Do not use confirm seeds for further
tuning.

Suggested first allocation, pending root confirmation and seed-ledger check:

- Train/search: seeds `95100-95107`, 8 common seeds × 2 seats × 2 opponents per
  candidate; 20 candidates × 4 generations = 1,280 matches per reference set
  (2,560 total).
- One-time validation after candidate/hash freeze: seeds `95120-95127`, 8
  unseen seeds × 2 seats × 2 opponents = 32 matches for the frozen candidate.
- If the 8-seed validation is nonnegative on both opponents, zero-error, and
  positive in at least 6/8 seed blocks, allocate a separate larger dev panel
  before any readiness claim. These are proposed ranges, not a claim that the
  seeds have been reserved. Check the shared ledger before running anything.

Use `simulation/tournament.py` with at most four workers and retain all replays
for training winners and the final validation arm. Hash and freeze every
candidate policy and opponent before each generation. Record every vector and
score; do not promote a policy because of one favorable seed. The designated
final holdout `93000-93049` remains sealed and is not part of this protocol.

## Compute feasibility and Kaggle GPU

A read-only `.venv/bin/kaggle quota` check on 2026-09-26 reported 0/30 GPU
hours and 0/20 TPU hours used, refreshing 2026-10-03. That quota is available,
but it does not speed up the Python Kaggriculture transition function or the
720-step, per-turn agent interface. The recent learned LightGBM match took
14.37 seconds per game; at that measured rate, 2,560 games are about 10.2 CPU
hours, or 2.6 hours of ideal wall time with four fully utilized workers, before
startup and analysis overhead. Treat that as an upper-bound planning estimate
for this slower model; profile a deterministic manager before reserving the
full budget. A small 32-match validation would take about eight CPU minutes at
the same rate.

A GPU is useful only if we later train a neural value model on a sufficiently
large simulator-generated corpus. For the first manager search, computation is
mostly environment stepping and candidate evaluation, so use local CPU workers
and keep Kaggle's GPU quota unused. The prior categorical LightGBM work fit in
231 seconds locally; uploading a private dataset and queueing a GPU kernel
would not help this search. The portable tree prototype was about 53× slower
than native LightGBM, so do not put it in the turn loop. If a value network is
justified later, first benchmark GPU training against local CPU on the same
synthetic rollout corpus; keep the Kaggle dataset/kernel private, never upload
the raw public replay cache, and never submit a competition agent from the
training kernel.

## Implemented prototype and negative trial

The prototype and its initial CEM-vector screening now exist under
`experiments/v58_validation/rl_design/`. Only seed `95100` has been used in
this branch: the original four-vector screen and two subsequent paired
diagnostics, all with both seat orders. No other proposed seed and no final
holdout seed has been used. The initial exact-loader checks had no errors, but
the best original screen was still far below v50 and failed the predeclared
cash/throughput gate, so the CEM was stopped.

Replay instrumentation then identified the concrete crop bottleneck: many
PLANT requests were rejected together by the engine's all-or-nothing seed
check; there were also 614 seed-starved crop task slots and 369 late-season
crop slots produced by the old blanket cutoff. Movement was mostly progress
(1,717 actions reduced distance to target, only 20 did not), so route churn was
not the primary cause. An atomic plant-budget mask passed four focused tests
and a paired spent-seed run improved action validity, but on the crop14/herd2/
staff7 vector the candidate still made only 68 plant actions, 340 water
actions, and $14,210 versus v50's $109,776.

A follow-up funded-work change caps crop task tokens at current seeds, prevents
sowing after day25, replenishes up to three seeds after current-turn actor
actions, and hires according to current task-token count. Its exact-loader
paired run also used only spent seed `95100`, with no runtime errors or
timeouts. It lost both orders: candidate $8,000 versus v50 $139,885 in each
order (−$131,885). The replay had 36 plants, 161 water actions, 33/33 feed
successes, two sheep lost after day26, and only $7,671 in observed-price
accepted-sale lower-bound value. The gate reduced seed purchases to 20 and
hires to 25, but it also left too few hands to sustain crop coverage. This is
a negative result, not support for a CEM search. The detailed hashes and game
records are in `experiments/v58_validation/rl_design/coverage95100/`; focused
invariants are in `test_atomic_plant_budget.py`.

Do not spend another seed on this candidate until the staffing rule values
the output of funded tasks and estimates their daily travel/work capacity,
rather than assigning a fixed four-token threshold. A valid next intervention
must raise crop coverage and sale income on a spent observation/replay first.
The earlier CEM train/validation allocations below remain proposals only;
their seed ledger must be checked before any future use. No current result is
a readiness or top-ten claim.

## Engine facts used

The installed engine is `.venv/lib/python3.12/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py`.
`interpreter` applies each unit action, then market orders, town consumption,
plant decay, and daily refresh every 24 turns; terminal reward is the farm's
cash after 720 turns. The action executor must respect silent no-op rules,
plant-seed atomicity, shed capacity 100, daily hand reset, daily animal feeding,
and market-order caps. These mechanics make cashflow and feed coverage
necessary state variables for the economy manager.

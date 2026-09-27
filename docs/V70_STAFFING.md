# V70 staffing economics from spent V69/V56 replays

## Finding

The evidence supports conditional staffing up to 14 hands when the farm has a
large, serviceable backlog; it does not support a fixed 10–14-hand target.
V56 reached 14 hands and generated substantially more productive work and
accepted sales than V69, but those matches do not isolate the causal return to
each hire. V69's shortfall is also a task-routing problem: its workers spent
more actions moving and generated far fewer productive operations. Hiring
more into that policy without changing accessible workload could amplify the
inefficiency.

## Engine cost and break-even

The exact engine uses a per-day Fibonacci hire ladder with `farmHandCostMult`
defaulting to 1. Hires reset each day, and a hand hired in the hour-0 market
phase works the remaining turns before disappearing at day end. Thus the
sequence is a daily cost, not a one-time wage or a season-long contract.

| Daily hire order | Cost of this hand | Cost for this many hires that day | Extra cost vs 10 hires/day | Extra cost over 10 remaining days |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 1 | 1 | — | — |
| 2 | 1 | 2 | — | — |
| 3 | 2 | 4 | — | — |
| 4 | 3 | 7 | — | — |
| 5 | 5 | 12 | — | — |
| 6 | 8 | 20 | — | — |
| 7 | 13 | 33 | — | — |
| 8 | 21 | 54 | — | — |
| 9 | 34 | 88 | — | — |
| 10 | 55 | 143 | — | — |
| 11 | 89 | 232 | 89/day | 890 |
| 12 | 144 | 376 | 233/day | 2,330 |
| 13 | 233 | 609 | 466/day | 4,660 |
| 14 | 377 | 986 | 843/day | 8,430 |

The last column is marginal accepted contribution that must be added by that
headcount versus ten hires each day, before any safety margin. For example,
maintaining fourteen instead of ten hires from day 20 through day 29 costs an
additional **$8,430** (10 × $843). “Contribution” means expected accepted
sales less incremental seed, feed, product, land, and other input costs; gross
sales alone are not a valid break-even measure.

## What the six spent seat-swapped replays show

These are three seed blocks (94700, 92802, 92804), each with both seats, not
six independent seeds. Exact replay observations show V56 issued 289 hire
orders per match (9.63/day), reached 14 concurrent hands, and incurred an
estimated **$8,366** in Fibonacci hire costs per match. V69 issued 231–243
orders (7.7–8.1/day), peaked at 8 hands, and incurred an estimated
**$1,952–$2,622** in hire costs per match (mean $2,175). These costs are
reconstructed from each day's submitted hire-order count and the engine
ladder; the corresponding replay reports have no errors.

| Mean per 30-day match | V69 | V56 |
| --- | ---: | ---: |
| Hire orders / average per day | 235 / 7.83 | 289 / 9.63 |
| Peak hands observed | 8 | 14 |
| Estimated hire cost | $2,175 | $8,366 |
| Productive hand actions | 1,282 | 3,297 |
| Hand movement actions | 3,261 | 2,839 |
| Productive share of productive + movement actions | 28.2% | 53.7% |
| Unharvested ripe crop tile-days | 632 | 542 |
| Due / served animal-care days | 170 / 146 | 412 / 387 |
| Due / served animal-feed days | 170 / 164 | 412 / 331 |

V56's roughly **$6,191** extra hire cost per match coincided with 2,015 more
productive hand actions, 1,723 fewer movement actions, more accepted product
sales, and mean cash of about $132,144 versus V69's $47,990. The observed
cost per extra productive action is about $3.07, but that ratio is descriptive
only: V56 also had a larger animal/crop portfolio, different routing and
market outcomes. It cannot be treated as the causal marginal return of a
hire. V69's high movement burden and roughly 632 ripe-but-unharvested tile-days
show work exists, but do not prove every such tile-day was reachable or worth
harvesting at the prevailing shop quote. Conversely, V56 still accumulated
542 ripe-but-unharvested tile-days and left about 25 animal-care-days and 81
feed-days unserved; this implies real contention even at fourteen hands.

The action totals suggest hired capacity was used: productive plus movement
actions averaged about 19.3 per V69 hire and 21.2 per V56 hire. A hand hired
at hour 0 has at most 23 remaining turns, so those totals are near the
available action ceiling. But V69's low productive share says adding workers
without reducing travel and prioritizing valuable tasks is unlikely to close
the gap. The result comparison is V69's three-seed, six-game panel against
V56; see [V69 dispatch results](V69_DISPATCH.md) and the retained replay
metrics in `experiments/v69_dispatch/panel_metrics.json`.

## State-derived hiring rule for V70

Use the live observation to construct a one-day work queue, then price the
marginal worker against the queue that can actually be served before tasks
expire:

1. Enumerate reachable jobs from the current board and inventories: dying or
   due crops, ripe crops with positive expected accepted contribution,
   animal feed/care due today, collectable output, and required handling or
   build steps. Exclude jobs blocked by missing inputs, inaccessible land,
   full inventory/shed, or zero/negative expected accepted value.
2. Estimate each job's full action cost, including movement from the proposed
   work zone, using the current hand/farmer positions. Order jobs by expected
   net contribution per action, with survival and animal-welfare deadlines as
   hard constraints. The result is a reachable action queue, not a count of
   all ripe tiles or all due animals.
3. Estimate the queue's served contribution under the current staffing and
   under one extra hand. Hire the next hand only when its expected incremental
   accepted contribution (including preserved crop value and avoided animal
   losses, less incremental inputs) exceeds that day's Fibonacci cost by a
   25% buffer. This buffer is a proposed risk margin, not a measured optimum.
4. Cap staffing at the point where the marginal worker adds no positive-value
   queue capacity. Permit orders through the observed fourteen-hand range;
   do not force fourteen when work is sparse, travel-heavy, or economically
   negative. Under V69-like routing, first target 8–10 hires and improve zones
   and task ordering. Expand toward 11–14 only when the computed marginal
   queue clears the $89, $144, $233, then $377 per-day thresholds.

This policy uses only the current state, known game rules and visible quotes;
it does not key decisions on seed or replay identity. It also avoids treating
“more backlog” as sufficient: distance, deadline, input availability and
expected accepted price all affect whether an additional worker pays.

## Limitations and next measurement

The sample has only three spent seeds, and the policies differ in far more
than headcount. Tile-day backlog is accumulated over time, not a point-in-time
queue; it can include jobs that were inaccessible or not profitable. Hire
spending is reconstructed from submitted order counts and the exact ladder,
not claimed as a causal cash treatment. The V70 capacity and dispatch branches
should log, per day, marginal reachable jobs with estimated action distance,
deadline, accepted contribution, current staffing capacity, and work left
unserved. A headcount ablation should then compare 8/10/12/14 only after the
same task policy and portfolio are fixed, using already-spent seeds first.

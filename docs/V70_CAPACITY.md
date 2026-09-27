# V70 observation-driven capacity experiment

## Result

`experiments/v70_capacity/agent.py` is frozen at SHA-256
`2002db9b4bbf20c654805adc35617eb787be3e9cb64e5aae46ae1044aad3b73e`.
It starts from the pinned V69 batch-assignment controller
`experiments/v69_dispatch/agent_v70_batchassign_frozen.py` (SHA-256
`a74027a6b053915beedde6a43da0d6aea81c70119406a1d3b566a003548f9bac`).
The V70 change estimates current task-route work and conservatively discounted
value from observable jobs, then hires above the baseline 4–8-hand target only
when estimated workload exceeds the current crew's 24-action-per-unit shift
and the remaining value clears the daily Fibonacci hire price plus 25%.
It does not add land or animals.

Exact-loader, seat-swapped games on spent seeds produced:

| Opponent | Games | Record | Mean candidate cash | Mean margin |
| --- | ---: | ---: | ---: | ---: |
| Frozen V69 batch dispatcher | 6 | 6–0 | $66,191 | +$3,877 |
| V56 | 6 | 0–6 | $57,185 | −$79,123 |

Per-seed V70 margin against the frozen dispatcher was +$1,826 on 94700,
+$8,883 on 92802, and +$924 on 92804, averaged over both seats. Against V56,
it remains far below the $130k target. These are spent-seed results only; no
fresh seed or submission was used.

## What the added capacity did

The exact settlement audit of seat-0 V70-vs-dispatch replays reconciled every
cash transition (1,438 aligned player-transitions per replay, zero mismatches).
Accepted sale value was:

| Seed | V70 accepted sales | Dispatcher accepted sales | Change |
| ---: | ---: | ---: | ---: |
| 94700 | $71,865 | $66,371 | +$5,494 |
| 92802 | $84,777 | $74,393 | +$10,384 |
| 92804 | $88,463 | $83,493 | +$4,970 |

Fertilizer, melon, and strawberry were the largest gains. On these same replays,
the V70 seat sold $12,070 / $11,415 / $12,070 fertilizer, $16,125 / $16,670 /
$16,125 melon, and $12,155 / $13,416 / $11,847 strawberry. The matching
dispatcher seat sold $10,039 / $8,245 / $10,039 fertilizer, $14,823 / $12,929 /
$14,823 melon, and $11,133 / $10,553 / $10,962 strawberry.

Aggregate action counts over the six seat-swapped games show why this is only
a modest improvement. Counting farmer and hands together, the candidate issued
8,417 direct production actions and 22,520 moves, versus 8,006 production
actions and 19,240 moves for the dispatcher. PASS rose from 4,911 to 7,257.
The productive share of production-plus-movement actions fell from 29.4% to
27.2%. HIRE intents rose from 1,477 to 2,445 across the six games; these are
submitted orders and must not be mistaken for hires that the engine accepted.
More capacity created more sale volume, but its marginal actions still had a
high travel/idle burden. The next iteration should improve task supply and
local work assignment before raising headcount again.

## Capacity budget and limits

The engine grants each active unit one action per hour, 24 per day. Fourteen
hands plus the farmer therefore give at most 360 unit-actions/day versus 216
for a farmer plus eight hands. With 17 placed animals, the recurring floor is
34 feed/care actions/day and up to 17 fertilizer collections; this excludes
travel, carrying, and product harvesting. A larger crew is physically useful
only when the farm can present enough reachable work in that same day.

Planting has deadlines that make raw acreage a poor workload proxy: fresh
plants need same-day water, wheat is a short one-shot crop, melon loses value
after its early yield window, and strawberries need to be established early
enough to reach their first harvest and still meet a buyer. The V70 estimate
uses current task positions, nearest-unit Manhattan distances, live quotes,
and an acceptance haircut. It does not estimate future crop demand or accepted
shop capacity, and its static task-value model remains a coarse approximation.

The separate [V70 staffing economics audit](V70_STAFFING.md) gives the exact
daily hire ladder and the observed V56/V69 service gap. Neither the six-game
positive margin over the corrected dispatcher nor the increased accepted
sales justify promotion: V70 loses every V56 match and its productive share
declines. The candidate is frozen so V71 can use it as a controlled baseline.

## Reproducibility

Frozen candidate and experiment paths are recorded in
`experiments/v70_capacity/manifest.json`. Reports and exact replays are under
`experiments/v70_capacity/spent94700_vs_batch/`,
`spent92802_92804_vs_batch/`, `spent94700_vs_v56/`, and
`spent92802_92804_vs_v56/`. The baseline source was hash-pinned before copying;
the official local Kaggle environment was version 1.32.7. No changes were made
after the candidate hash above was recorded.

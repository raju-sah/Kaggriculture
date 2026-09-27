# V69 deadline-aware dispatch

## Change

[`experiments/v69_dispatch/agent.py`](../experiments/v69_dispatch/agent.py)
starts from frozen V67 and changes only crop-water task eligibility. A crop
already watered recently can wait one day: a water task is created when a
plant is new today, its unwatered streak is already one (it will die after a
second missed day), or an existing strawberry is due for fertilizer. Such
watering tasks use the urgent priority. This uses the engine's actual
two-consecutive-unwatered-day death rule instead of asking workers to water
every healthy crop every day. All planting, market, herd, land, and hiring
rules remain as in V67.

The source SHA-256 is
`8c69e1f4d756a83effc43b966b808df8441aec22c159396e2b7cd98a15a3112f`.
The exact V67 base hash is
`3957e2b5cc48218ac1259899e5ca7c8f7a71d61dd2fabf7faa4ef1226d5ce364`;
the V56 control hash is
`d9e9670921b62afedfa8cbc7086d2a2ec19e153ee26006cef477eadd462bd19c`.
V69 has no tape and reads the live observation each turn.

## Paired results on spent seeds

| Seed | V69 mean cash | V67 mean cash | V69 margin vs V67 | V69 mean cash vs V56 | V56 mean cash | V69 margin vs V56 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 94700 | $48,730.50 | $43,239.50 | +$5,491 | $40,335 | $138,910 | −$98,575 |
| 92802 | $59,065.50 | $54,864.50 | +$4,201 | $52,341 | $131,143 | −$78,802 |
| 92804 | $46,737 | $42,455 | +$4,282 | $51,294 | $126,379 | −$75,085 |

V69 won **6/6** seat-swapped games against V67, with mean margin **+$4,658**.
It lost **0/6** to V56; mean margin was **−$84,154**. All games completed
without execution errors. The 94700 V67 pair, 92802/92804 V67 panel, and
three-seed V56 panel, including replays and ledgers, are retained under
[`experiments/v69_dispatch`](../experiments/v69_dispatch/).

## What improved

Across the six V69-versus-V67 matches, V69 maintained 12 live strawberry
plants at days 12, 13, 14, and 20 in every match. The corresponding V67 mean
was 7.8 at day 12, 5 at days 13 and 14, and 0.2 by day 20. In particular, on
seed 94700 V67 fell from 4 and 2 live plants in its two seats at day 12 to
one or zero by day 20; V69 kept 12 in both seats through day 20.

V69 harvested and sold 151 strawberry units in the six paired matches,
compared with 6 for V67. Its accepted sales also shifted toward wheat and
melon. The six-game accepted unit totals were:

| Product | V69 | V67 | V69 vs V56 | V56 |
| --- | ---: | ---: | ---: | ---: |
| Strawberry | 151 | 6 | 138 | 960 |
| Wheat | 1,282 | 1,057 | 1,334 | 2,472 |
| Melon | 392 | 270 | 416 | 72 |
| Milk | 409 | 432 | 406 | 648 |
| Wool | 539 | 594 | 542 | 306 |
| Egg | 229 | 363 | 186 | 1,326 |
| Fertilizer | 523 | 594 | 538 | 1,838 |

The overall hand action rate did not rise: V69 averaged 1,290 productive
hand actions and 3,269 moves per match against V67's 1,435 and 3,219. Its
productive share of non-pass hand actions was 28.3% versus 30.8%. The gain is
therefore about assigning the limited work budget to crops with survival and
sale value, not increasing total actions. Strawberry-specific watering rose
from 180 to 622 actions across the six games, keeping the long-lived crop
portfolio alive long enough to harvest.

That gain carried an animal-care tradeoff. V69 served 911 of 1,050 due
animal-days for care (87%) and 1,016 of 1,050 for feed (97%); V67 served
1,090 of 1,115 for care (98%) and 1,084 of 1,115 for feed (97%). Neither side
had animal escapes. Against V56, the structural scale gap remains: V69
averaged 1,282 productive hand actions and 3,261 moves, versus V56's 3,297
and 2,839. V69 sold 138 strawberries versus V56's 960 and averaged $47,990
cash versus $132,144.

## Additional probe and limits

I tested a separate value-based harvest-priority variant on 94700. It still
won both seats against V67 but averaged +$2,530, below the +$5,491 from the
water-deadline source; it is retained as
[`agent_harvestvalue.py`](../experiments/v69_dispatch/agent_harvestvalue.py)
with SHA-256
`ee941500bad1e4f6c3de88a32f0fea550eee37e2c79fbe5e60b3f86b3f6d75cd` and is
not promoted.

V69 improves the V67 comparison but remains far behind V56. It also leaves
most ripe strawberry tile-days unharvested and misses more animal care than
V67. The next scale work should combine this deadline-aware water policy with
more efficient local work assignment and sufficient hands, then recheck feed,
care, crop sales, and cash together. No fresh seeds or Kaggle submissions
were used.

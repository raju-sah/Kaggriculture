# V68 strawberry duty ablation

## Implementation

[`experiments/v68_straw_duty/agent.py`](../experiments/v68_straw_duty/agent.py)
is based on frozen V67 SHA-256
`3957e2b5cc48218ac1259899e5ca7c8f7a71d61dd2fabf7faa4ef1226d5ce364`.
V68 separates the strawberry planting gate from crop-duty discovery: it keeps
every live strawberry tile in the water/harvest/fertilizer task set even if
the shop or price gate closes. Planting continues to require the original
market gate. V68 source SHA-256 is
`3f13a4375fbd67ba859dc5e23f56cae1dd70c646b5a3c855cf816fff73dc54a2`.

## Spent seed 94700 paired result

Both seat-swapped games completed without errors. Candidate V68 went 1–1
against V67 with mean margin **$0**. The score was always $41,638 for seat 0
and $40,258 for seat 1, independent of which source occupied each seat. The
replay action sequences also match exactly by seat across the two swapped
games. This means the $1,380 seat margin is a positional effect, not a V68
improvement; the ablation made no action or cash difference on this seed.

The planting gate never closed while strawberry plants were alive in either
farm. The minimum strawberry quote was $128, but it occurred only after the
live strawberry count had reached zero. Thus 94700 did not exercise the
condition this patch targets.

The board snapshots show substantial crop attrition despite the gate staying
open. Live strawberry counts peaked at 11 tiles for seat 0 and 12 for seat 1.
At day 12 those counts were 10 and 11; by day 13 they fell to 2 and 5, and by
day 14 both had only 2. Seat 0 reached zero by day 20. Seat 1 held two live
plants through day 20, one at day 25, and zero by day 29. Strawberry-related
actions across the season were:

| Seat | Successful water actions on live strawberry tiles | Harvest actions on live strawberry tiles | Accepted strawberry sales |
| --- | ---: | ---: | ---: |
| 0 | 32 | 0 | 0 units |
| 1 | 48 | 7 | 7 units |

The seven seat-1 sale orders each had strawberry stock in the shed when
submitted, so all seven units were accepted. Seat 0 had no strawberry sale
orders. These figures were identical under V67 and V68 for the same seat.
This points to a harvest/watering throughput problem on this replay, rather
than the shop/price gate suppressing existing-plant duties.

Detailed match records and replays are in
[`experiments/v68_straw_duty/spent94700_vs_v67`](../experiments/v68_straw_duty/spent94700_vs_v67/).
No fresh seeds or Kaggle submissions were used. Since the target gate did not
change while crops were alive, this result validates compatibility but does
not establish that the defect is fixed in a regime where the gate closes.

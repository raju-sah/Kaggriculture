# V71 adaptive crop portfolio test

## Candidate and result

`experiments/v71_portfolio/agent.py` is frozen at SHA-256
`b2f4174e40e12809557b97ac17f57463acb1c3eb491d33d671ad4487374fae5f`.
It copies frozen V70 (`2002db9b4bbf20c654805adc35617eb787be3e9cb64e5aae46ae1044aad3b73e`)
and changes only the crop allocation. When a strawberry buyer is open and the
live strawberry quote is at least $170, it reserves up to four empty near-shed
melon plots for strawberries; at $210 or more it reserves up to six. It stops
new berry planting after day 8 and continues to service existing strawberry
and melon plants after a price or buyer change. It makes no herd, land, or
staffing changes.

The exact-loader, seat-swapped test on spent seeds 94700, 92802, and 92804
finished 5–1 against frozen V70, with mean margin **+$762** and mean candidate
cash $65,433. It lost all six games against V56, with mean candidate cash
$56,452 and mean margin **−$78,867**. Against V56, V70 averaged $57,185 on the
same three seed blocks, so V71's own cash was about $733 lower. The candidate
is not promoted; no fresh seed or submission was used.

| Seed | Mean V71 margin vs V70 | V71 cash vs V56 | V56 cash |
| ---: | ---: | ---: | ---: |
| 94700 | +$830 | $56,599 | $146,670 |
| 92802 | +$412 | $58,440 | $127,537 |
| 92804 | +$1,043 | $54,318 | $131,750 |

## Market value and crop conversion

V70's seat-1 accepted-sale ledger from the three V71-vs-V70 AB replays gives
an empirical crop baseline. Accepted sales averaged about $8,378 for 241 wheat
units (roughly $35/unit), $15,566 for 76 melon units (about $205/unit), and
$11,935 for 53 strawberry units (about $225/unit). These are realized average
values, not true marginal prices: both players share a nonlinear market
inventory, shops consume products every four turns, and every sale changes
later quotes. The engine's wheat, melon, and strawberry seeds cost $10, $80,
and $100; wheat is one-shot with up to six units, melon is one-shot with up to
six, and strawberry produces up to four fruit from its day-10 start. Strawberries
therefore have stronger realized value per unit, while melon can yield more
units per planting with less repeated harvesting.

| Seed | V71 vs V70 accepted sale total | V70 total | Strawberry units, V71 / V70 | Melon units, V71 / V70 |
| ---: | ---: | ---: | ---: | ---: |
| 94700 | $70,346 | $69,564 | 56 / 51 | 76 / 76 |
| 92802 | $82,304 | $82,483 | 57 / 57 | 76 / 76 |
| 92804 | $90,699 | $89,733 | 56 / 51 | 76 / 76 |

The V71 sale-value changes were +$782, −$179, and +$966. Strawberry sales
increased by five units on two seeds and did not increase on 92802. Melon
accepted unit counts did not change. The replay's 339 ripe-wheat and 209
ripe-melon tile-days show unmet harvest capacity, but they cannot be priced as
lost revenue: ripe tile-days do not say whether the unit could still be
harvested, sold at a good quote, or accepted before market conditions changed.
V56's 255 accepted strawberry units (about $49.6k–$62.3k across these seeds)
show considerably more berry throughput is possible, but V71's small plot
reallocation did not approach it.

Every settlement audit aligned 1,438 transitions per replay with zero cash
mismatches. In the one lost game, seed 92802 with V71 in seat 0, candidate cash
was $67,761 versus V70's $68,561 (−$800). Accepted sale value was $82,304
versus $82,483. Strawberry units were identical (57); V71 gained $262 of
fertilizer sales but lost value in eggs (−$345), milk (−$260), and wool
(−$326), with small offsets in melon and wheat. Thus the field change did not
produce the intended extra berries in that matchup.

## Action conversion and decision

Across the six V71-vs-V70 games, direct production actions changed from 8,417
to 8,423, movement from 22,520 to 22,437, and PASS from 7,257 to 7,280; HIRE
intents changed from 2,445 to 2,447. The intervention did not increase travel,
but its production and accepted-sale gains were small. The crop mix shifted
only when plots were empty and the quote gate remained open, while planted
crops stayed sticky. This protected existing output but left few cells
available for early reassignment.

This test does not justify another staffing or crop-area increase on the same
evidence. A later portfolio revision would need to act before low-value crops
occupy their plots and measure the resulting accepted units and cash, not just
the number of seeded fields. Animal expansion is intentionally not mixed into
this result: it would add feed/care work and obscure the crop-mix effect.

## Reproduction

The frozen source, baseline hashes, engine pin, spent seeds, and report paths
are recorded in `experiments/v71_portfolio/manifest.json`. Reports and replays
are under `experiments/v71_portfolio/spent_vs_v70/` and
`experiments/v71_portfolio/spent_vs_v56/`.

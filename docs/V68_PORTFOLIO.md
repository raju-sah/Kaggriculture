# V68 portfolio experiment

## Decision

V68 is an isolated state-derived experiment, not a submission candidate. On three already-spent seeds (94700, 92802, 92804), it beat V67 on two seeds and lost on one, with a mean paired score margin of only **+$1,167** across the three seed pairs. It lost every seat-swapped match against V56, averaging **−$102,869**. The narrow portfolio repair is real but far too small to address the production gap, and its V67 improvement is not reliable enough to promote.

No new seed was used. Each comparison used the repository's exact Kaggle Environments 1.32.7 loader and both seat orders. All 12 games completed without agent or infrastructure errors. The results and retained replays are in `experiments/v68_portfolio/spent94700/` and `experiments/v68_portfolio/spent92802_92804/`.

## Candidate design

The candidate starts from frozen V67 SHA `3957e2b5cc48218ac1259899e5ca7c8f7a71d61dd2fabf7faa4ef1226d5ce364`, saved as its own controller at `experiments/v68_portfolio/agent.py`. It reserves four cells nearest the shed in the first expansion for strawberries, uses later cells for wheat and melon, and opens that quadrant only when a strawberry buyer and a strawberry price of at least $150 are visible. It begins berry planting only when the seventh hand is present and the shop/price gate remains active. Once plants exist, it keeps them in the service plan even if the quote changes. It avoids fertilizer trips at this four-plant scale, waters only as needed to avoid a second dry day, and holds three days of feed for the current herd before selling wheat.

The testable hypothesis was that a small, short-route berry lot could turn seed spend into sales while preserving the existing animal route. It did: against V67 on seed 94700, V68 accepted an average of 14 strawberry units worth about $3,482 across seat swaps, versus V67's four units worth about $919. But V68 did not deliver enough incremental production to justify expansion as a general policy.

## Match results

| Spent seed | V68 vs V67, mean coin margin | V68 vs V56, mean coin margin |
|---|---:|---:|
| 94700 | +$3,719 | −$107,928 |
| 92802 | +$2,440 | −$92,023 |
| 92804 | −$2,657 | −$108,655 |
| Mean | **+$1,167** | **−$102,869** |

V68's V56 score averaged about $41,455; V56 averaged about $144,324. The V68/V56 margin did not change materially with seat order.

For seed 94700, accepted sales explain the gap. V68 sold 16 strawberries for $3,854, 36 milk for $6,224, 68 eggs for $3,588, 74 fertilizer for $4,915, and 174 wheat for $6,834. V56 sold 255 strawberries for $61,979, 185 milk for $33,216, 225 eggs for $11,873, 329 fertilizer for $22,996, and 426 wheat for $17,419. V68 sold more wool ($12,268 vs $9,348), but that did not offset its lower volume elsewhere. V68 also had no accepted tomato or carrot sales; V56 accepted $11,786 of those products. Total accepted sale value was about $49,628 for V68 and $185,570 for V56 in that match.

The action counts point to capacity and breadth, not a single berry-planning bug. On the seed-94700 V56 comparison, V68 issued 130 plant, 548 water, 225 harvest, and 0 fertilize unit actions, with 219 hire orders. V56 issued 249 plant, 1,184 water, 546 harvest, 149 fertilize, and 289 hire orders. These are submitted actions, not proof that every action succeeded, but they show the scale of V56's larger workforce and crop/animal portfolio. The four-plant plot can only add a few thousand dollars; it does not close a six-figure volume gap.

## Limits and next implication

This was a deliberately small portfolio intervention, not a reconstruction of V56. It did not add animal buildings or herd size: prior route economics show that each extra animal creates daily feed and care demand, and the small V68 workforce already produces far fewer milk and eggs than V56. A larger animal/crop expansion without a stronger staffing and routing design would repeat V67's conversion failure. The data support retiring this candidate as a promotion choice and treating multi-product throughput and labor routing as the next research target.

Candidate SHA-256: `11b977bf9dc5dd3b0f32363cfe78f22732a557142dea0df44939b3a42e23d1ca`.

# V75: how elite farms finance early scale

I reconstructed the cash path from six public winner replays sampled in the V63 top-lineage panel and four saved V70-vs-V56 replays (94700 in both seats, plus 92802 and 92804). I replayed each recorded action through the pinned Kaggle Kaggriculture 1.32.7 engine settlement. Across 10 seat-replays, reconstructed cash matched every recorded frame: 0 mismatches, maximum error $0. The policy hypothesis below uses only state-visible prices, shops, inventory, crops, herd and cash; no replay action tape is part of it.

The six selected winners finished day 12 with at least three lands, at least 32 strawberry plants, and 18–21 animals. Their public episodes are 113423918 (Fourth Quadrant), 113537919 (Azat Akhtyamov), 113664666 (Vadim Vasilenko), 113681377 (DSM), 113685931 (Unknown Mother-Goose), and 113696381 (Yizhou). Exact replay hashes and checkpoint reconstruction are in [`experiments/v75_elite_cashflow/reconstructed.json`](../experiments/v75_elite_cashflow/reconstructed.json); the reproducible settlement/checkpoint script is [`reconstruct.py`](../experiments/v75_elite_cashflow/reconstruct.py). Raw official replay sources remain in the V63 panel cache.

At end-of-day checkpoints, elite winners move from one land at day 3 to two by day 6 and three by day 9. By day 6 they have a median 12.5 animals and 24 strawberries, compared with V70's 5 animals and 1 strawberry. By day 9 they have 18 animals and 31.5 strawberries, compared with V70's 5 animals and 12 strawberries. Elite active hands are lower: medians are 8.5 at day 6, 9 at day 9, and 8 at day 12; V70 has 10, 9, and 10. The edge is productive asset mix, not a bigger crew.

| End-of-day checkpoint | Elite winner median cash | Lands | Animals | Strawberries | V70 median cash | Lands | Animals | Strawberries |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Start day 0 | $3,000 | 1 | 0 | 0 | $3,000 | 1 | 0 | 0 |
| Day 3 | $28 | 1 | 7 | 6 | $601 | 1 | 5 | 0 |
| Day 6 | $33 | 2 | 12.5 | 24 | $1,830 | 2 | 5 | 1 |
| Day 9 | $110 | 3 | 18 | 31.5 | $5,936 | 2 | 5 | 12 |
| Day 12 | $13,933 | 3 | 20 | 37.5 | $7,868 | 2 | 6 | 12 |

The striking pattern is temporary cash depletion followed by output conversion. During days 0–5, elite farms have median accepted sales of $3,644 in sales, spend $624 on products, $1,740 on seeds, and $3,900 on animals, with only $92 in inferred land/hire cost. Day-0–5 accepted sales are mostly fertilizer ($3,012 median) and wheat ($632); seed purchases include $900 strawberry, $680 melon, and $135 wheat. In the same period V70 accepts $2,590 in sales, buys $804 of products, $1,000 of seeds, and $2,300 of animals. Both policies start with $3,000 and end the period nearly broke, but elite farms have bought more productive animals and laid down more berry/melon cohorts.

| Days 6–11, accepted cash flow | Elite winner median | V70 median |
|---|---:|---:|
| Product sales | $26,430 | $11,573 |
| Product purchases (mainly feed) | $3,548 | $757 |
| Seed purchases | $3,115 | $1,450 |
| Animal purchases | $7,600 | $600 |
| Residual land/hire cost | $3,826 | $1,638 |
| Net cash change | +$10,726 | +$7,128 |

The sales timing identifies which day-0–6 assets repay those commitments. The elite group’s median accepted wool proceeds start at about $3,456 on day 6, milk sales begin around day 8 (roughly $2,500–$4,000 in most selected games), and melon sales arrive on day 10 (about $8,800–$9,000 in five of six winners). Day 10 median total sales are $9,634 and day 11 median total sales are $5,969. In the days 6–11 aggregate, the median sale mix is $11,236 melon, $5,114 fertilizer, $4,902 wool, and $4,486 milk. Elite winners therefore did not finance land with a static cash buffer: their planted day-0–2 melon crop and day-0 livestock began yielding before the day-10 sale wave, while later animal/seed purchases raised that stream. Strawberry sales are not yet the main day-6–11 source; strawberry stands prepare the following phase.

V70 diverges at the production layer: it remains at the opening 2-cow/3-sheep herd until a small goose purchase, grows only 12 strawberries by day 9, and never has the same early melon sales stream. Its day-6–11 median sales are fertilizer $2,478, wool $4,355, milk $3,318, and wheat $1,397; median melon sales are zero. V72's third land purchase alone did not replicate the winning sequence: its day-9 replay had 3 lands but only 12 berries and a single goose, so the new acreage lacked the livestock/crop cohorts already producing the winners' day-6-to-10 sales.

## State-derived macro hypothesis for testing

Use a **production-coupled tranche gate**, not a land-first rule. During days 0–5, keep the initial herd small enough to feed and care reliably, sell fertilizer/wheat for liquidity, and plant time-to-sale cohorts whose maturity falls inside the remaining horizon: early melon for the day-10 sale window and strawberry only when an observed buyer and quote support its later persistent yield. Expand at most one tranche at a time from day 6 onward. A tranche consists of a land purchase plus the needed seeds, productive herd/care capacity, and workers; do not buy land without the means to activate it.

At each observation, forecast next 4–5 days of saleable output from existing crop ages/yield units and animal readiness, cap it using live town inventory/shop demand and market price, subtract feed, seed, land and marginal-hire costs, and reserve enough for one day of feed and wages. Commit only if that forecast supports the tranche and current action capacity can reach harvest/care deadlines. Reforecast after the next accepted sales/cash observation. This directly targets the measured split: elites accept roughly $26k in days 6–11 sales after spending into assets; V70 accepts roughly $11.6k; V72 buys acreage without the corresponding sale-ready asset mix. This is a hypothesis from selected public matches, not a causal win guarantee.

The sample is purposive and outcome-conditioned; it is not a random tournament or controlled policy comparison. V70 controls are four saved spent-seed seat trajectories, not 4 independent random seeds. Medians of separate cost/sales categories do not sum to the median cash change. The settlement audit validates accepted transactions, not hidden intentions or whether a transaction was strategically profitable.

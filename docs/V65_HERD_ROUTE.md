# V65 early-herd route feasibility

## Decision

No-go before candidate construction or matches. I evaluated trading two early melon plots for two animal housing tiles and compared the resulting crop opportunity cost with the best price/shop-conditioned animal choices visible in the spent replays. The simple, no-care production case is negative after purchase, feed, and lost melon sales. The higher-output case requires a recurring worker route that has not been shown to fit without displacing feed/water coverage, and the opening budget cannot safely fund the two animals before the shop regime is visible. No code was created and no games or seeds were run.

## Observed opening states

The frozen-v57 candidate has SHA-256 `4173479fe1f80d031d570d1ea23b694dfe86e1d162317a4c9c7df0058a40208e`. I read only its existing saved candidate-side replays for losses 92802 vs v48 and 92804 vs v51, and win 92900 vs v48. At day 5 opening, each state has 19 crop tiles (12 melon, 7 wheat), six occupied pastures (4 cows and 2 sheep), $762, and three active hands. The one unlocked 5×5 quadrant is full. By day 6 the candidate has $937–$941, six animals, and 19 crop tiles.

Wheat tiles are not suitable trade targets: all animals need wheat feed every day, and the prior wheat-liquidation audit documented a feed-starvation failure. The two melon tiles are the lower-risk acreage trade because melon is a one-time crop and the observed early shops do not unlock melon-consuming shops in these opening states. They still have meaningful market value.

For the day 6–11 window, accepted candidate MELON sale value is $14,436 in seed 92802, $14,425 in 92804, and $15,995 in 92900. If two of the twelve day-6 melon plots contributed proportionally, the gross sale opportunity forgone is approximately $2,406, $2,404, and $2,666, respectively. This is an estimate, not a direct tile-level attribution: accepted product sales can include bought-and-resold stock, and the market price/capacity is endogenous. Removing those tiles would save seed and watering/harvest work, but the measured accepted-sale difference is not available from the saved replay without a counterfactual.

## Best gated animal economics from these replays

The observed shops at day 6 are `YARN_STORE` in 92802, `BRUNCH_SPOT` and `SMOOTHIE_SHOP` in 92804, and `ICE_CREAM_SHOP` in 92900. Thus sheep are the plausible extra animal in 92802; cows are the plausible milk-demand choice in 92804/92900. This gate cannot safely be used at the day-0 purchase point because these shops are not yet unlocked. At day 6, the candidate has less cash than the $1,000 needed for two sheep in 92802. Waiting until day 7 makes the shop observable and cash reaches $1,553, but delays production and further shortens payback.

I used the official Kaggriculture animal schedule as a deliberately simple base-yield benchmark: sheep cost $500 each, begin producing wool after 6 days and then every 3 days; cows cost $400 each, begin producing milk after 8 days and then every 2 days. Animals consume one wheat each per day. [Kaggriculture rules](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/README.md)

| Spent seed and gated choice | Earliest observed-shop purchase assumption | Base production through day 29 | Gross sales at observed mean price | Purchase + feed cost | Net before crop loss and worker actions |
|---|---|---:|---:|---:|---:|
| 92802, 2 sheep | Day 7, after Yarn is visible; 6 outputs each (12 total) | 12 wool | ~$2,788 at $232.3 mean wool price | $1,000 + ~$1,891 feed (46 wheat × $41.1) | **−$103** |
| 92804, 2 cows | Day 6; milk shops visible; 8 outputs each (16 total) | 16 milk | ~$1,755 at $109.7 mean milk price | $800 + ~$1,920 feed (48 wheat × $40.0) | **−$965** |
| 92900, 2 cows | Day 6; Ice Cream is visible; 8 outputs each (16 total) | 16 milk | ~$1,515 at $94.7 mean milk price | $800 + ~$2,059 feed (48 wheat × $42.9) | **−$1,344** |

After subtracting the estimated two-melon opportunity cost, these base-yield scenarios are roughly $2.5k–$4.0k negative before valuing additional route actions. The purchase costs use the published animal prices. Feed costs value 46–48 wheat units at each replay’s observed mean wheat price from day 6 through day 29; an actual intervention could buy at different prices or use farm-produced wheat, but that wheat then has its own sale/feed opportunity cost.

These are upper bounds on simple production cash, not guaranteed accepted proceeds. They assume every base-yield unit sells at the mean observed item price, with no price impact, competition, demand cap, animal loss, or added sales labor. Actual accepted wool sales from the existing two sheep are heterogeneous: $16,166 in 92802, $7,169 in 92804, and $4,191 in 92900 during days 6–11. This variation shows why extrapolating two additional animals linearly is unsafe; the extra units may increase accepted volume, depress price, or remain unsold. Care bonuses could raise production above the simple schedule, but only with additional actions.

## Route capacity

The two extra animals require two new buildings and two placements, in addition to purchase and feed inventory. The frozen day-0–5 route already builds six pastures, places six animals, plants the 19 crop tiles, and has a repeated feeding/care schedule. Trading two melons frees at most two daily watering actions while those plants would otherwise be maintained, plus two one-time harvest actions. It does not provide a persistent route for 2 animals × (daily feed + daily care): that is 4 animal actions per day, or about 92–96 recurring actions over the post-purchase horizon before movement, pickup, placement, or shed transfers. The current route has no scheduled extra housing/placement windows, and the saving from removing two one-time melons ends once they would have been harvested.

The existing replay records show baseline accepted net sales, not the counterfactual prices or quantities after doubling livestock output. Without a route that preserves the existing crops' water schedule and reserves wheat for the whole herd, the cash calculation is optimistic and insufficient to justify the added animals. No safe `BUY_ANIMAL`-only change was attempted.

## Provenance and limits

The public top-ten sample in V63 shows an association between day-6 herd size and later cash flow; it does not identify a treatment effect. This audit used the frozen v57 route as its only policy source and did not copy any third-party replay actions. The frozen source itself states that its farm route was adapted from the public Lizs replay and remains under the existing internal-research/source-rights boundary. Its hash is unchanged. The prior broad V58 expansion screen also failed across historical opponents, so this animal-only trade cannot be treated as a general substitute for expansion.

The economics omit care bonuses, downstream product-price changes, labor opportunity cost, and stochastic shop/market effects. They establish that a narrow route-preserving early-herd intervention is not currently supported; a new worker planner or controlled market simulation would be needed to assess more ambitious alternatives. No candidate was built, no matches were run, and no new seed was consumed.

## Inputs

- [`V63_ELITE_PANEL.md`](V63_ELITE_PANEL.md) and [`V63_LOCAL_CONTROL.md`](V63_LOCAL_CONTROL.md): descriptive public association and saved local controls.
- [`V58_EXPANSION.md`](V58_EXPANSION.md) and [`V58_WHEAT_FAILURE.md`](V58_WHEAT_FAILURE.md): broader expansion results and wheat-reserve failure.
- Seed 92802 replay: `experiments/v58_diagnostics/replays/v48-seed-92802-ab-repeat-0.json`.
- Seed 92804 replay: `experiments/v58_diagnostics/replays/v51-seed-92804-ab-repeat-0.json`.
- Seed 92900 replay: `experiments/v58_policy/baseline_vs_v48/replays/v48-seed-92900-ab-repeat-0.json`.
- Reconciled local accepted transactions: `experiments/v63_local_control/players.csv`.

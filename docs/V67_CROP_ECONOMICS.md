# V67 crop economics and expansion gate

## Result from the spent-seed replay

V67's expansion did not improve cash conversion. The exact-loader seed-94700 pair lost both seats to V66. Reconstructing accepted market transactions with the installed Kaggriculture **1.32.7** engine reconciles cash exactly; the two orientation gaps are:

| Seat order | V67 sales | V66 sales | V67 product buys | V66 product buys | V67 seed buys | V66 seed buys | Extra land + hire cost | Closing V67−V66 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| V67 seat 0 | $54,099 | $56,794 | $4,350 | $5,960 | $6,500 | $2,270 | $9,712 | **−$15,027** |
| V67 seat 1 | $56,160 | $57,637 | $4,502 | $5,959 | $6,230 | $2,270 | $9,712 | **−$13,692** |

The cash identity is `sales difference − product-buy difference − seed-buy difference − extra land/hire cost`. For the first order this is `−2,695 + 1,610 − 4,230 − 9,712 = −15,027`; the reversed order gives `−1,477 + 1,457 − 3,960 − 9,712 = −13,692`. V67 saved some feed purchases and sold more wheat, but its total sales fell. Wheat receipts rose by $3,719–$4,342 while melon receipts fell by $5,192–$6,041. It spent $7,000 on three land unlocks and about $2,712 more on accepted hires than V66.

The expansion had a large task cost without comparable harvest throughput. Across the two runs, V67 issued 169–174 plant commands and 572–600 water commands, versus V66's 73 and 337. V67 added only 17–35 harvest commands, hired 279–280 times versus 148, and made three land purchases. That is a queue conversion failure: planting and watering the extra acreage consumed turns and cash, while market receipts did not rise. The second-quadrant crop mix is particularly telling: extra wheat cash did not replace the melon cash displaced by the expanded wheat/melon route.

## One-plot return screen at day 6, 9, and 12

This table estimates one additional crop tile on an already-bought second quadrant. The calculator schedules complete harvests through day 29, prices the crop against the actual market inventory path from the seed-94700 V67-vs-V66 replay, and shifts inventory by the added tile's preceding sales using the engine's exact `market_price` curve. It allocates the $1,000 first-land price over 25 productive crop tiles ($40 per tile). “Net” subtracts crop seeds and that land share; the last column also subtracts a conservative $1.83 per explicit worker task turn, the largest V67 daily hire wage per added action-capacity unit. It still excludes movement and task conflicts.

| Plant day | Crop | Units / last harvest | Projected sale cash | Seed cost | Market impact from this tile | Task turns: plant + water + harvest | Net after seed, $40 land share, and direct wage |
|---:|---|---:|---:|---:|---:|---:|---:|
| 6 | Wheat | 20 / day 26 | $792 | $50 | −$8 | 30 | $647 |
| 6 | Melon | 10 / day 24 | $2,254 | $160 | −$46 | 18 | $2,021 |
| 6 | Strawberry | 4 / day 22 | $916 | $100 | −$3 | 14 | $750 |
| 6 | Tomato | 8 / day 28 | $2,011 | $100 | −$57 | 16 | $1,842 |
| 9 | Wheat | 20 / day 29 | $836 | $50 | −$8 | 30 | $691 |
| 9 | Melon | 5 / day 18 | $1,162 | $80 | −$8 | 9 | $1,026 |
| 9 | Strawberry | 4 / day 25 | $992 | $100 | −$1 | 14 | $826 |
| 9 | Tomato | 4 / day 20 | $478 | $50 | −$6 | 8 | $373 |
| 12 | Wheat | 16 / day 28 | $680 | $40 | $0 | 24 | $556 |
| 12 | Melon | 5 / day 21 | $1,140 | $80 | −$10 | 9 | $1,004 |
| 12 | Strawberry | 4 / day 28 | $1,067 | $100 | −$1 | 14 | $901 |
| 12 | Tomato | 4 / day 23 | $788 | $50 | −$8 | 8 | $683 |

The **unit crop** return screen is positive across these observed states, so the replay loss does not justify rejecting every new plot. It rejects automatic whole-quadrant planting: the realized batch failed to keep the per-plot water/harvest schedule feasible, and the $7,000 land plus recurring hires and excess seed purchases were committed before the extra plants converted into sale cash. Tomato's day-6 estimate is especially fragile: it benefits from a late-game price spike while the replay produced no tomatoes. A one-tile price effect is small, but scaling its 8 units to an entire field can erase that scarcity price.

The explicit task schedules used by the calculator are engine-grounded: wheat produces four units in a four-day crop window (6 explicit actions per cycle); the V67 melon harvester accepts a five-unit yield (9 actions per cycle); tomato is held for four daily yields (8 actions); and strawberry is harvested on four two-day pulses (14 actions using V67's harvest-as-ready behavior). The game costs no cash to press WATER or HARVEST; their cost is labor capacity. V67's added-hire cash rate is roughly $0.58, $0.79, and $1.83 per potential action turn at 8, 9, and 10 hands, respectively, relative to the proven five-hand baseline. The calculator charges the highest of those rates to every turn, but a full labor value must also include travel and the higher-value task displaced.

### Observed price and demand path

| Day | Wheat | Melon | Strawberry | Tomato | Unlocked shops |
|---:|---:|---:|---:|---:|---|
| 6 | $31 | $268 | $144 | $63 | Pizza Shop, Farmers Market |
| 9 | $33 | $271 | $165 | $68 | + a second Pizza Shop |
| 12 | $36 | $240 | $180 | $75 | + Smoothie Shop |
| 20 | $41 | $232 | $235 | $121 | + second Smoothie Shop, Yarn Store |
| 29 | $47 | $209 | $289 | $488 | + Brunch Spot, third Pizza Shop |

Pizza and Farmers Market consume wheat and tomato; Farmers Market consumes strawberry; Smoothie and later Brunch provide more strawberry demand. Melon has no town-shop buyer in this sequence and fell from $271 on day 9 to $209 at the end. Price movement is nonlinear: a plot's added units have a small marginal effect in the table, while 10–20 crop plots can sharply move the market. The day-6 tomato estimate relies on future prices from this exact seed and is not a safe day-6 forecast.

The 50-game top-line panel supports a selective test rather than a fixed-acreage rule: winners had fewer median crop tiles than losers on days 6, 12, and 20. Strawberry and wheat showed positive paired winner-minus-loser net product cash in that panel, while tomato and carrot were negative; these are descriptive correlations, not crop treatment effects.

## Cash-positive expansion gate

For an incremental crop tile, use a rolling estimate:

`margin = accepted-sale forecast + avoided feed purchases − seed cost − land share − marginal hire cash − λ × (plant + water + harvest + movement turns)`

Price the next `q` sale units with the engine curve at projected market inventory after current town-shop consumption and the crop's own prior sales. For wheat, credit the smaller of projected wheat yield and forecast feed shortage as avoided `BUY_PRODUCT` cost; do not count the same units again as sale revenue. Estimate crop output from the actual growth/decay calendar and require each harvest deadline to fit before day 29. Set `λ` to the marginal cash contribution of the best baseline task displaced in the current state, not zero.

Buy one land quadrant only when the positive-margin crop batch planned for that land covers the full $1,000/$2,000/$4,000 purchase and the expected added daily-hire bill, with feed and seed reserve left over. Initially cap the trial batch to one or two plots, observe whether they reach harvest and accepted sale, then update price and labor forecasts before planting more. Prioritize wheat only for a projected feed deficit; consider strawberry where an unlocked Farmers Market, Smoothie, Brunch, or Ice Cream shop supports its delayed harvest; consider tomato only when its market scarcity remains after adding the candidate quantity. Do not fill unassigned cells with melon solely because its spot quote is high: no shop buys it in this path and its market curve penalizes added supply strongly.

## Reproducibility and limits

The calculator and compact output are [`crop_roi.py`](../experiments/v67_economics/crop_roi.py) and [`crop_roi.json`](../experiments/v67_economics/crop_roi.json). Inputs are the two local spent-seed-94700 replays: V67-vs-V66 AB SHA-256 `b0be19d72af0ce25ef0cbc7c5d45de61a38078e33961a4ad27ce17db0c680943` and BA SHA-256 `4aa53508177ec1f156b9958d259c1be345625d897c1ffa3b30b6bbc55d2b5b35`; both report module `1.32.7`. Raw local replay files remain ignored.

The cash reconciliation uses both seats from one spent seed, so it explains this failure but does not establish broad win rates. The per-plot ROI uses one replay's realized future price/inventory path as a counterfactual baseline, assumes each crop task completes on schedule, amortizes land across 25 productive tiles, and omits movement and displaced work. Treat it as a screen for which crop to test; the margin and cash-reserve gate must be tested on held-out seeds before promotion.

# V66 implementation audit

## Scope and evidence

Read-only audit of the uploaded V66 source at `experiments/submission_candidate_20260926/bundle/main.py`, the archived spent-seed exact-loader replay `experiments/submission_candidate_20260926/spent94700_v56/replays/v56-seed-94700-ab-repeat-0.json`, its game summary, and the exact Kaggle Environments engine at `.venv/lib/python3.12/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py`. No new games were run and no agent code was changed. The archived head-to-head is one spent seed in both seat orders, so it diagnoses mechanism and scale, not general win probability.

## Decisive structural defect: no land purchase or expansion plan

The production entry point calls `_bridge_agent` every turn. Its market function `_bridge_market` never appends `BUY_LAND` (lines 725–807). Its geometry helper explicitly chooses only `unlocked[0]` and makes a 5-pasture / 10-wheat / 10-melon footprint inside that one quadrant (lines 81–128). `_bridge_agent` continues to use those same returned coordinates even if later quadrants are unlocked (line 834 and subsequent fixed `wheat_tiles` / `melon_tiles` task generation). This means that adding land purchases alone would still leave new land unused for crops and livestock.

In the archived replay, V66 stayed at `unlocked_quadrants=['NW']` through day 12 and made zero land purchases for the whole game. The engine sets `LAND_ORDER=['NE','SW','SE']` and `LAND_PRICES=[1000,2000,4000]` (engine lines 96–97); its `_do_buy_land` performs an unlock when it receives the order and the cash is available (lines 713–722). V66 already held $1,133 at the end of day 5 and $4,320 at the end of day 6, yet no unlock occurred. The paired V56 opponent bought land three times.

Other expansion assumptions are also hard-coded: `_empty_structures` only scans `x,y` in `range(5)` (V66 lines 652–659), and animal and crop tasks use fixed coordinate tuples. A dynamic expansion patch must update structure discovery and task zones together or it will fail to place or service assets outside the first 5×5 quadrant.

V66's farm held $53 after day 0, $403 after day 4, $6,219 after day 8, and $15,115 after day 12. Its standing board on day 12 held 6 wheat and 6 melon plants, 2 cows, 3 sheep, and 2 geese. It ended at $44,930 against V56's $129,477 on this spent seed. The candidate's initial crop/animal targets fit one quadrant; they do not capitalize on the season's cash to expand production capacity.

## Throughput defect: a fixed five-hand ceiling with high travel overhead

`OPENING_HANDS_TARGET=4` and `BRIDGE_HANDS_TARGET=5` (lines 38–39) fix the roster at four hands during days 0–1 and five thereafter. `_bridge_market` restores only that target each day (lines 745–749), regardless of the number or distance of pending tasks. The planner processes one action per unit per hour and assigns all open tasks from scratch each turn (lines 1098 onward), so a fixed roster cannot scale when new territory and crops are added.

The same archived replay's action counters show 148 V66 hire orders over the season (roughly five per day) versus 289 for V56. V66 made 1,400 non-movement unit actions and 2,530 movement actions; V56 made 3,680 non-movement actions and 3,121 movement actions. Thus V66 made only 38% as many work actions while making 81% as many moves. V66 submitted 132 sell orders versus V56's 309. These counts support a labor and routing bottleneck: adding area without scaling staff and task throughput would worsen the current mismatch.

## Opening cash and day 0–12 behavior

The day-0 market sequence is close to all-in: four hire orders, two animal-buy orders, and four seed-buy orders leave only $53. The four seed orders include the initial melon and wheat seed purchases; animals are placed by the end of the day. From day 1 onward the market repeatedly funds feed and seed purchases as products are collected and sold. That lets cash turn positive, but the V66 market planner has no investment step: it never converts the observed day-5/day-6 cash into the $1,000 first land unlock.

The source's animal and crop task rules are explicit and state-aware, and the replay does not show a runtime failure. The dominant observable loss is insufficient productive scale, not an exception. V66 completes the season and its final balance is positive, but it generates less than half V56's ending cash in this head-to-head.

## V67 implementation implications

A correction needs both parts of expansion: a cash-gated `BUY_LAND` schedule using the engine's order and prices, plus live geometry/task generation that assigns newly unlocked tiles to crop or animal production. It also needs worker count to follow service backlog and cash capacity rather than stopping at five hands; use the existing fed/cared/watered/harvest task counts and distances to estimate required daily actions. Preserve feed, care, harvest, and planting-day watering while expanding. Because `maxMarketOrdersPerTurn` is 10 (engine market processing slices each submitted queue to this limit at lines 544–555), explicitly cap the market queue and reserve slots for feed and seed orders when increasing hires or selling several products.

For the next spent-replay validation, report by day: unlocked quadrants and occupied tiles; hand count; actions spent moving versus feeding/caring/watering/harvesting/planting; market order count and rejected/truncated intentions; cash after settlement; crop output and animal count. Verify that land is bought once cash can afford it, newly unlocked tiles become productive, and worker growth improves completed work rather than movement alone. Fresh benchmark seeds remain necessary before making any win-rate claim.

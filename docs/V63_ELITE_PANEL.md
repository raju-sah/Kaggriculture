# V63 public elite replay panel

## Scope and selection

I sampled 50 distinct public Kaggriculture episodes from the current top-ten leaderboard lineages as of 2026-09-26: five episodes for each of Boey, DSM, Fourth Quadrant, M & M & P & Q, Vadim Vasilenko, DECEM, Majkel1337, Unknown Mother-Goose, Azat Akhtyamov, and Yizhou. For each lineage I used the highest public score among its latest two public submissions, then sampled episodes at spaced positions through the recent portion of that submission’s episode list. The games were created 2026-09-24 through 2026-09-26; this yielded 50 unique seeds. Every game contributes both its winner and loser, so the outcome comparison is paired within the same market, shops, seed, and replay. No V62 episode was reused.

The episode and submission IDs, leaderboard lineage, scores, dates, seeds, participant names, rewards, configuration, engine version, replay SHA-256, and Kaggle CLI source commands are in [`episode_manifest.json`](../experiments/v63_elite_panel/episode_manifest.json). Kaggle's public CLI/API supplied the data (`team-submissions`, `episodes`, and `replay` commands). All 50 replays identify engine module version `1.32.7`.

The selection is balanced across the ten leaderboard lineages and includes a winner/loser pair per episode. It was not randomized and was not explicitly quota-sampled by shop category. Shop exposure was nevertheless diverse: the unique unlocked-shop sets numbered 25 at day 6, 44 at day 12, and 45 at day 20. Most individual sets therefore have too few games for reliable regime-specific comparisons. Episode-level shop lists and market prices are retained in the participant table for follow-up conditioning.

## Settlement and measures

The replay stores an action with the resulting frame. I therefore replayed `steps[t][seat].action` from `steps[t-1][seat].observation` and compared simulated cash with `steps[t][seat].observation`. For each transition the script uses the matching Kaggriculture engine to apply unit actions and market settlement, and records only accepted transactions. Across 50 games this checked 71,900 seat-transitions with **zero cash mismatches** and a maximum discrepancy of `$0.00`.

Snapshots are taken at day 0, and at `day * 24 + 1` for days 6, 12, 20, and 29. The one-step offset avoids the engine’s hour-zero transition where the active `hands` list is temporarily empty. Reported land is the number of unlocked quadrants; crop plots and animals are counts of occupied farm tiles. Day-20 shed value is marked at the observed market price, not guaranteed sale proceeds.

“Net product market cash” means accepted product sale value minus accepted `BUY_PRODUCT` value. It does not subtract seed/animal investment, worker/land costs, or value any unsold stock. The phase tables retain those other accepted purchases and inferred land/hire cash separately. Thus this measure isolates gross cash through product transactions; it is not crop profit and cannot distinguish a produced sale from purchase-and-resale by itself. These caveats are especially relevant to wheat and fertilizer, which can be bought as well as sold.

## Paired findings

| Observation | Winner median | Loser median | Median within-game winner difference | Winner leads in paired games |
|---|---:|---:|---:|---:|
| Day 6 cash | $279 | $674 | −$174 | 14/50 |
| Day 6 active hands | 9 | 8 | 0 | 22/50 |
| Day 6 animals | 8 | 5 | +1.5 | 27/50 |
| Day 6 crop tiles | 17 | 20 | −3 | 14/50 |
| Day 12 cash | $11,053 | $9,090 | +$1,617 | 28/50 |
| Day 12 active hands | 8 | 8 | 0 | 17/50 |
| Day 12 crop tiles | 57 | 60.5 | −3.5 | 23/50 |
| Day 20 cash | $59,241 | $54,945 | +$5,046 | 37/50 |
| Day 20 shed value at current prices | $3,506 | $3,722 | +$99 paired median | 27/50 |
| Day 29 hour 1 cash | $99,693 | $94,180 | +$4,778 | 46/50 |
| Closing cash (day 29, hour 23) | $105,479 | $99,712 | +$5,767 | 50/50 |
| Closing shed value at current prices | $0 | $0 | $0 paired median | 14/50 |

The median final score gap was `$4,864.50`; 15 of 50 games ended with a gap greater than `$10,000` (maximum `$34,291`). The winner’s cash advantage generally emerged after day 6: median paired differences in cash change were `−$173` for days 0–5, `+$1,010` for days 6–11, `+$4,606` for days 12–23, and `+$1,597` for days 24–29. The day 12–23 cash-flow advantage appeared in 33/50 games. At the final hour, every winner had more cash than its paired loser; both groups had zero median shed value at current prices, so winners were not finishing with a larger typical stockpile.

The cash turn is not accompanied by a broad acreage lead. Winners had fewer crop tiles at the day 6, 12, 20, and day-29-hour-1 medians; by day 12 active hands were tied at eight, the paired day-20 shed mark-to-market difference was close to zero, and both groups had zero median shed value at close. This panel therefore does not support “add more plots/workers” or “hold more inventory” as a general explanation for these wins.

Accepted sales rose more than product inputs during the productive midgame. Winner-minus-loser paired medians for days 12–23 were `+$4,328` in accepted product sales and `−$145` in direct product purchases, for `+$3,438` in net product-market cash. In the late phase, sales were `+$2,598`, product purchases tied at zero median difference, and net product-market cash was `+$1,524`. During days 6–11, the sales difference was `+$1,579` but winners also spent `+$801` more on product purchases, leaving only `+$156` median net product-market advantage. The larger midgame cash turn is consequently the clearest common timing pattern.

Across the whole game, the paired median winner-minus-loser difference in net product-market cash was `$8,258`, and winners had the higher value in 39/50 games. Item differences were heterogeneous: milk `+$2,184` (37/50 games), strawberry `+$1,576` (33/50), wheat `+$1,120` (32/50), egg `+$985` (28/47), and fertilizer `+$334` (27/50). Carrot and tomato differences were negative (`−$814` and `−$1,157`); these patterns are descriptive and may reflect the market, shop path, agent lineage, and item-price distribution rather than item-level profitability. Per-product net figures subtract only direct purchases of that same product, not its production costs.

## State-conditioned lead to test

A useful **hypothesis**, not an established causal effect, is that an early productive-herd investment can explain some of the delayed cash conversion. Winners spent a median `$400` more than losers on accepted animal purchases during days 0–5, finished day 6 with a median 1.5-animal lead while holding `$174` less cash, then had a median `$1,010` cash-flow advantage during days 6–11. In this selected panel, the winner had more animals at day 6 in 27 games and fewer in 8; where the winner had the animal lead, its median day 6–11 cash-flow advantage was `$6,068`, compared with `−$1,433` when day-6 herd counts tied and `−$2,467` when the winner had fewer animals. The paired Spearman association between day-6 animal-count difference and day 6–11 cash-flow difference was `0.60` (`n=50`).

This suggests a testable state-time decision for our agent: during days 0–5, buy an additional animal only when the observed purchase cost, remaining production horizon, available feed/care actions, pasture or coop capacity, and current market/shop prices imply positive expected net cash after upkeep; then check whether the day-6 herd yields enough accepted sales to recover that investment over days 6–11. The policy should use an expected-payback gate, not copy a fixed herd count or replay actions. The comparison should be seed-balanced and stratified by animal type, shop unlocks, feed price, and opponent lineage. The observed pattern may be entirely lineage-driven, and the outcome-conditioned subgroup is not a treatment effect.

A second state-based policy to test is horizon-aware late liquidation: once remaining days are too few to use an item productively, sell suitable excess shed stock when current prices and market capacity make the sale worthwhile. In days 24–29, winners’ median product sales exceeded losers’ by `$2,598`, while median product purchases tied at zero; yet this was only a `$1,597` cash-flow advantage and was not the whole final gap. Since median closing shed value is zero on both sides, the panel does not prove that unsold surplus caused losses.

A practical instrumentation lead is to expose per-product cash flow as `accepted sale proceeds − accepted product purchases`, separately from seed, animal, land, and hire expenses. Gross sales alone can be misleading when agents buy inventory to resell it; the V62 Boey/DSM target replay is an example. At decision time, a policy could limit product purchases to planned production/processing needs with forecast positive contribution margin, but this panel alone does not justify any hard threshold.

## Confounding and limits

These are public self-play/competition episodes, not controlled policy experiments. Every selected lineage contributes five games, and top-ten bots also appear as opponents; the same submission may share code ancestry with other top entries. Pairing controls the common episode’s seed, market and shop path, but does not identify which action caused a result. The 50 unique seeds avoid duplicate seed observations in this sample but do not remove lineage, opponent-pool, or submission-selection bias. Price and shop categories are high-dimensional and sparsely represented, so the per-item and phase results should guide experiments rather than become fixed rules. Public accepted transaction reconstruction is verified for module `1.32.7`; that does not establish that another agent’s hidden intent was to produce, store, or resell an item.

## Artifacts

- [`players.csv`](../experiments/v63_elite_panel/players.csv): one row per participant per episode, with outcomes, phase cash/transactions, day 0/6/12/20/29 state, observed shop sets and prices, and replay hash.
- [`games.csv`](../experiments/v63_elite_panel/games.csv): episode-level winner/loser pairing, seed, lineage, gap, and audit counts.
- [`summary.json`](../experiments/v63_elite_panel/summary.json) and [`descriptive_details.json`](../experiments/v63_elite_panel/descriptive_details.json): compact aggregate statistics.
- [`accepted_sales.json`](../experiments/v63_elite_panel/accepted_sales.json): compact exact accepted-transaction summaries and reconciliation audit per episode; per-step transaction tapes are omitted.
- [`profiles.json`](../experiments/v63_elite_panel/profiles.json): compact action and state profiles.
- [`accepted_sales.py`](../experiments/v63_elite_panel/accepted_sales.py), [`profile_replays.py`](../experiments/v63_elite_panel/profile_replays.py), and [`analyze_panel.py`](../experiments/v63_elite_panel/analyze_panel.py): reproducible local analysis scripts. Raw replay blobs remain local and gitignored; `episode_manifest.json` preserves SHA-256 hashes and replay download commands.

For the one-game, exact product-by-step reconciliation and the `$3,005` DSM-vs-Boey result, see [`V62 elite-game research`](V62_ELITE_GAME_RESEARCH.md).

# V63 local-control replay panel

## Result

No recurring, controllable gap above $10,000 is supported by the existing frozen-v57 reset replays. The clearest elite-panel early-state association is herd size: elite winners have median 8 animals at day 6 versus 5 for losers, with 9 versus 8 hands. The reset candidate has exactly 6 animals, 7 hands, 19 crop tiles, one quadrant, and median $938 cash at day 6 in both its winning and losing rows. Its day6–11 accepted animal spend is $3,700 in wins and $3,900 in losses. That does not identify a successful animal-purchase intervention; the state has no local outcome separation and additional animals could displace planting or hiring.

The paired reset-minus-opponent comparison also does not reveal a large general market throughput deficit: median terminal reward margin is +$468, median net product-market margin +$4,776, and wheat-plus-fertilizer net margin +$690. The reset candidate's day12–23 net product market flow is the one consistent soft spot against the public elite panel (medians $62,145 local vs $69,011 elite, a $6,866 gap), but local late-phase flow is $39,997 vs $31,930 (+$8,067), and whole-run net product market is $132,065 vs $125,854 (+$6,211). These are descriptive distributions from different opponent pools, not paired treatment effects. The phase dip is below the requested $10k scale and is offset later.

| Metric | Reset candidate | Elite public panel |
|---|---:|---:|
| Day 6 animals, winner / loser median | 6 / 6 | 8 / 5 |
| Day 6 hands, winner / loser median | 7 / 7 | 9 / 8 |
| Day 6–11 cash flow, winner / loser median | $16,420 / $15,516 | $10,322 / $7,216 |
| Day 6–11 accepted net product flow, winner / loser median | $27,072 / $26,329 | $22,450 / $22,415 |
| Whole-run net product flow median | $132,065 | $125,854 |
| Day 12–23 net product flow median | $62,145 | $69,011 |
| Late net product flow median | $39,997 | $31,930 |

Winner/loser rows in the local column refer to frozen reset-candidate results in the sampled diagnostics. Elite values use all 50 winner and 50 loser participants in the separate public panel. In the reset sample, shop-stratified day-6 snapshots also remain fixed at six animals: day-6 shop-mix groups have 8 `BOTH` rows (4 seeds), 34 milk-shop-only rows (19 seeds), 6 yarn-only rows (3 seeds), and 10 neither rows (5 seeds). The `BOTH` group has 0 wins of 8; the other small groups vary, so these small purposive strata do not establish a shop-conditioned livestock effect. By day 12, all sampled reset rows have at least one milk-consuming shop unlocked; shop-regime medians are 17 animals and 53 crop tiles, with day12–23 net flow between $60,046 and $62,450 across the overlapping milk/yarn categories.

## Method and provenance

The local panel contains 58 saved frozen-reset games from 31 distinct seeds and 11 opponent lineages. It uses only the frozen reset candidate SHA-256 `4173479fe1f80d031d570d1ea23b694dfe86e1d162317a4c9c7df0058a40208e`; one matchup was selected per seed, retaining seat-swapped outcomes when present. The source replays are purposively selected diagnostics, not a fresh or random tournament. No games were run for this study.

Accepted settlements follow the V62 elite-panel one-frame alignment: for each frame `t=1..N-1`, apply the action recorded at current frame `t` to copies of the prior frame's observations, run `_apply_unit_action` and `_process_market`, and capture accepted transactions at `_commit_unit`. The procedure reconciles cash after every transition. All 83,404 aligned transitions across 58 games have zero cash mismatches (Kaggle environment 1.32.7). Snapshot observations use step 0 for day 0 and step `day*24+1` for days 6, 12, 20, and 29, avoiding the transient empty-hands hour-0 state.

The public comparator is `experiments/v63_elite_panel/players.csv`: 100 participant rows from 50 episodes, 10 leaderboard lineages, 71,900 reconciled transitions. Its game pool and opponents differ from local diagnostics, so comparisons support screening for large repeated divergences, not causal claims. All dollar quantities are accepted transaction values; land/hire cost is kept in its separate residual category.

## Reproducible artifacts

- [`build_panel.py`](../experiments/v63_local_control/build_panel.py) selects and reconciles saved replays.
- [`analyze_panel.py`](../experiments/v63_local_control/analyze_panel.py) computes seed-balanced and shop-stratified summaries.
- [`summary.json`](../experiments/v63_local_control/summary.json) contains full quantiles, phase flows, product metrics, shop strata, and provenance.
- [`players.csv`](../experiments/v63_local_control/players.csv) and [`games.csv`](../experiments/v63_local_control/games.csv) contain row-level outputs; matching JSON exports and a source manifest are alongside them.

# V83: what actually separates elite winners — mechanism analysis

Read-only. No agent code edited, no new seeds, no submission. Evidence: 100 elite player-games
(`experiments/v63_elite_panel/players.csv`, exact 1.32.7 settlement, `audit_max_cash_error` 0.0 on all
100) plus four freshly downloaded leaderboard replays pulled with the Kaggle CLI
(`experiments/top_replays` corpus; episodes 113928363, 113933108, 113985943, 113985944, top-10
finishes at ~2,875–3,084).

This report exists to record **what the elite evidence does and does not support**, because two
earlier branches (V80, V81) were built on a reading of a single matchup that turned out to be wrong.

## Headline: the wool thesis is refuted, and so is "volume"

Earlier work (V80/V81) treated a 46,937-coin wool gap on spent seed 92802, V57-reset versus local
v50, as the central defect. The elite corpus says that reading was wrong on every axis.

**Composition is not the separator.** Day-12 herd composition, winners versus losers:

| | COW | GOOSE | SHEEP |
|---|---:|---:|---:|
| Winners | 9.02 | 5.24 | 5.52 |
| Losers | 8.98 | 5.24 | 5.42 |

Goose share of herd: **26.4% win, 26.3% lose**. Sheep share: **27.4% win, 27.6% lose**. Elite winners
are goose-heavy, and if anything finish the season with *fewer* sheep than losers (day 29: 0.88 vs
1.38) — they convert wool rather than hoard it. A sheep-for-goose substitution is not the lever.

**Volume is not the separator either.** In the four fresh replays, during days 12–23 the losing side
sold **more** units than the winning side (mean 3,113 vs 2,997) and still finished lower. Elite
agents that appear to sell "9,102 units" are filling all ten `maxMarketOrdersPerTurn` slots with
repeat orders; those inflated counts are an artifact of counting queue slots, not sales. Any
analysis that counts market order *slots* rather than accepted units is measuring nothing.

## What the separator actually is: throughput per unit of asset, and contribution margin

Asset levels are near-identical between winners and losers. What differs is how much each asset
converts into cash.

| Metric (days 12–23) | Winners | Losers | Ratio |
|---|---:|---:|---:|
| Animals at day 12 | 19.8 | 19.6 | 1.01x |
| Crop tiles at day 12 | 62.2 | 60.8 | 1.02x |
| Unlocked quadrants | 3.48 | 3.48 | 1.00x |
| **Sales per animal** | **4,233** | **3,681** | **1.15x** |
| **Sales per crop tile** | **1,346** | **1,189** | **1.13x** |

Identical inputs, ~14% more output. That is the entire edge, and it is an *execution* difference, not
a composition or scale difference.

**Contribution margin runs the other way from what intuition suggests.** Winners convert sales to
cash *less* efficiently per sale:

| | Winners | Losers |
|---|---:|---:|
| Total sales | 156,423 | 136,481 |
| Net product market | 132,360 | 124,703 |
| **net / sales** | **0.846** | **0.914** |
| Product purchases | 24,064 | 11,778 |
| Land + hire cost | 10,975 | 10,968 |

Winners buy **2.04x** more product and spend the same on land and hires, and still finish ~7,900
ahead. The extra spend is overwhelmingly **wheat (18,043 vs 10,006, 1.80x) and fertilizer
(6,020 vs 1,772, 3.40x)** — that is feed and soil inputs, i.e. capital deliberately pushed into
production rather than left as idle bank.

## The clearest single behavioral signal: winners commit capital early and are *poorer* for it

| Metric | Winners | Losers | Effect size |
|---|---:|---:|---:|
| Day-6 cash | **361** | **594** | 0.78 sd |
| Opening (d0–5) animal purchases | 3,430 | 2,782 | 0.77 sd |
| Opening product purchases | 2,657 | 1,327 | 0.39 sd |
| Day-6 animals | 8 | 6 | 0.76 sd |
| Day-6 crop tiles | 17 | 18 | 0.59 sd |
| Total sales | 156,423 | 136,481 | 0.56 sd |

The strongest single separator in the entire corpus is that **winners hold less cash at day 6** —
they end the opening window nearly broke because they converted bank into animals and soil. The
losers are the ones sitting on unspent cash at day 6. This is the opposite of a "preserve liquidity"
instinct, and it is the one early-game signal with an effect size above 0.7 sd.

## Where the margin is made, by phase

| Phase | Winners net | Losers net | Difference | Share of winner total |
|---|---:|---:|---:|---:|
| Days 0–5 | 2,662 | 2,368 | +293 | 2.0% |
| Days 6–11 | 22,993 | 22,054 | +939 | 17.4% |
| **Days 12–23** | **73,437** | **68,054** | **+5,383** | **55.5%** |
| Days 24–29 | 33,269 | 32,227 | +1,042 | 25.1% |
| **Total** | **132,360** | **124,703** | **+7,657** | — |

More than half the entire difference accrues in days 12–23, the phase after the third land unlocks
and before the terminal liquidation. That phase is where a throughput intervention would have to act.

Net contribution by product (accepted sell minus accepted buy) confirms there is no single-product
exploit to copy — the gain is spread across almost every line:

| Product | Winners | Losers | Difference |
|---|---:|---:|---:|
| MILK | 25,095 | 22,442 | +2,652 |
| STRAWBERRY | 31,501 | 29,091 | +2,410 |
| WOOL | 18,029 | 16,538 | +1,491 |
| WHEAT | 11,852 | 10,415 | +1,436 |
| FERTILIZER | 12,753 | 12,017 | +736 |
| EGG | 8,168 | 7,598 | +570 |
| MELON | 14,354 | 13,791 | +563 |
| CARROT | 6,843 | 7,138 | −295 |
| TOMATO | 3,764 | 5,673 | **−1,908** |

Every product is positive except tomato, which losers do *better* on. A "buy more sheep" or "sell
more wool" rule cannot produce this pattern; only uniformly higher asset utilization can.

## Action-level observations from the four fresh replays

- **Idle rate is low and is not the separator.** Elite agents run 2–5% PASS across hand slots. In the
  four games the winners were not systematically busier than the losers; a "keep workers busy" rule
  has no support here.
- **Land count is not the separator.** Quadrant means are identical at days 6, 12, 20 and 29. Three-
  and four-quadrant games both win. V72's third-land heuristic has no elite support.
- **Terminal liquidation is common to all.** All eight sides end days 24–29 selling steadily, ~80–100
  sell-active turns in the window. This is table stakes, not an edge.
- **Elite herd shapes are goose-heavy.** Winners in the fresh games finish at 6–11 GOOSE with 5–7 COW
  and 0–5 SHEEP. This is the opposite of the V81 intervention.

## What this supports, and what it does not

**Supported by evidence:** commit opening capital into animals and fertilizer rather than holding
cash (0.78 sd, 0.77 sd); improve asset-to-cash conversion in days 12–23; expect no benefit from
sheep-vs-goose substitution; expect no benefit from land count.

**Not supported:** any specific per-product buy/sell rule. The margin is spread thin across every
line, which is what a ~15% execution edge looks like, and it is not reproducible from a static
ordering rule without the underlying execution quality.

**Not measurable locally.** From the same corpus, 50% of elite games are decided by under 5,000 coins
and 32% by under 2,000, on totals near 108,000. A local panel of 10 games per opponent cannot resolve
a 15% execution difference. The V82 baseline measured V56 at 40-32-8 (50.0%) on five spent seeds and
63% on a 36-seed panel — the same agent, same opponents, a 13-point swing from sample size alone.

## Limits

- The 100-game panel is purposive (top-lineage sampled) and outcome-conditioned, not a controlled
  experiment. Associations are not causal.
- Winners and losers in this corpus are *opponents within the same games*, so they share market state.
  Their comparison is paired, which strengthens it, but it is not a randomized policy comparison.
- The four fresh replays are a sample of 8 player-games and are used only for action-shape
  confirmation, not for effect estimation.
- Effect sizes in standard deviations are a rough ranking aid, not significance tests. No p-values
  or multiple-comparison correction are claimed.
- Nothing here supports a submission or a promotion claim.

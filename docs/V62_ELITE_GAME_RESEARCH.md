# V62 elite replay research

## Finding

The supplied replay, episode **113718271**, ends DSM **$85,693** to Boey **$82,688**, a **$3,005** margin. The target is a close, useful example because the bank leader changes during the season: Boey leads by $3,187 on day 12, but DSM earns $6,192 more net cash from day 12 to the final reward; Boey then recovers $1,454 over the final day. The durable difference is throughput and liquidation over the middle and late season, not the opening bankroll or a fixed land count.

| Observed point | DSM cash | Boey cash | Lead |
|---|---:|---:|---:|
| Start | $3,000 | $3,000 | tied |
| Day 6 | $139 | $23 | DSM $116 |
| Day 12 | $13,152 | $16,339 | Boey $3,187 |
| Day 20 | $58,483 | $57,386 | DSM $1,097 |
| Day 29, start of day | $81,131 | $76,672 | DSM $4,459 |
| Final reward | $85,693 | $82,688 | DSM $3,005 |

Between day 12 and day 20, DSM’s observed cash rises $45,331 and Boey’s rises $41,047. Between day 20 and day 29, DSM gains $22,648 and Boey gains $19,286. Boey makes the stronger final-day increase ($6,016 vs DSM’s $4,562), narrowing the gap. Both players have three quadrants and 55 planted crops on day 12; DSM has 20 animals and Boey 19. Boey’s larger day-12 cash reserve did not translate into a final lead.

At day 29, both farms still show substantial stocks in the shed: DSM has 61 items, principally 41 wheat; Boey has 93, including 44 wheat and 26 strawberries. By the terminal observation, Boey’s shed is empty while DSM retains nine items (one egg, four fertilizer, four milk). The shared displayed terminal prices are $20 wheat, $14 strawberry, $10 fertilizer, and $1 milk. These are direct replay observations, not a reconstruction of which particular sale caused the score gap.

The action stream shows similar labor and production effort in this matchup: DSM records 7,130 farmer/hand action commands, including 3,698 non-PASS commands; Boey records 6,835 commands, including 3,589 non-PASS. DSM records 519 HARVEST, 1,120 WATER, 270 PLANT, 223 FERTILIZE, 357 FEED, 357 CARE, and 451 COLLECT_FERTILIZER commands. Boey records 503 HARVEST, 1,103 WATER, 268 PLANT, 205 FERTILIZE, 346 FEED, 361 CARE, and 442 COLLECT_FERTILIZER. The counts show deliberate work rather than idle turns; they do not certify that each action was legal or changed state.

## Cross-game patterns

The seven-game sample includes the supplied episode plus six other distinct public games listed in the [episode manifest](../experiments/v62_elite_games/episode_manifest.json). At day 6, each farm has only its starting quadrant, 14–20 planted crops, and 5–11 animals; observed cash is only $23–$856. By day 12, farms hold 51–86 crop tiles and 18–24 animals, usually with three or four quadrants unlocked and $4,401–$16,339 cash. The range is wide even among strong players, so these values are reference bands, not fixed targets.

Early fields repeatedly contain melon and strawberry plantings. By day 12, wheat and strawberry are common, while tomato and carrot appear selectively. Herds tend to combine cattle and sheep with a smaller goose group, though the precise mix varies sharply. This points to a state-conditioned sequence: establish early long-cycle/high-value crops and a manageable fed herd, then expand only when open productive land and available work capacity justify the price. Do not hard-code a particular crop count or herd recipe from one seed.

Land count is not a reliable stand-alone signal. In episode 113619306, DSM wins $131,846–$120,032 with three quadrants while DECEM has four. In 113716848, M & M & P & Q wins $129,636–$125,973 with three quadrants while Unknown Mother-Goose has four. Other games show four-quadrant winners. Gate another land purchase on available planting/harvesting capacity, current cash, and the marginal production the extra tiles can support.

All 14 player-games produce roughly 7,100–7,600 logged farmer/hand commands over 720 turns. At least 94% are non-PASS; the remainder is low. This suggests successful agents keep nearly all available units occupied. In the target, both command portfolios are very similar, so merely increasing water/harvest orders is unlikely to close the $3,005 gap. Improve the value produced and sold per worker action, especially when sheds are already stocked.

## Accepted sales expose the input-cost gap

The replay action is paired with the resulting frame: `action[t]` was chosen from `observation[t-1]` and produced `observation[t]`. After settling in that alignment with Kaggle environment 1.32.7, cash matches exactly for all 1,438 player transitions in the target and every sampled episode. This yields an accepted-sale ledger rather than order intent. The complete per-step audit is in [accepted_sales.json](../experiments/v62_elite_games/accepted_sales.json); the [target market timeline](../experiments/v62_elite_games/target_market_timeline.json) joins accepted units and values to submitted orders, observed pre-action prices/stock, and cash movement.

| Accepted target sales | DSM units | DSM gross proceeds | Boey units | Boey gross proceeds |
|---|---:|---:|---:|---:|
| Wheat | 724 | $18,445 | 3,744 | $115,499 |
| Fertilizer | 221 | $12,234 | 1,148 | $42,165 |
| Strawberry | 219 | $24,801 | 208 | $22,556 |
| Melon | 72 | $14,749 | 83 | $15,283 |
| Milk | 180 | $16,533 | 217 | $17,388 |
| Egg | 268 | $11,982 | 242 | $10,946 |
| Wool | 75 | $7,768 | 81 | $6,487 |
| Carrot | 79 | $2,359 | 133 | $3,730 |
| **Total** | **1,838** | **$108,871** | **5,856** | **$234,054** |

The season total by phase shows when the margin developed:

| Phase | DSM sale proceeds | DSM purchases + land/hire | DSM net | Boey sale proceeds | Boey purchases + land/hire | Boey net |
|---|---:|---:|---:|---:|---:|---:|
| Days 0–5 | $3,709 | $6,570 | **−$2,861** | $20,349 | $23,326 | **−$2,977** |
| Days 6–11 | $26,276 | $13,263 | **+$13,013** | $60,943 | $44,627 | **+$16,316** |
| Days 12–23 | $59,402 | $4,725 | **+$54,677** | $115,960 | $66,918 | **+$49,042** |
| Days 24–29 | $19,484 | $1,620 | **+$17,864** | $36,802 | $19,495 | **+$17,307** |

DSM starts the middle phase behind by $3,187, then nets $5,635 more than Boey during days 12–23 and another $557 more during days 24–29. Their phase totals reconcile exactly to the final $3,005 result. Boey’s much greater gross sales are largely offset by much greater input purchases:

- DSM sells for $108,871, buys $4,452 of products (126 wheat), $6,300 of seeds, and $7,600 of animals, and spends a net $7,826 on land and hires. Sales minus these costs are $82,693; plus the $3,000 starting bank gives $85,693.
- Boey sells for $234,054, buys $133,624 of products (3,268 wheat and 920 fertilizer), $6,590 of seeds, and $7,300 of animals, and spends a net $6,852 on land and hires. Sales minus these costs are $79,688; plus the starting bank gives $82,688.

Wheat and fertilizer sale proceeds are $30,679 for DSM and $157,664 for Boey. After accepted product purchases, that part of market cash flow nets **$26,227 for DSM and $24,040 for Boey**. DSM’s net advantage there is $2,187 even though Boey sells more than five times the units. Boey’s additional sales of all other products are $1,802 lower net than DSM’s; DSM also spends $290 less on seeds, while its animal and land/hire costs are respectively $300 and $974 higher. Together these pieces explain the final $3,005 gap. This is the strongest actionable finding: optimize contribution after feed/fertilizer purchases, not sales volume or gross proceeds.

## Tactics to test in the agent

1. **Feed and fertilizer break-even.** Forecast next-day wheat demand from the live herd and forecast harvestable wheat. Protect the feed reserve, then buy only the shortfall; do not buy wheat speculatively while also liquidating wheat unless marginal prices and feed need justify that turnover. The target’s actual $129,172 gap in product purchases is larger than its $125,183 gross-sale advantage. Fertilizer purchases should likewise be limited to tiles and worker turns that can use the supply profitably before season end.
2. **Price-aware liquidation order.** For products in the shed, estimate accepted marginal sale value unit by unit using the current market inventory and official price function. Rank sale routes by contribution after feed/fertilizer reserve rather than a static product order. This is a testable state rule; do not copy per-turn action tapes.
3. **Per-item seed deficits.** Buy each seed type against its own planned plantings and available tiles, so an excess of one seed cannot hide another crop’s shortage.
4. **Land by marginal throughput.** Buy the next quadrant only if projected crop/animal value over the remaining turns exceeds land cost and the current workforce can reach and maintain those tiles. Three-quadrant wins in the sample rule out “always buy all land” as a robust tactic.
5. **Measure wins across independent seeds and lineages.** The same DSM/Boey seat pairing has different winners in the supplied game and episode 113726340. Treat seed as the independent unit, use at least six fresh seeds, and include opponent lineages beyond the current champion.

These are hypotheses to test, not claims that one observed action sequence is optimal. A direct next experiment is a sale-router change only: preserve the agent’s production plan, route sellable stocks using current marginal price and feed reserve, then compare against the baseline across at least six paired seeds and multiple opponent lineages.

## Other public games inspected

All games are completed, public episodes retrieved using `kaggle competitions episodes <submission_id> --format csv` and `kaggle competitions replay <episode_id>`. Exact SHA-256 values, seeds, source submission IDs, participants, rewards, and timestamps are in the [manifest](../experiments/v62_elite_games/episode_manifest.json).

| Episode | Participants | Result | Source submission | Replay SHA-256 prefix |
|---|---|---:|---:|---|
| [113718271](https://www.kaggle.com/competitions/kaggriculture/leaderboard?submissionId=56521745&episodeId=113718271) | DSM vs Boey | DSM 85,693–82,688 | 56521745 | `8a5ca36d7f33` |
| [113726340](https://www.kaggle.com/competitions/kaggriculture/leaderboard?submissionId=56521745&episodeId=113726340) | DSM vs Boey | Boey 75,245–72,702 | 56521745 | `a44b568541c0` |
| [113725041](https://www.kaggle.com/competitions/kaggriculture/leaderboard?submissionId=56521745&episodeId=113725041) | Boey vs Fourth Quadrant | Fourth Quadrant 125,458–120,369 | 56521745 | `fd54a5833c91` |
| [113716848](https://www.kaggle.com/competitions/kaggriculture/leaderboard?submissionId=56553720&episodeId=113716848) | Unknown Mother-Goose vs M & M & P & Q | M & M & P & Q 129,636–125,973 | 56553720 | `3cbda3e818e2` |
| [113619306](https://www.kaggle.com/competitions/kaggriculture/leaderboard?submissionId=56552482&episodeId=113619306) | DECEM vs DSM | DSM 131,846–120,032 | 56552482 | `39e5e871af4c` |
| [113616641](https://www.kaggle.com/competitions/kaggriculture/leaderboard?submissionId=56552482&episodeId=113616641) | DECEM vs Unknown Mother-Goose | DECEM 92,109–91,962 | 56552482 | `b31dc89e8451` |
| [113612113](https://www.kaggle.com/competitions/kaggriculture/leaderboard?submissionId=56552482&episodeId=113612113) | DECEM vs Fourth Quadrant | DECEM 86,974–81,271 | 56552482 | `5c9b24dff6fb` |

## Kaggle discussion findings

- The [“Six things I wish I'd known before trusting my local win rates” discussion](https://www.kaggle.com/competitions/kaggriculture/discussion/743231) reports seed clustering, non-transitive matchups, and lineage-dependent opponent pools. Its author recommends at least six seeds and opponent pools by lineage. They also describe mirror games decided by sale timing and report that even-slicing late bulk sales reduced score in a six-seed check. This is community evidence, not an official guarantee; it supports evaluating state-aware market changes rather than assuming that smaller sale batches are always better.
- The [“Scoring Formula or conditions” thread](https://www.kaggle.com/competitions/kaggriculture/discussion/743179) explains that a high coin score can still lose when the opponent scores more; raw bank size alone does not determine ladder wins. That matches the close target game and supports win-rate gates alongside cash-score tracking.
- The [“Finally reached the silver medal zone with Reinforcement Learning” thread](https://www.kaggle.com/competitions/kaggriculture/discussion/741743) describes a macro-action PPO approach with behavior-cloning warm-up. The author says public high-rated replays can supply demonstrations and that they select checkpoints against a local pool before occasional ladder checks. This supports learning strategic mode changes from the replays, not copying their turn tapes.
- Kaggle’s [“Daily Top Episodes Dataset” topic](https://www.kaggle.com/competitions/kaggriculture/discussion/731215) describes daily replay archives selected by average participant rating, with a stated 20 GB cap. This is useful for future sampling but creates selection and freshness bias; the seven games here are targeted examples, not a representative sample of the ladder.

## Method and artifacts

The primary evidence is Kaggle’s public episode API/replay output, downloaded with Kaggle CLI 2.2.4. The replay schema stores 720 observations/actions per game; each has the matching Kaggle environment module version 1.32.7. The local environment rules source used to interpret crop, herd, market, and action fields is `.venv/lib/python3.12/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py`; the accompanying environment guide is `.venv/lib/python3.12/site-packages/kaggle_environments/envs/kaggriculture/AGENTS.md`.

- [Episode manifest and full replay hashes](../experiments/v62_elite_games/episode_manifest.json)
- [State/action profiles for all seven games](../experiments/v62_elite_games/profiles.json)
- [Accepted transaction and cash-reconciliation audit](../experiments/v62_elite_games/accepted_sales.json)
- [Target per-step observed market timeline](../experiments/v62_elite_games/target_market_timeline.json)
- [Profile extractor](../experiments/v62_elite_games/profile_replays.py)
- [Target timeline extractor](../experiments/v62_elite_games/target_market_timeline.py)
- Raw public replay JSON files: `experiments/v62_elite_games/replays/`

The profiles count commands and market order arguments as serialized. They do not prove that an attempted action succeeded. The target timeline makes that distinction explicit and preserves the observed evidence needed for a later settlement-alignment investigation.

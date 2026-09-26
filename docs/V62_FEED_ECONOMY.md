# V62 wheat and feed economy audit

## Decision

No-go for a wheat/feed policy edit. In the three saved v57-equivalent replays, wheat production and purchases fully covered feed and wheat sales, with no live-unfed feed failures and no wheat left at episode end. The losing seed traces have the same feed and wheat quantities as the winning trace. There is no observed late-season wheat shortage or isolated $10,000 controllable cash deficit to target.

## v57-equivalent replay evidence

The sample is candidate seat 0 against v50 on spent seed 95501 (win), 95508 (loss), and 95518 (loss), from `experiments/v59_state_teacher/dev95501_95519/replays/`. The replay candidate wrapper records the frozen v57 route; the intended teacher perturbation was inactive on the recorded observation format, as documented in [V59_STATE_TEACHER.md](V59_STATE_TEACHER.md). The transaction reconstruction used the pinned 1.32.7 engine and reproduced observed cash on all 1,438 seat-transitions per replay with zero mismatch.

| Seed / result | Accepted wheat product buys | Wheat buy spend | Wheat harvested | Accepted wheat sales | Wheat sale value | Successful FEED | Failed FEED |
|---|---:|---:|---:|---:|---:|---:|---:|
| 95501 win | 140 | $4,820 | 618 | 426 | $16,011 | 332 | 1 already-fed |
| 95508 loss | 140 | $4,583 | 618 | 426 | $14,400 | 332 | 1 already-fed |
| 95518 loss | 140 | $4,888 | 618 | 426 | $15,459 | 332 | 1 already-fed |

All three have the same wheat quantity balance: **618 harvested + 140 bought = 426 sold + 332 fed**. Terminal shed and worker-inventory wheat are both zero. The one rejected `FEED` request in each trace targeted an animal that was already fed; none failed for lack of carried wheat. Thus the large win/loss coin difference is not explained by v57 wheat starvation.

Accepted wheat buying was front-loaded: 33 units during days 0–5, 97 during days 6–11, 8 during days 12–23, and 2 during days 24–29. Wheat sales were 25, 41, 131, and 229 units over those same phases. The phased wheat cash flow below includes product purchases and wheat seed purchases; it excludes feed's implicit operating value.

| Phase | Seed 95501 | Seed 95508 | Seed 95518 |
|---|---:|---:|---:|
| Days 0–5 | −$401 | −$401 | −$401 |
| Days 6–11 | −$2,277 | −$2,163 | −$2,327 |
| Days 12–23 | +$4,179 | +$3,788 | +$4,099 |
| Days 24–29 | +$8,050 | +$6,953 | +$7,560 |
| Season wheat cash flow | **+$9,551** | **+$8,177** | **+$8,931** |

Late-season accounting also closes. Across days 24–29, v57 harvested 254 wheat units, bought 2, sold 229, fed 62 animals, and began the phase with 35 wheat. `35 + 254 + 2 = 229 + 62`; terminal stock is zero. Daily opening stock ranged from 33 to 59 units during these days. There was no late feed failure.

## Comparison with elite target 113718271

The reconciled replay is DSM (seat 0) versus Boey (seat 1). Values below are accepted transactions settled against the same installed engine:

| Policy | Gross accepted sales | Accepted BUY_PRODUCT | Wheat buy units / spend | Wheat sale units / value | Wheat harvested | Successful FEED | Wheat feed failures |
|---|---:|---:|---:|---:|---:|---:|---:|
| v57, seed 95501 | $112,356 | $8,685 | 140 / $4,820 | 426 / $16,011 | 618 | 332 | 0 |
| v57, seed 95508 | $142,144 | $8,448 | 140 / $4,583 | 426 / $14,400 | 618 | 332 | 0 |
| v57, seed 95518 | $129,118 | $8,760 | 140 / $4,888 | 426 / $15,459 | 618 | 332 | 0 |
| DSM target | $108,871 | $4,452 | 126 / $4,452 | 724 / $18,445 | 952 | 356 | 0 |
| Boey target | $234,054 | $133,624 | 3,268 / $104,024 | 3,744 / $115,499 | 834 | 346 | 0 |

The local policy's wheat sales less wheat-product purchases are +$9.5k to +$11.4k before seed cost; after accepted wheat-seed purchases, its wheat cash flow is +$8.2k to +$9.6k. DSM's corresponding wheat flow after $1,730 in wheat seeds is +$12,263; Boey's is +$9,745. The large Boey wheat buy and sell volumes are a high-throughput market stream with a similar final wheat cash contribution, not evidence that v57 is leaving an equally large net wheat margin unclaimed. Both elite players also completed their observed feed work without a live-unfed, no-wheat failure. Boey's unusually high $133,624 product-buy total includes $104,024 of wheat and $29,600 of fertilizer.

## Land, labor, and crop scale

I compared the local v57 route with 14 player-episode profiles across the seven public elite games in `experiments/v62_elite_games/profiles.json`. For each day, hands, crop plots, and animals are the maximum observed during that day; the engine resets hands overnight. The local numbers are representative of all three v57 traces, which share the same route.

| Day | v57: hands / land quadrants / crops / animals | Elite 14-player median: hands / land / crops / animals | Elite ranges: hands; land; crops; animals |
|---:|---:|---:|---|
| 6 | 7 / 2 / 30 / 8 | 8.5 / 2 / 36 / 12 | 8–9; 2; 32–40; 10–16 |
| 9 | 8 / 2 / 37 / 13 | 10 / 3 / 55.5 / 18 | 9–11; 3; 50–61; 14–22 |
| 12 | 9 / 3 / 57 / 17 | 11 / 3.5 / 66.5 / 20 | 10–13; 3–4; 51–86; 14–24 |
| 20 | 13 / 4 / 68 / 17 | 12 / 3.5 / 61 / 20 | 10–12; 3–4; 52–83; 14–23 |
| 29 | 13 / 4 / 31 / 17 | 9.5 / 3.5 / 27.5 / 13 | 9–10; 3–4; 16–42; 9–20 |

V57 expands labor, land, and crop production more slowly through day 12, then has at least as many workers/plots/crops as the median by day 20. At day 9, it retains $2.3k–$3.6k cash while the elite median is $217, so the state shows an early investment-pace difference, not a $10k cash reserve. By day 20 the v57 median cash in these three traces is about $52.2k versus $60.6k for the elite median, with substantial spread and different opponents, shop sequences, and policies. The replay evidence does not isolate a dollar-valued counterfactual for accelerating land, hiring, or planting.

The local accepted land/hire net cost is $15,366 over the season, with $7,593 during days 12–23 and $4,031 during days 24–29. Those are realized investments, not unspent cash. No individual wheat phase deficit exceeds $2.4k, and the full-season wheat cash flow is positive. The observed early scale lag is a general investment hypothesis, not a feed-economy intervention with a demonstrated $10,000 gain.

## Artifacts and limits

The public target's accepted transactions are in `experiments/v62_elite_games/accepted_sales.json`; replay metadata is in `experiments/v62_elite_games/episode_manifest.json`. The local replay actions and final rewards are diagnostic, with three seed samples against one opponent. Public replay comparisons are observational and have different shops, opponents, and production histories. No games or agent files were changed for this audit. No new policy change is recommended.

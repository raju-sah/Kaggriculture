# V76 early collection and melon liquidation: small V70 lift, no promotion

V76 changes only the V70 task schedule. It elevates manure collection to priority 2.3 during days 2–11 when the observed fertilizer quote is at least $60 (otherwise leaving the old priority 4), while preserving care and animal harvest ahead of it. It also allows a melon with at least four yield units to be harvested from day 10 when the observed melon quote is at least $150. V70's market policy already sells everything in the shed; the new behavior brings some day-10 melon into that existing sale queue. Land, animals, crop targets, and hire macro stay unchanged.

Source: `experiments/v76_fertilizer/agent.py`, SHA-256 `36bb69952e3f06d37406881e7b5afc356fafbedeaef7e1f449f7d873de7054cc`. Exact-loader panels used spent seed 94700 in both seats and completed without errors/timeouts. Results:

| Opponent | Record | Mean candidate cash | Median coin gap |
|---|---:|---:|---:|
| Frozen V70 | 2–0 | $57,300 | +$4,884 |
| V56 | 0–2 | $52,200 | −$94,495 |

The V70 gap misses the requested +$5,000 cash gate, and candidate cash against V56 is below V70's previously measured $57,066 seed-94700 result. No other seeds were run. Full outputs are in [`experiments/v76_fertilizer/spent94700_v70/`](../experiments/v76_fertilizer/spent94700_v70/) and [`experiments/v76_fertilizer/spent94700_v56/`](../experiments/v76_fertilizer/spent94700_v56/).

## Exact item ledger

The V75 reconstruction uses the exact Kaggriculture 1.32.7 settlement routine to replay the paired actions. The frozen V70 ledger below is the median of four saved trajectories (seed 94700 both seats plus 92802 and 92804); V76 numbers are from its two seat-swapped seed-94700 games against V70. Accepted cash is grouped into days 0–5 and 6–11.

| Policy/phase | Accepted sales | Fertilizer sales | Melon sales | Product buys | Seed buys | Animal buys | Land/hire residual | Cash change |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Elite median, days 0–5 | $3,644 | $3,012 | $0 | $624 | $1,740 | $3,900 | $92 | −$2,785 |
| V70 median, days 0–5 | $2,590 | $1,924 | $0 | $804 | $1,000 | $2,300 | $62 | −$1,576 |
| V76, days 0–5 | $2,798 | $1,924 | $0 | $841 | $1,000 | $2,300 | $62 | −$1,405 |
| Elite median, days 6–11 | $26,430 | $5,114 | $11,236 | $3,548 | $3,115 | $7,600 | $3,826 | +$10,726 |
| V70 median, days 6–11 | $11,573 | $2,478 | $0 | $757 | $1,450 | $600 | $1,638 | +$7,128 |
| V76, days 6–11 | $15,963 | $2,174 | $6,170 | $936 | $2,150 | $600 | $1,536 | +$10,741 |

V70 already collects and sells manure: its days 0–5 fertilizer proceeds ($1,924) are unchanged in V76. The new high-value effect is earlier melon liquidation: V76 accepts $2,147 melon sales on day 10 and $6,170 in total during days 6–11, where the frozen V70 median has no accepted melon sales. Earlier harvesting likely explains most of the days 6–11 lift, while manure proceeds actually fall by $304 against the V70 control median; the combined experiment does not isolate the priority tweak as a cause. V76's d0–11 sales total $18,761 versus V70's $14,163 control median, but V56 still earns far more later in the game.

V70's seed-94700 melon plants planted on day 0 had four yield units around day 10 while the live melon quote was about $213. V70's original eligibility waited for five yield units or age 12, so some saleable crop remained on the plant until day 12. V76 opens that state-derived sale window at yield four/age ten when the live quote remains economic. This recovers earlier cash and clears tiles for the existing replant schedule. It does not match elite throughput: the six elite winners' median days 6–11 melon proceeds were $11,236, versus $6,170 for this V76 game.

V76 is not promoted. It gives a small, narrowly timed V70 improvement but fails the cash threshold and loses heavily to V56. The fertilizer-collection leg has no support in the measured result; the clearer follow-up, if reopened, would be a separately isolated ripe-melon window with accepted units and sale prices tracked by day. No fresh seeds or submission were used.

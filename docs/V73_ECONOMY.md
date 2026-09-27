# V73 cash-first opening: initial screen stopped

V73 tested a cash-first opening policy on spent seed 94700. The candidate is `experiments/v73_economy/agent.py`, SHA-256 `67283e3bdd5b122ab6caa3b1ce4ccd8d68af9337ea51744f1ff84828a7f147db`. It derives from our frozen V70 source (SHA-256 `2002db9b4bbf20c654805adc35617eb787be3e9cb64e5aae46ae1044aad3b73e`) and retains its state parser, route legality, and task allocator. It replaces the V70 expansion rule with a day-12-only land gate requiring a strawberry buyer/quote plus funds for land, seed, and a $2,200 reserve. It also admits an eight-plot berry footprint from observable buyer/price state, buys berry seeds in two-tile batches while preserving $700, and keeps berry service attached to existing plants.

The benchmark completed both seat assignments without candidate errors or timeouts. It lost both games against each opponent:

| Opponent | Record | Candidate mean coins | Mean/median coin gap |
|---|---:|---:|---:|
| Frozen V70 | 0–2 | $59,222.50 | −$5,987.50 median |
| V56 | 0–2 | $52,904 | −$95,801 median |

The local tournament reports and full replays are in [`experiments/v73_economy/spent94700_v70/`](../experiments/v73_economy/spent94700_v70/) and [`experiments/v73_economy/spent94700_v56/`](../experiments/v73_economy/spent94700_v56/). No 92802/92804 or fresh seeds were run because the 94700 screen was negative.

The V70 matchup replays expose a seat-sensitive bottleneck. At the day-12 snapshot, the candidate had $7,353, two lands, and zero strawberries in one seat; in the swapped seat it had $6,835, two lands, and 12 strawberries. The opposing V70 farms at those snapshots had $6,835/12 berries and $7,353/zero berries respectively. Thus this policy did not improve the shared economic outcome: it largely exchanged which seat reached the same state. It also confirms the berry policy is still gated by observed buyer/price and available actions, rather than a guaranteed early production stream.

This was an economic-rule rebuild, not a full from-scratch scheduler: task allocation remained V70's. The policy did not forecast accepted unit sales or estimate the marginal net cash of an extra worker-day; it used current cash thresholds and seed batches as a conservative proxy. The panel provides no basis to promote it, and further work should first explain seat-dependent crop outcomes and measure accepted sales per productive action before adding land or staffing.

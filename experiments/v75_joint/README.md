# V75 joint herd and crop experiment

The standalone, observation-driven candidate is `agent.py`, SHA-256
`6d4e7c18c81fc499ee97849b988e821e1f6fabdbea687279b95abb92b85db6c4`.
It derives from the frozen V75 service planting repair
`69e0ebd88b23c805d6d2184823c32a4bf9a6ed1b17bcffc6e1ca02fa4d95896b`.
The macro requests a second quadrant when at least four opening animals are working
and cash covers land, feed, and seeds; it then asks for five more sheep as
sites and cash permit. Strawberry fields depend on visible demand and price.
An unreserved weed is dug if it blocks the only remaining site for livestock
already bought. No replay actions, episode IDs, or seed lookup appear in the
policy.

The unpatched first variant is frozen as `agent_tranche1.py`, SHA-256
`6c409254327383845307de2221884970743aa0b12254b38dc5e22c5014730d0c`.
It left one bought sheep in the shed on 94700 because a weed occupied the
last pasture cell. A second cash-reserve variant ran on 94700 only and fell
to $56,211 own cash against V56; its discarded run is in `runs/tranche2_94700/`.

## Exact-loader paired screen

The final weed repair ran with Kaggriculture 1.32.7 on spent seeds 94700 and
92802, each seat, against frozen V70 SHA
`2002db9b4bbf20c654805adc35617eb787be3e9cb64e5aae46ae1044aad3b73e`
and V56 SHA
`d9e9670921b62afedfa8cbc7086d2a2ec19e153ee26006cef477eadd462bd19c`.
Full results, actions, logs, and replays are in
`runs/weed_repair_94700_92802/`.

| Seed/opponent | Candidate coins (seat 0 / 1) | Opponent coins (seat 0 / 1) | Margins (seat 0 / 1) | Wins | Candidate errors | End sheep placed / in shed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 94700 / V56 | 70,962 / 70,962 | 152,982 / 152,982 | -82,020 / -82,020 | 0/2 | 0 | 8 / 0 |
| 92802 / V56 | 70,001 / 70,001 | 116,335 / 116,335 | -46,334 / -46,334 | 0/2 | 0 | 8 / 0 |
| 94700 / V70 | 44,410 / 50,131 | 61,478 / 61,372 | -17,068 / -11,241 | 0/2 | 0 | 8 / 0 |
| 92802 / V70 | 86,379 / 86,593 | 71,412 / 71,457 | +14,967 / +15,136 | 2/2 | 0 | 8 / 0 |

Against V56, accepted sales were $92,873 on 94700 and $92,192 on 92802;
the same-seed saved V70/V56 replays accepted $73,052 and $74,213. Candidate
PLANT action counts were 120 and 127 per V56 game. Exact engine settlement
reconstruction for each candidate V56 seed/seat-0 replay matched observed
cash at every frame (zero mismatches and $0 maximum error). Both seat orders
produced identical V56 results on each seed. All eight final games completed
without candidate, opponent, infrastructure, or timeout errors.

The unpatched comparator earned $69,525 on 94700 and $70,001 on 92802
against V56, losing both seats on both seeds. The weed repair raises 94700
own cash by $1,437 and removes the stranded sheep; it leaves 92802 unchanged.
Against V70 on 94700, the unpatched variant split its seats: candidate cash
$72,543 / $48,665 versus V70 cash $70,568 / $60,974, margins +$1,975 /
-$12,309. The repaired variant lost both seats, as shown above. In candidate
seat 0, its accepted sales fell from $92,231 to $66,943; V70's same-game
sales fell from $86,887 to $77,942. The extra dig/placement work changes the
subsequent deterministic task assignment and shared market. The $25,288
candidate sales loss in that seat explains the flipped result; the exact
route and product mix causal path is not yet isolated. This is a meaningful
regression even though sheep placement and own cash against V56 improve.
It does not make the agent competitive with V56. Cash gains against the saved
V70/V56 baseline are $13,896 and $10,279, below the predefined $15,000
per-seed confirmation gate. Seed 92804 and fresh validation seeds remain
unopened. This candidate is diagnostic, not ready for submission.

The remaining causal bottleneck is early productive throughput: day 6–11
accepted sales were only $7,863 and $9,062 on candidate V56 games, versus
$11,756 and $10,455 for saved V70/V56 games. The extra herd boosts later
sales but spends cash needed to hire hands and plant berries around day 9;
on 94700 the candidate had $50 and five hands at the day-9 checkpoint.

Reproduce the final screen:

```sh
.venv/bin/python -m simulation.tournament --candidate experiments/v75_joint/agent.py --opponent V70=experiments/v70_capacity/agent.py --opponent V56=agents/v56_agent.py --seeds 94700,92802 --repeats 1 --workers 4 --replay-policy all --output-dir experiments/v75_joint/runs/weed_repair_94700_92802
```

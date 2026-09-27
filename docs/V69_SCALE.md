# V69 scale experiments

## Decision

Stop both V69 scale variants. The broad herd/land overlay reduced cash and sales on spent seed 94700. The dispatch-based scale experiment also lost to V67 and V56. A final isolated berry-only trial lost to the frozen dispatch controller by about $2,003 per seat pair and sold fewer strawberries than dispatch in that direct comparison. Nothing here is a promotion or submission candidate.

All matches used the exact Kaggle Environments 1.32.7 loader, both seat orders, and already-spent seed 94700 only. Every game completed without candidate or infrastructure errors. No fresh seed or Kaggle submission was used.

## Broad scale attempt

`experiments/v69_scale/agent.py` (SHA-256 `d4e433b944e23dc663749e0dff7579816478540945c60a81a616499fe97d850a`) expanded to three quadrants, targeted 12 hands, added extra pasture/coop sites, and gated herd growth on observed milk/egg/strawberry demand and prices. It also fixed the structure scan to cover the full board and reserved a three-day wheat buffer.

It won both seats against V67 by an average of $4,493, but lost both against V56 by $120,300 on average, finishing with $34,280 against V56. In that V56 matchup it bought $7,700 of animals and ended with 14 placed animals (6 cows, 3 sheep, 5 geese) and 12 hands. Accepted sale value was $5,282 fertilizer, $19,269 milk, and $6,194 eggs, with no strawberry sales. V56 accepted $23,163 fertilizer, $33,379 milk, $10,720 eggs, and $65,576 strawberry sales. More animals and more land did not become more accepted production; delayed expansion also missed the inherited day-8 strawberry planting deadline.

## Dispatch-based scale attempt

I froze the dispatch controller at SHA-256 `8c69e1f4d756a83effc43b966b808df8441aec22c159396e2b7cd98a15a3112f` before copying it to `experiments/v69_scale/agent_dispatch_combo.py`. The first exact-loader check of that unchanged copy finished at about $40,335 against V56 and beat V67 in both seats. I then added a moderate demand-gated scale step: one extra land unlock, 10 hands, up to five cows and four geese, extra housing in the new quadrant, three-day feed stock, and an explicit ten-order market cap.

That overlay finished at $24,693 against V56 (−$67,676 mean margin) and lost both seats to V67 (candidate mean $35,532, −$19,144 mean margin). It bought 5 cows and 4 geese in total, but ended with only four cows, three sheep, and four geese placed. Its accepted sales were $7,260 fertilizer, $4,800 milk, and $3,285 eggs. This isolates the failure more clearly: buying the extra animals and hiring ten hands did not translate into productive service; it reduced the cash result from the dispatch baseline.

## Berry-only correction

At the parent's request, I tested one isolated correction on an untouched copy of dispatch in `experiments/v69_scale/agent_berry_dispatch.py` (SHA-256 `f4960d13e895c48fc77d3c86a389b5fedb526e8dbad96f40507424c868f8fc92`). It kept dispatch's normal land, herd, and staffing policy; it made existing strawberry plants remain in the task plan when today's price/shop gate changed, reserved feed and shift cash before seed purchases, and capped market orders at ten with strawberry seeds ahead of low-value seeds.

The berry-only candidate lost both seats to frozen dispatch by a mean $2,003. In the direct dispatch matchup it accepted 18 strawberry units worth $3,671, while dispatch accepted 23 worth $4,703. It also lost both seats to V56, averaging $39,363 against V56's $139,120. It beat V67 both seats by about $4,399 on average, but this is below the untouched dispatch branch's seed-94700 margin. The correction did not improve the stronger base.

## Conclusion

The replay evidence rejects this production-scale approach. The central unresolved issue is service conversion: simply adding pens, animals, hires, or berry seeds raises input commitments without ensuring accepted output. V69 scale work stops here; the isolated source files and reports remain for audit, with no variant promoted.

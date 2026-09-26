# V62 actionable-gap audit: no-go on a >$10k intervention

## Decision

No isolated candidate or new game run. The evidence does not identify a
repeatable, observation-conditioned v57 loss worth at least $10,000 across
multiple games. The largest visible macro flow is wheat/fertilizer trading, but
accepted transactions show that it is profitable in both the elite target and
the available frozen-v57 reset replay. Changing it would risk removing a
profitable mechanism without evidence of a better current-state decision.

## Product-flow comparison

The seven-game public replay audit in `experiments/v62_elite_games/accepted_sales.json`
settles accepted units by replaying the Kaggle 1.32.7 engine; the target
balances reconcile on all 1,438 player transitions with zero cash mismatches.
For close episode 113718271, the winning DSM player receives $30,679 from
WHEAT/FERTILIZER sales and spends $4,452 on accepted product purchases, for
+$26,227 net. Boey receives $157,664 and spends $133,624, for +$24,040 net.
Despite a $129,172 gross purchase gap, their net contribution differs by only
$2,187; this does not support removing bulk buying or selling as a $10k-scale
improvement. The final result differs by $3,005, so the remaining game gap is
also below the requested scale.

The saved v57-reset mirror replay on seed 95600 supplies a second local check.
Using the same accepted-transaction settlement and verifying zero cash
mismatches, the v57 seat-0 replay sells WHEAT/FERTILIZER for $33,452 and buys
$9,483 of those products, netting +$23,969. Seat 1 nets +$24,088. Both finish
with empty sheds and rewards of $95,489 and $91,304. The AB and BA replays
produce the same seat outcomes, so these are two seat outcomes from one seed,
not independent game evidence.

The v57 source already adds price-drift liquidation for non-input stock
(`agents/v57_agent.py`, the online price-state block) and later compacts empty
SELL orders before the market action cap (the market compaction block). Its
terminal overlays are exercised in the local replay: no stock remains in either
terminal shed. A state-triggered extra liquidation or order-slot cleanup would
therefore overlap existing behavior and has no demonstrated $10k headroom.

## Limits and rights

The elite replays expose public observations, actions, and accepted transaction
outcomes, not the participants' private source. This audit uses their aggregate
accepted flows only; it does not copy or infer private agent code or replay
turn tapes. The v57 reset comparison uses local saved replays and the local
frozen source. No fresh validation seeds were used, no candidate was created,
and `main.py` was not changed.

The transaction evidence can establish cash contribution, but it cannot
establish whether a different production or purchase decision would preserve
the same sales. In particular, the elite target's $2,187 product-net difference
is below the requested threshold, while v57's local product trading is itself
strongly positive. On this evidence, market-flow intervention is a no-go.

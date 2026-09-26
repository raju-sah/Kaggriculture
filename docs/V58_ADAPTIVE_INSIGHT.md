# v58 adaptive-policy follow-up: feed audit on seed 92902

The retained seed-92902 loss replays do not show the wheat-feed failure seen
in the rejected liquidation overlay. I checked the original goose-switch probe
and all four seat-swapped capped-sheep replays against the pinned engine's
FEED/PICKUP rules. In the candidate seat, none contains a FEED request standing
on a live, unfed animal with zero carried WHEAT. The original probe has six
animals at the day-5 boundary, eight by day 9, and ten by day 11; its maximum
`consecutive_unfed` at those boundaries is one. The cap-five candidate shows
the same herd trajectory. There is no feed-starvation attrition to repair in
these losses.

The retained loss notes instead point to a production-mix difference: around
day 15 the losing candidate has six milk and no wool in the shed and requests
21 milk sales, while its opponent requests six milk and 19 wool sales. The
shop sequence includes a Yarn Store, so relative wool output is a reasonable
lead. The capped goose-to-sheep experiment changed that mix but still lost to
both v52 and v53 by $9,485 and $10,157 respectively. The current evidence does
not validate a new observation-based animal purchase rule; no additional
candidate or matches are justified from this replay set.

The wheat-sale overlay's collapse is therefore specific to its new all-stock
liquidation behavior. It is not evidence that the frozen/base policy needs a
global WHEAT reserve guard. A different targeted strategy would need a new
causal signal and a fresh controlled screen before changing policy.

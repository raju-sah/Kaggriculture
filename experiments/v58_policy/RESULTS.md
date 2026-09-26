# v58 policy branch results

All comparisons use the local Kaggriculture 1.32.7 engine and `v48_agent.py`
unless noted. New tuning work used development seeds 93200–93205; these are
spent. The validation allocation remains 92900–92904 and final holdout
93000–93049.

## Callable-order correction

The original `v58_policy_candidate.py` has SHA-256
`1d7c4591ebb50888e14ba49165bfb1075d4b9ba44b3b41a138a31c5c6e19f959`.
Its v58 wrapper definitions occur after `_kaggle_submission_entrypoint`, but
the Kaggle loader chooses the last callable by definition order. Reassigning
the existing `agent` name did not move it after that alias, so the tested
wrapper code was inactive. The 92900–92901 and 93200–93203 results for that
file are therefore baseline-only and provide no evidence for the v58 rules.
Each active variant below adds a unique callable at end of file; the harness
resolves that callable as expected.

## Active variants

| Variant | SHA-256 | Paired evidence | Outcome |
|---|---|---|---|
| `v58_policy_candidate_earlyshops.py` | `712813412242d5423079cfc469b3af150627ae9f647c9d406734d9b3fea13516` | v48, seed 92802, both seats | 0/2 wins; margins −18,366 and −16,982 (mean −17,674), versus frozen reset margin −6,568 in the original replay. Removing extra livestock when specialist demand is absent was harmful. |
| `v58_policy_candidate_livestock_active.py` | `ca1f5eee5620e99560abd437f90c532fa9de1475ac90c2802d46d5cb3b950445` | v48, seed 92802, both seats; fresh seeds 93204–93205, both seats | 0/2 wins on 92802, both margins −10,930. On 93204–93205 it produced no action differences from frozen reset and all four seat-swapped scores matched exactly. The later cow-to-sheep substitution did not generalize and hurt the known loss case. |
| `v58_policy_candidate_early_liquidation.py` | `c520dca15334e1a9acf0c6149d1ff70cfe669c9f160ff3f42d2bf3bcd1848479` | v48, seed 92802, both seats | Same margins as the active livestock variant and no action differences from it. The base policy already placed the available milk sale when the liquidation trigger was met. |
| `v58_policy_candidate_goose_sheep_cap5.py` | `878c0a5c54edca435ddcad78bdcf959f232777de8f9132cedaa2a91046df0836` | v52 and v53, seed 92902, both seats | Active conversions were capped at five total sheep. It lost to v52 by $9,485 in both seats and to v53 by $10,157 in both seats, worse than frozen reset margins of $6,260 and $7,089. This reduced the damage of the uncapped variant but still failed its paired baseline. No fresh seeds were run. |

The fresh 93204–93205 frozen-reset margins against v48 were respectively
`+468/+468` and `+5,096/−9,625` by candidate seat 0/1. The active livestock
variant repeated these exact scores. No active variant improved the observed
historical sweep. No final holdout seed was used.

## Conclusion

The shop-aware purchase edits do not address the broader throughput weakness.
The early filter loses value by suppressing useful production; the later
substitution only changes a known loss replay and reduces its score. Extra
liquidation duplicated a sale already made by the base policy. These variants
are retained as negative experiments and are not release candidates.

## Retained seed 92902 loss replay

The baseline first briefly falls behind by $90 on day 4, then leads by $736
at day 9. The durable reversal starts on day 15: cash changes from a $939
lead at day 14 to an $1,811 deficit at day 15. By day 18 it trails by $8,303.
At day 12 both farms occupy three quadrants and have the same 71 active tiles.
At day 18 both still occupy three quadrants and each hires 11–13 workers that
day, so this trace does not show a worker or land shortage at the time the cash
gap opens.

The candidate's animal mix differs before the reversal. On day 6 it buys two
geese while v52/v53 buys two sheep; on day 9 it adds two more geese while the
opponent adds one sheep. The shop sequence is Pizza, Pizza, Yarn, Bakery, Ice
Cream, Smoothie, Pizza, Ice Cream, with no Brunch Spot. At day 15 the candidate
has six milk and no wool in its shed and requests 21 milk sales; the opponent
requests six milk and 19 wool sales. By day 18 the candidate requests 24 milk
and two wool sales, while the opponent requests nine milk and 24 wool sales.
These are submitted quantities, not evidence that every unit sold. Replay
statuses remain active/completed and per-step `info` is empty; the retained
artifacts do not identify rejected movement or placement actions.

This evidence motivated the capped goose-to-sheep diagnostic above. It did
change actions as intended, but still lost to both opponents by more than the
frozen reset policy. Treat animal mix as a lead for further audit, not a
validated intervention. The separate elite market audit found a much larger
realized-sales gap in wheat and fertilizer; the expansion branch is testing
that higher-level throughput hypothesis. Its cross-replay quantities are
diagnostic only: same numeric seed does not guarantee a matched shop sequence,
because weed spawning over different farm occupancy consumes RNG before the
next shop is drawn. Fair comparisons need realized-shop stratification or a
fixed-shop counterfactual.


## Wheat/fertilizer sell overlay on frozen expansion (rejected)

Variant `v58_expansion_wheat_fert_candidate.py` was copied from the frozen
expansion artifact (SHA-256
`20c5a4a2e0d96d39cdd9e26de9daff0e685b66b5ec7f943f1e85ae38330e09fc`) and
adds at most one `SELL WHEAT`/`SELL FERTILIZER` order when the matching shop is
unlocked, price exceeds its floor, shed stock exists, and a market slot is
free. The variant's SHA-256 is
`5b2b7844debc0084252c76f4fb11feed941b6e22553de22dc796ea735d216755`. A retained
replay action probe showed a live difference at step 72: with Pizza unlocked,
$30 wheat, and six wheat in the shed, the frozen route had five hire orders and
no wheat sale; the overlay added `SELL WHEAT 6`.

The paired screen used seeds 93700–93703 against v50/v53, both seats, with
frozen expansion as control. Control completed 16/16 games (8/16 wins, mean
margin −419.4). The overlay completed 12/16 before early stopping: it lost all
12, with mean margin −69,383.7. All eight v50 overlay games completed and lost
(versus control's 4 wins/4 losses); four v53 overlay games completed and lost.
Across the 12 completed same-opponent/seed/seat pairs, overlay margin change
was −73,096.75 on average (range −98,188 to −48,168). Four remaining v53 games
were terminated after the large losses were already apparent; this stopping
rule was post hoc, so treat this as a rejected screen rather than a formal
sequential test. No further overlay runs were made.

An accepted-sale audit of overlay replay v50/93700, seat 0, found 671 accepted
wheat sales for $19,860 and 96 fertilizer for $7,189. The overlay game ended
with candidate reward $35,446 against opponent $105,552. This confirms sales
were executed, but no corresponding control replay was retained for a matched
accepted-volume difference. The replay also shows the policy selling wheat
from shed stock while the action route frequently issues `FEED` with no carried
wheat (for example, steps 158 and 198); the engine's FEED action consumes only
carried WHEAT, so those particular FEED orders are already no-ops. This is a
measured route/stock overlap, not proof that the extra sales caused the losses.
The extreme paired margin decline rejects the overlay; future sales logic must
reserve feed stock and test action consequences before broader runs.

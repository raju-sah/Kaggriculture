# V60 market interaction lead from seed 92902

## Decision

No adaptive market or portfolio change is supported by this same-seed audit.
The frozen candidate earns more gross sale revenue in the two losing matches
than in the winning match, and accepted candidate sale quantities are the same
across all three. The result flips because opponent market supply differs,
especially WOOL. Changing the candidate's selling or portfolio policy to chase
these outcomes would be speculative and would enter the excluded sheep-mix or
market-solver space.

## Exact transaction reconstruction

I reconstructed each transition in the saved v58 baseline replays for
`v52-seed-92902-ab-repeat-0`, `v53-seed-92902-ab-repeat-0`, and
`v54-seed-92902-ab-repeat-0`. The audit applied the engine's unit actions and
`_process_market` to the preceding observation, logging every accepted sale at
its actual unit quote. Reconstructed balances matched the saved next-frame
balances exactly for all three replays.

The candidate's accepted sale quantities were identical in all three matches:
221 MILK, 252 STRAWBERRY, 80 TOMATO, 46 WOOL, 224 EGG, and the same quantities
of the other goods. Its total gross sales were $140,401 against v52, $139,905
against v53, and $133,757 against v54. The losses were $6,260 to v52 and $7,089
to v53; it beat v54 by $2,454. The candidate therefore did not lose because
its own sale quantities or gross proceeds were lower.

| Product | Candidate revenue vs v52 | vs v53 | vs v54 | Largest difference |
|---|---:|---:|---:|---:|
| TOMATO (80 units each) | $13,484 | $13,484 | $8,062 | $5,422 |
| MILK (221 units each) | $52,131 | $52,095 | $50,420 | $1,711 |
| FERTILIZER (327 units each) | $15,710 | $15,710 | $16,549 | $839 |
| WOOL (46 units each) | $8,533 | $8,533 | $9,840 | $1,307 |

TOMATO has the largest change in candidate proceeds, but the candidate earns
more from tomatoes in both losses than in the win. It is not a supported target
for intervention. The larger reward difference is the opponent's WOOL market:
v52 and v53 each sold 278 accepted WOOL units for $49,165, while v54 sold 72
for $15,881. The candidate sold 46 WOOL units in each replay. This opponent
output difference is larger than any candidate-side revenue change, but a
candidate response would require the excluded livestock/production-mix change.

## Earliest opponent-derived state signal

Market state first separates at step 92 (day 3, hour 20): WHEAT is $29 in the
v52/v53 matches and $30 against v54. The first notable WOOL signal is step 150
(day 6, hour 6): price is $206 with market inventory 9,999 against v52/v53,
versus $199 and inventory 10,005 against v54. TOMATO inventory first splits at
step 505 (day 21, hour 1); its price first splits at step 513 (day 21, hour 9),
$92 against v52/v53 and $90 against v54. By the candidate's first TOMATO sale
at step 647 (day 26), the observed price is $185 against v52/v53 but $141 against v54; the candidate still submits the
same 10-unit sale. Subsequent candidate tomato sales also have identical
quantities, while the price gap widens.

Thus an observable opponent signal exists before tomato liquidation, but it
does not identify a profitable change: the candidate receives higher tomato
proceeds in the losing matches. The early WOOL signal precedes later wool
sales, but candidate wool volume is only 46 units and the main effect is the
opponent's own larger WOOL production. The worker-action stream is identical
across the three matches, as documented in `docs/V60_DISPATCH.md`.

## Recommendation and risks

Do not change the frozen candidate from this evidence. The state differences
are real and the transaction reconstruction is exact, but the strongest
explanation is opponent-side production of WOOL, not a candidate decision with
a demonstrated profitable alternative. TOMATO revenue varies by $5.4k, but
its direction contradicts the match outcomes. A price-triggered hold or crop
switch could sacrifice revenue in the losing matches or increase market
exposure elsewhere. No tournament or new seed was run, and no candidate file
was edited.

Reproducible audit: [audit_market_interaction.py](../experiments/v60_dispatch/audit_market_interaction.py)
and its [transaction summary](../experiments/v60_dispatch/market_interaction_92902.json).
The inputs are the three saved replays and game records under
`experiments/runs/v58_validation_baseline/`; replay accounting uses the installed
Kagriculture engine's `_apply_unit_action`, `_process_market`, and `_commit_unit`
functions.

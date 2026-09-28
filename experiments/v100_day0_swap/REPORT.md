# V100 day-zero sheep-to-cow swap

## Intervention

V100 wraps the pinned V92 policy and changes only the day-0 opening animal sequence: buy one fewer sheep and one additional cow at hour 1, then have the farmer pick up/place that cow at hours 3/8. All other policy logic is unchanged. Candidate source SHA-256: `4614982d09515cf1b03d98e65410e189d3d913169f5a92e3312e28185163f5ed`. Embedded V92 SHA-256: `0d5d356baa25703f1a7b753527d1b39e1c7d63478985913be5b3c2550261b806`.

## Exact-loader microtrace

Seed 92600 vs V92, both seats, produced identical deterministic outcomes: V100 $85,960 vs V92 $89,012, a $3,052 loss in either seat. The changed actions were accepted: market order was COW×3/SHEEP×1; farmer picked up and placed a cow on the original pasture at (3,3). The cow survived through close and received 29 CARE, 28 FEED, and 8 HARVEST actions; final yield_units was 3 and consecutive_unfed was 1. Final herd counts were 6 cows/10 sheep for V100 and 6 cows/11 sheep for V92: by day 8 the control had caught up in cow count, so V100 shifted the timing and displaced one sheep rather than adding a season-long cow.

Accepted sale cash for V100 was MILK $41,455 and WOOL $4,558. The control sold MILK $39,848 and WOOL $6,697. Thus the shift gained $1,607 in milk receipts but lost $2,139 in wool receipts, before other category differences. Replayed market cash matched saved observation money to within $0.01 throughout (zero mismatches).

## Spent-seed panel

Exact-loader, 10 already-spent seeds `[92600, 92601, 92602, 92603, 92604, 92802, 93700, 94700, 95100, 95300]`, paired with both AB and BA seats against V92 and V50 (40 games; artifacts in `runs/panel_10_spent_vs_v92_v50`). Result: **0 wins, 40 losses, 0 draws**; no candidate errors, opponent errors, infrastructure errors, or timeouts. Mean candidate cash was $95,153.43; median margin was −$5,830.50. Against V50: 0/20, mean margin −$5,955 (median −$5,538); against V92: 0/20, mean margin −$6,664.15 (median −$5,991). Neither seat won (0/20 each).

## Decision

Do not promote or submit V100, and do not spend fresh holdout on it. The intended extra-cow production was partly offset by sheep displacement and subsequent baseline catch-up; the paired panel is consistently and materially negative. This does not support complementarity with a day-6 cow swap: V100 only shifts opening timing and loses an animal later, so combining it with another cow-buy intervention risks further purchase suppression rather than adding productive capacity. Keep the V99 day-6 experiment separate.

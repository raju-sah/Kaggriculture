# V92 official 10-game diagnosis (2026-09-27)

This report freezes the first ten official V92 episodes as the diagnosis cohort. Later episodes are retained in `experiments/v92_official/replay_summary.{csv,json}` as out-of-sample checks and are not used to define the original cohort.

## Audit method and integrity

`experiments/v92_official/analyze_replays.py` joins the observation at `steps[t]` to the action at `steps[t+1]`, replays each recorded transition through the pinned installed Kaggriculture engine, and measures accepted sales at the engine's per-unit commit point. For candidate reproduction it replays V92 sequentially on each observation. Seat-1 public observations omit `step`; the analyzer reconstructs it as `day * turnsPerDay + hour` before policy calls. Without this normalization, source comparisons are invalid.

All ten frozen episodes reproduce 719/719 Rajusah actions; all 20 player ledgers have zero cash mismatches. The V92 guard fires at observation step 575 in every game. The V50 base action buys 16 WHEAT and 11 FERTILIZER, giving guard projection 128 against shed capacity 100; V92 rewrites both buys to 4 and leaves SELL WHEAT 8 intact. The observation has 4 shed units and 91 carried units. These are reproduced facts, not counterfactual score estimates.

## Frozen cohort

| Episode | Result / margin | Cash gap Rajusah−opponent at days 10 / 15 / 20 / 23 / 27 / 29 | Accepted sales cash Rajusah / opponent |
|---|---:|---:|---:|
| 114158802 | W +34,317 | +15,242 / +14,517 / +20,099 / +20,065 / +25,838 / +34,317 | 136,926 / 89,798 |
| 114160308 | W +18,396 | +13,221 / +19,721 / +43,540 / +38,981 / +23,509 / +18,396 | 146,027 / 129,196 |
| 114161728 | W +133,896 | +14,811 / +28,594 / +68,412 / +91,666 / +117,517 / +133,896 | 171,066 / 28,382 |
| 114163744 | W +10,702 | +10,780 / +9,025 / +11,610 / +10,716 / +12,532 / +10,702 | 92,200 / 79,877 |
| 114164630 | W +30,593 | +1,538 / +3,614 / +14,002 / +16,698 / +17,755 / +30,593 | 135,532 / 117,118 |
| 114166061 | L −22,706 | +1,924 / −7,398 / −6,490 / −11,909 / −18,994 / −22,706 | 133,341 / 153,999 |
| 114167570 | L −9,100 | +314 / −6,612 / −6,397 / −8,609 / −11,383 / −9,100 | 121,295 / 130,543 |
| 114169079 | L −22,088 | +423 / −6,174 / −5,681 / −11,494 / −21,033 / −22,088 | 137,840 / 160,165 |
| 114170594 | W +49,344 | +13,294 / +16,738 / +23,791 / +32,874 / +38,635 / +49,344 | 135,457 / 84,956 |
| 114172061 | W +15,234 | +12,676 / +3,427 / +10,299 / +13,956 / +16,263 / +15,234 | 101,104 / 85,440 |

All ten share Rajusah's day-15 herd of 6 cows and 11 sheep. Each loss has an 8–9-cow opponent at day 15 and accepted MILK sales cash exceed Rajusah's by $13,500–$25,451. Yet winners include opponents with 12 and 11 cows, while Rajusah wins a large milk advantage in 114161728. This identifies opponent herd/product performance as correlated with these losses, but does not support a blanket cow conversion as a discriminating intervention.

## Low-quote sales and capacity

The settlement audit confirms repeated low WOOL sales in both outcomes. Exact engine quote histories show 114166061 accepted 19 WOOL units at $1–$5 on day 15, 18 on day 16, and 16 on day 17; its day-end WOOL quote was $1 on days 15–21, then $18 on day 21 and $31 on day 22. 114167570 likewise has 19 / 18 / 16 WOOL units at $1–$5 on days 15–17, and the quote remains $1 at day 21 before recovering to $55 by day 22. This is a real price collapse with partial later recovery, but not proof that withholding those units improves total proceeds: those sales help replenish market inventory and subsequent prices are endogenous.

The pattern is not loss-specific. Winner 114158802 also sells 19 / 18 / 16 WOOL units at $1–$5 on days 15–17, then continues through the low-price period and wins by $34,317. Winner 114164630 earns $66,498 in accepted WOOL sales and wins despite a $1 WOOL quote at day 15; winner 114170594 earns $66,050 in WOOL sales and wins. MILK does not show the same loss signal: Rajusah's day-15 quote is $204, $199, and $228 in the three losses, and accepted MILK sale cash exceeds the opponent in 114166061 while the other two losses trail.

At the day-23 guard observation, each frozen game has 4 items in shed and 91 carried, before the action and end-of-day drop. At sampled hour-23 snapshots, shed alone is below 100; at day 25 it is 15 with 86 carried. The combined count can exceed capacity, but the engine applies capacity to shed deposits, not to carried units already in hands. These observation snapshots do not prove whether any items were discarded during that day's end-of-day deposit. A candidate overflow mechanism would require replaying each end-of-day action and measuring the exact drop; no loss-specific recurring overflow is established here.

## Decision

The evidence does not isolate a controllable loss cause shared by all three losses in the frozen cohort. Low-quote WOOL liquidation is a measurable market behavior, but winners exhibit it too, and the evidence does not establish that waiting is profitable or route-safe. Do not promote it as a V93 intervention from these replays alone. The existing guard is demonstrably active and reproduces exactly; a next experiment should use paired seeds and evaluate any proposed change against both the three loss controls and the seven wins.

The later official episodes remain explicitly out-of-sample in the analyzer: 114173483 (L), 114175006 (W), 114176499 (L), and 114177946 (W). The 14-game loader audit is 719/719 per game with zero market cash mismatches.

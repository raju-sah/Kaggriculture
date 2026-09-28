# V102 specialist-shop sale overlay — stopped, no-go

## Hypothesis and implementation

V56 conditionally sells several goods only after a matching specialist shop opens (fertilizer and late clearance are exceptions). V102 tested that exact observable rule as a low-disruption market-only overlay on V92: for WHEAT, EGG, MILK, WOOL, CARROT, STRAWBERRY, MELON, and TOMATO, suppress the base SELL order until any shop in the corresponding map is unlocked; clear all at step 630. Unit actions and all non-sell orders stay with V92. Candidate SHA-256: `2353aa49b4e2b57893e68790ec35ff4bab9ebdc33c1b5f1ad43953e51d99d141`; embedded V92 SHA-256: `0d5d356baa25703f1a7b753527d1b39e1c7d63478985913be5b3c2550261b806`.

## Early spent-seed result

The exact-loader screen began on ten already-spent seeds against V92 and V56 in both seats, with two repeats. It was stopped after the early result was decisively negative; no fresh holdout seed was used. Of the partial V102-vs-V92 group, 27 completed games produced **0 wins, 27 losses**, mean margin **−$71,142**, median **−$69,388**, and mean candidate cash **$41,974**. Four additional jobs ended as worker failures during the intentional stop. The V56 arm had not begun, so there is no V102-vs-V56 result.

An exact saved replay (seed 92600, V102 seat 0 vs V92) shows the filter withheld 180 WOOL, 17 WHEAT, and 12 MILK SELL units that the underlying V92 policy requested. V102's shed reached capacity (100 units) on 14 observed frames; shed plus carried inventory exceeded 100 on 142 frames and peaked at 134 units (day 19, hour 20: shed 64, carried 70). These are occupancy observations, not a claim that all excess was destroyed; V93's engine-instrumented audit remains the authoritative discard measurement.

## Comparison with V93 and decision

This reproduces the same risky assumption as V93, with a broader set of held goods. V93's 11-seed matched study withheld 1,150 wool units and lost to V92 0–12 with 10 draws (median margin −$4,540). Its unit-by-unit audit found that withheld wool was not recovered later: V92 realized $462 on the relevant days while V93 realized $381, and V93 ended with 81 fewer wool units sold. The V93 audit also measured the physical constraint: the shed is capped at 100, stock left in the shed scores zero, and only two units per official game were actually discarded after V92's guard. The practical failure was stranded cash conversion and shed occupancy, not an unexploited wool-price peak.

V102's sampled losses are much larger than V93's, while its inventory audit confirms sustained capacity pressure. Reject V102 and do not finish its tournament panel or spend fresh seeds. Shop unlock is an exact observable trigger, but it does not establish that deferred inventory will later be sold at a better price or that the policy has capacity to hold it. The evidence does not support this as a robust switch or as a complement to V92.

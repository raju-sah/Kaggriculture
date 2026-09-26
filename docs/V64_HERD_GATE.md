# V64 early herd-gate feasibility audit

## Decision

Stopped before implementing a candidate or running the requested spent-seed matches. The frozen v57 route has no demonstrated spare housing or placement route for an extra early animal, and its day-0–5 route state is the same in two saved losses and one saved win. A buy-only overlay would therefore leave the purchased animal unplaced, while adding housing/placement/feed work would change the route and compete with existing work. The audit does not support a narrow ROI gate that preserves crops and workers.

## Saved-state comparison

Inspected candidate-seat replays for losses `92802` vs v48 and `92804` vs v51, and the win `92900` vs v48. At the day-5 opening (step 121), all three have the same observed setup:

| State | Loss 92802 | Loss 92804 | Win 92900 |
|---|---:|---:|---:|
| Cash | $762 | $762 | $762 |
| Active hands | 3 | 3 | 3 |
| Animals | 6 | 6 | 6 |
| Pastures / occupied pasture tiles | 6 / 6 | 6 / 6 | 6 / 6 |
| Cropped tiles | 19 | 19 | 19 |
| Crops | 12 melon, 7 wheat | 12 melon, 7 wheat | 12 melon, 7 wheat |

The route buys 4 animals at day 0 (2 cows and 2 sheep), then one cow each on days 2 and 3. It builds exactly 6 pastures by day 5 and places the six animals. Across days 0–5, the saved actions contain 6 `BUILD_PASTURE` commands, 15 `PLACE` commands (including fertilizer placement), 24 `FEED`, and 30 `CARE`. These are route-level counts, not all animal-specific actions; the replay audit does not identify a free recurring feed/care allocation. Day-5 cash is $762, so even the additional animal purchase competes with the cash reserve before paying for housing or upkeep.

The extra animal needs, at minimum, an additional pasture, an animal purchase, and a successful placement. The frozen route has no empty pasture at the decision point and no planned additional build/placement pair. Finding a tile in the remaining farm area is not sufficient evidence of route feasibility: the route must reach and build it, retrieve the animal, place it, then sustain feeding and care without disrupting the crop/work schedule. Day-5 cash is only $762 before the added animal's continuing costs. No saved state demonstrates spare action capacity. The first unsupported transition occurs before any ROI calculation can rescue the intervention.

The early state is also not outcome-discriminative in these saved games. The two losses and one win all reach day 5 with the same cash, staffing, herd, housing, and crop counts. A threshold based only on these quantities would take the same action in both outcome classes. Market/shop observations can vary, but there is still no available slot to house the added animal, and the V63 elite-panel relationship between day-6 herd size and later cash flow is descriptive rather than a treatment effect.

## Interpretation and constraints

The V63 elite sample supports an early-herd hypothesis (winner median 8 animals vs loser median 5 at day 6), but the V63 local-control sample finds exactly 6 animals in both the frozen-v57 winning and losing rows, with no day-6 state separation. V58's broader expansion overlay also failed the historical robustness screen (42/80 vs v54/v56 in the loss-concentrated panel). This narrow animal-only follow-up cannot safely transplant the public winner median into the route without solving housing and labor allocation first.

No experimental candidate was created; no game was run; no new seed was consumed. The original frozen candidate file was left unchanged at SHA-256 `4173479fe1f80d031d570d1ea23b694dfe86e1d162317a4c9c7df0058a40208e`. That source documents that its farm route was adapted from the public Lizs replay. Any future derivative remains within the existing internal-research boundary unless the original-work/licensing question is resolved; this audit creates no submission artifact.

## Sources

- [`V63_ELITE_PANEL.md`](V63_ELITE_PANEL.md): 50 paired public episodes; day-6 herd association and its confounds.
- [`V63_LOCAL_CONTROL.md`](V63_LOCAL_CONTROL.md): saved frozen-v57 control panel, including the identical six-animal day-6 state in wins and losses.
- [`V58_EXPANSION.md`](V58_EXPANSION.md): earlier broad expansion failure and its market-sequence caveat.
- Saved action replays: `experiments/v58_diagnostics/replays/v48-seed-92802-ab-repeat-0.json`, `experiments/v58_diagnostics/replays/v51-seed-92804-ab-repeat-0.json`, and `experiments/v58_policy/baseline_vs_v48/replays/v48-seed-92900-ab-repeat-0.json`.

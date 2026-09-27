# V91: V50 day-23 last-hour overflow — CORRECTED, feasible, candidate NOT built

Read-only. Saved replay, pinned Kaggriculture 1.32.7, exact engine transitions. No fresh holdout, no
sealed seed, **no Kaggle submission**. Frozen agents not modified.

**This report supersedes the first V91 README, which was wrong. The correction is material and it
reverses the conclusion: the loss is heterogeneous and the intervention is feasible. No candidate
was built, and the reason is stated precisely under "Why no candidate was built".**

## The error in the first V91 report

The first V91 report concluded the discarded units were "14 STRAWBERRY worth $42". That was wrong.
It computed the discard by simulating the drop against the **carried inventory observed at
`obs[575]` (91 units)**, omitting the `HARVEST` that `action[576]` performs **before** the market
and the overnight drop. Correcting this reproduces V90 exactly and matches the engine's own recorded
next-frame shed.

**The correction chain, all verified under the pinned engine:**

1. Replay alignment, proven not assumed: applying `act_of(steps[575])` to `obs[574]` reproduces
   `obs[575]` exactly (`match=True`). So `act_of(steps[t])` is chosen from `obs[t-1]`.
2. `action[576]` contains `HARVEST` and `COLLECT_FERTILIZER`; these run first and add units.
3. Inventory **at drop time** is therefore **93**, not 91 (STRAWBERRY 20 → 21, FERTILIZER 16 → 17).
4. The market then runs, leaving shed at 23 and 93 carried.
5. `_drop_inventories_to_shed` fills to 100 and discards:

| Product | Lost | Quote at d23 h23 | Value |
|---|---:|---:|---:|
| WOOL | 4 | **$133** | $532 |
| WHEAT | 4 | $37 | $148 |
| FERTILIZER | 5 | $29 | $145 |
| STRAWBERRY | 3 | $3 | $9 |
| **Total** | **16** | — | **$834** |

**Predicted post-drop shed matches the engine's recorded `obs[576]` shed item-for-item**
(FERTILIZER 23, MILK 6, STRAWBERRY 18, WHEAT 45, WOOL 8 = 100). This agrees with V90's
`lost_day_by_product` for day 23 (FERTILIZER 5, STRAWBERRY 3, WHEAT 4, WOOL 4 = 16) and is worth
**$834**, not $42. The bulk is **wool at $133/unit**, the most valuable product in the game.

## The engine order that makes the loss, confirmed in source

`_apply_unit_action` (unit actions, incl. HARVEST) → `_process_market` (BUY lands in shed, SELL
removes) → `_end_of_day` → `_drop_inventories_to_shed` (capacity 100, overflow discarded, engine
lines 843-857). Drop order is **worker-inventory index order, then item order within each worker**,
so the discarded tail is whatever sits in the highest-index hands.

State at d23 h23: shed holds **4 WHEAT**, workers carry 91; after the harvest and market, 23 in the
shed and 93 carried against capacity 100.

## Feasibility: a last-hour SELL does work, but only standalone

Nine market-order variants, each replayed through the pinned engine from the same `obs[575]` state.
`cash+shed` at d24 h00 valued at the d23 h23 quote is a proxy, not a score.

| Variant | cash | shed | lost units | lost value | cash+shed | delta |
|---|---:|---:|---:|---:|---:|---:|
| as played (BUY W16, BUY F11, SELL W8) | 54,868 | 100 | 16 | $834 | 58,348 | — |
| SELL W4 then BUY W16, BUY F11 | 54,693 | 100 | **20** | $982 | 58,173 | −175 |
| SELL W4 then BUY W10 | 54,921 | 100 | 14 | $802 | 58,359 | +11 |
| SELL W4 then BUY W6 | 55,073 | 100 | 10 | $686 | 58,479 | +131 |
| SELL W4 then BUY W3 | 55,187 | 100 | 7 | $547 | 58,621 | +273 |
| **SELL W4 only (no buys)** | **55,660** | **93** | **0** | **$0** | **59,211** | **+863** |

**The intervention is feasible and quantified: replacing the last-hour order with a single
`SELL WHEAT 4` eliminates the overflow entirely (16 → 0 units) and is worth +$863 on the cash+shed
proxy in this game.**

The mechanism is precise, and it is the opposite of the intuition that motivated the first report:

- **Prepending a SELL does not help** (SELL-then-BUY16 is *worse* at 20 lost). The engine settles
  SELL and BUY_PRODUCT **in the submitted order, in a lockstep loop** (lines 583-626): the four freed
  slots are immediately refilled by the next `BUY_PRODUCT`, so the shed is full again before the
  drop. A committed `_commit_unit` trace shows the buy/sell pair alternating four times, exactly
  cancelling.
- **Only removing the buys works**, because the shed must be left below 100 when the overnight drop
  runs. 4 (shed) − 4 (sold) = 0, and 93 carried ≤ 100.

So the effective rule is not "sell more", it is **"do not let the shed reach capacity before the
overnight drop"** — which in this state means declining the 16 WHEAT and 11 FERTILIZER inputs.

## Why no candidate was built

The +$863 figure is real engine arithmetic, but building a guard around it would be a mistake, for
three reasons that the evidence supports directly:

1. **The gain is a trade, not a windfall.** The zero-loss variant pays for it by forfeiting 16 WHEAT
   and 11 FERTILIZER — the feed and soil inputs for the final six days. The `cash+shed` proxy does
   **not** price that cost, because shed contents are valued at the d23 h23 quote and the forfeited
   inputs were never bought (so they never appear as cash out). The true net effect on the final
   score is not determined by this arithmetic and was not measured.
2. **The deadline is one hour wide.** The overflow occurs only because the shed is at 93–100 at the
   single day-23 hour-23 boundary. A guard active only at that hour is correct here, but I have not
   verified that the same condition is reached in the other 55 head-to-head games with the same
   composition, and V90's per-game mean of ~$991 is an average over a mixed, un-decomposed loss.
3. **The recoverable amount is small relative to measurement noise.** $834 in a game that ends near
   100,000 coins, on a lever that exists for one hour of one day. V87, V88, V90 and V91 have each
   terminated at a diagnostic for the same reason, and the five dead ends share a cause: the
   remaining levers are below what a 48-game panel can resolve.

A candidate here would be a one-hour, one-day, input-deferring rule whose sign depends on an
unmeasured feed/soil trade-off. The honest next step is not to build it on this evidence but to
**measure the trade-off**: replay days 24–29 under both variants and settle the full season, which
converts the proxy into a real cash delta. That is a diagnostic, not a candidate, and it is recorded
as the recommended follow-up.

## Limits

- One game (seed 92802, V50 seat 1) reconstructed in depth. The 16-unit loss is repeatable across
  56 clean head-to-head games per V90, but the **per-product composition** and the exact recoverable
  value are from this game and vary with portfolio and shed state.
- The valuation uses prices visible in the d23 h23 observation. Shed contents persist to day 29 and
  their eventual sale prices differ; the `cash+shed` column is a proxy, not a score.
- The lockstep settlement behaviour (SELL/BUY interleaving) was verified by a `_commit_unit` trace on
  this state; it is engine-level and should generalise, but was not re-verified on other games.
- No fresh holdout, no sealed seed, no submission, and no frozen file was modified. V90's invalid
  V56 loss artifacts were not used.

## Artifacts

- This report supersedes the earlier `README.md` in this directory. No candidate file was created,
  and `plan.json` was deliberately not written, because the gate cannot be honestly predeclared
  until the day 24–29 trade-off is measured.

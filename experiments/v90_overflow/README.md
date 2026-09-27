# V90: mid-season shed overflow — diagnostic only, NO CANDIDATE

Read-only. Saved replays with SHA provenance, pinned Kaggriculture 1.32.7, exact engine transitions.
No fresh holdout, no sealed seed, **no Kaggle submission**. Frozen agents were not modified.

**Outcome: no candidate built. The branch stops at the diagnostic**, because the measured loss does not
meet the stated bar and, where it exists, is not attributable to the seat under study.

## Instrument bugs found and fixed before any number was trusted

Three defects in the first version of `overflow_diagnostic.py` were caught and corrected. They are
recorded because the first outputs were wrong in ways that would have supported a false candidate.

1. **The day-end path was never invoked.** `analyse()` replayed unit and market actions but never
   ran `_end_of_day`, so `_drop_inventories_to_shed` — the only place overflow is discarded — was
   never called. Every loss read as **0**. A positive control (shed at 100/100, a hand carrying 5
   WHEAT) confirmed the harness detected nothing. After invoking the engine's own day-end sequence
   at `hour == turnsPerDay - 1`, the same game reports **132 units lost**.
2. **Both seats were tallied on every call.** `drop_inventories(private, capacity)` receives both
   seats at the same day end, and the wrapper tallied whichever it was handed, so V50 and V56
   reported identical loss in all 56 games. Fixed by filtering on **object identity** against the
   private dict of the seat under analysis (`tracked[0] = priv[seat]`).
3. **Provenance labels were reversed.** `main()` assigned `v50 = analyse(v56_seat)`. Corrected so
   both the seat and the label come from the recorded agent SHA-256.

A reconstruction check was added at the same time: after the day-end sequence, the reconstructed
shed for the analysed seat is compared against the shed the engine recorded in the next frame's
private view. This is what exposed the remaining problem below.

## Honest measurement, with artifacts excluded

| Measure | V50 | V56 |
|---|---:|---:|
| Paired games | 56 | 56 |
| Games with **clean** shed validation | **56 / 56** | **29 / 56** |
| Lost units, days 6–23 (clean games only) | **16.0** (identical in every game) | **0.0** |
| Lost coin value, days 6–23 (clean games only) | **$991** mean ($387–$1,915) | **$0** |

**V50 loses 16 units per game, worth about $991, on day 23 only.** Composition across all 56 games:
FERTILIZER 280, WHEAT 224, WOOL 224, STRAWBERRY 168. All of it is discarded at the day-23 boundary,
never during days 6–22.

**V56 loses nothing measurable.** In all 29 games where the shed reconstruction validates, its
loss is exactly 0 units and $0. In the other 27 games the reconstruction fails, and the reported
71-unit and 116-unit "losses" appear **only** in those failed games — they are artifacts of my
harness diverging from the recorded stream, not engine loss. They are excluded.

The shed reaches its capacity of 100 in **56 / 56** games on at least one seat, so the capacity
constraint is real and binding; it is simply not being paid in discarded goods on the V56 seat.

## Does this clear the bar for a candidate?

The brief set the threshold at a meaningful repeatable loss, several seeds, with a current-observation
action that prevents it without displacing protected feed or seed. Against that:

- **V56, the seat the candidate would improve, loses 0 units and $0 across 29 validated games.**
  There is nothing to recover. A guard would have nothing to guard.
- **V50's loss is real but real only on day 23**, the final day of the measured window, and it is
  identical (exactly 16 units) in all 56 games, which is the signature of a fixed terminal
  behaviour rather than a capacity accident. The bulk of it is FERTILIZER, which is the cheapest
  item in the game (realized prices in the $18–101 range across the panel) and the largest single
  component of ordinary shed occupancy for both agents.
- Recovering it would mean freeing shed space on day 22 by selling FERTILIZER earlier. That is a
  market-timing change, not an overflow guard, and `docs/V58_TERMINAL_INSIGHT.md` already
  established — and advised against — a terminal-side overlay, on the grounds that the actors are
  already shed-adjacent issuing DROP with no mature crop left. The current finding is consistent
  with that: the loss is FERTILIZER, a collected good, not stranded harvest.

## Why no candidate

Building an overflow-sale guard would mean one of two things, and neither is justified:

- **Guard V56**: nothing to guard. Measured loss is zero on every validated game.
- **Guard V50's day-23 FERTILIZER**: this is a terminal market-timing change, already flagged and
  discouraged by V58, worth roughly $991 on a single day out of 30, and it would require displacing
  market slots in the exact window the terminal overlay already manages. The V89 result is directly
  relevant: the only V56-only market rule that touches this area, `reorder_market(impact_slots)`,
  fires on **1–2 frames in 720** and was shown not to be load-bearing.

The predeclared bar was "meaningful repeatable loss (>~k average/game, several seeds)". V56's
measured loss is $0, and V50's $991 sits at the bottom of that range on one day only, with the
majority in the cheapest product. **Neither justifies a candidate.**

## Prior work audited

- `docs/V57_RESEARCH_2026-09-25.md` records the engine rule: "shed capacity defaults to 100 and
  overflow can be lost", and lists "delay too long risks overflow and stranded terminal goods" as a
  research implication, not a measured finding. This report is the first measurement of it.
- `docs/V58_TERMINAL_INSIGHT.md` audited the terminal actor route and recommended **against** a late
  DROP/harvest overlay, since actors are already shed-adjacent with no mature crop remaining.
- `docs/V60_ORIGINAL_STRATEGY.md` lists a "feasibility and liquidation guard" that should "avoid shed
  overflow", again as design intent without measurement.
- No prior report contains a measured overflow-loss figure, so this does not duplicate prior work;
  it supplies the number those documents assumed.

## Limits

- Loss is measured only for seats whose shed reconstruction validates against the engine's next-frame
  record: 56/56 for V50, 29/56 for V56. The 27 unvalidated V56 games are excluded rather than
  estimated, so V56's loss is bounded at "zero where measurable" and not proven zero everywhere.
- The 29 clean V56 games are a subset of 28 spent seeds; no fresh holdout was used and no seed was
  spent for this report.
- The unit loss is exact engine behaviour, but the coin valuation uses the prevailing market price at
  the day-end tick, which is the price that would have applied to a sale at that moment. Actual
  realizable proceeds would differ if selling had shifted the market.
- FERTILIZER and WHEAT are cheap relative to animal and fruit products, so unit counts and coin
  values rank losses very differently; a unit-count-only reading would overstate the opportunity.
- No candidate was implemented, so the causal question — whether preventing this loss actually
  improves a score — is untested and remains open.

## Artifacts

- `overflow_diagnostic.py` — exact-transition diagnostic with the identity filter and the
  next-frame shed validation
- `overflow_diagnostic.json` — per-game, per-seat, per-day loss with validation status

# V95 — loss-driven throughput candidate: report

**Recommendation: NO-SUBMIT. No candidate earned a promotion panel. All four submission
slots should be conserved.**

Two parts: a correction to the V94 evidence, and a causal loss analysis of the five
official V92 losses that produced one new, non-holding lever — which was then measured,
diagnosed, and found negative.

No Kaggle submission was made. No prior agent, doc or test was modified.

---

## Part 1 — V94 evidence correction

The V94 report quoted sale cash of **$3,448,243** and total spend of **$338,688**. Both
were wrong. They came from `experiments/v94_sell_rate/probe_out/cash_flow.json`, which
sums the market hooks across **both seats** (28 ledgers). The correct denominator for the
Rajusah cash identity is `probe_out/cash_reconciliation.json`, which holds the 14
Rajusah rows.

| Figure | As stated in V94 | Corrected |
|---|---:|---:|
| Sale cash | $3,448,243 | **$1,832,002** |
| Total spend (incl. HIRE) | $338,688 | **$415,898** |
| — of which HIRE | (not shown) | **$77,210** (18.6% of spend) |
| Spend excluding HIRE | $338,688 | $338,688 (this one was right) |
| Final money (= reward) | — | **$1,458,104** |

**The $0.00 cash reconciliation still holds** on all 14 rows (worst absolute unexplained
$0.00, zero cash mismatches), and the per-product sale-cash figures were always
Rajusah-only and remain correct. Only the totals and the spend shares were wrong.
Recomputation: `experiments/v95_loss_driven/recompute_v94_aggregates.py` →
`v94_aggregate_correction.json`.

A second correction, of scope rather than arithmetic. V94 concluded that "holding is
strictly dominated" and offered that as a general property of the game. The evidence
supports something narrower: four specific hold/defer overlays, on 3–5 paired spent seeds
each, all lost cash, and shed saturation (measured at shed+in-hand 102 against capacity
100) is the best available mechanism for those losses. That is not a theorem about every
strategy, every seed or every opponent. The V94 report has been amended to say so.

Corrected V94 report: `experiments/v94_sell_rate/REPORT.md`
sha256 `dd094a0369d8ed37082166d2514a1378e020cf17e0cc829ff3459056c289e81f`.

---

## Part 2 — the loss-to-intervention chain

### Step 1: there is no execution difference to exploit (hard negative)

The assignment asked for a controllable difference in asset utilization or worker
execution between the five losses and matched wins, focused on days 12–23. I measured it
directly (`analyze_losses.py`, exact loader alignment, zero cash mismatches on all 14):

| Metric, whole game | All 14 replays |
|---|---:|
| WATER actions | 1096 — **identical in every game** |
| CARE actions | 397 — identical |
| FEED actions | 346 — identical |
| Worker moves | 3039 — identical |
| Harvested units | 744 — identical |
| Day-12 animals / crop tiles | 17 / 57 — identical |
| PASS | 685–686 |

V92's execution is **byte-identical in every game, win or loss**. And the V83
throughput separator runs the *wrong way* here: days 12–23 sell-per-animal is **3,691 in
losses vs 3,623 in wins**.

The cause is structural and was already known: V50/V92 is a 719-entry open-loop action
tape indexed by `step`, not a decision function. It executes the same work against a
different board and a different market, so the outcome spread is carried entirely by the
shared price path, which the tape does not control. **No "fix the mistake" intervention
is available on this lineage, because there is no mistake.**

### Step 2: input starvation is also closed

`docs/V83_ELITE_MECHANISM.md` identifies the elite separator as winners applying
**3.40x more fertilizer** and buying **1.80x more wheat** on identical assets. So the
obvious V95 lever is "V92 is short of feed or soil". It is not:

- FEED actions that failed for want of WHEAT: **0** (all 14 games)
- FERTILIZE actions that failed for want of fertilizer: **0**
- Animals lost to escape (2 unfed days = permanent deletion): **0**
- WATER actions wasted on a non-plant tile: **0**

There is no unmet demand for extra WHEAT or FERTILIZER to relieve. Buy-more-input cannot
help a farm that is already fully supplied.

### Step 3: the one real asymmetry, and a break-even that looked positive

The only non-zero, non-constant number in the input picture:

| | 14 games |
|---|---:|
| FERTILIZER collected free from animals | 5,222 |
| FERTILIZER applied to tiles | 1,400 (26.8%) |
| FERTILIZER **sold** | 4,438 for **$215,146** |
| FERTILIZER discarded unused | 35 |

A first reading looked like a large waste ("3,822 units of yield thrown away"). That
reading was wrong and I caught it before building on it: the fertilizer is not idle, it is
**monetized** — 11.7% of all sale cash.

The real question is a margin question, and it has a clean break-even. FERTILIZE
consumes one unit and makes a watered in-window tile yield +2 instead of +1
(kaggriculture.py 442-443, 475-482), so applying a collected unit is worth one extra crop
unit. Against measured realized prices (not peak quotes — the mistake that killed V93 and
V94):

| Product | realized $/unit | vs FERTILIZER $48.48 |
|---|---:|---:|
| MELON | 218.73 | +170.25 |
| STRAWBERRY | 142.65 | +94.17 |
| MILK | 139.33 | +90.85 |
| WOOL | 69.32 | +20.85 |
| CARROT | 67.42 | +18.95 |
| **WHEAT** | **40.83** | **−7.65** |

So five of six crops favour applying. This is a genuine, non-holding lever: it converts
inventory V92 already has into yield rather than parking stock, so it does not run into
the shed-saturation mechanism that sank the hold family.

### Step 4: build, verify, and measure — v1 loses badly

`candidate.py` embeds the frozen V92 source verbatim (sha256 verified byte-identical)
and adds one overlay: substitute FERTILIZE for a displaceable action when the actor is
carrying fertilizer and standing on an in-window crop tile. 13 self-checks pass, including
"protected actions never displaced", "market list untouched", "input not mutated", and a
proof that the Kaggle loader binds the entrypoint.

Dev panel, 11 already-spent seeds, both seats, exact loader, V50/V92/V56 untouched:

| Arm | Games | Record | Mean paired margin | Range | Errors |
|---|---:|---|---:|---|---:|
| **V95 v1 vs V92** | 22 | **0W-22L-0D** | **−6,926** | −9,585 .. −5,428 | 0 |

### Step 5: diagnose v1's failure, fix it, re-measure

`diagnose_overlay.py` replayed the 22 retained games and found the cause exactly:

> **97% of the overlay's FERTILIZE actions (2,640 of 2,728) landed on a tile that was not
> already watered that day.**

The engine pays the fertilizer bonus only inside a WATER action. FERTILIZE consumes the
unit unconditionally. So v1 was spending fertilizer on tiles whose bonus would never
materialise, while displacing work V92 was already doing.

v2 requires the tile to be `watered_today` and not already fertile. Two regression tests
were added to the builder for exactly this case.

| Version | Rule | Games | Record | Mean margin | Range |
|---|---|---:|---|---:|---|
| v1 | any in-window tile | 22 | 0W-22L | −6,926 | −9,585 .. −5,428 |
| **v2** | **+ watered today, not already fertile** | 22 | 0W-22L | **−361** | **−299 .. −399** |
| v3 | v2 minus WHEAT | 22 | 0W-0L-22D | **+0** | +0 .. +0 |

The fix removed **95% of the loss**, which confirms the diagnosis was right. The residual
is small but unmistakably negative and low-variance, so it is signal rather than noise.

### Step 6: attribute the residual, and stop

The v2 attribution shows the fert-apply economics are not where the loss comes from:

- v2 issued 2,728 FERTILIZE actions, of which only **224** landed on a tile the engine
  would actually pay a bonus on.
- The estimated gross value of those 224 correct applications is **−$88 across 22 games**
  (about −$4/game), 66 of them on WHEAT where applying provably loses.
- The measured paired margin is **−361/game, −7,942 total**.

Roughly **$7,854 of the $7,942 loss is opportunity cost**: the overlay replaced 2,728
working actions to chase 224 near-worthless applications. The lever is negative because
the action it displaces is worth more than the yield it creates.

v3 removed WHEAT, the only provably value-destroying crop, and the result was **22/22
exact draws at +0** — a byte-identical no-op (11 distinct replay hashes over 22 games, the
ab/ba pairs matching exactly, confirming engine determinism). Per the assignment, a no-op
is not progress and is reported as such.

The fertilizer family is closed.

---

## 3. Results table (all exact-loader, zero errors everywhere)

| Version | Opponent | Seeds | Games | W-L-D | Mean margin | Median | Positive | Errors |
|---|---|---|---:|---|---:|---:|---:|---:|
| V95 v1 | V92 | 11 spent, both seats | 22 | 0-22-0 | −6,926 | −5,909 | 0/22 | 0 |
| V95 v2 | V92 | 11 spent, both seats | 22 | 0-22-0 | −361 | −354 | 0/22 | 0 |
| V95 v3 | V92 | 11 spent, both seats | 22 | 0-0-22 | 0 | 0 | 0/22 | 0 |

Runtime, v2 arm: mean 45 s, max 52 s per game. No timeouts, no candidate errors, no
opponent errors, no infrastructure errors in any of the 66 games.

**No promotion panel was run and no holdout was consumed**, because no candidate
produced a credible positive paired cash signal. Freezing a gate and spending fresh
seeds on a signal already measured as negative would waste a scarce resource and risk the
appearance of validation. The holdout seed set remains unspent and available.

---

## 4. Failed hypotheses (explicit)

1. **Fix a worker-execution gap in the losses.** No gap exists: V92's water/care/feed/
   move/harvest counts are identical in all 14 games, and losses show *higher* days-12–23
   sell-per-animal than wins.
2. **Buy more WHEAT/FERTILIZER** (the V83 elite lever). V92 has zero unmet input demand;
   every feed and fertilize succeeds and no animal ever escapes.
3. **Apply free collected fertilizer instead of selling it** (v1). Margin looked
   positive on price, but 97% of applications missed the watered-tile condition and the
   bonus never paid. −6,926/game.
4. **Apply it only to tiles the engine will actually pay for** (v2). Correct
   mechanism, 95% repair, but still −361/game because the displaced action is worth more
   than the +1 yield.
5. **Apply it only to crops where applying beats selling** (v3). WHEAT is the only such
   crop and removing it produced a byte-identical no-op, 22/22 draws.

## 5. What this establishes for a future attempt

Three structural facts, each measured rather than assumed, that any successor should
start from:

1. **V92 is an open-loop tape, not a decision function.** It cannot adapt to a board or a
   market, and its action counts are identical in every game. An improvement therefore
   has to be a post-hoc overlay on the action stream, exactly as V92, V93, V94 and V95
   each were — and the overlay's own reach, not the tape's, is the binding constraint.
2. **The shed is the binding resource, not price.** At end of day the farm already
   carries shed+in-hand of 102 against a capacity of 100, with 2 units deleted per game.
   Anything that parks stock is destroyed, and anything that displaces working actions
   must beat the value of the action it replaced.
3. **The remaining headroom is not in this lineage's inputs.** Execution is saturated,
   input demand is met, terminal liquidation already leaves $0 stranded, overflow is down
   to 2 units, and the only products priced above fertilizer are already being harvested
   at the tempo the tape dictates. The 15% elite execution edge V83 documents is a
   difference in *worker routing quality*, which a fixed action tape cannot express and
   which a local panel of this size cannot resolve.

## 6. Files and hashes

New files are confined to `experiments/v95_loss_driven/`. Prior agents are byte-unchanged,
verified against the values frozen in the V92 holdout plan.

| Artifact | SHA-256 |
|---|---|
| `experiments/v95_loss_driven/candidate.py` (V95 v2, not promoted) | `3cd4bb8a264974e904ec55e6d41aede25b4a0023bd01066b8481e0802ec3fe7f` |
| `experiments/v95_loss_driven/candidate_overlay.py` (rule source) | `563553f794302b50883d25331e800575a5d925b9c9a5c2f4f59c76a58ddf7c6b` |
| `experiments/v94_sell_rate/REPORT.md` (corrected) | `dd094a0369d8ed37082166d2514a1378e020cf17e0cc829ff3459056c289e81f` |
| `experiments/v95_loss_driven/v94_aggregate_correction.json` | `48a9fd4fcf303d96f303f6a805ce75aba312ff9ee4cd7cf5faf80436185fcf55` |
| V92 incumbent (unchanged) | `0d5d356baa25703f1a7b753527d1b39e1c7d63478985913be5b3c2550261b806` |
| V93 (unchanged) | `fa81a78e79d1d3639f036102a212f84c9334971bc34b7d1e1f11c1d53591c8d5` |
| V94 candidate (unchanged) | `a7ec12eb79fee948041d88fb01d2ffebd103080f9d4a0fa562deefe8dd85dccf` |
| V56 benchmark (unchanged) | `d9e9670921b62afedfa8cbc7086d2a2ec19e153ee26006cef477eadd462bd19c` |
| V50 frozen base (unchanged) | `e6b50128e023e3b9fafa1841e4cd520c5e581acb48e8628657585c18272eab2b` |

Audit and analysis scripts: `recompute_v94_aggregates.py`, `analyze_losses.py`,
`input_feasibility.py`, `fert_gap.py`, `fert_breakeven.py`, `build_candidate.py`,
`probe_gate.py`, `diagnose_overlay.py`, `attribute_residual.py`, `probe_v3.py`.
Evidence: `loss_analysis.json`, `input_feasibility.json`, `fert_gap.json`,
`v94_aggregate_correction.json`, `overlay_diagnosis.json`, `probe_dev_results.json`,
`probe_v3_results.json`, `candidate_build.json`, plus per-game records under
`runs/dev_v95_vs_v92/` and `runs/dev_v3_vs_v92/`.

Engine: pinned kaggriculture 1.32.7. All games run through `simulation.tournament` /
`simulation.match_worker`, the exact Kaggle loader. Every replay audit required zero cash
mismatches on both ledgers. The V88 replay joins were not used.

## 7. Recommendation

**NO-SUBMIT.** Do not spend any of the four remaining submission slots on this work. V92
remains the strongest verified agent. The four remaining submission slots should be
conserved until a candidate shows a positive paired cash signal on development seeds,
which this work did not produce.

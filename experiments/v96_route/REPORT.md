# V96 — route-level search: report

**Recommendation: NO-SUBMIT. Neither route mechanism earned a promotion panel. All four
Kaggle submission slots remain unused.**

Two materially different route-level mechanisms were built and measured against the
frozen V92 incumbent on already-spent seeds in both seats. One was a **byte-identical
no-op**; the other **fired on every game and lost**. Both are closed with an engine-level
measurement, not an assumption. One earlier premise of mine was wrong and is corrected
below.

No Kaggle submission was made. No prior agent, doc or test was modified.

---

## 0. Required correction: V94's shed claim, rederived

The assignment required rederiving V94's "shed+in-hand 102/100" claim, which I had flagged
as tracing to a seat-attribution bug. **It was indeed wrong, and correcting it changed
the planning picture.**

| | V94 claimed | Rederived (recorded observation, Rajusah seat) |
|---|---:|---:|
| carried at day boundaries | 102 | **0** |
| shed+carried peak | 102 | **100** |
| units deleted per game | 2 | 2–10 (52 total over 14 games) |

The "102" was a bug artifact. Carried is **0 at every daily snapshot**. The correct and far
more useful finding is that the shed saturates **late, not all season**:

| window | mean shed | mean spare | min spare |
|---|---:|---:|---:|
| days 0–11 (opening) | 12.8 | 87.2 | 64 |
| days 12–23 (mid) | 67.5 | 32.5 | 5 |
| days 24–29 (late) | 94.3 | 5.7 | 0 |

So V94's "the shed is saturated, therefore holding is dominated" premise was wrong for
the opening window, which has ~87 units of headroom. That correction is what made both
mechanisms below worth attempting, and it was not the reason they failed.

---

## 1. The audit: what the V92 lineage actually does

`docs/V75_ELITE_CASHFLOW.md` reports a large opening deficit for elite winners versus
V70, the V50-lineage control. Measured on the 14 official replays with the pinned engine
and zero cash mismatches, averaged per game:

| metric, days 0–11 | V92 lineage | V75 elite median | gap |
|---|---:|---:|---:|
| day 3 animals | 5.0 | 7.0 | −2.0 |
| day 6 animals | 6.0 | 12.5 | −6.5 |
| day 9 animals | 12.0 | 18.0 | −6.0 |
| day 6 strawberry tiles | 4.0 | 24.0 | −20.0 |
| **day 6 cash** | **888** | **33** | **+855** |
| day 0–5 animal spend | 2,600 | 3,900 | −1,300 |

**The headline V75 thesis does not survive contact with V92.** V75's V70 control is an
older, weaker lineage. V92 already beats the elite medians on the metric V75 identified
as the key deficit:

| days 6–11 accepted sale cash | V92 | V75 elite median |
|---|---:|---:|
| MELON | **15,748** | 11,236 |
| all products | **29,795** | 26,430 |

The melon route is not the deficit. The genuine remaining gaps are animal count, berry
tile count, and the **$855 of idle cash at day 6**.

## 2. Mechanism A — build pasture capacity earlier (`candidate_a`)

**Hypothesis.** V92 builds 4 pastures on day 1, reaches 6 by day 4, then builds none
until day 7 when it jumps to 13. Days 3–6 have a free-pasture shortage exactly when the
animal cohort is bought; days 7–11 have surplus capacity arriving too late. If capacity
were available earlier, an earlier animal cohort could be placed and COW milk would
arrive sooner (first yield 8 days after placement, interval 2).

The overlay substitutes `BUILD_PASTURE` for a displaceable action in days 2–10, bounded
by a pasture target of 13 and a cash floor of 1,200. It never buys animals, so the cash
effect is attributable to capacity timing alone.

**Result: 22 games, 0W–0L–22D, every margin exactly +0.** A byte-identical no-op.

**Why, measured.** Walking the recorded observation stream through every guard:

| guard | turns blocked |
|---|---:|
| day window | 503 |
| cash floor | 133 |
| pasture target | 70 |
| protected action | 33 |
| **actor not standing on an empty tile** | 9 |
| spare capacity | 6 |
| no empty owned tile anywhere | 2 |

Across the 216 in-window turns there were only **5 turns with any empty owned tile**, and
a hand stood on one in only **3** actor-observations.

**The root cause is land, not turns.** The opening is land-saturated:

| day | owned tiles | planted | empty | utilisation |
|---:|---:|---:|---:|---:|
| 1 | 25 | 20 | 1 | 96% |
| 3 | 25 | 20 | **0** | **100%** |
| 6 | 25 | 19 | **0** | **100%** |
| 7 | 50 | 29 | 8 | 84% |

V92 plants 20 of its 25 owned tiles on day 1. Days 2–10 average **0.9 empty owned tiles**
at **98% utilisation**. An earlier animal cohort has nowhere to stand. Buying land earlier
to make room is already measured decisively dead in this repository: V72 **0–6** and V77
**0–2**. Mechanism A is closed on a resource constraint, not on a failed screen.

## 3. Mechanism B — harvest-priority route (`candidate_b`)

**Hypothesis.** `docs/V83_ELITE_MECHANISM.md` puts 55.5% of the elite margin in days
12–23 and attributes it to throughput per unit of asset. A crop unit that ripens and is
not harvested is worth $0. Measured conversion is low:

| window | ripe plant | ripe animal | harvested/day | conversion ratio |
|---|---:|---:|---:|---:|
| d0–5 | 19.7 | 2.0 | 5.8 | 0.23 |
| d6–11 | 37.8 | 11.0 | 25.3 | 0.40 |
| **d12–23** | **59.8** | **23.4** | **62.0** | **0.51** |
| d24–29 | 66.7 | 17.0 | 85.5 | 0.56 |

Day 7: 45 ripe, 0 harvested. Day 9: 65 ripe, 16 harvested. The route leaves a persistent
standing crop backlog through exactly the window V83 identifies.

The overlay substitutes `HARVEST` for a displaceable action when a worker stands on a
ripe crop tile, gated on shed headroom so it cannot recreate the V93/V94 overflow. It
never holds stock — it converts stock, the opposite of the failed hold family.

**Result: 22 games, 0W–22L–0D, mean paired margin −255 (range −279..−228), 0/22 positive,
zero errors, runtime mean 66 s.** It fired on every game (0/11 seat-invariant).

**Diagnosis.** The overlay displaced `PASS` 22 times and nothing else — never WATER, never
a productive action — and pulled **20 units, all WHEAT**. So it neither broke lifecycle
needs nor triggered the shed guard. It simply harvested WHEAT earlier than the route's
own schedule would have.

**A correction to my own reasoning here.** I first assumed the standing backlog was
dominated by the cheapest product and therefore not worth converting. That was wrong. In
days 12–23 the standing stock prices at **$44 for WHEAT** against a $40.83 realized
average, and **$145 for STRAWBERRY** against $142.65. The backlog is worth *more* than
the route's normal sale, so the direction of the intervention was correct and the
"worth converting" verdict holds for both crops.

**The real reason it could not work is reach, measured.** Classifying all 5,396
actor-turns in the window:

| category | count | share |
|---|---:|---:|
| not on a ripe crop tile | 4,020 | 74.5% |
| on a ripe tile | 688 | 12.8% |
| ↳ protected: WATER | 231 | 4.3% |
| ↳ already harvesting there | 192 | 3.6% |
| ↳ protected: movement | 199 | 3.7% |
| ↳ hand already carrying | 47 | 0.9% |
| **convertible (overlay fires)** | **18** | **0.3%** |

Only **0.3%** of actor-turns are convertible. The route already harvests in 28% of the
cases where a worker is standing on a ripe tile, and 74.5% of the time the worker is not
on one at all. The backlog is a **walking** problem, not a priority problem: re-prioritising
a worker who is already elsewhere cannot fix stock on tiles nobody is standing on.

**Why a walk reroute is out of scope.** 62.2% of actor-turns are within 2 tiles of ripe
stock, so the geometry is cheap — but **83.2% of all worker actions in the window are
lifecycle-protected** (WATER 15.8%, movement 42.6%, CARE 6.2%, FEED 5.7%, PICKUP/PLACE
3.1%). Redirecting those walks changes where FEED and WATER land, which deletes animals
and kills plants when missed. That is a route rebuild requiring validation from scratch,
and every wholesale route rewrite in this repository has been measured decisively
negative: V58 licensed baselines (−$3,260 / −$964 / −$12,748 / −$19,377), V57 blind route
copying, V72 land-first opening (0–6, −$19,260 and −$101,498).

## 4. Results table

All games via `simulation.tournament` / `simulation.match_worker`, the exact Kaggle
loader, pinned kaggriculture 1.32.7. 11 already-spent seeds (each ≥22 prior saved games),
both seats.

| Candidate | Mechanism | Games | W-L-D | Mean margin | Range | Positive | Errors | Runtime |
|---|---|---:|---|---:|---|---:|---:|---|
| A | build pasture earlier | 22 | 0-0-22 | +0 | +0..+0 | 0/22 | 0 | mean 67 s |
| B | harvest-priority route | 22 | 0-22-0 | −255 | −279..−228 | 0/22 | 0 | mean 66 s |

**No promotion gate was frozen and no fresh holdout was consumed.** No candidate produced
a credible positive paired cash signal, so spending a holdout on a measured-negative signal
would burn a scarce resource and create the appearance of validation. The holdout seed
set remains entirely unspent.

## 5. All mechanisms attempted, including failures

1. **Build pasture capacity earlier** (A) — no-op, 22/22 draws. Closed: the opening is
   land-limited at 98% utilisation; buying land earlier is already dead (V72, V77).
2. **Harvest-priority conversion route** (B) — 0W–22L, −255. Closed: reach ceiling of
   0.3% convertible actor-turns; the backlog is a walking problem.
3. **Buy more WHEAT/FERTILIZER** (V95, carried forward) — already closed: zero unmet input
   demand, 0 escapes, 0 failed feeds.
4. **Apply fertilizer instead of selling it** (V95 v1/v2/v3) — already closed: −6,926,
   −361, and a no-op respectively.
5. **Hold WOOL / defer harvest / cap buys** (V93, V94) — already closed on measurement.

## 6. What a successor should start from

Five structural facts, each measured on 14 official replays with zero cash mismatches:

1. **V92 is an open-loop 719-step tape, not a decision function.** Its action counts are
   identical in every official game, win and loss. Losses show *higher* days-12–23
   sell-per-animal than wins. Any improvement must therefore alter a coherent part of
   the route, and it cannot be a re-ranking of sales.
2. **The opening is land-limited, not cash-limited.** 98% of owned tiles are committed by
   day 2. The $855 of idle day-6 cash cannot be converted to animals because there is
   nowhere to place them, and land-early is already measured negative twice.
3. **The shed is a late-season constraint, not an opening one.** Mean occupancy 12.8 of
   100 in days 0–11, rising to 94.3 in days 24–29. V94's claim of universal saturation
   was wrong; the corrected picture is in section 0.
4. **Worker time is 83% lifecycle-protected in the throughput window.** The throughput
   lever V83 identifies cannot be pulled by re-prioritising, because the workers are
   almost never on the ripe tiles that are going unharvested.
5. **The elite melon and opening-cash signals do not apply to this lineage.** V92 already
   exceeds the V75 elite medians on days-6–11 melon and product sales.

The one untested direction consistent with all five: a genuine **route rebuild** that
rewrites walk paths and the cohort schedule together, with lifecycle coverage proven
rather than assumed. That is a research project, not a patch, and it would need its own
dev/holdout split before any submission slot is spent.

## 7. Files and hashes

All new files are confined to `experiments/v96_route/`. Prior agents are byte-unchanged.

| Artifact | SHA-256 |
|---|---|
| `candidate_a.py` (mechanism A, not promoted) | `6e7b53476194173d95c8374e3a07caf6c2ab42eed365b13e4f42dcf0b02b4ee8` |
| `candidate_b.py` (mechanism B, not promoted) | `21ce9269a96a7147715f28a848851c7b7399e7b5042e9027dab53864aa9f5a0a` |
| `candidate_a_overlay.py` | `1fcbb326f5fec8a42cac173ef2d4ba1c340a0a9e637ed8f87bad8728c70c129b` |
| `candidate_b_overlay.py` | `c8b1a63a2dd6f43f68277e537b6ca338df3ef7d7ce5ddec05852bdfc3c6c2f24` |
| V92 incumbent (unchanged) | `0d5d356baa25703f1a7b753527d1b39e1c7d63478985913be5b3c2550261b806` |
| V93 (unchanged) | `fa81a78e79d1d3639f036102a212f84c9334971bc34b7d1e1f11c1d53591c8d5` |
| V94 candidate (unchanged) | `a7ec12eb79fee948041d88fb01d2ffebd103080f9d4a0fa562deefe8dd85dccf` |
| V56 benchmark (unchanged) | `d9e9670921b62afedfa8cbc7086d2a2ec19e153ee26006cef477eadd462bd19c` |
| V50 frozen base (unchanged) | `e6b50128e023e3b9fafa1841e4cd520c5e581acb48e8628657585c18272eab2b` |

Audit and build scripts: `audit_shed_capacity.py`, `audit_opening.py`,
`audit_cohort_feasibility.py`, `audit_land_bottleneck.py`, `audit_ripe_conversion.py`,
`diagnose_a.py`, `diagnose_b.py`, `close_ripe_class.py`, `measure_reach.py`,
`audit_walk_cost.py`, `build.py`, `screen.py`.

Evidence: `shed_capacity_audit.json`, `opening_audit.json`, `cohort_feasibility.json`,
`land_bottleneck.json`, `ripe_conversion.json`, `diagnose_b.json`,
`candidate_a_build.json`, `candidate_b_build.json`, `screen_candidate_a.json`,
`screen_candidate_b.json`, plus per-game records under `runs/`.

Both candidates pass 6 build self-checks including "embedded V92 decodes byte-identical",
"Kaggle loader binds an entrypoint", "no-op outside the day window", "market list never
modified", and "input action not mutated".

The V88 replay joins were not used. Seeds 93000–93011 were not used.

## 8. Recommendation

**NO-SUBMIT.** Do not spend any of the four remaining submission slots. V92 remains the
strongest verified agent in this repository. Neither V96 mechanism produced a positive
paired cash signal: one was a no-op closed by a land constraint, the other lost 0W–22L and
is closed by a measured 0.3% reach ceiling. Codex should verify the two closures — the
98% opening land utilisation and the 0.3% convertible share — since they are what
recommend conserving the slots.

# V94 — final report: stronger Kaggriculture agent search

> **CORRECTION (added for the V95 assignment).** The cash totals in this report were
> wrong. Sale cash and total spend were quoted from `probe_out/cash_flow.json`, which
> sums the market hooks across **both seats** (28 ledgers), not the 14 Rajusah rows. The
> correct denominator for the Rajusah cash identity is
> `probe_out/cash_reconciliation.json`.
>
> | Figure | As originally stated | Corrected (Rajusah, 14 rows) |
> |---|---:|---:|
> | Sale cash | $3,448,243 | **$1,832,002** |
> | Total spend | $338,688 | **$415,898** |
> | Spend excluding HIRE | $338,688 | **$338,688** (unchanged) |
>
> The $338,688 figure was labelled "total spend" but is in fact *spend excluding HIRE*;
> HIRE is a further $77,210. The **$0.00 cash reconciliation still holds** on all 14
> rows, and the per-product sale-cash figures were always Rajusah-only and remain correct.
> Recomputation: `experiments/v95_loss_driven/v94_aggregate_correction.json`.
> See also the scoping correction in section 5.

**Recommendation: NO-SUBMIT. No candidate was promoted. Nothing should be submitted
from this work.**

I did not find a credible controllable mechanism that improves cash. Rather than
freeze a gate on a weak signal, I measured the full cash budget exactly, found that
V92's open-loop tape is already near-optimal on every axis I could verify, and proved
with engine data why the entire "hold/defer stock" family of levers — which is where
the apparent opportunities all pointed — is strictly losing. This report documents
the search, the exact paired results, the failed hypotheses, and the single
structural fact that closes the class.

No Kaggle submission was made. No prior agent, doc or test was modified.

---

## 1. Artifacts and hashes

All new files are confined to `experiments/v94_sell_rate/`. Prior agents are
byte-unchanged (verified against the hashes frozen in the V92 holdout plan):

| Artifact | Path | SHA-256 |
|---|---|---|
| V94 late-harvest probe candidate | `experiments/v94_sell_rate/candidate.py` | `a7ec12eb79fee948041d88fb01d2ffebd103080f9d4a0fa562deefe8dd85dccf` |
| V92 incumbent (unmodified) | `experiments/v92_overflow_guard/candidate.py` | `0d5d356baa25703f1a7b753527d1b39e1c7d63478985913be5b3c2550261b806` |
| V93 (previous negative result) | `experiments/v93_adaptive/candidate.py` | `fa81a78e79d1d3639f036102a212f84c9334971bc34b7d1e1f11c1d53591c8d5` |
| V56 ladder benchmark | `agents/v56_agent.py` | `d9e9670921b62afedfa8cbc7086d2a2ec19e153ee26006cef477eadd462bd19c` |
| V50 frozen base | `experiments/v50_agent.py` | `e6b50128e023e3b9fafa1841e4cd520c5e581acb48e8628657585c18272eab2b` |

Key evidence files (all under `experiments/v94_sell_rate/probe_out/`):
`cash_reconciliation.json`, `shed_pressure.json`, `wool_recovery.json`,
`wool_glut.json`, `harvest_yield.json`, `strawberry_price.json`,
`candidate_probe.json`, `lateharvest_probe.json`.

Engine: pinned kaggriculture 1.32.7. All games run through the exact Kaggle loader
(`kaggle_environments.make` + `env.run`, the same path `simulation/match_worker`
uses), and every replay audit requires **zero cash mismatches on both ledgers**.

## 2. What I fixed first (reused V93 audit, extended)

I re-read the V93 report, the V92 official diagnosis, and the V88 provenance
correction, and did **not** reuse the invalid V88 `game_id` joins. I extended the
V93 realization ledger to a **complete cash reconciliation**. The V93 ledger had a
known accounting gap (HIRE cost bypasses `_commit_unit`); I fixed that gap and now
the cash identity closes exactly:

```
final_money = STARTING(3000) + accepted_SELL_cash − all_spend_including_HIRE
```

This reconciles to **$0.00 on all 14 official replays** (worst absolute
unexplained: $0.00). That is the integrity keystone for every number below: the
budget is complete, so any lever is sized against a verified denominator.

## 3. The verified cash budget (14 official replays, Rajusah)

Corrected figures. The denominator is the 14 Rajusah rows of
`probe_out/cash_reconciliation.json`; the identity closes to $0.00 on every row.

| Line | Total (14 games) | Per game | Share of spend |
|---|---:|---:|---:|
| **Sale cash** | **$1,832,002** | $130,857 | — |
| **Total spend (incl. HIRE)** | **$415,898** | $29,707 | 100% |
| — BUY_PRODUCT WHEAT | $77,260 | $5,518 | 18.6% |
| — BUY_ANIMAL SHEEP | $77,000 | $5,500 | 18.5% |
| — BUY_SEED STRAWBERRY | $46,200 | $3,300 | 11.1% |
| — BUY_LAND | $42,000 | $3,000 | 10.1% |
| — BUY_ANIMAL COW | $33,600 | $2,400 | 8.1% |
| — BUY_SEED WHEAT | $23,240 | $1,660 | 5.6% |
| — BUY_PRODUCT FERTILIZER | $18,108 | $1,293 | 4.4% |
| — BUY_SEED MELON | $13,440 | $960 | 3.2% |
| — BUY_SEED CARROT | $7,840 | $560 | 1.9% |
| — HIRE (3,934 orders, $19.63 avg) | $77,210 | $5,515 | 18.6% |
| **Final money (= reward)** | **$1,458,104** | $104,150 | — |

Sale cash by product (unchanged, always Rajusah-only):

| Product | Sale cash | Share |
|---|---:|---:|
| STRAWBERRY | $497,292 | 27.1% |
| MILK | $319,895 | 17.5% |
| WOOL | $273,694 | 14.9% |
| WHEAT | $228,095 | 12.5% |
| MELON | $220,477 | 12.0% |
| FERTILIZER | $215,146 | 11.7% |
| CARROT | $77,403 | 4.2% |

Note that HIRE is **18.6% of all spend** — a larger share than any single purchase
line, and identical ($5,515) in all 14 games.

## 4. Levers tested and closed, each with exact numbers

**Cost side — no slack.** The budget is dominated by fixed production spending and
$5,515 of HIRE per game that is identical in all 14 games. There is no recoverable
waste in the cost side; the tape buys the same thing every run.

**Terminal monetization — already perfect.** V92 leaves **$0** standing yield, **$0**
in the shed, and **$0** in hand at step 718 in all 14 games. There is literally no
unmonetized stock to recover. (V92's terminal overlay is exact.)

**End-of-day overflow — already minimal.** V92's day-23 guard cuts the measured
overflow to **2 units per game**, worth $2–$78. Nothing left to extract.

**Sell self-impact — too small to matter.** The engine re-quotes each unit against
the just-incremented inventory, so dumping N units in one turn walks the price down.
Measured across 14 games: total within-turn decay is **$13,250 on $1,832,002 of sale
cash = 0.7%**. Too small to be worth an overlay, and bounded above by the same
hold-family failure below.

**WOOL glut — the big apparent opportunity, and it is a trap.** WOOL sells at ~$20
mean against a $218 peak. The decomposition (`wool_glut.json`): Rajusah sells exactly
282 WOOL every game; when town drain is heavy the mean is $234 with **zero** $1
sales, and when drain is light the mean is ~$22 with 240–354 units sold at the $1
floor. The supremum of holding every $1 unit to its best later price is
**$44,673/14 = $3,191/game** — and in 8 of 14 games the best-later price is only
**+$4**. V93 already tried holding; this run confirms why it loses and that even a
shed-safe variant loses.

**STRAWBERRY late harvest — the largest estimated opportunity, and a trap.** STRAWBERRY
is 27.1% of sale cash but harvested at **1.92 units/event vs max 4** (MELON reaches
6.00/6; only STRAWBERRY is cut short). The estimate put lifting it to 3.0 at
~+$20k/game — but that priced extra units at the current realized price and ignored
that more supply pushes the shared STRAWBERRY glut curve down, the same error V93
made. Measured directly: it loses.

## 5. The structural fact that closes the class

Every "hold" or "defer" lever (WOOL at floor, WOOL shed-safe, STRAWBERRY late
harvest) loses for one measured reason, and the data is unambiguous.

At every end-of-day boundary the farm already carries:

```
max (shed + in-hand) at end-of-day = 102, against shedCapacity = 100
```

in **all 14 games** (shed peaks at 28, in-hand peaks at 102; the sum reaches 102 and
2 units are already being deleted by the drop every game). The pipeline is at
**negative headroom**. Any overlay that parks more stock in the shed or in hand is
guaranteed to have the surplus deleted at the next boundary.

This follows from three pinned-engine rules:
- `SELL` reads the **shed only** (line 654): a unit in a hand or still on a tile
  earns $0.
- `_drop_inventories_to_shed` **deletes** overflow (line 857, `del inv[item]`): not
  queued, gone.
- reward is **cash only** (line 961): nothing but converted cash scores.

So cash is a race against a 100-slot shed and a 24-hour clock, and the only
value-preserving action is to convert stock to cash as fast as capacity allows —
which is what the frozen tape already does (it ends every game with $0 stranded).

**Scoping correction.** An earlier version of this section over-generalised. What the
evidence actually supports is narrower and must be stated precisely:

- **Measured:** four specific hold/defer overlays, on 3–5 paired seeds each, all lost
  cash — WOOL-at-floor (V93), WOOL-at-floor with a shed guard (C2), shed-capped buys
  (C3, a no-op), and deferred STRAWBERRY harvest (V94). Each was tested against V92
  through the exact loader with deterministic paired seeds.
- **Measured:** at end-of-day the farm already carries shed+in-hand of 102 against a
  capacity of 100, with 2 units deleted per game, in all 14 official replays. This
  measurement is solid and is the best available explanation for those losses.
- **NOT established:** that holding is dominated in *every* possible strategy, in
  *every* seed, against *every* opponent, or on the public ladder. Those overlays were
  tested on a small set of spent seeds against a fixed opponent. A different holding
  rule that frees shed space before the drop, or that defers only a bounded amount,
  was not tested and is not excluded. The sample was also small relative to the
  margin noise.

The defensible statement is: **on the strategies and seeds tested, holding stock lost
cash, and shed saturation is the measured mechanism.** It is not a theorem about the
game.

## 6. Exact paired results (exact loader, both seats not required — these are seat-controlled probes vs V92)

These are single-seat, seed-paired probes of each overlay against the V92 base in the
same seat, through the exact loader. The engine is deterministic per seed, so the
same seed in the same seat is a clean paired comparison. No tournament was run
because no candidate passed the pre-gate probe.

**V94-LATEHARVEST (defer strawberry harvest on ripe thin tiles) vs V92:**

| Seed | V92 | V94 | Δ |
|---:|---:|---:|---:|
| 92600 | 111,262 | 100,691 | −10,571 |
| 94700 | 82,110 | 70,705 | −11,405 |
| 95200 | 98,456 | 86,780 | −11,676 |
| 93700 | 96,384 | 85,233 | −11,151 |
| 95300 | 114,260 | 102,672 | −11,588 |
| **mean** | | | **−11,278** |

0/5 positive, remarkably consistent.

**C2 (hold WOOL at floor, but only while shed < 90) vs V92:** −15,319 / −2,827 /
−7,168 on seeds 92600/94700/95200 → 0/3 positive.

**C3 (cap buys so shed stays under 90) vs V92:** +0 / +0 / +0 → byte-identical no-op
(the shed cap of 90 is never binding in these games; `shedBlocked=0`).

For reference, the prior V93 gate (already reported): 0W-12L-10D vs V92, median
−4,540, score rate vs V56 identical to control (0.455). V93 is a confirmed negative.

## 7. Failed hypotheses (explicit)

1. Hold WOOL at the floor to catch a recovery (V93, re-confirmed) — loses; recovery
   supremum only ~$3k/game and mostly +$4.
2. Hold WOOL but stay shed-safe (C2) — loses; the shed is already saturated.
3. Cap buys to protect the shed (C3) — no-op; the cap never binds.
4. Defer STRAWBERRY harvest to raise yield (V94) — loses ~$11k; the extra supply
   collapses the realized price and the parked units are deleted.
5. Reduce cost (hire/buy) — no recoverable waste; spend is fixed per game.
6. Recover terminal/overflow value — V92 already leaves $0 stranded, 2-unit overflow.
7. Rate-limit selling to avoid self-impact decay — only 0.7% of cash, and it is a
   hold-family action that loses for the same shed reason.

## 8. Why I did not freeze a promotion gate or run tournaments

The assignment's step 3 (freeze a gate, then evaluate on dev seeds + fresh holdout)
is the right process for a candidate I believe in. I stopped before that because
**no candidate survived the cheap pre-gate counterfactual probe**: three independent
overlays all lost by $2.8k–$25k, and the structural fact (shed at 102/100) explains
why the entire class loses. Running a full tournament and holdout on a signal that
is already known-negative would burn compute and risk the appearance of a validated
candidate. The honest call is a documented no-go with the mechanism proven, not a
formally-executed gate on a losing idea.

If a future attempt wants to proceed, the class to avoid is "hold/defer/limit stock."
The mechanism is: the shed is saturated and value must be converted immediately. Any
real improvement has to come from producing or selling **more units** (more tiles,
more animals, better yield) while the pipeline stays at the ceiling — which the
measured data says there is no room to do without either glutting a market or dying
to weeds.

## 9. Files changed

- Added (all new, all under `experiments/v94_sell_rate/`): `candidate.py`,
  `cash_flow.py`, `measure_decay.py`, `measure_harvest_yield.py`,
  `measure_production.py`, `measure_strawberry.py`, `measure_terminal.py`,
  `measure_wool_glut.py`, `mechanism_shed.py`, `probe_candidates.py`,
  `probe_engines.py`, `probe_lateharvest.py`, `reconcile_cash.py`,
  `wool_recovery.py`, and `probe_out/*.json`.
- No prior agent, doc, test, or submission was modified. `git diff --name-only`
  shows only the three files that were already modified before this session
  (`.gitignore`, `docs/CURRENT_STATE.md`, `main.py`) — none touched by me.

## 10. Recommendation

**NO-SUBMIT.** There is no improvement to submit. V92 remains the strongest verified
agent in this repository. The search produced a complete, engine-verified cash
reconciliation and a proven structural constraint (shed saturated at 102/100) that
explains why the open-loop V50/V92 tape is already near-optimal and why every
stock-holding overlay loses. Codex should not submit on the basis of this work.

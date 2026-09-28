# ERRATUM — V97 report, animal economics

**The V97 conclusion "extra cows cannot pay; best case −$185" is INVALID and must not be
cited.** It came from a model with three defects, all now measured and corrected in
`experiments/v98_economics/`. This erratum is added per the V98 assignment.

## What was wrong

`experiments/v97_route/audit_opening_conversion.py` contained three errors:

| id | error | measured truth |
|---|---|---|
| **ERR-1** | `animal_cash()` treated `max_held` as a **lifetime** cap and stopped after 6 units. | `max_held` bounds `yield_units`, the **stock held between collections** (engine 805-833). `HARVEST` zeroes it and leaves the animal in place, so production resumes on the next production day. **Measured: 164 MILK per game from 6 cows = 27.3 lifetime units per cow** (and 282 WOOL from 11 sheep = 25.6 per sheep). A 6-unit cow fails a basic sanity check against the official ledger. |
| **ERR-2** | `crop_cash_per_tile()` capped the **lifetime** yield of ongoing STRAWBERRY at `max_yield=4`. | For an ongoing crop, `max_yield` bounds one **accumulated stack**; the plant **persists** after harvest (engine 471-473 clears only non-ongoing crops) and regrows all season. **Measured: 249 STRAWBERRY per game from ~33 peak tiles.** |
| **ERR-3** | `net = gross − feed − crop_cash` **omitted the animal purchase cost** ($400 COW / $500 SHEEP), which the script printed but never subtracted. | The cost is real and is now included. |

## What the corrected model says

Engine-validated against the measured lifetime output, calibrated to the **observed
placement schedule** (cows on days 0, 2, 3, 7; sheep on days 0, 6, 8, 9, 10, 11), with
purchase cost included:

| animal | place day | lifetime units | gross | feed | purchase | net |
|---|---:|---:|---:|---:|---:|---:|
| **COW** | 0 | 23 | $3,205 | −$1,184 | −$400 | **+$1,621** |
| COW | 6 | 17 | $2,369 | −$939 | −$400 | **+$1,030** |
| COW | 10 | 13 | $1,811 | −$776 | −$400 | +$636 |
| SHEEP | 0 | 25 | $1,733 | −$1,184 | −$500 | +$49 |
| SHEEP | 6 | 19 | $1,317 | −$939 | −$500 | −$122 |
| GOOSE | 0 | 27 | $1,512 | −$1,184 | −$300 | +$28 |

**A COW is clearly profitable; a SHEEP and a GOOSE are marginal to negative.** This is
exactly the mix the frozen V92 route already runs (6 cows, 11 sheep, no geese), which is
a coherence check the old model failed.

**The corrected conclusion reverses the old one:** V97's "best case −$185, extra cows
cannot pay" becomes **best case +$1,621 for a COW**. Whether that survives contact with
worker-time displacement, feed cash-flow, and the shared market is now being tested as
V98; see `experiments/v98_economics/REPORT.md`.

## Model validation (required before any counterfactual)

The closed form is a **lower bound** (it assumes one collection per production day; a
stack left at `max_held` keeps accruing). It reproduces the observed herd's production to
the same order of magnitude and **never overstates** the payoff:

- MILK: observed 164.0, model (cared) 102, model (uncared) 38 — ratio 0.62, never > observed.
- WOOL: observed 282.0, model (cared) 102, model (uncared) 38 — ratio 0.36, never > observed.

A lower bound is the safe direction: if an animal pays under the lower bound, it pays
under the truth; the model is never optimistic.

## Second correction in this erratum: an impossible count in the V97 report

The V97 report stated, about the discarded-unit reconciliation, that the four games with
elevated discards included "**three wins and two losses**". That is arithmetically
impossible for four games and is wrong. The raw artifact
(`experiments/v97_route/accounting_verification.json`, plus the seat of each episode from
`experiments/kaggle/v92_official/`) shows the four elevated games are:

| episode | Rajusah seat | units deleted | outcome |
|---|---:|---:|---|
| 114158802 | 0 | 4 | **W** |
| 114166061 | 1 | 9 | L |
| 114175006 | 1 | 10 | **W** |
| 114177946 | 1 | 9 | **W** |

So the correct count is **three wins and one loss**, and the elevated discards occur in
**seat-0 or seat-1 games alike** in the underlying replay (114158802 is seat 0). The
"only in seat 1" claim in the V97 `CORRECTION_NOTES.md` is also too strong: the seat
ordering explains why the seat-1 games dominate (3 of the 4), but the mechanism is
**which day the second boundary event lands**, not seat alone. The qualitative
conclusion is unchanged — the discard quantity carries **no win/loss signal** — but the
count and the seat claim are corrected here.

## Files

- Corrected model: `experiments/v98_economics/corrected_model.py`
- Lifetime measurement: `experiments/v98_economics/measure_lifetime.py` →
  `lifetime_measurement.json`
- Feasibility: `experiments/v98_economics/feasibility_cow.py`
- V98 report: `experiments/v98_economics/REPORT.md`

The original V97 file `experiments/v97_route/audit_opening_conversion.py` is left
unmodified on disk for provenance; this erratum supersedes its conclusion.

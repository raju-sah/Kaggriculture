# V98 — corrected animal economics and the extra-cow route: report

**Recommendation: NO-SUBMIT. The corrected economics are real and overturn V97's no-go
reason, but the profit is not REACHABLE by an overlay on this tape. All four Kaggle
submission slots remain unused.**

This is the assignment's requested work: correct the V97 economic model, validate it
against the engine, and test a V98 candidate if the corrected estimate left a positive
opportunity. The model is corrected and validated; the opportunity is real in the
abstract (+$1,030 per early COW) and unreachable in practice (the animal can never be
placed). Both findings are measured below.

No Kaggle submission was made. No prior agent, `main.py`, or prior candidate was
modified. A prominent erratum was added to the V97 report.

---

## 1. The V97 bug is confirmed, and V97's no-go reason is invalid

`experiments/v97_route/audit_opening_conversion.py` had three errors, all now measured.
Full detail and hashes in `experiments/v97_route/ERRATUM.md`.

| id | V97 error | Measured truth (14 official replays, 0 cash mismatches) |
|---|---|---|
| **ERR-1** | `max_held` treated as a **lifetime** cap (6 units) | It bounds `yield_units`, the stock **held between collections** (engine 805-833). HARVEST zeroes it and the animal keeps producing. **164 MILK / 6 cows = 27.3 lifetime units per cow**; 282 WOOL / 11 sheep = 25.6 per sheep. |
| **ERR-2** | STRAWBERRY lifetime capped at `max_yield=4` | Ongoing crops **persist and regrow** (engine 471-473 clears only non-ongoing). **249 STRAWBERRY / game from ~33 peak tiles.** |
| **ERR-3** | `net` **omitted the animal purchase cost** ($400/$500) | Printed but never subtracted. Now included. |

A second, separate error was also corrected: the V97 report's "three wins and two losses"
for four elevated-discard games is arithmetically impossible. The raw artifact shows
**three wins and one loss**, and the elevated set is **3 of 4 in seat 1** (114158802 is
seat 0). The "only seat 1" claim is too strong. The qualitative point stands — the
discard quantity carries no win/loss signal — but the count and seat claim are corrected.

## 2. The corrected, engine-validated economics REVERSE the conclusion

Rebuilt from `_daily_refresh_animals` (engine 813-827) and `_daily_refresh_plants`
(770-802), calibrated to the **observed placement schedule** (cows d0,2,3,7; sheep
d0,6,8,9,10,11), with purchase cost included:

| animal | place day | lifetime units | gross | feed | purchase | net |
|---|---:|---:|---:|---:|---:|---:|
| **COW** | 0 | 23 | $3,205 | −$1,184 | −$400 | **+$1,621** |
| COW | 6 | 17 | $2,369 | −$939 | −$400 | **+$1,030** |
| COW | 10 | 13 | $1,811 | −$776 | −$400 | +$636 |
| SHEEP | 0 | 25 | $1,733 | −$1,184 | −$500 | +$49 |
| SHEEP | 6 | 19 | $1,317 | −$939 | −$500 | −$122 |
| GOOSE | 0 | 27 | $1,512 | −$1,184 | −$300 | +$28 |

**A COW is clearly profitable**; SHEEP is marginal and GOOSE negative. This matches the
frozen route's actual mix (6 cows, 11 sheep, no geese) — a coherence check the V97 model
failed. **V97's "best case −$185" becomes "+$1,030 to +$1,621 for a COW."**

Validation gate: the closed form is a **lower bound** (one collection per production day;
a stack at `max_held` keeps accruing) and never overstates: MILK model 102 vs observed
164, WOOL model 102 vs observed 282. A lower bound is the safe direction for a cost test.

Feasibility of an extra cow, measured on the official replays: free pastures exist on
days 2,7,8,9,11; cash clears $400 from day 6 ($910) and is ample from day 10 ($3,582);
opening shed peaks at 36 of 100. **The opportunity is feasible in resources.** So a V98
candidate was warranted and built.

## 3. V98 candidate: an extra COW, funded without borrowing a worker

`candidate.py` — frozen V92 embedded verbatim, plus a day-6 `BUY_ANIMAL COW 1` gated on
free pasture, cash floor, shed headroom, and a free market slot. It never displaces a
lifecycle action, because V97 measured that borrowing a worker from this tape is
catastrophic (v1: −89,887).

**Screen (11 spent seeds, both seats, exact loader, 0 errors): every game negative, mean
−$4,600.** The lifecycle audit (`diagnose_cow.py`) is unambiguous:

| stage | V92 recorded | V98 | delta |
|---|---:|---:|---:|
| S1 COW bought | 6 | 19 | **+13** |
| S2 COW placed | 6 | 6 | **+0** |
| S5 MILK harvested | 164 | 164 | +0 |
| S7 net of the extra cows | | | **−$5,200** |

**The overlay bought 13 cows and placed none.** A cow lands in the shed; PLACE requires the
actor to be CARRYING it, which needs a prior PICKUP from a shed-adjacent tile
(358-375) and a walk to a free PASTURE (377-392). The tape performs that dance for its
own herd on a fixed schedule; a foreign cow is not on it.

## 4. The one permitted revision, and the structural wall

**R1** (`candidate_r1.py`) buys the cow only on a turn where the **tape itself is already
issuing an animal PICKUP**, so the cow rides the walk that is already happening, plus a
one-shot latch. It works as designed — **exactly 1 cow bought, not 13** — but the audit
still shows **+0 placed, +0 milk, −$400**. The cow is bought and never collected.

**Why, structurally** (`audit_pickup_closure.py`, 14 replays): the tape picks up
**exactly the animals it bought**, same day and species — **238 matched units, 0
unmatched**. Its collection walk is **closed-loop on its own purchases**. An animal the
tape did not buy is not on that walk's manifest and can never be carried.

So the corrected economics are **real but unreachable by an overlay**: the only way to
place a foreign animal is a NEW worker errand, and V97 measured that borrowing a worker
from this tape is catastrophic. The extra cow's realised value on this tape is exactly its
$400 cost.

## 5. The R2 gate, re-examined as the assignment requires

The assignment said a zero-trigger gate is not evidence that bounded reroutes are
impossible. So I measured a **gate ladder** (reach 2-4, value threshold 400→50, clean-tile
required or not) against the **measured** displacement cost (V97 v1 borrowed 219
in-window turns for −70,127, i.e. **−$320 per borrowed turn**):

| gate | admits | turns/game | gross/game | displacement | net |
|---|---:|---:|---:|---:|---:|
| R2 as shipped | 1,918 | 639 | $57,265 | −$204,617 | **−$147,353** |
| reach 3 | 2,842 | 1,091 | $84,852 | −$349,354 | −$264,502 |
| reach 4 | 3,472 | 1,453 | $103,662 | −$465,272 | −$361,610 |
| value 100, dirty tile OK | 10,836 | 4,060 | $259,014 | −$1,300,071 | −$1,041,058 |
| value 50, dirty tile OK | 13,944 | 5,734 | $310,804 | −$1,836,111 | −$1,525,307 |

Two findings, in the assignment's favour and against it:

- **In the assignment's favour:** the R2 gate is not a zero-opportunity gate. Loosening it
  admits up to 13,944 trigger opportunities, and the tape harvests only **1.9%** of ripe
  tile-turns in the window, so the backlog is genuinely uncovered. The targets exist.
- **Against a proposal:** **no gate on the ladder produces a positive net** even before any
  other risk, because the measured −$320/borrowed-turn displacement cost swamps the gross
  value of the best reachable target at every reach and threshold. So a revised gate is
  **not proposed**: there is no setting at which the gross clears the cost.

This is the stronger form of the close the assignment asked for: not "the gate was too
strict" but "no admissible gate clears the measured displacement cost."

## 6. Results table

Exact loader, pinned kaggriculture 1.32.7, 11 already-spent seeds (each ≥22 prior saved
games), both seats, **0 errors and 0 timeouts in all 44 games**.

| Candidate | Opponent | Games | W-L-D | Mean margin | Positive | Errors |
|---|---|---:|---|---:|---:|---:|
| V98 (day-6 buy) | V92 | 22 | 0-22-0 | −4,600 | 0/22 | 0 |
| V98-R1 (windowed buy) | V92 | 22 | 0-22-0 | −460 | 0/22 | 0 |

**No promotion gate was frozen and no fresh holdout was consumed.** No candidate showed a
positive paired cash signal on development seeds, so a holdout was not warranted and
remains unspent. Four Kaggle slots remain unused pending Codex review.

## 7. What this establishes

1. **The V97 "extra cows cannot pay" no-go is retracted.** A COW is worth **+$1,030 to
   +$1,621** under engine-validated lifetime economics. The old −$185 came from a
   6-unit lifetime cap and an omitted purchase cost.
2. **The correct economics are real but structurally unreachable on this tape.** The tape's
   animal-collection walk is closed-loop on its own purchases (238/238), so a foreign
   animal cannot be placed without a new worker errand, and worker borrowing is measured
   catastrophic. The realised value of an overlay-bought cow is its $400 cost.
3. **The uncropped ripe backlog is real (the tape covers 1.9% of ripe tile-turns) but not
   monetizable by borrowing a worker**, because the measured displacement cost (−$320 per
   borrowed turn) exceeds the gross value of the best reachable target at every gate
   setting.
4. Any future extra-animal idea must either extend the tape's own buy-then-collect manifest
   (so the animal rides the existing walk) or replace the walk wholesale — the latter
   being the class V97 measured as a −$89,887 catastrophe.

## 8. Files and hashes

All new V98 evidence under `experiments/v98_economics/`. Prior files preserved.

| Artifact | SHA-256 |
|---|---|
| `candidate.py` (V98) | `ae99ac2c53af53c38c7602f907ff00ed7fab771a57988bb2da8dcaa855c8fe82` |
| `candidate_r1.py` (V98-R1) | `f5b931ebabb992e4d990991a5c563afa0cf5095ed087796254c2b4d687b38d83` |
| `candidate_overlay.py` | `005965d03b7ba2f7176c45875158371bde362cebaa267c57cac338166f595254` |
| `candidate_r1_overlay.py` | `220d6bd5400fd5c492f44773d15d3fdcffb0ce21c8d6045823efd64e25fc8c75` |
| `experiments/v97_route/ERRATUM.md` | `31383d5d4f9a7f7de2291e9184bcd1ea40db3b3d4cd5e16ffc8297e1beb322ee` |

V92, V93, V94, V95, V56, V50 all byte-unchanged. Every candidate passes 10-11 build
self-checks (embedded V92 byte-identical, loader binds the entrypoint, existing orders
preserved, and each gate condition has a negative test). Evidence: `lifetime_measurement.json`,
`model_validation.json`, `candidate_build.json`, `candidate_r1_build.json`, and per-game
records under `runs/`. The V88 replay joins were not used; seeds 93000–93011 were not used.

## 9. Recommendation

**NO-SUBMIT.** The corrected economics overturn the previous *reason* for the no-go but do
not produce a candidate: an extra cow is profitable in the abstract and worth exactly its
purchase price in practice, because this tape cannot place an animal it did not buy. The
four Kaggle slots should remain unused. Codex should verify the two load-bearing numbers:
the **27.3 lifetime MILK per cow** (which retracts the V97 no-go) and the **238 matched /
0 unmatched pickup closure** (which is why it cannot be cashed).

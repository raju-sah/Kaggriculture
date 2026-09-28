# V101 precommitted fresh-holdout gate

**Written before any fresh holdout seed was run.** The candidate hash below was
frozen from the file as built; the development panel on 160001–160060 is
already-spent data and is *not* holdout evidence. No holdout result is reported
in this repository, because no holdout has been run.

## What is frozen

| Item | Value |
|---|---|
| Candidate file | `experiments/v101_commandcode/candidate.py` |
| Candidate SHA-256 | `8c572b9027ca4f5a0d656d1b1dd6fb74b4b121bd67c69b97aef16d66e21052e7` |
| Embedded V92 source SHA-256 | `0d5d356baa25703f1a7b753527d1b39e1c7d63478985913be5b3c2550261b806` (frozen V92, unchanged) |
| Engine | kaggle-environments 1.32.7, `kaggriculture.py` sha256 `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e` |
| Episode | 720 steps, 24 turns/day (30 days) |
| Rule | swap one unit of the incumbent's day-6 `BUY_ANIMAL SHEEP 2` into `SHEEP 1` + `COW 1` **iff** the exact-arithmetic model delta > 0 |
| Development seeds | 160001–160060 (spent for this purpose) |

## Holdout seed range (frozen, unused, disjoint from every prior range)

**170001–170024** (24 seeds). These are fresh: disjoint from this worker's
development range 160001–160060, the other agent's 150001–150080, V99's spent
panel (92600–95300) and V99's failed fresh holdout (137501–137524), and the
older 93000–93011 holdout. If these are run, they are spent afterwards and
cannot be reused.

## Numerical gate (decided now, before the holdout is touched)

Run the exact loader, both seat orders, against frozen V92 (primary), frozen V50
and frozen V56 (controls). The independent unit is the **seed**, not the game:
the engine is deterministic and both seat orders were verified to produce
identical margins, so 24 seeds → 24 effective samples per opponent, 72 total.

The gate passes only if **all** of the following hold:

1. **V92 (primary).** Score rate > 0.55 across the 24 seeds, and mean paired
   margin > +$300.
2. **V92 distinct-seed triggers.** The rule fires (observable model delta > 0
   on the day-6 tape) on **at least 6 distinct holdout seeds**. This exists
   because V99's gate fired on only 2 of 24 and that was its disqualifying
   weakness; a rule that barely fires cannot be a real improvement even if it
   is safe.
3. **V50 control.** Score rate > 0.55 and mean paired margin > +$300.
4. **V56 control.** Score rate > 0.45 and mean paired margin > 0. (V56 is the
   strongest known opponent; V99 lost 20W/28L to it.)
5. **Cleanliness.** Zero candidate errors, zero infrastructure errors, zero
   timeouts, and the three-step rewrite (BUY COW at d6h6, PICKUP COW, PLACE COW)
   present in the replay on every seed the rule fires, with the cow ending the
   episode alive on a PASTURE.
6. **No harm.** No holdout seed may show a negative paired margin larger than
   −$2,000 against V92. A single large regression invalidates the rule even if
   the mean passes, because the V99 report showed this intervention's losses are
   heavy-tailed.

## What passing this gate does and does not mean

Passing means the local evidence is consistent with a real improvement and is
worth a Codex review. It does **not** mean the candidate is ready to submit, and
this report makes no claim of top-ten readiness: 24 seeds cannot support that,
and the whole V93–V100 series is a record of locally-positive rules that failed
a fresh panel. Submission remains a separate, human decision.

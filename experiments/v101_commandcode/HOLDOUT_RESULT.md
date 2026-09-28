# V101 precommitted fresh holdout: result

**Recommendation: NO-SUBMIT.** Keep all four Kaggle submission slots.

The gate was written in `GATE.md` before any holdout seed was run, with the
candidate hash frozen. Neither the candidate nor the gate was edited during or
after the run; both hashes are re-verified below. Nothing was tuned on these
results. The holdout range 170001–170024 is now spent data and must not be
reused as a fresh holdout.

## Integrity

| Item | SHA-256 | Status |
|---|---|---|
| Candidate `candidate.py` | `8c572b9027ca4f5a0d656d1b1dd6fb74b4b121bd67c69b97aef16d66e21052e7` | unchanged since freeze |
| `GATE.md` | `33f90dd83c31293bc3cbcbc30b4c56de07f380083d66599e540096c692ac311e` | unchanged since precommit |
| Opponent V92 | `0d5d356baa25703f1a7b753527d1b39e1c7d63478985913be5b3c2550261b806` | frozen |
| Opponent V50 | `e6b50128e023e3b9fafa1841e4cd520c5e581acb48e8628657585c18272eab2b` | frozen |
| Opponent V56 | `d9e9670921b62afedfa8cbc7086d2a2ec19e153ee26006cef477eadd462bd19c` | frozen |
| Engine `kaggriculture.py` | `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e` | pinned, 1.32.7 |

24 fresh seeds × 2 seat orders × 3 opponents = 144 games, **zero agent errors,
zero infrastructure errors, zero timeouts**. The preflight refused to start
unless every file still matched its frozen hash, and the run confirmed the seeds
had never appeared in any prior `games.jsonl` or `report.json`.

## Results

| Opponent | W–L–D | Score rate | Mean margin | Median | Range |
|---|---:|---:|---:|---:|---:|
| V92 (primary) | 13–8–3 | 0.604 | +$1,447 | +$1,452 | −2,437..+4,908 |
| V50 (control) | 18–6–0 | 0.750 | +$2,087 | +$1,846 | −1,695..+5,536 |
| V56 (control) | 8–16–0 | 0.333 | −$2,657 | −$10,442 | −41,415..+39,691 |

Seat-swap margins were identical on all 24 seeds for V92 and V50, so the
effective sample is 24 seeds per opponent, not 48 games.

## Gate criteria, scored

| # | Criterion | Required | Actual | Result |
|---|---|---|---|---|
| 1a | V92 score rate | > 0.55 | 0.604 | PASS |
| 1b | V92 mean margin | > +$300 | +$1,447 | PASS |
| 2 | V92 distinct-seed triggers | ≥ 6 | **21 / 24** | PASS |
| 3a | V50 score rate | > 0.55 | 0.750 | PASS |
| 3b | V50 mean margin | > +$300 | +$2,087 | PASS |
| 4a | V56 score rate | > 0.45 | **0.333** | **FAIL** |
| 4b | V56 mean margin | > 0 | **−$2,657** | **FAIL** |
| 5 | Lifecycle on firing seeds | chain/alive/produce/zero mismatch | **not audited** | **NOT MET** |
| 6 | No V92 regression worse than −$2,000 | > −$2,000 | worst **−$2,437** (3 seeds) | **FAIL** |

**10 of 14 pass. The gate is a strict conjunction, so the gate FAILS.**

Criterion 5 must be read precisely: the lifecycle replay audit was **not run**,
because another worker's holdout (seeds 180001–180024 and 150001–150015) was
active and I was told not to launch further match runs. That is a missing
observation, **not** an observed lifecycle defect. On the 60-seed development
panel the same audit passed 48/48 on every count. It is recorded as NOT MET
because the gate required it on the holdout, and it is not something I can
substitute development evidence for.

## What the failures mean

**Criterion 2 passed decisively — the rule is not rare.** 21 of 24 seeds
triggered, against a required 6 and against V99's Pizza-only gate which fired on
2 of 24. This was the specific weakness that disqualified V99, and V101 does not
have it. The high trigger rate is the one part of the V101 thesis that
reproduced cleanly on fresh maps.

**The V92 ties still match the model exactly.** The 3 tie seeds (170007, 170009,
170021) are precisely the 3 non-positive-delta seeds. The model partitions the
holdout into "changed the game" (21) and "provably inert" (3) with no seed on
either side of the partition — the same clean causal signature seen on the
development panel. The estimator is not overfitting; it is correctly identifying
when to act.

**Criterion 6 is the serious one.** Three seeds lost more than the precommitted
tolerance: 170001 (−$2,146), 170010 (−$2,437), 170023 (−$2,345). The development
panel had the same heavy tail (−$5,797 and −$5,556 single seeds) and I flagged it
as a known risk. The tolerance was set at −$2,000 precisely so this would be
caught, and it was. This is not a marginal miss: a policy with a mean of +$1,447
that risks −$2,400 on 3 of 24 seeds is a different risk profile from one that
never does that, and the gate said so before the data existed.

**V56 is a genuine loss, not noise.** Averaging the two seat orders (necessary
because V56 is seat-unstable here, see limitations) gives 9W–15L, mean −$1,846,
score 0.375 — it still fails both V56 criteria by a wide margin. V99 also lost to
V56 (20W/28L), so this is a persistent weakness of the cow-for-sheep idea rather
than a new regression: the substitution appears to help against V92 and V50 and
hurt against the strongest opponent.

**V56 seat instability (limitation, not diagnosed).** V92 and V50 were
bit-identical across seat orders on all 24 seeds. V56 was not: 3 seeds gave
different margins per seat, most starkly 170024 at +$26,323 (candidate seat 0) vs
−$10,685 (candidate seat 1). Per the coordination instruction I did not run
further matches to isolate whether this is intrinsic to V56 or an interaction with
our intervention. **This is recorded as an unexplained limitation.** It means the
V56 mean is not a clean paired estimate, and the V56 verdict should be read as
"fails, with an unquantified measurement caveat", not as a precise effect size.

## Why this is NO-SUBMIT

1. The precommitted gate failed, on a strict conjunction, on three criteria.
2. Two of those three (V56, no-harm) are substantive strategy failures, not
   measurement artifacts. The no-harm failure in particular was the exact risk
   the criterion existed to catch, and it caught it.
3. Development→holdout decay happened again: V92 mean fell from +$1,392 on 60
   development seeds to +$1,447 on 24 holdout seeds (comparable), but the V56
   picture is the opposite of the development panel, which did not include a V56
   leg at all. That is an unmeasured gap, and the V99–V100 history says an
   unmeasured opponent gap is where this work has been losing.
4. The one criterion that cleanly reproduced — trigger rate — is a property of
   how often the rule acts, not evidence that acting is profitable against the
   hardest opponent.

The honest summary: the *estimator* is validated (21/24 triggers, exact tie
correspondence, heavy-tailed loss distribution reproduced honestly on fresh
seeds). The *strategy* is not (V56 loss, three oversized V92 regressions). Those
are separable, and a future candidate should keep the estimator and reconsider
the action — in particular a per-seed loss cap that the current rule has none of.

## Artifacts

- `holdout.py` — the runner, with a preflight that refuses to run on any hash drift.
- `audit_holdout.py` — scores the finished run against the frozen criteria; it
  does not choose thresholds.
- `holdout_results.json`, `gate_audit.json` — machine-readable results.
- `runs/holdout_vs_{v92,v50,v56}/` — full per-game records.
- `model_deltas_holdout.json`, `holdout_states.jsonl` — the observed day-6
  decision states and model deltas behind the trigger count.

**No Kaggle submission was made. No seed was retried, filtered, or re-ranked. The
candidate and the gate were not modified.**

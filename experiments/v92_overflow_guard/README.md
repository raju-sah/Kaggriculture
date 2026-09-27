# V92: day-23 shed-capacity guard on V50 — spent-panel PASS, identity verified

Read-only with respect to frozen sources. `agents/v56_agent.py` and `experiments/v50_agent.py` were
not modified. **No Kaggle submission**; root decides on that.

## Provenance

| File | SHA-256 |
|---|---|
| `experiments/v92_overflow_guard/candidate.py` | `0d5d356baa25703f1a7b753527d1b39e1c7d63478985913be5b3c2550261b806` (66,855 bytes) |
| `experiments/v50_agent.py` (base, unmodified) | `e6b50128e023e3b9fafa1841e4cd520c5e581acb48e8628657585c18272eab2b` |
| `agents/v56_agent.py` (opponent and control basis, unmodified) | `d9e9670921b62afedfa8cbc7086d2a2ec19e153ee26006cef477eadd462bd19c` |

The candidate embeds the frozen V50 source as base64 and exec's it at import.
`verify_embedded_source.py` confirms three things before any game is played:

1. the embedded text decodes to `experiments/v50_agent.py` **byte-for-byte**;
2. `kaggle_environments.agent.get_last_callable` selects `_kaggle_submission_entrypoint` (the loader
   returns the *last* module-level callable, so a helper defined after the entrypoint would be
   selected instead — the class of bug that hit V89 and V87);
3. a full 720-step game completes with **only this file copied into an empty temp directory**
   (candidate 113,260 vs opponent 78,451, 6,410 non-PASS actions).

An earlier draft read V50 from an absolute local path. That would have raised inside V50's
`try/except`, fallen through to its all-PASS fallback, and silently submitted a do-nothing agent
while passing every local test run from inside the repository. It was fixed before any panel game.

## The guard

Active **only** on `day == 23 and hour == 23`, and only when

    shed_now + carried_now + committed_WHEAT + committed_FERTILIZER + 6  >  100

`carried_now` is every farmer/hand inventory — exactly what `_drop_inventories_to_shed` will try to
store. The `+6` is a conservative allowance for units this hour's own `HARVEST` actions can still
produce. When the projection would overflow, FERTILIZER is trimmed first (cheaper unit, $29 vs $37
at the d23 quote) and capped at 12, then WHEAT, until the projection fits. The floor keeps
`min(ordered FERTILIZER, 4)` purchased and never buys less WHEAT than the shed already holds.

It never adds orders, never touches any farmer/hand action, never touches SELL, and never fires on
another day or hour.

**It fires on 56 of 56 reachable day-23 hour-23 states** across the saved head-to-head replays, so the
24-0 below is not a null result from an inert overlay.

## Spent-panel result: 12 spent seeds, both seats, 72 games

| Run | Opponent | W-L-D | Win rate | Score rate | Median margin | Errors |
|---|---|---|---:|---:|---:|---:|
| Candidate | V50 | **24-0-0** | **100.0%** | 100.0% | +412 | 0 |
| Candidate | V56 | 11-13-0 | 45.8% | 45.8% | −2,534 | 0 |
| Control (frozen V50) | V56 | 11-13-0 | 45.8% | 45.8% | −2,313 | 0 |

Zero errors, zero timeouts, zero infrastructure failures across all 72 games.

## Identity check: the 24-0 is real, not self-play

A 24-0 sweep against your own base lineage is exactly the result that should be treated as a red flag,
so it was tested directly rather than accepted.

**Null run — frozen V50 against itself, same 12 seeds, both seats:** **0-0-24**, median margin **0**,
mean coins 86,375. Identical policies draw, exactly as V82 found for V56 against itself (7-7-58,
median 0) and as V89 confirmed.

V92's 24-0 with a median margin of +412 is not that signature. The candidate and the base are also
distinct files (`0d5d356b…` vs `e6b50128…`), and the guard demonstrably changes the market order on
every reachable trigger state.

On the audited state (seed 92802, V50 seat 1, day 23 hour 23) exact engine settlement gives:

| | Shed after drop | Units discarded | Cash |
|---|---:|---:|---:|
| Frozen V50 | 100 | **16** (WOOL 4, FERT 5, WHEAT 4, STRAW 3) | 54,868 |
| V92 guard | 91 | **0** | 55,658 |

All farmer/hand actions are identical; only the buy quantities differ.

## Predeclared gate (frozen in `plan.json` before the run)

| Criterion | Threshold | Result |
|---|---|---|
| Zero errors | all counters zero | **PASS** |
| Wins vs V50 | ≥ 15 of 24 (60%) | **PASS** — 24 |
| Median margin vs V50 | strictly positive | **PASS** — +412 |
| No score-rate regression vs V56 | within 5pp of matched control | **PASS** — 45.8% vs 45.8%, **+0.0pp** |

**VERDICT: PASS, 4 of 4.** Per `plan.json`, a pass authorises reporting to root; the Kaggle
submission decision is root's, not mine.

## Honest reading

The V56 comparison is **exactly neutral**: 45.8% for both candidate and control, a +0.0pp delta. The
guard neither helps nor hurts against V56 on this panel. Its entire measured effect is against the
V50 lineage, where it is a clean sweep.

Two cautions on the 24-0:

- The panel is 12 **spent** seeds, several of which were used while developing earlier V50-lineage
  work. A sweep on seeds the base has been tuned against is expected to favour a small overlay and
  should not be read as an unbiased estimate.
- The median margin is **+412**, not thousands. The guard wins on *consistency*, not magnitude, and
  +412 is a small margin against an opponent that usually draws. That is why the fresh holdout is the
  real test.

V91's own warning still applies and is now quantified: the guard pays for the preserved goods by
forgoing part of the last-hour WHEAT and FERTILIZER purchase. On this panel that trade is clearly
favourable, but the full-season cost was not isolated separately from the overflow saving.

## Artifacts

- `candidate.py`, `plan.json` (schema 2, frozen SHA and gate), `verify_embedded_source.py`
- `runs/candidate_panel/` — 48 games, `runs/control_panel/` — 24 games, `runs/null_selfplay/` — 24 games

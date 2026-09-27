# V80: early-Yarn sheep-route candidate — REJECTED

One bounded candidate built on the frozen V57-reset lineage, screened once on spent seed 92802
against frozen V50 in both seats, then rejected on the predeclared gate. No performance tuning, no
retest, no fresh seed, no submission.

## Sources and SHA-256

| File | SHA-256 | Role |
|---|---|---|
| `experiments/v80_wool_route/candidate.py` | `9fbe95d33ed25a6168cae58d2a3310208c204e6548db4b6d8f7f479ec20f0d31` | new candidate (frozen before the screen) |
| `experiments/v57_broad/v57_reset_candidate.py` | `4173479fe1f80d031d570d1ea23b694dfe86e1d162317a4c9c7df0058a40208e` | frozen base, **unmodified** |
| `experiments/v50_agent.py` | `e6b50128e023e3b9fafa1841e4cd520c5e581acb48e8628657585c18272eab2b` | opponent, **unmodified** |
| `experiments/v59_route_rules/mix_gate/candidate_isolated.py` | `50430cd46641f5b2b26b5b99a2fe4738513f8a9186b011f8620e8c14dbd94a20` | prior V59 rule, read only, **unmodified** |

Candidate SHA was frozen before any scoring run. Screen command:

```
.venv/bin/python -m simulation.tournament \
  --candidate experiments/v80_wool_route/candidate.py \
  --opponent v50=experiments/v50_agent.py \
  --seed 92802 --repeats 1 --replay-policy all \
  --output-dir experiments/v80_wool_route/runs/screen_92802
```

Artifacts: `runs/screen_92802/{report.json,summary.json,games.jsonl,games.csv,games/,logs/,replays/}`.
Engine: `kaggle_environments` 1.32.7, 720 steps. Settlement reconstructed with
`experiments/v75_elite_cashflow/reconstruct.py` against the same pinned engine:
**`max_cash_error` 0.0, `mismatches` 0** for every seat of both replays.

## The exact diff

The overlay is one new file that execs the frozen V57-reset source into a private namespace and wraps
its `agent`. Four bounded changes, all gated on the early-Yarn regime (`YARN_STORE` unlocked,
`WOOL >= 180`, `day <= 8`):

1. **Market conversion** — at exactly the 2-sheep trigger state, the first `BUY_ANIMAL GOOSE` inside
   the window becomes `BUY_ANIMAL SHEEP`. Capped at `CONVERT_CAP = 2` animals, fires once
   (`purchase_step` latches), and never touches a later purchase.
2. **Infrastructure priority** — while converted units are undelivered and no pasture is vacant, a
   `BUILD_COOP` emitted by the frozen route is redirected to `BUILD_PASTURE`.
3. **Shed pickup** — a `PICKUP GOOSE/COW` turn becomes `PICKUP SHEEP` while converted sheep sit in
   the shed.
4. **Pasture delivery** — a unit carrying a converted sheep walks to the nearest vacant pasture and
   `PLACE SHEEP`s.

Nothing else is altered. Feed, care, planting, watering, harvesting and the market-impact ordering are
the frozen route's.

### Offline fidelity check (before scoring)

Against the saved 92802 observation stream, candidate vs frozen, 1,440 frames, state reset at episode
start: **0 exceptions, 2 changed market frames, 14 changed worker frames.** The conversion fires at
**step 150** — the frame whose action settles into step 151's state, which is why the recorded order
at step 150 changes and not step 151.

## Changed action chronology (live screen, ab seat, candidate = seat 0)

| Step | Day/hour | Change |
|---:|---|---|
| 150 | 6h06 | `BUY_ANIMAL GOOSE 2` → `BUY_ANIMAL SHEEP 2` (cash 1,324, affordable) |
| 152 | 6h08 | hand 7 `PICKUP GOOSE` → `PICKUP SHEEP 1` |
| 153 | 6h09 | hand 1 `PICKUP GOOSE` → `PICKUP SHEEP 1` |
| 154 | 6h10 | `BUILD_PASTURE` (frozen route's own build) |
| 156 | 6h12 | `BUILD_PASTURE` (frozen route's own build) |
| 157 | 6h13 | hand 1 `PLACE SHEEP` — **first converted sheep placed, 7 hours after purchase** |
| 159 | 6h15 | second converted sheep placed; herd reaches 4 sheep at (5,2) and (6,2) |

Both converted sheep were placed **within 24 hours** of the step-150 purchase. That gate passes.

## The failure: the converted sheep starved and escaped

Herd observed in the live screen:

| Day | Herd | Cash |
|---:|---|---:|
| 6 | COW 4, SHEEP 2 | 880 |
| 7 | **COW 4, SHEEP 4** | 862 |
| 8 | **COW 4, SHEEP 2** | 286 |

The two converted sheep existed for exactly one day and were gone by day 8. The converted tiles
`(5,2)` and `(6,2)` sat at `consecutive_unfed = 1` for **all 24 hours of day 7** — the frozen feed
route never visits them, because it was built for a farm with no animals at those coordinates. At the
day-7 → day-8 end-of-day tick, `_daily_refresh_animals` (engine lines 805-820) increments
`consecutive_unfed` to 2 and deletes the animal, leaving the pasture behind.

Note for anyone re-running this: the escape leaves **no trace in any observation**.
`consecutive_unfed` is reset to 0 at the same tick, so scanning frames for `>= 2` returns zero for
both seats. The loss is only visible as a herd count that drops. That is why the "zero errors/escapes"
gate below is reported as measured from herd trajectory, not from the tile field.

The mechanism is exactly the risk the V80 diagnosis flagged. The diagnosis established that *v50*
could absorb two more animals on a comparable hand budget — but v50 ran **its own** feed/care route
with the animals included from the start. Copying the animals into the frozen route's route table
does not extend that route. Preserving "daily feed/care" was not achieved by leaving the frozen feed
loop untouched; it requires the feed loop to be **extended** to the new coordinates, which is a second
change with its own crop/care displacement risk.

## Ledger

Settlement-exact reconstruction, ab seat, candidate vs saved frozen reset:

| Cash component | Frozen reset | V80 candidate | diff |
|---|---:|---:|---:|
| Accepted sales | 112,963 | 89,578 | **−23,385** |
| Product purchases | 8,446 | 10,225 | +1,779 |
| Seed purchases | 7,020 | 7,020 | 0 |
| Animal purchases | 6,500 | 6,900 | +400 |
| Land + hire (residual) | 15,366 | 15,366 | 0 |
| **Final cash** | **78,631** | **53,067** | **−25,564** |

Accepted product sales:

| Product | Frozen reset | V80 candidate | diff |
|---|---:|---:|---:|
| WOOL | 16,166 | **9,716** | **−6,450** |
| STRAWBERRY | 21,034 | **3,606** | **−17,428** |
| CARROT | 10,634 | 5,062 | −5,572 |
| EGG | 9,726 | 6,725 | −3,001 |
| FERTILIZER | 15,733 | 13,272 | −2,461 |
| MILK | 4,709 | 13,069 | +8,360 |
| WHEAT | 13,936 | 15,986 | +2,050 |
| TOMATO | 6,589 | 7,706 | +1,117 |
| MELON | 14,436 | 14,436 | 0 |
| **Total** | **112,963** | **89,578** | **−23,385** |

**Wool fell, it did not rise.** The intervention removed the two geese that were producing egg
(9,726 → 6,725) and replaced them with sheep that were fed for one day, produced nothing, and escaped.
Milk rose because cow pasture capacity was freed, but strawberry collapsed by 17,428 — a second-order
route displacement from the same edit.

## Predeclared gate, both seats

| # | Gate | Threshold | ab | ba | Result |
|---:|---|---|---|---|---|
| 1 | Errors / escapes | zero | 0 errors, **2 animal escapes** | same | **FAIL** |
| 2 | Two extra sheep placed | within 24h of purchase | placed step 157, 7h | same | PASS |
| 3 | Accepted wool revenue | ≥ 16,166 + 15,000 = **31,166** | **9,716** | same | **FAIL** |
| 4 | Own final cash | ≥ 90,000 | **53,067** | same | **FAIL** |
| 5 | Margin improvement vs frozen −33,587 | ≥ +10,000 | **−52,728** | same | **FAIL** |
| 6 | Non-wool accepted sales drop | ≤ 5,000 | **16,935** | same | **FAIL** |

Both seats produced identical results (53,067 / 105,795, seat-swapped), so the economy is
seat-invariant here as in the frozen baseline.

**5 of 6 gates fail. Verdict: REJECT.**

## Honest reading of what this does and does not show

- **Rejected.** The candidate is worse than the frozen reset by 25,564 coins on this seed, and worse
  on wool, the very product it targeted. It is not a candidate.
- **The wool-route hypothesis is not refuted by this.** The gate failure is a *feed/care routing*
  failure, not evidence that sheep are the wrong product. The two sheep produced no wool because they
  were dead before their first yield day (SHEEP `first_yield_day` is 6, so a day-6 purchase yields
  nothing until roughly day 12 even when it survives).
- **V50's sequence remains feasibility evidence only.** It shows the day-6 conversion is reachable
  with no crop displacement *for an agent whose feed route already covers the new animals*. That is
  a stronger precondition than this overlay assumed, and the V80 diagnosis flagged it as a hypothesis
  rather than proof. This screen is consistent with that caution.
- One seed, one opponent, one run. It is a screen, not a measurement, and it is recorded as such.

## What a next attempt would have to fix

Not attempted here — the instruction was one bounded candidate and a single screen, with no tuning or
retest. For the record, the minimum additional change is a **feed/care route extension** that reaches
the newly built pastures and keeps two more animals alive for the ~6 days before their first yield.
That is a different and larger intervention than a market-order overlay, and it would need its own
isolation argument. No fresh seed should be spent on it until the converted animals demonstrably
survive to first yield on a spent seed.

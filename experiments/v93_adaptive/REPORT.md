# V93 adaptive candidate — final report

**Verdict: NO-GO. The predeclared gate FAILED. No submission was made and none is
recommended. The candidate is not an improvement over V92.**

This is a negative result. It is reported in full because the mechanism it tested was
believable, the evidence for it was real, and the reason it fails is measured and
transferable.

---

## 1. Hashes for verification

| Artifact | Path | SHA-256 |
|---|---|---|
| V93 candidate | `experiments/v93_adaptive/candidate.py` | `fa81a78e79d1d3639f036102a212f84c9334971bc34b7d1e1f11c1d53591c8d5` |
| V92 incumbent (unmodified) | `experiments/v92_overflow_guard/candidate.py` | `0d5d356baa25703f1a7b753527d1b39e1c7d63478985913be5b3c2550261b806` |
| V56 ladder opponent | `agents/v56_agent.py` | `d9e9670921b62afedfa8cbc7086d2a2ec19e153ee26006cef477eadd462bd19c` |
| V50 frozen base | `experiments/v50_agent.py` | `e6b50128e023e3b9fafa1841e4cd520c5e581acb48e8628657585c18272eab2b` |

The V92, V56 and V50 hashes are unchanged from the values frozen in
`experiments/v92_overflow_guard/holdout_plan.json`. **No existing agent, doc or test was
modified.** All new files are confined to `experiments/v93_adaptive/`.

Pinned engine: kaggriculture 1.32.7. Runner: `simulation.tournament` /
`simulation.match_worker` (the exact Kaggle loader), same as the V92 holdout.

## 2. What the audit found, and what it ruled out

All 14 official replays were replayed through the pinned engine, observation at `steps[t]`
paired with action at `steps[t+1]`, with `step` reconstructed as `day*24 + hour`. **Zero
cash mismatches on both ledgers in all 14 episodes.** The independent ledger in
`realization_ledger.py` reproduces the prior analyzer's accepted-sales totals exactly
(136,926 / 146,027 / 171,066 / 92,200 / 135,532 / 133,341 / 121,295 / 137,840 / 135,457 /
101,104 / 96,604 / 122,652 / 151,764 / 150,194), which is the cross-check that the replay
is faithful.

**The invalid V88 replay joins were not used.** Nothing in this directory reads
`experiments/v88_terminal_phase/`, consistent with the provenance correction.

Three candidate causes were tested and closed with measurement:

- **Shed overflow beyond V92's guard.** `audit_economics.py` found apparent overflow at eight
  further boundaries (up to 107 units against a 100 cap), which looked like a large
  unhandled lever. `measure_discard.py` instrumented the engine's own
  `_drop_inventories_to_shed` and measured what is *actually* destroyed: **exactly 2 units
  per official game, worth $2–$78**. The apparent drops are `feeder → CORRECT`: market
  settlement, feed consumption, and PICKUP/DROP reshuffles all move units between shed and
  hands. Sizing is identical in the 10 wins and 4 losses, so it cannot be a separator, and
  there is nothing left to extract. **V92's lever is fully spent.**
- **Herd loss.** `audit_herd_shed.py`: peak animals 17, final animals 17, **zero shrink
  events in all 14 episodes**. The engine's hard failure mode
  (`consecutive_unfed >= 2` permanently deletes an animal) never fires.
- **Low-quote WOOL liquidation.** Real and large, and **not loss-specific** — winners
  114158802, 114164630 and 114170594 all show the same $1–$5 day-15-to-17 sales.

The root reason a win/loss separator does not exist is structural: **V50/V92 has no decision
function.** It is a 719-entry open-loop action tape indexed by `step`, plus a market-impact
SELL reordering and a terminal liquidation overlay. The replay evidence is identical in wins
and losses because the policy itself is identical. The prior diagnosis's "no controllable
loss cause" conclusion is correct, and this audit independently confirms it.

## 3. The mechanism tested

Acting on the second clause of the brief (a robust profit opportunity that survives win
controls), I measured a production-vs-realization ledger. `reward = money` (engine line
961) and shed contents are worth $0, so cash is the only score. For episode 114166061:

| item | harvested | sold | realised cash | avg price | peak quote | realization |
|---|---:|---:|---:|---:|---:|---:|
| WHEAT | 595 | 399 | 17,283 | 43.3 | 46 | ~100% |
| STRAWBERRY | 249 | 249 | 42,952 | 172.5 | 220 | ~100% |
| MELK | 72 | 72 | 14,231 | 197.7 | 272 | ~100% |
| MILK | 164 | 164 | 36,239 | 221.0 | 267 | ~100% |
| **WOOL** | **282** | **282** | **6,146** | **21.8** | **218** | **~10%** |
| FERTILIZER | 0 | 317 | 13,108 | 41.4 | 100 | 100% |

WOOL is produced at scale and realized at roughly a tenth of its own peak quote. The cause
is arithmetic, not luck: `MARKET_I0 = 10000`, the market starts exactly at I0, and WOOL uses
`above_func "sq"`, `above_target 3.20`, so price falls as `200 − 0.05805·d²` and hits the $1
floor at `d ≈ 58`. WHEAT and EGG use `"log"` and never saturate at this scale — which is
exactly the difference the ledger shows.

Engine line 659 makes the hold worth considering: a SELL at or below $1 does **not** add
supply, so a floored sale is a pure $1 liquidation of a unit that could be worth $200, and
the only exogenous demand (`_town_consume`) is what allows any recovery. The cohort shows
the quote genuinely recovering inside the game ($18/$31 by day 22 in 114166061, $55 by day
22 in 114167570).

**The candidate (V93):** withhold the WOOL SELL quantity the frozen route adds on any turn
whose *observed* WOOL quote is at or below the $1 floor. Harvest, feed, care, every
non-WOOL order and every unit action are untouched. The trigger is a field of the
observation, not a forecast, so the rule needs no timing model. It is a no-op whenever the
quote is healthy.

## 4. Gate results — FAILED

Gate frozen in `GATE.md` / `gate.json` before any V93 game was run. 11 already-spent seeds
(≥22 prior saved games each, all previously played against V56), both seats, 22 games per
arm. Seeds 93000–93011 were excluded entirely. V56 is this project's own prior submitted
agent and local benchmark, not a public ladder opponent in the V92 official games; it is the
strongest available internal proxy, which is why the matched control arm is required.

| Arm | Games | Record | Score rate | Median margin | Errors |
|---|---:|---|---:|---:|---:|
| A: V93 vs V92 | 22 | 0W–12L–10D | 0.227 | **−4,540** | 0 |
| B: V93 vs V56 | 22 | 10W–12L–0D | 0.455 | **−8,700** | 0 |
| Control: V92 vs V56 | 22 | 10W–12L–0D | 0.455 | −2,534 | 0 |

| Gate condition | Result |
|---|---|
| 1. Zero errors | **PASS** (0 across all 66 games) |
| 2. Action differences actually fire | **PASS** — 176 of 7,909 turns differ, 1,150 WOOL units withheld, **0 non-WOOL differences** and 0 unit-action differences |
| 3. No regression vs incumbent V92 | **FAIL** — 0 wins, median margin −4,540 |
| 4. No score-rate regression vs V56 | score rate **PASS** (0.455 vs 0.455); **median margin FAIL** (−8,700 vs −2,534) |
| 5. Honest sizing | Reported below |

**Overall: FAIL.** Conditions 3 and 4 fail. Per the predeclared `on_fail`, this is a no-go:
no retune, no rerun on different seeds, no submission.

## 5. Why it failed — the mechanism, not the implementation

The overlay fired exactly as designed and still lost. `measure_fire.py` re-ran both
policies turn by turn and priced the decision day by day (seed 94700):

| day | V92 units | V92 cash | V93 units | V93 cash | delta |
|---:|---:|---:|---:|---:|---:|
| 15 | 19 | 19 | 1 | 1 | −18 |
| 16 | 22 | 22 | 0 | 0 | −22 |
| 17 | 30 | 30 | 4 | 4 | −26 |
| 18 | 22 | 36 | 12 | 26 | −10 |
| 19–29 | 109 | 253 | 109 | 253 | 0 |
| **total** | **220** | **462** | **139** | **381** | **−81** |

**The premise was wrong, and specifically wrong in a way the audit data had hinted at but
I under-weighted.** V92 was *not* dumping WOOL at the floor and then watching the price
recover. It was already almost perfectly timed: it sold 19/22/30/22 units on days 15–18 and
then 12/12/16 units on days 19–22, buying $36, $70 and $58 on days 18, 22 and 29. **The
deferred units were simply never recovered** — V93 ended with 81 fewer units sold and $81
less, and the *identical* realization on days 19–29 shows the withheld WOOL was not
recovered at a better price, it was not recovered at all.

Two engine facts explain this, and they are the transferable finding:

1. **The terminal overlay is the safety net that the hold defeated.** The frozen route
   liquidates the entire projected shed at step 718 with `replace=True`. By suppressing
   WOOL sells during the glut, V93 shrank the very stock that the terminal step was
   designed to cash in, and the step-718 list is a `replace` take-over — it rebuilds from
   current shed contents, so units withheld upstream and never re-offered simply do not
   appear. score is cash, so stock left in the shed is worth exactly $0.
2. **Supply is not the binding constraint; the shed is.** `shedCapacity` is 100 and
   `_commit_unit` blocks `BUY_PRODUCT` when the shed is full, while the end-of-day drop
   deletes overflow outright (engine line 857). Holding WOOL keeps shed occupancy high,
   which blocks the wheat purchases the feed chain depends on, and the farm carries a
   full-shed overflow risk on every boundary. The 10 draws and 12 losses with a −4,540
   median are consistent with that coupling rather than with a pricing error.

The honest reading is that the 10% WOOL realization gap I measured in the *official
replays* is not a loss of value at all. It is the price the market charged, and V92's
existing timing was already extracting essentially all of it. A large realization gap
measured against a *peak* quote is not by itself evidence of waste; the counterfactual has
to be measured, and when it was, it was negative.

## 6. Sizing and what would be needed

The paired-seed bootstrap 95% interval on V93's win rate against V92 is reported by the
runner in `summary.json`. The margin effect (−4,540 median, 0 wins in 22 paired games) is
large relative to the sample and points one way. The **score rate against V56 is exactly
neutral** (0.455 vs the 0.455 control), which is the same neutrality V92 itself showed
against V56 — so the score-rate arm carries no signal either way and only the margin arm
distinguishes V93 from V92. That is reported as measured rather than dressed up.

## 7. Recommendation to the root reviewer

- **Do not submit V93.** It is strictly worse than the incumbent on the only arm with
  signal.
- **Retain the audit artifacts.** `realization_ledger.json` (per-product harvest → sale →
  discard → stranded ledger over 14 official games, zero cash mismatches, exact agreement
  with the prior analyzer) and `discard_measurement.json` (exact engine-measured overflow)
  are reusable, verified measurements that no prior document in the repo contains. The
  discard result in particular closes the V91/V92 overflow axis permanently.
- **Two structural findings worth carrying forward**, both from the engine source and
  independent of this failed candidate:
  1. V50/V92 is an open-loop tape with no decision function. Any "adaptive" claim on this
     lineage has to be implemented as a post-hoc overlay, exactly as V92 and V93 both did.
  2. The shed, not the market price, is the binding constraint. `BUY_PRODUCT` and
     `BUY_ANIMAL` both fail at capacity, and the end-of-day drop deletes overflow. Any
     strategy that holds stock must be evaluated against that constraint, not against the
     product's own price curve — which is the mistake this experiment made and has now
     measured.

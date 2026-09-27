# V89: bounded ablation of `reorder_market(impact_slots)` — REJECTED (gate FAIL)

Read-only. Frozen `agents/v56_agent.py` was copied and modified; **no frozen file was altered**.
No submission. No fresh or sealed seed was used. SHA and gate were frozen in `plan.json` before any
game was run.

## What the ablation is

One behavioural difference, isolated to a single call site in `agent()`:

```python
# removed
action = reorder_market(obs, action, mode="impact_slots")
```

Everything else is byte-identical to `agents/v56_agent.py`: the embedded `_ACTIONS` tape (719
entries), the seat-1 step normalization, the `_PLANNER` base call, `CLEARANCE_STEP = 629` with
`terminal_market(..., "collision", replace=False)`, the late-collision `apply_overlay`, and the
all-PASS exception fallback. `reorder_market` is still imported and defined, so the module surface
is unchanged; only the call is removed.

| File | SHA-256 |
|---|---|
| `experiments/v89_impact_ablation/candidate.py` | `b772baee2a9149ec52d0e7c440c1e0cdbc3ad95572c8701b5ba4014ee649b9f8` |
| `agents/v56_agent.py` (base, unmodified) | `d9e9670921b62afedfa8cbc7086d2a2ec19e153ee26006cef477eadd462bd19c` |

## Equivalence challenge: raised, tested, and NOT proven

The challenge was that a single swapped frame with unchanged final cash might mean the rule is
behaviourally inert. A synthetic settlement test against the pinned engine settles it, using the
exact swap observed in the audit (`SELL STRAWBERRY 8` and `SELL FERTILIZER 14` exchanged):

| Scenario | Seat 1 proceeds, order A | Seat 1 proceeds, order B | Identical? |
|---|---:|---:|---|
| Opponent sells nothing | 8,840 | 8,840 | **yes** |
| Opponent sells STRAWBERRY 5 | 8,765 | 8,735 | **no** (−30) |
| Opponent sells FERTILIZER 5 | 8,826 | 8,829 | **no** (+3) |

The two seats settle in lockstep, so a reordering is a no-op only when the opponent is not selling
a product whose price is being re-anchored. When they are, proceeds move. **The ablation is not
behaviourally equivalent**, so the panel was warranted and was run.

This also corrects my own offline harness, which was unreliable. It reported identical final cash
alongside a ~$93k sell-proceeds gap; the cause is that a replay harness re-settles a *divergent*
stream from recorded observations, so the accepted set and the recorded cash stop corresponding once
one seat's actions change. The panel is the authoritative measurement; the harness is not.

## How often the rule actually fires

Across 8 saved spent-seed replays, comparing frozen V56 against the ablation frame by frame:

| Seed | Frames where the market differs (of 720) | First change |
|---|---:|---|
| 92802 | 1 | step 600 (d25h00) |
| 92804 | 1 | step 624 (d26h00) |
| 93700 | 2 | step 163 (d6h19) |
| 94110 | 1 | step 433 (d18h01) |
| 94111 | 1 | step 552 (d23h00) |
| 94112 | 1 | step 360 (d15h00) |
| 94113 | 2 | step 457 (d19h01) |
| 94114 | 1 | step 673 (d28h01) |

**The rule fires on 1–2 frames in 720** and every observed change is a reordering of SELL orders
for different products, never an added or removed order. That is consistent with the upstream
description "safe sorting of sell slots without order dropping".

## Panel result: 12 spent seeds, both seats, vs V50 and V56, 48 games

| Opponent | W | L | D | Win rate | Median margin | Mean coins | Errors |
|---|---:|---:|---:|---:|---:|---:|---:|
| v50 | 13 | 11 | 0 | 54.2% | +2,313 | 95,299 | 0 |
| v56 | 9 | 3 | 12 | 37.5% | 0 | 92,815 | 0 |

## Predeclared gate, evaluated as frozen

| Criterion | Threshold | Result |
|---|---|---|
| Zero errors | candidate + opponent + infra + timeouts == 0 | **PASS** (0) |
| Wins vs V50 | >60% (≥15 of 24) | **FAIL** — 13/24, 54.2% |
| Wins vs V56 | >60% (≥15 of 24) | **FAIL** — 9/24 decisive, 37.5% |
| Median margin vs V50 | positive | **PASS** — +2,313 |
| Median margin vs V56 | positive | **FAIL** — 0 |

**VERDICT: FAIL. 3 of 5 criteria failed. Stopping, no retune, no rerun, no fresh seed.**

The V56 row is the informative one: 12 of 24 games are exact draws with a median margin of 0. That
is the V56-vs-V56 self-play signature already measured in V82 (V56 against itself gave 7-7-58 on 72
games, median margin 0). The ablation candidate and frozen V56 share the same production tape and
the same terminal and overlay rules, so removing a rule that fires on 1–2 sell-order reorderings
leaves them functionally the same policy, and they tie. The gate required ">60% wins", which 9
decisive wins in 24 cannot deliver under any honest reading.

## What this tells the V88 question

V88 could not isolate `impact_slots` from the portfolio difference. V89 is that isolation, and the
answer is that **`impact_slots` is not load-bearing**: removing it costs nothing measurable, and
gains nothing measurable. So the days 12–23 deficit V56 shows against V50 in V88 is **not**
attributable to `impact_slots`. It remains attributable to the portfolio difference in the
production tape, which V89 did not touch and which is out of scope for a wrapper ablation.

That closes the one V56-only behaviour that was active during the days 12–23 window. There is no
remaining wrapper-level difference between the two frozen agents to test.

## Limits

- The audit covers 8 spent seeds and the panel 12; both are subsets of the 28 spent seeds that have
  direct V50-vs-V56 replays. Neither is a fresh or sealed holdout.
- The 12 seeds were used in prior work and V50 and V56 have both been tuned on some of them, so the
  54.2% and 37.5% figures are not unbiased estimates of either agent's strength.
- The synthetic equivalence test uses a constructed market state, not a replay, though it exercises
  the same `_process_market` and `_commit_unit` code the engine runs.
- The frame-level firing counts come from offline comparison on recorded observation streams; they
  measure action divergence, not score effect.
- The offline harness's unreliability is documented above and its earlier accepted-transaction and
  sell-proceeds figures should not be quoted.
- Nothing here supports a submission or a promotion claim. The gate semantics were preserved: the
  panel was run only after equivalence was disproven, and a failure ends the branch.

## Artifacts

- `candidate.py` — the ablation
- `plan.json` — SHA and gate, frozen before the run
- `divergence_audit.py` / `divergence_audit.json` — frame-level divergence audit
- `runs/panel_92802/` — 48 games, all replays retained, exact-loader, pinned 1.32.7

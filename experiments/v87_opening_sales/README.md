# V87: opening harvest-to-sale — REJECTED on the predeclared gate (0-32)

Read-only research. No submission was made. No fresh holdout was used. All outputs live under
`experiments/v87_opening_sales/`. The candidate SHA was frozen in `plan.json` before the screen ran,
and the gate was fixed in that file before any result was known.

## Verdict

**REJECTED. 0 wins, 32 losses, 0 draws.** Median margin −79,260 vs V50 and −80,012 vs V56. Zero
execution errors, so this is a genuine strategic failure, not a crash.

The branch stops here per the predeclared instruction: no retune, no rerun, no fresh seed.

## What the diagnostic found (this part was correct and is reusable)

`diagnose_opening_sales.py` replays saved actions through the pinned Kaggriculture 1.32.7 engine and
records, per seat, what the agent **ordered** versus what the engine **accepted**. Results on
`saved replay v56-seed-94400-ab` and `v56-seed-94401-ab`, both `max_cash_error` 0.0:

| Opening days 0–5 | Ordered units | Accepted units | Rejected | Proceeds |
|---|---:|---:|---:|---:|
| V56 seed 94400 | 49 | 49 | **0 (0.0%)** | $3,035 |
| V56 seed 94401 | 49 | 49 | **0 (0.0%)** | $3,035 |
| V50 seed 94400 | 49 | 49 | **0 (0.0%)** | $3,034 |
| V50 seed 94401 | 49 | 49 | **0 (0.0%)** | $3,034 |

**The premise in the brief is answered: the opening gap is neither failed SELL orders nor
rejection.** V56 orders 49 units and the engine accepts all 49. V50 on the same seeds does exactly
the same thing for the same ~$3,034. The V83 comparison (V56 $3,035 vs elite winners $5,319) is a
real gap against the *elite* profile, but V50 does not close it either.

Phase decomposition, seed 94400, exact settlement:

| Phase | V50 | V56 | Difference |
|---|---:|---:|---:|
| Days 0–5 | 3,034 | 3,035 | **−1** |
| Days 6–11 | 29,658 | 29,887 | −229 |
| Days 12–23 | 41,072 | 40,598 | +474 |
| Days 24–29 | 36,513 | 32,996 | **+3,517** |
| Final | 75,819 | 71,344 | +4,475 |

**V50's entire advantage is in days 24–29.** The opening window is identical between them, so
"beat V50 in the opening" was never available as a target.

The mechanism the diagnostic did find is real: V56 holds 19–20 plants at `yield_units > 0` from day
1, issues its first `HARVEST` only at step 61 (day 2, hour 13), spends **67 `PASS` turns** across
days 1–2 while those crops sit ready, and banks nothing but a day-0 wheat dribble ($449) and
fertilizer resale (~$2,600). The 12 melon planted on day 0 are worth ~$268 each in the days 1–5
window and ~$73 by day 11, when V56 finally sells them.

## Why the candidate failed: two implementation defects, not a wrong hypothesis

`candidate.py`, sha256 `2c2c8d8d4c2fe9a8d6e4437b232e62b4441e426be977d59228d3a7d4fd1459e6`, wrapping
`agents/v56_agent.py` (sha256 `d9e9670921b62afedfa8cbc7086d2a2ec19e153ee26006cef477eadd462bd19c`).
Offline fidelity: 128 changed frames, 114 `HARVEST` actions across days 0–5, zero errors. The overlay
did exactly what it was written to do.

**Defect 1 — harvested goods never reached the shed.** The overlay commanded `HARVEST` but never
commanded the walk-to-shed and `DROP` that `_commit_unit` requires before a `SELL` can commit
(`if private["shed"].get(item, 0) <= 0: return False`). Measured in the rejected run: **26–41
`HARVEST` actions per day and zero `DROP` actions until day 5.** The shed held 3–10 wheat and
nothing else. Every harvest was wasted worker-turn cost with no cash return, and the overlay
suppressed the `PASS`/idle turns that the frozen route had been using.

**Defect 2 — it starved the herd.** The overlay's own docstring claims it "never displaces a FEED,
CARE or WATER action", and that part held. But it replaced the frozen route's *idle* turns with
harvesting, and those idle turns were not idle: measured herd attrition in the rejected run shows
**2 COW on day 1 → 0 COW on day 2**, against the frozen baseline's 4 COW by day 6. Animals with
`consecutive_unfed >= 2` are deleted at the day-end tick
(`_daily_refresh_animals`, lines 817-820). The overlay destroyed the productive herd it was meant to
help, and the gap in later phases shows it: days 6–11 net proceeds collapsed relative to baseline.

Net effect: 32/32 losses with margins far larger than the baseline's, i.e. a severe regression rather
than a marginal one.

## What is worth keeping

- `diagnose_opening_sales.py` and `opening_sale_diagnostic.json`. The ordered-versus-accepted
  decomposition is reusable and the finding is settled: **the opening sales deficit is a production
  and scheduling problem, not a market-access or order-rejection problem, and it is identical for
  V50 and V56.**
- The measured fact that V56 idles 67 `PASS` turns on days 1–2 with 20 ready crops and a high melon
  quote, and that the same melons are worth ~3.7x more early than at day 11.
- The pre-registered screen design: eight spent seeds, both seats, against both V50 and V56, with
  the SHA and the gate frozen in advance.

## What is not worth keeping

`candidate.py` as written. The harvest idea was sound in the abstract, but the implementation was
incomplete in exactly the way that makes an overlay dangerous: it added a worker turn without
completing the task's follow-through (pickup → walk → drop), and it consumed the slack that the
herd's feed cycle depended on. A correct version would need a full harvest-to-shed state machine
per hand, plus a hard guarantee that animal service is never displaced — which is a substantially
larger change than a bounded overlay, and would need its own isolation argument before any panel.

## Limits

- One candidate, one screen, 32 games. The rejection is unambiguous in direction and magnitude.
- The diagnostic ran on two seeds (94400, 94401) from one saved directory. The ordered-versus-accepted
  result (0% rejection) is consistent across V50, V56 and both seeds, but it was not checked on the
  other six panel seeds.
- The day-0-5 phase comparison against elite uses the 100-game elite corpus, which is purposive and
  outcome-conditioned, not a controlled experiment.
- No fresh holdout. No submission. Nothing here authorises a promotion.

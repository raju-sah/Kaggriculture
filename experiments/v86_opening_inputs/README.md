# V86: opening input budget — REJECTED before the panel

No panel was run. No seed was spent. No submission was made. The candidate is retained for audit
only.

## What was built

`experiments/v86_opening_inputs/candidate.py`, sha256
`9dfe5239511579fc06503901b980377a9acf52fb6181cb1eb4ae2e3ff9261c0c`, wrapping the frozen
`agents/v56_agent.py` (sha256 `d9e9670921b62afedfa8cbc7086d2a2ec19e153ee26006cef477eadd462bd19c`).
Loader contract verified: `_kaggle_submission_entrypoint` is the last callable.

The intended intervention was the one number where V56 sits furthest from the elite profile. Exact
reconstruction of a saved V56 game (seed 94400, seat 0, `max_cash_error` 0.0) against the 100-game
elite means:

| Opening days 0–5 | V56 | Elite winner | Elite loser |
|---|---:|---:|---:|
| Accepted sales | 3,035 | 5,319 | 3,695 |
| Product purchases | **967** | **2,657** | 1,327 |
| Animal purchases | 2,600 | 3,430 | 2,782 |

## Why it was rejected

**The premise was wrong.** The overlay was designed to spend "opening capital V56 is idling on feed
and soil". V56 is not idling capital. It is **broke from hour 21 of day 0 onward**:

```
day 0, hour-by-hour cash:
h00 3000 → h02 1042 (5 hires + 2 cow + 2 sheep) → h12 482 (melon/wheat seeds)
→ h18 42 → h21 12 → h25 8
```

After the opening it never recovers above ~1,000 until day 10, and it holds 12 coins at day 1. The
guard `MIN_CASH_AFTER = 200` is therefore not a conservative safety margin, it is a description of
the state: **there is no opening cash to spend on inputs.** An overlay that can only fire when the
farm is rich is an overlay that cannot fire at all in the window it targets.

Measured against the saved replay, the corrected hour-0 variant changed **2 frames in 720**
(fertilizer on days 0 and 5, wheat on day 0). It is inert. A candidate that changes two turns cannot
win a panel, and shipping it would be submitting noise.

**The under-buying is a symptom, not the cause.** V56 buys 967 of product against the elite losers'
1,327 because it has no money to buy with, and it has no money because it spends 1,800 on two cows
and two sheep, 1,040 on seeds, and hires five hands in the first two hours. The elite profile buys
*more* animals in the same window (3,430 vs 2,600), which is only possible because elite agents
sell more early (5,319 vs 3,035) and are not cash-bound at hour 21.

So the causal chain runs the other way:

> V56 sells less early → V56 is cash-bound from day 0 → V56 cannot buy inputs →
> V56 under-buys product → V56 produces less

Buying more input is not available as an intervention. The binding constraint is **early sale
volume**, and the overlay was aimed one step downstream of the actual problem.

## What this says about the remaining plan

Three consecutive overlays have now been rejected for the same underlying reason, and it is worth
naming it plainly:

| Branch | Aimed at | Why it failed |
|---|---|---|
| V80 | day-6 animal substitution | converted sheep starved; feed route not extended |
| V81 | day-6 expert switch | wool gained, three other product lines collapsed |
| V84 | feed reserve | lever is +1 unit/interval against a 13,920 median margin |
| V86 | opening input budget | the budget does not exist; farm is cash-bound at hour 21 |

Every one of them tried to make V56 *spend* its way out of a problem. The elite evidence says the
advantage is execution — 1.15x more sales from an identical asset base — and V56's specific measured
deficit is that it **liquidates less in the opening week** than even the elite losers do
(3,035 vs 3,695). That is a selling-side and scheduling problem, not a buying-side one, and none of
these four branches touched it.

**No submission was made.** The live submission remains `56544001` (`v56_agent.py`, public score
1,181.0), which is the best-measured artifact currently in hand. Submitting an inert candidate
would be strictly worse than not submitting, and the recorded cost of a bad submission in this
project is severe: `56583862` (v66) scored 464.6, a **−716 regression** against the live v56.

## Limits

- Rejected on an offline single-replay inspection plus engine-rule reading. V86 was never run in a
  live game, so its effect is unmeasured; the claim is that it is inert (2 changed frames), which is
  measured, not that it is harmful.
- The hour-by-hour cash trace comes from one saved V56 game on seed 94400. V56's cash trajectory
  varies by seed, though the V83 elite corpus shows the cash-bound opening is the common case
  (elite day-6 cash means: 361 winners, 594 losers).
- No fresh seeds spent. Nothing here supports a promotion or submission claim.

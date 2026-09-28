# V93 adaptive candidate — mechanism analysis and frozen predeclared gate

Status at time of writing: **gate frozen, no games run yet.**
Author: independent candidate engineer. No Kaggle submission is planned or made.

## 1. Evidence base and provenance

Sources, all read-only, none modified:

- `experiments/kaggle/v92_official/episode-*-replay.json` — the 14 official V92 episodes.
- `experiments/v92_official/replay_summary.{csv,json}` — the prior analyzer's output.
- `docs/V92_OFFICIAL_10_GAME_DIAGNOSIS_2026-09-27.md`, `docs/V92_SUBMISSION_2026-09-27.md`.
- `docs/V88_REPLAY_PROVENANCE_CORRECTION_2026-09-27.md`.
- The pinned installed engine, kaggriculture 1.32.7.

**The invalid V88 replay joins are not reused.** Per the provenance correction, V88's
replay-derived direct-match and phase conclusions come from joining on `game_id` alone, and
those joins are misattributed. Nothing in this directory reads `experiments/v88_terminal_phase/`.
Every number below is recomputed from the 14 official replays with the same alignment the
prior analyzer validated (observation at `steps[t]` pairs with the action at `steps[t+1]`;
public replays omit `observation.step`, so it is reconstructed as `day * 24 + hour`).

Audit integrity: all 14 episodes replay with **zero cash mismatches** on both ledgers, and my
independent `realization_ledger.py` reproduces the prior analyzer's accepted-sales totals
exactly (e.g. 136,926 / 146,027 / 171,066 / 133,341 for episodes 114158802 / 114160308 /
114161728 / 114166061). The two independent replays agreeing is the correctness check for
everything that follows.

## 2. Why the levers the prior diagnosis considered are dead ends

I first re-tested the three candidate causes the V92 diagnosis left open, and each is now
closed with a measurement rather than an argument.

**End-of-day shed overflow is already fully extracted.** The V92 guard covers the
day-23 -> day-24 boundary only. `audit_economics.py` found apparent overflow at eight further
boundaries, which looked like a large unhandled lever. Exact measurement via
`measure_discard.py` shows the reality: **exactly 2 units are destroyed per official game**,
worth $2 to $78 at the prevailing quote. The apparent drops are mostly
`feeder -> CORRECT` at days 13/16/17/18/19/25/28 (market settlement, the FEED-consumption
effect, and pickup/place reshuffles all move units between shed and hands). The engine
deletes overflow with `del inv[item]`, so this cannot be a win/loss separator anyway: the
sizing is identical in the 10 wins and the 4 losses.

**Herd loss is never a cause.** `audit_herd_shed.py` records peak animals = 17 and
final animals = 17 with **zero** shrink events in all 14 episodes. The engine's hard failure
mode (`consecutive_unfed >= 2` permanently deletes an animal) never fires. There is no herd
to rescue.

**Low-quote WOOL liquidation is not loss-specific.** Confirmed and now quantified: the
realization ledger below shows WOOL collapsing to a $1 quote, and it does so in wins too.

The prior diagnosis's conclusion — that no controllable loss cause is isolated — is correct,
and the reason is structural: **V50/V92 has no decision function.** It is a 719-entry
open-loop action tape indexed by `step`, plus a market-impact SELL reordering and a terminal
liquidation overlay. The replay evidence is identical in wins and losses because the policy
itself is identical. There is no "loss state" for the agent to detect.

## 3. The mechanism I am acting on

Since a win/loss separator does not exist, I am using the second clause of the brief: a
robust profit opportunity that survives win controls.

`reward = float(money)` (engine line 961). Shed contents, tiles, herds and seeds are worth
exactly $0 at the end. So cash is the only score, and any unit that is *produced* but never
converted to cash is work thrown away.

The realization ledger for episode 114166061 (a loss) shows the position clearly:

| item  | harvested | sold units | realised cash | avg price | peak quote | realization |
|-------|----------:|-----------:|--------------:|----------:|-----------:|------------:|
| WHEAT | 595 | 399 | 17,283 | 43.3 | 46 | ~100% |
| STRAWBERRY | 249 | 249 | 42,952 | 172.5 | 220 | ~100% |
| MELON | 72 | 72 | 14,231 | 197.7 | 272 | ~100% |
| MILK | 164 | 164 | 36,239 | 221.0 | 267 | ~100% |
| **WOOL** | **282** | **282** | **6,146** | **21.8** | **218** | **~10%** |
| FERTILIZER | 0 | 317 | 13,108 | 41.4 | 100 | 100% (bought) |

**WOOL is produced at scale and realized at roughly a tenth of its own peak quote.** In
episode 114161728 the WOOL collapse did not happen (11,492 realised against a 200+ peak), and
that is the single biggest win in the cohort at +133,896. Where the collapse happens the
contribution is small; where it does not, WOOL is worth a six-figure sum.

The engine cause is the pricing curve, and it is deterministic and known in advance
(`kaggriculture.py` lines 38-56, 192-206):

- `MARKET_I0 = 10000` and the market **starts at exactly I0**, so every product begins at the
  peak of the curve and every sale immediately enters the glut branch. There is no headroom.
- WOOL uses `above_func: "sq"`, `above_target: 3.20`, base 200. Price falls as
  `200 - 0.05805 * d^2` where `d = inventory - 10000`, hitting the `$1` floor at `d ~ 58`.
  WOOL is the most saturating product in the game.
- WHEAT and EGG use `above_func: "log"`, which has no practical saturation at this scale.
  Their realized prices match their peak quotes, which is exactly what the ledger shows.

So the collapse is not bad luck and not opponent-driven. It is arithmetic.

**The control.** A sheep held 6 WOOL stops producing (`yield_units` is capped by `min(max_held,
...)` at line 827). The farm must clear the stack. The unexploited move is to wait and sell
*earlier* units at *higher* price:

> **Do not add new WOOL to the sell queue on a turn whose observed WOOL quote is at or below
> the price floor. Keep harvesting and feeding exactly as before, and let the town drain the
> market. Sell the existing WOOL as soon as the quote recovers above the floor.**

The forecast-free property is the whole point: the trigger is the **currently observed quote**,
which is a field of the observation, not a prediction of when it will recover. The decision
rule never needs to know the future, only the present.

Why this should be worth money rather than just moving cash around:

- The engine floors the price at 1 and line 659 does **not** add supply for a sale at $1 or
  below, so a floor-price sale is a pure $1 liquidation that also fails to depress the
  opponent. It is the worst possible time to sell.
- Withholding supply lets the exogenous town demand (`_town_consume`, lines 728-747) — the
  only exogenous demand in the game, and the entire reason prices recover at all — clear the
  glut, so a later sale receives a strictly higher price for the same unit.
- Crucially the quote was observed at **$55 by day 22 in 114167570** and **$18/$31 by day
  22 in 114166061**, i.e. the recovery is real and lands inside the game, which is the only
  thing that makes deferral worth anything.

### Why this survives the win controls

The brief requires the opportunity to survive the wins, and this is the test the prior
diagnosis could not apply to WOOL because it could not establish that waiting pays. It is
now testable, because the candidate makes **no change at all when the WOOL quote is healthy**:

- In a game where WOOL holds a good quote the entire time, the rule never fires and V93 is
  byte-identical to V92. Wins like 114161728 (WOOL 11,492, no collapse) are untouched.
- In a game where WOOL is in glut, V93 holds and the cohort shows the quote recovering to
  $18-$55 later, so the held units are sold higher.
- The cohort shows the collapse is **not** loss-specific (winners 114158802, 114164630 and
  114170594 all show the same $1-$5 day-15-to-17 WOOL sales), which is precisely why the
  upside is a *profit* argument rather than a win/loss argument.

## 4. What the rule deliberately does not do

- It does not stop production. Harvest and feed are untouched; the herd is identical.
- It does not suppress a SELL that the tape or the terminal overlay already made. V93 only
  ever *withholds new WOOL sell volume on a floored turn*, and it restores the tape's own
  WOOL order on any later turn whose quote is above the floor.
- It does not touch WHEAT, FERTILIZER, MILK, EGG, STRAWBERRY or MELON, which realize at
  ~100% of their peak quote.
- It does not add, remove or reorder any non-WOOL market order, and it never touches a unit
  action. The overlay runs after V92's own guard.
- It is a single, auditable overlay seam over the frozen V92 source, exactly as V92 did over
  V50. The V50 source stays embedded and byte-identical.

## 5. FROZEN PREDECLARED GATE

**This gate is frozen before any V93 game is run. It is written here first so it cannot be
moved after seeing results. If V93 fails it, the result is a no-go; there is no retune, no
variant, and no fresh-seed run.**

Seeds: already-spent seeds only, both seats, run through the exact Kaggle loader
(`simulation.tournament` / `simulation.match_worker`, pinned kaggriculture 1.32.7).
Seeds 93000-93011 are **consumed** and are not used, not as fresh seeds and not at all.
The seed set is listed in `gate.json` and was chosen from seeds with many prior games in
`experiments/**/games.jsonl`; spending them again costs no new evidence.

Arms:

- **A.** V93 vs V92 — both seats, every seed. This is the paired arm. The engine is
  deterministic for a fixed seed, so the same seed in the same seat order gives the same
  board, the same market and the same opponent behaviour; V92 and V93 differ only by the
  overlay. This isolates the change.
- **B.** V93 vs V56 — both seats, every seed, with a matched frozen **V92 vs V56** control on
  the same seeds in the same seats. V56 is this project's own prior submitted agent and
  local benchmark (it is not a public ladder opponent in the V92 official games), and it is
  the strongest available internal proxy, so this is the arm that matters. The matched
  control is required: V92 was already measured at exactly neutral against V56, so a
  V93-vs-V56 number is meaningless without the control.

**Predeclared pass conditions, all of which must hold:**

1. **Zero errors.** `candidate_errors + opponent_errors + infrastructure_errors + timeouts == 0`
   across every run in both arms.
2. **Action differences actually fire.** The number of turns where V93's submitted market list
   differs from V92's must be greater than zero, and the differences must be confined to
   WOOL SELL quantity. A run where the overlay never fires is an invalid test, not a win.
3. **Arm A, no regression against the incumbent.** V93 must not lose its paired head-to-head
   against V92: wins plus draws against V92 must be at least as many as losses, and the
   median paired coin margin must be greater than or equal to zero.
4. **Arm B, no score-rate regression versus V56.** V93's score rate against V56 must be within
   5 percentage points of the matched frozen V92-vs-V56 control score rate on the same seeds
   in the same seats, and the median paired coin margin against V56 must not be negative by
   more than 5 percent of the control's median margin.
5. **Honest sizing.** The reported effect must be reported with its confidence interval and
   its raw per-game numbers, and the report must state plainly whether the effect is
   distinguishable from zero at this sample size. A positive median on a handful of games
   that the interval straddles zero is reported as **inconclusive**, not as a pass.

**On pass:** report to the root reviewer with artifact paths and hashes. The root reviewer
decides on any Kaggle submission. This candidate engineer does not submit.
**On fail:** no-go, no retune, no rerun on different seeds, no submission.

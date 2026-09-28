# V107 precommitted fresh holdout gate

**WRITTEN BEFORE ANY FRESH SEED WAS OPENED.** The candidate hash below is frozen
from the built file. The spent-seed screen that motivated this gate is
development data and is **not** holdout evidence. No seed in the range below has
been run. Nothing will be submitted to Kaggle; the user submits.

## What is frozen

| Item | Value |
|---|---|
| Candidate | `experiments/v107_commandcode/candidate.py` |
| **Candidate SHA-256** | **`7623988b6a1b2dff66759951f4843b5fd546ed1ded115597998817dc45953d0e`** |
| Base (embedded verbatim) | `experiments/v50_agent.py`, sha256 `e6b50128e023e3b9fafa1841e4cd520c5e581acb48e8628657585c18272eab2b` |
| Engine | kaggle-environments 1.32.7, `kaggriculture.py` sha256 `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e` |
| Episode | 720 steps, 24 turns/day, 30 days |
| Rule | one-cow no-Yarn day-6 swap: `SHEEP 2` → `SHEEP 1` + `COW 1`, cow carried on the tape's own sheep pickup and placed on that sheep's pasture |
| Gate | visible MILK sink (PIZZA / ICE_CREAM / SMOOTHIE) and no `YARN_STORE` |
| Spent screen (development) | 160001–160012 only |

## Holdout seed range (fresh, unused, frozen now)

**190001–190024** — 24 seeds, both seat orders.

Explicitly excluded as spent or protected: 137501–137524, 150001–150015,
160001–160060, 170001–170024, 180001–180024, 92600–95300, 94700. If 190001–
190024 is run, it is spent afterwards and is not reused as a fresh holdout.

## Design

Every opponent is run twice on identical seeds and seats — once with V107 and
once with the **frozen V50 base** — so the reported quantity is the **paired
delta**, `margin(V107 vs OPP) − margin(V50 vs OPP)`, which cancels the
opponent's own strength. The engine is deterministic; seat-swap margins are
verified identical where the opponent permits, so the independent unit is the
**seed** (24 per opponent), not the game.

| Arm | Purpose |
|---|---|
| **V92 — primary** | the matchup that the two-cow V105 regressed on; also the strongest *known* rival to V50 (V50 is 0W–24L vs it on dev) |
| V56 — control | the strongest opponent overall |
| V50 — control | mirror; must show the swap helps its own base |

## Numerical gate (decided now, before the seeds are opened)

Pass requires **ALL** of:

1. **V92 primary, paired.** Mean paired delta > **+$300** and a **majority** of
   seeds strictly positive (≥ 13 of 24).
2. **V92 primary, outcome preservation.** The V107 arm's official W/L vs V92 must
   not be worse than the V50 control arm's, and there must be **zero win→loss
   flips** on any seed where the control won and V107 lost. *This is the criterion
   that V105 failed (flips on 160005/160008) and it is included precisely for
   that reason — margin alone is not sufficient.*
3. **V50 mirror.** Mean paired delta > **+$300**, and V107 must beat V50 on a
   majority of seeds.
4. **V56 control.** Mean paired delta > **+$300**.
5. **Triggers.** The rule fires on **≥ 8 of 24** fresh seeds. (V99's gate died at
   2/24; a rule that rarely acts cannot be a real improvement even if it is safe.
   V107 fires 7/12 = 58% on dev, so 8/24 = 33% is a deliberately low bar.)
6. **Cleanliness.** Zero candidate errors, zero infrastructure errors, zero
   timeouts; the three-step chain (BUY COW d6h6, PICKUP COW, PLACE COW) present
   on every seed that fires; and the cow alive on a PASTURE at season end on
   every firing seed.
7. **No harm.** No seed may show a paired delta worse than **−$2,000** against
   any opponent.

Any failure = **NO-SUBMIT**; the four Kaggle slots are kept.

## What passing does and does not mean

Passing means the local evidence is consistent with a real improvement and is
worth the user's attention with a reviewable artifact. It does **not** mean the
candidate is top-ten, and this gate makes no such claim: 24 seeds cannot support
one. The V101–V107 history is a record of locally-positive rules that failed a
fresh panel, which is exactly why this gate is frozen in advance and run once.
Submission remains the user's decision, made separately.

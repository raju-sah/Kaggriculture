# V107 — V50 + one-cow no-Yarn day-6 swap: spent-seed screen

**No Kaggle submission was made. No fresh or protected seed was used
(137501–137524 / 170001–170024 / 180001–180024 all untouched).** All evidence
below is spent-seed, exact-loader, paired against a matched control.

## Candidate

| Item | Value |
|---|---|
| File | `experiments/v107_commandcode/candidate.py` |
| **SHA-256** | **`7623988b6a1b2dff66759951f4843b5fd546ed1ded115597998817dc45953d0e`** |
| Base | `experiments/v50_agent.py`, official prior-best public agent (1233.2) |
| Base SHA-256 | `e6b50128e023e3b9fafa1841e4cd520c5e581acb48e8628657585c18272eab2b` (embedded verbatim; file untouched, re-verified after build) |
| Loader | binds `_v107_entrypoint` (last callable), verified with `get_last_callable` |
| Engine | kaggle-environments 1.32.7, `kaggriculture.py` `bc8a5487…653e` |

V107 is V50 verbatim plus exactly one intervention, and **does not include the
V92 day-23 overflow guard**, per instruction. The intervention is the one-cow
no-Yarn day-6 swap:

- **buy** `BUY_ANIMAL SHEEP 2` → `SHEEP 1` + `COW 1` at d6 h6;
- **pickup** the tape's first sheep `PICKUP` on day 6 → `PICKUP COW`;
- **place** that carrier's sheep `PLACE` on day 6 → `PLACE COW`;
- gate: a visible MILK sink (Pizza / Ice Cream / Smoothie) and no `YARN_STORE`;
  a strict no-op on every other day and every non-firing seed.

## Micro-check (exact loader, spent seeds, before the screen)

| Seed | Result |
|---|---|
| **160003 (firing)** | V107 day-6 cow buy/pick/place = **1/1/1**, placed on pasture tile **(5, 3)**, **new cow live at season end**, accepted MILK cash **$28,738 vs V50 $27,100 → +$1,638**. V50 control: 0/0/0. |
| **160001 (non-firing)** | seat-0 action frames differing from V50: **0**; final coins identical (**87,595** both). |

So the swap demonstrably buys, collects, places and *sells* a cow on a firing
seed, and is a byte-for-byte no-op where the gate does not fire.

## Screen: 160001–160012, both seats, exact loader, replay-policy `none`, 4 workers

Zero agent errors, zero infrastructure errors, zero timeouts in all jobs.

| Comparison | Official W/L/D | Mean margin |
|---|---|---|
| **V107 vs V50** | **12W–2L–10D** | +$1,158 |
| V50 self-play (control) | 0W–0L–24D | $0 |
| **V107 vs V56** | **12W–12L–0D** | +$3,414 |
| V50 vs V56 (matched control) | 12W–12L–0D | +$1,800 |
| **V107 vs V92** | **12W–12L–0D** | **+$374** |
| **V50 vs V92 (matched control)** | **0W–24L–0D** | **−$791** |

**Paired deltas (V107 − matched V50 control, same seeds/seats):**

| Opponent | Mean delta | Median | better / worse / tie | Worst tail |
|---|---:|---:|---:|---|
| V50 | **+$1,158** | +$182 | 6 / 1 / 5 | seed 160006, **−$744** |
| V56 | **+$1,614** | +$744 | 6 / 1 / 5 | seed 160006, **−$88** |
| V92 | **+$1,164** | +$174 | 6 / 1 / 5 | seed 160006, **−$706** |

**The V92 leg is the important one, and it is the opposite of V105.** The matched
control shows bare V50 is **0W–24L (−$791) against V92** — the V92 overflow guard
genuinely beats the raw prior-best on these seeds. V107 with the one-cow swap
reverses that to **12W–12L (+$374)**. So V107 does not merely avoid the V92
outcome regression that made the two-cow V105 a no-go; it **converts a losing
matchup into a winning one**, with a paired improvement of +$1,164 and the same
bounded worst case (−$706 on one seed).

**Triggers.** 7 of 12 seeds fire the gate (160003–160009); the 5 that do not
(160001, 160002, 160010, 160011, 160012) are **exact ties in every comparison**,
confirming the rule is a strict no-op where it abstains. The single negative
delta is 160006, on all three opponents, and is small (−$706 to −$744).

Seat-swap stability: True for both V50 comparisons and the V92 legs; False for
both V56 legs (V56 is seat-unstable on this seed set, a pre-existing property
noted in V101, not introduced by V107).

## Interpretation, and what this does NOT establish

This is the strongest and most consistent result in the V101/V105/V107 line.
The one-cow swap is:

- **positive in a mirror against its own base**: 12W–2L–10D vs V50, paired +$1,158;
- **margin-positive against V56** relative to the matched V50 control: +$1,614;
- **outcome-positive against V92** where the bare base is 0W–24L: 12W–12L,
  paired +$1,164.

All three opponents, one bounded worst seed (−$706 to −$744), zero errors, and
exact ties on every non-firing seed.

But it is still **spent-seed evidence on 12 seeds**, and this project's history
is a record of exactly this kind of locally-positive small-panel result failing
on a fresh holdout. Specifically:

- 12 seeds is a small panel; the paired medians (+$174 to +$744) are well below
  the means, so the result is carried by a few large seeds.
- The V56 legs are not seat-stable on this set, so V56 deltas carry extra noise.
- The control set was chosen after the fact to *include* V92, because the V105
  no-go was diagnosed on V92. That is legitimate for a screen, but it means the
  opponent set was not chosen blind.
- Crucially, the *gate* (a MILK-sink shop name) is a hand-chosen proxy. V106
  showed that the features available at day 6 do **not** reliably predict which
  seeds benefit, so the 7/12 trigger rate is a known-weak selector.

**Therefore: V107 is the strongest defensible candidate so far and is ready for
a fresh, hash-frozen holdout — but it is not submission-ready on this evidence.**
I have **not** opened any fresh seed; the next step is to write the precommitted
gate, then run it once.

## Next step (gate not yet written, no fresh seed opened)

1. Write `GATE.md` freezing the candidate SHA `7623988b…`, a **fresh unused**
   seed block (**190001–190024**; 137501/170001/180001 and all other spent blocks
   are excluded), and a numerical bar decided **before** the seeds are opened.
2. The bar should mirror what the V101 gate got wrong: require both a paired
   improvement **and** a minimum trigger count, and include a **V92 primary**
   leg with an outcome-preservation criterion (no win→loss flips vs the V50
   control), because that is the axis that killed V105.
3. Run it exactly once. Submit only on a pass, and only when the user says so.

## Artifacts
- `candidate.py` (SHA `7623988b…`), `build_candidate.py` (V50 embedded verbatim, V50 file untouched)
- `microcheck.py` — firing/non-firing proof with accepted-MILK settlement
- `screen.py` — paired runner with hash preflight, return-code and record-count checks
- `runs/{v107_vs_v50,v107_vs_v56,v50_self,v50_vs_v56}/`, `screen_results.json`
- `HANDOVER_LOG.md` — project-wide progress log

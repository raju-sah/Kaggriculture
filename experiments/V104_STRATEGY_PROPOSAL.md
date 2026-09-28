# V104 strategy proposal: why the day-6 cow swap loses to V56, and one new intervention

**Status: analysis + proposal only. No matches were run, no candidate was edited,
and no holdout seed range (137501, 170001, 180001) was touched.** All numbers
below come from the pinned engine (kaggle-environments 1.32.7, `kaggriculture.py`
sha256 `bc8a5487…653e`), from spent artifacts already on disk, and from closed-form
engine arithmetic. The one novel move is the V104 proposal in §5.

## 1. Executive finding — **CORRECTED, see the correction notice below**

> **CORRECTION (2026-09-28).** The first version of this section compared
> **absolute** margins and concluded the cow swap "loses to V56". That was wrong,
> and the error is mine: **absolute margin against a strong opponent conflates
> "the swap hurt" with "the opponent beats V92 anyway."** The correct comparison
> is the swap's effect **relative to a matched V92 baseline on the same seeds**.
>
> The matched control now on disk
> (`experiments/v101_adaptive_swap/runs/fresh_holdout_180001_180024/`, another
> worker's spent run) shows the cow swap vs V56 at **10W–14L, mean +$5,210** —
> i.e. it *loses more often than not* yet is **clearly positive on margin**,
> improving on **all 9 triggering seeds, 18/18 seat games, mean +$3,433 triggered,
> +$1,287 overall, zero negative, zero outcome flips**. So on those seeds the cow
> swap **helps against V56**, and §1's original reading inverted the sign.
>
> **What survives:** the engine mechanics in §2–§3 (V56 is a large milk supplier;
> MILK/WOOL floor to $1 above I0 while EGG does not) are properties of the pinned
> engine and are unaffected. What does **not** survive is the causal claim that
> the swap is specifically value-destroying against V56. The matched control does
> not support that claim.
>
> **Consequence for this proposal:** the GOOSE idea is no longer justified by
> "the cow loses to V56." It is now justified only as a hypothesis that GOOSE
> might retain the gain *without* the outcome-flip risk, and **must be measured
> against a matched V92 baseline**, never against an absolute V56 number. My own
> V101 V56 leg on 170001–170024 has **no matched V92-vs-V56 arm** and therefore
> cannot separate the two explanations; its −$1,846 seat-averaged figure should be
> read as uninterpretable with respect to the swap's effect.

The original (superseded) numbers, retained for traceability: on the 21 firing
V101 holdout seeds, mean absolute margin was +$1,654 vs V92, +$2,244 vs V50 and
−$7,540 vs V56. The V56 column is an absolute margin and is not evidence about
the swap's effect.

## 2. The strategic difference between V56 and V92

Both buy 12 animals and both sell in a shared market, so the difference is not
spend level — it is *what* they produce and *how much of each thing*.

| | V92 | V56 (Lizs, Elo 2522 backbone) |
|---|---|---|
| Herd | 4 COW + 2 SHEEP | 6 COW + 4 SHEEP + **7 GOOSE** |
| Pastures used | 6 | 10 (COW+SHEEP) |
| COOP use | 0 | 7 (GOOSE) |
| Season animal output (uncared, base-price) | ~39 MILK + 27 WOOL | ~78 MILK + 54 WOOL + 78 EGG |

V56 runs **2.3× the animal output** of V92 and, critically, is a *large supplier
of milk* (6 cows) as well as a large consumer. V92's own herd is modest and
light on milk.

The GOOSE line is the structural tell. GOOSE ($300) is cheaper than COW ($400)
and SHEEP ($500), starts producing on **day 4** (vs 6/8), yields **every single
day** (interval 1) for 21 harvest days, and does so in a **COOP**, not a pasture
— so it competes for a *different* tile type and never with the cow/sheep
pastures. Per-animal season totals: GOOSE 78 units, COW 39, SHEEP 27. V56
therefore earns from a third, non-overlapping product stream that V92 does not
touch at all.

## 3. The engine asymmetry that makes the swap lose to V56

This is the mechanism, and it is exact engine arithmetic, not a story.

**MILK and WOOL are floored to $1 the moment supply exceeds I0; EGG is not.**

The pinned `market_price` uses, per product, a different shape above I0
(`MARKET_PARAMS`):

- **MILK** above-I0: `linear` → price falls to `PRICE_FLOOR = 1` almost at once
- **WOOL** above-I0: `sq` → also floors to 1 under glut
- **EGG** above-I0: `log` → decays slowly, stays profitable far above I0

Observed on the engine:

```
inventory   EGG   MILK   WOOL
   10000     50    160    200
   10100     42      1      1
   10500     39      1      1
   13000     36      1      1
```

So **any marginal unit of MILK sold once the market is even slightly over I0 is
worth $1**. The swap *creates exactly that condition* when the rival is also a
big milk seller.

Now price the marginal cow under V56's 78 units of prior milk supply:

```
MILK, 4 cows, after V56's 78 milk:      $156
MILK, 5 cows, after V56's 78 milk:      $195   -> extra cow yields only   +$39
WOOL, 2 sheep:                          $7,839
WOOL, 3 sheep:                          $7,950  -> extra sheep costs      -$111
purchase price difference (cow cheaper):          +$100
                                       net:         ~ -$72 per swap
```

The cow is $100 cheaper, but it lands in a market where its marginal output is
floored to near-worthless, while the sheep it displaces sits in a *different*
product (WOOL) that V56's 6 cows do **not** flood. **We are trading a
non-glutted product into a glutted one.** That is the whole reason the swap wins
against V92 (whose 4 cows barely move the milk market) and loses against V56
(whose 6 cows already floored it).

**One-sentence causal statement:** V56's herd is large enough to push MILK past
I0 and onto the $1 floor, so the cow swap's marginal revenue collapses to almost
nothing while the displaced WOOL — untouched by V56's cows — stays valuable,
making the same substitution strictly value-destroying against V56 specifically.

## 4. Why the V101 model did not catch this

The V101 estimator is *not wrong*; it is **incomplete on one axis**. It computes
the marginal accepted MILK-vs-WOOL value from the market state **at the moment
of the day-6 decision** (market inventory, shop sinks, remaining days). It
therefore answers "is milk scarce right now?" — and at day 6, in these seeds,
milk is not yet flooded, so the model says fire.

It has **no term for the opponent's future supply**. By the time V56's 6 cows have
dumped their milk (the glut that matters is days 14–30), the cow we added is
worth $1/unit. The model is a good *one-step-ahead* estimate and a poor
*equilibrium* estimate. V56 is the first opponent that made that distinction
bite. This also explains the heavy left tail seen against V92 (−$2,437 on seed
170010) and why removing the wool-sink seeds does not rescue V56 — the problem
is the *opponent's* milk, not the town's shop sinks.

## 5. Proposed V104 intervention: convert the sheep to a GOOSE, not a COW — **INFEASIBLE, CLOSED**

> **VERDICT (Phase 0 feasibility check, spent seed 160001, no fresh games run):
> INFEASIBLE. Stopped before any match, as instructed.**
>
> **Concrete obstruction.** A GOOSE requires a **COOP** tile
> (`ANIMALS["GOOSE"]["structure"] == "COOP"`), and the engine's animal `PLACE`
> branch requires the unit to be **standing on** a matching unoccupied structure
> tile. The incumbent's day-6 route places the sheep on a **PASTURE** at
> `(5, 4)`, and the placing actor (actor 5) visits only `(5, 4)`, `(8, 4)`,
> `(9, 4)` on day 6 — **never a COOP**.
>
> The reason is temporal, not incidental: **no COOP exists on the board before
> day 11** on any spent seed checked (160001, 160003–160010, 160013–160015,
> 160017–160019 all build their first COOP on **day 11**; seed 160001's only COOP
> is at `(3, 7)`, first present **day 28**). The day-6 route is five days too
> early. A goose therefore has nowhere to go, and the "no extra unplaced animals"
> invariant that V99/V101 were built around would be violated on every seed.
>
> Reaching a COOP would require building one before day 6 or rerouting a worker,
> which is precisely the "extra unplaced cows / borrowed worker route" failure
> mode the V93–V100 postmortem forbids. **The proposal is closed as written.**
>
> Evidence: `experiments/v104_commandcode/feasibility_check.py` and
> `feasibility_160001.md`.

**One-line change, same route, same latch, same "no extra worker-time" property
as V101/V99:** on the day-6 `BUY_ANIMAL SHEEP 2` order, when the V101-style
marginal estimate fires, split `SHEEP 1` + **`GOOSE 1`** instead of
`SHEEP 1` + `COW 1`; the goose is carried on the tape's existing sheep pickup and
placed via the existing sheep `PLACE` — **into a COOP tile**, not a pasture.

**Why this is the right one intervention (causal mechanism):**

1. **It sidesteps the glut instead of feeding it.** GOOSE produces EGG, and EGG's
   above-I0 shape is `log` — it does **not** floor to $1. A 78-EGG season sale
   into a market at I0 still returns ~$3,447 (avg ~$44/unit), and even *behind a
   7-goose rival* it returns ~$2,981 (a −$466 penalty, not a collapse). The
   marginal unit of EGG keeps real value under supply where a marginal unit of
   MILK is worth $1. This is the single most important property: it is robust to
   exactly the opponent behaviour (big milk herd) that kills the cow swap.

2. **It produces more, and earlier, for less.** GOOSE 78 units from day 10, every
   day, at $300; the cow gives 39 units from day 14, every 2 days, at $400. The
   goose roughly doubles units, starts 4 days sooner, and is $100 cheaper than the
   cow and $200 cheaper than the sheep it replaces. On base prices alone
   (EGG $50) that is a positive expected value the cow cannot match once milk is
   saturated.

3. **It does not compete for the tiles V56 is defending.** GOOSE uses a COOP.
   V56's 10 pastures and 7 coops are the thing we are avoiding; a goose does not
   take a pasture, so it neither displaces our own cows nor adds to the pasture
   contention that makes the cow fragile.

**Caveat, stated honestly:** EGG's scarcity shape below I0 is `hinge`, so when
EGG is scarce its price spikes (I saw $31982 at inv 5000 in a probe). That upside
is not something to bank on, and the *downside* case — a rival that also floods
EGG — is real but bounded (−$466 in the measured 7-goose case, versus the
cow-swap's catastrophic milk floor). I have **not** proven V104 wins; I have shown
(a) the cow swap is specifically wrong against milk-heavy opponents, and (b) the
goose structurally avoids that failure mode by choosing a product whose glut curve
does not floor, and by not competing for pasture tiles. Whether the realized
margin against V56 is positive must be decided by the test plan in §6, not by
this argument.

### Minimal-disruption design constraints (carried from V93–V100 failures)
- Same day-6 latch, same three-turn chain (buy → pickup → place). No new moves,
  no borrowed worker time, no extra unplaced animal.
- Do not change the wool SELL schedule or hold any product back.
- **New:** the placement must target a **COOP** tile the tape already stands on or
  reaches on the existing route; if no COOP is on the route, the rule does not
  fire. (This is the one genuinely new placement constraint; it is the price of
  GOOSE's COOP housing and must be verified in the test plan.)

## 6. Small spent-seed test plan (no new holdout)

Goal: decide whether GOOSE beats COW **specifically against V56**, without
touching any protected range and without a large tournament. The other worker is
running a holdout now, so this is deliberately sized for ≤2 workers.

**Phase 0 — feasibility micro-check (no matches, 1 seed).** On ONE spent seed
(e.g. 160001, already used in my dev panel), instrument the day-6 route and
confirm a COOP tile is actually available on the existing sheep-placement route.
If no COOP is on-route, the GOOSE variant is not viable as stated and the
proposal must be revised before any match is run. This is a read of existing
replays, not a new game.

**Phase 1 — paired spent-seed screen (the decision).** Build the V104 GOOSE
variant and run it **against V92 and V56 only**, both seats, on **12 already-spent
seeds** that my dev panel used and that are not in any protected range
(e.g. 160001–160012). The comparison that matters is **GOOSE vs COW on the same
seeds vs the same V56**:
- If GOOSE's mean paired margin vs V56 is materially better than COW's −$7,540-per-21-seeds profile (i.e. clearly better than ~ −$300/seed and ideally positive), the mechanism is confirmed and V104 is worth promoting to a fresh gate.
- If GOOSE is not clearly better, abandon the animal-substitution direction; the engine evidence says the whole family of swaps is structurally fragile against milk-heavy opponents.

**Phase 2 (only if Phase 1 is positive) — confirm no harm vs V92/V50.** Run the
GOOSE variant vs V92 and V50 on the same 12 spent seeds and require it to be
**non-inferior** to the V101 cow swap (which scored +$1,654 / +$2,244 on firing
seeds). If GOOSE helps V56 but hurts V92/V50, it is not a safe substitution and
stays unsubmitted.

**Explicitly not done and not to be inferred:** this plan uses only spent seeds.
It cannot produce a "ready to submit" claim. Any V104 promotion must go through
its **own** precommitted fresh-holdout gate, written and hash-frozen before a
single fresh seed is run — exactly as V101 did — and must include a V56 control,
since V56 is where the cow swap is revealed. I am not claiming top-ten or
submission readiness here.

## 7. Artifacts this analysis rests on (all already on disk)
- `experiments/v101_commandcode/REPORT.md`, `GATE.md`, `HOLDOUT_RESULT.md`
- `experiments/v101_commandcode/runs/holdout_vs_{v92,v50,v56}/` (per-game records, spent)
- `experiments/v101_adaptive_swap/runs/v92_vs_v56_spent15/` (V92-vs-V56, spent)
- `experiments/v101_commandcode/model_deltas_holdout.json` (model deltas)
- Pinned engine `kaggriculture.py` (market shapes, animal constants) for all
  arithmetic in §3 and §5.

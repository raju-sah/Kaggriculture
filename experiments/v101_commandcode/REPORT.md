# V101 independent result: observable adaptive animal decision

Worker: visible Herdr CommandCode worker (Space Bunny Alpha). Isolated under
`experiments/v101_commandcode/`. **No Kaggle submission was made; the four
submission slots are untouched.** No API key was read, printed, or accessed.

## What was built

A standalone exact-loader candidate that is the frozen V92 policy byte-for-byte,
plus one day-6 intervention. Candidate SHA-256
`8c572b9027ca4f5a0d656d1b1dd6fb74b4b121bd67c69b97aef16d66e21052e7`; the embedded
V92 source hash is the frozen `0d5d356baa…b806`. Engine kaggle-environments
1.32.7, `kaggriculture.py` sha256 `bc8a54879ef0…653e`, 720 steps, 24 turns/day.

**The intervention.** On the incumbent's own day-6 `BUY_ANIMAL SHEEP 2` order, if
an exact-arithmetic model says the substitution pays, convert one unit to
`SHEEP 1` + `COW 1`, carry the new cow on the sheep pickup the tape already
performs, and convert that carrier's sheep `PLACE` into a cow `PLACE` on the same
tile. Measured on the real tape: buy d6h6, pickup d6h8, place d6h12 — V99's route,
unchanged, so no worker-time is borrowed.

**The estimate is observable and engine-exact.** It uses only market inventory,
market prices, the town shop list, our own shed balances, our own animal layout,
the day number and the pinned season length. It never looks at a seed id. It
reimplements the engine's own `market_price` in-file, and the accepted cash is
computed by walking the per-unit price path `p(q), p(q+1), …` the way
`_process_market` settles SELL, not by multiplying a headline price by a count.
The in-file price function was cross-checked against the engine on 40,000
inventory/item pairs (0 mismatches) and the whole estimate against an
engine-backed reference on 2,000 randomized states (0 mismatches); both checks
are in `test_candidate.py`.

**The trigger rate is much higher than V99's Pizza-only rule.** On the 60
development seeds the model fires on **48 (80%)**, versus 2/24 (8%) for the V99
gate on its own fresh holdout. The reason is structural: the delta depends on
the *relative* draw-off the town applies to MILK versus WOOL, not on one shop
name, so it fires whenever milk is favoured and correctly stays silent when a
YARN_STORE is present.

## A two-bug detour worth recording

The first build was a no-op and two verifiers caught it, correctly.

1. I collapsed V99's three separate day-6 hooks into a single `hour == 6` guard.
   That made the h8 pickup and h12 place unreachable and required a sheep
   `PLACE` on the buy turn, which never happens. Fixed as a latched all-chain
   gate: decide once at d6h6, then rewrite on later day-6 turns.
2. My first fix still gated the place on `shed COW > 0`, which vetoes the place
   on the very turn after the pickup emptied the shed. Fixed so the pickup is
   guarded by the shed and the place by the carrier's own inventory, independently.

Both were caught before any panel was run, and both are now covered by
`test_candidate.py` (sections 6–8) and by a real exact-loader micro replay
(`micro_replay.py`) that asserts all three changed steps.

## Development panel: seeds 160001–160060, both seats, exact loader

These are this worker's development seeds and are spent. The other agent's
150001–150080 range and V99's spent holdouts (137501–137524, 93000–93011) were
not touched. Two workers were used; the machine was otherwise free.

| Opponent | Games | W–L–D | Score rate | Mean margin | 95% CI (paired, seed) | Errors/timeouts |
|---|---:|---:|---:|---:|---:|---:|
| V92 (primary) | 120 | 66–30–24 | 0.650 | +$1,392 | [+718, +2,041] | 0 |
| V50 (control) | 120 | 100–20–0 | 0.833 | +$2,042 | [+1,394, +2,669] | 0 |

**Effective sample size.** The engine is deterministic and both seat orders
produced identical margins on all 60 seeds (`seat-swap identical: True` for both
opponents). The independent unit is therefore the **seed**, not the game: 60 seeds
per opponent, and against V92 the 48 firing seeds are decisive while the 12
non-firing seeds are exact ties. Against V92 that is 33W/15L on the decisive
seeds (0.688). I am not claiming 120 independent games.

**The ties are the model.** The 12 tie seeds against V92 are exactly the 12 seeds
with a non-positive model delta — an exact one-to-one correspondence, with no
seed on either side of the partition. That is a causal signature rather than a
correlation: the rule changes the game on 48 seeds and is provably a no-op on the
other 12, and the paired margin is non-zero on precisely the 48.

## Lifecycle, on the real replays

Every one of the 48 firing seeds was re-run under the exact loader and audited
(`verify_lifecycle.py`; replays in `lifecycle_replays/`):

- three-step chain complete: **48/48**, and the same three steps are **absent**
  from a frozen-V92 self-play control on all 48;
- the cow is **still a COW on a PASTURE in the final frame: 48/48**;
- it **produces 21 MILK units** on every seed, from harvest days 14 onward;
- **342 feed-days and 338 care-days** — the incumbent's daily sweep fully
  services it, confirming the zero extra worker-time claim;
- **zero cash-reconstruction mismatches** against the engine's own settlement.
  Accepted MILK cash spans $4,604–$50,462 and WOOL $5,238–$60,385 per game.

The model predicted 21 units uncared (first harvest day 14, then every 2 days, 1
unit each, 8 harvests). The realised figure is 21, i.e. the tape's care bonus did
not materialise on this route, so the estimate is neither optimistic nor
pessimistic here — it is exact.

## Known failure modes, and how each is excluded

| V93–V100 failure | How this candidate avoids it |
|---|---|
| wool deferral | we never hold wool back; the wool SELL order and every other order keep their position, and only the sheep *quantity* changes |
| extra unplaced cows | the cow is placed by rewriting the same carrier's same `PLACE` on the same tile; there is no unplaced-cow path, and 48/48 audits end with the cow alive on a pasture |
| worker-route borrowing | no move, pickup, or placement is added; only species labels on existing actions change, on V99's measured d6h6/h8/h12 route |
| broad sell holding | the market list grows by exactly one inserted `BUY_ANIMAL COW 1`; the unit test asserts the sell count is unchanged |
| day-0 sheep swap | gated on `day == 6`; the unit test asserts every other day is a strict no-op |
| a Jev profitability guess | the estimate walks the engine's own per-unit price path; it is arithmetic on the observed market, not a guess |

## Honest limits

- The development panel is development data. V99's own 8W/12D on its development
  set became 4W/44D on a fresh holdout. The gap between "positive here" and
  "positive on new maps" is exactly what killed the last several attempts, and
  nothing in this report closes it.
- Losses are heavy-tailed: −$5,797 and −$5,556 against V92 on single seeds. The
  mean is positive, but a single bad seed can erase a good one.
- 60 seeds cannot support a claim of top-ten readiness, and I make none.
- The 48/48 lifecycle result is on seeds where the rule fires, which is the
  expected population; it is not evidence about the 12 seeds where it abstains
  beyond the fact that the game is unchanged there.

## Precommitted fresh holdout (not run)

`GATE.md` was written **before** any fresh holdout seed was touched. It freezes
the candidate hash, a fresh disjoint range **170001–170024**, and a numerical
gate: score rate > 0.55 and mean margin > +$300 against V92, at least 6 distinct
triggering seeds, score rate > 0.55 and mean > +$300 against V50, score rate
> 0.45 and mean > 0 against V56, zero errors, and no single V92 regression worse
than −$2,000. The trigger-count criterion exists specifically because V99's
gate failed on it by firing on only 2 of 24 seeds.

**No holdout has been run. No submission has been made. Codex is asked to review
the gate before anyone spends those seeds.**

## Artifacts

- `candidate.py` — the standalone agent (frozen hash above).
- `build_candidate.py` — reproduces `candidate.py` from frozen V92 + the block.
- `valuation.py` — engine-backed reference model used for the cross-checks.
- `test_candidate.py` — loader, price, estimate, no-op and safety invariants.
- `micro_replay.py` — exact-loader replay asserting the three changed steps.
- `observe_seeds.py`, `probe_agent.py`, `decision_states.jsonl` — the recorded
  day-6 decision states; `analyze_states.py`, `model_deltas.json` — the model.
- `screen.py`, `runs/dev_vs_v92/`, `runs/dev_vs_v50/`, `dev_results.json` — the
  development panel.
- `verify_lifecycle.py`, `audit_panel.py`, `lifecycle_replays/`,
  `lifecycle_results.json` — replay lifecycle and settlement audit.
- `GATE.md` — the precommitted holdout gate.

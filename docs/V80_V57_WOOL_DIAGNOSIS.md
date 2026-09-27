# V80: V57-reset wool-route diagnosis on spent seed 92802

Read-only diagnosis. No agent code was edited, no simulation was run, no submission was made. The
lost seed-92802 replays were located in an existing artifact and analysed in place.

This revision corrects five material errors in the first draft. Corrections are listed in
[Corrections to the first draft](#corrections-to-the-first-draft).

## Sources and provenance

| Item | Value |
|---|---|
| Replay dir | `experiments/v58_planner_eval/model_based/spent_seed_92802/reset/replays/` |
| ab replay | `v50-seed-92802-ab-repeat-0.json` |
| ba replay | `v50-seed-92802-ba-repeat-0.json` |
| Game metadata | `experiments/v58_planner_eval/model_based/spent_seed_92802/reset/games/*.json` |
| Seed | 92802 (already spent) |
| Candidate seat 0 (ab) | `experiments/v57_broad/v57_reset_candidate.py`, sha256 `4173479fe1f80d031d570d1ea23b694dfe86e1d162317a4c9c7df0058a40208e` — re-verified by recomputing the digest |
| Opponent seat 1 (ab) | `experiments/v50_agent.py`, sha256 `e6b50128e023e3b9fafa1841e4cd520c5e581acb48e8628657585c18272eab2b` — re-verified |
| Engine | `kaggle_environments` 1.32.7, `boardSize` 10, `episodeSteps` 720, `turnsPerDay` 24, `farmHandCostMult` 1, `startingMoney` 3000 |
| ab result | 78,631 (seat 0, V57) – 112,218 (seat 1, v50); **gap −33,587** |
| ba result | 112,218 (seat 0, v50) – 78,631 (seat 1, V57); seat-swapped, identical outcome |
| Stored `replay_sha256` in game JSON | ab `e5c5fd8e74dc6c8b25ec8ed89f72d3a88a91d85d1aec4672c60d7e95a8ae8dab`, ba `d57f4d0abf68b6818e4f540f7ff5cae346e787c0a8bee34134c69b46c13b3860` |
| Recomputed on-disk file sha256 | ab `9021876d26b46ee5455b061f8a6eafe2be521b8f68526b1067ba02a115fd6a71`, ba `8de781caedd9736286ac621c678250b5f121e615cc19171acb57618c1cac3ea2` |

The recomputed on-disk digest does not match the `replay_sha256` stored in the game JSON. The stored
field is the hash of the normalized artifact; `replay_normalization` is
`{'removed_top_level_fields': ['id']}`. Both values are reported so neither is mistaken for the
other. **The stored `replay_sha256` is the field of record for provenance**; the on-disk digest was
recomputed only as a sanity check and is not claimed to be an independent provenance anchor.

Settlement was reproduced with the existing pinned-engine routine in
`experiments/v75_elite_cashflow/reconstruct.py` (`reconstruct()`), which replays each recorded action
through Kaggriculture 1.32.7 `_commit_unit` / `_process_market` and reconciles observed cash
frame-by-frame. Both seats of both files: **`max_cash_error` 0.0, `mismatches` 0** across all 720
frames. The two seat files are exact seat-swaps, so all findings below are seat-invariant.

## Cash and ledger reconciliation

Accepted transaction totals, ab seat, identical in ba:

| Cash component | V57-reset | v50 |
|---|---:|---:|
| Accepted sales | 112,963 | 138,960 |
| Product purchases | −8,446 | −6,847 |
| Seed purchases | −7,020 | −6,480 |
| Animal purchases | −6,500 | −7,900 |
| Land + hire (residual) | −15,366 | −8,515 |
| Starting cash | +3,000 | +3,000 |
| **Reconstructed total** | **78,631** | **112,218** |
| **Observed final coins** | **78,631** | **112,218** |

Both sides reconcile to the coin exactly. The land+hire line is a **residual**, computed as observed
cash delta minus explicit market transactions, so it bundles hire wages with any land cost. It is not
a pure land figure. V57-reset also hired more often late (day 24: 14 HIRE orders vs v50's 12), which
is the main reason its residual is larger; the two accepted 2,000 and 4,000 land purchases are equal
on both sides.

## Accepted sales by product

| Product | V57-reset | v50 | diff |
|---|---:|---:|---:|
| WOOL | 16,166 | 63,103 | **−46,937** |
| MILK | 4,709 | 5,311 | −602 |
| MELON | 14,436 | 14,043 | +393 |
| WHEAT | 13,936 | 12,924 | +1,012 |
| CARROT | 10,634 | 9,390 | +1,244 |
| STRAWBERRY | 21,034 | 19,773 | +1,261 |
| FERTILIZER | 15,733 | 14,416 | +1,317 |
| TOMATO | 6,589 | 0 | +6,589 |
| EGG | 9,726 | 0 | +9,726 |
| **Total sales** | **112,963** | **138,960** | **−25,997** |

**Wool accounts for 139.7% of the final coin gap** (46,937 / 33,587). Excluding wool, V57-reset is
**+20,940 in aggregate** on the remaining products, and it is the only side selling tomato and egg at
all. That aggregate is **not** uniformly positive: **MILK is −602**, the single other negative line.
The claim is aggregate non-wool strength with a milk exception, not universal dominance.

## Accepted wool volume and realized price

Earlier drafts quoted v50's wool as 379 units. **379 was ordered, not accepted.** Engine settlement
gives the accepted figures:

| Side | Ordered | Accepted | Rejected | Accepted $/unit | min | max |
|---|---:|---:|---:|---:|---:|---:|
| V57-reset | 72 | **72** | 0 | 224.5 | 192 | 238 |
| v50 | 379 | **278** | 101 | 227.0 | 194 | 238 |

The accepted per-unit ranges are **192–238 for V57-reset and 194–238 for v50**, derived from the
engine's own `_commit_unit` prices, not from a quoted-price model. The two sides realize effectively
the same unit price, so the entire wool deficit is a **volume** difference, not a pricing one. The
first draft's claim that both sides traded in a common 190–237 band described pre-order quotes, which
is not the same quantity as accepted proceeds; the range is now stated from settlement.

## The exact herd divergence

The farms are identical through day 6 hour 06 and diverge on a single simultaneous market step:

| Step | Day/hour | V57-reset buys | v50 buys |
|---|---|---|---|
| 2 | 0h02 | COW, SHEEP | COW, SHEEP |
| 66, 89 | 2h18, 3h17 | COW | COW |
| **151** | **6h07** | **GOOSE ×2** | **SHEEP ×2** |

**Correction — the farms are NOT byte-identical at step 151.** An earlier draft said so; that was
wrong. A field-by-field comparison gives the precise picture:

| Farm field | V57-reset | v50 | Match |
|---|---|---|---|
| `unlocked_quadrants` | `['NW','NE']` | `['NW','NE']` | **same** |
| building counts | `PLANT: 19, PASTURE: 6` | `PLANT: 19, PASTURE: 6` | **same** |
| pasture occupants | `(4,2)COW (3,3)SHEEP (4,3)COW (2,4)COW (3,4)SHEEP (4,4)COW` | identical list | **same** |
| `money` | 1,724 | 1,614 | differ (−110) |
| `farmer` | `[5,4]` | `[4,4]` | differ |
| `hands` | 7 entries | 8 entries | differ |
| `hires_today` | 7 | 8 | differ |
| `tiles` (deep compare) | — | — | **differ** |
| `private.shed` | `FERTILIZER 1, GOOSE 2, WHEAT 13` | `FERTILIZER 1, SHEEP 2, WHEAT 3` | differ |
| `town`, `market.prices`, `market.inventory` | shared | shared | same by construction |

So what matched is exactly: **the board's structure and livestock layout, and the unlocked
quadrants**. Cash, worker positions, hand count, hires, the deep `tiles` structure, and the shed all
differed. The shed divergence is the *consequence* of this very order, not a prior difference — V57's
shed shows `GOOSE: 2` and v50's shows `SHEEP: 2` at step 151 because step 150's actions settled into
step 151's observation. The defensible claim is narrower: **the two farms held the same six occupied
pastures, the same 4 cows and 2 sheep, and the same two quadrants, and both had cash well above the
1,000 cost of two sheep, when they chose different animals on the same step.**

| Day | V57-reset herd | v50 herd |
|---|---|---|
| 6 | COW 4, GOOSE 2, SHEEP 2 | COW 4, SHEEP 4 |
| 9 | COW 6, GOOSE 2, SHEEP 4 | COW 6, SHEEP 6 |
| 12 | COW 6, GOOSE 7, SHEEP 4 | COW 6, SHEEP 11 |
| 12–29 (frozen) | COW 6, GOOSE 7, SHEEP 4 | COW 6, SHEEP 11 |

Lifetime animal spend: V57-reset 6 COW / 5 GOOSE / 4 SHEEP = $6,500; v50 5 COW / 11 SHEEP = $7,900.
V57-reset spends **$1,400 less** on animals and loses by $33,587, because it buys the animal that
does not produce the high-value product.

## Is the shop / buyer regime responsible? No.

- At the divergence the town already shows `unlocked_shops: ['PET_CAFE', 'YARN_STORE']`. The yarn
  shop is open **before** the divergence, so v50's sheep decision was not a reaction to anything
  V57-reset could not see.
- Wool price is shared and identical. It was $190 at step 151 and stayed in the high band all season.
- Market inventory is shared: `WHEAT` 9,985, `FERTILIZER` 10,049 at the divergence, same for both.
- V57-reset sold wool on **14 separate days** across the season. It is not blocked or price-shy; it
  has 2 sheep against v50's 11, so there is little to sell.

## Relationship to the earlier V59 mix gate

This is the material distinction, and it changes the conclusion.

`docs/V59_MIX_GATE.md` already tested an early-Yarn/high-Wool goose-to-sheep substitution. Its gate is
`day <= 11 and 'YARN_STORE' in shops and prices['WOOL'] >= 180`
(`experiments/v59_route_rules/mix_gate/candidate_isolated.py:188-192`). On seed 92802 at step 151
**all three conditions are true**: day 6, YARN_STORE present, WOOL $190.

**The gate was active and still could not act.** Its conversion is further guarded by
`sheep_count >= 4` (line 234), and V57-reset had only **2 sheep** at step 151. The gate is explicitly
designed to leave the first four sheep alone and only convert an *extra* purchase past that floor.
Seed 92802's divergence happens at the **second** sheep purchase, which is by construction outside
the gate's scope.

**(Revised in Part 2: the `sheep_count` floor is not the only blocker.)** The same line 234 also
requires a non-empty `vacant` list of unoccupied pastures, and at step 151 all 6 pastures are
occupied. Two independent conditions block the gate there, so removing the sheep floor alone would
still yield zero changes. See [Part 2](#part-2-feasibility-check-of-the-v59-intervention-on-seed-92802).

So the correct framing is:

- **V59 is a zero-effect implementation on a different trigger point.** Its fresh 95611 screen found
  the gate active for 60 frames with **zero changed actions**, and the paired coin margin delta was
  exactly $0. Candidate and frozen control both scored 72,608 vs 100,543 in both seat orders. A rule
  that changes nothing cannot be evidence for or against the wool hypothesis; it is untested
  behaviour, not a negative result.
- **92802 step 151 is a genuine earlier substitution opportunity** that V59's `sheep_count >= 4`
  floor structurally excludes.

This is a gap in prior coverage, not a contradiction of it. It also means the earlier "V79 falsified
the unconditional version" claim needs restating, below.

## Correction to the V79 characterization

The first draft described `v79_sheep4` as "a blanket sheep increase" that "went 0–2" and therefore
falsified the unconditional fix. **That is wrong on both counts.**
`experiments/v75_joint/agent_v79_sheep4.py:18` sets
`desired_animal_targets = {"COW": 2, "SHEEP": 4, "GOOSE": 2}`, with the docstring describing a
"Two-cow/four-sheep/two-goose champion". V79 is a **different agent family**, not the V57 reset
lineage, and it *reduced* the sheep target relative to the 8-sheep route it derived from. It is not
evidence about V57-reset's animal route and must not be cited as a falsification of it.

## Secondary finding: rejected fourth land purchase

V57-reset issues `BUY_LAND` at steps 151, 266, and 435 (day 18h03); v50 issues only the first two.
`LAND_PRICES = [1000, 2000, 4000]` and `_do_buy_land` returns early when
`n_unlocked_extra >= len(LAND_ORDER)` (engine lines 712-716), so the step-435 order at 3 extra
quadrants is a **no-op that can never succeed**. It is a dead order in the stream, and it costs no
cash. The day-18 residual difference is hire wages, not this order. Recorded as an observation only;
**not offered as a cause of the loss.**

## Other 92802 opponents: no saved replays

Searched all `experiments/**/games.jsonl` for games on seed 92802 containing the V57-reset or V57-orig
sha. **No other 92802 game involving the V57 lineage has a saved replay.** The only V57-lineage 92802
replays on disk are the two v50 files in this directory. The remaining 92802 panel losses
(v52, v53, v55) have no replay and are individually uncharacterized. The
`experiments/v58_planner_eval/model_based/spent_seed_92802/allocator/` replays use a different
candidate (sha `0ee6071166a6685f6ba61f21bce264b0fe8c5b38bdc16f66e1ed5e77d989eceb`), not the frozen
reset, and are not evidence about the V57-reset route.

## Verdict: supported on this seed, and precisely scoped

The wool-route hypothesis is **supported on seed 92802** and is not falsified. Three spent seeds show
the same signature, but only 92802 is settlement-exact:

| Seed | Wool diff | Non-wool diff | Coin gap | Wool as % of gap | Settlement-exact |
|---|---:|---:|---:|---:|---|
| 92802 (this report) | −46,937 | +20,940 | −33,587 | 139.7% | yes (0.0 error) |
| 95300 (prior) | −56,889 | +9,538 | −24,344 | 233.7% | no — `market_price` model |
| 95611 (prior) | −48,874 | +16,008 | −27,935 | 174.9% | no — `market_price` model |

The 95300 and 95611 figures used ordered-not-accepted wool volumes and a quoted-price model. They
should be treated as indicative, not as the 95300/95611 rows in the first draft implied. Only 92802
carries a 0.0 settlement audit.

## Limits

- Seed 92802 is spent and is **not** part of the frozen 540-game common panel in
  `docs/V57_BROAD_VALIDATION.md`. It is a diagnostic artifact, not validation evidence.
- The 14 reset-panel losses on seed 92804 have no saved replay. Whether wool also explains 92804 is
  **unknown**.
- Both opponents here are local agents, not a leaderboard sample. A wool deficit against `v50` may be
  matchup-specific.
- The ledger proves what was sold and bought. It does **not** prove that substituting a sheep for a
  goose at step 151 would have closed the gap. No counterfactual was simulated, and the two farms
  share a market, so a substitution at step 151 would also have changed v50's own quoted prices. That
  coupling is unmodelled here.
- The aggregate non-wool lead includes TOMATO +6,589 and EGG +9,726 from animals V57-reset has and
  v50 does not. Those are not independent of the herd composition decision.

## One falsifiable next action

The V59 result leaves a specific untested question, and it is a diagnostic, not a code change.

**Run the existing V59 isolated candidate against the frozen reset on spent seed 92802, both seat
orders, and diff the accepted-sale ledger.** This is a counterfactual on an already-spent seed and
touches no fresh seed. The V59 gate is known to be *active* at step 151; the question is only whether
its `sheep_count >= 4` floor blocks it there as the state suggests, and if the floor is lowered,
whether the resulting wool revenue delta is large enough to matter.

Stated before running, so the test can fail:

1. If the V59 gate changes **zero** actions on 92802 in both seat orders, that confirms the
   `sheep_count >= 4` floor is the binding constraint and the earlier "V59 falsified the idea"
   reading is dead. The correct next step is then a **new** rule that admits the second sheep
   purchase, not a retry of V59.
2. If the gate **does** act and wool revenue for the candidate seat rises by **less than 15,000**, the
   substitution is too small to close a 33,587 gap and the wool hypothesis is **not** sufficient on
   its own, regardless of being necessary.
3. If wool rises by **more than 20,000** with no loss exceeding 3,000 on any other product line, the
   hypothesis is confirmed as practically actionable.

Falsifiable in every branch. Outcome 1 kills the reuse of V59; outcomes 2 and 3 respectively cap and
support the change. No agent code is modified by this step, and no fresh seed is consumed.

## Corrections to the first draft

1. **Wool price claim was false.** The draft asserted both sides realized 190–237. v50's true accepted
   average is 227.0 (63,103 / **278** accepted), not 166.5; 379 was ordered, 101 units were rejected.
   Replaced with engine-settlement ranges: V57-reset 192–238, v50 194–238.
2. **"Every other product line positive" was false.** MILK is −602. Replaced with the accurate
   aggregate: non-wool +20,940 with a milk exception.
3. **V79 was mischaracterized.** It is a different agent family whose `desired_animal_targets` is
   `{"COW":2,"SHEEP":4,"GOOSE":2}` — 4 sheep, reduced from the 8-sheep route it derives from. It is
   not a blanket sheep increase, not a V57-reset variant, and does not falsify this hypothesis.
4. **V59 mix gate prior work was not distinguished.** `docs/V59_MIX_GATE.md` tested goose-to-sheep
   conversion but is gated behind `sheep_count >= 4`; on 92802 step 151 the gate was active yet
   blocked by exactly that floor, since the divergence is at the second sheep. V59's zero-change
   95611 screen is untested behaviour, not a negative result.
5. **Provenance and coverage verified.** Candidate and opponent shas recomputed and matching; the
   `replay_sha256` vs on-disk digest discrepancy is explained and attributed; land language corrected
   to call the line a residual bundling hire wages, and the rejected 4th `BUY_LAND` is a no-op that
   costs no cash; and a full search confirms **no other 92802 V57-lineage replays exist**.

# Part 2: Feasibility check of the V59 intervention on seed 92802

Read-only. No agent code edited, no game run, no seed spent, nothing submitted.

## Correction 6: step-151 pastures are occupied, and `vacant` also blocks

The corrected Part 1 notes that V59's gate was active at step 151 but its `sheep_count >= 4` floor
blocked conversion. There is a **second, independent blocker** that the first draft missed, and it is
the more fundamental of the two.

`_v59_iso_counts` (`candidate_isolated.py:204-213`) returns a `vacant` list containing only
`kind == 'PASTURE'` tiles with **no animal key at all**, and the conversion requires `vacant` to be
truthy (line 234). At step 151 V57-reset has **6 pastures, 6 occupied, 0 vacant**. The trigger state
is therefore false on two independent counts:

| V59 condition at step 151 | Value | Passes |
|---|---|---|
| `day <= 11` | 6 | yes |
| `'YARN_STORE' in shops` | present | yes |
| `prices['WOOL'] >= 180` | 190 | yes |
| `sheep_count >= 4` | 2 | **no** |
| `vacant` non-empty | 0 vacant pastures | **no** |

This is a correction to the Part 1 framing as well. Lowering the `sheep_count` floor alone **cannot
make V59 act at step 151** — the pasture precondition independently blocks it. V59 would still make
zero changes at the divergence point even with the floor removed.

## Action-fidelity check of the existing V59 candidate

The V59 candidate **was** run against the frozen reset across the saved 92802 observation stream —
offline, frame by frame, with no environment and no game. Each frame's saved observation was fed to
both agents' real submission entrypoints (`_kaggle_submission_entrypoint`), candidate and frozen
module state starting clean at episode step 0. **1,440 frames evaluated (720 steps × 2 seats).**

| Metric | Result |
|---|---|
| Exceptions | **0** |
| Frames with changed **market** orders | **2** |
| Frames with changed **worker/farmer** actions | **0** |
| First market change | **step 217, seat 0, day 9 hour 1** |

The first and only category of change:

```
step 217, seat 0 (day 9, hour 1)
  frozen   : [['BUY_ANIMAL','GOOSE',1], ['BUY_PRODUCT','FERTILIZER',1]]
  candidate: [['BUY_ANIMAL','SHEEP',1], ['BUY_PRODUCT','FERTILIZER',1]]
```

The second change is at step 226, seat 0, the same substitution. Both occur at **day 9**, after the
second land purchase created 5 free pastures, not at the day-6 divergence.

This is the branch-1 outcome predicted in the first draft, and it is now **measured rather than
predicted**: on 92802 the V59 candidate changes exactly 2 market frames and 0 worker frames, both at
day 9. It does not touch step 151, for the two independent reasons above. The V59 rule is therefore
confirmed to be a day-9 "extra sheep" tweak, not a fix for the day-6 divergence, and reusing it
unchanged cannot address the seed-92802 loss.

## Minimum intervention to convert 2 day-6 geese into producing sheep

Engine rules, from `.venv/lib/python3.12/site-packages/kaggle_environments/envs/kaggriculture/
kaggriculture.py` at version 1.32.7:

| Rule | Citation | Consequence |
|---|---|---|
| `PLACE` needs the unit standing on an unoccupied tile of the animal's structure | lines 377-392 | sheep need an **empty PASTURE**; goose needs an empty **COOP** |
| `BUILD_PASTURE` costs one worker turn, no coins, requires `tile is None` | lines 499-502 | pasture is a **turn cost, not a cash cost** |
| `PICKUP`/`DROP` require standing on a shed-adjacent tile | lines 343-374, `_shed_access_tiles` = `[(4,4),(5,4),(4,5),(5,5)]` | animals must reach the shed and a pasture |
| `FEED` consumes 1 WHEAT per animal per day | lines 505-512 | 2 more animals = **+2 WHEAT/day** ongoing |
| `CARE` is free but must occur on a fed production day for the bonus | lines 524-529, 829-830 | care route must be preserved |
| Animal escapes after `consecutive_unfed >= 2`; the structure remains | lines 817-820 | **feed failure destroys the animal, not the pasture** |
| `SHEEP`: cost 500, PASTURE, first yield day 6, interval 3, max held 6 | `ANIMALS` | placed day 6 → first wool ≈ **day 12** |
| `GOOSE`: cost 300, COOP, first yield day 4, interval 1 | `ANIMALS` | placed day 6 → first egg ≈ **day 10** |

The cash side is not the obstacle. At step 151 V57-reset holds 1,724. Two sheep cost 1,000 versus
600 for two geese — a **$400 difference**, comfortably affordable. v50 made exactly this purchase at
the same step with 1,614.

**The obstacle is worker turns and pasture supply, not money.** The observed minimum sequence for
replacing the two day-6 geese with two sheep:

1. `step 151` — change one market order: `['BUY_ANIMAL','GOOSE',2]` → `['BUY_ANIMAL','SHEEP',2]`.
   Same step, same cost class, affordable. *(market-only change)*
2. `step 151-153` — at the shed-adjacent tile, `PICKUP` the two sheep instead of the two geese.
   The farmer is already at `[5,4]`, which is shed-adjacent, so no repositioning is needed.
   *(worker change, same turns the goose pickup already occupies)*
3. **A new `BUILD_PASTURE` on an empty owned tile, before either `PLACE`.** At step 151 there are
   **0 empty pastures**, so this is genuinely new infrastructure that the frozen route does not
   perform here. In the observed timeline the frozen route builds its first new pasture at step 154
   and places the first goose at step 156 into a COOP built the same day.
4. `PLACE` each sheep on a freshly built pasture once built. Same turn cost as the goose `PLACE`s.
5. **Feed and care**: the two new animals need `FEED` (1 WHEAT each, per day) and `CARE` every day
   they are alive, and a 2-day feed miss kills them outright while leaving the pasture behind. The
   frozen route's hand roster already services 6 cows + 2 sheep + geese; adding 2 more animals needs
   2 more feed deliveries and care touches per day.

**This is not one isolated change.** It is at minimum a market-order edit **plus** a new
`BUILD_PASTURE` trigger **plus** a placement-route edit **plus** a persistent daily feed/care
commitment for two additional animals. The feed/care obligation is the hard part: it is an ongoing
season-long cost, not a one-time edit, and it interacts with the same hand budget that V75 documented
as already saturated (V57-reset ran 93.9% non-PASS hand actions in the 95611 game, so there is no
spare worker capacity to absorb 2 more animals without displacing existing work).

**Verdict: no feasible isolated one-change intervention exists.** The single-change hypothesis —
"flip one order so the two day-6 animals are sheep" — is false at step 151 for three independently
sufficient reasons, any one of which is decisive:

1. **No empty pasture exists** at step 151, and `PLACE` requires one. A market-order edit alone
   produces two sheep that cannot be placed; they would sit in the shed doing nothing.
2. **Pasture construction costs worker turns** the frozen route does not spend at that point, so the
   crop and care routes must be displaced to make room — which is a second and third change, not one.
3. **Feed and care are recurring**: 2 extra WHEAT/day plus daily care, against a hand roster already
   near saturation, with a 2-day-unfed escape that permanently deletes the animals.

The V59 candidate is the correct shape of intervention — it substitutes the order *and* re-routes
placement — but by its own design it fires at day 9 when a vacant pasture already exists, and it caps
at the sixth sheep. Adapting it to day 6 requires solving pasture supply and the recurring feed/care
commitment, which is a new agent family, not a parameter change.

## Revised next action

The Part 1 "run V59 on 92802" action is now **already executed offline** above, and its result is
branch 1: 2 market frames changed, both at day 9, none at the divergence. It should be closed rather
than repeated, and no new game is warranted for it.

The revised diagnostic, still read-only and still on spent seeds, is to ask whether the day-6
divergence is reachable at all under the frozen route's own resource limits. Concretely: from the
saved 92802 stream, count the worker turns the frozen route spends on `BUILD_PASTURE` and on
feed/care between day 6 and day 9, and compare against the same count for v50, which reached 11 sheep
without a 7th animal. **If v50 fed 11 sheep on the same hand budget that V57-reset used for 4 cows,
2 sheep and 7 geese, then the feed/care argument above is weak and the binding constraint is pasture
construction order, not labour** — which would make a narrow, single-purpose pasture-priority change
plausible. If the turn budgets are comparable and v50 simply built pastures earlier, then the
day-6 purchase is not the binding decision at all and the divergence is a downstream consequence of
build ordering. That distinction decides whether any one-change fix exists, and it can be settled from
the saved replay without running anything.

# Part 3: Days 5-12 resource diagnostic — the "no slack" verdict is refuted

Read-only, saved seed-92802 replays only. No game run, no seed spent, no code edited, nothing
submitted. All rows below are **observed recorded actions** unless explicitly marked hypothetical.

## Observed days 5-12, both agents, ab seat (seat 0 = V57-reset, seat 1 = v50)

### Infrastructure

| Day | V57 BUILD_PASTURE | V57 BUILD_COOP | V57 vac/tot pasture | V57 vac/tot coop | v50 BUILD_PASTURE | v50 BUILD_COOP | v50 vac/tot pasture | v50 vac/tot coop |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 5 | 0 | 0 | 0/6 | 0/0 | 0 | 0 | 0/6 | 0/0 |
| 6 | **5** | **2** | 0/6 | 0/0 | **7** | **0** | 0/6 | 0/0 |
| 7 | 0 | 0 | 5/11 | 0/2 | 0 | 0 | 5/13 | 0/0 |
| 8 | 0 | 0 | 3/11 | 0/2 | 0 | 0 | 3/13 | 0/0 |
| 9 | 0 | 1 | 1/11 | 0/2 | 0 | 0 | 1/13 | 0/0 |
| 10 | 0 | 5 | 0/10 | 0/3 | 4 | 0 | 0/13 | 0/0 |
| 11 | 0 | 0 | 0/10 | 2/8 | 0 | 1 | 1/17 | 1/1 |
| 12 | 0 | 0 | 0/10 | 1/8 | 0 | 0 | 0/17 | 1/1 |

### Labour, feed and herd

| Day | V57 slots/PASS/non-PASS | V57 FEED | V57 CARE | V57 WHEAT bought | V57 herd | v50 slots/PASS/non-PASS | v50 FEED | v50 CARE | v50 WHEAT bought | v50 herd |
|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|
| 5 | 91/16/75 | 6 | 6 | 0 | 4C2S | 91/17/74 | 6 | 7 | 0 | 4C2S |
| 6 | 158/5/153 | 8 | 8 | 10 | 4C2S | 177/33/144 | 7 | 8 | 0 | 4C2S |
| 7 | 160/8/152 | 7 | 11 | 0 | 4C2G2S | 183/34/149 | 9 | 10 | 1 | 4C4S |
| 8 | 183/23/160 | 10 | 13 | 21 | 6C2G2S | 200/28/172 | 11 | 11 | 16 | 6C4S |
| 9 | 184/5/179 | 13 | 12 | 18 | 6C2G4S | 206/32/174 | 13 | 14 | 9 | 6C6S |
| 10 | 269/14/255 | 16 | 16 | 27 | 6C3G4S | 250/23/227 | 16 | 16 | 7 | 6C7S |
| 11 | 227/11/216 | 13 | 18 | 21 | 6C6G4S | 247/17/230 | 15 | 17 | 20 | 6C10S |
| 12 | 208/7/201 | 17 | 17 | 0 | 6C7G4S | 209/23/186 | 17 | 17 | 10 | 6C11S |

C = cow, S = sheep, G = goose. Cash at day 12 hour 0: V57 $14,541, v50 $13,376.

**Escapes:** zero tiles reached `consecutive_unfed >= 2` for either agent on days 5-13. No animal was
lost to a missed feed in this window.

## The earliest feasible window: day 6, hours 07-13 — and v50 already used it

This is the key result, and it **refutes** the Part 2 "no feasible isolated one-change intervention"
verdict. v50 faced the *identical* constraint at the *identical* step — 0 vacant pastures, 6 occupied,
cash 1,614 — and converted it into two producing sheep **without displacing any crop work**.

Observed v50 sequence, steps 151-157:

| Step | Day/hour | v50 action | Vacant pasture |
|---:|---|---|---|
| 151 | 6h07 | `BUY_ANIMAL SHEEP 2` (with `SELL WOOL 12`, `BUY_LAND`) | 0/6 |
| 153 | 6h09 | two hands `PICKUP SHEEP` at the shed | 0/6 |
| 155 | 6h11 | `BUILD_PASTURE` | **1/7** |
| 156 | 6h12 | `BUILD_PASTURE` + `PLACE SHEEP` (same turn) | 2/9 |
| 157 | 6h13 | `PLACE SHEEP` | 2/10 |

By **step 157, six hours after the purchase, both sheep are placed and alive.** The mechanism is that
`PICKUP` and `BUILD_PASTURE` do not compete: the purchased animals sit in the shed, and
`BUILD_PASTURE` is a free worker turn on an empty owned tile (engine lines 499-502, no coin cost).
Placement simply waits for a pasture to exist.

## It costs nothing: the crop route was not displaced

Day 6 full action tallies, both agents:

| Agent | PLANT | WATER | HARVEST | BUILD_PASTURE | BUILD_COOP | FEED | CARE | PASS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| V57-reset | 13 | 27 | 4 | 5 | 2 | 8 | 8 | 14 |
| v50 | 13 | 29 | 5 | **7** | **0** | 7 | 8 | 36 |

v50 ran **more** pasture builds (7 vs 5), **zero** coop builds, and **identical or better** crop work
(13 PLANT both, 29 WATER vs 27, 5 HARVEST vs 4). Board state is identical at every day boundary:
19/29/37/37 plant tiles at steps 144/168/192/216, and `ready_to_harvest` 15/17/21/17 for both.

**The V57 day-6 build spend was 5 pastures + 2 coops. v50's was 7 pastures + 0 coops.** The two coop
builds are the entire structural difference, and they are exactly what funded the goose route that
produced the wool deficit.

## Feed headroom exists

V57-reset ended day 6 holding **18 WHEAT** in the shed versus v50's **8**, and bought 21 more WHEAT on
day 8 while v50 bought 16. V57-reset was the *better* funded feeder on day 6 and spent its advantage
on geese. No starvation constraint applies to adding two sheep; feed was never the binding resource.

## Decision: the route is feasible; the single change is an infrastructure-priority change

The Part 2 verdict rested on two claims that this diagnostic refutes:

1. *"No empty pasture exists, so a market-order edit alone cannot place the sheep."* True but
   **irrelevant**: the animals can wait in the shed while `BUILD_PASTURE` runs, exactly as v50's did.
   v50 held 2 sheep in the shed from step 153 to step 156.
2. *"Feed and care are recurring against a saturated hand budget."* v50 carried 4 more animals than
   V57-reset through days 9-12 (10-11 sheep vs 4 sheep + 7 geese) at comparable non-PASS counts
   (days 9-12: v50 174/227/230/186 vs V57 179/255/216/201) with **zero escapes**. Labour was not
   binding.

**The one change that reproduces the outcome** is a build-priority rule, not a purchase rule: when the
agent is about to buy an animal, prefer spending the next free `BUILD_PASTURE` turns on pastures over
coops, so pasture capacity is never the constraint. The purchase order at step 151 need not change
at all — v50's own GOOSE purchase would still be legal, it simply would not have found a coop to put
two geese in if the second build slot had gone to a pasture.

**This is still a hypothesis, not a result.** v50 is a different agent and the causal attribution to
build order is inferred from a single paired game. What the diagnostic establishes firmly is the
narrow factual claim: **a two-sheep conversion at day 6 is achievable in six hours with no crop
displacement and no additional cash beyond the $400 price difference, and one agent in this very
replay demonstrated exactly that sequence.** What it does not establish is that a build-priority rule
applied to V57-reset would reproduce v50's final score.

**Recommendation: do not abandon this route.** Abandoning it is not justified — a concrete,
observed, zero-slack-cost build window exists and is demonstrably reachable. The correct next step is
narrow and read-only: confirm from this same replay whether the two day-6 `BUILD_COOP` actions are
what forced the goose route, by checking whether V57-reset had coop vacancy available at any point on
day 6 that it chose to spend on a pasture instead. If the two coop builds were capacity-forced rather
than priority-chosen, a build-priority change is the correct intervention; if coops were genuinely the
better use of those two turns, then the goose purchase was a sound local decision and the wool deficit
needs a different explanation entirely.

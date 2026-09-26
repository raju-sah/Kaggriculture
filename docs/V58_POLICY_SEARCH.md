# V58 adaptive production search

## Question and evidence boundary

This search tests whether the reset baseline can allocate its existing melon-plot planting schedule to a more valuable crop using only the current market quote, the shops already unlocked, the visible market inventory, and the known shop-unlock process. It does not alter the frozen candidate, `main.py`, opponent policies, or the official 93000–93049 holdout.

Prior probes make a broad shop-rule search a poor next step: early shop filtering suppressed useful livestock; cow/sheep and capped goose/sheep substitutions reduced scores; early liquidation duplicated sales already made; staffing/land expansion failed the eight-agent follow-up, especially against v54/v56; the wheat/fertilizer sale overlay was sharply negative; and late sale ranking was score-neutral. The seed-92900–92904 reset baseline scored 66/110 (60%) and failed both acceptance gates. The new family therefore changes one production decision at a time: which crop occupies a melon planting slot, while preserving the base route, animal mix, planting locations, and terminal policy.

The selection rule estimates each eligible crop's remaining harvestable units and demand sinks. It counts already unlocked shops directly, forecasts only the expected product share of not-yet-drawn shops from the pinned engine's with-replacement shop distribution, and discounts that forecast by a searched weight. It caps estimated sales at sink volume, values them at the current observed price, subtracts seed cost, and charges a searched opportunity cost per harvest after the first. It never reads the seed, future shops, hidden state, or evaluation outcomes. The candidate's last callable is an explicit, uniquely named wrapper; the tournament loader must execute that entrypoint for every match.

This is a small, predeclared grid, not an open-ended optimizer: forecast weight is 0.5 or 1.0; harvest opportunity cost is 200 or 400 coins per additional harvest cycle. The baseline is included as a control. Tuning seeds are 94200–94202 against v48, v50, v53, and v54 in both seats. The scorer selects the configuration with the best worst-opponent mean paired margin change, then breaks ties by overall mean paired margin change. Confirmation is a one-time comparison of that fixed configuration with the reset control on seeds 94210–94214 against all eight historical labels v48 and v50–v56, both seats. There is no retuning after confirmation results are observed. These five confirmation seeds are development evidence only; the separate 93000–93049 final holdout stays sealed.

The candidate's sale path adds a sell order for produced strawberry or tomato only when projected shed stock exists and a market slot remains. Existing melon and wheat orders are preserved. All candidate and control runs use identical seed/opponent/seat keys; report both seat-level outcomes and paired coin-margin deltas. Because policies can perturb RNG draw order, a shared numeric seed does not imply identical realized shop sequences. The search is rejected if it introduces any errors, if its confirmation paired mean gain is not positive, if fewer than two of the four tuning opponent groups improve, or if the confirmation result depends on one opponent alone. A pass is not release approval or leaderboard evidence.

## Seed-use ledger

| Range | Allocation | Status |
| --- | --- | --- |
| 92802 | Earlier v58 diagnosis and known-policy probes | Spent |
| 92900–92904 | Frozen reset baseline validation | Spent |
| 93000–93049 | Final byte-frozen candidate holdout | Reserved, untouched |
| 93200–93205 | Earlier v58 policy branch probes | Spent |
| 93300+ | Diagnostics follow-up allocations | Existing project allocation; do not reuse |
| 93400–93403 | Early expansion screen | Spent |
| 93600–93604 | Eight-opponent expansion screen | Spent |
| 93700–93703 | Wheat/fertilizer sell overlay screen | Spent |
| 93800–93804 | Late-only value-order probe | Spent |
| 94100+ | Elite route | Allocated elsewhere |
| 94200–94202 | Adaptive crop search/tuning | Allocated here |
| 94210–94214 | One-time adaptive crop confirmation | Allocated here; do not inspect before freeze |
| 94203–94209, 94215+ | Unallocated | Untouched by this search |

Configuration hashes, candidate hashes, runner output, all tried parameter sets, and per-game records belong under the ignored `experiments/runs/v58_policy_search/` directory. The generator, evaluator, and analysis scripts are under `experiments/v58_validation/search/`.

## Tuning outcome (94200–94202)

The exact Kaggle `get_last_callable` loader was exercised against actual replay observations before the full panel. It selected `_v58_adaptive_production_search_entrypoint`; for both seat observations at step 6, the control bought two MELON seeds and the adaptive arm bought two STRAWBERRY seeds. This verifies that the tournament actually tested the wrapper.

All 120 planned tuning games completed with zero agent or infrastructure errors. Each candidate was paired against the same opponent/seed/seat control. Results were:

| Configuration | Mean paired coin-margin delta | Worst opponent mean delta | Paired win gains / losses | Candidate W-L-D |
| --- | ---: | ---: | ---: | ---: |
| f050_h200 | -30,192.5 | -41,973.7 | 0 / 16 | 1-23-0 |
| f050_h400 | -1.0 | -17.7 | 0 / 0 | 17-7-0 |
| f100_h200 | -30,192.5 | -41,973.7 | 0 / 16 | 1-23-0 |
| f100_h400 | -1.0 | -17.7 | 0 / 0 | 17-7-0 |

Per-opponent mean paired deltas were -18,629.2 (v48), -41,973.7 (v50), -41,814.8 (v53), and -18,352.5 (v54) for either h200 configuration. Either h400 configuration produced -10.5 (v48), +12.0 (v50), +12.0 (v53), and -17.7 (v54). The two forecast weights produced identical matches at a given harvest cost, so the forecast parameter did not change decisions in this panel. The h200 setting reversed 16 control wins and gained none; the h400 settings changed no paired win/loss result and averaged slightly negative coin margin.

The predeclared tuning rule selects f100_h400 only by its final lexical tie-break with f050_h400. Neither has positive overall paired margin gain, neither has a positive worst-opponent gain, and neither improves the paired win record. Therefore the adaptive family does not merit the reserved 94210–94214 confirmation panel; those seeds remain unused. This is negative development evidence, not release evidence. The baseline route's reuse/originality concern remains separate and unresolved by this wrapper search.

All per-game records, plans, generated source, and hashes are in `experiments/runs/v58_policy_search/tune/` (ignored runtime data). The four generated agent SHA-256 values are f050_h200 `cf7b125f1b7483814627ad950541984aef1a1f33e21f22fe56856fb1d212cc2`, f050_h400 `3c05b12d84cb8e1e38827ff7b515eb45e57f94ee1b237acc253f95ed22795f7a`, f100_h200 `5901526b57cd516cf5896be12ae5e96ac67d141fe1a16517ec5504f87d172100`, and f100_h400 `868ab62f92640c1275f22c787ed4a03d4793ae819c003e048d749113f70a9e73`.

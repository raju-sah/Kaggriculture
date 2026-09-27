# V88: V50 versus V56 causal difference — rigorous diagnostic, NO CANDIDATE

Read-only. Saved replays, pinned Kaggriculture 1.32.7, exact per-step settlement. No new holdout,
no agent code edited, no submission. All outputs under `experiments/v88_terminal_phase/`.

**Outcome: no candidate implemented. The branch stops here with a diagnostic**, because the valid
data does not contain a reachable single-rule action change that satisfies the predeclared gate.

## Correction: the first V88 pass was invalid and is discarded

The first pass compared replay files matched by **filename prefix** and reported a "days 24–29"
delta of −2,163 per game. That is wrong and is retracted.

In this project a replay file is named for the **opponent**, not the candidate. Proof from the five
distinct `v50-seed-92802-ab-repeat-0.json` files on disk:

| Path | Recorded agents | Final coins |
|---|---|---|
| `v57_broad/.../spent_seed_92802/reset/replays/` | v57_reset_candidate.py vs v50_agent.py | [78631, 112218] |
| `v58_planner_eval/.../allocator/replays/` | candidate_agent.py vs v50_agent.py | [77947, 113785] |
| `v80_wool_route/runs/screen_92802/replays/` | candidate.py vs v50_agent.py | [53067, 105795] |
| `v81_expert_switch/runs/screen_92802/replays/` | hybrid.py vs v50_agent.py | [65182, 88632] |
| `v87_opening_sales/runs/screen_92802/replays/` | candidate.py vs v50_agent.py | [51204, 133203] |

The first pass therefore compared a **V50 opponent seat in one game** against a **V56 opponent seat
in a different game with a different opponent**. Nothing in it was attributable. It also conflated
**stock** (shed contents, yield on tiles) with **flow** (accepted SELL units), and attributed a
production gap to a market-clearance rule before auditing actor composition.

Discarded artifacts, retained only as a record of the error:
`paired_terminal_diff.py`, `production_vs_liquidation.py` and their JSON outputs.

## Valid basis, rebuilt from agent SHA-256 rather than filenames

`provenance_audit.py` reads every `games.jsonl`, maps each recorded agent SHA-256 to a name, and
requires both seats to be exactly the frozen V50 and V56 hashes:

- `experiments/v50_agent.py` = `e6b50128e023e3b9fafa1841e4cd520c5e581acb48e8628657585c18272eab2b`
- `agents/v56_agent.py` = `d9e9670921b62afedfa8cbc7086d2a2ec19e153ee26006cef477eadd462bd19c`

**66 direct V50-vs-V56 games exist, of which 56 have a saved replay**, covering **28 already-spent
seeds** in both seat orders (92802, 93700, 94700, 95100, 95200, 95300, 95301, 95302, 95500–95519,
95600). In those games the two agents share the seed, the market and the weather, so a difference is
attributable to the agent. This satisfies the "at least 4 spent paired seeds, both seats"
requirement with room to spare. No fresh seed was spent to obtain it.

## Result on valid data: the head-to-head is genuinely mixed

| Measure | Value |
|---|---|
| Games | 56 (28 seeds × both seats) |
| V56 wins | **32 / 56 (57%)** |
| Mean final coin delta (V56 − V50) | **−19,919** |

V56 wins more often and loses harder. Phase decomposition of accepted SELL proceeds:

| Phase | V50 | V56 | Delta | V50 units | V56 units | Delta |
|---|---:|---:|---:|---:|---:|---:|
| Days 0–5 | 3,037 | 2,636 | −402 | 51.0 | 42.8 | −8.2 |
| Days 6–11 | 28,485 | 25,254 | −3,231 | 188.0 | 194.0 | +6.0 |
| **Days 12–23** | **64,368** | **51,216** | **−13,152** | 691.0 | 612.7 | **−78.3** |
| Days 24–29 | 38,541 | 37,093 | −1,448 | 638.0 | 604.3 | −33.7 |

The dominant deficit is **days 12–23**, not the terminal window. The earlier claim that the two
agents are identical in days 0–5 and differ only at the tail does not survive: the day 0–5 gap is
small but real, and the largest single gap is mid-season.

## The causal difference is product composition, not liquidation efficiency

This is the answer to the question asked. Measured with exact transitions, days 24–29:

| Product | V50 units | V56 units | V50 $ | V56 $ |
|---|---:|---:|---:|---:|
| WHEAT | 14,336 | 11,230 | 520,754 | 396,331 |
| WOOL | **5,376** | **596** | 470,273 | 67,414 |
| STRAWBERRY | 4,256 | 3,821 | 430,707 | 340,987 |
| CARROT | 4,592 | 4,288 | 263,207 | 248,194 |
| MILK | 2,352 | 3,066 | 360,360 | 427,449 |
| FERTILIZER | 4,816 | 3,528 | 112,976 | 64,852 |
| **EGG** | **0** | **3,662** | 0 | 180,452 |
| **TOMATO** | **0** | **3,652** | 0 | 351,530 |

**V56 is the tomato and egg line. V50 is the wool line.** V50 sells 9.0x more wool; V56 sells eggs
and tomatoes that V50 never produces at all. Neither is "better at selling": they are running
different production portfolios, and the embedded `_ACTIONS` tapes differ (719 entries each,
584 positions differ, tape digests `f8c9a271…` vs `2a251049…`).

**The stock evidence rules out a liquidation gap.** Shed capacity entering day 24 is **91 units for
both agents**; animal yield standing on tiles at day 24 is 26.0 (V50) and 27.8 (V56). V56 is not
short of inventory and is not failing to clear it. The d24–29 unit shortfall of −33.7 per game is
fully explained by which products each portfolio contains.

**Action-level differences are consistent with the portfolios, not with a defect.** Per game, days
24–29: HARVEST 162.0 (V50) vs 180.1 (V56), FERTILIZE 35.0 vs 56.3, PICKUP 32.0 vs 42.5,
PASS 83.0 vs 115.4. V56 harvests more, fertilises more, picks up more, and idles more — the
signature of a different crop mix (tomato needs repeated fertilising and four daily yields; wool
needs feeding and shearing) rather than an execution shortfall. WATER is effectively identical
(259.0 vs 260.1).

## Why the two V56-only rules are not the cause

V56's wrapper adds exactly two calls that V50 lacks:

1. `reorder_market(obs, action, mode="impact_slots")` on **every** turn from step 0;
2. `terminal_market(obs, action, "collision", replace=False)` from `CLEARANCE_STEP = 629`
   (day 26, hour 5).

The terminal rule cannot explain the dominant **days 12–23** deficit, which begins five days before
it activates. The `impact_slots` rule is the only V56-only behaviour active during that window, so
it is the one candidate mechanism the data cannot exclude. It is not, however, isolable from the
portfolio difference with the data available: the portfolio is set by the differing `_ACTIONS` tape
and the planner's own targets, and the two are entangled in the same 12–23 window. Separating them
would need a V56 variant with the same tape and `impact_slots` disabled, screened on spent seeds,
which is a new agent family rather than a bounded overlay.

## Prior work checked, to avoid repeats

- `docs/V58_TERMINAL_INSIGHT.md` audited the terminal actor route and **recommended against** a
  late-game DROP/harvest overlay: by step 716–719 the actors are already at the shed issuing DROP,
  with no mature crop left, and the last two actions earn the same $1,109 for both seats. That
  finding is consistent with the stock measurements here and is not re-litigated.
- The same document names market-order sequencing as the only untested close-game axis, and notes
  the expansion agent is independently testing final-market order ranking. `impact_slots` touches
  that axis on every turn, not only at the close, so it is broader than the prior test.

## Why no candidate is implemented

The predeclared gate was: 8 spent seeds × both seats vs V50 and V56, ≥60% wins vs both, positive
median cash delta vs both. A candidate would have to beat **both** frozen agents. The valid data
shows the two agents occupy **different product portfolios**, and the mid-season (days 12–23)
deficit that dominates V56's losses is consistent with the portfolio itself rather than with a
discrete, bypassable rule. There is no single action change evidenced here that would move V56
above both.

Building a candidate anyway would mean tuning against a 57%-win head-to-head whose per-seed sign
flips (V56 loses 12 of 28 seeds outright, including 95518 at −39,441), which is the same failure mode
that produced the rejected V80, V81, V84, V86 and V87 branches.

**Stop condition met: no credible candidate. Branch closed without implementation.**

## Limits

- 56 games over 28 spent seeds, all previously spent. V50 and V56 have both been tuned on some of
  these seeds, so the 57% head-to-head is not an unbiased estimate of either agent's strength.
- The `impact_slots` rule is not isolated. Its contribution to the days 12–23 deficit is untested,
  and separating it requires a new agent family and a fresh spent-seed screen.
- Product attribution uses accepted engine transactions, which is exact, but the *decision* to plant
  tomato and eggs sits in the differing `_ACTIONS` tapes and the planner, not in the wrapper, so
  "composition not efficiency" is a strong association rather than a proven cause.
- Days 12–23 is measured as a phase total of accepted proceeds; it mixes crop, herd and market
  contributions and is not further decomposed.
- No new seed was spent, nothing was submitted, and no frozen file was modified
  (`v50_agent.py` and `v56_agent.py` digests re-verified unchanged after the audit).

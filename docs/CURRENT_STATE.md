# Current Kaggle submission and leaderboard — 2026-09-26

## V77 runway screen — 2026-09-27

The third-land cash/service runway candidate was rejected on its prescribed spent-seed first screen. After correcting a provisional planting-window defect, frozen [`agent_v77.py`](../experiments/v75_joint/agent_v77.py), SHA-256 `03a94dd08fb588c68ff6ef9cc7cf522403b6ee6e6f0e06f8bb01e3aa2627ffa6`, bought no third land: the best pre-cutoff V56 checkpoint had only $946 projected cash after the land, seed, and three-day feed commitments, below the $4,500 reserve. It scored $70,962 and $92,873 accepted sales in each V56 seat, versus required $85,962 and $110,000; it lost both V70 seats. All four games had zero execution errors and exact settlements, but one sheep remained unplaced for much longer than 48 hours in three of four games. The provisional late-land run also failed and is retained separately. No 92802/92804, fresh seed, holdout, or Kaggle submission was used. Full gate audit: [V77 runway report](../experiments/v75_joint/V77_RUNWAY.md). Top-ten readiness and the requested historical 100% sweep remain unproven.

## Live update — 2026-09-27 01:47:49 UTC

The latest full public leaderboard download places Rajusah at **rank 3,475/10,059**, score **1,184.3**. The current tenth-place score is **2,889.1**, leaving a **1,704.8-point** gap. This remains the rating of the existing V56 submission, not a result for an experimental candidate. The exact downloaded snapshot is `/tmp/kaggriculture_leaderboard_latest/kaggriculture.zip`; the temporary download is not a durable project artifact.

The next full leaderboard download at **2026-09-27 02:04:25 UTC** places Rajusah at **rank 3,481/10,059**, score **1,180.8**; tenth place is **2,890.4**, a **1,709.6-point** gap. The rating movement is on the current submission, not a candidate result.

The repaired V75 service baseline produced a staged, locally authored herd-and-crop candidate, SHA-256 `6d4e7c18c81fc499ee97849b988e821e1f6fabdbea687279b95abb92b85db6c4`. Its exact-loader screen on the spent seeds 94700 and 92802 was **0–4 vs V56** and **2–2 vs V70**, with zero execution errors. It raised own cash over the saved V70/V56 comparison by $13,896 and $10,279, respectively, but both gains missed the $15,000 gate. Its direct V56 margins were -$82,020 on 94700 and -$46,334 on 92802. Sheep placement is now fixed, yet day 6–11 sales still trail the baseline. The placement repair also changed the direct V70 result on seed 94700 from 1–1 to 0–2 as candidate seat-0 accepted sales fell by $25,288; the exact work-routing cause is unresolved. No fresh seed, holdout, or submission was used; this is not promotion-ready. Details and replay audit: [V75 joint experiment](../experiments/v75_joint/README.md) and [historical unpatched tranche audit](../experiments/v75_joint/AUDIT.md).

A single follow-up third-land/strawberry/cow macro variant, SHA-256 `4e0cf678ccb2173c9b062d66ddd25e157fa3d87e039863f5e6d9ce70fa0c0887`, failed its first spent-seed gate on 94700: **0–2 vs V56** at $45,639 own cash and **0–2 vs V70**, with zero errors. It reached three lands and 21 strawberries by day 12 but had only $408 and five hands; livestock later escaped. Seed 92802 was not spent on this variant. It is rejected, not promoted. See [macro variant report](../experiments/v75_joint/MACRO_VARIANT.md).

An isolated V76-style early melon harvest window was also overlaid on the frozen V75 joint repair, source SHA-256 `893c53176d523fc62f7d72ac66dcf593c2d0f3fd47e64c7e918c75cc7b0e9990`. On spent 94700, it raised days 6–11 accepted melon sales from $0 to $4,727 per V56 game but reduced final own cash to $46,240/$47,317 (both losses) from the parent's $70,962. It also lost both seats to V70. Later wool/crop sales fell sharply; exact settlement matched every cash frame and no errors occurred. This variant is rejected after the first gate; no second seed, holdout, or submission was used. See [melon-window report](../experiments/v75_joint/MELON_WINDOW.md).

The latest official leaderboard ZIP snapshot checked at **2026-09-26 17:14:31 UTC** shows team Rajusah at rank **3448/10049** with score **1189.7**; rank 10 had score **2880.3**. The 1189.7 score is the existing V56 best. Submission **56583862** (V66) had score **442.2** at this latest check. These are dated leaderboard observations, not a readiness assessment.

An original state-derived planner was uploaded to Kaggle as **submission 56583862** at 16:13:55 UTC with message `Original state-driven planner v66; dynamic opening geometry; exact-loader validated`. The official Kaggle CLI reports **COMPLETE**; its public rating was **506.5** at the first result query and **492.1** on a later query (the rating is dynamic). This is far below top-ten readiness. Uploaded file: [`experiments/submission_candidate_20260926/bundle/main.py`](../experiments/submission_candidate_20260926/bundle/main.py), SHA-256 `d82c430c9562b6b213b92899d4df59aa9b9b58bcc8bdf3522b9e819da03e083d`. The source/provenance and standalone packaging audit are in [submission provenance](SUBMISSION_PROVENANCE_2026-09-26.md), [candidate result](SUBMISSION_IMPROVEMENT_2026-09-26.md), and the bundled manifest. It did not meet the requested 10/10 sweep: on spent seed 94700 it lost both seats to each of v50, v54, and v56, with zero errors. No fresh promotion seeds or sealed final holdout were used.

# V70 local comparison and validation status

The strongest original local candidate currently recorded is V70 capacity source SHA-256 `2002db9`. It won 6/6 games against the prior frozen batch across three spent seeds and lost 0/6 against V56, with mean own cash **$57,185** and mean margin **−$79,123** against V56; no errors were reported. It has not undergone fresh validation or an official submission, and top-ten readiness remains unproven. See the [V70 capacity report](V70_CAPACITY.md) and [V70 assignment report](V70_ASSIGNMENT.md). The leaderboard snapshot above remains timestamped **2026-09-26 17:14:31 UTC**.

# Previous v62–v65 research state — 2026-09-26

**No new agent or submission was promoted.** The user-supplied DSM–Boey episode 113718271 and six other public games were analyzed with exact action-to-result alignment; accepted transactions reconcile every cash transition. DSM won the supplied game by **$3,005**, despite Boey's much larger gross sales, because Boey also bought far more products. See [V62 elite-game research](V62_ELITE_GAME_RESEARCH.md). [Recent Kaggle discussion research](V62_DISCUSSION_RESEARCH.md) and the pinned engine confirmed fertilizer timing and market/RNG mechanics; a fertilizer action change had mixed or negative estimated value and was not tested in games ([mechanics audit](V62_FERTILIZE_MECHANICS.md)). Frozen v57's wheat/feed accounting showed no starvation or large feed-cost leak ([feed audit](V62_FEED_ECONOMY.md)); the matched-flow audit found no supported >$10k market gap ([actionable-gap audit](V62_ACTIONABLE_GAP.md)).

An expanded panel of **50 public top-player games** across ten leader lineages reconciled **71,900 player transitions with zero cash error**. Winners tended to invest earlier in animals, but this was observational and lineage-confounded; see [V63 elite panel](V63_ELITE_PANEL.md). A comparable exact-hash local panel of **58 frozen-reset games/31 spent seeds** found no recurring >$10k cash-flow deficit or day-6 herd separation between local wins and losses ([V63 local control](V63_LOCAL_CONTROL.md)). A small herd overlay failed offline feasibility: sampled wins and losses all had **6/6 occupied pastures** by day 5, so extra animals need a new housing/placement/feed/care route ([V64 herd gate](V64_HERD_GATE.md)). No V64 candidate or fresh matches were run. Existing validation and final-holdout seeds remain untouched; replay-derived submission rights remain unresolved.

The follow-up [V65 herd-route calculation](V65_HERD_ROUTE.md) tested the alternative of replacing two melon tiles with housing. On three spent replay states, the estimated lost melon sales were **$2.4k–$2.7k**, while two extra animals required further feed/care work and had negative estimated net value after the crop trade. This remained an offline, assumption-limited no-go: no V65 agent or matches were created.

# Previous v61 state — 2026-09-26

**No v61 agent is ready for promotion or submission.** A spent-seed replay audit found two real bugs in the original v60 economy policy: cross-crop seed inventory hid per-crop shortages, and optional buys suppressed affordable daily hires. The independent evidence is in [V61 audit](V61_INDEPENDENT_AUDIT.md). Separate corrected variants still lost **0/2 in both seats** against each of v50, v54, and frozen reset-v57 on spent seed 94700. The seed-only variant scored about **14.0k coins vs v50**; adding hire priority lowered that to **12.0k**, far below the reference policies. See [V61 cash-flow report](V61_CASHFLOW.md). Fresh seeds 96000–96001, the v59 validation gates, and final holdout 93000–93049 remain untouched; no submission was made.

# Previous v60 state — 2026-09-26

**The target remains unmet; no v60 candidate is ready for validation or submission.** An offline worker-dispatch audit found identical v57 worker actions on one seed against opponents it both beat and lost to; a reconstructed market audit found no candidate-side sales signal that explained those results. See [dispatch audit](V60_DISPATCH.md) and [causal lead audit](V60_CAUSAL_LEAD.md). Public top-player replays suggest earlier productive hiring and land access, but that is observational research, not a tested gain; see [original strategy research](V60_ORIGINAL_STRATEGY.md).

An original observation-driven economy agent was built and run on spent seed 94700 in both seats against v50/v54. It lost all four games at about **13.8k mean coins**; a daily-hiring correction also lost all four at **4.2k vs v50** and **12.3k vs v54**. A replay audit then found crop-agnostic seed budgeting that blocked target crops, but an isolated per-crop fix only raised the v50 score to **14.0k** and remained far behind v50, v54, and frozen v57. A separate hire-priority ablation also lost all six games and did not improve the score. Fresh seeds 96000–96001 remain **unused**. See [v60 agent report](V60_ORIGINAL_AGENT.md) and [v61 cash-flow diagnosis](V61_CASHFLOW.md). Validation gates and final holdout remain untouched; no new Kaggle submission was made.

# Previous v59 state — 2026-09-26

**No v59 agent is ready for submission or the requested 10/10 historical sweep.** The latest official leaderboard snapshot (11:39:11 UTC) places Rajusah **#3,450 at 1,186.5**, with tenth place **2,896.5**; see [V59 leaderboard](V59_LEADERBOARD.md). This is the existing submission's rating, not a v59 result.

The v59 teacher run was **79–35 across 114 games** on seeds 95501–95519 versus v50/v53/v54, but a coordinate-format bug left its intended perturbation inactive. These were frozen-v57 collection games, not learned-policy wins. A clock-free LightGBM worker clone reached 99.52% held-out action accuracy yet tied frozen v57 exactly in both seat orders on fresh seed 95600; see [state-teacher report](V59_STATE_TEACHER.md) and [diagnostics](V59_TEACHER_DIAGNOSTICS.md). An isolated early-Yarn sheep mix gate also had **zero action changes and zero paired gain** on fresh seed 95611 versus v50; see [mix-gate report](V59_MIX_GATE.md). Neither is promoted. Seeds 95500–95519, 95600, 95610, and 95611 are spent as individually documented; do not present them as fresh validation.

The [v59 validation protocol](V59_VALIDATION.md) now uses fresh smoke seeds 95900–95901, historical gate 95902–95906, and stronger development gate 95910–95914. Its 95800–95829 paired panel remains reserved, and final holdout 93000–93049 remains sealed. No v59 submission or final validation was run. Replay-derived agent rights remain unresolved for submission; see [replay rights](V58_REPLAY_RIGHTS.md).

# Previous v58 state — 2026-09-26

**No v58 candidate is ready for submission.** No competition submission was made. The official Sep 26 leaderboard snapshot places Rajusah at **#3,406, score 1,203.1**; tenth place is **2,904.7** ([snapshot report and archived rows](V58_ELITE_RESEARCH.md), [`leaderboard_snapshot_2026-09-26.json`](../experiments/v58_elite/leaderboard_snapshot_2026-09-26.json)). This is a dated status snapshot, not a result for a new candidate. The submitted policy has not been shown to meet the user's 100% historical-opponent target or top-ten readiness standard.

The strongest frozen-reset evidence is **66/110** wins (60%) across the five-seed, eleven-opponent screen, with losses to six of eight historical agents; its report is [V58 baseline screen](V58_BASELINE_SCREEN_2026-09-26.md), with run records in `experiments/runs/v58_validation_baseline/`. The later frozen-reset panel reached **60/80**, while early expansion fell to **42/80**; see the eight-opponent comparison in [V58 expansion](V58_EXPANSION.md). Neither establishes readiness.

Other routes and overlays also failed to justify promotion: the DSM replay-route study first scored **36/40** ([first-panel summary](../experiments/v58_expansion/elite_route/fresh_94100/dsm_route/summary.json)); its follow-up was stopped at **19/38** (records under [`experiments/v58_expansion/elite_route/`](../experiments/v58_expansion/elite_route/)); imitation scored **0/2** after its sowing correction ([V58 imitation](V58_IMITATION.md)); market optimization, handwritten original routes, and the original RL/economy prototypes were rejected or stopped after negative/near-no-op diagnostics ([market solver](V58_MARKET_SOLVER.md), [original route](V58_ORIGINAL_ROUTE.md), [original second route](V58_ORIGINAL_SECOND.md), [RL design](V58_RL_DESIGN.md), [strong economy](V58_STRONG_ECONOMY.md)). No broad expansion/search is justified by these results.

Final holdout seeds **93000–93049 remain sealed**. The shared validation allocation and original baseline protocol are recorded in [`experiments/v58_validation/plan.json`](../experiments/v58_validation/plan.json) and [V58 validation](V58_VALIDATION.md); additional per-branch plans and spent ranges are linked from the reports above. Do not reuse spent seeds as fresh evidence. Public-replay-derived routes still have unresolved reuse/originality questions; see [V58 replay rights](V58_REPLAY_RIGHTS.md). `main.py` and all submission actions remain outside this validation update.

# Current State

## Broad validation and overnight repair screening completed

- Frozen v57/v56 comparison completed **540 games**, seeds 92700–92729, both seats, zero execution errors. Common panel: v57 **186/240 (77.5%)**, v56 **177/240 (73.75%)**; paired gain **+3.75 pp**, 95% seed-block interval **[+0.83,+7.50] pp**. Nine favorable win flips, zero unfavorable flips. Direct v57–v56: **45–15**.
- The predeclared +5 pp minimum gain was not met; the other three gates passed. See [V57_BROAD_VALIDATION.md](V57_BROAD_VALIDATION.md). Original release remains frozen and unsubmitted.
- A severe direct loss on seed 92718 revealed an inherited weed-repair transaction surviving the overnight actor reset. A separate candidate clears transactions on day change; the exact game improves from a **59,146-coin loss** to a **4,292-coin win**. Eleven targeted checks pass. See [V57_RESET_DIAGNOSIS.md](V57_RESET_DIAGNOSIS.md).
- Experimental candidate: `experiments/v57_broad/v57_reset_candidate.py`. Fresh 80-game screening against all eight requested historical agents on seeds 92800–92804 completed **54–26 (67.5%)**, zero errors; v56 **8–2**. This uses different seeds and opponents from the broad panel, so the percentages are not comparable. **Continue fine-tuning before promotion/submission.** See [V57_RESET_VALIDATION.md](V57_RESET_VALIDATION.md). Plan/results: `experiments/runs/v57_reset_validation/`. No change to existing `main.py` or original v57 submission archive.
- Seeds 92700–92729 and 92800–92804 are now allocated/spent; do not represent subsequent tuning on them as fresh validation.

## Verified v57 update — 2026-09-25

- Latest verified live snapshot (17:39:40 UTC): Rajusah / rajucode **#3,464 of 10,012**, score **1187.7**; top-ten cutoff **2916.2**. This is the existing submission's rating.
- New local candidate: `agents/v57_agent.py`; standalone archive: `experiments/v57/v57_submission.tar.gz`. Existing `main.py` preserved; no submission performed.
- Frozen holdout: **56 wins, 24 losses, zero draws/errors in 80 games**. Exactly ten games against each requested version, using seeds 92600–92604 in both seats. v54 and v56: **10–0 each**. The overall 100% target and top-ten placement are not achieved.
- Seven new release-control checks pass. Standalone full-game timing: median **0.80 ms**, maximum **7.27 ms**. Six legacy opener tests still fail against existing `main.py`.
- Details, limitations, exact results, and reproduction: [V57_RESULTS.md](V57_RESULTS.md). Live-source research: [V57_RESEARCH_2026-09-25.md](V57_RESEARCH_2026-09-25.md).
- Development seeds 92500–92508 and holdout seeds 92600–92604 are spent. Do not reuse them as fresh validation for subsequent changes.

## Historical state below

The following earlier notes are retained for provenance; their leaderboard claims and next-task recommendations are superseded by the verified update above.


Updated: 2026-09-24 (v54 Lizs Elo 2522 Multi-Livestock Champion PROMOTED & DEPLOYED: 104.4k Mean Coins, +1,949 vs v53, 20-0 Clearance Sweep)

## Active supervisor

Antigravity is the active supervisor. Kaggle submission is authorized under standing rules.
Submissions deployed:
- S14 (ref 56527901): `main.py` (v54 Lizs Elo 2522 Multi-Livestock Champion: 6C/4S/7G + Step 630 Clearance + Weed Repair + Market Reorder). Status: PENDING/EVALUATING.
- S13 (ref 56522380): `agents/v53_agent.py` (v53 Step-630 Early Clearance Champion, 40-0 clean sweep vs v52 & v50, 100% win rate). Public score: 1039.4.
- S12 (ref 56515893): `experiments/v52_agent.py` (v52 Seat-Invariant Champion). Public score: 1219.4.
- S11 (ref 56512315): `experiments/v51_agent.py` (v51 Multi-Product Animal Engine). Public score: 1204.6.
- S10 (ref 56508894): `experiments/v50_agent.py` (v50 High-Velocity Opening + Late-Collision Terminal Overlay). Public score: 1233.2.
- S9 (ref 56504561): `experiments/kag-corpus/refagents/broker_bea.py` (Tier-6 Meta Line, opportunistic wheat timing). Public score: 748.6.
- S8 (ref 56504554): `experiments/kag-corpus/refagents/ledger_lena.py` (Tier-7 Meta Line, 164.5k bank target). Public score: 742.8.
- S7 (ref 56498149): `experiments/kag-corpus/refagents/closer_cleo.py` (Tier-9 Reordered Sell Meta). Public score: 708.5.
- S6 (ref 56498144): `experiments/v48_agent.py` (v48 Fast-Climber Sparse Route Hybrid). Public score: 1043.2.
Remaining quota: 0 submissions remaining today.

## Current champion

`main.py` is the v54 Lizs Elo 2522 Multi-Livestock Champion (sha256 `9c374f64...`, 41,344 bytes).
Prior v53 retained at `agents/v53_agent.py`. Prior v52 retained at `experiments/v52_agent.py`.

### Empirical Replay Autopsy of v53 on Kaggle Ladder:
- Downloaded and analyzed 43 completed live public replays (`experiments/v53_replays/` via `experiments/analyze_v53_losses.py`).
- **The Deciding Divergence**:
  - In 100% of losses to top ladder opponents (arlenjim, Shantanu, Ernnnn4u, Utkarsh, Alex, lizs Elo 2522), opponents bought **only 4 sheep** and **6-11 cows + geese**.
  - v53 bought **11 sheep**, flooding town with 379 wool. Whenever `YARN_STORE` was missing or shared with opponent sheep, wool prices quadratically collapsed to $1-$17.
  - In contrast, milk has 3 town shops (`ICE_CREAM_SHOP`, `SMOOTHIE_SHOP`, `PET_CAFE`), eggs have 2 shops (`BRUNCH_SPOT`, `PET_CAFE`), and fertilizer/wheat have linear/logarithmic decay that never collapses.
  - In the live match against Grandmaster `lizs` (Ep 112896760), `lizs` crushed v53 132,281 to 86,047 (+46,234 coin margin).

### Architectural Innovations in v54:
1. **Grandmaster Lizs (Elo 2522.4) Balanced Multi-Livestock Backbone**:
   - 6 Cows, 4 Sheep, 7 Geese.
   - Sells Eggs (225), Milk (203), Wheat (426), Strawberry (263), Fertilizer (342), and moderate Wool (120).
   - Immune to Yarn Store absence; captures high-value Milk and Egg town shop demand in every game.
2. **Step-630 Early Continuous Clearance Engine**:
   - 20-0-0 (100.0% Clean Sweep) over raw policy; +453.5 coins margin per match across all seeds.
3. **Safe Market Impact Slot Reordering**: Reorders SELL slots within execution groups to protect buy orders from cash starvation while eliminating market price slippage.
4. **Closed-Loop Weed Repair**: Reclaims choked tiles while preserving open-loop hand synchronization.
5. **Full Seat 1 Normalization**: Guarantees zero step-drift in Kaggle evaluation containers (`obs["step"] = day * 24 + hour`).

### Promotion Tournament Evidence:
- **vs v53 Champion** (Seeds 6000-6009, both seats, 20 matches):
  - **Mean Coins**: **104,419.0** vs 102,469.8 (+1,949.2 coin advantage).
  - Massive blowout wins on diverse seeds:
    - Seed 6005: **148,910** vs 106,243 (+42,667 win)
    - Seed 6001: **146,198** vs 118,949 (+27,249 win)
    - Seed 6002: **116,517** vs 87,465 (+29,052 win)
    - Seed 6003: **87,553** vs 68,212 (+19,341 win)
    - Seed 6007: **73,672** vs 65,900 (+7,772 win)
- **vs v52 Champion** (Seeds 6000-6009, both seats, 20 matches):
  - **Mean Coins**: **104,953.5**; Median Difference: **+3,296.0**.
  - Seed 6005: **149,644** vs 105,786 (+43,858 win)
- **Ablation Sweep (Step 630 Clearance vs No Clearance)**:
  - **20-0-0 (100.0% Clean Sweep)**; average margin **+453.5 coins**.
- **Determinism Audit**:
  - Re-run self-play match on Seed 6000 produces identical coins `[94352.0, 94352.0]` (Determinism Verified: True).
  - **8-0-0 (100.0% Clean Sweep)**, Margins: **+11,327 to +52,587 coins**.

Superseded exp-s9 record:

Superseded exp-s5 record:

`main.py` is the exp-s5 straw-late champion (exp-3cow + late-strawberry
scale: 12-tile NE/SW field, plant d9-16, +2 hands, SELL strawberry;
sha256 `b894a8c0...`). Prior exp-3cow retained at `agents/exp3cow_3c2s.py`.

Promotion evidence (fresh holdout 5160-5169, both seats, 4 workers, 0 errors):
20-0-0 vs exp-3cow; Wilson 83.9%-100%; min +2,928, median +5,804. Dev
combined 40-0 (smoke 4412-4416 10-0 +4,641; gate 4417-4431 30-0 +5,353).
Regression 4417-4421 (50 games): 50-0-0 incl. jared 10-0. Determinism audit
4432: True. Seeds spent: dev 4412-4431 (+4432 audit); holdout 5160-5169.
Fresh dev starts 4433, holdouts start 5170.

Superseded exp-3cow record:

`main.py` is the exp-3cow champion (exp-s3 + animal-forward d0: (4,3)
converts sheep->cow, opener 3C2S; sha256 `55782c28...` — filled at submit).
Prior exp-s3 retained at `agents/exps3_sw_expansion.py`.

Promotion evidence (fresh holdout 5150-5159, both seats, 4 workers, 0 errors):
20-0-0 vs exp-s3; min +566, median +4,809. Dev combined 38-2 (smoke
4391-4395 8-2 with lone outlier 4395 -2.5k symmetric; gate 4396-4410 30-0
median +3,725). Regression 4396-4400 (50 games): 50-0-0 incl. jared 10-0.
Determinism audit 4411: True. Seeds spent: dev 4391-4410 (+4411 audit);
holdout 5150-5159. Fresh dev starts 4412, holdouts start 5160.

Superseded exp-s3 record:

`main.py` is the exp-s3 SW-expansion champion (exp-s2 + SW belt: BUY_LAND SW
d11-15 sequenced after NE, 4000 guard; pastures (3,5),(4,5),(3,6),(4,6);
herd to 6 cows, +1 hand; sha256 `b9f1d5b1...`). Prior exp-s2 retained at
`agents/exps2_ne_expansion.py`.

Promotion evidence (fresh holdout 5140-5149, both seats, 4 workers, 0 errors):
20-0-0 vs exp-s2; Wilson 83.9%-100%; min +2,760, median +3,112. Dev combined
39-1 (smoke 4370-4374 10-0; gate 4375-4389 29-1, lone loss 4386-s0 -180 vs
opponent 52.9k overperformance, diagnosed RNG-divergence not bug).
Regression 4375-4379 (50 games): 49-1 — jared 9-1 (+23,925), rest 10-0.
Determinism audit 4390: True. Seeds spent: dev 4370-4389 (+4386 probe, 4390
audit); holdout 5140-5149. Fresh dev starts 4391, holdouts start 5150.

Superseded exp-s2 record:

`main.py` is the exp-s2 NE-expansion champion (exp-0044 bridge + NE belt:
BUY_LAND NE d7-11, pastures (5,3),(5,4),(6,3),(6,4), herd to 4 cows, +1 hand;
artifact sha256 `a4f4c552...`). Prior exp-0044 policy retained as regression
opponent at `agents/exp0044_top_opener_bridge.py`.

Promotion evidence (fresh holdout seeds 5130-5139, both seats, 4 workers,
0 errors): 20-0-0 vs exp-0044; Wilson 83.9%-100%; min +3,144, median +3,799.
Dev 4350-4369: 30-0-0 (median +4,015, min +426); smoke 4350-4354: 10-0-0.
Regression 4355-4359 (50 games): 47-3 — pass/straw2/mixed/expansion 10-0 each,
jared 7-3 (+8,781). Determinism audit 4360 (both seats, 2 repeats):
deterministic True. Coin-for-coin transfer re-run 5130-5131 verified.
Seeds spent: dev 4350-4369, holdout 5130-5139; fresh dev starts 4370,
fresh holdouts start 5140.

Superseded exp-0044 record (merged `18e3a9f`, sha256
`e6941adcdc0b5fbefc8e7e2ae174068088ad20890dcb8031e5369cc15d7cbee9`):
reproduce the public top-agent pattern (2 cows, 3 sheep, 5 pastures at
(4,4)/(4,2)/(4,3)/(3,4)/(2,4), 4 hands, 10 wheat, 6 melon, near-capital);
day 2+ is a monotone-ownership duty planner: planting-day watering, feeding/
care, decay-deadline harvests, fertilizer collect+sell income, wheat/melon
replant cycles, goose coops + 2 geese (eggs from ~day 15). Champion body
(exp-0043a) retained inside the file as anomaly fallback; the exp-0043a
policy itself remains available as a regression opponent at
`agents/deterministic_straw2_hand.py` (sha256 `d51350f4ea90ade85efa4830f53654c74bba1f715a9c75382d4e60678f03ffeb`).

Promotion evidence (fresh holdout seeds 5120-5129, both seats, 4 workers,
0 errors — one run, no repeats):

- Direct comparison: 20-0-0 vs the exp-0043a champion; Wilson 83.9%-100%;
  median coin difference +6,662 (seat 0 +8,145, seat 1 +6,037.5 — symmetric,
  no seed subgroup regression); mean candidate 49.9k.
- Regression panel `exp-0044-regression-004` (dev 4331-4340, 7 opponents,
  both seats): 140-0-0 — champion 20-0 (median +5,938.5), jared scale clone
  20-0 (median +12,064.5), stopmelon/expansion/mixed/cowbase/pass 20-0 each
  (all decisive).
- Repeatability: determinism audits on dev 4341 and 4347 (both seats,
  2 repeats each) report `deterministic: True` with identical hashes per
  repeat group.
- Invariant audits (full-replay scans, dev 4342/4345/4346 vs
  champion/jared/stopmelon, both seats): day-0 pattern exact, zero escapes,
  zero aggregate plant rejections, zero stranded animals, roster 7 (2 cows,
  3 sheep, 2 geese), 2 coops, no weeds mid-season.
- Coin-for-coin transfer: post-promotion re-run of 5120-5121 with the
  promoted master bytes reproduced the holdout coins exactly.

Previous champion (exp-0043a two-strawberry-plot policy, source at
`agents/deterministic_straw2_hand.py`) is retained as a regression opponent.

Promotion evidence for exp-0043a itself (superseded 2026-09-20): fresh
holdout 5110-5119 18-0-2 (median +8,753); regression 70-0-0; determinism
verified.

Promotion evidence from holdout runs on untouched seeds 5080–5089 (both seats, 4 workers, 0 errors):

- Direct comparison: 20–0–0 against the previous 2c2s2g champion; Wilson 83.9%–100%; median +900.5; symmetric seats (10–0 each). Combined with dev (26–0 on 4147–4166): 46–0 over 56 paired games — never lost. Post-promotion re-run with promoted bytes reproduced 5080–5081 coin-for-coin.
- Regression panel (5080–5084, 70 games): 70–0–0 across pass/cowbase/2c2s2g/stopmelon/expansion/mixed/strawberry.
- Combined holdout: 90–0 over 90 games, 0 errors.
- Repeatability: determinism audit (4147–4148, both seats, 2 repeats) reports `deterministic: True` with identical hashes per repeat group.

Previous champion (2c2s2g, source at `agents/deterministic_cow2sheep2goose2h4_hand.py`) is retained as a regression opponent.

Promotion evidence from holdout runs on untouched seeds 5060–5069 (both seats, 4 workers, 0 errors):

- Direct comparison: 20–0–0 against the previous 2c2s champion; Wilson 83.9%–100%; median +3,539.5; symmetric seats (10–0 each). Combined with dev (10–0 on 4122–4126): 30–0 over 34 paired games. Post-promotion re-run with promoted bytes reproduced 5060–5061 coin-for-coin.
- Fourth-hand productivity proven live: 58 wool + 61 eggs with care bonuses earned (vs 10/31 without split), zero rebuys, continuous sell flow.
- Regression panel (5060–5064, 70 games): 70–0–0 across pass/cowbase/2c2s/stopmelon/expansion/mixed/strawberry, median +22,848.
- Combined holdout: 90–0 over 90 games, 0 errors.
- Repeatability: determinism audit (4122–4123, both seats, 2 repeats) reports `deterministic: True` with identical hashes per repeat group.

Previous champion (2c2s, source at `agents/deterministic_cow2sheep2_fert_berry_hand.py`) is retained as a regression opponent.

Promotion evidence from holdout runs on untouched seeds 5050–5059 (both seats, 4 workers, 0 errors):

- Direct comparison: 20–0–0 against the previous fertstraw champion; Wilson 83.9%–100%; median +11,359; mean 33,738; symmetric seats (10–0 each). Combined with dev (4–0–6 on 4096–4100): 14–0–16 over 30 paired games — never lost. Post-promotion re-run with promoted bytes reproduced 5050–5051 coin-for-coin.
- Regression panel (5050–5054, 70 games): 70–0–0 — 10–0 vs pass/cowbase/berry/stopmelon/expansion/mixed/strawberry, median +19,969.
- Combined holdout: 90–0 over 90 games, 0 errors, zero escapes, continuous sell flow.
- Repeatability: determinism audit (4112–4113, both seats, 2 repeats) reports `deterministic: True` with identical hashes per repeat group.

Previous champion (fertstraw, source at `agents/deterministic_cow_fert_berry_fertstraw_hand.py`) is retained as a regression opponent.

Promotion evidence from holdout runs on untouched seeds 5040–5049 (both seats, 4 workers, 0 errors):

- Direct comparison: 10–0–10 against the previous berry champion; median +1,066; decisive record 10–0 with symmetric seats (5–0–5 each). Combined with dev (4–0–6 on 4096–4100): 14–0–16 over 30 paired games — never lost. Post-promotion re-run with promoted bytes reproduced 5040–5041 coin-for-coin.
- Fertilizer synergy verified in-action: 8 applications cover all 16 productions (trigger seeds 4097/4099: +2.9k/+3.1k decisive wins; non-trigger seeds draw identically, no regression).
- Regression panel (5040–5044, 60 games): 58–2 overall — 10–0 vs cowbase/mixed/strawberry/pass/stopmelon (stopmelon threat fixed: was 6–4), 8–2 vs expansion (+4,030).
- Combined holdout: 68–2–10 over 80 games, 0 errors.
- Repeatability: determinism audit (4096–4097, both seats, 2 repeats) reports `deterministic: True` with identical hashes per repeat group.

Previous champion (berry without synergy, source at `agents/deterministic_cow_fert_berry_hand.py`) is retained as a regression opponent.

Promotion evidence from holdout runs on untouched seeds 5030–5039 (both seats, 4 workers, 0 errors):

- Direct comparison: 10–0–10 against the previous fert-cow champion; median coin difference +1,140.5; decisive record 10–0 with symmetric seats (5–0–5 each). Combined with dev (6–0–4 on 4070–4074): 16–0–14 over 30 paired games — never lost. Post-promotion re-run with promoted bytes reproduced 5030–5031 coin-for-coin.
- Loss-seed flips: 4046/5021/5024 (all lost by the previous champion) go 6–0 with +3.1k to +6.0k gains.
- Regression panel (5030–5034, 60 games): 56–4 overall — 10–0 vs cowbase/mixed/strawberry/pass/stop-melon, 6–4 vs expansion-melon (+709, matching the previous champion's own level).
- Combined holdout: 66–4–10 over 80 games, 0 errors.
- Repeatability: determinism audit (4070–4071, both seats, 2 repeats) reports `deterministic: True` with identical hashes per repeat group.

Previous champion (two-cow fert-collect, source at `agents/deterministic_cow_fert_hand.py`) is retained as a regression opponent.

Promotion evidence from holdout runs on untouched seeds 5020–5029 (both seats, 4 workers, 0 errors, GLM review CLEAN):

- Direct comparison: 16–4 against the previous melon champion (6–4 on 5020–5024, 10–0 on 5025–5029); symmetric seats; champion invariant at exactly 21,201 in every game, confirming per-product market separability. A post-promotion re-run with the promoted bytes reproduced the 5020–5024 games coin-for-coin.
- Regression panel (5020–5024): 47–3 overall — 10–0 vs cow-base (+4,642), 10–0 vs mixed (+8,633), 10–0 vs strawberry (+12,140), 10–0 vs pass (+20,227), 7–3 vs expansion-melon (+1,517, closest games).
- Combined holdout: 63–7 over 70 games. Losses are seed-symmetric town-shop demand draws (5021, 5024, and dev seed 4046), not execution errors.
- Dev evidence: 18–2 vs champion over 4040–4049, 10–0 vs pass (mean 26,083.6), 10–0 vs cow-base.
- Repeatability: determinism audit (5020–5021, both seats, 2 repeats) reports `deterministic: True` with identical hashes per repeat group.

Previous champion (eight-tile melon stop-day-19, source at `agents/deterministic_multitile_melon_stop19.py`) is retained as the melon-regime regression opponent.

Promotion evidence from `experiments/runs/exp-melonstop19-holdout-012` (untouched seeds 5010–5019, both seats):

- Direct incremental comparison: 20–0 against the previous melon champion; median coin difference +720; strict-win Wilson 95% interval approximately 83.9%–100%.
- Regression panel: 20–0 against each of mixed, strawberry, wheat, and pass.
- Combined holdout record: 100 wins, 0 losses, 0 draws, 0 errors. The 80 weak-opponent games are regression checks, not independent evidence for the incremental stop-day change.
- Dev-seed evidence from `exp-melonstop19-panel-011`: 135–1–0 across 17 seeds 4000–4016 (sole loss a weed-divergence seat).
- Eight-game exact-repeat audit produced identical normalized replay hashes per repeat group.

Promotion evidence from `experiments/runs/exp-melon-holdout-gate-004` (untouched seeds 5000–5009, both seats):

- 80 games, 80 wins, 0 losses, 0 draws, 0 errors.
- 20–0 against the previous carrot champion; median coin difference +14,211.
- 20–0 against mixed; 20–0 against wheat; 20–0 against pass.
- Identical win/loss results in player seats 0 and 1 (40–0 each).
- Dev-seed evidence from `exp-melon-panel-003`: 102–0–0 across 17 seeds 4000–4016.
- Eight-game exact-repeat audit produced identical normalized replay hashes per repeat group.

Melon is the strongest known local policy, but the promoted panel is still crop-only and dominated by deterministic single-route agents. Animal, worker, expansion, adaptive, and market-focused regimes remain unrepresented, so this remains an engineering champion rather than evidence of leaderboard strength.

Promotion evidence from `experiments/runs/exp-multitile-carrot-panel-001`:

- 136 games over 17 seeds, four opponents, and both seats.
- 102 wins, 0 losses, 34 self-play draws, and 0 errors.
- 34–0 against the previous champion; median coin difference +2,655.
- 34–0 against deterministic wheat and 34–0 against pass.
- Identical win/loss/draw results in player seats 0 and 1.
- Eight exact-repeat self-play games produced identical normalized replays.

These opponents are weak smoke baselines, so this is an engineering champion rather than evidence of leaderboard strength.

## Latest experiment

- Candidate: exp-0044 milestone-1 integrated (state-derived top opener + day-2
  bridge in `main.py`; champion body retained as anomaly fallback only)
- Source: `main.py` (single file, self-contained); evidence tools
  `analysis/public_replay_profile.py` + five replay JSONs under
  `/tmp/kag-video-analysis/replay`; literal transcript reference committed as
  `opening_script_literal.py` (agent 0, episode 111058336, day 0)
- Change: replaced the champion opening with the public top-agent pattern.
  Audit of the prior partial implementation found duplicate `OPENER_*`
  constant blocks (the later shadowed the former) and y=5 pasture
  coordinates, which are SW-quadrant LOCKED tiles (NW = x,y in 0..4) — both
  deleted; exact replay geometry is now the single source of truth. Days 0+
  are driven by a per-turn duty planner over live tile state ("monotone
  ownership"): place/fetch/build the five-pasture roster, feed/care all
  animals, harvest before one-shot crop decay, water every unwatered plant
  (planting-day watering is mandatory on the local engine — verified
  empirically; the public server replay is more lenient), plant the fixed
  10-wheat/10-melon footprint from seed stock with a plant+water deadline
  gate, collect and sell the daily fertilizer flow, goose coops day 4+ /
  geese day 10-14. Day-0 capital ladder mirrors the public transcript with
  affordability guards. Mechanics baked in: aggregate PLANT rejection, 2-day
  unfed escape, 2-day unwatered plant death, care-bonus fed+cared rule.
- Smoke evidence (vs pass, seat 0, seeds 4312/4313/4314): end of day 0 = 10
  wheat, 6 melon, 2 cows, 3 sheep, 5 pastures, 4 hands, ~53 coins (public
  ends ~5; the difference is the local-strict watering discipline and feed
  timing). 10 wheat by day 1; full 10-melon footprint by day 3-4 (the
  fourth day-1 melon seed defers to feed survival — one tile-day of drift
  vs the server-engine replay). Zero escapes, zero aggregate plant
  rejections, zero infra errors; finals 59.2k-60.1k vs pass 3k.
- Dev gate `experiments/runs/exp-0044-dev-gate-001` (fresh seeds 4315-4330,
  both seats, 4 workers, 0 errors): 64-0-0 overall — 32-0 vs the exp-0043a
  champion (median coin difference +8,674.5, mean candidate 52.3k) and 32-0
  vs pass (median +60,409); symmetric seats (32-0 each); Wilson 95%
  [0.89, 1.0]. The opening is a strict improvement on these dev seeds.
- Standing: milestone 1 complete. Not submitted; holdout 5120+ untouched.
  Next stage (milestone 2): third-quadrant expansion, price-driven
  cow/sheep allocation, 50+ crop scheduling, bought-feed fallback routing.

## Superseded exp-0042 details (signal screen; no promotion)

- Source: `analysis/pair_scan.py` + `analysis/gate_eval.py` (new) over paired `agents/deterministic_jared_wilder_clone.py` vs `main.py`
- Change: no agent change. 198 paired games (calibration 4182–4191, fresh dev 4202–4301), both seats, four workers, zero failures/errors, sampled public state only (no replay bodies).
- Finding: the first town unlock is a causal, legal, seed-level demand read. First shop ∈ {PIZZA_SHOP, ICE_CREAM_SHOP, SMOOTHIE_SHOP} → clone beats champion in 87 games at +12,001 mean (winner rate 0.98); otherwise 111 games at −3,658 (0.38). Mechanically confirmed: the engine reseeds its end-of-day RNG per day from one shared seed, so season shop draws are correlated (synthetic 20,000-seed test: 3.63 vs 2.63 milk shops per season); MILK rises 175 → 261 by day 29 in the triggered group and collapses to 76 by day 20 otherwise.
- Standing: signal question answered YES, no promotion. A clone-splice selector is impossible by construction (scale opening commits capital days 0–2; signal exists from day 3), so an adaptive selector can only stage expansion. Final current-day Kaggle slot held; no submission while no strict improvement exists.
- Superseded exp-0041 details (clone retained as a regression opponent): reconstructed from replay 110927326 (Jared Wilder 65,074 vs our 16,206); public seed 60,079 mean; dev 4182–4191 vs champion 10–10 (median −1,348); regression 5080–5082 26–4 overall (median +15,465).

## Current priorities

1. Add the 2c2s2g champion, 2c2s, fertstraw, berry, fert-cow, melon stop-19, expansion-melon, and cow-base to all future regression panels. Seeds 4040–4049, 5020–5029, 4050–4064, 4070–4181, 5030–5109, and 4182–4201 are now touched; next promotion checks start at 5110. Scheduler hybrid (branch exp-0040) rejected: ferry livelock, scheduler line parked. Scheduler prototype (branch exp-0039) parked: robust but −750 vs champ; scale-up deferred. Wool module (branch `exp-0035`) promoted on strict dominance (46-0 paired). Gated hybrid (branch `exp-0034`) archived: valid shop signal, persistent skip subgroup. Geese probe (branch `exp-0029`) superseded by the promoted 4th-hand design (branch `exp-0030`). NE scale-up (branch `exp-0031`) rejected: unlock-night weed clusters + deadline fragility, Gate A missed at 46.9k. Readiness variant (branch `exp-0032`) rejected: +5k ceiling. Bought-feed + early-straw2 (branch `exp-0033`) lateral 10-10 vs champ, viable but not superior; slot preserved. Carrot module (branch `exp-0036`) rejected 0-10: early capital contention delays planting to day 11 (~15 units, negative net); tile-overlap bug found and fixed separately (+5.7-7.2k on trigger seeds, promotion track TBD). Jared Wilder clone (exp-0041) validates scale hypothesis on public seed (60k vs 43k) but lacks adaptive logic for general seeds; diagnostic probe only. exp-0042 (2026-09-20) screened the early-signal gate question: the day-3 first unlock causally predicts the regime (clone wins 98% of 87 games at +12,001 mean when the first shop consumes milk, 38% of 111 at −3,658 otherwise; mechanism verified at the engine RNG level), but no gate was implemented and nothing was promoted because a clone-splice selector cannot retro-fit an opening that commits capital on days 0–2. Analysis tooling `analysis/pair_scan.py` and `analysis/gate_eval.py` is committed and should front every future demand-signal probe.
2. Milk-gate (branch `exp-0020`), tuning probes (branch `exp-0022`), 8-tile probe (branch `exp-0023`), 4-cow probe (branch `exp-0025`), hand-3 roster (branch `exp-0026`), scale imitation (branch `exp-0027`) all retained as measured rejections.
3. H2 carrot conversion retired (stale premise: no melon in our regime since exp-0019). Open probes, each bounded one-file with paired dev gates: stopmelon-loss diagnosis (only opponent taking games, 6–4), strawberry-plot edge cases, expansion pressure. Prefer `z-ai/glm-5.3-flashx` for review; `qwen/qwen3.8-max` blocked once (10 min, zero output) and `z-ai/glm-5.3-flash` blocked once — record per-model routing evidence.
4. Keep DeepSeek H2 (contested-melon→carrot at replant boundary) queued behind demand-variance work; the champion already sidesteps melon pools by construction.
5. Prefer `z-ai/glm-5.3-flashx` over `z-ai/glm-5.3-flash` for review tasks (flash blocked 7+ min with zero output; flashx returned a CLEAN verdict with 2 nits in minutes). 2026-09-20 routing evidence: `z-ai/glm-5.3-flash` answered a trivial headless prompt instantly ("READY") but produced zero bytes on a bounded 900 s read-only review of analysis/pair_scan.py + docs + engine source, so it remains unusable for review; `meta/muse-spark-1.3-contributor` is listed as available for implementation review and is the next reviewer to try.
6. Keep field-size and sell-timing probes archived; both are resolved.

## Important commands

```bash
uv sync
uv run python -m unittest discover -s tests -v

# Determinism audit
uv run python -m simulation.tournament \
  --candidate main.py \
  --opponent carrot=agents/deterministic_carrot.py \
  --seed 20260919 \
  --repeats 2 \
  --workers 4 \
  --replay-policy all \
  --output-dir experiments/runs/determinism

# Paired opponent panel
uv run python -m simulation.tournament \
  --candidate main.py \
  --opponent pass=agents/deterministic_pass.py \
  --opponent wheat=agents/deterministic_wheat.py \
  --opponent carrot=agents/deterministic_carrot.py \
  --seeds 1000-1049 \
  --workers 4 \
  --output-dir experiments/runs/panel

# Engine-derived economic snapshot
uv run python -m analysis.economics
```

## Known issues

- One isolated Python process per match gives good crash containment but startup dominates runtime.
- Existing promotion evidence used a crop-only panel. Worker/animal and expansion/market-pressure opponents now exist for future panels, but adaptive opponent-aware behavior remains missing.
- Kaggle does not publish an immutable evaluator image lock; server parity needs later validation.
- The built-in `random` agent is not deterministic from the episode seed.
- Exact-file self-play can force identical stochastic trajectories. Use it for repeatability checks, not as evidence of strategy strength or seat balance; competitive comparisons must use distinct candidate files and both seats.
- Command Code 1.58.0 headless execution is verified for both a synthetic read-only DeepSeek task and a Kimi implementation in an isolated Herdr worktree. On this installation, headless writes required `--yolo --tools-all`; `--auto-accept --tools-all` remained read-only. Use only inside disposable worktrees and review every diff before cherry-picking.
- Herdr remains on 0.7.4; automation must follow installed help rather than current 0.9.1 documentation.

## Next recommended task

exp-0043b REJECTED at the dev gate 2026-09-20 (10–10 vs champion on
4302–4311, median −322.5; see RESEARCH_LOG/DECISIONS). Candidate archived at
`agents/deterministic_goose4_eggcond_hand.py`. exp-0044 PROMOTED 2026-09-20
(merge 18e3a9f): dev regression 140-0 (4331-4340), holdout 20-0 (5120-5129).
Seed ledger: dev seeds 4312-4314 (smoke), 4315-4330 (dev gate), 4331-4340
(regression x2), 4341-4347 (determinism/invariant audits), and holdout
5120-5129 are now spent; fresh holdouts start at 5130 (11 remain);
next dev checks start at 4348.

Ranked next options (bounded, single-file, inside the champion's
architecture):

1. Scale-shaped work stays the objective (server field winners 44–65k vs our
   30–45k). The exp-0041 clone validated that 60k+ seasons exist on the
   public seed; the missing piece is a general-seed opening, not a gate
   (exp-0042 showed a day-3 selector cannot retro-fit a days-0–2 opening).
2. exp-0043c (small, cheap): re-gate the archived goose2 pair on the
   champion's own roster state — build/buy only when the YARN sheep2 pair is
   behind schedule at day 9 — verified +1.4–1.8k on the 4307–4311 regime and
   byte-identical elsewhere. Expected +~1.5k on a seed subset; a dev gate on
   4312+ settles it in one run.
3. Kaggle slot decision for the exp-0043a artifact is still open (validated
   strict improvement locally; needs a separate submission call; four slots
   remain).

Supporting tools: `analysis/pair_scan.py` (compact per-day signal scanner, no replay bodies) and `analysis/gate_eval.py` (per-game gate evidence with Wilson intervals and oracle regret). Use them for every future demand-signal question before writing agent code — the day-3 unlock is now a measured, causal read on the season's demand composition.

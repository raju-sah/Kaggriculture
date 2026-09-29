# Decisions

## 2026-09-19 — Pin the official environment

Use `kaggle-environments==1.32.7` for local evaluation. Its Kaggriculture documentation matches the competition download byte-for-byte, and its environment sources matched current upstream during discovery. Record fingerprints because Kaggle does not publish an immutable evaluator lock.

## 2026-09-19 — Use paired seeds and seat swaps

Every comparison must run both player assignments for each environment seed. Player order affects market processing and the mapping of seeded random events, so an unpaired result can confuse strategy strength with seat effects.

## 2026-09-19 — Keep M0 deterministic and isolated

Run each match in a subprocess, repeat both seat assignments, and compare normalized replay hashes. Do not use the built-in random agent as a determinism oracle because it owns an unseeded random generator.

The Kaggle framework adds a fresh top-level replay `id` UUID on every run. M0 normalization removes only this field. Raw replay hashes are retained separately for artifact integrity.

## 2026-09-19 — Defer orchestration infrastructure

Herdr upgrades, Command Code workers, SQLite, Jev, automatic promotion, and Kaggle submission are outside M0. They must not gate establishment of a trustworthy local simulator.

## 2026-09-19 — Use four isolated match workers

Run one game per Python subprocess for reliable crash and state isolation, with four concurrent workers on the current 4-core/8-thread, 12 GiB machine. During the first 102-game panel, available memory remained about 4.1 GiB. Process startup is currently the main throughput cost, but reliability is more valuable until tournament volume becomes a bottleneck.

## 2026-09-19 — Retain full replays selectively

Keep result records, hashes, action counts, and logs for every game. Retain full replay bodies for errors by default, with explicit `all`, `losses`, and `none` policies. A 102-game all-replay run consumed about 409 MiB, which would scale poorly.

## 2026-09-19 — Establish carrot as the initial champion

Promote the deterministic single-tile carrot loop to root `main.py` after a 102-game panel produced 68 wins, 0 losses, and 34 self-play draws across 17 seeds and both seats. Carrot beat wheat 34–0 and pass 34–0 with no errors or seat discrepancy. This creates a reproducible engineering baseline, not a claim of competitive strength.

## 2026-09-19 — Promote the eight-tile carrot route

Replace the single-tile champion after the multi-tile candidate went 34–0 against it, 34–0 against wheat, and 34–0 against pass across 17 paired seeds. It also drew all 34 self-play games, had no errors, showed identical results by seat, and passed an eight-game exact-repeat audit. Keep the source candidate under `agents/` so the promoted submission can be reproduced.

This promotion is strong relative to the local panel but says little about leaderboard strength because the non-self opponents remain simple baselines. The next work must diversify opponents rather than merely inflate the seed count against already dominated agents.

## 2026-09-19 — Restrict the meaning of exact-file self-play

Use an agent against the exact same file only to test repeatability. In a parity diagnostic, byte-identical copies drew while behaviorally equivalent files with different source hashes followed different player-specific stochastic paths and split wins by seat. Therefore self-play draws do not establish seat neutrality or competitive robustness. All strength comparisons continue to use distinct candidate files, paired seeds, and both seat assignments.

## 2026-09-19 — Diversify the panel with melon and mixed routes

Add an all-melon route and a carrot/melon mixed route on the champion's field skeleton as panel opponents. Both beat the eight-tile carrot champion 34–0 across 17 paired dev seeds with no errors, and melon beats mixed 34–0 in the reciprocal panel. Seeds 4000–4016 are now touched development seeds; seeds 5000 and above stay reserved for holdout promotion checks. Promotion of any candidate still requires paired evidence on seeds the candidate was not tuned against plus regression checks by opponent.

## 2026-09-19 — Promote the eight-tile melon route

Replace the carrot champion after the melon route went 20–0 against it, 20–0 against mixed, and 20–0 against wheat/pass across 10 untouched holdout seeds with symmetric seats and no errors, backed by 102–0–0 on dev seeds and a clean eight-game repeat audit. Keep the source candidate under `agents/` so the promoted submission can be reproduced. The panel is still deterministic single-route agents, so this is an engineering champion, not leaderboard evidence. Next promotion checks must use fresh holdout seeds at 5010+.

## 2026-09-19 — Promote the stop-plant melon route

Replace the melon champion with the day-19 stop-plant variant after a direct 20–0 holdout comparison against the previous champion on seeds 5010–5019, with median coin difference +720 and no errors. The remaining 80 holdout games against weaker crop/pass baselines are regression checks rather than independent evidence for the incremental change. Dev evidence was 33–1 against the previous champion, including one −428 weed-divergence loss, and the repeat audit was clean. Next promotion checks must use fresh holdout seeds at 5020+.

## 2026-09-19 — Verify Command Code without sharing project material

Use the installed Command Code 1.58.0 headless CLI rather than assuming Provider API access. Discover model IDs with `--list-models`; the current catalog includes DeepSeek, Kimi, Qwen, GLM, and GPT-5.6 Luna. The initial smoke test used `deepseek/deepseek-v4-flash` at its CLI-reported supported `high` effort from `/tmp`, with no tools, no skills, no persistent session, plan permissions, one turn, and a synthetic JSON-only prompt. This proves the transport and structured-output path without sending competition code or data. Code-writing workers must later run in isolated Git worktrees.

## 2026-09-19 — Retain the hired-hand cow policy as an opponent

Keep `agents/deterministic_cow_wheat_hand.py` as the first stable worker/animal regime, but do not promote it. Its first four-cow design collapsed to 41 coins because feed shortages caused 13 cow purchases in an escape/rebuy loop. A bounded revision with two cows, three wheat tiles, one daily hand, startup feed, and no rebuy after day 0 scored 16,890.7 mean coins and went 2–8 against the champion over five paired dev seeds with no errors. Its different labor and product-market exposure makes it useful for regression testing despite the losing aggregate record.

## 2026-09-19 — Require disposable worktrees for Command Code writes

The first Kimi implementation experiment used Herdr branch/worktree `exp-0018-kimi-expansion`. In Command Code 1.58.0, `--auto-accept --tools-all` still exposed a read-only session; `--yolo --tools-all` was required for the model to write. Permit that mode only inside a disposable isolated worktree with a one-file task, inspect scope before committing, and cherry-pick only a reviewed commit. The main working tree must remain single-owner.

## 2026-09-19 — Retain the expansion policy as a market-pressure opponent

Keep Kimi's reviewed `agents/deterministic_expansion_melon.py` as an opponent, but do not promote it. It buys the NE quadrant immediately, expands from eight to twelve melon tiles, and scored 22,920 against pass. Against the melon champion it fell to 16,009.7 mean coins and lost 0–10 on five paired dev seeds, with median difference −1,244 and no errors. The collapse under same-product competition makes it useful for market-pressure regression testing even though it is weaker head-to-head.

## 2026-09-19 — Hold fert-cow promotion pending a fresh holdout

(Superseded by the promotion below; kept as the staged-gate record.) Keep `agents/deterministic_cow_fert_hand.py` (branch `exp-0019`) as a dev-stage candidate until a 5020+ holdout gate passes.

## 2026-09-19 — Promote the fertilizer-collecting cow/hand champion

Replace the melon stop-19 champion after the fert-cow policy went 16–4 against it on untouched seeds 5020–5029 (both seats, symmetric, median positive, no errors) with the champion invariant at exactly 21,201 in every game, backed by a 47–3 holdout regression (10–0 cow-base/mixed/strawberry/pass, 7–3 expansion), 18–2 dev evidence, a clean determinism audit, and a CLEAN GLM `z-ai/glm-5.3-flashx` review (2 economic nits, no material issues). Cherry-picked single-file commit `869c072` as `f4852a9`; `main.py` carries identical logic with a champion docstring, verified by a coin-for-coin re-run of the 5020–5024 direct games. Losses are seed-symmetric demand draws, not errors. Keep the stop-19 melon route under `agents/` as the melon-regime opponent. Next promotion checks start at seeds 5030.

## 2026-09-19 — Promote the conditional-strawberry cow champion

Replace the fert-cow champion after the berry policy went undefeated against it across 30 paired dev+holdout games (dev 6–0–4 on 4070–4074; holdout 10–0–10 on untouched 5030–5039, median +1,140.5, symmetric seats, no errors), flipped all three diagnosed low-milk loss seeds 4046/5021/5024 (6–0, +3.1k to +6.0k), and swept a 60-game holdout regression 56–4 (10–0 vs cowbase/mixed/strawberry/pass/stop-melon; 6–4 vs expansion at the previous champion's own level), with a clean determinism audit. Draws reflect different-file RNG divergence, not weakness: the decisive record is 16–0. Cherry-picked single-file commit `8f87c6b` as `41bc803`; `main.py` carries identical logic (docstring only differs), verified by a coin-for-coin re-run. GLM reviews were twice inconclusive on this experiment (turns-exhausted, early-exit) and are recorded as non-approvals; verification rested on supervisor diff review (which caught and fixed a real hour-0 HIRE bug) plus simulation. Keep fert-cow under `agents/` as a regression opponent. Next promotion checks start at seeds 5040.

## 2026-09-19 — Promote the fertilized-strawberry cow champion

Replace the berry champion after the synergy policy went undefeated against it across 30 paired dev+holdout games (dev 4–0–6 on 4096–4100; holdout 10–0–10 on untouched 5040–5049, median +1,066, symmetric seats, no errors), with synergy verified live in replays (8 applications covering 16 productions via the 3-day effect window; trigger seeds +2.9k/+3.1k, non-trigger draws identical), plus a 58–2 holdout regression (10–0 vs cowbase/mixed/strawberry/pass/stopmelon — stopmelon threat fixed from 6–4; 8–2 vs expansion) and a clean determinism audit. GLM `flashx` review was inconclusive (early exit, no vendored engine in worktree); verification rested on supervisor diff review plus simulation. Draws reflect different-file RNG divergence; decisive record is 14–0. Cherry-picked single-file commit `bd4d4b0` as `7d20a48`; `main.py` carries identical logic (docstring only differs), verified by a coin-for-coin re-run. Keep berry under `agents/` as a regression opponent. Next promotion checks start at seeds 5050.

## 2026-09-19 — Promote the 2-cow/2-sheep foundation champion

Replace the fertstraw champion after the 2c2s policy went 20–0–0 against it on untouched seeds 5050–5059 (both seats, Wilson 83.9%–100%, median +11,359, no errors), backed by 40–0–0 dev (4112–4116, mean 37.2k, zero escapes, continuous sells), a 70–0–0 holdout regression across 7 opponents, and a clean determinism audit — 130–0 combined with no errors. The wool stream (+~7k net of 1,060 capital/hire) is robust at 2-sheep scale (cannot glut: max Δ+35). Cherry-picked single-file commit `ce62897` as `8407e6c`; `main.py` carries identical logic (docstring only differs), verified by a coin-for-coin re-run. Supervisor implemented and reviewed locally (model quota blocked; documented bypasses). Submission of this artifact is authorized once a slot is coordinated. Keep fertstraw under `agents/` as a regression opponent. Next promotion checks start at seeds 5060.

## 2026-09-20 — Promote the 2c2s2g exclusive-geese champion

Replace the 2c2s champion after the geese policy went 20–0–0 against it on untouched seeds 5060–5069 (both seats, Wilson 83.9%–100%, median +3,539.5, no errors), backed by 40–0–0 dev (4122–4126), a 70–0–0 holdout regression across 7 opponents, and a clean determinism audit — 130–0 combined with no errors. The fourth hand's productivity is proven live (58 wool + 61 eggs with bonuses vs 10/31 unsplit; zero rebuys). Dev pass-mean 42.1k missed the aspirational 45k target but the gate's substance (material lift, productive hand, zero failures) passed. Cherry-picked single-file commit `7c3483a` as `ee0b3fd`; `main.py` carries identical logic (docstring only differs), verified by a coin-for-coin re-run. Supervisor implemented and reviewed locally (model quota blocked twice; documented bypasses). Submission of this artifact is authorized once a slot is coordinated. Keep 2c2s under `agents/` as a regression opponent. Next promotion checks start at seeds 5070.

## 2026-09-20 — Promote the YARN-triggered wool module champion

Replace the 2c2s2g champion after the wool policy went 20–0–0 against it on untouched seeds 5080–5089 (both seats, Wilson 83.9%–100%, median +900.5, no errors), backed by 26–0 dev (4147–4166) with the trigger validated live on 4 in-matchup seeds (+4.2k median, no losses) and non-trigger subgroups never negative, plus a 70–0–0 holdout regression across 7 opponents and a clean determinism audit — 136–0 combined with no errors. Strict dominance (never lost in 46 paired games) carried the promotion over thin median. Cherry-picked single-file commit `2617c06` as `8313139`; `main.py` carries identical logic (docstring only differs), verified by a coin-for-coin re-run. Supervisor implemented and reviewed locally (model quota blocked; documented bypasses). Submission of this artifact is authorized once a slot is coordinated. Keep 2c2s2g under `agents/` as a regression opponent. Next promotion checks start at seeds 5090.

## 2026-09-20 — Jared Wilder clone (exp-0041): scale probe, not promotion

Staged reconstruction of public opponent Jared Wilder from ignored replay `experiments/kaggle/submission-56368891/episode-110927326-replay.json` (seed 1003439700, 65,074 coins). Exact day/hour capital, hires, land, purchases/placements, cash, first sales, and fixed worker ownership reconciled. Built guarded scripted clone with fixed exclusive roles (farmer=planter/builder/ferry; hands 1-3=cow zones; hands 4-5=sheep zones; hands 6-7=goose zones; hands 8+=wheat), hard feed/care, one planter, cash preconditions, continuous selling, no rebuys. 8 cows, 8 sheep, 4 geese, 9 hands, NE land day 10.
Public seed gate (1003439700, both seats, 4 workers, 0 errors): 60,079 mean (≥55k gate PASSED), zero failures.
Dev seeds 4182–4191 vs pass (20 games): 39,708 mean; vs champion (20 games): 10–10, median −1,348; seat-symmetric.
Regression panel (seeds 5080–5082, 5 opponents, 30 games): 26–4 overall (86.7%); beats champ 5–1, expansion 6–0, fertcow 6–0, pass 6–0; splits 3–3 vs 2c2s2g; median +15,465.
Verdict: scale probe validates SCALE hypothesis (60k on public seed vs champion's 43k); general-seed performance (40–44k) trails champion's adaptive logic (45k). Not a promotion candidate — diagnostic probe only. Retained at `agents/deterministic_jared_wilder_clone.py` for regression coverage. Next promotion checks start at seeds 5110.
## 2026-09-20 — exp-0042: early-signal gate screened (no promotion); day-3 unlock is a causal seed-level demand read

The staged scale clone (exp-0041) loses on general seeds as an aggregate −1,348
median, but paired data shows the effect is bimodal, not a shift. Paired
clone-vs-champion games were collected with a new compact scanner
(`analysis/pair_scan.py`, sampled public state only, no replay bodies; 198 games,
both seats, four workers, zero failures) and evaluated per game with
`analysis/gate_eval.py`.

Finding: the first town unlock, public from the start of day 3 and before any
post-opening capital commitment, predicts the regime. If the first shop is a
milk consumer (PIZZA/ICE_CREAM/SMOOTHIE), the clone wins 98% of 87 games with a
+12,001 mean; otherwise it wins 38% of 111 games with a −3,658 mean. This is not
a behavioural artefact of our own agents: the engine reseeds its end-of-day RNG
per day from one shared seed, so the season's shop draws are correlated, and a
direct synthetic test (20,000 seeds, 30–46 consumed draws per unlock) reproduces
the association (3.63 vs 2.63 milk shops per season). The economics match: on
d3-milk games MILK rises 175 → 261 by day 29, on others it collapses to 76 by
day 20.

Decision: the signal is real and usable, but no gate was implemented and nothing
was promoted. A "switch to the scale program" selector cannot work as designed
because the clone's opening commits capital on days 0–2 while the signal appears
only on day 3; a selector can stage expansion from day 3 onward but cannot
retro-fit an opening. The final current-day Kaggle slot is therefore held:
`main.py` (exp-0035) remains the best validated artifact and no candidate is a
strict improvement. Next experiment is pre-registered as exp-0043 (strawberry
capacity expansion with a second dedicated plot hand) with the gate criteria
recorded in `docs/RESEARCH_LOG.md`. Fresh holdout seeds still begin at 5110.

## 2026-09-20 — exp-0043b goose expansion rejected at the dev gate

Second goose pair on GOOSE2_COOPS=((0,0),(1,0)), gated on a day-9
EGG-consumer trigger (BAKERY/BRUNCH_SPOT), went 10–10 vs the champion on dev
seeds 4302–4311 (median −322.5, mean −987.7, both seats, 4 workers, 0
errors). The trigger fired on 10/10 seeds and separated nothing. Replay- and
action-count-verified mechanism: the pair is +1.4–1.8k only where the
champion's own YARN sheep2 pair missed its money floor (behind-schedule
regime: champ 6 buys), −1.2k to −5.8k where the full 2c4s2g roster funded
(+19 hires, 15 fewer sells, a knock-on 5th sheep), and the hire ladder alone
costs −647 when the GOOSE+100 floor blocks the buys (seed 4305). Public
shop-signal gates (egg6/egg9, d3 unlocks) do not separate the regimes on the
4302–4311 scan. Candidate archived at
`agents/deterministic_goose4_eggcond_hand.py` (sha256
`1966295fa3503429985b3f3d7e5251de47e4a6e1af492a6956fcbd2367773552`). No
holdout spend: 5120+ preserved. Dev seeds 4302–4311 touched; next dev checks
start at 4312. exp-0043c pre-registered as the roster-state-gated
single-variable variant, ranked below scale-shaped work.

## 2026-09-20 — exp-0043c/d goose line CLOSED; pivot to top-replay reconstruction (exp-0044)

exp-0043c devgate2: 16W-4L-20D, mean +432 but the pre-registered latch
invariant was violated (4327 seat 1: partial module, seat-dependent
activation) and all four losses traced to seat-mirror ±100 cash knife-edges
plus late activation. exp-0043d fixed the latch (COOP-kind marker, weed DIG
duty, verifier alignment corrected: steps[i].action derives from obs[i-1]),
pre-trigger identity proven (1,728 decisions, 0 mismatches), cow care demoted
correctly above goose slack — and the targeted collapse gate STILL lost all
six games (−9.0k..−13.5k, module fully completed). Conclusion: the far-NW
days-10-11 goose2 module is negative even when executed perfectly; its cost
is farmer-day displacement of the day-10/11 sell/restock loop, which
compounds through the milk/strawberry engines. Per Codex gate decision the
entire goose line is closed. Candidate archived at
`agents/deterministic_goose2_latch_slack_care.py` (sha256
`8c9167efd5e6412a877392435afade1ff5169ce678a04950ec59740e9cba33cc`). 5120+
holdout preserved (20 seeds untouched).

New priority from public top-1/top-2 replay evidence (5 episodes, both
agents, exact opener identical in all 10 seats): day0 all-in opener — t1 BUY
COW1 + BUY WHEAT5; t2 PICKUP COW, SELL WHEAT1, HIRE x4, BUY COW1 + SHEEP3;
t3 BUILD_PASTURE + worker pickups + SELL WHEAT1; day0 ends at ~$5 with 2
cows, 3 sheep, 4 hands, 5 pastures, 16 planted tiles (10 wheat + 6 melon).
Top agents reach 100k+ vs our 45k ceiling via 2nd/3rd land day6/day9, 8-11
hands, and large strawberry/carrot/tomato rotations. exp-0044 = exact staged
opening reconstruction with monotone build/place/feed/care ownership.
Milestone 1 only: reproduce day0/day1 without stranded inventory, escapes,
rejected plants, or cash deadlock on fresh dev seeds, both seats, vs
champion. Land expansion only after opener stability. Evidence and plan:
`docs/TOP_REPLAY_ANALYSIS.md` + `analysis/public_replay_profile.py`
(cherry-picked from analysis/top-replay 47b916d).

## 2026-09-23 — Promote the NE-expansion champion (exp-s2, S1)

Add exactly one scale step to exp-0044: BUY_LAND NE days 7-11 (2200 coin guard), four shed-belt pastures (5,3),(5,4),(6,3),(6,4), herd to 4 cows, +1 hand while expanded. Replay-backed: ladder winners (Sarthak 48.9k, Alex 50.2k) expand d7-11 and herd 7-8 cows; our 47-60k local band left scale on the table. Rejected alternative same night: bridge-timed goose2 re-gate (exp-0043c) went 1-5-14 twice on 4350-4359 (symmetric -1k: late pair-2 cannot pay back 600 capital + hire + wheat-tile loss); archived as measured rejection, not promoted.

## 2026-09-23 — Promote the SW-expansion champion (exp-s3, S2)

Second sequenced scale step: SW d11-15 after NE (4000 guard), belt
(3,5),(4,5),(3,6),(4,6), herd to 6, +1 hand. Combined 108-2 across
smoke/dev/regression/holdout. 4386-s0 loss diagnosed as opponent-seat
overperformance via replay probe, not a candidate defect.

## 2026-09-23 — Promote the 3C2S animal-forward champion (exp-3cow, S3)

(4,3) converts sheep->cow in the bridge opener; day-0 ladder buys 3C2S
(-100 net vs 2C3S). Milk+fert compounding from d1. Combined 108-2 across
smoke/dev/regression/holdout. 4395 outlier (-2.5k symmetric) did not repeat
in 15 fresh gate seeds.

## 2026-09-23 — Promote the straw-late scale champion (exp-s5, S4)

12-tile late-strawberry field on expansion land (plant d9-16, ongoing crop
no decay), +2 hands, SELL strawberry, hires-first market reorder (10-order
cap was truncating HIREs). Path: 91.6k ladder replay (mass straw d10-12).
Two measured failures en route: uncapped-24 labor drown (-27k), missing
consts (fallback all game). Combined 110-0.

## 2026-09-23 — Promote the +1 hand champion (exp-s9, S5)

BRIDGE_HANDS_TARGET 5->6 (one line). Elites run 9-10 hands from day 9;
labor (~30 coins/day) was the binding constraint on water/harvest
parallelism. Combined 110-0, strongest margins yet (min +4,615).

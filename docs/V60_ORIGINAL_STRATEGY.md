# V60 original state-responsive strategy research

## Evidence and provenance

This note uses four public Kaggriculture episode replays already retrieved through the official Kaggle CLI: `kaggle competitions episodes <submission_id>` followed by `kaggle competitions replay <episode_id>`. They are episode 113508987 (Boey–Vadim), 113508988 (DSM–M & M & P & Q), 113508989 (mtmr_s1–DECEM), and 113507961 (M & M & P & Q–Unknown Mother-Goose). In the 2026-09-26 11:39 UTC official leaderboard refresh, Boey, M & M & P & Q, DSM, DECEM, Unknown Mother-Goose and Vadim were all in the top ten. Episode replays are publicly accessible for viewing/analysis through Kaggle; the [official competition page](https://www.kaggle.com/competitions/kaggriculture) and [official replay instructions](https://www.kaggle.com/competitions/kaggriculture/overview/citation) document the competition and replay CLI workflow.

The compact state profiles are [`elite_profiles.json`](../experiments/v58_elite/elite_profiles.json). The frozen baseline profiles are [`v57_proxy_profiles.json`](../experiments/v58_elite/v57_proxy_profiles.json), generated for [`v57_agent.py`](../agents/v57_agent.py) across 18 games (three seeds, three replay-derived opponents, both seats). Its file SHA-256 is `6b2e3ace3b9d500047e9ae8f2da4fd7729cf65f2f29b16315a2b8aa1b476ba59`. Public replay SHA-256s:

| Episode | Replay SHA-256 |
|---:|---|
| 113508987 | `2f82968a73b6b616645d841cd1d5d9f5722f450e8a59a199fa996792003368f8` |
| 113508988 | `1b6be94632fbe56de2c6f3e5d13c7604ad6f06e630be6c594211fff3ad824a6a` |
| 113508989 | `5179fbfa17b539535b75b1e02ef3cf7277c3cd7ab7b93621f579d0bb6de65bcf` |
| 113507961 | `de4c61aea51e4478e8464c40a2d14b4f1fc069d07ec57b42165ffb0f093052ea` |

Raw replay files remain in the participant workspace under `experiments/v58_elite/replays/` and are gitignored. The comparisons below summarize visible replay states; they do not use a replay action tape as a policy, nor do they claim causal or rating performance.

## Early investment and worker throughput comparison

At the sampled checkpoints, the median public leader had 9 hands and 2 land quadrants by day 6, then 10 hands/3 quadrants by day 9 and 11 hands/3 quadrants by day 12. Frozen v57's medians across its 18 local proxy games were 7/2, 8/2 and 9/3, respectively. At day 20, v57 had expanded to 13 hands/4 quadrants, compared with sampled public median 12/3. The profiles therefore suggest an **earlier** throughput ramp and earlier third-quadrant unlock among the leaders, not that v57 needs higher terminal headcount or more total land.

| Checkpoint | Public leader traces (n=7 player-episodes) median hands / quadrants | Frozen v57 traces (n=18) median hands / quadrants | Public median wheat / strawberry plots; v57 median |
|---:|---:|---:|---|
| Day 0 | 4 / 1 | 5 / 1 | Wheat 10 / 8; strawberry 0 / 0 |
| Day 6 | 9 / 2 | 7 / 2 | Wheat 3 / 6; strawberry 21 / 12 |
| Day 9 | 10 / 3 | 8 / 2 | Wheat 19 / 5; strawberry 24 / 20 |
| Day 12 | 11 / 3 | 9 / 3 | Wheat 24 / 24; strawberry 28 / 33 |
| Day 20 | 12 / 3 | 13 / 4 | Wheat 29 / 25; strawberry 20 / 33 |

The public median points to investment reallocation, not universal copying of one herd or crop mix. For example, Boey had 3 quadrants/10 hands on day 9 and later sold high accepted wheat volume; DSM and DECEM expanded cows/sheep differently. The sampled leaders spend down close to zero cash immediately after early hires/land purchases in several traces, so a fixed aggressive buy schedule also risks running out of operating cash. Snapshot money and crop counts are available in the profile JSON.

**Capacity scale, not a coin forecast:** the day-6 to day-12 median headcount difference is two workers. If two additional hands were hired early enough and remained active for those six days, the theoretical ceiling is about **288 extra hand-turn opportunities** (2 hands × 6 days × 24 turns/day). This is an upper-bound action-capacity estimate, not 288 productive actions or a projected revenue increase. The public and local worlds differ in opponent and shop sequence, and the 7 public player-episodes include M & M & P & Q twice; outcomes cannot isolate the impact of hiring. In the separate accepted-sales audit, Boey's public episode accepted 5,386 units / $261,207 gross while one local v57 reset/proxy trace accepted 1,738 / $174,268. The latter match has different shops and opponent and is only a scale reference, not evidence that early hires would close the $86,939 difference. See [`V58_ELITE_RESEARCH.md`](V58_ELITE_RESEARCH.md) and [`market_audit_summary_2026-09-26.json`](../experiments/v58_elite/market_audit_summary_2026-09-26.json).

## Original architecture to test

Build an observation-driven hierarchical planner with four cooperating parts:

1. **State and cash ledger.** Recompute available cash, hands, unlocked land, working crop/animal capacity, inventory, prices and visible shop demand from each current observation. Track hires already issued that day in the agent state for their escalating same-day cost. Keep only short-lived reserve variables for near-term feed, seed and wages; never use a seed, episode ID or hidden future shop schedule as a lookup key.
2. **Capacity investment gate.** Evaluate each available hire or quadrant buy by whether it unlocks productive parallel work before the next income event. Prioritize moving toward a useful 9–10 hands / third quadrant around days 6–9 only when cash and task backlog support it. Preserve enough operating cash for feed and planting, and defer hires that have no reachable productive job. Use measured action availability per turn as the test metric; the raw hand count alone is insufficient.
3. **Adaptive production portfolio.** Score candidate crop/herd activities from current shop demand, market price/inventory, time-to-yield, marginal expected price impact, required worker turns, seed/feed cost, and remaining season. Allocate open plots and hands to the best marginal return with a wheat/fertilizer throughput option, while allowing strawberry/milk or other routes to dominate when live demand and prices justify them. Add hysteresis to avoid changing route on one noisy quote.
4. **Feasibility and liquidation guard.** Convert the macro targets to routes from current positions and storage. Ensure orders respect the 10 market-order-slot cap, avoid shed overflow and no-op actions, and submit sales only when the expected proceeds beat inventory's future value. This separates action execution from strategic choice and can be ablated independently.

The hypothesis is narrow and testable: move available worker capacity forward by roughly two hands during days 6–12, while funding it from actual income and placing the third quadrant only when it enables work. The candidate gain to look for is increased useful action rate and accepted product throughput before day 12, not merely higher final land/headcount. The public traces quantify available capacity; they do not establish how many extra coins the policy can earn. No new match seeds or games were run for this note.

## Rules, licenses, and scope boundary

The [official competition rules](https://www.kaggle.com/competitions/kaggriculture/rules), fetched through Kaggle PageService on 2026-09-26 and recorded in [`source_manifest.json`](../experiments/v58_rights/source_manifest.json), say replays can be public/downloadable (Rule 2.11), but the same rules require an original submission with rights to grant its required licenses (Rule 3.14) and limit redistribution of Competition Data to non-participants (Rule 2.4(b)). Kaggle's [official environment repository](https://github.com/Kaggle/kaggle-environments) is Apache-2.0 licensed; the installed local engine is `kaggle-environments==1.32.7`. Kaggle notebook authors' Apache notices apply to their licensed code components and do not automatically grant rights in a third party's replay action sequence. The official [`kaggriculture.py`](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/kaggriculture.py) defines the worker-cost Fibonacci sequence, land purchase ladder, crop and animal production timing, shop demand, and market behavior; [`kaggriculture.json`](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/kaggriculture.json) defines observation/action limits and turn settings. The repository's detailed assessments are [`V58_REPLAY_RIGHTS.md`](V58_REPLAY_RIGHTS.md) and [`V58_LICENSED_BASELINES.md`](V58_LICENSED_BASELINES.md).

Accordingly, this architecture is derived from general economic behavior, current observations, and the published engine mechanics. It excludes literal 719-turn schedules, replay medoids, seed/episode-indexed routes, and copied third-party tape code. This is a conservative provenance boundary, not legal advice. No code was copied from another participant and no submission was made.

# v58 original second route study

## Result

No-go for competition use. This route is an observation-conditioned worker planner, but its economy is too small and its animal placement pipeline fails to turn purchases into production. It never beat any of v50, v53, or v54 in two small fresh-seed screens. It is not credible top-ten readiness evidence.

The standalone callable is [original_second_candidate.py](../experiments/v58_original_second/original_second_candidate.py). It was run through the repository tournament worker, which loads agent files using Kaggle Environments' normal path; all 54 runs completed without an agent or worker error. The entrypoint accepts the Kaggle observation and returns `farmer`, `hands`, and `market` actions. The candidate builds tasks from the current farm tiles, carried inventories, shed stocks, money, unlocked quadrants, and current day. It repairs feeding, care, planting, watering, harvest, construction, and collection tasks from live state rather than indexing a full replay action sequence.

The implementation was copied from the repository's existing handwritten `agents/exp3cow_3c2s.py` bridge and then modified in this study to fetch expansion livestock after day 2. Its startup footprints and capital plan are fixed constants and the implementation comments cite a public opener pattern. Therefore this study does not claim a new route lineage or resolve replay-rights questions; it is a useful failure diagnosis for the observation-derived planner family.

## Tournament evidence

The first screen used seeds 94500–94502, both seats, versus v50, v53, and v54 (18 games). The candidate went 0–6 against each opponent, with mean coin margins of −$103,865 vs v50, −$103,763 vs v53, and −$97,488 vs v54. There were no runtime errors. See [the plan](../experiments/v58_original_second/screen/plan.json), [game records](../experiments/v58_original_second/screen/games.json), and [summary](../experiments/v58_original_second/screen/summary.json).

The replay audit for v50, seed 94500, candidate in seat 0 found reward $44,709, 88.27% observable valid actor actions, 87.25% productive hand turns, 100% feed success, and no animal attrition. The same game’s v50 opponent earned $127,381. On a paired v57 reset candidate vs v50 at seed 94500 and seat 0, the reset earned $94,882; its observed valid-action rate was 92.75%, hand productivity 92.96%, and feed success 99.7%. Neither route beat v50 on that seed.

The candidate’s seed-94500 checkpoints had three placed cows and two placed sheep throughout, and never grew strawberries. The opponent had six cows, two sheep, and 16 strawberries by day 7, then eight cows and 33 strawberries by day 11. The candidate’s observed accepted-sale-value lower bound was about $52.6k across eggs, fertilizer, melon, milk, wheat, and wool; the reset candidate’s was about $126k across nine products. This proxy only counts inventory drawdown and is not a ledger of accepted sale revenue.

## Diagnosed failure and attempted repair

The original planner fetched shed livestock only through day 2, even though its market plan bought animals later. That left purchased livestock idle in the shed. I removed the early-day cutoff and expanded fetch targets to unlocked pasture regions in [the candidate](../experiments/v58_original_second/original_second_candidate.py). On fresh seeds 94510–94512, that change still went 0–6 versus every opponent (mean margins −$66,972 vs v50, −$66,831 vs v53, and −$78,431 vs v54). The replay showed why a simple cutoff removal did not help: daily hires reset at night, and some animals were still in worker inventories at hour 18, so they returned to the shed at the day boundary.

I then raised fetch-task priority from 1 to 0.1 so animals would leave the shed earlier. On fresh seeds 94513–94515, that variant also went 0–6 against every opponent (mean margins −$93,068 vs v50, −$92,914 vs v53, and −$97,519 vs v54). In the seed-94513 v50 seat-0 replay, candidate reward was $41,886, valid-action rate 86.46%, hand productivity 85.12%, and feed success 100%. It still had only three placed cows at day 29 and no strawberries; two to three cows remained in the shed late in the game. Prioritizing fetch consumed the same scarce daily hand time needed for care and crop work, while still failing to complete placement reliably.

The distinct seed batches are preserved in [screen](../experiments/v58_original_second/screen), [fetch repair](../experiments/v58_original_second/screen_fetch_repair), and [fast fetch](../experiments/v58_original_second/screen_fast_fetch). Replay action success is inferred from consecutive observations, so movement/productivity rates are observable proxies rather than engine audit logs. The detailed evaluator is [evaluate_replays.py](../experiments/v58_planner_eval/evaluate_replays.py).


## Confirmed target persistence bug

Source inspection explained the failed handoff. The carried-animal loop used one sticky-goal key per unit and cleared that key when checking each species absent from inventory. For a cow carrier, the loop assigned a cow pasture goal, then the missing sheep and goose checks immediately removed it. The replay shows the resulting behavior: one hand fetched a cow, built at one pasture, then changed destination and built elsewhere on successive turns.

The isolated candidate now keys animal goals by `(unit index, species)` and removes a target only after that species is no longer carried. A focused regression in [test_goal_persistence.py](../experiments/v58_original_second/test_goal_persistence.py) verifies a cow target survives the missing sheep/goose checks and emits `PLACE COW` while standing on its matching pasture; it also verifies goals clear after inventory empties. Both tests pass. Engine inspection confirms `PLACE` consumes the animal only when the unit stands on a vacant matching `PASTURE`/`COOP`, and the nightly refresh returns remaining carried inventory to the shed before resetting workers.

Per instruction, I ran one spent-seed replay (94513, seat 0 vs v50) after this fix. Reward rose from $41,886 in the fast-fetch run to $47,857, still below the frozen v57 reset's $94,882 on seed 94500 and far below the opponent's $140,377 in this run. Two and then four cows attrited on days 9 and 13; only three remained by day 15, so improved placement exposed a feed-capacity failure. Valid-action rate was 87.42%, productive-hand rate 86.33%, and feed success 100% among attempted feed actions. The result is not a material competitive improvement, so the route remains no-go and no further sweep was run. The run record and replay are in [single_fix](../experiments/v58_original_second/single_fix); the run record preserves the exact candidate hash.

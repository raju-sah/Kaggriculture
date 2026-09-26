# V58 model-based resource allocator probe

## Design

`experiments/v58_planner_eval/model_based/resource_controller.py` is an observation-only market allocation seam. A route policy supplies its current actor orders and market plan. The allocator estimates a one-day wheat/feed liability from visible animals, carried and shed wheat, then estimates seed cash committed by current `PLANT` intents. It caps planned purchases so they preserve those reserves; it never treats submitted sale orders as cash. It retains the route planner's actor choices and planned order priorities.

`build_agent.py --planner PATH` embeds the controller after a standalone planner and checks it with Kaggle Environments' `get_last_callable`; the generated wrapper must be selected as `_model_based_entrypoint`. The exact loader check passed for the frozen reset route. The standalone wrapper accepted retained observations and returned only `farmer`, `hands`, and `market` keys, with at most ten market orders.

This is a fast seam for integrating a route planner. The tested policy reused the frozen reset route for that reason; it did not copy actions from replays. The proposed longer-term controller remains unvalidated as an independent complete route planner.

## Spent-seed diagnostic and decision

The first match check used already-spent seed 92802 against v50, both seats, with the frozen reset route as paired control. Each match completed without errors. The reset route's margin was -$33,587 in both seat orders; the allocator wrapper's margin was -$35,838 in both orders, a paired change of -$2,251 per game. Candidate-seat feed success fell from 99.7% to 92.79% in seat 0; it remained 100% in seat 1. Actor action-effect rate fell from 0.9282 to 0.9132 in seat 0. The game-by-game scores, hashes, and evaluator output are retained in [`summary.json`](../experiments/v58_planner_eval/model_based/spent_seed_92802/summary.json).

The guard therefore fails this first diagnostic and does not merit fresh 94800+ games. The feed change is consistent with the controller's central risk: keeping the estimated wheat liability as cash can block other purchases while failing to make wheat physically available to the feeding route at the needed point in the day. One seed and two seat orders are only screening evidence, and shared-market/shop RNG interactions complicate attribution, but the paired loss and lower feed completion are enough to stop this prototype before fresh evaluation. Do not interpret it as a general result against all routes.

The final holdout seeds 93000–93049 were not used. No submission was made.

## Files

- `experiments/v58_planner_eval/model_based/resource_controller.py` — reserve calculation and allocator.
- `experiments/v58_planner_eval/model_based/build_agent.py` — standalone composition and exact Kaggle loader check.
- `experiments/v58_planner_eval/model_based/candidate_agent.py` — generated diagnostic wrapper over the frozen reset route.
- `experiments/v58_planner_eval/model_based/spent_seed_92802/summary.json` — compact per-game evidence.

# V58 original observation-conditioned route prototype

## Scope

`experiments/v58_validation/original_route/agent.py` is an independent task
allocator. It reads the current observation, estimates crop value from visible
prices and unlocked shops, manages cash/seed/feed reserves, assigns movement
and productive actions, and uses a single demand-selected animal as a limited
livestock experiment. It contains no replay action sequence and imports no
other policy. Public replay evidence informed general mechanics and economic
patterns only. See [V58_REPLAY_RIGHTS.md](V58_REPLAY_RIGHTS.md); this is
performance research, not a claim that the policy is ready or original enough
for submission.

## Exact-loader and preflight result

The controller was exercised through Kaggle's `get_last_callable` loader on 12
observation/seat probes from the public replay. All action shapes were valid,
and all 12 chosen actions differed from the reset policy. The final tested
source SHA-256 was
`daab0e4f92ae103e2e5ab00b4a88de3b4781b41342ef9b7ae283e8f2b0c63f0f`.

A two-seat, same-seed development preflight against v48 used seed 94403. Both
games completed without errors and the candidate lost in both seats, finishing
at $9,236 against $183,905. The retained seat-0 replay showed 83.94% observed
valid actor actions and 83.28% productive hand actions. Eight feed actions all
succeeded and the one cow suffered no observed attrition. Inventory-drawdown
sales provide a lower bound of about $13.6k at observed prices (60 strawberry,
23 tomato, one fertilizer and one milk); this is not an exact revenue ledger.

The feed correction changed task-eligibility checking to use the task label,
because the action was stored as a list and comparing that list to the string
`"feed"` silently bypassed wheat-carrier selection. This repaired feeding but
did not make the controller competitive. The earlier cashflow-only iteration
on the same development seed ended at $12,898; outcomes across controller
revisions are diagnostic rather than a clean paired estimate because each
controller changes the game trajectory and market state.

## Budget and status

No fresh 94400–94402 benchmark panel was run: the preflight outcome did not
justify spending it. Seeds 93000–93049 remain sealed. The controller still has
weak observed action productivity, low realized sales, and a very large score
gap to v48. It is not recommended as a candidate. A follow-up would need to
improve action-effectiveness and production throughput before broader matches;
adding more rule overlays without that evidence is not justified.

The source is a development artifact. No official submission was made. The
public route study has an unresolved derivative/originality concern in addition
to this poor performance result.

# V69 original macro-policy research

This branch tests authored policy changes against spent seed `94700` only. It
does not use opponent source code, public replay action tapes, new seeds, or a
Kaggle submission. The V67 in-house state-derived task planner is the starting
point; source modifications here are retained as separate experiments.

## Spent-seed outcomes

Every match used the exact local tournament loader and both seat orders against
the pinned V56 executable. No errors or timeouts occurred in the completed
runs. Cash and action throughput are the candidate's own metrics; opponent cash
can move because both farms share the market.

| Candidate | Source SHA-256 | Candidate cash | V56 cash | Wins | Non-move farmer/hand actions | Farmer/hand moves | Water / harvest | Hires |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| V67 baseline | `3957e2b5cc48218ac1259899e5ca7c8f7a71d61dd2fabf7faa4ef1226d5ce364` | $40,039 | $136,343 | 0/2 | 1,698 | 3,658 | 535 / 200 | 217 |
| Extra pens + ninth-hand target | `5c7555e4b06aa9a5ec194f209fdb6264ff468fcab0bbe8d731348aca95e37493` | $42,326.50 | $144,757 | 0/2 | 1,766.5 | 3,713 | 540 / 228 | 236 |
| Tomato task experiment | `264c6037fddfd9b3d0736ff3c41da79532c5b2033c3d8407a4ec910263d438a7` | $27,060 | $106,932 | 0/2 | 2,249 | 3,746 | 523 / 191 | 219 |
| Second land + late wheat | `da917ad121ced97b2a67551a8b763208fbadb79ef3bf9adc74a4c635b05eafb8` | $34,092 | $137,512 | 0/2 | 1,648 | 3,896 | 531 / 174 | 217 |

The extra-pens experiment did not scale its herd: the final farm still had two
cows, three sheep, and two geese. Five additional pasture slots were built, but
the YARN_STORE appeared after its sheep-buy window. Hiring increased by 19
orders but remained below V56's 289; productive non-movement actions remained
less than half of V56's 3,680. The candidate moved 592 more times than V56 while
watering less than half as often (540 versus 1,184). That confirms a task
throughput and routing gap rather than a shortage of available plots alone.

The tomato trial used a predeclared $100 quote threshold. On this seed, tomato
prices were only $61–73, so that crop choice did not activate. The implementation
also stopped filling unused strawberry plots after day 8 and earned only
$27,060; this variant is retained as a failed, attributable trial.

The second-land experiment unlocked a third quadrant by day 12 and planted
short-cycle wheat into available extension cells. It reached 20 wheat plants
at mid-season but spent on land, seed, and travel without enough remaining
workforce to convert the acreage into sales. It reduced own cash by $5,947
against V67 on the same seed and increased movement to 3,896. This is a no-go;
do not retune on 94700.

## Offline task-ranker diagnostic

`train_task_ranker.py` fits a depth-7 decision tree from candidate-seat action
labels in the V69 macro rollout and evaluates it on the V69 late-wheat rollout.
It uses no V56 action rows. `task_ranker_tree.json` is a portable data-only tree
artifact and `task_ranker_report.json` records hashes and diagnostics. The split
holds out source variant and seat-swapped episodes, but both sources use the
same seed; it is not independent-seed generalization.

The model saw 11,940 training and 11,404 held-out unit decisions. Exact action
top-1 accuracy was **4.89%**, against the corrected **18.94%** training-majority
baseline. The action-family accuracy was 5.19%. Only 30.48% of raw top-1
predictions mutated the state under the pinned engine's unit-action
preconditions. Ranking the tree leaf's observed actions and selecting the
first action that passes the engine check yielded 23.62% exact-action accuracy;
its 100% applicability is by construction, with no PASS fallback in this test.
These results reject the prototype for deployment. The state-only model omits
the V69 dispatcher's hidden sticky-goal assignment and learned too little from
one highly correlated seed block.

The final eligible research direction is a compact decision model over
explicitly enumerated macro-intents, with observable profitability and task
capacity features plus deterministic legality masking. It needs diverse
simulator-generated seed blocks and an out-of-seed holdout before training
claims are meaningful. Do not use the current tree to control an agent. No
further same-seed tuning, training, fresh-seed games, or submission is planned
in this branch.

# V68 routing ablation

## Result

No V68 routing variant improved on the frozen V67 planner on spent seed 94700.
The strongest incumbent-only setting reduced movement but cut productive work
and cash; a milder setting retained similar task counts but lost paired cash.
The combined quadrant/incumbent setting also lost. I stopped before expanding
to other seeds because no variant passed the first-seed improvement gate.

V67 baseline SHA-256: `3957e2b5cc48218ac1259899e5ca7c8f7a71d61dd2fabf7faa4ef1226d5ce364`.
The routing variants changed only assignment costs/order; macro land, hire,
and crop spending rules were left as V67.

| Variant | Source SHA-256 | Paired V67 result on 94700 | Candidate hands: productive actions / moves | HIRE orders |
| --- | --- | ---: | ---: | ---: |
| incumbent −8, same-quadrant −2, incumbent task ordering | `ae3f80624f11a195b567d950e70487ff3f366897065c6d6c4c934504baa83e8a` | 0–2, mean margin −$18,233 | 1,053–1,083 / 2,834–2,839 | 201–202 vs opponent 217 |
| incumbent −5 only | `569de3e8dab2cf88777e1a841e6c6765ce24aadae77e44718950d0b8d349836e` | 0–2, mean margin −$6,108.50 | approximately 1,448 / 3,057 across seats; V67 comparison 1,439 / 3,197 | 218 vs 218 |
| incumbent −12 only | `9f644d56db54e36ee73639aedd78fc245bb373c90bc86e1f90ac5497db5d3fd9` | 0–2, mean margin −$14,474.50 | 1,214 / 2,767 mean across seats | 199 vs 217–218 |

Action counts are hand actions, excluding movement directions and `PASS`;
the −5 candidate produced 1,433–1,463 productive actions and 3,053–3,061
moves depending on seat. V67's spent-seed profile was 1,430 productive actions
and 3,235 moves. The moderate variant did not produce a meaningful throughput
change, and its score losses show that near-equal activity is not sufficient.
The strong variant's fewer moves did not translate into more work: productive
actions fell by about 15% and hires by 18–19 orders.

Against V56 on the same spent seed, incumbent −5 scored **$28,625** in both
seats against **$134,689**, margin **−$106,064**. It made 1,458 productive
hand actions over 3,063 moves with 218 hires. This is below V67's previous
$40,039 result against V56 and provides no evidence of a competitive gain.
Both paired match sets completed with no execution errors.

The combined variant had original source hash
`ae3f80624f11a195b567d950e70487ff3f366897065c6d6c4c934504baa83e8a`; its
exact source is retained at
[`agent_zone_commit.py`](../experiments/v68_routing/agent_zone_commit.py).
The −5 and −12 variants are retained at
[`agent_sticky5.py`](../experiments/v68_routing/agent_sticky5.py) and
[`agent_sticky12.py`](../experiments/v68_routing/agent_sticky12.py).
Replays, summaries, and action ledgers are under
[`experiments/v68_routing`](../experiments/v68_routing/).

## Decision

Do not promote routing changes or spend additional seeds on this hypothesis.
The task matcher already favors the nearest worker and previous tile; simply
raising incumbent retention either had negligible effect or starved other
productive tasks. The policy audit found a more specific crop-duty defect:
the strawberry planting gate also removes care tasks for existing strawberry
plants when current shop/price conditions change. That issue is isolated in a
separate V68 strawberry-duty ablation so the routing result remains
attributable.

No fresh seeds or Kaggle submissions were used.

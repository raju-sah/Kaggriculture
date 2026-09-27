# V74 executor test: min-cost task matching did not lift production

V74 holds V70's macro policy and task generation fixed, replacing only worker/task pairing. Its executor makes a per-priority candidate pool from each free worker's nearby tasks and solves a minimum-total-distance bipartite assignment (Hungarian algorithm) over that pool. Excess workers may remain idle and an oversized task pool is subset-selected. It uses the current observation, unit positions/inventories, task destinations, and V70's existing urgency ordering; it does not use a replay tape or alter crop, animal, land, or market decisions.

The source is `experiments/v74_executor/agent.py`, SHA-256 `802feefb6b3675247d84164cb6405e1644e8040f395fb6b1e0e1df89b213ffe4`. The base is frozen V70 SHA-256 `2002db9b4bbf20c654805adc35617eb787be3e9cb64e5aae46ae1044aad3b73e`.

Exact-loader paired games on spent seed 94700 completed in both seats without errors or timeouts:

| Opponent | Record | Mean candidate coins | Median coin gap |
|---|---:|---:|---:|
| Frozen V70 | 0–2 | $59,244.50 | −$342 |
| V56 | 0–2 | $50,486 | −$86,298 |

Full artifacts are under [`experiments/v74_executor/spent94700_v70/`](../experiments/v74_executor/spent94700_v70/) and [`experiments/v74_executor/spent94700_v56/`](../experiments/v74_executor/spent94700_v56/). Since the candidate did not clear the requested +$10,000 own-cash gate against V70, no other seeds were run.

Action summaries show no material throughput change. Across the two V70 matches, V74 averaged about 1,536 work actions, 3,431 moves, and 1,112 PASS actions. The corresponding V70 baseline in these games was approximately 1,500 work actions, 3,400 moves, and 1,100 PASS. Candidate SELL command counts were 158 and 161; these are command counts, not accepted units or revenue. The local assignment solution therefore did not materially reduce travel or create more productive work. The close V70 coin result is not an economic gain, and the large deficit to V56 remains.

The experiment falsifies this narrow executor hypothesis: the prior greedy edge assignment was not the main source of V70's low productive-action count. V74 is not promoted. Further executor work should first trace which generated work is unreachable or invalid and quantify accepted product per non-movement action, rather than broaden this matching variant.

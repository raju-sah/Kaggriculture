# V61 cash-flow and task-allocation diagnosis

## Finding

The first concrete economic bug was crop-agnostic seed budgeting in `_market_plan`: it subtracted the sum of every seed type from total plant demand, then used that single deficit to decide whether to buy more seeds. Seeds of one species cannot satisfy another species' target. On the candidate's saved seed-94700 trajectory, this caused wheat, carrot, and tomato targets to go without seed while surplus melon seeds remained unused. The bug explains some missing plant actions, but fixing it alone did not materially improve play. A separately controlled hire-priority ablation was also negative. The agent remains a no-go.

## Replay evidence

[`experiments/v61_cashflow/analyze_replays.py`](../experiments/v61_cashflow/analyze_replays.py) reads retained replays only. Its [`replay_audit.json`](../experiments/v61_cashflow/replay_audit.json) records day-close farm snapshots, action counts, modeled requested purchase costs, and a worker-task utilization proxy. Purchase costs use requested quantities at the observed quote; they are not accepted-transaction ledgers, since the replay schema does not expose each market commit. The supplemental [`variant_audit.json`](../experiments/v61_cashflow/variant_audit.json) contains the corrected-policy day-close snapshots.

The V60 baseline replay (candidate seat 0, v50 seat 1) starts both farms at $3,000 with no hands, crops, or animals. Their first market actions diverge immediately. V60 buys 4 melon seeds, 2 strawberry seeds, one cow, and hires two hands. v50 requests 20 wheat, a 15-wheat sale, one wheat seed, and then quickly builds a larger crop and herd base. By day 0 close, V60 has $2,078, two hands, one crop, and one cow; v50 has $15, five hands, 20 crops, and four animals. By day 6, V60 has $1,389, two hands, and eight crops; v50 has $1,284, eight hands, 29 crops, and eight animals. By day 9, V60 has $1,853, two hands, and ten crops; v50 has $4,057, nine hands, 37 crops, and 13 animals. This same-seed trajectory is the causal comparison; the frozen reset reference below is from another seed.

At the day-2 opening state, V60's desired targets already include one wheat crop while it holds three melon seeds. The aggregate seed check sees enough total seed and buys no wheat. On day 3 it needs carrot and wheat seeds while still carrying those melon seeds; the same aggregate check suppresses both purchases. Similar mismatches recur through day 10. By day 12 the state still holds three melon seeds while the target requires two melon and two carrot seeds. Across days 0–12, V60 attempts 12 PLANT actions versus 103 for v50 and 103 for the frozen v57 reset reference. The candidate's full-game total is 15 versus 239 for v50 and 249 for the reset reference.

Worker turns show a second scale gap, without proving a single additional code defect. Across days 0–12, the V60 baseline had 596 hand turns: 122 visible state-changing task actions (20.5%), 297 movements (49.8%), and 177 passes (29.7%). v50 had 2,037 hand turns: 858 task effects (42.1%), 855 moves (42.0%), and 319 passes (15.7%). Frozen v57 reset had 1,954 turns: 875 task effects (44.8%), 864 moves (44.2%), and 200 passes (10.2%). The whole-game observable productive-hand proxy was 72.36% for V60, 90.26% for v50, and 92.76% for reset v57; that broader proxy counts movement as productive, so the task-effect ratio is more informative here.

Modeled requested outlays during days 0–12 quantify investment priorities:

| Policy trace | Seeds | Feed/product | Animals | Hires | Land |
|---|---:|---:|---:|---:|---:|
| V60 baseline | $1,620 | $676 | $2,000 | $26 | $0 |
| v50, same seed | $4,840 | $3,173 | $7,900 | $885 | $3,000 |
| frozen v57 reset, seed 92718 | $4,840 | $5,697 | $6,300 | $830 | $3,000 |

These are order-cost estimates rather than cash accepted by the market. The v57 row is only a scale reference from seed 92718, not a same-seed comparison. Despite lower outlays, V60's portfolio and labor base remained too small to scale production; the source policy ended at $13,842 versus $140,225 for v50 on seed 94700.

## Controlled fixes and results

The original V60 policy code hash was `e107ce59f2ab4f384f296c7eb6701f875b9c5ebd37c00e2429ba42f8b292f4c2`. The subsequent daily-hire calculation correction was `e4f989c7d12f82edf00f40fd9df69bdbe1c38aa0e4b89c421b6e3520d784800b`; that file is preserved as [`baseline_agent.py`](../experiments/v61_cashflow/baseline_agent.py). The V61 per-crop seed fix is [`agent_seedfix.py`](../experiments/v61_cashflow/agent_seedfix.py), SHA-256 `e0793a4690310fa4f3d4789925e9aab075b94321d75781545fbafd400c42e489`. It buys only the crop-specific gap between target plots, current plots, and that crop's seed inventory. On spent seed 94700, this raised candidate coins from $13,842 to $14,024 against v50, but the margin stayed −$131,298. It scored $11,957 against v54 and $11,876 against the frozen reset policy.

Root also identified a separate hire-priority defect: discretionary buys reduced the planner's virtual cash before it calculated hires, even when an affordable hire could have been ordered first. The isolated second ablation, [`agent_hirepriority.py`](../experiments/v61_cashflow/agent_hirepriority.py), uses the per-crop seed fix and reserves hire cash before optional purchases. Its SHA-256 is `ee4fdeba696e164bb7bb9b5702e0ebf160085283a916256f929fdf11adc33c9c`. This version also lost both seats on seed 94700: mean margins were −$134,106 vs v50, −$154,511 vs v54, and −$158,666 vs reset v57. The v61 hire-priority run therefore does not support promoting the policy or continuing tuning. The two changes remain separately inspectable; the second variant adds only the hire-budget ordering change to the first.

| V61 variant | Opponent | Candidate final coins | Opponent final coins | Mean margin | Record |
|---|---|---:|---:|---:|---:|
| Seed fix | v50 | $14,024 | $145,322 | −$131,298 | 0–2 |
| Seed fix | v54 | $11,957 | $164,723 | −$152,766 | 0–2 |
| Seed fix | Frozen v57 reset | $11,876 | $167,609 | −$155,733 | 0–2 |
| Seed + hire priority | v50 | $11,971 | $146,077 | −$134,106 | 0–2 |
| Seed + hire priority | v54 | $11,973 | $166,484 | −$154,511 | 0–2 |
| Seed + hire priority | Frozen v57 reset | $11,973 | $170,639 | −$158,666 | 0–2 |

All 12 matches used spent seed 94700, completed through the exact local Kaggle loader, and had no agent or timeout errors. Seat swaps produced identical final scores. No fresh seeds, including 96000–96001, were used; no submission was made. The v50/v54 comparisons use the same seed; the frozen reset comparison is on the same spent seed for these V61 matchups, while the replay profile comparison above uses its previously saved seed-92718 trace.

## Limits and stopping point

The per-crop shortage bug is directly observable in the saved state and explains why policy targets were not converted into seed-backed plant tasks. Its correction produced additional crop diversity but only a $182 gain versus v50 and did not overcome the wider production gap. The hire-priority change was tested separately and did not improve outcomes. Low task-effect utilization remains a major limitation: the corrected policy still has far fewer productive actions and crops by day 12 than the references. This is not a justification for another isolated patch on one world. Work stops here, with the data and code available for a fresh design rather than continued tuning.

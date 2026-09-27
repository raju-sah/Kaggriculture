# V77 third-land cash and service runway — rejected

The corrected standalone candidate is [`agent_v77.py`](agent_v77.py), SHA-256 `03a94dd08fb588c68ff6ef9cc7cf522403b6ee6e6f0e06f8bb01e3aa2627ffa6`. It copies frozen repaired parent [`agent.py`](agent.py), SHA-256 `6d4e7c18c81fc499ee97849b988e821e1f6fabdbea687279b95abb92b85db6c4`. Frozen opponents: V56 `d9e9670921b62afedfa8cbc7086d2a2ec19e153ee26006cef477eadd462bd19c`; V70 `2002db9b4bbf20c654805adc35617eb787be3e9cb64e5aae46ae1044aad3b73e`. Engine is Kaggriculture 1.32.7, SHA-256 `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`.

The only intervention is a third-land admission check in `_bridge_market`, driven by the task planner's read-only mandatory workload. It estimates three days of feed, a minimum eight-hand crew and an incremental 12-cell planting/watering route, then requires $4,500 cash after land and seed commitments. It credits only cash plus a discounted quote for inventory already in the shed with a current buyer. No future sales are credited. The corrected check also requires that the existing strawberry planter still has enough time to sow the new beds before its unchanged day-11 cutoff. Species targets, crop and harvest thresholds, task priorities, and the executor are inherited from the parent. The gate's capacity estimate is a heuristic, not a simulation of individual worker routes. Its cash model charges only same-day hiring, while the engine rehires daily; two further eight-hand ladders would cost about $108 more. That omission cannot reverse this screen's rejection, because the best pre-cutoff cash projection already misses the reserve by $3,554.

## First screen, spent seed 94700, both seats

| Opponent | Candidate cash, seats 0 / 1 | Accepted sales, seats 0 / 1 | Margin, seats 0 / 1 | Wins |
| --- | ---: | ---: | ---: | ---: |
| V56 | $70,962 / $70,962 | $92,873 / $92,873 | −$82,020 / −$82,020 | 0/2 |
| V70 | $44,410 / $50,131 | $66,943 / $72,425 | −$17,068 / −$11,241 | 0/2 |

All four games finished with zero candidate, opponent, infrastructure, and timeout errors. Exact engine settlement reconstruction matched every cash frame in all four replays: zero mismatches, maximum error $0. Replays, logs, action counts, and exact audit results are retained under [`runs/v77_runway_corrected_94700/`](runs/v77_runway_corrected_94700/). This screen has the same outcomes as the repaired parent because the new land was never admitted.

The best pre-cutoff V56 checkpoint was day 11 hour 1: after the proposed $2,000 land, $1,200 seed, and $666 feed commitments, projected cash was **$946**, $3,554 below the $4,500 reserve. Estimated three-day mandatory plus incremental work was 288.3 hand turns versus 453.6 available. V70 seat 0's best projected cash was −$659; seat 1's was −$1,694. Worker capacity therefore passed this coarse estimate, but funding failed before the unchanged planting window closed. No third land was bought in any corrected game.

The predeclared V56 gate required at least **$85,962 cash and $110,000 accepted sales in each seat**. Corrected V77 fell short by $15,000 cash and $17,127 sales per seat. Its longest zero-sales streak over days 10–16 was one day, passing that subcondition. The three-land eight-hand check did not apply because there was no third land. The livestock condition also failed: in both V56 seats and V70 seat 1, one paid sheep remained in the shed or carried from day 13 through day 24 and was placed on day 25, far beyond 48 hours. The replay auditor counted seven wheat plants decaying with unharvested yield per V56 seat; against V70 it counted 5–7 melons and 7–8 wheat plants, depending on seat. These counts use plant-to-weed transitions at the recorded lifespan deadline. The 2/2 V70 win requirement also failed (0/2).

## Provisional implementation retained for diagnosis

The original implementation is frozen as [`agent_v77_initial.py`](agent_v77_initial.py), SHA-256 `05d88037804f42cf95b1d1946c24d0840983a9e0ca255a2b9c8d4c7d472d0232`, with its unchanged first run in [`runs/v77_runway_94700/`](runs/v77_runway_94700/). It admitted third land on day 14 versus V56 and days 17/18 versus V70, after the fixed strawberry sowing cutoff. This did not test the intended berry expansion: new land became late wheat capacity. It scored $68,914 and $93,966 accepted sales in both V56 seats (0/2), and $33,681/$45,898 against V70 (0/2). There were zero execution errors and zero exact-settlement mismatches. Its day-14 V56 admission predicted $5,777 cash after commitments and 340.5 required hand turns versus 453.6 available; the actual day-14 last in-day checkpoint had $7,334 and ten paid hands, but no new strawberry plants. This defect prompted only the planting-window feasibility correction above; the failed provisional result is not pooled with the corrected screen.

The corrected V77 fails multiple predeclared gates and is **rejected**. Seeds 92802/92804, fresh validation, holdout, and official submission were not used. This result does not establish 100% historical-agent wins or top-ten readiness. Reproduce the corrected screen:

```sh
.venv/bin/python -m simulation.tournament --candidate experiments/v75_joint/agent_v77.py --opponent V70=experiments/v70_capacity/agent.py --opponent V56=agents/v56_agent.py --seed 94700 --repeats 1 --workers 4 --replay-policy all --output-dir experiments/v75_joint/runs/v77_runway_corrected_94700
.venv/bin/python experiments/v75_joint/v77_audit.py v77_runway_corrected_94700
```

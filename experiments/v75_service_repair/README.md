# V75 service planting repair (spent seed 94700)

Source: `agent.py`, SHA-256 `69e0ebd88b23c805d6d2184823c32a4bf9a6ed1b17bcffc6e1ca02fa4d95896b`.
It is a copy of V75 (`57ffc54f7598db028696af2f2c6b3cc36efc2cf5e9e131432d58ef943417612a`) with only one guard removed from `_plant_task`.

The new `service_reserved_cells` returns planned wheat, melon, and strawberry cells so the animal site planner can protect them. The same set was then checked inside `_plant_task`, rejecting those very crop cells. In the two original V75–V70 games, V75 issued 3 PLANT commands per game, compared with 135 in each repaired V75–V70 game. The repair restores crop task generation; other V75 service changes remain intact.

Exact-loader, seat-swapped tournament on the already-spent seed 94700 (`repeats=1`, engine 1.32.7) produced:

| Opponent | Record | Mean repair cash | Mean margin |
| --- | ---: | ---: | ---: |
| Frozen V70 `2002db9b4bbf20c654805adc35617eb787be3e9cb64e5aae46ae1044aad3b73e` | 2–0 | $47,770 | +$2,493 |
| Frozen V56 `d9e9670921b62afedfa8cbc7086d2a2ec19e153ee26006cef477eadd462bd19c` | 0–2 | $54,426 | −$96,505 |

Full game, action, and replay artifacts are in `spent94700_v70_v56/`. The original V75 averaged $44,166.50 and lost both games to V70 by $30,496.50. Restored planting changed competitive supply and lowered V70's own cash in the head-to-head matchup; the 2–0 record does not mean a large own-cash gain. In a separate matchup with V56, repaired V75 earns $2,640 less than V70's saved $57,066 on this seed. This is a causal bug repair, not a candidate for promotion based on one spent seed.

Command:

```sh
.venv/bin/python -m simulation.tournament --candidate experiments/v75_service_repair/agent.py --opponent V70=experiments/v70_capacity/agent.py --opponent V56=agents/v56_agent.py --seed 94700 --repeats 1 --workers 4 --replay-policy all --output-dir experiments/v75_service_repair/spent94700_v70_v56
```

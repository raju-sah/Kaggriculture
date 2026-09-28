# V104 feasibility check: seed 160001 (spent replay, no new games)

Run: `.venv/bin/python experiments/v104_commandcode/feasibility_check.py`

Source: `experiments/v101_commandcode/lifecycle_replays/seed_160001.json`
(an already-saved V101 replay for the SPENT development seed 160001, seat 0).
No match was run for this check; it only reads the replay on disk.

## Result: INFEASIBLE

### The day-6 route on the incumbent tape

| Event | Hour | Actor | Tile |
|---|---:|---:|---|
| `BUY_ANIMAL SHEEP 2` | 1 | — | — |
| `PICKUP SHEEP` | 8 | 5 | (5, 4) |
| `PLACE SHEEP` | 11 | 5 | (5, 4) |

Actor 5's entire day-6 trace:

```
h08 PICKUP      SHEEP        (5, 4)
h09 PICKUP      WHEAT        (5, 4)
h11 PLACE       SHEEP        (5, 4)
h19 PLANT       STRAWBERRY   (8, 4)
h22 PLANT       STRAWBERRY   (9, 4)
```

Tiles visited: `(5, 4)`, `(8, 4)`, `(9, 4)`. **No COOP among them.**

The tile the sheep is placed on, `(5, 4)` at d6h11, is `{'kind': 'PASTURE'}`.

### The obstruction

1. `ANIMALS["GOOSE"]["structure"] == "COOP"` — a goose cannot stand on a pasture.
2. The engine's animal `PLACE` branch (`kaggriculture.py`, `_apply_unit_action`)
   only places when the unit **is standing on** a matching, unoccupied structure
   tile. There is no "carry to a distant tile" action and no adjacent-placement
   fallback for animals (that path exists only for the shed drop).
3. **No COOP exists on the board before day 11** on any spent seed inspected:
   160001, 160003–160010, 160013–160015, 160017–160019 all build their first COOP
   on **day 11**. Seed 160001's only COOP, at `(3, 7)`, is first present on
   **day 28**.

The day-6 route is therefore **five days too early** for a COOP to exist. A goose
bought on day 6 has nowhere to go on the existing route.

### Why it is not worked around

Making it work would require either building a COOP before day 6 (new spending
and new tiles, a much larger change than a one-for-one substitution) or sending a
worker to a COOP that does not exist yet. Both are exactly the "extra unplaced
cows" and "borrowed worker route" failure modes recorded in the V93–V100
postmortem, which this whole line of work is required to avoid.

**Verdict: the V104 GOOSE substitution is closed as written.** No candidate was
built, no match was run, and no fresh seed was touched.

## Note carried into V105

The obstruction is specific to GOOSE's COOP housing, not to the pasture
substitution idea generally. A **COW** also lives in a PASTURE, and the day-6
route *does* place a sheep on a pasture at `(5, 4)`. The question V105 must still
answer is the placement-count one: the day-6 route shows only **one** sheep
`PICKUP` and **one** sheep `PLACE` for a cohort of **2**, so replacing both
bought sheep with cows requires two placements, and this route demonstrably
supplies one.

# V70 deadline-ordered batch assignment

V70 changes the task scheduler in frozen V69. V69 assigned every actor-bound
task before considering any open task, even when the bound task had a much
lower urgency. A worker carrying products could therefore be sent toward a
DROP while a crop was about to die or an animal still needed care. V70 keeps
actor-specific tasks assigned to their carrier, but processes them in the
same strict priority bands as open tasks. Within each band it repeatedly
assigns the globally cheapest worker/task pair, including the existing feed,
build, and tile-affinity adjustments.

The frozen implementation is
[`agent_v70_batchassign_frozen.py`](../experiments/v69_dispatch/agent_v70_batchassign_frozen.py),
SHA-256 `a74027a6b053915beedde6a43da0d6aea81c70119406a1d3b566a003548f9bac`.
It descends from the frozen deadline-aware V69 source, SHA-256
`8c69e1f4d756a83effc43b966b808df8441aec22c159396e2b7cd98a15a3112f`.
The matching tests used the same bytes as the frozen file. All seeds below
were previously spent; no fresh seeds were run.

## Paired results

| Seed | V70 cash | V69 cash | V70 margin | Result vs V69 | V56 cash | V70 margin vs V56 |
| ---: | ---: | ---: | ---: | :---: | ---: | ---: |
| 94700 | $48,832 / $51,649 | $33,586 / $38,943 | +$15,246 / +$12,706 | 2/2 | $148,352 | −$98,647 |
| 92802 | $57,871 / $66,381 | $43,775 / $55,556 | +$14,096 / +$10,825 | 2/2 | $125,434 | −$69,783 |
| 92804 | $74,891 / $74,891 | $59,507 / $59,507 | +$15,384 / +$15,384 | 2/2 | $146,882 | −$92,045 |

V70 won all 6 seat-swapped games against frozen V69, with an average margin
of $13,940. It lost all 6 games against V56. Its own cash versus V56 rose from
V69's $40,335 / $52,341 / $51,294 to $49,705 / $55,651 / $54,837 on the three
seeds, but the remaining deficit is large. V56's settled cash was
$138,910 / $131,143 / $126,379 in the original V69 panel; same-game V56 cash
in the V70 matches was $148,352 / $125,434 / $146,882, respectively.

## Work allocation and limits

Across the six V56 seat-swapped games, V70 averaged 1,367 productive hand
actions and 2,827 hand moves per game. Frozen V69 averaged 1,282 and 3,261.
V70 also averaged 751 hand PASS actions, compared with V69's 422. Those extra
passes came with fewer moves and a slightly higher productive-action count:
the new scheduler converts part of the movement budget into both useful work
and idle turns, rather than increasing total worker-hours. PASS counts remain
a concern for future work.

Care coverage rose from 146/170 animal-days (85.9%) in V69 to 170/186 (91.5%)
in V70; the denominator is higher because the matches produced more animal
days. Accepted strawberry sales rose from 23 to 39.3 units per match, and
strawberry harvest actions from 13.3 to 35.3. No animal escaped in the V70
replays. The scheduler produced these improvements with the macro spending
and 8-hand maximum unchanged.

The V56 gap is still primarily capacity and crop conversion. V70 has not
tested more hires, and this assignment change alone does not approach V56's
roughly $130k cash. The files, game records, and replays are in
[`experiments/v69_dispatch/batchassign_94700`](../experiments/v69_dispatch/batchassign_94700)
and [`experiments/v69_dispatch/batchassign_panel`](../experiments/v69_dispatch/batchassign_panel).
The initial two worker launches used the system Python without
`kaggle-environments` and produced infrastructure failures; they were rerun
with the project `.venv`, and all 12 recorded matches used in this report
completed cleanly.

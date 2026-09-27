# Isolated V76 melon window on V75 joint

`agent_melon.py` SHA-256
`893c53176d523fc62f7d72ac66dcf593c2d0f3fd47e64c7e918c75cc7b0e9990`
is a copy of the frozen V75 joint placement repair `agent.py` SHA-256
`6d4e7c18c81fc499ee97849b988e821e1f6fabdbea687279b95abb92b85db6c4`
with **one conditional change**: a melon may be harvested at four yield units
from day 10 when the visible melon quote is at least $150. The existing five
unit/age-12 paths remain. `diff -u` confirms no other source change. This
transplants only the melon part of [V76](../../docs/V76_FERTILIZER.md), not its
fertilizer-priority change.

The Kaggriculture 1.32.7 exact-loader tournament used spent seed 94700 in
both seats against frozen V56 and V70. Full artifacts are in
`runs/melon_window_94700/`. All four games finished without agent,
infrastructure, or timeout errors. Exact engine settlement reconstruction
matched every cash frame of all four candidate replays ($0 error).

| Opponent / seat | Melon-window candidate cash | Opponent cash | Margin | Frozen parent cash in corresponding game | Melon-window result |
| --- | ---: | ---: | ---: | ---: | --- |
| V56 / 0 | $46,240 | $153,773 | -$107,533 | $70,962 | Loss |
| V56 / 1 | $47,317 | $153,868 | -$106,551 | $70,962 | Loss |
| V70 / 0 | $51,513 | $56,317 | -$4,804 | $44,410 | Loss |
| V70 / 1 | $46,227 | $54,240 | -$8,013 | $50,131 | Loss |

The parent also lost both games to each opponent on 94700. The melon rule
raises V70 seat-0 own cash by $7,103 but lowers its seat-1 cash by $3,904;
it lowers V56 own cash by $24,722 and $23,645. Thus there is no robust
per-seat gain and no V56 improvement. Earlier melon liquidation is real:
against V56, accepted melon sales on days 6–11 rise from $0 to $4,727 per
seat, lifting total accepted sales in that phase from $7,863 to $12,498.
Against V70, accepted early melon sales rise from $0 to $6,170 per seat,
matching the approximate V76 early window. The sale occurs by day 11 against
V56; V70 seat 0 already has $3,175 melon accepted on day 10.

Against V56, the early gain is overwhelmed later. Candidate accepted sales
for the full game fall from $92,873 (parent) to $66,570/$67,631. Wool falls
from $36,885 to $14,316 in seat 0, wheat from $4,511 to $2,118, and late
melon from $13,014 to $7,182. PLANT actions fall from 120 to 109 in seat 0;
WATER falls 486 to 447, DROP 93 to 72, while FEED and CARE increase. The
single early-harvest condition changes the subsequent task assignments and
crop cycle, reducing animal-product shipping and later crop income. The
specific route causing the wool loss has not been isolated; the accepted
sales and lower cash establish that the overlay is harmful in this coupled
planner. All 12 bought animals were still placed at the end of both V56
games, with none in the shed.

This variant fails the first spent-seed gate. No 92802, 92804, fresh seed, or
submission was used.

Reproduce:

```sh
.venv/bin/python -m simulation.tournament --candidate experiments/v75_joint/agent_melon.py --opponent V70=experiments/v70_capacity/agent.py --opponent V56=agents/v56_agent.py --seed 94700 --repeats 1 --workers 4 --replay-policy all --output-dir experiments/v75_joint/runs/melon_window_94700
```

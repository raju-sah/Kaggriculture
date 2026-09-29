# Submission improvement check — 2026-09-26

## Result

I replaced exp0044's literal opening crop and pasture coordinate sets with a deterministic layout computed from the starting unlocked quadrant and Manhattan travel costs. The generated candidate is [`experiments/submission_candidate_20260926/original_planner.py`](../experiments/submission_candidate_20260926/original_planner.py), SHA-256 `d82c430c9562b6b213b92899d4df59aa9b9b58bcc8bdf3522b9e819da03e083d`. The source was [`agents/exp0044_top_opener_bridge.py`](../agents/exp0044_top_opener_bridge.py), SHA-256 `e6941adcdc0b5fbefc8e7e2ae174068088ad20890dcb8031e5369cc15d7cbee9`; it remains unchanged.

The opening layout chooses five pasture sites nearest the shed-facing corner of the first unlocked quadrant. For the remaining twenty cells, it tests pairs of field centers, assigns ten cells to each center by relative Manhattan distance, then selects the split with the lowest center plus within-field travel cost. Ties are resolved by coordinates. The layout is cached by board dimensions and first unlocked quadrant, so later land purchases do not change it. This uses current farm land metadata and engine geometry; it does not use replay IDs, seeds, episode actions, or imported replay data.

## Spent-seed evidence

All matches used the exact local tournament loader and spent diagnostic seed 94700, with candidate and opponent seats swapped. Full outputs are under [`experiments/submission_candidate_20260926/`](../experiments/submission_candidate_20260926/).

| Opponent | Candidate scores | Candidate result | Median candidate margin | Errors / timeouts |
|---|---:|---:|---:|---:|
| Original exp0044 | 43,786 / 43,786 | 2–0 | +2,796 | 0 / 0 |
| v50 | 38,685 / 38,685 | 0–2 | −96,127 | 0 / 0 |
| v54 | 38,598 / 38,598 | 0–2 | −79,633 | 0 / 0 |

Runtime averaged 17.15 seconds per game against exp0044 and 25.57 seconds in the four-game control panel. The candidate beats its source narrowly, but loses heavily to both stronger controls. This is a no-go for further match spend or submission advancement.

## Provenance and limits

The candidate retains exp0044's observation-driven duty planner and other fixed route constants. The only geometry rewritten here is the former `OPENER_*` opening layout. No replay action sequence or former `OPENER_*` replay-derived coordinate table is included in the candidate. The remaining fixed planner coordinates still need the team's normal provenance review before any submission claim; this experiment establishes neither competition eligibility nor stronger play.

Exact-loader validation: two complete seat-swapped games against exp0044 and four against v50/v54 completed at 720 steps without candidate errors, opponent errors, infrastructure errors, or timeouts. No fresh seeds were used and no submission was made.

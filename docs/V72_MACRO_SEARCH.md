# V72 compact macro-policy search

## Result

The compact search did not find a candidate worth confirming. Nine variants
changed two visible-state investment choices in the frozen V70 original
controller: when to seek a third quadrant, and the strawberry price gate for
expanded land. Seven eligible variants received the same four-game screen
(94700 and 92802, both seat orders) against V56. All seven lost all four
games. Best own cash was **$49,496**, versus frozen V70's **$58,394** on those
same spent seeds. No candidate met the gate of at least $2,000 more own cash
than V70, no worse margin against V56, and no regression in direct production
actions. The held spent seed 92804 was therefore not used as a confirmation
run, and no fresh seed or submission was used.

| V72 macro variant | Own cash | Margin vs V56 | Direct production actions | Own-cash lift vs V70 | Margin lift vs V70 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Price $100, third land day 12 | $49,496 | −$76,454 | 1,486.5 | −$8,898 | +$3,763 |
| Price $150, third land day 12 | $49,209 | −$76,427 | 1,439 | −$9,185 | +$3,789 |
| Price $100, third land day 10 | $47,952 | −$78,664 | 1,590.5 | −$10,442 | +$1,553 |
| Price $150, third land day 10 | $47,515 | −$78,253 | 1,583 | −$10,880 | +$1,964 |
| Price $200, third land day 12 | $47,469 | −$85,590 | 1,375 | −$10,925 | −$5,374 |
| Price $100, third land day 8 | $44,306 | −$83,672 | 1,443 | −$14,088 | −$3,456 |
| Price $150, third land day 8 | $43,802 | −$89,566 | 1,435 | −$14,592 | −$9,349 |
| Price $200, third land day 8 | $43,447 | −$82,013 | 1,366.5 | −$14,948 | −$1,797 |
| Price $200, third land day 10 | $43,447 | −$82,013 | 1,366.5 | −$14,948 | −$1,797 |

The V70 comparison baseline on these two seeds was $58,394 own cash,
−$80,216.5 mean margin versus V56, and 1,393.5 direct production actions.
The best V72 variant's margin improved by $3,763, but its own cash fell by
$8,898. Reconstructing the implied V56 cash from the paired final scores,
V56 averaged $125,950 against that variant versus $138,611 against V70.
This margin movement mostly reflects a lower opposing score; it does not
indicate better candidate economics. Direct production actions are farmer
and hand PLANT, WATER, HARVEST, FERTILIZE, FEED, CARE, and
COLLECT_FERTILIZER counts from the exact tournament records. They are a
throughput measure, not accepted sale value.

Two variants (`gate100_land8` and `gate100_land10`) had already completed
seat-swapped games on 92804 during the first screen before that seed was
reserved for confirmation. Those third-seed results are excluded from the
comparison table and from finalist selection. Their 94700/92802 values are
included for a same-seed comparison. Two other initial 94700 runs were
interrupted and repeated; their duplicate records are not counted. The exact
loader recorded zero candidate errors in the completed comparisons. No V70
head-to-head or held-seed confirmation was run because the economic gate
failed.

## Search and provenance

The search generator is
[`experiments/v72_search/generate_candidates.py`](../experiments/v72_search/generate_candidates.py);
the bounded exact-loader runner is
[`experiments/v72_search/run_search.py`](../experiments/v72_search/run_search.py).
The machine-readable parameters (strawberry price gate and day the third
quadrant is requested) and candidate hashes are in
[`manifest.json`](../experiments/v72_search/manifest.json), with paired
results in [`screen_results.json`](../experiments/v72_search/screen_results.json)
and exact game records/replays under `experiments/v72_search/runs/`.

The only source basis is frozen in-house V70,
`experiments/v70_capacity/agent.py`, SHA-256
`2002db9b4bbf20c654805adc35617eb787be3e9cb64e5aae46ae1044aad3b73e`. Each
V72 file is a standalone copied snapshot with only the two search parameters
changed. No V56 source, public replay action sequence, seed lookup, or other
opponent artifact is included. The best V72 snapshot,
`experiments/v72_search/agents/gate100_land12.py`, has SHA-256
`1e92e937965a6b98af5b0b80873800094fa97bc06d3fa716a9ae654501c03bba`.
All nine candidate files pass Python bytecode compilation. Exact-loader
matches exercised their runtime entrypoint; no candidate was promoted.

## Compute and next research path

The screened set took about **200 seconds wall time** with at most four
matches concurrently (two tournament processes, two games each). Mean match
runtime was **23.7 seconds**, about **663 match-seconds** over 28 paired games.
This two-dimensional parameter sweep is small enough for CPU; a GPU would not
speed the Python game engine or the policies' per-turn decision work. A
100-candidate expansion over the same two seeds and seats would be roughly
400 matches, or about 2.6 CPU-hours of match runtime and roughly 40 minutes
wall time at four-way concurrency, before any confirmation panel.

Do not continue same-family threshold or headcount tuning on these seeds. A
more promising next search is an original **route-template planner**: encode
compact day-level macro choices (investment order, number and location of
crop/herd zones, and temporary worker roles), simulate those plans in the
exact engine, and re-plan from the live observation every turn. The macro is
a policy template, not a prerecorded action sequence: if the board, shop,
inventory, or worker position diverges, the agent recomputes feasible tasks
and routes. Use a small beam or coordinate search over perhaps 20–40 macro
templates, first pruning plans that violate cash, feed, care, seed, or
deadline constraints with a lightweight state evaluator, then exact-seat-test
only the few strongest candidates against V56. The V72 screen shows why that
funnel matters: each exact paired candidate screen costs minutes even when
only two seeds are used. Keep V56 cash and direct production separate from
margin so market suppression cannot masquerade as income lift.

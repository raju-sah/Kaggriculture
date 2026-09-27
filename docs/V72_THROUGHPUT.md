# V72 throughput screen

The frozen base was V70 capacity source
[`experiments/v70_capacity/agent.py`](../experiments/v70_capacity/agent.py),
SHA-256 `2002db9b4bbf20c654805adc35617eb787be3e9cb64e5aae46ae1044aad3b73e`.
V70 and its files were left untouched. The spent-replay audit is retained in
[`v70_spent_audit.json`](../experiments/v72_throughput/v70_spent_audit.json).

## V70 bottleneck evidence

On seed 94700 against V56, V70 ended with $57,066 versus V56's $146,563. V70
made 1,502 productive hand actions, 3,567 hand moves, and 1,064 hand PASS
actions. It served 179/187 care-days and 181/187 feed-days, with no escapes.
Accepted sales were 149 fertilizer, 230 wheat, 97 wool, 71 milk, 68 melon,
62 egg, and 56 strawberry units. It harvested every observed ripe strawberry
tile-day, but left 339 ripe wheat and 209 ripe melon tile-days unharvested.
V56 had 3,297 productive hand actions and 2,839 moves, and sold 412 wheat,
306 fertilizer, 160 strawberries, and 221 eggs. Across the 94700/92802/92804
V70-versus-V56 spent replays, V70's crop-sales pattern remained narrow: wheat
227–230, melon 68, and strawberries 56 per match.

This audit points to a task/asset conversion limit, rather than a lack of
workers during the early expansion window. V70 has more hands than V56 on
many day-6-to-12 snapshots, while its third-quadrant and larger strawberry
asset mix remains absent. The V72-opening branch separately tests that
portfolio question.

## Dispatcher experiment

V72 attempted hour-aware task assignment with a soft local-cluster bonus.
The first implementation ranked each worker/task pair by its own remaining
deadline slack. That accidentally selected the farthest worker for each task,
causing visible east/west oscillation, only 24 productive hand actions, four
animal escapes, and $11–$12 terminal cash on 94700. After fixing the scoring
to use each task's best feasible slack across available workers and preserving
V70's opening through day 2, the candidate had no animal escapes but still
settled below the V70 control: $33,916/$34,856 versus $51,704/$54,926.

The final soft-local variant preserves V70's priority-band and nearest-worker
matching. It uses deadline slack and nearby task counts as small travel-cost
adjustments, without persisting worker/task ownership. Frozen source:
[`agent_v72_softlocal_frozen.py`](../experiments/v72_throughput/agent_v72_softlocal_frozen.py),
SHA-256 `74a4cdc5eae30b01ab724cc46d7cf59215b5d5a41a3065ad850d9d20f96f2b8f`.
On spent seed 94700 against V70 it lost both seats, ending at $50,781 versus
$53,902. It made 1,514 productive hand actions, 3,436 moves, and 1,003 PASS
actions, with 178/186 care-days served and no escapes. Accepted wheat and
fertilizer sales rose to 259 and 160 units, while strawberries fell to 49.
The action mix improved slightly, but terminal cash did not.

Per the screening gate, no 92802/92804 games and no V56 games were run for the
final V72 source. The dispatcher was not promoted and no fresh seeds or
submissions were used.

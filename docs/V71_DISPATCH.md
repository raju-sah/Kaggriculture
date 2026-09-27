# V71 dispatcher investigation

V71 was an isolated branch from frozen V70 capacity source
[`experiments/v70_capacity/agent.py`](../experiments/v70_capacity/agent.py),
SHA-256 `2002db9b4bbf20c654805adc35617eb787be3e9cb64e5aae46ae1044aad3b73e`.
The V70 source was not modified. The branch tested persistent ownership of
unfinished local tasks so an extra worker would continue toward a crop or
animal task instead of being retargeted each hour.

## V70 baseline on spent seed 94700

In the seat-swapped V70-versus-V56 games, V70 settled at **$57,066** and V56
at **$146,563**. V70 recorded 1,502 productive hand actions, 3,567 hand moves,
1,064 hand PASS actions, 76 DROP actions, and 211 PICKUP actions. It served
179/187 care-days and 181/187 feed-days with no escapes. Its accepted sales
were 149 fertilizer, 230 wheat, 97 wool, 71 milk, 68 melon, 62 eggs, and 56
strawberries. It harvested all 48 observed ripe strawberry tile-days, while
339 wheat and 209 melon ripe tile-days remained unharvested at the replay's
observation granularity. V56 recorded 3,297 productive hand actions and 2,839
moves, and sold 412 wheat, 306 fertilizer, and 160 strawberries, among other
products.

## Dispatcher variants

The first V71 scheduler persisted every open task, including FEED and
FERTILIZE tasks whose progress depends on shared shed inventory. Its source
SHA-256 is `ca08f4eca77fd463b6e9e40f73331c09730e257446bdd515cae68b8bdfeccd99`
at [`agent_sticky_failed.py`](../experiments/v71_dispatch/agent_sticky_failed.py).
On the spent 94700 seat swap, it lost 0/2 to V70: V71 finished with $43,575
versus V70's $52,295 in both seat orders. It also lost 0/2 to V56, finishing
with $40,357 versus $149,527.

The action trace identified the cause. V71's hand PASS count rose from 1,064
to 1,561. Care fell from 179/187 to 151/162; the task assignment could retain
a feed job for a worker without wheat after another carrier consumed the
shared stack, leaving that worker to PASS while the carrier could no longer
claim the task.

The corrected variant excludes FEED, FERTILIZE, FETCH, and DROP from sticky
ownership. Frozen source:
[`agent_v71_nostocksticky_frozen.py`](../experiments/v71_dispatch/agent_v71_nostocksticky_frozen.py),
SHA-256 `d240b3408ef8f750cca988f83c0f2b6cea08d195bc3a70010c98425fc1e22e0b`.
It reduced PASS to 923, restored care to 175/186 and feed to 180/186, and
raised accepted strawberry units to 59. It still lost both seats to V70:
$52,242 versus $55,674 and $51,381 versus $52,977. Against V56 it settled at
$49,253 versus $147,329 in both seats. Its 1,482 productive actions and 3,609
moves were close to V70's baseline, without a cash gain.

Only spent seed 94700 was used for V71 screening. Following the initial
negative result and the root task's stop gate, no games were run on seeds
92802 or 92804. The persistent-task design is not promoted; the commodity
task correction explains and reduces its PASS regression but does not show
an advantage over V70.

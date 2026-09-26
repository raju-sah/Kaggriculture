# V61 independent audit: v60 original early economy

## Scope and comparison limits

This is a read-only audit of `experiments/v60_original/agent.py`, the spent
seed-94700 replays (original and hirefix panels), and a saved frozen-v57 replay.
No games were run and no agent file was changed. The frozen-v57 replay is seed
95600, so its realized coin outcomes are not a paired control for seed 94700.
For same-state comparison, I also called the frozen v57 policy on recorded
seed-94700 observations; this is a one-step offline action comparison, not a
counterfactual game rollout.

## Earliest economic divergence: day 0 staffing and crop portfolio

At seed 94700 day 0/hour 0, v60 sees $3,000 and no hired hands. The corrected
v60 replay requests three HIREs, four MELON seeds, two STRAWBERRY seeds, and one
COW. The engine accepts all three hires and purchases; next-frame cash is
$2,076 with three hands. On the exact same recorded observation, frozen v57
requests BUY_PRODUCT WHEAT 20, SELL WHEAT 15, and one WHEAT seed. Its saved
seed-95600 replay executes that sequence from $3,000, ending at $2,854, then
hires five hands in the next market phase and buys two COW plus two SHEEP,
ending at $1,042. This establishes an early policy split in labor timing and
portfolio, but seed 95600's outcome cannot quantify the causal value of that
split for seed 94700.

## Concrete day-10/day-12 hiring suppression

The corrected v60 seed-94700 replay has nine hired hands on day 9, then no
hands on day 10 or day 12. The offline call of the exact v60 source on each
hour-0 observation reproduces the saved market action exactly.

On day 10/hour 0, the observation has $1,561, one active COW, two WHEAT in the
shed, and WHEAT at $34. The action sells six MILK and two FERTILIZER, buys one
WHEAT, four STRAWBERRY seeds, and two COW. It submits no HIRE. On day 12/hour
0, it has $1,599, two active COW, two WHEAT in the shed, and 25 MELON, three
MILK, and one FERTILIZER in saleable stock. It sells those goods and buys four
WHEAT, five seeds across MELON/WHEAT, and two COW, again with no HIRE. Both
plans contain fewer than ten market orders, so order-slot capacity is not the
cause. The staffing-day condition is also active (`day <= 13`, positive
projected work).

The cause is the planner's budget order in `_market_plan`: it first subtracts
feed, seed, and animal purchase estimates from its local `money` variable, then
computes the hire count against that reduced balance and the cash floor. At
day 10, the planned $800 COW purchase and $400 STRAWBERRY purchase suppress
hiring. At day 12, planned feed and seed/animal spending likewise consumes the
virtual budget before staffing is evaluated. It does not count the proceeds of
its planned sales in that local budget either.

The engine semantics make this consequential: `_process_market` processes all
HIRE orders atomically before the per-unit SELL/BUY loop, so hires do not need
to wait for the planner's later-ordered purchases or sales. A day-10 nine-hire
batch costs $88 (Fibonacci sequence 1, 1, 2, 3, 5, 8, 13, 21, 34); a day-12
ten-hire batch costs $143 (adding 55). Both amounts fit within the respective
opening balances, before any planned sale proceeds. The engine then clears
`hands` and resets `hires_today` at each day boundary, so omitted hires mean a
full day with no hired labor. The replay shows the omission and its affordable
nominal cost; this audit does not estimate the resulting lost crop/animal
revenue or claim a specific coin gain from hiring.

## Independent per-crop seed accounting defect

A separate source-level defect is present in `_market_plan`: it computes
`available_seed` as the sum of all crop seed inventories, then subtracts that
aggregate from `plantable` to derive `seed_need`. `_tasks` later checks seed
availability by the specific crop. A surplus of one seed type can therefore
mask a shortage of another and suppress the needed purchase. The implementation
worker independently reports this mismatch across days 2–10 and a 15-plant
season total, versus 239 plants for v50 and 249 for frozen v57 in the saved
comparisons. These aggregate counts are suggestive; this audit did not replay an
alternative seed policy or attribute a coin delta.

## Conclusion

There are two concrete early-economic defects: per-crop seed shortages are
masked by aggregate seed accounting, and the staffing budget evaluates hires
after optional purchases even though the engine executes hires first. Both
warrant isolated fixes. The first has reported whole-season planting evidence;
the second has exact day-10/day-12 no-hire observations and affordable hire
costs, but its causal coin impact remains unmeasured. No new games were run.

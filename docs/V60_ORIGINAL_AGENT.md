# V60 original economy agent: no-go

## Result

The original state-driven agent runs under the Kaggriculture loader, but it is not competitive. On the spent diagnostic seed 94700 it lost in both seats to each of v50 and v54. The initial version finished with mean coins of $13,800 (versus $140,225 for v50 and $159,186 for v54); its SHA-256 is `e107ce59f2ab4f384f296c7eb6701f875b9c5ebd37c00e2429ba42f8b292f4c2`. The daily-hire-corrected version fell to $4,230 versus v50 ($152,221) and $12,291 versus v54; its SHA-256 is `e4f989c7d12f82edf00f40fd9df69bdbe1c38aa0e4b89c421b6e3520d784800b`. No fresh seeds were used, including 96000–96001, and no submission was made. The later seed-stock and hire-order diagnosis is in [V61 cash-flow diagnosis](V61_CASHFLOW.md).

## Policy and bounded correction

[`experiments/v60_original/agent.py`](../experiments/v60_original/agent.py) is a standalone, standard-library-only observation policy. It scores crops and animals from the current market, allocates unique tasks to actors using positions and inventory, plans seed/feed/investment purchases, and emits no episode-specific or replay-indexed action sequence. It reads no replay data or third-party policy code. The purpose was to test whether an online economic portfolio plus task allocator could approach the scale of the frozen agents.

The initial spent run revealed a worker-count bug: hired hands reset at each day boundary, but the policy treated the current day's worker count as persistent and limited orders to two hires. The intended schedule could not produce the roughly 8/10/11 total units by days 6/9/12. I changed the day-start target to budget from the farmer baseline and prioritized hires after feed. This single correction produced far more hires but displaced other investments and worsened the result. That points to a deeper cash-flow and action-allocation problem; simply increasing daily headcount is not a viable fix.

## Reproduction and evidence

The first panel is recorded under [`experiments/v60_original/spent94700/`](../experiments/v60_original/spent94700/). It used initial code SHA-256 `e107ce59f2ab4f384f296c7eb6701f875b9c5ebd37c00e2429ba42f8b292f4c2`. The corrected-policy panel is under [`experiments/v60_original/spent94700_hirefix/`](../experiments/v60_original/spent94700_hirefix/); it used code SHA-256 `e4f989c7d12f82edf00f40fd9df69bdbe1c38aa0e4b89c421b6e3520d784800b`. Each panel ran seed 94700 against v50 and v54 with both candidate seats, using the exact local tournament loader. The corrected panel completed four games with no candidate errors or timeouts; runtime was about 14.2–19.4 seconds per game. Seat swaps produced identical scores.

Environment: `kaggle-environments==1.32.7`, 720 episode steps; engine SHA-256 `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`. `python3 -m py_compile experiments/v60_original/agent.py` passes. Both tournament panels also exercised the policy through the Kaggle environment's normal agent loader.

The first replay panel showed only two hands at days 6, 9, and 12, with 15 PLANT commands across the season. The staffing bug was therefore material, but after correction the candidate still ended far below both opponents. The available evidence does not isolate one remaining economic cause, and seed 94700 is only one world; the large negative margins are enough to reject spending the reserved fresh-seed budget on this implementation.

## Scope and limitations

This is a local research artifact, not a submission. It uses only current observation fields and no memorized episode/seed action table. The later replay-based seed-budget diagnosis and two bounded spent-seed ablations are documented in [`V61_CASHFLOW.md`](V61_CASHFLOW.md). These one-seed local results are not general win-rate estimates. The V60 strategy hypothesis and rationale are in [`V60_ORIGINAL_STRATEGY.md`](V60_ORIGINAL_STRATEGY.md).

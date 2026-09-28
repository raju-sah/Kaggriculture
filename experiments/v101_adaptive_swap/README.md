# V101 adaptive cow-for-sheep experiment

Isolated development experiment. No Kaggle submissions and no changes to V99 candidates.

## Hypothesis

At the day-6 h6 order observation, an already unlocked shop that consumes MILK is a direct downstream demand signal for adding a cow to the existing animal route. The candidate uses the same rule at BUY, PICKUP, and PLACE; absent the precondition, V92 actions pass through unchanged. Milk sinks in the pinned engine are Pizza Shop, Ice Cream Shop, and Smoothie Shop.

## Frozen artifacts

- `candidate_unconditional.py`: same-route one-for-one day-6 sheep-to-cow change with no shop gate.
- `candidate_milk_sink.py`: all-chain MILK-sink shop gate.
- Exact baseline/opponent: `experiments/v92_overflow_guard/candidate.py` (SHA-256 `0d5d356baa25703f1a7b753527d1b39e1c7d63478985913be5b3c2550261b806`).
- Candidate SHA-256 values and run records will be added after screening.

## Development protocol

Only seeds 150001–150080 are used here. Paired seat order runs against exact V92 are executed with the repo virtualenv and the pinned tournament harness, at eight workers. The fresh holdout seeds from the V99 audit and prior 93000–93011 seeds are not used. A distinct holdout plan is deferred until the development rule is frozen.

## First triage result

The unconditional swap completed 80 distinct seed pairs (both seats, 160 games). A broad pre-swap condition requiring any visible MILK sink (Pizza, Ice Cream, Smoothie) triggered on 9/20 in an initial 20-seed replay audit. Those swaps averaged +$1,802, but included four losses. All four losses either had a Yarn Store, or had Smoothie as the only MILK sink alongside Farmers Market. This suggests distinguishing direct Pizza/Ice Cream milk outlets and avoiding a direct wool outlet.

A narrower rule was frozen for a development confirmation split: require a visible Pizza Shop or Ice Cream Shop, and no visible Yarn Store; use the same predicate on BUY, PICKUP, and PLACE. On the exploratory first 20 seeds it triggered on four seeds, all wins (+$4,475 mean among those four). This is selection-stage evidence only; it is being evaluated on seeds 150021–150080 before any holdout plan.

## Updated confirmation rule (after examining the same 20-seed triage table)

A broader but still interpretable refinement had better triage coverage: any direct MILK sink (Pizza, Ice Cream, or Smoothie) and no Yarn Store. On the same exploratory 20 seeds it triggered on six seeds (150001, 150002, 150004, 150006, 150010, 150020), 5W–1L, mean +$3,289. This excludes all Yarn Store losses while retaining the additional Smoothie-only case. That rule is frozen in `candidate_milk_sink_no_yarn.py` and will be confirmed on seeds 150021–150080. The narrower Pizza/Ice Cream-only rule remains as an unrun exploratory artifact; do not treat its four perfect outcomes as independent evidence.

## Broad gate 80-seed result

Across 150001–150080 against exact V92 (both seats, 160 games), the any-MILK-sink gate triggered on 48/80 distinct seeds. The 48 triggered seeds averaged +$1,875.5, with 35 wins and 13 losses; the 32 no-op seeds were exact ties. Overall mean margin was +$1,125.3. The harness reported zero candidate errors, opponent errors, timeouts, or infrastructure errors. Because the broad rule can trigger when a Yarn Store is also unlocked, the no-Yarn variant is undergoing a disjoint 60-seed development confirmation on 150021–150080.

# V58 terminal actor and delivery audit

## Finding

The retained close-game replays do not support an actor-side terminal delivery overlay. By the last processed actions, the reset policy is already staging the farmer and hands at the shed, repeatedly issuing `DROP`, and has no mature crop output left to harvest. In the two seed-93600 AB/BA repeats and seed-93602 AB/BA repeats, the last two actions earn the same $1,109 for both seats in the reset-vs-v54/56 comparisons; the pre-existing score margin therefore does not change at the tail. The hidden final private state in the existing baseline summaries also reports zero carried inventory and zero shed inventory for both sides.

This leaves no observed late actor-side cargo or harvest opportunity to recover. The only remaining close-game axis visible from these replays is how already-collected shed stock is sold; the expansion agent is independently testing final-market order ranking, so this audit does not overlap or recommend changing that behavior.

## Evidence and limits

- Baseline replay files: `experiments/v58_expansion/diagnostic_93600/baseline/replays/` (v54 and v56, both seat orientations) and `experiments/v58_expansion/diagnostic_93602/baseline/replays/` (v54, both orientations).
- At replay rows 716–719 (day 29), the farmer is already at `[5,4]`, a shed-access tile. The action tail repeatedly contains farmer `DROP`; hand actions also use `DROP` while their positions converge on the shed. This repeats under both player orientations.
- Seed 93600 final scores are 111393 vs 116987 (or reversed by orientation); seed 93602 scores are 77327 vs 77243 (or reversed). The close margin is established before the final two successful delivery actions.
- At row 716, all ten planted tomato tiles in the inspected seed-93600 observation have `yield_units: 0`; the row-716 to row-719 observations show no later crop yield. Animals may still have stored yield, but actors already occupy the shed area and the end state clears all carried and shed inventory.
- The pinned engine applies unit actions before market actions, supports farmer/hand `DROP` only from shed-adjacent tiles, and sends remaining carried goods to the shed at day end up to capacity. No replay evidence points to route desynchronization as the source of the close tail.

Replay observations intentionally omit private inventories and shed contents, so the zero-inventory terminal check comes from the serialized full-state summaries rather than observations. This is a small sample of spent diagnostic seeds, adequate to reject an immediate endgame delivery guard, not a claim that cargo routing never fails earlier in a season.

## Recommendation

Do not add a global late-game `DROP`/harvest overlay from this evidence. It would duplicate behavior already present in the frozen reset policy, with no demonstrated action difference that could improve these close outcomes. Keep investigation on independently evidenced opportunities such as market-order sequencing, or an earlier-season event where cargo is actually stranded.

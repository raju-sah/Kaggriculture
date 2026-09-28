# V101 no-Yarn rule: precommitted fresh gate

Written before opening any seed in the range below. The standalone candidate is
`experiments/v101_adaptive_swap/candidate_milk_sink_no_yarn.py`, SHA-256
`d166d2420440a0a96643c061b010c444f372a89e236e9c22a8417b4008b81763`.
Its sole strategic change is the day-6 existing-route sheep-to-cow swap when a
MILK-consuming shop (Pizza, Ice Cream or Smoothie) is open and no Yarn Store is
open. The same shop condition guards BUY, PICKUP and PLACE. The distinct
development seeds 150001–150080 are spent. No 137501–137524, 160001–160060,
or 170001–170024 outcomes were used to choose this candidate.

Fresh holdout: seeds **180001–180024**, both seat orders, exact Kaggle loader,
against unchanged V92, V50 and V56. Run unchanged V92 vs V56 on the same seeds
as a matched control. Do not tune this candidate on these seeds.

Pass only if every condition holds:

1. V92: score rate at least 0.60, mean candidate margin above +$500, at least
   six distinct seeds with the full swap, and no per-seed loss worse than $4,000.
2. V50: score rate at least 0.75 and mean candidate margin above +$700.
3. V56: candidate score rate at least 0.50, mean candidate margin positive, and
   score rate no lower than unchanged V92's score on the matched control.
4. Zero agent errors, infrastructure errors or timeouts. Every triggered seed
   must show the changed BUY→PICKUP→PLACE chain, the cow surviving on a PASTURE,
   and accepted MILK sales. Untriggered games must be action-identical to V92.

If all conditions pass, Codex may package and submit the frozen candidate to
Kaggle under the user's standing authorization. Report the official submission
ID and status; local results do not guarantee a higher mutable public rating.
If any condition fails, do not submit this candidate or tune it on these seeds.

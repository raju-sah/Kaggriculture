# V75 funded third-land macro screen

`agent_macro.py` is one separate, observation-driven macro variant from the
frozen weed repair `agent.py`. Its SHA-256 is
`4e0cf678ccb2173c9b062d66ddd25e157fa3d87e039863f5e6d9ce70fa0c0887`;
the parent SHA-256 is
`6d4e7c18c81fc499ee97849b988e821e1f6fabdbea687279b95abb92b85db6c4`.
It reduces the sheep target from eight to five, attempts a third land tranche
on days 10–14 only when cash covers land, 12 strawberry seeds, and $900
operating cash, buys berry seeds in batches, and targets up to four cows after
the third land is unlocked if a milk buyer exists. Pasture-site, feed, and
cash checks remain live. The added strawberry planting window runs to day 15.
This was a single hypothesis-led variant, not a parameter sweep.

The exact-loader screen used spent seed 94700, both seats, against frozen V70
and V56 with Kaggriculture 1.32.7. Full logs/replays/results are in
`runs/macro_variant_94700/`. There were zero candidate, opponent,
infrastructure, or timeout errors. Engine settlement reconstruction matched
every observed cash frame in all four games ($0 maximum mismatch).

| Opponent / candidate seat | Candidate cash | Opponent cash | Margin | Result | Accepted sales, days 0–5 / 6–11 / 12–29 |
| --- | ---: | ---: | ---: | --- | ---: |
| V56 / 0 | $45,639 | $160,473 | -$114,834 | Loss | $2,680 / $9,258 / $53,802 |
| V56 / 1 | $45,639 | $160,473 | -$114,834 | Loss | $2,680 / $9,258 / $53,802 |
| V70 / 0 | $13,944 | $74,307 | -$60,363 | Loss | $2,714 / $8,379 / $15,418 |
| V70 / 1 | $58,103 | $72,635 | -$14,532 | Loss | $2,714 / $8,808 / $76,517 |

Against V56, the parent weed repair earned $70,962 own cash and lost 0/2 on
the same seed. This variant loses another $25,323 and remains 0/2. At day 9
it held two lands, five sheep, two cows, 12 strawberries, $5,353 and nine
hands; at day 12 it held three lands, 21 strawberries, five sheep, two cows,
one goose, only $408 and five hands. By the end, just three cows and two
sheep remained on the farm, with no animal held in the shed. The third-land
and berry tranche used cash needed for recurring daily hires and feed, so
animals escaped and later sales fell. The V70 seat-0 game was more severe:
day-12 cash was $26, and accepted sales after day 12 totaled only $15,418.

The elite checkpoint pattern of roughly three lands, 30+ strawberries, and
18 animals by day 9–12 was a prior, not an enforced script. The new land
reached only 21 strawberries and eight animals on the V56 seed at day 12;
service/cash capacity was not sufficient to turn the asset purchase into
income. This variant fails the first spent-seed gate. Seed 92802, 92804,
fresh seeds, and official submission were not used.

Reproduce:

```sh
.venv/bin/python -m simulation.tournament --candidate experiments/v75_joint/agent_macro.py --opponent V70=experiments/v70_capacity/agent.py --opponent V56=agents/v56_agent.py --seed 94700 --repeats 1 --workers 4 --replay-policy all --output-dir experiments/v75_joint/runs/macro_variant_94700
```

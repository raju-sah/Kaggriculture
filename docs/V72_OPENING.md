# V72 opening/capacity rebuild: stopped after a negative spent-seed screen

V72 tested whether advancing the berry/animal opening and making land affordable earlier could lift V70's accepted production. The state-derived candidate is `experiments/v72_opening/agent.py`, SHA-256 `319062ce7909b90a6385aba70129ac658becae8c901db997068222240a51b8a2`. It was derived from frozen V70 `experiments/v70_capacity/agent.py` (SHA-256 `2002db9b4bbf20c654805adc35617eb787be3e9cb64e5aae46ae1044aad3b73e`). It contains no replay tape or third-party action trace.

The variant lowered the strawberry planting quote threshold from 150 to 125 when a buyer was observable; allowed strawberry management on the reserved berry plots plus expanded crop cells; made existing berry service sticky; moved goose purchases from day 10 to day 5; and permitted a third land unlock from day 9, subject to a seed and cash reserve. The original dynamic hiring policy and batch assignment stayed in place.

Exact-loader paired runs used only spent seeds `94700, 92802, 92804`, with both seats. All 12 games completed without candidate, opponent, worker, or timeout errors.

| Opponent | Record | Mean candidate coins | Mean coin difference |
|---|---:|---:|---:|
| Frozen V70 | 0–6 | $52,508 | −$19,260 |
| V56 | 0–6 | $42,440 | −$101,498 |

Artifacts are under [`experiments/v72_opening/spent_vs_v70/`](../experiments/v72_opening/spent_vs_v70/) and [`experiments/v72_opening/spent_vs_v56/`](../experiments/v72_opening/spent_vs_v56/). The tournament loader reports the tested candidate source hash as `319062ce7909b90a6385aba70129ac658becae8c901db997068222240a51b8a2`.

Replay snapshots show the failure mode on seed 94700. At day 6, V72 had one land, one remaining cow, three sheep, and one goose, with $2,410; its V70 opponent had two lands, two cows, three sheep, no geese, and $2,162. At day 9 V72 had expanded to three lands with only $791 and 12 strawberry plants; V70 had two lands, $7,044, and the same 12 strawberry plants. By day 12 V72 had $226, 19 strawberries, and only one cow/one goose, while V70 had $7,768, 12 strawberries, and two cows/one goose. The early goose timing coincided with a cow disappearing, and V72's third-land purchase/expanded planting consumed operating cash before the new acreage could produce accepted sales. The extra berry slots also created more service load; the candidate did not convert its additional planted area into enough sales.

The replay action summaries show the candidate issued substantially more purchase/planting activity but the cash outcome is decisively worse. The seed-94700 candidate sold 119 market lots in its first seat versus V70's 122, despite buying 90 seed lots versus V70's 80. I did not derive a product-by-product accepted-sales ledger from this panel, so the causal attribution above is based on replay state snapshots and action summaries rather than claimed revenue totals.

No further tuning was done on these seeds. This candidate is not promoted; the next opening design needs a stricter cash-flow gate and proof that early additional animals survive care/feed before investing in third-quadrant acreage.

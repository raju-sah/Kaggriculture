# V67 original policy rebuild

## Result

The best V67 variant makes a single, gated expansion into the adjacent NE
quadrant and plants wheat plus strawberries only when the live shop list and
strawberry quote support the crop. It is observation-driven and contains no
replay action tape. Its exact source is
[`agent.py`](../experiments/v67_original/agent.py), SHA-256
`3957e2b5cc48218ac1259899e5ca7c8f7a71d61dd2fabf7faa4ef1226d5ce364`.
The V66 standalone bundle used as the control is
`experiments/submission_candidate_20260926/bundle/main.py`, SHA-256
`d82c430c9562b6b213b92899d4df59aa9b9b58bcc8bdf3522b9e819da03e083d`.

On two spent seeds, 92802 and 92804, with both seat orders against that exact
V66 bundle, V67 won **4/4**, with mean margin **+$2,045** and no execution or
infrastructure errors. The candidate averaged $55,497. These are two seed
blocks, not four independent seeds. Settlement reconstruction covered 2,876
seat-transitions with zero cash mismatches. The complete records and replays
are under [`frozenpanel_92802_92804`](../experiments/v67_original/frozenpanel_92802_92804/).

The earlier spent-seed check on 94700 was **1–1** against V66, with a mean
margin of **+$1,142**. Across all three spent seeds, the record is **5/6**
seat-swapped wins against V66. However, V67 still lost **both seats** to V56
on seed 94700, averaging $40,039 against the opponent's $136,343 (mean margin
−$96,304). V67 is far from strong-agent parity. The seed-94700 V66 comparison,
V56 comparison, and rejected broad-expansion variant are retained under
[`experiments/v67_original`](../experiments/v67_original/).

## What the controlled comparison shows

The first V67 experiment expanded all new land into wheat and melon and hired
up to ten hands. Against V66 on seed 94700 it went 0–2, scoring $33,287 and
$35,466 against $48,314 and $49,158. The broad version planted many more
plots, but its expansion failed to pay back: on one seat it sold $64,099 versus
V66's $56,794, while seed purchases rose from $2,270 to $6,500 and land/hire
costs rose from $350 to $10,062. It is preserved as
[`agent_broad.py`](../experiments/v67_original/agent_broad.py), SHA-256
`1283f2b89a5c38053ad13a2ef4c0c3b0dec17b6cde914bd56d8f82d2fc6d7e99`.

The selective variant capped expansion at one quadrant, used eight wheat and
twelve strawberry plots, and waited for a strawberry-demand shop and an
adequate cash reserve. Its accepted strawberry sales were just $214 on 92802
and $0 on 92804. The score lift therefore does not establish that strawberries
caused the improvement. It seems to come mostly from increased wheat and
other accepted sales, with the delayed expansion cost partly recovered during
days 12–23. On 92802, phase net cash was −$1,867 in days 0–5, +$13,322 in
days 6–11, +$29,603 in days 12–23, and +$15,455 in days 24–29. V66's paired
figures were −$1,867, +$13,818, +$25,751, and +$14,992. On 92804 the V67
phase figures were −$1,867, +$11,456, +$24,022, and +$14,937; V66 had
−$1,867, +$13,634, +$20,949, and +$15,426.

These are useful, narrow V66 comparisons. They do not validate the requested
10/10 wins against v48, v50–v56 or establish leaderboard readiness. No fresh
seeds or Kaggle submissions were used.

## V67's remaining scale gap against V56

In the live reactive V67-versus-V56 match on spent seed 94700, both seat orders
reproduced the same outcome. V67 ended at $40,039; V56 ended at $136,343.
At day 12 V67 had 32 crop tiles (16 wheat, 10 strawberry, 6 melon), 6 animals,
and 2 unlocked quadrants. V56 had 57 crop tiles (24 wheat, 33 strawberry),
17 animals, and 3 quadrants. At day 20 V67 had 20 crops and 7 animals with
8 hands; V56 had 68 crops and 17 animals with 13 hands.

The accepted market ledger makes the revenue gap concrete. V67 sold 544
product units worth $49,006; V56 sold 1,734 units worth $174,262. V67 sold
zero strawberry units, while V56 sold 255 for $52,714. V67 sold 72 milk and
58 eggs, compared with V56's 185 milk and 225 eggs. V67 sold more wool (99
versus 72), so wool volume alone does not explain the loss. The transaction
audit reconciled with zero cash mismatches.

V67 issued 217 HIRE orders against V56's 289. Its hands performed 1,430
non-movement actions (excluding direction changes and PASS) and 3,235 moves;
V56 performed 3,257 non-movement actions and 2,839 moves. V67 therefore
generated roughly 44% of V56's productive hand actions while making more
movement actions. Adding acreage without better worker routing left a smaller
livestock base and a weak conversion of actions into accepted sales.

The next architectural work should give hands stable, nearby work zones and
assign the animal workload by feeding, care, collection, and harvest capacity.
That would address the measured movement/action gap and allow a larger herd
and crop portfolio without starving either one. The main constraint is not
simply the land count: it is converting hired turns into sustained care,
harvest, and accepted product volume while preserving feed cash. A credible
next build must demonstrate that conversion on multiple spent opponent
regimes before any fresh-seed validation.

# V58 early expansion screen — 2026-09-26

## Intervention

The frozen reset policy under-hired during its opening growth window and did
not open its third quadrant until later. This standalone overlay fronts up to
nine hands on days 6–9 and eleven hands on day 12, respecting the engine's
10-order turn cap. From day 9 it queues the third quadrant purchase once the
policy has at least $2,400 available. The base route still chooses the farms'
work; the overlay only changes hiring and land orders. Its callable is the
unique `_v58_expansion_submission_entrypoint`, verified through Kaggle's
loader.

The reset candidate on seed 93400 reached peak staffing of 7, 7, 8, and 8 hands
on days 6–9, with two quadrants through day 9; on day 12 it reached 9 hands and
three quadrants. The expansion version reached 9, 10, 9, and 9 hands on days
6–9, two quadrants on days 6–8 and three by day 9; on day 12 it reached 11
hands and four quadrants. The same schedule appeared in all 16 expansion
replays. Minimum observed cash was $8, so the added investments kept cash
positive in the tested panel.

The intervention's action differences were checked against actual captured
observations: at day 6's opening it adds hires to the base policy's queued
hires, at day 9 it raises the day's hire count to nine and issues the land
order, and it honors the market-order cap. The output on seed 93400 vs v50 was
117,996–82,928 (+$35,068), compared with reset's 111,834–76,185 (+$35,649).

## Paired development panel

Both arms used seeds 93400–93403, both seats, and v50 and v53 (32 games total;
16 per arm). Results below are candidate wins–losses; average margin is
candidate coins minus opponent coins over both seat records per seed.

| Opponent | Reset | Expansion | Mean margin reset | Mean margin expansion |
| --- | ---: | ---: | ---: | ---: |
| v50 | 6–2 | 8–0 | +12,037.6 | +25,568.5 |
| v53 | 6–2 | 8–0 | +11,440.5 | +24,861.8 |
| Total | 12–4 | 16–0 | +11,739.1 | +25,215.1 |

The improvement concentrates on seed 93402, where reset lost in both seats
against both opponents and expansion won all four games. Paired mean-margin
changes for seeds 93400/93401/93402/93403 were −$581/−$9,143/+ $30,596/+ $33,252
vs v50 and −$700/−$9,277/+ $31,033/+ $32,629 vs v53. Thus expansion hurt
margins on two seed blocks, even as it flipped both losses on the third and
raised margins sharply on the fourth. The four-seed screen is development
evidence, not a broad readiness estimate.

The first test build had a recursive wrapper caused by an alias resolving the
rebound `agent`; it was discarded before the paired panel. A second loader
ordering issue made Kaggle select the old callable. The final artifact uses a
unique last callable, which the match worker loaded and executed in all 16
games. No execution or infrastructure errors occurred in the measured panel.

## Reproduction and artifacts

- Candidate: [`experiments/v58_expansion/v58_expansion_candidate.py`](../experiments/v58_expansion/v58_expansion_candidate.py)
- Runner: [`experiments/v58_expansion/run_paired.py`](../experiments/v58_expansion/run_paired.py)
- Plans, game records, summaries, and retained expansion replays:
  `experiments/v58_expansion/paired/{baseline,expansion}/`
- Baseline artifact SHA-256: `4173479fe1f80d031d570d1ea23b694dfe86e1d162317a4c9c7df0058a40208e`
- Expansion artifact SHA-256: `20c5a4a2e0d96d39cdd9e26de9daff0e685b66b5ec7f943f1e85ae38330e09fc`
- Engine: `kaggle-environments==1.32.7`, SHA-256
  `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`

The screen meets the specific day-6–9 and day-12 staffing/land milestones and
improves this small v50/v53 panel, but it does not establish a 100% sweep
against the eight historical agents. A principal limitation is that the
policy still inherits its crop mix and sales routing from the reset backbone;
the separate accepted-sale audit suggests wheat/fertilizer throughput is a
stronger next target than simply adding land and staff. Continue with fresh
seed blocks before considering this a promotion candidate. No final seeds
93000–93049 or Kaggle submissions were used.

## Frozen eight-opponent follow-up

After the initial screen, the expansion artifact was frozen at the SHA above
and compared to the frozen reset on seeds 93600–93604, both seats, against all
eight requested historical versions. This is 80 games per arm, 160 total.
There were zero execution or infrastructure errors. The per-match realized
eight-shop list was extracted from each full replay and the replay payload was
deleted after extraction; shop sequences are retained in the game records.

| Opponent | Reset wins–losses | Expansion wins–losses | Reset mean margin | Expansion mean margin |
| --- | ---: | ---: | ---: | ---: |
| v48 | 8–2 | 7–3 | +11,309.6 | +4,188.5 |
| v50 | 8–2 | 7–3 | +4,664.6 | +4,881.6 |
| v51 | 8–2 | 7–3 | +7,740.6 | +6,672.9 |
| v52 | 8–2 | 7–3 | +4,664.6 | +4,881.6 |
| v53 | 8–2 | 7–3 | +3,656.4 | +4,034.4 |
| v54 | 6–4 | 0–10 | −1,035.2 | −1,195.2 |
| v55 | 8–2 | 7–3 | +3,656.4 | +4,034.4 |
| v56 | 6–4 | 0–10 | −1,035.6 | −1,195.2 |
| Total | 60–20 | 42–38 | +4,202.7 | +3,287.9 |

The expansion's aggregate result is worse: 42/80 wins versus 60/80 for reset.
The losses against v54 and v56 are especially important. Those games often end
within a few hundred coins, and the overlay turned the reset's six wins per
opponent into ten strict losses. The expansion improved its mean margin
slightly against v50, v52, v53, and v55, but did not recover their 8/10 reset
win rate. It also lowered margin against v48 and v51.

Per-seed paired mean-margin changes across all opponents and seats were
−$150.5, +$6,927.9, +$1,013.6, −$4,449.3, and −$7,915.8 for seeds
93600–93604, respectively. These are score comparisons, not controlled
same-demand effects: **none of the 80 reset/expansion pairs had an identical
realized full shop sequence**. The expansion produced 19 distinct sequences.
One sequence, `FARMERS_MARKET, SMOOTHIE_SHOP, YARN_STORE, ICE_CREAM_SHOP,
ICE_CREAM_SHOP, FARMERS_MARKET, FARMERS_MARKET, YARN_STORE`, accounts for ten
expansion losses with mean margin −$25,909.2. Several sequences had all ten
games win, showing how sharply outcomes depend on the realized shop regime.
The sequence-stratified records are in `paired_comparison.json` and each arm's
`games.json`.

This screen rejects expansion as a promotion candidate for the 100% historical
goal. The early staffing and land schedule was achieved, but it is not robust
against the near-tied v54/v56 policies or the weak-demand sequence that clusters
losses. Hold this artifact unchanged for the report; the next policy should
measure net sale proceeds per hand-hour under controlled or stratified shop
demand, with wheat/fertilizer output as a focused hypothesis.

The paired screen is reproducible with
[`experiments/v58_expansion/run_historical_screen.py`](../experiments/v58_expansion/run_historical_screen.py).
Its arm plans record candidate, opponent, and engine hashes. Compact outcomes
and all realized shop sequences are under
`experiments/v58_expansion/historical_93600/{baseline,expansion}/`; no full
replays remain.

## Near-tie flip diagnosis: seed 93602 vs v54

The earliest baseline-win/expansion-loss case against v54/v56 is seed 93602.
Reset wins by $84 (77,327–77,243); expansion loses by $342 (82,005–82,347), a
$426 margin swing. Both seats produce the same margins. Full replays were
rerun against v54 and checked with the pinned transaction audit; each replay
reproduced all 719 transitions with zero coin, market-inventory, or
market-price error.

The first action difference is on day 6: expansion hires two additional
workers and trails reset cash by $55. That gap grows to $233 by day 9; the
third-land purchase accounts for the $2,000 lower cash observed day 10
(16,628 reset vs 14,395 expansion, after equal day sales of $16,865). However,
the expansion candidate finishes with $4,678 more cash than reset. The
opponent finishes with $5,104 more, which explains the final $426 relative
margin loss. Candidate accepted-sale totals also diverge from day 12 onward.

The realized shop sequence first diverges on day 12. The expansion's changed
land occupancy changes the RNG draws used for weeds before shops are drawn,
so the paired games no longer share market demand. This replay pair therefore
does not show that the extra hires or land caused lower candidate earnings;
the candidate earns more, while the opponent gains slightly more under the
different market path. This is evidence that a small paired flip can be
market-sequence-sensitive, not a causal justification for a liquidity gate.
The seed 93600 full-replay comparison likewise has reset and expansion both
lose, with expansion's relative margin better by $3,956, so it does not
explain the broad v54/v56 win-rate regression.

Replays and transaction audits for both arms and seats are retained in
`experiments/v58_expansion/diagnostic_93602/`. The policy effect on RNG/shop
sequence prevents clean causal attribution from this paired panel; a
controlled fixed-shop replay or broader shop-stratified evaluation is needed
before proposing a conditional expansion rule.

## Late-only value-order probe

Because seed 93602 suggested the final-stage market might affect a near tie,
a separate frozen variant reranks only existing SELL slots from step 630 onward
by current quote multiplied by requested quantity. It does not add market
orders or change farm actions. In a replay-faithful same-history counterfactual
on seed 93602 vs v54, the control reproduced the original +$84 margin exactly;
the reranked arm finished +$798, with candidate coins +$310 and opponent coins
−$404 relative to control. This is one selected-seed result, so it was not
treated as evidence of a general profit increase.

The frozen variant was then compared with reset on fresh seeds 93800–93804,
both seats, against v54 and v56 (40 matches total). All 40 games completed with
zero errors. All 20 baseline/variant pairs retained the same realized shop
sequence, and none had an action difference in the actual matches. Candidate
coin delta and margin delta were exactly $0 in every pair. The v54 margins by
seed were +$189, +$6,516, +$554, −$7, and +$68; v56 produced +$189, +$6,514,
+$554, −$7, and +$68. The intervention therefore had no effect in this
disjoint panel and does not meet the >$500 net-gain target. The candidate
callable itself was action-difference checked against reset on the retained
seed-93602 replay observation at step 649: it reordered SELL slots as
specified. The fresh panel simply did not contain an order ranking whose
change altered execution or score.

The late-only variant SHA-256 is
`ec0e983d6ba2db269c2382e0c923ff6260a33a4ba3e94fa4103074279fdb0527`.
Plans, per-game records, and paired seat-level coin deltas are in
`experiments/v58_expansion/late_value_93800/`; full replays were deleted after
shop and action-difference checks. Stop this line without an all-eight follow-
up: the fresh panel shows no lift.

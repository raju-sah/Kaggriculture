# v58 observation-conditioned economy overlays

## Decision

**No-go.** No tested overlay earned a material improvement over the frozen
reset route. The first four-vector screen is useful as bug evidence but cannot
be interpreted as a valid economy-policy comparison: a shared wrapper guard
removed baseline investments and sale orders. A corrected append-only seed
refill preserved the route, then changed just one market order on seed 95200;
it finished $8 below the reset control in both seat orders. No more games were
run after that near-no-op result.

This remains internal research. The reset backbone has public Lizs replay
lineage, and the rights question is unresolved; see
[V58 replay rights](V58_REPLAY_RIGHTS.md). No candidate was submitted and
`main.py` was not changed by this study.

## Invalid first screen and shared wrapper bug

The predeclared four-vector test used seeds 95200–95201, opponents v50/v53/v54,
both seats, plus reset controls: 48 candidate games and 12 controls, zero
execution errors. The wrappers passed the loader preflight and did change
market outputs, but their common cash filter removed baseline orders instead
of adding independently funded actions. As a result, the observed 0/12 record
per vector and large negative margins do not isolate the proposed parameter
choices; they show that the filter broke the route's economy.

Seed 95200 examples from the retained action-count records show the mechanism:
balanced reduced BUY_SEED from 191 to 132, HIRE from 289 to 257, BUY_ANIMAL from
12 to 9, and SELL from 285 to 193. In the exact-loader fixture observations,
it removed the baseline MELON seed buy at step 11, three hires at step 24, and
the WHEAT product buy at step 30. These are material route changes. The first
screen's complete arm records and hashes are in
[`early_screen`](../experiments/v58_validation/strong_economy/early_screen/);
the frozen four-vector design and result summary are in
[`early_futility_plan.json`](../experiments/v58_validation/strong_economy/early_futility_plan.json).
Seeds 95202–95207 were not used.

## Corrected append-only probe

The replacement wrapper, [`append_seed_refill.py`](../experiments/v58_validation/strong_economy/append_seed_refill.py),
can append at most one WHEAT seed purchase when a current planned wheat plant
would otherwise lack seed. It gives no credit for same-turn sale proceeds,
reserves $500 after conservative costs of all baseline buy/hire/land orders,
and never removes, edits, or reorders a baseline order.

The actual Kaggle loader selected the unique final callable
`zzz_economy_policy_entrypoint`. A 1,440-observation preflight found zero actor
action changes and zero baseline-order-prefix mismatches; fixture market
orders at steps 11, 24, and 30 stayed identical. The preflight record is
[`append_preflight.json`](../experiments/v58_validation/strong_economy/append_preflight.json),
and the frozen one-seed plan is
[`append_spent95200_plan.json`](../experiments/v58_validation/strong_economy/append_spent95200_plan.json).

On spent seed 95200 against v50, the candidate finished with $103,346 in both
seat orders; v50 finished with $84,823. The same-seed frozen reset control
finished with $103,354 in both orders, so the candidate-minus-reset margin
change was **−$8 per game**. There were no errors or timeouts. The candidate
added exactly one `BUY_SEED WHEAT 1` at observation step 5 / action step 6
(day 0, hour 5; cash $1,042; one planned WHEAT plant; one seed in stock).
The rest of the market order stream was preserved. Plant counts were
unchanged; observed WHEAT watering actions were eight fewer than reset, a
small downstream trajectory difference. This is a near-no-op with a tiny
negative score delta, not evidence of a useful gain. Full games, logs, and
replays are under
[`append_spent95200`](../experiments/v58_validation/strong_economy/append_spent95200/).

The source SHA-256 was
`d406f4920d0e9ef810d6b1e4b1f1aaa8fd68367031b8ba79ac25ad2e1165f695`;
the frozen reset hash was
`4173479fe1f80d031d570d1ea23b694dfe86e1d162317a4c9c7df0058a40208e`.
This result closes the branch. Do not spend seeds 95202–95207 on this policy.
Final holdout seeds 93000–93049 remain sealed.

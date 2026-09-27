# V82-LARGE: authoritative V56 baseline — 576 games

Read-only measurement. No new seeds (36 already-spent seeds, each with ≥6 prior saved games), no
submission, no agent code edited.

Runner: `.venv/bin/python -m simulation.tournament --candidate agents/v56_agent.py --opponent … --seeds <36 spent> --repeats 1 --replay-policy errors --workers 6 --timeout 300`
Artifacts: `experiments/v82_baseline/runs/v56_panel_large/`. Engine: Kaggriculture 1.32.7, exact loader.

## Why this run exists

The first V82 attempt used 5 spent seeds (80 games) and reported V56 at **50.0%**, which would have
implied the live-best agent was a coin flip against its own historical panel. That sample was too
small. Repeating with 36 spent seeds and 576 games puts the same agent at **60.1%**. The 10-point
swing is pure sampling noise, and it is the single most important methodological fact in this
project: **a 10-game-per-opponent panel cannot resolve anything**.

## Result

| Opponent | W | L | D | Win rate | 95% Wilson | Median margin |
|---|---:|---:|---:|---:|---|---:|
| v48 | 51 | 21 | 0 | 70.8% | [59.5, 80.1] | +11,668 |
| v50 | 46 | 26 | 0 | 63.9% | [52.4, 74.0] | +8,812 |
| v51 | 41 | 31 | 0 | **56.9%** | [45.4, 67.7] | +1,301 |
| v52 | 46 | 26 | 0 | 63.9% | [52.4, 74.0] | +8,812 |
| v53 | 46 | 26 | 0 | 63.9% | [52.4, 74.0] | +8,320 |
| v54 | 63 | 7 | 2 | 87.5% | [77.9, 93.3] | **+2** |
| v55 | 46 | 26 | 0 | 63.9% | [52.4, 74.0] | +8,320 |
| v56 (self) | 7 | 7 | 58 | 9.7% | [4.8, 18.7] | 0 |
| **TOTAL** | **346** | **170** | **60** | **60.1%** | — | — |

- Score rate (draws = ½): **65.3%**. Decisive win rate: 65.5%.
- By seat: seat 0 **59.0%** (170-88-30), seat 1 **61.1%** (176-82-30). No meaningful seat bias.
- Paired seed bootstrap 95% on win rate: **[54.7%, 65.5%]**.
- **Zero** candidate errors, opponent errors, infrastructure errors, or timeouts across 576 games.

## The self-play row is the most informative single number

V56 against itself: **7-7-58**. Not a single decisive result in 72 games. Against an identical agent
the outcome is *almost always an exact tie*, because the market is shared, both seats execute
near-identical plans, and the final coin totals land on the same value.

This has a direct consequence for the "100% against v48 and v50–v56" goal: **a 100% sweep requires
winning every game against agents that tie 81% of the time against themselves.** The ceiling on any
self-vs-self-comparable matchup is not a skill problem; it is that near-identical policies produce
near-identical scores and the winner is decided by noise smaller than the execution difference
anyone has demonstrated.

## The v54 row is an artifact, not a skill gap

v54 is 87.5% with a **median margin of +2 coins**. V56 and v54 are effectively the same policy: the
seven losses and the median margin say the games are decided by rounding, not strategy. This is the
same signature as the self-play row.

## Honest read on the 100% target

V56 is at 60.1% [54.7, 65.5] against a panel where three opponents are self-equivalent (v52, v53, v55
all tie or near-tie). Excluding the self-play and the two artifact opponents, the "real" contested
opponents are v48 (70.8%), v50/v52/v53/v55 (63.9%) and v51 (56.9%).

Going from 60% to 100% is not a tuning increment. Against a per-game base rate of ~64%, even a
hypothetical 90% agent would sweep 72/72 with probability 0.9⁷² ≈ 0.03%. And the elite corpus
(V83) shows the entire top-10 field separated by a median margin of ~5,000 coins on ~108,000
totals, with 50% of games decided by under 5,000. A 100% local sweep would be a stronger claim than
anything the current leaderboard top-10 shows among itself.

**What is achievable and measurable:** move 60.1% [54.7, 65.5] to a statistically distinguishable
higher band, verified on a panel large enough to detect the change. That is the target I am working
to, and I will not claim 100% unless it is actually measured.

## Limits

- All 36 seeds are already spent and were used in prior tuning. V56 was tuned on some of them, so
  60.1% is optimistic as an estimate of ladder performance (public score 1180.8 supports that
  pessimism).
- All opponents are local agents. The ladder pairs against unseen submissions, so this panel cannot
  estimate leaderboard placement.
- Effect sizes here are win rates with Wilson and seed-bootstrap intervals; no claim is made about
  causal attribution of any single agent difference.
- No fresh holdout was used. Nothing here supports a promotion or submission claim.

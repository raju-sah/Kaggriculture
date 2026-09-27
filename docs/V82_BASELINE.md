# V82: honest baseline — V56 vs the historical panel

Read-only measurement. No new seeds, no submission, no agent code edited.

> **SUPERSEDED IN PART.** The 5-seed run below (80 games, 50.0%) was **too small to measure
> anything** and is retained only as a record of that failure. The authoritative baseline is the
> 36-seed, 576-game run in [V82_BASELINE_LARGE.md](V82_BASELINE_LARGE.md), which gives **60.1%**
> (95% seed-bootstrap [54.7%, 65.5%]) for the same agent against the same opponents. The two
> results differ by 10 points purely from sample size. Do not cite the 50.0% figure.

Five already-spent seeds (92802, 93700, 94700, 95300, 95600), both seat orders, 10 games per
opponent, 80 games total.
Runner: `.venv/bin/python -m simulation.tournament` (exact loader, pinned Kaggriculture 1.32.7).
Artifacts: `experiments/v82_baseline/runs/v56_panel_spent/`.

## Source hashes

| File | SHA-256 |
|---|---|
| `agents/v56_agent.py` (candidate) | live submission `56544001`, public score 1180.8 |
| `experiments/v48_agent.py` | `dadee25a9840313218384208c53b2c4752f82c3209cc654632e0b96c65e2664a` |
| `experiments/v50_agent.py` | `e6b50128e023e3b9fafa1841e4cd520c5e581acb48e8628657585c18272eab2b` |
| `experiments/v51_agent.py` | `274f5913c4c4787cf825d10fde4de65f79b61d25c764aa6761d36d0840c04eb4` |
| `experiments/v52_agent.py` | `a53025fce6e901df0083d3115c8e422d77c8c86fac86be99da3e4725b6a50e5b` |
| `agents/v53_agent.py`, `v54`, `v55`, `v56` | as recorded in prior frozen reports |

Execution errors: **0**. Timeouts: **0**. Infrastructure errors: **0**.

## Result

| Opponent | W | L | D | Win rate | Mean candidate coins | Median margin |
|---|---:|---:|---:|---:|---:|---:|
| v48 | 6 | 4 | 0 | 60.0% | 99,810 | +8,766 |
| v50 | 5 | 5 | 0 | 50.0% | 93,823 | +476 |
| v51 | 4 | 6 | 0 | 40.0% | 93,438 | −2,164 |
| v52 | 5 | 5 | 0 | 50.0% | 93,823 | +476 |
| v53 | 5 | 5 | 0 | 50.0% | 93,171 | −325 |
| v54 | 9 | 1 | 0 | 90.0% | 94,096 | +2 |
| v55 | 5 | 5 | 0 | 50.0% | 93,171 | −325 |
| v56 (self) | 1 | 1 | 8 | 10.0% | 94,096 | 0 |
| **TOTAL** | **40** | **32** | **8** | **50.0%** | — | — |

Seat split: seat 0 **19-17-4** (47.5%), seat 1 **21-15-4** (52.5%). Paired seed bootstrap 95%
interval on win rate: **[0.325, 0.625]**.

## What this means, plainly

**The live best agent is a coin flip against its own historical panel.** V56, at public score
1180.8, wins **40 of 80** — 50.0%, with a bootstrap interval spanning 32.5% to 62.5%. It is not
close to dominant against the agents it was built to beat.

**The 100% target is not a tuning gap; it is a different regime.** To win 80/80 from a true 50%
per-game rate, the required improvement is not incremental. As a sanity check, even a genuine
90% per-game agent wins 80/80 with probability 0.9⁸⁰ ≈ 0.02%. A 100% sweep against this panel
would require the agent to be *structurally* better than every lineage in it, not marginally tuned.

**The v54 and v56 rows are artifacts of lineage, not skill.**
- v54 at 90% with a median margin of **+2** means V56 and V54 produce nearly identical outcomes; the
  nine wins are coin-flip noise on tiny margins.
- v56-vs-v56 gives 1-1-8. The eight draws are the informative part: **against an identical agent the
  game frequently ends exactly level.** Median margin 0.

**This is the same thin-margin world the elite panel shows.** From the 100-game elite corpus,
50% of top-player games are decided by under 5,000 coins and 32% by under 2,000, on ~108,000
totals. Local panels cannot resolve differences of that size at 10 games per opponent.

## Consequence for the plan

The V80/V81 wool direction is dead on independent evidence: across 100 elite player-games, day-12
goose share is **26.4% for winners vs 26.3% for losers**, and sheep share **27.4% vs 27.6%** —
identical. Elite winners are goose-heavy, and V81's +19,513 wool gain still lost 13,449 net cash
because it destroyed three other product lines. The seed-92802 "wool gap" was a matchup artifact
against local v50.

**Before any new agent is written, the panel needs enough resolution to measure what it is
measuring.** Ten games per opponent cannot separate a 50% agent from a 60% agent. The honest next
step is either a larger paired panel on spent seeds, or accepting that local winrate is a weak proxy
and prioritising the throughput axis the elite data does support (total sales +19,942 for winners
over losers, concentrated in days 12–23).

## Limits

- Five spent seeds, reused across many prior experiments. Any agent tuned on them is overfit, and
  V56 was tuned on some of them.
- All opponents are local agents, not the ladder. The ladder pairs against unknown submissions.
- Draws are scored as half-wins; the 8 self-play draws make the 50.0% figure an average of two very
  different regimes (near-coin-flip vs identical-agent).
- No fresh holdout was used. Nothing here supports a promotion or a submission claim.

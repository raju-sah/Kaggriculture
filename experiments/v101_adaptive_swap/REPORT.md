# V101 adaptive same-route cow swap

## Finding

A visible day-6 milk-demand gate raises the same-route sheep-to-cow swap’s development trigger rate far above the failed V99 Pizza-only gate. The broad all-milk-sink rule fired on 48/80 distinct development seeds (60%), averaging +$1,875.5 on fired seeds and +$1,125.3 overall versus exact V92. A more conservative frozen rule, “at least one direct MILK sink is unlocked and no YARN_STORE is unlocked,” was confirmed on a disjoint 60-seed development slice: 36/60 triggers, 28 wins, 8 losses, 24 no-op ties, and +$1,186.68 mean margin overall. No errors or timeouts occurred.

This is development evidence, not fresh-holdout evidence. No fresh seeds were run by this experiment.

## Frozen rule and engine behavior

The candidate is `candidate_milk_sink_no_yarn.py`, SHA-256 `d166d2420440a0a96643c061b010c444f372a89e236e9c22a8417b4008b81763`. At day 6 hour 6 it replaces one of the existing two SHEEP buys with one COW only if the visible town has a Pizza Shop, Ice Cream Shop, or Smoothie Shop and has no Yarn Store. The identical predicate guards the existing sheep pickup and sheep placement conversion. The pickup conversion additionally requires a COW in shed inventory; placement conversion requires that actor to carry a COW. If the baseline SHEEP order is not at least two, the buy change does not fire.

The gate reflects visible downstream product demand: those three shops consume MILK, while Yarn Store consumes WOOL. In the pinned engine, shop inventories are visible in `town.unlocked_shops`; the day-6 list is stable through the day. The candidate leaves V92’s market and worker routing intact outside these guarded transitions.

Exact V92 opponent: `experiments/v92_overflow_guard/candidate.py`, SHA-256 `0d5d356baa25703f1a7b753527d1b39e1c7d63478985913be5b3c2550261b806`. V50 SHA-256: `e6b50128e023e3b9fafa1841e4cd520c5e581acb48e8628657585c18272eab2b`; V56 SHA-256: `d9e9670921b62afedfa8cbc7086d2a2ec19e153ee26006cef477eadd462bd19c`. Pinned engine SHA-256: `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e` (kaggle-environments 1.32.7).

## Development results

All outcomes below are grouped by distinct seed, with both seat orders run. Margins are candidate cash minus opponent cash.

| Candidate / panel | Seeds | Triggered | Fired-seed W–L | Mean margin when fired | Mean margin overall | No-op outcomes | Errors/timeouts |
|---|---:|---:|---:|---:|---:|---:|---:|
| Unconditional swap vs V92 | 150001–150080 | 80/80 | 44–36 | +$723.06 | +$723.06 | 0 | 0 |
| Any MILK sink vs V92 | 150001–150080 | 48/80 | 35–13 | +$1,875.50 | +$1,125.30 | 32 ties | 0 |
| MILK sink, no Yarn vs V92 (confirmation) | 150021–150080 | 36/60 | 28–8 | +$1,977.80 | +$1,186.68 | 24 ties | 0 |

On the same 60-seed confirmation interval, the broad any-MILK-sink gate triggered on 39 seeds (30W–9L, +$1,892.36 among triggered seeds, +$1,230.03 overall). The no-Yarn rule excludes three additional swaps (two wins and one loss) and has a similar overall margin; the current development panel does not show a large causal advantage from excluding Yarn Store. The no-Yarn predicate is retained as the frozen confirmation candidate because it has an explicit wool-market rationale and was specified before the disjoint 60-seed run.

The initial 20 seeds 150001–150020 were used for rule exploration, so their selected-rule result is not counted as independent confirmation. On that exploratory slice, no-Yarn fired on six seeds with five wins and one loss (+$3,289 fired-seed mean). Do not pool that selected result with the 60-seed confirmation when estimating future performance.

| Opponent control, frozen no-Yarn candidate | Seeds | W–L by seed | Mean margin | Median margin | Errors/timeouts |
|---|---:|---:|---:|---:|---:|
| V50 | 150001–150015 | 14–1 | +$1,570.13 | +$602 | 0 |
| V56 | 150001–150015 | 7–8 | +$3,348.73 | −$4,812 | 0 |
| Exact V92 vs V56 control | 150001–150015 | 7–8 | +$1,629.53 | −$6,861 | 0 |

The V50/V56 candidate panel’s per-seed results are in `runs/milk_sink_no_yarn_vs_v56_v50_spent15/seed_opponent_margins.csv`; the exact V92-versus-V56 control is in `runs/v92_vs_v56_spent15/seed_opponent_margins.csv`. Compared with exact V92 on the same 15 spent seeds, the no-Yarn candidate increased its mean margin versus V56 by $1,719 and its own mean cash by $1,746. V56's mean cash increased by only $27. The seed-level W–L record stayed 7–8 for both candidates, and the median stayed negative, so this small panel does not show a reliable change in V56 outcomes. The V101-versus-V56 mean is skewed by large wins.

## Artifacts

- `candidate_unconditional.py`, `candidate_milk_sink.py`, `candidate_milk_sink_no_yarn.py`; `candidate_primary_milk_no_yarn.py` is an unrun alternative and is not the frozen candidate
- `runs/unconditional_vs_v92_retry/report.json` and `unconditional_seed_margins.csv`
- `runs/milk_sink_gate_vs_v92_dev80/report.json` and `seed_margins.csv`
- `runs/milk_sink_no_yarn_vs_v92_confirm60/report.json` and `seed_margins.csv`
- `runs/milk_sink_no_yarn_vs_v56_v50_spent15/report.json` and `seed_opponent_margins.csv`
- `runs/v92_vs_v56_spent15/report.json` and `seed_opponent_margins.csv`
- `summarize_panel.py`, `summarize_opponents.py`

No Kaggle submission was made. Stop before opening or running any fresh holdout.

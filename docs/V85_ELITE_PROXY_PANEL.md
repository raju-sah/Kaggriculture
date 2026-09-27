# V85: V56 versus elite proxies — the local yardstick is valid after all

Read-only. Eight already-spent seeds, both seat orders, 16 games per proxy, 48 games total. No new
seeds, no submission, no agent code edited.
Runner: `.venv/bin/python -m simulation.tournament`. Engine Kaggriculture 1.32.7, exact loader.
Artifacts: `experiments/v85_baseline/runs/v56_vs_elite_proxies/`.

## Source hashes

| File | SHA-256 | Role |
|---|---|---|
| `agents/v56_agent.py` | `d9e9670921b62afedfa8cbc7086d2a2ec19e153ee26006cef477eadd462bd19c` | candidate |
| `experiments/boey_agent.py` | `75e9924d5d6c8a68…` | elite proxy (leaderboard ~3,041) |
| `experiments/lizs_agent.py` | `9c374f64e8e82027…` | elite proxy (Lizs backbone) |
| `experiments/ernnn_agent.py` | `4fe6d1584f3cba03…` | elite proxy |

Seeds: 92802, 94700, 95300, 95600, 95500, 95100, 93700, 95611.

## Result

| Proxy | W | L | Win rate | 95% Wilson | Median margin | Mean candidate coins |
|---|---:|---:|---:|---|---:|---:|
| boey | 16 | 0 | **100.0%** | [80.6, 100.0] | **+57,032** | 121,580 |
| ernnn | 16 | 0 | **100.0%** | [80.6, 100.100] | +31,924 | 97,234 |
| lizs | 15 | 1 | 93.8% | [71.7, 98.9] | **+2** | 94,991 |
| **Total** | **47** | **1** | **98.0%** | — | — | — |

By seat: seat 0 **24-0** (100%), seat 1 **23-1** (95.8%). Zero errors, zero timeouts.

## The prediction in V84's write-up was wrong

V84 stated: "my honest expectation is that step 1 is likely to show we *lose* to the elite proxies."
**That is falsified.** V56 does not merely survive elite-level opponents, it beats all three
overwhelmingly:

- vs **boey**, the agent whose recorded elite finishes are 2,900–3,041, V56 wins **16/16** with a
  median margin of **+57,032 coins**. That is a rout, not a coin flip.
- vs **ernnn**, **16/16**, median **+31,924**.
- vs **lizs**, **15/16**, but the median margin is **+2 coins** — the same artefact signature as the
  V54/V56-self rows. lizs is the Lizs backbone, which V56 descends from, so this is a near-identical
  lineage matchup, not evidence of strength.

**The yardstick is valid and it is not saturated.** This contradicts the concern that drove V84's
recommendation. Local measurement against strong opponents has resolution: 16/16 with a +57,032
median is unambiguous, and it is the first strong local signal in the project.

## What this implies about the score gap

The local evidence and the leaderboard now have to be reconciled:

- V56 beats a boey-class agent 16/16, median +57,032 coins, and finishes at 121,580 mean coins.
- Yet the live public score is **1,181.0**, against a top-10 cutoff of 2,892.8 and a leader at
  3,083.9.
- Elite winners in the 100-game corpus average 108,339 closing coins. V56 against boey averages
  **121,580** — *above* the elite-winner mean.

So V56 is **beating elite agents locally while scoring ~1,180 publicly.** Either the ladder pairs
against substantially stronger policies than the local proxies, or the public score is measuring
something other than per-game coin margin (episode sample size, opponent pool, or variance across a
small number of ladder episodes).

The first hypothesis is the more likely one, and it is testable: the local proxies are re-derivation
or imitation agents, not the actual top submissions. Winning 16/16 against a *reconstruction* of
boey does not mean winning against boey.

## Honest answer to "+500 to +1000 gain"

**I cannot promise that, and I want to be direct about the base rate.**

What the project history actually shows:

| Submission | Public score | Note |
|---|---:|---|
| v50 | 1,233.2 | best ever |
| v52 | 1,219.4 | |
| v55 | 1,131.2 | |
| v56 | 1,181.0 | current live (id 56544001) |
| v66 | **464.6** | latest attempt — a severe regression |

Six consecutive local iterations (v51→v56) moved the public score in a band of roughly
1,080–1,233, i.e. **~150 points of total drift across all of them**. A +500 to +1,000 gain is
3–7x the entire observed historical range of this project's tuning. There is no evidence in the
record that local iteration produces gains of that size, and one recorded attempt (v66) lost
**716 points**.

The honest position: +500 to +1,000 from further tuning of this lineage is **not supported by any
evidence I have**. I will not claim it, and I would be misleading you if I said otherwise.

What I can say honestly:
- There is a **large measurable local headroom signal** — the elite-proxy margins are wide, so
  improvements are detectable, unlike the saturated self-play panel.
- Whether any of that converts into **public score** is currently unproven, and V85 is the first
  result that even makes the question coherent.

## Recommendation

Do **not** submit yet. A submission costs a ladder slot and the record shows the downside is
severe (v66: −716). The next step is to find out whether *any* local change moves the elite-proxy
margin at all, using the panel that now demonstrably has resolution. If a change moves boey/ernnn
margins, that is a real signal worth carrying toward a submission. If nothing does, no submission
should be made and the strategy needs rethinking.

## Limits

- 8 spent seeds, 16 games per proxy. The Wilson lower bound at 16/16 is 80.6%, so "100%" here is
  16/16, not a proven rate.
- The elite proxies are local re-derivations, not the actual top submissions. Beating them is
  necessary, not sufficient.
- lizs and V56 share a backbone, so that row is near-identical-policy and its +2 median margin
  should not be read as a strength result.
- The v66 score comparison relies on the recorded submission list, not on a re-run.
- No fresh holdout. Nothing here supports a promotion or submission claim.

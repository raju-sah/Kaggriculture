# V84: feed-budget overlay — REJECTED before the panel

Read-only analysis plus one candidate that was **not** promoted. No new seeds spent on it, no panel
run, no submission. Recorded because the rejection is informative and the candidate is retained for
audit.

## What was built

`experiments/v84_feed_budget/candidate.py`, sha256
`7c4ad6e83466de8c65fe96c5f38d6ab3bf669bbed1ebd9468fa8a2f50054faa0`, wrapping the frozen
`agents/v56_agent.py` (sha256 `d9e9670921b62afedfa8cbc7086d2a2ec19e153ee26006cef477eadd462bd19c`).
One overlay: when the farm has animals and shed WHEAT is below 40, buy enough wheat to restore the
reserve, subject to cash and the 10-order market cap. Loader contract verified
(`_kaggle_submission_entrypoint` is the last callable, per
`experiments/v81_expert_switch/test_loader_contract.py`).

## Why it was rejected

**It does not do what the hypothesis said.** Offline replay of a saved V56 game: the overlay changed
**592 of 719 frames**, adding a `BUY_PRODUCT WHEAT` order. It fired on essentially every hour of
every day, including at cash 42. The reserve condition never clears because V56's wheat is consumed
by its own feeding loop as fast as the overlay replenishes it, so `shortfall` is positive almost
permanently. The overlay is a constant drip, not a reserve top-up, and it spends farm cash in a way
V56 never chose to.

**The mechanism it targeted is too small to matter.** The engine grants base yield 1 unit on every
production day regardless of feeding, and adds the `pending_care_bonus` only if the animal was fed
*and* cared on that day (`_daily_refresh_animals`, lines 821-830). So a missed feed costs at most
**+1 unit**, never the base yield:

| Animal | Production interval | Max loss per missed day |
|---|---:|---|
| COW | 2 days | 1 unit / 2 days |
| SHEEP | 3 days | 1 unit / 3 days |
| GOOSE | 1 day | 1 unit / 1 day |

V56's reference game did show chronic pressure — 11 animals at `consecutive_unfed >= 1` on day 29 —
but it triggered **zero escapes** and finished 71,344 vs 71,325, a 19-coin game. The measured feed
deficit is real but its ceiling is a few dozen units, while the median contested margin in the
576-game panel is **13,920 coins**. Feeding better is not a path to that.

## The finding that actually matters: the panel has a duplicate-opponent problem

From the 576-game V56 panel, per-opponent margin distributions are **bit-identical across lineages**:

| Opponent | W/L | Median margin | Margin vector identical to v50? |
|---|---|---:|---|
| v50 | 46-26 | +8,812 | (reference) |
| v52 | 46-26 | +8,812 | **yes** |
| v53 | 46-26 | +8,320 | no |
| v55 | 46-26 | +8,320 | no |

v50 and v52 produce **the same margin on all 72 shared game keys (100%)**, and v53/v55 likewise
(100%). v50 vs v53 differ on 0% of keys. So the "eight opponent panel" is really **five distinct
policies**, and three of them are v50's policy.

Note the source files are *not* identical — v50 is `e6b5012e…` and v52 is `a53025fc…` — so this is
behavioural equivalence, not file duplication. The different hashes come from metadata or dead code;
the executed policy is the same. This was verified by comparing per-game margins, not by inspecting
the sources line by line.

Restricting to genuinely distinct opponents:

| Group | W-L | Win rate | Median margin |
|---|---|---:|---:|
| v48 | 51-21 | 70.8% | +11,668 |
| v50 / v52 | 46-26 | 63.9% | +8,812 |
| v53 / v55 | 46-26 | 63.9% | +8,320 |
| v51 | 41-31 | **56.9%** | **+1,301** |
| v54 | 63-7-2 | 87.5% | +2 (artifact) |
| v56 self | 7-7-58 | n/a | 0 (81% exact ties) |

**v51 is the only opponent that is genuinely hard for V56**, and it is hard in a specific way: its
median *loss* margin is only **−4,114** against V56's other losses at −20,000 to −31,000. V51 is a
near-mirror matchup decided on a small margin, not a wall.

## Corrected understanding of the margin distribution

Across the 504 contested games (self-play excluded):

- Median |margin| **13,920**; p25 4,231; p75 20,754.
- Only **18%** are decided by under 2,000 coins and **27%** by under 5,000.
- Wins median **+12,763**; losses median **−22,939**.

This is the opposite of what the elite corpus suggested locally (V83: 50% of elite games decided
under 5,000). The local panel's margins are *wider* than elite margins, which means the local panel
is dominated by genuine policy differences against this older lineage, not by coin-flip noise. The
v54 and v56-self rows are the exceptions and are artifacts.

## Consequences for the 100% target

The 100% requirement is arithmetically out of reach on this panel, and now for a concrete reason
rather than a hand-wave:

- Three of the eight listed opponents are the same policy. Winning 10/10 "against v50, v52" means
  winning 20 games against one opponent.
- Against v50/v52, a loss costs a median of **−29,797** and a win is worth **+15,211**. This is a
  genuine strength gap, not a coin flip.
- v51 is the closest matchup and the only plausible place to gain.

A realistic goal is raising the **distinct-opponent** win rate above 60% with a seed-bootstrap
interval that excludes 60%. The 100% figure should be dropped as a target rather than pursued and
quietly restated when it is not met.

## What the elite evidence still supports, and what it does not

Still supported (V83): commit opening capital into animals and soil rather than holding cash;
improve asset-to-cash conversion in days 12-23. Still unsupported: sheep-for-goose substitution
(refuted by day-12 herd composition), land-count heuristics, and — as shown here — feed-budget
top-ups as a meaningful lever.

## Limits

- The V84 overlay was rejected on an offline single-replay inspection plus engine-rule reading. It
  was **not** run on a panel, so its true effect is unknown; "too small to matter" is an argument
  from the engine's yield rule and the measured margin distribution, not a measured score.
- Duplicate-opponent detection was verified by comparing per-game margins across all 72 shared
  keys (100% match for v50/v52 and v53/v55, 0% for v50/v53). The agents' source SHA-256 values
  differ, so the equivalence is behavioural rather than textual and was not confirmed by a
  line-by-line source diff.
- No fresh seeds were spent. Nothing here supports a submission or promotion claim.

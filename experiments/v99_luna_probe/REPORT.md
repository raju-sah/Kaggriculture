# Independent V99 day-6 sheep-to-cow probe

## Finding

The same-route substitution is engine-feasible. On seed 92600 in both seat orders, the isolated V92 wrapper converted one unit from the day-6 `BUY_ANIMAL SHEEP 2` cohort into `SHEEP 1` plus `COW 1`; the existing farmer picked up the cow at day 6 hour 8 and placed it in the existing pasture route at hour 12. The worker path, slot, and daily service actions remained on the tape. The cow stayed alive through day 29 and produced five observed MILK harvests totaling 24 units. The replay also shows accepted MILK sale cash. This directly disproves the claim that 238 matched baseline pickups make a species substitution unreachable.

## Frozen candidate and probe method

`candidate.py` is an isolated wrapper around the V92 source embedded in the V98-R1 standalone artifact. Its only strategic edits are the day-6 quantity split, changing one existing sheep pickup when the new cow is in the shed, and changing that carrier's sheep placement to cow placement. The market keeps the original wool sale ahead of animal buys. The exact tournament loader selected this file; tournament metadata records candidate SHA `15a94e4be00339597ec4577ac3195f57c2e5218ac082db2275eae897ba178ea9` (see raw `games.jsonl`; the SHA in that field is authoritative). The opponent was the exact frozen V92 SHA `0d5d356baa25703f1a7b753527d1b39e1c7d63478985913be5b3c2550261b806`. Engine was kaggle-environments 1.32.7, SHA `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`.

Seed 92600, both seats: candidate finished with $103,717 against $98,938 (+$4,779) in each seat order, with zero errors/timeouts and zero cash-reconstruction mismatches. Frozen V92 self-play on this spent seed finished $99,145 per seat, so candidate own cash was +$4,572 versus that control. This is one-seed evidence only.

The lifecycle audit in `audit_replays.py` observes: purchase at d6h6; COW pickup at d6h8; COW placement at d6h12 on tile (5,3); FEED on 22 production days, CARE on 23 days; MILK harvests on days 15, 18, 21, 24, and 27 (6, 6, 3, 6, 3 units); the animal remains a COW on a PASTURE at the final frame. The candidate's whole-farm accepted sales in that replay were $44,318 MILK and $5,238 WOOL. These sales are market totals, not a causal allocation to the substituted cow.

## Ten-seed development screen

The ten seeds were already spent in prior V92/V98/V97 work: 92600–92604, 92802, 93700, 94700, 95100, 95200. Each ran in both seats against exact V92 and V50 (40 games total); there were no agent, infrastructure, or timeout errors. The seat-swapped outcomes were identical, so the independent unit is ten seeds, not twenty games.

| Opponent | Seed-level results | Mean margin | Median margin |
|---|---:|---:|---:|
| V92 | 5W–5L | +$999 | +$635 |
| V50 | 6W–2L–2D | +$1,508 | +$1,152 |

Paired margins (candidate minus opponent cash):

| Seed | vs V92 | vs V50 | d6 milk / wool quote | d6 unlocked shops |
|---:|---:|---:|---:|---|
| 92600 | +4,779 | +5,315 | 205 / 218 | Pizza Shop, Farmers Market |
| 92601 | +4,446 | +4,890 | 205 / 218 | Pizza Shop, Brunch Spot |
| 92602 | −1,003 | $0 | 205 / 221 | Ice Cream Shop, Yarn Store |
| 92603 | −3,335 | −2,962 | 183 / 233 | Yarn Store, Pet Cafe |
| 92604 | +3,381 | +3,772 | 205 / 218 | Pizza Shop, Brunch Spot |
| 92802 | −2,493 | −2,053 | 183 / 221 | Pet Cafe, Yarn Store |
| 93700 | +4,758 | +5,157 | 207 / 218 | Pizza Shop, Ice Cream Shop |
| 94700 | −262 | +151 | 183 / 218 | Brunch Spot, Farmers Market |
| 95100 | −1,817 | −1,342 | 205 / 218 | Ice Cream Shop, Pet Cafe |
| 95200 | +1,532 | +2,153 | 183 / 218 | Brunch Spot twice |

The replay-grounded accepted MILK / WOOL sale cash against V92 was respectively: 92600 $44,318 / $5,238; 92601 $42,093 / $5,238; 92602 $34,287 / $50,512; 92603 $5,148 / $31,429; 92604 $36,610 / $7,272; 92802 $5,756 / $24,026; 93700 $44,670 / $7,991; 94700 $8,187 / $7,991; 95100 $18,413 / $32,592; 95200 $21,906 / $6,456. Each audited run successfully placed and retained the cow and harvested 24 MILK units; each had 22 feed days, 23 care days and zero cash mismatch.

The losses do not line up with one market quote threshold. All six non-positive seeds have d6 MILK quotes between $183 and $205, while winners include both $183 and $207. Four of five wins coincide with Pizza Shop; the fifth is Brunch Spot twice. Yarn Store is present in three losing shop mixes and none of the winning mixes, but Ice Cream Shop also loses in two cases. The pinned engine has no weather mechanic (`kaggriculture.py` contains no weather state or transition), so weather cannot explain this split. These are correlations in a small spent panel, not an estimated treatment effect.

## Exploratory shop gate

To avoid tuning on seed IDs, `candidate_pizza_gate.py` adds one visible, pre-swap condition: the same `PIZZA_SHOP` check guards BUY, PICKUP, and PLACE, and substitution occurs only when `PIZZA_SHOP` is already in `town.unlocked_shops` at the day-6 purchase decision. The engine defines Pizza Shop as a direct MILK sink (`kaggriculture.py`, `SHOPS` lines 104–106). The d6 shop list stays stable during that day: shop draws happen at end of day when the next day is divisible by three, so the day-6 h6 decision sees the shop set drawn at the day-5 boundary. It was screened on the same spent seeds, in both seats against both opponents; this is exploratory and reuses the unconditional screen's development set.

| Gated variant | Games | W–L–D | Mean margin | Median margin | Errors/timeouts |
|---|---:|---:|---:|---:|---:|
| vs V92 | 20 | 8–0–12 | +$1,736 | $0 | 0 |
| vs V50 | 20 | 20–0–0 | +$2,258 | +$795 | 0 |

The corrected all-chain gate was re-run after the safety invariant change. Tournament metadata records its SHA `7e1cede46e4d6c8ad6ae81af66cc1c49d205e7c8c1a9a9cde24f548b383a85aa`; V92 and V50 opponent hashes match the frozen files; errors, timeouts, and infrastructure errors are all zero. The gate fires on four seeds, all four positive against V92; the other six are no-op ties against V92. It skips seed 95200's smaller positive swap and seed 94700's small loss. Against V50, all ten seed outcomes are wins. This is a promising development signal, but it is too small and selected to justify promotion. The all-chain gate hash is now frozen for any independently chosen holdout; do not tune it on a holdout.

## Artifacts

- Unconditional standalone candidate: `candidate.py` (SHA-256 `15a94e4be00339597ec4577ac3195f57c2e5218ac082db2275eae897ba178ea9`).
- Exploratory Pizza gate variant: `candidate_pizza_gate.py` (frozen all-chain gate SHA `7e1cede46e4d6c8ad6ae81af66cc1c49d205e7c8c1a9a9cde24f548b383a85aa`, re-screen in `runs/pizza_gate_v2_vs_*`).
- Full paired run records: `runs/panel_vs_v92/` and `runs/panel_vs_v50/`; seed-92600 transition replays: `runs/seed92600_both_seats/`.
- Settlement and lifecycle audit: `audit_replays.py`; per-seed metrics: `panel_metrics.csv`; tournament summaries and logs remain under each `runs/` directory.

**Recommendation: the pickup-closure no-go is disproven. Keep the same-route swap branch alive. The unconditional variant is mixed in development; the visible Pizza Shop gate is the stronger exploratory candidate, but neither screen is holdout evidence. No submission was made.**

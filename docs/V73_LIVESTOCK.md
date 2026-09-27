# V73 livestock expansion screen

## Decision

Do not promote the V73 expansion. It was a state-driven attempt to grow the goose herd after V70's adjacent NE land unlock, using two otherwise unallocated NE cells as extra coops. The policy gated the extra pair on a bakery/brunch buyer, an egg quote of at least $35, and the day-14 placement window. It kept V70's crop plan and staffing targets unchanged. The spent-seed 94700 screen produced only a $315 mean cash lift over V70 in head-to-head self-play, and V73 averaged $55,121.50 against V56—$1,944.50 below V70's earlier $57,066 baseline. The own-cash gate failed, so no other seeds were tested.

V73 source SHA-256: `6217b21efcebedc88facc92e470050c170ac9f62c47ac39666564aadc7987304`.
Frozen base SHA-256: `2002db9b4bbf20c654805adc35617eb787be3e9cb64e5aae46ae1044aad3b73e`.

## Evidence and policy rationale

The engine defines a goose at $300, with egg production beginning four days after placement and then daily; a cow costs $400, begins milk production after eight days, and produces every other day. Every occupied animal tile requires one wheat daily to avoid escape after two consecutive unfed days. Care increases the next production event only when combined with feed on the same day; each animal can also produce one collectable fertilizer per day. A coop is a single-animal tile, so growing the goose count requires additional coops, placement actions, daily feed/care/collection, and egg harvest and sale. These rules are in the installed engine at `.venv/lib/python3.12/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py` (`ANIMALS`, `_new_animal`, `_daily_refresh_animals`, and unit action handlers).

The saved public elite panel (`docs/V63_ELITE_PANEL.md`, derived from `experiments/v63_elite_panel/profiles.json` and its 50 replay states) supports a test, not a fixed roster: day-6 winners had a median 1.5-animal lead, and their whole-game paired median net product-market difference included +$985 for eggs, +$2,184 for milk, and +$334 for fertilizer. The panel also shows substantial heterogeneity and is observational. V73 therefore used observed shop/price state and available spare land rather than copying another player's action schedule.

## Paired spent-seed result

All matches used the exact local tournament runner, both seat orders, and seed 94700. Replay settlement through the installed engine reconciled 1,438 transitions per game with zero cash mismatches.

| Opponent | V73 final cash, seat 0 / seat 1 | V73 mean own cash | Result | Reference |
|---|---:|---:|---:|---|
| Frozen V70 | $54,189 / $54,189 | $54,189 | 2–0, mean margin +$315 | `experiments/v73_livestock/spent94700_vs_v70/` |
| V56 | $60,957 / $49,286 | $55,121.50 | 0–2 | `experiments/v73_livestock/spent94700_vs_v56/` |
| Frozen V70 vs V56, prior paired run | $57,066 / $57,066 | $57,066 | 0–2 | `experiments/v70_capacity/spent94700_vs_v56/` |

The close V70 comparison shows a small shift rather than a durable own-cash gain. Against V70, V73 accepted $73,756 in sales versus $70,668 for the opponent. Egg receipts were $5,931 versus $3,604, milk $12,800 versus $12,951, and fertilizer $12,969 versus $11,507. V73 spent $1,200 on geese versus $600, and $5,382 on bought wheat versus $4,638. Higher egg and fertilizer receipts were mostly consumed by the extra animal and feed burden; one purchased goose never produced.

## Placement failure and limits

The replay shows only three live geese at day 12 and day 29, with one additional goose stranded in the shed from day 12 through close. V73's task generator stopped targeting four geese when its day-14 expansion gate expired. The existing `(2, 2)` coop also remained unavailable while occupied by a crop during the purchase/build window; the new NE slots at `(5, 0)` and `(6, 1)` did accept geese. Thus the candidate both bought into a placement bottleneck and disabled the follow-up placement work too early. Expanding `_empty_structures` to the full board was necessary to see the new coops, but did not resolve the occupied base slot or the expired goal.

This implementation defect does not justify another tuned replay: even before a placement correction, V73's own cash was below V70 on the comparison against V56, and its V70 self-play gain was only $315. More geese would also increase recurring feed and service demand, while the proposed output includes market acceptance and price competition. No evidence here establishes that a corrected animal expansion would recover its full costs.

## Provenance

- Candidate: `experiments/v73_livestock/agent.py` (SHA above), copied from the frozen V70 source and changed only for conditionally enabled spare-NE coops, a goose goal of four, and full-board empty-structure scanning.
- Exact game results, logs, and replays: `experiments/v73_livestock/spent94700_vs_v70/` and `experiments/v73_livestock/spent94700_vs_v56/`.
- Exact accepted-sale reconciliation: `experiments/v63_elite_panel/accepted_sales.py` against each retained V73 replay.
- Top-player state evidence: `docs/V63_ELITE_PANEL.md`, `experiments/v63_elite_panel/profiles.json`, and saved public replay files in `experiments/top_episodes/`.
- No action tape was replayed or copied. No fresh seeds or submission were used.

## Placement correction and final screen

After the first screen, the stranded bird was diagnosed as two coupled state-machine errors: V73 stopped reserving the original coop cell at two placed geese, allowing the day-12 melon harvest/replant cycle to occupy it again; and the market gate expired on day 14 even if a fourth goose was already purchased but awaiting a usable tile. The final V73 source now reserves coop cells until the live goose goal is placed, keeps the four-goose service goal while more than two geese are owned (including shed/carried inventory), and continues building through day 18. `_empty_structures` scans the full board so an unlocked NE coop is discoverable. The corrected source SHA-256 is `a093f27dbbc1256cb927ec951a6b05565308dc86fc9c1a84b5cd9982ae3bc37e`.

The corrected seed-94700 replay placed all four geese by day 15 against V70 and by day 20 against V56; no goose remained in the shed at close. The paired results still fail the own-cash criterion:

| Opponent | Corrected V73 own cash by seat | Mean own cash | Margin / result |
|---|---:|---:|---:|
| V70 | $55,616 / $55,616 | $55,616 | +$1,559, 2–0 |
| V56 | $60,790 / $50,156 | $55,473 | 0–2 |
| Frozen V70 vs V56 reference | $57,066 / $57,066 | $57,066 | V73 mean is −$1,593.50 |

Corrected V73 accepted-sales totals in these games were $76,072 against V70 and a $73,153 mean against V56. Against V70, accepted egg, milk, and fertilizer receipts were $7,458, $12,769, and $13,319; bought wheat cost $6,157 and goose purchases cost $1,200. Against V56, the two seat-specific egg receipts were $6,483 and $6,956, milk was $11,018 in both games, and fertilizer was $6,657 in both; mean accepted sales were $73,153. These receipts confirm that the new herd produced and sold more eggs, but the route still does not convert it into a cash lead over the stronger V70 reference.

A first attempted corrected run in `fixed_spent94700_*` failed because the edit placed `goose_goal` in the legacy fallback instead of `_bridge_agent`; the tournament correctly marked two candidate errors and no performance result. The repaired source was then rerun in `fixed2_spent94700_*`, with zero candidate or opponent errors and zero timeouts. Only the successful `fixed2` games count in the table above. Per the screen's predeclared gate, no further seeds or variants were run.

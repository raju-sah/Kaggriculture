# V59 teacher-run diagnostics

## Scope and result

This audit uses only the completed `experiments/v59_state_teacher/dev95501_95519`
report and its saved replays. It does not alter the teacher files or launch
games. There is a report-scope discrepancy: `report.json` covers seeds 95501–95519
against **v50, v53, and v54** (114 games), not v50/v54/v56. Findings for v56
cannot be inferred from this run.

The teacher/collector scored 79–35 (69.3%) overall. This is not a learned
student result. Against v50 it scored
28–10; all 10 losses came from five two-seat seed pairs: 95503, 95508, 95515,
95516, and 95518. Against v53, the losses clustered on those same five seeds
(plus 95513). Against v54 it scored 25–13; 13 losses spanned seeds 95506,
95508, 95511–95513, 95515, 95517, and 95518. Most v54 losses were narrow;
seed 95506 lost by only 10 coins. The repeatable large losses are therefore
seed/regime-conditioned rather than a broad seat failure.

## State and action evidence

`student.py` appends a hand-drop perturbation guarded by
`isinstance(pos, dict)`. The replay observations store hand positions as
`[x, y]` lists. In sampled loss and win replays, the guard is never reached, so
the scored student run did not apply its stated perturbation and is effectively
the frozen v57 policy for worker actions. The observed farm action tape confirms
this: comparing candidate seat 0 on v50 seeds 95508 (loss) and 95501 (win), the
farmer commands and hand commands match on **720/720 turns**; only the market
list differs, on 23/720 turns. The farm plan consequently leaves little room
for shop-regime adaptation.

The fixed worker route is not generally issuing impossible commands. Aligning
each recorded action with the preceding frame's observation (the action at
frame *t* follows the observation at *t−1*), a direct precondition audit found
66/3,301 obvious no-op crop/animal operations (2.0%) in the v50 95508 loss and
the same 66/3,301 in the 95501 win. v54 samples were similar (66–68/3,301).
Most detected no-ops were `COLLECT_FERTILIZER` with no collectible output (26),
`HARVEST` without yield (14–16), and already-satisfied `WATER` (12). These
counts do not distinguish losses from wins and are not a strong causal lead.

Seed 95508 against v50 is a clear divergence point: the candidate led by 460
coins at step 360, then trailed by 15,849 at step 480 and 32,563 at the end.
Its shop sequence was SMOOTHIE_SHOP, YARN_STORE, ICE_CREAM_SHOP, BAKERY,
FARMERS_MARKET, YARN_STORE, BAKERY, PIZZA_SHOP. MILK remained valuable
($154–$211 through step 600), WOOL stayed above $230, while STRAWBERRY fell
from $187 at step 480 to $30 at step 600. By comparison, seed 95501 against
v50 won by 12,061 even though MILK and WOOL prices had already reached $1 by
step 360. This rules out a simple price-floor or absent-shop trigger as a
sufficient explanation; the loss reflects the opponent-relative yield/sales
mix and timing, not one low price in isolation.

There is one narrower, falsifiable production-mix lead. In seed 95508, the
town unlocked YARN_STORE on days 6 and 18 while WOOL stayed above $200. The
candidate purchased 7 GOOSE and 4 SHEEP total, then sold 72 WOOL; v50 purchased
11 SHEEP total and sold 379 WOOL. Seed 95518 had YARN_STORE on days 9 and 12,
WOOL above $180, and the same gap (46 versus 379 WOOL sold), alongside a
$39,441 loss. On seed 95501, YARN_STORE did not unlock until day 24 and WOOL
had collapsed to $1 by day 15; the candidate's goose-heavy mix still beat v50
by $12,061. This supports a testable rule: redirect some optional goose
purchases to sheep only when YARN demand arrives early and the observed WOOL
price remains high. The replay evidence does not set a safe quantity or
threshold, and this intervention has not been tested.

## Decision

**No-go for the V59 teacher/student improvement claim.** The hand-drop
perturbation was inactive, so the teacher/collector games measure frozen v57
behavior and do not show that imitation or state-conditioned student actions
improve play. No additional games were run. The sheep-for-goose rule above is a
separate hypothesis for a later, isolated development test; it should not be
treated as a result of this run.

Source artifacts: `experiments/v59_state_teacher/dev95501_95519/report.json`,
`summary.json`, and the corresponding replay files. The report's candidate is
`experiments/v59_state_teacher/student.py`; its checked-in appended perturbation
is inactive on the recorded observation shape. The report lists v53, not v56,
so this audit makes no claims about a v56 matchup.

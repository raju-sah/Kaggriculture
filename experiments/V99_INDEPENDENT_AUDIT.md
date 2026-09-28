# V99 independent engine feasibility audit

Read-only audit for the Pixel Canary candidate. The V98 `238 matched / 0 unmatched` buys/pickups result describes the **unchanged baseline by day and species**. It does not prove a changed purchase and matching changed pickup cannot ride the same worker route.

- Pinned engine `kaggriculture.py:358-375`: `PICKUP` accepts either animal species from the shed. `PLACE` at lines 377-392 checks structure and vacancy. Both `COW` and `SHEEP` require `PASTURE` (animal config near lines 21-22), so a sheep pasture can hold a cow.
- Day-6 cohort: V50/V92 step 150 (day 6 hour 06) buys `SHEEP 2`; the route then picks those up at steps about 152/153 and places them at about 155/156. Recheck the replay's observation/action one-step offset before editing.
- Minimal counterfactual: buy `SHEEP 1` plus `COW 1`; change exactly one matching worker `PICKUP SHEEP` to `PICKUP COW` and its downstream `PLACE SHEEP` to `PLACE COW`. Leave worker movement and pasture coordinates unchanged. Preserve sell-before-buy market order. A cow costs $400 versus $500 for a sheep, but its production timing and milk quote differ.
- FEED/CARE actions and animal HARVEST use the occupied tile; verify they still serve the converted cow. Check MILK sale orders, accepted MILK/WOOL units and cash, animal survival, and market impact across a complete game. A changed species-label count in a baseline-only pickup audit is expected and is not itself a mismatch.
- Prior goose-to-sheep conversion in `experiments/v80_wool_route/README.md` physically fired, but the converted sheep escaped because the route did not serve their new coordinates. The same-pasture V99 swap must verify service; do not assume it.

Independent conclusion: **the proposed transition is engine-feasible in principle**, but profitability is untested. Run a tiny exact-loader probe before larger matches, then compare paired own cash against V50/V92 in both seats.

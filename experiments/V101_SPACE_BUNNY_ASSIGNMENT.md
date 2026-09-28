# Visible CommandCode assignment: independent V101 adaptive animal decision

You are the visible Herdr CommandCode worker on the free Space Bunny Alpha model.
Your prior Pixel Canary run was interrupted after prolonged zero-token stalls; it
left no candidate. Use this concise handoff instead of reconstructing old chat.

Goal: find a materially better original Kaggriculture policy than V50/V92/V56,
then give Codex a reviewable local result. Do **not** submit to Kaggle yourself.
Four competition submission slots remain. Do not print or access API keys.

Read `experiments/v99_luna_probe/REPORT.md`,
`experiments/v99_luna_probe/FRESH_HOLDOUT_RESULT.md`, and the pinned engine
shop/market rules. V99's day-6 cow-for-sheep swap physically works, but its
Pizza-only rule failed the precommitted fresh holdout: only 2/24 distinct seed
triggers, 4W/44D vs V92, and 20W/28L vs V56. Do not reuse or tune on those
holdout seeds (137501–137524) or the older 93000–93011 holdout.

Independent task, isolated under `experiments/v101_commandcode/`:

1. Derive an observable pre-swap estimate of **marginal accepted MILK vs WOOL
   value** from shops, market inventory, current farm output, and remaining
   production days. Avoid classifying seeds by exact IDs. Check that the cow
   replaces one sheep on an existing worker route; preserve buy/pickup/place
   alignment and V92 source.
2. Build one standalone exact-loader candidate with a higher trigger rate than
   Pizza-only, then test on development seeds 160001–160060 (both seats vs V92
   and V50). The other agent uses 150001–150080, so keep directories and seeds
   separate. Report per-seed own cash, decisive W/L/D, errors, lifecycle, and
   effective sample size. Do not claim 100% or top-ten readiness from local tests.
3. If development is positive, freeze hash and a fresh **different** holdout
   seed range and numerical gate in a file before running it. Ask Codex to
   review the gate. Do not run Kaggle submissions.

Avoid repeating the V93–V100 failures: wool deferral, extra unplaced cows,
worker route borrowing, broad sell holding, and day-0 sheep swap. Use exact
engine arithmetic and paired games, not an unsupported Jev profitability guess.

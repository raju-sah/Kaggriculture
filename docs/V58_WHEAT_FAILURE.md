# v58 wheat-sale overlay failure analysis

## Finding

The strongest replay-grounded explanation is feed-stock depletion followed by
livestock escape. The overlay sold WHEAT from the shed without reserving the
expansion policy's future feed supply. A step-72 probe recorded the first
overlay-only action: with Pizza Shop unlocked, $30 WHEAT, and six WHEAT in the
shed, it retained five HIRE orders and appended `SELL WHEAT 6`. In the retained
93700 AB replay, that response is serialized in frame 73. The farmer also
requested `PICKUP WHEAT 3`; the engine applies farmer and hand actions before
market orders, so the pickup ran first and the sale accepted the remaining
three units. The requested sale therefore exceeded what was left after the
route's pickup.

The sharper failure appears at the start of day 5. After overnight inventory
drop, the candidate had four WHEAT in the shed. Frame 121 sold all four for
$116. The next two frames tried to pick up two WHEAT each from shed-access
tiles, but both saw an empty shed and picked up zero. Six subsequent FEED
commands on animal tiles had no carried WHEAT and failed that day. The candidate
had six active animals at the day-5 boundary; five remained at day 6, four at
day 7, one at day 9, and none at day 10. The same trace's market audit records
only 3 milk units (zero MILK) and 3 wool units sold by the candidate, versus
the opponent's 164 MILK and 278 WOOL. Those missing livestock streams are
consistent with a large score loss.

The day-4 queue shows why the overlay needs to account for *all* same-turn
orders: at frame 119 the base queue buys one WHEAT product, then the overlay
sells two WHEAT. The audit records one buy followed by two accepted sales. At
frame 120 it sells the last shed WHEAT; the overnight drop replenishes four,
which frame 121 liquidates before the next pickup cycle. This is inventory
desynchronization between the unchanged route and its new market overlay, not
seed starvation. The engine stores crop seeds separately in `private.seeds`,
and `SELL WHEAT` reads only the shed.

## Evidence and limits

The retained replay audit for candidate seat 0 on v50/seed 93700 records 671
accepted WHEAT sales worth $19,860 and 96 fertilizer sales worth $7,189. The
first live action difference was reported at input step 72. The replay JSON
stores its resulting action in frame 73 because the action is paired with the
next serialized state; the market audit calls the transaction step 73. Across
the 12 completed matched seed/opponent/seat pairs, overlay margin change versus
frozen expansion averaged −$73,096.75 (range −$98,188 to −$48,168). Four other
v53 games were stopped after large losses, so the paired result is descriptive,
not a formal sequential test. Controls retained only game summaries, not paired
replays, so this audit cannot show the exact counterfactual animal history.

The recorded FEED failures begin after repeated shed liquidation. Some later
FEED commands also target empty structures after animals have escaped, so the
raw count of failed FEED actions should not be read as a count of missed feeds.
For the day-5 chain above, the six counted failures were checked against the
pre-action tile, `fed_today` flag, and carried inventory using the pinned engine
semantics; all six stood on live animals without carried WHEAT.

This is not explained by seed depletion: WHEAT seeds do not pass through the
shed. The sell operation itself does not draw random numbers. Engine shop RNG
is initialized from seed and day, then consumed by weed spawning and the shop
choice. The sale does not directly advance that RNG. Since there is no matched
control replay, this analysis cannot rule out later RNG-state changes mediated
by a policy-driven change to board occupancy; there is no evidence that such a
change caused the initial collapse.

## Safe next step

Do not sell WHEAT while the farm has active animals unless a route-aware reserve
proves the remaining shed/carry stock covers the next feed and pickup cycle.
For a minimal safeguard, turn off the WHEAT branch whenever any animal is
active; retain fertilizer liquidation only if its existing consumers and
market-slot ordering are accounted for. Any revised rule should be screened on
the already assigned development allocation before it is promoted.

## Reproduction from retained data

Run `experiments/v58_wheat_analysis/analyze_existing_replays.py` from the repo
root to rebuild `experiments/v58_wheat_analysis/findings.json`. It reads the
existing game summaries, replay, and transaction audit; it does not instantiate
the game engine or run matches. The source engine used for semantics is the
pinned `kaggle-environments` 1.32.7 module at
`.venv/lib/python3.12/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py`
(SHA-256 `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`).

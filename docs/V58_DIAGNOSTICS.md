# V57 reset candidate loss diagnosis

## Finding

The 26 losses in the fresh 80-game panel are concentrated in two seeds rather
than spread across the five-seed panel. Seed 92802 accounts for 12 losses out
of 16 games; seed 92804 accounts for 14/16. The candidate won every game on
92800, 92801, and 92803. On 92802 it lost in both seats to v48, v50, v51, v52,
v53, and v55. On 92804 it lost in both seats to v50–v55, and to v56 in seat 0.
This is consistent with a seed-specific market and shop-demand mismatch, not a
seat asymmetry or the day-reset issue fixed in the candidate.

## Minimal replay

The decisive reproduction is candidate vs v48, seed 92802, candidate in seat 0.
It reproduces the frozen panel exactly: candidate finishes with 70,037 coins,
v48 with 76,605, a 6,568 loss. The candidate leads at step 480/day 20 (38,345
to 32,277), but is behind at step 600/day 25 (46,856 to 49,662). The complete
replay is `experiments/v58_diagnostics/replays/v48-seed-92802-ab-repeat-0.json`.

The market history explains the reversal. Seed 92802 unlocks BAKERY on day 3,
YARN_STORE on day 6, another BAKERY on day 9, another YARN_STORE on day 12,
FARMERS_MARKET twice on days 15 and 18, and PIZZA_SHOP only on day 21. Until
late in the season, the town has no shop consuming milk and only delayed
strawberry demand. While this shop mix is active, observed prices fall sharply:
MILK goes from $181 at step 168 to $1 by step 384; STRAWBERRY goes from $151 at
step 384 to $1 around step 484; FERTILIZER declines from about $90 to single
digits. The candidate first sells MILK at step 340 when it is $97 and
STRAWBERRY at step 404 when it is $101, then sells further inventory after
those markets have nearly bottomed out. For example, it sells 6 strawberries
at step 404 and additional 6-unit orders later, when the price is $1.

Seed 92804 shows the same exposure with a different demand mix. BRUNCH_SPOT,
SMOOTHIE_SHOP, and ICE_CREAM_SHOP unlock on days 3, 6, and 9; YARN_STORE does
not appear until day 18. WOOL falls from $187 to $1 by about step 372, and MILK
reaches $1 late in the game. In the candidate-v51 seat-0 replay, the final
margin is only 538 coins (114,967 to 115,505), which shows that the panel losses
on this seed are often close even though they are consistent across opponents.
That replay is `experiments/v58_diagnostics/replays/v51-seed-92804-ab-repeat-0.json`.

The engine confirms that the town consumes each unlocked shop's products every
four steps and the town center consumes products every 24 steps. Shop unlocks
are seed-keyed, while farm output and player market orders add supply. Prices
respond to this shared inventory. The candidate's general price-drift overlay
reacts once decline is visible, but that signal arrives after production has
already built inventory in goods with weak or delayed demand.

## Ranked improvement opportunities

1. **Use shop-specific demand and price trend before choosing livestock/crops.**
   Avoid building a large MILK/WOOL/STRAWBERRY surplus when the corresponding
   shop is absent or arrives late. Adapt product selection to `town.unlocked_shops`
   and current market prices, not only to the static farm plan.
2. **Sell or throttle exposed inventory earlier.** The observed sell overlay
   waits for a negative drift or a crowded shed. Add a forward-looking trigger
   based on production rate, current market inventory/price, and town demand;
   reduce new production or liquidate when a price floor is becoming likely.
3. **Reserve market slots for valuable inventory.** Keep late hiring and
   low-value sales from crowding out timely sales of perishable/high-volume
   products. Compare expected sale proceeds per market slot and front-load
   inventory that is likely to lose value.
4. **Validate across shop-sequence regimes.** The seed panel has three clean
   wins and two seeds responsible for all losses. Future comparisons should
   pair candidate changes on shop sequences with early/late milk, wool, and
   strawberry demand; report per-seed margins alongside aggregate win rate.

These are diagnosis and experiment leads, not a claim that any change is already
validated. No Kaggle submission was made.

## Artifacts and reproduction

- Frozen panel results: `experiments/runs/v57_reset_validation/results.json`.
- Captured replay runs were made with `simulation.tournament._run_worker`, the
  frozen candidate, the listed opponent, and the exact panel seed/seat.
- The installed canonical engine was Kaggle Environments 1.32.7 at
  `.venv/lib/python3.12/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py`.

## V58 focused probe: sales timing versus the 10-order cap

The engine limits a turn's market action to 10 order entries (`maxMarketOrdersPerTurn`;
the engine slices the submitted list to that length). I audited the candidate-seat
actions in both captured loss replays with
`experiments/v58_diagnostics/audit_replays.py`; its output is
`experiments/v58_diagnostics/replay_audit.json`.

The candidate submitted exactly 10 entries on 20/720 turns in the 92802 replay
and 19/720 in the 92804 replay; no recorded action exceeded 10. These cap hits
usually contained eight or nine `HIRE` entries. There is some tradeoff between
hiring and other order types on those turns, but the evidence does not show the
engine truncating an attempted sale: the serialized actions themselves contain
at most 10 entries.

For the focus goods MILK, WOOL, and STRAWBERRY, 33/40 observed-price-at-most-$5
sale orders on seed 92802 had fewer than 10 submitted orders. On seed 92804,
11/12 did. Examples include milk sold at observed price $1 on step 393 with one
market order (92802), milk at $1 on step 506 with eight orders (92804), and
strawberry at $1 on step 482 with six orders (92802). This weakens a direct
market-slot-cap explanation for most late liquidations. It does not rule out
earlier production throttling or a policy tradeoff on capped hire turns. These
are observed pre-market prices, not reconstructed average transaction prices.

The falsifiable follow-up is a paired comparison on fresh diagnostics seeds
93300–93302:
run the frozen v57 reset candidate and a candidate with only the early-sale
policy change, each against the same v48 opponent in both seats. Keep each seed
and seat order identical across arms. The prepared runner is
`experiments/v58_diagnostics/run_paired_probe.py`; write each arm to its own
output directory and preserve the candidate hashes recorded in `plan.json`.
Compare per-seed seat-swapped coin margins, plus replay-derived first sale step
and sale proceeds for MILK/WOOL/STRAWBERRY. Evidence for the early-sale
hypothesis requires the modified arm to sell the relevant goods earlier and
improve paired margins on the weak-demand shop regimes without merely shifting
losses to other seeds. If the sales happen earlier but paired margins do not
improve, the intervention fails this probe; if most sales were already on
turns with spare order entries, slot-reordering alone is not supported.

No probe games have been launched from this runner yet; it is waiting for a
stable policy candidate. Existing diagnostics processes were not running when
this audit resumed.

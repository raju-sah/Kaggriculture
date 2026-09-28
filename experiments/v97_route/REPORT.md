# V97 — genuine multi-turn route intervention: report

**Recommendation: NO-SUBMIT. The multi-turn worker route was built, verified alive, and
measured. It lost badly. All four Kaggle submission slots remain unused.**

This report satisfies the assignment's requirement of a *tested coherent route*. It is
not a single-action overlay and it is not an out-of-scope conclusion: a bounded multi-turn
worker route that walks, harvests, delivers and rejoins was implemented, proven to emit
multi-turn MOVE+work sequences under the pinned engine, and measured on spent seeds in
both seats. It lost. Two revisions were made and measured. Both assigned mechanisms are
now closed with numbers.

No Kaggle submission was made. No prior agent, doc or `main.py` was modified.

---

## 1. Required correction: the discarded-unit conflict is reconciled

The assignment required verifying the V96 accounting before relying on it. Both figures
were partly right. Full detail in `CORRECTION_NOTES.md`; the resolution:

| scope | units deleted | where |
|---|---:|---|
| **universal, all 14 games** | **exactly 2 FERTILIZER at the day-27 boundary**, shed at 100 | the farm's own route, identical in wins and losses |
| additional, 4 games only | 2–8 more at days 25/26/28 | **only when Rajusah is in seat 1** |

V93's "exactly 2" is correct for the farm's own route. V96's "2–10" is correct for the
total, because `_end_of_day` drops seat 0 first (kaggriculture.py:878), so a seat-1 player
faces a shed the opponent has already filled. Both are right at their own scope. The
elevated cases include three wins and two losses, so it carries **no** win/loss signal.

Shed occupancy, rederived from the recorded observation stream (Rajusah seat, carried is
0 at every day boundary):

| window | mean shed | mean spare | min spare |
|---|---:|---:|---:|
| days 0–11 | 12.8 | 87.2 | 64 |
| days 12–23 | 67.5 | 32.5 | 5 |
| days 24–29 | 94.3 | 5.7 | 0 |

## 2. The V96 reach number was wrong, and correcting it is what enabled this route

V96 closed the route lane on a **0.3% reach ceiling** (18 of 5,396 actor-turns). That
figure counted only actors *already standing* on a ripe tile. Re-audited across **all 14
official replays and 46,116 actor-turns**, the addressable set for a route that can
**walk** is:

| measure | value |
|---|---:|
| within 1 tile of a ripe target | 64.3% |
| within 2 tiles | **81.8%** |
| shed has ≥40 spare slots | 95.1% of turns |
| shed has <20 spare slots | 2.4% of turns |
| mean standing ripe units per turn (days 12–23) | 46.2 (median 42, p90 82) |

So the targets are close and the shed is roomy. V96's conclusion was an artifact of
measuring co-location instead of reach. That is why the assignment was right to demand a
multi-turn route.

## 3. Mechanism 1: the bounded multi-turn worker route

`route_overlay.py` → `candidate.py`. A stateless (observation-derived) route that, in
days 12–23, takes authority over one hand to walk to the highest-value reachable ripe
target, harvest it, carry the product to a shed-access tile, drop it so it becomes
sellable, then rejoin the frozen route. It never touches the market list, never displaces
FEED/CARE/WATER/HARVEST/PICKUP/PLACE, checks collision, and refuses when shed headroom is
short.

**Route verification (the assignment's core requirement), 14 official replays:**

| measure | value |
|---|---:|
| turns the route acted | 3,192 |
| MOVE steps emitted | **2,198, all 2,198 legal under the pinned engine** |
| HARVEST emitted | 224, all 224 legal |
| DROP emitted | 770 (518 legal in v1) |
| longest consecutive errand | **19 turns** |
| products harvested | MILK 84, WOOL 42, STRAWBERRY 84, WHEAT 14 |

This is a genuine multi-turn route, verified alive before any tournament.

**Spent-seed screen, 11 seeds, both seats, exact loader, zero errors:**

| Candidate | Games | W-L-D | Mean paired margin | Range | Positive |
|---|---:|---|---:|---|---:|
| v1 (unbounded) | 22 | 0-22-0 | **−89,887** | −124,037..−61,267 | 0/22 |

### The bug the diagnosis found

Step 5/6 replayed the route over the recorded stream: **identical cash (136,926 both),
identical animals, zero escapes — but +39 harvested and +0 sold.** The cause was a real
defect: **18 of 84 DROPs were issued from tiles the engine does not treat as
shed-adjacent.** The engine's `_shed_access_tiles(10)` is the **inner** corner
`{(4,4),(4,5),(5,4),(5,5)}`; my route used the **outer** corner `{(0,0),(0,4),(4,0),(4,4)}`.
Only (4,4) coincided. Every other DROP was a silent no-op, the hand stayed loaded, and
the end-of-day drop deleted the load. Fixed to derive from the engine's own rule;
**68/68 DROPs then legal, 0 wrong tiles.**

### The real mechanism, and why fixing the bug was not enough

With the DROP fixed the route still lost **−57,852 to −114,136**. Three measurements
explain it:

1. **Replay-harmless, live-catastrophic.** Replaying the route over the recorded V92
   stream gives *identical* final cash (108,954), identical animals, identical 1,565
   sales, zero escapes. The farm is not damaged. The damage is live-only.
2. **The shared market barely moves** (WHEAT inventory 9,631 vs 9,552 at day 27), so it
   is not a market-mediated cost.
3. **Both policies selfplay exactly symmetric** (0 differential on every seed), so the
   head-to-head is a clean comparison and the deficit is systematic. V97-vs-V92
   −70,127 mean; V92-vs-V97 +70,127. The route roughly **halves the farm's own score in
   selfplay** (99,145 → 46,462 on seed 92600).

The exposure is the mechanism. The route acted on **30.5% of in-window turns**, and the
actions it displaced were almost all **MOVEMENT** — which is not idle time but the tape's
delivery mechanism. Hand 0 alone spent 65 turns on errands. A 719-step open-loop tape
earns its score by being correct everywhere at once; borrowing a hand for a long errand
removes a share of every duty that hand performed.

## 4. The two revisions, both measured

| build | change | Games | W-L-D | Mean margin |
|---|---|---:|---|---:|
| v1 | unbounded per-turn | 22 | 0-22-0 | −89,887 |
| **R1** | one-shot latch + board-wide duty gate | 22 | 0-0-22 | **0 (no-op)** |
| **R2** | one-shot latch + local duty gate | 22 | 0-0-22 | **0 (no-op)** |

R1 was a byte-identical no-op because its gate refused whenever *any* animal was unfed or
*any* plant was unwatered — true on essentially every turn of a 33-tile farm. R2 replaced
it with a local gate (the hand's own tile must be clean). R2 fires in unit tests, but
across **30,996 in-window actor-turns on all 14 replays the errand can start on exactly
0**: 48.2% of actor-turns are blocked because the hand's frozen action is a duty, 29.3%
because its own tile is dirty, and **all 6,972 that clear both fail on "no target in
reach"**.

The lane is closed by measurement: **too much exposure is catastrophic; any bounded
exposure is a no-op**, and there is no setting between, because exposure is discrete (a
whole errand) and the payoff is capped by a shed that is contended in exactly the days
the route runs.

## 5. Mechanism 2: opening tile reallocation with a full animal lifecycle

The assignment's second hypothesis, never tested by V96 (which never purchased an animal).
Converting one crop tile to a pasture, then running buy → build → pickup → place → feed
→ care → collect → sell, priced with **realized** unit prices (corrected V94 identity),
feed at the real recurring WHEAT cost, and the animal's real purchase price:

| animal | place day | units | product cash | feed cost | net before tile cost |
|---|---:|---:|---:|---:|---:|
| COW | 4 | 6 | $836 | $1,021 | −185 |
| COW | 8 | 6 | $836 | $857 | −21 |
| COW | 10 | 6 | $836 | $776 | +60 |
| SHEEP | 8 | 6 | $416 | $857 | −442 |

**Best case over every (crop, plant day, animal, place day) combination: −$185.** A COW's
feed cost exceeds its milk revenue beyond the $400 purchase. The route already runs 17
animals with zero escapes; a 18th costs more than it returns. Refuted on arithmetic before
any candidate was written.

## 6. Results table

Exact loader, pinned kaggriculture 1.32.7, 11 already-spent seeds (each ≥22 prior saved
games), both seats, zero errors and zero timeouts in all 110 games.

| Candidate | Opponent | Games | W-L-D | Mean margin | Median | Positive | Errors | Runtime |
|---|---|---:|---|---:|---:|---:|---:|---|
| v1 route | V92 | 22 | 0-22-0 | −89,887 | −84,941 | 0/22 | 0 | mean 68 s |
| R1 route | V92 | 22 | 0-0-22 | 0 | 0 | 0/22 | 0 | mean 48 s |
| R2 route | V92 | 22 | 0-0-22 | 0 | 0 | 0/22 | 0 | mean 48 s |

Seat-order mirror (3 seeds, confirming the deficit is symmetric and not a seat artifact):
V97-vs-V92 −70,127, V92-vs-V97 +70,127, both selfplays exactly 0.

**No promotion gate was frozen and no fresh holdout was consumed.** No candidate showed a
positive paired cash signal on development seeds, so a holdout was not warranted and
remains unspent.

## 7. All mechanisms attempted, including failures

1. **Unbounded multi-turn worker route (v1)** — alive and verified, −89,887. Closed:
   exposure displaces the tape's delivery walk; plus a real shed-tile bug, fixed.
2. **One-shot bounded route, board-wide gate (R1)** — no-op, 0 of 216 turns. Closed:
   the gate is unsatisfiable on a 33-tile farm.
3. **One-shot bounded route, local gate (R2)** — no-op, 0 of 30,996 actor-turns. Closed:
   the tape is never simultaneously free and near ripe stock.
4. **Opening tile reallocation with animal lifecycle** — refuted on arithmetic, best case
   −$185.
5. Carried forward and already closed: V93 WOOL hold, V94 deferred harvest, V95 fertilizer
   apply, V96 early pasture / harvest priority.

## 8. Files and hashes

All new files confined to `experiments/v97_route/`. Prior agents byte-unchanged.

| Artifact | SHA-256 |
|---|---|
| `candidate.py` (v1 route) | `cca2e17db514c44a24eed38c8b86b06ee27431cfc3dd44ef713d6110495bc82b` |
| `candidate_r1.py` | `4ae899687f87f361b0cd176955a51ef30162e9a8284db98f03d24c2049b66c43` |
| `candidate_r2.py` | `3229271bcef7e97cc604441c9e66bf18d46c982d1a5c5432a6801f655bbd1712` |
| `route_overlay.py` / `route_r1_overlay.py` / `route_r2_overlay.py` | `c561c4d9…` / `d9bd8f23…` / `fac00003…` |
| V92 incumbent (unchanged) | `0d5d356baa25703f1a7b753527d1b39e1c7d63478985913be5b3c2550261b806` |
| V93 / V94 / V95 (unchanged) | `fa81a78e…` / `a7ec12eb…` / `3cd4bb8a…` |
| V56 / V50 (unchanged) | `d9e96709…` / `e6b50128…` |

All three candidates pass 9–12 build self-checks: embedded V92 byte-identical, loader
binds the route entrypoint, shed tiles match `engine._shed_access_tiles`, market list
never modified, input never mutated, plus latch / duty-gate / reach / value / delivery
regression tests. `route_r2_overlay.py` documents the shed-tile bug and its measured
effect inline.

Evidence: `CORRECTION_NOTES.md`, `accounting_verification.json`, `reach_audit.json`,
`route_verification.json`, `seat_spread.json`, `lane_closure.json`,
`screen_results.json`, `screen_r1_results.json`, `screen_r2_results.json`, plus per-game
records under `runs/`. The V88 replay joins were not used; seeds 93000–93011 were not
used.

## 9. What a successor should start from

1. **V96's reach ceiling was a measurement artifact.** Co-location is not reach. A route
   that can walk has 81.8% of actors within 2 tiles of ripe stock.
2. **The worker-reroute lane is closed with a real route, not an overlay.** Unbounded
   exposure is catastrophic because the displaced actions are the tape's delivery walk;
   bounded exposure is a no-op because the tape is never simultaneously free and near
   ripe stock. A route that *replaced* the walk wholesale would need validation from
   scratch, and every wholesale route rewrite in this repository has been measured
   decisively negative.
3. **Adding animals to this lineage loses money** (best case −$185): feed is a recurring
   cost that crops do not have, and the route already runs 17 animals with zero escapes.
4. **The shed ceiling is reached at day 26–28**, and the day-27 delete of exactly 2
   FERTILIZER units is universal and route-caused. Any route that converts more standing
   yield must free shed slots *before* day 27, not merely hold or release stock.

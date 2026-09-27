# V81: expert-switch feasibility (V50 driving the V57-reset seat from day 6)

Read-only feasibility probe. No agent code edited, no game run, no new seed, no secrets, no
submission. All evidence comes from saved artifacts and from **counterfactual action queries** on a
saved observation stream.

## Sources and SHA-256

| File | SHA-256 | Role |
|---|---|---|
| `experiments/v57_broad/v57_reset_candidate.py` | `4173479fe1f80d031d570d1ea23b694dfe86e1d162317a4c9c7df0058a40208e` | incumbent, seat 0 in the replay |
| `experiments/v50_agent.py` | `e6b50128e023e3b9fafa1841e4cd520c5e581acb48e8628657585c18272eab2b` | proposed expert, seat 1 in the replay |
| `experiments/v58_planner_eval/model_based/spent_seed_92802/reset/replays/v50-seed-92802-ab-repeat-0.json` | on-disk `9021876d26b46ee5455b061f8a6eafe2be521b8f68526b1067ba02a115fd6a71`; stored `replay_sha256` `e5c5fd8e74dc6c8b25ec8ed89f72d3a88a91d85d1aec4672c60d7e95a8ae8dab` | saved seed-92802 game, both frozen agents |
| `docs/V58_ROUTE_SWITCH.md` | n/a | prior passive-state route-switch test |

Neither agent file was modified.

## How this differs from V58's prior test

`docs/V58_ROUTE_SWITCH.md` queried several agents on the **same observation after three passive
days** at the first shop opening, and compared only *immediate market cash*. Its own conclusion was
"establishes action divergence only", and it reported that passive farms are unlike a played route.

This probe is different in three ways that matter:

1. **Played state, not passive.** The observation is the real seat-0 V57 state at day 6 hour 06,
   after six days of actual play, with a real shed, real hands, and a real herd.
2. **Whole-route behaviour, not one order.** The question is whether V50's *complete* route produces a
   viable purchase → build → pickup → place → feed/care chain on that state, which is the property
   V80 failed on.
3. **Direct, matched comparison.** V50's action on V57 state is compared against V50's own recorded
   action on its own state in the same game, at the same step.

## Result: the V50 expert produces a viable chain on the V57 seat-0 state

V50 was loaded as a callable, its module state reset, and run over the saved seat-0 (V57)
observation stream from episode start through step 150, then queried at step 150.

**No exception fallback fired on any of the 151 frames.** This matters because V50's `agent`
(`experiments/v50_agent.py:409-421`) wraps the planner in a bare `except Exception` and silently
returns all-PASS. Zero fallbacks means the planner accepted the V57 state stream without error.

**Action at step 150, V50 queried on the V57 seat-0 state:**

```
market: [['SELL','WOOL',12], ['BUY_LAND'], ['BUY_ANIMAL','SHEEP',2]]
```

**V50's own recorded action at the same step in the real game** (stored at step 151, since an action
in the replay is chosen from the previous observation):

```
market: [['SELL','WOOL',12], ['BUY_LAND'], ['BUY_ANIMAL','SHEEP',2]]
```

The two are **identical**. On the V57 state, at the moment the V57 route chose 2 geese, the V50
expert independently chooses 2 sheep — the exact substitution the wool diagnosis targets.

**Counterfactual action queries on the subsequent saved V57 observations (150–175)** show a
complete, self-consistent chain:

| Obs | Day/hour | V50 action on V57 state |
|---:|---|---|
| 150 | 6h06 | `BUY_ANIMAL SHEEP 2` |
| 152 | 6h08 | hand 0 and hand 5 `PICKUP SHEEP` |
| 154 | 6h10 | hand 5 `BUILD_PASTURE` |
| 155 | 6h11 | hand 0/4 `BUILD_PASTURE`, hand 5 `PLACE SHEEP` |
| 156 | 6h12 | hand 0 `PLACE SHEEP`, hand 1 `CARE`, hand 5 `FEED` |
| 157 | 6h13 | hand 0 `FEED`, hand 5 `CARE` |
| 159 | 6h15 | hand 5 `BUILD_PASTURE`, hand 6 `CARE` |
| 171 | 7h03 | three `FEED` actions |
| 172 | 7h04 | `CARE` + three `FEED` |
| 173 | 7h05 | `BUY_ANIMAL COW 1` — resumes its own cow route |

So the expert answers all three questions asked of it: it **buys 2 SHEEP**, it **builds pasture to
receive them**, and it produces a **pickup → placement → feed/care path** that continues across the
day-6→7 boundary. It then carries on with its normal cow/herd route, which is what a competent
full-route agent should do.

## Statefulness and midgame-switch safety

**V50 is stateless across frames.** Its module defines no mutable module-level containers
(`experiments/v50_agent.py` assigns no `{}`/`dict()`/`defaultdict` globals). Verified empirically:
querying step 150 cold, and again after warming the module over frames 0–150, returns
**byte-identical actions**. The only mutable attribute is `_PLANNER.telemetry`, a counter dict
(`games`, `legacy_turns`, `rebalance_turns`, `reordered_turns`) that does not feed back into planning.

This matters for a midgame switch: V50 has no per-episode memory that a reset would need to satisfy.
It is a pure function of the observation.

**V57-reset, by contrast, is stateful** — it carries `_v57_price_state` keyed by seat, holding price
drift and step. A hybrid that abandons V57 midgame leaves that dict frozen at the switch point. It is
harmless as long as the hybrid never calls the V57 route again, but it means the two agents cannot be
interleaved arbitrarily.

## The seat-state difference at step 150

The two seats are **not** identical at the switch point, which is the honest caveat on this probe:

| Field | V57 seat 0 | V50 seat 1 |
|---|---|---|
| cash | 2,254 | 1,204 |
| farmer position | `[4,4]` | `[4,4]` |
| hands | 7 | 8 |
| hires_today | 7 | 8 |
| unlocked quadrants | `['NW']` | `['NW']` |
| shed | `WHEAT 11` | `FERTILIZER 1, WHEAT 3` |

Both are past the land purchase for this hour (both hold `['NW']`, and both spend on `BUY_LAND` at
step 150), the farmer is co-located, and both have cash well above the 1,000 cost of two sheep. The
board and herd match. The differences that remain are one extra hand on the V50 seat, a different
shed mix, and ~1,050 more cash on the V57 seat — none of which blocks the substitution, and all of
which V50's route demonstrably handles.

## Why this would have avoided the V80 failure

V80 was rejected because the converted sheep starved: the V57 route's feed loop had no reason to
visit the two new pasture tiles, so they sat at `consecutive_unfed = 1` through day 7 and were
deleted at the day-7→8 tick. The contrast is visible directly in this replay:

| | V50 seat (its own sheep) | V57 seat (frozen route) |
|---|---|---|
| Day 7 sheep `consecutive_unfed` | `0` on all four, all day | n/a — V57 never bought sheep |
| Day 8 start herd | `COW 6, SHEEP 4` — all four survived | `COW 6, GOOSE 2, SHEEP 2` |

In the real game, V50's four sheep are fed by its own route every day. A V50-driven V57 seat would
receive that same route, including the feed/care coverage the V80 overlay lacked.

## What this does not prove

This is a **counterfactual action query**, not a rollout. Querying V50 on the saved V57 observation
stream answers "what would V50 have done on this state, given only past frames of that stream". It
cannot answer "what would the game have become", for three reasons:

1. **The stream does not follow V50's actions.** Frames 151+ are the *recorded V57 outcome*. V50's
   proposed `PICKUP`/`BUILD_PASTURE`/`FEED` actions are never applied to it. The chain above is
   therefore a plan evaluated on frozen states, not a simulated trajectory.
2. **Shared market coupling is unmodelled.** The market is shared. A different herd changes what is
   quoted, what sells, and what the opponent faces. V50 buying sheep at step 150 on the V57 seat
   would also change the opponent's environment.
3. **The opponent is unchanged.** In the real 92802 game the other seat is V50 itself. A hybrid
   screened against V50 is a different matchup than this replay.

There is also a licensing note carried forward from V58: these are internal benchmark agents. The
switch would be an internal candidate, not a submission, and rights questions about any bundled
third-party sources are unresolved.

## Go / no-go

**GO for exactly one matched spent-seed hybrid screen, with a fixed trigger.** The action-level
evidence is the strongest available without running a game, and it is directly targeted:

- V50 is a pure function of the observation, so the switch is stateless and safe to trigger.
- On the V57 seat-0 state at day 6 hour 06, V50's action is **byte-identical to its own recorded
  action** in the real game, and it selects the exact 2-sheep substitution.
- It then emits a complete build → pickup → place → feed/care chain, which is precisely the property
  the V80 overlay lacked and which the V80 failure showed to be decisive.

**Fixed trigger, stated before the run:**

> Switch seat authority from the frozen V57-reset route to the V50 route on the **first** observation
> where all hold: `YARN_STORE` in `town.unlocked_shops`, `market.prices['WOOL'] >= 180`,
> `day == 6`, and the farm holds exactly 2 sheep. Latch for the remainder of the episode. Never
> switch back. Never switch on any other day.

Latch-only, single-switch, day-6-only. The day-6 and exact-2-sheep conditions bound it to the one
divergence this diagnosis identified, so the screen measures the wool hypothesis and nothing else.

**Screen:** one spent seed, 92802, both seat orders, one repeat, replay retained, candidate = hybrid
vs frozen V50. Predeclare the same settlement audit used in V80 (pinned-engine reconstruction, cash
error must be 0.0) and a wool-revenue gate against the frozen reset's 16,166.

**Stop conditions, checked first, before any scoring:** the hybrid must actually switch on the 92802
replay (i.e. V50 must be the authority at step 150) and must not raise. If it does not switch, the
screen is void — fix the trigger, do not score it.

**NO-GO conditions.** Stop the branch without further work if any of these hold:

- The hybrid raises an exception or falls back to PASS on the V57 stream (the silent `except` in V50
  would otherwise hide a broken switch and produce a meaningless score).
- The two extra sheep are not placed within 24 hours of purchase, or any converted animal reaches
  `consecutive_unfed >= 2` — that is the exact V80 failure mode and would mean the route switch does
  not carry its feed loop across a farm that V50 did not open.
- Accepted wool revenue fails to exceed the frozen reset's 16,166 by a predeclared margin.

This remains feasibility evidence for a switch, not proof of a win. The action diff is exact and
matched; the outcome is not measured, and this probe deliberately did not measure it.

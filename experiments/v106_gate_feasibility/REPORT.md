# V106 gate feasibility: can any inspected public feature separate the V92
# regression from the V56 benefit?

**Read-only study. No candidate was created or edited. No new match was run
(`extract.py` was written but never executed). No protected seed
(137501 / 170001 / 180001) was touched. Nothing was submitted.**

**Recommendation for the current data: NO-GO — do not gate or promote the
second cow on this evidence.**

**Claim scope.** This is a small spent-sample feasibility study, not a proof
about the observation space. The conclusion is that **no reliable simple gate is
supported by the features I inspected on the seeds available** (10 V92 seeds
with raw replays, 1 V56 seed). It is *not* a claim that no gate could ever
exist. Two limits are stated explicitly below, because they are the difference
between a finding and an overreach:

- Seeds 160008 and 160009 match on the features I inspected (shops, MILK/WOOL
  inventory and price, opponent herd). They may still differ in aspects I did
  **not** compare — map geometry, our own farm and private state, unit
  positions, and the accumulated public history of the game. I did not test
  those, so I do not claim the full public observation is identical, only that
  the *inspected* subset fails to separate them.
- I have **one** V56 day-6 replay (seed 94700). It shows an opponent herd
  identical to V92's cohort, which is evidence that a day-6 herd fingerprint
  does not work on that seed. It is not sufficient to establish that all V56
  games are indistinguishable from V92.

## Sources (all pre-existing and spent; no simulation)

| Source | Contents |
|---|---|
| `experiments/v101_commandcode/lifecycle_replays/seed_16000{1,3..10}.json` | raw replays, seat 0 = V101 candidate, seat 1 = V92; frame 150 = day-6 h6 |
| `experiments/v101_commandcode/micro_replays/candidate_seed_160002.json` | same, seed 160002 |
| `experiments/v70_capacity/spent94700_vs_v56/replays/v56_agent-seed-94700-ab-repeat-0.json` | raw replay, seat 0 = V70 candidate, seat 1 = **V56**; frame 150 = day-6 h6 |

A filesystem search for existing exact-loader day-6 snapshots versus V56 found
only the 94700 replay. Everything below is parsed directly from these files.

## Extraction method

Day-6 h6 is **frame 150** (6 days × 24 turns + hour 6). For that frame I read
only what a player can observe before acting:

- `town.unlocked_shops` (public);
- `market.inventory["MILK"/"WOOL"]` and `market.prices["MILK"/"WOOL"]` (public);
- the opponent's on-board animal counts and COOP/PASTURE counts, read from
  `obs["farms"][1]`, which the engine shares with both players (public);
- our own pasture/COOP counts, free-pasture count, shed and money (ours).

**What was validated, and what was not.** The *tile-counting and snapshot logic*
was validated against both replays above (it reproduces the frame-150 values,
including the corrected total-pasture count of 6 with 0 free — see §"Bug fixed").
However, **the extractor script `extract.py` was not executed end to end**: its
agent-binding and early-stop loop are unexercised and should be treated as
unvalidated scaffolding for future use, not as a tested pipeline. The data in
this report came from **direct parsing of the saved replays**, not from running
`extract.py`.

Agent hashed for the study: `candidate_milk_sink_no_yarn.py`
sha256 `d166d2420440a0a96643c061b010c444f372a89e236e9c22a8417b4008b81763`.
Engine: kaggle-environments 1.32.7, `kaggriculture.py`
sha256 `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`.

### Bug fixed in the extractor (found during review, before any run)

The original `scan()` used `if "animal" in tile: … elif kind == "PASTURE"`,
so an *occupied* pasture tile (which keeps `kind: "PASTURE"` and additionally
has an `animal` key) was counted as neither animal nor pasture — the
`pastures` field silently counted only empty tiles. This is now fixed to count
`kind` independently and to count a pasture as *free* only when unoccupied.
Because the script was never run, no data in this report is affected; the fix is
recorded so the script is not reused in a wrong state.

## Public day-6 features, V92 cohort

| seed | MILK $ | WOOL $ | MILK inv | WOOL inv | shops (sorted) | V105 | base |
|---:|---:|---:|---:|---:|---|---|---|
| 160001 | 183 | 218 | 9993 | 9993 | FARMERS_MARKET, FARMERS_MARKET | draw | draw |
| 160002 | 183 | 233 | 9993 | 9953 | BAKERY, YARN_STORE | draw | draw |
| 160003 | 205 | 218 | 9973 | 9993 | FARMERS_MARKET, ICE_CREAM_SHOP | win | win |
| 160004 | 207 | 218 | 9971 | 9993 | PIZZA_SHOP, SMOOTHIE_SHOP | win | win |
| 160005 | 186 | 218 | 9991 | 9993 | **BAKERY, PIZZA_SHOP** | **loss** | **win** |
| 160006 | 186 | 218 | 9991 | 9993 | **BAKERY, PIZZA_SHOP** | loss | loss |
| 160007 | 205 | 218 | 9973 | 9993 | BAKERY, PIZZA_SHOP | win | win |
| 160008 | 205 | 218 | 9973 | 9993 | **BRUNCH_SPOT, SMOOTHIE_SHOP** | **loss** | **win** |
| 160009 | 205 | 218 | 9973 | 9993 | **BRUNCH_SPOT, SMOOTHIE_SHOP** | win | win |
| 160010 | 183 | 218 | 9993 | 9993 | BAKERY, FARMERS_MARKET | draw | draw |

Opponent herd at day 6 is **constant 4 COW / 2 SHEEP / 0 GOOSE on every V92
seed**, with 6 pastures and 0 coops.

## Finding 1 — inspected features do not separate the two V92 flips

Two groups share the **same inspected public market + shop values**:

- **160005 and 160006** — both (186, 218, 9991, 9993, {BAKERY, PIZZA_SHOP}).
  160005 flips base win → V105 loss; 160006 is a loss under both.
- **160007, 160008, 160009** — all (MILK 205, WOOL 218, MILK inv 9973), differing
  only in shop set/order. 160008 flips base win → V105 loss; the other two stay
  wins.

So on the features I compared, a gate would have to treat 160008 the same as
160009, yet their outcomes differ. **A shop/market/herd threshold on the
inspected features does not separate the V92 regressions from the V92 wins.**
(Per the scope note, other observable state may differ; I did not test it, so I
stop at "these features are insufficient" rather than "no gate can exist".)

## Finding 2 — a day-6 opponent-herd fingerprint does not work on the evidence available

The one V56 replay at day-6 h6 shows the **same** public opponent herd as the
entire V92 cohort:

| | MILK $ | WOOL $ | MILK inv | WOOL inv | opponent herd | coops |
|---|---:|---:|---:|---:|---|---:|
| V56 (94700) | 205 | 206 | 9973 | 9999 | **4 COW / 2 SHEEP / 0 GOOSE** | 0 |
| V92 (160009) | 205 | 218 | 9973 | 9993 | **4 COW / 2 SHEEP / 0 GOOSE** | 0 |

V56's larger 6 COW / 4 SHEEP / 7 GOOSE herd is built later in the season; at the
day-6 decision turn, on this seed, it is publicly the same as V92's. A gate
keyed on "opponent runs a heavy cow herd" therefore has nothing to key on at
day 6. With a single V56 seed this is suggestive, not established.

## Finding 3 — the only feature that varies against V56 is weakly supported

The only inspected public feature that differs against V56 is the WOOL price
(206 vs 218) and the matching WOOL inventory. This is compatible with a real
later-season effect, but across the V92 cohort the wool price is pinned at 218
for every decisive seed, so it carries no within-opponent discriminating power
here. Treating it as a gate would be fitting a one-seed distinction.

## Overfitting / opponent-fingerprint warning (explicit)

- **Do not fit a shop rule to these seeds.** With ~10 distinct public feature
  vectors across 10 seeds, a threshold can reproduce the observed W/L exactly
  and mean nothing. Finding 1 shows it would fail even to distinguish some
  already observed seed outcomes.
- **Do not infer opponent identity from the day-6 herd alone.** The inspected
  V56 and V92 replays show the same day-6 livestock counts (Finding 2). Other
  public observations may differ, but one V56 replay is too little evidence
  to turn such differences into a reliable opponent-classification gate.
- **Shop *order* carries no economic content** in this engine (160007 vs
  160008/160009 differ only in ordering); using it would be noise-fitting.
- Any future attempt should be judged on a **fresh, precommitted, hash-frozen**
  panel and pass on **official W/L with no win→loss flips vs V92**, not on
  margin. I set no threshold here and recommend none be set on this data.

## Recommendation

**Keep the frozen one-cow no-Yarn candidate as the current best. Do not promote
V105 or any V106 refinement of it on this evidence.** The second cow's effect is
opponent-dependent in outcome on the spent sample (margin-positive vs V56;
win→loss flips vs V92 on 160005/160008) and the inspected public features do not
reliably predict which case applies. A gate built on this data would be
overfit; a rule run unconditionally regresses the incumbent (V105: 8W–6L–10D vs
base 12W–2L–10D). The V104 GOOSE line remains separately closed as infeasible
(no COOP exists before day 11; `experiments/v104_commandcode/feasibility_160001.md`).

## Artifacts
- `extract.py` — day-6 h6 snapshot extractor; tile-count bug fixed, but the
  agent-binding and early-stop path are **unexecuted/unvalidated** (left for
  future use; no data here comes from running it)
- Source replays listed above (all pre-existing and spent)
- Paired outcomes: `experiments/v105_commandcode/runs/{v105,base}_vs_v92_s1/games.jsonl`

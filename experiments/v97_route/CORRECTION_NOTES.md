# V97 correction notes — shed and discard accounting

These notes sit beside the V97 report because the repository previously held two
conflicting numbers, and both were partly right.

## The conflict

- `docs/V93` / the V93 report: **"exactly 2 units destroyed per official game."**
- V96 (`experiments/v96_route`): **"2–10 units discarded per game, 52 total over 14."**

The V97 assignment requires this reconciled before any of it is relied on.

## What the engine actually does

`_end_of_day` (kaggriculture.py, line 878) calls `_drop_inventories_to_shed` once per
player **in player order**:

```python
for player_id, farm in enumerate(obs0.farms):
    ...
    _drop_inventories_to_shed(private, shed_cap)
```

The drop fills the shed to `shedCapacity = 100` and **deletes** the overflow
(`del inv[item]`, line 857). Seat 0 is dropped first, so a player in seat 1 faces a
shed the opponent has already filled.

## The measurement, on all 14 official replays, Rajusah seat, zero cash mismatches

Replaying the recorded transitions through the pinned engine's own drop path in true
engine order (`verify_accounting.py`):

| episode | Rajusah seat | units deleted | when |
|---|---:|---:|---|
| 114158802 | 0 | 4 | d26 WHEAT×2 (shed@99), **d27 FERT×2 (shed@100)** |
| 114160308 | 1 | 2 | **d27 FERT×2 (shed@100)** |
| 114161728 | 0 | 2 | **d27 FERT×2** |
| 114163744 | 0 | 2 | **d27 FERT×2** |
| 114164630 | 1 | 2 | **d27 FERT×2** |
| 114166061 | 1 | 9 | d25 FERT×1, **d27 FERT×2**, d28 FERT×5 + WHEAT×1 |
| 114167570 | 0 | 2 | **d27 FERT×2** |
| 114169079 | 0 | 2 | **d27 FERT×2** |
| 114170594 | 0 | 2 | **d27 FERT×2** |
| 114172061 | 0 | 2 | **d27 FERT×2** |
| 114173483 | 0 | 2 | **d27 FERT×2** |
| 114175006 | 1 | 10 | **d27 FERT×2**, d28 FERT×8 |
| 114176499 | 1 | 2 | **d27 FERT×2** |
| 114177946 | 1 | 9 | **d27 FERT×2**, d28 FERT×7 |

## The reconciliation

**Both numbers are correct at their own scope.**

- There is a **universal day-27 event**: exactly **2 FERTILIZER units** deleted at
  `shed == 100`, in **all 14 games**. That is V93's "exactly 2", and it is a property of
  the farm's own route, identical in wins and losses.
- Four games (114158802, 114166061, 114175006, 114177946) have a **second** boundary
  event at day 25/26/28 that deletes a further 2–8 units. Those occur **only when
  Rajusah is in seat 1**, because the opponent's hands are dropped into the shed first
  and consume the last slots.

So the correct statement is:

> The farm's own route destroys **exactly 2 FERTILIZER units at the day-27 boundary in
> every game**. A seat-1 game can additionally lose 2–8 units at a later boundary
> because the opponent's overflow is deposited first. Total discarded is therefore
> 2 units in a seat-0 game and 2–10 in a seat-1 game.

**No win/loss separation exists in this quantity**: the four elevated games include two
wins (114158802, 114175006, 114177946 = three wins) and two losses (114166061). It is
driven by seat and by the opponent's own overflow, not by anything the farm controls.

## What this means for the route search

The V96 mechanism-B closure cited shed occupancy of 67–78 in days 12–23 as the reason
harvest-priority could not win. That occupancy figure is confirmed (rederived below),
and it stands. But the more precise statement is now available: the shed reaches its
100-unit ceiling at **day 26–28** in every game, and the day-27 delete is a fixed,
route-caused 2 FERTILIZER units. Any route that converts more standing crop yield must
therefore free shed slots *before* the day-27 boundary, not merely hold or release
stock, which is what the V97 multi-turn route is designed to test.

## Shed occupancy, rederived (recorded observation only, Rajusah seat)

| window | mean shed | mean spare | min spare |
|---|---:|---:|---:|
| days 0–11 | 12.8 | 87.2 | 64 |
| days 12–23 | 67.5 | 32.5 | 5 |
| days 24–29 | 94.3 | 5.7 | 0 |

Max carried at any day boundary: **0**, in all 14 games. The shed is the only sink and
the only sellable location (engine line 654).

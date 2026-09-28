"""Phase 0: is a COOP placement reachable on the day-6 route? (spent seed only)

Reads an ALREADY-SAVED replay for seed 160001 -- no new games are run. The
question is concrete: V104 wants the tape's own day-6 sheep errand to place a
GOOSE instead, and a GOOSE needs a COOP tile, not a PASTURE.

So we need, on seed 160001:
  * where the tape buys SHEEP on day 6 (the h6 BUY_ANIMAL SHEEP cohort),
  * where the tape picks up a SHEEP on day 6 (which actor, which tile),
  * where that same actor PLACEs a SHEEP on day 6 (the target tile),
  * whether any COOP tile exists on the farm, and whether one is reachable by
    that actor on the same route (adjacent to where it stands, or a tile it
    stands on during the day-6 window).

Nothing here runs a match. It only reads a replay already on disk.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
REPLAY = Path(sys.argv[1]) if len(sys.argv) > 1 else \
    ROOT / "experiments/v101_commandcode/lifecycle_replays/seed_160001.json"
SEAT = int(sys.argv[2]) if len(sys.argv) > 2 else 0

ANIMAL_STRUCT = {"COW": "PASTURE", "SHEEP": "PASTURE", "GOOSE": "COOP"}


def main() -> int:
    game = json.loads(REPLAY.read_text())
    steps = game["steps"]
    print(f"replay: {REPLAY}")
    print(f"seed 160001, seat {SEAT}, steps {len(steps)}\n")

    # ---- final board: what structures exist at all? ----
    final = steps[-1][SEAT]["observation"]["farms"][SEAT]
    coops, pastures, coops_on_day6 = [], [], []
    for y, row in enumerate(final["tiles"]):
        for x, tile in enumerate(row):
            if isinstance(tile, dict) and tile.get("kind") == "COOP":
                coops.append((x, y))
            if isinstance(tile, dict) and tile.get("kind") == "PASTURE":
                pastures.append((x, y))
    print("COOP tiles on the final board   :", coops)
    print("PASTURE tiles on the final board:", pastures)

    # structures present at the day-6 h12 frame (around the sheep place)
    # ---- trace the day-6 route ----
    buy = pickup = place = None
    actors_day6 = {}
    for frame in range(1, len(steps)):
        obs = steps[frame - 1][SEAT]["observation"]
        act = steps[frame][SEAT].get("action") or {}
        day = int(obs.get("day", 0))
        hour = int(obs.get("hour", 0))
        farm = obs["farms"][SEAT]
        if day == 6:
            coops_on_day6 = [(x, y) for y, row in enumerate(farm["tiles"])
                             for x, tile in enumerate(row)
                             if isinstance(tile, dict) and tile.get("kind") == "COOP"]
            if coops_on_day6 and not coops_on_day6:
                coops_on_day6 = []
        units = [act.get("farmer", ["PASS"]), *(act.get("hands") or [])]
        positions = [farm.get("farmer"), *list(farm.get("hands") or [])]
        for order in (act.get("market") or []):
            if (isinstance(order, list) and len(order) >= 3 and order[0] == "BUY_ANIMAL"
                    and order[1] == "SHEEP" and buy is None):
                buy = {"hour": hour, "qty": int(order[2]), "order": order}
        for ui, a in enumerate(units):
            if not isinstance(a, list) or len(a) < 2 or day != 6:
                continue
            pos = tuple(positions[ui]) if ui < len(positions) and positions[ui] else None
            actors_day6.setdefault(ui, []).append((hour, tuple(a) if len(a) > 1 else (a[0],), pos))
            if a[0] == "PICKUP" and a[1] == "SHEEP" and pickup is None:
                pickup = {"hour": hour, "actor": ui, "pos": pos}
            if a[0] == "PLACE" and a[1] == "SHEEP" and place is None:
                place = {"hour": hour, "actor": ui, "pos": pos}

    print("\n=== day-6 route on the incumbent tape ===")
    print("SHEEP buy  :", buy)
    print("SHEEP pickup:", pickup)
    print("SHEEP place :", place)

    if not place:
        print("\nRESULT: no SHEEP PLACE on day 6 -> the V101 three-turn chain does not"
              " even form on this seed; goose substitution is moot.")
        return 2

    # Where does the placing actor actually stand / travel on day 6?
    actor = place["actor"]
    path = [(h, op, p) for (h, op, p) in actors_day6.get(actor, [])]
    print(f"\nactor {actor} full day-6 trace (hour, op, position):")
    for h, op, p in path:
        print(f"   h{h:02d} {op[0]:8}{op[1] if len(op) > 1 else '':8} {p}")

    visited = {p for (_, _, p) in path if p is not None}
    target = tuple(place["pos"]) if place["pos"] else None
    print("\nactor visited tiles on day 6:", sorted(visited))
    print("sheep placed on tile        :", target)

    coops_visited = sorted(set(coops_on_day6) & visited) if coops_on_day6 else []
    print("COOP tiles present at day 6 :", sorted(coops_on_day6))
    print("COOP tiles the actor stands on:", coops_visited)

    # A COOP is usable if the actor stands on one during day 6 (PLACE uses the
    # tile underfoot). Adjacency alone is not enough for animals: the engine
    # requires the unit to BE on the structure tile.
    if coops_visited:
        print("\nFEASIBLE: actor stands on a COOP during day 6, so the SHEEP PLACE"
              " can be relabelled GOOSE with no extra movement.")
        return 0
    print("\nOBSTRUCTED: the placing actor never stands on a COOP during day 6.")
    print("Engine PLACE for an animal requires the unit to be standing on a matching")
    print("unoccupied structure tile (kaggriculture.py _apply_unit_action PLACE branch),")
    print("so a GOOSE cannot be placed on the pasture tile the sheep would have used.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

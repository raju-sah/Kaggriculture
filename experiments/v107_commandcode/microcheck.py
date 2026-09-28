"""V107 micro-check on spent seeds, before any screen.

Firing seed 160003 must show, on seat 0:
  * a day-6 `BUY_ANIMAL COW 1` that V50 alone never issues,
  * a later day-6 `PICKUP COW` and `PLACE COW` (V50 has neither),
  * the cow alive on a PASTURE at season end, and
  * accepted MILK cash in the settlement (the cow actually produced and sold).

Non-firing seed 160001 must be action-identical to V50 (V107 must be a strict
no-op where the gate does not fire).

Runs sequentially (the V50 agent installs a shared module bundle, so threaded
env.run races on sys.modules). No replay is written to disk.

    .venv/bin/python experiments/v107_commandcode/microcheck.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "experiments/v101_commandcode"))  # engine-exact settlement

CAND = HERE / "candidate.py"
V50 = ROOT / "experiments/v50_agent.py"
OPP = ROOT / "agents/v56_agent.py"


def run(agent: Path, seed: int, opp: Path):
    from kaggle_environments import make
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=True)
    env.run([str(agent), str(opp)])
    return env.toJSON()


def day6_and_final(game: dict, seat: int) -> dict:
    steps = game["steps"]
    cow_buy = cow_pick = cow_place = 0
    cow_tiles = set()
    for frame in range(1, len(steps)):
        o = steps[frame - 1][seat]["observation"]
        a = steps[frame][seat].get("action") or {}
        if int(o.get("day", 0)) != 6:
            continue
        for x in (a.get("market") or []):
            if isinstance(x, list) and len(x) >= 3 and x[0] == "BUY_ANIMAL" and x[1] == "COW":
                cow_buy += int(x[2])
        units = [a.get("farmer", ["PASS"]), *(a.get("hands") or [])]
        pos = [o["farms"][seat].get("farmer"), *list(o["farms"][seat].get("hands") or [])]
        for ui, x in enumerate(units):
            if not isinstance(x, list) or len(x) < 2:
                continue
            if x[0] == "PICKUP" and x[1] == "COW":
                cow_pick += 1
            if x[0] == "PLACE" and x[1] == "COW":
                cow_place += 1
                p = pos[ui] if ui < len(pos) and pos[ui] else None
                if p:
                    cow_tiles.add(tuple(p))
    fin = steps[-1][seat]["observation"]["farms"][seat]
    live = sum(1 for r in fin["tiles"] for t in r
               if isinstance(t, dict) and t.get("animal") == "COW")
    new_live = sum(1 for (x, y) in cow_tiles
                   if isinstance(fin["tiles"][y][x], dict) and fin["tiles"][y][x].get("animal") == "COW")
    return {"buy": cow_buy, "pick": cow_pick, "place": cow_place,
            "tiles": sorted(cow_tiles), "live_cows": live, "new_live": new_live}


def milk_cash(game: dict, seat: int) -> float:
    import audit_panel  # from v101_commandcode; engine-exact settlement
    totals, _ = audit_panel.settle(game)
    return float(totals[seat].get(("SELL", "MILK"), 0))


def main() -> int:
    import audit_panel  # ensure importable
    ok = True

    print("=== firing seed 160003 (PIZZA/SMOOTHIE, no YARN) ===")
    gc = run(CAND, 160003, OPP)
    gv = run(V50, 160003, OPP)
    c = day6_and_final(gc, 0)
    v = day6_and_final(gv, 0)
    mc_c, mc_v = milk_cash(gc, 0), milk_cash(gv, 0)
    print(f"  V107 day6 cow buy/pick/place: {c['buy']}/{c['pick']}/{c['place']} "
          f"tiles {c['tiles']} new_live {c['new_live']}")
    print(f"  V50  day6 cow buy/pick/place: {v['buy']}/{v['pick']}/{v['place']} "
          f"tiles {v['tiles']} new_live {v['new_live']}")
    print(f"  accepted MILK cash  V107 ${mc_c:,.0f}   V50 ${mc_v:,.0f}  "
          f"(delta ${mc_c - mc_v:+,.0f})")
    if not (c["buy"] >= 1 and c["pick"] >= 1 and c["place"] >= 1 and c["new_live"] >= 1):
        print("  FAIL: V107 did not buy/pick/place/retain a cow on the firing seed")
        ok = False
    if v["buy"] or v["place"]:
        print("  WARN: V50 control also moved cows on day 6 (unexpected)")
    if mc_c <= mc_v:
        print("  FAIL: V107 accepted MILK not above V50 (cow did not add milk)")
        ok = False

    print("\n=== non-firing seed 160001 (FARMERS_MARKET, no MILK sink) ===")
    gc1 = run(CAND, 160001, OPP)
    gv1 = run(V50, 160001, OPP)
    # action-identical on seat 0 across all frames
    diffs = 0
    for f in range(1, len(gc1["steps"])):
        if gc1["steps"][f][0].get("action") != gv1["steps"][f][0].get("action"):
            diffs += 1
    coins_c = gc1["steps"][-1][0].get("reward")
    coins_v = gv1["steps"][-1][0].get("reward")
    print(f"  seat0 action frames differing: {diffs}  "
          f"final coins V107 {coins_c} V50 {coins_v}")
    if diffs != 0 or coins_c != coins_v:
        print("  FAIL: non-firing seed is not action-identical to V50")
        ok = False

    print("\nVERDICT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

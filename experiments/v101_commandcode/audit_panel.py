"""Replay lifecycle audit for the V101 development panel.

For every retained replay this confirms the three-step chain really executed and
the cow actually lived and produced, then cross-checks the cow's realised MILK
against the model's predicted units. It also reconstructs accepted MILK/WOOL
sale cash per seat so the report can quote settlement rather than a guess.

    .venv/bin/python experiments/v101_commandcode/audit_panel.py
"""

from __future__ import annotations

import copy
import json
import sys
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from kaggle_environments.envs.kaggriculture import kaggriculture as engine  # noqa: E402

MILK_SINKS = ("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP")


def settle(game: dict) -> tuple[list[Counter], list[int]]:
    """Replay accepted market cash per seat, exactly as the engine did it."""
    steps = game["steps"]
    cfg = game.get("configuration", {})
    config = SimpleNamespace(**{k: cfg.get(k, v) for k, v in {
        "boardSize": 10, "turnsPerDay": 24, "maxMarketOrdersPerTurn": 10,
        "farmHandCostMult": 1, "shedCapacity": 100}.items()})
    totals = [Counter(), Counter()]
    mismatch = [0, 0]
    original = engine._commit_unit
    current_farms: list = []
    committed: list = []

    def hook(op, item, price, farm, private, market, shed_capacity=100):
        ok = original(op, item, price, farm, private, market, shed_capacity)
        if ok:
            seat = next((i for i, x in enumerate(current_farms) if x is farm), -1)
            committed.append((seat, op, item, float(price)))
        return ok

    engine._commit_unit = hook
    try:
        for frame in range(1, len(steps)):
            prev, now = steps[frame - 1], steps[frame]
            obs = prev[0]["observation"]
            day = int(obs.get("day", 0))
            farms = copy.deepcopy(obs["farms"])
            current_farms = farms
            private = [copy.deepcopy(prev[s]["observation"]["private"]) for s in (0, 1)]
            market = copy.deepcopy(obs["market"])
            acts = [copy.deepcopy(now[s].get("action") or {}) for s in (0, 1)]
            for s in (0, 1):
                units = [acts[s].get("farmer", ["PASS"]), *(acts[s].get("hands") or [])]
                demand = Counter(a[1] for a in units
                                 if isinstance(a, list) and len(a) >= 2 and a[0] == "PLANT")
                blocked = {c for c, n in demand.items() if n > private[s].get("seeds", {}).get(c, 0)}
                for ui, a in enumerate(units):
                    if isinstance(a, list) and len(a) >= 2 and a[0] == "PLANT" and a[1] in blocked:
                        a = ["PASS"]
                    engine._apply_unit_action(farms[s], private[s], ui, a,
                                              int(config.boardSize), day,
                                              int(config.turnsPerDay), int(config.shedCapacity))
            states = [SimpleNamespace(
                observation=SimpleNamespace(market=market, farms=farms, private=private[s]),
                action=acts[s]) for s in (0, 1)]
            committed.clear()
            engine._process_market(states, SimpleNamespace(configuration=config))
            for s, op, item, price in committed:
                totals[s][(op, item)] += price
            for s in (0, 1):
                if abs(float(farms[s]["money"]) - float(now[s]["observation"]["farms"][s]["money"])) > 0.011:
                    mismatch[s] += 1
    finally:
        engine._commit_unit = original
    return totals, mismatch


def lifecycle(game: dict, seat: int) -> dict:
    steps = game["steps"]
    out = {"buy": [], "pickup": [], "place": [], "feed": [], "care": [], "harvest": []}
    cow_pos = None
    cow_tile = None
    for frame in range(1, len(steps)):
        prev, now = steps[frame - 1], steps[frame]
        obs = prev[seat]["observation"]
        act = now[seat].get("action") or {}
        day = int(obs.get("day", 0))
        hour = int(obs.get("hour", 0))
        farm = obs["farms"][seat]
        units = [act.get("farmer", ["PASS"]), *(act.get("hands") or [])]
        positions = [farm.get("farmer"), *list(farm.get("hands") or [])]
        for ui, a in enumerate(units):
            if not isinstance(a, list) or not a:
                continue
            if day == 6 and a[0] == "BUY_ANIMAL":
                pass
            if day == 6 and a[0] == "PICKUP" and len(a) > 1 and a[1] == "COW":
                out["pickup"].append({"hour": hour, "actor": ui})
            if day == 6 and a[0] == "PLACE" and len(a) > 1 and a[1] == "COW":
                cow_pos = tuple(positions[ui]) if ui < len(positions) and positions[ui] else None
                out["place"].append({"hour": hour, "actor": ui, "pos": cow_pos})
            if cow_pos and ui < len(positions) and tuple(positions[ui] or ()) == cow_pos:
                if a[0] == "FEED":
                    out["feed"].append(day)
                if a[0] == "CARE":
                    out["care"].append(day)
                if a[0] == "HARVEST":
                    tile = farm["tiles"][cow_pos[1]][cow_pos[0]]
                    if isinstance(tile, dict) and tile.get("animal") == "COW":
                        out["harvest"].append({"day": day, "units": tile.get("yield_units", 0)})
                        cow_tile = cow_pos
        for order in (act.get("market") or []):
            if (isinstance(order, list) and len(order) >= 3 and order[0] == "BUY_ANIMAL"
                    and order[1] == "COW" and day == 6):
                out["buy"].append({"hour": hour, "n": int(order[2])})
    farms = steps[-1][seat]["observation"]["farms"]
    final = farms[seat]
    alive = any(isinstance(t, dict) and t.get("animal") == "COW"
                for row in final.get("tiles") or [] for t in row)
    out["cow_alive_at_end"] = alive
    out["milk_harvest_units"] = sum(h["units"] for h in out["harvest"])
    return out


def main() -> int:
    rows = []
    for tag in ("v92", "v50"):
        run = HERE / "runs" / f"dev_vs_{tag}" / "games.jsonl"
        if not run.exists():
            continue
        for line in run.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            replay_path = r.get("replay_path")
            if not replay_path or not Path(replay_path).exists():
                continue
            game = json.loads(Path(replay_path).read_text())
            life = lifecycle(game, r["candidate_seat"])
            totals, mismatch = settle(game)
            rows.append({
                "opponent": tag, "seed": r["seed"], "game_id": r["game_id"],
                "candidate_seat": r["candidate_seat"],
                "fired": bool(life["buy"]),
                "buy": life["buy"], "pickup": life["pickup"], "place": life["place"],
                "cow_alive_at_end": life["cow_alive_at_end"],
                "milk_harvest_units": life["milk_harvest_units"],
                "feed_days": len(set(life["feed"])), "care_days": len(set(life["care"])),
                "cash_milk": totals[r["candidate_seat"]].get(("SELL", "MILK"), 0),
                "cash_wool": totals[r["candidate_seat"]].get(("SELL", "WOOL"), 0),
                "cash_mismatch_turns": mismatch[r["candidate_seat"]],
            })
    (HERE / "panel_lifecycle.json").write_text(
        json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    fired = [r for r in rows if r["fired"]]
    print(f"retained replays audited: {len(rows)}  fired: {len(fired)}")
    if fired:
        print(f"  three-step complete: "
              f"{sum(1 for r in fired if r['pickup'] and r['place'])}/{len(fired)}")
        print(f"  cow alive at end:    "
              f"{sum(1 for r in fired if r['cow_alive_at_end'])}/{len(fired)}")
        print(f"  milk harvested:      min {min(r['milk_harvest_units'] for r in fired)} "
              f"max {max(r['milk_harvest_units'] for r in fired)} "
              f"mean {sum(r['milk_harvest_units'] for r in fired)/len(fired):.1f}")
        print(f"  cash mismatches:     {sum(r['cash_mismatch_turns'] for r in fired)}")
        print(f"  accepted cash:       milk ${min(r['cash_milk'] for r in fired):,.0f}.."
              f"${max(r['cash_milk'] for r in fired):,.0f}  "
              f"wool ${min(r['cash_wool'] for r in fired):,.0f}.."
              f"${max(r['cash_wool'] for r in fired):,.0f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

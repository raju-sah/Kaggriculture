"""Exact-loader probe agent: frozen V92 + a day-6 h6 state recorder.

Kaggle's `get_last_callable` execs this file in a fresh namespace with no
`__file__` and binds the LAST module-level callable, so the entrypoint is
assigned last. Paths resolve from the current working directory (the tournament
and match_worker always run from the repo root).
"""

import json
import os

from kaggle_environments.agent import get_last_callable

ROOT = os.getcwd()
V92_PATH = os.path.join(ROOT, "experiments", "v92_overflow_guard", "candidate.py")

_V92 = get_last_callable(open(V92_PATH, encoding="utf-8").read(), path=V92_PATH)


def _probe_state(obs):
    private = obs.get("private") or {}
    shed = private.get("shed") or {}
    market = obs.get("market") or {}
    inv = market.get("inventory") or {}
    prices = market.get("prices") or {}
    farms = obs.get("farms")
    player = obs.get("player")
    farm = None
    if farms is not None and player is not None and 0 <= player < len(farms):
        farm = farms[player]
    pasture_slots = 0
    live = {}
    for row in (farm.get("tiles") if farm else None) or []:
        for tile in row:
            if isinstance(tile, dict) and "animal" in tile:
                live[tile["animal"]] = live.get(tile["animal"], 0) + 1
            if isinstance(tile, dict) and tile.get("kind") == "PASTURE":
                pasture_slots += 1
    return {
        "market_milk": int(inv.get("MILK", 10000)),
        "market_wool": int(inv.get("WOOL", 10000)),
        "price_milk": int(prices.get("MILK", 0)),
        "price_wool": int(prices.get("WOOL", 0)),
        "shops": list((obs.get("town") or {}).get("unlocked_shops") or []),
        "shed_milk": int(shed.get("MILK", 0)),
        "shed_wool": int(shed.get("WOOL", 0)),
        "shed_total": int(sum(shed.values())),
        "live_animals": live,
        "pasture_slots": pasture_slots,
        "money": (farm or {}).get("money"),
    }


def _tape_animals(action):
    sheep_buy = cow_buy = 0
    for order in (action.get("market") or []):
        if isinstance(order, list) and len(order) >= 3 and order[0] == "BUY_ANIMAL":
            if order[1] == "SHEEP":
                sheep_buy += int(order[2])
            elif order[1] == "COW":
                cow_buy += int(order[2])
    acts = [action.get("farmer") or ["PASS"]] + list(action.get("hands") or [])
    sheep_pickup = sum(1 for a in acts if isinstance(a, list) and len(a) > 1 and a[0] == "PICKUP" and a[1] == "SHEEP")
    cow_place = sum(1 for a in acts if isinstance(a, list) and len(a) > 1 and a[0] == "PLACE" and a[1] == "COW")
    sheep_place = sum(1 for a in acts if isinstance(a, list) and len(a) > 1 and a[0] == "PLACE" and a[1] == "SHEEP")
    return {"tape_sheep_buy": sheep_buy, "tape_cow_buy": cow_buy,
            "tape_sheep_pickup": sheep_pickup, "tape_cow_place": cow_place,
            "tape_sheep_place": sheep_place}


def _probe(obs, configuration=None):
    action = _V92(obs, configuration)
    out = os.environ.get("V101_PROBE_OUT")
    if not out or not isinstance(obs, dict):
        return action
    day = obs.get("day")
    hour = obs.get("hour")
    if day != 6:
        return action
    rec = _probe_state(obs)
    rec.update(_tape_animals(action))
    rec["hour"] = hour
    rec["seed"] = int(os.environ.get("V101_PROBE_SEED", "-1"))
    rec["opponent"] = os.environ.get("V101_PROBE_OPPONENT", "?")
    with open(out, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")
    return action


_kaggle_submission_entrypoint = _probe

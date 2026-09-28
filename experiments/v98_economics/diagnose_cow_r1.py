#!/usr/bin/env python3
"""V98 step 4: did the extra cow actually get bought, placed, fed and sold?

The screen showed a small but perfectly consistent loss (every seed negative, roughly
-400 to -8,500). That is the signature of a route that pays a real cost and does not
collect the modeled gain, not of a route that never fired. This isolates which of the
lifecycle stages worked, using a retained game replayed under the exact loader.

The candidate's lifecycle promise is:
    buy -> build -> pickup -> place -> feed -> care -> harvest -> drop -> sell

Each stage is checked against the real engine on a retained replay:

  S1 BOUGHT      does BUY_ANIMAL COW actually commit? (cost deducted, shed +1)
  S2 PLACED      does the cow reach a PASTURE tile, and how long does it sit in the shed?
  S3 FED         is it fed every day from placement to the end? Feed failure deletes the
                 animal after 2 days (engine 813-820), which would turn a +$1,030 cow
                 into a -$400 loss plus a freed structure.
  S4 CARED       is CARE issued, and does the pending_care_bonus actually get spent?
  S5 PRODUCED    how many MILK units does it yield relative to the 17 the model predicts?
  S6 SOLD        is the milk sold, and at what price relative to the $139.33 realized?
  S7 COST        the full cash effect: purchase + feed + market impact vs milk revenue.

The stage that fails determines the revision, and the assignment allows exactly one.

Run from repo root:
    .venv/bin/python experiments/v98_economics/diagnose_cow.py
"""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

from kaggle_environments.envs.kaggriculture import kaggriculture as engine

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
TURNS_PER_DAY = 24
SHED_CAPACITY = 100

spec = importlib.util.spec_from_file_location("cand", HERE / "candidate_r1.py")
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
spec_v92 = importlib.util.spec_from_file_location("v92", ROOT / "experiments/v92_overflow_guard/candidate.py")
V92 = importlib.util.module_from_spec(spec_v92)
spec_v92.loader.exec_module(V92)


def norm(obs):
    if obs.get("step") is not None:
        return obs
    obs = dict(obs)
    obs["step"] = int(obs.get("day", 0) or 0) * TURNS_PER_DAY + int(obs.get("hour", 0) or 0)
    return obs


def run_policy(policy, game, seat, label):
    steps = game["steps"]
    cfg = SimpleNamespace(boardSize=10, maxMarketOrdersPerTurn=10, farmHandCostMult=1,
                          shedCapacity=SHED_CAPACITY, turnsPerDay=TURNS_PER_DAY)
    identity = {}
    stats = {"bought": 0, "purchase_cash": 0.0, "placed": 0, "feed_ok": 0, "feed_fail": 0,
             "care": 0, "milk_harvested": 0, "milk_sold": 0, "milk_cash": 0.0,
             "wheat_bought": 0, "wheat_cash": 0.0, "shed_cow_frames": 0, "escapes": 0}
    orig_commit = engine._commit_unit
    orig_apply = engine._apply_unit_action
    prev_cows = None

    def tracked_commit(op, item, price, farm, private, market, shed_capacity=SHED_CAPACITY):
        who = identity.get(id(private))
        ok = orig_commit(op, item, price, farm, private, market, shed_capacity)
        if ok and who == seat:
            if op == "BUY_ANIMAL" and item == "COW":
                stats["bought"] += 1
                stats["purchase_cash"] += float(price)
            elif op == "SELL" and item == "MILK":
                stats["milk_sold"] += 1
                stats["milk_cash"] += float(price)
            elif op == "BUY_PRODUCT" and item == "WHEAT":
                stats["wheat_bought"] += 1
                stats["wheat_cash"] += float(price)
        return ok

    def tracked_apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity=SHED_CAPACITY):
        who = identity.get(id(private))
        op = action[0] if isinstance(action, list) and action else None
        if who == seat and op == "HARVEST":
            pos = engine._farmer_position(farm, idx)
            if pos is not None:
                t = farm["tiles"][pos[1]][pos[0]]
                if isinstance(t, dict) and t.get("animal") == "COW":
                    stats["milk_harvested"] += int(t.get("yield_units", 0) or 0)
        if who == seat and op == "PLACE" and len(action) > 1 and action[1] == "COW":
            stats["placed"] += 1
        if who == seat and op == "CARE":
            stats["care"] += 1
        if who == seat and op == "FEED":
            pos = engine._farmer_position(farm, idx)
            if pos is not None:
                t = farm["tiles"][pos[1]][pos[0]]
                if isinstance(t, dict) and t.get("animal") and not t.get("fed_today"):
                    inv = engine._farmer_inventory(private, idx)
                    if inv.get("WHEAT", 0) >= 1:
                        stats["feed_ok"] += 1
                    else:
                        stats["feed_fail"] += 1
        return orig_apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity)

    engine._commit_unit = tracked_commit
    engine._apply_unit_action = tracked_apply
    try:
        for frame in range(1, len(steps)):
            prev, cur = steps[frame - 1], steps[frame]
            prev_obs = prev[0]["observation"]
            day = int(prev_obs.get("day", 0))
            obs = norm(prev[0]["observation"])
            farms = copy.deepcopy(prev_obs["farms"])
            private = [copy.deepcopy(prev[s]["observation"]["private"]) for s in range(2)]
            market = copy.deepcopy(prev_obs["market"])
            identity.clear()
            identity[id(private[0])] = 0
            identity[id(private[1])] = 1

            cows = sum(1 for row in farms[seat]["tiles"] for t in row
                       if isinstance(t, dict) and t.get("animal") == "COW")
            if prev_cows is not None and cows < prev_cows:
                stats["escapes"] += prev_cows - cows
            prev_cows = cows
            stats["shed_cow_frames"] += int(private[seat]["shed"].get("COW", 0) or 0)

            if policy is None:
                actions = [copy.deepcopy(cur[s].get("action") or {}) for s in range(2)]
            else:
                mine = policy(obs, {})
                other = copy.deepcopy(cur[1 - seat].get("action") or {})
                actions = [mine, other] if seat == 0 else [other, mine]
            for s in range(2):
                units = [actions[s].get("farmer", ["PASS"]), *(actions[s].get("hands") or [])]
                for ui, a in enumerate(units):
                    engine._apply_unit_action(farms[s], private[s], ui, a, 10, day,
                                              TURNS_PER_DAY, SHED_CAPACITY)
            states = [SimpleNamespace(observation=SimpleNamespace(market=market, farms=farms, private=private[s]),
                                      action=actions[s]) for s in range(2)]
            engine._process_market(states, SimpleNamespace(configuration=cfg))
            step = int(obs.get("step", day * TURNS_PER_DAY))
            if (step + 1) % TURNS_PER_DAY == 0:
                engine._drop_inventories_to_shed(private[0], SHED_CAPACITY)
                engine._drop_inventories_to_shed(private[1], SHED_CAPACITY)
    finally:
        engine._commit_unit = orig_commit
        engine._apply_unit_action = orig_apply

    stats["label"] = label
    return stats


def main():
    import glob
    p = sorted(glob.glob(str(ROOT / "experiments/kaggle/v92_official/episode-*-replay.json")))[0]
    game = json.loads(Path(p).read_text())
    names = [a["Name"] for a in game["info"]["Agents"]]
    seat = names.index("Rajusah")

    base = run_policy(None, game, seat, "V92 recorded")
    route = run_policy(lambda o, c: C._r1_entrypoint(o, c), game, seat, "V98-R1 windowed cow")

    print("=" * 100)
    print(f"V98 STEP 4b: LIFECYCLE AUDIT (R1) (episode {game['info']['EpisodeId']}, seat {seat})")
    print("=" * 100)
    print(f"\n  {'stage':<28} {'V92 recorded':>14} {'V98 route':>12} {'delta':>12}")
    keys = [("bought", "S1 bought COW"), ("purchase_cash", "   purchase cash"),
            ("placed", "S2 placed COW"), ("shed_cow_frames", "   cow-turns in shed"),
            ("feed_ok", "S3 FEED succeeded"), ("feed_fail", "S3 FEED failed (no wheat)"),
            ("care", "S4 CARE"), ("milk_harvested", "S5 MILK harvested"),
            ("milk_sold", "S6 MILK sold"), ("milk_cash", "   milk cash"),
            ("wheat_bought", "   WHEAT units"), ("wheat_cash", "   WHEAT cash"),
            ("escapes", "   cows escaped")]
    for k, label in keys:
        b, r = base[k], route[k]
        print(f"  {label:<28} {b:>14} {r:>12} {r-b:>+12}")

    print()
    print("  S7 FULL CASH EFFECT of the extra cow:")
    d_cash = (route["milk_cash"] - base["milk_cash"]) - (route["purchase_cash"] - base["purchase_cash"]) \
        - (route["wheat_cash"] - base["wheat_cash"])
    print(f"     extra milk cash      ${route['milk_cash'] - base['milk_cash']:>+10,.0f}")
    print(f"     extra purchase cost  ${-(route['purchase_cash'] - base['purchase_cash']):>+10,.0f}")
    print(f"     extra WHEAT spend    ${-(route['wheat_cash'] - base['wheat_cash']):>+10,.0f}")
    print(f"     NET of the extra cow ${d_cash:>+10,.0f}")
    print()
    print("  MODEL PREDICTION: a cow placed day 6 yields 17 MILK lifetime, gross $2,369,")
    print("  minus $939 feed and $400 purchase = +$1,030.")
    print()
    if route["bought"] == 0:
        print("  FINDING: the cow was never bought. The overlay's guards are too strict for the")
        print("  real tape state on day 6, and the route is a no-op that still loses, which")
        print("  would mean the loss is market-side, not farm-side.")
    elif route["placed"] == 0:
        print("  FINDING: the cow was BOUGHT but never PLACED. It sat in the shed, blocked a")
        print("  shed slot, and was eventually deleted at the end-of-day drop. That is a")
        print("  -$400 loss plus a contended shed, which matches the observed small loss.")
    elif route["feed_fail"] > 0:
        print("  FINDING: the cow was placed but FEED failed on some days, so it was at risk")
        print("  of the 2-day escape. A cow that is placed but not fed is worse than no cow.")
    else:
        print("  FINDING: the lifecycle completed. Compare the realised NET with the model's")
        print("  +$1,030 to see which assumption was wrong (price, yield, or feed cost).")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""V94 step 5: is the WOOL glut self-inflicted, and is there a cash lever?

The verified cash identity (exact to $0.00 on all 14 official replays) closes the
cost side: there is no waste to recover in spending. It also closes the terminal
side: V92 leaves $0 standing yield, $0 in the shed, $0 in hand at step 718. So
the only lever that can move the score is REVENUE, and the largest revenue
anomaly is WOOL: 14.9% of sale cash (273,694) but sold at ~$20 mean against a
$218 peak quote.

V93 tried "hold WOOL at the floor" and it FAILED, for a measured reason: it
crowded the shed and never re-offered the stock, so cash fell ~25k and was
mostly lost OUTSIDE WOOL. That failure tells us the lever is not about the price
of the WOOL sold, it is about the OTHER revenue that WOOL crowding destroyed.

This script isolates the counterfactual precisely. The engine's glut is driven by
the SHARED market inventory (market["inventory"]["WOOL"]), which is fed by BOTH
players' sales and drained only by town demand. So the question that decides a
real WOOL strategy is:

  Does Rajusah's OWN WOOL selling push the shared price down, and how much of the
  glut is self-inflicted vs the opponent's?

It records, per game, the exact trajectory of market WOOL inventory and the
price, decomposed into: town drain, opponent supply, and Rajusah's own supply.
This tells us whether reducing our own WOOL volume raises our own WOOL price
enough to be net-positive, and whether the opponent's WOOL is the real glut.

Replay integrity: every transition replayed through the pinned engine; cash must
match exactly. Only experiments/kaggle/v92_official/ read; no V88 joins.
"""

from __future__ import annotations

import copy
import glob
import json
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

from kaggle_environments.envs.kaggriculture import kaggriculture as engine

ROOT = Path(__file__).resolve().parents[2]
REPLAY_DIR = ROOT / "experiments/kaggle/v92_official"
HERE = Path(__file__).resolve().parent
TURNS_PER_DAY = 24
SHED_CAPACITY = 100
I0 = engine.MARKET_I0


def norm(obs: dict) -> dict:
    if obs.get("step") is not None:
        return obs
    obs = dict(obs)
    obs["step"] = int(obs.get("day", 0) or 0) * TURNS_PER_DAY + int(obs.get("hour", 0) or 0)
    return obs


def analyze(path: Path, seat: int) -> dict:
    game = json.loads(path.read_text())
    steps = game["steps"]
    cfg = SimpleNamespace(boardSize=10, maxMarketOrdersPerTurn=10, farmHandCostMult=1,
                          shedCapacity=SHED_CAPACITY, turnsPerDay=TURNS_PER_DAY)
    identity: dict = {}
    cash_mismatches = [0, 0]

    # WOOL market trajectory and who fed it.
    wool_inv: list[int] = []          # shared inventory after each town consume
    wool_price: list[int] = []
    own_wool_supply = 0               # units Rajusah added to shared supply (price>1)
    opp_wool_supply = 0
    own_wool_sold = 0
    own_wool_cash = 0.0
    own_wool_price_list: list[int] = []
    floor_supply_skipped = 0          # units sold at $1 that did NOT add supply
    town_drain_wool = 0

    orig_commit = engine._commit_unit
    turn_own_supply = 0
    turn_opp_supply = 0

    def tracked_commit(op, item, price, farm, private, market, shed_capacity=SHED_CAPACITY):
        nonlocal own_wool_supply, opp_wool_supply, own_wool_sold, own_wool_cash, floor_supply_skipped
        nonlocal turn_own_supply, turn_opp_supply
        who = identity.get(id(private))
        ok = orig_commit(op, item, price, farm, private, market, shed_capacity)
        if ok and op == "SELL" and item == "WOOL":
            p = int(price)
            if p > engine.PRICE_FLOOR:
                if who == seat:
                    own_wool_supply += 1
                    turn_own_supply += 1
                elif who is not None:
                    opp_wool_supply += 1
                    turn_opp_supply += 1
            else:
                floor_supply_skipped += 1
            if who == seat:
                own_wool_sold += 1
                own_wool_cash += float(p)
                own_wool_price_list.append(p)
        return ok

    engine._commit_unit = tracked_commit
    try:
        for frame in range(1, len(steps)):
            prev, cur = steps[frame - 1], steps[frame]
            turn_own_supply = 0
            turn_opp_supply = 0
            prev_obs = prev[0]["observation"]
            day = int(prev_obs.get("day", 0))
            farms = copy.deepcopy(prev_obs["farms"])
            private = [copy.deepcopy(prev[s]["observation"]["private"]) for s in range(2)]
            market = copy.deepcopy(prev_obs["market"])
            identity.clear()
            identity[id(private[0])] = 0
            identity[id(private[1])] = 1
            actions = [copy.deepcopy(cur[s].get("action") or {}) for s in range(2)]
            for s in range(2):
                units = [actions[s].get("farmer", ["PASS"]), *(actions[s].get("hands") or [])]
                for ui, a in enumerate(units):
                    engine._apply_unit_action(farms[s], private[s], ui, a,
                                              int(cfg.boardSize), day, TURNS_PER_DAY, int(cfg.shedCapacity))
            states = [SimpleNamespace(observation=SimpleNamespace(market=market, farms=farms, private=private[s]),
                                      action=actions[s]) for s in range(2)]
            engine._process_market(states, SimpleNamespace(configuration=cfg))
            # The recorded next-observation market already contains this turn's
            # settlement AND the town drain, so the honest read of the shared WOOL
            # glut is the recorded inventory itself. No _town_consume call here:
            # it would double-drain the state the cash audit depends on.
            next_inv = int(cur[0]["observation"]["market"]["inventory"].get("WOOL", I0))
            wool_inv.append(next_inv)
            wool_price.append(int(cur[0]["observation"]["market"].get("prices", {}).get("WOOL", 0)))
            # Town drain this turn = prev_inv + our supply + opponent supply - next_inv,
            # recovered from the recorded shared inventory rather than by re-running
            # _town_consume, which would double-drain the state the cash audit needs.
            prev_inv = int(prev_obs["market"]["inventory"].get("WOOL", I0))
            town_drain_wool += prev_inv + turn_own_supply + turn_opp_supply - next_inv
            market["inventory"]["WOOL"] = next_inv
            for s in range(2):
                observed = float(cur[s]["observation"]["farms"][s]["money"])
                if abs(float(farms[s]["money"]) - observed) > 0.011:
                    cash_mismatches[s] += 1
    finally:
        engine._commit_unit = orig_commit

    return {
        "episode_id": game.get("info", {}).get("EpisodeId"),
        "cash_mismatches": sum(cash_mismatches),
        "own_wool_sold": own_wool_sold,
        "own_wool_cash": round(own_wool_cash, 2),
        "own_wool_mean_price": round(own_wool_cash / max(1, own_wool_sold), 2),
        "own_wool_supply_added": own_wool_supply,
        "opp_wool_supply_added": opp_wool_supply,
        "floor_supply_skipped": floor_supply_skipped,
        "town_drain_wool": town_drain_wool,
        "wool_inv_min": min(wool_inv) if wool_inv else I0,
        "wool_inv_final": wool_inv[-1] if wool_inv else I0,
        "wool_price_min": min(wool_price) if wool_price else 0,
        "wool_price_first": own_wool_price_list[0] if own_wool_price_list else 0,
        "own_wool_price_first_10": own_wool_price_list[:10],
    }


def main():
    paths = [Path(p) for p in sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))]
    results = []
    for p in paths:
        game = json.loads(p.read_text())
        names = [a["Name"] for a in game["info"]["Agents"]]
        results.append(analyze(p, names.index("Rajusah")))
        r = results[-1]
        print(f"  {r['episode_id']} mism={r['cash_mismatches']} ownSold={r['own_wool_sold']} "
              f"meanP={r['own_wool_mean_price']} ownSupply={r['own_wool_supply_added']} "
              f"oppSupply={r['opp_wool_supply_added']} townDrain={r['town_drain_wool']}")
    (HERE / "probe_out/wool_glut.json").write_text(json.dumps(results, indent=2) + "\n")

    print()
    print("=" * 108)
    print("WOOL GLUT DECOMPOSITION: who drives the shared WOOL glut?")
    print("=" * 108)
    print(f"{'epid':>10} {'ownSold':>8} {'ownSupply':>10} {'oppSupply':>10} {'townDrain':>10} {'ownMeanP':>9} {'floorSkipped':>12}")
    to = oo = td = 0
    for r in results:
        print(f"{r['episode_id']:>10} {r['own_wool_sold']:>8} {r['own_wool_supply_added']:>10} "
              f"{r['opp_wool_supply_added']:>10} {r['town_drain_wool']:>10} {r['own_wool_mean_price']:>9} "
              f"{r['floor_supply_skipped']:>12}")
        to += r["own_wool_supply_added"]; oo += r["opp_wool_supply_added"]; td += r["town_drain_wool"]
    print(f"{'TOTAL':>10} {'':>8} {to:>10} {oo:>10} {td:>10}")
    print(f"\n  own supply {to} vs opponent supply {oo} vs town drain {td}")
    if oo > to:
        print("  => the OPPONENT's WOOL is the larger glut driver; our WOOL is the minority contributor.")
    else:
        print("  => OUR OWN WOOL is the majority glut driver; reducing our own supply could help.")


if __name__ == "__main__":
    main()

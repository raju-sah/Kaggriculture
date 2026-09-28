"""Contract and safety tests for the V101 candidate.

The rule is a multi-turn all-chain gate, so the tests drive it the way the game
does, across the three day-6 turns V99 measured: d6h6 BUY, a later-turn PICKUP,
and a later-turn PLACE.

  1. the Kaggle exact loader binds the intended entrypoint;
  2. the embedded in-file price function equals the engine's `market_price`;
  3. the full estimate equals the engine-backed reference model;
  4. the rule is a strict no-op on every day other than 6, and at d6h6 with a
     non-positive delta;
  5. a positive delta buys exactly one cow at d6h6 and leaves every other order
     alone (no broad sell holding);
  6. the cow pickup and the cow place are rewritten on LATER day-6 turns, never
     on the buy turn (this is the regression that made the first build a no-op);
  7. with no cow in the shed the later turns are untouched (no unplaced cow);
  8. the place rewrite is gated on that carrier actually carrying a COW.

Run:  .venv/bin/python experiments/v101_commandcode/test_candidate.py
"""

from __future__ import annotations

import hashlib
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from kaggle_environments.agent import get_last_callable  # noqa: E402
from kaggle_environments.envs.kaggriculture import kaggriculture as K  # noqa: E402

import valuation as V  # noqa: E402

CAND = HERE / "candidate.py"
V92 = ROOT / "experiments/v92_overflow_guard/candidate.py"
V92_SHA = "0d5d356baa25703f1a7b753527d1b39e1c7d63478985913be5b3c2550261b806"

failures: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}  {detail}")
        failures.append(label)


def make_obs(*, milk=10000, wool=10000, shops=(), shed=None, inventories=(),
             day=6, hour=6):
    return {
        "day": day, "hour": hour, "player": 0,
        "market": {"inventory": {"MILK": milk, "WOOL": wool}},
        "town": {"unlocked_shops": list(shops)},
        "private": {"shed": dict(shed or {}), "inventories": [dict(i) for i in inventories]},
    }


def buy_action():
    return {
        "farmer": ["PLACE", "SHEEP"],
        "hands": [],
        "market": [["SELL", "WOOL", 12], ["BUY_ANIMAL", "SHEEP", 2],
                   ["BUY_PRODUCT", "WHEAT", 5]],
    }


def main() -> int:
    fn = get_last_callable(CAND.read_text(encoding="utf-8"), path=str(CAND))
    g = fn.__globals__
    apply = g["_v101_apply"]
    price = g["_v101_price"]
    estimate = g["_v101_estimate"]

    print("1. loader contract")
    check("loader binds an entrypoint", callable(fn))
    check("V101 wrapper present", g.get("_v101_entrypoint") is not None)
    check("frozen V92 source hash matches",
          hashlib.sha256(V92.read_bytes()).hexdigest() == V92_SHA)
    check("frozen V92 source embedded verbatim in candidate",
          V92.read_text(encoding="utf-8") in CAND.read_text(encoding="utf-8"))

    print("\n2. in-file price == engine price")
    bad = sum(1 for inv in range(0, 14001, 7) for item in ("MILK", "WOOL")
              if price(item, inv) != K.market_price(item, inv))
    check("all sampled prices match the engine", bad == 0, f"{bad} mismatches")

    print("\n3. estimate == engine-backed reference")
    random.seed(11)
    shops = list(K.SHOPS)
    bad = 0
    for _ in range(2000):
        obs = make_obs(milk=random.randint(0, 12000), wool=random.randint(0, 12000),
                       shops=random.sample(shops, random.randint(0, 4)),
                       shed={"MILK": random.randint(0, 30), "WOOL": random.randint(0, 30)})
        ref = V.estimate(obs, shed={}, sheep_placed_day=6, cow_placed_day=6,
                         own_milk=obs["private"]["shed"]["MILK"],
                         own_wool=obs["private"]["shed"]["WOOL"])["delta"]
        if estimate(obs) != ref:
            bad += 1
    check("2000 randomized estimates match", bad == 0, f"{bad} mismatches")

    print("\n4. no-op guards")
    for day, hour in ((0, 6), (5, 6), (6, 5), (6, 7), (7, 6)):
        obs = make_obs(shops=("PIZZA_SHOP",), day=day, hour=hour, shed={"COW": 1})
        action = buy_action()
        check(f"day={day} hour={hour} untouched", apply(obs, action) == action)
    for day in range(0, 31):
        if day == 6:
            continue
        obs = make_obs(shops=("PIZZA_SHOP",), day=day, hour=8, shed={"COW": 1})
        action = {"farmer": ["PICKUP", "SHEEP"], "hands": [], "market": []}
        check(f"day {day} pickup untouched", apply(obs, action) == action)
    obs = make_obs(wool=9500, shops=("YARN_STORE",))
    check("wool sink gives a negative delta", estimate(obs) < 0, f"{estimate(obs)}")
    action = buy_action()
    check("negative delta does not fire at d6h6", apply(obs, action) == action)

    print("\n5. positive delta buys exactly one cow at d6h6")
    obs = make_obs(milk=9800, wool=10000, shops=("PIZZA_SHOP",))
    check("delta is positive", estimate(obs) > 0, f"{estimate(obs)}")
    out = apply(obs, buy_action())
    buys = [o for o in out["market"] if o[0] == "BUY_ANIMAL"]
    check("two animal buys", len(buys) == 2, str(buys))
    check("one sheep left", any(o[1] == "SHEEP" and o[2] == 1 for o in buys))
    check("one cow bought", any(o[1] == "COW" and o[2] == 1 for o in buys))
    check("wool SELL still first", out["market"][0] == ["SELL", "WOOL", 12])
    check("wheat buy retained", any(o[:2] == ["BUY_PRODUCT", "WHEAT"] for o in out["market"]))
    check("no sell added",
          sum(1 for o in out["market"] if o[0] == "SELL") ==
          sum(1 for o in buy_action()["market"] if o[0] == "SELL"))
    check("list grew by exactly one", len(out["market"]) == 4)

    print("\n6. pickup/place rewritten on LATER day-6 turns")
    # buy turn must not rewrite the pickup/place
    action = {"farmer": ["PLACE", "SHEEP"], "hands": [["PICKUP", "SHEEP"]], "market": []}
    check("h6 does not rewrite a sheep pickup",
          apply(make_obs(shops=("PIZZA_SHOP",), hour=6, shed={"COW": 1}), action) == action)
    # pickup turn, cow in shed
    obs = make_obs(shops=("PIZZA_SHOP",), hour=8, shed={"COW": 1})
    action = {"farmer": ["PICKUP", "SHEEP"], "hands": [], "market": []}
    out = apply(obs, action)
    check("h8 sheep pickup becomes cow pickup", out["farmer"][:2] == ["PICKUP", "COW"],
          str(out["farmer"]))
    check("h8 rest of the action is unchanged", out["farmer"][2:] == action["farmer"][2:])
    # hand pickup
    obs = make_obs(shops=("PIZZA_SHOP",), hour=8, shed={"COW": 1})
    action = {"farmer": ["MOVE", "EAST"], "hands": [["PICKUP", "SHEEP"]], "market": []}
    out = apply(obs, action)
    check("hand sheep pickup becomes cow pickup", out["hands"][0][:2] == ["PICKUP", "COW"],
          str(out["hands"][0]))
    check("farmer untouched when a hand carries the cow",
          out["farmer"] == ["MOVE", "EAST"])
    # place turn, carrier holding the cow
    obs = make_obs(shops=("PIZZA_SHOP",), hour=12, shed={"COW": 0},
                   inventories=[{"COW": 1}])
    action = {"farmer": ["PLACE", "SHEEP"], "hands": [], "market": []}
    out = apply(obs, action)
    check("h12 sheep place becomes cow place", out["farmer"][:2] == ["PLACE", "COW"],
          str(out["farmer"]))
    check("h12 place keeps the same tile", out["farmer"][2:] == action["farmer"][2:])

    print("\n7. later turns with no cow in the shed")
    obs = make_obs(shops=("PIZZA_SHOP",), hour=8, shed={})
    action = {"farmer": ["PICKUP", "SHEEP"], "hands": [], "market": []}
    check("no cow in shed -> pickup untouched", apply(obs, action) == action)
    # The place is guarded by the CARRIER's inventory, not the shed: on the turn
    # after the pickup the shed is empty but the cow is in the carrier's hands,
    # and that is exactly the turn that must still be rewritten.
    obs = make_obs(shops=("PIZZA_SHOP",), hour=12, shed={}, inventories=[{"COW": 1}])
    action = {"farmer": ["PLACE", "SHEEP"], "hands": [], "market": []}
    out = apply(obs, action)
    check("empty shed but carrier holds the cow -> place still rewritten",
          out["farmer"][:2] == ["PLACE", "COW"], str(out["farmer"]))
    # and with no cow anywhere it must not fire
    obs = make_obs(shops=("PIZZA_SHOP",), hour=12, shed={}, inventories=[{"SHEEP": 1}])
    action = {"farmer": ["PLACE", "SHEEP"], "hands": [], "market": []}
    check("no cow anywhere -> place untouched", apply(obs, action) == action)

    print("\n8. place rewrite needs the carrier to hold the cow")
    obs = make_obs(shops=("PIZZA_SHOP",), hour=12, shed={"COW": 0},
                   inventories=[{}, {"SHEEP": 1}])
    action = {"farmer": ["PLACE", "SHEEP"], "hands": [["PLACE", "SHEEP"]], "market": []}
    out = apply(obs, action)
    check("farmer without a cow keeps its sheep place", out["farmer"][:2] == ["PLACE", "SHEEP"])
    check("hand without a cow keeps its sheep place", out["hands"][0][:2] == ["PLACE", "SHEEP"])

    print("\n9. nothing to split")
    obs = make_obs(milk=9800, shops=("PIZZA_SHOP",))
    action = {"farmer": ["PLACE", "SHEEP"], "hands": [["PICKUP", "SHEEP"]],
              "market": [["BUY_ANIMAL", "SHEEP", 1]]}
    check("single-sheep buy is left alone", apply(obs, action) == action)
    # The buy turn is judged on the buy alone. The tape's placement lives on a
    # later day-6 turn, so a MOVE on this turn must still allow the split.
    obs = make_obs(milk=9800, shops=("PIZZA_SHOP",))
    action = {"farmer": ["MOVE", "EAST"], "hands": [], "market": [["BUY_ANIMAL", "SHEEP", 2]]}
    out = apply(obs, action)
    check("buy fires on the buy turn even with no sheep placement yet",
          any(o[:2] == ["BUY_ANIMAL", "COW"] for o in out["market"]), str(out["market"]))

    print()
    if failures:
        print(f"{len(failures)} FAILED: {failures}")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

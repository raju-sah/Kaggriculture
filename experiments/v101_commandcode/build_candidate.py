"""Build the standalone exact-loader V101 candidate.

The candidate is the frozen V92 policy verbatim, plus one day-6 intervention that
converts one unit of the incumbent's own `BUY_ANIMAL SHEEP 2` cohort into
`SHEEP 1` + `COW 1` when an exact-arithmetic model says the marginal accepted
MILK cash beats the marginal accepted WOOL cash it gives up.

Design constraints taken from the V93-V100 postmortems, all enforced here:

  * No wool deferral. We still sell every WOOL unit the tape produces; we only
    choose not to *buy one more sheep*, and only when the model is positive.
  * No extra unplaced cows. The cow is placed by rewriting the SAME carrier's
    SAME `PLACE` action, on the same tile, in the same turn. There is no
    unplaced-cow path at all: if the tape has no sheep errand on day 6, the
    rule does not fire.
  * No worker-route borrowing. We do not add a move, a pickup or a placement;
    we only change the *species label* on actions the tape already emits, and we
    only change the species on the errand that already exists.
  * No broad sell holding. The market list is untouched apart from the one
    sheep quantity and the one inserted cow order, which sits at the same
    index; the wool SELL order and every other order keep their position.
  * No day-0 swap. The rule is gated on `day == 6 and hour == 6`, which is the
    incumbent's own animal-buy turn, so the buy, the pickup and the place all
    line up on one route with no extra worker time.

OUTPUT: a single self-contained agent file, byte-identical to frozen V92 outside
the appended block, whose last module-level callable is the Kaggle entrypoint.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
V92 = ROOT / "experiments/v92_overflow_guard/candidate.py"
OUT = HERE / "candidate.py"

# ---------------------------------------------------------------------------
# Frozen gate. Chosen on the 160001-160060 development panel via
# analyze_states.py; written down here BEFORE any fresh holdout is touched.
# See GATE.md for the derivation and the precommitted numerical criteria.
# ---------------------------------------------------------------------------
DELTA_THRESHOLD = 0

INTERVENTION = '''
# =============================================================================
# V101 adaptive animal decision: observable marginal MILK vs WOOL value.
#
# Appended to the frozen V92 source; nothing above this line is modified.
#
# THE ESTIMATE
# ------------
# At the day-6 h6 BUY_ANIMAL turn the market state, the shop list, our shed and
# the remaining production days are all observable. The engine prices goods with
#     price(inv) = base -/+ amp * f(|inv - I0|)
# and `_process_market` re-quotes *per unit*, so the cash actually banked for n
# units is the walk p(q), p(q+1), ... , p(q+n-1). We reproduce that walk with the
# engine's own `market_price`, walking the town draw-off that `_town_consume`
# applies. That is exact arithmetic, not a Jev profitability guess.
#
# The marginal question the rule answers is one-for-one:
#     accepted MILK cash from one COW
#   - accepted WOOL cash from the one SHEEP we stop buying
#   - the $100 COW-vs-SHEEP purchase difference
#
# Yields come from the engine's own `_daily_refresh_animals` constants
# (COW: first 8, every 2; SHEEP: first 6, every 3) replayed as a pure function
# of the placement day, so a cow placed on day 6 has its first harvest on day 14.
# We deliberately give the cow NO care bonus, which understates it: the tape's
# daily sweep cares for whatever is on the pasture, so the real figure is at
# least this conservative one.
# =============================================================================

_V101_FINAL_DAY = 30          # 720 steps / 24 turns per day, inclusive
_V101_SHOP_SELL_INTERVAL = 4   # engine townShopSellInterval default
_V101_CENTER_SELL_INTERVAL = 24  # engine townCenterSellInterval default
_V101_COW_COST = 400           # engine ANIMALS["COW"]["cost"]
_V101_SHEEP_COST = 500         # engine ANIMALS["SHEEP"]["cost"]
_V101_COW_FIRST, _V101_COW_INTERVAL, _V101_COW_MAX = 8, 2, 6
_V101_SHEEP_FIRST, _V101_SHEEP_INTERVAL, _V101_SHEEP_MAX = 6, 3, 6
_V101_DELTA_THRESHOLD = 0

# Direct MILK sinks. A single-product shop draws TWICE, which is why the
# multiplier matters: YARN_STORE is the only single-product WOOL sink and
# therefore the only shop that doubles the wool draw-off.
_V101_MILK_SINKS = ("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP")
_V101_WOOL_SINKS = ("YARN_STORE",)

_V101_SHOP_TABLE = {
    "BAKERY": ("EGG", "WHEAT"),
    "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE": ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE": ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}


def _v101_price(item, inventory):
    """The engine's own price function, reimplemented in-file.

    `market_price` is not importable from a Kaggle agent file, so this is a
    literal transcription of the pinned engine: MARKET_PARAMS below and
    PRICE_FLOOR = 1. It is arithmetic on the observable market inventory only.
    """
    base, i0, T = _V101_MP[item]
    below, above = _V101_MP_F[item]
    if inventory < i0:
        amp = below[0] * base / _v101_shape(below[1], T, T)
        price = base + amp * _v101_shape(below[1], i0 - inventory, T)
    else:
        amp = above[0] * base / _v101_shape(above[1], T, T)
        price = base - amp * _v101_shape(above[1], inventory - i0, T)
    return 1 if price < 1 else int(round(price))


def _v101_shape(func, x, T):
    if x < 0:
        x = 0.0
    if func == "linear":
        return x
    if func == "sq":
        return x * x
    if func == "sqrt":
        return x ** 0.5
    if func == "log":
        import math
        return math.log(1.0 + x)
    return x


def _v101_sink_units(shop, item):
    products = _V101_SHOP_TABLE[shop]
    if item not in products:
        return 0
    return 2 if len(products) == 1 else 1


def _v101_sink_drain(shops, item):
    total = 0
    for name in shops or ():
        if name in _V101_SHOP_TABLE:
            total += _v101_sink_units(name, item)
    return total


def _v101_produced(placed_day, first, interval, cap, until_day):
    """Units held after each harvest day, from the engine's own constants.

    `_daily_refresh_animals` adds `1 + care_bonus` to `yield_units` on a
    production day and clamps at `max_held`; we pass care_bonus = 0.
    """
    out = []
    units = 0
    for day in range(placed_day + 1, until_day + 1):
        since = day - placed_day - first
        if since >= 0 and since % interval == 0:
            units = min(cap, units + 1)
            out.append((day, units))
    return out


def _v101_accepted_cash(item, inventory0, units, days, drain):
    """Cash from selling `units`, dumped on each eligible day.

    The walk is the point: each unit settles at the price of the inventory
    *before* it lands, so selling into a glut walks the price down unit by unit,
    and a floor of 1 caps the loss. Returns (cash, final_inventory).
    """
    cash = 0
    q = int(inventory0)
    left = int(units)
    for day in days:
        if left <= 0:
            break
        if day % _V101_SHOP_SELL_INTERVAL == 0:
            q -= drain
        if day % _V101_CENTER_SELL_INTERVAL == 0:
            q -= 1
        take = left
        for _ in range(take):
            cash += _v101_price(item, q)
            q += 1
            left -= 1
    return cash, q


def _v101_estimate(obs):
    """Signed dollar value of one SHEEP -> COW substitution, or None."""
    if not isinstance(obs, dict):
        return None
    market = obs.get("market") or {}
    inventory = market.get("inventory") or {}
    if "MILK" not in inventory or "WOOL" not in inventory:
        return None
    shops = (obs.get("town") or {}).get("unlocked_shops") or []

    private = obs.get("private") or {}
    shed = private.get("shed") or {}
    own_milk = int(shed.get("MILK", 0) or 0)
    own_wool = int(shed.get("WOOL", 0) or 0)

    day = int(obs.get("day", 0) or 0)
    placed = day  # the cow is placed on the same day the sheep would have been
    until = _V101_FINAL_DAY
    days = list(range(day, until + 1))

    milk0 = int(inventory["MILK"])
    wool0 = int(inventory["WOOL"])
    milk_drain = _v101_sink_drain(shops, "MILK")
    wool_drain = _v101_sink_drain(shops, "WOOL")

    cow_units = sum(u for _, u in _v101_produced(
        placed, _V101_COW_FIRST, _V101_COW_INTERVAL, _V101_COW_MAX, until))
    sheep_units = sum(u for _, u in _v101_produced(
        placed, _V101_SHEEP_FIRST, _V101_SHEEP_INTERVAL, _V101_SHEEP_MAX, until))

    milk_with, _ = _v101_accepted_cash("MILK", milk0, own_milk + cow_units, days, milk_drain)
    milk_without, _ = _v101_accepted_cash("MILK", milk0, own_milk, days, milk_drain)
    wool_with, _ = _v101_accepted_cash("WOOL", wool0, own_wool + sheep_units, days, wool_drain)
    wool_without, _ = _v101_accepted_cash("WOOL", wool0, own_wool, days, wool_drain)

    return ((milk_with - milk_without)
            - (wool_with - wool_without)
            - (_V101_COW_COST - _V101_SHEEP_COST))


def _v101_find_sheep_buy(orders):
    for index, order in enumerate(orders):
        if (isinstance(order, list) and len(order) >= 3
                and order[0] == "BUY_ANIMAL" and order[1] == "SHEEP"
                and int(order[2]) >= 2):
            return index, int(order[2])
    return None, 0


def _v101_apply(obs, action):
    if not isinstance(obs, dict) or not isinstance(action, dict):
        return action
    if int(obs.get("day", -1) or 0) != 6:
        return action
    hour = int(obs.get("hour", -1) or 0)

    if hour == 6:
        # ---- the single buy decision, made once on the recorded tape ----
        # The tape's own route is fixed (V99 measured: buy d6h6, pickup d6h8,
        # place d6h12), so the buy turn is validated on its own terms only --
        # a sheep cohort of 2+ to split. We deliberately do NOT require a
        # sheep PLACE here: the placement is on a later day-6 turn, so
        # requiring one on this turn made the whole rule unreachable.
        orders = list(action.get("market") or [])
        index, quantity = _v101_find_sheep_buy(orders)
        if index is None:
            return action
        delta = _v101_estimate(obs)
        if delta is None or delta <= _V101_DELTA_THRESHOLD:
            return action
        out = _v92_copy.deepcopy(action)
        out["market"][index][2] = quantity - 1
        out["market"].insert(index + 1, ["BUY_ANIMAL", "COW", 1])
        return out

    # ---- later day-6 turns. The two rewrites are guarded INDEPENDENTLY:
    #      the pickup by the COW waiting in the shed, the place by the COW the
    #      carrier is already holding. A single shed check would wrongly veto the
    #      place on the turn AFTER the pickup emptied the shed. ------------
    out = None
    shed = (obs.get("private") or {}).get("shed") or {}
    actors = [action.get("farmer")] + list(action.get("hands") or [])
    if int(shed.get("COW", 0) or 0) > 0:
        for ai, a in enumerate(actors):
            if isinstance(a, list) and len(a) > 1 and a[0] == "PICKUP" and a[1] == "SHEEP":
                out = out or _v92_copy.deepcopy(action)
                a = list(a)
                a[1] = "COW"
                if ai == 0:
                    out["farmer"] = a
                else:
                    out["hands"][ai - 1] = a
                break
    inventories = (obs.get("private") or {}).get("inventories") or []
    source = out if out is not None else action
    actors = [source.get("farmer")] + list(source.get("hands") or [])
    for ai, a in enumerate(actors):
        if (ai < len(inventories)
                and int((inventories[ai] or {}).get("COW", 0) or 0) > 0
                and isinstance(a, list) and len(a) > 1
                and a[0] == "PLACE" and a[1] == "SHEEP"):
            out = out or _v92_copy.deepcopy(action)
            a = list(a)
            a[1] = "COW"
            if ai == 0:
                out["farmer"] = a
            else:
                out["hands"][ai - 1] = a
            break
    return out if out is not None else action


def _v101_entrypoint(obs, configuration=None):
    return _v101_apply(obs, _v92_entrypoint(obs, configuration))


_kaggle_submission_entrypoint = _v101_entrypoint
'''


def main() -> None:
    src = V92.read_text(encoding="utf-8")
    # The two goods the estimate touches, transcribed from the pinned engine's
    # MARKET_PARAMS: (base, I0, T) and ((below_target, below_func),
    # (above_target, above_func)).
    numeric = {"MILK": (160, 10000, 122), "WOOL": (200, 10000, 105)}
    funcs = {
        "MILK": ((0.60, "sqrt"), (1.60, "linear")),
        "WOOL": ((0.20, "log"), (3.20, "sq")),
    }
    lines = [
        "# MARKET_PARAMS subset used by the V101 estimate, transcribed from the",
        "# pinned engine: (base, I0, T) and ((below_target, below_func),",
        "# (above_target, above_func)).",
        "_V101_MP = " + repr(numeric).replace("'", '"'),
        "_V101_MP_F = " + repr(funcs).replace("'", '"'),
        "",
    ]
    body = "\n".join(lines) + INTERVENTION
    OUT.write_text(src + "\n\n" + body, encoding="utf-8")

    digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
    print(f"wrote {OUT}")
    print(f"sha256 {digest}")
    print(f"v92 source sha256 {hashlib.sha256(src.encode()).hexdigest()}")


if __name__ == "__main__":
    main()

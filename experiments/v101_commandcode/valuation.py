"""Exact-engine marginal accepted-value model for one SHEEP -> COW substitution.

Pinned engine: kaggle-environments 1.32.7, kaggriculture.py
sha256 bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e

Every number here is produced by the engine's own `market_price`, not by an
approximation, and the yield counts are the engine's own `_daily_refresh_animals`
arithmetic replayed as a pure function of (day, placed_day, first_yield_day,
interval, max_held, care bonus, fed).

INPUTS (all observable at the day-6 h6 BUY_ANIMAL decision, none of them a seed id)
  * market inventory / prices for MILK and WOOL   (obs["market"])
  * town unlocked_shops                          (obs["town"])
  * our own shed + pasture supply / output        (obs["private"], own farm tiles)
  * current day, and the pinned episode length    (obs["day"], 720 steps / 24)

OUTPUT: delta = (accepted MILK cash from the COW) - (accepted WOOL cash lost from
the SHEEP), in dollars, net of the $100 purchase-price difference. `delta > 0`
means the substitution is worth making.

WHY ACCEPTED AND NOT QUOTED PRICE
--------------------------------
`_process_market` re-quotes on every single unit. A SELL is settled at the price
of the inventory level *before that unit lands*, so the cash a player actually
banks for n units is the sum of the walk p(q), p(q+1), ..., p(q+n-1). Both a
price collapse and a price rise are therefore exactly captured, per game, by the
replay. The model reproduces that walk rather than multiplying a headline price
by a unit count, which is what the V99 report's "$44,318 / $5,238" market
totals could not do.

WHY THE SELL SCHEDULE IS OBSERVED
---------------------------------
The pinned candidate already places a WOOL SELL order on the tape. The decision
turn is the same turn the tape emits that order, so the *arrival pattern* of
wool is a property of the incumbent policy, not a guess. Milk is a new product
with no incumbent schedule; the model sells it greedily on the first day it can,
which is the best case for the substitution and therefore the conservative
choice for a "do not swap" default.
"""

from kaggle_environments.envs.kaggriculture import kaggriculture as K

# --- pinned season geometry (match_worker passes episodeSteps=720) ------------
TURNS_PER_DAY = 24
EPISODE_STEPS = 720
FINAL_DAY = EPISODE_STEPS // TURNS_PER_DAY  # day 30, inclusive of the last harvest

# Engine defaults, restated so the model is self-documenting against the pin.
SHOP_SELL_INTERVAL = 4        # townShopSellInterval default
TOWN_CENTER_SELL_INTERVAL = 24  # townCenterSellInterval default

MILK_SINKS = frozenset({"PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"})
WOOL_SINKS = frozenset({"YARN_STORE"})


def _price(item, inventory):
    return K.market_price(item, int(inventory))


def milk_sink_units(shop_list):
    """Extra market draw on MILK that a shop list imposes, per consumption step.

    Engine: a shop instance consumes `2 if len(products) == 1 else 1` of each of
    its products, every `townShopSellInterval` steps, for every instance listed.
    """
    units = 0
    for name in shop_list or []:
        products = K.SHOPS[name]
        multiplier = 2 if len(products) == 1 else 1
        if "MILK" in products:
            units += multiplier
    return units


def wool_sink_units(shop_list):
    units = 0
    for name in shop_list or []:
        products = K.SHOPS[name]
        multiplier = 2 if len(products) == 1 else 1
        if "WOOL" in products:
            units += multiplier
    return units


def _project_inventory(item, inventory0, units, day, until_day, include_town_center):
    """Inventory of `item` on each day d in [day, until_day), if nobody sells it.

    The town is the only automatic buyer. Shops draw on `step % 4 == 0`, so days
    `day, day+4, ...`; the town centre draws on `step % 24 == 0`, so exactly the
    days where the hour crosses 0. Both use the day list below, which is the
    authoritative form of the two modulo tests.
    """
    out = {}
    for d in range(day, until_day + 1):
        q = inventory0
        # draws strictly before this day
        for k in range(day, d):
            if k % SHOP_SELL_INTERVAL == 0:
                q -= units
            if include_town_center and k % TOWN_CENTER_SELL_INTERVAL == 0:
                q -= 1
        out[d] = q
    return out


def _milks_kept_without_us(inv_by_day, base_inventory0, day, until_day):
    """How much MILK would sit in the market if we produced and sold none."""
    total = 0
    for d, q0 in inv_by_day.items():
        # start of day d, after that day's own draw is already in inv_by_day
        total += max(0, q0 - base_inventory0)
    return total


def _accepted_cash(item, inventory0, units_available, days, drain, include_town_center, price_cap=12):
    """Cash from selling `units_available`, spread as `drain` per eligible day.

    Models the incumbent behaviour the pinned policy actually runs: dump the
    current shed balance onto the market on each harvest day. `days` is the list
    of days we are on the market. If the shelf is empty on a day the order is a
    no-op, which is exactly what the engine does with an empty shed.
    """
    cash = 0
    q = int(inventory0)
    remaining = int(units_available)
    for d in days:
        if remaining <= 0:
            break
        for k in range(d, d + 1):  # that day's own draw
            if k % SHOP_SELL_INTERVAL == 0:
                q -= drain
            if include_town_center and k % TOWN_CENTER_SELL_INTERVAL == 0:
                q -= 1
        take = remaining
        for _ in range(take):
            p = _price(item, q)
            cash += p
            q += 1
            remaining -= 1
    return cash, q


def _sheep_milks(placed_day, care, fed_every_day, until_day):
    """Engine `_daily_refresh_animals` for a SHEEP, as a pure function.

    `care` counts days the incumbent cared; the bonus is only banked on a day the
    animal is both fed and cared, and is only spent on a fed production day.
    """
    spec = K.ANIMALS["SHEEP"]
    acc = []
    pending = 0
    units = 0
    care_left = int(care)
    for day in range(placed_day + 1, until_day + 1):
        fed = fed_every_day
        if not fed:
            continue  # unfed consecutive days escape the animal; V92 feeds daily
        since = day - placed_day - spec["first_yield_day"]
        banked = 0
        if since >= 0 and since % spec["interval"] == 0:
            if care_left > 0:
                pending += 1
                care_left -= 1
            bonus = pending
            pending = 0
            units = min(spec["max_held"], units + 1 + bonus)
            banked = units
        acc.append((day, banked))
    return acc


def _cow_milks(placed_day, care, until_day):
    """Same function for a COW. First yield is 8 days out, then every 2."""
    spec = K.ANIMALS["COW"]
    acc = []
    pending = 0
    units = 0
    care_left = int(care)
    for day in range(placed_day + 1, until_day + 1):
        since = day - placed_day - spec["first_yield_day"]
        if since < 0 or since % spec["interval"] != 0:
            continue
        if care_left > 0:
            pending += 1
            care_left -= 1
        bonus = pending
        pending = 0
        units = min(spec["max_held"], units + 1 + bonus)
        acc.append((day, units))
    return acc


def _own_sell_days(day, until_day):
    return list(range(day, until_day + 1))


def estimate(obs, shed, sheep_placed_day, cow_placed_day, own_milk, own_wool,
             until_day=FINAL_DAY, cow_cost=400, sheep_cost=500):
    """Return the signed dollar delta of the substitution plus its evidence.

    own_milk / own_wool: our current shed balances for those goods.
    """
    market = obs.get("market") or {}
    inv = market.get("inventory") or {}
    shops = (obs.get("town") or {}).get("unlocked_shops") or []
    day = int(obs.get("day", 0))

    milk0 = int(inv.get("MILK", K.MARKET_PARAMS["MILK"]["I0"]))
    wool0 = int(inv.get("WOOL", K.MARKET_PARAMS["WOOL"]["I0"]))

    milk_drain = milk_sink_units(shops)
    wool_drain = wool_sink_units(shops)

    days = _own_sell_days(day, until_day)

    # --- COW branch: add `own_milk + cow` units, keep the same daily dump -----
    cow_units = _cow_milks(cow_placed_day, care=0, until_day=until_day)
    cow_produced = sum(u for _, u in cow_units)
    milk_in, _ = _accepted_cash("MILK", milk0, int(own_milk) + cow_produced,
                                days, milk_drain, include_town_center=True)
    # counterfactual without the cow
    milk_out, _ = _accepted_cash("MILK", milk0, int(own_milk), days, milk_drain,
                                 include_town_center=True)
    milk_delta = milk_in - milk_out

    # --- SHEEP branch: we stop adding wool --------------------------------
    sheep_units = _sheep_milks(sheep_placed_day, care=0, fed_every_day=True, until_day=until_day)
    sheep_produced = sum(u for _, u in sheep_units)
    wool_in, _ = _accepted_cash("WOOL", wool0, int(own_wool) + sheep_produced,
                                days, wool_drain, include_town_center=True)
    wool_out, _ = _accepted_cash("WOOL", wool0, int(own_wool), days, wool_drain,
                                 include_town_center=True)
    wool_delta = wool_in - wool_out

    cost_delta = cow_cost - sheep_cost

    return {
        "day": day,
        "milk_price": _price("MILK", milk0),
        "wool_price": _price("WOOL", wool0),
        "milk_inventory": milk0,
        "wool_inventory": wool0,
        "milk_drain_per_shop_step": milk_drain,
        "wool_drain_per_shop_step": wool_drain,
        "shops": list(shops),
        "cow_produced": cow_produced,
        "sheep_produced": sheep_produced,
        "own_milk": int(own_milk),
        "own_wool": int(own_wool),
        "milk_accepted_delta": milk_delta,
        "wool_accepted_lost": wool_delta,
        "purchase_price_delta": cost_delta,
        "delta": milk_delta - wool_delta - cost_delta,
    }


if __name__ == "__main__":
    import json
    base = {"market": {"inventory": {"MILK": K.MARKET_PARAMS["MILK"]["I0"],
                                      "WOOL": K.MARKET_PARAMS["WOOL"]["I0"]}},
            "town": {"unlocked_shops": []}, "day": 6}
    r = estimate(base, shed={}, sheep_placed_day=6, cow_placed_day=6, own_milk=0, own_wool=0)
    print("empty market, no shops:", json.dumps(r, indent=2, sort_keys=True))

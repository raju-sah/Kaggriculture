"""V86: opening product-input budget on the frozen V56 lineage.

New file. No frozen file is modified. The frozen V56 agent is exec'd into a
private namespace and one overlay is applied to its market orders.

Why this exists
---------------
V83 (100 elite player-games, exact 1.32.7 settlement) resolved that the elite
separator is execution, not composition: winners and losers hold the same herd
and land, but winners extract 1.15x more sales per animal, and the strongest
early signal is that winners spend opening capital into assets rather than
holding it (day-6 cash 361 vs 594, 0.78 sd).

V85 established a panel with real resolution: V56 beats boey 16/16 with a
median margin of +57,032, so local measurements against strong opponents are
detectable.

This overlay targets the one opening-window number where V56 is far off the elite
profile. Exact reconstruction of a saved V56 game (seed 94400, seat 0) against
the 100-game elite means:

    opening days 0-5     V56      elite WIN   elite LOSE
    accepted sales        3,035      5,319       3,695
    product purchases       967      2,657       1,327
    animal purchases      2,600      3,430       2,782

V56 already sells *below* the elite-losing mean (3,035 vs 3,695) and buys product
far below even that (967 vs 1,327). The overlay spends the opening cash that V56
is currently idling on feed and soil, which is the input that gates both feeding
and fertilising, and therefore gates output.

Scope, fixed before the panel run:
  - applies only on days 0-5 (the measured deficit window);
  - tops up FERTILIZER and WHEAT only, the two products V56 under-buys;
  - only while the farm is still short of hands, i.e. before it has a crew;
  - never spends the last operating coins, never exceeds the market order cap;
  - never adds an order for a product the frozen agent already buys this turn.

This is a hypothesis from observational elite data. It is built to be measured,
not assumed to work, and it is expected to be rejected if it does not win.
"""

V56_SOURCE = "/home/raju/AI-ML Projects/Kaggle Competition/Kaggriculture/agents/v56_agent.py"

OPENING_DAY_MAX = 5      # the measured deficit window
FERT_TOPUP = 3           # units per turn
WHEAT_TOPUP = 4          # units per turn
MIN_CASH_AFTER = 200     # never spend the farm's last operating coins
MAX_MARKET_ORDERS = 10   # engine per-turn cap


def _load(path):
    namespace = {"__name__": "v86_frozen_v56"}
    with open(path, "r", encoding="utf-8") as handle:
        exec(compile(handle.read(), path, "exec"), namespace)  # noqa: S102
    return namespace


_v56_ns = _load(V56_SOURCE)
_v56_agent = _v56_ns["agent"]


def _v86_apply(obs, action):
    day = int(obs.get("day", 0) or 0)
    if day > OPENING_DAY_MAX:
        return action

    seat = int(obs.get("player", 0) or 0)
    farms = obs.get("farms") or []
    if seat >= len(farms):
        return action
    farm = farms[seat]

    # The opening deficit is measured at day boundaries, and the daily reset
    # empties the crew at hour 0, so hour 0 is the one turn in the opening window
    # where V56 still holds uncommitted cash and has no crew. Restricting the
    # overlay to that turn makes it a single decision per day rather than a
    # per-hour drip.
    if int(obs.get("hour", 0) or 0) != 0:
        return action

    cash = float(farm.get("money", 0) or 0)
    if cash <= MIN_CASH_AFTER:
        return action

    market = list(action.get("market") or [])
    room = MAX_MARKET_ORDERS - len(market)
    if room <= 0:
        return action

    existing = {tuple(o[:2]) for o in market if o}

    additions = []
    if ("BUY_PRODUCT", "FERTILIZER") not in existing and room > len(additions):
        if cash - FERT_TOPUP * 90 > MIN_CASH_AFTER:  # fertilizer trades far above wheat
            additions.append(["BUY_PRODUCT", "FERTILIZER", FERT_TOPUP])
    if ("BUY_PRODUCT", "WHEAT") not in existing and room > len(additions):
        if cash - FERT_TOPUP * 90 - WHEAT_TOPUP * 40 > MIN_CASH_AFTER:
            additions.append(["BUY_PRODUCT", "WHEAT", WHEAT_TOPUP])

    if not additions:
        return action
    action["market"] = market + additions
    return action


def _v86_entrypoint(obs, configuration=None):
    return _v86_apply(obs, _v56_agent(obs, configuration))


def _kaggle_submission_entrypoint(obs, configuration=None):
    return _v86_entrypoint(obs, configuration)

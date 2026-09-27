"""V84: feed-budget candidate on the frozen V56 lineage.

New file. No frozen file is modified. The frozen V56 agent is exec'd into a private
namespace and one overlay is applied on top of its market orders.

Why this exists
---------------
V83 resolved what separates elite winners from the panel, using 100 elite
player-games with exact 1.32.7 settlement:

  * Herd composition is NOT the separator. Day-12 goose share 26.4% (winners) vs
    26.3% (losers), sheep share 27.4% vs 27.6%. Elite winners are goose-heavy.
    This falsifies the V80/V81 sheep-for-goose direction.
  * Asset levels are NOT the separator. Day-12 animals 19.8 vs 19.6, crop tiles
    62.2 vs 60.8, quadrants 3.48 vs 3.48 - all within 2%.
  * Execution IS. Winners extract 1.15x more sales per animal and 1.13x more per
    crop tile from an identical asset base.
  * The strongest early signal is that winners hold LESS day-6 cash (361 vs 594,
    0.78 sd) because they spend it into animals and soil inputs.

The concrete input gap this overlay targets, measured on a saved V56 run against
the elite winner means:

    item          V56 accepted spend    elite winner mean    ratio
    WHEAT             ~$4,935                 $18,043         0.27x
    FERTILIZER        ~$8,890                  $6,020         1.48x

The wheat gap is the large one, and it is the item with a hard per-day cost:
every animal consumes 1 WHEAT per day (engine `_apply_unit_action`, FEED
branch) and an animal that misses two consecutive days is deleted at the
day-end tick (`_daily_refresh_animals`, consecutive_unfed >= 2). On the
reference run V56's herd sits at consecutive_unfed >= 1 on most days and peaks
at 11 unfed animals on day 29 - it never triggers the cliff, but it is running
with no margin, and it finishes the season at 71,344 vs the opponent's 71,325,
a 19-coin game.

The overlay therefore does one thing: when the farm has a positive animal
population and the observed shed wheat stock is below a small reserve, buy
enough wheat to restore that reserve, subject to not spending the last reserve
coin and not exceeding the market order limit. It does not change herd targets,
crops, land, hiring, or the sale schedule.

This is a hypothesis from observational elite data, not a demonstrated causal
mechanism. It is built to be measured on a 36-seed panel, not assumed to work.
"""

V56_SOURCE = "/home/raju/AI-ML Projects/Kaggle Competition/Kaggriculture/agents/v56_agent.py"
V56_SHA256 = "see docs; recompute and record before the panel"

# --- overlay parameters (fixed before the panel run) ---
WHEAT_RESERVE = 40        # keep this many WHEAT in the shed for the herd
MAX_WHEAT_BUY = 25        # per turn, and never exceed the order cap
MIN_CASH_AFTER = 150      # never spend the farm's last operating coins on feed
EARLY_DAY_MAX = 29        # no overlay after the season is effectively over


def _load(path):
    namespace = {"__name__": "v84_frozen_v56"}
    with open(path, "r", encoding="utf-8") as handle:
        exec(compile(handle.read(), path, "exec"), namespace)  # noqa: S102
    return namespace


_v56_ns = _load(V56_SOURCE)
_v56_agent = _v56_ns["agent"]


def _animal_count(farm):
    return sum(
        1
        for row in farm.get("tiles") or []
        for tile in row
        if isinstance(tile, dict) and tile.get("animal")
    )


def _shed_wheat(private):
    return int(((private or {}).get("shed") or {}).get("WHEAT", 0) or 0)


def _v84_apply(obs, action):
    """Top up the wheat feed reserve when the herd is live and the buffer is thin."""
    day = int(obs.get("day", 0) or 0)
    if day > EARLY_DAY_MAX:
        return action

    seat = int(obs.get("player", 0) or 0)
    farms = obs.get("farms") or []
    if seat >= len(farms):
        return action
    farm = farms[seat]

    animals = _animal_count(farm)
    if animals <= 0:
        return action

    private = obs.get("private") or {}
    wheat = _shed_wheat(private)
    shortfall = WHEAT_RESERVE - wheat
    if shortfall <= 0:
        return action

    cash = float(farm.get("money", 0) or 0)
    if cash <= MIN_CASH_AFTER:
        return action

    market = action.get("market") or []
    # Respect the engine's per-turn market order cap.
    room = 10 - len(market)
    if room <= 0:
        return action

    # Do not stack another wheat buy in the same turn.
    if any(len(o) > 2 and o[0] == "BUY_PRODUCT" and o[1] == "WHEAT" for o in market if o):
        return action

    buy = min(shortfall, MAX_WHEAT_BUY, room)
    if buy <= 0:
        return action
    action["market"] = list(market) + [["BUY_PRODUCT", "WHEAT", buy]]
    return action


def _v84_entrypoint(obs, configuration=None):
    return _v84_apply(obs, _v56_agent(obs, configuration))


def _kaggle_submission_entrypoint(obs, configuration=None):
    return _v84_entrypoint(obs, configuration)

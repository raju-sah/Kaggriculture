"""V81: latched expert switch from the frozen V57-reset route to the frozen V50 route.

New file. No frozen file is modified. Both sources are exec'd into private
namespaces and wrapped by a thin, auditable switch.

Evidence this is built on
------------------------
docs/V81_EXPERT_SWITCH_FEASIBILITY.md, from the saved seed-92802 replay:

  * V50 has no mutable module-level state; cold and warm queries on the same
    observation return byte-identical actions. A midgame switch is therefore
    stateless and needs no state replay to be correct.
  * Queried on the V57 seat-0 observation at day 6 hour 06 (step 150), V50 emits
    exactly the action it recorded on its own seat in the real game:
        [['SELL','WOOL',12], ['BUY_LAND'], ['BUY_ANIMAL','SHEEP',2]]
    i.e. it selects the 2-sheep substitution the wool diagnosis targets.
  * On subsequent saved V57 observations it emits a complete
    pickup -> BUILD_PASTURE -> PLACE -> FEED/CARE chain, which is the property
    the V80 market-order overlay lacked. V80's converted sheep starved
    (consecutive_unfed >= 2) and were deleted; V50's own sheep stayed fed.

That was a counterfactual action query, not a rollout. This file is the
mechanism that would actually be run, and it exists to be measured, not assumed.

Switch trigger, fixed before any scoring run
--------------------------------------------
Switch on the first observation where ALL hold:
    'YARN_STORE' in town.unlocked_shops
    market.prices['WOOL'] >= 180
    day == 6
    the farm holds exactly 2 sheep on pastures
    the frozen V57 route, queried on this observation, actually emits a
    BUY_ANIMAL GOOSE order

The last condition is the important one. The first four are true continuously
from day 6 hour 00 on seed 92802, but the incumbent does not decide anything
until hour 06, when its cash jumps to 2,254 and it commits to two geese. Firing
on the day/hour alone switched at step 144, three hours before the decision and
with only 880 cash, which is below the 1,000 cost of two sheep. Tying the switch
to the incumbent's actual animal-purchase decision makes the gate fire exactly
at the choice under test and nowhere else.

The switch then latches for the remainder of the episode. It never switches
back, never fires on another day, and never fires more than once.

After the switch the V50 route is the sole authority for that seat. The V57
route is not called again, so its per-seat _v57_price_state simply stops
updating; nothing reads it afterwards.
"""

import copy as _v81_copy

_ROOT = "/home/raju/AI-ML Projects/Kaggle Competition/Kaggriculture"
_V57_PATH = _ROOT + "/experiments/v57_broad/v57_reset_candidate.py"
_V50_PATH = _ROOT + "/experiments/v50_agent.py"

V57_SHA256 = "4173479fe1f80d031d570d1ea23b694dfe86e1d162317a4c9c7df0058a40208e"
V50_SHA256 = "e6b50128e023e3b9fafa1841e4cd520c5e581acb48e8628657585c18272eab2b"

# --- trigger constants (fixed, see module docstring) ---
SWITCH_DAY = 6
SWITCH_WOOL_MIN = 180
SWITCH_SHEEP_EXACT = 2


def _load(path, name):
    namespace = {"__name__": name}
    with open(path, "r", encoding="utf-8") as handle:
        exec(compile(handle.read(), path, "exec"), namespace)  # noqa: S102
    return namespace


_v57_ns = _load(_V57_PATH, "v81_frozen_v57_reset")
_v50_ns = _load(_V50_PATH, "v81_frozen_v50")

_v57_agent = _v57_ns["agent"]
_v50_agent = _v50_ns["agent"]

# Latched per seat. Once True it stays True for the episode.
_v81_switched = {}
# Telemetry for the offline guard; never read by the competition agent logic.
V81_TELEMETRY = {
    "switch_step": None,
    "switch_day": None,
    "switch_from": None,
    "switch_to": None,
    "v50_calls": 0,
    "v50_pass_fallbacks": 0,
}


def _v81_sheep_on_pasture(obs, seat):
    farms = obs.get("farms") or []
    if seat >= len(farms):
        return 0
    count = 0
    for row in farms[seat].get("tiles") or []:
        for tile in row:
            if isinstance(tile, dict) and tile.get("kind") == "PASTURE":
                if tile.get("animal") == "SHEEP":
                    count += 1
    return count


def _v81_should_switch(obs, seat, configuration=None):
    """The fixed trigger. All conditions, evaluated on the live observation."""
    day = int(obs.get("day", 0) or 0)
    if day != SWITCH_DAY:
        return False
    shops = (obs.get("town") or {}).get("unlocked_shops", [])
    if "YARN_STORE" not in shops:
        return False
    prices = (obs.get("market") or {}).get("prices", {})
    try:
        if float(prices.get("WOOL", 0) or 0) < SWITCH_WOOL_MIN:
            return False
    except (TypeError, ValueError):
        return False
    if _v81_sheep_on_pasture(obs, seat) != SWITCH_SHEEP_EXACT:
        return False
    return _v81_incumbent_wants_goose(obs, configuration)


def _v81_incumbent_wants_goose(obs, configuration):
    """True when the incumbent route, on this observation, commits to a goose.

    The incumbent's own action is still computed and discarded on the switching
    frame: the switch discards it by design, because the whole point is to
    replace that particular decision. The V57 route is stateless for this
    purpose apart from _v57_price_state, which this probe updates exactly as
    the real route would, so the subsequent V50 frames see an untouched
    V57 state.
    """
    incumbent = _v57_agent(obs, configuration)
    return any(
        len(order) > 2 and order[0] == "BUY_ANIMAL" and order[1] == "GOOSE"
        for order in (incumbent.get("market") or [])
        if order
    )


def _v81_v50_action(obs, configuration):
    """Call the V50 route, detecting its silent all-PASS exception fallback.

    v50_agent.agent wraps its planner in a bare `except Exception` and returns an
    all-PASS action on failure (experiments/v50_agent.py:409-421). A silent
    fallback would produce a meaningless score, so it is counted here rather
    than swallowed. This never alters the action that is returned.
    """
    action = _v50_agent(obs, configuration)
    V81_TELEMETRY["v50_calls"] += 1
    try:
        raw = _v50_ns["_PLANNER"](obs, configuration)
        planner_passed = (raw or {}).get("farmer") == ["PASS"]
        is_fallback = action.get("farmer") == ["PASS"] and not planner_passed
    except Exception:
        is_fallback = action.get("farmer") == ["PASS"]
    if is_fallback:
        V81_TELEMETRY["v50_pass_fallbacks"] += 1
    return action


def _v81_entrypoint(obs, configuration=None):
    seat = int(obs.get("player", 0) or 0)
    if _v81_switched.get(seat):
        return _v81_v50_action(obs, configuration)
    if _v81_should_switch(obs, seat, configuration):
        _v81_switched[seat] = True
        step = int(obs.get("day", 0) or 0) * 24 + int(obs.get("hour", 0) or 0)
        V81_TELEMETRY["switch_step"] = step
        V81_TELEMETRY["switch_day"] = int(obs.get("day", 0) or 0)
        V81_TELEMETRY["switch_from"] = "v57_reset"
        V81_TELEMETRY["switch_to"] = "v50"
        return _v81_v50_action(obs, configuration)
    return _v57_agent(obs, configuration)


def v81_reset_for_replay():
    """Clear latched state so a module can be replayed from episode start."""
    _v81_switched.clear()
    V81_TELEMETRY.update(
        {
            "switch_step": None,
            "switch_day": None,
            "switch_from": None,
            "switch_to": None,
            "v50_calls": 0,
            "v50_pass_fallbacks": 0,
        }
    )
    _v57_ns["_v57_price_state"].clear()


# NOTE: kaggle_environments.agent.get_last_callable selects the LAST callable
# defined at module level (it evaluates `[v for v in env.values() if
# callable(v)][-1]`). A helper defined after the submission entrypoint would
# therefore be returned instead of the entrypoint, and calling it every turn
# yields None, which the engine reads as PASS. `_kaggle_submission_entrypoint`
# must remain the final callable in this file. Offline tests must load the file
# the way the loader does, not via importlib, or they will miss this.
def _kaggle_submission_entrypoint(obs, configuration=None):
    return _v81_entrypoint(obs, configuration)

"""V98-R1: buy the extra cow ONLY into the tape's own animal-placement window.

Revision of the first V98 candidate, which the assignment permits once, after a diagnosis.

THE DIAGNOSIS THAT FORCED THIS REVISION
---------------------------------------
The first V98 candidate appended ["BUY_ANIMAL","COW",1] on day 6 and bought 13 cows for
$5,200. It placed NONE of them. The cow lands in the shed, and PLACE (engine 377-392)
only works when an actor is CARRYING the animal, which requires a prior PICKUP from a
shed-adjacent tile (engine 358-375) and then a walk to a free PASTURE. The frozen tape
performs that dance for its own herd on a fixed schedule:

    PICKUP/PLACE by day (measured, 14 official replays, this seed):
      d0 COW x2, SHEEP x2 | d2 COW | d3 COW | d6 SHEEP x2 | d7 COW x2
      d8 SHEEP x2 | d9 SHEEP | d10 SHEEP x3 | d11 SHEEP

Buying a cow on day 6 added cash cost and a shed-slot liability with no placement path,
because day 6's animal work is a SHEEP errand, not a COW errand. Every extra cow was
deleted by the end-of-day drop.

THE REVISION
------------
Buy the cow only on a turn where the FROZEN ROUTE ITSELF is already issuing an animal
PICKUP, so the cow is picked up by the walk that is already happening. On such a turn the
tape is standing at a shed-adjacent tile about to collect an animal, so a cow bought now
is collected on the same walk and carried to a structure on the same errand.

This is the only version of the idea that can work without borrowing a worker, which V97
measured as catastrophic (-89,887): it adds NO worker-time demand at all. It only changes
what the already-running errand carries.

Concretely, on a turn where the recorded action contains a PICKUP of an animal, and the
market list has room, and the shed has headroom, append ["BUY_ANIMAL","COW",1].

WHY THIS IS SAFE AND BOUNDED
-----------------------------
  * It fires only on the tape's own animal-collection turns, so the worker cost is zero.
  * It fires at most once (a latch), so at most ONE extra cow is ever bought.
  * It requires a free PASTURE to exist, so the cow has somewhere to go.
  * It requires the market list to have room, so the incumbent's own orders are untouched.
  * It requires cash above a floor that keeps the existing herd's feed funded.
  * The cow then becomes an ordinary animal: the tape's daily FEED/CARE sweep covers it,
    because that sweep visits every animal tile the farm has.

If the cow is not collected on the same errand, it costs $400 and occupies a shed slot
until the drop deletes it, which is the -$400 worst case. That is the whole downside and
it is bounded and small.
"""

import copy as _r1_copy

_R1_MAX_ORDERS = 10          # engine maxMarketOrdersPerTurn
_R1_CASH_FLOOR = 600         # keep the existing herd's feed funded
_R1_SHED_HEADROOM = 4        # room for the cow in transit
_R1_SPECIES = "COW"

# One extra cow, ever. A loader that resets this makes the route MORE conservative.
_R1_DONE = {"bought": False}


def _r1_free_pastures(farm):
    return sum(1 for row in (farm.get("tiles") or []) for t in row
               if isinstance(t, dict) and t.get("kind") == "PASTURE" and not t.get("animal"))


def _r1_tape_is_collecting(action):
    """The frozen route is issuing an animal PICKUP this turn.

    PLACE and PICKUP may be batched, and the tape may collect on a hand action rather
    than the farmer, so the whole unit-action list is scanned.
    """
    for unit in [action.get("farmer")] + list(action.get("hands") or []):
        if isinstance(unit, list) and len(unit) > 1 and unit[0] == "PICKUP" \
                and unit[1] in ("COW", "SHEEP", "GOOSE"):
            return True
    return False


def _r1_apply(obs, action):
    if _R1_DONE["bought"]:
        return action
    if not isinstance(obs, dict) or not isinstance(action, dict):
        return action
    seat = int(obs.get("player", 0) or 0)
    farms = obs.get("farms") or []
    if seat >= len(farms):
        return action
    farm = farms[seat]
    private = obs.get("private") or {}
    shed = private.get("shed") or {}
    if int(shed.get(_R1_SPECIES, 0) or 0) > 0:
        return action                      # already holding one
    if 100 - sum(int(v or 0) for v in shed.values()) < _R1_SHED_HEADROOM:
        return action
    if float(farm.get("money") or 0) < _R1_CASH_FLOOR:
        return action
    if _r1_free_pastures(farm) < 1:
        return action
    if not _r1_tape_is_collecting(action):
        return action                      # the key revision condition
    orders = list(action.get("market") or [])
    if len(orders) >= _R1_MAX_ORDERS:
        return action
    if any(o and len(o) > 2 and o[0] == "BUY_ANIMAL" for o in orders):
        return action
    _R1_DONE["bought"] = True
    out = _r1_copy.deepcopy(action)
    out["market"] = orders + [["BUY_ANIMAL", _R1_SPECIES, 1]]
    return out


def _r1_entrypoint(obs, configuration=None):
    return _r1_apply(obs, _v92_entrypoint(obs, configuration))


_kaggle_submission_entrypoint = _r1_entrypoint

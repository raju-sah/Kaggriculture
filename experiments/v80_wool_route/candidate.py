"""V80 early-Yarn sheep-route candidate: frozen V57-reset lineage + one coupled day-6 conversion.

New file. The frozen lineage files are not modified. This module bundles the frozen
V57 reset candidate source verbatim and appends a single bounded overlay.

The intervention is coupled, not build-only. When the early-Yarn regime holds
(YARN_STORE unlocked, WOOL >= 180, day in the early window) and the farm is at
exactly the 2-sheep state that the frozen route reached before its first goose
purchase, the frozen first goose purchase of that window is converted to two
sheep. The overlay then, and only then:

  1. converts the market order  (GOOSE -> SHEEP, capped at 2 animals total);
  2. routes BUILD_PASTURE ahead of BUILD_COOP while the converted sheep are
     undelivered, so a pasture always exists to receive them;
  3. redirects the shed PICKUP and the delivery PLACE of the converted units so
     the animals travel from the shed to a pasture;
  4. leaves the frozen feed/care route intact, so the extra animals are fed and
     cared for by the same daily worker loop that already services the herd.

Scope limits, all enforced in code:
  - at most 2 animals are ever converted (CONVERT_CAP);
  - the conversion fires only while the farm holds exactly 2 sheep, so it acts on
    the first goose purchase and never on a later one;
  - the window is closed after the first purchase step (day/hour bounded), so a
    second goose purchase is never touched;
  - no other animal purchase is added, removed or resized.

This is evidence-driven but unproven. V50's day-6 sequence in the saved seed
92802 replay shows the same conversion is reachable with no crop displacement;
that is feasibility evidence, not proof that this overlay achieves it.
"""

import copy as _v80_copy

_V80_FROZEN_SOURCE = "/home/raju/AI-ML Projects/Kaggle Competition/Kaggriculture/experiments/v57_broad/v57_reset_candidate.py"

# ---------------------------------------------------------------------------
# Frozen V57-reset lineage, loaded verbatim. Read-only; never written.
# ---------------------------------------------------------------------------
# The frozen bundle is self-contained: it defines its own module-level helpers
# and entrypoint. It is executed into a private namespace rather than this
# module's globals, so its internal names cannot shadow the overlay below and
# this file stays a thin, auditable wrapper around frozen behaviour.
_v80_frozen_ns: dict = {"__name__": "v80_frozen_v57_reset"}
with open(_V80_FROZEN_SOURCE, "r", encoding="utf-8") as _v80_handle:
    exec(compile(_v80_handle.read(), _V80_FROZEN_SOURCE, "exec"), _v80_frozen_ns)

_v80_frozen_agent = _v80_frozen_ns["agent"]

# ---------------------------------------------------------------------------
# V80 overlay
# ---------------------------------------------------------------------------
# Frozen V57 reset candidate sha256, recorded so drift is detectable.
V80_FROZEN_SHA256 = "4173479fe1f80d031d570d1ea23b694dfe86e1d162317a4c9c7df0058a40208e"

CONVERT_CAP = 2           # never convert more than two animals
EARLY_DAY_MAX = 8         # window closes after this day
WOOL_PRICE_MIN = 180      # early-Yarn / high-Wool regime
SHEEP_TRIGGER = 2         # only at the 2-sheep state (first goose purchase)
PLACEMENT_DEADLINE_HOURS = 24

_v80_state: dict = {}


def _v80_counts(farm, private):
    """Return (sheep_total, vacant_pastures, coop_vacancy)."""
    sheep = 0
    vacant_pastures = []
    coop_vacancy = 0
    for y, row in enumerate(farm.get("tiles") or []):
        for x, tile in enumerate(row):
            if not isinstance(tile, dict):
                continue
            kind = tile.get("kind")
            if kind == "PASTURE":
                if tile.get("animal") == "SHEEP":
                    sheep += 1
                elif "animal" not in tile:
                    vacant_pastures.append((x, y))
            elif kind == "COOP" and "animal" not in tile:
                coop_vacancy += 1
    shed = private.get("shed") or {}
    sheep += int(shed.get("SHEEP", 0) or 0)
    for inv in private.get("inventories") or []:
        sheep += int((inv or {}).get("SHEEP", 0) or 0)
    return sheep, vacant_pastures, coop_vacancy


def _v80_gate(obs):
    """Early-Yarn / high-Wool regime inside the bounded early window."""
    day = int(obs.get("day", 0) or 0)
    if day > EARLY_DAY_MAX:
        return False
    shops = (obs.get("town") or {}).get("unlocked_shops", [])
    if "YARN_STORE" not in shops:
        return False
    prices = (obs.get("market") or {}).get("prices", {})
    return float(prices.get("WOOL", 0) or 0) >= WOOL_PRICE_MIN


def _v80_get_state(seat, step):
    state = _v80_state.get(seat)
    if state is None or step <= state.get("step", -1):
        # Episode start, or a new episode in this seat: reset all overlay state.
        state = {
            "step": step,
            "converted": 0,
            "pending": 0,
            "purchase_step": None,
            "routed": set(),
            "delivered": 0,
        }
    else:
        state = {
            "step": state["step"],
            "converted": state["converted"],
            "pending": state["pending"],
            "purchase_step": state["purchase_step"],
            "routed": set(state["routed"]),
            "delivered": state["delivered"],
        }
    return state


def _v80_move(src, dst):
    x, y = int(src[0]), int(src[1])
    tx, ty = dst
    dx, dy = tx - x, ty - y
    if abs(dx) >= abs(dy) and dx:
        return ["EAST" if dx > 0 else "WEST"]
    if dy:
        return ["SOUTH" if dy > 0 else "NORTH"]
    if dx:
        return ["EAST" if dx > 0 else "WEST"]
    return ["PASS"]


def _v80_apply(obs, action):
    action = _v80_copy.deepcopy(action)
    seat = int(obs.get("player", 0) or 0)
    day = int(obs.get("day", 0) or 0)
    hour = int(obs.get("hour", 0) or 0)
    step = day * 24 + hour
    farms = obs.get("farms") or []
    if seat >= len(farms):
        return action

    state = _v80_get_state(seat, step)
    farm = farms[seat]
    private = obs.get("private") or {}
    sheep_total, vacant_pastures, coop_vacancy = _v80_counts(farm, private)
    orders = action.get("market") or []

    # ---- 1. market conversion (coupled step, fires at most once) ------------
    if (
        _v80_gate(obs)
        and state["purchase_step"] is None
        and state["converted"] < CONVERT_CAP
        and sheep_total == SHEEP_TRIGGER
    ):
        for index, order in enumerate(orders):
            if (
                len(order) > 2
                and order[0] == "BUY_ANIMAL"
                and order[1] == "GOOSE"
                and int(order[2]) > 0
            ):
                room = CONVERT_CAP - state["converted"]
                shift = min(int(order[2]), room)
                if shift <= 0:
                    break
                replacement = list(orders[:index])
                if int(order[2]) > shift:
                    replacement.append(["BUY_ANIMAL", "GOOSE", int(order[2]) - shift])
                replacement.append(["BUY_ANIMAL", "SHEEP", shift])
                replacement.extend(orders[index + 1 :])
                if len(replacement) <= 10:
                    action["market"] = replacement
                    orders = replacement
                    state["converted"] += shift
                    state["pending"] += shift
                    state["purchase_step"] = step
                break

    # ---- 2. infrastructure priority while converted units are undelivered ----
    # While sheep bought by this overlay are still in transit, a BUILD_COOP on
    # a turn that the frozen route would have used to raise pasture capacity is
    # redirected to BUILD_PASTURE. Feed/care/crop actions are never touched.
    if state["pending"] > 0 and not vacant_pastures:
        units = [action.get("farmer", ["PASS"]), *(action.get("hands") or [])]
        for i, unit in enumerate(units):
            if unit and unit[0] == "BUILD_COOP":
                units[i] = ["BUILD_PASTURE"]
                break
        action["farmer"] = units[0]
        action["hands"] = units[1:]
        _, vacant_pastures, _ = _v80_counts(farm, private)

    # ---- 3. shed pickup + pasture delivery of the converted units ----------
    # Gated strictly on this overlay having converted something. Before the
    # conversion fires, the frozen route's own sheep delivery must run untouched.
    if state["converted"] == 0:
        state["step"] = step
        _v80_state[seat] = state
        return action

    positions = [farm.get("farmer", [0, 0]), *(farm.get("hands") or [])]
    inventories = list(private.get("inventories") or [])
    inventories += [{} for _ in range(max(0, len(positions) - len(inventories)))]
    units = [action.get("farmer", ["PASS"]), *(action.get("hands") or [])]
    shed = private.get("shed") or {}
    shed_sheep = int(shed.get("SHEEP", 0) or 0)

    # Pickup first: the frozen route emits PICKUP for the animals it just bought.
    # While converted sheep are in the shed, that same turn takes sheep instead.
    if state["pending"] > 0 and shed_sheep > 0:
        for i, unit in enumerate(units):
            if (
                unit
                and unit[0] == "PICKUP"
                and len(unit) > 1
                and unit[1] in ("GOOSE", "COW")
                and int((inventories[i] or {}).get("SHEEP", 0) or 0) == 0
            ):
                units[i] = ["PICKUP", "SHEEP", 1]
                state["routed"].add(i)
                state["pending"] = max(0, state["pending"] - 1)
                break

    # Then deliver: a unit that is carrying a converted sheep walks to the
    # nearest vacant pasture and places it. Units that are not carrying one keep
    # whatever the frozen route asked them to do this turn.
    for i, (pos, inv) in enumerate(zip(positions, inventories)):
        carried = int((inv or {}).get("SHEEP", 0) or 0)
        if i not in state["routed"] or carried <= 0:
            continue
        if not vacant_pastures:
            # No pasture yet: hold position rather than wander, so the animal
            # stays reachable for the next turn's build.
            units[i] = ["PASS"]
            continue
        target = min(
            vacant_pastures,
            key=lambda p: (abs(int(pos[0]) - p[0]) + abs(int(pos[1]) - p[1]), p[1], p[0]),
        )
        if tuple(int(v) for v in pos) == target:
            units[i] = ["PLACE", "SHEEP"]
            vacant_pastures.remove(target)
            state["delivered"] += 1
            state["routed"].discard(i)
            if state["delivered"] >= state["converted"]:
                state["pending"] = 0
        else:
            units[i] = _v80_move(pos, target)

    action["farmer"] = units[0]
    action["hands"] = units[1:]
    state["step"] = step
    _v80_state[seat] = state
    return action


def _v80_entrypoint(obs, configuration=None):
    return _v80_apply(obs, _v80_frozen_agent(obs, configuration))


def _kaggle_submission_entrypoint(obs, configuration=None):
    return _v80_entrypoint(obs, configuration)

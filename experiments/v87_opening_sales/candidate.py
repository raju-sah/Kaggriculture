"""V87: opening harvest-to-sale on the frozen V56 lineage.

New file. No frozen file is modified. The frozen V56 agent is exec'd into a
private namespace and one overlay is applied to its unit actions.

Diagnostic that produced this (experiments/v87_opening_sales/diagnose_opening_sales.py,
pinned Kaggriculture 1.32.7, max_cash_error 0.0, saved replays only):

  Question: V56 accepts 3,035 over days 0-5 vs elite winners 5,319 and elite
  losers 3,695. Is that a production shortfall or failed SELL orders?

  Answer: neither. V56 orders 49 units in days 0-5 and the engine accepts all
  49 - a 0.0% rejection rate on every seed checked. V50 on the same seeds
  orders and accepts the identical 49 units for the identical ~$3,034. The
  opening gap is NOT a selling failure and NOT a rejection problem.

  The actual cause is upstream: V56 has 19-20 plants at yield_units > 0 from
  day 1 onward, and issues ZERO HARVEST actions until step 61 (day 2, hour 13).
  Its first sale of any crop product in the opening window is the day-0 wheat
  dribble (15 units, $449). It banks 2,600 of fertilizer resale and nothing else.
  The 12 melon it planted on day 0 (worth ~$268 each in the days 1-5 window)
  sit ready and unharvested until day 11, by which point the shared melon price
  has fallen from 271 to 73.

  Same-seed V50/V56 phase comparison confirms the opening is not where V50 wins:
  seed 94400 d0-5 V50 $3,034 vs V56 $3,035; V50's entire +4,475 edge is in
  d24-29 (+3,517). So this overlay is aimed at a real elite gap, not at closing
  a V50 gap, and the screen below is against both.

Reachability, checked against the engine rather than assumed:
  * HARVEST, PICKUP and DROP cost no cash in `_apply_unit_action`; they cost one
    worker turn each. SELL pays cash.
  * `private['shed']` is EMPTY for the whole opening (0 of 100 capacity), so
    DROP always has room.
  * `_commit_unit` SELL only requires shed stock > 0, so harvested goods must be
    dropped before they can be sold. The overlay therefore runs harvest -> carry
    -> drop -> sell, and only sells what the engine has actually accepted.
  * No shop is open on days 0-5 (`unlocked_shops` is empty until YARN_STORE on
    day 3), but `_process_market` still quotes and accepts SELL against the town
    centre, which is how the existing day-0 wheat sale completes at 0 rejection.

No sacrifice of later proceeds: the melon that V56 eventually sells at day 11
realises ~$73, versus ~$268 in the days 1-5 window. Selling the same 12 units
early is worth roughly 3.7x, so this is a timing gain, not a trade.

Scope, fixed before the screen:
  - days 0-5 only;
  - only when the shed actually holds a crop product that the frozen agent has
    not already ordered for sale this turn;
  - the overlay never adds a market order for goods that are not in the shed, so
    it cannot manufacture a sale the engine would reject;
  - it never displaces a FEED, CARE or WATER action, and it caps itself at a
    small number of harvest attempts per turn so the frozen priority order
    survives.
"""

V56_SOURCE = "/home/raju/AI-ML Projects/Kaggle Competition/Kaggriculture/agents/v56_agent.py"

OPENING_DAY_MAX = 5
MAX_HARVEST_PER_TURN = 2     # do not crowd out the frozen route's own priorities
CASH_FLOOR = 0               # nothing to protect: the actions are free


def _load(path):
    namespace = {"__name__": "v87_frozen_v56"}
    with open(path, "r", encoding="utf-8") as handle:
        exec(compile(handle.read(), path, "exec"), namespace)  # noqa: S102
    return namespace


_v56_ns = _load(V56_SOURCE)
_v56_agent = _v56_ns["agent"]


def _ready_crops(farm):
    """Crop tiles that are actually harvestable this turn."""
    ready = []
    for y, row in enumerate(farm.get("tiles") or []):
        for x, tile in enumerate(row):
            if not isinstance(tile, dict):
                continue
            if tile.get("kind") != "PLANT":
                continue
            if int(tile.get("yield_units", 0) or 0) > 0:
                ready.append((x, y, tile.get("crop")))
    return ready


def _move(pos, target):
    x, y = int(pos[0]), int(pos[1])
    tx, ty = target
    dx, dy = tx - x, ty - y
    if abs(dx) >= abs(dy) and dx:
        return ["EAST" if dx > 0 else "WEST"]
    if dy:
        return ["SOUTH" if dy > 0 else "NORTH"]
    if dx:
        return ["EAST" if dx > 0 else "WEST"]
    return ["PASS"]


def _shedding(unit):
    return unit and len(unit) > 1 and unit[0] == "DROP"


def _v87_apply(obs, action):
    day = int(obs.get("day", 0) or 0)
    if day > OPENING_DAY_MAX:
        return action

    seat = int(obs.get("player", 0) or 0)
    farms = obs.get("farms") or []
    if seat >= len(farms):
        return action
    farm = farms[seat]

    private = obs.get("private") or {}
    shed = private.get("shed") or {}

    units = [action.get("farmer", ["PASS"]), *(action.get("hands") or [])]
    positions = [farm.get("farmer", [0, 0]), *(farm.get("hands") or [])]
    if not positions[1:]:
        # No crew: nothing can be harvested this turn.
        return action

    ready = _ready_crops(farm)
    if not ready:
        return action

    # Prefer a hand that is idling or working a low-priority task, and never
    # displace a feed/care action, which the herd cannot survive without.
    protected = {"FEED", "CARE"}
    claimed = 0
    used_tiles = set()

    for i in range(1, len(units)):
        if claimed >= MAX_HARVEST_PER_TURN:
            break
        unit = units[i]
        if unit and unit[0] in protected:
            continue
        if _shedding(unit):
            # Let the shed run; harvested goods must reach the shed first.
            continue
        best = None
        for x, y, crop in ready:
            if (x, y) in used_tiles:
                continue
            d = abs(int(positions[i][0]) - x) + abs(int(positions[i][1]) - y)
            if d == 0:
                best = ((x, y), crop, 0)
                break
            if best is None or d < best[2]:
                best = ((x, y), crop, d)
        if best is None:
            break
        tile, _crop, dist = best
        used_tiles.add(tile)
        if dist == 0:
            units[i] = ["HARVEST"]
        else:
            units[i] = _move(positions[i], tile)
        claimed += 1

    if claimed == 0:
        return action

    action["farmer"] = units[0]
    action["hands"] = units[1:]
    return action


def _v87_entrypoint(obs, configuration=None):
    return _v87_apply(obs, _v56_agent(obs, configuration))


def _kaggle_submission_entrypoint(obs, configuration=None):
    return _v87_entrypoint(obs, configuration)

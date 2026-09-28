"""Build the V107 candidate: V50 + ONLY the one-cow no-Yarn day-6 swap.

DERIVATION (deliberate, and deliberately minimal)
------------------------------------------------
Base: experiments/v50_agent.py   sha256
      e6b50128e023e3b9fafa1841e4cd520c5e581acb48e8628657585c18272eab2b
      (the official prior-best public agent, 1233.2)

V107 = V50 verbatim + exactly one intervention: the V101-style one-cow
no-Yarn day-6 swap.

  buy    : `BUY_ANIMAL SHEEP 2` -> `SHEEP 1` + `COW 1`   (at d6 h6)
  pickup : the tape's first sheep PICKUP on day 6 -> PICKUP COW
  place  : that carrier's sheep PLACE on day 6 -> PLACE COW

The swap is gated on the same frozen no-Yarn predicate used everywhere else in
this line of work -- a visible MILK sink (PIZZA_SHOP / ICE_CREAM_SHOP /
SMOOTHIE_SHOP) and no YARN_STORE -- and it is confined to day 6, so it changes
no later-day behaviour.

WHAT IS DELIBERATELY EXCLUDED
----------------------------
* NO V92 day-23 shed overflow guard. V92 is an overflow patch layered on top of
  V50; V107 starts from the untouched V50, as required.
* NO second cow (that was V105, a NO-GO).
* NO valuation model. This is the pure shop-gate swap, so the only strategic
  difference from V50 is "one sheep becomes one cow on day 6, under the no-Yarn
  gate".

CALLABLE ORDER (the loader gotcha)
----------------------------------
`kaggle_environments.agent.get_last_callable` execs the file and binds the LAST
module-level callable. Every helper is therefore defined ABOVE the final
assignment, and the final line re-points `_kaggle_submission_entrypoint` at the
V107 wrapper. `_v50_agent` is captured once at build time, so V50's own
`_kaggle_submission_entrypoint` name is left intact but no longer the last
callable -- no shadowing of the swap logic.

`experiments/v50_agent.py` is read only; it is never modified.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
V50 = ROOT / "experiments/v50_agent.py"
V50_SHA = "e6b50128e023e3b9fafa1841e4cd520c5e581acb48e8628657585c18272eab2b"
OUT = HERE / "candidate.py"

SWAP = '''

# =============================================================================
# V107: frozen V50 + ONE no-Yarn day-6 sheep->cow swap. Nothing above this line
# is modified; in particular the V92 overflow guard is NOT included.
#
# The swap rides the tape's own day-6 errand, so it adds no worker time: the cow
# is bought at the incumbent's own animal-buy turn, collected on the sheep
# pickup the tape already performs, and placed on the pasture that sheep's own
# PLACE targets.
#
# Loader note: get_last_callable binds the LAST module-level callable, so the
# entrypoint is re-assigned last, below every helper.
# =============================================================================

import copy as _v107_copy

_V107_MILK_SINKS = frozenset(("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"))
_V107_WOOL_SINKS = frozenset(("YARN_STORE",))


def _v107_no_wool_route(obs):
    """Frozen gate: at least one visible MILK sink, and no YARN_STORE.

    YARN_STORE is the only single-product WOOL sink, and a single-product shop
    draws TWICE per consumption step, so its presence doubles the wool draw-off
    and is the condition under which the swap is known to be harmful.
    """
    shops = (obs.get("town") or {}).get("unlocked_shops", [])
    return (any(s in _V107_MILK_SINKS for s in shops)
            and not any(s in _V107_WOOL_SINKS for s in shops))


def _v107_apply(obs, action):
    """One-cow no-Yarn day-6 swap. A strict no-op everywhere else."""
    if not isinstance(obs, dict) or not isinstance(action, dict):
        return action
    if obs.get("day") != 6 or not _v107_no_wool_route(obs):
        return action
    private = obs.get("private") or {}
    shed = private.get("shed") or {}
    invs = private.get("inventories") or []
    out = None
    hour = obs.get("hour")

    # --- BUY at the tape's own animal-buy turn: split SHEEP 2 -> SHEEP 1 + COW 1
    if hour == 6:
        orders = list(action.get("market") or [])
        for i, order in enumerate(orders):
            if (isinstance(order, list) and len(order) >= 3
                    and order[0] == "BUY_ANIMAL" and order[1] == "SHEEP"
                    and int(order[2]) >= 2):
                out = _v107_copy.deepcopy(action)
                out["market"][i][2] = int(order[2]) - 1
                out["market"].insert(i + 1, ["BUY_ANIMAL", "COW", 1])
                return out
        return action

    # --- PICKUP, only once a COW is actually waiting in the shed
    if int(shed.get("COW", 0) or 0) > 0:
        actors = [action.get("farmer")] + list(action.get("hands") or [])
        for ai, a in enumerate(actors):
            if isinstance(a, list) and len(a) > 1 and a[0] == "PICKUP" and a[1] == "SHEEP":
                out = out or _v107_copy.deepcopy(action)
                new = list(a)
                new[1] = "COW"
                if ai == 0:
                    out["farmer"] = new
                else:
                    out["hands"][ai - 1] = new
                break

    # --- PLACE, only for a carrier already holding a cow. Guarded separately
    # from the pickup: on the turn after the collection the shed is empty but
    # the cow is in the carrier's hands.
    base = out if out is not None else action
    actors = [base.get("farmer")] + list(base.get("hands") or [])
    for ai, a in enumerate(actors):
        if (ai < len(invs)
                and int((invs[ai] or {}).get("COW", 0) or 0) > 0
                and isinstance(a, list) and len(a) > 1
                and a[0] == "PLACE" and a[1] == "SHEEP"):
            out = out or _v107_copy.deepcopy(action)
            new = list(a)
            new[1] = "COW"
            if ai == 0:
                out["farmer"] = new
            else:
                out["hands"][ai - 1] = new
            break

    return out if out is not None else action


def _v107_entrypoint(obs, configuration=None):
    return _v107_apply(obs, _v50_agent(obs, configuration))


# Last callable in the file: this is what Kaggle's loader binds.
_kaggle_submission_entrypoint = _v107_entrypoint
'''


def main() -> None:
    base = V50.read_text(encoding="utf-8")
    got = hashlib.sha256(base.encode()).hexdigest()
    if got != V50_SHA:
        raise SystemExit(f"V50 drifted: {got} != {V50_SHA}")

    # Capture V50's own entrypoint under a private name BEFORE the swap block is
    # appended, so the swap helpers can call it without any name collision, and
    # so V50's original _kaggle_submission_entrypoint is not the last callable.
    capture = '''
# V50's own entrypoint, captured under a private name for the V107 wrapper.
# Must appear after V50's definition and before the swap block.
_v50_agent = _kaggle_submission_entrypoint
'''
    body = base + capture + SWAP
    OUT.write_text(body, encoding="utf-8")

    # V50's file must be byte-identical to how we found it.
    after = hashlib.sha256(V50.read_bytes()).hexdigest()
    if after != V50_SHA:
        raise SystemExit("V50 file was modified during build")
    print(f"wrote {OUT}")
    print(f"candidate sha256 {hashlib.sha256(OUT.read_bytes()).hexdigest()}")
    print(f"v50 base sha256  {got} (embedded verbatim, file untouched: {after == V50_SHA})")


if __name__ == "__main__":
    main()

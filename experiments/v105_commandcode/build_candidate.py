"""Build the V105 candidate: the frozen no-Yarn one-cow candidate, plus a SECOND
sheep->cow swap on the other existing day-6 route.

DERIVATION (deliberate, for a clean paired comparison)
-----------------------------------------------------
Base: experiments/v101_adaptive_swap/candidate_milk_sink_no_yarn.py
      sha256 d166d2420440a0a96643c061b010c444f372a89e236e9c22a8417b4008b81763
That file is the ONE-cow candidate with the frozen no-Yarn shop gate: on day 6 it
turns `BUY_ANIMAL SHEEP 2` into `SHEEP 1` + `COW 1`, then relabels the FIRST sheep
pickup on day 6 to a cow pickup and the first carrier's sheep PLACE to a cow PLACE.

V105 keeps all of that byte-for-byte and changes exactly one thing: it also
performs the SAME swap a second time, on the SECOND sheep pickup/place pair that
the same day-6 route supplies. The measured day-6 route on spent seeds is:

    PICKUP SHEEP h08 by actor 5  ->  PLACE SHEEP h11 by actor 5, tile (5, 4)
    PICKUP SHEEP h08 by actor 0  ->  PLACE SHEEP h12 by actor 0, tile (5, 3)

Two different actors, two different pastures, same day, no extra movement. So the
second cow rides the second existing errand and costs zero extra worker time.

WHY THE BASE FILE IS USED VERBATIM
-----------------------------------
The point of this experiment is a PAIRED comparison: V105 vs the one-cow no-Yarn
candidate on identical seeds and seats. Any other change (a different valuation
model, a different gate, a different threshold) would confound "one cow" with
"two cows". V105 therefore imports the base file's own gate and its own
arithmetic untouched, and re-executes the base's swap twice instead of once.

Gate, buy, pickup, place semantics are all the base's. The only delta is a second
pass over the day-6 route.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASE = ROOT / "experiments/v101_adaptive_swap/candidate_milk_sink_no_yarn.py"
BASE_SHA = "d166d2420440a0a96643c061b010c444f372a89e236e9c22a8417b4008b81763"
OUT = HERE / "candidate.py"

OVERRIDE = '''

# =============================================================================
# V105 = the no-Yarn one-cow candidate, PLUS a second sheep->cow swap on the
# other existing day-6 route. Nothing above this line is modified: the gate, the
# buy rewrite, and the first pickup/place all come from the base candidate.
#
# The day-6 route supplies two independent sheep pickup/place pairs (measured on
# spent seeds: actor 5 h8/h11 onto (5,4) and the farmer h8/h12 onto (5,3)), so the
# second cow rides the second errand with no added movement and no worker-time.
# =============================================================================

import copy as _v105_copy


def _v105_apply_second(obs, action):
    """Run one more sheep->cow swap on a route the first one did not take.

    The three rewrites are INDEPENDENT branches over the same observation. An
    earlier version chained them and returned early when a PICKUP was not
    present, which meant the h12 PLACE was never converted on any turn that had
    already spent its pickup -- exactly the turn the second cow needs.

    Each branch is separately guarded:
      buy    - hour 6, a remaining sheep order, and no COW order already emitted
      pickup - a cow in the shed and a sheep pickup still on the tape
      place  - a carrier already holding a cow and a sheep place still on the tape
    """
    if not isinstance(obs, dict) or not isinstance(action, dict):
        return action
    if obs.get("day") != 6:
        return action
    if not _v101_milk_sink_without_wool_route(obs):
        return action

    private = obs.get("private") or {}
    shed = private.get("shed") or {}
    invs = private.get("inventories") or []
    out = None

    def actors_of(a):
        return [a.get("farmer")] + list(a.get("hands") or [])

    # --- branch 1: BUY at h6 -------------------------------------------------
    # The base already turned SHEEP 2 into SHEEP 1 + COW 1. We want COW 2 total.
    # Emitting a second COW order is legal (the engine settles per order), but a
    # single merged COW 2 order is cleaner and provably within
    # maxMarketOrdersPerTurn, so fold the base's COW 1 into COW 2.
    if obs.get("hour") == 6:
        orders = list(action.get("market") or [])
        cow_idx = None
        cow_qty = 0
        sheep_idx = None
        for i, order in enumerate(orders):
            if (isinstance(order, list) and len(order) >= 3
                    and order[0] == "BUY_ANIMAL"):
                if order[1] == "COW":
                    cow_idx = i
                    cow_qty += int(order[2])
                elif order[1] == "SHEEP" and int(order[2]) >= 1 and sheep_idx is None:
                    sheep_idx = i
        if sheep_idx is None:
            return action
        out = _v105_copy.deepcopy(action)
        if cow_idx is not None:
            # base's COW order already exists: take one more cow, and drop the
            # sheep order entirely (it is the one we are converting).
            out["market"][cow_idx] = ["BUY_ANIMAL", "COW", cow_qty + 1]
            out["market"].pop(sheep_idx)
        else:
            out["market"][sheep_idx] = ["BUY_ANIMAL", "COW", 1]
        return out

    # --- branch 2: PICKUP, guarded by a cow waiting in the shed -------------
    if int(shed.get("COW", 0) or 0) > 0:
        for ai, a in enumerate(actors_of(action)):
            if isinstance(a, list) and len(a) > 1 and a[0] == "PICKUP" and a[1] == "SHEEP":
                out = out or _v105_copy.deepcopy(action)
                new = list(a)
                new[1] = "COW"
                if ai == 0:
                    out["farmer"] = new
                else:
                    out["hands"][ai - 1] = new
                break

    # --- branch 3: PLACE, guarded by the carrier already holding a cow -------
    # Independent of branch 2: on the h12 turn the pickup is long gone, and this
    # is the only thing that can place the second cow.
    base = out if out is not None else action
    for ai, a in enumerate(actors_of(base)):
        if (ai < len(invs)
                and int((invs[ai] or {}).get("COW", 0) or 0) > 0
                and isinstance(a, list) and len(a) > 1
                and a[0] == "PLACE" and a[1] == "SHEEP"):
            out = out or _v105_copy.deepcopy(action)
            new = list(a)
            new[1] = "COW"
            if ai == 0:
                out["farmer"] = new
            else:
                out["hands"][ai - 1] = new
            break

    return out if out is not None else action


def _v105_entrypoint(obs, configuration=None):
    # _luna_swap_entrypoint is the base candidate's full policy (gate + first cow).
    return _v105_apply_second(obs, _luna_swap_entrypoint(obs, configuration))


_kaggle_submission_entrypoint = _v105_entrypoint
'''


def main() -> None:
    base = BASE.read_text(encoding="utf-8")
    got = hashlib.sha256(base.encode()).hexdigest()
    if got != BASE_SHA:
        raise SystemExit(f"base candidate drifted: {got} != {BASE_SHA}")
    OUT.write_text(base + OVERRIDE, encoding="utf-8")
    print(f"wrote {OUT}")
    print(f"sha256 {hashlib.sha256(OUT.read_bytes()).hexdigest()}")
    print(f"base sha256 {got} (embedded verbatim)")
    print(f"base text preserved byte-for-byte: {base in OUT.read_text(encoding='utf-8')}")


if __name__ == "__main__":
    main()

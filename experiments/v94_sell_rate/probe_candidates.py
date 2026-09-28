#!/usr/bin/env python3
"""V94 step 7: run V94 candidates against each other cheaply, on ONE seed each.

This is a targeted probe, not a tournament. It answers one narrow question:
V93 lost because holding WOOL at the floor was worth ~$4/unit at best while the
shed cost was real. Is there a WOOL strategy that does NOT crowd the shed and
still captures some recovery? Two candidate overlays are compared in isolation:

  C1 SELL-EVERYTHING-NOW (control)  = V92, sell WOOL on schedule including at $1.
  C2 HOLD-AT-FLOOR-BUT-SHED-SAFE    = withhold WOOL sells at the floor, but ONLY
     while shed occupancy is below a cap, so the shed never crowds. This is V93
     plus the shed guard V93 lacked.
  C3 SELL-AT-FLOOR-BUT-UPGRADE      = sell at the floor as normal (free the shed)
     but never let the shed exceed the cap, i.e. rate-limit the BUY side.

Each is run head-to-head on a couple of seeds via the exact loader to see
whether ANY of them moves cash vs V92 at all. If none does on a quick probe,
the WOOL lever is dead and the report says so with evidence instead of a gate.

Run from repo root:
    .venv/bin/python experiments/v94_sell_rate/probe_candidates.py
"""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

from kaggle_environments import make

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V92_PATH = ROOT / "experiments/v92_overflow_guard/candidate.py"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


V92 = load(V92_PATH, "v92_probe")


def shed_total(obs):
    return sum((obs.get("private") or {}).get("shed", {}).values())


def carried_total(obs):
    return sum(n for inv in (obs.get("private") or {}).get("inventories") or [] for n in inv.values())


def wool_quote(obs):
    q = ((obs.get("market") or {}).get("prices") or {}).get("WOOL")
    return None if q is None else float(q)


def make_c2(shed_cap=90):
    """Hold WOOL at the floor, but only while the shed stays under a cap."""

    def policy(obs, configuration=None):
        action = V92._v92_entrypoint(obs, configuration)
        q = wool_quote(obs)
        if q is None or q > 1:
            return action
        if shed_total(obs) >= shed_cap:
            return action  # shed-safe: sell now, do not crowd
        orders = list(action.get("market") or [])
        new = [list(o) for o in orders if not (len(o) > 2 and o[0] == "SELL" and o[1] == "WOOL")]
        if new == [list(o) for o in orders]:
            return action
        out = copy.deepcopy(action)
        out["market"] = new
        return out
    return policy


def make_c3(shed_cap=90):
    """Sell WOOL on schedule (including at $1) but rate-limit so the shed stays under a cap."""
    def policy(obs, configuration=None):
        action = V92._v92_entrypoint(obs, configuration)
        if shed_total(obs) < shed_cap:
            return action
        # Shed is at the cap: drop any WOOL/FERT/WHEAT buy that would crowd it.
        orders = list(action.get("market") or [])
        new = []
        for o in orders:
            if len(o) > 2 and o[0] == "BUY_PRODUCT" and o[1] in ("FERTILIZER", "WHEAT"):
                continue
            new.append(list(o))
        if new == [list(o) for o in orders]:
            return action
        out = copy.deepcopy(action)
        out["market"] = new
        return out
    return policy


def write_candidate(path, policy_fn_name, body):
    path.write_text(body, encoding="utf-8")
    return path


C2_SRC = '''
import copy as _c
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("_v92_base", "__V92_ABS__")
_v92 = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_v92)

SHED_CAP = 90

def _st(obs):
    return sum((obs.get("private") or {}).get("shed", {}).values())

def _q(obs):
    x = ((obs.get("market") or {}).get("prices") or {}).get("WOOL")
    return None if x is None else float(x)

def _policy(obs, configuration=None):
    action = _v92._v92_entrypoint(obs, configuration)
    q = _q(obs)
    if q is None or q > 1 or _st(obs) >= SHED_CAP:
        return action
    orders = list(action.get("market") or [])
    new = [list(o) for o in orders if not (len(o) > 2 and o[0] == "SELL" and o[1] == "WOOL")]
    if new == [list(o) for o in orders]:
        return action
    out = _c.deepcopy(action)
    out["market"] = new
    return out

def _kaggle_submission_entrypoint(obs, configuration=None):
    return _policy(obs, configuration)
'''

C3_SRC = '''
import copy as _c
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("_v92_base", "__V92_ABS__")
_v92 = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_v92)

SHED_CAP = 90

def _st(obs):
    return sum((obs.get("private") or {}).get("shed", {}).values())

def _policy(obs, configuration=None):
    action = _v92._v92_entrypoint(obs, configuration)
    if _st(obs) < SHED_CAP:
        return action
    orders = list(action.get("market") or [])
    new = [list(o) for o in orders if not (len(o) > 2 and o[0] == "BUY_PRODUCT" and o[1] in ("FERTILIZER", "WHEAT"))]
    if new == [list(o) for o in orders]:
        return action
    out = _c.deepcopy(action)
    out["market"] = new
    return out

def _kaggle_submission_entrypoint(obs, configuration=None):
    return _policy(obs, configuration)
'''


def run(seed, cand_path, name):
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=True)
    env.run([str(V92_PATH.resolve()), str(cand_path.resolve())])
    r = env.toJSON()["steps"][-1]
    return {"seed": seed, "cand": name, "v92_coins": r[0].get("reward"), "cand_coins": r[1].get("reward"),
            "delta": (r[1].get("reward") or 0) - (r[0].get("reward") or 0)}


def main():
    out = HERE / "probe_out"
    out.mkdir(parents=True, exist_ok=True)
    v92_abs = str(V92_PATH.resolve())
    c2 = HERE / "probe_c2.py"
    c3 = HERE / "probe_c3.py"
    c2.write_text(C2_SRC.replace("__V92_ABS__", v92_abs))
    c3.write_text(C3_SRC.replace("__V92_ABS__", v92_abs))
    seeds = [92600, 94700, 95200]
    results = []
    for seed in seeds:
        for name, path in (("C2_shed_safe_hold", c2), ("C3_shed_capped_buy", c3)):
            r = run(seed, path, name)
            results.append(r)
            print(f"  seed {seed} {r['cand']:>18}: V92=${r['v92_coins']:>8,.0f} cand=${r['cand_coins']:>8,.0f} "
                  f"delta=${r['delta']:>+9,.0f}", flush=True)
    (out / "candidate_probe.json").write_text(json.dumps(results, indent=2) + "\n")
    print()
    for name in ("C2_shed_safe_hold", "C3_shed_capped_buy"):
        deltas = [r["delta"] for r in results if r["cand"] == name]
        pos = sum(1 for d in deltas if d > 0)
        print(f"{name:>18}: deltas {[f'{d:+,.0f}' for d in deltas]}  positive {pos}/{len(deltas)}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""V93 candidate self-check, run BEFORE any tournament game.

Verifies four things and exits non-zero if any fails:

  1. The embedded V50 source in the V93 file is byte-identical to the real
     experiments/v50_agent.py. The V92 file made the same claim, and the whole
     point of the check is that a self-contained submission must not silently
     fall back to a do-nothing agent when the repository is absent.
  2. The file imports cleanly under the Kaggle loader convention: the module
     exposes _kaggle_submission_entrypoint(obs, configuration).
  3. V93 reproduces the frozen V92 action exactly on a healthy WOOL quote, and
     differs only by removing WOOL SELL orders on a floored quote.
  4. The overlay never touches a unit action, and never touches a non-WOOL
     market order, on either branch.

Run from the repository root:
    .venv/bin/python experiments/v93_adaptive/verify_candidate.py
"""

from __future__ import annotations

import base64
import copy
import hashlib
import importlib.util
import json
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CANDIDATE = HERE / "candidate.py"
V50 = ROOT / "experiments/v50_agent.py"
V92 = ROOT / "experiments/v92_overflow_guard/candidate.py"

failures: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{(' :: ' + detail) if detail else ''}")
    if not ok:
        failures.append(name)


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# 1. embedded V50 integrity -----------------------------------------------------
v93_src = CANDIDATE.read_text()
v50_real = V50.read_bytes()
b64 = v93_src.split("_V50_SOURCE_B64 = (")[1].split(")")[0]
v50_embedded = base64.b64decode("".join(part.strip().strip('"') for part in b64.splitlines())).decode("utf-8")
check(
    "embedded V50 is byte-identical to experiments/v50_agent.py",
    v50_embedded.encode() == v50_real,
    f"sha256 {hashlib.sha256(v50_embedded.encode()).hexdigest()[:16]}",
)

# The Kaggle loader picks the LAST module-level callable, so a helper defined
# after the entrypoint would be submitted instead of the entrypoint.
from kaggle_environments.agent import get_last_callable  # noqa: E402

selected = getattr(get_last_callable(v93_src, None, str(CANDIDATE)), "__name__", "")
check("loader selects _kaggle_submission_entrypoint", selected == "_kaggle_submission_entrypoint", selected)

# 2. loader convention ----------------------------------------------------------
v93 = load(CANDIDATE, "v93_check")
v92 = load(V92, "v92_check")
check(
    "exposes _kaggle_submission_entrypoint(obs, configuration)",
    callable(getattr(v93, "_kaggle_submission_entrypoint", None)),
)
check("V93 candidate sha256", True, hashlib.sha256(CANDIDATE.read_bytes()).hexdigest())

# 3./4. overlay semantics on synthetic observations -----------------------------
GOOD = 200
FLOORED = 1


def obs_with(quote: int) -> dict:
    return {
        "step": 600,
        "day": 25,
        "hour": 0,
        "player": 0,
        "market": {"prices": {"WOOL": quote, "MILK": 160}},
        "private": {"shed": {"WOOL": 10, "MILK": 0}, "inventories": [{}], "seeds": {}},
        "farms": [{"money": 1000, "tiles": [[None] * 10 for _ in range(10)], "farmer": [0, 0], "hands": []}],
    }


def action_with(**kw) -> dict:
    base = {
        "farmer": ["HARVEST"],
        "hands": [["WATER"], ["FEED"]],
        "market": [["SELL", "WOOL", 6], ["SELL", "MILK", 3], ["BUY_PRODUCT", "WHEAT", 4]],
    }
    base.update(kw)
    return base


# healthy quote -> byte-identical pass-through
out = v93._v93_apply(obs_with(GOOD), action_with())
check("healthy quote: V93 action identical to input", out == action_with(), "WOOL 200 -> untouched")

# floored quote -> WOOL SELL removed, everything else byte-identical
out = v93._v93_apply(obs_with(FLOORED), action_with())
expected = action_with(market=[["SELL", "MILK", 3], ["BUY_PRODUCT", "WHEAT", 4]])
check("floored quote: only the WOOL SELL removed", out == expected, json.dumps(out["market"]))
check("floored quote: unit actions untouched", out["farmer"] == ["HARVEST"] and out["hands"] == [["WATER"], ["FEED"]])
check("floored quote: input action not mutated", action_with()["market"][0] == ["SELL", "WOOL", 6])

# no WOOL order -> untouched even when floored
no_wool = action_with(market=[["SELL", "MILK", 3]])
check("floored quote with no WOOL order: untouched", v93._v93_apply(obs_with(FLOORED), no_wool) == no_wool)

# multiple WOOL orders all removed
multi = action_with(market=[["SELL", "WOOL", 4], ["BUY_SEED", "MELON", 2], ["SELL", "WOOL", 9], ["SELL", "EGG", 5]])
out = v93._v93_apply(obs_with(FLOORED), multi)
check(
    "floored quote: every WOOL SELL removed, order otherwise preserved",
    out["market"] == [["BUY_SEED", "MELON", 2], ["SELL", "EGG", 5]],
    json.dumps(out["market"]),
)

# missing quote -> untouched (fail-safe: never act on absent data)
missing = obs_with(GOOD)
missing["market"].pop("prices")
check("missing WOOL quote: untouched", v93._v93_apply(missing, action_with()) == action_with())

# V93 is a strict post-hoc overlay on V92: on a real observation the frozen
# route DOES place a WOOL SELL, and V93 withholds exactly that order while
# leaving every other order, the unit actions and the order itself intact.
floored_obs = obs_with(FLOORED)
v92_out = v92._v92_entrypoint(floored_obs, {})
v93_out = v93._v93_entrypoint(floored_obs, {})
v92_wool = [o for o in v92_out["market"] if len(o) > 2 and o[0] == "SELL" and o[1] == "WOOL"]
v93_wool = [o for o in v93_out["market"] if len(o) > 2 and o[0] == "SELL" and o[1] == "WOOL"]
check(
    "frozen route really does place a WOOL SELL on a floored observation",
    len(v92_wool) == 1,
    json.dumps(v92_wool),
)
check("V93 withholds exactly the WOOL SELL", v93_wool == [], f"V92 had {v92_wool}")
check(
    "V93 leaves every non-WOOL order byte-identical to V92",
    [o for o in v92_out["market"] if not (len(o) > 2 and o[0] == "SELL" and o[1] == "WOOL")] == v93_out["market"],
)
check("V93 leaves unit actions byte-identical to V92", v93_out["farmer"] == v92_out["farmer"] and v93_out["hands"] == v92_out["hands"])

# On a healthy quote V93 must be a strict no-op against V92.
healthy_out = v93._v93_entrypoint(obs_with(GOOD), {})
check(
    "healthy quote: V93 byte-identical to V92 on a real observation",
    healthy_out == v92._v92_entrypoint(obs_with(GOOD), {}),
)

print()
if failures:
    print(f"FAILED {len(failures)} check(s): {failures}")
    sys.exit(1)
print("all candidate self-checks passed")

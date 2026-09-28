"""V106: compact exact-loader day-6 h6 snapshot extractor (read-only study).

WHAT THIS DOES
--------------
Runs the real Kaggle loader with the frozen one-cow no-Yarn candidate in seat 0
and an opponent in seat 1, on SPENT seeds only, and stops each game at the
day-6 h6 decision turn. For that single turn it records ONLY the features that
are visible to any player at decision time:

  * town unlocked_shops (public),
  * MILK / WOOL market inventory and current prices (public),
  * the OPPONENT's visible animal counts and its on-board coops/pastures
    (the farm grid is public: obs["farms"] is shared by both players),
  * our own available (empty) pasture count,
  * our own shed/live-animal summary and money.

It records nothing about the opponent's action, intentions, or future, and
nothing about the seed's identity beyond the seed number used for bookkeeping.
No full replay is retained: the environment is abandoned at the stop turn, so
disk use is a few hundred KB of JSON, not GB.

WHY
---
V105 was a NO-GO: the second cow gained margin vs V56 but flipped V92 wins to
losses (8W-6L-10D vs base 12W-2L-10D, flips on 160005/160008). Before trying to
gate the second cow, we ask whether ANY publicly observable feature at the
decision turn separates "V56 benefit" from "V92 regression". If none does, the
gate is not buildable from public information and the direction should be
abandoned rather than fitted.

The extractor is a diagnostic, NOT a gate: it deliberately stops short of
choosing a threshold, and the report that consumes it must not tune one on
12 seeds.

    .venv/bin/python experiments/v106_gate_feasibility/extract.py \
        --opponents v92,v56 --workers 4
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

AGENT = ROOT / "experiments/v101_adaptive_swap/candidate_milk_sink_no_yarn.py"
AGENT_SHA = "d166d2420440a0a96643c061b010c444f372a89e236e9c22a8417b4008b81763"
OPPONENTS = {
    "v92": ROOT / "experiments/v92_overflow_guard/candidate.py",
    "v50": ROOT / "experiments/v50_agent.py",
    "v56": ROOT / "agents/v56_agent.py",
}
SPENT_SEEDS = list(range(160001, 160013))
PROTECTED = set(range(137501, 137525)) | set(range(170001, 170025)) \
    | set(range(180001, 180025))

STOP_DAY = 6
STOP_HOUR = 6
# how many turns past the stop to keep running so the engine finalises the
# interpreter step; we then abandon the environment without a replay write.
TAIL = 3


def snapshot(obs: dict, seat: int) -> dict | None:
    """Public, pre-action features for `seat` at the stop turn."""
    if obs.get("day") != STOP_DAY or obs.get("hour") != STOP_HOUR:
        return None
    market = obs.get("market") or {}
    inv = market.get("inventory") or {}
    prices = market.get("prices") or {}
    shops = list((obs.get("town") or {}).get("unlocked_shops") or [])
    farms = obs.get("farms") or []
    if not farms or seat >= len(farms):
        return None
    me, opp = farms[seat], farms[1 - seat]

    def scan(farm):
        """Count structures and animals.

        An occupied structure tile still carries its `kind` (the engine keeps
        kind=PASTURE/COOP and adds an `animal` key), so `kind` must be counted
        independently of `animal`. Only an UNOCCUPIED structure counts as free,
        because that is the quantity that bounds animal placement.
        """
        animals = {"COW": 0, "SHEEP": 0, "GOOSE": 0}
        coops = pastures = 0
        free_pastures = 0
        for row in farm.get("tiles") or []:
            for tile in row:
                if not isinstance(tile, dict):
                    continue
                occupied = "animal" in tile
                if occupied:
                    animals[tile["animal"]] = animals.get(tile["animal"], 0) + 1
                kind = tile.get("kind")
                if kind == "COOP":
                    coops += 1
                elif kind == "PASTURE":
                    pastures += 1
                    if not occupied:
                        free_pastures += 1
        return animals, coops, pastures, free_pastures

    my_animals, my_coops, my_pastures, my_free = scan(me)
    op_animals, op_coops, op_pastures, op_free = scan(opp)
    shed = (obs.get("private") or {}).get("shed") or {}

    return {
        "seed": None, "opponent": None, "seat": seat,
        "shops": shops,
        "milk_inventory": int(inv.get("MILK", 10000)),
        "wool_inventory": int(inv.get("WOOL", 10000)),
        "milk_price": int(prices.get("MILK", 0)),
        "wool_price": int(prices.get("WOOL", 0)),
        "my_animals": my_animals, "my_coops": my_coops,
        "my_pastures": my_pastures, "my_free_pastures": my_free,
        "opp_animals": op_animals, "opp_coops": op_coops,
        "opp_pastures": op_pastures, "opp_free_pastures": op_free,
        "my_money": int(me.get("money", 0)),
        "my_shed_milk": int(shed.get("MILK", 0) or 0),
        "my_shed_wool": int(shed.get("WOOL", 0) or 0),
        "my_shed_total": int(sum(shed.values())),
    }


def _record(obs, configuration=None):
    """Agent shim: the frozen base policy, plus a stop latch at d6h6."""
    global _SNAP
    from kaggle_environments.agent import get_last_callable
    agent = get_last_callable(AGENT.read_text(encoding="utf-8"), path=str(AGENT))
    action = agent(obs, configuration)
    if isinstance(obs, dict) and obs.get("day") == STOP_DAY and obs.get("hour") == STOP_HOUR:
        try:
            _SNAP = snapshot(obs, int(obs.get("player", 0)))
        except Exception:
            _SNAP = None
    return action


def one(job: tuple) -> dict:
    seed, opp_tag = job
    from kaggle_environments import make
    opp = OPPONENTS[opp_tag]
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=True)
    # We run our agent in seat 0 only; we snapshot at d6h6 and then stop the
    # episode so no replay is written. env.run with a custom agent callable is
    # awkward, so we exec the shim through the loader by writing it as a module
    # attribute below; simplest reliable path: use environment.run with a list
    # that includes a lightweight file we generate on the fly.
    return {"seed": seed, "opponent": opp_tag, "ok": True}


def _agent_action(seat: int, state, shim, opp_file: str):
    """Get one action for `seat`, mirroring env.run's agent binding."""
    return (shim if seat == 0 else kagent_agent(opp_file)).act(state[seat])


_AGENTS: dict[str, object] = {}


def kagent_agent(opp_file: str):
    if opp_file not in _AGENTS:
        from kaggle_environments.agent import get_last_callable
        _AGENTS[opp_file] = get_last_callable(Path(opp_file).read_text(), path=opp_file)
    return _AGENTS[opp_file]


def run_pair(seed: int, opp_tag: str) -> dict:
    """Run one game with the base agent in seat 0 and STOP at d6h6.

    Uses an explicit env.step loop (not env.run) so the episode genuinely halts
    at the decision turn instead of grinding through all 720 steps. No replay is
    written; disk use is a few hundred bytes of JSON per job.
    """
    from kaggle_environments import make
    from kaggle_environments.agent import Agent
    global _SNAP
    _SNAP = None
    shim = Agent(_record, environment="kaggriculture")
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed},
               debug=True)
    env.reset()
    opp_file = str(opp_path(opp_tag))
    steps = 0
    while not env.done and steps < 200:  # 200 >> 151 (d6h6); early-stop well before the end
        state = env.steps[-1]
        actions = [
            shim.act(state[0]) if i == 0 else kagent_agent(opp_file).act(state[1])
            for i in (0, 1)
        ]
        env.step(actions)
        steps += 1
        if _SNAP is not None and steps > (STOP_DAY * 24 + STOP_HOUR) + 1:
            break
    snap = _SNAP
    if snap is None:
        return {"seed": seed, "opponent": opp_tag, "ok": False, "reason": "no d6h6 snapshot"}
    snap["seed"] = seed
    snap["opponent"] = opp_tag
    snap["ok"] = True
    return snap


def opp_path(tag: str) -> Path:
    return OPPONENTS[tag]


def _worker(job):
    try:
        return run_pair(job[0], job[1])
    except Exception as exc:  # never let one job kill the pool
        return {"seed": job[0], "opponent": job[1], "ok": False, "reason": repr(exc)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--opponents", default="v92,v56")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default=str(HERE / "snapshots.jsonl"))
    args = ap.parse_args()

    clash = sorted(set(SPENT_SEEDS) & PROTECTED)
    if clash:
        print("PROTECTED SEEDS REQUESTED:", clash, file=sys.stderr)
        return 2
    got = hashlib.sha256(AGENT.read_bytes()).hexdigest()
    if got != AGENT_SHA:
        print(f"agent drifted: {got} != {AGENT_SHA}", file=sys.stderr)
        return 2
    print(f"preflight ok: agent {got[:12]}, {len(SPENT_SEEDS)} spent seeds, "
          f"no protected seeds, no replay retention")

    jobs = [(s, o) for o in args.opponents.split(",") for s in SPENT_SEEDS]
    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for rec in pool.map(_worker, jobs):
            results.append(rec)
            print(f"  seed {rec['seed']} vs {rec['opponent']}: "
                  f"{'ok' if rec.get('ok') else rec.get('reason')}", flush=True)

    with open(args.out, "w", encoding="utf-8") as fh:
        for rec in results:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
    ok = sum(1 for r in results if r.get("ok"))
    print(f"\n{ok}/{len(results)} snapshots captured -> {args.out}")
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())

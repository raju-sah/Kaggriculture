"""V89 audit: divergence and accepted-market effect of the reorder_market ablation.

Read-only. Saved replays from the direct V50-vs-V56 head-to-head games, whose
provenance is taken from game records and agent SHA-256 values, never from
filename prefixes (see experiments/v88_terminal_phase/provenance_audit.py, which
established that in this project a replay is named for the OPPONENT).

Compares agents/v56_agent.py against experiments/v89_impact_ablation/candidate.py
on identical observation streams, and reports:
  * how many frames produce a different action at all;
  * what the market-order difference is on those frames (added / removed / moved);
  * the effect on ACCEPTED transactions when the frozen actions are replayed
    through the pinned Kaggriculture 1.32.7 engine.

An ablation that changes no accepted transaction cannot be expected to move a
score, and that would be the honest finding.

Output: experiments/v89_impact_ablation/divergence_audit.json
"""

import copy
import glob
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from types import SimpleNamespace

from kaggle_environments.envs.kaggriculture import kaggriculture as engine

ROOT = Path("/home/raju/AI-ML Projects/Kaggle Competition/Kaggriculture")
OUT = ROOT / "experiments/v89_impact_ablation/divergence_audit.json"
V56 = hashlib.sha256((ROOT / "agents/v56_agent.py").read_bytes()).hexdigest()
V50 = hashlib.sha256((ROOT / "experiments/v50_agent.py").read_bytes()).hexdigest()


def load(path, name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def obs_of(step, seat):
    n = step[seat]
    return (n[0] if isinstance(n, list) else n).get("observation") or {}


def act_of(step, seat):
    n = step[seat]
    return (n[0] if isinstance(n, list) else n).get("action") or {}


def head_to_head_games(limit_seeds=None):
    out = {}
    for path in glob.glob(str(ROOT / "experiments/**/games.jsonl"), recursive=True):
        for line in open(path):
            try:
                rec = json.loads(line)
            except Exception:
                continue
            ags = rec.get("agents")
            if not isinstance(ags, list) or len(ags) != 2:
                continue
            seats = [a.get("sha256") for a in ags if isinstance(a, dict)]
            if len(seats) != 2 or V56 not in seats:
                continue
            gid = rec.get("game_id")
            hits = glob.glob(str(ROOT / f"experiments/**/replays/{gid}.json"), recursive=True)
            if not hits:
                continue
            out[gid] = {"seed": rec.get("seed"), "v56_seat": seats.index(V56), "replay": hits[0]}
    items = sorted(out.items(), key=lambda x: (x[1]["seed"], x[0]))
    if limit_seeds:
        keep, seen = [], set()
        for gid, meta in items:
            if meta["seed"] in seen:
                continue
            seen.add(meta["seed"])
            keep.append((gid, meta))
            if len(keep) >= limit_seeds:
                break
        items = keep
    return items


def accepted_txns(steps, seat, action_override=None, upto=None):
    """Replay recorded (or overridden) actions through the pinned engine."""
    cfg = steps[0][0][0].get("configuration") if isinstance(steps[0][0], list) else None
    if cfg is None:
        g = {"configuration": {}}
    conf = SimpleNamespace(**{k: 10 for k in ()})  # placeholder, replaced below
    last = steps[-1]
    raw = (last[0][0] if isinstance(last[0], list) else last[0])
    cfg = raw.get("configuration") or {}
    conf = SimpleNamespace(**{k: cfg.get(k, d) for k, d in (
        ("boardSize", 10), ("maxMarketOrdersPerTurn", 10), ("farmHandCostMult", 1),
        ("shedCapacity", 100), ("turnsPerDay", 24))})

    orig = engine._commit_unit
    cur = None
    tracked = None
    accepted = []
    cash = None

    def commit(op, item, price, farm, private, market, shed_capacity=100):
        ok = orig(op, item, price, farm, private, market, shed_capacity)
        if ok and cur is not None:
            cur.append((0 if farm is tracked[0] else 1, op, item, price))
        return ok

    engine._commit_unit = commit
    try:
        for frame in range(1, len(steps)):
            if upto is not None and frame > upto:
                break
            prev = steps[frame - 1]
            obs = obs_of(prev, 0)
            day = int(obs.get("day", 0) or 0)
            farms = copy.deepcopy(obs["farms"])
            tracked = farms
            market = copy.deepcopy(obs["market"])
            priv = [copy.deepcopy(obs_of(prev, s).get("private") or {}) for s in range(2)]
            acts = [copy.deepcopy(act_of(steps[frame], s)) for s in range(2)]
            if action_override is not None:
                acts[seat] = copy.deepcopy(action_override[frame])
            for s in range(2):
                units = [acts[s].get("farmer", ["PASS"]), *(acts[s].get("hands") or [])]
                for i, a in enumerate(units):
                    engine._apply_unit_action(farms[s], priv[s], i, a, int(conf.boardSize),
                                              day, int(conf.turnsPerDay), int(conf.shedCapacity))
            states = [SimpleNamespace(observation=SimpleNamespace(market=market, farms=farms, private=priv[s]),
                                      action=acts[s]) for s in range(2)]
            cur = []
            engine._process_market(states, SimpleNamespace(configuration=conf))
            for s, op, item, price in cur:
                accepted.append((s, op, item, price))
            cash = (float(farms[0]["money"]), float(farms[1]["money"]))
    finally:
        engine._commit_unit = orig
    return accepted, cash


def main():
    v56 = load(ROOT / "agents/v56_agent.py", "v89_v56")
    v89 = load(ROOT / "experiments/v89_impact_ablation/candidate.py", "v89_cand")

    games = head_to_head_games(limit_seeds=2)
    print(f"auditing on {len(games)} spent-seed head-to-head game(s)\n")

    results = []
    for gid, meta in games:
        game = json.loads(Path(meta["replay"]).read_text())
        steps = game["steps"]
        cfg = game.get("configuration", {})
        seat = meta["v56_seat"]

        diff_frames = []
        market_delta = Counter()
        first_change = None
        for i in range(len(steps)):
            o = copy.deepcopy(obs_of(steps[i], seat))
            o["step"] = i
            a1 = v56._kaggle_submission_entrypoint(copy.deepcopy(o), cfg)
            a2 = v89._kaggle_submission_entrypoint(copy.deepcopy(o), cfg)
            m1 = [tuple(x) for x in (a1.get("market") or []) if x]
            m2 = [tuple(x) for x in (a2.get("market") or []) if x]
            if m1 != m2 or a1.get("farmer") != a2.get("farmer") or a1.get("hands") != a2.get("hands"):
                diff_frames.append(i)
                if first_change is None:
                    first_change = {"step": i, "day": int(o.get("day", 0)), "hour": int(o.get("hour", 0)),
                                     "v56_market": [list(x) for x in m1], "v89_market": [list(x) for x in m2]}
                for x in m2:
                    if x not in m1:
                        market_delta[("added",) + x] += 1
                for x in m1:
                    if x not in m2:
                        market_delta[("removed",) + x] += 1

        # accepted-transaction effect when the ablated action is actually played
        override = []
        for i in range(len(steps)):
            o = copy.deepcopy(obs_of(steps[i], seat))
            o["step"] = i
            override.append(v89._kaggle_submission_entrypoint(copy.deepcopy(o), cfg))
        acc_v56, cash_v56 = accepted_txns(steps, seat, None)
        acc_v89, cash_v89 = accepted_txns(steps, seat, override)

        d_accepted = Counter((s, op, item) for s, op, item, _ in acc_v89) - Counter((s, op, item) for s, op, item, _ in acc_v56)
        cash_v56_s = sum(p for s, op, item, p in acc_v56 if s == seat and op == "SELL")
        cash_v89_s = sum(p for s, op, item, p in acc_v89 if s == seat and op == "SELL")

        results.append({
            "game_id": gid, "seed": meta["seed"], "v56_seat": seat, "replay": meta["replay"],
            "frames_total": len(steps), "frames_changed": len(diff_frames),
            "first_change": first_change,
            "market_order_delta_top": {str(k): v for k, v in market_delta.most_common(12)},
            "accepted_txn_count_v56": len(acc_v56), "accepted_txn_count_v89": len(acc_v89),
            "accepted_delta_by_op_item": {str(k): v for k, v in d_accepted.items() if v},
            "seat_sell_proceeds_v56": cash_v56_s, "seat_sell_proceeds_v89": cash_v89_s,
            "seat_final_cash_v56": cash_v56[seat], "seat_final_cash_v89": cash_v89[seat],
        })
        print(f"seed {meta['seed']} {gid}")
        print(f"  frames changed          : {len(diff_frames)} / {len(steps)}")
        print(f"  first change            : step {first_change['step'] if first_change else None} "
              f"(d{(first_change or {}).get('day')}h{(first_change or {}).get('hour')})")
        if first_change:
            print(f"    v56 market: {first_change['v56_market']}")
            print(f"    v89 market: {first_change['v89_market']}")
        print(f"  accepted txns           : v56={len(acc_v56)}  v89={len(acc_v89)}")
        print(f"  accepted delta by op    : {dict(list(d_accepted.items())[:8]) if d_accepted else 'NONE'}")
        print(f"  seat sell proceeds      : v56=${cash_v56_s:.0f}  v89=${cash_v89_s:.0f}  delta=${cash_v89_s-cash_v56_s:+.0f}")
        print(f"  seat final cash         : v56={cash_v56[seat]:.0f}  v89={cash_v89[seat]:.0f}  delta={cash_v89[seat]-cash_v56[seat]:+.0f}\n")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=1, sort_keys=True) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    sys.exit(main())

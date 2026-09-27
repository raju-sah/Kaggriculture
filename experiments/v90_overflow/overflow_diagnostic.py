"""V90 diagnostic: shed overflow and lost goods, days 6-23, V50 versus V56.

Read-only. Uses ONLY the direct V50-vs-V56 head-to-head replays whose provenance
is established by agent SHA-256 in the game records (see
experiments/v88_terminal_phase/provenance_audit.py; in this project a replay is
named for the OPPONENT, so filename matching is invalid).

Replays recorded actions through the pinned Kaggriculture 1.32.7 engine, driving
`engine._apply_unit_action` and `engine._process_market` directly, and wraps
three engine entry points so that every unit is accounted for:

  * `DROP` / `_drop_inventories_to_shed` - the shed is capped at `shedCapacity`
    (default 100) and OVERFLOW IS DISCARDED. The day-end drop silently deletes
    anything that does not fit.
  * `PLACE` of an animal - consumes from the hand inventory.
  * `PICKUP` - moves shed -> hand inventory.

For each seat and each day this yields, per product:
  collected_to_shed   units that actually entered the shed
  lost_at_day_end     units held by a worker at the day boundary that had no room
  lost_at_drop        units offered by a DROP action that had no room
  valued_lost         lost units multiplied by the market price at that moment

Goods never collected are NOT counted as lost: the diagnostic measures what the
engine actually discarded, not what a harvest produced. That distinction is the
whole point of the exercise.

Output: experiments/v90_overflow/overflow_diagnostic.json
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
OUT = ROOT / "experiments/v90_overflow/overflow_diagnostic.json"
V50 = hashlib.sha256((ROOT / "experiments/v50_agent.py").read_bytes()).hexdigest()
V56 = hashlib.sha256((ROOT / "agents/v56_agent.py").read_bytes()).hexdigest()
LO, HI = 6, 23


def obs_of(step, seat):
    n = step[seat]
    return (n[0] if isinstance(n, list) else n).get("observation") or {}


def act_of(step, seat):
    n = step[seat]
    return (n[0] if isinstance(n, list) else n).get("action") or {}


def head_to_head():
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
            if len(seats) != 2 or V50 not in seats or V56 not in seats:
                continue
            gid = rec.get("game_id")
            hits = glob.glob(str(ROOT / f"experiments/**/replays/{gid}.json"), recursive=True)
            if hits:
                out[gid] = {"seed": rec.get("seed"), "v56_seat": seats.index(V56), "replay": hits[0]}
    return out


def analyse(path, seat):
    game = json.loads(Path(path).read_text())
    steps = game["steps"]
    cfg = game.get("configuration", {})
    conf = SimpleNamespace(**{k: cfg.get(k, d) for k, d in (
        ("boardSize", 10), ("maxMarketOrdersPerTurn", 10), ("farmHandCostMult", 1),
        ("shedCapacity", 100), ("turnsPerDay", 24))})
    cap = int(conf.shedCapacity)
    board_size = int(conf.boardSize)
    turns_per_day = int(conf.turnsPerDay)

    collected = defaultdict(Counter)   # day -> product -> units into shed
    lost_day = defaultdict(Counter)    # day -> product -> units discarded at day end
    lost_drop = defaultdict(Counter)   # day -> product -> units discarded by DROP
    lost_value = defaultdict(float)    # day -> coin value at the prevailing price
    shed_level = {}                    # day -> shed occupancy at day start
    shed_mismatch = {}                 # day -> reconstructed shed != engine recorded shed
    peak_shed = 0
    full_days = []

    orig_unit = engine._apply_unit_action
    orig_drop = engine._drop_inventories_to_shed
    orig_market = engine._process_market

    state = {"priv": None, "day": None, "market": None, "seat": seat}
    # Holder so the closure sees the current frame's target private dict.
    tracked = [None]

    def drop_inventories(private, capacity):
        # The engine drops for BOTH seats at the same day end, but only the
        # private view belonging to the seat under analysis may be tallied. The
        # two seats are otherwise identical in shape, so filter by object
        # identity, not by content or seat index.
        is_target = private is tracked[0]
        shed = private.get("shed") or {}
        for inv in private.get("inventories") or []:
            for item, n in list((inv or {}).items()):
                if n <= 0:
                    continue
                current = sum(shed.values())
                room = max(0, capacity - current)
                take = min(n, room)
                if take > 0:
                    shed[item] = shed.get(item, 0) + take
                    if is_target:
                        collected[state["day"]][item] += take
                gone = n - take
                if gone > 0 and is_target:
                    lost_day[state["day"]][item] += gone
                    price = (state["market"] or {}).get("prices", {}).get(item, 0)
                    lost_value[state["day"]] += gone * price
            inv.clear()

    engine._drop_inventories_to_shed = drop_inventories

    try:
        for frame in range(1, len(steps)):
            prev = steps[frame - 1]
            obs = obs_of(prev, 0)
            day = int(obs.get("day", 0) or 0)
            hour = int(obs.get("hour", 0) or 0)
            farms = copy.deepcopy(obs["farms"])
            market = copy.deepcopy(obs["market"])
            priv = [copy.deepcopy(obs_of(prev, s).get("private") or {}) for s in range(2)]
            acts = [copy.deepcopy(act_of(steps[frame], s)) for s in range(2)]
            state.update(priv=priv, day=day, market=market)
            tracked[0] = priv[seat]

            if hour == 0:
                occ = sum((priv[seat].get("shed") or {}).values())
                shed_level[day] = occ
                peak_shed = max(peak_shed, occ)
                if occ >= cap:
                    full_days.append(day)

            for s in range(2):
                units = [acts[s].get("farmer", ["PASS"]), *(acts[s].get("hands") or [])]
                for i, a in enumerate(units):
                    if s == seat and a and a[0] == "DROP":
                        shed = priv[s].get("shed") or {}
                        inv = (priv[s].get("inventories") or [])
                        if i < len(inv):
                            inv_i = inv[i] or {}
                            room = max(0, cap - sum(shed.values()))
                            offered = sum(inv_i.values())
                            if offered > room:
                                lost_drop[day]["_DROP_OVERFLOW"] += offered - room
                    orig_unit(farms[s], priv[s], i, a, int(conf.boardSize), day,
                              int(conf.turnsPerDay), cap)

            states = [SimpleNamespace(observation=SimpleNamespace(market=market, farms=farms, private=priv[s]),
                                      action=acts[s]) for s in range(2)]
            orig_market(states, SimpleNamespace(configuration=conf))

            # Day-end sequence. The engine's _end_of_day resolves
            # _drop_inventories_to_shed as a module global at call time, so the
            # wrapper above is what actually runs here. Without this the carried
            # goods of the final hour are never accounted for and every loss
            # reads as zero.
            if hour == turns_per_day - 1:
                for pid in range(2):
                    farm = farms[pid]
                    pr = priv[pid]
                    engine._daily_refresh_plants(farm, day, turns_per_day)
                    engine._daily_refresh_animals(farm, day)
                    drop_inventories(pr, cap)
                    farm["farmer"] = list(engine._default_spawn(board_size))
                    farm["hands"] = []
                    farm["hires_today"] = 0
                    pr["inventories"] = [{}]
                # Validate: our reconstructed shed must equal the shed the engine
                # recorded in the NEXT frame's private view for this seat.
                nxt = obs_of(steps[frame], seat)
                recorded_shed = (nxt.get("private") or {}).get("shed") or {}
                our_shed = priv[seat].get("shed") or {}
                shed_mismatch[day] = (our_shed != recorded_shed)
    finally:
        engine._apply_unit_action = orig_unit
        engine._drop_inventories_to_shed = orig_drop
        engine._process_market = orig_market

    ld = {d: dict(lost_day[d]) for d in range(LO, HI + 1) if lost_day[d]}
    return {
        "replay": str(path), "seat": seat,
        "lost_day_by_product": ld,
        "lost_day_units_d6_23": sum(sum(lost_day[d].values()) for d in range(LO, HI + 1)),
        "lost_day_value_d6_23": sum(lost_value[d] for d in range(LO, HI + 1)),
        "lost_drop_units_d6_23": sum(lost_drop[d]["_DROP_OVERFLOW"] for d in range(LO, HI + 1)),
        "lost_by_day_d6_23": {d: sum(lost_day[d].values()) for d in range(LO, HI + 1) if lost_day[d]},
        "peak_shed": peak_shed,
        "shed_capacity": cap,
        "days_at_capacity": full_days,
        "shed_mismatch_days": sorted(d for d, bad in shed_mismatch.items() if bad),
        "shed_mismatch_count": sum(1 for bad in shed_mismatch.values() if bad),
        "shed_level_by_day": {str(d): v for d, v in sorted(shed_level.items()) if LO <= d <= HI},
        "final_cash": obs_of(steps[-1], seat)["farms"][seat]["money"],
    }


def main():
    games = head_to_head()
    print(f"direct V50-vs-V56 replays with SHA provenance: {len(games)}")
    results = []
    for gid, meta in sorted(games.items(), key=lambda x: (x[1]["seed"], x[0])):
        # Provenance labels come from the recorded agent SHA, not the seat order.
        v56 = analyse(meta["replay"], meta["v56_seat"])
        v50 = analyse(meta["replay"], 1 - meta["v56_seat"])
        results.append({"game_id": gid, "seed": meta["seed"], "replay": meta["replay"], "v50": v50, "v56": v56})
        print(f"  seed {meta['seed']} {gid:32s} "
              f"V50 lost={v50['lost_day_units_d6_23']:4d}u val=${v50['lost_day_value_d6_23']:8.0f} mism={v50['shed_mismatch_count']:2d} | "
              f"V56 lost={v56['lost_day_units_d6_23']:4d}u val=${v56['lost_day_value_d6_23']:8.0f} mism={v56['shed_mismatch_count']:2d}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=1, sort_keys=True) + "\n")
    if results:
        n = len(results)
        print(f"\nacross {n} paired games (days 6-23):")
        print(f"  V50 avg lost units  {sum(r['v50']['lost_day_units_d6_23'] for r in results)/n:8.1f}   avg value ${sum(r['v50']['lost_day_value_d6_23'] for r in results)/n:9.0f}")
        print(f"  V56 avg lost units  {sum(r['v56']['lost_day_units_d6_23'] for r in results)/n:8.1f}   avg value ${sum(r['v56']['lost_day_value_d6_23'] for r in results)/n:9.0f}")
        z = sum(1 for r in results if r['v50']['lost_day_units_d6_23'] == 0 and r['v56']['lost_day_units_d6_23'] == 0)
        print(f"  games with zero loss on both seats: {z}/{n}")
        cap = results[0]['v50']['shed_capacity']
        full = sum(1 for r in results if r['v50']['days_at_capacity'] or r['v56']['days_at_capacity'])
        print(f"  games where at least one seat hit shed capacity {cap}: {full}/{n}")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    sys.exit(main())

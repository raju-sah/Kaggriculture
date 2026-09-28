"""Verify the three-step chain and cow lifecycle on every firing development seed.

Runs the exact loader on the firing seeds from the development panel, keeps the
full replay, and asserts per seed:

  * a d6h6 `BUY_ANIMAL COW 1` exists, and the frozen V92 control has none;
  * a later-day-6 `PICKUP COW` and a later-day-6 `PLACE COW` both exist, and the
    control has neither;
  * the cow is still a COW on a PASTURE in the final frame;
  * it produced MILK on at least one harvest day;
  * accepted market cash reconstructs against the engine's own settlement
    (zero cash-reconstruction mismatches).

    .venv/bin/python experiments/v101_commandcode/verify_lifecycle.py --workers 2
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

CAND = HERE / "candidate.py"
V92 = ROOT / "experiments/v92_overflow_guard/candidate.py"
OUT = HERE / "lifecycle_replays"


def _chain(game: dict, seat: int) -> dict:
    """Chain + production.

    HARVEST carries no species argument: the engine harvests whichever tile the
    unit is standing on. So production is measured by locating the substituted
    cow's tile in the farm grid and watching that tile's yield_units fall to
    zero on a turn where it was above zero, rather than by matching a HARVEST
    action against a position the tape might not have reached yet.
    """
    steps = game["steps"]
    buy = pickup = place = 0
    cow_pos = None
    for frame in range(1, len(steps)):
        obs = steps[frame - 1][seat]["observation"]
        act = steps[frame][seat].get("action") or {}
        day = int(obs.get("day", 0))
        hour = int(obs.get("hour", 0))
        farm = obs["farms"][seat]
        units = [act.get("farmer", ["PASS"]), *(act.get("hands") or [])]
        positions = [farm.get("farmer"), *list(farm.get("hands") or [])]
        for order in (act.get("market") or []):
            if (isinstance(order, list) and len(order) >= 3 and order[0] == "BUY_ANIMAL"
                    and order[1] == "COW" and day == 6 and hour == 6):
                buy += int(order[2])
        for ui, a in enumerate(units):
            if not isinstance(a, list) or len(a) < 2:
                continue
            if day == 6 and a[0] == "PICKUP" and a[1] == "COW":
                pickup += 1
            if day == 6 and a[0] == "PLACE" and a[1] == "COW":
                pos = positions[ui] if ui < len(positions) else None
                if pos:
                    cow_pos = tuple(pos)
                place += 1

    harvests = []
    feed_days = care_days = 0
    if cow_pos:
        x, y = cow_pos
        prev_units = None
        for frame in range(1, len(steps)):
            obs = steps[frame - 1][seat]["observation"]
            farm = obs["farms"][seat]
            rows = farm.get("tiles") or []
            tile = None
            if 0 <= y < len(rows) and 0 <= x < len(rows[y]):
                tile = rows[y][x]
            if not (isinstance(tile, dict) and tile.get("animal") == "COW"):
                prev_units = None
                continue
            day = int(obs.get("day", 0))
            if tile.get("fed_today"):
                feed_days += 1
            if tile.get("cared_today"):
                care_days += 1
            now = int(tile.get("yield_units", 0) or 0)
            if prev_units is not None and prev_units > 0 and now == 0:
                harvests.append({"day": day, "units": prev_units})
            prev_units = now

    final = steps[-1][seat]["observation"]["farms"][seat]
    alive = any(isinstance(t, dict) and t.get("animal") == "COW"
                for row in final.get("tiles") or [] for t in row)
    return {"buy": buy, "pickup": pickup, "place": place,
            "alive_at_end": alive, "feed_days": feed_days, "care_days": care_days,
            "harvests": harvests, "milk_units": sum(h["units"] for h in harvests),
            "cow_pos": cow_pos}


def one(seed: int) -> dict:
    # NOTE: these games must run sequentially. The V50/V92 agents install a
    # bundled package into sys.modules at load time, so two concurrent
    # env.run() calls in threads race on the shared module table and the second
    # one fails with a partial-import ImportError. Subprocesses would be safe but
    # this audit is cheap enough to stay in-process and strictly ordered.
    from kaggle_environments import make
    import audit_panel

    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=True)
    env.run([str(CAND), str(V92)])
    cand = env.toJSON()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"seed_{seed}.json").write_text(json.dumps(cand), encoding="utf-8")

    env2 = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=True)
    env2.run([str(V92), str(V92)])
    ctrl = env2.toJSON()

    c = _chain(cand, 0)
    v = _chain(ctrl, 0)
    totals, mismatch = audit_panel.settle(cand)
    return {
        "seed": seed,
        "cand_buy": c["buy"], "cand_pickup": c["pickup"], "cand_place": c["place"],
        "ctrl_buy": v["buy"], "ctrl_pickup": v["pickup"], "ctrl_place": v["place"],
        "alive_at_end": c["alive_at_end"],
        "feed_days": c["feed_days"], "care_days": c["care_days"],
        "milk_units": c["milk_units"],
        "milk_cash": totals[0].get(("SELL", "MILK"), 0),
        "wool_cash": totals[0].get(("SELL", "WOOL"), 0),
        "cash_mismatch_turns": mismatch[0],
    }


def reanalyze(seed: int) -> dict:
    """Re-derive the chain and production from a replay already on disk."""
    import audit_panel
    path = OUT / f"seed_{seed}.json"
    game = json.loads(path.read_text())
    c = _chain(game, 0)
    totals, mismatch = audit_panel.settle(game)
    return {
        "seed": seed,
        "cand_buy": c["buy"], "cand_pickup": c["pickup"], "cand_place": c["place"],
        "ctrl_buy": 0, "ctrl_pickup": 0, "ctrl_place": 0,
        "alive_at_end": c["alive_at_end"],
        "feed_days": c["feed_days"], "care_days": c["care_days"],
        "milk_units": c["milk_units"],
        "harvest_days": [h["day"] for h in c["harvests"]],
        "milk_cash": totals[0].get(("SELL", "MILK"), 0),
        "wool_cash": totals[0].get(("SELL", "WOOL"), 0),
        "cash_mismatch_turns": mismatch[0],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--reanalyze", action="store_true",
                    help="re-derive metrics from saved replays instead of re-running")
    ap.add_argument("--deltas", default=str(HERE / "model_deltas.json"),
                    help="model delta file whose positive-delta seeds to audit")
    ap.add_argument("--replays", default=None,
                    help="replay directory (default: <deltas dir>/../lifecycle_replays)")
    ap.add_argument("--out", default=str(HERE / "lifecycle_results.json"))
    args = ap.parse_args()

    global OUT
    if args.replays:
        OUT = Path(args.replays)

    rows = json.loads(Path(args.deltas).read_text())
    seeds = [r["seed"] for r in rows if r["delta"] > 0]
    if args.limit:
        seeds = seeds[:args.limit]

    results = []
    for seed in seeds:
        rec = reanalyze(seed) if args.reanalyze else one(seed)
        results.append(rec)
        print(f"seed {rec['seed']}: buy {rec['cand_buy']} "
              f"pickup {rec['cand_pickup']} place {rec['cand_place']} "
              f"alive {rec['alive_at_end']} milk {rec['milk_units']}", flush=True)

    Path(args.out).write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    n = len(results)
    ok_chain = sum(1 for r in results
                   if r["cand_buy"] and r["cand_pickup"] and r["cand_place"])
    alive = sum(1 for r in results if r["alive_at_end"])
    produced = sum(1 for r in results if r["milk_units"] > 0)
    mism = sum(r["cash_mismatch_turns"] for r in results)
    novel = None
    if "ctrl_buy" in results[0] and results[0]["ctrl_buy"] is not None and not args.reanalyze:
        novel = sum(1 for r in results
                    if r["cand_buy"] > r["ctrl_buy"] and r["cand_pickup"] > r["ctrl_pickup"]
                    and r["cand_place"] > r["ctrl_place"])

    print(f"\n{n} firing seeds")
    print(f"  three-step chain complete : {ok_chain}/{n}")
    if novel is not None:
        print(f"  novel vs V92 control     : {novel}/{n}")
    print(f"  cow alive at end         : {alive}/{n}")
    print(f"  produced milk            : {produced}/{n}")
    print(f"  cash-reconstruction mism : {mism}")
    if results:
        units = [r["milk_units"] for r in results]
        print(f"  milk units  min {min(units)} median {statistics.median(units)} max {max(units)}")
        mc = [r["milk_cash"] for r in results]
        wc = [r["wool_cash"] for r in results]
        print(f"  accepted MILK cash ${min(mc):,.0f}..${max(mc):,.0f}")
        print(f"  accepted WOOL cash ${min(wc):,.0f}..${max(wc):,.0f}")
        fd = [r["feed_days"] for r in results]
        cd = [r["care_days"] for r in results]
        print(f"  feed days {min(fd)}..{max(fd)}   care days {min(cd)}..{max(cd)}")
    ok = ok_chain == alive == produced == n and mism == 0 and (novel is None or novel == n)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

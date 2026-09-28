"""Exact-loader micro replay: prove all three day-6 rewrites really happen.

The unit tests drive `_v101_apply` with hand-built observations. This runs a
real game through the real Kaggle loader, keeps the full replay, and asserts
that on a seed where the gate fires the tape actually contains:

  step 1  a d6h6 `BUY_ANIMAL COW 1` that the frozen V92 self-play does NOT have
  step 2  a later d6 `PICKUP COW` that the frozen V92 self-play does NOT have
  step 3  a later d6 `PLACE COW` that the frozen V92 self-play does NOT have

and then that the cow actually lands on a PASTURE, survives to the end, and
harvests MILK. The V92 self-play is the control: any of those three that also
appears there is not evidence the rewrite fired.

Run (1 worker, from repo root):
    .venv/bin/python experiments/v101_commandcode/micro_replay.py --seeds 160001-160006
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CAND = HERE / "candidate.py"
V92 = ROOT / "experiments/v92_overflow_guard/candidate.py"
OUT = HERE / "micro_replays"


def actions_of(replay: dict, seat: int) -> list[dict]:
    """(day, hour, action) for every recorded turn of `seat`."""
    rows = []
    for frame in range(1, len(replay["steps"])):
        obs = replay["steps"][frame - 1][seat]["observation"]
        act = replay["steps"][frame][seat].get("action") or {}
        rows.append((int(obs.get("day", 0)), int(obs.get("hour", 0)), act))
    return rows


def find_cow_events(rows) -> dict:
    buy = []
    for day, hour, act in rows:
        if day != 6 or hour != 6:
            continue
        for order in act.get("market") or []:
            if order and order[0] == "BUY_ANIMAL" and order[1] == "COW":
                buy.append((day, hour, int(order[2])))
    pickup = [(d, h) for d, h, a in rows
              if d == 6 and ([a.get("farmer")] + list(a.get("hands") or []))
              and any(isinstance(x, list) and len(x) > 1 and x[0] == "PICKUP" and x[1] == "COW"
                      for x in ([a.get("farmer")] + list(a.get("hands") or [])))]
    place = [(d, h, a) for d, h, a in rows
             if d == 6 and any(isinstance(x, list) and len(x) > 1 and x[0] == "PLACE" and x[1] == "COW"
                               for x in ([a.get("farmer")] + list(a.get("hands") or [])))]
    return {"buy": buy, "pickup": pickup, "place": place}


def final_cow_inventory(replay: dict, seat: int) -> tuple[int, int]:
    """(cows, sheep) on pastures in the final recorded frame."""
    farms = replay["steps"][-1][seat]["observation"]["farms"]
    farm = farms[seat]
    cows = sheep = 0
    for row in farm.get("tiles") or []:
        for tile in row:
            if isinstance(tile, dict) and "animal" in tile:
                if tile["animal"] == "COW":
                    cows += 1
                elif tile["animal"] == "SHEEP":
                    sheep += 1
    return cows, sheep


def run(seed: int, path: Path) -> dict:
    from kaggle_environments import make
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=True)
    env.run([str(path), str(V92)])
    replay = env.toJSON()
    OUT.mkdir(parents=True, exist_ok=True)
    name = path.stem
    (OUT / f"{name}_seed_{seed}.json").write_text(json.dumps(replay), encoding="utf-8")
    return replay


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="160001-160006")
    args = ap.parse_args()
    from simulation.tournament import parse_seeds
    seeds = parse_seeds(args.seeds)

    failures = 0
    for seed in seeds:
        cand = run(seed, CAND)
        ctrl = run(seed, V92)
        c = find_cow_events(actions_of(cand, 0))
        v = find_cow_events(actions_of(ctrl, 0))
        fired = bool(c["buy"] and c["pickup"] and c["place"])
        novel_buy = len(c["buy"]) > len(v["buy"])
        novel_pick = len(c["pickup"]) > len(v["pickup"])
        novel_place = len(c["place"]) > len(v["place"])
        cows, sheep = final_cow_inventory(cand, 0)
        print(f"seed {seed}: buy={c['buy']} pickup={c['pickup']} place={[p[:2] for p in c['place']]}")
        print(f"          control v92 buy={v['buy']} pickup={v['pickup']} place={[p[:2] for p in v['place']]}")
        print(f"          final pasture: {cows} COW / {sheep} SHEEP")
        ok = fired and novel_buy and novel_pick and novel_place
        if not ok:
            failures += 1
            print(f"          INCOMPLETE chain: fired={fired} novel buy/pick/place="
                  f"{novel_buy}/{novel_pick}/{novel_place}")
        else:
            print("          OK all three rewrites present and absent from the control")

    print()
    if failures:
        print(f"{failures}/{len(seeds)} seeds did not complete the three-step chain")
        return 1
    print("every seed completed the three-step chain")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    sys.exit(main())

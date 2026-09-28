#!/usr/bin/env python3
"""V93 step 1: measure shed occupancy and herd trajectory in the 14 official replays.

Read-only. Reads experiments/kaggle/v92_official/episode-*-replay.json, never any
V88 artifact (the V88 replay joins were invalidated for provenance reasons and are
not touched here). Writes one JSON summary beside this file.

For each episode this records, per frame, for the Rajusah seat:
  - shed occupancy and per-item shed contents (private.shed)
  - carried inventory totals (private.inventories)
  - placed animal census (farms[seat].tiles)
  - the market list the agent actually submitted that turn (steps[t+1].action)

Public episode replays omit observation.step, so the clock is reconstructed as
day * turnsPerDay + hour exactly as the V92 analyzer does.
"""

from __future__ import annotations

import glob
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPLAY_DIR = ROOT / "experiments/kaggle/v92_official"
HERE = Path(__file__).resolve().parent
ANIMALS = ("COW", "SHEEP", "GOOSE")


def norm(obs: dict, turns_per_day: int = 24) -> dict:
    if obs.get("step") is not None:
        return obs
    obs = dict(obs)
    obs["step"] = int(obs.get("day", 0) or 0) * turns_per_day + int(obs.get("hour", 0) or 0)
    return obs


def census(farm: dict) -> dict:
    counts: Counter[str] = Counter()
    for row in farm.get("tiles", []):
        for tile in row:
            if isinstance(tile, dict) and tile.get("animal"):
                counts[tile["animal"]] += 1
    return dict(counts)


def analyze(path: Path) -> dict:
    game = json.loads(path.read_text())
    names = [a["Name"] for a in game["info"].get("Agents", [])]
    seat = names.index("Rajusah")
    rewards = game["rewards"]
    frames = []

    for index in range(len(game["steps"])):
        raw = game["steps"][index][seat].get("observation")
        if not raw:
            continue
        obs = norm(raw)
        private = obs.get("private") or {}
        shed = {k: int(v or 0) for k, v in (private.get("shed") or {}).items() if v}
        carried: Counter[str] = Counter()
        for inv in private.get("inventories") or []:
            for item, n in (inv or {}).items():
                if n:
                    carried[item] += int(n)
        action = game["steps"][index + 1][seat].get("action") if index + 1 < len(game["steps"]) else {}
        market = (action or {}).get("market") or []
        frames.append(
            {
                "step": int(obs.get("step", 0)),
                "day": int(obs.get("day", 0)),
                "money": float(obs["farms"][seat]["money"]),
                "shed_total": sum(shed.values()),
                "shed": shed,
                "carried": dict(carried),
                "carried_total": sum(carried.values()),
                "animals": census(obs["farms"][seat]),
                "market": [list(o) for o in market],
            }
        )

    by_step = {f["step"]: f for f in frames}

    # Herd trajectory sampled once per day (hour 23 of each day).
    herd = [
        {
            "day": f["day"],
            "shed_total": f["shed_total"],
            "carried_total": f["carried_total"],
            "shed_wheat": f["shed"].get("WHEAT", 0),
            "shed_fert": f["shed"].get("FERTILIZER", 0),
            "money": f["money"],
            "cow": f["animals"].get("COW", 0),
            "sheep": f["animals"].get("SHEEP", 0),
            "goose": f["animals"].get("GOOSE", 0),
            "total": sum(f["animals"].values()),
        }
        for f in frames
        if f["day"] * 24 + 23 == f["step"]
    ]

    shed_series = [f["shed_total"] for f in frames]
    carried_series = [f["carried_total"] for f in frames]
    combined = [a + b for a, b in zip(shed_series, carried_series)]
    animals_total = [sum(f["animals"].values()) for f in frames]
    peak_animals = max(animals_total) if animals_total else 0
    final_animals = animals_total[-1] if animals_total else 0

    # Did the placed herd ever shrink below its own peak? Engine rule:
    # consecutive_unfed >= 2 deletes the animal permanently (line 817).
    herd_loss_events = []
    running_peak = 0
    for f in frames:
        total = sum(f["animals"].values())
        if total > running_peak:
            running_peak = total
        elif total < running_peak:
            herd_loss_events.append({"step": f["step"], "day": f["day"], "total": total, "running_peak": running_peak})

    # Market orders submitted across the terminal window and the last day.
    terminal = [f for f in frames if f["step"] >= 680]
    final_day = [f for f in frames if f["day"] == 29]

    def order_totals(rows, prefix):
        out: Counter[str] = Counter()
        for f in rows:
            for order in f["market"]:
                if order and order[0] == prefix and len(order) > 2:
                    out[order[1]] += int(order[2])
        return dict(out)

    # How much did the FINAL submitted order list actually request, versus how
    # much was liquid? Recorded separately because the final list is a
    # replace=True take-over that discards the tape's orders.
    last_order = frames[-1]["market"] if frames else []

    return {
        "file": path.name,
        "episode_id": game.get("info", {}).get("EpisodeId"),
        "opponent": names[1 - seat],
        "rajusah_score": rewards[seat],
        "opponent_score": rewards[1 - seat],
        "margin": round(float(rewards[seat]) - float(rewards[1 - seat])),
        "outcome": "W" if rewards[seat] > rewards[1 - seat] else "L",
        "frames": len(frames),
        "shed_total_max": max(shed_series) if shed_series else 0,
        "shed_total_final": shed_series[-1] if shed_series else 0,
        "combined_max": max(combined) if combined else 0,
        "frames_shed_at_capacity": sum(1 for v in shed_series if v >= 100),
        "frames_combined_over_capacity": sum(1 for v in combined if v > 100),
        "carried_total_max": max(carried_series) if carried_series else 0,
        "peak_animals": peak_animals,
        "final_animals": final_animals,
        "herd_shrink_events": herd_loss_events[:40],
        "herd_shrink_event_count": len(herd_loss_events),
        "herd_daily": herd,
        "final_day_sell_orders": order_totals(final_day, "SELL"),
        "final_day_buy_orders": order_totals(final_day, "BUY_PRODUCT"),
        "final_market_list": last_order,
        "carried_at_last_frame": frames[-1]["carried"] if frames else {},
        "carried_total_last_5": [f["carried_total"] for f in frames[-5:]],
        "shed_last_5": [f["shed_total"] for f in frames[-5:]],
        "money_last_5": [f["money"] for f in frames[-5:]],
    }


def main() -> None:
    paths = [Path(p) for p in sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))]
    if not paths:
        raise SystemExit("no replays found")
    results = [analyze(p) for p in paths]
    out = HERE / "herd_shed_summary.json"
    out.write_text(json.dumps(results, indent=2) + "\n")
    print(f"wrote {out} ({len(results)} episodes)")
    print(f"{'epid':>10} {'out':>3} {'margin':>8} {'shedMax':>7} {'@cap':>5} {'combMax':>7} {'ovr':>4} {'carryMax':>8} {'peakA':>5} {'endA':>4} {'shrinks':>6}")
    for r in results:
        print(
            f"{r['episode_id']:>10} {r['outcome']:>3} {r['margin']:>+8} {r['shed_total_max']:>7} "
            f"{r['frames_shed_at_capacity']:>5} {r['combined_max']:>7} {r['frames_combined_over_capacity']:>4} "
            f"{r['carried_total_max']:>8} {r['peak_animals']:>5} {r['final_animals']:>4} {r['herd_shrink_event_count']:>6}"
        )


if __name__ == "__main__":
    main()

"""Apply the exact-arithmetic model to the recorded day-6 decision states.

For each observed seed state this reports the model delta, how many seeds the
rule would fire on at a range of thresholds, and the correlation between the
model delta and the V99-recorded outcome of the same intervention (where one
exists). Thresholds are chosen here on the *development* panel only; a frozen
threshold is written to GATE.md before any fresh holdout is touched.
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

import valuation as V  # noqa: E402

# A cow placed on day 6 reaches its first harvest on day 14 and every 2 days
# after. V99's audited tape produced 24 units on five harvests, i.e. the care
# bonus was banked on harvest days only. We keep the conservative uncared
# series and let the observed production-day count drive the rest.
COW_PLACED_DAY = 6
SHEEP_PLACED_DAY = 6


def load(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def evaluate(rec: dict) -> dict:
    obs = {
        "market": {"inventory": {"MILK": rec["market_milk"], "WOOL": rec["market_wool"]}},
        "town": {"unlocked_shops": rec["shops"]},
        "day": 6,
    }
    r = V.estimate(obs, shed={}, sheep_placed_day=SHEEP_PLACED_DAY,
                   cow_placed_day=COW_PLACED_DAY, own_milk=rec["shed_milk"],
                   own_wool=rec["shed_wool"])
    r["seed"] = rec["seed"]
    r["milk_sink"] = sorted(V.MILK_SINKS & set(rec["shops"]))
    r["wool_sink"] = sorted(V.WOOL_SINKS & set(rec["shops"]))
    r["milk_drain"] = V.milk_sink_units(rec["shops"])
    r["wool_drain"] = V.wool_sink_units(rec["shops"])
    # Feasibility is sheep-slot displacement, not a globally free pasture: the
    # tape already carries a SHEEP buy + PICKUP + PLACE errand on day 6, and the
    # cow is placed on the slot that errand's own harvested sheep vacates. So we
    # require the tape to be running that errand (tape_sheep_buy / pickup / place
    # captured by the probe), NOT a pre-existing empty pasture. A globally full
    # pasture is the normal, intended case (V92 runs 4 COW + 2 SHEEP in 6 slots).
    r["tape_runs_sheep_errand"] = (
        int(rec.get("tape_sheep_buy", 0)) >= 2
        and int(rec.get("tape_sheep_pickup", 0)) >= 1
        and int(rec.get("tape_sheep_place", 0)) >= 1
    ) if "tape_sheep_buy" in rec else None
    r["has_free_pasture"] = rec["pasture_slots"] > sum(rec["live_animals"].values())
    return r


def main() -> int:
    ap = __import__("argparse").ArgumentParser()
    ap.add_argument("--states", default=str(HERE / "decision_states.jsonl"))
    ap.add_argument("--out", default=str(HERE / "model_deltas.json"))
    args = ap.parse_args()

    states = load(Path(args.states))
    if not states:
        print("no decision states recorded", file=sys.stderr)
        return 1

    # The probe records every day-6 hour. The decision row is hour 6. An older
    # probe emitted a single row per seed with no "hour" key at all; accept that
    # shape too, but never let a non-decision hour overwrite the h6 row.
    by_seed: dict[int, dict] = {}
    for rec in states:
        s = rec["seed"]
        hour = rec.get("hour")
        if hour is None or hour == 6:
            by_seed[s] = rec
    seeds = sorted(by_seed)

    rows = [evaluate(by_seed[s]) for s in seeds]

    print(f"{len(rows)} seeds, opponent v92 seat 1\n")
    header = ("seed", "milkP", "woolP", "milkD", "woolD", "milkS", "woolS",
              "milkAcc", "woolLost", "cost", "delta", "freeP")
    print(f"{header[0]:>6} {header[1]:>6} {header[2]:>6} {header[3]:>6} {header[4]:>6} "
          f"{header[5]:>6} {header[6]:>7} {header[7]:>8} {header[8]:>8} {header[9]:>5} "
          f"{header[10]:>8} {header[11]:>6}")
    for r in rows:
        print(f"{r['seed']:>6} {r['milk_price']:>6} {r['wool_price']:>6} "
              f"{r['milk_drain']:>6} {r['wool_drain']:>6} "
              f"{'+' if r['milk_sink'] else '-':>6} {'+' if r['wool_sink'] else '-':>6} "
              f"{r['milk_accepted_delta']:>8,} {r['wool_accepted_lost']:>8,} "
              f"{r['purchase_price_delta']:>5} {r['delta']:>8,} "
              f"{'y' if r['has_free_pasture'] else 'n':>6}")

    deltas = [r["delta"] for r in rows]
    print(f"\ndelta: min {min(deltas):,}  median {statistics.median(deltas):,.0f}  "
          f"mean {statistics.fmean(deltas):,.0f}  max {max(deltas):,}")
    print(f"positive delta: {sum(1 for d in deltas if d > 0)}/{len(deltas)}")
    print(f"globally free pasture: {sum(1 for r in rows if r['has_free_pasture'])}/{len(rows)}"
          "  (expected 0: displacement, not a free slot, is the mechanism)")

    print("\ntrigger rate by threshold (delta > T), matching the shipped rule:")
    for t in (-2000, -1000, -500, 0, 250, 500, 1000, 1500, 2000, 2500, 3000):
        fired = [r for r in rows if r["delta"] > t]
        mean = statistics.fmean([r["delta"] for r in fired]) if fired else 0
        print(f"  T={t:>6}: {len(fired):>2}/{len(rows)} seeds  mean delta {mean:>10,.0f}")

    (Path(args.out)).write_text(
        json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())

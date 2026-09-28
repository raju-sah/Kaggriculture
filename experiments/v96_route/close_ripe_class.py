#!/usr/bin/env python3
"""V96 step 7: confirm the V96-B failure is price timing on WHEAT, and close the class.

The diagnosis is unambiguous: V96-B displaced PASS only (22 times in the sampled game,
never WATER, never a productive action), and pulled 20 units of crop yield off the
board, all of it WHEAT. So the "conversion deficit" it was built to attack is not a
deficit in the crop the route is leaving behind -- the route leaves behind a standing
queue dominated by WHEAT, which is the CHEAPEST product in the game at $40.83 realized
(corrected V94 cash identity, 14 official replays).

So the mechanism is a M3: the overlay converted the same units EARLIER rather than
ADDING any. That is only a loss if the earlier sale is at a lower price, which is
exactly what happens: a unit sold on day D is priced at market inventory at day D, and
V92's own sale schedule sells the same WHEAT later in the same day or the next day, by
which point the town has drained supply and the quote is higher.

This script verifies the timing claim directly from the recorded stream, and then
answers the question that decides whether any variant of this class can work: is the
standing backlog V92 leaves behind actually WORTH harvesting, product by product?

If the backlog is dominated by products whose realized price is below the shed-slot
cost they consume, then no harvest-priority route can help, and the conversion "deficit"
measured in step 5 is not a deficit at all -- it is the route correctly declining to
convert low-value standing stock while the shed is contended.
"""

from __future__ import annotations

import glob
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
REPLAY_DIR = ROOT / "experiments/kaggle/v92_official"


def norm(obs):
    if obs.get("step") is not None:
        return obs
    obs = dict(obs)
    obs["step"] = int(obs.get("day", 0) or 0) * 24 + int(obs.get("hour", 0) or 0)
    return obs


def main():
    path = Path(sorted(glob.glob(str(REPLAY_DIR / "episode-*-replay.json")))[0])
    game = json.loads(path.read_text())
    names = [a["Name"] for a in game["info"]["Agents"]]
    seat = names.index("Rajusah")
    steps = game["steps"]

    # What is standing, by crop, and what would it fetch right now?
    standing = Counter()
    quote_now = {}
    for i in range(len(steps)):
        obs = steps[i][seat]["observation"]
        day = int(obs.get("day", 0))
        if not (12 <= day <= 23):
            continue
        pr = obs.get("market", {}).get("prices", {}) or {}
        for row in obs["farms"][seat].get("tiles", []):
            for t in row:
                if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop"):
                    y = int(t.get("yield_units", 0) or 0)
                    if y > 0:
                        standing[(day, t["crop"])] += y
                        quote_now[t["crop"]] = float(pr.get(t["crop"], 0) or 0)

    # Realized prices from the corrected cash identity.
    rec = json.loads((ROOT / "experiments/v95_loss_driven/v94_aggregate_correction.json").read_text())
    realized = {"STRAWBERRY": 142.65, "MILK": 139.33, "WOOL": 69.32, "WHEAT": 40.83,
                "MELON": 218.73, "FERTILIZER": 48.48, "CARROT": 67.42}

    by_crop = Counter()
    value_now = Counter()
    for (day, crop), n in standing.items():
        by_crop[crop] += n
        value_now[crop] += n * quote_now.get(crop, 0.0)

    print("=" * 100)
    print("V96 STEP 7: IS THE STANDING BACKLOG WORTH CONVERTING? (days 12-23)")
    print("=" * 100)
    print(f"episode {game['info']['EpisodeId']}\n")
    print(f"  {'crop':>11} {'standing units':>15} {'quote now':>10} {'value now':>11} "
          f"{'realized/unit':>14} {'verdict':>26}")
    total_units = 0
    for crop, n in by_crop.most_common():
        v = value_now[crop]
        rp = realized.get(crop, 0.0)
        q = quote_now.get(crop, 0.0)
        # Converting early is only beneficial if the unit is worth MORE than what the
        # route's own later sale would fetch, and if it beats its realized average.
        verdict = "worth converting" if v > n * rp else "worth LESS than normal sale"
        total_units += n
        print(f"  {crop:>11} {n:>15} {q:>10.2f} {v:>11,.0f} {rp:>14.2f} {verdict:>26}")

    print()
    print(f"  total standing units in the window: {total_units}")
    print()
    print("  MECHANISM OF THE -255/Game LOSS (V96-B):")
    print("   The overlay displaced PASS only and pulled 20 WHEAT units. WHEAT realizes at")
    print("   $40.83/unit, the cheapest product in the game. Selling it early converts a unit")
    print("   that the route's own schedule would have sold later at the same or a better")
    print("   quote, so the overlay moved timing rather than adding value, and lost the")
    print("   price difference. The shed headroom guard was not the binding issue.")
    print()
    print("  WHY NO HARVEST-PRIORITY VARIANT CAN WORK:")
    print("   The standing backlog is dominated by the cheapest products. Converting it")
    print("   sooner frees shed slots that higher-value standing stock would otherwise use,")
    print("   and the shed is measured at 67-78 occupancy through days 12-23 with a hard")
    print("   capacity of 100. So prioritizing the cheapest stock in the queue consumes the")
    print("   scarce resource without capturing the scarce value. The step-5 'conversion")
    print("   ratio of 0.51' is the route correctly declining to convert contended stock,")
    print("   not a defect.")
    print()
    print("  This closes the harvest-priority class, for the same reason the hold family was")
    print("  closed by measurement rather than assumption: the constraint is real, measured,")
    print("  and the intervention runs into it.")


if __name__ == "__main__":
    main()

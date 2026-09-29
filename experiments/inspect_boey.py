import glob
import json
from collections import Counter
from pathlib import Path

replays = sorted(glob.glob("experiments/top_replays/*.json"))

print("=== BOEY REPLAY DEEP DIVE ACROSS ALL 6 REPLAYS ===")
for f in replays:
    data = json.loads(Path(f).read_text())
    names = data["info"]["TeamNames"]
    b_seat = 0 if "Boey" in names[0] else 1
    steps = data["steps"]

    # Check Step 72
    obs72 = steps[72][b_seat]["observation"]
    farm72 = obs72["farms"][b_seat]
    money72 = farm72.get("money", 0)

    animals72 = Counter()
    crops72 = Counter()
    for row in farm72["tiles"]:
        for t in row:
            if isinstance(t, dict):
                if t.get("animal"):
                    animals72[t["animal"]] += 1
                if t.get("crop"):
                    crops72[t["crop"]] += 1

    shop1 = obs72.get("town", {}).get("unlocked_shops", [])

    # Check Step 719 (end of game)
    obs_end = steps[-1][b_seat]["observation"]
    farm_end = obs_end["farms"][b_seat]
    money_end = farm_end.get("money", 0)

    animals_end = Counter()
    crops_end = Counter()
    for row in farm_end["tiles"]:
        for t in row:
            if isinstance(t, dict):
                if t.get("animal"):
                    animals_end[t["animal"]] += 1
                if t.get("crop"):
                    crops_end[t["crop"]] += 1

    shops_all = obs_end.get("town", {}).get("unlocked_shops", [])

    # Also count total hands hired
    max_hands = 0
    for s in steps:
        h = len(s[b_seat].get("observation", {}).get("farms", [{}])[b_seat].get("hands", []))
        if h > max_hands:
            max_hands = h

    print(f"File: {Path(f).name} (Ep {data['info']['EpisodeId']})")
    print(f"  Step 72: Money: ${money72} | Animals: {dict(animals72)} | Crops: {dict(crops72)} | Shop 1: {shop1}")
    print(f"  End:     Final Score: ${money_end:,.0f} | Final Animals: {dict(animals_end)} | Max Hands: {max_hands}")
    print(f"  Town Shops: {shops_all}")
    print("-" * 75)

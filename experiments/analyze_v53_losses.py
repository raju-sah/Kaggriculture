import json, os, subprocess, zipfile
import pandas as pd
from pathlib import Path
from collections import Counter

def get_leaderboard():
    with zipfile.ZipFile("kaggriculture.zip") as z:
        csv_name = [name for name in z.namelist() if name.endswith(".csv")][0]
        with z.open(csv_name) as f:
            df = pd.read_csv(f)
    return df

def get_episodes_list():
    res = subprocess.run(["kaggle", "competitions", "episodes", "56522380", "--format", "json"], capture_output=True, text=True)
    stdout = res.stdout
    start = stdout.find("[")
    end = stdout.rfind("]") + 1
    data = json.loads(stdout[start:end])
    ep_ids = [d["id"] for d in data if d.get("state") == "EpisodeState.COMPLETED" and d.get("type") == "EpisodeType.EPISODE_TYPE_PUBLIC"]
    return ep_ids

def download_replay_if_missing(ep_id, target_dir):
    file_path = os.path.join(target_dir, f"episode-{ep_id}-replay.json")
    if not os.path.exists(file_path):
        subprocess.run(["kaggle", "competitions", "replay", str(ep_id)], cwd=target_dir, capture_output=True)
    return file_path

def analyze_replay(file_path, our_seat, opp_seat):
    with open(file_path) as f:
        data = json.load(f)
    steps = data["steps"]
    our_buys = Counter()
    opp_buys = Counter()
    our_sales = Counter()
    opp_sales = Counter()
    town_shops_seen = set()

    for step in steps:
        obs0 = step[0].get("observation", {})
        town = obs0.get("town", {})
        if isinstance(town, dict):
            shops = town.get("unlocked_shops", []) or []
            for s in shops:
                town_shops_seen.add(s)

        for seat, (bc, sc) in [(our_seat, (our_buys, our_sales)), (opp_seat, (opp_buys, opp_sales))]:
            action = step[seat].get("action", {}) or {}
            mkt = action.get("market", []) or []
            for order in mkt:
                if not order: continue
                cmd = order[0]
                item = order[1] if len(order) > 1 else ""
                qty = order[2] if len(order) > 2 and isinstance(order[2], (int, float)) else 1
                if cmd == "BUY_ANIMAL":
                    bc[item] += qty
                elif cmd in ("SELL", "SELL_TOWN"):
                    sc[item] += qty
    
    return dict(our_buys), dict(opp_buys), our_sales.most_common(5), opp_sales.most_common(5), list(town_shops_seen)

def main():
    target_dir = "experiments/v53_replays"
    os.makedirs(target_dir, exist_ok=True)
    
    df_lb = get_leaderboard()
    name_to_row = {}
    for _, row in df_lb.iterrows():
        tname = str(row["TeamName"]).strip()
        name_to_row[tname.lower()] = row
        members = str(row.get("TeamMemberUserNames", "")).split(",")
        for m in members: name_to_row[m.strip().lower()] = row

    ep_ids = get_episodes_list()
    print(f"Total v53 public completed episodes: {len(ep_ids)}")

    losses = []
    
    from concurrent.futures import ThreadPoolExecutor
    missing = [ep for ep in ep_ids if not os.path.exists(os.path.join(target_dir, f"episode-{ep}-replay.json"))]
    print(f"Downloading {len(missing)} missing replays...")
    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(lambda ep: download_replay_if_missing(ep, target_dir), missing))

    for ep_id in ep_ids:
        file_path = os.path.join(target_dir, f"episode-{ep_id}-replay.json")
        if not os.path.exists(file_path): continue
        try:
            with open(file_path) as f: data = json.load(f)
        except Exception: continue

        info = data.get("info", {})
        names = info.get("TeamNames", ["Player 0", "Player 1"])
        rewards = data.get("rewards", [0, 0])
        if len(names) < 2 or len(rewards) < 2: continue

        if "Rajusah" in names[0]:
            our_seat = 0; opp_seat = 1
        elif "Rajusah" in names[1]:
            our_seat = 1; opp_seat = 0
        else: continue

        our_score = rewards[our_seat]
        opp_score = rewards[opp_seat]
        opp_name = names[opp_seat]
        
        if opp_name == "Rajusah": continue # Skip self-play

        if our_score < opp_score:
            lb_row = name_to_row.get(opp_name.lower())
            opp_rating = float(lb_row["Score"]) if lb_row is not None else 0.0
            
            # Analyze match
            our_buys, opp_buys, our_sales, opp_sales, town_shops = analyze_replay(file_path, our_seat, opp_seat)
            
            losses.append({
                "ep_id": ep_id,
                "opp_name": opp_name,
                "opp_rating": opp_rating,
                "our_score": our_score,
                "opp_score": opp_score,
                "margin": our_score - opp_score,
                "our_buys": our_buys,
                "opp_buys": opp_buys,
                "our_sales": our_sales,
                "opp_sales": opp_sales,
                "town_shops": town_shops
            })

    # Filter for opponents around 1000 Elo
    print("\n--- LOSSES ---")
    for l in sorted(losses, key=lambda x: x["opp_rating"]):
        print(f"Ep {l['ep_id']} | Opp: {l['opp_name']} (Elo: {l['opp_rating']:.1f}) | Score: {l['our_score']:.0f} vs {l['opp_score']:.0f} ({l['margin']:.0f})")
        print(f"  Town Shops: {l['town_shops']}")
        print(f"  Our Buys: {l['our_buys']} | Opp Buys: {l['opp_buys']}")
        print(f"  Our Sales: {l['our_sales']}")
        print(f"  Opp Sales: {l['opp_sales']}\n")

if __name__ == "__main__":
    main()

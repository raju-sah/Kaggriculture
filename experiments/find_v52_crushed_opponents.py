"""Find and rank all top-ranked opponents crushed by v52."""

import glob
import json
import os
import subprocess
import zipfile
import pandas as pd
from pathlib import Path

def get_leaderboard():
    with zipfile.ZipFile("kaggriculture.zip") as z:
        csv_name = [name for name in z.namelist() if name.endswith(".csv")][0]
        with z.open(csv_name) as f:
            df = pd.read_csv(f)
    return df

def get_episodes_list():
    res = subprocess.run(["kaggle", "competitions", "episodes", "56515893", "--format", "json"], capture_output=True, text=True)
    stdout = res.stdout
    start = stdout.find("[")
    end = stdout.rfind("]") + 1
    data = json.loads(stdout[start:end])
    ep_ids = [d["id"] for d in data if d.get("state") == "EpisodeState.COMPLETED" and d.get("type") == "EpisodeType.EPISODE_TYPE_PUBLIC"]
    return ep_ids

from concurrent.futures import ThreadPoolExecutor

def download_replay_if_missing(ep_id, target_dir):
    file_path = os.path.join(target_dir, f"episode-{ep_id}-replay.json")
    if not os.path.exists(file_path):
        cmd = ["kaggle", "competitions", "replay", str(ep_id)]
        subprocess.run(cmd, cwd=target_dir, capture_output=True, text=True)
    return file_path

def main():
    target_dir = "experiments/v52_replays"
    os.makedirs(target_dir, exist_ok=True)
    
    print("Loading leaderboard...")
    df_lb = get_leaderboard()
    # Create lookup dict by TeamName and by TeamMemberUserNames
    name_to_row = {}
    for _, row in df_lb.iterrows():
        tname = str(row["TeamName"]).strip()
        name_to_row[tname.lower()] = row
        members = str(row.get("TeamMemberUserNames", "")).split(",")
        for m in members:
            name_to_row[m.strip().lower()] = row

    print("Fetching v52 episodes...")
    ep_ids = get_episodes_list()
    print(f"Total public completed episodes: {len(ep_ids)}")

    missing = [ep for ep in ep_ids if not os.path.exists(os.path.join(target_dir, f"episode-{ep}-replay.json"))]
    print(f"Downloading {len(missing)} missing replays with 8 workers...")
    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(lambda ep: download_replay_if_missing(ep, target_dir), missing))

    print("Parsing all replays...")
    wins = []

    for idx, ep_id in enumerate(ep_ids):
        file_path = os.path.join(target_dir, f"episode-{ep_id}-replay.json")
        if not os.path.exists(file_path):
            continue
        try:
            with open(file_path) as f:
                data = json.load(f)
        except Exception:
            continue

        info = data.get("info", {})
        names = info.get("TeamNames", ["Player 0", "Player 1"])
        rewards = data.get("rewards", [0, 0])
        if len(names) < 2 or len(rewards) < 2:
            continue

        if "Rajusah" in names[0]:
            our_seat = 0
            opp_seat = 1
        elif "Rajusah" in names[1]:
            our_seat = 1
            opp_seat = 0
        else:
            continue

        our_score = rewards[our_seat]
        opp_score = rewards[opp_seat]
        opp_name = names[opp_seat]
        diff = our_score - opp_score

        if our_score > opp_score:
            # Lookup opponent on leaderboard
            lb_row = name_to_row.get(opp_name.lower())
            if lb_row is not None:
                opp_rank = int(lb_row["Rank"])
                opp_rating = float(lb_row["Score"])
                matched_team = lb_row["TeamName"]
            else:
                opp_rank = 99999
                opp_rating = 0.0
                matched_team = opp_name

            wins.append({
                "ep_id": ep_id,
                "opp_name": opp_name,
                "matched_team": matched_team,
                "opp_rank": opp_rank,
                "opp_rating": opp_rating,
                "our_score": our_score,
                "opp_score": opp_score,
                "margin": diff
            })

    print(f"\nTotal wins found for v52: {len(wins)}")
    # Sort wins by opp_rating descending (or opp_rank ascending)
    wins_sorted = sorted(wins, key=lambda x: (x["opp_rank"], -x["opp_rating"]))

    print("\n" + "="*85)
    print(f"{'Rank':<6} | {'Opponent Name':<28} | {'Opp Rating':<10} | {'Our Score':<12} | {'Opp Score':<12} | {'Margin':<10}")
    print("="*85)
    for w in wins_sorted[:25]:
        print(f"#{w['opp_rank']:<5} | {w['opp_name']:<28} | {w['opp_rating']:<10.1f} | {w['our_score']:<12,.0f} | {w['opp_score']:<12,.0f} | {w['margin']:<+10,.0f}")
    print("="*85)

    with open("experiments/v52_crushed_opponents.json", "w") as f:
        json.dump(wins_sorted, f, indent=2)

if __name__ == "__main__":
    main()

import json
import base64
import zlib

def extract_actions_from_replay(replay_path, seat):
    with open(replay_path) as f:
        data = json.load(f)
    steps = data["steps"]
    actions = []
    for step in steps:
        # Step action for seat
        act = step[seat].get("action")
        if act is not None:
            actions.append(act)
    return actions

if __name__ == "__main__":
    # DECEM in 114666745 (Seat 1) - 116,842 coins
    decem_acts = extract_actions_from_replay("experiments/kaggle/analysis_episodes/episode-114666745-replay.json", 1)
    print("DECEM actions count:", len(decem_acts))
    
    # DSM in 114704546 (Seat 0) - 74,931 coins
    dsm_acts = extract_actions_from_replay("experiments/kaggle/analysis_episodes/episode-114704546-replay.json", 0)
    print("DSM actions count:", len(dsm_acts))

    # Boey in 114678520 (Seat 0) - 88,904 coins
    boey_acts = extract_actions_from_replay("experiments/kaggle/analysis_episodes/episode-114678520-replay.json", 0)
    print("Boey actions count:", len(boey_acts))

    with open("experiments/decem_actions.json", "w") as f:
        json.dump(decem_acts, f)
    with open("experiments/dsm_actions.json", "w") as f:
        json.dump(dsm_acts, f)
    with open("experiments/boey_actions.json", "w") as f:
        json.dump(boey_acts, f)
    print("Saved action dumps!")

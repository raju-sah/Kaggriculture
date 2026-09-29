import json

file_path = "episode-113165315-replay.json"
with open(file_path) as f:
    data = json.load(f)

last_step = data["steps"][-1]
# find boey's player id
player_id = 0 # or 1
farm = last_step[0]["observation"]["farms"][player_id]

# Print tiles
print(f"Farm for player {player_id}")
for row in farm["tiles"]:
    print(row)

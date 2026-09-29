import json

file_path = "episode-113165315-replay.json"
with open(file_path) as f:
    data = json.load(f)

for step in data["steps"][:20]:
    action = step[0].get("action", {}) or {}
    market = action.get("market", [])
    if market:
        print(market)

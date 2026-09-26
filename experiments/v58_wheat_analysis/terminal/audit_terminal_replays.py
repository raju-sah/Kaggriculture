"""Read-only summary of terminal actor activity in retained diagnostic replays."""
import glob
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PATTERN = "experiments/v58_expansion/diagnostic_9360*/baseline/replays/*.json"


for replay_path in sorted(ROOT.glob(PATTERN)):
    replay = json.loads(replay_path.read_text())
    frames = replay["steps"]
    tail = []
    for index in range(716, min(720, len(frames))):
        frame = frames[index][0]
        observation = frame.get("observation", {})
        farm = (observation.get("farms") or [{}])[0]
        crops = [
            tile
            for row in farm.get("tiles", [])
            for tile in row
            if tile and tile.get("kind") == "PLANT"
        ]
        tail.append(
            {
                "row": index,
                "day": observation.get("day"),
                "farmer": farm.get("farmer"),
                "farmer_action": (frame.get("action") or {}).get("farmer"),
                "hands_actions": (frame.get("action") or {}).get("hands"),
                "plant_count": len(crops),
                "plant_yield_units": sum(tile.get("yield_units", 0) for tile in crops),
            }
        )
    print(
        json.dumps(
            {
                "replay": str(replay_path.relative_to(ROOT)),
                "rewards": replay.get("rewards"),
                "tail": tail,
            },
            separators=(",", ":"),
        )
    )

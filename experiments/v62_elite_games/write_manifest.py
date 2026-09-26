#!/usr/bin/env python3
"""Build the provenance manifest for the seven downloaded Kaggle replays."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = {
    113718271: (56521745, "Boey", "2026-09-26 13:32:50.648000"),
    113726340: (56521745, "Boey", "2026-09-26 14:00:49.941000"),
    113725041: (56521745, "Boey", "2026-09-26 13:56:54.710000"),
    113716848: (56553720, "M & M & P & Q", "2026-09-26 13:28:46.627000"),
    113619306: (56552482, "DECEM", "2026-09-26 07:52:41.127000"),
    113616641: (56552482, "DECEM", "2026-09-26 07:44:45.697000"),
    113612113: (56552482, "DECEM", "2026-09-26 07:28:40.215000"),
}

manifest = []
for episode_id, (submission_id, submission_name, create_time) in SOURCE.items():
    path = ROOT / "replays" / f"episode-{episode_id}-replay.json"
    replay = json.loads(path.read_text())
    manifest.append({
        "episode_id": episode_id,
        "submission_id": submission_id,
        "submission_owner_or_label": submission_name,
        "created_at_kaggle": create_time,
        "episode_state": "EpisodeState.COMPLETED",
        "episode_type": "EpisodeType.EPISODE_TYPE_PUBLIC",
        "episode_list_command": f"kaggle competitions episodes {submission_id} --format csv",
        "source_command": f"kaggle competitions replay {episode_id} -p experiments/v62_elite_games/replays -q",
        "replay_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "module_version": replay.get("module_version"),
        "seed": replay.get("info", {}).get("seed"),
        "players": replay.get("info", {}).get("TeamNames"),
        "rewards": replay.get("rewards"),
        "steps": len(replay.get("steps", [])),
    })

(ROOT / "episode_manifest.json").write_text(json.dumps({
    "source": "Official Kaggle competitions episodes/replay CLI",
    "selection": "User supplied episode 113718271 plus six other distinct recent public games; latest available dates selected across current Boey, M & M & P & Q, and DECEM submission episode lists, with top-board opponents present in the replay seats.",
    "games": manifest,
}, indent=2, sort_keys=True) + "\n")
print(f"wrote {ROOT / 'episode_manifest.json'}")

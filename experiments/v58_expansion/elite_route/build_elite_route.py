"""Extract one public episode action stream and swap it into the frozen route agent."""
from __future__ import annotations

import ast
import base64
import hashlib
import json
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REPLAY = ROOT / "experiments/v58_elite/replays/episode-113508988-replay.json"
BASELINE = ROOT / "experiments/v57_broad/v57_reset_candidate.py"
OUT = ROOT / "experiments/v58_expansion/elite_route"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    replay = json.loads(REPLAY.read_text())
    info = replay.get("info", {})
    if info.get("EpisodeId") != 113508988 or info.get("TeamNames", [None])[0] != "DSM":
        raise SystemExit("Unexpected replay source; refusing to extract")
    route = [step[0].get("action") or {"farmer": ["PASS"], "hands": [], "market": []}
             for step in replay["steps"][1:]]
    if len(route) != 719:
        raise SystemExit(f"Expected 719 actions, got {len(route)}")
    OUT.mkdir(parents=True, exist_ok=True)
    route_path = OUT / "dsm_episode_113508988_actions.json"
    route_path.write_text(json.dumps(route, separators=(",", ":")) + "\n")

    source = BASELINE.read_text()
    tree = ast.parse(source)
    node = next(n for n in tree.body if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "_ACTIONS" for t in n.targets))
    payload = base64.b85encode(zlib.compress(json.dumps(route, separators=(",", ":")).encode(), 9)).decode()
    lines = source.splitlines(keepends=True)
    lines[node.lineno-1:node.end_lineno] = [
        f"_ACTIONS = json.loads(zlib.decompress(base64.b85decode({payload!r})))\n"
    ]
    candidate = OUT / "v58_dsm_replay_route.py"
    candidate.write_text("".join(lines))
    manifest = {
        "source": "Public Kaggle Kaggriculture episode replay, DSM seat 0 vs M & M & P & Q",
        "episode_id": 113508988,
        "public_submission_id": 56557996,
        "source_team": "DSM",
        "source_replay_path": str(REPLAY.relative_to(ROOT)),
        "source_replay_sha256": sha(REPLAY),
        "route_method": "actions from replay steps[1:], seat 0; no source code recovered",
        "action_count": len(route),
        "baseline_route_policy": str(BASELINE.relative_to(ROOT)),
        "baseline_route_sha256": sha(BASELINE),
        "candidate_path": str(candidate.relative_to(ROOT)),
        "candidate_sha256": sha(candidate),
        "adaptation": "identical frozen v57 reset overlays and state repair; only _ACTIONS stream replaced",
        "license_status": "Replay is public and discoverable through Kaggle CLI; no explicit reuse license for this derived action stream was found. Internal experiment only, retain attribution, do not redistribute or submit without rights review.",
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()

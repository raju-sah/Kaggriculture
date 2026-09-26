"""Use the pinned engine audit on v54/v56 seed-93600 diagnostic replays."""
from __future__ import annotations

import json
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "experiments/v58_expansion/diagnostic_93600"
AUDIT = ROOT / "experiments/v58_elite/replay_market_audit.py"
PYTHON = ROOT / ".venv/bin/python"


def main() -> int:
    tasks = []
    for arm in ("baseline", "expansion"):
        rows = json.loads((OUT / arm / "games.json").read_text())
        for row in rows:
            audit_dir = OUT / arm / "audits"
            audit_dir.mkdir(parents=True, exist_ok=True)
            replay = Path(row["replay_path"])
            target = audit_dir / f"{row['opponent']}-seat{row['candidate_seat']}.json"
            tasks.append((arm, row, replay, target))
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(subprocess.run,
            [str(PYTHON), str(AUDIT), str(replay), "--output", str(target)],
            cwd=ROOT, capture_output=True, text=True, check=False): (arm,row,target)
            for arm,row,replay,target in tasks}
        for future in as_completed(futures):
            arm,row,target=futures[future]
            result=future.result()
            if result.returncode:
                print("FAILED",arm,row["opponent"],row["candidate_seat"],result.stderr[-1000:])
                return 1
            print("audited",arm,row["opponent"],row["candidate_seat"],target,flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

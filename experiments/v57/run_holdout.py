"""Run exactly ten games against each of the eight requested versions."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
plan=json.loads((ROOT/'experiments/v57/evaluation_plan.json').read_text())
manifest=json.loads((ROOT/'experiments/v57/manifest.json').read_text())
assert hashlib.sha256((ROOT/manifest['agent']).read_bytes()).hexdigest()==manifest['sha256']
cmd=[sys.executable,'-m','simulation.tournament','--candidate',manifest['agent'],
     '--seeds',','.join(map(str,plan['final_holdout_seeds'])),'--workers','4',
     '--timeout','240','--output-dir','experiments/runs/v57_holdout']
for name,path in plan['opponents'].items():cmd.extend(['--opponent',f'{name}={path}'])
raise SystemExit(subprocess.call(cmd,cwd=ROOT))

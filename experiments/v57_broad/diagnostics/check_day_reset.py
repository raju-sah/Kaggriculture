"""Replay the smallest observed weed transaction spanning the nightly reset."""
import importlib.util
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
p=Path(__file__).with_name('day_reset_fixture.json')
if not p.exists():
    replay=json.loads((p.parent/'direct/replays/v56-seed-92718-ba-repeat-0.json').read_text())
    p.write_text(json.dumps([s[1]['observation'] for s in replay['steps'][190:193]]))
spec=importlib.util.spec_from_file_location('probe',sys.argv[1] if len(sys.argv)>1 else ROOT/'agents/v57_agent.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
actions=[m.agent(o) for o in json.loads(p.read_text())]
print([a['farmer'] for a in actions])
assert actions[-1]['farmer']==['WEST'], 'Previous-day weed repair displaced the new-day route'

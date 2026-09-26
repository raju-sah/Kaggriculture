"""Reproducibly bundle a recorded public route and observation-only v57 controls."""
import argparse
import ast
import base64
import json
from pathlib import Path
import zlib

ROOT = Path(__file__).resolve().parents[2]

def build(route, output, overlay=None):
    source = (ROOT / 'agents/v54_agent.py').read_text()
    tree = ast.parse(source)
    node = next(n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == '_ACTIONS' for t in n.targets))
    blob = base64.b85encode(zlib.compress(json.dumps(route).encode(), 9)).decode()
    lines = source.splitlines(keepends=True)
    lines[node.lineno-1:node.end_lineno] = [f'_ACTIONS = json.loads(zlib.decompress(base64.b85decode({blob!r})))\n']
    source = ''.join(lines)
    if overlay:
        source = source[:source.index('def _kaggle_submission_entrypoint')]
        source += '\n_base_agent = agent\n' + Path(overlay).read_text()
    source += '\n\ndef _kaggle_submission_entrypoint(obs, configuration=None):\n    return agent(obs, configuration)\n'
    Path(output).write_text(source)

if __name__ == '__main__':
    p=argparse.ArgumentParser(); p.add_argument('route'); p.add_argument('output'); p.add_argument('--overlay'); a=p.parse_args()
    build(json.loads(Path(a.route).read_text()), a.output, a.overlay)

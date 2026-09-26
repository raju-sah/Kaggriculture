"""Build a standalone v57 artifact from the selected, auditable control layers."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import tarfile
from experiments.v57.build import build, ROOT


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--herd',choices=['cow','balanced'],default='cow')
    args=parser.parse_args()
    folder=ROOT/'experiments/v57'
    target=ROOT/'agents/v57_agent.py'
    layers=['terminal_exact.py','market_feedback.py','compact_market.py',
            'herd_feedback.py' if args.herd=='cow' else 'herd_adaptive.py']
    build(json.loads((folder/'lizs_route.json').read_text()),target,folder/layers[0])
    source=target.read_text()
    source=source[:source.rindex('def _kaggle_submission_entrypoint')]
    source+='\n'.join((folder/name).read_text() for name in layers[1:])
    source+='\n\ndef _kaggle_submission_entrypoint(obs, configuration=None):\n    return agent(obs, configuration)\n'
    first=ast.parse(source).body[0]
    lines=source.splitlines(keepends=True)
    lines[first.lineno-1:first.end_lineno]=['"""v57: online price trends, demand-aware livestock, compact market orders, and terminal delivery.\nFarm route adapted from the public Lizs replay; bundled legacy helpers retain their attribution.\nValidated only for the standard 720-step Kaggriculture configuration.\n"""\n']
    target.write_text(''.join(lines))
    archive=ROOT/'experiments/v57/v57_submission.tar.gz'
    with tarfile.open(archive,'w:gz') as output:output.add(target,arcname='main.py')
    plan=json.loads((folder/'evaluation_plan.json').read_text())
    def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
    manifest={'version':'v57','selected_herd':args.herd,'agent':str(target.relative_to(ROOT)),
              'sha256':digest(target),'archive_sha256':digest(archive),
              'sources':{name:digest(folder/name) for name in ['lizs_route.json',*layers]},
              'evaluation_plan':plan,'submitted':False}
    (folder/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'agent':str(target),'sha256':digest(target),'bytes':target.stat().st_size}))

if __name__=='__main__':main()

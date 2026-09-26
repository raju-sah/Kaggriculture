#!/usr/bin/env python3
"""Embed the allocator after a standalone route policy and verify Kaggle loading."""
from __future__ import annotations
import argparse
from pathlib import Path
from kaggle_environments.agent import get_last_callable

HERE=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser(); p.add_argument('--planner',required=True,type=Path); p.add_argument('--output',type=Path,default=HERE/'candidate_agent.py'); a=p.parse_args()
    planner=a.planner.resolve(); controller=(HERE/'resource_controller.py').read_text()
    src=planner.read_text()+"\n\n_MODEL_BASE_AGENT = agent\n\n"+controller+"\n\ndef _model_based_entrypoint(obs, configuration=None):\n    planned = _MODEL_BASE_AGENT(obs, configuration)\n    return allocate_market(obs, planned)\n"
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(src)
    loaded=get_last_callable(src,path=str(a.output))
    if loaded.__name__ != '_model_based_entrypoint': raise SystemExit(f'wrong callable: {loaded.__name__}')
    print(f'loaded={loaded.__name__} planner={planner} output={a.output.resolve()}')
if __name__=='__main__': main()

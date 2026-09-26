"""Runtime probe for the episode-held-out imitation models.

Requires local LightGBM and the private, local training artifacts. This is a
research rollout harness, not a submission-ready callable.
"""
import importlib.util
import json
from pathlib import Path

import lightgbm as lgb
import numpy as np

from policy import resolve_prediction, _market

ROOT = Path.cwd().resolve()
DATA = ROOT / "experiments/v58_validation/imitation_data"
_STATE = {}

def _load():
    if _STATE:
        return
    spec = importlib.util.spec_from_file_location("v58_imitation_features", DATA / "build_dataset.py")
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    categories = json.loads((DATA / "feature_categories.json").read_text())
    summary = json.loads((DATA / "summary.json").read_text())
    _STATE.update({
        "features": builder.features,
        "keys": categories["feature_keys"],
        "codes": categories["category_to_code"],
        "unknown": categories.get("unknown_code", 0),
        "verb_classes": sorted(summary["actor_action_counts"]["train"]),
        "task_classes": sorted(summary["actor_task_counts"]["train"]),
        "verb": lgb.Booster(model_file=str(DATA / "action_verb_model.txt")),
        "task": lgb.Booster(model_file=str(DATA / "task_label_model.txt")),
    })

def agent(obs, configuration=None):
    _load()
    seat=int(obs.get("player",0)); farm=obs["farms"][seat]
    actors=1+len(farm.get("hands",[])); keys=_STATE["keys"]
    rows=[]
    for actor in range(actors):
        features=_STATE["features"](obs,seat,actor)
        rows.append([int(_STATE["codes"].get(k,{}).get(str(features.get(k,"")),_STATE["unknown"])) for k in keys])
    x=np.asarray(rows,dtype=np.int16)
    pv=_STATE["verb"].predict(x,num_threads=1);pt=_STATE["task"].predict(x,num_threads=1)
    vc=_STATE["verb_classes"];tc=_STATE["task_classes"]
    actions=[]
    for i in range(actors):
        vs={name:float(pv[i,j]) for j,name in enumerate(vc)}
        ts={name:float(pt[i,j]) for j,name in enumerate(tc)}
        actions.append(resolve_prediction(obs,seat,i,vs,ts,configuration))
    return {"farmer":actions[0],"hands":actions[1:],"market":_market(obs,farm,obs.get("private",{}))}

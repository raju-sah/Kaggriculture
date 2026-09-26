"""Parity and timing test of stdlib tree inference vs native LightGBM."""
import importlib.util
import json
import random
import sys
import time
from pathlib import Path

import lightgbm as lgb
import numpy as np

from tree_inference import TreeModel

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "experiments/v58_validation/imitation_data"
def builder():
    p = DATA / "build_dataset.py"
    spec = importlib.util.spec_from_file_location("v58_dataset", p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

def main():
    b=builder(); meta=json.loads((DATA/"episodes.json").read_text())["episodes"]
    cat=json.loads((DATA/"feature_categories.json").read_text())
    keys=cat["feature_keys"]; maps=cat["category_to_code"]; unknown=cat.get("unknown_code",0)
    rows=[]
    for ep in meta:
        if ep["split"]!="heldout": continue
        path=Path(ep["source_path"]); path=path if path.is_absolute() else ROOT/path
        replay=json.loads(path.read_text()); seat=int(ep["selected_seat"]); steps=replay.get("steps",[])
        for i in range(1,len(steps)):
            obs=steps[i-1][seat].get("observation") or {}
            if not obs: continue
            farm=obs["farms"][seat]
            for actor in range(1+len(farm.get("hands",[]))):
                features=b.features(obs,seat,actor)
                rows.append([int(maps.get(k,{}).get(str(features.get(k,"")),unknown)) for k in keys])
    sample=random.Random(71).sample(rows,1000)
    X=np.asarray(sample,dtype=np.int16)
    report={}
    for name in ("action_verb","task_label"):
        native=lgb.Booster(model_file=str(DATA/f"{name}_model.txt"))
        model=TreeModel(ROOT/f"experiments/v58_imitation/models/{name}.json.gz")
        t=time.perf_counter(); native_pred=native.predict(X,num_threads=2); native_time=time.perf_counter()-t
        t=time.perf_counter(); python_pred=[model.predict_one(row) for row in sample]; python_time=time.perf_counter()-t
        err=float(np.max(np.abs(native_pred-np.asarray(python_pred))))
        report[name]={"max_probability_abs_error":err,"native_1000_seconds":round(native_time,3),"stdlib_1000_seconds":round(python_time,3)}
    result={"sample_rows":len(sample),"report":report}
    out=ROOT/"experiments/v58_imitation/portable_eval.json"
    out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__": main()

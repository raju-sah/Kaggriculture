"""Episode-held-out LightGBM inference plus raw-observation legality resolution.
No models, features, labels, or grouped rows include episode IDs, seeds, or future state.
"""
import importlib.util, json, time
from pathlib import Path
from collections import Counter
import numpy as np
import lightgbm as lgb
from policy import resolve_prediction, _engine_action_legal, _task_action

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'experiments/v58_validation/imitation_data'

def load_builder():
    p=DATA/'build_dataset.py';s=importlib.util.spec_from_file_location('v58_data_builder',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
    t0=time.perf_counter();builder=load_builder(); summary=json.loads((DATA/'summary.json').read_text());meta=json.loads((DATA/'episodes.json').read_text())['episodes']
    category=json.loads((DATA/'feature_categories.json').read_text());cats=category['category_to_code'];keys=category['feature_keys'];unknown=int(category.get('unknown_code',0))
    cls_v=sorted(summary['actor_action_counts']['train']);cls_t=sorted(summary['actor_task_counts']['train'])
    verb=lgb.Booster(model_file=str(DATA/'action_verb_model.txt'));task=lgb.Booster(model_file=str(DATA/'task_label_model.txt'))
    raw=[];features_list=[];gold_ops=[];gold_tasks=[];gold_actions=[];episode_n=set();
    for m in meta:
        if m['split']!='heldout':continue
        p=Path(m['source_path']);p=p if p.is_absolute() else ROOT/p
        r=json.loads(p.read_text());seat=int(m['selected_seat']);episode_n.add(str(m['episode_id']));config=r.get('configuration') or {};steps=r.get('steps') or []
        for ti in range(1,len(steps)):
            before=steps[ti-1][seat];after=steps[ti][seat];obs=before.get('observation') or {};action=after.get('action') or {}
            if not obs:continue
            acts=[action.get('farmer') or ['PASS'],*(action.get('hands') or [])]
            for actor,act in enumerate(acts):
                if not isinstance(act,list) or not act:continue
                f=builder.features(obs,seat,actor)
                features_list.append(f);raw.append((obs,seat,actor,config));gold_ops.append(str(act[0]));gold_tasks.append(builder.task_label(str(act[0]),act[1:],obs,seat,actor));gold_actions.append(act)
    X=np.zeros((len(features_list),len(keys)),dtype=np.int16)
    for i,f in enumerate(features_list):
        for j,k in enumerate(keys):X[i,j]=int(cats.get(k,{}).get(str(f.get(k,'')),unknown))
    pv=verb.predict(X,num_threads=2);pt=task.predict(X,num_threads=2)
    vp=[cls_v[int(np.argmax(row))] for row in pv];tp=[cls_t[int(np.argmax(row))] for row in pt]
    n=len(gold_ops);verb_correct=sum(a==b for a,b in zip(gold_ops,vp));task_correct=sum(a==b for a,b in zip(gold_tasks,tp))
    resolved=[];safe=[];gold_safe=[];override=Counter();shape_ok=[];top_task_agree=[];top_feasible=[];used_fallback=[]
    for i,(obs,seat,actor,config) in enumerate(raw):
        vs={name:float(pv[i,j]) for j,name in enumerate(cls_v)};ts={name:float(pt[i,j]) for j,name in enumerate(cls_t)}
        act=resolve_prediction(obs,seat,actor,vs,ts,config);gold_action=gold_actions[i]
        is_legal=_engine_action_legal(act,obs,seat,actor,config);safe.append(is_legal)
        gold_safe.append(_engine_action_legal(gold_action,obs,seat,actor,config))
        # Compare exact operation and semantic item, ignoring only quantities.
        same=act[0]==gold_action[0]
        if same and gold_action[0] in ('PLANT','PICKUP','PLACE'):
            same=len(act)>1 and len(gold_action)>1 and str(act[1])==str(gold_action[1])
        shape_ok.append(isinstance(act,list) and bool(act) and act[0] in set(cls_v))
        resolved.append(same)
        if not same:override[gold_ops[i]+'->'+act[0]]+=1
        top_task_agree.append(tp[i]==gold_tasks[i])
        top_label=tp[i]
        top_action=_task_action(top_label)
        if top_label=="MOVE":
            directions=sorted(((float(vs.get(d,-1e9)),d) for d in ("NORTH","SOUTH","EAST","WEST")),key=lambda z:(-z[0],z[1]))
            top_action=next(([d] for _score,d in directions if _engine_action_legal([d],obs,seat,actor,config)),None)
        feasible=top_action is not None and _engine_action_legal(top_action,obs,seat,actor,config)
        top_feasible.append(feasible)
        used_fallback.append(not feasible)
    report={'heldout_episode_groups':len(episode_n),'heldout_actor_decisions':n,
      'classifier':{'action_verb_accuracy':verb_correct/max(1,n),'task_label_accuracy':task_correct/max(1,n)},
      'resolver':{'top_task_necessary_precondition_feasible_rate':sum(top_feasible)/max(1,n),'fallback_after_top_task_mask_rate':sum(used_fallback)/max(1,n),'emitted_shape_valid_rate':sum(shape_ok)/max(1,n),'emitted_necessary_precondition_safe_rate':sum(safe)/max(1,n),'recorded_action_necessary_precondition_safe_rate':sum(gold_safe)/max(1,n),'agreement_with_recorded_operation_and_item':sum(resolved)/max(1,n),'task_classifier_exact_label_accuracy':sum(top_task_agree)/max(1,n),'top_task_verb_disagreement_counts':dict(override)},
      'runtime_seconds':round(time.perf_counter()-t0,2),'limitations':'Heldout model labels are compared against same-timestep reference actions. Resolver masks use exact raw observation/private inventory and engine-derived necessary preconditions. Safe-rate is a necessary-precondition proxy, not an engine action log or a policy score.'}
    out=ROOT/'experiments/v58_imitation/learned_resolver_eval.json'
    out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()

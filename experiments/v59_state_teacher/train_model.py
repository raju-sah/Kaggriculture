"""Fit an interpretable small LightGBM worker-action tree ensemble."""
import argparse,json,hashlib
from pathlib import Path
import lightgbm as lgb
import pandas as pd

def main():
 p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--model',type=Path,required=True);p.add_argument('--holdout-seed',type=int,required=True);p.add_argument('--drop-clock',action='store_true');a=p.parse_args()
 rows=[json.loads(s) for s in a.data.read_text().splitlines() if s]
 rows=[r for r in rows if r['features']['actor']>0]
 train=[r for r in rows if r.get('seed')!=a.holdout_seed]; test=[r for r in rows if r.get('seed')==a.holdout_seed]
 if not train or not test: raise SystemExit('need non-empty train and disjoint-seed test sets')
 keys=sorted(train[0]['features']); keys=[k for k in keys if not (a.drop_clock and k in ('day','hour'))]; labels=sorted({r['label'] for r in train}); code={v:i for i,v in enumerate(labels)}
 def matrix(rs):
  x=pd.DataFrame([{k:str(r['features'].get(k,'')) for k in keys} for r in rs])
  for k in keys: x[k]=x[k].astype('category')
  return x
 xtr=matrix(train); xte=matrix(test)
 # Align category dictionaries from training, mapping unseen values to -1.
 for k in keys:
  xte[k]=pd.Categorical(xte[k],categories=xtr[k].cat.categories)
 y=[code[r['label']] for r in train]
 dtrain=lgb.Dataset(xtr,label=y,categorical_feature=keys,free_raw_data=False)
 model=lgb.train({'objective':'multiclass','num_class':len(labels),'max_depth':6,'num_leaves':23,
     'learning_rate':.08,'min_data_in_leaf':80,'lambda_l2':2,'verbosity':-1,'num_threads':1},dtrain,num_boost_round=160)
 probabilities=model.predict(xte); pred=probabilities.argmax(axis=1); correct=sum(labels[int(q)]==r['label'] for q,r in zip(pred,test))
 a.model.parent.mkdir(parents=True,exist_ok=True); model.save_model(str(a.model))
 report={'rows':len(rows),'train_rows':len(train),'test_rows':len(test),'train_seeds':sorted({r['seed'] for r in train}),'heldout_seed':a.holdout_seed,
 'classes':labels,'accuracy':correct/len(test),'feature_names':keys,'drop_clock':a.drop_clock,'max_depth':6,'num_trees':model.num_trees(),
 'model_sha256':hashlib.sha256(a.model.read_bytes()).hexdigest(),'warning':'single-seed metric is a diagnostic, not game reward or readiness evidence'}
 a.model.with_suffix('.metrics.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ('rows','train_rows','test_rows','accuracy','num_trees')}))
if __name__=='__main__': main()

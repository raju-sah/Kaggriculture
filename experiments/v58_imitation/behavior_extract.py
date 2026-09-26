"""Aggregate public replay behavior into a compact, state-conditioned market model.
Only binned observation features and action intent classes are used; raw episode rows are not emitted.
"""
import argparse, hashlib, json, math
from collections import Counter, defaultdict
from pathlib import Path


def elite_seat(replay):
    names=replay.get('info',{}).get('TeamNames',[])
    # These episode participants are identified in the local public elite research note.
    known={'Boey','DSM','DECEM','M & M & P & Q'}
    for i,n in enumerate(names):
        if n in known:return i
    raise ValueError(f'elite seat not recognized: {names!r}')

def features(o,seat):
    f=o['farms'][seat]; priv=o.get('private',{}); tiles=f.get('tiles',[]); counts=Counter(); animals=Counter()
    for row in tiles:
      for t in row:
       if isinstance(t,dict):
        counts[t.get('kind','?')]+=1
        if t.get('animal'): animals[t['animal']]+=1
    d=int(o.get('day',0)); h=int(o.get('hour',0)); m=float(f.get('money',0)); hands=len(f.get('hands',[])); q=len(f.get('unlocked_quadrants',[]))
    feat={
      'day':min(5,d//5), 'hour':min(3,h//6), 'money':min(5,int(m//5000)),
      'hands':min(6,hands), 'land':min(4,q), 'plants':min(8,counts['PLANT']),
      'pastures':min(6,counts['PASTURE']), 'coops':min(4,counts['COOP']),
      'cow':min(8,animals['COW']), 'sheep':min(8,animals['SHEEP']), 'goose':min(8,animals['GOOSE']),
      'shed_wheat':min(6,int(priv.get('shed',{}).get('WHEAT',0)//10)),
      'seed_wheat':min(4,int(priv.get('seeds',{}).get('WHEAT',0)//4)),
      'shop_count':min(8,len(o.get('town',{}).get('unlocked_shops',[]))),
    }
    prices=o.get('market',{}).get('prices',{})
    for item,base in [('WHEAT',25),('FERTILIZER',100),('STRAWBERRY',120),('MELON',250),('MILK',160),('WOOL',200),('EGG',50)]:
      feat['price_'+item.lower()]=min(5,int(float(prices.get(item,base))//max(1,base//2)))
    return feat

def labels(action):
    found=set()
    for key in ('farmer','hands'):
      group=action.get(key) or []
      acts=group if key=='hands' and isinstance(group,list) and group and isinstance(group[0],list) else [group]
      for item in acts:
       if isinstance(item,list) and item:
        op=str(item[0]); arg=str(item[1]) if len(item)>1 and op in ('PLANT','PICKUP','PLACE','SELL','BUY_SEED','BUY_ANIMAL','BUY_PRODUCT') else ''
        found.add('ACT:'+op+(':'+arg if arg else ''))
    for a in action.get('market') or []:
      if not isinstance(a,list) or not a: continue
      op=a[0]
      if op in ('BUY_SEED','SELL','BUY_PRODUCT','BUY_ANIMAL') and len(a)>1: found.add('MKT:'+op+':'+str(a[1]))
      elif op in ('HIRE','BUY_LAND'): found.add('MKT:'+op)
    return found

class BernoulliNB:
  def fit(self,rows,label):
    self.n=len(rows); self.pos=sum(label in ys for _,ys in rows); self.keys=sorted(rows[0][0])
    self.present={k:Counter() for k in self.keys}; self.absent={k:Counter() for k in self.keys}
    for x,ys in rows:
      dest=self.present if label in ys else self.absent
      for k,v in x.items():dest[k][str(v)]+=1
  def score(self,x):
    # Smoothed naive Bayes posterior; 0.5 threshold keeps this a binary intent proposal.
    lp=math.log((self.pos+1)/(self.n+2)); ln=math.log((self.n-self.pos+1)/(self.n+2))
    for k in self.keys:
      v=str(x[k]); cp=self.present[k][v]; cn=self.absent[k][v]
      np=sum(self.present[k].values()); nn=sum(self.absent[k].values())
      # Include unseen feature values in a categorical Laplace prior.
      vocab=max(2,len(set(self.present[k])|set(self.absent[k])))
      lp+=math.log((cp+1)/(self.pos+vocab)); ln+=math.log((cn+1)/(self.n-self.pos+vocab))
    delta=max(-40,min(40,lp-ln)); return 1/(1+math.exp(-delta))

def main():
 p=argparse.ArgumentParser();p.add_argument('replays',nargs='+',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--holdout',default='113507961');a=p.parse_args()
 allrows=[]; manifests=[]; held=[]
 for path in a.replays:
  raw=path.read_bytes(); r=json.loads(raw); eid=str(r.get('info',{}).get('EpisodeId') or r.get('id') or path.stem); seat=elite_seat(r)
  rows=[]
  for step in r['steps']:
   state=step[seat]; o=state.get('observation') or {}
   if not o: continue
   rows.append((features(o,seat),labels(state.get('action') or {})))
  manifests.append({'episode_id':eid,'elite_name':r['info']['TeamNames'][seat],'seat':seat,'steps':len(rows),'sha256':hashlib.sha256(raw).hexdigest()})
  (held if a.holdout in eid else allrows).extend(rows)
 if not allrows or not held: raise ValueError('need nonempty train and held-out episodes')
 classes=sorted(set().union(*(ys for _,ys in allrows)))
 models={c:BernoulliNB() for c in classes}
 for c,m in models.items():m.fit(allrows,c)
 truth=[]; pred=[]
 per=[]
 for x,ys in held:
  guess={c for c,m in models.items() if m.score(x)>=.5}
  truth.append(ys);pred.append(guess)
 tp=sum(len(y&g) for y,g in zip(truth,pred)); fp=sum(len(g-y) for y,g in zip(truth,pred)); fn=sum(len(y-g) for y,g in zip(truth,pred))
 metrics={'heldout_steps':len(held),'micro_precision':tp/max(1,tp+fp),'micro_recall':tp/max(1,tp+fn),'micro_f1':2*tp/max(1,2*tp+fp+fn),'exact_set_accuracy':sum(y==g for y,g in zip(truth,pred))/len(held),'positive_intent_rate':sum(bool(y) for y in truth)/len(truth)}
 for prefix in ('MKT:','ACT:'):
  t=sum(1 for y,g in zip(truth,pred) for c in y&g if c.startswith(prefix)); fpos=sum(1 for y,g in zip(truth,pred) for c in g-y if c.startswith(prefix)); fneg=sum(1 for y,g in zip(truth,pred) for c in y-g if c.startswith(prefix)); metrics[prefix.lower()+'_f1']=2*t/max(1,2*t+fpos+fneg)
 model={}
 for c,m in models.items():
  model[c]={'prior_positive':m.pos/m.n,'n':m.n,'positive':m.pos,'present':{k:dict(v) for k,v in m.present.items()},'absent':{k:dict(v) for k,v in m.absent.items()}}
 a.out.parent.mkdir(parents=True,exist_ok=True)
 a.out.write_text(json.dumps({'features':'categorical bins; see behavior_extract.py','threshold':.5,'classes':model},sort_keys=True,separators=(',',':'))+'\n')
 report={'provenance':manifests,'train_episodes':[m['episode_id'] for m in manifests if a.holdout not in m['episode_id']],'heldout_episode':a.holdout,'train_steps':len(allrows),'metrics':metrics,'model_sha256':hashlib.sha256(a.out.read_bytes()).hexdigest(),'caveat':'Public replay actions are noisy labels for per-turn intents, not proof of an optimal policy. Only aggregate feature/category counts are written.'}
 a.out.with_suffix('.metrics.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()

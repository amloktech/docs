"""Executed CPU pilot on real public rows, not an LLM or lending decision model."""
import csv,hashlib,json,os,platform,sys,time
from collections import Counter
from datetime import date
from pathlib import Path
os.environ.setdefault('OMP_NUM_THREADS','4')
import numpy as np
import sklearn
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score,average_precision_score,brier_score_loss,log_loss

ROOT=Path(os.environ.get('AMLOK_RESEARCH_WORKSPACE', 'artifacts/research-corpus-20261101'));P=ROOT/'processed';O=ROOT/'outputs'
O.mkdir(parents=True,exist_ok=True)
NUM=['log_amount','guarantee_fraction','initial_rate_pct'];CAT=['program','industry','business_age','rate_type']
def main():
 raw=json.loads((P/'training-cohort.json').read_text());groups=set();parts={};exclusions=Counter()
 for split,years in [('train',range(2010,2014)),('validation',[2014]),('test',[2015,2016])]:
  keep=[];local=set()
  for r in raw:
   if r['year'] not in years:continue
   if r['party_group'] in groups:exclusions['overlap_prior_split']+=1;continue
   if r['status']=='CHGOFF' and not r['chargeoff_date']:exclusions['missing_chargeoff_date']+=1;continue
   try:
    start=date.fromisoformat(r['first_disbursement_date'])
    try:end=start.replace(year=start.year+3)
    except ValueError:end=start.replace(year=start.year+3,day=28)
    charged=date.fromisoformat(r['chargeoff_date']) if r['chargeoff_date'] else None
    if end>date(2026,9,30):exclusions['insufficient_followup']+=1;continue
    if charged and charged<start:exclusions['invalid_chronology']+=1;continue
   except ValueError:exclusions['invalid_dates']+=1;continue
   if not r['amount'] or r['amount']<=0:exclusions['missing_amount']+=1;continue
   r['label']=int(bool(charged and charged<=end));r['split']=split
   r['log_amount']=np.log1p(r['amount']);r['guarantee_fraction']=(r['guaranteed_amount']/r['amount']) if r['guaranteed_amount'] is not None else None
   keep.append(r);local.add(r['party_group'])
  groups.update(local);parts[split]=keep
 assert all(parts.values())
 gsets={k:{r['party_group'] for r in v} for k,v in parts.items()}
 assert not(gsets['train']&gsets['validation'] or gsets['train']&gsets['test'] or gsets['test']&gsets['validation'])
 def arrays(rows):return np.array([[r.get(k) if r.get(k) is not None else np.nan for k in NUM]+[r.get(k) or 'MISSING' for k in CAT] for r in rows],dtype=object),np.array([r['label'] for r in rows])
 X,y=arrays(parts['train']);vx,vy=arrays(parts['validation']);tx,ty=arrays(parts['test'])
 def preprocess():return ColumnTransformer([('num',make_pipeline(SimpleImputer(strategy='median',add_indicator=True),StandardScaler()),list(range(len(NUM)))),('cat',OneHotEncoder(handle_unknown='ignore',sparse_output=False),list(range(len(NUM),len(NUM)+len(CAT))))])
 models={'logistic_regression':LogisticRegression(max_iter=1500,C=1,random_state=42),'gradient_boosted_trees':HistGradientBoostingClassifier(max_iter=120,max_leaf_nodes=15,learning_rate=.08,l2_regularization=1,early_stopping=False,random_state=42)}
 def score(y,p):return {'roc_auc':float(roc_auc_score(y,p)),'average_precision':float(average_precision_score(y,p)),'brier_score':float(brier_score_loss(y,p)),'log_loss':float(log_loss(y,p))}
 results=[];preds={}
 for name,model in models.items():
  started=time.time();pipe=make_pipeline(preprocess(),model);pipe.fit(X,y);p=pipe.predict_proba(tx)[:,1];preds[name]=p
  joblib.dump(pipe,O/(name+'.joblib'))
  result={'model':name,'status':'measured_cpu_pilot','train_seconds':time.time()-started,'validation':score(vy,pipe.predict_proba(vx)[:,1]),'test':score(ty,p)};results.append(result);print(json.dumps(result),flush=True)
 # Borrower-group bootstrap preserves repeated loans within the test set.
 bygroup={}
 for i,r in enumerate(parts['test']):bygroup.setdefault(r['party_group'],[]).append(i)
 keys=list(bygroup);rng=np.random.default_rng(42);auc={k:[] for k in preds};deltas=[]
 for _ in range(300):
  ix=np.concatenate([bygroup[k] for k in rng.choice(keys,len(keys),replace=True)])
  if len(np.unique(ty[ix]))<2:continue
  a={k:roc_auc_score(ty[ix],p[ix]) for k,p in preds.items()}
  for k,v in a.items():auc[k].append(v)
  deltas.append(a['gradient_boosted_trees']-a['logistic_regression'])
 for r in results:r['test']['roc_auc_95pct_group_bootstrap']=np.quantile(auc[r['model']],[.025,.975]).tolist()
 rows=[{**{k:r[k] for k in ['record_id','party_group','split','year','label']},'endpoint':'SBA-reported charge-off within 36 months of first disbursement'} for split in parts for r in parts[split]]
 with (O/'pilot-cohort.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 with (O/'pilot-test-predictions.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['record_id','actual_36m_chargeoff']+list(preds))
  for i,r in enumerate(parts['test']):w.writerow([r['record_id'],int(ty[i])]+[float(p[i]) for p in preds.values()])
 report={'kind':'measured_retrospective_pipeline_pilot','not':'foundation model training, frontier model benchmark, production risk score or proof of AMLOK superiority','outcome':'SBA-reported charge-off within 36 calendar months of first disbursement; not all defaults','source_asof':'2026-09-30','sampling':'deterministic approximately 10 percent by record hash; funded-status records approved 2010-2016','features':NUM+CAT,'split_rule':'2010-2013 train; 2014 validation; 2015-2016 test; exact normalized-name/state groups removed from later splits','split_counts':{k:{'rows':len(v),'positives':sum(r['label'] for r in v),'entity_groups':len(gsets[k])} for k,v in parts.items()},'exclusions':dict(exclusions),'models':results,'paired_auc_delta_95pct_ci':np.quantile(deltas,[.025,.975]).tolist(),'seed':42,'bootstrap_repetitions':300,'limitations':['Current FOIA snapshot does not prove that every predictor has its original underwriting-time value.','Normalized borrower names do not resolve beneficial ownership or all aliases.','US government-guaranteed small-business loans are not representative of Canadian borrowers or all consumer lending.','Registry-reported charge-offs do not capture all delinquency, restructuring or default events.','No bank transaction, card, ecommerce or accounting event-stream training is supported by these rows.','No operational lending decisions should use these pilot predictions.'],'runtime':{'python':sys.version,'sklearn':sklearn.__version__,'numpy':np.__version__,'platform':platform.platform()},'training_data_sha256':hashlib.sha256((P/'training-cohort.json').read_bytes()).hexdigest()}
 (O/'pilot-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['split_counts']),flush=True)

if __name__=='__main__':main()

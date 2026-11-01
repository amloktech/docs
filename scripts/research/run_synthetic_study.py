"""Reproducible synthetic method study. No real borrowers or production model.

Run with Python 3.12 and the adjacent requirements.txt. All model fitting is local.
The target is GENERATED future liquidity stress, not observed credit default.
"""
from pathlib import Path
import argparse, csv, hashlib, json, math, platform, time
from datetime import datetime, timezone
import numpy as np
import torch
from torch import nn
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, log_loss

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ['bank_receipts', 'bank_debt_service', 'processor_sales', 'commerce_orders',
           'accounting_margin', 'invoice_overdue_share', 'payroll_cost']
CONFIG = dict(dataset_seed=74191, entities=1200, months=12, sources=SOURCES,
              split_sizes=[720,240,240], seeds=[17,29,43], width=32, heads=4, layers=2,
              pretrain_epochs=4, supervised_epochs=16, batch_size=72, mask_rate=.20,
              learning_rate=.001, weight_decay=.01, bootstrap_replicates=500)

def generate():
    rng = np.random.default_rng(CONFIG['dataset_seed'])
    n, months = CONFIG['entities'], CONFIG['months']
    trend = rng.normal(0,.20,n)
    debt = rng.uniform(.05,.40,n)
    margin = rng.uniform(.05,.40,n)
    arrears = rng.uniform(0,.45,n)
    scale = rng.lognormal(0,.4,n)
    sequence = np.zeros((n,months,7),dtype=np.float32)
    for m in range(months):
        seasonal = .10*np.sin(2*np.pi*m/12)
        commerce = np.maximum(.05, scale*(1+trend*m/11+seasonal)+rng.normal(0,.06,n))
        prior = sequence[:,max(0,m-1),3] if m else commerce
        sales = .88*commerce + rng.normal(0,.04,n)
        sequence[:,m,0] = .90*prior + rng.normal(0,.08,n)
        sequence[:,m,1] = debt*scale + rng.normal(0,.015,n)
        sequence[:,m,2] = sales
        sequence[:,m,3] = commerce
        sequence[:,m,4] = margin + .15*trend*m/11 + rng.normal(0,.025,n)
        sequence[:,m,5] = np.clip(arrears-.25*trend*m/11+rng.normal(0,.03,n),0,1)
        sequence[:,m,6] = .30*scale+rng.normal(0,.035,n)
    # This equation defines a toy world. It is NOT fitted to Canadian outcomes.
    logit = -1.25 - 3.0*trend + 4.0*(debt-.20) - 4.0*(margin-.20) + 3.5*(arrears-.20)
    probability = 1/(1+np.exp(-logit))
    y = rng.binomial(1,probability).astype(np.float32)
    return sequence,y

def metrics(y,p):
    p=np.clip(p,1e-7,1-1e-7)
    return {'auroc':float(roc_auc_score(y,p)), 'average_precision':float(average_precision_score(y,p)),
            'brier':float(brier_score_loss(y,p)), 'log_loss':float(log_loss(y,p))}

def bootstrap(y,p,seed=191):
    rng=np.random.default_rng(seed); values={k:[] for k in metrics(y,p)}
    for _ in range(CONFIG['bootstrap_replicates']):
        ix=rng.integers(0,len(y),len(y))
        if len(np.unique(y[ix]))<2: continue
        for k,v in metrics(y[ix],p[ix]).items(): values[k].append(v)
    return {k:[float(x) for x in np.quantile(v,[.025,.975])] for k,v in values.items()}

def summarize(x):
    # Identical causal window for every comparator; no labels used in feature construction.
    return np.concatenate([x.mean(1),x[:,-1,:],x[:,-3:,:].mean(1)-x[:,:3,:].mean(1)],axis=1)

class TinyEventTransformer(nn.Module):
    def __init__(self):
        super().__init__(); d=CONFIG['width']
        self.value=nn.Linear(1,d); self.source=nn.Embedding(7,d); self.month=nn.Embedding(12,d)
        self.mask=nn.Parameter(torch.zeros(d))
        layer=nn.TransformerEncoderLayer(d,CONFIG['heads'],d*2,dropout=0,batch_first=True)
        self.encoder=nn.TransformerEncoder(layer,CONFIG['layers'],enable_nested_tensor=False)
        self.reconstruct=nn.Linear(d,1); self.classify=nn.Linear(d,1)
    def forward(self,x,mask=None):
        b=x.shape[0]; flat=x.reshape(b,84,1)
        h=self.value(flat)
        if mask is not None: h=torch.where(mask[:,:,None],self.mask[None,None,:],h)
        h=h+self.source(torch.arange(7).repeat(12))[None,:,:]+self.month(torch.arange(12).repeat_interleave(7))[None,:,:]
        h=self.encoder(h)
        return self.classify(h.mean(1)).squeeze(-1),self.reconstruct(h).squeeze(-1)

def train_transformer(x,y,seed,pretrain):
    torch.manual_seed(seed); model=TinyEventTransformer(); tr=720; va=960
    x=torch.from_numpy(x); y=torch.from_numpy(y)
    opt=torch.optim.AdamW(model.parameters(),lr=CONFIG['learning_rate'],weight_decay=CONFIG['weight_decay'])
    losses=[]
    if pretrain:
        model.train()
        for epoch in range(CONFIG['pretrain_epochs']):
            total=0; count=0
            for ids in torch.randperm(tr).split(CONFIG['batch_size']):
                m=torch.rand(len(ids),84)<CONFIG['mask_rate']; _,rec=model(x[ids],m)
                loss=((rec-x[ids].reshape(-1,84))[m]**2).mean()
                opt.zero_grad();loss.backward();nn.utils.clip_grad_norm_(model.parameters(),1);opt.step()
                total+=float(loss.detach())*len(ids);count+=len(ids)
            losses.append({'stage':'masked_pretraining','epoch':epoch+1,'training_loss':total/count})
    best=float('inf');state=None
    # Full fine-tuning in this small demonstration. No LoRA or language decoder is claimed.
    opt=torch.optim.AdamW(model.parameters(),lr=CONFIG['learning_rate'],weight_decay=CONFIG['weight_decay'])
    for epoch in range(CONFIG['supervised_epochs']):
        model.train(); total=0
        for ids in torch.randperm(tr).split(CONFIG['batch_size']):
            z,_=model(x[ids]); loss=nn.functional.binary_cross_entropy_with_logits(z,y[ids])
            opt.zero_grad();loss.backward();nn.utils.clip_grad_norm_(model.parameters(),1);opt.step()
            total+=float(loss.detach())*len(ids)
        model.eval()
        with torch.no_grad():
            z,_=model(x[tr:va]); val=float(nn.functional.binary_cross_entropy_with_logits(z,y[tr:va]))
        losses.append({'stage':'supervised','epoch':epoch+1,'training_loss':total/tr,'validation_loss':val})
        if val<best:
            best=val;state={k:v.detach().clone() for k,v in model.state_dict().items()}
    model.load_state_dict(state);model.eval()
    with torch.no_grad(): p=torch.sigmoid(model(x)[0]).numpy()
    return model,p,losses

def run(out):
    started=time.perf_counter(); out.mkdir(parents=True,exist_ok=True)
    torch.set_num_threads(2); torch.use_deterministic_algorithms(True)
    x,y=generate(); n=len(y); tr=720;va=960
    np.savez_compressed(out/'synthetic-data.npz',events=x,labels=y)
    # All normalization is estimated on the training split only.
    mean=x[:tr].mean((0,1)); std=x[:tr].std((0,1)); xs=(x-mean)/std
    runs=[];predictions=[];curves={}
    def record(name,seed,p,seconds,parameters=None):
        result={'name':name,'seed':seed,'test':metrics(y[va:],p[va:]),
                'test_ci95':bootstrap(y[va:],p[va:]),'fit_seconds':seconds,'parameters':parameters}
        runs.append(result)
        for i in range(tr,n):
            predictions.append({'entity_id':f'SYN-{i:05d}','split':'validation' if i<va else 'test',
                                'model':name,'seed':seed,'label':int(y[i]),'probability':float(p[i])})
        print(name,seed,json.dumps(result['test']),flush=True)
    for name,cols,method in [('bank_logistic',[0,1],'lr'),('multisource_logistic',list(range(7)),'lr'),
                             ('multisource_boosting',list(range(7)),'gb')]:
        t=time.perf_counter();features=summarize(x[:,:,cols])
        model=make_pipeline(StandardScaler(),LogisticRegression(C=1,max_iter=1000,random_state=17)) if method=='lr' else HistGradientBoostingClassifier(max_iter=100,max_leaf_nodes=7,l2_regularization=1,random_state=17)
        model.fit(features[:tr],y[:tr]);p=model.predict_proba(features)[:,1]
        record(name,17,p,time.perf_counter()-t)
    for pretrain in [False,True]:
        name='transformer_pretrained' if pretrain else 'transformer_scratch'
        for seed in CONFIG['seeds']:
            t=time.perf_counter();model,p,losses=train_transformer(xs.astype(np.float32),y,seed,pretrain)
            record(name,seed,p,time.perf_counter()-t,sum(v.numel() for v in model.parameters()))
            curves[f'{name}-{seed}']=losses
            np.savez_compressed(out/f'{name}-{seed}-weights.npz',**{k:v.detach().numpy() for k,v in model.state_dict().items()},normalization_mean=mean,normalization_std=std)
    with (out/'predictions.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=predictions[0].keys());w.writeheader();w.writerows(predictions)
    cohorts=[]
    for name,start,end,year,institution in [('train',0,tr,2023,'SYN-A'),('validation',tr,va,2024,'SYN-B'),('test',va,n,2025,'SYN-C')]:
        cohorts.append({'split':name,'entities':end-start,'source_month_records':(end-start)*84,
                        'positive_labels':int(y[start:end].sum()),'prevalence':float(y[start:end].mean()),
                        'observation_year':year,'institution':institution})
    report={'study':'AMLOK synthetic structured-event experiment','status':'executed_synthetic_only',
            'report_date':'2026-11-01','executed_at_utc':datetime.now(timezone.utc).isoformat(),
            'configuration':CONFIG,'cohorts':cohorts,'runs':runs,'learning_curves':curves,
            'limitations':['Generated monthly source summaries, not raw transactions or Canadian population data.',
                           'Synthetic institutions and dates are partition labels; this does not test real institutional or temporal shift.',
                           'The label-generating equation is authored and not estimated from any actual borrower outcome.',
                           'A small encoder experiment, not an LLM, production foundation model, graph validation, or competitor benchmark.',
                           'Percentile intervals describe sampling uncertainty within this toy test set only.',
                           'No frontier APIs, commercial competitors, or real lending systems were called.'],
            'environment':{'python':platform.python_version(),'torch':torch.__version__,'numpy':np.__version__,'sklearn':sklearn.__version__,'machine':platform.machine(),'device':'cpu','threads':2},
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'data_sha256':hashlib.sha256((out/'synthetic-data.npz').read_bytes()).hexdigest(),
            'elapsed_seconds':time.perf_counter()-started}
    (out/'synthetic-results.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'artifacts/research-review/experiment')
    a=p.parse_args();run(a.output)

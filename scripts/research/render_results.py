"""Render measured outputs; does not choose or tune models using test results."""
from pathlib import Path
raise SystemExit('This archived generator is retired. Use the public-record research workflow.')

import csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'artifacts/research-review/experiment'
PUBLIC=ROOT/'downloads/research'

def main():
    (ROOT/'research').mkdir(parents=True,exist_ok=True)
    r=json.loads((OUT/'synthetic-results.json').read_text())
    PUBLIC.mkdir(parents=True,exist_ok=True)
    (PUBLIC/'synthetic-results.json').write_text(json.dumps(r,indent=2)+'\n')
    with (OUT/'predictions.csv').open() as f:
        rows=list(csv.DictReader(f))
    def pred(name):
        x=sorted([x for x in rows if x['model']==name and x['seed']=='17' and x['split']=='test'],key=lambda a:a['entity_id'])
        return np.array([float(t['label']) for t in x]),np.array([float(t['probability']) for t in x])
    pairs=[]
    for a,b in [('multisource_logistic','bank_logistic'),('transformer_pretrained','transformer_scratch')]:
        y,pa=pred(a); yb,pb=pred(b);assert np.array_equal(y,yb)
        rng=np.random.default_rng(441);delta=[]
        for _ in range(500):
            ix=rng.integers(0,len(y),len(y))
            if len(np.unique(y[ix]))<2:continue
            delta.append(roc_auc_score(y[ix],pa[ix])-roc_auc_score(y[ix],pb[ix]))
        pairs.append({'comparison':a+' minus '+b,'seed':17,'metric':'AUROC',
                      'difference':float(roc_auc_score(y,pa)-roc_auc_score(y,pb)),
                      'paired_percentile_ci95':[float(z) for z in np.quantile(delta,[.025,.975])],
                      'bootstrap_replicates':500,'scope':'Synthetic test subjects only; no population claim.'})
    (PUBLIC/'paired-comparisons.json').write_text(json.dumps(pairs,indent=2)+'\n')
    runs=[x for x in r['runs'] if x['seed']==17]
    names={'bank_logistic':'Bank-only logistic','multisource_logistic':'Multi-source logistic',
           'multisource_boosting':'Multi-source boosting','transformer_scratch':'Transformer from scratch',
           'transformer_pretrained':'Transformer with pretraining'}
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11})
    fig,ax=plt.subplots(figsize=(10,4.8),layout='constrained')
    for i,x in enumerate(runs):
        v=x['test']['auroc'];lo,hi=x['test_ci95']['auroc']
        ax.errorbar(v,i,xerr=[[v-lo],[hi-v]],fmt='o',color='#052698',capsize=5,markersize=8)
    ax.set_yticks(range(len(runs)),[names[x['name']] for x in runs]);ax.invert_yaxis()
    ax.set_xlim(.45,.9);ax.axvline(.5,color='#94a3b8',linestyle='--');ax.set_xlabel('AUROC; seed 17; 95% subject-bootstrap intervals')
    ax.set_title('Synthetic study only: no real borrower or competitor results',loc='left',fontweight='bold',pad=15)
    ax.grid(axis='x',alpha=.15)
    fig.savefig(ROOT/'images/research/synthetic-comparison.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,4.5),layout='constrained')
    for k,color in [('transformer_scratch-17','#052698'),('transformer_pretrained-17','#007ac2')]:
        q=[x for x in r['learning_curves'][k] if x['stage']=='supervised']
        ax.plot([x['epoch'] for x in q],[x['validation_loss'] for x in q],label=k.replace('-17','').replace('_',' '),color=color)
    ax.set(xlabel='Supervised epoch',ylabel='Validation binary cross-entropy',title='Synthetic validation curves; selection uses validation only')
    ax.legend();ax.grid(alpha=.15);fig.savefig(ROOT/'images/research/synthetic-learning.png',dpi=180);plt.close(fig)
    lines=['---','title: "Initial experiments and measured results"','description: "Executed synthetic training results, uncertainty, and the limits of what they establish."','keywords: ["AMLOK research", "synthetic study"]','sidebarTitle: "Initial results"','mode: "wide"','---','',
           'This page reports an actual local experiment on generated data. It does not report a trained production LLM, Canadian borrower performance, or a comparison against commercial systems. The public-data descriptive study is documented separately under [Canadian data](/research/canadian-data).','',
           '<Warning>Every subject, financial observation, and outcome in this training study is synthetic. The target is authored future liquidity stress, not observed default. Do not use these probabilities or scores for lending.</Warning>','',
           '## Study design','',
           'The fixed-seed generator creates 1,200 fictional subjects with 12 monthly summaries across two bank channels and five business-system channels: processor sales, commerce orders, accounting margin, overdue invoices, and payroll. This yields 100,800 source-month observations. They are not raw transaction records. Latent trend, debt burden, margin, and overdue share determine a probabilistic toy stress label. The equation is in the source code; it was not estimated from Canadian borrowers.','',
           '| Partition | Subjects | Generated observations | Positive labels | Prevalence |', '| --- | ---: | ---: | ---: | ---: |']
    for c in r['cohorts']:lines.append(f"| {c['split'].capitalize()} | {c['entities']} | {c['source_month_records']:,} | {c['positive_labels']} | {c['prevalence']:.3f} |")
    lines += ['', 'Subjects are disjoint. Training, validation, and test have nominal observation years 2023, 2024, and 2025 and different synthetic institution identifiers. The generator uses the same stochastic mechanism across partitions, so this is **not** evidence of robustness to real temporal or institutional shift. No future observations or outcome labels enter input features.','',
              '## Models and selection','',
              'Logistic models use means, last values, and recent-minus-early differences. The bank-only model receives two channels; the multi-source models receive all seven. Boosting uses the same aggregate features. The transformer receives 84 source-month tokens with numeric value, source identity, and month embeddings. It has two layers, width 32, four attention heads, and mean pooling. It is an event encoder, not a text-generating LLM.','',
              f"The model contains **{next(x['parameters'] for x in r['runs'] if x['parameters']):,} parameters** including reconstruction and classification heads. Pretraining masks 20% of numeric tokens for four epochs. Both variants receive 16 supervised epochs with AdamW, learning rate 0.001, weight decay 0.01, batch size 72, gradient clipping at 1, and no dropout. The best epoch is selected using validation loss. Normalization uses only training data. Seeds are 17, 29, and 43. No hyperparameter search or post-hoc selection of the best test seed was performed.", '',
              'The pretraining arm receives additional optimization steps. This experiment does not isolate pretraining from an equal-compute supervised control. No probability recalibration is applied; this study uses validation for checkpoint selection and has no separate calibration partition.','',
              '## Held-out results','',
              'The table reports every run. AP means average precision and depends on the synthetic test prevalence. Lower Brier score and log loss are better. Seed 17 was designated as the display run; the chart does not select the best-performing seed.','',
              '| Model | Seed | AUROC | AP | Brier | Log loss |','| --- | ---: | ---: | ---: | ---: | ---: |']
    for x in r['runs']:
        m=x['test'];lines.append(f"| {names[x['name']]} | {x['seed']} | {m['auroc']:.3f} | {m['average_precision']:.3f} | {m['brier']:.3f} | {m['log_loss']:.3f} |")
    lines += ['', '![Synthetic-only model comparison with bootstrap uncertainty](/images/research/synthetic-comparison.png)','',
              '## Paired comparisons','', '| Contrast, seed 17 | AUROC difference | Paired 95% interval |','| --- | ---: | --- |']
    for p in pairs:
        lines.append(f"| {p['comparison'].replace('_',' ')} | {p['difference']:+.3f} | [{p['paired_percentile_ci95'][0]:+.3f}, {p['paired_percentile_ci95'][1]:+.3f}] |")
    lines += ['', 'Intervals use 500 subject-bootstrap replicates on the same 240 synthetic test subjects. They capture resampling uncertainty conditional on this toy dataset and fitted model, not Canadian population uncertainty, synthetic-generator uncertainty, or variability across institutions. The three training seeds are not three independent test cohorts. These are exploratory engineering results, not a pre-registered real-world efficacy study.','',
              '## Interpretation','',
              'The multi-source logistic baseline has the strongest point estimates in this run. Adding sources helps in a toy world deliberately constructed to contain information in those sources. That is a pipeline demonstration, not empirical proof that borrower-permissioned integrations reduce real credit losses.','',
              'The pretrained transformer does not improve on the from-scratch transformer or the multi-source logistic baseline here. The negative result is retained. It argues for testing strong simple baselines and for separating information gains from model-complexity claims. It does not show that pretraining is ineffective at realistic scale.','',
              '![Synthetic-only validation learning curves](/images/research/synthetic-learning.png)','',
              '## Unmeasured capabilities','',
              'This study does not evaluate bilingual descriptors, entity resolution, graph learning, raw settlements, consumer affordability, loan outcomes, fairness, production monitoring, adversarial documents, or hosted frontier models. Its monthly aggregates omit the hard record-linkage problem. It cannot validate the proposed full architecture.','',
              '## Reproduction','',
              'See the [reproducibility guide](/research/reproducibility), [complete result manifest](/downloads/research/synthetic-results.json), and [paired comparisons](/downloads/research/paired-comparisons.json). The manifest records the actual environment, script digest, data digest, parameter count, epoch losses, fitting times, and execution timestamp. Timings describe this local CPU experiment only.']
    (ROOT/'research/synthetic-study.mdx').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'pairs':pairs,'parameters':next(x['parameters'] for x in r['runs'] if x['parameters'])},indent=2))

if __name__=='__main__': main()

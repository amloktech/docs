"""Render only measured retrieval quantities from the saved result manifest."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
r=json.loads((ROOT/'downloads/research/public-records/retrieval-results.json').read_text())
fig,ax=plt.subplots(figsize=(10,5.1),layout='constrained')
x=np.arange(4);width=.34
labels=['Recall@1','Recall@3','Recall@5','Complete evidence@5']
for offset,method,color in [(-width/2,'tfidf','#9BAFDE'),(width/2,'bm25','#052698')]:
 values=[r['results'][method][str(k)]['recall']*100 for k in [1,3,5]]+[r['results'][method]['5']['complete']*100]
 bars=ax.bar(x+offset,values,width,label={'tfidf':'TF-IDF','bm25':'BM25'}[method],color=color)
 ax.bar_label(bars,labels=[f'{v:.1f}%' for v in values],padding=4,fontsize=10)
ax.set_xticks(x,labels);ax.set_ylim(0,100);ax.set_ylabel('Questions / mean evidence recall (%)')
ax.set_title('Evidence retrieval on real financial reports',loc='left',fontweight='bold',fontsize=17,pad=33)
ax.text(0,1.04,'FinQA: 1,147 questions • 380 source filenames • Fixed lexical baselines',transform=ax.transAxes,color='#475569',fontsize=10)
ax.legend(frameon=False,ncol=2,loc='upper right');ax.spines[['top','right']].set_visible(False)
ax.grid(axis='y',alpha=.13);ax.set_axisbelow(True)
fig.text(.04,-.02,'Measures evidence retrieval, not answer accuracy, credit performance or frontier-model superiority.',fontsize=9,color='#475569')
out=ROOT/'images/research';out.mkdir(parents=True,exist_ok=True)
fig.savefig(out/'public-retrieval.png',dpi=180,bbox_inches='tight',facecolor='white')
fig.savefig(out/'public-retrieval.svg',bbox_inches='tight',facecolor='white')

"""Real FinQA evidence-retrieval baselines. No gold answers enter ranking."""
import hashlib
import json
import math
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'artifacts/research-review/public-records'
OUT = ROOT / 'downloads/research/public-records'
OUT.mkdir(parents=True, exist_ok=True)

def tokens(s):
    return re.findall(r'[a-z0-9]+', s.lower())

def evidence(item):
    # Only source fields. Deliberately ignore retrieved_* and qa.model_input.
    records = [(f'text_{i}', s) for i, s in enumerate(item['pre_text'] + item['post_text'])]
    table = item['table']
    for i, row in enumerate(table):
        cells = [str(x) for x in row]
        if i and table:
            cells = [f'{table[0][j] if j < len(table[0]) else ""}: {v}' for j, v in enumerate(cells)]
        records.append((f'table_{i}', ' ; '.join(cells)))
    return records

def rank(question, records, method):
    texts = [v for _, v in records]
    if method == 'tfidf':
        vectorizer = TfidfVectorizer(tokenizer=tokens, token_pattern=None, lowercase=False)
        vectors = vectorizer.fit_transform(texts)
        scores = (vectors @ vectorizer.transform([question]).T).toarray().ravel()
    elif method == 'bm25':
        docs = [Counter(tokens(v)) for v in texts]
        # Fixed accumulation order avoids hash-seed-dependent floating-point ties.
        query = sorted(set(tokens(question)))
        n = len(docs)
        average = sum(map(lambda d: sum(d.values()), docs)) / max(n, 1)
        df = Counter(t for d in docs for t in d)
        scores = []
        for doc in docs:
            dl = sum(doc.values())
            score = 0.0
            for t in query:
                tf = doc[t]
                if tf:
                    idf = math.log(1 + (n - df[t] + .5) / (df[t] + .5))
                    score += idf * tf * 2.5 / (tf + 1.5 * (.25 + .75 * dl / max(average, 1)))
            scores.append(score)
    else:
        raise ValueError(method)
    # Numerically equivalent scores use the documented evidence-ID tie break.
    indices = sorted(range(len(records)), key=lambda i: (-round(float(scores[i]),12), records[i][0]))
    return [records[i][0] for i in indices]

def metric(ranked, gold, k):
    selected = set(ranked[:k])
    return {'recall': len(selected & gold) / len(gold), 'complete': float(gold <= selected)}

def run():
    outputs = []
    for item in json.loads((DATA / 'finqa-test.json').read_text()):
        records = evidence(item)
        question = item['qa']['question']
        rankings = {name:rank(question, records, name) for name in ['bm25','tfidf']}
        # Scoring starts only after predictions exist.
        gold = set(item['qa']['gold_inds'])
        unknown = gold - {k for k, _ in records}
        if not gold or unknown:
            raise ValueError(f'Invalid gold IDs: {item["id"]}, {unknown}')
        outputs.append({'id':item['id'],'document':item['filename'],
                        'gold_ids':sorted(gold),
                        'predictions':{m:r[:5] for m,r in rankings.items()},
                        'metrics':{m:{str(k):metric(r,gold,k) for k in [1,3,5]} for m,r in rankings.items()}})
    summary = {'study':'FinQA published test-split evidence retrieval',
               'executed_at':datetime.now(timezone.utc).isoformat(),
               'evidence_class':'real_public_financial_documents',
               'task':'rank supplied text sentences and table rows; not answer generation or OCR',
               'configuration':{'bm25_k1':1.5,'bm25_b':.75,'k':[1,3,5],
                                'fitting':'document-local unsupervised vocabulary only',
                                'test_tuning':'none; one configuration per baseline'},
               'examples':len(outputs),'documents':len({x['document'] for x in outputs}),
               'source_sha256':hashlib.sha256((DATA/'finqa-test.json').read_bytes()).hexdigest(),
               'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'results':{}, 'frontier_runs':[], 'amlok_foundation_model_runs':[]}
    for model in ['bm25','tfidf']:
        summary['results'][model]={str(k):{metric_name:float(np.mean([x['metrics'][model][str(k)][metric_name] for x in outputs])) for metric_name in ['recall','complete']} for k in [1,3,5]}
    # Paired bootstrap by source document, preserving questions within each document.
    groups={doc:[i for i,x in enumerate(outputs) if x['document']==doc] for doc in sorted({x['document'] for x in outputs})}
    all_groups=list(groups.values())
    rng=np.random.default_rng(20261101)
    delta=np.array([x['metrics']['bm25']['5']['recall']-x['metrics']['tfidf']['5']['recall'] for x in outputs])
    sums=np.array([delta[g].sum() for g in all_groups]);counts=np.array([len(g) for g in all_groups])
    boots=[]
    for _ in range(2000):
        draw=rng.integers(0,len(all_groups),len(all_groups))
        boots.append(float(sums[draw].sum()/counts[draw].sum()))
    summary['paired_comparison']={'metric':'recall_at_5','difference':'bm25 minus tfidf',
                                 'point':float(delta.mean()),'ci95':np.quantile(boots,[.025,.975]).tolist(),
                                 'resampling_unit':'source filename','replicates':2000,'seed':20261101,
                                 'scope':'conditional on this corpus; not independent institutions or Canadian borrowers'}
    (OUT/'retrieval-predictions.json').write_text(json.dumps(outputs,indent=2)+'\n')
    summary['predictions_sha256']=hashlib.sha256((OUT/'retrieval-predictions.json').read_bytes()).hexdigest()
    (OUT/'retrieval-results.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    run()

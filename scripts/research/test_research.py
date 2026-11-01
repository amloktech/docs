"""Validate delivered measured results and adversarial evidence fixtures."""
from pathlib import Path
import csv,hashlib,json,unittest
from decimal import Decimal
import numpy as np
from sklearn.metrics import roc_auc_score,average_precision_score,brier_score_loss
from evidence_checks import as_of,cash_proxy,settlement

ROOT=Path(__file__).resolve().parents[2]

class EvidenceTests(unittest.TestCase):
    def row(self,**kw):
        x=dict(workspace='A',source='bank',id='1',version=1,event_time='2025-01-01T00:00:00+00:00',known_at='2025-01-02T00:00:00+00:00',amount='100.00');x.update(kw);return x
    def test_late_knowledge_is_excluded(self):
        self.assertEqual(as_of([self.row(known_at='2025-02-01T00:00:00+00:00')],'A','2025-01-31T00:00:00+00:00'),[])
    def test_other_workspace_is_excluded(self):
        self.assertEqual(as_of([self.row(workspace='B')],'A','2025-01-31T00:00:00+00:00'),[])
    def test_future_event_is_excluded(self):
        self.assertEqual(as_of([self.row(event_time='2025-03-01T00:00:00+00:00')],'A','2025-01-31T00:00:00+00:00'),[])
    def test_duplicate_delivery_not_double_counted(self):
        r=self.row();self.assertEqual(len(as_of([r,r],'A','2025-01-31T00:00:00+00:00')),1)
    def test_correction_not_retroactive(self):
        old=self.row();new=self.row(version=2,known_at='2025-02-01T00:00:00+00:00',amount='80.00')
        self.assertEqual(as_of([old,new],'A','2025-01-31T00:00:00+00:00')[0]['amount'],'100.00')
        self.assertEqual(as_of([old,new],'A','2025-02-02T00:00:00+00:00')[0]['amount'],'80.00')
    def test_conflicting_same_version_fails(self):
        with self.assertRaises(ValueError):as_of([self.row(),self.row(amount='90.00')],'A','2025-01-31T00:00:00+00:00')
    def test_older_conflict_is_not_hidden_by_new_version(self):
        with self.assertRaises(ValueError):as_of([self.row(version=2),self.row(),self.row(amount='90.00')],'A','2025-01-31T00:00:00+00:00')
    def test_checkpoint_reproduces_predictions(self):
        import torch
        from run_synthetic_study import TinyEventTransformer
        torch.set_num_threads(2)
        directory=ROOT/'artifacts/research-review/experiment'
        with (directory/'predictions.csv').open() as f:rows=list(csv.DictReader(f))
        x=np.load(directory/'synthetic-data.npz')['events'][960:]
        for variant in ['transformer_scratch','transformer_pretrained']:
            for seed in [17,29,43]:
                with np.load(directory/f'{variant}-{seed}-weights.npz') as saved:
                    model=TinyEventTransformer()
                    model.load_state_dict({k:torch.from_numpy(saved[k]) for k in model.state_dict()})
                    normalized=(x-saved['normalization_mean'])/saved['normalization_std']
                model.eval()
                with torch.no_grad():p=torch.sigmoid(model(torch.from_numpy(normalized))[0]).numpy()
                expected=[float(z['probability']) for z in rows if z['model']==variant and int(z['seed'])==seed and z['split']=='test']
                np.testing.assert_allclose(p,expected,rtol=1e-6,atol=1e-6)
    def test_cash_proxy_and_stress(self):
        self.assertEqual(cash_proxy(100000,70000,15000),Decimal('2'))
        self.assertEqual(cash_proxy(80000,70000,15000),Decimal(2)/3)
    def test_missing_or_zero_debt_not_infinite(self):
        self.assertIsNone(cash_proxy(100000,70000,0));self.assertIsNone(cash_proxy(100000,70000,None))
    def test_net_payout_differs_from_net_sales(self):
        self.assertEqual(settlement('13560','560','350','600'),Decimal('12050'))
        self.assertNotEqual(settlement('13560','560','350','600'),Decimal('11500'))
    def test_saved_predictions_recompute(self):
        r=json.loads((ROOT/'downloads/research/synthetic-results.json').read_text())
        with (ROOT/'artifacts/research-review/experiment/predictions.csv').open() as f:
            rows=list(csv.DictReader(f))
        for run in r['runs']:
            x=[z for z in rows if z['split']=='test' and z['model']==run['name'] and int(z['seed'])==run['seed']]
            self.assertEqual(len(x),240);self.assertEqual(len({z['entity_id'] for z in x}),240)
            y=np.array([int(z['label']) for z in x]);p=np.array([float(z['probability']) for z in x])
            self.assertTrue(np.isfinite(p).all());self.assertTrue(((p>=0)&(p<=1)).all())
            self.assertAlmostEqual(roc_auc_score(y,p),run['test']['auroc'],places=6)
            self.assertAlmostEqual(average_precision_score(y,p),run['test']['average_precision'],places=6)
            self.assertAlmostEqual(brier_score_loss(y,p),run['test']['brier'],places=6)
    def test_dataset_manifest_and_scope(self):
        r=json.loads((ROOT/'downloads/research/synthetic-results.json').read_text())
        p=ROOT/'artifacts/research-review/experiment/synthetic-data.npz'
        self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),r['data_sha256'])
        d=np.load(p);self.assertEqual(d['events'].shape,(1200,12,7));self.assertEqual(r['status'],'executed_synthetic_only')
        self.assertEqual(sum(x['source_month_records'] for x in r['cohorts']),100800)
    def test_public_data_recomputed(self):
        raw=(ROOT/'artifacts/research-review/boc-fx-2025.json').read_bytes()
        s=json.loads((ROOT/'downloads/research/public-data-summary.json').read_text())
        x=[float(r['FXUSDCAD']['v']) for r in json.loads(raw)['observations'] if 'FXUSDCAD' in r]
        self.assertEqual(hashlib.sha256(raw).hexdigest(),s['sha256']);self.assertEqual(len(x),s['count'])
        self.assertAlmostEqual(sum(x)/len(x),s['arithmetic_mean'],places=12)

if __name__=='__main__':unittest.main(verbosity=2)

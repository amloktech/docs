"""Validate observed-source lineage and independently recompute saved benchmark metrics."""
import copy
import hashlib
import json
import math
import unittest
from pathlib import Path

from benchmark_public_evidence import evidence,rank

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'artifacts/research-review/public-records'
OUT=ROOT/'downloads/research/public-records'

def read(name):return json.loads((OUT/name).read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

class PublicResearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=read('acquisition-manifest.json')
        cls.summary=read('source-analysis.json')
        cls.results=read('retrieval-results.json')
        cls.predictions=read('retrieval-predictions.json')
        cls.index=[json.loads(x) for x in (OUT/'record-index.jsonl').read_text().splitlines()]

    def test_acquired_file_integrity_and_scope(self):
        for row in self.manifest:
            if row['status']==200:
                path=DATA/row['file']
                self.assertEqual(sha(path),row['sha256'],row['file'])
                self.assertEqual(path.stat().st_size,row['bytes'])
                self.assertIn(row['scope'],['complete_file','byte_prefix_not_random_sample'])
        prefix=next(x for x in self.manifest if x['file']=='sba-prefix.csv')
        self.assertEqual(prefix['scope'],'byte_prefix_not_random_sample')
        self.assertTrue((DATA/prefix['file']).read_bytes().endswith(b'\n'))

    def test_source_register_does_not_imply_downloads(self):
        register=read('source-register.json')['sources']
        self.assertEqual(len(register),26)
        self.assertEqual(len({r['source_id'] for r in register}),len(register))
        files={x['file'] for x in self.manifest}
        for row in register:
            self.assertTrue(set(row['acquisition_files'])<=files)
            self.assertTrue(row['record_unit'])
            self.assertTrue(row['verified_scope'])
        self.assertEqual(next(x for x in register if x['source_id']=='berka')['status'],'unavailable')

    def test_counts_keep_their_source_units(self):
        s=self.summary
        self.assertEqual(sum(x['loans'] for x in s['csbfp']['years']),214158)
        self.assertEqual(s['csbfp']['annual_observations'],27)
        self.assertEqual(s['csbfp']['individual_loan_rows_in_file'],0)
        self.assertEqual(sum(s['edc']['products'].values()),s['edc']['visible_table_rows'])
        self.assertEqual(sum(s['iq']['types'].values()),1014)
        self.assertEqual(s['sba']['sample_rows'],548)
        self.assertEqual(s['bce']['reconciliation_residual'],0)
        self.assertEqual(s['record_index']['observations'],len(self.index))
        self.assertEqual(len(self.index),1047)

    def test_record_index_ids_and_locators(self):
        manifest={r['file']:r for r in self.manifest}
        self.assertEqual(len({r['record_id'] for r in self.index}),len(self.index))
        for row in self.index:
            self.assertEqual(row['source_sha256'],manifest[row['source_file']]['sha256'])
            identity=json.dumps([row['source_sha256'],row['locator']],sort_keys=True,ensure_ascii=False)
            self.assertEqual(row['record_id'],'pub_'+hashlib.sha256(identity.encode()).hexdigest()[:24])
            self.assertFalse(row['independent_outcome'])
            self.assertEqual(row['facility_deduplication'],'not_adjudicated')
        self.assertEqual(sha(OUT/'record-index.jsonl'),self.summary['record_index']['sha256'])

    def test_result_artifact_digests(self):
        self.assertEqual(sha(DATA/'finqa-test.json'),self.results['source_sha256'])
        self.assertEqual(sha(ROOT/'scripts/research/benchmark_public_evidence.py'),self.results['script_sha256'])
        self.assertEqual(sha(OUT/'retrieval-predictions.json'),self.results['predictions_sha256'])

    def test_every_question_and_gold_id(self):
        original=json.loads((DATA/'finqa-test.json').read_text())
        self.assertEqual(len(self.predictions),1147)
        self.assertEqual(len({x['id'] for x in self.predictions}),1147)
        self.assertEqual({x['id'] for x in self.predictions},{x['id'] for x in original})
        self.assertEqual(len({x['document'] for x in self.predictions}),380)
        saved={x['id']:x for x in self.predictions}
        for item in original:
            row=saved[item['id']]
            candidates={k for k,_ in evidence(item)}
            self.assertEqual(set(row['gold_ids']),set(item['qa']['gold_inds']))
            self.assertTrue(set(row['gold_ids'])<=candidates)
            for predicted in row['predictions'].values():
                self.assertEqual(len(set(predicted)),len(predicted))
                self.assertTrue(set(predicted)<=candidates)

    def test_independently_recomputed_metrics(self):
        for method in ['bm25','tfidf']:
            for k in [1,3,5]:
                recall=[];complete=[]
                for row in self.predictions:
                    gold=set(row['gold_ids']);selected=set(row['predictions'][method][:k])
                    recall.append(len(gold&selected)/len(gold));complete.append(float(gold<=selected))
                    self.assertAlmostEqual(recall[-1],row['metrics'][method][str(k)]['recall'])
                    self.assertEqual(complete[-1],row['metrics'][method][str(k)]['complete'])
                self.assertAlmostEqual(sum(recall)/len(recall),self.results['results'][method][str(k)]['recall'])
                self.assertAlmostEqual(sum(complete)/len(complete),self.results['results'][method][str(k)]['complete'])
        delta=self.results['results']['bm25']['5']['recall']-self.results['results']['tfidf']['5']['recall']
        self.assertAlmostEqual(delta,self.results['paired_comparison']['point'])
        low,high=self.results['paired_comparison']['ci95']
        self.assertLess(low,delta);self.assertGreater(high,delta)

    def test_gold_and_answer_mutations_cannot_change_ranking(self):
        original=json.loads((DATA/'finqa-test.json').read_text())
        for item in original[::57]:
            modified=copy.deepcopy(item)
            modified['qa']={'question':item['qa']['question'],'answer':'POISON','program':'POISON','gold_inds':{'poison':'POISON'},'model_input':'POISON'}
            modified['retrieved_text']='POISON';modified['retrieved_table']='POISON'
            self.assertEqual(evidence(item),evidence(modified))
            saved=next(x for x in self.predictions if x['id']==item['id'])
            for method in ['bm25','tfidf']:
                self.assertEqual(rank(modified['qa']['question'],evidence(modified),method)[:5],saved['predictions'][method])

    def test_unrun_comparisons_are_not_filled(self):
        self.assertEqual(self.results['frontier_runs'],[])
        self.assertEqual(self.results['amlok_foundation_model_runs'],[])
        self.assertEqual(set(self.results['results']),{'bm25','tfidf'})

    def test_public_outputs_exclude_local_paths_and_private_rows(self):
        for name in ['source-register.json','acquisition-manifest.json','record-index.jsonl']:
            s=(OUT/name).read_text()
            self.assertNotIn('/Users/',s)
            self.assertNotIn('BorrStreet',s)
            self.assertNotIn('first_record',s)
        for row in self.index:
            self.assertNotIn('name',row)
            self.assertNotIn('address',row)

if __name__=='__main__':unittest.main(verbosity=2)

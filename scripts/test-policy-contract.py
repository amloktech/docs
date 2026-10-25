"""Cross-check the new contract decisions and reject invalid monetary/workspace inputs."""
from pathlib import Path
from copy import deepcopy
import json,hashlib
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parent.parent
spec=json.loads((ROOT/'openapi/amlok-v1.json').read_text())
index=json.loads((ROOT/'data/api-reference-index.json').read_text())
ops={x['id']:x for x in index}
checks=0
def check(value,message):
 global checks
 assert value,message
 checks+=1
def valid(name,value):
 return Draft202012Validator({'$ref':'#/components/schemas/'+name,'components':spec['components']}).is_valid(value)
baselines=json.loads((ROOT/'data/baseline-api-index.json').read_text())
check(len(baselines)==4,'Baseline list/retrieve coverage')
for row in baselines:
 operation=spec['paths'][row['path']]['get']
 check(row['method']=='GET','Baseline mutation exposed')
 check(operation['security']==[{'BearerAuth':[]}],'Baseline not authenticated')
 check('workspace_id' not in [x['name'] for x in operation['parameters']],'Caller can override workspace')
 check('402' not in operation['responses'],'Read charges credits')
 records=row['response']['data']
 if isinstance(records,list):
  check(any(x['name']=='subject_id' and x['required'] for x in operation['parameters']),'List is not subject-bound')
 else:records=[records]
 check(all(x['workspace_id']=='wsp_example' and x['subject_id']=='biz_example' for x in records),'Baseline example crosses scope')
baseline=ops['BB002']['response']['data'];manifest=ops['BM002']['response']['data']
check(baseline['snapshot_id']==ops['EP150']['request']['baseline_snapshot_id'],'Monitor bootstrap identifier mismatch')
check(baseline['input_manifest_id']==manifest['id']==ops['EP148']['request']['input_manifest_id'],'Frozen evidence identifier mismatch')
request=ops['EP148']['request']
check(manifest['window_start']<=request['window_start']<request['window_end']<=manifest['window_end'],'Calculation window outside manifest')
check('workspace' in spec['components']['securitySchemes']['BearerAuth']['description'],'API key scope missing workspace')
workflow=spec['paths']['/v1/workflow-runs']['post']
check(workflow['responses']['402']['$ref'].endswith('Error402'),'No insufficient-credit error')
error=spec['components']['responses']['Error402']['content']['application/json']['examples']['insufficient_credits']['value']
check(error['error']['retryable'] is False,'Insufficient funds automatically retried')
for endpoint in ['/v1/billing/credits','/v1/billing/usage','/v1/billing/rate-card']:
 check('402' not in spec['paths'][endpoint]['get']['responses'],'Credit pause blocks reports')
application=deepcopy(ops['EP146']['request'])
for bad in ['-1.00','0.00','1.001']:
 bad_request=deepcopy(application);bad_request['requested_amount']['amount']=bad
 check(not valid('EP146Request',bad_request),'Invalid requested loan amount '+bad)
for bad in [-1,0]:
 check(not valid('EP146Request',{**application,'requested_term_months':bad}),'Invalid requested loan term')
for file in ROOT.rglob('*.mdx'):
 if any(x in file.parts for x in ['node_modules','artifacts','.mintlify']):continue
 text=file.read_text()
 check(not any(x in text for x in ['Didit','Baselayer','Natomi','SUP-01','SUP-02','SUP-03','/integrations/supplemental-providers']),'Internal provider published: '+str(file))
 check(chr(0x2014) not in text,'Em dash: '+str(file))
 check(',.00' not in text,'Malformed price: '+str(file))
 check('records_per_analysis' not in text,'Old record limit naming: '+str(file))
backup=Path('/private/tmp/amlok-review-decisions-before/data/api-contract-source.json')
if backup.exists():check(backup.read_bytes()==(ROOT/'data/api-contract-source.json').read_bytes(),'Source workbook snapshot changed')
print(json.dumps({'checks':checks,'baselineEndpoints':len(baselines),'scope':'Documentation schemas and examples, not a running backend.'}))

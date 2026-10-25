"""Contract regression tests: sparse responses, cancellation cutoff, reproducible reporting."""
from pathlib import Path
from copy import deepcopy
import json
from jsonschema import Draft202012Validator, FormatChecker
ROOT=Path(__file__).resolve().parent.parent
spec=json.loads((ROOT/'openapi/amlok-v1.json').read_text())
index=json.loads((ROOT/'data/reporting-api-index.json').read_text())
ops={(x['path'],x['method']):x for x in index}
checks=0
def check(value,message):
 global checks
 assert value,message
 checks+=1
def valid(name,value):
 return Draft202012Validator({'$ref':'#/components/schemas/'+name,'components':spec['components']},format_checker=FormatChecker()).is_valid(value)
def response(path):return ops[(path,'GET')]['response']['data']
account=response('/v1/billing/account')
check(account['processing_cutoff']=='immediate_on_cancellation','Wrong cancellation cutoff')
cancelled={**account,'status':'cancellation_pending','cancellation_requested_at':'2026-10-23T14:00:00Z','scheduled_closure_at':'2026-11-01T00:00:00Z'}
check(valid('BillingAccount',cancelled),'Cancellation-pending account not representable')
check(not valid('BillingAccount',{**account,'processing_cutoff':'after_closure'}),'Old cutoff accepted')
snapshot=response('/v1/billing/snapshot')
for path in ['/v1/billing/credits','/v1/billing/usage','/v1/billing/consumption','/v1/billing/rate-card','/v1/billing/rate-cards','/v1/billing/funding','/v1/billing/credit-holds','/v1/billing/credit-ledger','/v1/billing/credit-ledger/{id}']:
 op=spec['paths'][path]['get']
 check(any(p['name']=='snapshot_id' and not p['required'] for p in op['parameters']),'Missing reusable snapshot '+path)
 check('X-Billing-Snapshot-ID' in op['responses']['200']['headers'],'Empty list cannot expose snapshot '+path)
 records=response(path);records=records if isinstance(records,list) else [records]
 check(all(row['snapshot_id']==snapshot['id'] and row['workspace_id']==snapshot['workspace_id'] for row in records),'Cross-snapshot example '+path)
 check('402' not in op['responses'],'Unfunded customer cannot read report')
rate=response('/v1/billing/rate-cards/{id}')
check(rate['id']==response('/v1/billing/usage/{id}')['rate_card_id'],'Historical pricing cannot be resolved')
for entry in rate['rates']:check(entry['workload_limits']['record_counting_rule']=='distinct_record_versions','Updated versions not counted')
request=deepcopy(ops[('/v1/billing/reports','POST')]['request'])
for kind,basis in [('usage','posted_at'),('ledger','posted_at'),('statement','posted_at'),('funding','initiated_at'),('holds','created_at')]:
 check(valid('CreateBillingReport',{**request,'report_type':kind,'time_basis':basis}),'Valid export rejected '+kind)
 for bad_basis in {'occurred_at','posted_at','initiated_at','created_at'}-{basis}-({'occurred_at'} if kind=='usage' else set()):
  check(not valid('CreateBillingReport',{**request,'report_type':kind,'time_basis':bad_basis}),'Invalid export basis accepted '+kind)
check(valid('CreateBillingReport',{**request,'time_basis':'occurred_at','filters':{'status':'pending'}}),'Pending event report rejected')
check(not valid('CreateBillingReport',{**request,'time_basis':'posted_at','filters':{'status':'pending'}}),'Pending usage claims posting date')
check(not valid('CreateBillingReport',{**request,'report_type':'ledger','filters':{'product':'signal'}}),'Filtered ledger export can masquerade as full reconciliation')
check(not valid('CreateBillingReport',{**request,'workspace_id':'someone_else'}),'Workspace override accepted')
for path,methods in spec['paths'].items():
 for method,op in methods.items():
  if op['operationId'].startswith('EP') and op['operationId']!='EP145' and method!='get':
   check('409' in op['responses'] and 'cancellation' in op['description'],'Cancellation rejection missing '+path)
  media=op['responses'].get('200',{}).get('content',{}).get('application/json',{})
  if 'projected' not in media.get('examples',{}):continue
  schema={'components':spec['components'],**media['schema']}
  validator=Draft202012Validator(schema)
  sparse=deepcopy(media['examples']['projected']['value'])
  check(validator.is_valid(sparse),'Documented projection invalid '+path)
  row=sparse['data'][0] if isinstance(sparse['data'],list) else sparse['data']
  del row['id']
  check(not validator.is_valid(sparse),'Projection loses mandatory identity '+path)
canonical=spec['components']['schemas']['BankTransaction']
check('account_id' in canonical['required'],'Canonical schema relaxed')
check('account_id' not in spec['components']['schemas']['BankTransactionRead']['required'],'Projection still requires domain fields')
for file in ['pricing/refunds-and-payouts.mdx','pricing/contract-terms.mdx','pricing/credits-and-billing.mdx','security/privacy.mdx','support/account-management.mdx']:
 text=(ROOT/file).read_text()
 check('stop immediately' in text,'Cutoff absent '+file)
 check('after account closure' not in text,'Obsolete cutoff '+file)
backup=Path('/private/tmp/amlok-enterprise-reporting-before')
check((backup/'data/api-contract-source.json').read_bytes()==(ROOT/'data/api-contract-source.json').read_bytes(),'Workbook changed')
old=json.loads((backup/'openapi/amlok-v1.json').read_text())
for path,methods in old['paths'].items():
 for method,op in methods.items():check(spec['paths'][path][method]['operationId']==op['operationId'],'Operation ID changed')
out={'checks':checks,'reportingOperations':len(index),'scope':'Documentation contract and examples only; no backend or payment execution.'}
(ROOT/'artifacts/enterprise-reporting-validation.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))

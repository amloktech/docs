"""Exercise product boundaries and reconcile the published multi-report fixture."""
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
import csv
import hashlib
import io
import json
import re
from jsonschema import Draft202012Validator, FormatChecker

ROOT=Path(__file__).resolve().parent.parent
spec=json.loads((ROOT/'openapi/amlok-v1.json').read_text())
schemas=spec['components']['schemas']
index=json.loads((ROOT/'data/api-reference-index.json').read_text())
by_id={item['id']:item for item in index}
checks=0
def check(value,message):
    global checks
    assert value,message
    checks+=1
def valid(schema,value):
    return Draft202012Validator({'$ref':'#/components/schemas/'+schema,'components':spec['components']},format_checker=FormatChecker()).is_valid(value)
def data(path,method='GET'):
    return next(x['response']['data'] for x in index if x['path']==path and x['method']==method)

# An endpoint cannot silently become an independently purchased service.
context={'product':'insights','workflow_run_id':'wfr_example'}
check(valid('ProcessingContext',context),'Insights parent rejected')
check(valid('ProcessingContext',{'product':'signal','monitoring_period_id':'period_example'}),'Signal parent rejected')
for bad in [{},{'product':'verification'},dict(context,monitoring_period_id='other'),{'product':'signal','workflow_run_id':'wfr_example'}]:
    check(not valid('ProcessingContext',bad),'Ambiguous or standalone context accepted')
for oid in ['EP142','EP143','EP148']:
    request=deepcopy(by_id[oid]['request'])
    check(valid(oid+'Request',request),oid+' valid request rejected')
    request.pop('processing_context')
    check(not valid(oid+'Request',request),oid+' can launch without product scope')
    response=by_id[oid]['response']['data']
    check(response['processing_context']==context,'Stage cannot be traced to parent')
root=by_id['EP147']['request']
check(not valid('EP147Request',{**root,'processing_context':context}),'Root underwriting doubles as included stage')
for kind in ['verify','monitor','investigate']:
    candidate={**root,'workflow_type':kind}
    check(not valid('EP147Request',candidate),'Unscoped child workflow accepted')
    check(valid('EP147Request',{**candidate,'processing_context':context}),'Authorized child rejected')

# All financial representations describe the same funding and two product charges.
usage=data('/v1/billing/usage');ledger=data('/v1/billing/credit-ledger');balance=data('/v1/billing/credits')
by_usage={r['id']:r for r in usage};by_ledger={r['id']:r for r in ledger}
running=Decimal('0.00')
for row in sorted(ledger,key=lambda r:r['sequence']):
    running+=Decimal(row['amount'])
    check(running==Decimal(row['balance_after']),'Ledger running balance diverges')
check(running==Decimal(balance['available_credits']),'Available credits diverge from ledger')
check(sum(Decimal(r['amount']) for r in usage)==Decimal(balance['spent_credits']),'Spent credits diverge from usage')
check(data('/v1/billing/funding')[0]['ledger_entry_id'] in by_ledger,'Funding has no ledger entry')
for row in usage:
    debit=by_ledger[row['ledger_entry_id']]
    check(debit['movement_id']==row['id'] and Decimal(debit['amount'])==-Decimal(row['amount']),'Charge/ledger mismatch')
    check(Decimal(row['quantity'])*Decimal(row['unit_rate'])==Decimal(row['amount']),'Charge math mismatch')
    check(not valid('BillingUsage',{**row,'quantity':'2'}),'Duplicate units allowed in one subject charge')
    check(not valid('BillingUsage',{**row,'product':'standalone'}),'Standalone usage accepted')
    check(not valid('BillingUsage',{**row,'unit':'active_account_month' if row['product']=='insights' else 'completed_underwriting'}),'Product/unit mismatch accepted')
period=data('/v1/monitoring-periods/{id}')
signal=by_usage[period['billing_usage_id']]
check(period['charged_at']==signal['occurred_at']==period['period_start'],'Signal does not charge at month start')
check(period['baseline_snapshot_id']==signal['risk_snapshot_id'],'Signal baseline audit link mismatch')
check(period['workload_id'] in {w['id'] for w in data('/v1/workloads')},'Missing monthly workload fixture')
for rate in data('/v1/billing/rate-card')['rates']:
    check(rate['billing_timing']==('month_start_or_first_activation' if rate['product']=='signal' else 'successful_output_completion'),'Wrong billing trigger')
    wrong='successful_output_completion' if rate['product']=='signal' else 'month_start_or_first_activation'
    check(not valid('BillingRate',{**rate,'billing_timing':wrong}),'Wrong billing trigger accepted')
for retired in ['total_held','total_posted','available_for_usage','pending_funding']:
    check(not valid('BillingCreditBalance',{**balance,retired:'0.00'}),'Removed credit category accepted')
check('/v1/billing/credit-holds' not in spec['paths'],'Credit hold endpoint remains')

# A full export is schema-valid, reconciles to the API, and its CSV preserves decimal text.
for kind in ['usage','ledger','statement','funding']:
    value=json.loads((ROOT/f'downloads/report-examples/{kind}.json').read_text())
    schema=json.loads((ROOT/f'downloads/report-schemas/{kind}.schema.json').read_text())
    check(Draft202012Validator(schema,format_checker=FormatChecker()).is_valid(value),kind+' invalid standalone export')
    raw=(ROOT/f'downloads/report-examples/{kind}.csv').read_bytes()
    check(b'\r\n' in raw and not raw.startswith(b'\xef\xbb\xbf'),'CSV encoding contract violated')
    rows=list(csv.DictReader(io.StringIO(raw.decode())))
    check(len(rows)==len(value['rows']),'CSV/JSON row mismatch')
    for a,b in zip(rows,value['rows']):
        for key,item in b.items():
            check(a[key]==('' if item is None else str(item)),kind+' CSV value diverges '+key)
        check(a['export_snapshot_id']==value['snapshot_id'],'CSV snapshot mismatch')
download=data('/v1/billing/reports/{id}/download-link','POST')
check(download['sha256']==hashlib.sha256((ROOT/'downloads/report-examples/usage.csv').read_bytes()).hexdigest(),'Download digest mismatch')
check(data('/v1/billing/reports/{id}')['row_count']==len(usage),'Ready report row count mismatch')

# Frozen membership and resumable empty change pages are complete contracts.
entries=data('/v1/input-manifests/{id}/entries');manifest=data('/v1/input-manifests/{id}')
content=''.join(json.dumps(row,sort_keys=True,ensure_ascii=False,separators=(',',':'))+'\n' for row in entries)
check(hashlib.sha256(content.encode()).hexdigest()==manifest['sha256'],'Manifest hash mismatch')
check(len(entries)==manifest['record_count'],'Manifest membership count mismatch')
changes=next(x['response'] for x in index if x['path']=='/v1/changes')
empty=deepcopy(changes);empty['data']=[]
check(valid('ChangePage',empty),'Empty poll cannot preserve a durable cursor')
empty.pop('resume_cursor')
check(not valid('ChangePage',empty),'Empty poll can lose the resume position')
for state in ['waiting_for_credits','blocked_by_limit','cancelled']:
    check(valid('Enum_workflow_status',state),'Missing processing lifecycle state')
check(not valid('Enum_workflow_status','waiting_for_approval'),'Removed action approval remains')
for enum in ['Enum_search_status','Enum_verification_status','Enum_sync_status']:
    check(valid(enum,'cancelled'),'Cancellation cannot terminate a processing stage')
for file in ['data-model/field-dictionary.mdx','data-model/enumerations.mdx']:
    content=(ROOT/file).read_text()
    for removed in ['document.legal_hold','workflow_run.approval_required','waiting_for_approval']:
        check(removed not in content,'Obsolete policy in data dictionary')
worked=(ROOT/'api-reference/examples.mdx').read_text()
blocks=[json.loads(m) for m in re.findall(r'```json\n(.*?)\n```',worked,re.S)]
for n,oid in [(0,'EP142'),(4,'EP143'),(9,'EP147')]:
    check(valid(oid+'Request',blocks[n]),'Worked request is invalid')
result={'checks':checks,'operations':len(index),'scope':'Schemas, examples, cross-report arithmetic and generated documentation; no backend executed.'}
(ROOT/'artifacts/enterprise-alignment-validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))

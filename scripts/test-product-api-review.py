"""Validate the single contract and product invariants; these are not backend tests."""
from copy import deepcopy
import csv
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from openapi_spec_validator import validate

ROOT=Path(__file__).resolve().parent.parent
spec=json.loads((ROOT/'openapi/amlok.json').read_text())
fixtures=json.loads((ROOT/'data/product-api-examples.json').read_text())
validate(spec)
assert spec['x-availability']=='published_contract'
assert all(path.startswith('/v1/') for path in spec['paths'])
assert not (ROOT/'legacy').exists()
assert {p.name for p in (ROOT/'openapi').glob('*.json')}=={'amlok.json'}
target_ops=[op for methods in spec['paths'].values() for op in methods.values()]
assert len(target_ops)==len({o['operationId'] for o in target_ops})==67
for path,methods in spec['paths'].items():
    assert not {'put','delete'} & methods.keys(), path
    if 'patch' in methods: assert path in {'/v1/monitors/{id}','/v1/borrowers/{id}','/v1/originations/{id}'}
    for method,op in methods.items():
        assert op['x-availability']=='published_contract'
        if method=='post': assert any(p['name']=='Idempotency-Key' and p['required'] for p in op['parameters'])
        if method=='patch': assert any(p['name']=='If-Match' and p['required'] for p in op['parameters'])
        assert not any(p['name'] in ('workspace_id','environment','tenant_id') for p in op['parameters'])
        if path.endswith(('healthcheck','service-status')): assert op['security']==[]
        else: assert op['security']==[{'BearerAuth':[]}] and op['x-required-scopes']
for schema in spec['components']['schemas'].values(): Draft202012Validator.check_schema(schema)

def valid(name, value):
    schema={'$ref':'#/components/schemas/'+name,'components':spec['components']}
    return list(Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(value))

for name,value in fixtures.items():
    errors=valid(name,value)
    assert not errors, (name,[e.message for e in errors])
negative=[]
def reject(name, mutate):
    value=deepcopy(fixtures[name]); mutate(value)
    assert valid(name,value), ('accepted invalid example',name,value)
    negative.append(name)

reject('CreateBorrower',lambda v:v.update(type='person'))
reject('CreateOrigination',lambda v:v.update(workspace_id='another-workspace'))
reject('CreateOrigination',lambda v:v['application']['requested_amount'].update(amount=50000.0))
reject('CreateOrigination',lambda v:v.pop('risk_policy_version_id'))
reject('CreateEmbeddingSession',lambda v:v.update(purpose='reauthorize'))
reject('CreateEmbeddingSession',lambda v:v.update(connection_id='con_unexpected'))
reject('RiskPolicyInput',lambda v:v['rules'][0].update(on_missing='pass'))
reject('Origination',lambda v:v.update(risk_package_id=None))
reject('Origination',lambda v:v.update(status='waiting_for_credits'))
reject('Metric',lambda v:v.update(value='0'))
reject('Metric',lambda v:v.update(status='available'))
reject('RiskPackage',lambda v:v['assessment'].update(is_institution_decision=True))
reject('RiskPackage',lambda v:v['assessment'].update(recommendation='within_policy'))
reject('RiskPackage',lambda v:v.update(application=None))
reject('RiskPackage',lambda v:v.update(product='signal'))
reject('UpdateMonitor',lambda v:v.clear())
reject('UpdateMonitor',lambda v:v.update(baseline_package_id='rewrite-history'))
reject('Event',lambda v:v.update(bank_transactions=[]))
reject('CreateExport',lambda v:v.update(billing_report_type='usage'))
reject('CreateExport',lambda v:v.update(kind='billing'))
reject('Evidence',lambda v:v.update(provider_report_document_id='restricted-file'))
reject('Evidence',lambda v:v['record'].update(access_reason=None))

# Export union and portfolio enrollment cover the non-origination paths too.
assert not valid('CreateExport',{'kind':'billing','billing_report_type':'usage','window':{'start':'2026-10-01T00:00:00Z','end':'2026-11-01T00:00:00Z'},'format':'csv'})
monitor=deepcopy(fixtures['CreateMonitor']);monitor['baseline']={'portfolio':{'lending_product_version_id':'lpv_synthetic','application':None,'document_ids':[]}}
assert not valid('CreateMonitor',monitor)
monitor['baseline']['risk_package_id']='rp_synthetic'
assert valid('CreateMonitor',monitor)
collection=json.loads((ROOT/'downloads/amlok-api.postman_collection.json').read_text())
assert '/v2/' not in json.dumps(collection)
assert len(collection['item'])==67
print(json.dumps({'primary_operations':67,'positive_examples':len(fixtures)+2,'negative_examples':len(negative)+1,'backend_executed':False}))

# Institution completeness invariants: direct data access, documents and billing.
paths=spec['paths'];schemas=spec['components']['schemas']
for path in ['/v1/data/records','/v1/data/records/{id}','/v1/data/changes','/v1/documents','/v1/billing/payments','/v1/billing/payments/{id}','/v1/billing/usage','/v1/billing/usage/{id}','/v1/billing/transactions/{id}']:
    assert 'get' in paths[path],path
for path,methods in paths.items():
    if path.startswith(('/v1/data/','/v1/billing/')):assert set(methods)=={'get'},path
assert paths['/v1/data/records']['get']['x-required-scopes']==['data:read']
assert not any(p['name']=='evidence_set_id' for p in paths['/v1/data/records']['get']['parameters'])
assert any(p['name']=='cursor' and p['required'] for p in paths['/v1/data/changes']['get']['parameters'])
assert {'snapshot_id','changes_cursor','as_of'} <= set(schemas['DataPage']['required'])
assert {'submitted_request','document_ids'} <= set(schemas['Origination']['required'])
assert set(spec['x-export-schemas'])=={'risk_package','evidence','data','usage','credits','statements','funding','rates','workload'}
for pointer in spec['x-export-schemas'].values():assert pointer.rsplit('/',1)[-1] in schemas
reject('DataRecord', lambda v:v.update(access='restricted',access_reason='Revoked'))
reject('DataRecord', lambda v:v['source_payload'].update(status='not_retained'))
reject('DataChange', lambda v:v.update(record_id=None))
reject('UploadDocument', lambda v:v.update(requirement_id='req_document'))
reject('BillingPayment', lambda v:v.update(status='processing'))
reject('BillingPayment', lambda v:v.update(status='failed',credited_amount='0.00',settled_at=None))
reject('BillingTransaction', lambda v:v.update(amount='40.00'))
reject('BillingTransaction', lambda v:v.update(kind='funding',funding_type='paid',amount='5000.00'))
reject('BillingUsage', lambda v:v.update(product='signal'))
reject('CreateExport', lambda v:v.update(data_snapshot_id='snap_data'))
assert not valid('CreateExport',{'kind':'data','data_snapshot_id':'snap_data','format':'json'})
assert valid('CreateExport',{'kind':'data','format':'json'})
restricted=deepcopy(fixtures['DataRecord']);restricted.update(access='restricted',access_reason='Authorization withdrawn',normalized=None,document_ids=[],source_payload={'status':'restricted','value':None,'reason':'Authorization withdrawn'})
assert not valid('DataRecord',restricted)
pending=deepcopy(fixtures['BillingPayment']);pending.update(status='processing',credited_amount='0.00',settled_at=None,transaction_ids=[])
assert not valid('BillingPayment',pending)
from decimal import Decimal
summary=fixtures['BillingSummary']
assert Decimal(summary['available_credits'])==sum(Decimal(summary[k]) for k in ['paid_funding_credits','promotional_credits','adjustment_credits'])-Decimal(summary['spent_credits'])-Decimal(summary['refunded_credits'])
usage=fixtures['BillingUsage'];txn=fixtures['BillingTransaction']
assert Decimal(usage['unit_rate'])*usage['quantity']==Decimal(usage['amount'])==-Decimal(txn['amount'])
assert usage['transaction_id']==txn['id'] and txn['usage_id']==usage['id']
assert fixtures['Origination']['submitted_request']==fixtures['CreateOrigination']
print(json.dumps({'institution_completeness':'passed','negative_examples':len(negative)+1,'backend_executed':False}))

# Prepayment discounts are additive reporting fields, separate from usage rates.
commitment=deepcopy(fixtures['BillingSummary']['pricing']['commitment'])
assert commitment['prepayment_discount_percent']==0
assert commitment['pre_discount_payment_amount']==commitment['payment_amount']
historical=deepcopy(commitment)
historical.pop('prepayment_discount_percent');historical.pop('pre_discount_payment_amount')
assert not valid('BillingCommitment',historical), 'Historical snapshots must remain valid'
negotiated=deepcopy(commitment)
negotiated.update(monthly_minimum='1000.00',payment_cadence='quarterly',months_per_payment=3,pre_discount_payment_amount='3000.00',prepayment_discount_percent=20,payment_amount='2400.00')
assert not valid('BillingCommitment',negotiated)
assert Decimal(negotiated['payment_amount'])==Decimal(negotiated['pre_discount_payment_amount'])*(1-Decimal(str(negotiated['prepayment_discount_percent']))/100)
for invalid in [-1,100.01,'20',None]:
 bad=deepcopy(negotiated);bad['prepayment_discount_percent']=invalid
 assert valid('BillingCommitment',bad), ('accepted invalid prepayment discount',invalid)
for invalid in ['3000',3000.00,'-3000.00']:
 bad=deepcopy(negotiated);bad['pre_discount_payment_amount']=invalid
 assert valid('BillingCommitment',bad), ('accepted invalid gross amount',invalid)
assert 'do not apply the discount a second time' in schemas['FinancialBillingRate']['properties']['discount_percent']['description']
assert 'does not reduce' in schemas['BillingCommitment']['properties']['prepayment_discount_percent']['description'].lower()
print(json.dumps({'negotiated_prepayment_discount':'passed','historical_snapshots':'compatible','backend_executed':False}))


# Shared identity maintenance must remain narrow and party checks purpose-bound.
assert spec['paths']['/v1/borrowers/{id}']['patch']['x-required-scopes']==['borrowers:write']
assert spec['paths']['/v1/originations/{id}']['patch']['x-required-scopes']==['insights:write']
reject('UpdateBorrower',lambda value:value.clear())
reject('UpdateBorrower',lambda value:value.update(subject_id='biz_replacement'))
reject('UpdateOrigination',lambda value:value.update(status='completed'))
party={'borrower_id':'bor_owner_synthetic','roles':['guarantor'],'ownership_share':None,
 'authority':{'basis':'institution_attested','attested_at':'2026-10-01T00:00:00Z','purposes':['credit_assessment']},
 'connection_ids':[],'document_ids':[]}
assert not valid('ParticipantInput',party)
assert valid('ParticipantInput',{**party,'ownership_share':'101'})
assert valid('ParticipantInput',{**party,'roles':['unrecognized_role']})
assert valid('ParticipantInput',{**party,'authority':{**party['authority'],'purposes':[]}})
assert valid('ParticipantInput',{**party,'connection_ids':['con_'+str(i) for i in range(101)]})
assert 'participants' in spec['x-risk-package-sections']
assert len(schemas['RiskPackageSummary']['properties']['sections']['items']['properties']['section']['enum'])==49
print(json.dumps({'borrower_lifecycle_and_participants':'passed'}))

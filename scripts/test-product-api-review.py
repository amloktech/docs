"""Validate the primary contract and migration completeness; these are not backend tests."""
from copy import deepcopy
import csv
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from openapi_spec_validator import validate

ROOT=Path(__file__).resolve().parent.parent
spec=json.loads((ROOT/'openapi/amlok-v2.json').read_text())
legacy=json.loads((ROOT/'openapi/amlok-v1.json').read_text())
audit=json.loads((ROOT/'data/api-surface-review.json').read_text())
fixtures=json.loads((ROOT/'data/product-api-examples.json').read_text())
validate(spec)
assert spec['x-availability']=='published_contract'
assert legacy['info']['version']=='1.4.2'
assert all(path.startswith('/v2/') for path in spec['paths'])
assert all(path.startswith('/v1/') for path in legacy['paths'])
source_ops={op['operationId']:(method.upper(),path) for path,methods in legacy['paths'].items() for method,op in methods.items()}
review_ops={op['operation_id']:(op['method'],op['path']) for op in audit['operations']}
assert source_ops==review_ops and len(audit['operations'])==len(source_ops)==192
assert sum(audit['dispositions'].values())==192
csv_rows=list(csv.DictReader((ROOT/'downloads/api-endpoint-migration.csv').open()))
assert {r['operation_id'] for r in csv_rows}==set(source_ops)
assert len(csv_rows)==192 and all(r['target'] and r['reason'] for r in csv_rows)
target_ops=[op for methods in spec['paths'].values() for op in methods.values()]
assert len(target_ops)==audit['target_operation_count']==45
assert len({o['operationId'] for o in target_ops})==45
for path,methods in spec['paths'].items():
    assert not {'put','delete'} & methods.keys(), path
    if 'patch' in methods: assert path=='/v2/monitors/{id}'
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
monitor=deepcopy(fixtures['CreateMonitor']);monitor['baseline']={'portfolio_onboarding_reference':'portfolio_synthetic'}
assert not valid('CreateMonitor',monitor)
monitor['baseline']['risk_package_id']='rp_synthetic'
assert valid('CreateMonitor',monitor)
collection=json.loads((ROOT/'downloads/amlok-api.postman_collection.json').read_text())
assert '/v1/' not in json.dumps(collection)
assert len(collection['item'])==45
assert not set(source_ops)&{o['operationId'] for o in target_ops}
print(json.dumps({'current_operations_mapped':192,'primary_operations':45,'positive_examples':len(fixtures)+2,'negative_examples':len(negative)+1,'backend_executed':False}))

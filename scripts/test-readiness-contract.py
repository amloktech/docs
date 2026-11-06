"""Cross-artifact and semantic regressions; never represents backend execution."""
from copy import deepcopy
import json
from pathlib import Path
from jsonschema import Draft202012Validator,FormatChecker
from readiness_contract import EVENT_RESOURCES
ROOT=Path(__file__).resolve().parent.parent
spec=json.loads((ROOT/'openapi/amlok.json').read_text());s=spec['components']['schemas'];f=json.loads((ROOT/'data/product-api-examples.json').read_text())
index={o['id']:o for o in json.loads((ROOT/'data/api-reference-index.json').read_text())}
checks=0

def errors(name,value):return list(Draft202012Validator({'$ref':'#/components/schemas/'+name,'components':spec['components']},format_checker=FormatChecker()).iter_errors(value))
def accept(name,value):
 global checks
 result=errors(name,value);assert not result,(name,[e.message for e in result]);checks+=1

def reject(name,value):
 global checks
 assert errors(name,value),(name,'invalid input accepted',value);checks+=1

# Field descriptions must retain their distinct financial and resource meanings.
assert 'Published Hub' in s['EmbeddingSession']['properties']['embedding_version_id']['description']
assert 'Requested payment amount' in s['BillingPayment']['properties']['amount']['description']
assert 'Total credits actually posted' in s['BillingPayment']['properties']['credited_amount']['description']
assert 'unit rate' in s['BillingUsage']['properties']['unit_rate']['description']
assert 'charge' not in s['Document']['properties']['created_at']['description']
assert 'Immutable identifier' in s['DataRecord']['properties']['id']['description']
for name in ['BillingPayment','BillingUsage','DataRecord']:
 props=s[name]['properties'];assert props['id']['description']!=props.get('amount',props['borrower_id'] if 'borrower_id' in props else props['snapshot_id'])['description']

req={'id':'req_test','code':'source_reauthorization_required','message':'Reconnect the source','action':'reauthorize_source','connection_id':'con_synthetic','integration_id':None,'document_type':None,'accepted_mime_types':[],'consent_purposes':['continuous_monitoring']}
accept('Requirement',req);reject('Requirement',{**req,'connection_id':None});reject('Requirement',{**req,'consent_purposes':[]})
docreq={**req,'code':'document_required','action':'upload_document','connection_id':None,'document_type':'financial_statement','accepted_mime_types':['application/pdf'],'consent_purposes':[]}
accept('Requirement',docreq);reject('Requirement',{**docreq,'document_type':None})
monitor={**f['Monitor'],'status':'requires_action','requirements':[req]};accept('Monitor',monitor);reject('Monitor',{**monitor,'requirements':[]});reject('Monitor',{**f['Monitor'],'requirements':[req]})
err={'code':'processing_failed','message':'Source evaluation failed','retryable':False,'request_id':'req_synthetic','field':None}
accept('Monitor',{**f['Monitor'],'status':'failed','failure':err});reject('Monitor',{**f['Monitor'],'status':'failed'})
reject('Document',{**f['Document'],'status':'rejected'});accept('Document',{**f['Document'],'status':'rejected','failure':{**err,'code':'document_rejected'}})
reject('MonitoringRun',{**f['MonitoringRun'],'status':'failed'});accept('MonitoringRun',{**f['MonitoringRun'],'status':'failed','risk_package_id':None,'failure':err})
reject('CreateEmbeddingSession',{**f['CreateEmbeddingSession'],'consent_purposes':[]})
reject('CreateEmbeddingSession',{**f['CreateEmbeddingSession'],'monitor_id':'mon_synthetic'})
accept('CreateEmbeddingSession',{**f['CreateEmbeddingSession'],'monitor_id':'mon_synthetic','requirement_id':'req_test'})
reject('CreateEmbeddingSession',{**f['CreateEmbeddingSession'],'monitor_id':'mon_synthetic','origination_id':'orgn_synthetic','requirement_id':'req_test'})
reject('DealSnapshotInput',{**f['DealSnapshotInput'],'previous_snapshot_id':None})
reject('DealSnapshotInput',{**f['DealSnapshotInput'],'workspace_id':'foreign'})
reject('DealSnapshot',{**f['DealSnapshot'],'record_version':2})
accept('BaselineInput',{'portfolio':{'lending_product_version_id':'lpv_synthetic','application':None,'document_ids':[]}})
reject('BaselineInput',{'portfolio_onboarding_reference':'unprovisioned'})
reject('BaselineInput',{'portfolio':{'lending_product_version_id':'lpv_synthetic','application':None,'document_ids':[]},'risk_package_id':'rp_synthetic'})
for event,(resource,operation,scope) in EVENT_RESOURCES.items():
 accept('Event',{**f['Event'],'type':event,'resource_type':resource})
 reject('Event',{**f['Event'],'type':event,'resource_type':'wrong'})
 response=index[operation]['response'];assert 'record_version' in s[response]['required'],(event,response)
 page=(ROOT/'api-reference/event-catalog.mdx').read_text();assert '`'+event+'`' in page
assert len(EVENT_RESOURCES)==len(s['Event']['properties']['type']['enum'])
assert 'sync.completed' not in (ROOT/'data-model/events.mdx').read_text()
for filename in ['journey-inputs.json','consumer-journey-inputs.json']:
 values=json.loads((ROOT/'downloads'/filename).read_text())
 for name,value in values.items():accept(name,value)
 application=values['CreateOrigination']['application'];schema=next(c['json_schema'] for c in f['Configuration']['application_schemas'] if c['id']==application['application_schema_id']);assert Draft202012Validator(schema).is_valid(application['declared_data'])
# Validate actual requests/responses made by the executed client against the OpenAPI.
log=json.loads((ROOT/'artifacts/client-contract-calls.json').read_text())
for call in log:
 op=index[call['operationId']];operation=spec['paths'][op['path']][op['method'].lower()]
 if 'request' in call:accept(op['request'],call['request'])
 if 'response' in call:
  media=operation['responses'][call['status']]['content']['application/json']
  errors_=list(Draft202012Validator({**media['schema'],'components':spec['components']},format_checker=FormatChecker()).iter_errors(call['response']))
  assert not errors_,(call['operationId'],[e.message for e in errors_]);checks+=1
# No generated scope or operation may silently drift from acceptance coverage.
assert len(index)==57
assert spec['x-contract-stage']=='backend-implementation-specification'
summary={'schema_and_client_checks':checks,'event_types':len(EVENT_RESOURCES),'offline_client_calls':len(log),'backend_execution':'not_run'}
(ROOT/'artifacts/backend-readiness.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))

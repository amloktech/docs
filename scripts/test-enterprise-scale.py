"""Validate enterprise schemas and execute transport/compatibility failure cases."""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
from jsonschema import Draft202012Validator, FormatChecker
ROOT=Path(__file__).resolve().parent.parent
spec=json.loads((ROOT/'openapi/amlok.json').read_text());schemas=spec['components']['schemas'];checks=0

def validate(schema,value,valid=True):
 global checks
 errors=list(Draft202012Validator({**schema,'components':spec['components']},format_checker=FormatChecker()).iter_errors(value))
 assert bool(errors)!=valid, [e.message for e in errors][:3]
 checks+=1

def named(name,value,valid=True):validate({'$ref':'#/components/schemas/'+name},value,valid)
def module(name,file):
 definition=importlib.util.spec_from_file_location(name,ROOT/file);module=importlib.util.module_from_spec(definition);definition.loader.exec_module(module);return module

client=module('enterprise_client','downloads/enterprise-client.py');compat=module('compat','downloads/check-contract-compatibility.py')
for methods in spec['paths'].values():
 for op in methods.values():
  for response in op['responses'].values():
   for media in response.get('content',{}).values():
    for key,view in media.get('x-response-views',{}).items():
     validate(view['schema'],view['example']);validate(media['schema'],view['example'])
     if view['example'].get('data',{}).get('view')=='section':
      bad=deepcopy(view['example']);bad['data']['section']='unknown';validate(view['schema'],bad,False)
profile=json.loads((ROOT/'downloads/development-profile.json').read_text())
named('OperationalProfile',profile)
bad=deepcopy(profile);bad['capacity']['max_in_flight_requests']=0;named('OperationalProfile',bad,False)
bad=deepcopy(profile);bad['max_page_items']=101;named('OperationalProfile',bad,False)
bad=deepcopy(profile);bad['capacity']['workloads'][1]['group']='origination';named('OperationalProfile',bad,False)
bad=deepcopy(profile);bad['capacity']['targets'].append(deepcopy(bad['capacity']['targets'][0]));named('OperationalProfile',bad,False)
for source in [{'kind':'data','data_record_id':'dr_test','format':'json'},{'kind':'data','data_snapshot_id':'snap_test','format':'csv'}]:named('CreateExport',source)
named('CreateExport',{'kind':'data','data_record_id':'dr_test','data_snapshot_id':'snap_test','format':'json'},False)
named('CreateExport',{'kind':'billing','billing_report_type':'usage','window':{'start':'2026-01-01T00:00:00Z','end':'2026-02-01T00:00:00Z'},'data_record_id':'wrong','format':'json'},False)
named('ExportDownloadPurpose',{'purpose':'Review','part_number':0},False)
recovery=spec['paths']['/v1/data/records']['get']['responses']['413']['content']['application/json']['example']['error']
named('Error',recovery);assert recovery['recovery']['export_request']['data_snapshot_id']==recovery['recovery']['data_checkpoint']['snapshot_id']
bad=deepcopy(recovery);del bad['recovery'];named('Error',bad,False)
capacity={'code':'queue_full','message':'Retry later','retryable':True,'request_id':'req_test','field':None,'capacity':{'group':'origination','reason':'queue_full','limit':100,'profile_id':'test','profile_version':'1'}}
named('Error',capacity);bad=deepcopy(capacity);bad['retryable']=False;named('Error',bad,False)

# A short nonterminal page must continue; stalled cursors and snapshot drift fail before commit.
committed=[]
pages=[{'data':[1],'page':{'snapshot_id':'same','next_cursor':'next','has_more':True}},{'data':[2],'page':{'snapshot_id':'same','next_cursor':None,'has_more':False}}]
client.consume_pages(lambda c:pages[0 if c is None else 1],lambda data,page:committed.extend(data));assert committed==[1,2];checks+=1
for broken in [dict(pages[0],page={**pages[0]['page'],'next_cursor':None}),dict(pages[0],data=[])]:
 try:client.consume_pages(lambda c:broken,lambda d,p:None);raise AssertionError('accepted stalled page')
 except ValueError:checks+=1
try:client.consume_pages(lambda c:pages[0] if c is None else {**pages[1],'page':{**pages[1]['page'],'snapshot_id':'foreign'}},lambda d,p:None);raise AssertionError('snapshot changed')
except ValueError:checks+=1

# Interrupted transfers resume an exact byte range, including split Unicode/JSON tokens.
body=json.dumps({'rows':[{'name':'Montréal 商店','amount':'123.45'}]*7},ensure_ascii=False).encode();size=37
parts=[body[i:i+size] for i in range(0,len(body),size)]
artifact={'id':'artifact_test','part_size_bytes':size,'part_count':len(parts),'total_bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()}
requests=[]
def link(number):
 value=parts[number-1]
 return {'artifact_id':artifact['id'],'part_number':number,'byte_offset':(number-1)*size,'byte_length':len(value),'sha256':hashlib.sha256(value).hexdigest(),'url':'https://download.example.com/private','etag':'"part-%d"'%number}
def interrupted(link,offset):
 value=parts[link['part_number']-1]
 if link['part_number']==2:
  yield value[offset:offset+7];raise IOError('simulated disconnect')
 yield value[offset:]
def resumed(link,offset):requests.append((link['part_number'],offset));yield parts[link['part_number']-1][offset:]
with tempfile.TemporaryDirectory() as temp:
 destination=Path(temp)/'result.json';state=Path(temp)/'checkpoint'
 try:client.download_export(artifact,link,destination,state,interrupted);raise AssertionError('expected disconnect')
 except IOError:pass
 client.download_export(artifact,link,destination,state,resumed)
 assert destination.read_bytes()==body and (2,7) in requests;checks+=1
 assert 'https' not in (state/'artifact.json').read_text();checks+=1
 try:client.download_export({**artifact,'id':'other'},link,destination,state,resumed);raise AssertionError('accepted foreign artifact')
 except ValueError:checks+=1
 corrupt=state/'00000001.part';corrupt.write_bytes(b'x'*size)
 try:client.download_export(artifact,link,destination,state,resumed);raise AssertionError('accepted corrupt part')
 except ValueError:assert not corrupt.exists();assert destination.read_bytes()==body;checks+=1
 bad=deepcopy(artifact);bad['part_count']+=1
 try:client.download_export(bad,link,destination,Path(temp)/'bad',resumed);raise AssertionError('accepted wrong layout')
 except ValueError:checks+=1

# Structural diff catches breaking enum/type changes and newly required request fields.
old={'paths':{'/v1/test':{'post':{'operationId':'test','requestBody':{'content':{'application/json':{'schema':{'$ref':'#/components/schemas/Input'}}}}}}},'components':{'schemas':{'Input':{'type':'object','properties':{'name':{'type':'string'}},'required':['name']},'Output':{'type':'object','properties':{'state':{'enum':['ready','failed']}},'required':['state']}}}}
new=deepcopy(old);new['components']['schemas']['Output']['properties']['extra']={'type':'string'};assert compat.compare(old,new)==[];checks+=1
new['components']['schemas']['Output']['properties']['state']['enum'].append('pending');assert compat.compare(old,new);checks+=1
new=deepcopy(old);new['components']['schemas']['Input']['properties']['extra']={'type':'string'};new['components']['schemas']['Input']['required'].append('extra');assert compat.compare(old,new);checks+=1
new=deepcopy(old);new['components']['schemas']['Output']['properties']['state']={'type':'integer'};assert compat.compare(old,new);checks+=1
assert len(spec['paths']['/v1/risk-packages/{id}']['get']['responses']['200']['content']['application/json']['x-response-views'])==len(spec['x-risk-package-sections'])+2
gate=module('evidence_gate','scripts/validate-enterprise-evidence.py')
acceptance=json.loads((ROOT/'implementation/enterprise-acceptance.json').read_text())
assert gate.problems(acceptance,acceptance), 'Unrun acceptance specification cannot pass as runtime evidence'
checks+=1
result={'contract_and_transport_checks':checks,'paged_risk_sections':len(spec['x-risk-package-sections']),'backend_load_execution':'not_run','provider_execution':'not_run'}
(ROOT/'artifacts/enterprise-scale-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

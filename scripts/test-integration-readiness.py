"""Validate recovery contracts and exercise sandbox clients against controlled responses."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import json
import subprocess
import tempfile
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parent.parent
spec=json.loads((ROOT/'openapi/amlok-v1.json').read_text())
index=json.loads((ROOT/'data/api-reference-index.json').read_text())
byid={x['id']:x for x in index}
S=spec['components']['schemas']; checks=0
def check(ok,msg):
    global checks
    assert ok,msg
    checks+=1
def valid(name,value):return Draft202012Validator({'$ref':'#/components/schemas/'+name,'components':spec['components']}).is_valid(value)
def data(path,method='GET'):return deepcopy(next(x['response']['data'] for x in index if x['path']==path and x['method']==method))

new=json.loads((ROOT/'data/integration-api-index.json').read_text())
check(len(new)==12,'Missing integration operations')
for x in new:
    check((ROOT/(x['page']+'.mdx')).exists(),'Missing endpoint page')
check(not valid('EP139Request',{k:v for k,v in byid['EP139']['request'].items() if k!='state'}),'Connection accepts no anti-CSRF state')
check(not valid('AuthorizationRequest',dict(byid['IR001']['request'],state='short')),'Short state accepted')
context={'product':'insights','workflow_run_id':'wfr_example','subject_association_id':'assoc_example'}
check(valid('EP142Request',dict(byid['EP142']['request'],subject_id='per_example',verification_type='kyc',processing_context=context)),'Owner KYC cannot use parent business')
check(not valid('EP142Request',dict(byid['EP142']['request'],verification_type='kyb',processing_context=context)),'Association exception leaks into KYB')
for oid in ['EP143','EP148']:
    check(not valid(oid+'Request',dict(byid[oid]['request'],processing_context=context)),'Association permits unrelated processing')
failed=data('/v1/workflow-runs/{id}');failed.update(status='failed',failure=None,billing_usage_id=None,output_resource_ids=[])
check(not valid('WorkflowRun',failed),'Failed workflow has no reason')
failed['failure']={'code':'processing_timeout','message':'Retry this run.','retryable':True,'recovery_action':'retry_same_run','retry_after_seconds':30,'occurred_at':'2026-10-23T14:00:00Z','request_id':'req_test'}
check(valid('WorkflowRun',failed),'Valid failed workflow rejected')
req=data('/v1/requirements/{id}');req.update(status='rejected',rejection=None)
check(not valid('Requirement',req),'Rejected requirement has no reason')
req['rejection']={'code':'unreadable','message':'Upload a clear document.','document_ids':['doc_example'],'reviewed_at':'2026-10-23T14:00:00Z'}
check(valid('Requirement',req),'Valid rejected requirement rejected')
for sample in spec['paths']['/v1/request-receipts/lookup']['get']['x-codeSamples']:
    check('Idempotency-Key' in sample['source'],'Receipt sample omits original key')
for route,ops in spec['paths'].items():
    if 'post' in ops:check('idempotency_result_expired' in ops['post']['description'],'POST lacks durable recovery semantics')
for term in ['API keys in the client portal','account manager']:
    check(term in (ROOT/'api-reference/authentication.mdx').read_text(),'Portal access not explicit')
check('Same-workspace and same-subject parent.' not in json.dumps(S['ProcessingContext']),'Old parent restriction remains')

loader=importlib.util.spec_from_file_location('journey',ROOT/'downloads/run-sandbox-journey.py')
mod=importlib.util.module_from_spec(loader);loader.loader.exec_module(mod)
class FakeClient:
    origin='https://sandbox.example.com'
    def __init__(self,product='insights',environment='sandbox',lose=False):self.product=product;self.environment=environment;self.posts=[];self.lose=lose
    def request(self,method,path,body=None,key=None):
        route=path.split('?')[0]
        if method=='POST':
            self.posts.append((method,route,deepcopy(body),key))
            if self.lose:
                self.lose=False
                raise TimeoutError('Simulated lost accepted response')
            if len(self.posts)>1:raise mod.APIError(409,'idempotency_result_expired')
            return {'data':{'id':'wfr_example' if self.product=='insights' else 'mon_example'}}
        if route=='/v1/configuration':
            d=data('/v1/configuration');d['environment']=self.environment;return {'data':d}
        if route=='/v1/sandbox/scenarios':
            return {'data':[{'id':self.product+'_success','subject_id':'biz_example','application_id':'app_example','input_manifest_id':'manifest_example','baseline_snapshot_id':'rsk_baseline','workflow_version':'underwrite-v1','ruleset_version':'monitoring-v1','cadence':'daily'}]}
        if route.endswith('/readiness'):return {'data':{'status':'ready'}}
        if route=='/v1/request-receipts/lookup':return {'data':{'status':'accepted','resource_id':'wfr_example'}}
        if route=='/v1/workflow-runs/wfr_example':
            d=data('/v1/workflow-runs/{id}');d.update(status='completed',billing_usage_id='billing_usage_example',output_resource_ids=['rsk_example'])
            return {'data':d}
        if route=='/v1/billing/usage':
            return {'data':[x for x in data('/v1/billing/usage') if x['product']==self.product]}
        if route.startswith('/v1/billing/usage/'):
            return {'data':next(x for x in data('/v1/billing/usage') if x['product']==self.product)}
        if route.startswith('/v1/monitors/'):return {'data':data('/v1/monitors/{id}')}
        if route.startswith('/v1/monitoring-periods/'):return {'data':data('/v1/monitoring-periods/{id}')}
        if route=='/v1/risk-snapshots':
            snap=data('/v1/risk-snapshots/{id}');snap.update(previous_snapshot_id='rsk_baseline',billing_usage_id='usage_signal_example');return {'data':[snap]}
        if route.startswith('/v1/risk-snapshots/'):return {'data':data('/v1/risk-snapshots/{id}')}
        if route=='/v1/alerts':return {'data':data('/v1/alerts')}
        raise AssertionError('Unexpected request: '+method+' '+path)

with tempfile.TemporaryDirectory() as temp:
    temp=Path(temp)
    for product in ['insights','signal']:
        client=FakeClient(product);state=temp/(product+'.json')
        result=mod.Journey(client,state,product,sleep=lambda _:None).run()
        check(bool(result['usage_id']),'Journey failed to reach usage')
        mod.Journey(client,state,product,sleep=lambda _:None).run()
        check(len(client.posts)==1,'Resuming journey created duplicate processing')
        check('api_key' not in state.read_text(),'Credential persisted')
    prod=FakeClient(environment='production')
    try:mod.Journey(prod,temp/'prod.json','insights').run();raise AssertionError('Production accepted')
    except RuntimeError as e:check('refuses production' in str(e),'Wrong production failure')
    check(not prod.posts,'Production mutation attempted')
    lost=FakeClient(lose=True);p=temp/'lost.json'
    try:mod.Journey(lost,p,'insights').run();raise AssertionError('Lost response not simulated')
    except TimeoutError:pass
    result=mod.Journey(lost,p,'insights',sleep=lambda _:None).run()
    check(lost.posts[0][3]==lost.posts[1][3],'Lost-response recovery changed key')
    check(result['workflow_id']=='wfr_example','Receipt did not restore original run')
    try:mod.Journey(lost,p,'signal');raise AssertionError('State rebound')
    except ValueError:check(True,'State binding')
    pm=json.loads((ROOT/'downloads/amlok-journeys.postman_collection.json').read_text())
    scripts=[]
    def walk(x):
        if isinstance(x,dict):
            for e in x.get('event',[]):scripts.append('\n'.join(e['script']['exec']))
            for v in x.values():walk(v)
        elif isinstance(x,list):
            for v in x:walk(v)
    walk(pm)
    for i,source in enumerate(scripts):
        p=temp/f'postman-{i}.js';p.write_text(source)
        subprocess.run(['node','--check',str(p)],check=True,capture_output=True)
        check(True,'Postman script syntax')
    check('{{$guid}}' in json.dumps(pm),'Postman keys are not generated with a valid dynamic variable')
report={'checks':checks,'operations':len(index),'contract':'Seven developer-readiness gaps addressed','execution':'Schema validation and controlled client tests only; no live backend calls.'}
(ROOT/'artifacts/integration-readiness-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))

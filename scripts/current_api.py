"""Build the single authoritative reference and client artifacts from one contract."""
from collections import OrderedDict
from copy import deepcopy
import json
import re
import shlex
from pathlib import Path
from product_api_review import ROOT, VERSION, build_spec, operations, generate as review
from product_api_examples import examples


def save(path, value):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2) + '\n')


def slug(value):
    return re.sub(r'(?<!^)([A-Z])', r'-\1', value).lower()


def fixtures():
    f = examples()
    now = '2026-11-06T12:00:00Z'
    f.update({
        'Borrower': {'id':'bor_synthetic','type':'business','subject_id':'biz_synthetic','created_at':now,'client_reference':'LOS-B-0042','profile':f['CreateBorrower']},
        'EmbeddingSession': {'id':'embs_synthetic','borrower_id':'bor_synthetic','status':'created','launch_url':'https://borrower.example.com/session/synthetic','expires_at':'2026-11-06T12:15:00Z','connection_ids':[],'consent_ids':[]},
        'Connection': {'id':'con_synthetic','borrower_id':'bor_synthetic','integration_id':'bank_synthetic','status':'connected','consent_id':'consent_synthetic','last_successful_sync_at':now,'source_as_of':now,'coverage':f['RiskPackage']['sources'][0]['window'],'missing_reason':None},
        'Consent': {'id':'consent_synthetic','borrower_id':'bor_synthetic','status':'active','purposes':['credit_assessment','continuous_monitoring'],'captured_at':now,'expires_at':None,'revoked_at':None},
        'RevokeConsent': {'reason':'Borrower withdrew authorization.'},
        'UploadDocument': {'file':'<binary file bytes>','context':'borrower','borrower_id':'bor_synthetic','document_type':'financial_statement'},
        'Document': {'id':'doc_synthetic','context':'borrower','borrower_id':'bor_synthetic','file_name':'financial-statement.pdf','mime_type':'application/pdf','sha256':'0'*64,'size_bytes':12500,'status':'available','restriction_reason':None},
        'DownloadPurpose': {'purpose':'Institution underwriting review'},
        'DownloadLink': {'url':'https://downloads.example.com/synthetic','expires_at':'2026-11-06T12:05:00Z','sha256':'0'*64,'mime_type':'application/pdf'},
        'LendingProductVersion': f['RiskPackage']['lending_product'],
        'RiskPolicyVersion': f['RiskPackage']['risk_policy'],
        'EvidenceSummary': f['Evidence']['record'],
        'Monitor': {'id':'mon_synthetic','borrower_id':'bor_synthetic','deal':f['CreateMonitor']['deal'],'status':'active','baseline_package_id':'rp_synthetic','latest_package_id':'rp_signal_synthetic','risk_policy_version_id':'rpv_synthetic','cadence_id':'cadence_synthetic','next_evaluation_at':'2026-11-07T12:00:00Z','record_version':1},
        'MonitoringRun': {'id':'mr_synthetic','monitor_id':'mon_synthetic','status':'partial','started_at':now,'completed_at':now,'risk_package_id':'rp_signal_synthetic','sources':f['RiskPackage']['sources'],'evidence_set_id':'es_synthetic','limitations':['Debt-service data remains incomplete.']},
        'Alert': {'id':'alert_synthetic','monitor_id':'mon_synthetic','borrower_id':'bor_synthetic','status':'open','severity':'warning','rule_id':'dscr-minimum','policy_version_id':'rpv_synthetic','message':'Required debt-service evidence is unavailable.','detected_at':now,'resolved_at':None,'previous_package_id':'rp_synthetic','current_package_id':'rp_signal_synthetic','metric_key':'dscr','previous_value':None,'current_value':None,'threshold':'1.25','unit':'ratio','evidence_ids':['ev_bank_synthetic']},
        'Export': {'id':'exp_synthetic','status':'queued','created_at':now,'format':'json','source':f['CreateExport'],'failure':None},
        'Delivery': {'id':'del_synthetic','event_id':'evt_synthetic','endpoint_id':'dest_synthetic','attempt':1,'status':'delivered','attempted_at':now,'http_status':200},
        'ReplayEvent': {'event_id':'evt_synthetic','endpoint_id':'dest_synthetic'},
        'ReplayReceipt': {'id':'replay_synthetic','event_id':'evt_synthetic','status':'accepted'},
        'BillingSummary': {'as_of':now,'currency':'CAD','available_credits':'4935.00','spent_credits':'65.00','billing_account_id':'billing_synthetic','snapshot_id':'snap_synthetic'},
        'BillingTransaction': {'id':'txn_usage_synthetic','snapshot_id':'snap_synthetic','posted_at':now,'amount':'-40.00','currency':'CAD','kind':'usage','product':'insights','description':'Synthetic underwriting usage, not a price quotation.','usage_id':'usage_synthetic'},
        'RequestReceipt': {'idempotency_key':'origination-synthetic-0042','operation_id':'createOrigination','resource_id':'orgn_synthetic','accepted_at':now,'response_replay_available':False},
        'Healthcheck': {'status':'ok'},
        'ServiceStatus': {'status':'operational','as_of':now},
    })
    f['Configuration'] = {'products':['insights','signal'],'embedding_version_ids':['embed_synthetic'],
        'application_schemas':[{'id':'app_schema_synthetic','version':'1','json_schema':{'type':'object','required':['annual_revenue'],'properties':{'annual_revenue':{'type':'string','pattern':'^[0-9]+\\.[0-9]{2}$'}},'additionalProperties':False}}],
        'pricing_schemas':[{'id':'pricing_synthetic','version':'1','json_schema':{'type':'object','required':['rate_type','annual_interest_rate','amortization_months','fees'],'properties':{'rate_type':{'const':'fixed'},'annual_interest_rate':{'type':'string'},'amortization_months':{'type':'integer','minimum':1},'fees':{'type':'array','items':{'type':'object'}}},'additionalProperties':False}}],
        'cadences':[{'id':'cadence_synthetic','description':'Illustrative daily schedule; use your provisioned cadence.'}],
        'dimensions':[{'key':'dscr','description':'Eligible cash flow divided by complete existing and proposed debt service over comparable periods.','unit':'ratio','calculation_version':'cashflow-dscr-synthetic-v1','borrower_types':['business']}],
        'integration_ids':['bank_synthetic']}
    for name in ['EmbeddingSession','Connection','Origination','Alert','Export']:
        f[name]['record_version'] = 1
    from institution_api import extend_fixtures
    extend_fixtures(f)
    from readiness_contract import extend_fixtures as readiness_fixtures
    readiness_fixtures(f)
    from risk_package_contract import extend_fixtures as risk_fixtures
    return risk_fixtures(f)


PURPOSE = {
    'createBorrower':'Register a business or consumer borrower. Registration records institution-supplied identity; it does not assert successful KYB or KYC.',
    'createEmbeddingSession':'Create a short-lived Integrations Hub session. Send only launch_url to the borrower. AMLOK captures consent and manages provider authorization and ingestion.',
    'createLendingProductVersion':'Store an immutable version of a lending product, including eligibility, pricing and repayment terms. This is your lending catalog, not merchant inventory.',
    'createRiskPolicyVersion':'Store an immutable policy version. AMLOK validates typed rules and units; attached policy documents provide context and do not become executable rules automatically.',
    'createOrigination':'Submit the borrower application with exact product and policy versions, connections and documents. AMLOK collects and normalizes data, runs included checks and publishes the risk package.',
    'getRiskPackage':'Retrieve an immutable Insights or Signal result with financial dimensions, policy evaluations, limitations and the frozen supporting evidence set. Recommendations do not replace the institution decision.',
    'listEvidence':'List frozen records and files belonging to an evidence set. Use resource_type to narrow the normalized resource family. Entitlement restrictions remain visible as metadata.',
    'getEvidence':'Read the exact normalized evidence version and its provenance, or the controlled document reference for a provider report. This never silently substitutes the latest source record.',
    'createMonitor':'Enroll a funded deal in Signal with an existing risk package or approved portfolio baseline. AMLOK schedules refreshes and change-driven reassessments.',
    'updateMonitor':'Change future monitoring configuration with the current ETag. Historical assessments, alerts, evidence and charges remain immutable. A stopped monitor cannot resume.',
    'listMonitoringRuns':'Inspect scheduled or change-driven monitoring evaluations, including per-integration freshness, coverage, failures and the resulting risk package.',
    'listAlerts':'Read system-derived risk conditions and their evidence. Missing or stale inputs are not a successful risk check. Institutions manage intervention in their own systems.',
    'createExport':'Prepare a risk package, evidence set or billing report for download. Each kind requires its own source permissions in addition to export access.',
    'listEvents':'Read the durable event feed. Start with start=now before a snapshot bootstrap, then retain resume_cursor after each committed batch. Delivery order is not resource-version order.',
    'replayEvent':'Requeue an event for an existing console-managed webhook destination. Replay only retries delivery; it never reruns analysis or adds usage charges.',
    'getBillingSummary':'Read the selected workspace CAD wallet shared across Insights and Signal. Payment methods and automatic funding controls belong to the organization billing console.',
    'listBillingTransactions':'Read immutable workspace funding, usage, adjustment and final-refund entries. Use typed billing exports for detailed statements, workload and historical rates.',
    'lookupRequestReceipt':'Recover the accepted resource using the original operation and idempotency key after a timeout or expired response cache. Do not submit accepted work as a new command.',
    'getConfiguration':'Discover the approved schemas, products, integration IDs, embedding versions and monitoring cadences available to this API key.',
    'uploadDocument':'Upload borrower evidence or documents supporting a lending product or risk policy. Upload creates a new record; it cannot overwrite an existing document.',
    'downloadDocument':'Issue a short-lived download URL for an authorized available file. Recheck source entitlement and borrower access; possession of a document ID alone grants nothing.',
    'revokeConsent':'Record withdrawal of authorization and stop future collection covered by that consent. Revocation does not edit historical assessments or serve as a data-deletion command.',
}


from institution_api import PURPOSE as INSTITUTION_PURPOSE
PURPOSE.update(INSTITUTION_PURPOSE)
from readiness_contract import PURPOSE as READINESS_PURPOSE
PURPOSE.update(READINESS_PURPOSE)

def enrich(spec, f):
    schemas = spec['components']['schemas']
    for schema_name,titles in {'CreateBorrower':['Business borrower','Consumer borrower'],'BaselineInput':['Existing risk package','Explicit portfolio baseline'],'RiskPackage':['Insights risk package','Signal risk package'],'CreateExport':['Risk-package export','Evidence export','Billing export']}.items():
        for branch,title in zip(schemas[schema_name]['oneOf'],titles):branch['title']=title
    for name in ['EmbeddingSession','Connection','Origination','Alert','Export']:
        schemas[name]['properties']['record_version']={'type':'integer','minimum':1,'description':'Monotonic version for this resource; compare with event.resource_version.'}
        schemas[name]['required'].append('record_version')
    schemas['UploadDocument']['properties']['file']['contentMediaType']='application/octet-stream'
    schemas['BillingTransaction']['properties']['related_transaction_id']={'anyOf':[{'type':'string','minLength':1},{'type':'null'}],'description':'Original immutable transaction corrected or reversed by this entry; null otherwise.'}
    schemas['BillingTransaction']['required'].append('related_transaction_id')
    f['BillingTransaction']['related_transaction_id']=None
    schemas['Error']['properties']['code']['enum'].append('idempotency_result_expired')
    # Stable public names for normalized evidence types; these are product data,
    # not source endpoints. Preserve the complete inherited field definitions.
    # Declare exact output schemas for report files, without separate report APIs.
    source=json.loads((ROOT/'data/normalized-schema-source.json').read_text())
    def copy_financial(name):
        target='Financial'+name
        if target in spec['components']['schemas']:return target
        def rewrite(v):
            if isinstance(v,dict):
                out={}
                for key,val in v.items():
                    if key=='$ref':out[key]='#/components/schemas/'+copy_financial(val.rsplit('/',1)[-1])
                    else:out[key]=rewrite(val)
                return out
            if isinstance(v,list):return [rewrite(x) for x in v]
            return v
        spec['components']['schemas'][target]={}
        spec['components']['schemas'][target]=rewrite(source['components']['schemas'][name])
        return target
    for name,resource in [('RatesExport','BillingRateCard'),('WorkloadExport','WorkloadReport')]:
        resource=copy_financial(resource)
        spec['components']['schemas'][name]={'type':'object','additionalProperties':False,'required':['schema_version','report_type','snapshot_id','as_of','rows'],'properties':{
            'schema_version':{'const':'1.0.0'},'report_type':{'const':'rates' if name=='RatesExport' else 'workload'},'snapshot_id':{'type':'string','minLength':1},'as_of':{'type':'string','format':'date-time'},'rows':{'type':'array','items':{'$ref':'#/components/schemas/'+resource}}}}
    spec['components']['schemas']['EvidenceExport']={'type':'object','additionalProperties':False,'required':['schema_version','evidence_set_id','rows'],'properties':{'schema_version':{'const':'1.0.0'},'evidence_set_id':{'type':'string','minLength':1},'rows':{'type':'array','items':{'$ref':'#/components/schemas/Evidence'}}}}
    schemas['DataExport']={'type':'object','additionalProperties':False,'required':['schema_version','snapshot_id','rows'],'properties':{'schema_version':{'const':VERSION},'snapshot_id':{'type':'string','minLength':1},'rows':{'type':'array','items':{'$ref':'#/components/schemas/DataRecord'}}}}
    spec['x-export-schemas']={'data':'#/components/schemas/DataExport','risk_package':'#/components/schemas/RiskPackage','evidence':'#/components/schemas/EvidenceExport','rates':'#/components/schemas/RatesExport','workload':'#/components/schemas/WorkloadExport'}
    # Keep all downloadable financial schemas discoverable in the same contract.
    for report, filename in [('usage','usage'),('credits','ledger'),('statements','statement'),('funding','funding')]:
        document=json.loads((ROOT/('downloads/report-schemas/'+filename+'.schema.json')).read_text())
        def rewrite_report(value):
            if isinstance(value,dict):
                return {key:('#/components/schemas/Report'+child.rsplit('/',1)[-1] if key=='$ref' else rewrite_report(child)) for key,child in value.items()}
            if isinstance(value,list):return [rewrite_report(child) for child in value]
            return value
        for name, schema in document['components']['schemas'].items():schemas['Report'+name]=rewrite_report(schema)
        spec['x-export-schemas'][report]='#/components/schemas/Report'+document['$ref'].rsplit('/',1)[-1]
    for op in operations():
        entry=spec['paths'][op['path']][op['method'].lower()]
        entry['description']=PURPOSE.get(op['id'],entry['summary']+'.')+' All IDs and cursors must belong to the authorized workspace and environment.'
        entry['description']+=' Required scope: '+op['scope']+'.' if op['scope']!='public' else ' No API key is required.'
        if op['id'] in ['createExport','getExport','downloadExport']:
            entry['description']+=' Data exports require data:read and source authorization; risk-package exports require results:read; billing exports require billing:read and Owner authority; evidence exports require evidence:read and source entitlements. Permissions are checked at creation, retrieval and download.'
        if op['group']=='Billing':entry['description']+=' Owner authority is required. Related reads can pin snapshot_id from billing summary to reconcile the same as-of state; expired snapshots return 410, never a silent refresh.'
        if op['id'] in ['listEvents','getEvent','listDeliveries','replayEvent']:
            entry['description']+=' Billing notifications require billing:read and current Owner authority in addition to event access. Data notifications require data:read. Lists and replays must not reveal unauthorized resource metadata.'
        entry['summary']=entry['summary'].replace('List borrower','List borrowers').replace('List origination','List originations').replace('List monitor','List monitor')
        if op['id']=='listLendingProductVersion':entry['summary']='List lending product versions'
        if op['id']=='listRiskPolicyVersion':entry['summary']='List risk policy versions'
        if op['id']=='listMonitor':entry['summary']='List monitors'
        data=deepcopy(f[op['response']])
        if op['id']=='createOrigination':data.update(status='accepted',risk_package_id=None)
        if op['id']=='createMonitor':data.update(status='initializing',latest_package_id=None,next_evaluation_at=None,deal=f['CreateMonitor']['deal'],latest_deal_snapshot_id='ds_initial')
        if op['id']=='updateMonitor':data.update(status='paused',record_version=2,next_evaluation_at=None)
        if op['id']=='revokeConsent':data.update(status='revoked',revoked_at='2026-11-06T12:00:00Z')
        if op['id']=='uploadDocument':data.update(status='processing')
        if op['id']=='downloadExport':data.update(mime_type='application/json')
        result={'data':[data] if op['many'] else data,'meta':{'request_id':'req_synthetic','schema_version':VERSION,'environment':'sandbox'}}
        if op['many']:
            result['page']={'next_cursor':None,'has_more':False,**({'resume_cursor':'resume_synthetic'} if op['id'] in ['listEvents','listDataChanges'] else {'snapshot_id':'snap_synthetic'})}
            if op['id']=='listDataRecords':result['page'].update(as_of='2026-11-06T12:00:00Z',changes_cursor='data_cursor_synthetic')
        for status,response in entry['responses'].items():
            if status.startswith('2'):
                response['content']['application/json']['example']=result
            else:
                code={'400':'validation_error','401':'unauthenticated','402':'insufficient_credits','403':'forbidden','404':'not_found','409':'idempotency_conflict' if op['method']=='POST' else 'invalid_state','410':'cursor_expired','412':'precondition_failed','422':'validation_error','429':'rate_limited','503':'temporarily_unavailable'}[status]
                response['content']['application/json']['example']={'error':{'code':code,'message':code.replace('_',' ').capitalize()+'.','retryable':status in ['429','503'],'request_id':'req_synthetic','field':None}}
                if status in ['429','503']:response['headers']={'Retry-After':{'description':'Minimum delay in seconds before retry.','schema':{'type':'integer','minimum':0}}}
        if op['request']:
            media=next(iter(entry['requestBody']['content']))
            entry['requestBody']['content'][media]['example']=f[op['request']]
    from readiness_contract import enrich as readiness_enrich
    return readiness_enrich(spec, f)


def sample_params(op, entry):
    values={'id':'record_synthetic','borrower_id':'bor_synthetic','evidence_set_id':'es_synthetic','operation_id':'createOrigination','idempotency_key':'origination-synthetic-0042','cursor':'data_cursor_synthetic'}
    return {p['name']:values.get(p['name'],'synthetic') for p in entry['parameters'] if p['in']=='query' and p.get('required',False)}


def code_samples(op, entry, f):
    path=op['path'].replace('{id}','record_synthetic')
    query=sample_params(op,entry)
    from urllib.parse import urlencode
    if query:path+='?'+urlencode(query)
    headers={'Accept':'application/json'}
    if op['method']=='POST':headers['Idempotency-Key']=op['id']+'-synthetic-0042'
    if op['method']=='PATCH':headers['If-Match']='"1"'
    body=f.get(op['request'])
    multipart=op['request']=='UploadDocument'
    if body and not multipart:headers['Content-Type']='application/json'
    curl=f'curl --request {op["method"]} --fail-with-body --max-time 30 \\\n  "${{AMLOK_API_BASE_URL}}{path}"'
    if op['scope']!='public':curl+=' \\\n  --header "Authorization: Bearer ${AMLOK_API_KEY}"'
    for key,value in headers.items():curl+=' \\\n  --header '+shlex.quote(key+': '+value)
    if multipart:
        for key,value in body.items():curl+=' \\\n  --form '+shlex.quote(key+'='+('@/path/to/financial-statement.pdf' if key=='file' else value))
    elif body:curl+=' \\\n  --data '+shlex.quote(json.dumps(body,separators=(',',':')))
    py='import os\nimport requests\n\n'
    py+='headers = '+repr(headers)+'\n'
    if op['scope']!='public':py+='headers["Authorization"] = "Bearer " + os.environ["AMLOK_API_KEY"]\n'
    if multipart:
        py+='with open("/path/to/financial-statement.pdf", "rb") as upload:\n    response = requests.request('+repr(op['method'])+', os.environ["AMLOK_API_BASE_URL"] + '+repr(path)+', headers=headers, data='+repr({k:v for k,v in body.items() if k!='file'})+', files={"file": upload}, timeout=30, allow_redirects=False)\n'
    else:
        py+='response = requests.request('+repr(op['method'])+', os.environ["AMLOK_API_BASE_URL"] + '+repr(path)+', headers=headers'+(', json='+repr(body) if body else '')+', timeout=30, allow_redirects=False)\n'
    py+='response.raise_for_status()\nprint(response.json())\n'
    js=('import { readFile } from "node:fs/promises";\n' if multipart else '')+'const headers = '+json.dumps(headers)+';\n'
    if op['scope']!='public':js+='headers.Authorization = `Bearer ${process.env.AMLOK_API_KEY}`;\n'
    if multipart:
        js+='const form = new FormData();\nform.append("file", new Blob([await readFile("/path/to/financial-statement.pdf")]), "financial-statement.pdf");\n'
        for k,v in body.items():
            if k!='file':js+='form.append('+json.dumps(k)+', '+json.dumps(v)+');\n'
    js+='const response = await fetch(process.env.AMLOK_API_BASE_URL + '+json.dumps(path)+', {\n  method: '+json.dumps(op['method'])+', headers, redirect: "error", signal: AbortSignal.timeout(30000)'+(',\n  body: '+('form' if multipart else 'JSON.stringify('+json.dumps(body)+')') if body else '')+'\n});\nif (!response.ok) throw new Error(`HTTP ${response.status}: ${await response.text()}`);\nconsole.log(await response.json());\n'
    return [{'lang':'Shell','label':'cURL','source':curl},{'lang':'Python','source':py},{'lang':'JavaScript','source':js}]


def build():
    review()
    f=fixtures(); source=json.loads((ROOT/'data/normalized-schema-source.json').read_text())
    base_spec=build_spec(source)
    from verification_examples import examples as verification_examples
    f['RiskPackage']['verification']=verification_examples(base_spec['components']['schemas'])['business']
    f['RiskPackage']['evidence_set']['count']+=1
    f['RiskPackage']['document_ids'].append('doc_registry_synthetic')
    spec=enrich(base_spec,f)
    from scale_contract import extend as scale_contract
    spec=scale_contract(spec,f)
    from sandbox_contract import extend as sandbox_contract
    sandbox_operations=sandbox_contract(spec,f)
    from data_model_alignment import annotate_fields
    annotate_fields(spec)
    groups=OrderedDict(); index=[]; items=[]
    for op in operations()+sandbox_operations:
        if op['id']=='downloadExport':op={**op,'request':'ExportDownloadPurpose','response':'ExportDownloadLink'}
        entry=spec['paths'][op['path']][op['method'].lower()]
        entry['x-codeSamples']=code_samples(op,entry,f)
        page='api-reference/endpoints/'+slug(op['group'])+'/'+slug(op['id'])
        path=ROOT/(page+'.mdx');path.parent.mkdir(parents=True,exist_ok=True)
        scopes='Public endpoint; no API key required.' if op['scope']=='public' else 'Required scope: `'+op['scope']+'`.'
        path.write_text('---\ntitle: '+json.dumps(entry['summary'])+'\ndescription: '+json.dumps(PURPOSE.get(op['id'],entry['summary']+'.'))+'\nopenapi: '+json.dumps('/openapi/amlok.json '+op['method']+' '+op['path'])+'\n---\n\n'+entry['description']+'\n\nExamples use synthetic IDs. Replace them with values returned by your environment.\n')
        groups.setdefault(op['group'],[]).append(page)
        index.append({**op,'page':page})
        headers=[{'key':'Accept','value':'application/json'}]
        if op['method']=='POST':headers.append({'key':'Idempotency-Key','value':op['id']+'-{{command_reference}}'})
        if op['method']=='PATCH':headers.append({'key':'If-Match','value':'{{record_etag}}'})
        params=sample_params(op,entry)
        request={'method':op['method'],'header':headers,'url':{'raw':'{{base_url}}'+op['path'].replace('{id}','{{record_id}}')+('?'+'&'.join(k+'='+v for k,v in params.items()) if params else ''),'host':['{{base_url}}'],'path':op['path'].replace('{id}','{{record_id}}').strip('/').split('/'),'query':[{'key':k,'value':v} for k,v in params.items()]},'description':entry['description']}
        if op['scope']=='public':request['auth']={'type':'noauth'}
        if op['request']:
            if op['request']=='UploadDocument':request['body']={'mode':'formdata','formdata':[{'key':k,'type':'file','src':''} if k=='file' else {'key':k,'type':'text','value':v} for k,v in f[op['request']].items()]}
            else:
                headers.append({'key':'Content-Type','value':'application/json'});request['body']={'mode':'raw','raw':json.dumps(f[op['request']],indent=2),'options':{'raw':{'language':'json'}}}
        status,response=next((s,r) for s,r in entry['responses'].items() if s.startswith('2'))
        items.append({'name':entry['summary'],'request':request,'response':[{'name':'Synthetic success','originalRequest':deepcopy(request),'status':'Accepted' if status=='202' else 'OK','code':int(status),'header':[{'key':'Content-Type','value':'application/json'}],'body':json.dumps(response['content']['application/json']['example'],indent=2)}]})
    spec['webhooks']['resourceEvent']['post']['requestBody']['content']['application/json']['example']=f['Event']
    save('openapi/amlok.json',spec)
    save('data/api-reference-index.json',index)
    save('data/product-api-examples.json',f)
    save('downloads/risk-package-example.json',f['RiskPackage'])
    save('downloads/amlok-api.postman_collection.json',{'info':{'name':'AMLOK API '+VERSION,'schema':'https://schema.getpostman.com/json/collection/v2.1.0/collection.json','description':str(len(index))+'-operation product API contract. Set the institution-issued base_url and API key in a private environment. All sample identifiers are synthetic. Fresh command_reference for each new action; preserve it for retries.'},'auth':{'type':'bearer','bearer':[{'key':'token','value':'{{api_key}}','type':'string'}]},'variable':[{'key':k,'value':v} for k,v in {'base_url':'','api_key':'','record_id':'record_synthetic','record_etag':'"1"','command_reference':'replace-for-each-new-command'}.items()],'item':items})
    from current_api_guides import write_guides, navigation
    write_guides(spec,f,index)
    navigation(groups)
    from readiness_guides import write_guides as readiness_guides
    readiness_guides(spec, f, index)
    from risk_package_guides import write_guides as risk_guides
    risk_guides(spec, f, index)
    from verification_guides import write_guides as verification_guides
    verification_guides(spec, f, index)
    from scale_guides import write_guides as scale_guides
    scale_guides(spec, f, index)
    from data_model_alignment import write_guides as model_guides
    model_guides(spec)
    from sandbox_guides import write_guides as sandbox_guides
    sandbox_guides(spec,index)
    print(f'Generated primary API {VERSION}: {len(index)} operations, endpoint pages and Postman requests.')

if __name__=='__main__':build()

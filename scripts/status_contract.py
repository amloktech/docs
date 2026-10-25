"""Public, read-only availability endpoints for the documentation contract."""
from copy import deepcopy
import json

STATUS_OPERATION_IDS = {'/v1/healthcheck':'ST001','/v1/service-status':'ST002'}

def extend(g):
    spec,schemas=g['SPEC'],g['SCHEMAS']
    timestamp={'type':'string','format':'date-time'}
    states=['operational','degraded','partial_outage','major_outage','maintenance','unknown']
    schemas['Healthcheck']={'type':'object','additionalProperties':False,'required':['status','timestamp'],
        'properties':{'status':{'type':'string','enum':['ok','unavailable']},'timestamp':timestamp}}
    schemas['ServiceStatus']={'type':'object','additionalProperties':False,'required':['status','updated_at','services'],
        'properties':{'status':{'type':'string','enum':states},'updated_at':timestamp,
        'services':{'type':'array','items':{'type':'object','additionalProperties':False,
            'required':['id','name','status','updated_at'],
            'properties':{'id':{'type':'string'},'name':{'type':'string'},'status':{'type':'string','enum':states},'updated_at':timestamp}}}}}
    definitions=[
        ('/v1/healthcheck','Healthcheck','Healthcheck',{'status':'ok','timestamp':g['NOW']},
         'Public unauthenticated readiness check for the AMLOK API. HTTP 200 with status ok means the API can accept requests; HTTP 503 with status unavailable means it cannot. No borrower or tenant data is exposed. This is a point-in-time check, not confirmation that a job completed, an integration is current, or every product is operational.'),
        ('/v1/service-status','Service status','ServiceStatus',{'status':'operational','updated_at':g['NOW'],
            'services':[{'id':i,'name':n,'status':'operational','updated_at':g['NOW']} for i,n in [('api','API'),('insights','AMLOK Insights'),('signal','AMLOK Signal'),('connections','Data connections'),('webhooks','Webhook delivery'),('reporting','Reporting')]]},
         'Public unauthenticated summary of AMLOK service availability. A successful HTTP 200 means the status report was retrieved; inspect the overall and per-service status to understand availability. unknown means a current state cannot be confirmed and must not be treated as operational. updated_at identifies the observation time; do not treat stale or unreachable status as healthy. Provider-specific freshness and account connection errors are separate from AMLOK service availability. This response contains no internal infrastructure identifiers or customer data.'),
    ]
    operations=[]
    for path,title,name,example,description in definitions:
        oid=STATUS_OPERATION_IDS[path];page='api-reference/endpoints/platform/'+title.lower().replace(' ','-')
        samples=g['samples']({'Path':path,'Method':'GET','Operation ID':oid},[],None,'res_example')
        for sample in samples:
            lines=sample['source'].splitlines()
            lines=[line for line in lines if not any(t in line for t in ['Authorization','const apiKey ='])]
            sample['source']='\n'.join(lines).replace('if (!baseUrl || !apiKey) throw new Error("Configure AMLOK_API_BASE_URL and AMLOK_API_KEY");','if (!baseUrl) throw new Error("Configure AMLOK_API_BASE_URL");')
        response={'description':'Current availability observation.','headers':{'Cache-Control':{'schema':{'type':'string'},'example':'no-store'}},
            'content':{'application/json':{'schema':g['ref'](name),'examples':{'synthetic':{'summary':'Illustrative healthy response','value':example}}}}}
        responses={'200':response,'429':{'$ref':'#/components/responses/Error429'}}
        if name=='Healthcheck':
            unavailable=deepcopy(response);unavailable['description']='API is not ready to accept requests.'
            response['content']['application/json']['schema']={'allOf':[g['ref'](name),{'properties':{'status':{'const':'ok'}}}]}
            unavailable['content']['application/json']['schema']={'allOf':[g['ref'](name),{'properties':{'status':{'const':'unavailable'}}}]}
            unavailable['content']['application/json']['examples']={'unavailable':{'value':{'status':'unavailable','timestamp':g['NOW']}}}
            responses['503']=unavailable
        else:
            responses['503']={'$ref':'#/components/responses/Error503'}
        spec['paths'][path]={'get':{'operationId':oid,'summary':title,'description':description,'tags':['Platform'],
            'security':[],'x-required-scopes':[],'parameters':[],'x-codeSamples':samples,'responses':responses}}
        g['NAV_GROUPS']['Platform'].insert(len(operations),page)
        request={'method':'GET','auth':{'type':'noauth'},'header':[{'key':'Accept','value':'application/json'}],'url':'{{base_url}}'+path,'description':description}
        g['POSTMAN_GROUPS']['Platform'].insert(len(operations),{'name':title,'request':request,'response':[{'name':'Illustrative 200','originalRequest':deepcopy(request),'status':'OK','code':200,'header':[{'key':'Content-Type','value':'application/json'}],'body':g['dump'](example)}]})
        notes='**Authentication:** public; no API key required.\n\n'+description+'\n\nUse your institution-issued `AMLOK_API_BASE_URL`. Responses use the lightweight status schema shown here, without the financial-data `data` / `meta` envelope. An unavailable status is not a valid zero-risk result.\n\nUse bounded polling with backoff and respect `Retry-After` on `429`. Contact [support](/support/create-ticket) with the observation time and affected workflow when an issue persists. See the [SLA](/support/sla) for availability measurement.\n'
        g['write'](page+'.mdx','---\ntitle: '+json.dumps(title)+'\nopenapi: '+json.dumps('/openapi/amlok-v1.json GET '+path)+'\nplayground: simple\n---\n\n'+notes)
        entry={'id':oid,'method':'GET','path':path,'title':title,'scope':'','group':'Platform','page':page,'resource':None,'request':None,'response':example,'success':'200'}
        g['OP_INDEX'].append(entry);operations.append(entry)
    return operations

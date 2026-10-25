"""Read-only discovery of frozen input manifests and approved monitoring baselines."""
from copy import deepcopy
from urllib.parse import urlencode
import json

def extend(g):
    S,E,spec=g['SCHEMAS'],g['EXAMPLES'],g['SPEC']
    text={'type':'string','minLength':1}
    timestamp={'type':'string','format':'date-time'}
    date={'type':'string','format':'date'}
    common={'id':text,'object':text,'workspace_id':text,'subject_id':text,
        'created_at':timestamp,'updated_at':timestamp,'record_version':{'type':'integer','minimum':1},
        'status':{'type':'string','enum':['ready','superseded','revoked']}}
    manifests={**common,'window_start':date,'window_end':date,
        'record_count':{'type':'integer','minimum':0},
        'source_connection_ids':{'type':'array','items':text},
        'sha256':{'type':'string','pattern':'^[a-f0-9]{64}$'}}
    baselines={**common,'snapshot_id':text,'input_manifest_id':text,'approved_at':timestamp}
    for name,properties in [('InputManifest',manifests),('MonitoringBaseline',baselines)]:
        S[name]={'type':'object','additionalProperties':False,'properties':properties,'required':list(properties)}
    shared={'workspace_id':'wsp_example','subject_id':'biz_example','created_at':g['NOW'],
        'updated_at':g['NOW'],'record_version':1,'status':'ready'}
    E['InputManifest']={**shared,'id':'manifest_example','object':'input_manifest','window_start':'2025-10-01',
        'window_end':'2026-10-01','record_count':72000,'source_connection_ids':['cnn_example'],'sha256':'a'*64}
    E['MonitoringBaseline']={**shared,'id':'baseline_example','object':'monitoring_baseline','snapshot_id':'rsk_baseline',
        'input_manifest_id':'manifest_example','approved_at':g['NOW']}
    operations=[]
    for path,title,name,scope,prefix in [
        ('/v1/input-manifests','input manifests','InputManifest','risk:read','BM'),
        ('/v1/monitoring-baselines','monitoring baselines','MonitoringBaseline','monitoring:read','BB'),
    ]:
        for index,is_list in enumerate([True,False],1):
            route=path if is_list else path+'/{id}'
            heading=('List '+title) if is_list else ('Retrieve '+title[:-1])
            oid=prefix+str(index).zfill(3)
            page='api-reference/endpoints/risk/'+heading.lower().replace(' ','-')
            example=deepcopy(E[name])
            params=[]
            if is_list:
                params=[g['parameter']('subject_id','query','id','Required authorized borrower/business in the key-bound workspace.',True,'biz_example'),
                    g['parameter']('status','query','string','Lifecycle filter. Use ready for new calculations or monitor creation.',False,'ready',enum=['ready','superseded','revoked']),
                    g['parameter']('limit','query','integer','Page size; default 100, maximum 200.',False,100,minimum=1,maximum=200,default=100),
                    g['parameter']('cursor','query','string','Opaque cursor bound to filters and snapshot.',False)]
            else:
                params=[g['parameter']('id','path','id','Identifier in the authorized workspace.',True,example['id'])]
            if name=='InputManifest':
                description='Read an immutable evidence manifest prepared by AMLOK from synchronized, borrower-permissioned records. window_start is inclusive and window_end exclusive. record_count covers the frozen input set; sha256 identifies its content. Manifest reads do not expose payment controls or create a charge. Use the ready manifest id as input_manifest_id when calculating attributes for the same subject and a window contained within the manifest. Superseded or revoked manifests cannot authorize new calculations.'
            else:
                description='Read an approved monitoring baseline prepared by AMLOK from a completed assessment or the agreed existing-portfolio onboarding process. Use its snapshot_id, not the baseline record id, as baseline_snapshot_id when creating a monitor. Retrieve that risk snapshot for the baseline evidence and attributes. Only ready baselines for the same subject and workspace can initialize a monitor. This read does not launch or charge an Insights underwriting. Signal change-driven reassessment remains included in Signal.'
            description+=' The API key identifies exactly one workspace, institution and environment. All linked resources must belong to that workspace and subject; caller-supplied workspace selectors cannot override authorization.'
            schema,response=g['envelope'](g['ref'](name),example,is_list)
            response['meta']=g['meta']('complete')
            if is_list: response['page']={'has_more':False,'next_cursor':None,'limit':100}
            sample_path=route.replace('{id}',example['id'])
            query={p['name']:p['example'] for p in params if p['in']=='query' and p.get('example') is not None}
            if query: sample_path+='?'+urlencode(query)
            samples=g['samples']({'Method':'GET','Path':sample_path,'Operation ID':oid},params,None,example['id'])
            responses={'200':{'description':'Authorized baseline metadata. An empty list means no matching baseline is available.',
                'headers':{'X-Request-ID':{'schema':{'type':'string'}}},
                'content':{'application/json':{'schema':schema,'examples':{'synthetic':{'value':response}}}}}}
            for status in ['400','401','403','404','429','500','503']:
                responses[status]={'$ref':'#/components/responses/Error'+status}
            spec['paths'][route]={'get':{'operationId':oid,'summary':heading,'description':description,'tags':['Risk'],
                'parameters':params,'security':[{'BearerAuth':[]}],'x-required-scopes':[scope],'x-codeSamples':samples,'responses':responses}}
            g['NAV_GROUPS']['Risk'].append(page)
            g['write'](page+'.mdx','---\ntitle: '+json.dumps(heading)+'\nopenapi: '+json.dumps('/openapi/amlok-v1.json GET '+route)+'\nplayground: simple\n---\n\n**Required scope:** '+scope+'\n\n'+description+'\n\nIf the list is empty, finish evidence synchronization and the agreed assessment or baseline onboarding process. Do not fabricate an identifier or treat missing baseline data as zero risk.\n\n[Baseline workflow](/api-reference/workflows#monitor-and-investigate) · [Authentication](/api-reference/authentication)\n')
            request={'method':'GET','header':[{'key':'Accept','value':'application/json'}],'url':'{{base_url}}'+sample_path,'description':description}
            g['POSTMAN_GROUPS']['Risk'].append({'name':heading,'request':request,'response':[{'name':'Synthetic 200','originalRequest':deepcopy(request),'status':'OK','code':200,'header':[{'key':'Content-Type','value':'application/json'}],'body':g['dump'](response)}]})
            entry={'id':oid,'method':'GET','path':route,'title':heading,'scope':scope,'group':'Risk','page':page,'resource':example['object'],'request':None,'response':response,'success':'200'}
            g['OP_INDEX'].append(entry);operations.append(entry)
    g['write']('data/baseline-api-index.json',g['dump'](operations))
    g['REFINEMENTS'].append('Added read-only manifest and monitoring-baseline discovery. Ready manifests feed attribute calculations; ready baseline snapshot_id initializes a monitor. All IDs are bound to one workspace and subject, and reads do not trigger another underwriting charge.')
    return operations

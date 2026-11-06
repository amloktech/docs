"""Enterprise transport and capacity contract; extends the same 57 operations."""
from copy import deepcopy
import hashlib
import json
from product_api_review import obj, ref, text, enum, array, nullable

REVISION = '2026-11-06.enterprise.1'
CAPACITY = {
 'max_in_flight_requests': 16,
 'workloads': [dict(group=g, max_running=r, max_queued=q, max_queue_wait_seconds=600, max_processing_seconds=1800) for g,r,q in [('origination',4,100),('monitoring',8,200),('export',2,20)]],
 'targets': [dict(group=g, percentile=95, elapsed_seconds=300, population='admitted_ready_work', window_seconds=2592000) for g in ['origination','monitoring','export']],
}
TRANSPORT = {'max_response_bytes':2097152,'max_export_bytes':68719476736,'export_part_bytes':8388608,'max_page_items':100}

def section_definitions(s):
 out={}
 p=s['RiskPackage']['properties']
 for k,v in p.items():
  if v.get('type')=='array':out[k]=(v['items'],None)
 for k,v in p['analyses']['properties'].items():
  name=v['$ref'].split('/')[-1]; out['analyses.'+k]=(s[name]['properties']['items']['items'],name)
 for k,v in s['VerificationAssessment']['properties'].items():
  if v.get('type')=='array':out['verification.'+k]=(v['items'],None)
  elif '$ref' in v:
   name=v['$ref'].split('/')[-1]
   if 'items' in s[name].get('properties',{}):out['verification.'+k]=(s[name]['properties']['items']['items'],name)
 return out

def section_value(package,key):
 value=package
 for part in key.split('.'):value=value[part]
 return value['items'] if isinstance(value,dict) else value

def summary(package,sections):
 return {'view':'summary', **{k:deepcopy(package[k]) for k in ['id','borrower_id','product','created_at','as_of','record_version','origination_id','monitoring_run_id','catalog_version','completeness']},
  'evidence_set_id':package['evidence_set']['id'],
  'sections':[{'section':key,'item_count':len(section_value(package,key))} for key in sections],
  'export_request':{'kind':'risk_package','risk_package_id':package['id'],'format':'json'}}

def section_page(package,key,sections):
 value=package
 for part in key.split('.'):value=value[part]
 metadata={k:v for k,v in value.items() if k!='items'} if isinstance(value,dict) else None
 items=section_value(package,key)
 return {'view':'section','risk_package_id':package['id'],'record_version':1,'section':key,'section_metadata':deepcopy(metadata),'items':deepcopy(items[:25]),'total_items':len(items)}

def extend(spec,f):
 s=spec['components']['schemas']
 integer=lambda desc,minimum=1:{'type':'integer','minimum':minimum,'maximum':9007199254740991,'description':desc}
 stamp=lambda:text(format='date-time')
 groups=['origination','monitoring','export']
 s['WorkloadCapacity']=obj({'group':enum(*groups),'max_running':integer('Maximum concurrently executing work in this group, shared by all keys in this workspace/environment.'),'max_queued':integer('Maximum accepted waiting jobs, excluding jobs waiting for credits or borrower action.',0),'max_queue_wait_seconds':integer('Maximum cumulative ready-queue wait for an accepted job.'),'max_processing_seconds':integer('Maximum cumulative running wall time including upstream waiting and internal retries; excludes credit/action pauses.')})
 s['ProcessingTarget']=obj({'group':enum(*groups),'percentile':{'type':'integer','enum':[95,99]},'elapsed_seconds':integer('Configured target for ready-to-terminal elapsed time including queueing. A target is not a measured result or an availability SLA.'),'population':{'const':'admitted_ready_work'},'window_seconds':integer('Rolling measurement period. Pauses for action/credits are excluded; provider waiting while running is included. Timed-out jobs count as target misses.')})
 s['CapacityProfile']=obj({'max_in_flight_requests':integer('Shared in-flight HTTP requests across all keys. Accepted background jobs have separate workload limits.'),'workloads':array(ref('WorkloadCapacity'),minItems=3,maxItems=3),'targets':array(ref('ProcessingTarget'),minItems=3,maxItems=6)},description='Exactly one workload capacity per group; at least one target per group and no duplicate group/percentile pair. Capacity is per workspace/environment; rotating or adding keys does not multiply it.')
 s['CapacityProfile']['properties']['workloads']['allOf']=[{'contains':{'properties':{'group':{'const':g}},'required':['group']},'minContains':1,'maxContains':1} for g in groups]
 s['CapacityProfile']['properties']['targets']['allOf']=[{'contains':{'properties':{'group':{'const':g}},'required':['group']},'minContains':1} for g in groups]+[{'contains':{'properties':{'group':{'const':g},'percentile':{'const':p}},'required':['group','percentile']},'minContains':0,'maxContains':1} for g in groups for p in [95,99]]
 p=s['OperationalProfile'];p['properties']['capacity']=ref('CapacityProfile');p['required'].append('capacity')
 for k,v in TRANSPORT.items():p['properties'][k]=integer({'max_response_bytes':'Maximum uncompressed UTF-8 JSON response bytes including envelope; no silent truncation.','max_export_bytes':'Maximum complete uncompressed export bytes. A larger export fails explicitly without a partial completed artifact.','export_part_bytes':'Maximum bytes per export part; parts concatenate byte-for-byte to the complete file.','max_page_items':'Collection and risk-section page limit. The API hard ceiling is 100.'}[k]);p['required'].append(k)
 p['properties']['max_page_items']['maximum']=100
 s['ContractPolicy']=obj({'revision':text('Descriptive revision of this single /v1 contract; not a version negotiation header.'),'schema_version':text('Current response schema revision.'),'compatibility':{'const':'additive_fields_only'},'enum_policy':{'const':'closed_within_v1'},'change_notice_days':integer('Institution-agreed minimum advance notice for disruptive configuration or contractual changes. Security revocation may take effect immediately.',0),'notice_channel':{'const':'registered_technical_contacts'},'documentation_url':text(format='uri')})
 s['Configuration']['properties']['contract']=ref('ContractPolicy');s['Configuration']['required'].append('contract')
 profile=deepcopy(f['Configuration']['operational_profile']);profile.update(TRANSPORT,capacity=deepcopy(CAPACITY));profile['version']='2'
 f['Configuration']['operational_profile']=profile
 f['Configuration']['contract']={'revision':REVISION,'schema_version':spec['info']['version'],'compatibility':'additive_fields_only','enum_policy':'closed_within_v1','change_notice_days':30,'notice_channel':'registered_technical_contacts','documentation_url':'https://docs.amlok.io/api-reference/client-compatibility'}
 s['Error']['properties']['code']['enum']+=['capacity_exceeded','queue_full','queue_wait_exceeded','processing_deadline_exceeded','response_too_large','export_too_large','export_expired','invalid_export_part']
 s['CapacityErrorDetail']=obj({'group':enum('http',*groups),'reason':enum('in_flight_limit','queue_full'),'limit':integer('Effective admission limit.',0),'profile_id':text(),'profile_version':text()})
 s['Error']['properties']['capacity']=ref('CapacityErrorDetail')
 # Exact-record exports provide a fallback for individual oversized source payloads.
 ce=s['CreateExport'];ce['properties']['data_record_id']=text('Exact immutable DataRecord version, alternative to data_snapshot_id for kind=data.')
 for branch in ce['oneOf']:
  if branch['properties']['kind']['const']=='data':
   branch['required']=[]
   branch['oneOf']=[{'required':['data_snapshot_id'],'not':{'required':['data_record_id']}},{'required':['data_record_id'],'not':{'required':['data_snapshot_id']}}]
  else:branch['not']['anyOf'].append({'required':['data_record_id']})
 s['LargeResponseRecovery']=obj({'export_request':ref('CreateExport'),'summary_available':{'type':'boolean'},'snapshot_expires_at':nullable(stamp())},description='Complete authorized export source captured before the failed response. Existing export scopes and source permissions still apply. Snapshot expiry is null for immutable package/record sources; create snapshot exports before expiry.')
 s['DataCheckpoint']=obj({'snapshot_id':text(),'as_of':stamp(),'changes_cursor':text(),'expires_at':stamp()},description='Atomic data snapshot and feed boundary retained even when the first record exceeds the response limit.')
 s['LargeResponseRecovery']['properties']['data_checkpoint']=nullable(ref('DataCheckpoint'))
 s['LargeResponseRecovery']['required'].append('data_checkpoint')
 s['Error']['properties']['recovery']=ref('LargeResponseRecovery')
 s['Error'].setdefault('allOf',[]).extend([
  {'if':{'properties':{'code':{'const':'response_too_large'}}},'then':{'required':['recovery'],'properties':{'retryable':{'const':False}}}},
  {'if':{'properties':{'code':{'enum':['capacity_exceeded','queue_full']}}},'then':{'required':['capacity'],'properties':{'retryable':{'const':True}}}},
 ])
 # One completed artifact with a fixed-size byte-part layout, not an unbounded manifest.
 s['ExportArtifact']=obj({'id':text('Immutable artifact identity, stable across renewed links.'),'total_bytes':integer('Complete file bytes, before any HTTP content encoding.'),'sha256':text('SHA-256 of the concatenated complete file.',pattern='^[a-f0-9]{64}$'),'mime_type':text(),'part_count':integer('ceil(total_bytes / part_size_bytes).'),'part_size_bytes':integer('Fixed byte size except the final part; frozen when the export is accepted.'),'row_count':integer('Number of exported top-level records; one for a risk package.',0),'schema_version':text(),'source_snapshot_id':nullable(text('Frozen collection/report snapshot when applicable.'))},description='Completed exports are immutable. Concatenate parts in numerical order before interpreting JSON/CSV/PDF. Part boundaries can split JSON tokens, CSV records or UTF-8 sequences; use a streaming decoder/parser across boundaries.')
 s['Export']['properties']['artifact']=nullable(ref('ExportArtifact'));s['Export']['required'].append('artifact')
 s['Export'].setdefault('allOf',[]).append({'if':{'properties':{'status':{'const':'completed'}}},'then':{'properties':{'artifact':ref('ExportArtifact')}},'else':{'properties':{'artifact':{'type':'null'}}}})
 s['ExportDownloadPurpose']=obj({'purpose':text('Authorized reason for accessing the export.'),'part_number':integer('One-based part number. Defaults to 1; iterate through artifact.part_count.')},required=['purpose']);s['ExportDownloadPurpose']['properties']['part_number']['default']=1
 s['ExportDownloadLink']=deepcopy(s['DownloadLink']);s['ExportDownloadLink']['properties'].update({'artifact_id':text(),'part_number':integer('Requested one-based part.'),'byte_offset':integer('Zero-based offset in complete artifact.',0),'byte_length':integer('Length of this part.'),'etag':text('Quoted strong ETag for this part. Use If-Match with Range to resume; never append a full 200 response to a partial file.')});s['ExportDownloadLink']['required']+=['artifact_id','part_number','byte_offset','byte_length','etag']
 s['ExportDownloadLink']['description']='sha256 covers this part; artifact.sha256 covers the complete concatenation. HTTPS GET supports single byte Range within this part (206 with Content-Range), If-Match (412 on mismatch), and 416 outside the part. Request identity encoding. Links recheck authorization and may expire before artifact retention.'
 f['Export']['artifact']=None
 # Bounded summary and separately paged sections on the existing result route.
 sections=section_definitions(s)
 summary_props={k:deepcopy(s['RiskPackage']['properties'][k]) for k in ['id','borrower_id','product','created_at','as_of','record_version','origination_id','monitoring_run_id','catalog_version','completeness']}
 summary_props.update({'view':{'const':'summary'},'evidence_set_id':text(),'sections':array(obj({'section':enum(*sections),'item_count':integer('Complete authorized item count at this package version.',0)}),minItems=len(sections),maxItems=len(sections)),'export_request':ref('CreateExport')})
 s['RiskPackageSummary']=obj(summary_props,description='Compact index of the immutable result. Inspect section status, limitations and required actions before making a decision. Summary never substitutes for an assessment or a complete package.')
 variants=[];views={'full':{'title':'Complete risk package','schema':obj({'data':ref('RiskPackage'),'meta':ref('Meta')}),'example':{'data':deepcopy(f['RiskPackage']),'meta':{'request_id':'req_synthetic','schema_version':spec['info']['version'],'environment':'sandbox'}}}}
 full_meta=deepcopy(views['full']['example']['meta'])
 views['summary']={'title':'Summary (view=summary)','schema':obj({'data':ref('RiskPackageSummary'),'meta':ref('Meta')}),'example':{'data':summary(f['RiskPackage'],sections),'meta':full_meta}}
 for key,(item,metadata_name) in sections.items():
  name='RiskSection'+''.join(v.title().replace('_','') for v in key.split('.'))
  metadata=deepcopy(s[metadata_name]) if metadata_name else {'type':'null'}
  if metadata_name:
   metadata['properties'].pop('items');metadata['required'].remove('items');metadata.pop('allOf',None)
  s[name]=obj({'view':{'const':'section'},'risk_package_id':text(),'record_version':{'const':1},'section':{'const':key},'section_metadata':metadata,'items':array(item,maxItems=100),'total_items':integer('Count for the complete section, not only this page.',0)})
  variants.append(ref(name))
  example={'data':section_page(f['RiskPackage'],key,sections),'meta':full_meta,'page':{'next_cursor':None,'has_more':False,'snapshot_id':'risk_section_synthetic','expires_at':'2026-11-06T13:00:00Z'}}
  views[key]={'title':key+' (view=section)','schema':obj({'data':ref(name),'meta':ref('Meta'),'page':ref('Page')}),'example':example}
 s['RiskPackageSection']={'oneOf':variants,'discriminator':{'propertyName':'section','mapping':{key:v['$ref'] for key,v in zip(sections,variants)}}}
 op=spec['paths']['/v1/risk-packages/{id}']['get']
 op['parameters'] += [{'name':name,'in':'query','required':False,'schema':schema,'description':desc} for name,schema,desc in [
  ('view',{'type':'string','enum':['full','summary','section'],'default':'full'},'full returns the complete bounded package; summary returns its compact index; section returns one page of a named collection.'),
  ('section',enum(*sections),'Required only with view=section. Names select the documented collection, not arbitrary JSON paths.'),
  ('cursor',text(),'Section cursor binds package, section and current authorization. Use only with view=section.'),
  ('limit',{'type':'integer','minimum':1,'maximum':100,'default':25},'Only with view=section. Server may return fewer items to respect max_response_bytes; use has_more, not item count.')]]
 media=op['responses']['200']['content']['application/json'];media['schema']={'oneOf':[views['full']['schema'],views['summary']['schema'],obj({'data':ref('RiskPackageSection'),'meta':ref('Meta'),'page':ref('Page')})]};media['x-response-views']=views
 op['description']+=' Use view=summary for the section index, or view=section with section/cursor/limit for bounded detail. Invalid parameter combinations return 400 validation_error. Full or single-item responses above max_response_bytes return 413 response_too_large with an export source; no fields are silently omitted.'
 spec['x-risk-package-sections']={key:{'items':item,'metadata_schema':metadata} for key,(item,metadata) in sections.items()}
 spec['x-contract-revision']=REVISION
 # Refresh affected response fixtures and add typed capacity/oversize errors.
 for path,methods in spec['paths'].items():
  for method,entry in methods.items():
   oid=entry['operationId']
   if oid=='downloadExport':entry['requestBody']['content']['application/json']['schema']=ref('ExportDownloadPurpose')
   for status,response in entry['responses'].items():
    media=response.get('content',{}).get('application/json',{})
    if status.startswith('2') and 'example' in media:
     data=media['example']['data']
     if oid=='getConfiguration':media['example']['data']=deepcopy(f['Configuration'])
     if oid in ['createExport','getExport']:data['artifact']=None
     if oid=='downloadExport':
      media['schema']=obj({'data':ref('ExportDownloadLink'),'meta':ref('Meta')});data.update(artifact_id='artifact_synthetic',part_number=1,byte_offset=0,byte_length=4096,etag='"part_synthetic"')
      f['ExportDownloadLink']=deepcopy(data);f['ExportDownloadPurpose']=deepcopy(f['DownloadPurpose'])
   if '429' in entry['responses']:
    entry['responses']['429']['description']='Rate budget, shared in-flight limit or ready-queue limit exceeded before admission. Retry-After is mandatory in whole seconds. Preserve command identity. No accepted receipt or charge is created.'
   if oid in ['getRiskPackage','getDataRecord','listDataRecords','getEvidence','listEvidence']:
    source=({'kind':'risk_package','risk_package_id':'rp_synthetic','format':'json'} if oid=='getRiskPackage' else {'kind':'data','data_record_id':'dr_synthetic','format':'json'} if oid=='getDataRecord' else {'kind':'data','data_snapshot_id':'snap_synthetic','format':'json'} if oid=='listDataRecords' else {'kind':'evidence','evidence_set_id':'es_synthetic','format':'json'})
    error={'code':'response_too_large','message':'Retrieve the complete authorized content through an export.','retryable':False,'request_id':'req_synthetic','field':None,'recovery':{'export_request':source,'summary_available':oid=='getRiskPackage','snapshot_expires_at':'2026-11-06T13:00:00Z' if oid=='listDataRecords' else None,'data_checkpoint':{'snapshot_id':'snap_synthetic','as_of':'2026-11-06T12:00:00Z','changes_cursor':'data_cursor_synthetic','expires_at':'2026-11-06T13:00:00Z'} if oid=='listDataRecords' else None}}
    entry['responses']['413']={'description':'Complete response or one indivisible item exceeds max_response_bytes. Use recovery.export_request with existing export permissions. No successful response is truncated.','content':{'application/json':{'schema':obj({'error':ref('Error')}),'example':{'error':error}}}}
 # Example for a completed multi-part export, independently selectable in Data Lookup.
 export_op=spec['paths']['/v1/exports/{id}']['get']['responses']['200']['content']['application/json']
 completed=deepcopy(export_op['example']);completed['data'].update(status='completed',expires_at='2026-11-07T12:00:00Z',failure=None,artifact={'id':'artifact_synthetic','total_bytes':10240,'sha256':'a'*64,'mime_type':'application/json','part_count':3,'part_size_bytes':4096,'row_count':1,'schema_version':spec['info']['version'],'source_snapshot_id':None})
 export_op['x-response-views']={'pending':{'title':'Pending export','schema':export_op['schema'],'example':deepcopy(export_op['example'])},'completed':{'title':'Completed export with download parts','schema':export_op['schema'],'example':completed}}
 return spec

"""Executable requirements for the backend to be built; one public API contract."""
from copy import deepcopy

PURPOSE = {
 'createDealSnapshot': 'Append a complete, immutable lender-supplied snapshot of a monitored deal. Compare previous_snapshot_id atomically; never edit old balances, evidence or assessments. Future Signal runs use the accepted snapshot.',
 'listDealSnapshots': 'List the immutable lender snapshots for this monitor, including its initial enrollment snapshot. Ordered by sequence ascending within a stable snapshot.',
 'getDealSnapshot': 'Retrieve the exact lender input version used by a monitoring run or risk package, including its effective time and previous version.',
}

EVENT_RESOURCES = {
 'embedding_session.completed': ('embedding_session','getEmbeddingSession','connections:read'),
 'connection.action_required': ('connection','getConnection','connections:read'),
 'connection.status_changed': ('connection','getConnection','connections:read'),
 'origination.action_required': ('origination','getOrigination','insights:read'),
 'origination.status_changed': ('origination','getOrigination','insights:read'),
 'origination.completed': ('origination','getOrigination','insights:read'),
 'origination.failed': ('origination','getOrigination','insights:read'),
 'risk_package.created': ('risk_package','getRiskPackage','results:read'),
 'monitor.status_changed': ('monitor','getMonitor','signal:read'),
 'monitoring_run.completed': ('monitoring_run','getMonitoringRun','signal:read'),
 'monitoring_run.failed': ('monitoring_run','getMonitoringRun','signal:read'),
 'alert.created': ('alert','getAlert','signal:read'),
 'alert.resolved': ('alert','getAlert','signal:read'),
 'export.ready': ('export','getExport','exports:read'),
 'export.failed': ('export','getExport','exports:read'),
 'data.updated': ('connection','getConnection','data:read'),
 'document.status_changed': ('document','getDocument','evidence:read'),
 'billing.payment_updated': ('billing_payment','getBillingPayment','billing:read'),
 'billing.transaction_posted': ('billing_transaction','getBillingTransaction','billing:read'),
 'deal_snapshot.created': ('deal_snapshot','getDealSnapshot','signal:read'),
}

# Development example values are deliberately not production quotas or SLAs.
PROFILE = {
 'id':'development-example', 'version':'1',
 'max_json_bytes':1048576, 'max_upload_bytes':20971520, 'max_document_pages':200,
 'allowed_document_mime_types':['application/pdf','image/png','image/jpeg','image/webp'],
 'document_types':['financial_statement','bank_statement','identity_document','business_registration','tax_return','lending_terms','risk_policy','other'],
 'session_ttl_seconds':900, 'download_ttl_seconds':300,
 'snapshot_ttl_seconds':3600, 'data_feed_retention_seconds':2592000,
 'event_retention_seconds':2592000, 'export_retention_seconds':86400,
 'poll_min_interval_seconds':5, 'poll_max_interval_seconds':60,
 'webhook_timeout_seconds':10, 'webhook_max_body_bytes':65536,
 'webhook_rotation_overlap_seconds':86400,
 'rate_limits':[{'group':'reads','requests':120,'window_seconds':60}, {'group':'commands','requests':30,'window_seconds':60}, {'group':'uploads','requests':10,'window_seconds':60}],
}

def extend_operations(add):
 add('createDealSnapshot','POST','monitors/{id}/deal-snapshots','Signal','DealSnapshot','DealSnapshotInput')
 add('listDealSnapshots','GET','monitors/{id}/deal-snapshots','Signal','DealSnapshot',many=True)
 add('getDealSnapshot','GET','deal-snapshots/{id}','Signal','DealSnapshot')


def extend_schemas(s):
 from product_api_review import obj, ref, text, enum, array, nullable
 ident=lambda desc='Opaque identifier in the authorized workspace and environment.':text(desc)
 stamp=lambda desc='UTC timestamp in RFC 3339 format.':text(desc,format='date-time')
 ids=lambda desc='Identifiers of the associated authorized records.':array(ident(),uniqueItems=True,description=desc)
 positive=lambda desc:{'type':'integer','minimum':1,'description':desc}
 def add(name,fields):
  s[name]['properties'].update(deepcopy(fields));s[name]['required']=list(dict.fromkeys(s[name].get('required',[])+list(fields)))
 s['PersonInput']['properties']['client_reference']=ident('Institution borrower reference, unique by borrower type in the workspace/environment when supplied.')
 # Shared schema instances must never allow one field description to mutate another.
 add('EmbeddingSession',{'embedding_version_id':ident('Published Hub configuration version used by this session.'), 'monitor_id':nullable(ident()), 'requirement_id':nullable(ident()), 'consent_purposes':array(enum('credit_assessment','continuous_monitoring'),minItems=1,uniqueItems=True), 'embed_origin':nullable(text(format='uri')), 'return_url':text(format='uri'), 'failure':nullable(ref('Error'))})
 s['EmbeddingSession']['properties']['status']['enum'].append('cancelled')
 s['EmbeddingSession']['properties']['launch_url']['description']='Short-lived borrower capability URL. Use in a permitted iframe or full-page navigation; never log or persist it as a reusable integration credential.'
 s['CreateEmbeddingSession']['properties'].update({
  'consent_purposes':array(enum('credit_assessment','continuous_monitoring'),minItems=1,uniqueItems=True,description='Explicit purposes presented for borrower authorization; must be a subset of the published Hub purposes. Credit assessment alone does not permit monitoring.'),
  'embed_origin':text('Exact HTTPS parent origin approved for this Hub. Omit for full-page redirects. No path, wildcard or opaque origin.',format='uri'),
  'monitor_id':ident('Monitor whose open requirement this session addresses. Mutually exclusive with origination_id.'),
  'requirement_id':ident('Open requirement on origination_id or monitor_id; completion atomically associates the authorized connection with that resource.'),
 })
 s['CreateEmbeddingSession']['required'].append('consent_purposes')
 s['CreateEmbeddingSession'].setdefault('allOf',[]).extend([
  {'not':{'required':['origination_id','monitor_id']}},
  {'if':{'required':['requirement_id']},'then':{'oneOf':[{'required':['origination_id']},{'required':['monitor_id']}]}},
  {'if':{'anyOf':[{'required':['origination_id']},{'required':['monitor_id']}]},'then':{'required':['requirement_id']}},
 ])
 s['Consent']['properties']['purposes']=array(enum('credit_assessment','continuous_monitoring'),minItems=1,uniqueItems=True)
 s['Requirement']=obj({
  'id':ident(), 'code':enum('source_missing','source_reauthorization_required','document_required','contact_support'),
  'message':text('Human-readable explanation; automate using code/action and typed fields.'),
  'action':enum('connect_source','reauthorize_source','upload_document','contact_support'),
  'connection_id':nullable(ident()), 'integration_id':nullable(ident()),
  'document_type':nullable(text()), 'accepted_mime_types':array(text()),
  'consent_purposes':array(enum('credit_assessment','continuous_monitoring'),uniqueItems=True),
 },allOf=[
  {'if':{'properties':{'action':{'const':'reauthorize_source'}}},'then':{'properties':{'code':{'const':'source_reauthorization_required'},'connection_id':ident(),'consent_purposes':{'minItems':1}}}},
  {'if':{'properties':{'action':{'const':'connect_source'}}},'then':{'properties':{'code':{'const':'source_missing'},'integration_id':ident(),'consent_purposes':{'minItems':1}}}},
  {'if':{'properties':{'action':{'const':'upload_document'}}},'then':{'properties':{'code':{'const':'document_required'},'document_type':text(),'accepted_mime_types':{'minItems':1}}}},
  {'if':{'properties':{'action':{'const':'contact_support'}}},'then':{'properties':{'code':{'const':'contact_support'}}}},
 ])
 add('Origination',{'connection_ids':ids('Current effective connections, including resolved requirements. submitted_request remains immutable.')})
 add('Monitor',{'connection_ids':ids(), 'requirements':array(ref('Requirement')), 'failure':nullable(ref('Error')), 'latest_deal_snapshot_id':ident(), 'updated_at':stamp()})
 s['UpdateMonitor']['properties']['connection_ids']=ids('Replacement set for future evaluations. Each source must belong to the borrower and authorize continuous_monitoring. Change uses If-Match and leaves past runs untouched.')
 for name in ['Monitor','Origination']:
  s[name].setdefault('allOf',[]).extend([
   {'if':{'properties':{'status':{'const':'requires_action'}}},'then':{'properties':{'requirements':{'minItems':1}}},'else':{'properties':{'requirements':{'maxItems':0}}}},
   {'if':{'properties':{'status':{'const':'failed'}}},'then':{'properties':{'failure':ref('Error')}},'else':{'properties':{'failure':{'type':'null'}}}},
  ])
 add('MonitoringRun',{'record_version':positive('Monotonic version for this run; terminal evaluations are immutable.'),'deal_snapshot_id':ident('Exact lender input snapshot frozen at evaluation start.'),'failure':nullable(ref('Error'))})
 for name in ['Document','BillingPayment','Consent']:
  add(name,{'record_version':positive('Monotonically increasing version of this resource. Compare with event.resource_version; snapshot reads preserve their historical version.')})
 add('Document',{'failure':nullable(ref('Error'))})
 s['Document'].setdefault('allOf',[]).append({'if':{'properties':{'status':{'const':'rejected'}}},'then':{'properties':{'failure':ref('Error')}},'else':{'properties':{'failure':{'type':'null'}}}})
 add('Export',{'expires_at':nullable(stamp('Retained file expiry; null until completed. Separate from each download-link expiry.'))})
 s['Export'].setdefault('allOf',[]).extend([{'if':{'properties':{'status':{'const':'completed'}}},'then':{'properties':{'expires_at':stamp(),'failure':{'type':'null'}}}}, {'if':{'properties':{'status':{'const':'failed'}}},'then':{'properties':{'failure':ref('Error')}}}])
 s['MonitoringRun'].setdefault('allOf',[]).extend([{'if':{'properties':{'status':{'enum':['failed','skipped']}}},'then':{'properties':{'failure':ref('Error'),'risk_package_id':{'type':'null'}}}}, {'if':{'properties':{'status':{'enum':['completed','partial']}}},'then':{'properties':{'risk_package_id':ident(),'completed_at':stamp(),'failure':{'type':'null'}}}}])
 for name in ['RiskPackage','BillingTransaction']:
  add(name,{'record_version':{'type':'integer','const':1,'description':'Immutable published record; event.resource_version is always 1.'}})
 add('RiskPackage',{'deal_snapshot_id':nullable(ident('Exact Signal lender snapshot used; null for Insights.'))})
 s['RiskPackage']['oneOf'][0]['properties']['deal_snapshot_id']={'type':'null'}
 s['RiskPackage']['oneOf'][1]['properties']['deal_snapshot_id']=ident()
 s['Deal']['description']='Complete institution-supplied deal terms at one point in time. Initial input is captured during enrollment; later inputs are append-only deal snapshots.'
 s['DealPerformance']=obj({'status':enum('current','delinquent','defaulted','paid_off','charged_off'), 'days_past_due':{'type':'integer','minimum':0},'amount_past_due':ref('Money'),'next_payment_due_at':nullable(text(format='date')),'last_payment_at':nullable(stamp())},description='Lender-reported performance, not an AMLOK servicing command. Currency must match the deal. Unknown values cannot be fabricated; omit performance entirely (null) when unavailable.')
 s['DealSnapshotInput']=obj({'previous_snapshot_id':ident('Current monitor.latest_deal_snapshot_id; atomically compared before acceptance.'),'effective_at':stamp('Lender as-of time; must be later than the current snapshot and no later than server acceptance time.'),'deal':ref('Deal'),'performance':nullable(ref('DealPerformance'))},description='Complete replacement input for future evaluations, stored as a new immutable record. Same borrower, institution_reference, currency, funded_at and funded_amount as enrollment; amendments to outstanding balance, maturity and terms are permitted. No backdating or mutation of past assessments.')
 s['DealSnapshot']=obj({'id':ident(),'monitor_id':ident(),'borrower_id':ident(),'previous_snapshot_id':nullable(ident()),'sequence':positive('1 for enrollment; strictly increments for each accepted snapshot.'),'record_version':{'type':'integer','const':1},'effective_at':stamp(),'received_at':stamp(),'deal':ref('Deal'),'performance':nullable(ref('DealPerformance'))})
 # Portfolio onboarding is explicit input, not an undocumented provisioning reference.
 s['BaselineInput']={'oneOf':[obj({'risk_package_id':ident()}),obj({'portfolio':obj({'lending_product_version_id':ident(),'application':nullable(ref('ApplicationInput')),'document_ids':ids()})})], 'description':'Use an existing compatible risk package, or explicit portfolio inputs for Signal baseline preparation. Portfolio initialization is included in Signal; no separate Insights purchase or undocumented reference is needed.'}
 s['Error']['properties']['code']['enum']+=['deal_snapshot_conflict','payload_too_large','unsupported_media_type','document_rejected','processing_failed','session_expired','consent_purpose_missing','sandbox_only','scenario_not_available']
 s['OperationalProfile']=obj({key:(array(obj({'group':enum('reads','commands','uploads'),'requests':positive('Allowed requests across all keys in the workspace/environment.'),'window_seconds':positive('Rolling window length in seconds.')})) if key=='rate_limits' else array(text()) if isinstance(value,list) else positive('Effective configured '+key.replace('_',' ')+'.') if isinstance(value,int) else text()) for key,value in PROFILE.items()},description='Effective environment settings, required before accepting traffic. Example values are a development test profile, not production capacity or an SLA. profile id/version freezes interpretation; lifetime fields apply to newly issued resources.')
 s['HubVersion']=obj({'id':ident(),'name':text(),'integration_ids':ids(),'consent_purposes':array(enum('credit_assessment','continuous_monitoring'),minItems=1,uniqueItems=True),'allowed_embed_origins':array(text(format='uri')),'allowed_return_urls':array(text(format='uri')),'hub_origin':text(format='uri')},description='Published console configuration visible to this key; origins are exact matches, return URLs match scheme/authority/path and configured query. Fragments and credentials are forbidden.')
 add('Configuration',{'operational_profile':ref('OperationalProfile'),'embedding_versions':array(ref('HubVersion')), 'sandbox':nullable(obj({'scenario_ids':ids('Scenario identifiers accepted by X-AMLOK-Sandbox-Scenario; only in Sandbox.'),'test_integration_id':ident('Synthetic integration available in the Sandbox Hub. No real bank login is required.')}))})
 s['Configuration']['properties']['embedding_version_ids']['description']='IDs of the published embedding_versions entries. Console owns design; API discovers immutable versions.'
 for name in ['Page','DataPage']:
  add(name,{'expires_at':stamp('Snapshot expiry. After expiry, respond 410 and restart with a new snapshot; never continue on a new snapshot silently.')})
 for name in ['EventPage','DataChangePage']:
  add(name,{'resume_expires_at':stamp('Expiration of the returned resume cursor. Poll empty pages too and atomically advance the checkpoint.')})
 s['Event']['properties']['type']['enum']=list(EVENT_RESOURCES)
 s['Event']['properties']['resource_type']['enum']=sorted({v[0] for v in EVENT_RESOURCES.values()})
 s['RequestReceipt']['properties']['operation_id']['description']='Original operationId. Combine with the retained resource ID and the operation index to recover accepted work; never create a new command solely because replay expired.'
 s['Event']['allOf']=[{'if':{'properties':{'type':{'const':event}}},'then':{'properties':{'resource_type':{'const':mapping[0]}}}} for event,mapping in EVENT_RESOURCES.items()]
 s['HubMessage']=obj({'protocol_version':{'const':'1'},'event_id':ident(),'session_id':ident(),'type':enum('amlok.hub.ready','amlok.hub.completed','amlok.hub.cancelled','amlok.hub.expired','amlok.hub.failed')},description='Browser postMessage envelope. Contains no credentials, financial data, provider URLs or consent proof. Parent must verify event.origin and event.source then fetch session through its authenticated backend.')
 # Make every authored property inspectable without a blank tooltip.
 for name,schema in s.items():
  if name.startswith(('Normalized','Financial','Report')):continue
  for key,field in schema.get('properties',{}).items():
   if not field.get('description'):
    field['description']={'id':'Opaque identifier for this '+name+' record.','created_at':'UTC time the record was created.','updated_at':'UTC time this resource last changed.','expires_at':'UTC expiration; do not use this resource after this instant.','status':'Current lifecycle state. See the product lifecycle and recovery guides.','borrower_id':'Borrower that owns this resource; must match the key workspace and environment.','record_version':'Monotonic resource version for event reconciliation.'}.get(key, key.replace('_',' ').capitalize()+' for '+name+'. Constraints, requiredness and allowed values are defined by this schema.')
 return s


def extend_fixtures(f):
 now='2026-11-06T12:00:00Z';previous='2026-11-05T12:00:00Z'
 f['CreateEmbeddingSession'].update(consent_purposes=['credit_assessment','continuous_monitoring'],embed_origin='https://institution.example.com')
 f['EmbeddingSession'].update(monitor_id=None,requirement_id=None,consent_purposes=['credit_assessment','continuous_monitoring'],embed_origin='https://institution.example.com',return_url='https://institution.example.com/connected',failure=None)
 f['Origination']['connection_ids']=deepcopy(f['CreateOrigination']['connection_ids'])
 f['Monitor'].update(connection_ids=['con_synthetic'],requirements=[],failure=None,latest_deal_snapshot_id='ds_synthetic',updated_at=now)
 f['MonitoringRun'].update(record_version=1,deal_snapshot_id='ds_synthetic',failure=None)
 f['Document'].update(record_version=1,failure=None)
 f['Export']['expires_at']=None
 for name in ['BillingPayment','BillingTransaction','RiskPackage','Consent']:f[name]['record_version']=1
 f['RiskPackage']['deal_snapshot_id']=None
 f['DealSnapshotInput']={'previous_snapshot_id':'ds_initial','effective_at':now,'deal':deepcopy(f['CreateMonitor']['deal']),'performance':None}
 f['DealSnapshotInput']['deal']['outstanding_amount']['amount']='48000.00'
 f['DealSnapshotInput']['deal']['funded_at']=previous
 f['DealSnapshot']={'id':'ds_synthetic','monitor_id':'mon_synthetic','borrower_id':'bor_synthetic','previous_snapshot_id':'ds_initial','sequence':2,'record_version':1,'effective_at':now,'received_at':now,'deal':deepcopy(f['DealSnapshotInput']['deal']),'performance':None}
 f['Monitor']['deal']=deepcopy(f['DealSnapshot']['deal'])
 f['CreateMonitor']['deal']['funded_at']=previous
 f['Configuration'].update(operational_profile=deepcopy(PROFILE),embedding_versions=[{'id':'embed_synthetic','name':'Synthetic borrower Hub','integration_ids':['bank_synthetic'],'consent_purposes':['credit_assessment','continuous_monitoring'],'allowed_embed_origins':['https://institution.example.com'],'allowed_return_urls':['https://institution.example.com/connected'],'hub_origin':'https://borrower.example.com'}],sandbox={'scenario_ids':['happy_path','source_reauthorization','document_required','missing_financial_input','restricted_report','provider_failure','insufficient_credits','monitoring_alert','payment_return','export_failure'],'test_integration_id':'bank_synthetic'})
 f['Configuration']['application_schemas'].append({'id':'consumer_app_schema_synthetic','version':'1','json_schema':{'type':'object','required':['gross_monthly_income','monthly_debt_payments'],'properties':{'gross_monthly_income':{'type':'string','pattern':r'^[0-9]+\.[0-9]{2}$'},'monthly_debt_payments':{'type':'string','pattern':r'^[0-9]+\.[0-9]{2}$'}},'additionalProperties':False}})
 f['Configuration']['dimensions'].append({'key':'debt_to_income','description':'Eligible monthly debt payments divided by established gross monthly income. Missing inputs yield unavailable, never zero.','unit':'ratio','calculation_version':'consumer-dti-synthetic-v1','borrower_types':['person']})
 return f


def enrich(spec,f):
 """Add wire-level requirements after ordinary endpoint example generation."""
 from product_api_review import obj,ref,text,enum
 spec['x-contract-stage']='backend-implementation-specification'
 spec['info']['description']+=' This is the implementation specification for the backend to be built. Publication does not certify a running service. All new environments must pass the integration acceptance checklist.'
 spec['x-browser-message-schema']='#/components/schemas/HubMessage'
 spec['x-event-resources']={k:{'resource_type':v[0],'read_operation_id':v[1],'scope':v[2]} for k,v in EVENT_RESOURCES.items()}
 spec['x-development-profile']=PROFILE
 for path,methods in spec['paths'].items():
  for method,op in methods.items():
   oid=op['operationId']
   if oid=='createDealSnapshot':op['description']+=' Failed monitors also reject new inputs; correct the failure and enroll a new monitor.'
   if oid in ['createDealSnapshot','listDealSnapshots']:
    op['parameters']=[p for p in op['parameters'] if p['name']!='borrower_id']
    next(p for p in op['parameters'] if p['name']=='id')['description']='Monitor ID whose lender input history is being accessed.'
   if method=='post':
    op['parameters'].append({'name':'X-AMLOK-Sandbox-Scenario','in':'header','required':False,'schema':enum(*f['Configuration']['sandbox']['scenario_ids']),'description':'Sandbox-only deterministic test scenario on borrower creation, persisted for that borrower. On other operations or any Live request, reject before side effects with 400 sandbox_only. Omit for happy_path.'}) if oid=='createBorrower' else None
   if oid=='createDealSnapshot':op['description']+=' previous_snapshot_id is mandatory optimistic concurrency; 409 deal_snapshot_conflict when stale. Same idempotency key replays the accepted snapshot even if the monitor has since advanced. New snapshot affects evaluations starting after acceptance; no retroactive analysis or new Insights charge.'
   if oid=='getConfiguration':op['description']+=' operational_profile and embedding_versions are required discovery; sandbox is null in Live. Never infer production quotas from synthetic examples.'
   for status,res in op['responses'].items():
    res.setdefault('headers',{})['X-Request-ID']={'schema':text(),'description':'Same request ID as meta.request_id or error.request_id.'}
    if status.startswith('2'):
     example=res['content']['application/json']['example']
     if 'page' in example:
      if oid in ['listEvents','listDataChanges']:example['page']['resume_expires_at']='2026-12-06T12:00:00Z'
      else:example['page']['expires_at']='2026-11-06T13:00:00Z'
     if oid=='getBillingSummary':
      # Snapshot lifetime is exposed on the summary itself because it has no page.
      spec['components']['schemas']['BillingSummary']['properties']['snapshot_expires_at']={'type':'string','format':'date-time','description':'Expiry for snapshot_id on related billing reads.'}
      if 'snapshot_expires_at' not in spec['components']['schemas']['BillingSummary']['required']:spec['components']['schemas']['BillingSummary']['required'].append('snapshot_expires_at')
      example['data']['snapshot_expires_at']='2026-11-06T13:00:00Z';f['BillingSummary']['snapshot_expires_at']=example['data']['snapshot_expires_at']
   if method in ['post','patch']:
    for status,code in [('413','payload_too_large'),('415','unsupported_media_type')]:
     op['responses'][status]={'description':'Request exceeds the effective profile size limit or media type is unsupported. No command is accepted.','content':{'application/json':{'schema':obj({'error':ref('Error')}),'example':{'error':{'code':code,'message':code.replace('_',' '),'retryable':False,'request_id':'req_synthetic','field':None}}}}}
 return spec

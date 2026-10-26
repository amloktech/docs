"""Developer integration and recovery contract. Generates documentation, not a backend."""
from copy import deepcopy
from urllib.parse import urlencode
import json


def extend(g):
    S, E, spec = g['SCHEMAS'], g['EXAMPLES'], g['SPEC']
    ref, nullable, now = g['ref'], g['nullable'], g['NOW']
    text = {'type': 'string', 'minLength': 1}
    date = {'type': 'string', 'format': 'date-time'}
    integer = {'type': 'integer', 'minimum': 0}
    enum = lambda *v: {'type': 'string', 'enum': list(v)}
    arr = lambda v: {'type': 'array', 'items': deepcopy(v)}
    obj = lambda p, req=None: {'type': 'object', 'properties': deepcopy(p), 'required': list(p) if req is None else req, 'additionalProperties': False}
    new = []
    cancel = ' Account cancellation rejects new processing immediately with 409 invalid_state. Read-only access lasts only until workspace deletion. No separate product charge or financial mutation is introduced.'

    def field(name, key, schema, example):
        for n in [name, name+'Read']:
            if n not in S: continue
            S[n]['properties'][key] = deepcopy(schema)
            if n == name and key not in S[n].setdefault('required', []): S[n]['required'].append(key)
        if name in E: E[name][key] = deepcopy(example)

    def param(name, description, required=False, schema=None):
        return {'name': name, 'in': 'query', 'required': required, 'description': description, 'schema': schema or text}

    def pages():
        return [param('limit', 'Default 100; maximum 200.', False, {'type':'integer','minimum':1,'maximum':200,'default':100}), param('cursor', 'Opaque cursor bound to filters and the first page snapshot. Do not change filters during pagination.')]

    def add(oid, method, path, title, group, scope, schema, example, desc, request=None, body=None, params=None, many=False, code=None):
        code = code or ('201' if method == 'POST' else '200')
        pars = list(params or [])
        if '{id}' in path: pars.insert(0, g['parameter']('id','path','id','Authorized identifier in this workspace.',True,example.get('id',example.get('subject_id','res_example'))))
        if method == 'POST': pars.append(g['parameter']('Idempotency-Key','header','string','Stable key for this intended action; retain across retries.',True,'idem_integration_example'))
        rs, value = g['envelope'](ref(schema), deepcopy(example), many)
        value['meta'] = g['meta']('complete')
        if many: value['page'] = {'has_more':False,'next_cursor':None,'limit':100}
        op = {'operationId':oid,'summary':title,'description':desc,'tags':[group],'security':[{'BearerAuth':[]}],
              'x-required-scopes':[scope],'parameters':pars,'responses':{code:{'description':'Authorized response.','content':{'application/json':{'schema':rs,'examples':{'synthetic':{'value':value}}}}}}}
        for err in ['400','401','403','404','409','410','422','429','500','503']: op['responses'][err]={'$ref':'#/components/responses/Error'+err}
        if request: op['requestBody']={'required':True,'content':{'application/json':{'schema':ref(request),'example':body}}}
        spec['paths'].setdefault(path,{})[method.lower()] = op
        page='api-reference/endpoints/'+group.lower()+'/'+title.lower().replace(' ','-')
        entry={'id':oid,'method':method,'path':path,'title':title,'scope':scope,'group':group,'page':page,'resource':example.get('object'), 'request':body,'response':value,'success':code}
        g['OP_INDEX'].append(entry);g['NAV_GROUPS'][group].append(page);new.append(entry)
        return op

    # Preserve the connection identity across renewed consent and expired interaction URLs.
    S['AuthorizationRequest']=obj({'consent_id':text,'redirect_uri':{'type':'string','format':'uri','pattern':'^https://'},'state':{'type':'string','minLength':32,'maxLength':256}})
    auth_body={'consent_id':'con_example','redirect_uri':'https://client.example.com/connected','state':'synthetic-random-state-at-least-32-characters'}
    auth = add('IR001','POST','/v1/connections/{id}/authorization','Renew connection authorization','Platform','connections:write','Connection',E['Connection'],
        'Create a fresh short-lived authorization action on the existing pending, active or reauth_required connection. Preserve its ID, records and synchronization lineage. The consent must authorize the same subject, provider products and purposes. Validate redirect_uri against portal registration. Bind state to this connection and action; echo it on return. A new action invalidates any older unused action. An identical idempotent retry returns the same action, including its original expiry; use a new key when intentionally replacing an expired action. Reauthorization does not backfill data until a successful sync. Revoked or disconnected connections cannot be reopened; obtain new consent and create a new connection.'+cancel,
        'AuthorizationRequest',auth_body,code='201')
    action={'type':'redirect','url':'https://authorize.example.com/session/synthetic','expires_at':'2026-10-23T14:15:00Z'}
    media=auth['responses']['201']['content']['application/json']
    media['schema']['properties']['action']=ref('Action');media['schema']['required'].append('action')
    media['examples']['synthetic']['value']['action']=action
    req=S['EP139Request'];req['properties']['state']=deepcopy(S['AuthorizationRequest']['properties']['state']);req['required'].append('state')
    create=spec['paths']['/v1/connections']['post']
    create['requestBody']['content']['application/json']['example']['state']=auth_body['state']
    callback=' Browser return parameters are connection_id, state and result (completed, cancelled or failed); failed returns a sanitized error_code. Verify the saved state and expected connection, then retrieve the connection server-side. The callback never proves consent or connection activation. No credentials or source data appear in return parameters. The state must be unpredictable, bound to the initiating browser session and accepted only once.'
    create['description']+=callback+' Renew an expired link or reauthorization-required connection through POST /v1/connections/{id}/authorization.'
    auth['description']+=callback
    S['ProviderProduct']=obj({'id':text,'resources':arr(text),'consent_scopes':arr(text),'purposes':arr(text)})
    field('ProviderCapability','products',arr(ref('ProviderProduct')), [{'id':'transactions','resources':['bank_account','bank_transaction'],'consent_scopes':['banking:read'],'purposes':['credit_assessment']}])
    S['EP139Request']['properties']['products']['description']='Product IDs from this provider\'s products[].id in GET /v1/providers. Resource names are not interchangeable with product IDs. Reject unsupported values with 422 validation_error.'

    # Authorize a person as part of the primary business product without changing billing subject.
    roles=enum('beneficial_owner','director','guarantor','authorized_signatory')
    S['SubjectAssociation']=obj({'id':text,'object':{'const':'subject_association','type':'string'},'business_id':text,'person_id':text,'role':roles,
        'status':enum('pending','active','rejected','revoked'),'evidence_document_ids':arr(text),'relationship_id':nullable(text),
        'reason_code':nullable(text),'created_at':date,'updated_at':date,'record_version':{'type':'integer','minimum':1}})
    association={'id':'assoc_example','object':'subject_association','business_id':'biz_example','person_id':'per_example','role':'beneficial_owner','status':'active',
        'evidence_document_ids':['doc_example'],'relationship_id':None,'reason_code':None,'created_at':now,'updated_at':now,'record_version':2}
    S['SubjectAssociationRequest']=obj({'business_id':text,'person_id':text,'role':roles,'evidence_document_ids':{'type':'array','items':text,'minItems':1,'uniqueItems':True}})
    association_desc='Associate an existing person with a business in this workspace using permitted evidence and recorded authorization. This is a client-declared association, not a verified legal ownership determination. AMLOK validates subject ownership, the authorization and supporting evidence; status becomes active automatically when checks pass, or remains pending for platform review. Rejected records expose reason_code. An active association authorizes only related-person verification within an agreed parent product workflow. It does not grant broader data access. Canonical verified relationships remain read-only evidence. Review, corrections and revocation occur in the portal; create a new association for corrected evidence. Completed assessments retain their historical association version.'
    add('IR002','POST','/v1/subject-associations','Create subject association','Identity','identity:write','SubjectAssociation',{**association,'status':'pending','record_version':1},association_desc+cancel,
        'SubjectAssociationRequest',{k:association[k] for k in ['business_id','person_id','role','evidence_document_ids']})
    add('IR003','GET','/v1/subject-associations','List subject associations','Identity','identity:read','SubjectAssociation',association,association_desc,params=pages()+[param('business_id','Filter primary business.'),param('person_id','Filter related person.'),param('status','Association status.',schema=S['SubjectAssociation']['properties']['status'])],many=True)
    add('IR004','GET','/v1/subject-associations/{id}','Retrieve subject association','Identity','identity:read','SubjectAssociation',association,association_desc)
    for branch in S['ProcessingContext']['oneOf']:branch['properties']['subject_association_id']=text
    S['ProcessingContext']['description']='Parent must belong to this workspace. Same-subject stages need no association. Only person KYC may target a different subject: supply an active subject_association_id linking that person to the parent business. Insights requires an unfinished authorized root run; Signal requires an active paid period. Stage scope, consent, association and workload are checked on every attempt. The parent business remains the billing and workload subject. No standalone service or extra charge.'
    verify=spec['paths']['/v1/verifications']['post']
    verify['description']+=' Person KYC within a business assessment requires processing_context.subject_association_id. Its person_id must match the verification subject; its business_id must match the parent subject. Store the association ID and validated record version on the verification for audit. Pending, rejected, revoked, mismatched or cross-workspace associations cannot authorize a stage. Revocation stops unfinished related-person work. Do not create a second product merely to verify its owner.'
    field('Verification','subject_association_version',nullable({'type':'integer','minimum':1}),None)
    for oid in ['EP143','EP147','EP148']:
        S[oid+'Request'].setdefault('allOf',[]).append({'properties':{'processing_context':{'not':{'required':['subject_association_id']}}}})
    S['EP142Request'].setdefault('allOf',[]).append({'if':{'properties':{'verification_type':{'const':'kyb'}}},'then':{'properties':{'processing_context':{'not':{'required':['subject_association_id']}}}}})

    # Failures must expose a safe reason and a supported recovery path.
    S['ProcessingFailure']=obj({'code':enum('provider_unavailable','processing_timeout','invalid_evidence','unsupported_scope','internal_processing_error'),
        'message':text,'retryable':{'type':'boolean'},'recovery_action':enum('retry_same_run','correct_evidence','contact_support'),
        'retry_after_seconds':nullable(integer),'occurred_at':date,'request_id':text})
    S['ProcessingFailure']['allOf']=[{'if':{'properties':{'retryable':{'const':True}}},'then':{'properties':{'recovery_action':{'const':'retry_same_run'},'retry_after_seconds':integer}},'else':{'properties':{'recovery_action':enum('correct_evidence','contact_support'),'retry_after_seconds':{'type':'null'}}}}]
    S['EvidenceRejection']=obj({'code':enum('unreadable','wrong_document_type','subject_mismatch','incomplete_period','expired_document','other'),
        'message':text,'document_ids':arr(text),'reviewed_at':date})
    field('WorkflowRun','failure',nullable(ref('ProcessingFailure')),None)
    field('WorkflowRun','attempt',{'type':'integer','minimum':1},1)
    field('Requirement','rejection',nullable(ref('EvidenceRejection')),None)
    S['WorkflowRun'].setdefault('allOf',[]).append({'if':{'properties':{'status':{'const':'failed'}},'required':['status']},'then':{'properties':{'failure':ref('ProcessingFailure'),'billing_usage_id':{'type':'null'},'output_resource_ids':{'maxItems':0}}},'else':{'properties':{'failure':{'type':'null'}}}})
    S['Requirement'].setdefault('allOf',[]).append({'if':{'properties':{'status':{'const':'rejected'}},'required':['status']},'then':{'properties':{'rejection':ref('EvidenceRejection')}},'else':{'properties':{'rejection':{'type':'null'}}}})
    retry_example={**E['WorkflowRun'],'status':'queued','attempt':2,'failure':None,'billing_usage_id':None,'output_resource_ids':[],'completed_at':None}
    add('IR005','POST','/v1/workflow-runs/{id}/retry','Retry failed workflow','Operations','workflows:execute','WorkflowRun',retry_example,
        'Retry an existing failed run only when failure.retryable is true and recovery_action is retry_same_run. Retain run identity, application, product context, evidence and the one eventual charge. Increment attempt once per accepted retry and append an audit event; replaying this idempotency key cannot increment it again. Revalidate active consent, parent context, association and workload. Respect retry_after_seconds. Non-retryable, completed, cancelled or already-running runs return 409 invalid_state; concurrent retries can start only one attempt. Unfunded accepted work uses waiting_for_credits, not a replacement run. For non-retryable invalid evidence, correct requirements or contact support as failure.recovery_action directs; do not invent a replacement billable operation.'+cancel,code='202')

    # Persist a small receipt beyond the full-response replay window.
    S['RequestReceipt']=obj({'id':text,'object':{'const':'request_receipt','type':'string'},'operation_id':text,'target_path':text,'request_id':text,
        'status':enum('accepted','completed','failed','resource_unavailable'),'resource_type':text,'resource_id':text,'resource_path':{'type':'string','pattern':'^/v1/','description':'Relative authorized GET route for the durable resource or parent. Never a signed URL, external origin or secret-bearing location.'},'original_http_status':{'type':'integer','minimum':200,'maximum':599},
        'accepted_at':date,'replay_expires_at':date})
    receipt={'id':'rcpt_example','object':'request_receipt','operation_id':'EP147','target_path':'/v1/workflow-runs','request_id':'req_example','status':'accepted',
        'resource_type':'workflow_run','resource_id':'wfr_example','resource_path':'/v1/workflow-runs/wfr_example','original_http_status':202,'accepted_at':now,'replay_expires_at':'2026-10-24T14:00:00Z'}
    lookup=add('IR006','GET','/v1/request-receipts/lookup','Look up request receipt','Platform','platform:read','RequestReceipt',receipt,
        'Find an accepted POST after losing its response, including after the 24-hour full-response replay window. Supply the original Idempotency-Key header, operation_id and exact resolved target_path (no origin or query). The same workspace, environment and original operation scopes are required; key rotation does not break lookup. Receipts are created atomically before acknowledging an accepted command and retained until workspace deletion, including after a linked resource expires. resource_unavailable retains its identity but does not authorize rerunning it. Store a non-reversible key digest, not the raw key. A 404 is not proof that an in-flight request never arrived; within 24 hours retry the same key, afterward contact support with the caller correlation ID before any new submission. This endpoint neither executes nor replays work.',
        params=[param('operation_id','Original OpenAPI operationId.',True),param('target_path','Exact resolved request path, for example /v1/connections/cnn_example/sync.',True)])
    lookup['parameters'].append(g['parameter']('Idempotency-Key','header','string','Original key being looked up. This GET does not create a command.',True,'idem_underwrite_example'))
    lookup['description']+=' resource_path identifies an authorized relative GET route and requires its read scope. For a short-lived document or report link, it identifies the document or report parent, never the signed URL. An expired link can be intentionally regenerated with a new key without paid processing. Webhook replay receipts identify the original webhook event; match delivery replay_request_id to receipt.request_id. A lost create-webhook response cannot reveal its one-time secret through lookup; rotate it in the portal.'
    for item in spec['paths'].values():
        if 'post' in item:
            item['post']['description']+=' Accepted commands have a durable request receipt. Full response replay lasts 24 hours; afterward the same key and target return 409 idempotency_result_expired without re-execution. Different payloads return 409 idempotency_conflict. Use GET /v1/request-receipts/lookup to find the original resource. The fingerprint includes the resolved target path and intended payload; a key used on another target is rejected rather than replayed onto it. Pre-execution validation or insufficient-credit rejection creates no accepted receipt.'

    # Discover the actual environment values instead of guessing string identifiers or limits.
    S['WorkflowConfiguration']=obj({'id':text,'workflow_type':enum('verify','underwrite','monitor','investigate'),'products':arr(enum('insights','signal')),'verification_types':arr(enum('kyc','kyb'))})
    S['RulesetConfiguration']=obj({'id':text,'attribute_keys':arr(text),'resource_types':arr(text)})
    S['CadenceConfiguration']=obj({'id':text,'description':text})
    S['EnvironmentConfiguration']=obj({'id':text,'object':{'const':'environment_configuration','type':'string'},'workspace_id':text,'environment':enum('sandbox','production'),
        'revision':text,'effective_at':date,'workflow_versions':arr(ref('WorkflowConfiguration')),'rulesets':arr(ref('RulesetConfiguration')),'cadences':arr(ref('CadenceConfiguration')),
        'limits':obj({'requests_per_minute':{'type':'integer','minimum':1},'burst_requests':{'type':'integer','minimum':1},'concurrent_jobs':{'type':'integer','minimum':1},'upload_bytes':{'type':'integer','minimum':1},'document_pages':{'type':'integer','minimum':1},'mime_types':arr(text)}),
        'webhooks':obj({'event_retention_seconds':{'type':'integer','minimum':1},'delivery_timeout_seconds':{'type':'integer','minimum':1},'rotation_overlap_seconds':{'type':'integer','minimum':1},'retained_from':date}),
        'idempotency_replay_seconds':{'type':'integer','const':86400}})
    configuration={'id':'config_example','object':'environment_configuration','workspace_id':'wsp_example','environment':'sandbox','revision':'cfg_example','effective_at':now,
        'workflow_versions':[{'id':'underwrite-v1','workflow_type':'underwrite','products':['insights'],'verification_types':[]},{'id':'kyc-ca-v1','workflow_type':'verify','products':['insights','signal'],'verification_types':['kyc']},{'id':'kyb-ca-v1','workflow_type':'verify','products':['insights','signal'],'verification_types':['kyb']}],
        'rulesets':[{'id':'monitoring-v1','attribute_keys':['cash_flow.net_monthly'],'resource_types':['bank_transaction']}],
        'cadences':[{'id':'daily','description':'Daily AMLOK evaluation subject to actual provider freshness and permission.'}],
        'limits':{'requests_per_minute':120,'burst_requests':20,'concurrent_jobs':5,'upload_bytes':10485760,'document_pages':100,'mime_types':['application/pdf']},
        'webhooks':{'event_retention_seconds':2592000,'delivery_timeout_seconds':10,'rotation_overlap_seconds':86400,'retained_from':'2026-09-23T14:00:00Z'},'idempotency_replay_seconds':86400}
    add('IR007','GET','/v1/configuration','Retrieve environment configuration','Platform','platform:read','EnvironmentConfiguration',configuration,
        'Read accepted identifiers and actual operational limits for the key-bound workspace and environment. Numbers in saved examples are synthetic, not production defaults or SLA promises. Use workflow_versions[].id as workflow_version, rulesets[].id as ruleset_version and cadences[].id as cadence. Resource and attribute selection must be allowed by that ruleset. GET /v1/providers supplies enabled product IDs and resource mappings. Rates and workload limits remain in read-only billing rate cards and workload reports. Cache by revision and refresh on configuration-related 422 errors or before adopting a new workflow. Changes to configured limits or identifiers are communicated through the account manager before taking effect under the agreement; in-flight work retains its accepted workflow revision.')
    for oid in ['EP142','EP147']:
        S[oid+'Request']['properties']['workflow_version']['description']='Approved ID from GET /v1/configuration workflow_versions, matching this workflow type and product.'
    for oid in ['EP150','EP151']:
        S[oid+'Request']['properties']['cadence']['description']='ID from GET /v1/configuration cadences. Invalid IDs return 422 validation_error. Source freshness is not guaranteed by this schedule.'
        S[oid+'Request']['properties']['ruleset_version']['description']='Approved ID from GET /v1/configuration rulesets; validate attributes and resource types against it.'

    S['ReadinessCheck']=obj({'code':text,'status':enum('passed','pending','blocked'),'message':text})
    S['SubjectReadiness']=obj({'subject_id':text,'product':enum('insights','signal'),'status':enum('ready','preparing','blocked'),
        'checks':arr(ref('ReadinessCheck')),'input_manifest_id':nullable(text),'baseline_snapshot_id':nullable(text),'next_action':enum('start_underwriting','create_monitor','wait','supply_evidence','contact_account_manager'),
        'retry_after_seconds':nullable(integer),'updated_at':date})
    S['SubjectReadiness']['allOf']=[
        {'if':{'properties':{'status':{'const':'ready'},'product':{'const':'insights'}}},'then':{'properties':{'input_manifest_id':text,'next_action':{'const':'start_underwriting'}}}},
        {'if':{'properties':{'status':{'const':'ready'},'product':{'const':'signal'}}},'then':{'properties':{'baseline_snapshot_id':text,'next_action':{'const':'create_monitor'}}}},
        {'if':{'properties':{'status':{'const':'preparing'}}},'then':{'properties':{'retry_after_seconds':{'type':'integer','minimum':1},'next_action':{'const':'wait'}}}},
    ]
    readiness={'subject_id':'biz_example','product':'insights','status':'ready','checks':[{'code':'bank_history_12_months','status':'passed','message':'At least 12 months of permitted banking evidence included.'}],
        'input_manifest_id':'manifest_example','baseline_snapshot_id':None,'next_action':'start_underwriting','retry_after_seconds':None,'updated_at':now}
    add('IR008','GET','/v1/subjects/{id}/readiness','Retrieve subject readiness','Risk','risk:read','SubjectReadiness',readiness,
        'Explain whether this subject has a ready evidence set for Insights or an approved baseline for Signal. After source sync and evidence acceptance, AMLOK automatically builds a frozen manifest. Checks include consent, source coverage, at least 12 months of banking history for Insights, required evidence and agreed scope. preparing supplies retry_after_seconds; blocked supplies actionable checks and next_action. Do not treat an empty manifest/baseline list as a completed onboarding. A ready Insights result identifies the manifest; a ready Signal result identifies the approved snapshot. Existing-portfolio Signal onboarding can create the baseline without charging Insights and is arranged with the account manager. This read does not approve evidence, process an underwriting or spend credits.',
        params=[param('product','Product being initialized.',True,enum('insights','signal'))])
    spec['paths']['/v1/subjects/{id}/readiness']['get']['description']+=' Signal readiness also requires monitoring:read. Initial Insights readiness covers intake evidence; staged owner KYC can remain a requirement on the subsequently accepted underwriting, avoiding a circular prerequisite.'

    # Durable delivery visibility; sensitive endpoint administration stays in the portal.
    event_example=deepcopy(E['WebhookEvent'])
    add('IR009','GET','/v1/webhook-events','List webhook events','Webhooks','webhooks:read','WebhookEvent',event_example,
        'Discover generated events even when none reached your receiver. Filter by creation time and type; order by (created_at, id), ascending. First page freezes the upper boundary; cursor retains it. Retention and retained_from are provided by configuration. A requested interval earlier than retained_from returns 410 event_history_expired, never a misleading empty success. Reconcile current state using checkpoints and the change feed after expiry. Event availability still requires the key\'s underlying resource read scopes. Polling events is read-only and does not redeliver them.',
        params=pages()+[param('created_from','Inclusive UTC lower boundary.',schema=date),param('created_to','Exclusive UTC upper boundary.',schema=date),param('type','Event type.',schema=S['WebhookEvent']['properties']['type'])],many=True)
    add('IR010','GET','/v1/webhook-events/{id}','Retrieve webhook event','Webhooks','webhooks:read','WebhookEvent',event_example,
        'Retrieve a retained event with its original ID and minimal payload. No provider credentials or signing secrets are returned. Enforce the original resource authorization. Expired known events return 410 event_history_expired; unknown or unauthorized IDs return 404. Retrieve the authoritative resource separately for current data.')
    S['WebhookDelivery']=obj({'id':text,'object':{'const':'webhook_delivery','type':'string'},'endpoint_id':text,'event_id':text,'attempt':{'type':'integer','minimum':1},
        'status':enum('queued','delivered','failed','exhausted'),'created_at':date,'attempted_at':nullable(date),'next_attempt_at':nullable(date),'http_status':nullable({'type':'integer','minimum':100,'maximum':599}),
        'failure_code':nullable(enum('timeout','dns_error','tls_error','http_error','endpoint_disabled')),'replay_request_id':nullable(text)})
    delivery={'id':'delivery_example','object':'webhook_delivery','endpoint_id':'whe_example','event_id':event_example['id'],'attempt':1,'status':'failed','created_at':now,'attempted_at':now,'next_attempt_at':'2026-10-23T14:01:00Z','http_status':503,'failure_code':'http_error','replay_request_id':None}
    add('IR011','GET','/v1/webhook-deliveries','List webhook deliveries','Webhooks','webhooks:read','WebhookDelivery',delivery,
        'Read one row per delivery attempt in ascending attempt time and ID order. Cursor freezes filters and upper boundary. Filter by endpoint_id or event_id to diagnose missed events, retries and replays. No receiver response body, authentication header or signing secret is retained in this public report. Queued attempts have null attempted_at. Final automatic failure is exhausted. Retention follows webhook event retention; earlier requested time returns 410 event_history_expired. Endpoint disablement cancels queued attempts without deleting retained events.',
        params=pages()+[param('endpoint_id','Registered destination.'),param('event_id','Original event ID.'),param('status','Delivery state.',schema=S['WebhookDelivery']['properties']['status']),param('created_from','Inclusive attempt creation time.',schema=date)],many=True)
    replay=spec['paths']['/v1/webhook-endpoints/{id}/replay']['post']
    replay['description']+=' Discover missing event IDs through GET /v1/webhook-events and inspect attempts through GET /v1/webhook-deliveries. Replay requires a retained event, original resource permission and an enabled endpoint subscribed to its type. Expired events return 410 event_history_expired; a disabled endpoint returns 409 invalid_state. Portal administrators manage destination URLs, subscriptions, enable/disable and signing-secret rotation. During the configured rotation overlap each delivery has v1 signatures for both old and new secrets; verifiers accept any matching v1. After the announced cutoff only the new secret signs deliveries.'
    replay['responses']['410']={'$ref':'#/components/responses/Error410'}

    # A sandbox fixture catalog supports executable customer acceptance journeys.
    S['SandboxScenario']=obj({'id':text,'object':{'const':'sandbox_scenario','type':'string'},'name':text,'subject_id':text,'application_id':nullable(text),
        'input_manifest_id':nullable(text),'baseline_snapshot_id':nullable(text),'connection_id':nullable(text),'person_id':nullable(text),'association_id':nullable(text),
        'document_id':nullable(text),'workflow_version':text,'ruleset_version':text,'cadence':text,'expected_http_status':{'type':'integer','minimum':200,'maximum':599},
        'expected_state':text,'instructions':text})
    scenarios=[]
    definitions=[
        ('insights_success','Completed full underwriting',202,'completed','Run the Insights journey. Includes two bank accounts, five business systems and at least twelve months of synthetic banking history. Expect one Standard Insights charge.'),
        ('signal_success','Monitoring and reassessment',201,'active','Run the Signal journey. A pre-approved existing-portfolio baseline and scheduled synthetic source update produce reassessment and an alert. Expect one Standard Signal charge and no Insights charge.'),
        ('insufficient_credits','Insufficient available credits',402,'insufficient_credits','Submit the Insights request; expect no accepted run or debit. Use portal sandbox funding to restore test credits, then retry the identical key.'),
        ('authorization_expired','Expired connection authorization',201,'reauth_required','Renew the supplied connection authorization; complete the sandbox hosted flow. Retrieve the same connection ID as active and then sync.'),
        ('rejected_evidence','Rejected evidence',202,'waiting_for_data','Start underwriting; the sandbox evidence validator rejects the seeded document and returns a rejected requirement with a reason. Upload its replacement from the portal-provided fixture pack using requirement_id; the same run resumes.'),
        ('workload_limit','Known workload limit exceeded',422,'workload_limit_exceeded','Submit the Insights request with over-limit evidence; expect no debit and no automatic tier change.'),
        ('retryable_failure','Retryable processing failure',202,'failed','Start the run and poll until failure.retryable is true. Retry that same run; its second attempt completes with one total Insights charge.'),
        ('owner_kyc','Related owner verification',201,'approved','Use an unfinished waiting-for-data business run from the fixture pack and its active association to request person KYC. The included check has no separate charge.'),
        ('duplicate_delivery','Duplicate webhook delivery',201,'delivered','Register a sandbox receiver; its seeded event is delivered twice with one event ID and fresh signatures. Reconcile attempts and replay using that ID; your consumer must apply the event once.'),
    ]
    for sid,name,http,status,instructions in definitions:
        x={'id':sid,'object':'sandbox_scenario','name':name,'subject_id':'biz_sandbox_'+sid,'application_id':'app_sandbox_'+sid,'input_manifest_id':'manifest_sandbox_'+sid,
           'baseline_snapshot_id':'rsk_sandbox_'+sid if sid=='signal_success' else None,'connection_id':'cnn_sandbox_'+sid,'person_id':'per_sandbox_'+sid,'association_id':'assoc_sandbox_'+sid,
           'document_id':'doc_sandbox_'+sid,'workflow_version':'underwrite-v1','ruleset_version':'monitoring-v1','cadence':'daily','expected_http_status':http,'expected_state':status,'instructions':instructions}
        scenarios.append(x)
    op=add('IR012','GET','/v1/sandbox/scenarios','List sandbox scenarios','Platform','platform:read','SandboxScenario',scenarios[0],
        'Return only synthetic fixtures provisioned in this sandbox workspace. Production returns 404; there are no production fault-injection or time-control commands. The account manager provides sandbox access and the fixture pack through the client portal. A portal administrator selects/reset scenarios before a test run; resetting discards only sandbox fixtures and test credits. GET never resets or mutates a scenario. Returned IDs and approved configuration are authoritative; do not use saved example IDs. Sandbox funding and simulated time controls stay in the portal, cannot move money, and cannot change production. Billing assertions use the real product rules with test credits.',many=True,params=pages())
    op['responses']['200']['content']['application/json']['examples']['synthetic']['value']['data']=scenarios

    # Explicit failure examples let generated clients exercise the recovery branch.
    failure_example={'code':'processing_timeout','message':'The processing attempt timed out.','retryable':True,'recovery_action':'retry_same_run','retry_after_seconds':30,'occurred_at':now,'request_id':'req_example'}
    media=spec['paths']['/v1/workflow-runs/{id}']['get']['responses']['200']['content']['application/json']
    failed=deepcopy(media['examples']['synthetic']['value'])
    failed['data'].update(status='failed',failure=failure_example,attempt=1,billing_usage_id=None,output_resource_ids=[])
    media['examples']['retryable_failure']={'summary':'Retryable failed attempt on the same run','value':failed}
    media=spec['paths']['/v1/requirements/{id}']['get']['responses']['200']['content']['application/json']
    rejected=deepcopy(media['examples']['synthetic']['value'])
    rejected['data'].update(status='rejected',rejection={'code':'unreadable','message':'Upload a legible replacement document.','document_ids':['doc_example'],'reviewed_at':now})
    media['examples']['rejected_evidence']={'summary':'Evidence rejected with a corrective action','value':rejected}

    # Keep every example, generated page and Postman request aligned with the refined schemas.
    defaults={'workflow_run':{'failure':None,'attempt':1},'requirement':{'rejection':None},'verification':{'subject_association_version':None}}
    def normalize(v):
        if isinstance(v,list):return [normalize(x) for x in v]
        if not isinstance(v,dict):return v
        v={k:normalize(x) for k,x in v.items()}
        kind=v.get('object')
        full=kind and any(k not in S['ResourceMetadata']['properties'] for k in v)
        if full and kind in defaults:
            for k,x in defaults[kind].items():v.setdefault(k,deepcopy(x))
        if full and kind=='workflow_run' and v.get('status')=='failed':
            v.update(failure={'code':'processing_timeout','message':'The processing attempt timed out.','retryable':True,'recovery_action':'retry_same_run','retry_after_seconds':30,'occurred_at':now,'request_id':'req_example'},billing_usage_id=None,output_resource_ids=[])
        if full and kind=='requirement' and v.get('status')=='rejected':v['rejection']={'code':'unreadable','message':'Upload a legible replacement document.','document_ids':['doc_example'],'reviewed_at':now}
        if 'provider_id' in v and 'resources' in v and 'limitations' in v and 'countries' in v and 'products' not in v:
            v['products']=[{'id':'transactions','resources':v['resources'],'consent_scopes':['banking:read'],'purposes':['credit_assessment']}]
        return v
    g['POSTMAN_GROUPS'].clear()
    for entry in g['OP_INDEX']:
        op=spec['paths'][entry['path']][entry['method'].lower()]
        media=op['responses'][entry['success']]['content']['application/json']
        for ex in media.get('examples',{}).values():ex['value']=normalize(ex['value'])
        entry['response']=media['examples']['synthetic']['value']
        reqmedia=next(iter(op.get('requestBody',{}).get('content',{}).values()),{})
        body=reqmedia.get('example');entry['request']=body
        path=entry['path']
        for p in op.get('parameters',[]):
            if p['in']=='path':path=path.replace('{'+p['name']+'}',str(p.get('example','res_example')))
        query={p['name']:p.get('example',('insights' if p['name']=='product' else 'EP147' if p['name']=='operation_id' else '/v1/workflow-runs' if p['name']=='target_path' else 'biz_example')) for p in op.get('parameters',[]) if p['in']=='query' and (p.get('required') or p.get('example') is not None)}
        if query:path+='?'+urlencode(query)
        if op.get('security')!=[]:op['x-codeSamples']=g['samples']({'Method':entry['method'],'Path':path,'Operation ID':entry['id']},op.get('parameters',[]),body,'res_example')
        item={'name':entry['title'],'request':{'method':entry['method'],'url':'{{base_url}}'+path,'header':[{'key':'Accept','value':'application/json'}],'description':op['description']}}
        if op.get('security')==[]:item['request']['auth']={'type':'noauth'}
        for p in op.get('parameters',[]):
            if p['in']=='header' and p.get('required'):item['request']['header'].append({'key':p['name'],'value':'{{idempotency_key}}' if p['name']=='Idempotency-Key' else p.get('example','')})
        if body:
            if entry['id']=='EP144':item['request']['body']={'mode':'formdata','formdata':[{'key':k,'type':'file','src':[]} if k=='file' else {'key':k,'type':'text','value':str(v)} for k,v in body.items()]}
            else:item['request']['header'].append({'key':'Content-Type','value':'application/json'});item['request']['body']={'mode':'raw','raw':g['dump'](body),'options':{'raw':{'language':'json'}}}
        item['response']=[{'name':'Synthetic '+entry['success'],'originalRequest':deepcopy(item['request']),'status':{'200':'OK','201':'Created','202':'Accepted'}[entry['success']],'code':int(entry['success']),'header':[{'key':'Content-Type','value':'application/json'}],'body':g['dump'](entry['response'])}]
        g['POSTMAN_GROUPS'][entry['group']].append(item)
        public='**Authentication:** public; no API key required.' if op.get('security')==[] else '**Required scope:** `'+entry['scope']+'`'
        g['write'](entry['page']+'.mdx','---\ntitle: '+json.dumps(entry['title'])+'\nopenapi: '+json.dumps('/openapi/amlok-v1.json '+entry['method']+' '+entry['path'])+'\nplayground: simple\n---\n\n'+public+'\n\n'+op['description']+'\n\n[Product scope](/api-reference/products-and-endpoints) · [Processing lifecycle](/api-reference/processing-lifecycle) · [Errors](/api-reference/errors)\n')
    g['write']('data/integration-api-index.json',g['dump'](new))
    for filename,items in [('reporting-api-index',[e for e in g['OP_INDEX'] if e['group']=='Reporting']),('baseline-api-index',[e for e in g['OP_INDEX'] if e['id'].startswith(('BM','BB'))]),('enterprise-api-index',[e for e in g['OP_INDEX'] if e['id'].startswith('EN')])]:g['write']('data/'+filename+'.json',g['dump'](items))
    return new

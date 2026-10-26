"""Final product, processing, synchronization and audit contracts.

This module authors documentation schemas. It does not implement a backend.
"""
from copy import deepcopy
from urllib.parse import urlencode
import csv
import hashlib
import io
import json


def extend(g):
    S, E, spec = g['SCHEMAS'], g['EXAMPLES'], g['SPEC']
    ref, nullable, now = g['ref'], g['nullable'], g['NOW']
    text = {'type': 'string', 'minLength': 1}
    date = {'type': 'string', 'format': 'date-time'}
    integer = {'type': 'integer', 'minimum': 0}
    enum = lambda *v: {'type': 'string', 'enum': list(v)}
    array = lambda v: {'type': 'array', 'items': deepcopy(v)}
    obj = lambda p, required=None: {'type': 'object', 'properties': {k:deepcopy(v) for k,v in p.items()}, 'required': list(p) if required is None else required, 'additionalProperties': False}
    new_ops = []

    def field(name, key, schema, value, required=True):
        S[name]['properties'][key] = schema
        if required and key not in S[name].setdefault('required', []):
            S[name]['required'].append(key)
        if name + 'Read' in S:
            S[name + 'Read']['properties'][key] = deepcopy(schema)
        if name in E:
            E[name][key] = deepcopy(value)

    def add(oid, method, path, title, group, schema, example, description, scope,
            params=None, request=None, body=None, is_list=False):
        parameters = list(params or [])
        if '{id}' in path and not any(p['name'] == 'id' for p in parameters):
            parameters.insert(0, g['parameter']('id', 'path', 'id', 'Authorized resource ID in this workspace.', True, example.get('id', 'manifest_example')))
        if method == 'POST':
            parameters.append(g['parameter']('Idempotency-Key', 'header', 'string', 'Stable key for one intended request. Reuse on retries.', True, 'idem_enterprise_example'))
        response_schema, response = g['envelope'](ref(schema), deepcopy(example), is_list)
        response['meta'] = g['meta']('complete')
        code = '201' if method == 'POST' else '200'
        op = {'operationId': oid, 'summary': title, 'description': description,
              'tags': [group], 'security': [{'BearerAuth': []}], 'x-required-scopes': [scope],
              'parameters': parameters, 'responses': {code: {'description': 'Authorized response.',
              'content': {'application/json': {'schema': response_schema, 'examples': {'synthetic': {'value': response}}}}}}}
        if request:
            op['requestBody'] = {'required': True, 'content': {'application/json': {'schema': ref(request), 'example': body}}}
        for error in ['400', '401', '403', '404', '409', '410', '422', '429', '500', '503']:
            op['responses'][error] = {'$ref': '#/components/responses/Error' + error}
        spec['paths'].setdefault(path, {})[method.lower()] = op
        page = 'api-reference/endpoints/' + ('billing' if group == 'Reporting' else group.lower()) + '/' + title.lower().replace(' ', '-')
        entry = {'id': oid, 'method': method, 'path': path, 'title': title, 'group': group,
                 'scope': scope, 'page': page, 'resource': example.get('object'),
                 'request': body, 'response': response, 'success': code}
        g['OP_INDEX'].append(entry)
        g['NAV_GROUPS'][group].append(page)
        new_ops.append(entry)
        return op

    def page_params():
        return [g['parameter']('limit', 'query', 'integer', 'Default 100; maximum 200.', False, 100, minimum=1, maximum=200),
                g['parameter']('cursor', 'query', 'string', 'Opaque continuation bound to the original filters and snapshot.')]

    # Approval of borrower actions is outside AMLOK. Evidence review remains a data-quality stage.
    S['Enum_workflow_status']['enum'] += ['waiting_for_credits', 'blocked_by_limit']
    S['Enum_search_status']['enum'].append('cancelled')
    S['Enum_verification_status']['enum'].append('cancelled')
    S['Enum_monitor_status']['enum'].append('blocked')
    S['Enum_alert_status']['enum'] = ['open', 'resolved']
    for name in ['WorkflowRun', 'WorkflowRunRead']:
        S[name]['properties'].pop('approval_required', None)
        S[name]['required'] = [k for k in S[name].get('required', []) if k != 'approval_required']
    for name in ['Document', 'DocumentRead']:
        S[name]['properties'].pop('legal_hold', None)
    field('Alert', 'status', {**ref('Enum_alert_status'), 'description': 'System-derived signal state. Open until comparable fresh evidence shows the triggering condition has cleared. No acknowledgement, case or borrower-contact workflow.'}, 'open')
    field('Monitor', 'blocked_reason', nullable(enum('insufficient_credits', 'workload_limit_exceeded', 'missing_evidence', 'consent_unavailable')), None)
    field('Monitor', 'monitoring_period_id', nullable(text), 'monitoring_period_example')
    field('WorkflowRun', 'product', enum('insights', 'signal'), 'insights')
    field('WorkflowRun', 'input_manifest_id', text, 'manifest_example')
    field('WorkflowRun', 'initial_input_manifest_id', text, 'manifest_example')
    field('WorkflowRun', 'workload_id', text, 'workload_example')
    field('WorkflowRun', 'billing_usage_id', nullable(text), 'billing_usage_example')
    field('WorkflowRun', 'monitoring_period_id', nullable(text), None)
    field('WorkflowRun', 'blocked_reason', nullable(enum('insufficient_credits', 'workload_limit_exceeded', 'missing_evidence')), None)
    field('RiskSnapshot', 'workflow_run_id', text, 'wfr_example')
    field('RiskSnapshot', 'application_id', nullable(text), 'app_example')
    field('RiskSnapshot', 'billing_usage_id', nullable(text), 'billing_usage_example')
    stop = nullable(enum('account_cancellation', 'parent_cancelled', 'consent_revoked'))
    for name in ['WorkflowRun', 'Verification', 'LienSearch', 'Document', 'CalculationJob']:
        field(name, 'stop_reason', stop, None)
    S['Document']['properties']['extraction_status'] = nullable(enum('pending', 'running', 'completed', 'partial', 'failed', 'cancelled'))
    S['DocumentRead']['properties']['extraction_status'] = deepcopy(S['Document']['properties']['extraction_status'])

    # A processing context authorizes a stage within an already agreed product, never a standalone fee.
    S['ProcessingContext'] = {'oneOf': [
        obj({'product': {'const': 'insights', 'type': 'string'}, 'workflow_run_id': text}),
        obj({'product': {'const': 'signal', 'type': 'string'}, 'monitoring_period_id': text}),
    ], 'discriminator': {'propertyName': 'product'},
       'description': 'Same-workspace and same-subject parent. Insights requires an unfinished authorized underwriting run; Signal requires an active paid monitoring period. AMLOK validates that this requested stage belongs to the agreed workflow and workload limits. No standalone service or additional product charge.'}
    context_example = {'product': 'insights', 'workflow_run_id': 'wfr_example'}
    for name in ['Verification', 'LienSearch', 'CalculationJob']:
        field(name, 'processing_context', ref('ProcessingContext'), context_example)
    for oid in ['EP142', 'EP143', 'EP148']:
        S[oid+'Request']['properties']['processing_context'] = ref('ProcessingContext')
        S[oid+'Request']['required'].append('processing_context')
        operation = next(o for methods in spec['paths'].values() for o in methods.values() if o['operationId'] == oid)
        operation['requestBody']['content']['application/json']['example']['processing_context'] = context_example
        operation['description'] += ' This is a stage of an authorized Insights or Signal workflow. processing_context is required; unrelated, completed, unpaid, cancelled or unentitled contexts return 409 invalid_state. It creates no separate AMLOK charge. The orchestrator deduplicates equivalent stage work within the parent.'
    verification_request=spec['paths']['/v1/verifications']['post']['requestBody']['content']['application/json']['example']
    verification_request.update(subject_id='biz_example',verification_type='kyb',workflow_version='kyb-ca-v1')
    S['EP147Request']['properties']['input_manifest_id'] = {**text, 'description': 'Ready immutable initial manifest for this run. All input references must exist in this manifest. Its ID is retained as initial_input_manifest_id. Accepted missing evidence can produce a successor manifest without changing the run or creating another charge; the current input_manifest_id and audit event identify it.'}
    S['EP147Request']['required'].append('input_manifest_id')
    S['EP147Request']['properties']['processing_context'] = ref('ProcessingContext')
    S['EP147Request']['allOf'] = [
        {'if': {'properties': {'workflow_type': {'const': 'underwrite'}}},
         'then': {'required': ['application_id'], 'not': {'required': ['processing_context']}}},
        {'if': {'properties': {'workflow_type': {'enum': ['verify', 'monitor', 'investigate']}}},
         'then': {'required': ['processing_context']}}
    ]
    run = spec['paths']['/v1/workflow-runs']['post']
    run['requestBody']['content']['application/json']['example']['input_manifest_id'] = 'manifest_example'
    run['requestBody']['content']['application/json']['example']['input_resource_ids'] = ['app_example', 'doc_example']
    run['description'] += ' A root underwrite request is a full Insights underwriting and requires application_id and input_manifest_id. Other workflow types require processing_context and are included stages. Signal reassessment is a Signal child run, never a separately billed root underwrite. Workload checks reject known over-limit inputs with 422 workload_limit_exceeded. If discovery reveals more records later, pause as blocked_by_limit before processing beyond the limit. No automatic tier upgrade occurs. Available credits are checked at acceptance and again atomically with output publication and the one usage debit at successful completion. No credits are reserved. If funds were spent by concurrent work, keep the run waiting_for_credits and withhold its final output; resume without duplicate processing when funded. Cancelled runs never publish or charge. Each evidence manifest is immutable. While an unfinished run waits for required evidence, accepted evidence can create a successor manifest; retain initial_input_manifest_id, update input_manifest_id and record_version, and emit an audit event identifying both manifests. The final snapshot and usage link to the final manifest. This continuation keeps the same run and single charge.'
    S['EP144Request']['properties']['requirement_id'] = {**text, 'description': 'Optional missing-evidence requirement in this subject and workspace. The upload is attached to the requirement; AMLOK validates evidence and resumes the parent when accepted.'}
    for oid in ['EP142', 'EP143', 'EP147', 'EP148', 'EP150', 'EP151']:
        operation = next(o for ms in spec['paths'].values() for o in ms.values() if o['operationId'] == oid)
        for code in ['402', '422']:
            operation['responses'][code] = {'$ref': '#/components/responses/Error'+code}

    signal_rule = 'Signal charges the full agreed monthly rate once per borrower/business/workspace at 00:00 UTC on the first day of the month, before monitoring proceeds. First activation during a month charges the full monthly rate immediately, without proration; the next charge is at the next month boundary. Repeated monitor creation, pauses, resumes, checks and reassessments do not add charges in an already paid period. Insufficient credits block monitoring without a debit or debt; funding resumes only the current period after its single successful charge, without charging missed inactive months. User-paused monitoring remains paused until the user resumes it. Account cancellation stops processing and all further deductions immediately.'
    for method in ['post', 'patch']:
        path = '/v1/monitors' if method == 'post' else '/v1/monitors/{id}'
        spec['paths'][path][method]['description'] += ' '+signal_rule
    # System-only blocked state must not be a user-controlled PATCH value.
    S['EP151Request']['properties']['status'] = enum('active', 'paused', 'cancelled')

    # Two-record shared fixture: one Signal month (3.00), one Insights underwriting (5.00).
    insights = deepcopy(E['BillingUsage'])
    signal = deepcopy(insights)
    signal.update(id='billing_usage_signal', product='signal', source_resource_id='biz_example', unit='active_account_month',
                  unit_rate='3.00', amount='3.00', workflow_run_id=None, application_id=None,
                  input_manifest_id='manifest_example', risk_snapshot_id='rsk_baseline', monitoring_period_id='monitoring_period_example',
                  ledger_entry_id='ledger_signal_example', occurred_at='2026-10-01T00:00:00Z', posted_at='2026-10-01T00:00:00Z',
                  created_at='2026-10-01T00:00:00Z', updated_at='2026-10-01T00:00:00Z')
    funding_entry = deepcopy(E['BillingCreditEntry'])
    funding_entry.update(id='ledger_funding_example', sequence=1, amount='12000.00', balance_after='12000.00', entry_type='funding',
                         movement_id=E['BillingFunding']['id'], posted_at='2026-09-30T14:00:00Z', created_at='2026-09-30T14:00:00Z', updated_at='2026-09-30T14:00:00Z', client_reference='annual-prepayment')
    signal_entry = deepcopy(E['BillingCreditEntry'])
    signal_entry.update(id='ledger_signal_example', sequence=2, amount='-3.00', balance_after='11997.00', movement_id=signal['id'],
                        posted_at='2026-10-01T00:00:00Z', created_at='2026-10-01T00:00:00Z', updated_at='2026-10-01T00:00:00Z', client_reference='signal-october')
    fixtures = {'usage': [signal, insights], 'ledger': [funding_entry, signal_entry, deepcopy(E['BillingCreditEntry'])],
                'statement': [deepcopy(E['BillingStatement'])], 'funding': [deepcopy(E['BillingFunding'])]}
    for path, records in [('/v1/billing/usage', fixtures['usage']), ('/v1/billing/credit-ledger', fixtures['ledger'])]:
        spec['paths'][path]['get']['responses']['200']['content']['application/json']['examples']['synthetic']['value']['data'] = records
    for name,key,description in [
        ('BillingCreditBalance','spent_credits','Cumulative product charges minus correcting reversals since account opening, at this snapshot. Refunds are not product spend. Read consumption reports for a particular period.'),
        ('BillingCreditBalance','available_credits','One spendable CAD balance. Top-ups increase it; completed product charges and final refunds decrease it. There are no reserved credits or separate posted-credit balances.'),
        ('BillingAccount','auto_top_up_threshold','Actual configured threshold, at least CAD 200. Compare against available_credits. Only the portal can change it.'),
        ('BillingAccount','auto_top_up_amount','Actual configured amount, at least CAD 500. Only the portal can change it.'),
    ]:
        S[name]['properties'][key]={**S[name]['properties'][key],'description':description}
    for r in E['BillingRateCard']['rates']:
        if r['product'] == 'signal':
            r['billing_timing'] = 'month_start_or_first_activation'
        else:
            r['billing_timing'] = 'successful_output_completion'
    S['BillingRate']['properties']['billing_timing'] = enum('month_start_or_first_activation', 'successful_output_completion')
    S['BillingRate']['required'].append('billing_timing')
    S['BillingRate'].setdefault('allOf',[]).extend([
        {'if':{'properties':{'product':{'const':'signal'}}},'then':{'properties':{'billing_timing':{'const':'month_start_or_first_activation'}}}},
        {'if':{'properties':{'product':{'const':'insights'}}},'then':{'properties':{'billing_timing':{'const':'successful_output_completion'}}}},
    ])
    S['BillingUsage']['allOf'] = [
        {'if':{'properties':{'product':{'const':'insights'}}},'then':{'properties':{'unit':{'const':'completed_underwriting'},'workflow_run_id':text,'input_manifest_id':text,'risk_snapshot_id':text,'monitoring_period_id':{'type':'null'}}}},
        {'if':{'properties':{'product':{'const':'signal'}}},'then':{'properties':{'unit':{'const':'active_account_month'},'monitoring_period_id':text}}},
        {'if':{'properties':{'entry_type':{'const':'charge'}}},'then':{'properties':{'quantity':{'const':'1'},'amount':{'pattern':r'^(0|[1-9][0-9]*)\.[0-9]{2}$'},'reverses_usage_id':{'type':'null'}}}},
        {'if':{'properties':{'entry_type':{'const':'reversal'}}},'then':{'properties':{'amount':{'pattern':r'^-(0|[1-9][0-9]*)\.[0-9]{2}$'},'reverses_usage_id':text}}},
    ]

    # Workload visibility is read-only. Counts are not credits, prices or extra billable units.
    S['WorkloadDimension'] = obj({'used': integer, 'limit': integer, 'remaining': integer})
    S['WorkloadReport'] = obj({'id': text, 'object': {'const': 'workload', 'type': 'string'}, 'workspace_id': text,
        'subject_id': text, 'product': enum('insights', 'signal'), 'workflow_run_id': nullable(text),
        'monitoring_period_id': nullable(text), 'rate_card_id': text, 'tier': enum('standard', 'advanced', 'complex'),
        'as_of': date, 'period_start': date, 'period_end': date, 'record_counting_basis': enum('per_underwriting', 'new_records_per_month'),
        'bank_accounts': ref('WorkloadDimension'), 'business_integrations': ref('WorkloadDimension'), 'records': ref('WorkloadDimension'),
        'status': enum('within_limits', 'at_limit', 'blocked'), 'blocking_dimensions': array(enum('bank_accounts', 'business_integrations', 'records', 'analysis_scope')),
        'analysis_scope': text, 'input_manifest_id': nullable(text)})
    workload = {'id': 'workload_example', 'object': 'workload', 'workspace_id': 'wsp_example', 'subject_id': 'biz_example', 'product': 'insights',
        'workflow_run_id': 'wfr_example', 'monitoring_period_id': None, 'rate_card_id': E['BillingRateCard']['id'], 'tier': 'standard', 'as_of': now,
        'period_start': '2025-10-01T00:00:00Z', 'period_end': '2026-10-01T00:00:00Z', 'record_counting_basis': 'per_underwriting',
        'bank_accounts': {'used': 2, 'limit': 2, 'remaining': 0}, 'business_integrations': {'used': 5, 'limit': 5, 'remaining': 0},
        'records': {'used': 2, 'limit': 75000, 'remaining': 74998}, 'status': 'at_limit', 'blocking_dimensions': [],
        'analysis_scope': 'Routine reconciliation and standard analysis', 'input_manifest_id': 'manifest_example'}
    workload_description = 'Read measured workload against the agreed limits. At a limit, work already within scope can continue; the next operation that would exceed any dimension is rejected or blocked before excess records are processed. Counts across monitors are deduplicated by subject, source record ID and source version during the month. No automatic repricing, mixed-tier limits or extra usage charge occurs. AMLOK must approve an amended rate card before blocked work resumes. Whole-underwriting counts include the complete evidence history; Signal counts only new processed record versions in the UTC calendar month. Counters and limit checks are atomic across concurrent work. as_of and the cursor freeze a read snapshot; a new first-page read gets current progress.'
    filters = [g['parameter']('subject_id', 'query', 'id', 'Authorized borrower/business.', False, 'biz_example'), g['parameter']('product', 'query', 'string', 'Product filter.', False, None, enum=['insights','signal'])] + page_params()
    add('EN001', 'GET', '/v1/workloads', 'List workload reports', 'Reporting', 'WorkloadReport', workload, workload_description, 'billing:read', params=filters, is_list=True)
    add('EN002', 'GET', '/v1/workloads/{id}', 'Retrieve workload report', 'Reporting', 'WorkloadReport', workload, workload_description, 'billing:read')
    signal_workload = deepcopy(workload)
    signal_workload.update(id='workload_signal_example', product='signal', workflow_run_id=None,
        monitoring_period_id='monitoring_period_example', period_start='2026-10-01T00:00:00Z',
        period_end='2026-11-01T00:00:00Z', record_counting_basis='new_records_per_month',
        records={'used': 50, 'limit': 75000, 'remaining': 74950}, input_manifest_id=None)
    spec['paths']['/v1/workloads']['get']['responses']['200']['content']['application/json']['examples']['synthetic']['value']['data'].append(signal_workload)

    S['MonitoringPeriod'] = obj({'id': text, 'object': {'const': 'monitoring_period', 'type':'string'}, 'workspace_id': text, 'subject_id': text,
        'period_start': date, 'period_end': date, 'first_activated_at': date, 'charged_at': nullable(date), 'billing_usage_id': nullable(text),
        'status': enum('active', 'paused', 'blocked', 'unfunded', 'cancelled'), 'workload_id': text, 'baseline_snapshot_id': text,
        'rate_card_id': text, 'tier': enum('standard','advanced','complex'), 'blocked_reason': nullable(enum('insufficient_credits','workload_limit_exceeded','missing_evidence','consent_unavailable'))})
    period = {'id':'monitoring_period_example','object':'monitoring_period','workspace_id':'wsp_example','subject_id':'biz_example',
        'period_start':'2026-10-01T00:00:00Z','period_end':'2026-11-01T00:00:00Z','first_activated_at':'2026-10-01T00:00:00Z','charged_at':'2026-10-01T00:00:00Z',
        'billing_usage_id':'billing_usage_signal','status':'active','workload_id':'workload_signal_example','baseline_snapshot_id':'rsk_baseline',
        'rate_card_id':E['BillingRateCard']['id'],'tier':'standard','blocked_reason':None}
    period_filters = [g['parameter']('subject_id','query','id','Authorized borrower/business.',False,'biz_example'),
        g['parameter']('period_start','query','datetime','Inclusive UTC period-start boundary.'),
        g['parameter']('period_end','query','datetime','Exclusive UTC period-start boundary.')] + page_params()
    add('EN003','GET','/v1/monitoring-periods','List monitoring periods','Risk','MonitoringPeriod',period,signal_rule+' Read one shared record per subject/month, including its charge and workload references. Periods are immutable in identity; current status and charged_at reflect activation. API reads never create a charge.', 'monitoring:read',params=period_filters,is_list=True)
    add('EN004','GET','/v1/monitoring-periods/{id}','Retrieve monitoring period','Risk','MonitoringPeriod',period,signal_rule,'monitoring:read')

    # Exact version references plus a specified digest allow an audit of frozen input sets.
    S['ManifestEntry'] = obj({'resource_type':text,'resource_id':text,'resource_version':{'type':'integer','minimum':1},'source_record_id':text,'source_version':text,'content_sha256':{'type':'string','pattern':'^[a-f0-9]{64}$'}})
    manifest_entries = [
        {'resource_type':'application','resource_id':'app_example','resource_version':1,'source_record_id':'client-application-example','source_version':'1','content_sha256':'a'*64},
        {'resource_type':'document','resource_id':'doc_example','resource_version':1,'source_record_id':'client-document-example','source_version':'1','content_sha256':'b'*64},
    ]
    digest_text = ''.join(json.dumps(e, ensure_ascii=False, sort_keys=True, separators=(',', ':'))+'\n' for e in manifest_entries)
    E['InputManifest']['record_count'] = 2
    E['InputManifest']['sha256'] = hashlib.sha256(digest_text.encode()).hexdigest()
    S['InputManifest']['properties']['sha256']['description'] = 'SHA-256 of UTF-8 NDJSON manifest entries sorted by (resource_type, resource_id, resource_version), with keys sorted lexically, compact separators and one LF after every entry. Concatenate every page before hashing. This proves manifest membership, not correctness of the source evidence.'
    manifest_op = add('EN005','GET','/v1/input-manifests/{id}/entries','List input manifest entries','Risk','ManifestEntry',manifest_entries[0],
        'Read the frozen source and normalized record-version references for an immutable input manifest. The path ID is the manifest ID. Order by resource_type, resource_id, resource_version; cursors remain bound to the same manifest. The record_count equals the complete entry count, including separately analyzed line items. Download the actual frozen normalized evidence through the record endpoint using manifest_id; raw documents use the document download route with the same manifest_id. Hash canonicalization is specified on InputManifest.sha256. Missing authorization returns 403; unavailable or deleted evidence returns 404 rather than substituting a newer record.', 'risk:read',params=page_params(),is_list=True)
    manifest_op['parameters'][0]['example'] = 'manifest_example'
    manifest_op['responses']['200']['content']['application/json']['examples']['synthetic']['value']['data'] = manifest_entries

    # A checkpoint freezes bootstrap reads and starts a durable change-feed position at that boundary.
    S['CreateSyncCheckpoint'] = obj({'resource_types':array(text)})
    S['CreateSyncCheckpoint']['properties']['resource_types']['minItems'] = 1
    S['CreateSyncCheckpoint']['properties']['resource_types']['items']['enum'] = list(g['ENTITIES'])
    S['SyncCheckpoint'] = obj({'id':text,'object':{'type':'string','const':'sync_checkpoint'},'workspace_id':text,'as_of':date,'expires_at':date,'resource_types':array(text),'resume_cursor':text})
    checkpoint = {'id':'checkpoint_example','object':'sync_checkpoint','workspace_id':'wsp_example','as_of':now,'expires_at':'2026-11-01T14:00:00Z','resource_types':['bank_transaction','lien'],'resume_cursor':'changes_after_checkpoint_example'}
    add('EN006','POST','/v1/sync-checkpoints','Create synchronization checkpoint','Platform','SyncCheckpoint',checkpoint,
        'Create a read-only synchronization boundary. This does not synchronize a provider, process a product or spend credits. Read each requested collection with snapshot_id equal to this checkpoint ID, then consume /v1/changes from resume_cursor. Both refer to the same as_of boundary, preventing a bootstrap gap. Snapshots and resume cursors remain valid until their explicit expires_at. Reject unentitled types. Workspace deletion revokes checkpoints. Checkpoint creation remains available while read-only reporting access remains active.', 'platform:read',request='CreateSyncCheckpoint',body={'resource_types':['bank_transaction','lien']})
    S['ChangePage']['properties']['resume_cursor'] = {**text,'description':'Durable position after every change in this response; returned even for an empty page. Persist atomically with processed changes.'}
    S['ChangePage']['properties']['cursor_expires_at'] = date
    S['ChangePage']['required'] += ['resume_cursor','cursor_expires_at']
    S['Change']['properties']['sequence'] = {'type':'integer','minimum':1,'description':'Monotonic workspace change sequence. Gaps are valid when filtering resource types.'}
    S['Change']['required'].append('sequence')
    change = spec['paths']['/v1/changes']['get']
    change['description'] = 'Read created, updated and deleted normalized-resource changes in ascending sequence order. A cursor from a synchronization checkpoint is required on the first request; thereafter use the returned resume_cursor. Never reuse a collection cursor. Persist the returned resume_cursor only after durably applying every event in the page, deduplicating by resource type, ID and version. A terminal or empty page still returns a resume_cursor; poll it later to receive new changes. Each successful poll returns cursor_expires_at. A cursor expired beyond that time returns 410 cursor_expired and requires a new checkpoint plus a fresh bootstrap. Filters and workspace binding cannot change mid-stream. Deleted resources emit tombstones. Billing resources use billing snapshots and billing events, not this normalized-data feed.'
    for p in change['parameters']:
        if p['name']=='cursor': p.update(required=True,example='changes_after_checkpoint_example')
        if p['name']=='resource_types': p.update(description='Optional comma-separated types. When omitted, inherit the checkpoint types; if supplied, must match them exactly.',example='bank_transaction,lien')
    val = change['responses']['200']['content']['application/json']['examples']['synthetic']['value']
    val.update(resume_cursor='changes_after_sequence_42',cursor_expires_at='2026-11-01T14:00:00Z')
    val['data'][0]['sequence']=42
    val['meta']=g['meta']('complete')
    change['responses']['410']={'$ref':'#/components/responses/Error410'}
    for entry in g['OP_INDEX']:
        op=spec['paths'][entry['path']][entry['method'].lower()]
        if entry['method']=='GET' and entry['resource'] in g['ENTITIES']:
            op['responses']['410']={'$ref':'#/components/responses/Error410'}
            if '{id}' not in entry['path']:
                op['parameters'].append(g['parameter']('snapshot_id','query','string','Optional synchronization-checkpoint ID. Freezes this collection at the checkpoint boundary; cursor binds the snapshot. Unsupported or expired snapshots return 410.'))
            else:
                op['parameters'].append(g['parameter']('manifest_id','query','string','Optional immutable input-manifest ID. Return the exact normalized resource version listed in that manifest, not the current version. Reject IDs absent from the manifest or another subject/workspace.'))
        if entry['id']=='EP145':
            S['EP145Request']['properties']['manifest_id']={**text,'description':'Return the exact document bytes referenced by this manifest. Never substitute the latest document version.'}

    # Synchronize every generated representation after schema refinements.
    def normalize(value):
        if isinstance(value,list): return [normalize(v) for v in value]
        if not isinstance(value,dict): return value
        value={k:normalize(v) for k,v in value.items() if k not in ['approval_required','legal_hold']}
        kind=value.get('object')
        canonical=next((n for n,x in E.items() if isinstance(x,dict) and x.get('object')==kind),None) if kind else None
        # Metadata-only projections deliberately omit all domain properties.
        full=kind and any(k not in S['ResourceMetadata']['properties'] for k in value)
        if full and canonical:
            for k in S.get(canonical,{}).get('required',[]):
                if k not in value and k in E[canonical]: value[k]=deepcopy(E[canonical][k])
        if kind=='workflow_run' and full:
            value.update(product='insights',input_manifest_id='manifest_example',workload_id='workload_example',monitoring_period_id=None,blocked_reason=None,stop_reason=None)
            if value.get('status') in ['queued','running']:
                value['billing_usage_id']=None;value['output_resource_ids']=[]
            else: value['billing_usage_id']='billing_usage_example'
        if kind=='alert' and full: value['status']='open';value['resolved_at']=None
        if kind=='verification' and full:
            value.update(subject_id='biz_example',verification_type='kyb',workflow_version='kyb-ca-v1')
        if kind=='document' and full and value.get('extraction_status') not in ['pending','running','completed','partial','failed','cancelled',None]:value['extraction_status']='completed'
        if kind=='input_manifest' and full:
            value['record_count']=2;value['sha256']=E['InputManifest']['sha256']
            value['created_at']=value['updated_at']='2026-10-01T00:00:00Z'
        if kind=='monitoring_baseline' and full:
            value['created_at']=value['updated_at']=value['approved_at']='2026-10-01T00:00:00Z'
        if kind=='billing_rate_card': value['rates']=deepcopy(E['BillingRateCard']['rates'])
        if kind=='billing_download': value['sha256']=hashlib.sha256((g['ROOT']/'downloads/report-examples/usage.csv').read_bytes()).hexdigest()
        return value

    # Machine-readable export schemas and real synthetic files share the HTTP examples.
    export_names={'usage':'BillingUsage','ledger':'BillingCreditEntry','statement':'BillingStatement','funding':'BillingFunding'}
    exports=[]
    for kind,name in export_names.items():
        schema_name='Billing'+kind.title()+'Export'
        S[schema_name]=obj({'schema_version':{'type':'string','const':g['VERSION']},'report_type':{'type':'string','const':kind},'snapshot_id':text,'as_of':date,'rows':array(ref(name))})
        # The ledger export uses the October window, unlike the unfiltered ledger endpoint.
        records=fixtures[kind][1:] if kind=='ledger' else ([] if kind=='funding' else fixtures[kind])
        payload={'schema_version':g['VERSION'],'report_type':kind,'snapshot_id':E['BillingSnapshot']['id'],'as_of':now,'rows':records}
        base='downloads/report-examples/'+kind
        g['write'](base+'.json',g['dump'](payload))
        columns=['export_schema_version','export_snapshot_id','export_as_of']+list(S[name]['properties'])
        buffer=io.StringIO(newline='');writer=csv.writer(buffer,lineterminator='\r\n');writer.writerow(columns)
        for record in records:
            cells=[g['VERSION'],E['BillingSnapshot']['id'],now]
            for key in S[name]['properties']:
                value=record.get(key)
                cell='' if value is None else json.dumps(value,separators=(',',':')) if isinstance(value,(dict,list)) else str(value)
                # Numeric decimal fields are validated numbers; escape formula-like text fields only.
                if cell and cell[0] in '=+-@\t\r' and 'pattern' not in S[name]['properties'][key]: cell="'"+cell
                cells.append(cell)
            writer.writerow(cells)
        (g['ROOT']/(base+'.csv')).write_bytes(buffer.getvalue().encode())
        selected={}
        def include_schema(n):
            if n in selected:return
            selected[n]=deepcopy(S[n])
            def visit(v):
                if isinstance(v,dict):
                    if '$ref' in v:include_schema(v['$ref'].split('/')[-1])
                    for child in v.values():visit(child)
                elif isinstance(v,list):
                    for child in v:visit(child)
            visit(S[n])
        include_schema(schema_name)
        g['write']('downloads/report-schemas/'+kind+'.schema.json',g['dump']({'$schema':'https://json-schema.org/draft/2020-12/schema','$ref':'#/components/schemas/'+schema_name,'components':{'schemas':selected}}))
        exports.append({'type':kind,'schema':schema_name,'columns':columns,'example':payload})
    g['write']('data/report-export-contract.json',g['dump'](exports))

    g['POSTMAN_GROUPS'].clear()
    for entry in g['OP_INDEX']:
        op=spec['paths'][entry['path']][entry['method'].lower()]
        body_media=next(iter(op.get('requestBody',{}).get('content',{}).values()),None)
        body=body_media.get('example') if body_media else None
        entry['request']=body
        response_media=op['responses'][entry['success']]['content']['application/json']
        for example in response_media.get('examples',{}).values():example['value']=normalize(example['value'])
        if entry['id'] in ['EP148','EP149']:
            response_media['examples']['synthetic']['value']['data']['stop_reason']=None
            response_media['examples']['synthetic']['value']['data']['processing_context']=deepcopy(context_example)
        if entry['id']=='EP143':
            created=response_media['examples']['synthetic']['value']['data']
            created.update(jurisdictions_requested=body['jurisdictions'],jurisdictions_completed=[],missing_fields=[])
        if entry['id']=='EP144':
            response_media['examples']['synthetic']['value']['data']['id']='doc_upload_example'
        response=response_media['examples']['synthetic']['value']
        if entry['path']=='/v1/billing/reports/{id}' and entry['method']=='GET':
            response['data'].update(status='ready',row_count=2,expires_at='2026-11-01T14:00:00Z',record_version=2)
            op['responses'][entry['success']]['headers']['ETag']['example']='"2:billing_snapshot_example"'
        entry['response']=response
        path=entry['path']
        for p in op['parameters']:
            if p['in']=='path':path=path.replace('{'+p['name']+'}',str(p.get('example','res_example')))
        query={p['name']:p['example'] for p in op['parameters'] if p['in']=='query' and p.get('example') is not None}
        if query:path+='?'+urlencode(query)
        # Preserve purpose-built unauthenticated examples.
        if op.get('security')!=[]:
            op['x-codeSamples']=g['samples']({'Method':entry['method'],'Path':path,'Operation ID':entry['id']},op['parameters'],body,'res_example')
        item={'name':entry['title'],'request':{'method':entry['method'],'url':'{{base_url}}'+path,'header':[{'key':'Accept','value':'application/json'}],'description':op['description']}}
        if op.get('security')==[]:item['request']['auth']={'type':'noauth'}
        for p in op['parameters']:
            if p['in']=='header' and p['required']:item['request']['header'].append({'key':p['name'],'value':'{{idempotency_key}}' if p['name']=='Idempotency-Key' else p.get('example','')})
        if body:
            if entry['id']=='EP144':item['request']['body']={'mode':'formdata','formdata':[{'key':k,'type':'file','src':[]} if k=='file' else {'key':k,'type':'text','value':str(v)} for k,v in body.items()]}
            else:item['request']['header'].append({'key':'Content-Type','value':'application/json'});item['request']['body']={'mode':'raw','raw':g['dump'](body),'options':{'raw':{'language':'json'}}}
        item['response']=[{'name':'Synthetic '+entry['success'],'originalRequest':deepcopy(item['request']),'status':{'200':'OK','201':'Created','202':'Accepted'}[entry['success']],'code':int(entry['success']),'header':[{'key':'Content-Type','value':'application/json'}],'body':g['dump'](response)}]
        g['POSTMAN_GROUPS'][entry['group']].append(item)
        page=g['ROOT']/(entry['page']+'.mdx')
        # Rebuild endpoint prose from the same operation contract to avoid stale side notes.
        public='**Authentication:** public; no API key required.' if op.get('security')==[] else '**Required scope:** `'+entry['scope']+'`'
        g['write'](entry['page']+'.mdx','---\ntitle: '+json.dumps(entry['title'])+'\nopenapi: '+json.dumps('/openapi/amlok-v1.json '+entry['method']+' '+entry['path'])+'\nplayground: simple\n---\n\n'+public+'\n\n'+op['description']+'\n\n[Product scope](/api-reference/products-and-endpoints) · [Processing lifecycle](/api-reference/processing-lifecycle) · [Errors](/api-reference/errors)\n')
    g['write']('data/reporting-api-index.json',g['dump']([o for o in g['OP_INDEX'] if o['group']=='Reporting']))
    g['write']('data/baseline-api-index.json',g['dump']([o for o in g['OP_INDEX'] if o['id'].startswith(('BM','BB'))]))
    g['write']('data/enterprise-api-index.json',g['dump'](new_ops))
    g['REFINEMENTS'].append('Credits expose only available and spent totals. Signal charges at month start or first activation. Included processing stages require a product context. Added immutable evidence membership, workload visibility, Signal period reports, bootstrap checkpoints, resumable changes, and specified billing export files. No backend was executed.')
    return new_ops

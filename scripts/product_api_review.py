"""Authoritative v2 contract and exhaustive v1 migration inventory.

Documentation publication does not deploy the product backend.
"""
from collections import Counter
from copy import deepcopy
import csv
import io
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION = '2.0.0'
STATUS = 'published_contract'


def ref(name):
    return {'$ref': '#/components/schemas/' + name}


def text(description='', **extra):
    return {'type': 'string', 'minLength': 1, **({'description': description} if description else {}), **extra}


def enum(*values):
    return {'type': 'string', 'enum': list(values)}


def array(items, **extra):
    return {'type': 'array', 'items': items, **extra}


def obj(properties, required=None, **extra):
    return {'type': 'object', 'properties': properties, 'required': list(properties) if required is None else required, 'additionalProperties': False, **extra}


def nullable(schema):
    return {'anyOf': [schema, {'type': 'null'}]}


def build_schemas(legacy):
    schemas = {}
    def legacy_schema(value):
        if isinstance(value, dict):
            return {key: ('#/components/schemas/Legacy' + child.rsplit('/', 1)[-1] if key == '$ref' else legacy_schema(child)) for key, child in value.items()}
        if isinstance(value, list): return [legacy_schema(child) for child in value]
        return value
    stamp = text(format='date-time')
    decimal = text(pattern=r'^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$')
    identifier = text('Opaque identifier, authorized within the API key workspace and environment.')
    ids = array(identifier, uniqueItems=True)
    money = obj({'amount': text(pattern=r'^(?:0|[1-9][0-9]*)\.[0-9]{2}$'), 'currency': text(pattern='^[A-Z]{3}$')})
    schemas['Money'] = money
    schemas['Window'] = obj({'start': stamp, 'end': stamp}, description='UTC interval [start, end). The server rejects end <= start.')
    schemas['VersionReference'] = obj({'id': identifier, 'version': text(), 'sha256': text(pattern='^[a-f0-9]{64}$')})
    schemas['Meta'] = obj({'request_id': identifier, 'schema_version': text(), 'environment': enum('sandbox', 'live')})
    schemas['Page'] = obj({'next_cursor': nullable(text()), 'has_more': {'type': 'boolean'}, 'snapshot_id': identifier}, description='Opaque cursor binds filters, authorization and a stable snapshot. Expired cursors return 410; never silently restart.')
    schemas['Error'] = obj({'code': enum('validation_error', 'unauthenticated', 'forbidden', 'not_found', 'invalid_state', 'idempotency_conflict', 'insufficient_credits', 'precondition_failed', 'cursor_expired', 'rate_limited', 'temporarily_unavailable'), 'message': text(), 'retryable': {'type': 'boolean'}, 'request_id': identifier, 'field': nullable(text())})
    schemas['BusinessInput'] = legacy_schema(legacy['EP135Request'])
    schemas['PersonInput'] = legacy_schema(legacy['EP136Request'])
    schemas['CreateBorrower'] = {'oneOf': [
        obj({'type': {'const': 'business'}, 'business': ref('BusinessInput')}),
        obj({'type': {'const': 'person'}, 'person': ref('PersonInput')})]}
    schemas['Borrower'] = obj({'id': identifier, 'type': enum('business', 'person'), 'subject_id': identifier, 'created_at': stamp, 'client_reference': nullable(text()), 'profile': ref('CreateBorrower')})
    schemas['CreateEmbeddingSession'] = obj({
        'borrower_id': identifier, 'embedding_version_id': identifier,
        'purpose': enum('connect', 'reauthorize'), 'connection_id': identifier,
        'return_url': text('Must match an institution-approved return URL. No arbitrary redirects.', format='uri'),
        'origination_id': identifier,
    }, ['borrower_id', 'embedding_version_id', 'purpose', 'return_url'], allOf=[{'if': {'properties': {'purpose': {'const': 'reauthorize'}}}, 'then': {'required': ['connection_id']}, 'else': {'not': {'required': ['connection_id']}}}])
    schemas['EmbeddingSession'] = obj({'id': identifier, 'borrower_id': identifier, 'status': enum('created', 'in_progress', 'completed', 'expired', 'failed'), 'launch_url': nullable(text('Short-lived borrower session, never an institution API key.', format='uri')), 'expires_at': stamp, 'connection_ids': ids, 'consent_ids': ids}, description='Completion means the connection journey completed, not that source ingestion or underwriting completed. URLs are returned only to authorized callers; never send in events.')
    schemas['Connection'] = obj({'id': identifier, 'borrower_id': identifier, 'integration_id': identifier, 'status': enum('pending', 'connected', 'reauthorization_required', 'revoked', 'failed'), 'consent_id': identifier, 'last_successful_sync_at': nullable(stamp), 'source_as_of': nullable(stamp), 'coverage': nullable(ref('Window')), 'missing_reason': nullable(text())})
    schemas['Consent'] = obj({'id': identifier, 'borrower_id': identifier, 'status': enum('active', 'revoked', 'expired'), 'purposes': array(text()), 'captured_at': stamp, 'expires_at': nullable(stamp), 'revoked_at': nullable(stamp)})
    schemas['RevokeConsent'] = obj({'reason': text()})
    schemas['UploadDocument'] = obj({'file': {'type': 'string', 'format': 'binary'}, 'context':enum('borrower','lending_product','risk_policy'), 'borrower_id': identifier, 'document_type': text(), 'origination_id': identifier, 'requirement_id': identifier}, ['file', 'context', 'document_type'], allOf=[{'if':{'properties':{'context':{'const':'borrower'}}},'then':{'required':['borrower_id']},'else':{'not':{'anyOf':[{'required':[key]} for key in ['borrower_id','origination_id','requirement_id']]}}}])
    schemas['Document'] = obj({'id': identifier, 'context':enum('borrower','lending_product','risk_policy'), 'borrower_id': nullable(identifier), 'file_name': text(), 'mime_type': text(), 'sha256': text(pattern='^[a-f0-9]{64}$'), 'size_bytes': {'type': 'integer', 'minimum': 0}, 'status': enum('processing', 'available', 'rejected', 'restricted'), 'restriction_reason': nullable(text())})
    schemas['DownloadPurpose'] = obj({'purpose': text('Authorized reason for accessing evidence or an export.')})
    schemas['DownloadLink'] = obj({'url': text('Short-lived HTTPS URL. Never include credentials in logs.', format='uri'), 'expires_at': stamp, 'sha256': text(pattern='^[a-f0-9]{64}$'), 'mime_type': text()})
    schemas['LendingProductInput'] = obj({
        'external_id': text(), 'version': text(), 'name': text(), 'borrower_type': enum('business', 'person'),
        'market': enum('US', 'CA'), 'currency': text(pattern='^[A-Z]{3}$'),
        'product_type': enum('term_loan', 'line_of_credit', 'receivables_financing', 'revenue_based_financing', 'other'),
        'minimum_amount': ref('Money'), 'maximum_amount': ref('Money'),
        'minimum_term_months': {'type': 'integer', 'minimum': 1}, 'maximum_term_months': {'type': 'integer', 'minimum': 1},
        'repayment_frequency': enum('daily', 'weekly', 'biweekly', 'monthly', 'at_maturity', 'variable'),
        'pricing_schema_id': identifier,
        'pricing': {'type': 'object', 'description': 'Rate, fees, amortization and other product-specific economics, validated against the approved pricing_schema_id. All inputs needed for repayment analysis must be captured, not inferred.'},
        'terms_document_ids': ids,
    }, description='An immutable catalog version, not a merchant inventory product. Validate amount currencies, ordered bounds and approved terms before accepting. No modification or deletion of an accepted version.')
    schemas['LendingProductVersion'] = obj({'id': identifier, 'created_at': stamp, 'definition': ref('LendingProductInput'), 'sha256': text(pattern='^[a-f0-9]{64}$')})
    schemas['PolicyRule'] = obj({'id': text(), 'dimension_key': text('An approved, typed dimension from configuration.'), 'operator': enum('gt', 'gte', 'lt', 'lte', 'eq'), 'threshold': decimal, 'unit': text(), 'on_missing': {'const': 'review'}, 'on_fail': enum('review', 'outside_policy')}, description='This rule language supports scalar comparisons only. Units and types must match the approved dimension. No executable code, arbitrary expressions or inferred pass for missing data.')
    schemas['RiskPolicyInput'] = obj({'external_id': text(), 'version': text(), 'name': text(), 'borrower_type': enum('business', 'person'), 'market': enum('US', 'CA'), 'rules': array(ref('PolicyRule'), minItems=1), 'policy_document_ids': ids}, description='Validated against authorized dimensions and the institution-approved policy before use. Documents provide context; they are not automatically executable policies.')
    schemas['RiskPolicyVersion'] = obj({'id': identifier, 'created_at': stamp, 'definition': ref('RiskPolicyInput'), 'sha256': text(pattern='^[a-f0-9]{64}$')})
    schemas['ApplicationInput'] = obj({'institution_reference': text(), 'requested_amount': ref('Money'), 'requested_term_months': {'type': 'integer', 'minimum': 1}, 'purpose': text(), 'declared_data': {'type': 'object', 'description': 'Institution-defined application fields validated against application_schema_id; additionalProperties here does not bypass that schema.'}, 'application_schema_id': identifier, 'related_borrower_ids': ids}, ['institution_reference', 'requested_amount', 'requested_term_months', 'purpose', 'application_schema_id', 'declared_data'])
    schemas['CreateOrigination'] = obj({'borrower_id': identifier, 'application': ref('ApplicationInput'), 'lending_product_version_id': identifier, 'risk_policy_version_id': identifier, 'connection_ids': ids, 'document_ids': ids}, description='AMLOK resolves authorized source data, coverage, verification and calculations. Clients do not provide workflow IDs, manifests or processing_context. Validate product, policy, currency, market and borrower-type compatibility.')
    schemas['Requirement'] = obj({'id': identifier, 'code': text(), 'message': text(), 'action': enum('connect_source', 'reauthorize_source', 'upload_document', 'contact_support'), 'connection_id': nullable(identifier)})
    schemas['Origination'] = obj({'id': identifier, 'borrower_id': identifier, 'institution_reference': text(), 'status': enum('accepted', 'collecting', 'requires_action', 'processing', 'waiting_for_credits', 'completed', 'failed', 'cancelled'), 'created_at': stamp, 'updated_at': stamp, 'requirements': array(ref('Requirement')), 'risk_package_id': nullable(identifier), 'failure': nullable(ref('Error'))}, allOf=[{'if': {'properties': {'status': {'const': 'completed'}}}, 'then': {'properties': {'risk_package_id': identifier}}, 'else': {'properties': {'risk_package_id': {'type': 'null'}}}}])
    schemas['Metric'] = obj({'key': text(), 'label': text(), 'status': enum('available', 'unavailable', 'not_applicable'), 'value': nullable(decimal), 'unit': text(), 'window': ref('Window'), 'calculation_version': text(), 'missing_reason': nullable(text()), 'evidence_ids': ids}, allOf=[{'if': {'properties': {'status': {'const': 'available'}}}, 'then': {'properties': {'value': decimal, 'missing_reason': {'type': 'null'}}}, 'else': {'properties': {'value': {'type': 'null'}, 'missing_reason': text()}}}])
    schemas['Dimension'] = obj({'key': enum('identity', 'cashflow', 'liquidity', 'revenue_quality', 'profitability', 'leverage', 'repayment_capacity', 'concentration', 'collateral', 'fraud_and_consistency', 'income_and_affordability'), 'status': enum('available', 'partial', 'unavailable', 'not_applicable'), 'summary': text(), 'metrics': array(ref('Metric')), 'evidence_ids': ids})
    schemas['PolicyResult'] = obj({'rule_id': text(), 'result': enum('pass', 'fail', 'unavailable', 'not_applicable'), 'actual': nullable(decimal), 'threshold': decimal, 'unit': text(), 'explanation': text(), 'evidence_ids': ids})
    schemas['PolicyResult']['allOf']=[{'if':{'properties':{'result':{'enum':['pass','fail']}}},'then':{'properties':{'actual':decimal}},'else':{'properties':{'actual':{'type':'null'}}}}]
    schemas['SourceCoverage'] = obj({'connection_id': identifier, 'integration_id': identifier, 'source_as_of': nullable(stamp), 'retrieved_at': stamp, 'window': nullable(ref('Window')), 'status': enum('complete', 'partial', 'unavailable', 'stale'), 'limitations': array(text())})
    schemas['RiskPackage'] = obj({
        'id': identifier, 'borrower_id': identifier, 'origination_id': nullable(identifier), 'monitoring_run_id': nullable(identifier),
        'product': enum('insights', 'signal'), 'created_at': stamp, 'as_of': stamp,
        'previous_package_id': nullable(identifier), 'application': nullable(ref('ApplicationInput')),
        'lending_product': ref('LendingProductVersion'), 'risk_policy': ref('RiskPolicyVersion'),
        'assessment': obj({'recommendation': enum('within_policy', 'outside_policy', 'review_required'), 'is_institution_decision': {'const': False}, 'summary': text(), 'reasons': array(text())}),
        'dimensions': array(ref('Dimension')), 'policy_results': array(ref('PolicyResult')),
        'sources': array(ref('SourceCoverage')), 'limitations': array(text()),
        'evidence_set': obj({'id': identifier, 'sha256': text(pattern='^[a-f0-9]{64}$'), 'count': {'type': 'integer', 'minimum': 0}}),
        'versions': obj({'schema': text(), 'normalization': text(), 'calculation': text(), 'model': nullable(text())}),
        'billing_usage_id': nullable(identifier),
    }, description='Immutable completed result. Summaries, metrics and evidence must reference the exact input versions. A Signal package does not incur another Insights charge. A model version is null when no validated, entitled model was used.', oneOf=[{'properties': {'product': {'const': 'insights'}, 'origination_id': identifier, 'monitoring_run_id': {'type': 'null'}}}, {'properties': {'product': {'const': 'signal'}, 'monitoring_run_id': identifier}}])
    schemas['RiskPackage']['oneOf'][0]['properties']['application']=ref('ApplicationInput')
    schemas['RiskPackage']['allOf']=[{'if':{'properties':{'policy_results':{'contains':{'properties':{'result':{'const':'unavailable'}},'required':['result']}}}},'then':{'properties':{'assessment':{'properties':{'recommendation':{'const':'review_required'}}}}}}]
    schemas['EvidenceSummary'] = obj({'id': identifier, 'evidence_set_id': identifier, 'resource_type': text(), 'resource_id': identifier, 'record_version': {'type': 'integer', 'minimum': 1}, 'kind': enum('normalized_record', 'provider_report', 'document'), 'source_id': text(), 'observed_at': nullable(stamp), 'sha256': text(pattern='^[a-f0-9]{64}$'), 'access': enum('available', 'restricted', 'deleted'), 'access_reason': nullable(text()), 'document_id': nullable(identifier)})
    # Keep the existing typed normalized dictionary, not 63 collection APIs.
    normalized = [name for name in legacy if name.endswith('Read') and name[:-4] in legacy]
    schemas['Evidence'] = obj({'record': ref('EvidenceSummary'), 'normalized': nullable({'oneOf': [ref('Legacy'+name) for name in normalized]}), 'provider_report_document_id': nullable(identifier)}, description='Read the frozen evidence version, never the latest replacement. Licensed provider reports and original files use controlled document downloads. Restricted evidence returns metadata and an explicit reason, never secret or unlicensed content.')
    schemas['Evidence']['allOf']=[{'if':{'properties':{'record':{'properties':{'access':{'enum':['restricted','deleted']}}}}},'then':{'properties':{'normalized':{'type':'null'},'provider_report_document_id':{'type':'null'},'record':{'properties':{'access_reason':text()}}}}}]
    schemas['Deal'] = obj({'institution_reference': text(), 'funded_amount': ref('Money'), 'outstanding_amount': ref('Money'), 'funded_at': stamp, 'maturity_date': text(format='date'), 'repayment_frequency': enum('daily', 'weekly', 'biweekly', 'monthly', 'at_maturity', 'variable'), 'terms_document_ids': ids}, description='Read-only snapshot of institution-supplied exposure terms. Changes arrive through the authorized lender integration as new versions; this API does not service the loan.')
    schemas['BaselineInput'] = {'oneOf': [obj({'risk_package_id': identifier}), obj({'portfolio_onboarding_reference': text('Approved onboarding reference, resolved and validated by AMLOK. Does not imply an Insights purchase.')})]}
    schemas['CreateMonitor'] = obj({'borrower_id': identifier, 'deal': ref('Deal'), 'baseline': ref('BaselineInput'), 'risk_policy_version_id': identifier, 'cadence_id': identifier, 'connection_ids': ids})
    schemas['UpdateMonitor'] = obj({'status': enum('active', 'paused', 'stopped'), 'risk_policy_version_id': identifier, 'cadence_id': identifier}, [], minProperties=1, description='Configuration only, with If-Match. Changes apply prospectively and never rewrite packages, evidence, events or historical charges. Stopped is terminal.')
    schemas['Monitor'] = obj({'id': identifier, 'borrower_id': identifier, 'deal': ref('Deal'), 'status': enum('initializing', 'active', 'paused', 'requires_action', 'waiting_for_credits', 'stopped', 'failed'), 'baseline_package_id': nullable(identifier), 'latest_package_id': nullable(identifier), 'risk_policy_version_id': identifier, 'cadence_id': identifier, 'next_evaluation_at': nullable(stamp), 'record_version': {'type': 'integer', 'minimum': 1}})
    schemas['MonitoringRun'] = obj({'id': identifier, 'monitor_id': identifier, 'status': enum('processing', 'completed', 'partial', 'failed', 'skipped'), 'started_at': stamp, 'completed_at': nullable(stamp), 'risk_package_id': nullable(identifier), 'sources': array(ref('SourceCoverage')), 'evidence_set_id': nullable(identifier), 'limitations': array(text())}, description='One scheduled or change-driven evaluation, with per-integration coverage and frozen evidence. A skipped or stale sync is not a clean risk result.')
    schemas['Alert'] = obj({'id': identifier, 'monitor_id': identifier, 'borrower_id': identifier, 'status': enum('open', 'resolved'), 'severity': enum('info', 'warning', 'critical'), 'rule_id': text(), 'policy_version_id': identifier, 'message': text(), 'detected_at': stamp, 'resolved_at': nullable(stamp), 'previous_package_id': nullable(identifier), 'current_package_id': identifier, 'metric_key': text(), 'previous_value': nullable(decimal), 'current_value': nullable(decimal), 'threshold': nullable(decimal), 'unit': text(), 'evidence_ids': ids}, description='System-derived risk condition. Resolution needs comparable fresh evidence; no customer edit, dismissal or deletion. Institutions handle case management elsewhere.')
    event_types = ['embedding_session.completed', 'connection.action_required', 'connection.status_changed', 'origination.action_required', 'origination.status_changed', 'origination.completed', 'origination.failed', 'risk_package.created', 'monitor.status_changed', 'monitoring_run.completed', 'monitoring_run.failed', 'alert.created', 'alert.resolved', 'export.ready', 'export.failed']
    schemas['Event'] = obj({'id': identifier, 'type': enum(*event_types), 'occurred_at': stamp, 'resource_type': text(), 'resource_id': identifier, 'resource_version': {'type': 'integer', 'minimum': 1}, 'borrower_id': nullable(identifier), 'environment': enum('sandbox', 'live')}, description='Minimal at-least-once notification, without financial payloads, tokens or download URLs. Fetch authorized resource detail. Events and delivery attempts are different records.')
    schemas['EventPage'] = obj({'next_cursor':nullable(text()),'has_more':{'type':'boolean'},'resume_cursor':text('Durable continuation position, present even on an empty page. Check retention before accepting; expired cursors return 410.')})
    schemas['CreateExport'] = obj({'kind': enum('risk_package', 'evidence', 'billing'), 'risk_package_id': identifier, 'evidence_set_id': identifier, 'billing_report_type': enum('usage', 'credits', 'statements', 'funding', 'rates', 'workload'), 'window': ref('Window'), 'format': enum('json', 'csv', 'pdf')}, ['kind', 'format'], oneOf=[{'properties': {'kind': {'const': 'risk_package'}, 'format': enum('json', 'pdf')}, 'required': ['risk_package_id'], 'not': {'anyOf': [{'required': [k]} for k in ['evidence_set_id', 'billing_report_type', 'window']]}}, {'properties': {'kind': {'const': 'evidence'}, 'format': enum('json', 'csv')}, 'required': ['evidence_set_id'], 'not': {'anyOf': [{'required': [k]} for k in ['risk_package_id', 'billing_report_type', 'window']]}}, {'properties': {'kind': {'const': 'billing'}, 'format': enum('json', 'csv')}, 'required': ['billing_report_type', 'window'], 'not': {'anyOf': [{'required': [k]} for k in ['risk_package_id', 'evidence_set_id']]}}])
    schemas['Export'] = obj({'id': identifier, 'status': enum('queued', 'processing', 'completed', 'failed'), 'created_at': stamp, 'format': enum('json', 'csv', 'pdf'), 'source': ref('CreateExport'), 'failure': nullable(ref('Error'))})
    schemas['Delivery'] = obj({'id': identifier, 'event_id': identifier, 'endpoint_id': identifier, 'attempt': {'type': 'integer', 'minimum': 1}, 'status': enum('pending', 'delivered', 'failed'), 'attempted_at': nullable(stamp), 'http_status': nullable({'type': 'integer', 'minimum': 100, 'maximum': 599})})
    schemas['ReplayEvent'] = obj({'event_id': identifier, 'endpoint_id': identifier})
    schemas['ReplayReceipt'] = obj({'id': identifier, 'event_id': identifier, 'status': {'const': 'accepted'}}, description='Requeues delivery only. It never reruns analysis, modifies an alert or creates a usage charge.')
    schemas['BillingSummary'] = obj({'as_of': stamp, 'currency': {'const': 'CAD'}, 'available_credits': text(pattern=r'^(?:0|[1-9][0-9]*)\.[0-9]{2}$'), 'spent_credits': text(pattern=r'^(?:0|[1-9][0-9]*)\.[0-9]{2}$'), 'billing_account_id': identifier, 'snapshot_id': identifier}, description='Read-only workspace balance shared by Insights and Signal. Organization owns billing profile and payment methods in the console. No held or reserved credits.')
    schemas['BillingTransaction'] = obj({'id': identifier, 'snapshot_id': identifier, 'posted_at': stamp, 'amount': text(pattern=r'^-?(?:0|[1-9][0-9]*)\.[0-9]{2}$'), 'currency': {'const': 'CAD'}, 'kind': enum('funding', 'usage', 'adjustment', 'final_refund'), 'product': nullable(enum('insights', 'signal')), 'description': text(), 'usage_id': nullable(identifier)}, description='Immutable entry. A correction is a linked new accounting entry, never an API edit or deletion.')
    schemas['ConfiguredSchema'] = obj({'id': identifier, 'version': text(), 'json_schema': {'type': 'object', 'description': 'JSON Schema 2020-12, enforced server-side. Clients can validate the same definition before submitting.'}})
    schemas['Configuration'] = obj({'products': array(enum('insights', 'signal')), 'embedding_version_ids': ids, 'application_schemas': array(ref('ConfiguredSchema')), 'pricing_schemas': array(ref('ConfiguredSchema')), 'cadences': array(obj({'id': identifier, 'description': text()})), 'dimensions': array(obj({'key':text(),'description':text(),'unit':text(),'calculation_version':text(),'borrower_types':array(enum('business','person'))})), 'integration_ids': ids}, description='Discover approved configuration for this key. The console manages embedding designs, API keys, webhook destinations and signing secrets. Integration catalog coverage does not by itself grant access.')
    schemas['RequestReceipt'] = obj({'idempotency_key': text(), 'operation_id': text(), 'resource_id': identifier, 'accepted_at': stamp, 'response_replay_available': {'type': 'boolean'}}, description='Durable acceptance reference survives expiry of the 24-hour response replay. Never execute accepted work again because a cached response expired.')
    schemas['Healthcheck'] = obj({'status': enum('ok', 'degraded')})
    schemas['ServiceStatus'] = obj({'status': enum('operational', 'degraded', 'unavailable'), 'as_of': stamp})
    # Resolve and retain only normalized dictionary dependencies used by the current contract.
    def collect(value):
        if isinstance(value, dict):
            name = value.get('$ref', '').split('/')[-1]
            if name and name not in schemas:
                assert name.startswith('Legacy'), name
                schemas[name] = legacy_schema(legacy[name[len('Legacy'):]]); collect(schemas[name])
            for child in value.values(): collect(child)
        elif isinstance(value, list):
            for child in value: collect(child)
    for schema in list(schemas.values()): collect(schema)
    return schemas


def operations():
    # name, method, relative path, group, response, request, list response, scope.
    rows = []
    def add(name, method, path, group, response, request=None, many=False, scope=None):
        rows.append(dict(id=name, method=method, path='/v2/'+path, group=group, response=response, request=request, many=many, scope=scope or group.lower().replace(' ', '-')+(':write' if method in ('POST','PATCH') else ':read')))
    def collection(path, singular, group, request):
        add('create'+singular, 'POST', path, group, singular, request)
        add('list'+singular, 'GET', path, group, singular, many=True)
        add('get'+singular, 'GET', path+'/{id}', group, singular)
    collection('borrowers', 'Borrower', 'Borrowers', 'CreateBorrower')
    add('createEmbeddingSession','POST','embedding-sessions','Connections','EmbeddingSession','CreateEmbeddingSession')
    add('getEmbeddingSession','GET','embedding-sessions/{id}','Connections','EmbeddingSession')
    add('listConnections','GET','connections','Connections','Connection',many=True)
    add('getConnection','GET','connections/{id}','Connections','Connection')
    add('getConsent','GET','consents/{id}','Connections','Consent')
    add('revokeConsent','POST','consents/{id}/revoke','Connections','Consent','RevokeConsent')
    add('uploadDocument','POST','documents','Evidence','Document','UploadDocument')
    add('getDocument','GET','documents/{id}','Evidence','Document')
    add('downloadDocument','POST','documents/{id}/download-links','Evidence','DownloadLink','DownloadPurpose',scope='evidence:read')
    collection('lending-product-versions','LendingProductVersion','Configuration','LendingProductInput')
    collection('risk-policy-versions','RiskPolicyVersion','Configuration','RiskPolicyInput')
    collection('originations','Origination','Insights','CreateOrigination')
    add('getRiskPackage','GET','risk-packages/{id}','Results','RiskPackage')
    add('listEvidence','GET','evidence','Evidence','EvidenceSummary',many=True)
    add('getEvidence','GET','evidence/{id}','Evidence','Evidence')
    collection('monitors','Monitor','Signal','CreateMonitor')
    add('updateMonitor','PATCH','monitors/{id}','Signal','Monitor','UpdateMonitor')
    add('listMonitoringRuns','GET','monitoring-runs','Signal','MonitoringRun',many=True)
    add('getMonitoringRun','GET','monitoring-runs/{id}','Signal','MonitoringRun')
    add('listAlerts','GET','alerts','Signal','Alert',many=True)
    add('getAlert','GET','alerts/{id}','Signal','Alert')
    add('listEvents','GET','events','Events','Event',many=True)
    add('getEvent','GET','events/{id}','Events','Event')
    add('createExport','POST','exports','Exports','Export','CreateExport')
    add('getExport','GET','exports/{id}','Exports','Export')
    add('downloadExport','POST','exports/{id}/download-links','Exports','DownloadLink','DownloadPurpose',scope='exports:read')
    add('listDeliveries','GET','webhook-deliveries','Events','Delivery',many=True)
    add('replayEvent','POST','webhook-replays','Events','ReplayReceipt','ReplayEvent')
    add('getBillingSummary','GET','billing/summary','Billing','BillingSummary')
    add('listBillingTransactions','GET','billing/transactions','Billing','BillingTransaction',many=True)
    add('getConfiguration','GET','configuration','Configuration','Configuration')
    add('lookupRequestReceipt','GET','request-receipts/lookup','Reliability','RequestReceipt')
    add('healthcheck','GET','healthcheck','Reliability','Healthcheck',scope='public')
    add('serviceStatus','GET','service-status','Reliability','ServiceStatus',scope='public')
    return rows


def build_spec(legacy):
    schemas = build_schemas(legacy['components']['schemas'])
    spec = {'openapi':'3.1.0', 'info': {'title': 'AMLOK API', 'version': VERSION, 'description': 'AMLOK API 2.0.0: borrower connections, Insights origination, immutable risk packages and Signal monitoring. Use your institution-issued API origin. Environment enablement is separate from publication of this contract; see the versioning guide.'}, 'x-availability': STATUS, 'security':[{'BearerAuth':[]}], 'paths':{}, 'components': {'schemas':schemas, 'securitySchemes':{'BearerAuth':deepcopy(legacy['components']['securitySchemes']['BearerAuth'])}}}
    def param(name, where='query', required=False, schema=None, description=''):
        return {'name':name,'in':where,'required':required,'schema':schema or text(), 'description':description or name.replace('_',' ')}
    for op in operations():
        result = obj({'data':array(ref(op['response'])) if op['many'] else ref(op['response']), 'meta':ref('Meta'), **({'page':ref('EventPage' if op['id']=='listEvents' else 'Page')} if op['many'] else {})})
        params = []
        if '{id}' in op['path']: params.append(param('id','path',True))
        if op['many']:
            params += [param('cursor'), param('limit',schema={'type':'integer','minimum':1,'maximum':100,'default':25})]
            if op['id'] not in ['listBorrower','listLendingProductVersion','listRiskPolicyVersion','listBillingTransactions','listDeliveries']: params.append(param('borrower_id'))
        filters = {'listBorrower':['client_reference'], 'listOrigination':['institution_reference','status'], 'listLendingProductVersion':['external_id','version'], 'listRiskPolicyVersion':['external_id','version'], 'listMonitor':['institution_reference','status'], 'listEvidence':['evidence_set_id','resource_type'], 'listMonitoringRuns':['monitor_id'], 'listAlerts':['monitor_id','status'], 'listEvents':['type'], 'listDeliveries':['event_id','endpoint_id'], 'listBillingTransactions':['snapshot_id'], 'lookupRequestReceipt':['operation_id','idempotency_key']}
        for name in filters.get(op['id'],[]): params.append(param(name,required=op['id'] in ['listEvidence','lookupRequestReceipt'] and name not in ['resource_type']))
        if op['id']=='listEvents': params.append(param('start',schema=enum('now'),description='Capture the current durable feed position with an empty page before initial collection bootstrap. Cannot be combined with cursor. Resume with the returned resume_cursor.'))
        if op['method']=='POST': params.append(param('Idempotency-Key','header',True,description='Stable for one intended command and its retries, scoped to key workspace/environment and operation. Mismatched body returns 409. Full response replay 24 hours; durable receipt remains.'))
        if op['method']=='PATCH': params.append(param('If-Match','header',True,description='Required ETag from the monitor. Reject stale values with 412.'))
        code = '202' if op['id'] in ['createOrigination','createMonitor','createExport','replayEvent','uploadDocument'] else ('201' if op['method']=='POST' and op['id'] not in ['revokeConsent','downloadDocument','downloadExport'] else '200')
        summary=re.sub(r'(?<!^)([A-Z])',r' \1',op['id']).capitalize()
        entry = {'operationId':op['id'], 'summary':summary, 'tags':[op['group']], 'x-availability':STATUS, 'x-required-scopes':[] if op['scope']=='public' else [op['scope']], 'parameters':params, 'responses':{code:{'description':('Accepted asynchronously; inspect status, not just HTTP success.' if code=='202' else 'Successful response.'),'content':{'application/json':{'schema':result}}}}, 'description':'All referenced IDs, cursor state and downloads require the same authorized workspace/environment. No caller-controlled workspace override.'}
        if op['scope']=='public': entry['security']=[]
        else: entry['security']=[{'BearerAuth':[]}]
        if op['id'] in ['createExport','getExport','downloadExport']:
            entry['description'] += ' Billing exports additionally require billing:read and Owner authority. Evidence exports require evidence:read and source entitlements. Recheck authorization on creation, retrieval and download; exports:read alone grants neither.'
        if op['id'] in ['getMonitor','createMonitor','updateMonitor']: entry['responses'][code]['headers']={'ETag':{'schema':text(),'description':'Quoted monitor record version for conditional configuration changes.'}}
        for status in ['400','401','403','404','409','410','429','503'] + (['402','422'] if op['method']=='POST' else []) + (['412','422'] if op['method']=='PATCH' else []):
            entry['responses'][status]={'description':'Inspect structured error; retry only when retryable. 429 and 503 can include Retry-After.', 'content':{'application/json':{'schema':obj({'error':ref('Error')})}}}
        if op['request']:
            media = 'multipart/form-data' if op['request']=='UploadDocument' else 'application/json'
            entry['requestBody']={'required':True,'content':{media:{'schema':ref(op['request'])}}}
        spec['paths'].setdefault(op['path'],{})[op['method'].lower()] = entry
    spec['webhooks']={'resourceEvent':{'post':{'description':'Resource event envelope. Apply the existing raw-body HMAC verifier; persist then acknowledge. Delivery may be duplicated or out of order.', 'security':[], 'requestBody':{'required':True,'content':{'application/json':{'schema':ref('Event')}}},'responses':{'200':{'description':'Durably accepted.'}}}}}
    return spec


def disposition(op):
    """Every existing operation gets exactly one explicit target disposition."""
    p, oid = op['path'], op['id']
    if p in ['/v1/healthcheck','/v1/service-status']: return 'retain', p.replace('/v1/','/v2/'), 'Operational availability stays separate from borrower outcomes.'
    if p.startswith('/v1/billing') or p.startswith('/v1/workloads'):
        return 'consolidate', '/v2/billing/summary; /v2/billing/transactions; /v2/exports', 'Read-only financial summary, immutable transactions and typed billing exports; preserve historical rates, funding, statements and workload reconciliation.'
    if oid in ['EP135','EP136','EP007','EP008','EP009','EP010']:
        return 'consolidate','/v2/borrowers','One discriminated business/person borrower boundary; preserve existing subject identifiers and associations.'
    if p.startswith('/v1/applications'):
        return 'consolidate','/v2/originations','Submit the application together with exact lending-product and risk-policy versions; distinguish institution reference from AMLOK origination ID.'
    if p.startswith('/v1/risk-snapshots') or p.startswith('/v1/decisions') or p.startswith('/v1/attributes'):
        return 'consolidate','/v2/risk-packages/{id}; /v2/evidence','One immutable result with dimensions, policy evaluations, reasons and evidence links. The institution makes the final decision.'
    if p.startswith('/v1/monitors'):
        return 'retain','/v2/monitors','Keep monitoring configuration; accept a deal and resolve its baseline internally. PATCH changes future configuration only.'
    if p.startswith('/v1/alerts'): return 'retain','/v2/alerts','Keep read-only risk conditions and their baseline/current evidence; separate from delivery attempts.'
    if p.startswith('/v1/documents'): return 'consolidate','/v2/documents; /v2/evidence','Keep uploads and controlled exact-version downloads. Discover files through evidence rather than another independent collection.'
    if oid in ['EP137','EP139','IR001']:
        return 'internalize','/v2/embedding-sessions','The borrower session handles authorization and provider connection creation. Institutions never manufacture consent or handle provider credentials.'
    if p.startswith('/v1/consents'): return 'consolidate','/v2/consents/{id}; /v2/consents/{id}/revoke','Keep authorization visibility and revocation. Discover consent IDs through sessions and connections.'
    if oid in ['EP001','EP002']: return 'retain','/v2/connections','Keep connection health, coverage and reauthorization visibility.'
    if oid in ['EP140','EP141'] or p.startswith('/v1/sync-jobs'):
        return 'internalize','/v2/embedding-sessions; /v2/consents/{id}/revoke; /v2/monitoring-runs','AMLOK schedules collection; expose customer action requirements and per-integration run results, not jobs that clients must orchestrate.'
    if p.startswith('/v1/subject-associations'):
        return 'consolidate','/v2/originations','Related borrowers are application inputs; AMLOK validates identity relationships and included KYB/KYC context.'
    if p.startswith('/v1/webhook-endpoints') and oid in ['EP158','EP159']:
        return 'console','/v2/configuration','Manage destinations and signing-secret rotation in Dev Tools. Preserve existing clients until replacement and deprecation are agreed.'
    if oid=='EP160': return 'retain','/v2/webhook-replays','Replay delivery without rerunning underwriting, monitoring or billing.'
    if p.startswith('/v1/webhook-deliveries'): return 'retain','/v2/webhook-deliveries','Retain delivery troubleshooting as read-only attempts.'
    if p.startswith('/v1/webhook-events') or p.startswith('/v1/changes'):
        return 'consolidate','/v2/events','One durable cursor-based event feed plus signed notifications; bootstrap through snapshot-bound collection reads.'
    if p.startswith('/v1/request-receipts'): return 'retain','/v2/request-receipts/lookup','Keep durable recovery for accepted commands independently from cached response expiry.'
    if p.startswith('/v1/configuration') or p.startswith('/v1/providers'):
        return 'consolidate','/v2/configuration','Discover approved products, schemas, integration coverage and configuration IDs in one place.'
    if p.startswith('/v1/sandbox/scenarios'):
        return 'console','Sandbox tooling','Keep test controls outside the production product API. Preserve runnable v1 test journeys during migration.'
    if p.startswith('/v1/audit-events'):
        return 'console','Console audit log','Keep organization and configuration audit history available to authorized owners in the console. Product evidence retains assessment lineage; do not misclassify administrative audit events as borrower evidence.'
    internal = ['/v1/workflow-runs','/v1/attribute-calculations','/v1/input-manifests','/v1/monitoring-baselines','/v1/monitoring-periods','/v1/sync-checkpoints','/v1/subjects/','/v1/requirements']
    if any(p.startswith(prefix) for prefix in internal) or (op['method']=='POST' and p in ['/v1/verifications','/v1/lien-searches']):
        return 'internalize','/v2/originations; /v2/risk-packages/{id}; /v2/monitoring-runs','AMLOK owns execution, evidence freezing, included checks and baseline preparation. Preserve useful results, requirements and traceability in product outputs.'
    return 'evidence','/v2/evidence; /v2/exports','Preserve this typed normalized resource, its exact version and authorized original files through a unified evidence surface; remove collection-per-table navigation from the replacement API.'


def generate():
    legacy=json.loads((ROOT/'openapi/amlok-v1.json').read_text())
    index=json.loads((ROOT/'legacy/v1/data/api-reference-index.json').read_text())
    spec=build_spec(legacy)
    def save(path,value):
        (ROOT/path).parent.mkdir(parents=True,exist_ok=True)
        (ROOT/path).write_text(json.dumps(value,indent=2)+'\n')
    save('openapi/amlok-v2.json',spec)
    from product_api_examples import examples
    fixtures=examples()
    save('downloads/risk-package-example.json',fixtures['RiskPackage'])
    save('data/product-api-examples.json',fixtures)
    rows=[]
    for op in index:
        action,target,reason=disposition(op)
        rows.append({'operation_id':op['id'],'method':op['method'],'path':op['path'],'group':op['group'],'disposition':action,'target':target,'reason':reason})
    counts=dict(Counter(r['disposition'] for r in rows))
    audit={'reviewed_at':'2026-11-06','availability':STATUS,'legacy_version':legacy['info']['version'],'published_version':VERSION,'legacy_operation_count':len(rows),'current_operation_count':len(operations()),'target_operation_count':len(operations()),'dispositions':counts,'operations':rows}
    save('data/api-surface-review.json',audit)
    out=io.StringIO(); writer=csv.DictWriter(out,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    (ROOT/'downloads/api-endpoint-migration.csv').write_text(out.getvalue())
    save('downloads/api-product-index.json',{'version':VERSION,'operations':operations()})
    return audit


if __name__=='__main__':
    from current_api import build
    build()

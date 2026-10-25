"""Validate reporting-only customer credit access without executing payments."""
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
import json
from jsonschema import Draft202012Validator, FormatChecker
from wallet_contract import OPERATION_IDS

ROOT=Path(__file__).resolve().parent.parent
spec=json.loads((ROOT/'openapi/amlok-v1.json').read_text())
index=json.loads((ROOT/'data/reporting-api-index.json').read_text())
ops={(op['path'],op['method']):op for op in index}
checks=0
def check(condition,message):
    global checks
    assert condition,message
    checks+=1
def valid(name,value):
    schema={'$ref':'#/components/schemas/'+name,'components':spec['components']}
    return Draft202012Validator(schema,format_checker=FormatChecker()).is_valid(value)
def response(path,method='GET'):
    return ops[(path,method)]['response']['data']

check(len(index)==21,'Expected 21 read-only reporting operations')
for path in spec['paths']:
    check(not path.startswith(('/v1/wallet','/v1/agreement-','/v1/deletion-requests')),'Unsupported customer endpoint remains: '+path)
for name in spec['components']['schemas']:
    check('wallet' not in name.lower(),'Obsolete wallet schema remains: '+name)
for event in spec['components']['schemas']['WebhookEvent']['properties']['type']['enum']:
    check(not event.startswith('wallet.'),'Obsolete wallet event remains')
for methods in spec['paths'].values():
    for op in methods.values():
        check(not any(scope.startswith('wallets:') for scope in op['x-required-scopes']),'Wallet scope remains')
postman=json.loads((ROOT/'downloads/amlok-api.postman_collection.json').read_text())
check('Wallets' not in [g['name'] for g in postman['item']],'Postman wallet folder remains')
check('/v1/wallet' not in json.dumps(postman),'Postman wallet route remains')
check(not list((ROOT/'api-reference/endpoints/wallets').glob('*.mdx')),'Wallet endpoint page remains')
check(not (ROOT/'api-reference/wallets.mdx').exists(),'Interactive wallet guide remains')
check(not (ROOT/'data/wallet-api-index.json').exists(),'Old wallet index remains')
account=response('/v1/billing/account')
check(account['outflow_policy']=='product_usage_or_final_cancellation_refund','Wrong wallet policy')
check(account['refund_policy']=='full_unused_balance_on_final_cancellation','Wrong refund policy')
check(account['access']=='reporting_only' and 'enabled_capabilities' not in account,'Interactive account capability remains')
check(set(account['portal_controls'])=={'payment_methods','automatic_top_ups','account_cancellation'},'Portal controls missing')
check(set(account['funding_methods'])=={'card','bank_account'},'Incorrect funding methods')
check(account['refund_destination']=='saved_portal_bank_account','Refund must use saved bank account')
check(account['default_auto_top_up_threshold']==account['minimum_top_up_threshold']=='200.00','Wrong automatic trigger')
check('processing_balance_floor' not in account,'Processing floor still exposed')
check(account['payment_frequency']=='every_12_months','Monthly funding payments implied')
check(account['closure_timing']=='end_of_request_month' and account['cancellation_notice_days']==0,'Cancellation timing mismatch')
check(account['minimum_top_up_amount']=='500.00','Wrong top-up minimum')
for policy in ['active_agreement_refunds','withdraw_anytime']:
    check(not valid('BillingAccount',{**account,'refund_policy':policy}),'Wrong policy accepted')
balance=response('/v1/billing/credits')
for obsolete in ['committed_credits','additional_funds','promotional_credits','remaining_paid_credits']:
    check(obsolete not in balance,'Obsolete credit bucket remains')
    check(not valid('BillingCreditBalance',{**balance,obsolete:{}}),'Schema accepts obsolete bucket')
check('withdrawable' not in balance,'Balance advertises immediate cash-out')
check(Decimal(balance['available_for_usage'])==Decimal(balance['total_posted'])-Decimal(balance['total_held']),'Pending funding counted as available')
check(not valid('BillingCreditBalance',{**balance,'processing_floor':'200.00'}),'Removed floor accepted')
check('spendable_for_processing' not in balance,'Duplicate spendable balance remains')
below={**balance,'total_posted':'180.00','total_held':'0.00','available_for_usage':'180.00'}
check(valid('BillingCreditBalance',below),'Credits below CAD 200 cannot be represented')
check(balance['workspace_id']==account['workspace_id']=='wsp_example','Workspace context missing')
entry=response('/v1/billing/credit-ledger')[0]
check(not set(entry)&{'bucket','credit_lot_id'},'Ledger still allocates consumption by source bucket')
check(not valid('BillingCreditEntry',{**entry,'bucket':'promotional_credits'}),'Ledger accepts source-priority allocation')
rate_card=response('/v1/billing/rate-card')
for rate in rate_card['rates']:
    check(rate['workload_limits']['minimum_banking_history_months']==(12 if rate['product']=='insights' else None),'Wrong history basis')
    check(rate['workload_limits']['record_counting_basis']==('per_underwriting' if rate['product']=='insights' else 'new_records_per_month'),'Wrong record-counting basis')
    check(rate['workload_limits']['record_limit']=={'standard':75000,'advanced':250000,'complex':1000000}[rate['tier']],'Published per-analysis limit wrong')
negotiated=deepcopy(rate_card['rates'][0]);negotiated.update(pricing_basis='negotiated',effective_rate='4.50',discount_percent='10')
check(valid('BillingRate',negotiated),'Negotiated rate must retain existing tier')
check(not valid('BillingRate',{**negotiated,'tier':'custom'}),'Fourth reporting tier accepted')
custom=deepcopy(rate_card['rates'][2]);custom.update(pricing_basis='negotiated');custom['workload_limits']['record_limit']=2000000
check(valid('BillingRate',custom),'Explicit custom allowance cannot be represented')
check(not valid('BillingWorkloadLimits',{**custom['workload_limits'],'minimum_banking_history_months':11}),'History shorter than twelve months accepted')
for bad in ['100.01','100.99','101','-1']:
    check(not valid('BillingRate',{**negotiated,'discount_percent':bad}),'Discount over 100 or below 0 accepted')
check(not valid('BillingRate',{**negotiated,'effective_rate':'4.555'}),'Fractional billing cent accepted')
bad=deepcopy(rate_card['rates'][3]);bad['workload_limits']['record_counting_basis']='per_underwriting'
check(not valid('BillingRate',bad),'Signal allowed historical counting basis')
check(valid('BillingCreditEntry',{**entry,'amount':'-5.00'}),'Signed ledger amount invalid')
statement=response('/v1/billing/statements/{id}')
closing=sum(Decimal(statement[k]) for k in ['opening_balance','funding','adjustments'])-sum(Decimal(statement[k]) for k in ['usage','refunds'])
check(closing==Decimal(statement['closing_balance'])==Decimal(balance['total_posted']),'Statement not reconciled')
check(not set(statement) & {'withdrawals','transfers_in','transfers_out','fees'},'Unsupported outflow columns remain')
consumption=response('/v1/billing/consumption')
check(sum(Decimal(r['net_amount']) for r in consumption['rows'])==Decimal(consumption['total_net_amount'])==Decimal(statement['usage']),'Consumption not reconciled')
usage=response('/v1/billing/usage/{id}')
check(Decimal(usage['quantity'])*Decimal(usage['unit_rate'])==Decimal(usage['amount']),'Usage math')
check(usage['quantity']=='1','Underwriting example must be one billable unit')

for path in ['/v1/healthcheck','/v1/service-status']:
    op=spec['paths'][path]['get']
    check(op['security']==[] and op['x-required-scopes']==[],'Availability check requires customer credentials')
    for sample in op['x-codeSamples']:
        check('AMLOK_API_KEY' not in sample['source'] and 'Authorization' not in sample['source'],'Public sample sends credentials')
check('503' in spec['paths']['/v1/healthcheck']['get']['responses'],'Healthcheck cannot report unavailability')
check(valid('Healthcheck',{'status':'unavailable','timestamp':'2026-10-25T12:00:00Z'}),'Unhealthy response rejected')
check(not valid('Healthcheck',{'status':'ok','timestamp':'2026-10-25T12:00:00Z','database_password':'secret'}),'Healthcheck exposes private infrastructure data')
status=spec['paths']['/v1/service-status']['get']['responses']['200']['content']['application/json']['examples']['synthetic']['value']
unknown=deepcopy(status);unknown['status']='unknown';unknown['services'][0]['status']='unknown'
check(valid('ServiceStatus',unknown),'Unknown service state cannot be represented')
config=json.loads((ROOT/'docs.json').read_text())
api=next(t for t in config['navigation']['tabs'] if t['tab']=='API Reference')
groups=next(g for g in api['groups'] if g['group']=='Endpoints')['pages']
check(all(g.get('icon') for g in groups),'Endpoint category missing icon')
reporting=next(g for g in groups if g['group']=='Reporting')
check(all(isinstance(p,str) for p in reporting['pages']),'Reporting contains redundant nested groups')
check(not any(g['group'] in ['Billing','Privacy','Wallets'] for g in groups),'Retired endpoint group remains')
for op in index:
    operation=spec['paths'][op['path']][op['method'].lower()]
    records=op['response']['data'] if isinstance(op['response']['data'],list) else [op['response']['data']]
    check(all(record['workspace_id']==account['workspace_id'] for record in records),'Report crosses workspace context')
    check(operation['operationId']==OPERATION_IDS[op['method']+' '+op['path']],'Existing operation identity changed')
    check(set(operation['x-required-scopes']) <= {'billing:read','billing:export'},'Unsupported reporting scopes remain')
    check(op['method']=='GET' or (op['method']=='POST' and op['path'] in ['/v1/billing/reports','/v1/billing/reports/{id}/download-link']),'Customer can mutate credits or payment settings')
    if op['method'] in ['POST','PATCH']:
        check(any(p['name']=='Idempotency-Key' and p['required'] for p in operation['parameters']),'Missing idempotency')
        for sample in operation['x-codeSamples']:check('Idempotency-Key' in sample['source'],'Sample omits idempotency')
    if op['method']=='PATCH' or op['path'].endswith(('/cancel','/decision','/disable','/retry')):
        check(any(p['name']=='If-Match' and p['required'] for p in operation['parameters']),'Missing concurrency check')
        for sample in operation['x-codeSamples']:check('If-Match' in sample['source'],'Sample omits ETag')
    for parameter in operation['parameters']:
        if parameter['in']=='query' and parameter.get('required'):
            for sample in operation['x-codeSamples']:check(parameter['name']+'=' in sample['source'],'Required query absent')
    request=operation.get('requestBody',{}).get('content',{}).get('application/json')
    if request:check(not valid(request['schema']['$ref'].split('/')[-1],{**request['example'],'balance':'999999.00'}),'Request accepts arbitrary balance')
check('/v1/billing/usage' in spec['paths'] and 'post' not in spec['paths']['/v1/billing/usage'],'Client can create a charge')
report=deepcopy(ops[('/v1/billing/reports','POST')]['request']);report.update(report_type='ledger',time_basis='occurred_at')
check(not valid('CreateBillingReport',report),'Ledger export permits event time')
check(not valid('CreateBillingReport',{**ops[('/v1/billing/reports','POST')]['request'],'billing_account_id':'another_institution'}),'Report permits client-selected billing account')
check(response('/v1/billing/credits')['billing_account_id']==account['id'],'Credit report account mismatch')
check(response('/v1/billing/credit-ledger')[0]['billing_account_id']==account['id'],'Credit ledger account mismatch')
out={'checks':checks,'reportingOperations':len(index),'scope':'Documentation contract only; no backend or payment rail executed.'}
(ROOT/'artifacts/wallet-contract-validation.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))

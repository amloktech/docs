"""Validate customer funding/reporting boundaries without executing payments."""
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
import json
from jsonschema import Draft202012Validator, FormatChecker
from wallet_contract import OPERATION_IDS

ROOT=Path(__file__).resolve().parent.parent
spec=json.loads((ROOT/'openapi/amlok-v1.json').read_text())
index=json.loads((ROOT/'data/wallet-api-index.json').read_text())
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

check(len(index)==26,'Expected 26 reporting and funding operations')
removed_prefixes=('/v1/wallet-withdrawals','/v1/wallet-transfers','/v1/wallet-refunds','/v1/wallet-payouts','/v1/wallet-approvals','/v1/wallet-quotes','/v1/wallet-closures','/v1/agreement-','/v1/deletion-requests')
for path in spec['paths']:
    check(not path.startswith(removed_prefixes),'Unsupported customer endpoint remains: '+path)
check('post' not in spec['paths']['/v1/wallets'],'Customer wallet creation remains')
for removed in ['WalletTransfer','WalletWithdrawal','WalletRefund','WalletPayout','WalletApproval','WalletQuote','WalletClosure','AgreementCancellation','AgreementCancellationQuote','DeletionJob','CreateWallet']:
    check(removed not in spec['components']['schemas'],'Obsolete schema remains: '+removed)
for event in ['wallet.refund.updated','wallet.payout.updated','wallet.approval.updated','wallet.closure.updated','billing.cancellation.updated','deletion.completed']:
    check(event not in spec['components']['schemas']['WebhookEvent']['properties']['type']['enum'],'Obsolete event remains')
session={'purpose':'funding_method','return_url':'https://client.example.com/wallet/return'}
check(valid('CreateWalletSession',session),'Funding setup rejected')
check(not valid('CreateWalletSession',{**session,'purpose':'payout_destination'}),'Session enables payout destination')
method=response('/v1/wallet-payment-methods/{id}')
check(not valid('WalletPaymentMethod',{**method,'capabilities':['payout']}),'Payout capability remains')
top_up=ops[('/v1/wallet-top-ups','POST')]['request']
for value in ['0.00','-1.00','1.001','1e3','NaN',500,0.5,'']:
    check(not valid('CreateWalletTopUp',{**top_up,'amount':value}),'Invalid top-up amount accepted')
for value in ['0.01','500.00','1000000.00']:
    check(valid('CreateWalletTopUp',{**top_up,'amount':value}),'Valid positive top-up rejected')
account=response('/v1/billing/account')
check(account['outflow_policy']=='product_usage_or_final_cancellation_refund','Wrong wallet policy')
check(account['refund_policy']=='full_remaining_paid_balance_on_final_cancellation','Wrong refund policy')
check(not set(account['enabled_capabilities']) & {'withdrawals','transfers','cancellation_refunds'},'Cash-out capability remains')
for policy in ['active_agreement_refunds','withdraw_anytime']:
    check(not valid('BillingAccount',{**account,'refund_policy':policy}),'Wrong policy accepted')
balance=response('/v1/wallets/{id}/balance')
for name in ['committed_credits','additional_funds','promotional_credits']:
    bucket=balance[name]
    check(Decimal(bucket['available'])==Decimal(bucket['posted'])-Decimal(bucket['held']),name+' does not reconcile')
check(Decimal(balance['total_posted'])==sum(Decimal(balance[b]['posted']) for b in ['committed_credits','additional_funds','promotional_credits']),'Posted sum')
check(Decimal(balance['remaining_paid_credits'])==sum(Decimal(balance[b]['posted']) for b in ['committed_credits','additional_funds']),'Paid principal includes promotional or excludes held paid credits')
check('withdrawable' not in balance,'Balance advertises immediate cash-out')
check(Decimal(balance['available_for_usage'])==Decimal(balance['total_posted'])-Decimal(balance['total_held']),'Pending funding counted as available')
statement=response('/v1/billing/statements/{id}')
closing=sum(Decimal(statement[k]) for k in ['opening_balance','funding','adjustments'])-sum(Decimal(statement[k]) for k in ['usage','refunds'])
check(closing==Decimal(statement['closing_balance'])==Decimal(balance['total_posted']),'Statement not reconciled')
check(not set(statement) & {'withdrawals','transfers_in','transfers_out','fees'},'Unsupported outflow columns remain')
consumption=response('/v1/billing/consumption')
check(sum(Decimal(r['net_amount']) for r in consumption['rows'])==Decimal(consumption['total_net_amount'])==Decimal(statement['usage']),'Consumption not reconciled')
usage=response('/v1/billing/usage/{id}')
check(Decimal(usage['quantity'])*Decimal(usage['unit_rate'])==Decimal(usage['amount']),'Usage math')
check(usage['quantity']=='1','Underwriting example must be one billable unit')

topup_op=ops[('/v1/wallet-top-ups','POST')]
check(topup_op['success']=='202','Funding must be asynchronous')
check(topup_op['response']['data']['status']=='pending','Creation fabricates settlement')
check(topup_op['request'].get('client_reference'),'Missing durable business reference')
check(any(p['name']=='client_reference' for p in spec['paths']['/v1/wallet-top-ups']['get']['parameters']),'Missing funding recovery lookup')
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
check(not any(g['group'] in ['Billing','Privacy'] for g in groups),'Retired endpoint group remains')
for op in index:
    operation=spec['paths'][op['path']][op['method'].lower()]
    check(operation['operationId']==OPERATION_IDS[op['method']+' '+op['path']],'Existing operation identity changed')
    check(not set(operation['x-required-scopes']) & {'wallets:withdraw','wallets:transfer','wallets:refund','wallets:approve','wallets:write','billing:manage','privacy:delete'},'Unsupported scopes remain')
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
out={'checks':checks,'walletOperations':len(index),'scope':'Documentation contract only; no backend or payment rail executed.'}
(ROOT/'artifacts/wallet-contract-validation.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))

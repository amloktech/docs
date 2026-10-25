"""Validate the cancellation-only wallet API contract, without executing payments."""
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

check(len(index)==49,'Expected 49 billing and wallet operations')
for path in spec['paths']:
    check(not path.startswith(('/v1/wallet-withdrawals','/v1/wallet-transfers')),'Cash-out endpoint remains')
for removed in ['WalletTransfer','WalletWithdrawal']:
    check(removed not in spec['components']['schemas'],'Obsolete movement schema remains')
for event in ['wallet.withdrawal.updated','wallet.transfer.updated']:
    check(event not in spec['components']['schemas']['WebhookEvent']['properties']['type']['enum'],'Obsolete wallet event remains')

quote={'kind':'refund','source_wallet_id':'wal_example','cancellation_id':'cancellation_final_example','currency':'CAD'}
check(valid('CreateWalletQuote',quote),'Cancellation quote rejected')
for missing in ['kind','source_wallet_id','cancellation_id','currency']:
    bad=deepcopy(quote);bad.pop(missing)
    check(not valid('CreateWalletQuote',bad),'Quote accepts missing '+missing)
for field,value in [('amount','1.00'),('currency','USD'),('kind','withdrawal'),('kind','transfer'),('destination_wallet_id','other'),('origin_top_up_id','arbitrary'),('status','refund_pending'),('tenant_id','other')]:
    check(not valid('CreateWalletQuote',{**quote,field:value}),'Quote permits arbitrary '+field)
check(valid('CreateWalletQuote',{**quote,'refund_id':'refund_example'}),'Retry quote rejected')
top_up=ops[('/v1/wallet-top-ups','POST')]['request']
for value in ['0.00','-1.00','1.001','1e3','NaN',500,0.5,'']:
    check(not valid('CreateWalletTopUp',{**top_up,'amount':value}),'Invalid top-up amount accepted')
for value in ['0.01','500.00','1000000.00']:
    check(valid('CreateWalletTopUp',{**top_up,'amount':value}),'Valid positive top-up rejected')
for field in ['balance','legal_owner_id','tenant_id','agreement_id']:
    check(not valid('CreateWallet',{'name':'Example','currency':'CAD','usage_enabled':True,field:'injected'}),'Client can supply '+field)

account=response('/v1/billing/account')
check(account['outflow_policy']=='product_usage_or_final_cancellation_refund','Wrong wallet policy')
check(account['refund_policy']=='full_remaining_paid_balance_on_final_cancellation','Wrong refund policy')
check(not set(account['enabled_capabilities']) & {'withdrawals','transfers'},'Cash-out capability remains')
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

q=response('/v1/wallet-quotes','POST');refund=response('/v1/wallet-refunds','POST')
for name,value in [('WalletQuote',q),('WalletRefund',refund)]:
    check(Decimal(value['fee_amount'])==0,'Refund fee reduces paid balance')
    check(value['amount']==value['recipient_amount']==value['total_debit'],'Full principal not returned')
    check(sum(Decimal(x['amount']) for x in value['allocations'])==Decimal(value['amount']),'Funding allocations do not sum')
    check(not valid(name,{**value,'fee_amount':'1.00'}),'Nonzero wallet refund fee accepted')
    check(value['cancellation_id'] and value['final_statement_id'],'Refund lacks final cancellation evidence')
check(q['holds_funds'] is False,'Quote reserves funds')
check(Decimal(refund['amount'])==Decimal(refund['paid_amount'])+Decimal(refund['remaining_amount']),'Refund obligation not reconciled')
quote_op=spec['paths']['/v1/wallet-quotes']['post']
create_refund=spec['paths']['/v1/wallet-refunds']['post']
check('cancellation_not_final' in quote_op['responses']['409']['content']['application/json']['examples'],'Missing cancellation gate error')
check('recheck' in create_refund['description'].lower() and 'atomically' in create_refund['description'],'Refund submission must recheck and reserve')
retry=spec['paths']['/v1/wallet-refunds/{id}/retry']['post']
check('refund_not_retryable' in retry['responses']['409']['content']['application/json']['examples'],'Missing unknown-outcome retry protection')
closure=ops[('/v1/wallet-closures','POST')]['request'];bad=deepcopy(closure);bad.pop('cancellation_id')
check(not valid('CreateWalletClosure',bad),'Closure bypasses cancellation linkage')
prepared=response('/v1/wallet-refunds','POST')
check(prepared['issued_at'] is None and prepared['account_closed_at'] is None,'Preparation fabricates account closure or refund issuance')
issued={**prepared,'status':'submitted','account_closed_at':'2026-10-23T14:00:00Z','issued_at':'2026-10-23T14:00:00Z','cancellable':False,'approval_id':None}
check(valid('WalletRefund',issued),'Issued refund awaiting bank receipt rejected')
check(issued['paid_amount']=='0.00' and issued['remaining_amount']==issued['amount'],'Issuance falsely implies bank receipt')
for field in ['account_closed_at','issued_at']:
    check(not valid('WalletRefund',{**issued,field:None}),'Submitted refund omits '+field)
check(not valid('WalletRefund',{**prepared,'issued_at':'2026-10-23T14:00:00Z'}),'Refund issued before account closure')
closed={**response('/v1/wallet-closures','POST'),'status':'completed','blocking_reasons':[],
    'final_statement_id':issued['final_statement_id'],'closed_at':issued['account_closed_at'],'refund_ids':[issued['id']]}
check(valid('WalletClosure',closed),'Closure wrongly requires bank settlement')
for field,value in [('closed_at',None),('final_statement_id',None),('blocking_reasons',['pending_reconciliation'])]:
    check(not valid('WalletClosure',{**closed,field:value}),'Completed closure accepts unresolved '+field)
check('immediately after account closure' in create_refund['description'],'Missing immediate refund issuance policy')
check('7-10 business days' in create_refund['description'],'Missing bank delivery expectation')
cancellation=response('/v1/agreement-cancellations','POST')
check(cancellation['final_refund_amount'] is None and cancellation['reconciled_at'] is None and cancellation['account_closed_at'] is None and cancellation['status']=='requested','Request fabricates final reconciliation or closure')
estimate=response('/v1/agreement-cancellation-quotes','POST')
check(Decimal(estimate['estimated_refund'])==Decimal(estimate['unused_credits'])-Decimal(estimate['estimated_final_usage']),'Cancellation estimate double-deducts hold')
for resource in ['wallet-top-ups','wallet-refunds']:
    op=ops[('/v1/'+resource,'POST')]
    check(op['success']=='202','Payment request must be asynchronous')
    check(op['response']['data']['status'] not in ['settled','completed','paid'],'Creation fabricates settlement')
    check(op['request'].get('client_reference'),'Missing durable business reference')
    check(any(p['name']=='client_reference' for p in spec['paths']['/v1/'+resource]['get']['parameters']),'Missing recovery lookup')
for op in index:
    operation=spec['paths'][op['path']][op['method'].lower()]
    check(operation['operationId']==OPERATION_IDS[op['method']+' '+op['path']],'Existing operation identity changed')
    check(not set(operation['x-required-scopes']) & {'wallets:withdraw','wallets:transfer'},'Unsupported scopes remain')
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

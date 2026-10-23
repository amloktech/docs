"""Check wallet contract invariants and negative requests, without executing payments."""
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
import json
from jsonschema import Draft202012Validator, FormatChecker

ROOT=Path(__file__).resolve().parent.parent
spec=json.loads((ROOT/'openapi/amlok-v1.json').read_text())
index=json.loads((ROOT/'data/wallet-api-index.json').read_text())
ops={(op['path'],op['method']):op for op in index}
checks=0
def check(condition, message):
    global checks
    assert condition,message
    checks+=1
def valid(name,value):
    schema={'$ref':'#/components/schemas/'+name,'components':spec['components']}
    return Draft202012Validator(schema,format_checker=FormatChecker()).is_valid(value)
def response(path, method='GET'):
    return ops[(path,method)]['response']['data']

check(len(index)==56,'Expected 56 wallet and billing operations')
quote={'kind':'withdrawal','source_wallet_id':'wal_example','amount':'500.00','currency':'CAD','payout_destination_id':'destination_example'}
for value in ['0.00','-1.00','1.001','1e3','NaN',500,0.5,'']:
    check(not valid('CreateWalletQuote',{**quote,'amount':value}),'Invalid movement amount accepted: '+repr(value))
for value in ['0.01','500.00','1000000.00']:
    check(valid('CreateWalletQuote',{**quote,'amount':value}),'Valid positive amount rejected')
for field,value in [('currency','USD'),('kind','transfer'),('destination_wallet_id','wal_other'),('tenant_id','other'),('status','paid')]:
    check(not valid('CreateWalletQuote',{**quote,field:value}),'Invalid quote shape accepted: '+field)
for kind,field in [('transfer','destination_wallet_id'),('withdrawal','payout_destination_id'),('refund','origin_top_up_id')]:
    request={'kind':kind,'source_wallet_id':'wal_example','amount':'5.00','currency':'CAD',field:'res_example'}
    check(valid('CreateWalletQuote',request),'Expected destination rejected')
    request.pop(field)
    check(not valid('CreateWalletQuote',request),'Missing destination accepted')
for field in ['balance','legal_owner_id','tenant_id']:
    check(not valid('CreateWallet',{'name':'Example','currency':'CAD','usage_enabled':True,field:'injected'}),'Client can supply '+field)

balance=response('/v1/wallets/{id}/balance')
for name in ['committed_credits','additional_funds','promotional_credits']:
    bucket=balance[name]
    check(Decimal(bucket['available'])==Decimal(bucket['posted'])-Decimal(bucket['held']),name+' does not reconcile')
check(Decimal(balance['total_posted'])==sum(Decimal(balance[b]['posted']) for b in ['committed_credits','additional_funds','promotional_credits']),'Posted sum')
check(Decimal(balance['withdrawable'])==Decimal(balance['committed_credits']['available'])+Decimal(balance['additional_funds']['available']),'Committed credits not withdrawable')
check(Decimal(balance['available_for_usage'])==Decimal(balance['total_posted'])-Decimal(balance['total_held']),'Pending funding counted as available')
statement=response('/v1/billing/statements/{id}')
closing=sum(Decimal(statement[k]) for k in ['opening_balance','funding','transfers_in','adjustments'])-sum(Decimal(statement[k]) for k in ['transfers_out','usage','withdrawals','refunds','fees'])
check(closing==Decimal(statement['closing_balance'])==Decimal(balance['total_posted']),'Statement not reconciled')
consumption=response('/v1/billing/consumption')
check(sum(Decimal(r['net_amount']) for r in consumption['rows'])==Decimal(consumption['total_net_amount'])==Decimal(statement['usage']),'Consumption not reconciled')
usage=response('/v1/billing/usage/{id}')
check(Decimal(usage['quantity'])*Decimal(usage['unit_rate'])==Decimal(usage['amount']),'Usage math')
check(usage['quantity']=='1','Underwriting example must be one billable unit')
q=response('/v1/wallet-quotes','POST')
check(Decimal(q['total_debit'])==Decimal(q['amount'])+Decimal(q['fee_amount']),'Quote debit math')
check(q['recipient_amount']==q['amount'] and q['holds_funds'] is False,'Quote changes principal or reserves funds')
check(response('/v1/billing/account')['committed_credits_withdrawable'] is True,'Approved credit policy missing')
check(response('/v1/billing/account')['transfer_scope']=='same_institution_same_legal_owner','Approved transfer boundary missing')
for resource in ['wallet-top-ups','wallet-transfers','wallet-withdrawals','wallet-refunds']:
    op=ops[('/v1/'+resource,'POST')]
    check(op['success']=='202','Money creation must be asynchronous')
    check(op['response']['data']['status'] not in ['settled','completed','paid'],'Creation fabricates settlement')
    check(op['request'].get('client_reference'),'Missing durable business reference')
    get=spec['paths']['/v1/'+resource]['get']
    check(any(p['name']=='client_reference' for p in get['parameters']),'Missing recovery lookup')
for op in index:
    operation=spec['paths'][op['path']][op['method'].lower()]
    if op['method'] in ['POST','PATCH']:
        check(any(p['name']=='Idempotency-Key' and p['required'] for p in operation['parameters']),'Missing idempotency')
        for sample in operation['x-codeSamples']:
            check('Idempotency-Key' in sample['source'],'Sample omits idempotency')
    if op['method']=='PATCH' or op['path'].endswith(('/cancel','/decision','/disable')):
        check(any(p['name']=='If-Match' and p['required'] for p in operation['parameters']),'Missing concurrency check')
        for sample in operation['x-codeSamples']:
            check('If-Match' in sample['source'],'Sample omits ETag')
    for parameter in operation['parameters']:
        if parameter['in']=='query' and parameter.get('required'):
            for sample in operation['x-codeSamples']:
                check(parameter['name']+'=' in sample['source'],'Required query absent')
    request=operation.get('requestBody',{}).get('content',{}).get('application/json')
    if request:
        invalid={**request['example'],'balance':'999999.00'}
        check(not valid(request['schema']['$ref'].split('/')[-1],invalid),'Request accepts arbitrary balance')
check('/v1/billing/usage' in spec['paths'] and 'post' not in spec['paths']['/v1/billing/usage'],'Client can create a charge')
report=deepcopy(ops[('/v1/billing/reports','POST')]['request'])
report.update(report_type='ledger',time_basis='occurred_at')
check(not valid('CreateBillingReport',report),'Ledger export permits event time')
out={'checks':checks,'walletOperations':len(index),'scope':'Documentation contract only; no backend or payment rail executed.'}
(ROOT/'artifacts/wallet-contract-validation.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))

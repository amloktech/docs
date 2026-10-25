"""Wallet and billing contract extension. No payment execution or backend implementation.

Keep the workbook snapshot unchanged. These definitions generate the same OpenAPI,
endpoint pages, example requests, and Postman collection as the workbook operations.
"""
from copy import deepcopy
from urllib.parse import urlencode
import json

# Stable identifiers survive removal of obsolete wallet operations.
OPERATION_IDS = {'GET /v1/billing/account': 'WA001', 'GET /v1/billing/rate-card': 'WA002', 'GET /v1/billing/usage': 'WA003', 'GET /v1/billing/usage/{id}': 'WA004', 'GET /v1/billing/consumption': 'WA005', 'POST /v1/billing/reports': 'WA006', 'GET /v1/billing/reports': 'WA007', 'GET /v1/billing/reports/{id}': 'WA008', 'POST /v1/billing/reports/{id}/download-link': 'WA009', 'GET /v1/billing/statements': 'WA010', 'GET /v1/billing/statements/{id}': 'WA011', 'POST /v1/wallets': 'WA012', 'GET /v1/wallets': 'WA013', 'GET /v1/wallets/{id}': 'WA014', 'GET /v1/wallets/{id}/balance': 'WA015', 'GET /v1/wallets/{id}/ledger': 'WA016', 'GET /v1/wallets/{id}/credit-lots': 'WA017', 'GET /v1/wallets/{id}/holds': 'WA018', 'POST /v1/wallet-sessions': 'WA019', 'GET /v1/wallet-payment-methods': 'WA020', 'GET /v1/wallet-payment-methods/{id}': 'WA021', 'POST /v1/wallet-payment-methods/{id}/disable': 'WA022', 'POST /v1/wallet-top-ups': 'WA023', 'GET /v1/wallet-top-ups': 'WA024', 'GET /v1/wallet-top-ups/{id}': 'WA025', 'POST /v1/wallet-top-ups/{id}/cancel': 'WA026', 'GET /v1/wallets/{id}/auto-top-up': 'WA027', 'PATCH /v1/wallets/{id}/auto-top-up': 'WA028', 'POST /v1/wallet-quotes': 'WA029', 'GET /v1/wallet-quotes/{id}': 'WA030', 'POST /v1/wallet-transfers': 'WA031', 'GET /v1/wallet-transfers': 'WA032', 'GET /v1/wallet-transfers/{id}': 'WA033', 'POST /v1/wallet-transfers/{id}/cancel': 'WA034', 'POST /v1/wallet-withdrawals': 'WA035', 'GET /v1/wallet-withdrawals': 'WA036', 'GET /v1/wallet-withdrawals/{id}': 'WA037', 'POST /v1/wallet-withdrawals/{id}/cancel': 'WA038', 'POST /v1/wallet-refunds': 'WA039', 'GET /v1/wallet-refunds': 'WA040', 'GET /v1/wallet-refunds/{id}': 'WA041', 'POST /v1/wallet-refunds/{id}/cancel': 'WA042', 'GET /v1/wallet-payouts': 'WA043', 'GET /v1/wallet-payouts/{id}': 'WA044', 'GET /v1/wallet-approvals': 'WA045', 'GET /v1/wallet-approvals/{id}': 'WA046', 'POST /v1/wallet-approvals/{id}/decision': 'WA047', 'POST /v1/agreement-cancellation-quotes': 'WA048', 'POST /v1/agreement-cancellations': 'WA049', 'GET /v1/agreement-cancellations': 'WA050', 'GET /v1/agreement-cancellations/{id}': 'WA051', 'POST /v1/agreement-cancellations/{id}/cancel': 'WA052', 'POST /v1/wallet-closures': 'WA053', 'GET /v1/wallet-closures': 'WA054', 'GET /v1/wallet-closures/{id}': 'WA055', 'POST /v1/wallet-closures/{id}/cancel': 'WA056', 'POST /v1/wallet-refunds/{id}/retry': 'WA057'}

WALLET_EVENTS = [
    ('billing.usage.posted', 'billing_usage', 'A usage charge or compensating adjustment is posted.'),
    ('billing.report.updated', 'billing_report', 'A report is ready, failed, or expired.'),
    ('billing.statement.finalized', 'billing_statement', 'A statement revision is finalized.'),
    ('wallet.balance.updated', 'wallet', 'A posted entry or hold changes a balance.'),
    ('wallet.top_up.updated', 'wallet_top_up', 'A funding attempt changes state.'),
]
WALLET_ERRORS = {
    'duplicate_client_reference': (409, 'This business reference already identifies another intended funding action.'),
    'wallet_restricted': (409, 'This wallet is restricted or closed for funding.'),
    'funding_method_not_verified': (422, 'Use a verified funding method authorized by the same legal entity.'),
    'unsupported_wallet_currency': (422, 'The funding currency or payment route is not enabled.'),
    'wallet_capability_disabled': (403, 'This funding capability is not enabled for the institution.'),
    'funding_method_in_use': (409, 'An active automatic top-up policy or pending payment still uses this method.'),
}


def extend(g):
    S, E, spec = g['SCHEMAS'], g['EXAMPLES'], g['SPEC']
    ref, write, dump = g['ref'], g['write'], g['dump']
    now = g['NOW']
    string = {'type': 'string', 'minLength': 1}
    date = {'type': 'string', 'format': 'date-time'}
    amount = {'type': 'string', 'pattern': r'^(0|[1-9][0-9]*)\.[0-9]{2}$',
              'description': 'Nonnegative CAD amount, exact decimal string in major units.'}
    positive = {**amount, 'pattern': r'^(?:0\.(?:0[1-9]|[1-9][0-9])|[1-9][0-9]*\.[0-9]{2})$'}
    signed = {**amount, 'pattern': r'^-?(0|[1-9][0-9]*)\.[0-9]{2}$'}
    integer = {'type': 'integer', 'minimum': 0}
    currency = {'type': 'string', 'enum': ['CAD']}
    boolean = {'type': 'boolean'}
    enum = lambda *values: {'type': 'string', 'enum': list(values)}
    array = lambda item: {'type': 'array', 'items': item}
    nullable = g['nullable']
    obj = lambda props, required=None: {'type': 'object', 'properties': props, 'required': list(props) if required is None else required, 'additionalProperties': False}
    identity = {'id': string, 'object': string, 'record_version': {'type': 'integer', 'minimum': 1}, 'created_at': date, 'updated_at': date}
    def example(object_kind, **props):
        return {'id': object_kind+'_example', 'object': object_kind, 'record_version': 1, 'created_at': now, 'updated_at': now, **props}
    def model(name, kind, props, values):
        S[name] = obj({**identity, **props})
        E[name] = example(kind, **values)
    def request(name, props, required=None):
        S[name] = obj(props, required)
        return name

    model('BillingAccount', 'billing_account', {
        'currency': currency, 'agreement_id': string, 'agreement_version': string,
        'minimum_monthly_commitment': amount, 'payment_for_12_months': amount,
        'term_start': date, 'term_end': date, 'renewal_payment_at': date,
        'wallet_type': enum('prepaid_service_credits'),
        'outflow_policy': enum('product_usage_or_final_cancellation_refund'),
        'refund_policy': enum('full_remaining_paid_balance_on_final_cancellation'),
        'enabled_capabilities': array(enum('funding','auto_top_up')),
        'policy_version': string
    }, dict(currency='CAD',agreement_id='agr_example',agreement_version='3',minimum_monthly_commitment='1000.00',
        payment_for_12_months='12000.00',term_start='2026-10-01T00:00:00Z',term_end='2027-10-01T00:00:00Z',
        renewal_payment_at='2027-10-01T00:00:00Z',wallet_type='prepaid_service_credits',
        outflow_policy='product_usage_or_final_cancellation_refund',refund_policy='full_remaining_paid_balance_on_final_cancellation',
        enabled_capabilities=['funding','auto_top_up'],policy_version='wallet-policy-account-manager-cancellation'))
    rate_props = {'product': enum('insights','signal'),'tier': enum('standard','advanced','complex'),'unit': enum('completed_underwriting','active_account_month'),'base_rate': amount,'discount_percent': {'type':'string','pattern':r'^(?:100|[0-9]{1,2})(?:\.[0-9]{1,2})?$'},'effective_rate': amount}
    S['BillingRate'] = obj(rate_props)
    rates = [dict(product=p,tier=t,unit=u,base_rate=f'{r:.2f}',discount_percent='0',effective_rate=f'{r:.2f}') for p,u,values in [('insights','completed_underwriting',[5,15,35]),('signal','active_account_month',[3,5,8])] for t,r in zip(['standard','advanced','complex'],values)]
    model('BillingRateCard','billing_rate_card',{'currency':currency,'effective_from':date,'rates':array(ref('BillingRate'))},dict(currency='CAD',effective_from='2026-10-01T00:00:00Z',rates=rates))
    model('BillingUsage','billing_usage',{
        'wallet_id':string,'product':enum('insights','signal'),'tier':enum('standard','advanced','complex'),
        'source_resource_id':string,'unit':enum('completed_underwriting','active_account_month'),
        'quantity':{'type':'string','pattern':r'^(0|[1-9][0-9]*)(\.[0-9]+)?$'},
        'unit_rate':amount,'currency':currency,'amount':signed,'entry_type':enum('charge','reversal'),
        'reverses_usage_id':nullable(string),'status':enum('pending','posted','voided'),
        'occurred_at':date,'posted_at':nullable(date),'billing_period_start':date,'billing_period_end':date,
        'rate_card_id':string,'ledger_entry_id':nullable(string)
    },dict(wallet_id='wal_example',product='insights',tier='standard',source_resource_id='uw_example',unit='completed_underwriting',
        quantity='1',unit_rate='5.00',currency='CAD',amount='5.00',entry_type='charge',reverses_usage_id=None,status='posted',
        occurred_at=now,posted_at=now,billing_period_start='2026-10-01T00:00:00Z',billing_period_end='2026-11-01T00:00:00Z',
        rate_card_id='billing_rate_card_example',ledger_entry_id='ledger_usage_example'))
    S['ConsumptionRow'] = obj({'product':enum('insights','signal'),'tier':enum('standard','advanced','complex'),
        'bucket_start':date,'bucket_end':date,'quantity':{'type':'string','pattern':r'^-?(0|[1-9][0-9]*)(\.[0-9]+)?$'},
        'unit':enum('completed_underwriting','active_account_month'),'gross_amount':amount,'adjustment_amount':signed,'net_amount':signed})
    model('BillingConsumption','billing_consumption',{'currency':currency,'from':date,'to':date,'as_of':date,
        'time_basis':enum('occurred_at','posted_at'),'group_by':enum('product_tier','day','month'),
        'rows':array(ref('ConsumptionRow')),'total_net_amount':signed,'provisional':boolean},
        dict(currency='CAD',**{'from':'2026-10-01T00:00:00Z','to':'2026-11-01T00:00:00Z'},as_of=now,
        time_basis='posted_at',group_by='product_tier',rows=[{'product':'insights','tier':'standard','bucket_start':'2026-10-01T00:00:00Z','bucket_end':'2026-11-01T00:00:00Z','quantity':'100','unit':'completed_underwriting','gross_amount':'500.00','adjustment_amount':'0.00','net_amount':'500.00'},
        {'product':'signal','tier':'standard','bucket_start':'2026-10-01T00:00:00Z','bucket_end':'2026-11-01T00:00:00Z','quantity':'200','unit':'active_account_month','gross_amount':'600.00','adjustment_amount':'0.00','net_amount':'600.00'}],total_net_amount='1100.00',provisional=True))
    period_props = {'from':date,'to':date,'wallet_id':string}
    period_values = {'from':'2026-10-01T00:00:00Z','to':'2026-11-01T00:00:00Z','wallet_id':'wal_example'}
    report_props = {**period_props,'report_type':enum('usage','ledger','statement'),'format':enum('csv','json'),'time_basis':enum('occurred_at','posted_at')}
    request('CreateBillingReport',report_props)
    S['CreateBillingReport']['allOf'] = [{
        'if': {'properties': {'report_type': {'enum': ['ledger','statement']}}},
        'then': {'properties': {'time_basis': {'const': 'posted_at'}}},
    }]
    report_values = {**period_values,'report_type':'usage','format':'csv','time_basis':'posted_at'}
    model('BillingReport','billing_report',{**report_props,'status':enum('queued','processing','ready','failed','expired'),
        'as_of':date,'row_count':nullable(integer),'expires_at':nullable(date),'failure_code':nullable(string)},
        {**report_values,'status':'queued','as_of':now,'row_count':None,'expires_at':None,'failure_code':None})
    model('BillingDownload','billing_download',{'url':{'type':'string','format':'uri'},'expires_at':date,'sha256':{'type':'string','pattern':'^[a-f0-9]{64}$'}},
        dict(url='https://downloads.example.com/authorized-report',expires_at='2026-10-23T14:05:00Z',sha256='a'*64))
    model('BillingStatement','billing_statement',{**period_props,'currency':currency,'status':enum('provisional','final'),
        'revision':{'type':'integer','minimum':1},'supersedes_id':nullable(string),'as_of':date,
        **{k:amount for k in ['opening_balance','funding','usage','refunds','closing_balance']},
        'adjustments':signed,'ledger_sequence_from':integer,'ledger_sequence_to':integer},
        {**period_values,'currency':'CAD','status':'provisional','revision':1,'supersedes_id':None,'as_of':now,
        'opening_balance':'12000.00','funding':'0.00','usage':'1100.00','refunds':'0.00','adjustments':'0.00','closing_balance':'10900.00',
        'ledger_sequence_from':1,'ledger_sequence_to':3})
    model('Wallet','wallet',{'name':string,'currency':currency,'agreement_id':string,'legal_owner_id':string,'status':enum('active','restricted','closing','closed'),
        'usage_enabled':boolean},dict(name='Operating wallet',currency='CAD',agreement_id='agr_example',legal_owner_id='institution_example',status='active',usage_enabled=True))
    bucket = obj({'posted':amount,'held':amount,'available':amount})
    model('WalletBalance','wallet_balance',{'wallet_id':string,'currency':currency,'as_of':date,'ledger_sequence':integer,
        'committed_credits':bucket,'additional_funds':bucket,'promotional_credits':bucket,'pending_incoming':amount,
        'total_posted':amount,'total_held':amount,'available_for_usage':amount,'remaining_paid_credits':amount},
        dict(wallet_id='wal_example',currency='CAD',as_of=now,ledger_sequence=3,
        committed_credits={'posted':'10900.00','held':'500.00','available':'10400.00'},
        additional_funds={'posted':'0.00','held':'0.00','available':'0.00'},
        promotional_credits={'posted':'0.00','held':'0.00','available':'0.00'},
        pending_incoming='250.00',total_posted='10900.00',total_held='500.00',available_for_usage='10400.00',remaining_paid_credits='10900.00'))
    model('WalletLedgerEntry','wallet_ledger_entry',{'wallet_id':string,'sequence':integer,'currency':currency,
        'amount':signed,'balance_after':amount,'entry_type':enum('funding','usage','refund','adjustment','reversal'),
        'bucket':enum('committed_credits','additional_funds','promotional_credits'),'credit_lot_id':string,
        'movement_id':string,'reverses_entry_id':nullable(string),'posted_at':date,'client_reference':nullable(string)},
        dict(wallet_id='wal_example',sequence=3,currency='CAD',amount='-600.00',balance_after='10900.00',entry_type='usage',
        bucket='committed_credits',credit_lot_id='lot_example',movement_id='billing_usage_signal',reverses_entry_id=None,posted_at=now,client_reference='signal-october'))
    model('WalletCreditLot','wallet_credit_lot',{'wallet_id':string,'currency':currency,
        'origin_type':enum('minimum_commitment','additional_funding','promotional'),'origin_top_up_id':string,
        'original_amount':amount,'remaining_amount':amount,'held_amount':amount,
        'refund_policy':enum('on_final_cancellation','non_cash_promotional'),'restrictions':array(string)},
        dict(wallet_id='wal_example',currency='CAD',origin_type='minimum_commitment',origin_top_up_id='top_up_annual',
        original_amount='12000.00',remaining_amount='10900.00',held_amount='500.00',refund_policy='on_final_cancellation',restrictions=[]))
    model('WalletHold','wallet_hold',{'wallet_id':string,'currency':currency,'amount':amount,'movement_id':string,
        'reason':enum('refund','usage','dispute','legal'),'status':enum('active','captured','released'),
        'expires_at':nullable(date)},dict(wallet_id='wal_example',currency='CAD',amount='500.00',movement_id='billing_usage_pending',reason='usage',status='active',expires_at=None))
    session_request = {'purpose':enum('funding_method'),'return_url':{'type':'string','format':'uri'}}
    request('CreateWalletSession',session_request)
    model('WalletSession','wallet_session',{'purpose':session_request['purpose'],'url':{'type':'string','format':'uri'},'expires_at':date},
        dict(purpose='funding_method',url='https://payments.example.com/hosted-session',expires_at='2026-10-23T14:15:00Z'))
    method_props = {'legal_owner_id':string,'status':enum('pending_verification','verified','disabled','failed'),'masked_label':string,
        'currency':currency,'capabilities':array(enum('funding'))}
    model('WalletPaymentMethod','wallet_payment_method',method_props,dict(legal_owner_id='institution_example',status='verified',masked_label='Business bank account ending 1234',currency='CAD',capabilities=['funding']))
    request('CreateWalletTopUp',{'wallet_id':string,'funding_method_id':string,'amount':positive,'currency':currency,'client_reference':string})
    topup_req = dict(wallet_id='wal_example',funding_method_id='wallet_payment_method_example',amount='250.00',currency='CAD',client_reference='top-up-1001')
    model('WalletTopUp','wallet_top_up',{**S['CreateWalletTopUp']['properties'],'status':enum('requires_action','pending','settled','failed','cancelled','reversed'),
        'action_url':nullable({'type':'string','format':'uri'}),'settled_at':nullable(date),'ledger_entry_ids':array(string),'failure_code':nullable(string)},
        {**topup_req,'status':'pending','action_url':None,'settled_at':None,'ledger_entry_ids':[],'failure_code':None})
    auto_props = {'enabled':boolean,'threshold':amount,'top_up_amount':positive,'monthly_cap':positive,
        'funding_method_id':string,'authorization_id':string,'currency':currency}
    request('UpdateWalletAutoTopUp',auto_props)
    auto_values = dict(enabled=False,threshold='250.00',top_up_amount='1000.00',monthly_cap='5000.00',
        funding_method_id='wallet_payment_method_example',authorization_id='mandate_example',currency='CAD')
    model('WalletAutoTopUp','wallet_auto_top_up',{**auto_props,'wallet_id':string,'spent_this_month':amount}, {**auto_values,'wallet_id':'wal_example','spent_this_month':'0.00'})
    request('WalletReason',{'reason':string})
    operations = []
    def add(method,path,title,name,scope,description,req=None,body=None,is_list=False,query=None,example_override=None):
        group='Reporting' if path.startswith('/v1/billing/') else 'Wallets'
        oid=OPERATION_IDS[method+' '+path]
        page='api-reference/endpoints/'+('billing' if group=='Reporting' else group.lower())+'/'+title.lower().replace(' ','-')
        params=[]
        if '{id}' in path:
            params.append(g['parameter']('id','path','string','Authorized resource identifier.',True,('wal_example' if path.startswith('/v1/wallets/{id}') else E[name]['id']) if not path.endswith(('/cancel','/decision','/download-link','/disable')) else 'res_example'))
        params += [g['parameter'](key,'query',typ,desc,required,value,**extra) for key,typ,desc,required,value,extra in (query or [])]
        if is_list:
            params += [g['parameter']('limit','query','integer','Page size; default 100, maximum 200.',False,100,minimum=1,maximum=200),
                       g['parameter']('cursor','query','string','Opaque cursor bound to filters and a stable snapshot.',False,None)]
        if method in ['POST','PATCH']:
            params.append(g['parameter']('Idempotency-Key','header','string','Stable key for this intended action; retain across retries.',True,'idem_wallet_example'))
        if method=='PATCH' or path.endswith(('/cancel','/decision','/disable','/retry')):
            params.append(g['parameter']('If-Match','header','string','Quoted current resource version. Stale decisions return 412.',True,'"1"'))
        result=deepcopy(example_override if example_override is not None else E[name])
        response_schema,response_example=g['envelope'](ref(name),result,is_list)
        response_example['meta']=g['meta']('complete')
        if is_list: response_example['page']={'has_more':False,'next_cursor':None,'limit':100}
        code='202' if method=='POST' and name not in ['Wallet','WalletSession','WalletQuote','AgreementCancellationQuote','BillingDownload','WalletApproval'] else ('201' if method=='POST' else '200')
        if code=='202': response_example['meta']=g['meta']('pending')
        op={'operationId':oid,'summary':title,'description':description+'\n\nRequired scope: '+scope+'. Tenant and legal-owner checks apply on every read and write.',
            'tags':[group],'parameters':params,'security':[{'BearerAuth':[]}],'x-required-scopes':[scope],'responses':{}}
        if req: op['requestBody']={'required':True,'content':{'application/json':{'schema':ref(req),'example':body}}}
        sample_path=path.replace('{id}',next((x['example'] for x in params if x['in']=='path'),'res_example'))
        query_values={p['name']:p['example'] for p in params if p['in']=='query' and p.get('example') is not None}
        if query_values:sample_path+='?'+urlencode(query_values)
        op['x-codeSamples']=g['samples']({'Method':method,'Path':sample_path,'Operation ID':oid},params,body,'res_example')
        # Samples share the documented current ETag and stable idempotency headers.
        for sample in op['x-codeSamples']:
            sample['source']=sample['source'].replace('"3"','"1"').replace('\\"3\\"','\\"1\\"')
        if method=='PATCH':
            for sample in op['x-codeSamples']:
                if sample['lang']=='Shell': sample['source']=sample['source'].replace('  --header \"Accept:', '  --header \"Idempotency-Key: idem_wallet_example\" \\\n  --header \"Accept:')
                elif sample['lang']=='Python': sample['source']=sample['source'].replace('\nresponse =', '\nheaders[\"Idempotency-Key\"] = \"idem_wallet_example\"\nresponse =')
                else: sample['source']=sample['source'].replace('const response =', 'headers[\"Idempotency-Key\"] = \"idem_wallet_example\";\nconst response =')
        if method=='POST' and any(p['name']=='If-Match' for p in params):
            for sample in op['x-codeSamples']:
                if sample['lang']=='Shell': sample['source']=sample['source'].replace('  --header "Accept:', '  --header \'If-Match: "1"\' \\\n  --header "Accept:')
                elif sample['lang']=='Python': sample['source']=sample['source'].replace('\nresponse =', '\nheaders["If-Match"] = \'"1"\'\nresponse =')
                else:sample['source']=sample['source'].replace('const response =', 'headers["If-Match"] = \'"1"\';\nconst response =')
        op['responses'][code]={'description':('Accepted; inspect the resource status. No settlement is implied.' if code=='202' else 'Successful response.'),
            'headers':{'X-Request-ID':{'schema':{'type':'string'}},'ETag':{'schema':{'type':'string'},'example':'"'+str(result['record_version'])+'"'}},
            'content':{'application/json':{'schema':response_schema,'examples':{'synthetic':{'summary':'Synthetic '+title.lower(),'value':response_example}}}}}
        for error_code in ['400','401','403','404','409','412','422','429','500','503']:
            if 'Error'+error_code in spec['components'].get('responses',{}):
                op['responses'][error_code]={'$ref':'#/components/responses/Error'+error_code}
        for key,(status,meaning) in WALLET_ERRORS.items():
            if method=='GET':continue
            ec=str(status)
            response=op['responses'].get(ec,{})
            if '$ref' in response:response=deepcopy(spec['components']['responses'][response['$ref'].split('/')[-1]])
            if not response: response={'description':'Wallet request rejected.','content':{'application/json':{'schema':ref('ErrorEnvelope'),'examples':{}}}}
            response['content']['application/json']['examples'][key]={'value':{'error':{'code':key,'message':meaning,'retryable':False,'request_id':'req_example'},'meta':g['meta']('complete')}}
            op['responses'][ec]=response
        spec['paths'].setdefault(path,{})[method.lower()]=op
        notes=f'**Required scope:** \x60{scope}\x60\n\n{description}\n\n'
        notes+='[Wallet lifecycle](/api-reference/wallets) · [Consumption reporting](/api-reference/consumption-reporting) · [Refunds and payouts](/pricing/refunds-and-payouts)\n'
        if method in ['POST','PATCH']:notes+='\nUse an idempotency key for every mutation. Money commands also require a durable, institution-scoped business reference. A successful submission is not confirmation of settlement.\n'
        write(page+'.mdx','---\ntitle: '+json.dumps(title)+'\nopenapi: '+json.dumps('/openapi/amlok-v1.json '+method+' '+path)+'\nplayground: simple\n---\n\n'+notes)
        g['NAV_GROUPS'][group].append(page)
        item={'name':title,'request':{'method':method,'header':[{'key':'Accept','value':'application/json'}],
            'url':'{{base_url}}'+sample_path,'description':op['description']}}
        for p in params:
            if p['in']=='header':item['request']['header'].append({'key':p['name'],'value':'{{idempotency_key}}' if p['name']=='Idempotency-Key' else p['example']})
        if req:
            item['request']['header'].append({'key':'Content-Type','value':'application/json'})
            item['request']['body']={'mode':'raw','raw':dump(body),'options':{'raw':{'language':'json'}}}
        item['response']=[{'name':'Synthetic '+code,'originalRequest':deepcopy(item['request']),'status':{'200':'OK','201':'Created','202':'Accepted'}[code],
            'code':int(code),'header':[{'key':'Content-Type','value':'application/json'}],'body':dump(response_example)}]
        g['POSTMAN_GROUPS'][group].append(item)
        entry={'id':oid,'method':method,'path':path,'title':title,'scope':scope,'group':group,'page':page,'resource':result['object'],
               'request':body,'response':response_example,'success':code}
        g['OP_INDEX'].append(entry);operations.append(entry)
    def reads(path,title,name,scope,desc,filters=None):
        add('GET',path,'List '+title,name,scope,desc,is_list=True,query=filters)
        add('GET',path+'/{id}','Retrieve '+title.rstrip('s'),name,scope,desc)
    def q(key,typ,desc,example=None,required=False,**extra):return (key,typ,desc,required,example,extra)
    window=[q('from','datetime','Inclusive UTC boundary. Must precede to.','2026-10-01T00:00:00Z',True),q('to','datetime','Exclusive UTC boundary.','2026-11-01T00:00:00Z',True)]
    wallet_filter=[q('wallet_id','string','Restrict to one authorized wallet.','wal_example')]
    reference_filter=[q('client_reference','string','Look up a previous business action before attempting a retry.')]
    add('GET','/v1/billing/account','Retrieve billing account','BillingAccount','billing:read','Read agreed pricing, the prepaid-service-credit policy and enabled funding capabilities. Agreement changes and final cancellation are handled by your account manager. The API cannot request refunds, payouts, transfers, approvals or account closure.')
    add('GET','/v1/billing/rate-card','Retrieve billing rate card','BillingRateCard','billing:read','Read effective product rates and negotiated discounts. Historical usage retains its own rate-card identifier.')
    reads('/v1/billing/usage','usage records','BillingUsage','billing:read','Read immutable billable events and compensating reversals. No customer endpoint creates usage charges.',window+wallet_filter+[q('time_basis','string','Choose event or posting time.','posted_at',enum=['occurred_at','posted_at']),q('product','string','Product filter.',None,enum=['insights','signal']),q('tier','string','Complexity filter.',None,enum=['standard','advanced','complex'])])
    add('GET','/v1/billing/consumption','Retrieve consumption summary','BillingConsumption','billing:read','Aggregate posted usage and reversals at a consistent as_of snapshot. Pending usage is excluded. Product and tier remain distinct even when grouping by day or month.',
        query=window+wallet_filter+[q('time_basis','string','Basis for selecting charges.','posted_at',True,enum=['occurred_at','posted_at']),q('group_by','string','Grouping.','product_tier',True,enum=['product_tier','day','month'])])
    add('POST','/v1/billing/reports','Create billing report','BillingReport','billing:export','Generate a snapshot export asynchronously. Dates are UTC [from,to); from must precede to. Poll until ready. CSV cells that could execute spreadsheet formulas are escaped.','CreateBillingReport',report_values)
    reads('/v1/billing/reports','billing reports','BillingReport','billing:export','Read export status, snapshot time and expiry.',wallet_filter)
    add('POST','/v1/billing/reports/{id}/download-link','Create billing report download link','BillingDownload','billing:export','Only ready, unexpired reports return a short-lived authorized URL. Treat the link as a secret.','WalletReason',{'reason':'Monthly reconciliation.'})
    reads('/v1/billing/statements','billing statements','BillingStatement','billing:read','Statements reconcile posted ledger movements. Final revisions are immutable; later corrections create a linked revision.',wallet_filter)
    reads('/v1/wallets','wallets','Wallet','wallets:read','Read wallets provisioned for the authenticated institution. Wallet creation and account closure are managed through the platform and your account manager, not this API.')
    for suffix,title,name,listing in [('balance','wallet balance','WalletBalance',False),('ledger','wallet ledger entries','WalletLedgerEntry',True),('credit-lots','wallet credit lots','WalletCreditLot',True),('holds','wallet holds','WalletHold',True)]:
        add('GET','/v1/wallets/{id}/'+suffix,('List ' if listing else 'Retrieve ')+title,name,'wallets:read',
            'Read a consistent wallet snapshot. Pending funding is excluded from usable credits. Paid credits fund AMLOK products and are refundable only after final agreement cancellation and reconciliation. remaining_paid_credits includes paid principal held for unresolved activity; it is not an on-demand withdrawal balance. Ledger and funding lineage are immutable.',
            is_list=listing,query=([q('sequence_after','integer','Read entries after this exclusive wallet sequence.',None,minimum=0)] if suffix=='ledger' else None))
    add('POST','/v1/wallet-sessions','Create wallet payment session','WalletSession','wallets:funding','Create a hosted funding-method setup session for wallet top-ups. The return URL must be pre-allowlisted. Never send raw bank credentials or card data to this API. A browser redirect does not prove verification.','CreateWalletSession',{'purpose':'funding_method','return_url':'https://client.example.com/wallet/return'})
    reads('/v1/wallet-payment-methods','wallet payment methods','WalletPaymentMethod','wallets:read','Read authorized funding methods for wallet top-ups. These methods cannot be used to request withdrawals or payouts through the API.')
    disabled={**E['WalletPaymentMethod'],'status':'disabled','record_version':2}
    add('POST','/v1/wallet-payment-methods/{id}/disable','Disable wallet payment method','WalletPaymentMethod','wallets:funding','Disable future use. Reject while an active mandate or pending movement requires the method.','WalletReason',{'reason':'Replace bank account.'},example_override=disabled)
    add('POST','/v1/wallet-top-ups','Create wallet top-up','WalletTopUp','wallets:funding','Initiate a payment using an authorized funding method. Pending incoming funds are unavailable. Credit once on confirmed settlement. Original payment references remain linked to the credit lot for reconciliation. Reject funding after account closure; recover an unknown payment outcome using the existing business reference.','CreateWalletTopUp',topup_req)
    reads('/v1/wallet-top-ups','wallet top-ups','WalletTopUp','wallets:read','Read funding status. A failed or reversed payment is not spendable. Never retry an unknown payment with a new business reference.',wallet_filter+reference_filter)
    add('GET','/v1/wallets/{id}/auto-top-up','Retrieve automatic top-up policy','WalletAutoTopUp','wallets:read','Read the authorized threshold, amount, monthly cap and funding mandate.')
    add('PATCH','/v1/wallets/{id}/auto-top-up','Update automatic top-up policy','WalletAutoTopUp','wallets:funding','Replace the policy with a current ETag and an institution-approved authorization. Amount cannot exceed cap. One pending automatic attempt per wallet; failed attempts do not loop indefinitely. The confirmed agreement end date disables automatic funding and new usage. Changing funding_method_id and top_up_amount updates future automatic attempts, within the cap and current authorization; it does not modify already submitted payments.','UpdateWalletAutoTopUp',auto_values)
    S['WebhookEvent']['properties']['type']['enum'] += [e[0] for e in WALLET_EVENTS]
    g['REFINEMENTS'] += [
        'The customer API exposes reporting, wallet reads and funding only. Account managers handle agreements, final cancellation, closure and the resulting refund. No customer refund, payout, transfer, wallet-approval or closure endpoints are published. This contract does not implement a backend.',
        'AMLOK issues the full remaining paid-balance refund immediately after account closure. Bank receipt may take 7-10 business days, depending on the bank. Reconcile usage and funding and verify refund instructions before closure; an outstanding cancellation refund does not keep the account open.',
        'Funding mutations preserve durable business references beyond request-idempotency retention. Pending top-ups do not become usable credits before settlement.',
        'CAD is the documented settlement currency. Cancellation refunds are server-calculated from paid principal after final usage, with no wallet fees or deduction of remaining term obligations. Promotional benefits have no cash principal. Payment reversals and corrections are system reconciliation, never client cash-out capabilities.',
        'Funding uses payment methods authorized during onboarding. Cancellation refunds are administered by AMLOK, with confirmation through the account manager. Examples do not establish a production provider or regulatory status.',
    ]
    write('data/wallet-api-index.json',dump(operations))
    write('data/wallet-events.json',dump([{'event':a,'resource':b,'trigger':c} for a,b,c in WALLET_EVENTS]))
    return operations

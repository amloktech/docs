"""Read-only credit and billing reporting contract extension. No payment execution or backend implementation.

Keep the workbook snapshot unchanged. These definitions generate the same OpenAPI,
endpoint pages, example requests, and Postman collection as the workbook operations.
"""
from copy import deepcopy
from urllib.parse import urlencode
import json

# Stable identifiers survive removal of obsolete wallet operations.
OPERATION_IDS = {'GET /v1/billing/account': 'WA001', 'GET /v1/billing/rate-card': 'WA002', 'GET /v1/billing/usage': 'WA003', 'GET /v1/billing/usage/{id}': 'WA004', 'GET /v1/billing/consumption': 'WA005', 'POST /v1/billing/reports': 'WA006', 'GET /v1/billing/reports': 'WA007', 'GET /v1/billing/reports/{id}': 'WA008', 'POST /v1/billing/reports/{id}/download-link': 'WA009', 'GET /v1/billing/statements': 'WA010', 'GET /v1/billing/statements/{id}': 'WA011', 'POST /v1/wallets': 'WA012', 'GET /v1/wallets': 'WA013', 'GET /v1/wallets/{id}': 'WA014', 'GET /v1/wallets/{id}/balance': 'WA015', 'GET /v1/wallets/{id}/ledger': 'WA016', 'GET /v1/wallets/{id}/credit-lots': 'WA017', 'GET /v1/wallets/{id}/holds': 'WA018', 'POST /v1/wallet-sessions': 'WA019', 'GET /v1/wallet-payment-methods': 'WA020', 'GET /v1/wallet-payment-methods/{id}': 'WA021', 'POST /v1/wallet-payment-methods/{id}/disable': 'WA022', 'POST /v1/wallet-top-ups': 'WA023', 'GET /v1/wallet-top-ups': 'WA024', 'GET /v1/wallet-top-ups/{id}': 'WA025', 'POST /v1/wallet-top-ups/{id}/cancel': 'WA026', 'GET /v1/wallets/{id}/auto-top-up': 'WA027', 'PATCH /v1/wallets/{id}/auto-top-up': 'WA028', 'POST /v1/wallet-quotes': 'WA029', 'GET /v1/wallet-quotes/{id}': 'WA030', 'POST /v1/wallet-transfers': 'WA031', 'GET /v1/wallet-transfers': 'WA032', 'GET /v1/wallet-transfers/{id}': 'WA033', 'POST /v1/wallet-transfers/{id}/cancel': 'WA034', 'POST /v1/wallet-withdrawals': 'WA035', 'GET /v1/wallet-withdrawals': 'WA036', 'GET /v1/wallet-withdrawals/{id}': 'WA037', 'POST /v1/wallet-withdrawals/{id}/cancel': 'WA038', 'POST /v1/wallet-refunds': 'WA039', 'GET /v1/wallet-refunds': 'WA040', 'GET /v1/wallet-refunds/{id}': 'WA041', 'POST /v1/wallet-refunds/{id}/cancel': 'WA042', 'GET /v1/wallet-payouts': 'WA043', 'GET /v1/wallet-payouts/{id}': 'WA044', 'GET /v1/wallet-approvals': 'WA045', 'GET /v1/wallet-approvals/{id}': 'WA046', 'POST /v1/wallet-approvals/{id}/decision': 'WA047', 'POST /v1/agreement-cancellation-quotes': 'WA048', 'POST /v1/agreement-cancellations': 'WA049', 'GET /v1/agreement-cancellations': 'WA050', 'GET /v1/agreement-cancellations/{id}': 'WA051', 'POST /v1/agreement-cancellations/{id}/cancel': 'WA052', 'POST /v1/wallet-closures': 'WA053', 'GET /v1/wallet-closures': 'WA054', 'GET /v1/wallet-closures/{id}': 'WA055', 'POST /v1/wallet-closures/{id}/cancel': 'WA056', 'POST /v1/wallet-refunds/{id}/retry': 'WA057'}

OPERATION_IDS.update({'GET /v1/billing/credits': 'WA058', 'GET /v1/billing/credit-ledger': 'WA059'})

REPORTING_EVENTS = [
    ('billing.usage.posted', 'billing_usage', 'A usage charge or compensating adjustment is posted.'),
    ('billing.report.updated', 'billing_report', 'A report is ready, failed, or expired.'),
    ('billing.statement.finalized', 'billing_statement', 'A statement revision is finalized.'),
]



def extend(g):
    S, E, spec = g['SCHEMAS'], g['EXAMPLES'], g['SPEC']
    ref, write, dump = g['ref'], g['write'], g['dump']
    now = g['NOW']
    string = {'type': 'string', 'minLength': 1}
    date = {'type': 'string', 'format': 'date-time'}
    amount = {'type': 'string', 'pattern': r'^(0|[1-9][0-9]*)\.[0-9]{2}$',
              'description': 'Nonnegative CAD amount, exact decimal string in major units.'}
    positive = {**amount, 'pattern': r'^(?:0\.(?:0[1-9]|[1-9][0-9])|[1-9][0-9]*\.[0-9]{2})$'}
    signed = {**amount, 'pattern': r'^-?(0|[1-9][0-9]*)\.[0-9]{2}$', 'description': 'Signed CAD amount with exactly two decimal places. Negative values represent deductions or reversing adjustments.'}
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
        S[name] = obj({**identity, 'workspace_id': {**string, 'description': 'Authorized workspace whose unified billing account owns this report.'}, **props})
        E[name] = example(kind, workspace_id='wsp_example', **values)
    def request(name, props, required=None):
        S[name] = obj(props, required)
        return name

    model('BillingAccount', 'billing_account', {
        'currency': currency, 'agreement_id': string, 'agreement_version': string,
        'minimum_monthly_commitment': amount, 'payment_for_12_months': amount,
        'term_start': date, 'term_end': date, 'renewal_payment_at': date,
        'credit_type': enum('prepaid_service_credits'),
        'outflow_policy': enum('product_usage_or_final_cancellation_refund'),
        'refund_policy': enum('full_unused_balance_on_final_cancellation'),
        'access': enum('reporting_only'),
        'portal_controls': array(enum('payment_methods','automatic_top_ups','account_cancellation')),
        'funding_methods': array(enum('card','bank_account')),
        'default_auto_top_up_threshold': {**amount, 'const': '200.00'},
        'payment_frequency': enum('every_12_months'),
        'cancellation_notice_days': {'type':'integer','const':0},
        'closure_timing': enum('end_of_request_month'),
        'minimum_top_up_threshold': {**amount, 'const': '200.00'},
        'minimum_top_up_amount': {**amount, 'const': '500.00'},
        'refund_destination': enum('saved_portal_bank_account'),
        'policy_version': string
    }, dict(currency='CAD',agreement_id='agr_example',agreement_version='3',minimum_monthly_commitment='1000.00',
        payment_for_12_months='12000.00',term_start='2026-10-01T00:00:00Z',term_end='2027-10-01T00:00:00Z',
        renewal_payment_at='2027-10-01T00:00:00Z',credit_type='prepaid_service_credits',
        outflow_policy='product_usage_or_final_cancellation_refund',refund_policy='full_unused_balance_on_final_cancellation',
        access='reporting_only',portal_controls=['payment_methods','automatic_top_ups','account_cancellation'],
        funding_methods=['card','bank_account'],default_auto_top_up_threshold='200.00',minimum_top_up_threshold='200.00',
        payment_frequency='every_12_months',cancellation_notice_days=0,closure_timing='end_of_request_month',
        minimum_top_up_amount='500.00',refund_destination='saved_portal_bank_account',policy_version='unified-workspace-credits'))
    rate_props = {'product': enum('insights','signal'),'tier': enum('standard','advanced','complex'),'unit': enum('completed_underwriting','active_account_month'),'base_rate': amount,'discount_percent': {'type':'string','pattern':r'^(?:100(?:\.0{1,2})?|[0-9]{1,2}(?:\.[0-9]{1,2})?)$'},'effective_rate': amount}
    S['BillingRate'] = obj(rate_props)
    S['BillingWorkloadLimits'] = obj({
        'bank_accounts': integer, 'business_integrations': integer,
        'record_limit': {'type':'integer','minimum':1},
        'record_counting_basis': enum('per_underwriting','new_records_per_month'),
        'minimum_banking_history_months': nullable({'type':'integer','minimum':12}),
        'analysis_scope': string,
    })
    S['BillingRate']['properties'].update({
        'pricing_basis': {**enum('published','negotiated'), 'description':'A custom quote uses negotiated pricing under an existing tier, with explicit agreed limits.'},
        'workload_limits': ref('BillingWorkloadLimits'),
    })
    S['BillingRate']['required'] += ['pricing_basis','workload_limits']
    tier_limits = {
        'standard': dict(bank_accounts=2,business_integrations=5,record_limit=75000,minimum_banking_history_months=12,analysis_scope='Routine reconciliation and standard analysis'),
        'advanced': dict(bank_accounts=4,business_integrations=10,record_limit=250000,minimum_banking_history_months=12,analysis_scope='Multiple entities or channels and deeper reconciliation'),
        'complex': dict(bank_accounts=8,business_integrations=20,record_limit=1000000,minimum_banking_history_months=12,analysis_scope='Extensive relationships, exceptions, and investigation'),
    }
    S['BillingRate']['allOf'] = [
        {'if': {'properties': {'product': {'const':'insights'}}}, 'then': {'properties': {
            'unit': {'const':'completed_underwriting'},
            'workload_limits': {'properties': {'record_counting_basis': {'const':'per_underwriting'}, 'minimum_banking_history_months': {'type':'integer','minimum':12}}}}}},
        {'if': {'properties': {'product': {'const':'signal'}}}, 'then': {'properties': {
            'unit': {'const':'active_account_month'},
            'workload_limits': {'properties': {'record_counting_basis': {'const':'new_records_per_month'}, 'minimum_banking_history_months': {'type':'null'}}}}}},
    ]
    rates = []
    for product,unit,values in [('insights','completed_underwriting',[5,15,35]),('signal','active_account_month',[3,5,8])]:
        for tier,rate in zip(['standard','advanced','complex'],values):
            limits=deepcopy(tier_limits[tier])
            limits['record_counting_basis']='per_underwriting' if product=='insights' else 'new_records_per_month'
            if product=='signal': limits['minimum_banking_history_months']=None
            rates.append(dict(product=product,tier=tier,unit=unit,base_rate=f'{rate:.2f}',discount_percent='0',effective_rate=f'{rate:.2f}',pricing_basis='published',workload_limits=limits))
    S['BillingRate']['description']='CAD rates have exactly two decimals. Round the discounted effective unit rate first using decimal half-up rounding; multiply by billable quantity and round each charge to two decimals. Negotiated effective rates already include any discount.'

    model('BillingRateCard','billing_rate_card',{'currency':currency,'effective_from':date,'rates':array(ref('BillingRate'))},dict(currency='CAD',effective_from='2026-10-01T00:00:00Z',rates=rates))
    model('BillingUsage','billing_usage',{
        'billing_account_id':string,'product':enum('insights','signal'),'tier':enum('standard','advanced','complex'),
        'source_resource_id':{**string, 'description':'Underwriting identifier for Insights; stable borrower/business identifier for Signal, never an individual monitor or facility identifier.'},'unit':{**enum('completed_underwriting','active_account_month'), 'description':'Signal counts each active borrower/business once per workspace per month, including change-driven reassessment without an additional Insights charge, regardless of checks, monitoring configurations, facilities or data connections. Partial-month and tier-change treatment follows the agreement without duplicate charges for the same active period.'},
        'quantity':{'type':'string','pattern':r'^(0|[1-9][0-9]*)(\.[0-9]+)?$'},
        'unit_rate':amount,'currency':currency,'amount':signed,'entry_type':enum('charge','reversal'),
        'reverses_usage_id':nullable(string),'status':enum('pending','posted','voided'),
        'occurred_at':date,'posted_at':nullable(date),'billing_period_start':date,'billing_period_end':date,
        'rate_card_id':string,'ledger_entry_id':nullable(string)
    },dict(billing_account_id='billing_account_example',product='insights',tier='standard',source_resource_id='uw_example',unit='completed_underwriting',
        quantity='1',unit_rate='5.00',currency='CAD',amount='5.00',entry_type='charge',reverses_usage_id=None,status='posted',
        occurred_at=now,posted_at=now,billing_period_start='2026-10-01T00:00:00Z',billing_period_end='2026-11-01T00:00:00Z',
        rate_card_id='billing_rate_card_example',ledger_entry_id='ledger_usage_example'))
    S['ConsumptionRow'] = obj({'product':enum('insights','signal'),'tier':enum('standard','advanced','complex'),
        'bucket_start':date,'bucket_end':date,'quantity':{'type':'string','pattern':r'^-?(0|[1-9][0-9]*)(\.[0-9]+)?$'},
        'unit':enum('completed_underwriting','active_account_month'),'gross_amount':amount,'adjustment_amount':signed,'net_amount':signed})
    model('BillingConsumption','billing_consumption',{'billing_account_id':string,'currency':currency,'from':date,'to':date,'as_of':date,
        'time_basis':enum('occurred_at','posted_at'),'group_by':enum('product_tier','day','month'),
        'rows':array(ref('ConsumptionRow')),'total_net_amount':signed,'provisional':boolean},
        dict(billing_account_id='billing_account_example',currency='CAD',**{'from':'2026-10-01T00:00:00Z','to':'2026-11-01T00:00:00Z'},as_of=now,
        time_basis='posted_at',group_by='product_tier',rows=[{'product':'insights','tier':'standard','bucket_start':'2026-10-01T00:00:00Z','bucket_end':'2026-11-01T00:00:00Z','quantity':'100','unit':'completed_underwriting','gross_amount':'500.00','adjustment_amount':'0.00','net_amount':'500.00'},
        {'product':'signal','tier':'standard','bucket_start':'2026-10-01T00:00:00Z','bucket_end':'2026-11-01T00:00:00Z','quantity':'200','unit':'active_account_month','gross_amount':'600.00','adjustment_amount':'0.00','net_amount':'600.00'}],total_net_amount='1100.00',provisional=True))
    period_props = {'from':date,'to':date,'billing_account_id':string}
    period_values = {'from':'2026-10-01T00:00:00Z','to':'2026-11-01T00:00:00Z','billing_account_id':'billing_account_example'}
    report_props = {'from':date,'to':date,'report_type':enum('usage','ledger','statement'),'format':enum('csv','json'),'time_basis':enum('occurred_at','posted_at')}
    request('CreateBillingReport',report_props)
    S['CreateBillingReport']['allOf'] = [{
        'if': {'properties': {'report_type': {'enum': ['ledger','statement']}}},
        'then': {'properties': {'time_basis': {'const': 'posted_at'}}},
    }]
    report_values = {'from':period_values['from'],'to':period_values['to'],'report_type':'usage','format':'csv','time_basis':'posted_at'}
    model('BillingReport','billing_report',{**report_props,'billing_account_id':string,'status':enum('queued','processing','ready','failed','expired'),
        'as_of':date,'row_count':nullable(integer),'expires_at':nullable(date),'failure_code':nullable(string)},
        {**report_values,'billing_account_id':'billing_account_example','status':'queued','as_of':now,'row_count':None,'expires_at':None,'failure_code':None})
    model('BillingDownload','billing_download',{'url':{'type':'string','format':'uri'},'expires_at':date,'sha256':{'type':'string','pattern':'^[a-f0-9]{64}$'}},
        dict(url='https://downloads.example.com/authorized-report',expires_at='2026-10-23T14:05:00Z',sha256='a'*64))
    model('BillingStatement','billing_statement',{**period_props,'currency':currency,'status':enum('provisional','final'),
        'revision':{'type':'integer','minimum':1},'supersedes_id':nullable(string),'as_of':date,
        **{k:amount for k in ['opening_balance','funding','usage','refunds','closing_balance']},
        'adjustments':signed,'ledger_sequence_from':integer,'ledger_sequence_to':integer},
        {**period_values,'currency':'CAD','status':'provisional','revision':1,'supersedes_id':None,'as_of':now,
        'opening_balance':'12000.00','funding':'0.00','usage':'1100.00','refunds':'0.00','adjustments':'0.00','closing_balance':'10900.00',
        'ledger_sequence_from':1,'ledger_sequence_to':3})
    model('BillingCreditBalance','billing_credit_balance',{'billing_account_id':string,'currency':currency,'as_of':date,'ledger_sequence':integer,
        'pending_incoming':amount,'total_posted':amount,'total_held':amount,'available_for_usage':amount},
        dict(billing_account_id='billing_account_example',currency='CAD',as_of=now,ledger_sequence=3,
        pending_incoming='500.00',total_posted='10900.00',total_held='500.00',available_for_usage='10400.00'))
    model('BillingCreditEntry','billing_credit_entry',{'billing_account_id':string,'sequence':integer,'currency':currency,
        'amount':signed,'balance_after':amount,'entry_type':enum('funding','usage','refund','adjustment','reversal'),
        'movement_id':string,'reverses_entry_id':nullable(string),'posted_at':date,'client_reference':nullable(string)},
        dict(billing_account_id='billing_account_example',sequence=3,currency='CAD',amount='-600.00',balance_after='10900.00',entry_type='usage',
        movement_id='billing_usage_signal',reverses_entry_id=None,posted_at=now,client_reference='signal-october'))
    request('BillingReportDownloadRequest',{'reason':string})
    operations = []
    def add(method,path,title,name,scope,description,req=None,body=None,is_list=False,query=None,example_override=None):
        group='Reporting'
        oid=OPERATION_IDS[method+' '+path]
        page='api-reference/endpoints/billing/'+title.lower().replace(' ','-')
        params=[]
        if '{id}' in path:
            params.append(g['parameter']('id','path','string','Authorized resource identifier.',True,E['BillingReport']['id'] if path.endswith('/download-link') else E[name]['id']))
        params += [g['parameter'](key,'query',typ,desc,required,value,**extra) for key,typ,desc,required,value,extra in (query or [])]
        if is_list:
            params += [g['parameter']('limit','query','integer','Page size; default 100, maximum 200.',False,100,minimum=1,maximum=200),
                       g['parameter']('cursor','query','string','Opaque cursor bound to filters and a stable snapshot.',False,None)]
        if method in ['POST','PATCH']:
            params.append(g['parameter']('Idempotency-Key','header','string','Stable key for this intended action; retain across retries.',True,'idem_reporting_example'))
        if method=='PATCH' or path.endswith(('/cancel','/decision','/disable','/retry')):
            params.append(g['parameter']('If-Match','header','string','Quoted current resource version. Stale decisions return 412.',True,'"1"'))
        result=deepcopy(example_override if example_override is not None else E[name])
        response_schema,response_example=g['envelope'](ref(name),result,is_list)
        response_example['meta']=g['meta']('complete')
        if is_list: response_example['page']={'has_more':False,'next_cursor':None,'limit':100}
        code='202' if method=='POST' and name=='BillingReport' else ('201' if method=='POST' else '200')
        if code=='202': response_example['meta']=g['meta']('pending')
        op={'operationId':oid,'summary':title,'description':description+'\n\nRequired scope: '+scope+'. The API key is bound to exactly one workspace, institution and environment. There is no workspace override; this binding applies to every read and export.',
            'tags':[group],'parameters':params,'security':[{'BearerAuth':[]}],'x-required-scopes':[scope],'responses':{}}
        if req: op['requestBody']={'required':True,'content':{'application/json':{'schema':ref(req),'example':body}}}
        sample_path=path.replace('{id}',next((x['example'] for x in params if x['in']=='path'),'res_example'))
        query_values={p['name']:p['example'] for p in params if p['in']=='query' and p.get('example') is not None}
        if query_values:sample_path+='?'+urlencode(query_values)
        op['x-codeSamples']=g['samples']({'Method':method,'Path':sample_path,'Operation ID':oid},params,body,'res_example')
        # Samples share the documented current ETag and stable idempotency headers.
        for sample in op['x-codeSamples']:
            sample['source']=sample['source'].replace('"3"','"1"').replace('\\"3\\"','\\"1\\"')
        op['responses'][code]={'description':('Accepted; inspect the report status. Credit balances are unchanged.' if code=='202' else 'Successful response.'),
            'headers':{'X-Request-ID':{'schema':{'type':'string'}},'ETag':{'schema':{'type':'string'},'example':'"'+str(result['record_version'])+'"'}},
            'content':{'application/json':{'schema':response_schema,'examples':{'synthetic':{'summary':'Synthetic '+title.lower(),'value':response_example}}}}}
        for error_code in ['400','401','403','404','409','412','422','429','500','503']:
            if 'Error'+error_code in spec['components'].get('responses',{}):
                op['responses'][error_code]={'$ref':'#/components/responses/Error'+error_code}
        spec['paths'].setdefault(path,{})[method.lower()]=op
        notes=f'**Required scope:** \x60{scope}\x60\n\n{description}\n\n'
        notes+='[Credit reporting](/api-reference/credit-reporting) · [Consumption reporting](/api-reference/consumption-reporting) · [Cancellation and refunds](/pricing/refunds-and-payouts)\n'
        if method in ['POST','PATCH']:notes+='\nUse an idempotency key when creating an export or download link. These actions do not add, spend, or move credits.\n'
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
    add('GET','/v1/billing/account','Retrieve billing account','BillingAccount','billing:read','Read the unified workspace billing policy, CAD 200 default automatic top-up trigger, and CAD 500 minimum customer-funded top-up. The client portal manages card or bank-account payment methods, automatic top-ups and cancellation; enterprise clients can also use their dedicated account manager. The public API provides reporting only. Cancellation is available at any time with no notice period. Full closure is at the end of the request month, with an immediate refund of all unused credits, including promotional credits, to the saved portal bank account. Data is deleted after the month closes and necessary final information is generated. Used credits are non-refundable.')
    add('GET','/v1/billing/rate-card','Retrieve billing rate card','BillingRateCard','billing:read','Read published or negotiated rates and agreed workload limits for the workspace. Custom quotes retain standard, advanced or complex as the tier and use pricing_basis negotiated with the agreed effective_rate and workload_limits. Insights record_limit covers the complete underwriting snapshot, including at least 12 months of banking history. Signal record_limit covers only newly processed records during the month; unchanged baseline records are not counted again. The tier must cover every workload dimension; custom allowances require an agreed quote. Historical usage retains its own rate-card identifier and effective rate.')
    reads('/v1/billing/usage','usage records','BillingUsage','billing:read','Read immutable billable events and compensating reversals. No customer endpoint creates usage charges.',window+[q('time_basis','string','Choose event or posting time.','posted_at',enum=['occurred_at','posted_at']),q('product','string','Product filter.',None,enum=['insights','signal']),q('tier','string','Complexity filter.',None,enum=['standard','advanced','complex'])])
    add('GET','/v1/billing/consumption','Retrieve consumption summary','BillingConsumption','billing:read','Aggregate posted usage and reversals at a consistent as_of snapshot. Pending usage is excluded. Product and tier remain distinct even when grouping by day or month.',
        query=window+[q('time_basis','string','Basis for selecting charges.','posted_at',True,enum=['occurred_at','posted_at']),q('group_by','string','Grouping.','product_tier',True,enum=['product_tier','day','month'])])
    add('POST','/v1/billing/reports','Create billing report','BillingReport','billing:export','Generate a read-only snapshot export asynchronously. This does not change credits or payment settings. Dates are UTC [from,to); from must precede to. Poll until ready. CSV cells that could execute spreadsheet formulas are escaped.','CreateBillingReport',report_values)
    reads('/v1/billing/reports','billing reports','BillingReport','billing:export','Read export status, snapshot time and expiry.')
    add('POST','/v1/billing/reports/{id}/download-link','Create billing report download link','BillingDownload','billing:export','Only ready, unexpired reports return a short-lived authorized URL. Treat the link as a secret.','BillingReportDownloadRequest',{'reason':'Monthly reconciliation.'})
    reads('/v1/billing/statements','billing statements','BillingStatement','billing:read','Statements reconcile posted ledger movements. Final revisions are immutable; later corrections create a linked revision.')
    add('GET','/v1/billing/credits','Retrieve credit balance','BillingCreditBalance','billing:read',
        'Read one unified workspace credit balance, including paid and promotional top-ups without consumption priority. Pending incoming payments are excluded. available_for_usage equals total_posted minus total_held. CAD 200 is an automatic top-up trigger, not a reserved balance floor. Processing may use credits below CAD 200 and is rejected only when available credits cannot cover its cost; rejected unprocessed work is not charged. The full unused balance is refunded only at month-end account closure after cancellation reconciliation. This endpoint cannot change credits or portal payment settings.')
    add('GET','/v1/billing/credit-ledger','List credit ledger entries','BillingCreditEntry','billing:read',
        'Read posted credit additions, product consumption, reconciliation adjustments and final-cancellation refunds. Entries are immutable and returned in ascending sequence order at a stable snapshot. The customer cannot create or change ledger entries. Read a statement or export for period reconciliation.',
        is_list=True,query=[q('sequence_after','integer','Read entries after this exclusive billing account sequence.',None,minimum=0)])
    S['WebhookEvent']['properties']['type']['enum'] += [e[0] for e in REPORTING_EVENTS]
    g['REFINEMENTS'] += [
        'The public API is reporting-only. Client portal controls manage card or bank-account funding, top-up thresholds of at least CAD 200, top-up amounts of at least CAD 500, and cancellation. No public wallet or payment-setting operations exist.',
        'Cancellation can be requested at any time with no notice, in the portal or through an enterprise account manager. Closure occurs at the end of the request month. Workspace deletion follows month closure and generation of final information. AMLOK immediately refunds all unused credits, including promotional credits, to the saved portal bank account when the account closes. Bank receipt may take 7-10 business days. Used credits are non-refundable.',
        'Each workspace has one shared balance with no paid/promotional consumption priority. Reports identify workspace and product usage. CAD 200 triggers automatic top-ups if enabled, not a processing floor. New processing is rejected only when available credits cannot cover it; pending payments are not spendable.',
        'Custom pricing retains standard, advanced or complex and publishes negotiated rates and workload limits. Insights limits cover the complete underwriting snapshot including at least 12 months of banking history. Signal limits cover newly processed records each month. The most demanding dimension sets the required tier.',
    ]
    write('data/reporting-api-index.json',dump(operations))
    write('data/reporting-events.json',dump([{'event':a,'resource':b,'trigger':c} for a,b,c in REPORTING_EVENTS]))
    return operations

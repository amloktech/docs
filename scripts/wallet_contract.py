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
    ('wallet.refund.updated', 'wallet_refund', 'A final-cancellation refund changes state.'),
    ('wallet.payout.updated', 'wallet_payout', 'A cancellation-refund payout changes state.'),
    ('wallet.destination.updated', 'wallet_destination', 'Destination verification or availability changes.'),
    ('wallet.approval.updated', 'wallet_approval', 'A required approval is decided or expires.'),
    ('billing.cancellation.updated', 'agreement_cancellation', 'An agreement cancellation changes state.'),
    ('wallet.closure.updated', 'wallet_closure', 'A wallet closure changes state.'),
]
WALLET_ERRORS = {
    'insufficient_available_balance': (409, 'The reconciled paid balance no longer covers the quoted cancellation refund.'),
    'quote_expired': (409, 'Obtain a new quote before submitting a new movement.'),
    'quote_mismatch': (409, 'The quote does not match the operation, source, destination, or amount.'),
    'duplicate_client_reference': (409, 'This business reference already identifies another intended action.'),
    'movement_not_cancellable': (409, 'The movement passed its cancellation boundary.'),
    'wallet_restricted': (409, 'The wallet is restricted or closing for this operation.'),
    'refund_limit_exceeded': (409, 'The amount exceeds the remaining refundable funding principal.'),
    'closure_balance_remaining': (409, 'Funds, holds, or pending settlements remain unresolved.'),
    'destination_not_verified': (422, 'Use a verified destination owned by the same legal entity.'),
    'cancellation_not_final': (409, 'The agreement must be effective, finally reconciled, and awaiting its remaining-balance refund.'),
    'refund_already_in_progress': (409, 'A refund already reserves this balance; retrieve the existing refund.'),
    'refund_not_retryable': (409, 'Retry only after a definitive failure, cancellation, or return; an unknown payment outcome cannot be retried.'),
    'refund_balance_changed': (409, 'The final statement or remaining paid balance changed; reconcile and obtain a fresh quote.'),
    'unsupported_wallet_currency': (422, 'The currency or payment route is not enabled.'),
    'approval_actor_conflict': (403, 'An independent authorized approver must decide this request.'),
    'wallet_capability_disabled': (403, 'This wallet capability is not enabled for the institution.'),
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
        'enabled_capabilities': array(enum('funding','cancellation_refunds','auto_top_up')),
        'approval_required_for': array(enum('refund_delivery','cancellation')),
        'policy_version': string
    }, dict(currency='CAD',agreement_id='agr_example',agreement_version='3',minimum_monthly_commitment='1000.00',
        payment_for_12_months='12000.00',term_start='2026-10-01T00:00:00Z',term_end='2027-10-01T00:00:00Z',
        renewal_payment_at='2027-10-01T00:00:00Z',wallet_type='prepaid_service_credits',
        outflow_policy='product_usage_or_final_cancellation_refund',refund_policy='full_remaining_paid_balance_on_final_cancellation',
        enabled_capabilities=['funding','cancellation_refunds','auto_top_up'],approval_required_for=['refund_delivery'],policy_version='wallet-policy-cancellation-only'))
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
    request('CreateWallet',{'name':string,'currency':currency,'usage_enabled':boolean})
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
    session_request = {'purpose':enum('funding_method','payout_destination'),'return_url':{'type':'string','format':'uri'}}
    request('CreateWalletSession',session_request)
    model('WalletSession','wallet_session',{'purpose':session_request['purpose'],'url':{'type':'string','format':'uri'},'expires_at':date},
        dict(purpose='payout_destination',url='https://payments.example.com/hosted-session',expires_at='2026-10-23T14:15:00Z'))
    method_props = {'legal_owner_id':string,'status':enum('pending_verification','verified','disabled','failed'),'masked_label':string,
        'currency':currency,'capabilities':array(enum('funding','payout'))}
    model('WalletPaymentMethod','wallet_payment_method',method_props,dict(legal_owner_id='institution_example',status='verified',masked_label='Business bank account ending 1234',currency='CAD',capabilities=['funding','payout']))
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
    zero_amount = {**amount, 'const':'0.00'}
    allocation_props = {'origin_top_up_id':string,'destination_id':string,'amount':amount}
    S['WalletRefundAllocation'] = obj(allocation_props)
    allocations = [{'origin_top_up_id':'top_up_annual','destination_id':'wallet_payment_method_example','amount':'10900.00'}]
    quote_props = {'kind':enum('refund'),'source_wallet_id':string,'cancellation_id':string,'currency':currency,
        'payout_destination_id':string,'refund_id':string}
    request('CreateWalletQuote',quote_props,['kind','source_wallet_id','cancellation_id','currency'])
    S['CreateWalletQuote']['description'] = 'Final-cancellation refund only. Amount and funding allocations are calculated by the server from the final reconciled paid balance. No client-selected partial amount. payout_destination_id is permitted only as a verified same-owner fallback when the original source cannot receive the refund. refund_id is required for a retry quote.'
    quote_values = dict(kind='refund',source_wallet_id='wal_example',cancellation_id='cancellation_final_example',currency='CAD')
    model('WalletQuote','wallet_quote',{'kind':enum('refund'),'source_wallet_id':string,'cancellation_id':string,
        'final_statement_id':string,'final_statement_revision':{'type':'integer','minimum':1},'refund_id':nullable(string),
        'allocations':array(ref('WalletRefundAllocation')),'amount':amount,'fee_amount':zero_amount,
        'total_debit':amount,'recipient_amount':amount,'currency':currency,'expires_at':date,'policy_version':string,
        'source_wallet_version':{'type':'integer','minimum':1},'approval_required':boolean,'holds_funds':{'const':False,'type':'boolean'}},
        dict(kind='refund',source_wallet_id='wal_example',cancellation_id='cancellation_final_example',final_statement_id='statement_final_example',
        final_statement_revision=1,refund_id=None,allocations=allocations,amount='10900.00',fee_amount='0.00',total_debit='10900.00',recipient_amount='10900.00',
        currency='CAD',expires_at='2026-10-23T14:10:00Z',policy_version='wallet-policy-cancellation-only',source_wallet_version=3,approval_required=True,holds_funds=False))
    request('CreateWalletMovement',{'quote_id':string,'client_reference':string})
    model('WalletRefund','wallet_refund',{'source_wallet_id':string,'cancellation_id':string,'final_statement_id':string,
        'quote_id':string,'client_reference':string,'currency':currency,'amount':amount,'fee_amount':zero_amount,'total_debit':amount,'recipient_amount':amount,
        'allocations':array(ref('WalletRefundAllocation')),'paid_amount':amount,'remaining_amount':amount,
        'hold_id':nullable(string),'approval_id':nullable(string),'payout_ids':array(string),'ledger_entry_ids':array(string),
        'status':enum('requires_approval','pending','submitted','partially_paid','paid','failed','cancelled','returned'),
        'cancellable':boolean,'failure_code':nullable(string)},
        dict(source_wallet_id='wal_example',cancellation_id='cancellation_final_example',final_statement_id='statement_final_example',
        quote_id='wallet_quote_refund',client_reference='cancellation-refund-1001',currency='CAD',amount='10900.00',fee_amount='0.00',
        total_debit='10900.00',recipient_amount='10900.00',allocations=allocations,paid_amount='0.00',remaining_amount='10900.00',
        hold_id='wallet_hold_refund',approval_id='wallet_approval_example',payout_ids=[],ledger_entry_ids=[],status='requires_approval',cancellable=True,failure_code=None))
    model('WalletPayout','wallet_payout',{'movement_id':string,'movement_type':enum('refund'),'cancellation_id':string,
        'status':enum('pending','submitted','paid','failed','returned'),'currency':currency,'amount':amount,
        'destination_id':string,'origin_top_up_id':string,'provider_reference':nullable(string),'submitted_at':nullable(date),'paid_at':nullable(date),
        'returned_at':nullable(date),'return_amount':amount,'failure_code':nullable(string)},
        dict(movement_id='wallet_refund_example',movement_type='refund',cancellation_id='cancellation_final_example',status='pending',currency='CAD',amount='10900.00',
        destination_id='wallet_payment_method_example',origin_top_up_id='top_up_annual',provider_reference=None,submitted_at=None,paid_at=None,returned_at=None,return_amount='0.00',failure_code=None))
    model('WalletApproval','wallet_approval',{'target_type':enum('refund'),'target_id':string,
        'target_version':{'type':'integer','minimum':1},'status':enum('pending','approved','rejected','expired','invalidated'),
        'requested_by':string,'decided_by':nullable(string),'expires_at':date,'decision_at':nullable(date)},
        dict(target_type='refund',target_id='wallet_refund_example',target_version=1,status='pending',
        requested_by='actor_initiator',decided_by=None,expires_at='2026-10-24T14:00:00Z',decision_at=None))
    request('DecideWalletApproval',{'decision':enum('approve','reject'),'reason':string})
    request('WalletReason',{'reason':string})
    cancellation_props = {'agreement_id':string,'requested_effective_at':date}
    request('CreateCancellationQuote',cancellation_props)
    model('AgreementCancellationQuote','agreement_cancellation_quote',{**cancellation_props,'agreement_version':string,'expires_at':date,
        'currency':currency,'unused_credits':amount,'held_amount':amount,'estimated_final_usage':amount,'estimated_remaining_obligation':amount,
        'estimated_refund':amount,'obligations_explanation':string,'provisional':{'type':'boolean','const':True}},
        dict(agreement_id='agr_example',requested_effective_at='2027-10-01T00:00:00Z',agreement_version='3',
        expires_at='2026-10-23T14:10:00Z',currency='CAD',unused_credits='10900.00',held_amount='500.00',
        estimated_final_usage='500.00',estimated_remaining_obligation='0.00',estimated_refund='10400.00',
        obligations_explanation='Estimated final usage includes the pending usage hold once. Remaining agreement obligations are disclosed separately and do not reduce the unused paid-balance refund.',provisional=True))
    request('CreateAgreementCancellation',{'quote_id':string,'reason':string,'client_reference':string})
    model('AgreementCancellation','agreement_cancellation',{'agreement_id':string,'quote_id':string,'client_reference':string,
        'status':enum('requested','scheduled','effective','reconciling','refund_pending','completed','rejected','withdrawn'),
        'requested_effective_at':date,'effective_at':nullable(date),'final_statement_id':nullable(string),
        'reconciled_at':nullable(date),'final_refund_amount':nullable(amount),'refunded_amount':amount,'refund_ids':array(string),
        'remaining_obligation':nullable(amount),'currency':currency,'reason':string},
        dict(agreement_id='agr_example',quote_id='agreement_cancellation_quote_example',client_reference='cancellation-1001',
        status='requested',requested_effective_at='2027-10-01T00:00:00Z',effective_at=None,final_statement_id=None,
        reconciled_at=None,final_refund_amount=None,refunded_amount='0.00',refund_ids=[],remaining_obligation=None,currency='CAD',reason='Do not renew this agreement.'))
    request('CreateWalletClosure',{'wallet_id':string,'cancellation_id':string,'reason':string,'client_reference':string})
    model('WalletClosure','wallet_closure',{**S['CreateWalletClosure']['properties'],'status':enum('requested','reconciling','blocked','completed','withdrawn'),
        'blocking_reasons':array(string),'final_statement_id':nullable(string),'closed_at':nullable(date)},
        dict(wallet_id='wal_example',cancellation_id='cancellation_final_example',reason='Close after final cancellation and refund.',client_reference='closure-1001',status='requested',
        blocking_reasons=['remaining_balance','pending_settlements'],final_statement_id=None,closed_at=None))

    E['WalletQuote']['id']='wallet_quote_refund'
    operations = []
    def add(method,path,title,name,scope,description,req=None,body=None,is_list=False,query=None,example_override=None):
        group='Billing' if path.startswith(('/v1/billing/','/v1/agreement-')) else 'Wallets'
        oid=OPERATION_IDS[method+' '+path]
        page='api-reference/endpoints/'+group.lower()+'/'+title.lower().replace(' ','-')
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
    add('GET','/v1/billing/account','Retrieve billing account','BillingAccount','billing:read','Read the minimum monthly commitment, prepaid-service-credit policy, enabled funding capabilities, and cancellation-refund delivery approvals. Funds are consumed by AMLOK products or returned in full after final agreement cancellation; on-demand withdrawals and transfers are not supported.')
    add('GET','/v1/billing/rate-card','Retrieve billing rate card','BillingRateCard','billing:read','Read effective product rates and negotiated discounts. Historical usage retains its own rate-card identifier.')
    reads('/v1/billing/usage','usage records','BillingUsage','billing:read','Read immutable billable events and compensating reversals. No customer endpoint creates usage charges.',window+wallet_filter+[q('time_basis','string','Choose event or posting time.','posted_at',enum=['occurred_at','posted_at']),q('product','string','Product filter.',None,enum=['insights','signal']),q('tier','string','Complexity filter.',None,enum=['standard','advanced','complex'])])
    add('GET','/v1/billing/consumption','Retrieve consumption summary','BillingConsumption','billing:read','Aggregate posted usage and reversals at a consistent as_of snapshot. Pending usage is excluded. Product and tier remain distinct even when grouping by day or month.',
        query=window+wallet_filter+[q('time_basis','string','Basis for selecting charges.','posted_at',True,enum=['occurred_at','posted_at']),q('group_by','string','Grouping.','product_tier',True,enum=['product_tier','day','month'])])
    add('POST','/v1/billing/reports','Create billing report','BillingReport','billing:export','Generate a snapshot export asynchronously. Dates are UTC [from,to); from must precede to. Poll until ready. CSV cells that could execute spreadsheet formulas are escaped.','CreateBillingReport',report_values)
    reads('/v1/billing/reports','billing reports','BillingReport','billing:export','Read export status, snapshot time and expiry.',wallet_filter)
    add('POST','/v1/billing/reports/{id}/download-link','Create billing report download link','BillingDownload','billing:export','Only ready, unexpired reports return a short-lived authorized URL. Treat the link as a secret.','WalletReason',{'reason':'Monthly reconciliation.'})
    reads('/v1/billing/statements','billing statements','BillingStatement','billing:read','Statements reconcile posted ledger movements. Final revisions are immutable; later corrections create a linked revision.',wallet_filter)
    add('POST','/v1/wallets','Create wallet','Wallet','wallets:write','Create a prepaid CAD service-credit wallet under the authenticated institution, onboarded legal owner and active billing agreement. The client cannot supply another tenant, owner or arbitrary agreement. A cancelled agreement cannot create a wallet to resume usage.','CreateWallet',{'name':'Operating wallet','currency':'CAD','usage_enabled':True})
    reads('/v1/wallets','wallets','Wallet','wallets:read','Read wallets owned by the authenticated institution.')
    for suffix,title,name,listing in [('balance','wallet balance','WalletBalance',False),('ledger','wallet ledger entries','WalletLedgerEntry',True),('credit-lots','wallet credit lots','WalletCreditLot',True),('holds','wallet holds','WalletHold',True)]:
        add('GET','/v1/wallets/{id}/'+suffix,('List ' if listing else 'Retrieve ')+title,name,'wallets:read',
            'Read a consistent wallet snapshot. Pending funding is excluded from usable credits. Paid credits fund AMLOK products and are refundable only after final agreement cancellation and reconciliation. remaining_paid_credits includes paid principal held for unresolved activity; it is not an on-demand withdrawal balance. Ledger and funding lineage are immutable.',
            is_list=listing,query=([q('sequence_after','integer','Read entries after this exclusive wallet sequence.',None,minimum=0)] if suffix=='ledger' else None))
    add('POST','/v1/wallet-sessions','Create wallet payment session','WalletSession','wallets:funding','Create a hosted funding-method or cancellation-refund destination verification session. The return URL must be pre-allowlisted. Never send raw bank credentials or card data to this API. A browser redirect does not prove verification.','CreateWalletSession',{'purpose':'payout_destination','return_url':'https://client.example.com/wallet/return'})
    reads('/v1/wallet-payment-methods','wallet payment methods','WalletPaymentMethod','wallets:read','Only verified methods with the required capability and the same legal owner can fund or receive wallet funds.')
    disabled={**E['WalletPaymentMethod'],'status':'disabled','record_version':2}
    add('POST','/v1/wallet-payment-methods/{id}/disable','Disable wallet payment method','WalletPaymentMethod','wallets:funding','Disable future use. Reject while an active mandate or pending movement requires the method.','WalletReason',{'reason':'Replace bank account.'},example_override=disabled)
    add('POST','/v1/wallet-top-ups','Create wallet top-up','WalletTopUp','wallets:funding','Initiate a payment using an authorized funding method. Pending incoming funds are unavailable. Credit once on confirmed settlement. Origin, disputes and refund capacity follow the funding lot.','CreateWalletTopUp',topup_req)
    reads('/v1/wallet-top-ups','wallet top-ups','WalletTopUp','wallets:read','Read funding status. A failed or reversed payment is not spendable. Never retry an unknown payment with a new business reference.',wallet_filter+reference_filter)
    add('POST','/v1/wallet-top-ups/{id}/cancel','Cancel wallet top-up','WalletTopUp','wallets:funding','Cancel an unsettled funding attempt only before irreversible processor submission. Once settled, the credits remain for product usage and can only be refunded through final agreement cancellation. A failed or reversed funding payment is reconciled without treating it as a customer withdrawal.','WalletReason',{'reason':'Funding no longer needed.'},example_override={**E['WalletTopUp'],'status':'cancelled','record_version':2})
    add('GET','/v1/wallets/{id}/auto-top-up','Retrieve automatic top-up policy','WalletAutoTopUp','wallets:read','Read the authorized threshold, amount, monthly cap and funding mandate.')
    add('PATCH','/v1/wallets/{id}/auto-top-up','Update automatic top-up policy','WalletAutoTopUp','wallets:funding','Replace the policy with a current ETag and an institution-approved authorization. Amount cannot exceed cap. One pending automatic attempt per wallet; failed attempts do not loop indefinitely. The confirmed agreement end date disables automatic funding and new usage. Changing funding_method_id and top_up_amount updates future automatic attempts, within the cap and current authorization; it does not modify already submitted payments.','UpdateWalletAutoTopUp',auto_values)
    add('POST','/v1/wallet-quotes','Create wallet movement quote','WalletQuote','wallets:read','Quote the full remaining paid balance for a final-cancellation refund. Require a cancellation belonging to the same agreement, institution and wallet, status refund_pending, an effective date at or before now, completed reconciliation, a final statement, and resolved usage holds and funding attempts. Otherwise return 409 cancellation_not_final. The server computes the amount and allocations across original funding sources; client amounts and partial cash-outs are rejected. Quotes bind cancellation, final statement revision, wallet version and destinations. No funds are reserved. Recheck every condition atomically on refund submission. For a definitive failed or returned refund, supply refund_id and quote only its still-unpaid balance; unresolved rail outcomes cannot be requoted for retry.','CreateWalletQuote',quote_values)
    add('GET','/v1/wallet-quotes/{id}','Retrieve wallet movement quote','WalletQuote','wallets:read','Read the final-cancellation refund amount, funding allocations, final statement revision and expiry. A quote does not authorize an active-agreement cash-out.')
    refund_desc='Return the full reconciled remaining paid balance only after final agreement cancellation. Require a valid cancellation-refund quote; recheck its cancellation state, effective date, statement revision, wallet version, verified same-owner destinations and settled funding. Reserve the complete unpaid balance atomically, with no wallet deduction for refund fees. One refund obligation exists per cancellation and wallet, across all funding sources; a duplicate request returns the existing refund or 409 refund_already_in_progress. No caller-selected partial amount, discretionary eligibility rejection, active-agreement refund, withdrawal or transfer is supported. Delivery approval validates instructions and cannot waive the obligation to refund. AMLOK owes the remaining balance on final cancellation even if the client does not call this endpoint.'
    add('POST','/v1/wallet-refunds','Create wallet refund','WalletRefund','wallets:refund',refund_desc,'CreateWalletMovement',{'quote_id':'wallet_quote_refund','client_reference':'cancellation-refund-1001'})
    reads('/v1/wallet-refunds','wallet refunds','WalletRefund','wallets:read',refund_desc,reference_filter)
    add('POST','/v1/wallet-refunds/{id}/cancel','Cancel wallet refund','WalletRefund','wallets:refund','Stop only a cancellable delivery attempt before rail submission. This does not cancel the agreement cancellation or forgive the remaining refund obligation. Confirm no funds left before releasing reservations. Resolve delivery instructions and retry the same refund; never create a second refund for the same balance.',
        'WalletReason',{'reason':'Correct refund delivery instructions.'},example_override={**E['WalletRefund'],'status':'cancelled','hold_id':None,'approval_id':None,'cancellable':False,'record_version':2})
    add('POST','/v1/wallet-refunds/{id}/retry','Retry wallet refund','WalletRefund','wallets:refund','Resume the same final-cancellation refund after a definitive failed, cancelled, or returned delivery. Require If-Match and a fresh quote bound to this refund_id and the reconciled unpaid balance. All earlier payouts must have known outcomes; otherwise return 409 refund_not_retryable. Never resend already-paid principal. A changed destination must be verified and may require renewed delivery approval. A distinct business reference identifies the retry, while the refund obligation and funding lineage remain unchanged.',
        'CreateWalletMovement',{'quote_id':'wallet_quote_retry','client_reference':'cancellation-refund-retry-1001'},example_override={**E['WalletRefund'],'quote_id':'wallet_quote_retry','record_version':3})
    reads('/v1/wallet-payouts','wallet payouts','WalletPayout','wallets:read','Track delivery of final-cancellation refunds only, including allocations to original funding sources or an approved verified same-owner fallback. This namespace is separate from provider payment /v1/payouts. A return restores the returned principal once to the closed or closing wallet, remains owed under the same cancellation, and cannot fund new services.')
    reads('/v1/wallet-approvals','wallet approvals','WalletApproval','wallets:approve','Read approvals assigned to the authenticated actor; tenant access alone is insufficient.')
    add('POST','/v1/wallet-approvals/{id}/decision','Decide wallet approval','WalletApproval','wallets:approve','An independent authorized actor approves or rejects the exact movement version. The initiator cannot self-approve. Expired, changed or already decided requests fail. Execution rechecks balance, holds and destination. This authorizes refund delivery instructions only. Rejecting or expiring an instruction does not forfeit the balance or cancel the refund obligation; no approval can bypass the final-cancellation requirement.',
        'DecideWalletApproval',{'decision':'approve','reason':'Verified payout instruction.'},
        example_override={**E['WalletApproval'],'status':'approved','decided_by':'actor_reviewer','decision_at':now,'record_version':2})
    add('POST','/v1/agreement-cancellation-quotes','Create agreement cancellation quote','AgreementCancellationQuote','billing:manage','Estimate unused paid credits, final usage and the full remaining-balance refund at the requested cancellation date. Pending usage holds are included in estimated final usage once, not deducted twice. Remaining agreement obligations are disclosed separately and do not become wallet deductions. A quote neither cancels services nor pays funds; reconciliation establishes the final amount.','CreateCancellationQuote',{'agreement_id':'agr_example','requested_effective_at':'2027-10-01T00:00:00Z'})
    add('POST','/v1/agreement-cancellations','Create agreement cancellation','AgreementCancellation','billing:manage','Request final agreement cancellation using the quoted agreement version and signed notice terms. Confirmation establishes the effective date. At that date, stop new usage and automatic top-ups; reconcile all incurred product usage and in-flight funding, then set refund_pending and return the entire remaining paid balance. The cancellation links its final statement, refund amount and refund records. No withdrawal request is needed to establish the refund obligation.','CreateAgreementCancellation',{'quote_id':'agreement_cancellation_quote_example','reason':'Do not renew this agreement.','client_reference':'cancellation-1001'})
    reads('/v1/agreement-cancellations','agreement cancellations','AgreementCancellation','billing:read','Track cancellation through requested, scheduled, effective, reconciling, refund_pending and completed. refund_pending requires a final statement and reconciled_at; completed requires every remaining paid balance returned, including late settled funding and returned payouts, or a zero final balance. Remaining term obligations are separately disclosed and are not deducted from the wallet refund.',reference_filter)
    add('POST','/v1/agreement-cancellations/{id}/cancel','Withdraw agreement cancellation','AgreementCancellation','billing:manage','Withdraw a cancellation request before its effective boundary, subject to agreement terms. This does not reverse already stopped services or completed payments.','WalletReason',{'reason':'Continue the agreement.'},example_override={**E['AgreementCancellation'],'status':'withdrawn','record_version':2})
    add('POST','/v1/wallet-closures','Create wallet closure','WalletClosure','wallets:write','Close only after final agreement cancellation, full remaining paid-balance refund and resolution of holds and in-flight funding. Require the same cancellation_id and legal owner. Zero-cost promotional credits are retired without cash payment. Closure cannot be used as an alternative cash-out path, does not delete audit records, and never re-enables funding or usage. A later payout return reopens refund reconciliation, not service access.','CreateWalletClosure',{'wallet_id':'wal_example','cancellation_id':'cancellation_final_example','reason':'Final cancellation refund completed.','client_reference':'closure-1001'})
    reads('/v1/wallet-closures','wallet closures','WalletClosure','wallets:read','Read closure blockers and final statement. A blocked closure does not forfeit funds.',wallet_filter+reference_filter)
    add('POST','/v1/wallet-closures/{id}/cancel','Withdraw wallet closure','WalletClosure','wallets:write','Withdraw a closure before completion. Does not automatically re-enable an automatic funding mandate.','WalletReason',{'reason':'Keep this wallet.'},example_override={**E['WalletClosure'],'status':'withdrawn','record_version':2})
    S['WebhookEvent']['properties']['type']['enum'] += [e[0] for e in WALLET_EVENTS]
    g['REFINEMENTS'] += [
        'Wallet policy revised by AMLOK: prepaid funds are consumed only by product usage and refunded in full only after final agreement cancellation. No on-demand withdrawals or wallet transfers. This is a documentation contract, not an executable wallet backend.',
        'Wallet mutations preserve durable business references beyond 24-hour request idempotency; quotes bind movement terms and submission reserves eligible funds atomically.',
        'CAD is the documented settlement currency. Cancellation refunds are server-calculated from paid principal after final usage, with no wallet fees or deduction of remaining term obligations. Promotional benefits have no cash principal. Payment reversals and corrections are system reconciliation, never client cash-out capabilities.',
        'Money movement enablement depends on institution onboarding, configured payment rails, legal-role and custody disclosures, and approval policy. Examples do not establish a production provider or regulatory status.',
    ]
    write('data/wallet-api-index.json',dump(operations))
    write('data/wallet-events.json',dump([{'event':a,'resource':b,'trigger':c} for a,b,c in WALLET_EVENTS]))
    return operations

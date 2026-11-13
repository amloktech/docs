"""Institution-facing completeness: data access, submitted inputs and reconciliation.

This extends the one public contract, not a second API or an implementation of
normalization, underwriting, payment collection, or provider connectors.
"""
from copy import deepcopy


def extend_schemas(s):
    from product_api_review import obj, ref, text, enum, array, nullable
    ident = text('Opaque ID within the authorized workspace and environment.')
    ids = array(ident, uniqueItems=True)
    stamp = text(format='date-time')
    amount = text(pattern=r'^(?:0|[1-9][0-9]*)\.[0-9]{2}$')
    signed = text(pattern=r'^-?(?:0|[1-9][0-9]*)\.[0-9]{2}$')
    # Keep the full existing normalized resource dictionary, including enrichment
    # fields, extensions, field provenance, missing-field reasons and units.
    s['DataRecord'] = obj({
        'id': ident, 'borrower_id': ident, 'connection_id': nullable(ident),
        'integration_id': nullable(ident), 'resource_type': text(),
        'resource_id': ident, 'record_version': {'type':'integer','minimum':1},
        'ingested_at': stamp, 'source_as_of': nullable(stamp),
        'access': enum('available','restricted','deleted'), 'access_reason': nullable(text()),
        'normalized': deepcopy(s['Evidence']['properties']['normalized']),
        'source_payload': obj({'status':enum('available','not_retained','restricted','not_applicable'),
            'value':nullable({'type':'object','additionalProperties':True,'description':'Authorized provider-native business fields. Never credentials, cookies, tokens or unrelated borrower data. Field meanings are provider-specific; consult the provider documentation in Data Lookup.'}),
            'reason':nullable(text())}, allOf=[{'if':{'properties':{'status':{'const':'available'}}},'then':{'properties':{'value':{'type':'object'},'reason':{'type':'null'}}},'else':{'properties':{'value':{'type':'null'},'reason':text()}}}]),
        'document_ids': ids,
    }, description='One immutable version of a collected or derived record, available independently of underwriting. resource_id identifies its logical record; id identifies this exact version. Normalized object, id and record_version must match resource_type, resource_id and record_version. Available records include all authorized populated fields, enrichment fields and provenance. Restricted/deleted records retain only permitted metadata.', allOf=[
        {'if':{'properties':{'access':{'enum':['restricted','deleted']}}},'then':{'properties':{'normalized':{'type':'null'},'document_ids':{'maxItems':0},'access_reason':text(),'source_payload':{'properties':{'status':{'const':'restricted'},'value':{'type':'null'},'reason':text()}}}}},
        {'if':{'properties':{'access':{'const':'available'}}},'then':{'properties':{'access_reason':{'type':'null'}}}},
    ])
    s['DataPage'] = obj({'next_cursor':nullable(text()),'has_more':{'type':'boolean'},'snapshot_id':ident,'as_of':stamp,
        'changes_cursor':text('Atomic change-feed position at snapshot creation, bound to the same borrower, filters and authorization. Save it; consume changes only after completing the snapshot pages.')})
    s['DataChange'] = obj({'id':ident,'type':enum('upsert','removed','access_changed'),'occurred_at':stamp,
        'record_id':nullable(ident),'borrower_id':ident,'resource_id':ident,'resource_type':text(),
        'record_version':{'type':'integer','minimum':1},'reason':nullable(text())},
        description='Ordered change notification for a logical record. upsert references an immutable DataRecord version. Removal and access changes can expose metadata only; purge affected local copies as required by the authorization/retention policy. Reading a feed never restores access.',
        allOf=[{'if':{'properties':{'type':{'const':'upsert'}}},'then':{'properties':{'record_id':ident}},'else':{'properties':{'reason':text()}}}])
    s['DataChangePage'] = obj({'next_cursor':nullable(text()),'has_more':{'type':'boolean'},'resume_cursor':text('Commit after applying the full batch. Present even for an empty page; pass as cursor for the next request.')})
    # The accepted request remains inspectable before any risk package exists.
    s['Origination']['properties'].update({'submitted_request':ref('CreateOrigination'),
        'document_ids':ids})
    s['Origination']['required'] += ['submitted_request','document_ids']
    s['Origination']['properties']['document_ids']['description']='Accepted primary-borrower document associations, including initially submitted files and later files accepted while the origination is open. Related-party files appear separately in participants[].document_ids. A completed risk package freezes its own document and evidence references; later borrower-only uploads do not change them.'
    s['CreateOrigination']['properties']['document_ids']=deepcopy(s['CreateOrigination']['properties']['document_ids'])
    s['CreateOrigination']['properties']['document_ids']['description']='Available borrower-context documents owned by the primary borrower. Upload first, wait until each Document.status is available, then include its ID here. Processing or rejected files return 422; a borrower-only upload is not associated automatically. Related-party files belong in participants[].document_ids.'
    s['RiskPackage']['properties']['document_ids']=deepcopy(ids)
    s['RiskPackage']['properties']['document_ids']['description']='Primary-borrower document IDs frozen when this risk package was published. Related-party files are preserved in participants[].document_ids and the evidence set. Later uploads do not change this historical result; current authorization still governs access.'
    s['RiskPackage']['required'].append('document_ids')
    s['Document']['properties'].update({'created_at':stamp,'document_type':text(),
        'origination_id':nullable(ident),'requirement_id':nullable(ident),
        'origin':enum('institution_upload','borrower_upload','integration','amlok_generated')})
    s['Document']['required'] += ['created_at','document_type','origination_id','requirement_id','origin']
    s['UploadDocument']['allOf'].append({'if':{'required':['requirement_id']},'then':{'required':['origination_id']}})
    s['Document']['properties']['origination_id']['description']='Origination explicitly supplied when this file was uploaded; null for an initial borrower-only upload, even if the file is later referenced by one or more assessments. Use GET /v1/documents?origination_id=... to resolve assessment associations, including primary and participant documents.'
    s['Document']['properties']['requirement_id']['description']='Document requirement explicitly supplied at upload, or null. Its presence records the upload target; inspection must succeed before the requirement is resolved.'
    s['UploadDocument']['properties']['origination_id']=deepcopy(s['UploadDocument']['properties']['origination_id'])
    s['UploadDocument']['properties']['origination_id']['description']='Optional collecting/requires_action origination to associate with this upload. Omit for initial borrower files and reference their IDs after they become available. Later uploads to other states return 409.'
    s['UploadDocument']['properties']['requirement_id']=deepcopy(s['UploadDocument']['properties']['requirement_id'])
    s['UploadDocument']['properties']['requirement_id']['description']='Open document requirement this file satisfies. Requires origination_id and the required borrower, document type and accepted MIME type. Successful inspection resolves the requirement; 202 alone does not.'
    s['UploadDocument']['description']='Create an immutable file record. 202 accepts the upload for asynchronous inspection and returns status processing; it does not confirm file readiness or use in an assessment. Poll GET /v1/documents/{id} until available before referencing an initial file. A later upload can name a collecting/requires_action origination and open requirement; accepted inspection adds its document association. Other origination states return 409. Borrower-only uploads never attach automatically or change completed assessments.'
    s['EvidenceSummary']['properties']['data_record_id']=nullable(ident)
    s['EvidenceSummary']['required'].append('data_record_id')
    s['EvidenceSummary']['properties']['data_record_id']['description']='Exact DataRecord version used, when this evidence originated in the data API. null for standalone files/reports. Evidence access never implicitly grants data:read.'
    s['EmbeddingSession']['properties'].update({'embedding_version_id':ident,'purpose':enum('connect','reauthorize'),'origination_id':nullable(ident)})
    s['EmbeddingSession']['required'] += ['embedding_version_id','purpose','origination_id']
    s['CreateEmbeddingSession']['description']='Launch an already published console-configured Hub for this borrower. Enabled integrations and categories come from embedding_version_id and cannot be overridden here. The backend verifies its own borrower association before creating a session; only the short-lived launch URL reaches the browser.'
    s['Connection']['properties']['data_status']=enum('not_started','collecting','ready','partial','failed')
    s['Connection']['required'].append('data_status')
    s['Connection']['properties']['data_status']['description']='Availability of collected data, independent from provider authorization status. ready does not mean an underwriting has completed; inspect source_as_of and coverage.'
    s['BillingPayment'] = obj({'id':ident,'snapshot_id':ident,'created_at':stamp,'updated_at':stamp,
        'status':enum('pending','processing','succeeded','failed','cancelled','partially_refunded','refunded','returned'),
        'purpose':enum('initial_funding','renewal','automatic_top_up','manual_top_up'),
        'amount':amount,'currency':{'const':'CAD'},'credited_amount':amount,'refunded_amount':amount,
        'method':obj({'type':enum('card','ach','bank_transfer'),'label':text('Masked display label only; no card number, routing number, bank credentials or payment token.')}),
        'external_reference':nullable(text()),'settled_at':nullable(stamp),'failure_reason':nullable(text()),'transaction_ids':ids},
        description='Read-only payment/funding state as of snapshot_id. Pending, processing, failed and cancelled attempts do not increase credits. credited_amount is cumulative credit actually posted for this payment; later returns/refunds are linked negative transactions, not a rewrite of funding history.',
        allOf=[{'if':{'properties':{'status':{'enum':['pending','processing','failed','cancelled']}}},'then':{'properties':{'credited_amount':{'const':'0.00'},'settled_at':{'type':'null'}}}},
               {'if':{'properties':{'status':{'const':'failed'}}},'then':{'properties':{'failure_reason':text()}}}])
    s['BillingUsage'] = obj({'id':ident,'snapshot_id':ident,'borrower_id':ident,'product':enum('insights','signal'),
        'origination_id':nullable(ident),'monitor_ids':ids,'risk_package_ids':ids,
        'period':ref('Window'),'charged_at':stamp,'tier':enum('standard','advanced','complex'),
        'quantity':{'type':'integer','minimum':1},'unit_rate':amount,'amount':amount,'currency':{'const':'CAD'},
        'rate_card_id':ident,'rate_version':text(),'transaction_id':ident,
        'workload':obj({'bank_accounts':{'type':'integer','minimum':0},'business_systems':{'type':'integer','minimum':0},'records':{'type':'integer','minimum':0},'record_counting_basis':enum('per_underwriting','new_records_per_month')}),
    }, description='Immutable charge explanation. Amount is the positive cost; the linked ledger usage transaction is negative. Rates are the actual historical agreed rates, never current estimates. Signal is one borrower/workspace/month across all monitored deals; included reassessments add no Insights charge.',
        allOf=[{'if':{'properties':{'product':{'const':'insights'}}},'then':{'properties':{'origination_id':ident,'workload':{'properties':{'record_counting_basis':{'const':'per_underwriting'}}}}},'else':{'properties':{'origination_id':{'type':'null'},'workload':{'properties':{'record_counting_basis':{'const':'new_records_per_month'}}}}}}])
    s['BillingTransaction']['properties'].update({'payment_id':nullable(ident),'borrower_id':nullable(ident),
        'balance_after':amount,'sequence':{'type':'integer','minimum':1},
        'funding_type':nullable(enum('paid','promotional'))})
    s['BillingTransaction']['required'] += ['payment_id','borrower_id','balance_after','sequence','funding_type']
    s['BillingTransaction']['description']='Immutable signed CAD wallet movement. Funding is positive, usage and final refunds negative, adjustments signed. sequence gives total posting order; balance_after is the historical balance after this entry. Promotional funding has no payment; paid funding links payment_id. related_transaction_id links corrections/reversals.'
    s['BillingTransaction']['allOf']=[
        {'if':{'properties':{'kind':{'const':'usage'}}},'then':{'properties':{'usage_id':ident,'product':enum('insights','signal'),'amount':text(pattern=r'^-[0-9]+\.[0-9]{2}$')}}},
        {'if':{'properties':{'kind':{'const':'funding'}}},'then':{'properties':{'funding_type':enum('paid','promotional'),'amount':amount}},'else':{'properties':{'funding_type':{'type':'null'}}}},
        {'if':{'properties':{'funding_type':{'const':'paid'}}},'then':{'properties':{'payment_id':ident}}},
        {'if':{'properties':{'funding_type':{'const':'promotional'}}},'then':{'properties':{'payment_id':{'type':'null'}}}},
    ]
    totals={'paid_funding_credits':amount,'promotional_credits':amount,'adjustment_credits':signed,'refunded_credits':amount}
    s['BillingSummary']['properties'].update(totals)
    s['BillingSummary']['required'] += list(totals)
    s['BillingSummary']['description']='Read-only lifetime workspace CAD totals as of one snapshot. available_credits = paid_funding_credits + promotional_credits + adjustment_credits - spent_credits - refunded_credits. Sum posted funding/usage/adjustment/final_refund entries; pending payments are excluded. Corrections use signed adjustments. No reserved credits.'
    s['BillingSummary']['properties']['auto_pay']=obj({'enabled':{'type':'boolean'},'trigger_amount':amount,'top_up_amount':amount}, description='Actual read-only portal configuration. Values do not authorize a payment or expose a payment method. Changes are made in the console.')
    s['BillingSummary']['required'].append('auto_pay')
    # One more export kind, with the same permissions as the source data.
    export=s['CreateExport'];export['properties']['kind']['enum'].append('data')
    export['properties']['data_snapshot_id']=ident
    export['oneOf'].append({'title':'Collected data export','properties':{'kind':{'const':'data'},'format':enum('json','csv')},'required':['data_snapshot_id'],'not':{'anyOf':[{'required':[k]} for k in ['risk_package_id','evidence_set_id','billing_report_type','window']]}})
    for branch in export['oneOf'][:-1]:branch['not']['anyOf'].append({'required':['data_snapshot_id']})
    descriptions = {
        'DataRecord': {'id':'Immutable identifier for this exact collected/enriched version. Use it in getDataRecord.', 'resource_type':'Normalized resource family, such as bank_transaction or invoice; matches normalized.object.', 'resource_id':'Stable logical record ID across successive versions.', 'record_version':'Increasing version of the logical record; a new version has a new DataRecord id.', 'ingested_at':'UTC time this version became available from AMLOK.', 'source_as_of':'UTC source freshness time, null when the provider did not establish it.', 'connection_id':'Borrower connection that supplied this record; null for data derived without a single connection.', 'integration_id':'Source integration identifier; null for data with no single provider.', 'access':'Whether content is currently available, restricted or deleted.', 'access_reason':'Explanation when content cannot be returned; null for available data.', 'document_ids':'Authorized source files or provider reports associated with this record.', 'normalized':'Typed normalized and enriched record including field-level provenance and missing-value reasons; null when unavailable.'},
        'DataChange': {'id':'Stable change notification ID for idempotent processing.', 'type':'upsert supplies a record version; removed and access_changed require reconciliation of a prior local record.', 'record_id':'Exact DataRecord version to fetch; can be null for a removal or access restriction.', 'occurred_at':'UTC time this change was committed to the data feed.', 'reason':'Reason for removal or access change when applicable.'},
        'BillingPayment': {'id':'Funding payment or top-up attempt identifier; not a wallet ledger ID.', 'snapshot_id':'Billing snapshot used for this representation.', 'amount':'Requested payment amount in CAD major units, as a two-decimal string.', 'credited_amount':'Total credits actually posted for this payment before subsequent reversals; zero until credit posting.', 'refunded_amount':'Total payment refunds recorded as of this snapshot, in CAD.', 'status':'Payment lifecycle status; only posted ledger entries change the wallet.', 'purpose':'Initial/renewal contract funding or an automatic/manual top-up.', 'created_at':'UTC time the payment attempt was recorded.', 'updated_at':'UTC time its state most recently changed.', 'settled_at':'UTC settlement time; null before settlement or if payment failed.', 'failure_reason':'Human-readable failure or return explanation, when available.', 'external_reference':'Non-secret reconciliation reference from the payment system.', 'transaction_ids':'Immutable wallet entries for credit posting and subsequent returns/refunds.'},
        'BillingUsage': {'id':'Stable usage charge ID, also referenced by risk-package billing_usage_id.', 'snapshot_id':'Billing snapshot used for this read.', 'product':'Insights underwriting or Signal monitoring; included stages are not separately billed.', 'origination_id':'Charged origination for Insights; null for a Signal monthly charge.', 'monitor_ids':'Monitored deals represented by a combined Signal borrower/month charge.', 'risk_package_ids':'Published results associated with this charge.', 'period':'UTC half-open service interval for this usage.', 'charged_at':'UTC time the charge was posted.', 'tier':'Historical workload tier determining the agreed unit rate.', 'quantity':'Billed units for this immutable charge.', 'unit_rate':'Actual effective CAD unit rate after two-decimal half-up rounding.', 'amount':'Positive CAD cost: quantity times rounded unit_rate, rounded half-up to two decimals.', 'rate_card_id':'Historical agreed rate-card reference.', 'rate_version':'Exact historical pricing version, not the current rate.', 'transaction_id':'Posted negative usage ledger entry for this charge.', 'workload':'Counts used to explain the charged tier, distinct from the billed quantity.'},
        'BillingSummary': {'paid_funding_credits':'Cumulative posted paid funding credits in CAD; excludes pending or failed payments.', 'promotional_credits':'Cumulative posted promotional credits in CAD.', 'adjustment_credits':'Signed sum of posted corrections and adjustments in CAD.', 'refunded_credits':'Cumulative final-refund deductions in CAD, expressed as a positive total.', 'spent_credits':'Cumulative posted usage deductions in CAD, expressed as a positive total.', 'available_credits':'Current spendable CAD credits at the reporting snapshot.'},
        'BillingTransaction': {'payment_id':'Related funding payment or refund source; null when no payment applies.', 'borrower_id':'Borrower charged when applicable; funding is workspace-wide and normally null.', 'balance_after':'Spendable CAD balance immediately after this entry in sequence order.', 'sequence':'Strictly increasing posting order within the workspace wallet.', 'funding_type':'Paid or promotional credit for funding entries; null for other kinds.'},
    }
    for name, fields in descriptions.items():
        for field, description in fields.items():
            s[name]['properties'][field]=deepcopy(s[name]['properties'][field])
            s[name]['properties'][field]['description']=description
    s['Event']['properties']['type']['enum'] += ['data.updated','document.status_changed','billing.payment_updated','billing.transaction_posted']
    return s


def extend_fixtures(f):
    now='2026-11-06T12:00:00Z'
    f['Origination'].update(submitted_request=deepcopy(f['CreateOrigination']),document_ids=[])
    f['RiskPackage']['document_ids']=[]
    f['EmbeddingSession'].update(embedding_version_id='embed_synthetic',purpose='connect',origination_id=None)
    f['Connection']['data_status']='partial'
    f['Document'].update(created_at=now,document_type='financial_statement',origination_id=None,requirement_id=None,origin='institution_upload')
    f['Evidence']['record']['data_record_id']='dr_synthetic_v1'
    f['EvidenceSummary']['data_record_id']='dr_synthetic_v1'
    # Explicit nullable fields avoid fabricating unavailable provider values.
    normalized={'id':'txn_synthetic','object':'bank_transaction','subject_id':'biz_synthetic','created_at':now,'updated_at':now,'observed_at':now,'record_version':1,'source_refs':[], 'data_status':'partial','missing_fields':[],'schema_version':'1.0.0','account_id':'acct_synthetic','direction':'inflow','status':'posted','amount':{'amount':'1250.00','currency':'CAD'},'extensions':{'synthetic_provider':{'original_description':'SYNTHETIC CUSTOMER PAYMENT'}}}
    f['DataRecord']={'id':'dr_synthetic_v1','borrower_id':'bor_synthetic','connection_id':'con_synthetic','integration_id':'bank_synthetic','resource_type':'bank_transaction','resource_id':'txn_synthetic','record_version':1,'ingested_at':now,'source_as_of':now,'access':'available','access_reason':None,'normalized':normalized,'source_payload':{'status':'available','value':{'description':'SYNTHETIC CUSTOMER PAYMENT','amount':'1250.00','currency':'CAD'},'reason':None},'document_ids':[]}
    f['DataChange']={'id':'change_synthetic','type':'upsert','occurred_at':now,'record_id':'dr_synthetic_v1','borrower_id':'bor_synthetic','resource_id':'txn_synthetic','resource_type':'bank_transaction','record_version':1,'reason':None}
    f['BillingPayment']={'id':'pay_synthetic','snapshot_id':'snap_synthetic','created_at':now,'updated_at':now,'status':'succeeded','purpose':'manual_top_up','amount':'5000.00','currency':'CAD','credited_amount':'5000.00','refunded_amount':'0.00','method':{'type':'card','label':'Visa ending 4242'},'external_reference':'PAY-SYNTHETIC-0042','settled_at':now,'failure_reason':None,'transaction_ids':['txn_funding_synthetic']}
    f['BillingUsage']={'id':'usage_synthetic','snapshot_id':'snap_synthetic','borrower_id':'bor_synthetic','product':'insights','origination_id':'orgn_synthetic','monitor_ids':[],'risk_package_ids':['rp_synthetic'],'period':{'start':'2026-11-06T00:00:00Z','end':'2026-11-07T00:00:00Z'},'charged_at':now,'tier':'standard','quantity':1,'unit_rate':'40.00','amount':'40.00','currency':'CAD','rate_card_id':'rate_synthetic','rate_version':'synthetic-1','transaction_id':'txn_usage_synthetic','workload':{'bank_accounts':1,'business_systems':2,'records':1500,'record_counting_basis':'per_underwriting'}}
    f['BillingTransaction'].update(payment_id=None,borrower_id='bor_synthetic',balance_after='4935.00',sequence=3,funding_type=None)
    f['BillingSummary'].update(paid_funding_credits='5000.00',promotional_credits='0.00',adjustment_credits='0.00',refunded_credits='0.00',auto_pay={'enabled':False,'trigger_amount':'200.00','top_up_amount':'500.00'})
    return f


def extend_operations(add):
    add('listDataRecords','GET','data/records','Data','DataRecord',many=True,scope='data:read')
    add('getDataRecord','GET','data/records/{id}','Data','DataRecord',scope='data:read')
    add('listDataChanges','GET','data/changes','Data','DataChange',many=True,scope='data:read')
    add('listDocuments','GET','documents','Evidence','Document',many=True,scope='evidence:read')
    add('getBillingTransaction','GET','billing/transactions/{id}','Billing','BillingTransaction')
    add('listBillingPayments','GET','billing/payments','Billing','BillingPayment',many=True)
    add('getBillingPayment','GET','billing/payments/{id}','Billing','BillingPayment')
    add('listBillingUsage','GET','billing/usage','Billing','BillingUsage',many=True)
    add('getBillingUsage','GET','billing/usage/{id}','Billing','BillingUsage')


PURPOSE = {
    'listDataRecords':'Read all authorized collected and enriched records for a borrower, independently of an origination or risk package. The first page creates a stable snapshot and an atomic changes_cursor. No page truncation; follow next_cursor until has_more is false.',
    'getDataRecord':'Read an exact immutable data-record version with normalized fields, enrichment fields, provenance, authorized source payload and file references. Never silently replace this version with newer data.',
    'listDataChanges':'Resume from the changes_cursor returned by a completed data snapshot, then persist resume_cursor after applying each batch. Includes upserts, source removals and access changes; expired or mismatched cursors fail explicitly.',
    'listDocuments':'Discover institution uploads, borrower uploads, integration files and generated documents. origination_id resolves primary-borrower and participant document associations plus files explicitly uploaded for that origination, including processing or rejected uploads. It does not include unrelated later borrower uploads or prove a file was used in a completed result. Other filters apply together, and current source authorization still applies. Follow next_cursor for the full snapshot; download available files through the authorized document endpoint.',
    'getBillingTransaction':'Retrieve one immutable wallet movement, its historical balance and links to payment or product usage.',
    'listBillingPayments':'Read top-up and contract-funding payment attempts, including pending, failed, settled, returned and refunded states. Pending or failed payments are not spendable credits.',
    'getBillingPayment':'Retrieve one payment and the wallet entries created by its settlement, return or refund. Uses the requested billing snapshot when supplied.',
    'listBillingUsage':'Read what was charged, for which borrower and product, with historical rate, tier, workload and links to the wallet transaction and assessment. Signal combines a borrower across deals once per workspace/month.',
    'getBillingUsage':'Retrieve the immutable calculation and product references explaining one usage charge. Historical rates are preserved; retries and included Signal reassessments are not duplicate charges.',
    'getOrigination':'Retrieve an underwriting request, its immutable submitted application, product and policy versions, document associations, requirements, status and risk-package reference, including before processing completes.',
    'getEmbeddingSession':'Inspect the borrower-specific execution of a Hub configured in the console. Session completion confirms connection setup, not ingestion readiness or underwriting completion.',
    'listConnections':'Inspect borrower-authorized integrations, connection status, ingestion readiness, freshness and coverage. The Hub performs authorization; this endpoint exposes its result without configuring integrations.',
    'getConnection':'Inspect one borrower connection and its collection status. Use a Hub reauthorization session when borrower action is required; no provider credentials are returned.',
}


def extend_parameters(op, params, param):
    oid=op['id']
    if oid=='listDataRecords':
        params[:] = [p for p in params if p['name']!='borrower_id']
        params.append(param('borrower_id',required=True,description='Borrower whose authorized data is read; required on every page.'))
        for name in ['connection_id','integration_id','resource_type']:
            params.append(param(name))
    if oid=='listDataChanges':
        params[:] = [p for p in params if p['name']!='borrower_id']
        next(p for p in params if p['name']=='cursor').update(required=True,description='Use data snapshot changes_cursor, then change-feed resume_cursor. Bound filters and borrower are encoded in the cursor; no arbitrary time or filter reset.')
    filters={
        'listDocuments':['origination_id','context','document_type','status'],
        'listBillingPayments':['status','purpose','created_from','created_to','snapshot_id'],
        'listBillingUsage':['product','origination_id','monitor_id','charged_from','charged_to','snapshot_id'],
        'listBillingTransactions':['kind','product','payment_id','usage_id','posted_from','posted_to'],
        'getBillingPayment':['snapshot_id'],'getBillingUsage':['snapshot_id'],'getBillingTransaction':['snapshot_id'],
    }
    for name in filters.get(oid,[]):
        schema={'type':'string','format':'date-time'} if name.endswith(('_from','_to')) else None
        params.append(param(name,schema=schema,description=(name.replace('_',' ')+'. UTC ranges are inclusive from and exclusive to; reject to <= from.' if schema else name.replace('_',' '))))
    choices={'product':['insights','signal'],'kind':['funding','usage','adjustment','final_refund'],'context':['borrower','lending_product','risk_policy']}
    if oid=='listBillingPayments':choices.update(status=['pending','processing','succeeded','failed','cancelled','partially_refunded','refunded','returned'],purpose=['initial_funding','renewal','automatic_top_up','manual_top_up'])
    if oid=='listDocuments':
        choices['status']=['processing','available','rejected','restricted']
        next(p for p in params if p['name']=='origination_id')['description']='Files associated with this origination through its primary or participant document IDs, or explicitly targeted at upload. Associations are fixed at the listing snapshot; current source authorization is rechecked. Excludes other borrower-only uploads. A missing origination or one outside this workspace/environment returns 404. Combined borrower_id, context, type and status filters narrow these results.'
    for p in params:
        if p['name'] in choices:p['schema']={'type':'string','enum':choices[p['name']]}
    if oid=='listBillingPayments':params[:] = [p for p in params if p['name']!='borrower_id']

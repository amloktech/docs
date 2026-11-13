"""Typed underwriting result, example builders and cross-field acceptance rules."""
from copy import deepcopy
from decimal import Decimal
from risk_package_catalog import catalog, VERSION

REASONS = ['missing_source','insufficient_history','stale_source','incomplete_coverage','restricted_source','invalid_denominator','conflicting_evidence','unsupported_scope','not_applicable','not_evaluated','no_comparable_baseline','model_not_eligible']

def extend_schemas(s):
 from product_api_review import obj, text, enum, array, ref, nullable
 c=catalog(); decimal=text(pattern=r'^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$'); ids=array(text(),uniqueItems=True); currency=text(pattern='^[A-Z]{3}$'); stamp=text(format='date-time'); integer={'type':'integer','minimum':0}
 def add(name,props):
  s[name]['properties'].update(deepcopy(props));s[name]['required']+=list(props)
 def section(name,item,description):
  s[name]=obj({'status':enum('available','partial','unavailable','not_applicable'),'reason':nullable(text()),'evidence_ids':ids,'items':array(ref(item))},description=description,allOf=[{'if':{'properties':{'status':{'enum':['unavailable','not_applicable']}}},'then':{'properties':{'reason':text(),'items':{'maxItems':0}}}},{'if':{'properties':{'status':{'const':'available'}}},'then':{'properties':{'reason':{'type':'null'}}}},{'if':{'properties':{'status':{'const':'partial'}}},'then':{'properties':{'reason':text(),'items':{'minItems':1}}}}])
 s['EvidenceLocation']=obj({'evidence_id':text(),'field_path':nullable(text('RFC 6901 JSON pointer into the frozen evidence record.')),'document_id':nullable(text()),'page':nullable({'type':'integer','minimum':1}),'quote':nullable(text('Short permitted excerpt, with sensitive information minimized.'))},description='Evidence belongs to this package evidence_set. Page is one-based; document_id is required whenever page is present.',allOf=[{'if':{'properties':{'page':{'type':'integer'}}},'then':{'properties':{'document_id':text()}}}])
 s['CalculationInput']=obj({'name':text(),'value':nullable(decimal),'unit':text(),'currency':nullable(currency),'basis':enum('observed','declared','derived','estimated'),'evidence':array(ref('EvidenceLocation'),minItems=1)},description='A numeric input to the exact calculation. Declared and estimated inputs remain distinguishable from observed values. Null input values cannot support an available metric.')
 s['MetricObservation']=obj({'window':ref('Window'),'status':enum('available','unavailable'),'value':nullable(decimal),'reason':nullable(text()),'evidence_ids':ids},allOf=[{'if':{'properties':{'status':{'const':'available'}}},'then':{'properties':{'value':decimal,'reason':{'type':'null'},'evidence_ids':{'minItems':1}}},'else':{'properties':{'value':{'type':'null'},'reason':text()}}}])
 add('Metric',{'analysis_basis':enum('historical','pro_forma','scenario'),'assumptions':array(text()),'definition_version':{'const':VERSION},'currency':nullable(currency),'as_of':stamp,'basis':enum('observed','declared','derived','estimated'),'reason_code':nullable(enum(*REASONS)),'inputs':array(ref('CalculationInput')),'coverage':obj({'observed_days':integer,'expected_days':integer,'scope_note':text()}),'series':array(ref('MetricObservation'))})
 s['Metric']['properties']['key']=enum(*[m['key'] for m in c['metrics']])
 s['Metric']['properties']['value']['description']='Exact decimal string. Ratio 0.25 means 25%; missing is null, never zero. No arbitrary composite credit score.'
 s['Metric']['properties']['series']['description']='Ordered historical observations using this metric definition, unit, currency and scope. Missing periods are explicit unavailable observations; no interpolation without an estimated basis.'
 s['Metric']['allOf'] += [
 {'if':{'properties':{'analysis_basis':{'enum':['pro_forma','scenario']}}},'then':{'properties':{'assumptions':{'minItems':1}}}},
 {'if':{'properties':{'unit':{'const':'currency'}}},'then':{'properties':{'currency':currency}},'else':{'properties':{'currency':{'type':'null'}}}},
 {'if':{'properties':{'status':{'const':'available'}}},'then':{'properties':{'reason_code':{'type':'null'},'inputs':{'minItems':1},'evidence_ids':{'minItems':1}}},'else':{'properties':{'reason_code':enum(*REASONS)}}},
 *[{'if':{'properties':{'key':{'const':m['key']}}},'then':{'properties':{'unit':{'const':m['unit']},'calculation_version':{'const':m['calculation_version']}}}} for m in c['metrics']]]
 s['Dimension']['properties']['key']=enum(*[d['key'] for d in c['dimensions']])
 s['Dimension']['properties']['metrics']['description']='Every catalog metric assigned to this dimension exactly once, including unavailable and not-applicable entries. Segment analyses are in analyses; do not silently drop metrics.'
 s['Dimension']['allOf']=[]
 for d in c['dimensions']:
  permitted=[m['key'] for m in c['metrics'] if m['dimension_key']==d['key']]
  condition={'if':{'properties':{'key':{'const':d['key']}}},'then':{'properties':{'metrics':{'items':{'properties':{'key':{'enum':permitted}}}}}}}
  s['Dimension']['allOf'].append(condition)
 s['RiskPackage']['properties']['dimensions'].update(minItems=len(c['dimensions']),maxItems=len(c['dimensions']))
 s['RiskPackage']['properties']['dimensions']['description']='All 24 dimension families, exactly once. Available means every applicable metric is available; partial means some are available; unavailable means none can be calculated; not_applicable means no metric applies.'
 s['RiskMetricDefinition']=obj({'key':text(),'dimension_key':text(),'label':text(),'description':text(),'unit':text(),'formula':text(),'required_inputs':array(text(),minItems=1),'eligibility':text(),'borrower_types':array(enum('business','person'),minItems=1),'source_families':array(text()),'definition_version':{'const':VERSION},'calculation_version':text(),'window_rule':text(),'unavailable_rule':text(),'interpretation':text()})
 # Existing configuration.dimensions is the scalar policy-key registry, not dimension-family names.
 s['Configuration']['properties']['dimensions']=array(ref('RiskMetricDefinition'),description='Entitled scalar metric definitions accepted by PolicyRule.dimension_key. Discovery can be a subset of the public catalog; unsupported or inapplicable policy keys are rejected. No family label is a scalar policy key.')
 add('Configuration',{'risk_catalog_version':{'const':VERSION}})
 s['PolicyRule']['properties']['dimension_key']['description']='Scalar metric key from configuration.dimensions, for example dscr or debt_to_income, never a dimension-family name. Unit, borrower applicability and calculation version must match approved configuration.'
 add('PolicyRule',{'calculation_version':text('Pin the calculation version returned by configuration.dimensions. A different method requires a new immutable risk-policy version.')})
 add('PolicyResult',{'metric_key':text(),'calculation_version':text(),'metric_window':ref('Window')})
 s['AssessmentScope']=obj({'borrower_type':enum('business','person'),'market':enum('US','CA'),'reporting_currency':currency,'window':ref('Window'),'account_ids':ids,'entity_ids':ids,'consolidation':enum('single_entity','consolidated','individual','joint'),'accounting_basis':enum('cash','accrual','mixed'),'coverage_basis':enum('observed_sources','declared_sources_reconciled'),'excluded_sources':array(obj({'source_id':text(),'reason':text()})),'fx_rates':array(obj({'from_currency':currency,'to_currency':currency,'rate':text(pattern=r'^(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$'),'as_of':stamp,'source':text(),'evidence_ids':ids}))},description='Assessment boundaries. Observed sources do not establish all external accounts. FX rates must be positive and evidenced; never sum unlike currencies. Joint assessments require authorized related borrowers and explicit allocation.')
 s['RiskFinding']=obj({'id':text(),'code':text(),'dimension_key':enum(*[d['key'] for d in c['dimensions']]),'severity':enum('info','warning','critical'),'nature':enum('observation','calculation','inconsistency','suspected_anomaly','model_output'),'summary':text(),'explanation':text(),'metric_keys':array(text()),'evidence':array(ref('EvidenceLocation'),minItems=1),'limitations':array(text())},description='Reviewable finding with source locations. Suspicion is not confirmed fraud; severity is not a probability of default.')
 s['VerificationCheck']=obj({'id':text(),'check':enum('identity','account_ownership','business_registration','beneficial_ownership','document_authenticity','income_verification','credit_report_match','lien','tax_filing'),'subject_id':text(),'result':enum('matched','not_matched','inconclusive','not_checked'),'provider':nullable(text()),'observed_at':nullable(stamp),'explanation':text(),'evidence':array(ref('EvidenceLocation'))},description='Provider and observation context remain visible. Inconclusive, not checked and no matching record must never become a verified pass.')
 s['FinancialStatement']=obj({'id':text(),'kind':enum('income_statement','balance_sheet','cash_flow'),'window':ref('Window'),'as_of':stamp,'basis':enum('cash','accrual'),'currency':currency,'consolidation':text(),'lines':array(obj({'key':text(),'label':text(),'amount':decimal,'parent_key':nullable(text()),'is_subtotal':{'type':'boolean'},'evidence':array(ref('EvidenceLocation'),minItems=1)}),minItems=1),'adjustments':array(obj({'line_key':text(),'amount':decimal,'reason':text(),'evidence':array(ref('EvidenceLocation'),minItems=1)}))},description='Normalized statements with hierarchy and sourced adjustments. Do not sum both a subtotal and its children. Adjustments never overwrite source statements.')
 s['DebtObligation']=obj({'id':text(),'creditor_reference':nullable(text()),'kind':enum('term_loan','revolving','lease','mortgage','trade','tax','other'),'basis':enum('observed','declared','inferred'),'proposed':{'type':'boolean'},'currency':currency,'outstanding':nullable(decimal),'limit':nullable(decimal),'annual_rate':nullable(decimal),'maturity_date':nullable(text(format='date')),'secured':nullable({'type':'boolean'}),'payment_schedule':array(obj({'due_at':stamp,'principal':decimal,'interest':decimal,'fees':decimal,'balloon':{'type':'boolean'}})),'coverage':enum('complete','partial'),'missing_fields':array(text()),'evidence':array(ref('EvidenceLocation'),minItems=1)},description='Resolved obligations and exact required payments, including proposed exposure. Inferred recurring debits do not prove outstanding principal, contract rate or complete liabilities. Schedules use stated currency; rate is a fraction.')
 s['IncomeStream']=obj({'id':text(),'kind':enum('employment','self_employment','benefit','pension','rental','other'),'payer_reference':nullable(text()),'basis':enum('observed','declared','estimated'),'gross_monthly':nullable(decimal),'net_monthly':nullable(decimal),'currency':currency,'cadence':enum('weekly','biweekly','semimonthly','monthly','irregular'),'first_observed_at':stamp,'last_observed_at':stamp,'verification':enum('verified','partially_verified','unverified'),'evidence':array(ref('EvidenceLocation'),minItems=1)},description='Independent gross and net income evidence. Deposits alone establish neither pretax income nor an employment relationship. Monthly conversion: weekly ×52/12, biweekly ×26/12, semimonthly ×2; disclose irregular-period method.')
 s['Reconciliation']=obj({'id':text(),'left_source':text(),'right_source':text(),'window':ref('Window'),'currency':currency,'left_total':decimal,'right_total':decimal,'adjustments':array(obj({'kind':enum('fees','refunds','tax','timing','fx','other'),'amount':decimal,'explanation':text(),'evidence':array(ref('EvidenceLocation'),minItems=1)})),'adjusted_left_total':decimal,'residual':decimal,'tolerance':decimal,'result':enum('matched','unmatched','inconclusive'),'evidence':array(ref('EvidenceLocation'),minItems=1)},description='Bridge: adjusted_left_total = left_total + signed adjustments; residual = adjusted_left_total - right_total. Matched requires abs(residual) <= nonnegative tolerance plus complete comparable populations. Differences are not automatically fraud.')
 s['ConcentrationSegment']=obj({'id':text(),'kind':enum('customer','supplier','income_source','channel','geography','currency'),'window':ref('Window'),'currency':currency,'total':decimal,'unallocated_amount':decimal,'buckets':array(obj({'reference':text(),'amount':decimal,'share':decimal,'evidence_ids':ids}))},description='Buckets plus unallocated_amount reconcile to total. Shares use the same positive denominator. Pseudonymous counterparties are limited to the authorized borrower scope; no unrelated customer data.')
 s['RiskProjection']=obj({'id':text(),'kind':enum('baseline','stress'),'method':enum('deterministic','statistical'),'model_version':text(),'horizon':ref('Window'),'assumptions':array(obj({'parameter':text(),'value':decimal,'unit':text(),'rationale':text()}),minItems=1),'metric_key':text(),'unit':text(),'currency':nullable(currency),'observations':array(ref('MetricObservation'),minItems=1),'interval':nullable(obj({'level':decimal,'method':text(),'calibration_reference':text(),'lower':decimal,'upper':decimal})),'limitations':array(text())},description='Conditional forecast under explicit parameter assumptions, not a promise or default probability. A statistical interval needs calibration evidence; a deterministic stress range is not a confidence interval. Each output identifies its horizon, currency and unit.')
 s['RiskBenchmark']=obj({'id':text(),'metric_key':text(),'cohort':obj({'market':enum('US','CA'),'industry':nullable(text()),'borrower_type':enum('business','person'),'size_band':nullable(text()),'period':ref('Window'),'sample_size':{'type':'integer','minimum':1},'source':text(),'methodology_version':text()}),'percentile':text(pattern=r'^(?:0(?:\.[0-9]+)?|1(?:\.0+)?)$'),'limitations':array(text())},description='Only an entitled, relevant, documented cohort can yield a percentile. No invented peers, universal cutoffs or source-free industry rankings.')
 s['RiskModelOutput']=obj({'id':text(),'kind':enum('probability_of_default','loss_given_default','expected_loss','provider_score'),'value':decimal,'unit':enum('ratio','currency','score'),'currency':nullable(currency),'model_version':text(),'provider':text(),'target_definition':text(),'horizon_months':{'type':'integer','minimum':1},'population':text(),'market':enum('US','CA'),'validation_reference':text(),'calibration_as_of':stamp,'reason_codes':array(text(),minItems=1),'limitations':array(text())},description='Only entitled, validated outputs applicable to this borrower/population. Provider scores retain their original model and scale. Never substitute a heuristic or deterministic scenario for a calibrated PD/LGD. Score scale and target are documented by validation_reference.')
 s['RiskModelOutput']['allOf']=[
  {'if':{'properties':{'kind':{'enum':['probability_of_default','loss_given_default']}}},'then':{'properties':{'unit':{'const':'ratio'},'currency':{'type':'null'},'value':text(pattern=r'^(?:0(?:\.[0-9]+)?|1(?:\.0+)?)$')}}},
  {'if':{'properties':{'kind':{'const':'expected_loss'}}},'then':{'properties':{'unit':{'const':'currency'},'currency':currency,'value':text(pattern=r'^(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$')}}},
  {'if':{'properties':{'kind':{'const':'provider_score'}}},'then':{'properties':{'unit':{'const':'score'},'currency':{'type':'null'}}}}]
 s['RiskProjection']['allOf']=[{'if':{'properties':{'method':{'const':'deterministic'}}},'then':{'properties':{'interval':{'type':'null'}}}},{'if':{'properties':{'unit':{'const':'currency'}}},'then':{'properties':{'currency':currency}},'else':{'properties':{'currency':{'type':'null'}}}}]
 s['RiskChange']=obj({'metric_key':text(),'previous_package_id':text(),'comparable':{'type':'boolean'},'reason':nullable(text()),'previous_value':nullable(decimal),'current_value':nullable(decimal),'absolute_delta':nullable(decimal),'relative_delta':nullable(decimal),'evidence_ids':ids},allOf=[{'if':{'properties':{'comparable':{'const':False}}},'then':{'properties':{'reason':text(),'absolute_delta':{'type':'null'},'relative_delta':{'type':'null'}}},'else':{'properties':{'previous_value':decimal,'current_value':decimal,'absolute_delta':decimal,'reason':{'type':'null'}}}}],description='Only compare compatible calculation versions, scope, units, currency, observation windows and evidence quality. relative_delta is null with zero/nonpositive baseline; absolute_delta remains numeric when valid.')
 s['CollateralAsset']=obj({'id':text(),'kind':enum('property','equipment','inventory','receivables','cash','investment','other'),'owner_subject_id':text(),'ownership_share':decimal,'currency':currency,'valuation':nullable(decimal),'valuation_at':nullable(stamp),'valuation_method':nullable(text()),'eligible_value':nullable(decimal),'haircut':nullable(decimal),'liens':array(obj({'holder_reference':text(),'priority':nullable({'type':'integer','minimum':1}),'amount':nullable(decimal),'status':enum('reported','verified','released','disputed')})),'limitations':array(text()),'evidence':array(ref('EvidenceLocation'),minItems=1)},description='Dated asset valuation, ownership and encumbrance evidence. Eligible value is a justified assessment, not an enforceability guarantee. Unknown liens or stale valuations are explicit limitations; do not report zero liens from an absent search.')
 s['BorrowerRelationship']=obj({'id':text(),'from_subject_id':text(),'to_reference':text(),'kind':enum('owner','controller','guarantor','related_party','customer','supplier'),'ownership_share':nullable(decimal),'valid_as_of':stamp,'basis':enum('verified','declared','inferred'),'explanation':text(),'evidence':array(ref('EvidenceLocation'),minItems=1)},description='An authorized borrower relationship with its basis and observation date. IDs are scoped references; an inferred relationship is never represented as verified ownership. No unrelated institution identity graph.')
 s['CreditReportAssessment']=obj({'id':text(),'provider':text(),'report_type':text(),'market':enum('US','CA'),'pulled_at':stamp,'subject_match':enum('matched','inconclusive','not_matched'),'report_document_id':nullable(text()),'score':nullable(obj({'value':decimal,'minimum':decimal,'maximum':decimal,'higher_is':enum('lower_risk','higher_risk'),'model':text(),'reason_codes':array(text())})),'obligation_ids':ids,'disputes':array(text()),'coverage_notes':array(text()),'evidence':array(ref('EvidenceLocation'),minItems=1)},description='Entitled matched bureau evidence retains provider/model/score scale, pull date and disputes. A missing report is unavailable, not a clean credit record. No cross-model score averaging. Linked obligations are resolved without double-counting.')
 s['TaxObligation']=obj({'id':text(),'jurisdiction':text(),'tax_type':text(),'period':ref('Window'),'currency':currency,'basis':enum('declared','filed','assessed'),'amount':nullable(decimal),'paid_amount':nullable(decimal),'due_date':nullable(text(format='date')),'filing_status':enum('filed','not_filed','unknown'),'payment_status':enum('paid','partially_paid','unpaid','unknown'),'disputed':{'type':'boolean'},'evidence':array(ref('EvidenceLocation'),minItems=1)},description='Separate tax declaration, filing, assessment and payment evidence. Unknown records cannot establish compliance or arrears. Duplicate tax obligations already in the debt schedule are linked in evidence rather than charged twice.')
 items=[('verifications','VerificationCheck'),('financial_statements','FinancialStatement'),('obligations','DebtObligation'),('income_streams','IncomeStream'),('reconciliations','Reconciliation'),('concentrations','ConcentrationSegment'),('projections','RiskProjection'),('benchmarks','RiskBenchmark'),('model_outputs','RiskModelOutput'),('changes','RiskChange'),('collateral','CollateralAsset'),('relationships','BorrowerRelationship'),('credit_reports','CreditReportAssessment'),('tax_obligations','TaxObligation')]
 for key,item in items:section(item+'Section',item,'Coverage and results for '+key.replace('_',' ')+'. Empty unavailable/not_applicable sections carry an explicit reason. Partial results must identify their limitation; an empty list alone never means a clean assessment.')
 add('RiskPackage',{'scope':ref('AssessmentScope'),'catalog_version':{'const':VERSION},'completeness':obj({'expected_metric_count':{'const':len(c['metrics'])},'available_metric_count':integer,'unavailable_metric_count':integer,'not_applicable_metric_count':integer,'coverage_statement':text()}),'findings':array(ref('RiskFinding')),'analyses':obj({key:ref(item+'Section') for key,item in items}),'required_actions':array(obj({'code':text(),'description':text(),'metric_keys':array(text()),'requirement_ids':ids}))})
 s['RiskPackage']['description']+=' Includes every defined metric with an explicit availability state, source-linked analyses and exact catalog/calculation versions. Completeness is evidence coverage, not creditworthiness. Cross-field invariants are specified in the risk-package methodology.'
 from risk_data_expansion import extend_normalized
 extend_normalized(s)
 return s


def metric(m,package,borrower_type):
 applicable=borrower_type in m['borrower_types'] and m['dimension_key']!='monitoring_change'
 return {'key':m['key'],'label':m['label'],'status':'unavailable' if applicable else 'not_applicable','value':None,'unit':m['unit'],'window':deepcopy(package['sources'][0]['window']),'calculation_version':m['calculation_version'],'missing_reason':'Required, comparable source inputs are not included in this synthetic example.' if applicable else 'This metric does not apply to this borrower or an initial Insights assessment.','evidence_ids':[],'analysis_basis':'historical','assumptions':[],'definition_version':VERSION,'currency':package['lending_product']['definition']['currency'] if m['unit']=='currency' else None,'as_of':package['as_of'],'basis':'derived','reason_code':'missing_source' if applicable else 'not_applicable','inputs':[],'coverage':{'observed_days':0,'expected_days':365,'scope_note':'Synthetic example; observed sources do not establish all external accounts.'},'series':[]}


def decorate(package,borrower_type='business'):
 p=deepcopy(package);c=catalog();p['catalog_version']=VERSION
 from verification_contract import empty_assessment
 p['verification']=empty_assessment(p['borrower_id'],p['as_of'],borrower_type)
 p['scope']={'borrower_type':borrower_type,'market':p['lending_product']['definition']['market'],'reporting_currency':p['lending_product']['definition']['currency'],'window':deepcopy(p['sources'][0]['window']),'account_ids':['acct_synthetic'],'entity_ids':[p['borrower_id']],'consolidation':'single_entity' if borrower_type=='business' else 'individual','accounting_basis':'mixed','coverage_basis':'observed_sources','excluded_sources':[],'fx_rates':[]}
 p['dimensions']=[{'key':d['key'],'status':'unavailable','summary':'See individual metric availability and reasons.','metrics':[metric(m,p,borrower_type) for m in c['metrics'] if m['dimension_key']==d['key']],'evidence_ids':[]} for d in c['dimensions']]
 p['analyses']={key:{'status':'unavailable','reason':'Necessary supporting evidence is not included in this synthetic example.','evidence_ids':[],'items':[]} for key in ['verifications','financial_statements','obligations','income_streams','reconciliations','concentrations','projections','benchmarks','model_outputs','changes','collateral','relationships','credit_reports','tax_obligations']}
 p['analyses']['changes'].update(status='not_applicable',reason='An initial Insights assessment has no comparable baseline.')
 p['analyses']['model_outputs']['reason']='No eligible validated model output is included; no score or default probability is fabricated.'
 p['findings']=[]
 p['required_actions']=[{'code':'provide_debt_schedule','description':'Supply complete existing and proposed debt-service evidence.','metric_keys':['dscr'] if borrower_type=='business' else ['debt_to_income'],'requirement_ids':[]}]
 for result in p['policy_results']:
  key='dscr' if borrower_type=='business' else 'debt_to_income';definition=next(m for m in c['metrics'] if m['key']==key)
  result.update(metric_key=key,calculation_version=definition['calculation_version'],metric_window=deepcopy(p['scope']['window']))
 return recount(p)


def recount(p):
 counts={'available':0,'unavailable':0,'not_applicable':0}
 for d in p['dimensions']:
  for m in d['metrics']:counts[m['status']]+=1
  active=[m for m in d['metrics'] if m['status']!='not_applicable'];n=sum(m['status']=='available' for m in active)
  d['status']='not_applicable' if not active else 'available' if n==len(active) else 'partial' if n else 'unavailable'
  d['evidence_ids']=sorted({e for m in d['metrics'] for e in m['evidence_ids']})
 p['completeness']={'expected_metric_count':len(catalog()['metrics']),**{k+'_metric_count':v for k,v in counts.items()},'coverage_statement':'All catalog entries are accounted for. Availability describes supplied evidence, not borrower credit quality.'}
 return p


def available(p,key,value,inputs,window=None):
 m=next(m for d in p['dimensions'] for m in d['metrics'] if m['key']==key)
 m.update(status='available',value=value,missing_reason=None,reason_code=None,evidence_ids=sorted({loc['evidence_id'] for i in inputs for loc in i['evidence']}),inputs=inputs)
 if window:m['window']=deepcopy(window)
 from datetime import datetime
 days=(datetime.fromisoformat(m['window']['end'].replace('Z','+00:00'))-datetime.fromisoformat(m['window']['start'].replace('Z','+00:00'))).days
 m['coverage'].update(observed_days=days,expected_days=days,scope_note='Complete for the explicitly illustrated source scope and period only.')
 m['series']=[{'window':deepcopy(m['window']),'status':'available','value':value,'reason':None,'evidence_ids':m['evidence_ids']}]
 recount(p);return m


def example_input(name,value,unit='currency',evidence_id='ev_bank_synthetic',field_path='/amount/amount'):
 return {'name':name,'value':value,'unit':unit,'currency':'CAD' if unit=='currency' else None,'basis':'observed','evidence':[{'evidence_id':evidence_id,'field_path':field_path,'document_id':None,'page':None,'quote':None}]}


def extend_fixtures(f):
 f['Configuration']['dimensions']=deepcopy(catalog()['metrics']);f['Configuration']['risk_catalog_version']=VERSION
 p=decorate(f['RiskPackage'])
 # A documented observed subtotal, with no pretence of complete annual revenue or capacity.
 available(p,'total_inflows','1250.00',[example_input('posted_inflow','1250.00')],{'start':'2026-10-31T00:00:00Z','end':'2026-11-01T00:00:00Z'})
 p['limitations'].append('The illustrated inflow is a one-day observed-source subtotal. It is not annual revenue. Authorized derived metrics can remain available while a licensed raw evidence record is restricted.')
 f['RiskPackage']=p
 definitions={m['key']:m for m in catalog()['metrics']}
 def pin_rules(value):
  if isinstance(value,dict):
   if 'dimension_key' in value and 'operator' in value:value['calculation_version']=definitions[value['dimension_key']]['calculation_version']
   for child in value.values():pin_rules(child)
  elif isinstance(value,list):
   for child in value:pin_rules(child)
 pin_rules(f)
 f['Metric']=deepcopy(next(m for d in p['dimensions'] for m in d['metrics'] if m['key']=='dscr'))
 return f


def semantic_errors(p):
 """Acceptance rules beyond JSON Schema; used by backend/consumer contract tests."""
 c=catalog();defs={m['key']:m for m in c['metrics']};errors=[];ms=[m for d in p['dimensions'] for m in d['metrics']];keys=[m['key'] for m in ms]
 if len(keys)!=len(set(keys)) or set(keys)!=set(defs):errors.append('Every catalog metric must occur exactly once.')
 if len({d['key'] for d in p['dimensions']})!=len(c['dimensions']):errors.append('Every dimension must occur exactly once.')
 for d in p['dimensions']:
  active=[m for m in d['metrics'] if m['status']!='not_applicable'];n=sum(m['status']=='available' for m in active)
  status='not_applicable' if not active else 'available' if n==len(active) else 'partial' if n else 'unavailable'
  if d['status']!=status:errors.append('Dimension availability does not match its metrics.')
  for m in d['metrics']:
   if m['key'] not in defs:continue
   definition=defs[m['key']]
   if d['key']!=definition['dimension_key']:errors.append('Metric is in the wrong dimension.')
   if p['scope']['borrower_type'] not in definition['borrower_types'] and m['status']!='not_applicable':errors.append('Metric is not applicable to borrower type.')
   if m['coverage']['observed_days']>m['coverage']['expected_days']:errors.append('Coverage exceeds expected days.')
   if m['window']['end']<=m['window']['start']:errors.append('Invalid metric window.')
   if m['status']=='available':
    if any(i['value'] is None for i in m['inputs']):errors.append('Available metric has missing calculation inputs.')
    if set(m['evidence_ids'])!={loc['evidence_id'] for i in m['inputs'] for loc in i['evidence']}:errors.append('Metric provenance and evidence IDs differ.')
    if m['unit']=='currency' and m['currency']!=p['scope']['reporting_currency']:errors.append('Metric currency differs from reporting currency without normalization.')
   if m['key']=='dscr' and m['status']=='available':
    values={i['name']:Decimal(i['value']) for i in m['inputs'] if i['value'] is not None}
    if {'eligible_cash_flow','existing_annual_debt_service','proposed_annual_debt_service'}<=set(values):
     denominator=values['existing_annual_debt_service']+values['proposed_annual_debt_service']
     if denominator<=0 or abs(Decimal(m['value'])-values['eligible_cash_flow']/denominator)>Decimal('0.000001'):errors.append('DSCR differs from supported capacity inputs.')
   if m['key']=='debt_to_income' and m['status']=='available':
    values={i['name']:Decimal(i['value']) for i in m['inputs'] if i['value'] is not None}
    if {'gross_monthly_income','existing_monthly_debt','proposed_monthly_debt'}<=set(values):
     denominator=values['gross_monthly_income']
     if denominator<=0 or abs(Decimal(m['value'])-(values['existing_monthly_debt']+values['proposed_monthly_debt'])/denominator)>Decimal('0.000001'):errors.append('DTI differs from supported income and obligations.')
   if m['unit'] in ['count','days','months'] and m['key']!='cash_conversion_cycle' and m['value'] is not None and Decimal(m['value'])<0:errors.append('Negative duration or count.')
 counts={k:sum(m['status']==k for m in ms) for k in ['available','unavailable','not_applicable']}
 if any(p['completeness'][k+'_metric_count']!=n for k,n in counts.items()):errors.append('Completeness counts do not match emitted metrics.')
 for rate in p['scope']['fx_rates']:
  if Decimal(rate['rate'])<=0 or not rate['evidence_ids']:errors.append('FX conversion needs a positive evidenced rate.')
 for r in p['analyses']['reconciliations']['items']:
  adjusted=Decimal(r['left_total'])+sum((Decimal(a['amount']) for a in r['adjustments']),Decimal(0));residual=adjusted-Decimal(r['right_total'])
  if adjusted!=Decimal(r['adjusted_left_total']) or residual!=Decimal(r['residual']):errors.append('Reconciliation arithmetic differs from evidence bridge.')
  if Decimal(r['tolerance'])<0 or (r['result']=='matched' and abs(residual)>Decimal(r['tolerance'])):errors.append('Invalid reconciliation tolerance or result.')
 for change in p['analyses']['changes']['items']:
  if change['comparable']:
   a,b=Decimal(change['previous_value']),Decimal(change['current_value'])
   if Decimal(change['absolute_delta'])!=b-a:errors.append('Incorrect absolute change.')
   if a<=0 and change['relative_delta'] is not None:errors.append('Relative change requires a positive baseline.')
   if a>0 and change['relative_delta'] is not None and abs(Decimal(change['relative_delta'])-(b-a)/a)>Decimal('0.000001'):errors.append('Incorrect relative change.')
 for projection in p['analyses']['projections']['items']:
  interval=projection['interval']
  if interval and (not Decimal(0)<Decimal(interval['level'])<Decimal(1) or Decimal(interval['lower'])>Decimal(interval['upper'])):errors.append('Invalid statistical interval.')
  if projection['horizon']['end']<=projection['horizon']['start']:errors.append('Invalid projection horizon.')
 for segment in p['analyses']['concentrations']['items']:
  total=Decimal(segment['total']);unallocated=Decimal(segment['unallocated_amount'])
  if total<=0 or unallocated<0 or sum((Decimal(b['amount']) for b in segment['buckets']),unallocated)!=total:errors.append('Concentration does not reconcile to total.')
  if total>0 and any(abs(Decimal(b['share'])-Decimal(b['amount'])/total)>Decimal('0.000001') for b in segment['buckets']):errors.append('Concentration shares use the wrong denominator.')
 for model in p['analyses']['model_outputs']['items']:
  if model['market']!=p['scope']['market']:errors.append('Risk model is not eligible for this market.')
 for finding in p['findings']:
  if not set(finding['metric_keys'])<=set(keys):errors.append('Finding references unknown metric.')
 for result in p['policy_results']:
  m=next((m for m in ms if m['key']==result['metric_key']),None)
  if m is None or result['actual']!=m['value'] or result['calculation_version']!=m['calculation_version'] or result['metric_window']!=m['window']:errors.append('Policy result does not match the assessed metric version/value/window.')
  rule=next((r for r in p['risk_policy']['definition']['rules'] if r['id']==result['rule_id']),None)
  if not rule or rule['dimension_key']!=result['metric_key'] or rule['unit']!=result['unit'] or rule['threshold']!=result['threshold'] or rule['calculation_version']!=result['calculation_version']:errors.append('Policy result differs from the frozen policy rule.')
  if rule and result['actual'] is not None:
   actual,threshold=Decimal(result['actual']),Decimal(result['threshold']);passed={'gt':actual>threshold,'gte':actual>=threshold,'lt':actual<threshold,'lte':actual<=threshold,'eq':actual==threshold}[rule['operator']]
   if (result['result']=='pass')!=passed:errors.append('Policy outcome contradicts its comparison.')
 if p['scope']['borrower_type']!=p['lending_product']['definition']['borrower_type']:errors.append('Borrower type differs from product.')
 return errors

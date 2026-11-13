"""Evidence-backed deterministic additions. No predictive score is synthesized."""
from copy import deepcopy
VERSION = '2026-11-12.1'
PREVIOUS_VERSION = '2026-11-06.1'
# dimension|key|label|unit|formula|minimum supported inputs
ROWS = '''cashflow|posted_transaction_count|Posted transaction count|count|Count eligible posted records, each current resource version once|Valid date, direction, currency and nonnegative amount
cashflow|operating_receipt_count|Operating receipt count|count|Count posted external sales receipts|Explicit classification and transfer exclusion
cashflow|owner_contribution_inflows|Owner capital contributions|currency|Sum external owner-contribution inflows|Explicit direction and category
cashflow|owner_distribution_outflows|Owner distributions|currency|Sum external owner-distribution outflows|Explicit direction and category
cashflow|debt_proceeds_inflows|Debt proceeds|currency|Sum external debt-proceeds inflows|Explicit direction and category
cashflow|observed_debt_service|Observed debt-service payments|currency|Sum external debt-service outflows, including principal and lender charges already included in the debit|Explicit debt-service classification; no assumption of complete contractual obligations
cashflow|bank_fee_outflows|Bank fees paid|currency|Sum external fee outflows|Explicit fee classification
cashflow|cash_withdrawal_outflows|Cash withdrawals|currency|Sum outflows explicitly identified as cash withdrawals|Known product_activity for every eligible external outflow
cashflow|payroll_outflows|Payroll paid|currency|Sum external payroll outflows|Explicit payroll classification
cashflow|inventory_purchase_outflows|Inventory purchases paid|currency|Sum outflows explicitly identified as inventory purchases|Known product_activity for every eligible external outflow
cashflow|internal_transfer_outflows|Internal transfer outflows|currency|Sum outflows explicitly identified as internal transfers|Known transfer status for every posted transaction
cashflow|spending_to_receipts_ratio|Operating spending to receipts|ratio|Operating cash payments divided by operating receipts|Positive operating receipts; complete classification
cashflow|spending_to_receipts_change_90d|Change in spending to receipts|ratio|Current 90-day operating spending/receipts minus preceding 90-day operating spending/receipts|Two fully observed 90-day windows; positive receipts in both
revenue_quality|receipt_gap_mean_days|Mean interval between receipts|days|Mean UTC-day gap between distinct operating-receipt dates|At least three distinct receipt dates; whole-window bank coverage
revenue_quality|receipt_gap_stddev_days|Receipt interval variability|days|Population standard deviation of UTC-day gaps between distinct operating-receipt dates|At least three distinct receipt dates; whole-window bank coverage
revenue_quality|receipt_day_of_month_stddev|Receipt calendar-day variability|days|Population standard deviation of day-of-month across distinct operating-receipt dates|At least three receipt dates; descriptive only, not a timing forecast
revenue_quality|zero_revenue_month_count|Months without recorded receipts|count|Count completely covered UTC calendar months with no operating receipts|Complete transaction coverage; exclude partial months; no receipts does not prove no accrual revenue
revenue_quality|operating_receipts_volatility|Operating receipts volatility|ratio|Population standard deviation divided by mean of complete monthly operating receipts|At least six complete months; positive mean
revenue_quality|operating_receipts_change_90d|Operating receipts change|ratio|Current 90-day receipts minus previous 90-day receipts divided by previous receipts|Two fully observed 90-day windows; positive previous receipts
revenue_quality|days_since_last_operating_receipt|Days since last observed receipt|days|Days from latest receipt date to the last included UTC date of the observation window|At least one classified receipt; no claim about time outside source coverage
operating_resilience|operating_outflows_change_90d|Operating payments change|ratio|Current 90-day operating payments minus preceding payments divided by preceding payments|Two fully observed 90-day windows; positive previous payments
liquidity|balance_stddev|Daily balance variability|currency|Population standard deviation of consolidated daily closing balances|At least 30 complete comparable calendar days across every included account
liquidity|balance_coefficient_of_variation|Relative daily balance variability|ratio|Daily balance population standard deviation divided by absolute mean balance|At least 30 complete comparable days; nonzero mean; near-zero sensitivity
liquidity|maximum_daily_balance|Maximum daily cash balance|currency|Maximum consolidated daily closing balance|Complete daily balances across every included account
liquidity|median_daily_balance|Median daily cash balance|currency|Median consolidated daily closing balance; mean of two central values when even|Complete daily balances across every included account
liquidity|low_balance_days|Days below the declared cash floor|days|Count covered days with consolidated closing cash below the explicit liquidity floor|Complete daily balances; evidenced reporting-currency liquidity floor
liquidity|balance_change_90d|Cash balance change over 90 days|currency|Last covered closing balance minus closing balance exactly 90 calendar days earlier|Both dates observed; complete comparable daily balances
liquidity|cash_shock_count|Observed cash-shock episodes|count|Count nonoverlapping episodes beginning with a one-day decline of at least 20 percent from a positive previous closing balance|Complete daily balances; episode ends when balance recovers to its pre-shock level; no predictive interpretation
liquidity|balance_recovery_days|Most recent cash-shock recovery|days|Calendar days to regain the pre-shock closing balance for the most recent episode|A completed most-recent episode; unavailable when no episode or when recovery is not observed
liquidity|unrecovered_cash_shock_count|Unrecovered cash-shock episodes|count|Count open episodes at the end of the observation window under the same nonoverlapping 20 percent shock rule|Complete daily balances; an unrecovered episode is right-censored, not a forecast
repayment_capacity|debt_service_to_outflows|Debt-service share of outflows|ratio|Observed external debt-service payments divided by all external posted outflows|Positive external outflows; explicit transfer and category classification
leverage|concurrent_financing_count|Observed active financing facilities|count|Count distinct active provider facilities after facility-ID deduplication|Explicit facility identity and active status; observed-source inventory only; lender deal snapshot excluded
leverage|new_financing_count_90d|Recently funded active facilities|count|Count observed active facilities funded in the 90 days ending at assessment time|Known funding date for every included active facility; observed-source inventory only
leverage|debt_to_operating_receipts|Debt to annual operating receipts|ratio|Supported total debt divided by observed trailing-year operating receipts|Complete trailing 12 calendar months and debt inventory; positive receipts; same scope; no silent annualization
revenue_quality|unclassified_receipt_share|Unclassified external receipts|ratio|External inflow amount in unknown or other categories divided by external inflows|Known transfer status; positive external receipts; uncertainty is not fraud
'''

def extend_catalog(c):
 for row in ROWS.strip().splitlines():
  dim,key,label,unit,formula,inputs=row.split('|')
  family=next(d for d in c['dimensions'] if d['key']==dim)
  c['metrics'].append(dict(key=key,dimension_key=dim,label=label,description=label+'. '+formula+'.',unit=unit,formula=formula,
   required_inputs=[v.strip() for v in inputs.split(';')],eligibility='Observed source scope only. Missing observations never become zero; all included accounts must have comparable currency and coverage.',
   borrower_types=['business'],source_families=['banking','accounting','documents'],definition_version=VERSION,calculation_version='amlok-'+key+'-1',
   window_rule='UTC start-inclusive/end-exclusive source observation window. Exclude records outside that window. Full-month and full-day coverage requirements are mandatory.',
   unavailable_rule='Return null and a typed reason for missing classification, incomplete history, invalid denominator, conflicting evidence or an unobserved recovery. A known zero requires supported source coverage.',
   interpretation='Descriptive historical measure, not a calibrated probability, fraud verdict or credit decision. Ratios are fractions; amount fields retain the reporting currency.'))
 c['version']=VERSION
 return c

def extend_normalized(s):
 def obj(p,required=None): return dict(type='object',properties=p,required=required or list(p),additionalProperties=False)
 def nullable(schema,description): return dict(anyOf=[schema,{'type':'null'}],description=description)
 def text(desc): return nullable({'type':'string','minLength':1},desc)
 decimal={'type':'string','pattern':r'^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$'}
 amount=obj({'amount':decimal,'currency':{'type':'string','pattern':'^[A-Z]{3}$'}})
 add={
 'NormalizedBankTransaction':{
  'stream_id':text('Stable provider-supported recurring event stream within this account. Null when recurrence has not been established; grouping is not a prediction.'),
  'payment_rail':text('Source-reported payment rail, such as ACH, wire or card. Distinct from sales channel.'),
  'intermediary_counterparty_id':text('Resolved payment intermediary; does not replace the economic counterparty.'),
  'economic_role':nullable({'type':'string','enum':['business','personal','mixed','unknown']},'Supported economic use of the transaction; not inferred from account ownership alone.'),
  'product_activity':nullable({'type':'string','enum':['none','loan','merchant_cash_advance','buy_now_pay_later','earned_wage_access','savings','investment','cash_withdrawal','inventory_purchase','unknown']},'Evidence-supported financial product or economic activity. Unknown is distinct from none.'),
  'return_reason':text('Normalized reported return cause. insufficient_funds identifies NSF; other returns must not be counted as NSF.'),
  'is_essential':nullable({'type':'boolean'},'Whether source-supported analysis identifies an essential cash payment. Unknown must not be treated as false.')},
 'NormalizedBankAccount':{
  'holder_addresses':nullable({'type':'array','items':{'$ref':'#/components/schemas/NormalizedAddress'}},'Source-reported account-holder addresses. May differ from business registered or mailing address.'),
  'transaction_coverage':nullable(obj({'start':{'type':'string','format':'date-time'},'end':{'type':'string','format':'date-time'},'status':{'type':'string','enum':['complete','partial','unknown']}}),'Source-established coverage, start-inclusive/end-exclusive; complete means every posted transaction for this interval is represented, including zero-activity days. It does not prove all external accounts are connected.')},
 'NormalizedAccountBalance':{
  'daily_balances':nullable({'type':'array','items':obj({'date':{'type':'string','format':'date'},'amount':decimal})},'Observed daily closing balances in current.currency. Missing dates are missing; never fill with zero or interpolate as observed.'),
  'restricted_amount':nullable(amount,'Source-supported restricted cash at as_of. A known zero is distinct from unknown. Not applicable to credit liabilities.')},
 'NormalizedLoan':{'creditor_counterparty_id':text('Resolved creditor; retain facility identity separately to avoid double-counting repeated source observations.')},
 }
 for base,props in add.items():
  for name in [base,base+'Read']:
   if name in s:s[name]['properties'].update(deepcopy(props))
 # A typed schedule exposes the exact accounting inputs otherwise hidden in fixture extensions.
 keys='revenue prior_year_revenue cogs payroll prior_year_payroll other_operating_expenses depreciation interest tax net_profit cash receivables inventory current_assets current_liabilities total_assets total_liabilities equity opening_assets capex existing_debt_service existing_principal_service total_debt revolving_used revolving_limit trade_payables overdue_receivables ar_90_plus overdue_payables related_party_receivables eligible_receivables tax_assessed tax_paid tax_outstanding prior_year_cash collateral_valuation collateral_realizable existing_secured_claims guarantee_amount required_dscr liquidity_floor gross_sales refunds chargebacks recurring_revenue prior_recurring_monthly recurring_churn recurring_expansion customer_count repeat_customers completed_orders fulfilled_orders on_time_orders eligible_item_days stockout_item_days settlement_days supplier_delay_days books_closing_lag_days required_filings filed_filings returned_payment_count nsf_event_count returned_payment_amount delinquent_obligations maximum_days_past_due elapsed_installments timely_installments declared_accounts matched_owners opening_receivables opening_trade_payables opening_inventory credit_sales credit_purchases short_term_investments'.split()
 s['FinancialSupportingSchedule']=obj({k:nullable(decimal,k.replace('_',' ').capitalize()+'. Source-supported numeric schedule input; money uses the parent statement currency and period. Count/day/ratio inputs use the named unit. Missing is null or omitted, never an assumed zero.') for k in keys},[])
 s['FinancialSupportingSchedule']['required']=[]
 for name in ['NormalizedFinancialStatement','NormalizedFinancialStatementRead']:
  if name in s:s[name]['properties']['supporting_schedule']=nullable({'$ref':'#/components/schemas/FinancialSupportingSchedule'},'Supported accounting and obligation schedule for this statement period and currency. Refer to metric definitions for eligibility; not a model output.')
 # Preserve old immutable assessments without rewriting their values to the new catalog.
 for name,prop in [('Metric','definition_version'),('RiskMetricDefinition','definition_version'),('RiskPackage','catalog_version')]:
  s[name]['properties'][prop]={'type':'string','enum':[PREVIOUS_VERSION,VERSION]}
 s['RiskPackage']['properties']['completeness']['properties']['expected_metric_count']={'type':'integer','minimum':1}

 from risk_package_catalog import catalog
 metrics=catalog()['metrics']; previous=[m for m in metrics if m['key'] not in {r.split('|')[1] for r in ROWS.strip().splitlines()}]
 rules=[]
 for version,definitions in [(PREVIOUS_VERSION,previous),(VERSION,metrics)]:
  by_dimension={d: [m['key'] for m in definitions if m['dimension_key']==d] for d in sorted({m['dimension_key'] for m in definitions})}
  dimensions={'type':'array','items':{'allOf':[{'if':{'properties':{'key':{'const':dim}}},'then':{'properties':{'metrics':{'minItems':len(keys),'maxItems':len(keys),'items':{'properties':{'key':{'enum':keys}}}}}}} for dim,keys in by_dimension.items()]}}
  rules.append({'if':{'properties':{'catalog_version':{'const':version}}},'then':{'properties':{'completeness':{'properties':{'expected_metric_count':{'const':len(definitions)}}},'dimensions':dimensions}}})
 existing=s['RiskPackage'].setdefault('allOf',[])
 for rule in rules:
  if rule not in existing:existing.append(rule)

def apply(spec,fixtures):
 """Run after lifecycle patches so snapshots cannot restore the previous catalog."""
 from risk_package_catalog import catalog
 from risk_package_contract import metric, recount
 c=catalog();extend_normalized(spec['components']['schemas'])
 spec['x-contract-revision']='2026-11-12.risk-data.1'
 schemas=spec['components']['schemas']
 for prop in ['catalog_version','completeness']:
  schemas['RiskPackageSummary']['properties'][prop]=deepcopy(schemas['RiskPackage']['properties'][prop])
 def visit(value):
  if isinstance(value,dict):
   if 'catalog_version' in value and isinstance(value.get('dimensions'),list) and 'scope' in value:
    value['catalog_version']=VERSION
    for dimension in value['dimensions']:
     by_key={m['key']:m for m in dimension['metrics']}
     dimension['metrics']=[by_key.get(m['key']) or metric(m,value,value['scope']['borrower_type']) for m in c['metrics'] if m['dimension_key']==dimension['key']]
     for m in dimension['metrics']:m['definition_version']=VERSION
    recount(value)
   if value.get('view')=='summary' and 'catalog_version' in value and 'completeness' in value:
    value['catalog_version']=VERSION
    completeness=value['completeness']
    previous=completeness['expected_metric_count']
    completeness['expected_metric_count']=len(c['metrics'])
    if 'unavailable_metric_count' in completeness:completeness['unavailable_metric_count']+=len(c['metrics'])-previous
   if 'risk_catalog_version' in value and isinstance(value.get('dimensions'),list):value['risk_catalog_version']=VERSION;value['dimensions']=deepcopy(c['metrics'])
   for child in list(value.values()):visit(child)
  elif isinstance(value,list):
   for child in value:visit(child)
 visit(spec);visit(fixtures)


def write_guides(root):
 path=root/'sandbox/businesses-and-scenarios.mdx'
 if path.exists():
  path.write_text(path.read_text().split("\n## Inspect financial evidence and missing inputs")[0]+"""
## Inspect financial evidence and missing inputs

The sample package includes six fictional businesses with different financial profiles. Scenario traces request `view=summary` for risk packages so the complete six-business journey stays readable. Retrieve the linked package directly, follow its paged section views or use its export request for full detail. The trace preserves the actual request and response; it does not truncate a full package. Run a scenario, retrieve its risk package, and follow a metric's `inputs[].evidence[]` to the frozen record and `field_path`. Banking examples include explicit coverage, transaction classifications and daily balances; accounting examples include a typed supporting schedule. Document records retain controlled download links.

Compare operating receipts with debt proceeds and owner contributions. Inspect cash-buffer days, receivable/payable/inventory days, receipt timing and observed cash-shock episodes. Read the metric's window, currency, version and missing reason before using its value. A review or missing-input scenario can legitimately return unavailable metrics.

Use **Dev Tools → Data Lookup** to inspect the request, response and field definitions. Discover scalar policy keys through `GET /v1/configuration`; use the returned calculation version when creating a risk-policy version. A required unavailable metric produces review instead of passing silently.

Existing saved results keep their original catalog. New runs use the current definitions, while missing source coverage remains explicit. Loading or resetting sample data is an explicit workspace action; a catalog update does not erase your existing Sandbox records. See [risk-package methodology](/api-reference/risk-package-methodology) for formulas and observation requirements. All sample businesses, funds and conclusions are synthetic.
""")

 path=root/'data-model/field-dictionary.mdx'
 if path.exists():
  import json
  props=json.loads((root/'openapi/amlok.json').read_text())['components']['schemas']['FinancialSupportingSchedule']['properties']
  special={
   'opening_receivables':'Trade receivables at the start of the statement period.',
   'receivables':'Trade receivables at the end of the statement period.',
   'opening_trade_payables':'Trade payables at the start of the statement period.',
   'trade_payables':'Trade payables at the end of the statement period.',
   'opening_inventory':'Inventory at the start of the statement period.',
   'inventory':'Inventory at the end of the statement period.',
   'credit_sales':'Sales on credit during this period; excludes cash sales. Required for receivable days.',
   'credit_purchases':'Purchases on credit during this period; excludes cash purchases. Required for payable days.',
   'nsf_event_count':'Specifically identified insufficient-funds events; other payment returns do not count.',
   'short_term_investments':'Supported short-term investment amount used in the quick ratio.',
   'liquidity_floor':'Explicit cash threshold in the statement currency; not an Amlok credit decision.',
  }
  content='\n## Financial supporting schedule fields\n\n`financial_statement.supporting_schedule` contains the following optional nullable decimal-string inputs. Amounts use the parent statement currency and reporting period. Missing fields are unknown, not zero. Opening balances mean the start of that period; closing balances mean its end. Exact formulas and eligibility are in [risk-package methodology](/api-reference/risk-package-methodology). The same nested fields are searchable in Console Data Lookup.\n\n| Field | Meaning |\n| --- | --- |\n'
  for key,value in props.items():content+='| `supporting_schedule.'+key+'` | '+special.get(key,value['description'])+' |\n'
  path.write_text(path.read_text().split('\n## Financial supporting schedule fields')[0]+content)

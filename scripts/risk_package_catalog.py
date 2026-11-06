"""Versioned AMLOK underwriting definitions; not a provider attribute-count claim."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent.parent
VERSION='2026-11-06.1'
# key, audience, source families, label, scope/eligibility rule
DIMENSIONS=[
('identity','both','identity registry banking documents','Identity and verification','Identity and account-ownership checks identify inconsistencies; they do not substitute for financial capacity.'),
('ownership_and_control','business','registry identity accounting application documents','Ownership and control','Use documented beneficial ownership, control, guarantees and related-party exposure. Do not infer family relationships or hidden ownership.'),
('cashflow','both','banking payments accounting','Cash flow','Use posted, deduplicated flows. Consolidation eliminates matched transfers; raw inflows remain distinct from operating receipts and revenue.'),
('liquidity','both','banking accounting','Liquidity','Separate available, restricted and observed balances. Reconstructed daily balances require reconciled opening/closing balances and complete transaction coverage.'),
('revenue_quality','business','banking payments commerce accounting','Revenue quality','Distinguish accrual revenue, gross sales, refunds, taxes, fees and cash settlement. Financing, transfers and owner injections are not sales.'),
('profitability','business','accounting tax documents','Profitability','Align accounting basis, reporting scope and periods. EBITDA addbacks require itemized justification; never infer profit from deposits alone.'),
('working_capital','business','accounting commerce inventory','Working capital','Use dated invoice/bill aging, sales and cost denominators on the same basis. Inventory valuation and credit-sales coverage must be explicit.'),
('leverage','both','accounting banking credit_bureau lender documents','Debt and leverage','Reconcile observed debt payments to disclosed and entitled bureau obligations. Unknown balances and undisclosed obligations are not zero.'),
('repayment_capacity','business','banking accounting lender application documents','Repayment capacity','Use complete existing and proposed debt schedules, eligible cash flow and consistent periods. Include balloon and variable-payment terms.'),
('concentration','both','accounting payments commerce payroll banking','Concentration','Aggregate only resolved counterparties within the authorized borrower scope. Unknown counterparties remain a disclosed unallocated bucket.'),
('collateral','both','collateral registry lender accounting documents','Collateral and security','Require current valuations, ownership, lien priority and permitted reports. This is collateral evidence, not a legal opinion or enforceability guarantee.'),
('fraud_and_consistency','both','documents banking accounting payments identity','Fraud and consistency','Signals identify evidence needing review; no signal or score alone confirms fraud. Preserve document locations and conflicting values.'),
('income_and_affordability','person','payroll banking tax credit_bureau application documents lender','Income and affordability','Distinguish verified gross income, net deposits and modeled estimates. Include housing, essential spending, obligations and proposed payments without counting them twice.'),
('income_stability','person','payroll banking tax documents','Income stability','Analyze authorized employment, self-employment and other recurring income streams separately. Income type is not itself an adverse risk reason.'),
('payment_behavior','both','banking accounting credit_bureau lender','Payment behavior','Deduplicate returns and their fees. Report payment outcomes and timing rather than inferring missed payments from missing source coverage.'),
('credit_history','both','credit_bureau lender documents','Credit history','Use entitled credit reports with source, score model, pull time and coverage. No matched report is not a clean credit history.'),
('commerce_performance','business','payments commerce subscriptions','Commerce and subscriptions','Keep store/platform coverage, settlement lags and currency explicit. Cohort metrics require stable customer identifiers and a complete comparable cohort.'),
('operating_resilience','business','payroll inventory accounting commerce logistics','Operating resilience','Measure payroll, supplier, inventory and fulfillment exposure from operational evidence. Do not infer management quality from personal traits or social media.'),
('tax_and_compliance','business','tax accounting registry documents','Tax and statutory obligations','Separate declared, filed, assessed and paid amounts and their periods. Registration or filing evidence is not a legal or tax-compliance certification.'),
('financial_reporting_quality','business','accounting banking documents','Financial reporting quality','Measure statement coverage, closing lag, reconciliations and material adjustments; missing accounting records are not fabricated statements.'),
('data_quality','both','banking accounting payments commerce payroll identity documents','Data quality and coverage','Describe observed coverage against declared/required sources; never imply visibility into all of a borrower\'s external accounts.'),
('forecasting_and_stress','both','banking accounting payroll application lender','Forecasting and stress','Separate scenario assumptions from observations. Forecasts require model/version, horizon and interval methodology; stress outcomes are conditional, not default probabilities.'),
('relationship_risk','business','registry accounting banking application','Related-party and network exposure','Only borrower-authorized ownership and transaction relationships are in scope. Links require evidence and uncertainty; no cross-institution identity graph is exposed.'),
('monitoring_change','both','banking accounting payroll lender','Monitoring changes','Compare compatible windows, scope, currencies and calculation versions. If comparability fails, expose the reason and no numeric delta.'),
]
# metric key | label | unit | calculation | necessary inputs / denominator or coverage condition
ROWS={
'identity':'''business_age_months|Business age|months|Whole calendar months from verified formation date to assessment date|Verified formation date; assessment date; business only
verified_account_owner_ratio|Verified account ownership share|ratio|Accounts with positively matched ownership divided by eligible disclosed connected accounts|Account ownership evidence and resolved borrower identity; nonzero eligible-account count''',
'ownership_and_control':'''ownership_disclosed_ratio|Disclosed ownership share|ratio|Sum of supported non-overlapping ownership fractions in the assessed entity|Current ownership register; common share basis; do not double-count direct and indirect paths
related_party_balance_share|Related-party receivables share|ratio|Related-party receivables divided by total receivables|Resolved related parties and same-date receivables; positive total receivables
supported_guarantee_coverage|Supported guarantee coverage|ratio|Documented collectible guarantee amount capped at exposure divided by exposure|Guarantee terms, guarantor assessment, currency and exposure; positive exposure; no unsupported collectible value''',
'cashflow':'''total_inflows|Posted inflows|currency|Sum posted inflow magnitudes before transfer or revenue exclusions|Complete eligible transaction set for the window, scope and currency
 total_outflows|Posted outflows|currency|Sum posted outflow magnitudes before transfer or operating exclusions|Complete eligible transaction set for the window, scope and currency
net_cash_flow|Net cash flow|currency|Posted inflows minus posted outflows after consolidation transfer elimination|Matched transfers, complete transactions and consistent scope/currency
operating_cash_inflows|Operating receipts|currency|Sum classified operating receipts excluding financing, internal transfers and owner injections|Supported transaction classifications and explicit exclusion bridge
operating_cash_outflows|Operating cash payments|currency|Sum operating outflows excluding financing principal, capital expenditures and matched transfers|Supported classifications and cash-flow basis; interest/tax treatment disclosed
operating_net_cash_flow|Net operating cash flow|currency|Operating receipts minus operating cash payments|Same-window receipts/outflows and documented classification basis
internal_transfer_inflows|Internal transfer inflows|currency|Sum inflows matched to outflows within the consolidation scope|Supported transfer pairs with stable IDs and explicit FX treatment
financing_inflows|Financing inflows|currency|Sum identified debt and equity financing receipts|Financing classification and evidence; uncertain receipts remain unclassified
positive_cashflow_month_share|Positive cash-flow months|ratio|Complete months with positive net cash flow divided by complete covered months|At least three complete months and consistent account scope
cashflow_volatility|Operating cash-flow volatility|ratio|Population standard deviation of complete monthly net operating cash flow divided by absolute mean|At least six complete months; nonzero mean; disclose near-zero denominator sensitivity
cashflow_change_90d|Operating cash-flow change|ratio|Current 90-day operating net flow minus previous 90-day flow, divided by absolute previous flow|Two complete comparable 90-day windows; nonzero previous flow''',
'liquidity':'''unrestricted_cash|Unrestricted cash|currency|Sum verified cash balances available for use, excluding restricted balances|Same-as-of reconciled balances and restriction status
average_daily_balance|Average daily cash balance|currency|Sum end-of-day balances divided by covered calendar days|Complete reconciled daily balances for the selected account scope
minimum_daily_balance|Minimum daily cash balance|currency|Minimum consolidated end-of-day balance|Complete comparable daily balances; disclose observed versus reconstructed basis
negative_balance_days|Days below zero|days|Count covered days with negative consolidated end-of-day balance|Complete daily balance series; no missing day treated as zero
cash_buffer_days|Cash buffer|days|Unrestricted cash divided by mean daily essential cash outflows|Positive essential-outflow denominator; current cash; documented window and exclusions
current_ratio|Current ratio|ratio|Current assets divided by current liabilities|Same-date classified balance sheet; positive current liabilities
quick_ratio|Quick ratio|ratio|Cash plus short-term investments plus eligible receivables, divided by current liabilities|Same-date asset/liability classifications; positive current liabilities
cash_ratio|Cash ratio|ratio|Unrestricted cash and cash equivalents divided by current liabilities|Same-date balances; positive current liabilities''',
'revenue_quality':'''verified_revenue|Verified revenue|currency|Sum supported revenue on the declared cash or accrual basis after exclusions|Reconciled bank, accounting or commerce evidence; taxes, financing and transfers excluded
recurring_revenue_share|Recurring revenue share|ratio|Supported recurring revenue divided by total verified revenue|Defined recurrence rule and matched periods; positive total revenue
revenue_growth_yoy|Revenue growth year over year|ratio|Current-period revenue minus prior-year comparable revenue, divided by prior-year revenue|Comparable periods separated by one year; positive prior revenue
revenue_growth_90d|Revenue growth over 90 days|ratio|Current 90-day revenue minus preceding 90-day revenue, divided by preceding revenue|Two complete 90-day periods; positive prior revenue
revenue_volatility|Monthly revenue volatility|ratio|Population standard deviation of monthly revenue divided by mean monthly revenue|At least six complete months; positive mean; consistent recognition basis
refund_amount_share|Refund amount share|ratio|Refunded sales amount divided by eligible gross sales amount|Matched sales/refund cohort and treatment of late refunds; positive gross sales
chargeback_amount_share|Chargeback amount share|ratio|Disputed chargeback amount divided by eligible processed sales amount|Matched processing cohort and consistent chargeback stage; positive denominator
revenue_cash_realization|Revenue cash realization|ratio|Matched collections on recognized sales divided by recognized sales|Defined collection horizon and sales cohort; positive recognized sales; not raw deposits/revenue
unverified_receipts_share|Unverified receipts share|ratio|Unclassified or unsupported operating-like receipts divided by total candidate receipts|Classification coverage and positive candidate receipts
nonrecurring_revenue_share|Nonrecurring revenue share|ratio|Identified nonrecurring revenue divided by verified revenue|Versioned recurrence criteria and positive revenue''',
'profitability':'''gross_profit|Gross profit|currency|Recognized revenue minus cost of goods sold|Same-period income statement with classified COGS
 gross_margin|Gross margin|ratio|Gross profit divided by recognized revenue|Positive revenue and consistent accounting basis
 ebitda|EBITDA|currency|Net income plus income tax expense, interest expense, depreciation and amortization|Complete supported statement line items; no automatic discretionary addbacks
 ebitda_margin|EBITDA margin|ratio|EBITDA divided by recognized revenue|Positive revenue and supported EBITDA
 operating_profit|Operating profit|currency|Revenue minus COGS and operating expenses|Complete same-period operating statement; financing excluded
 operating_margin|Operating margin|ratio|Operating profit divided by revenue|Positive recognized revenue
 net_profit|Net profit|currency|Total recognized income minus all recognized expenses|Complete statement on declared accounting basis
 net_margin|Net margin|ratio|Net profit divided by recognized revenue|Positive recognized revenue
 free_cash_flow|Free cash flow|currency|Operating cash flow minus cash capital expenditures|Reconciled cash-flow statement or supported cash reconstruction; no debt proceeds
 return_on_assets|Return on assets|ratio|Period net profit divided by mean opening and closing total assets|Positive average assets and complete period; disclose annualization, never apply silently''',
'working_capital':'''net_working_capital|Net working capital|currency|Current assets minus current liabilities|Same-date classified balance sheet
receivables_days|Receivable days|days|Average trade receivables divided by credit sales, multiplied by period days|Positive credit sales; opening/closing receivables; same accounting period
payables_days|Payable days|days|Average trade payables divided by credit purchases, multiplied by period days|Positive credit purchases; opening/closing payables; do not substitute COGS silently
inventory_days|Inventory days|days|Average inventory divided by COGS, multiplied by period days|Positive COGS; opening/closing comparable inventory valuation
cash_conversion_cycle|Cash conversion cycle|days|Receivable days plus inventory days minus payable days|All three components available on comparable periods and basis
ar_overdue_share|Overdue receivables share|ratio|Overdue collectible trade receivables divided by total collectible trade receivables|Due dates and same-as-of open balances; positive receivables
ar_90_plus_share|Receivables over 90 days past due|ratio|Receivables more than 90 days past due divided by total trade receivables|Aging based on due date, not invoice date; positive receivables
ap_overdue_share|Overdue payables share|ratio|Overdue trade payables divided by total trade payables|Due dates and open balances; positive payables
inventory_turnover|Inventory turnover|ratio|Period COGS divided by average inventory|Positive comparable inventory and supported COGS''',
'leverage':'''total_debt|Total interest-bearing debt|currency|Sum outstanding principal of resolved interest-bearing obligations|Complete disclosed and supported debt inventory; leases treatment explicit
net_debt|Net debt|currency|Total debt minus unrestricted cash eligible for offset|Same-as-of currency and consolidated scope
 debt_to_assets|Debt to assets|ratio|Total interest-bearing debt divided by total assets|Positive total assets and matched scope; excludes non-debt liabilities by definition
 debt_to_equity|Debt to equity|ratio|Total debt divided by equity|Positive equity; zero/negative equity produces unavailable ratio and a separate finding
 net_debt_to_ebitda|Net debt to EBITDA|ratio|Net debt divided by trailing-12-month EBITDA|Positive EBITDA and complete 12-month period
 credit_utilization|Revolving credit utilization|ratio|Used revolving principal divided by committed revolving limits|Positive known limits; distinguish drawn balances from pending authorizations
 short_term_debt_share|Debt due within one year|ratio|Principal contractually due within 365 days divided by total debt|Complete maturity schedule and positive total debt
 debt_maturing_90d|Debt maturing within 90 days|currency|Sum principal contractually due within the next 90 days|Complete maturity schedule including balloon payments''',
'repayment_capacity':'''dscr|Cash-flow debt-service coverage|ratio|Eligible cash flow available for debt service divided by existing plus proposed contractual debt service|Complete eligible cash-flow bridge and existing/proposed principal, interest and mandatory debt fees for the same period; positive debt service
fixed_charge_coverage|Fixed-charge coverage|ratio|Cash flow before the specified fixed charges divided by those fixed charges|Explicit non-overlapping charge set, including leases where applicable; positive charges
interest_coverage|Interest coverage|ratio|EBIT divided by interest expense|Supported same-period EBIT and positive interest expense
existing_debt_service|Existing debt service|currency|Sum existing contractual principal, interest and mandatory debt fees over the assessment window|Complete schedule; variable and balloon assumptions explicit
proposed_debt_service|Proposed debt service|currency|Sum proposed contractual principal, interest and mandatory debt fees over the assessment window|Exact proposed product terms, amount, rate, amortization, fees and timing
 total_debt_service|Total debt service|currency|Existing plus proposed debt service with duplicates removed|Comparable complete schedules and shared currency
residual_cash_after_debt|Cash after debt service|currency|Eligible cash available for debt service minus total debt service|Supported cash-flow bridge and complete obligations
 debt_service_headroom|Debt-service headroom|currency|Eligible cash flow divided by institution DSCR requirement, minus total debt service|Positive institution-approved DSCR threshold and complete components; analytical capacity, not an offer
 debt_payment_to_receipts|Debt payments to operating receipts|ratio|Observed debt payments divided by operating cash receipts|Positive receipts; payments classified with evidence; not a substitute for DSCR''',
'concentration':'''top_customer_share|Largest customer share|ratio|Largest resolved customer revenue divided by covered customer revenue|Positive covered revenue and disclosed unknown-counterparty share
 top_five_customer_share|Top five customer share|ratio|Revenue of five largest resolved customers divided by covered customer revenue|Positive covered revenue; fewer than five uses all resolved customers
 top_supplier_share|Largest supplier share|ratio|Largest resolved supplier spend divided by covered supplier spend|Positive supplier spend and explicit coverage
 top_channel_share|Largest sales channel share|ratio|Largest channel revenue divided by total covered channel revenue|Positive channel revenue; no duplicated cross-platform sales
 customer_hhi|Customer concentration index|ratio|Sum squared customer revenue fractions on a 0-to-1 scale|Complete resolved customer allocation or explicit partial coverage; unknown is not one customer
 income_source_hhi|Income-source concentration index|ratio|Sum squared verified income-source fractions on a 0-to-1 scale|Positive verified income and resolved income streams''',
'collateral':'''collateral_ltv|Loan to collateral value|ratio|Assessed facility exposure divided by supported collateral valuation|Positive eligible valuation with valuation date, currency and ownership
combined_ltv|Combined loan to value|ratio|All known secured claims including proposed exposure divided by collateral value|Positive valuation and complete supported lien/priority inventory
collateral_coverage|Collateral coverage|ratio|Eligible realizable collateral value after approved haircuts divided by secured exposure|Positive exposure, documented haircut and enforceability assumptions
eligible_receivables|Eligible borrowing-base receivables|currency|Sum receivables meeting institution eligibility and concentration rules|Versioned borrowing-base rules, aging, dilution and prior-pledge evidence
collateral_haircut_ratio|Collateral haircut|ratio|Gross eligible valuation minus supported realizable valuation, divided by gross valuation|Positive valuation and disclosed approved valuation/haircut method''',
'fraud_and_consistency':'''reconciliation_break_share|Unreconciled value share|ratio|Unmatched absolute value divided by eligible source-side absolute value|Comparable transaction populations, period, currency and matching tolerance
 duplicate_transaction_share|Duplicate transaction share|ratio|Confirmed duplicate records divided by examined records before deduplication|Nonzero examined records and documented duplicate criteria
 document_contradiction_count|Document contradictions|count|Count distinct supported inconsistencies between comparable document fields|Document-level findings with page/field evidence; a signal is not proof of fraud
 identity_mismatch_count|Unresolved identity mismatches|count|Count distinct unresolved mismatches across supported borrower identity attributes|Comparable identity sources; absent attributes are missing, not mismatched
 declared_income_gap_ratio|Declared-to-verified income gap|ratio|Declared income minus verified comparable income, divided by verified income|Positive verified income; same gross/net basis, currency, scope and period''',
'income_and_affordability':'''verified_gross_monthly_income|Verified gross monthly income|currency|Supported recurring pretax income normalized to one calendar month|Payroll, tax or supported gross-income evidence; net deposits alone do not establish gross income
verified_net_monthly_income|Verified net monthly income|currency|Supported recurring after-deduction income normalized to one calendar month|Verified income streams, recurrence and calendar conversion; transfers excluded
 debt_to_income|Debt to income|ratio|Existing plus proposed required monthly debt payments divided by verified gross monthly income|Positive verified gross income and complete monthly obligations; housing treatment explicit
 housing_to_income|Housing cost to income|ratio|Required monthly housing cost divided by verified gross monthly income|Positive gross income; rent/mortgage/tax/insurance/components explicit
 essential_monthly_spend|Essential monthly expenditure|currency|Sum evidenced essential non-debt spending normalized to one month|Versioned institution expense taxonomy; exclude sensitive merchant categories and avoid housing/debt duplication
 residual_monthly_income|Residual monthly income|currency|Verified net income minus essential spending, housing and existing/proposed debt payments|Complete non-overlapping monthly expense/obligation set
 payment_to_income|Proposed payment to income|ratio|Proposed required monthly payment divided by verified gross monthly income|Positive verified gross income and exact proposed terms
 liquid_reserve_months|Liquid reserve months|months|Unrestricted liquid funds divided by required monthly outgoings|Positive complete essential/housing/debt outgoings; verified liquid balances''',
'income_stability':'''income_source_count|Verified income sources|count|Count distinct supported recurring income streams|Deduplicated income identities and complete observed window
 income_volatility|Monthly income volatility|ratio|Population standard deviation of complete monthly verified income divided by mean|At least six complete months; positive mean; gross/net basis fixed
 income_growth_yoy|Income growth year over year|ratio|Current verified income minus comparable prior-year income, divided by prior-year income|Positive prior income; same income basis and comparable periods
 days_since_last_income|Days since last income|days|Days from most recent verified recurring income receipt to assessment date|Supported receipt and assessment date; missing history is unavailable
 income_interruption_days|Income interruption|days|Days past the next expected income date without a matched receipt|Documented payment cadence, complete account coverage and nonnegative elapsed interval
 income_continuity_share|Income continuity|ratio|Expected income periods with a supported receipt divided by elapsed expected periods|Explicit expected cadence and nonzero elapsed periods; missing account coverage cannot count as interruption''',
'payment_behavior':'''nsf_event_count|Insufficient-funds events|count|Count distinct supported returned-payment events caused by insufficient funds|Return reason evidence; deduplicate event and related fee records
 overdraft_days|Overdraft days|days|Count covered days with a negative balance in any assessed account|Complete per-account daily balances; union calendar days, not sum across accounts
 returned_payment_amount|Returned payment amount|currency|Sum principal amounts of distinct returned payment events|Return reason, direction and event linkage; exclude duplicate fees
 delinquent_obligation_count|Delinquent obligations|count|Count verified obligations past due at the assessment date|Due dates, payment allocation and complete supported debt schedule
 maximum_days_past_due|Maximum days past due|days|Maximum verified days past due among assessed obligations|Known contractual dues and allocated repayments; no delinquency inferred from missing feed
 on_time_payment_share|On-time payment share|ratio|Obligations paid by contractual due date divided by elapsed eligible obligations|Complete due/payment pairs and positive eligible count''',
'credit_history':'''open_credit_obligation_count|Open credit obligations|count|Count resolved open obligations in entitled credit evidence|Current permitted report or lender records; duplicate trades resolved
 bureau_utilization|Reported revolving utilization|ratio|Reported used revolving balances divided by reported limits|Same-report-date positive limits; disclose bureau coverage and currency
 recent_credit_inquiry_count|Recent credit inquiries|count|Count supported inquiry events in the requested window|Entitled report; group duplicates/rate-shopping only under disclosed rules
 severe_delinquency_count|Severe delinquency events|count|Count reported obligations meeting institution-defined severe-delinquency criteria|Current entitled report, criterion version and observation window
 public_record_event_count|Relevant public-record events|count|Count supported relevant insolvency/judgment events in entitled evidence|Verified matching, jurisdiction, record date and status; disputed records remain flagged''',
'commerce_performance':'''gross_sales|Gross sales|currency|Sum eligible sales before refunds and discounts, excluding taxes|Complete store/processor scope and consistent order versus settlement basis
net_sales|Net sales|currency|Gross sales minus discounts, cancellations and refunds|Same sales cohort and recognition window; taxes excluded
average_order_value|Average order value|currency|Net eligible order sales divided by completed noncancelled order count|Positive comparable order count; order-based rather than settlement data
 repeat_customer_share|Repeat customer share|ratio|Customers with more than one completed purchase divided by purchasing customers|Stable authorized customer IDs and positive cohort count
 monthly_recurring_revenue|Monthly recurring revenue|currency|Contracted recurring subscription revenue normalized to a month|Active recurring subscriptions, currency and documented usage/discount treatment
 gross_revenue_retention|Gross revenue retention|ratio|Opening recurring revenue minus churn and contraction divided by opening recurring revenue|Positive opening cohort revenue; expansion excluded
 net_revenue_retention|Net revenue retention|ratio|Opening recurring revenue minus churn/contraction plus expansion divided by opening recurring revenue|Same opening customer cohort and positive starting revenue
 settlement_delay_days|Settlement delay|days|Amount-weighted days from captured sale to corresponding bank settlement|Matched eligible captures and settlements; positive settled value''',
'operating_resilience':'''payroll_burden_share|Payroll burden|ratio|Payroll cash cost including employer costs divided by verified revenue|Positive comparable revenue; supported payroll records
 payroll_growth_yoy|Payroll growth year over year|ratio|Current payroll cost minus prior-year cost divided by prior-year cost|Comparable periods; positive prior payroll; no employee protected attributes
 inventory_stockout_share|Inventory stockout share|ratio|Observed sellable item-days out of stock divided by observed eligible item-days|Inventory history and eligible active-item scope; positive coverage
 fulfillment_on_time_share|On-time fulfillment share|ratio|Fulfilled eligible orders on/before promised date divided by eligible fulfilled orders|Complete order and shipment dates; positive eligible count
 supplier_payment_delay_days|Supplier payment delay|days|Amount-weighted days paid after contractual due date for settled trade bills|Matched bill/payment allocations; positive paid amounts; early payments recorded as zero delay''',
 'tax_and_compliance':'''tax_liability|Reported tax liability|currency|Sum supported outstanding assessed tax obligations at the assessment date|Entitled tax/statement evidence with assessed versus estimated status
 tax_overdue_amount|Overdue tax amount|currency|Sum supported unpaid tax obligations past their due dates|Actual due dates and paid allocations; estimated taxes not treated as arrears
 tax_payment_coverage|Tax payment coverage|ratio|Payments allocated to due assessed taxes divided by due assessed taxes|Positive due taxes and matched same-period payments
 filing_coverage|Filing evidence coverage|ratio|Required filings with supported filing evidence divided by known required filings|Explicit jurisdiction and obligation inventory; positive required count; not a compliance opinion''',
'financial_reporting_quality':'''bank_accounting_match_share|Bank-to-books match share|ratio|Matched bank-side absolute value divided by eligible bank-side absolute value|Same currency/period; positive eligible value; timing/FX/fees reconciled explicitly
 statement_balance_discrepancy|Balance-sheet discrepancy|currency|Assets minus liabilities minus equity|Same-date complete statement and currency
 material_adjustment_share|Material accounting adjustments|ratio|Absolute supported adjustment value divided by absolute pre-adjustment eligible activity|Versioned materiality rule; positive activity; journal reversals handled
 books_closing_lag_days|Books closing lag|days|Days between accounting period end and supported closing/finalization date|Both dates; draft or unknown close state yields unavailable''',
'data_quality':'''observed_account_coverage|Declared-account coverage|ratio|Assessed declared accounts divided by known declared relevant accounts|Explicit declared account inventory and positive denominator; not all external accounts
 covered_history_days|Covered history|days|Count fully covered days across the required source/account set|Required source roster and gap-aware observed intervals
 stale_source_share|Stale required sources|ratio|Required sources exceeding configured freshness tolerance divided by required sources|Nonzero required-source count; source-specific freshness policy
 unclassified_transaction_share|Unclassified transactions|ratio|Unclassified eligible transaction count divided by eligible transaction count|Nonzero posted deduplicated population and versioned classification taxonomy
 reconciled_value_share|Reconciled financial value|ratio|Reconciled eligible absolute amount divided by eligible absolute amount|Same comparable matching universe and positive denominator''',
'forecasting_and_stress':'''projected_minimum_cash|Projected minimum cash|currency|Minimum closing cash in the defined forecast horizon|Versioned model or deterministic projection, explicit assumptions, horizon and complete starting balances
 stress_dscr|Stressed debt-service coverage|ratio|Scenario eligible cash flow divided by scenario existing/proposed debt service|Explicit parameter shocks, transmission method and positive complete debt service
 stress_residual_income|Stressed residual income|currency|Scenario verified net income minus scenario non-overlapping essential/housing/debt outgoings|Defined consumer scenario, exact payment terms and complete base components
 liquidity_shortfall|Projected liquidity shortfall|currency|Maximum of zero and required liquidity floor minus minimum projected cash|Institution-defined floor and supported forecast horizon; no default-probability interpretation
 break_even_revenue_decline|Break-even revenue decline|ratio|Smallest modeled proportional revenue reduction that breaches an explicit capacity threshold|Documented cost elasticity, search bounds, institution threshold and scenario model; no universal shock''',
'relationship_risk':'''related_party_receipts_share|Related-party receipts share|ratio|Identified related-party operating receipts divided by operating receipts|Evidence-supported relationships and positive operating receipts
 circular_flow_amount|Potential circular-flow amount|currency|Sum uniquely attributed flow amount in evidence-supported return paths|Versioned temporal/value matching and unique path attribution; suspicion requires review
 connected_counterparty_share|Connected-counterparty exposure|ratio|Exposure to evidence-linked counterparties divided by total covered counterparty exposure|Authorized relationship graph, positive exposure and declared edge types''',
'monitoring_change':'''revenue_change_from_baseline|Revenue change from baseline|ratio|Current comparable revenue minus baseline revenue divided by baseline revenue|Positive baseline revenue and compatible equal-length windows and calculation versions
 liquidity_change_from_baseline|Liquidity change from baseline|currency|Current unrestricted cash minus baseline unrestricted cash|Compatible account scope, currency, basis and source quality
 dscr_change_from_baseline|DSCR change from baseline|ratio|Current DSCR minus baseline DSCR|Comparable complete schedules, windows, methodology and lending scope
 obligation_growth_from_baseline|Debt change from baseline|ratio|Current total debt minus baseline debt divided by baseline debt|Positive baseline debt, compatible reporting scope and verified obligations'''
}

def catalog():
 dimensions=[];metrics=[]
 for key,audience,sources,label,rule in DIMENSIONS:
  types=['business','person'] if audience=='both' else [audience]
  dimensions.append({'key':key,'label':label,'borrower_types':types,'source_families':sources.split(),'eligibility':rule})
  for row in ROWS[key].strip().splitlines():
   metric,label,unit,formula,inputs=[v.strip() for v in row.split('|')]
   metrics.append({'key':metric,'dimension_key':key,'label':label,'description':label+'. '+formula+'.','unit':unit,'formula':formula,'required_inputs':[x.strip() for x in inputs.split(';')],'eligibility':rule,'borrower_types':(['business'] if metric=='business_age_months' else types),'source_families':sources.split(),'definition_version':VERSION,'calculation_version':'amlok-'+metric+'-1','window_rule':'Return the actual UTC observation window and as-of date. Point-in-time metrics use dated observations; period, cohort and prior-period requirements above are mandatory. No silent annualization.','unavailable_rule':'Return null with a typed reason when inputs, coverage, entitlement or a valid denominator are missing. Do not replace missing values with zero.','interpretation':'Ratios are fractions, not percentages. Amounts have an explicit currency. A metric is an assessment input, not an institution decision.'})
 business_only={'current_ratio','quick_ratio','cash_ratio','debt_to_assets','debt_to_equity','net_debt_to_ebitda','top_customer_share','top_five_customer_share','top_supplier_share','top_channel_share','customer_hhi','eligible_receivables','stress_dscr','break_even_revenue_decline','revenue_change_from_baseline','dscr_change_from_baseline'}
 person_only={'income_source_hhi','stress_residual_income'}
 for metric in metrics:
  if metric['key'] in business_only: metric['borrower_types']=['business']
  if metric['key'] in person_only: metric['borrower_types']=['person']
 assert len({m['key'] for m in metrics})==len(metrics)
 return {'version':VERSION,'dimensions':dimensions,'metrics':metrics}

if __name__=='__main__':
 c=catalog();print(json.dumps({'dimensions':len(c['dimensions']),'metrics':len(c['metrics'])}))

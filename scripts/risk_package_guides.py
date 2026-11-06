"""Public risk-package reference generated from the same metric definitions as OpenAPI."""
from copy import deepcopy
import json
from pathlib import Path
from risk_package_catalog import catalog, VERSION
from risk_package_contract import decorate, available, example_input, recount
ROOT=Path(__file__).resolve().parent.parent

def save(path,value): (ROOT/path).write_text(json.dumps(value,indent=2)+'\n')
def page(path,title,description,body): (ROOT/path).write_text('---\ntitle: '+json.dumps(title)+'\ndescription: '+json.dumps(description)+'\n---\n\n'+body.strip()+'\n')
def find(p,key):return next(m for d in p['dimensions'] for m in d['metrics'] if m['key']==key)

def rich_examples(f):
 business=deepcopy(f['RiskPackage']);business['id']='rp_business_comprehensive_synthetic';business['evidence_set'].update(id='es_comprehensive_synthetic',count=3)
 business['document_ids']=['doc_capacity_synthetic','doc_debt_synthetic']
 business['sources'][0]['status']='complete';business['sources'][0]['limitations']=['Coverage is complete for the synthetic assessed account and period only.']
 for key,value in [('operating_cash_inflows','600000.00'),('operating_cash_outflows','480000.00'),('operating_net_cash_flow','120000.00')]:
  inputs=[example_input('operating_receipts','600000.00',evidence_id='ev_capacity_synthetic',field_path=None)]
  if key!='operating_cash_inflows':inputs.append(example_input('operating_payments','480000.00',evidence_id='ev_capacity_synthetic',field_path=None))
  if key=='operating_cash_outflows':inputs=inputs[1:]
  for i in inputs:i['evidence'][0].update(document_id='doc_capacity_synthetic',page=1)
  available(business,key,value,inputs)
 # Pro forma affordability uses equal-length historical cash flow and next-year contractual service, never silently interchangeable windows.
 inputs=[example_input('eligible_cash_flow','120000.00',evidence_id='ev_capacity_synthetic',field_path=None),example_input('existing_annual_debt_service','10000.00',evidence_id='ev_debt_synthetic',field_path=None),example_input('proposed_annual_debt_service','50000.00',evidence_id='ev_debt_synthetic',field_path=None)]
 for i in inputs:i['evidence'][0].update(document_id='doc_capacity_synthetic' if i['name']=='eligible_cash_flow' else 'doc_debt_synthetic',page=1)
 inputs[2]['basis']='declared'
 m=available(business,'dscr','2.00',inputs);m['analysis_basis']='pro_forma';m['assumptions']=['Eligible historical cash flow for 2025-11-01 through 2026-10-31 is compared with contractual debt service for 2026-11-01 through 2027-10-31, both 12 months.','Historical cash flow is held constant for this capacity comparison; this is not a forecast or a default probability.','Synthetic proposed loan: CAD 50,000 principal, 0% interest, no fees, one maturity payment; the terms are illustrative, not an offered product.']
 for key,value,values in [('existing_debt_service','10000.00',inputs[1:2]),('proposed_debt_service','50000.00',inputs[2:]),('total_debt_service','60000.00',inputs[1:]),('residual_cash_after_debt','60000.00',inputs)]:
  debt_metric=available(business,key,value,deepcopy(values));debt_metric['analysis_basis']='pro_forma';debt_metric['assumptions']=deepcopy(m['assumptions'])
 business['lending_product']['definition']['repayment_frequency']='at_maturity';business['lending_product']['definition']['pricing']['annual_interest_rate']='0.00'
 business['policy_results'][0].update(result='pass',actual='2.00',explanation='Illustrative pro forma DSCR 2.00 is above this institution example threshold 1.25. Other missing dimensions still require review.')
 business['assessment'].update(summary='Supported cash flow covers the illustrated pro forma annual debt service twice. Remaining evidence gaps require review.',reasons=['Illustrative DSCR policy passes.','Other required underwriting evidence remains incomplete.'])
 business['required_actions']=[{'code':'complete_underwriting_evidence','description':'Resolve remaining required evidence gaps before an institution decision.','metric_keys':['tax_overdue_amount'],'requirement_ids':[]}]
 business['findings']=[{'id':'finding_capacity_synthetic','code':'capacity_policy_satisfied','dimension_key':'repayment_capacity','severity':'info','nature':'calculation','summary':'Pro forma debt-service coverage is 2.00.','explanation':'CAD 120,000 eligible annual cash flow / (CAD 10,000 existing + CAD 50,000 proposed annual debt service). Assumptions and periods are explicit.','metric_keys':['dscr'],'evidence':[i['evidence'][0] for i in inputs],'limitations':['An illustrative policy result is not an institution approval.']}]
 obligations=[]
 for proposed,amount,identifier in [(False,'10000.00','debt_existing_synthetic'),(True,'50000.00','debt_proposed_synthetic')]:
  obligations.append({'id':identifier,'creditor_reference':'lender_synthetic','kind':'term_loan','basis':'declared' if proposed else 'observed','proposed':proposed,'currency':'CAD','outstanding':amount,'limit':None,'annual_rate':'0.00','maturity_date':'2027-10-31','secured':False,'payment_schedule':[{'due_at':'2027-10-31T00:00:00Z','principal':amount,'interest':'0.00','fees':'0.00','balloon':True}],'coverage':'complete','missing_fields':[],'evidence':[inputs[1]['evidence'][0]]})
 business['analyses']['obligations']={'status':'available','reason':None,'evidence_ids':['ev_debt_synthetic'],'items':obligations}
 reconciliation={'id':'recon_synthetic','left_source':'accounting_synthetic','right_source':'bank_synthetic','window':deepcopy(business['scope']['window']),'currency':'CAD','left_total':'610000.00','right_total':'600000.00','adjustments':[{'kind':'timing','amount':'-10000.00','explanation':'Supported sales still in accounts receivable at period close.','evidence':[inputs[0]['evidence'][0]]}],'adjusted_left_total':'600000.00','residual':'0.00','tolerance':'1.00','result':'matched','evidence':[inputs[0]['evidence'][0]]}
 business['analyses']['reconciliations']={'status':'available','reason':None,'evidence_ids':['ev_capacity_synthetic'],'items':[reconciliation]}
 business['sources'].append({'connection_id':'con_accounting_synthetic','integration_id':'accounting_synthetic','source_as_of':'2026-11-01T00:00:00Z','retrieved_at':business['as_of'],'window':deepcopy(business['scope']['window']),'status':'complete','limitations':['Complete only for the synthetic assessed entity and stated period.']})
 business['limitations'].append('Comprehensive example: source statements and obligations are synthetic. Other catalog metrics remain explicitly unavailable; no completeness, score or peer percentile is inferred.')
 consumer=decorate(f['RiskPackage'],'person');consumer['id']='rp_consumer_comprehensive_synthetic';consumer['lending_product']['definition']['borrower_type']='person';consumer['risk_policy']['definition']['borrower_type']='person'
 consumer['lending_product']['definition'].update(minimum_amount={'amount':'1000.00','currency':'CAD'},repayment_frequency='monthly')
 consumer['lending_product']['definition']['pricing']['annual_interest_rate']='0.00'
 consumer['application'].update(requested_amount={'amount':'3600.00','currency':'CAD'},purpose='Personal expenses',application_schema_id='consumer_app_schema_synthetic',declared_data={'gross_monthly_income':'6000.00','monthly_debt_payments':'1200.00'})
 consumer['risk_policy']['definition']['rules']=[{'id':'dti-test','dimension_key':'debt_to_income','calculation_version':'amlok-debt_to_income-1','operator':'lte','threshold':'0.40','unit':'ratio','on_missing':'review','on_fail':'review'}]
 win={'start':'2026-10-01T00:00:00Z','end':'2026-11-01T00:00:00Z'}
 gross=example_input('gross_monthly_income','6000.00',evidence_id='ev_payroll_synthetic',field_path=None);net=example_input('net_monthly_income','4500.00',evidence_id='ev_payroll_synthetic',field_path=None)
 for i in [gross,net]:i['evidence'][0].update(document_id='doc_payroll_synthetic',page=1)
 existing=example_input('existing_monthly_debt','1200.00',evidence_id='ev_consumer_debt_synthetic',field_path=None);proposed=example_input('proposed_monthly_debt','300.00',evidence_id='ev_consumer_debt_synthetic',field_path=None)
 for i in [existing,proposed]:i['evidence'][0].update(document_id='doc_consumer_debt_synthetic',page=1)
 proposed['basis']='declared'
 for key,value,values in [('verified_gross_monthly_income','6000.00',[gross]),('verified_net_monthly_income','4500.00',[net]),('debt_to_income','0.25',[gross,existing,proposed])]:available(consumer,key,value,deepcopy(values),win)
 dti=find(consumer,'debt_to_income');dti['analysis_basis']='pro_forma';dti['assumptions']=['One-month verified gross-income basis; existing debt includes required housing debt without duplication.','Proposed CAD 3,600 loan: 12 equal monthly principal payments of CAD 300, 0% interest and no fees; synthetic terms only.']
 consumer['policy_results']=[{'rule_id':'dti-test','metric_key':'debt_to_income','result':'pass','actual':'0.25','threshold':'0.40','unit':'ratio','explanation':'(1200 + 300) / 6000 = 0.25; this example rule passes, while other required evidence remains incomplete.','evidence_ids':dti['evidence_ids'],'calculation_version':dti['calculation_version'],'metric_window':win}]
 consumer['assessment'].update(summary='Verified gross income supports an illustrated DTI of 25%; other required evidence remains incomplete.',reasons=['Illustrative DTI rule passes.','Resolve remaining evidence gaps.'])
 consumer['sources']=[{'connection_id':'con_payroll_synthetic','integration_id':'payroll_synthetic','source_as_of':'2026-11-01T00:00:00Z','retrieved_at':consumer['as_of'],'window':deepcopy(consumer['scope']['window']),'status':'partial','limitations':['Only income and debt inputs are illustrated; full expenses and assets are not established.']}]
 consumer['evidence_set'].update(id='es_consumer_synthetic',count=2);consumer['document_ids']=['doc_payroll_synthetic','doc_consumer_debt_synthetic']
 consumer['analyses']['income_streams']={'status':'available','reason':None,'evidence_ids':['ev_payroll_synthetic'],'items':[{'id':'income_synthetic','kind':'employment','payer_reference':'employer_synthetic','basis':'observed','gross_monthly':'6000.00','net_monthly':'4500.00','currency':'CAD','cadence':'monthly','first_observed_at':'2026-01-31T00:00:00Z','last_observed_at':'2026-10-31T00:00:00Z','verification':'verified','evidence':[gross['evidence'][0]]}]}
 consumer['required_actions']=[{'code':'complete_expenses','description':'Provide supported essential spending and complete liquid reserves for residual-income analysis.','metric_keys':['essential_monthly_spend','liquid_reserve_months'],'requirement_ids':[]}]
 signal=deepcopy(business);signal.update(id='rp_signal_comprehensive_synthetic',product='signal',monitoring_run_id='mr_synthetic',deal_snapshot_id='ds_synthetic',previous_package_id=business['id'])
 signal['analyses']['changes']={'status':'available','reason':None,'evidence_ids':find(signal,'dscr')['evidence_ids'],'items':[{'metric_key':'dscr','previous_package_id':business['id'],'comparable':True,'reason':None,'previous_value':'2.00','current_value':'2.00','absolute_delta':'0.00','relative_delta':'0.00','evidence_ids':find(signal,'dscr')['evidence_ids']}]}
 signal['analyses']['changes']['items'][0]['reason']=None
 m=available(signal,'dscr_change_from_baseline','0.00',[example_input('baseline_dscr','2.00','ratio','ev_capacity_synthetic',None),example_input('current_dscr','2.00','ratio','ev_capacity_synthetic',None)])
 m['analysis_basis']='pro_forma';m['assumptions']=['Comparable frozen annual windows, sources, loan terms and calculation version; no new cash-flow change in this illustrative follow-up.']
 for metric_ in [m for d in signal['dimensions'] for m in d['metrics'] if d['key']=='monitoring_change' and m['key']!='dscr_change_from_baseline']:
  if signal['scope']['borrower_type'] in next(x for x in catalog()['metrics'] if x['key']==metric_['key'])['borrower_types']:metric_.update(status='unavailable',reason_code='no_comparable_baseline',missing_reason='No supported comparable baseline metric is included.')
 return {k:recount(v) for k,v in [('business',business),('consumer',consumer),('signal',signal)]}


def write_guides(spec,f,index):
 c=catalog();save('downloads/underwriting-metric-catalog.json',c)
 examples=rich_examples(f)
 for name,value in examples.items():save('downloads/risk-package-'+name+'-example.json',value)
 page('api-reference/risk-package.mdx','Risk package','Read underwriting results, financial dimensions, evidence and monitoring changes.', '''
A risk package is the immutable assessment returned by Insights or Signal. It combines your application, product and risk-policy versions with authorized integration data and documents. You receive the underlying facts, calculated dimensions, supporting analyses and evidence references through the same API.

## What you receive

| Section | Purpose |
| --- | --- |
| `scope` | Borrower type, market, currency, assessed period, entities, accounts, consolidation and excluded sources. |
| `assessment` | Your policy outcome and review reasons. `is_institution_decision` is always `false`; your institution makes the lending decision. |
| `dimensions` | 24 assessment families with 149 defined metrics. Every metric appears once with `available`, `unavailable` or `not_applicable` status. |
| `completeness` | Counts of each availability state. Coverage measures evidence availability, not creditworthiness. |
| `findings` | Explained observations, inconsistencies and risk signals with metric keys and exact evidence locations. |
| `policy_results` | Each evaluated rule, actual value, threshold, calculation version, window and evidence. |
| `analyses` | Verification checks, financial statements, debt schedules, income streams, reconciliations, concentrations, collateral, ownership/related parties, credit reports, tax obligations, projections, benchmarks, eligible model outputs and monitoring changes. |
| `required_actions` | Missing information or review steps; links to origination requirements when a collection action exists. |
| `sources`, `evidence_set`, `document_ids` | Source freshness, coverage, immutable evidence and controlled file access. |
| `versions` and `catalog_version` | Exact schema, normalization, calculation, model and metric-definition versions. |

Use the [dimension and metric dictionary](/api-reference/underwriting-dimensions) for each formula, unit, input requirement and applicability rule. Use the [methodology](/api-reference/risk-package-methodology) for consolidation, missing data, period alignment and interpretation.

## Retrieve and inspect a result

1. Submit your borrower, application, product, policy, connection IDs and documents through [origination](/api-reference/workflows).
2. Receive `origination.completed`, then retrieve the origination's `risk_package_id` through [Get risk package](/api-reference/endpoints/results/get-risk-package).
3. Read `scope`, `completeness`, `assessment` and `required_actions` before interpreting a metric. Read all rule outcomes; a package with required missing evidence needs review.
4. Use [List evidence](/api-reference/endpoints/evidence/list-evidence) with the package's `evidence_set.id`, then retrieve the exact frozen evidence record. Metric inputs and findings link to record fields or document pages.
5. Use [Data access](/api-reference/data-access) for normalized records and permitted source payloads. Use [Documents](/api-reference/documents) for controlled downloads. Source restrictions remain explicit; provider credentials are never exposed.
6. Export the same package and evidence using [Exports](/api-reference/workflows#exports) when you need an offline archive.

You do not configure provider jobs, enrichment pipelines or internal calculation services. The Hub captures connection authorization; Insights and Signal produce the assessment and traceable outputs.

## Available does not mean complete underwriting

An available metric has a decimal value, unit, currency when monetary, exact window, calculation version, input values and evidence. A ratio of `0.25` means 25%. A missing or inapplicable value is `null` with a reason; it is never substituted with zero.

An individual source can support cash-flow metrics without supporting complete debt, profitability or collateral analysis. All 149 catalog entries are accounted for, but only applicable metrics with sufficient entitled evidence have values. The connected-source set does not prove that every external account or liability is known.

## Examples

All examples use synthetic borrowers, sources, amounts, IDs and hashes. They demonstrate different evidence coverage, not recommended lending thresholds or investment advice.

- [Partial assessment](/downloads/risk-package-example.json): an observed inflow is available while debt-service coverage is unavailable.
- [Business assessment](/downloads/risk-package-business-example.json): cash-flow calculations, pro forma DSCR, debt schedule, a bank-to-accounting reconciliation and evidence-linked findings.
- [Consumer assessment](/downloads/risk-package-consumer-example.json): independently verified gross/net income and pro forma debt-to-income, with missing affordability inputs explicit.
- [Signal assessment](/downloads/risk-package-signal-example.json): the same result structure with a monitoring run, exact deal snapshot and comparable baseline changes.
- [Machine-readable metric catalog](/downloads/underwriting-metric-catalog.json): all definitions and calculation versions.

A package does not imply a bureau report, collateral valuation, benchmark percentile or calibrated risk model exists for every borrower. Those analyses require applicable evidence and entitlement. Their sections explain why a result is unavailable instead of fabricating one.
''')
 body='''Every risk package accounts for the following 24 dimension families and 149 metric definitions. A value is available only when its applicability, evidence, history and denominator requirements are met. The [machine-readable catalog](/downloads/underwriting-metric-catalog.json) is generated from the same definitions used by the API and console Data Lookup.\n\n`GET /v1/configuration` returns the entitled scalar definitions in `dimensions`. These are the keys accepted by `PolicyRule.dimension_key`; a family such as `liquidity` is not itself a scalar policy field. An API key can have access to a subset of the public catalog.\n\nRatios are fractions; currency metrics use `scope.reporting_currency`. Counts and durations are nonnegative; the cash conversion cycle can be negative when suppliers are paid after cash is collected. Unsupported values are null with explicit reasons. [Calculation and interpretation rules](/api-reference/risk-package-methodology) apply to every entry.\n\n'''
 for d in c['dimensions']:
  body+='## '+d['label']+'\n\n'+d['eligibility']+'\n\nSources: '+', '.join(d['source_families'])+'.\n\n'
  for m in [m for m in c['metrics'] if m['dimension_key']==d['key']]:
   body+='### '+m['key']+'\n\n**'+m['label']+'** · `'+m['unit']+'` · '+', '.join(m['borrower_types'])+'\n\n'+m['formula']+'.\n\nRequired inputs and conditions: '+'; '.join(m['required_inputs'])+'.\n\nCalculation version: `'+m['calculation_version']+'`.\n\n'
 page('api-reference/underwriting-dimensions.mdx','Underwriting dimensions','Definitions, formulas, evidence requirements and applicability for 149 risk metrics.',body)
 page('api-reference/risk-package-methodology.mdx','Risk-package methodology','Interpret financial metrics, missing data, forecasts, policy results and source evidence.',METHODOLOGY)
 nav=json.loads((ROOT/'docs.json').read_text());tab=next(t for t in nav['navigation']['tabs'] if t['tab'].lower()=='api reference')
 for group in tab['groups']:
  if 'api-reference/risk-package' in group.get('pages',[]):
   pos=group['pages'].index('api-reference/risk-package')+1;group['pages'][pos:pos]=['api-reference/underwriting-dimensions','api-reference/risk-package-methodology']
 save('docs.json',nav)
 # Make the normalized-data versus assessment distinction discoverable without replacing the source dictionary.
 path=ROOT/'data-model/derived-attributes.mdx'
 if path.exists():
  text=path.read_text();notice='\n## Underwriting assessment metrics\n\nFor the complete risk-package metric definitions, formulas and availability rules, use the [underwriting dictionary](/api-reference/underwriting-dimensions). The fields on this page describe normalized data attributes; they are not the complete assessment catalog.\n'
  if '## Underwriting assessment metrics' not in text:path.write_text(text+notice)

METHODOLOGY='''
## Assessment boundaries

Read the package's borrower type, market, period, reporting currency, account/entity scope and exact product/policy versions before consuming its results. The scope is either the sources observed or the declared sources reconciled against evidence; neither claims visibility into unknown external accounts. Consolidated assessments eliminate supported inter-account and intercompany transfers without deleting the original records. Joint or related-party assessments require authorized borrower relationships and explicit allocation.

Every catalog metric appears exactly once in its assigned dimension. All 24 dimension families appear exactly once. Every metric and every analysis section states availability. A dimension is `available` when all applicable metrics are available, `partial` when some are available, `unavailable` when no applicable metric is available, and `not_applicable` when no metric applies. Completeness counts reconcile to the emitted metrics. A section with an empty list and no explanation does not represent a clean assessment.

## Values, units and periods

- Monetary values are decimal strings with an explicit ISO currency; ratios are fractions, not percentage points. Preserve precision in storage. Round displayed ratios to at most six decimal places, with half-even rounding; do not round inputs before calculations or policy comparisons.
- Sum amounts only on the same currency basis. Currency conversion records the positive rate, source, timestamp and evidence. The reported metric uses the package reporting currency; original amounts remain in source records.
- A window is a UTC interval `[start, end)`. Point-in-time metrics carry an `as_of` date. Record actual observation coverage, missing days, accounting basis and consolidation. Never assume missing bank days have zero transactions.
- `analysis_basis` distinguishes historical, pro forma and scenario results. Pro forma repayment capacity can compare historical eligible cash flow with prospective debt service only for equal-length periods, with both periods and the unchanged-cash-flow assumption explicit. It is not a forecast. A historical DSCR uses cash flow and debt service from the same period.
- Compare growth only across compatible populations and periods. Year-over-year needs the comparable prior-year window, not a shorter interval annualized without disclosure. Volatility specifies complete periods and uses population standard deviation. Seasonal or irregular data does not silently become recurring income.
- Daily balance metrics require reliable daily balances or a reconciled reconstruction. A point balance does not establish a full history. Per-account negative days are combined as a union for an all-account day count.
- A zero or invalid denominator produces `unavailable` with `invalid_denominator`, not infinity, 999 or an automatic policy pass. A nonpositive EBITDA or equity denominator is not a healthy leverage ratio. Negative cash flow and losses remain negative where the definition permits them.

## Missingness and quality

Metric `reason_code` identifies missing source, insufficient history, stale source, incomplete coverage, restricted source, invalid denominator, conflicting evidence, unsupported scope, not applicable, not evaluated, no comparable baseline or model ineligibility. `missing_reason` explains the specific cause and required input.

An available metric has non-null input values, evidence IDs and exact calculation/definition versions. Its evidence IDs match the union of its input evidence references. Declared, observed, derived and estimated bases remain distinct. An estimated result includes its assumptions and cannot be described as verified. An unavailable metric has a null value and a reason; a genuine measured zero retains evidence and an available status.

Missing or stale data does not prove financial distress or fraud. It can require review or prevent a required rule from being evaluated. Do not turn source coverage into a creditworthiness score. A missing mandatory policy input always produces `review_required`.

## Cash flow and accounting

Retain original transactions and normalized records. Calculation populations use posted, deduplicated records. Pending transactions, duplicates, transfers, financing proceeds, owner injections, refunds, taxes, processor fees and capital expenditures have explicit treatments appropriate to each metric. Gross deposits, cash sales, accrual revenue, gross profit, EBITDA and free cash flow are different quantities.

Reconciliations compare aligned populations, currencies and dates. The bridge is `adjusted_left_total = left_total + signed adjustments` and `residual = adjusted_left_total - right_total`. A matched result requires complete comparable populations and an absolute residual within the documented nonnegative tolerance. Timing, refunds, tax, fees and FX adjustments require evidence. A mismatch alone is not fraud.

Statements preserve line hierarchy and sourced adjustments. Do not add both subtotal lines and their children. EBITDA addbacks are itemized and justified, not automatically approved because a borrower supplied them. Receivable/payable aging uses due dates and allocated settlements; net working capital and cash-conversion-cycle calculations use comparable statement periods. HHI uses squared fractional shares and identifies unallocated exposure; unknown counterparties cannot silently disappear.

## Repayment and affordability

DSCR uses eligible cash flow and complete existing plus proposed required debt service over comparable periods. Include principal, interest, fees, balloon obligations and variable-payment assumptions. Do not substitute arbitrary bank debits for a complete debt schedule. Recurring payments can suggest an obligation while principal, rate or maturity remain unknown. Distinguish observed, declared and inferred obligations.

Consumer DTI uses supported gross income and monthly required existing plus proposed debt payments. Net deposits alone do not establish gross income. Payroll/tax evidence identifies gross, deductions and net amounts. Weekly income converts by `52/12`, biweekly by `26/12`, semimonthly by `2`; irregular income needs its own supported observation window and method. Include housing exactly once. Residual income uses net income less nonoverlapping essential expenses, housing and debt service. Household allocation requires authorized joint scope; do not infer household liabilities from co-location.

Each policy rule pins its calculation version from configuration discovery. A calculation change requires a new immutable policy version. A policy result refers to the exact metric key, value, window, unit and pinned calculation version. Missing inputs cannot pass a rule. Approved product/policy definitions determine the comparison; the public examples' thresholds are illustrative, not universal credit standards. An institution decision, offer, adverse-action notice or regulatory finding is not implied by an AMLOK recommendation.

## Evidence and verification

Every finding cites immutable evidence in the package evidence set. A JSON pointer identifies a source field; document evidence identifies a document and one-based page. Preserve provider name, observation date, identity matching status and permitted report access. KYB/KYC or account ownership checks cannot establish financial capacity, and a suspected document anomaly is not a confirmed fraud finding.

A source restriction can permit a derived attribute while preventing redistribution of an underlying licensed report. Return the permitted result with its lineage and explicit access restriction. Retrieve raw/source values, normalized records, documents and provider reports using the data/evidence endpoints under the same workspace, environment, consent and license boundaries. Never expose provider credentials, unrelated borrowers or unlicensed reports.

## Projections, stress and benchmarks

Baseline forecasts and stress scenarios state their model version, future horizon, starting balances, assumptions, shock units and limitations. Typical supported parameters include revenue/income changes, collection delays, cost changes, interest-rate resets and customer loss, when the necessary source data exists. Output series retain their dates, units, currency and evidence. Deterministic stress results are conditional arithmetic, not calibrated probabilities. A statistical interval states its level, method and calibration reference; its bounds must be ordered and its level between zero and one.

Benchmarks require an eligible, entitled cohort with market, industry when relevant, borrower type, size band when relevant, time period, sample size, source and methodology. Percentiles are fractions from zero to one. If those conditions are not established, return an unavailable benchmark section; do not manufacture industry percentiles.

PD, LGD, expected loss and provider scores require an applicable validated model, target definition, horizon, population, market, version, calibration date, reason codes and limitations. A provider score retains its original scale. A heuristic score, missing-data count or stress DSCR is not a default probability. No model output is returned as available solely because the schema supports it.

Use authorized financial evidence and purpose-appropriate identity checks. Protected personal characteristics and inferred sensitive merchant/behavioral attributes are not underwriting metric inputs. Regulatory eligibility, provider licensing and institutional model governance determine which analyses can be returned in the relevant market; availability in one market does not imply availability in another.

## Signal and change detection

Signal uses the same dimensions and definitions, linked to an exact monitoring run and lender deal snapshot. Each change identifies its baseline package, current value, previous value and comparability. The absolute delta is current minus previous. The relative delta uses a positive previous value; otherwise it is null. Incompatible units, currency, account scope, periods, calculation versions or source quality make numeric deltas null with an explanation.

An unavailable sync is not evidence that an alert condition resolved. Only fresh comparable evidence can support a resolved condition. A re-evaluation appends a new package and evidence set; it never rewrites prior findings, policy results, loan snapshots or billing usage.
'''

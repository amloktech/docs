"""Workspace agreements and assessed complexity; shared by reference and lookup."""
from copy import deepcopy

def extend(spec, fixtures):
    s = spec['components']['schemas']
    amount = {'type':'string','pattern':r'^(0|[1-9][0-9]*)\.[0-9]{2}$','description':'CAD amount as an exact decimal string.'}
    def obj(properties, description):
        return {'type':'object','properties':properties,'required':list(properties),'additionalProperties':False,'description':description}
    assessment = obj({'tier':{'type':'string','enum':['standard','advanced','complex']}, 'assessed_at':{'type':'string','format':'date-time'}, 'policy_version':{'type':'string','minLength':1}, 'basis':{'type':'string','enum':['amlok_assessment','sandbox_fixture']}, 'rationale':{'type':'string','minLength':1}}, 'Amlok-assessed analysis complexity and its explanation. Sandbox uses deterministic synthetic business assessments. Request counts, record volume, approval/decline and customer-submitted tier claims do not determine price.')
    commitment = obj({'monthly_minimum':amount,'payment_cadence':{'type':'string','enum':['quarterly','annual']},'months_per_payment':{'type':'integer','enum':[3,12]},'payment_amount':amount,'currency':{'const':'CAD'},'treatment':{'const':'wallet_funding'}},'Negotiated funding commitment. Gross prepayment = monthly minimum × 3 quarterly or × 12 annually. Apply the separately agreed prepayment discount to obtain payment_amount, rounded to two CAD decimals using half-up rounding. The nominal monthly minimum and product rates are unchanged. Funds credit the wallet on settlement. This is not an additional usage deduction, payment instruction, invoice or proof of payment.')
    commitment['properties']['pre_discount_payment_amount']={**amount,'description':'Gross CAD prepayment before its negotiated discount: monthly_minimum × months_per_payment. Present on new snapshots; may be absent on historical snapshots.'}
    commitment['properties']['prepayment_discount_percent']={'type':'number','minimum':0,'maximum':100,'description':'Agreed prepayment-only discount percentage, reported to at most two decimal places. 20 means 20%, not 0.20. Does not reduce monthly_minimum or apply again to product effective_rate. Present on new snapshots; may be absent on historical snapshots.'}
    commitment['properties']['payment_amount']={**amount,'description':'Net agreed CAD prepayment after the prepayment-only discount, rounded half-up to two decimals. This stored amount is authoritative for the snapshot; it is not proof that payment settled.'}
    commitment['properties']['monthly_minimum']={**amount,'description':'Nominal monthly CAD commitment before any prepayment-only discount. This is not a separate monthly usage deduction.'}
    s['BillingComplexityAssessment'] = assessment
    s['BillingCommitment'] = commitment
    details = obj({key:deepcopy(s['BillingUsage']['properties'][key]) for key in ['tier','quantity','unit_rate','rate_card_id','rate_version']}, 'Historical pricing used for this usage debit; absent on funding and on older records without pricing metadata.')
    details['properties']['complexity_assessment']={'$ref':'#/components/schemas/BillingComplexityAssessment'}
    details['required'].append('complexity_assessment')
    s['BillingChargeDetails']=details
    s['BillingTransaction']['properties']['charge_details']={'$ref':'#/components/schemas/BillingChargeDetails'}
    s['BillingUsage']['properties']['complexity_assessment']={'$ref':'#/components/schemas/BillingComplexityAssessment'}
    s['BillingUsage']['properties']['workload']['description']='Observed processing counts for operational visibility. These are not the billing quantity and do not select a complexity price.'
    s['BillingUsage']['properties']['tier']['description']='Amlok-assessed complexity. Signal pins the assessed tier and rate for the borrower-month; later evaluations do not create another charge. Reassessed complexity and revised rates apply to the next new billing month.'
    s['BillingSummary']['properties']['pricing']={'$ref':'#/components/schemas/FinancialBillingRateCard','description':'Current workspace agreement captured at this billing snapshot; includes all six rates and the funding commitment. Present on new snapshots. For historical costs use each usage record’s rate_card_id and rate_version.'}
    s['FinancialBillingRateCard']['properties']['commitment']={'$ref':'#/components/schemas/BillingCommitment'}
    s['FinancialBillingRate']['properties']['discount_percent']['description']='Informational discount from the published base rate, rounded to two decimals. Zero when the negotiated price is at or above the base. effective_rate is the authoritative charge rate; do not apply the discount a second time.'
    s['FinancialBillingWorkloadLimits']['description']='Agreed operational capacity, separate from Amlok’s analysis-complexity assessment. Increasing request or record counts does not automatically change the charged tier.'
    s['ReportBillingUsage']['properties']['rate_version']=deepcopy(s['BillingUsage']['properties']['rate_version'])
    s['ReportBillingUsage']['properties']['complexity_assessment']={'$ref':'#/components/schemas/BillingComplexityAssessment'}
    stamp='2026-11-07T12:00:00Z'
    assessment_example={'tier':'standard','assessed_at':stamp,'policy_version':'sandbox-complexity-1','basis':'sandbox_fixture','rationale':'Single domestic entity with straightforward operating finances.'}
    card={'id':'pricing_ws_synthetic_1','object':'billing_rate_card','record_version':1,'created_at':stamp,'updated_at':stamp,'workspace_id':'ws_synthetic','currency':'CAD','effective_from':stamp,'effective_to':None,'agreement_id':'agreement_ws_synthetic','agreement_version':'1','supersedes_id':None,'snapshot_id':'snap_synthetic','commitment':{'monthly_minimum':'1000.00','payment_cadence':'annual','months_per_payment':12,'payment_amount':'12000.00','pre_discount_payment_amount':'12000.00','prepayment_discount_percent':0,'currency':'CAD','treatment':'wallet_funding'},'rates':[]}
    for product, prices in [('insights',['8.00','25.00','45.00']),('signal',['5.00','8.00','12.00'])]:
        for tier, price in zip(['standard','advanced','complex'],prices):
            card['rates'].append({'product':product,'tier':tier,'unit':'completed_underwriting' if product=='insights' else 'active_account_month','base_rate':price,'effective_rate':price,'discount_percent':'0','pricing_basis':'published','billing_timing':'successful_output_completion' if product=='insights' else 'month_start_or_first_activation','workload_limits':{'bank_accounts':8,'business_integrations':20,'record_limit':1000000,'record_counting_basis':'per_underwriting' if product=='insights' else 'new_records_per_month','record_counting_rule':'distinct_record_versions','minimum_banking_history_months':12 if product=='insights' else None,'analysis_scope':'Operational capacity; complexity is assessed separately by Amlok.'}})
    fixtures['BillingSummary']['pricing']=card
    usage=fixtures['BillingUsage']
    usage.update(unit_rate='8.00',amount='8.00',tier='standard',rate_card_id=card['id'],rate_version='1',complexity_assessment=assessment_example)
    # Keep example amounts internally reconciled: one eight-dollar Insights debit.
    fixtures['BillingSummary'].update(available_credits='4992.00',spent_credits='8.00')
    transaction=fixtures['BillingTransaction']
    if transaction['kind']=='usage':
        transaction.update(amount='-8.00',balance_after='4992.00',charge_details={key:deepcopy(usage[key]) for key in ['tier','quantity','unit_rate','rate_card_id','rate_version','complexity_assessment']})
    for methods in spec['paths'].values():
        for op in methods.values():
            oid=op.get('operationId','')
            resource='BillingSummary' if oid=='getBillingSummary' else 'BillingUsage' if oid in ['getBillingUsage','listBillingUsage'] else 'BillingTransaction' if oid in ['getBillingTransaction','listBillingTransactions'] else None
            if resource:
                op['description']+=' Complexity is assessed by Amlok, not selected by HTTP volume. Usage records preserve the original tier, rate and agreement version. Funding commitments are available in billing summary pricing.commitment.'
                for status,response in op['responses'].items():
                    if status.startswith('2'):
                        example=response['content']['application/json']['example']
                        example['data']=[deepcopy(fixtures[resource])] if isinstance(example['data'],list) else deepcopy(fixtures[resource])
    return spec


def write_billing_guides(root):
    p=root/'sandbox/simulated-billing.mdx'
    p.write_text(p.read_text().split("\n## Complexity examples")[0].rstrip()+"\n"+"""
## Complexity examples

Amlok assigns a deterministic synthetic assessment to each example business. Selecting approval, decline or another scenario does not alter its complexity. Your workspace's agreed rates apply to simulated usage.

| Business | Synthetic complexity | Published Insights / Signal monthly rate |
| --- | --- | --- |
| Maple Retail | Standard | CAD 8.00 / CAD 5.00 |
| Harbor Logistics | Advanced | CAD 25.00 / CAD 8.00 |
| Cedar Software | Advanced | CAD 25.00 / CAD 8.00 |
| Prairie Manufacturing | Complex | CAD 45.00 / CAD 12.00 |
| Summit Hospitality | Advanced | CAD 25.00 / CAD 8.00 |
| Atlas Wholesale | Complex | CAD 45.00 / CAD 12.00 |

Custom synthetic borrowers use Standard. Inspect `complexity_assessment` on usage for the rationale and policy version. One successful underwriting charges once. Multiple monitors for a borrower reuse its first paid UTC-month charge, including its original tier and price.

Billing summary `pricing` shows the current workspace rates, nominal monthly minimum, prepayment discount and net quarterly or annual payment amount. For example, a synthetic agreement with a CAD 1,000.00 monthly minimum and 20% quarterly prepayment discount shows CAD 3,000.00 before discount and CAD 2,400.00 payable. The discount does not apply again to product rates. Updating an agreement does not deposit credits, send an invoice or charge a payment method. All Sandbox funding and charges remain simulated.
""")

    p=root/'api-reference/credit-reporting.mdx'
    text=p.read_text()
    text=text.replace('quarterly or annual cadence, and calculated payment amount.', 'quarterly or annual cadence, gross prepayment, prepayment-only discount and net payment amount.')
    text=text.replace('quarterly funding at that minimum is CAD 3,000.', 'quarterly funding at that minimum is CAD 3,000 before any agreed prepayment discount.')
    p.write_text(text.split("\n## Negotiated prepayment discounts")[0].rstrip()+"\n"+"""
## Negotiated prepayment discounts

Read `pricing.commitment` as agreement terms, independently of individual funding transactions:

| Field | Meaning |
| --- | --- |
| `monthly_minimum` | Nominal monthly commitment before a prepayment discount |
| `months_per_payment` | 3 for quarterly or 12 for annual funding |
| `pre_discount_payment_amount` | Monthly minimum multiplied by months per payment |
| `prepayment_discount_percent` | Discount on that scheduled prepayment; `20` means 20% |
| `payment_amount` | Net prepayment after discount, rounded half-up to two CAD decimals |

For a synthetic CAD 1,000.00 monthly commitment with quarterly funding and a 20% prepayment discount, the gross amount is CAD 3,000.00 and `payment_amount` is `2400.00`. The monthly minimum remains `1000.00`. This discount does not reduce the six negotiated product rates again, change past charges or create promotional credit. Use settled funding and ledger records to determine the amount actually credited. Saving or editing terms does not collect money.

The gross amount and discount fields may be absent on historical snapshots. Use the snapshot's stored `payment_amount`; do not infer a zero discount or recompute history from the current agreement.
""")

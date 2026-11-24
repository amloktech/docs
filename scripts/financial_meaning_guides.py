"""Publish reading definitions without changing API schemas or calculation catalogs."""
import csv
import hashlib
import io
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads((ROOT / path).read_text())


def read_meanings(name):
    rows = list(csv.DictReader(io.StringIO((ROOT / 'data' / name).read_text()), delimiter='\t'))
    result = {r['key']: r['meaning'] for r in rows}
    assert len(result) == len(rows), 'Duplicate meaning key in ' + name
    return result


def clean(value):
    return str(value).replace('—', '-').replace('–', '-').replace('|', '&#124;')


def table(headers, rows):
    return '| ' + ' | '.join(headers) + ' |\n| ' + ' | '.join('---' for _ in headers) + ' |\n' + ''.join('| ' + ' | '.join(clean(x) for x in row) + ' |\n' for row in rows) + '\n'


def page(path, title, description, body, sidebar=None):
    front = {'title': title, 'description': description, 'keywords': ['API definitions', 'financial metrics', 'data dictionary']}
    if sidebar:
        front['sidebarTitle'] = sidebar
    (ROOT / path).write_text('---\n' + '\n'.join(k + ': ' + json.dumps(v) for k, v in front.items()) + '\n---\n\n' + body.replace('—', '-').replace('–', '-').strip() + '\n')


def append_section(path, marker, text):
    target = ROOT / path
    content = target.read_text()
    begin, end = '{/* BEGIN ' + marker + ' */}', '{/* END ' + marker + ' */}'
    block = begin + '\n' + text.replace('—', '-').replace('–', '-').strip() + '\n' + end
    if begin in content:
        content = re.sub(re.escape(begin) + r'.*?' + re.escape(end), lambda _: block, content, flags=re.S)
    else:
        content = content.rstrip() + '\n\n' + block + '\n'
    target.write_text(content)


STATISTICS = {
    'amount': 'Total money amount of the selected posted activity in one direction. It is not a net cash-flow or revenue figure.',
    'count': 'Number of distinct current posted transactions in the selection.',
    'amount_share': 'Selected activity as a share of all posted value in the same account context, currency, direction and period.',
    'mean': 'Average money amount of the selected transactions.',
    'median': 'Middle transaction amount, describing a typical transaction with less influence from extremes.',
    'p90': 'The transaction amount at the 90th percentile, describing the upper end of the observed amount distribution.',
    'maximum': 'Largest money amount of a selected transaction.',
    'stddev': 'Spread of the selected transaction amounts, expressed in currency units rather than a percentage.',
    'active_days': 'Number of distinct UTC posting dates with selected activity.',
    'days_since_last': 'Time since the latest selected posting, measured at the last complete day in the period rather than the retrieval date.',
}

AXES = {
    'account_contexts': ('Account context', 'The kind of account on which the activity is recorded.', {
        'depository': 'A deposit account holding cash.', 'credit': 'An issuer credit account, where a purchase and payment affect a liability.',
        'loan': 'A loan account recording borrowing and repayment activity.', 'unknown': 'The account context is not supported.'}),
    'cash_flow_roles': ('Cash-flow role', 'The economic role of the activity, separate from its cash effect.', {
        'operating_receipt': 'Receipt related to operating activity.', 'operating_payment': 'Payment related to operating activity.',
        'nonoperating_receipt': 'Receipt outside ordinary operations.', 'financing_receipt': 'Funds from financing or capital contributions.',
        'financing_payment': 'Debt settlement or a capital distribution.', 'investing_receipt': 'Receipt from investments or asset recovery.',
        'investing_payment': 'Payment for investments or asset acquisition.', 'internal_transfer': 'Movement within the relevant own-account scope.',
        'cash_movement': 'Movement involving physical cash with origin or use assessed separately.',
        'contra_receipt': 'Activity offsetting an earlier receipt.', 'contra_payment': 'Activity offsetting an earlier payment.',
        'unknown': 'The economic cash-flow role is unresolved.'}),
    'cash_effects': ('Cash effect', 'Whether the posting actually moves cash in the assessed context.', {
        'cash_inflow': 'Cash enters the account scope.', 'cash_outflow': 'Cash leaves the account scope.',
        'noncash': 'The activity does not move cash in this context, such as a credit-card purchase.', 'unknown': 'The cash effect is unresolved.'}),
    'balance_sheet_effects': ('Balance-sheet effect', 'The supported direction of the effect on assets, liabilities or equity.', {
        'asset_increase': 'Increases an asset balance.', 'asset_decrease': 'Decreases an asset balance.',
        'liability_increase': 'Increases an amount owed.', 'liability_decrease': 'Reduces an amount owed.',
        'equity_increase': 'Increases equity.', 'equity_decrease': 'Reduces equity.',
        'mixed': 'Has more than one balance-sheet effect or a combined effect.', 'unknown': 'The effect is unsupported.'}),
    'activity_bases': ('Activity basis', 'The nature of the recorded financial event.', {
        'adjustment': 'A correction or change to a recorded amount.', 'borrowing': 'Obtaining borrowed funds.', 'capital': 'An equity or owner-capital movement.',
        'cash': 'A physical-cash movement.', 'dispute': 'An event relating to a disputed payment.', 'fee': 'A separately identified service or financing charge.',
        'interest': 'A separately identified interest charge or receipt.', 'investment': 'An investment or longer-term asset movement.',
        'noncash_adjustment': 'An adjustment that does not move cash.', 'purchase': 'Acquiring goods or services.',
        'receipt': 'Receiving funds.', 'refund': 'Returning value from an earlier payment.', 'settlement': 'Discharging an amount due or settling prior activity.',
        'tax': 'A tax or statutory-remittance event.', 'transfer': 'Moving value between accounts or systems.', 'unknown': 'The event basis is unresolved.'}),
    'economic_roles': ('Economic role', 'Whether evidence supports business, personal or mixed use.', {
        'business': 'Supported business use.', 'personal': 'Explicitly supported non-business use.',
        'mixed': 'Documented business and non-business use.', 'unknown': 'Use is not supported by sufficient evidence.'}),
    'payment_rails': ('Payment rail', 'The normalized transfer mechanism or network label, not the economic purpose.', {
        'ACH': 'Automated Clearing House transfer.', 'EFT': 'Electronic funds transfer recorded as EFT.', 'INTERAC': 'Transfer through Interac.',
        'WIRE': 'Wire transfer.', 'SEPA': 'Transfer through the Single Euro Payments Area scheme.', 'SWIFT': 'Transfer identified through SWIFT messaging.',
        'CARD': 'Card-network payment.', 'CHECK': 'Cheque or check payment.', 'CASH': 'Physical cash.',
        'BOOK_TRANSFER': 'An internal book transfer between accounts.', 'OTHER': 'A known rail outside the listed values.', 'UNKNOWN': 'The rail is not established.'}),
    'payment_channels': ('Payment channel', 'Where or how the payment was initiated, separate from the rail.', {
        'in_store': 'At a physical point of sale.', 'online': 'Through an online channel.', 'mobile': 'Through a mobile channel.',
        'telephone': 'By telephone.', 'mail': 'By mail.', 'branch': 'At a financial-institution branch.', 'atm': 'At an automated teller machine.',
        'other': 'A known channel outside the listed values.', 'unknown': 'The initiation channel is unknown.'}),
    'card_event_types': ('Card event', 'The issuer-card event, separate from merchant sector and purchase purpose.', {
        'purchase': 'A purchase charged to the card.', 'settlement': 'Payment toward the card balance.', 'cash_advance': 'Borrowing cash through the card.',
        'balance_transfer': 'Moving a balance between credit facilities.', 'refund': 'Credit for a returned or refunded purchase.',
        'chargeback': 'A disputed payment adjustment.', 'fee': 'A separately identified card fee.', 'interest': 'A card interest charge.',
        'reward': 'A card reward or rebate.', 'reversal': 'Reversal of prior card activity.',
        'authorization': 'An authorization event that does not by itself establish a posted purchase.', 'unknown': 'The card-event type is unknown.'}),
    'counterparty_roles': ('Counterparty role', 'The supported role of the other party in the activity; a role does not verify identity.', {
        'customer': 'A purchaser of the business\'s goods or services.', 'supplier': 'A provider of goods or services.', 'employee': 'An employee of the business.',
        'contractor': 'A nonemployee service provider.', 'creditor': 'A party to whom a financial obligation is owed.', 'owner': 'An owner or equity holder.',
        'related_party': 'A party with a supported relationship to the subject.', 'tax_authority': 'A public authority receiving or returning taxes.',
        'insurer': 'An insurance provider.', 'processor': 'A payment processor or settlement intermediary.',
        'financial_institution': 'A bank or other financial institution acting as counterparty.',
        'other': 'A supported role outside the listed values.', 'unknown': 'The role is unresolved.'}),
}


def category_meaning(category, curated):
    key, label, group = category['id'], category['label'].lower(), category['parent_id']
    if key in curated:
        return curated[key]
    if group.startswith('expense.'):
        return 'Business spending for ' + label + '. The category identifies the supported purpose of the payment or purchase.'
    if group == 'financial.fee':
        return 'Separately identified ' + label + ', distinct from the principal value of the underlying payment, investment or borrowing.'
    if group == 'financial.interest':
        return 'Separately identified ' + label + ', distinct from repayment of borrowed principal.'
    if group == 'tax':
        return 'Payments or charges identified as ' + label + ' under the applicable jurisdiction.'
    if group == 'financing.debt_service':
        return 'Settlement of obligations through ' + label + '. The posting may combine principal and charges unless a supported split is available.'
    if group == 'investing.acquisition':
        return 'Payments for ' + label + ' recorded as supported asset or investment activity rather than an ordinary operating purchase.'
    if group == 'investing.disposal':
        return 'Receipts identified as ' + label + ', distinguished from ordinary operating sales.'
    raise AssertionError('Missing category meaning: ' + key)


def cross_meaning(d):
    """Expand repeated definitions; every non-repeated key has curated prose."""
    key = d['key'].removeprefix('cross_system.')
    parts = key.split('.')
    if parts[0] in ('ar', 'ap'):
        noun, party, action = ('customer invoices', 'customer', 'collection') if parts[0] == 'ar' else ('supplier bills', 'supplier', 'payment')
        prefix = 'Observed ' + noun
        suffix = '.'.join(parts[1:])
        if parts[1] == 'aging':
            bucket = {'current': 'not yet past due, including amounts due today', '1_30': '1-30 days past due', '31_60': '31-60 days past due', '61_90': '61-90 days past due', '91_120': '91-120 days past due', 'over_120': 'more than 120 days past due'}[parts[2]]
            return {'amount': 'Outstanding money owed on ', 'count': 'Number of open ', 'share': 'Portion of observed outstanding value on '}[parts[3]] + noun + ' that are ' + bucket + '. Age is measured from the payment due date.'
        if suffix.startswith('paid_document_days.'):
            return {'mean': 'Average', 'median': 'Middle', 'p90': '90th-percentile'}[parts[-1]] + ' time from issue to full ' + action + ' for observed ' + noun + ' fully paid within the reporting window.'
        return {
            'open_document_count': 'Number of observed non-draft, non-void ' + noun + ' with a positive balance still owed.',
            'observed_outstanding_amount': 'Total outstanding value of observed non-draft, non-void ' + noun + '. This does not establish the whole business\'s balance.',
            'weighted_days_past_due': 'Lateness of open ' + noun + ', weighted by outstanding value. Amounts not yet overdue contribute zero days.',
            'maximum_days_past_due': 'Age of the most overdue open ' + ('customer invoice' if parts[0] == 'ar' else 'supplier bill') + '. No open documents is not applicable.',
            'largest_counterparty_outstanding_share': 'Portion of observed outstanding value attributable to the largest identified ' + party + '.',
            'paid_document_late_share': 'Portion of observed ' + noun + ' fully paid in the window that were paid after their due dates.',
            'paid_document_mean_late_days': 'Average lateness among late ' + noun + ' fully paid in the window. On-time documents are excluded.',
            'partial_payment_outstanding_share': 'Portion of observed outstanding value on ' + noun + ' explicitly marked partially paid.',
            'issued_document_credit_share': 'Source-reported credits applied to ' + noun + ' issued in the window, relative to their original totals. This follows the issue cohort, not when credits or write-offs occurred.',
        }[suffix]
    if key.startswith('settlements.payout.'):
        state, stat = parts[2:]
        meaning = {'pending': 'awaiting processing', 'in_transit': 'in transit', 'paid': 'reported as paid', 'failed': 'reported as failed', 'cancelled': 'reported as cancelled'}[state]
        return ('Number' if stat == 'count' else 'Source-reported net value') + ' of observed payouts created in the window and currently ' + meaning + '. A payout status alone does not establish reconciled bank cash.'
    if key.startswith('payments.dispute.'):
        state = {'needs_response': 'requiring a response', 'under_review': 'under review', 'won': 'explicitly recorded as won', 'lost': 'explicitly recorded as lost', 'closed': 'closed without inferring whether they were won or lost'}[parts[2]]
        return 'Number of observed disputes opened in the window and currently ' + state + '.'
    if key.startswith('inventory.ownership.'):
        owner = {'owned': 'owned by the business', 'consigned': 'held under a consignment arrangement', 'third_party': 'classified as third-party inventory'}[parts[2]]
        return 'Recorded carrying value of observed inventory explicitly ' + owner + '. Carrying value is not liquidation value or confirmed collateral eligibility.'
    if key.startswith('inventory.expiry.'):
        expiry = {'expired': 'already expired before the assessment date', '0_30': 'expiring from today through 30 days ahead', '31_60': 'expiring 31-60 days ahead', '61_90': 'expiring 61-90 days ahead'}[parts[2]]
        what = {'carrying_value': 'Recorded carrying value', 'position_count': 'Number of recorded positions', 'value_share': 'Share of total observed carrying value'}[parts[3]]
        return what + ' for inventory ' + expiry + '. Missing expiry dates do not establish nonperishability.'
    if key.startswith('inventory.movements.'):
        event = {'write_off': 'write-offs', 'adjustment': 'adjustments', 'return': 'returns'}[parts[2]]
        return 'Magnitude of source-recorded cost associated with inventory ' + event + ' in the window. An adjustment or return does not automatically establish shrinkage.'
    if key.startswith('debt.maturing_'):
        days = parts[1].split('_')[-1][:-1]
        return 'Observed outstanding loan principal on facilities maturing from the assessment date up to, but excluding, ' + days + ' days later. This is maturity exposure, not the amount of scheduled installments.'
    if key.startswith('debt.installments_due_'):
        days = parts[1].split('_')[-1][:-1]
        return 'Remaining payments on supplied installments due from the assessment date up to, but excluding, ' + days + ' days later. It does not assert that all external debt was supplied.'
    if key.startswith('subscriptions.next_invoice_'):
        days = parts[1].split('_')[-1][:-1]
        return 'One next recurring billing amount per observed active subscription due from the assessment date up to, but excluding, ' + days + ' days later. It is not a collection forecast and excludes additional future cycles and usage charges.'
    if key.startswith('reconciliation.'):
        pair = {'order_payment': 'orders and payments', 'payment_payout': 'payments and payouts', 'payout_bank': 'payouts and bank transactions', 'invoice_bank': 'invoices and bank transactions', 'bank_journal': 'bank transactions and journals'}[parts[1]]
        return {'observed_link_count': 'Number of supplied reconciliation links between ' + pair + '.',
                'matched_link_share': 'Portion of supplied links between ' + pair + ' marked matched. This describes link status, not the share of all transaction value reconciled.',
                'conflict_link_count': 'Number of supplied links between ' + pair + ' explicitly marked as conflicting.'}[parts[2]]
    return CROSS_SPECIFIC[key]


CROSS_SPECIFIC = {
    'commerce.cancelled_order_share': 'Portion of observed orders placed in the window that are cancelled.',
    'commerce.discounted_order_share': 'Portion of observed noncancelled orders placed in the window with a positive discount.',
    'commerce.discount_to_subtotal_share': 'Discount value relative to source-reported subtotals on observed noncancelled orders. The source subtotal convention matters; this is not a profit margin.',
    'commerce.paid_unfulfilled_order_count': 'Number of observed noncancelled orders that are paid but remain wholly or partially unfulfilled.',
    'commerce.paid_unfulfilled_order_value': 'Full current value of paid orders that remain wholly or partially unfulfilled. Partial fulfillment does not mean this entire value is undelivered.',
    'commerce.oldest_paid_unfulfilled_order_days': 'Age of the oldest paid, wholly or partially unfulfilled order among observed orders placed in the reporting window.',
    'commerce.channel_concentration_hhi': 'Concentration of observed noncancelled order value across sales channels. Higher zero-to-one values indicate greater dependence on fewer channels.',
    'commerce.customer_concentration_hhi': 'Concentration of observed noncancelled order value across identified customers. Higher zero-to-one values indicate greater dependence on fewer customers.',
    'commerce.location_concentration_hhi': 'Concentration of observed noncancelled order value across identified locations. Higher zero-to-one values indicate greater dependence on fewer locations.',
    'settlements.payout_failure_share': 'Portion of observed payouts created in the window that failed. The assessed population also includes pending attempts.',
    'settlements.payout_delay_days.median': 'Middle lateness of paid payouts against their expected arrival dates, with early arrivals counted as zero delay. This is not total payout-processing time.',
    'settlements.payout_delay_days.p90': '90th-percentile lateness of paid payouts against their expected arrival dates, with early arrivals counted as zero delay. This is not total payout-processing time.',
    'payments.effective_processing_fee_share': 'Explicitly reported processing fees relative to captured payment value. Missing fees are not estimated from a nominal fee schedule.',
    'payments.refunded_payment_count_share': 'Portion of payments captured in the window with a positive refunded amount. This follows the capture cohort rather than the date of refund events.',
    'payments.capture_to_settlement_days.median': 'Middle elapsed time from payment capture to settlement among observed settled payments captured in the window.',
    'payments.capture_to_settlement_days.p90': '90th-percentile elapsed time from payment capture to settlement among observed settled payments captured in the window.',
    'payments.resolved_dispute_win_share': 'Portion of explicitly won or lost disputes recorded as won. Unresolved and generically closed disputes do not count as wins.',
    'payments.open_dispute_exposure': 'Value disputed in cases requiring a response or under review. This is unresolved exposure, not expected loss.',
    'payments.overdue_dispute_response_count': 'Number of observed disputes still requiring a response after their response deadlines.',
    'inventory.negative_quantity_position_count': 'Number of inventory positions with negative recorded on-hand quantity. It does not combine quantities of unrelated products.',
    'inventory.reserved_value_share': 'Portion of observed inventory carrying value represented by reserved quantities within each position. Reservations do not establish a completed sale.',
    'debt.overdue_installment_amount': 'Remaining amount on observed installments whose due dates are before the assessment date.',
    'debt.overdue_installment_count': 'Number of observed past-due installments with a positive amount still owed.',
    'debt.variable_rate_principal_share': 'Portion of observed loan principal explicitly subject to variable interest rates. Unknown rate types are not treated as fixed.',
    'debt.largest_creditor_principal_share': 'Portion of observed outstanding loan principal owed to the largest identified creditor.',
    'subscriptions.active_customer_count': 'Distinct customers with an observed active subscription at the assessment time. This is current membership, not a historical retention measure.',
    'subscriptions.past_due_subscription_share': 'Portion of observed active or past-due subscriptions recorded as past due.',
    'accounting.reversal_journal_share': 'Portion of observed posted or reversed journals with an explicit link to the journal they reverse. Missing links do not prove no reversals occurred.',
    'accounting.source_document_link_share': 'Portion of observed posted or reversed journals linked to a source document. An absent link alone does not establish fraud or manual origin.',
    'accounting.manual_origin_journal_share': 'Portion of observed posted or reversed journals explicitly identified as manual entries. Narrative text is not used to guess manual origin.',
}

ANALYSES = {
    'verifications': 'Source-linked identity, business and related-person verification observations, with unresolved findings retained.',
    'financial_statements': 'Structured financial-statement observations on the stated reporting period, currency and accounting basis.',
    'obligations': 'Supported borrowing and payment obligations used to understand existing commitments.',
    'income_streams': 'Identified income sources, cadence and supported income amounts, including their verification basis.',
    'reconciliations': 'Links and differences between records describing related activity across source systems.',
    'concentrations': 'Exposure by customer, supplier, channel or another supported segment, with coverage identified.',
    'projections': 'Future financial paths under stated assumptions and horizons, separated from observed history.',
    'benchmarks': 'Comparisons against identified reference populations and measures, with applicability and evidence stated.',
    'model_outputs': 'Eligible model outputs with their model identity and limitations. This section does not imply every assessment includes a score or default probability.',
    'changes': 'Changes against a previous package, including whether the values are comparable.',
    'collateral': 'Supported asset valuations, security and competing-claim observations.',
    'relationships': 'Evidence-supported links among entities and counterparties.',
    'credit_reports': 'Entitled credit-report observations with their report dates and coverage.',
    'tax_obligations': 'Supported tax obligations and related evidence, distinguished from a tax-compliance opinion.',
}


def bank_meaning(d, bank, categories, groups):
    selector = bank['selectors'][d['selector']]
    kind, sid = selector['kind'], selector['id']
    selected = {
        'posted': 'all posted activity', 'external': 'explicitly external activity',
        'unclassified': 'unclassified or conflicting activity',
    }.get(kind, selector['label'].lower())
    period = next(p['label'].lower() for p in bank['periods'] if p['id'] == d['period'])
    context = 'depository-account cash' if d['context'] == 'bank_cashflow' else 'issuer-card account activity'
    stat = bank['statistics'][d['statistic']]['label']
    text = stat + ' for ' + d['direction'] + ' ' + context + ', selecting ' + selected + ', over ' + period + '.'
    if kind == 'category':
        text += ' ' + categories[sid]
    elif kind == 'group':
        text += ' ' + groups[sid]
    text += ' ' + STATISTICS[d['statistic']]
    if d['context'] == 'card_activity':
        text += ' Card direction is account activity, not a second bank cash flow.'
    return text


def build_dictionary():
    metrics = read_json('downloads/underwriting-metric-catalog.json')
    bank = read_json('downloads/financial-attribute-catalog.json')
    cross = read_json('downloads/cross-system-attribute-catalog.json')
    taxonomy = read_json('downloads/transaction-taxonomy.json')
    meanings = read_meanings('metric-meanings.tsv')
    expected = {r['key'] for r in metrics['dimensions'] + metrics['metrics']}
    assert set(meanings) == expected, ('Metric meaning coverage mismatch', expected - set(meanings), set(meanings) - expected)
    curated = read_meanings('transaction-meanings.tsv')
    known = {r['id'] for r in taxonomy['groups'] + taxonomy['categories']}
    assert set(curated) <= known, set(curated) - known
    groups = {g['id']: curated[g['id']] for g in taxonomy['groups']}
    categories = {c['id']: category_meaning(c, curated) for c in taxonomy['categories']}
    for axis, values in taxonomy['axes'].items():
        assert set(AXES[axis][2]) == set(values), axis
    assert set(STATISTICS) == set(bank['statistics'])
    semantic = {'description': 'Plain-language documentation of the published catalogs. These definitions do not add API fields or change calculations.',
                'api_version': read_json('openapi/amlok.json')['info']['version'],
                'metric_catalog_version': metrics['version'], 'attribute_catalog_version': bank['version'], 'taxonomy_version': taxonomy['version'],
                'source_sha256': {name: hashlib.sha256((ROOT / 'downloads' / name).read_bytes()).hexdigest() for name in ['underwriting-metric-catalog.json', 'financial-attribute-catalog.json', 'cross-system-attribute-catalog.json', 'transaction-taxonomy.json']},
                'dimensions': {d['key']: meanings[d['key']] for d in metrics['dimensions']},
                'metrics': {m['key']: meanings[m['key']] for m in metrics['metrics']},
                'groups': groups, 'categories': categories,
                'axes': {k: {'label': v[0], 'meaning': v[1], 'values': v[2]} for k, v in AXES.items()},
                'statistics': STATISTICS, 'analyses': ANALYSES,
                'supporting_schedule': read_meanings('schedule-meanings.tsv'),
                'cross_system_attributes': {d['key']: cross_meaning(d) for d in cross['definitions']}}
    return semantic, metrics, bank, cross, taxonomy


def write_guides():
    meaning, metrics, bank, cross, taxonomy = build_dictionary()
    (ROOT / 'downloads/financial-definitions.json').write_text(json.dumps(meaning, indent=2, ensure_ascii=False) + '\n')
    # Each published key gets its own row; descriptions are expanded, never invented key combinations.
    with (ROOT / 'downloads/financial-attribute-dictionary.csv').open('w', newline='') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerow(['key', 'meaning', 'unit', 'context', 'direction', 'selector', 'period', 'statistic', 'catalog_version'])
        for d in bank['definitions']:
            writer.writerow([d['key'], bank_meaning(d, bank, meaning['categories'], meaning['groups']), bank['statistics'][d['statistic']]['unit'], d['context'], d['direction'], d['selector'], d['period'], d['statistic'], bank['version']])
        for d in cross['definitions']:
            writer.writerow([d['key'], meaning['cross_system_attributes'][d['key']], d['unit'], 'observed_records', '', '', d['period_basis'], '', cross['version']])

    body = '''AMLOK organizes underwriting observations into **24 dimension families and 184 scalar metrics**. Each definition below explains the financial concept, its unit and the borrower types it applies to. The metric is an assessment input; your institution retains the credit decision.

## Find the right definition

| Term | What it represents | Where to read it |
| --- | --- | --- |
| Dimension | A family of related financial concepts, such as liquidity | `dimensions[].key` in a risk package |
| Metric | One scalar measurement, such as unrestricted cash | `dimensions[].metrics[].key` |
| Detailed attribute | A more specific observation by category, period or source population | `financial_attributes[].key`; see [Financial attributes](/data-model/financial-attributes) |
| Transaction category | The supported economic purpose of activity | See [Category dictionary](/data-model/transaction-category-dictionary) |
| Analysis | Structured supporting records or segments behind the assessment | `analyses`; see [Read assessment fields](/data-model/assessment-definitions) |

The `dimensions` list returned by `GET /v1/configuration` contains **metric definitions**. A policy rule's `dimension_key` uses a scalar metric key such as `dscr`, not a family name such as `repayment_capacity`. Detailed financial-attribute keys do not become policy-rule keys.

## Read values consistently

`currency` values are money amounts in the returned currency. `count`, `days` and `months` retain those units. `ratio` values are decimal fractions or multiples: `0.25` is 25 percent and DSCR `1.50` is 1.5 times the stated debt service. Ratio changes can be absolute changes rather than relative growth; their definitions say which.

Read the actual observation window, as-of date, basis, availability and evidence with the value. An unavailable value is null, not zero. A family marked available means its applicable metrics are available; it does not mean the borrower meets policy. See [field and status meanings](/data-model/assessment-definitions).

Catalog version: **VERSION**. Exact calculation specifications and required inputs remain in the [metric catalog](/downloads/underwriting-metric-catalog.json) and [methodology](/api-reference/risk-package-methodology). [Download plain-language definitions](/downloads/financial-definitions.json).

'''.replace('VERSION', metrics['version'])
    for dim in metrics['dimensions']:
        body += '## ' + dim['label'] + '\n\n' + meaning['dimensions'][dim['key']] + '\n\nFamily key: `' + dim['key'] + '`.\n\n'
        for m in (m for m in metrics['metrics'] if m['dimension_key'] == dim['key']):
            # Retain existing key-based anchors used by research and API guides.
            body += '### ' + m['key'] + '\n\n**' + m['label'] + '** · `' + m['unit'] + '` · ' + ', '.join(m['borrower_types']) + '\n\n' + meaning['metrics'][m['key']] + '\n\nCalculation version: `' + m['calculation_version'] + '`.\n\n'
    page('api-reference/underwriting-dimensions.mdx', 'Underwriting dimensions', 'Understand all 24 risk dimensions and 184 underwriting metrics, including their business meaning, units, borrower applicability and interpretation.', body)

    body = '''AMLOK classifies transaction purpose separately from account context, cash effect, payment rail and counterparty role. Use the leaf category to understand the activity and the group to summarize related purposes. The current taxonomy contains **327 leaf categories within 45 groups**; groups are not additional leaf categories.

These meanings do not establish tax deductibility, accounting recognition, verified identity, fraud or creditworthiness. A card purchase can share a purpose category with a bank payment while having a different cash and liability effect. [Read the classification rules](/data-model/transaction-categorization) and [all classification-axis values](/data-model/assessment-definitions#transaction-classification-axes).

Use the exact `category_id`, not a translated label. The [taxonomy download](/downloads/transaction-taxonomy.json) supplies allowed account contexts, directions, parent IDs and evidence requirements. [Plain-language definitions](/downloads/financial-definitions.json) are also available as JSON.

'''
    for group in taxonomy['groups']:
        body += '## ' + group['label'] + '\n\n`' + group['id'] + '` - ' + meaning['groups'][group['id']] + '\n\n'
        children = [c for c in taxonomy['categories'] if c['parent_id'] == group['id']]
        if children:
            body += table(['Category key', 'Name and meaning'], [('`' + c['id'] + '`', '**' + c['label'] + '**. ' + meaning['categories'][c['id']]) for c in children])
        else:
            body += 'This parent group summarizes its child groups below.\n\n'
    page('data-model/transaction-category-dictionary.mdx', 'Transaction category dictionary', 'Read the meaning of every transaction-purpose category and group, with distinctions between operating activity, funding, transfers and adjustments.', body, 'Category dictionary')

    body = '''AMLOK's **150 cross-system attributes** describe the supplied invoices, bills, orders, payments, inventory and other authorized records. This dictionary explains each key without requiring you to read its calculation specification.

Every entry describes **observed records**, not a claim that all accounts or business systems are known. Read the result's scope, dates, currency, status and input manifest. Missing records do not establish zero. Receivables and payables aging follows due dates; timed observations follow the cohort specified in the definition.

Amounts use the returned currency. Ratios are fractions; concentration indices run from zero to one. Higher concentration means greater dependence on fewer parties, not an automatic adverse decision. [Retrieve attributes](/data-model/financial-attributes), [read result fields](/data-model/assessment-definitions), or [download the full attribute dictionary](https://raw.githubusercontent.com/amloktech/docs/main/downloads/financial-attribute-dictionary.csv).

'''
    families = {'ar': ('Accounts receivable', 'Customer invoices, unpaid balances, aging and collection experience.'), 'ap': ('Accounts payable', 'Supplier bills, unpaid balances, aging and payment experience.'),
                'commerce': ('Commerce', 'Observed order activity, discounts, fulfillment and concentration.'), 'settlements': ('Settlements', 'Processor payout status, failure and arrival timing.'),
                'payments': ('Payments and disputes', 'Captured-payment fees, refunds, settlement and dispute observations.'), 'inventory': ('Inventory', 'Recorded stock ownership, carrying value, expiry and movements.'),
                'debt': ('Debt and installments', 'Observed loan balances, upcoming maturities and supplied payment schedules.'), 'subscriptions': ('Subscriptions', 'Current recurring-billing membership and the next scheduled charges.'),
                'accounting': ('Accounting', 'Explicit journal origins, reversal links and source-document links.'), 'reconciliation': ('Reconciliation', 'Status of supplied links between records across systems.')}
    for prefix, (label, description) in families.items():
        body += '## ' + label + '\n\n' + description + '\n\n'
        for d in (d for d in cross['definitions'] if d['key'].split('.')[1] == prefix):
            body += '### ' + d['key'] + '\n\nUnit: `' + d['unit'] + '`.\n\n' + meaning['cross_system_attributes'][d['key']] + '\n\n'
    page('data-model/cross-system-attribute-dictionary.mdx', 'Cross-system attribute dictionary', 'Understand all 150 cross-system attributes across receivables, payables, commerce, payments, inventory, debt, subscriptions and reconciliation.', body, 'Cross-system dictionary')

    body = '''## Read every bank and card attribute

The **12,805 bank and card definitions** combine an account context, direction, activity selection, observation period and statistic. Only combinations present in the published catalog are defined; do not construct arbitrary keys.

For example, `transactions.bank_cashflow.outflow.expense.inventory.rolling_30d.amount` means the **total bank cash paid for inventory and direct inputs over the last 30 complete days**. It does not mean inventory on hand, cost of goods sold or the amount eligible as collateral.

### Account context and direction

| Context | Meaning |
| --- | --- |
| `bank_cashflow` | Posted cash movement in depository accounts. Inflow is cash received and outflow is cash paid. |
| `card_activity` | Issuer credit-account activity. Direction follows the normalized account posting; a purchase can increase a liability without moving bank cash. |

Use `cash_effect`, `balance_sheet_effect` and `card_event_type` to interpret issuer-card activity. Merchant payment acceptance and processor payouts are separate cross-system observations. Do not add card purchases to the bank payments that later settle those purchases.

### Activity selection

| Selector | Meaning |
| --- | --- |
| `category:<id>` | A single supported leaf economic-purpose category. |
| `group:<id>` | Activity under a category group, including its supported descendants. Group totals overlap their leaf totals; do not add them together. |
| `posted:posted` | All eligible posted activity in the context and direction. |
| `external:external` | Activity explicitly identified as external under the transfer classification. |
| `unclassified:unclassified` | Activity whose purpose is unclassified or conflicting. |

The [category dictionary](/data-model/transaction-category-dictionary) explains every category and group. A merchant sector alone does not prove economic purpose.

### Observation periods

'''
    body += table(['Period key', 'Meaning'], [('`' + p['id'] + '`', p['label'] + ', anchored to the stated observation window rather than the retrieval time.') for p in bank['periods']])
    body += '### Statistics\n\n' + table(['Statistic', 'Unit', 'What it represents'], [('`' + k + '`', bank['statistics'][k]['unit'], v) for k, v in STATISTICS.items()])
    body += '''The 90th percentile needs at least ten selected transactions; standard deviation needs at least three. Amount distributions and recency are unavailable for an empty selection. An available zero total or count requires sufficient coverage and classification to establish no matching activity.

### Browse definitions or download

Read and search every key in the [definition catalog](/data-model/definition-catalog). Its table shows the explanation, unit, category and context without opening a file.

- [Full attribute dictionary (CSV)](https://raw.githubusercontent.com/amloktech/docs/main/downloads/financial-attribute-dictionary.csv): one row and a plain-language meaning for every one of the 12,955 bank/card and cross-system keys, with units and context.
- [Cross-system dictionary](/data-model/cross-system-attribute-dictionary): all 150 cross-system definitions grouped by business area.
- [Definition meanings (JSON)](/downloads/financial-definitions.json): all scalar metric, category, group, axis and cross-system meanings, with source-catalog versions and checksums.
- [Assessment field glossary](/data-model/assessment-definitions): how to read statuses, evidence, units and supporting analyses.
'''
    append_section('data-model/financial-attributes.mdx', 'PLAIN LANGUAGE ATTRIBUTES', body)
    append_section('data-model/transaction-categorization.mdx', 'CATEGORY MEANINGS', '''## Find a category's meaning

The [category dictionary](/data-model/transaction-category-dictionary) defines all 327 leaf categories and 45 groups. The [assessment glossary](/data-model/assessment-definitions#transaction-classification-axes) explains every value in the ten independent classification axes. Use these meanings alongside the category's permitted context, direction and evidence requirements.
''')
    write_assessment_glossary(meaning)
    write_verification_meanings()
    schedule = read_json('openapi/amlok.json')['components']['schemas']['FinancialSupportingSchedule']['properties']
    assert set(schedule) == set(meaning['supporting_schedule'])
    path = ROOT / 'data-model/field-dictionary.mdx'
    schedule_text = '''\n## Financial supporting schedule fields

`financial_statement.supporting_schedule` contains 76 optional nullable decimal-string inputs. The meanings below identify the financial concept rather than its calculation. Money amounts use the parent statement currency and reporting period. Counts, days and the required DSCR ratio keep their stated units. Missing is unknown, not zero. Opening balances refer to the start of the period; closing balances refer to its end.

These inputs do not automatically establish eligibility for a risk metric. Read the supported scope and evidence with the [metric definition](/api-reference/underwriting-dimensions). The same nested fields are searchable in Console Data Lookup.

'''
    schedule_text += table(['Field', 'Meaning'], [('`supporting_schedule.' + key + '`', meaning['supporting_schedule'][key]) for key in schedule])
    path.write_text(path.read_text().split('\n## Financial supporting schedule fields')[0].rstrip() + '\n' + schedule_text)
    append_section('data-model/api-alignment.mdx', 'DEFINITION COVERAGE', '''## Read the definition dictionaries

| Definition set | What it explains |
| --- | --- |
| [24 dimensions and 184 metrics](/api-reference/underwriting-dimensions) | The business meaning, unit and applicability of each scalar underwriting measure. |
| [12,955 financial attributes](/data-model/financial-attributes) | Every bank/card and cross-system observation, with a complete downloadable key-by-key dictionary. |
| [327 transaction categories and 45 groups](/data-model/transaction-category-dictionary) | The supported purpose of activity, distinct from its rail, merchant sector and cash effect. |
| [Assessment glossary](/data-model/assessment-definitions) | Result fields, availability, evidence basis, 14 supporting analysis sections and all values in the ten classification axes. |
| [981 normalized fields](/data-model/field-dictionary) | Source-record attributes, their meaning and their exact schema presence rules. |
| [860 verification fields](/api-reference/verification-fields) | Identity, ownership, screening and other verification observations with source-specific limitations. |
| [56 source-derived attributes](/data-model/derived-attributes) | Retained evidence-level analytical definitions, separate from the scalar policy metric catalog. |

These sets describe different layers and can reference the same underlying evidence. Do not add their counts together as independent facts available for every borrower. Definition versions identify their own catalogs; they do not change the public API's version.
''')
    nav = read_json('docs.json')
    additions = {'data-model/start-here': ['data-model/definition-catalog'], 'data-model/financial-attributes': ['data-model/cross-system-attribute-dictionary', 'data-model/assessment-definitions'], 'data-model/transaction-categorization': ['data-model/transaction-category-dictionary']}
    new_pages = {p for pages in additions.values() for p in pages}
    def walk(item):
        if isinstance(item, dict):
            if 'pages' in item:
                item['pages'] = [p for p in item['pages'] if not isinstance(p, str) or p not in new_pages]
                rebuilt = []
                for p in item['pages']:
                    rebuilt.append(p)
                    if isinstance(p, str):
                        rebuilt.extend(additions.get(p, []))
                item['pages'] = rebuilt
            for value in item.values():
                walk(value)
        elif isinstance(item, list):
            for value in item:
                walk(value)
    walk(nav)
    (ROOT / 'docs.json').write_text(json.dumps(nav, indent=2, ensure_ascii=False) + '\n')
    from definition_table import write_definition_table
    write_definition_table(ROOT, meaning, metrics, bank, cross, taxonomy)


def write_verification_meanings():
    """Replace generic documentation prose while preserving schema-derived metadata."""
    meanings = read_meanings('verification-meanings.tsv')
    catalog = read_json('downloads/verification-field-catalog.json')
    target = ROOT / 'api-reference/verification-fields.mdx'
    body = target.read_text()
    covered = set()
    for field in catalog['fields'].values():
        path = field['path']
        if path not in meanings:
            assert 'Preserve the source meaning' not in field['description'], 'Undocumented verification field: ' + path
            continue
        old, new = field['description'], meanings[path]
        heading = re.sub(r'[.\[\]]+', '-', path).strip('-')
        pattern = r'(### ' + re.escape(heading) + r'\n\n[^\n]+\n\n)' + re.escape(old)
        body, count = re.subn(pattern, lambda m: m[1] + new, body)
        assert count == 1, 'Verification field paragraph missing: ' + path
        field['description'] = new
        field['details']['Normalization / validation'] = new
        covered.add(path)
    assert covered == set(meanings), set(meanings) - covered
    target.write_text(body)
    (ROOT / 'downloads/verification-field-catalog.json').write_text(json.dumps(catalog, indent=2) + '\n')


def write_assessment_glossary(meaning):
    body = '''AMLOK returns financial measurements together with the information you need to interpret them. Use this glossary to distinguish a supported value from missing evidence, a financial observation from an institution decision, and a transaction purpose from its cash effect.

## Metric fields

'''
    fields = {
        'key / label': 'The stable machine identifier and its readable name. Use the key for integration and the label for display.',
        'value / unit / currency': 'The decimal-string observation, its unit and its currency when monetary. Null is missing or inapplicable; zero is an actual supported value.',
        'status': 'Whether the metric is available, unavailable or not applicable. It is not a risk grade.',
        'window': 'The exact UTC observation interval, including its start and excluding its end.',
        'as_of': 'The assessment knowledge cutoff. Later source updates do not rewrite the saved observation.',
        'definition_version / calculation_version': 'The pinned definition and calculation implementation used for this result. Compare compatible versions and scopes.',
        'basis': 'Whether the supporting value is observed, declared, derived or estimated. These bases are not interchangeable.',
        'analysis_basis': 'Historical describes past activity; pro_forma describes the assessed financing configuration; scenario describes an explicitly assumed alternative.',
        'assumptions': 'Conditions used in the assessment, such as financing or scenario assumptions. They are not observed facts.',
        'inputs': 'Named numerical components with their own units, currency, evidence and basis.',
        'coverage': 'Observed versus expected days and a note defining the assessed scope. Coverage is not confidence in creditworthiness.',
        'missing_reason / reason_code': 'A readable explanation and structured reason for an unavailable or inapplicable result.',
        'evidence_ids': 'References to supporting evidence in the authorized package. The references support traceability, not an automatic verified conclusion.',
        'series': 'Ordered historical observations under the same metric definition, unit, currency and scope. Missing periods remain explicit.',
    }
    body += table(['Field', 'Meaning'], [('`' + k + '`', v) for k, v in fields.items()])
    body += '''## Availability and basis

| Value | Meaning |
| --- | --- |
| Metric `available` | Evidence supports a value under the definition and stated scope. |
| Metric `unavailable` | The metric applies but a supported value cannot be returned; read its reason. |
| Metric `not_applicable` | The definition does not apply to this borrower or assessment context. |
| Dimension `available` | All applicable metrics in the family are available. |
| Dimension `partial` | Some applicable metrics are available and others are unavailable. |
| Dimension `unavailable` | None of the applicable metrics can be calculated. |
| Dimension `not_applicable` | No metric in the family applies. |
| Basis `observed` | Directly supported by source observations. |
| Basis `declared` | Supplied as a declaration rather than independently observed evidence. |
| Basis `derived` | Obtained from supported inputs through the applicable definition. |
| Basis `estimated` | An estimate whose assumptions and limitations remain relevant. |

### Metric reason codes

'''
    reasons = {
        'missing_source': 'A required source is absent.', 'insufficient_history': 'The observed history is shorter than the definition requires.',
        'stale_source': 'Required evidence is older than the permitted freshness tolerance.', 'incomplete_coverage': 'The source or account population has known coverage gaps.',
        'restricted_source': 'Required evidence cannot be used under the applicable access or authorization.',
        'invalid_denominator': 'A ratio cannot be meaningfully calculated with the available denominator, such as zero or nonpositive values where prohibited.',
        'conflicting_evidence': 'Relevant sources disagree in a way that prevents a supported value.', 'unsupported_scope': 'The requested population or scope is not supported.',
        'not_applicable': 'The definition does not apply to this assessment.', 'not_evaluated': 'No evaluation of this item is represented.',
        'no_comparable_baseline': 'A valid comparable prior observation is not available.', 'model_not_eligible': 'An applicable eligible model output is not available for the assessment.'}
    body += table(['Code', 'Meaning'], [('`' + k + '`', v) for k, v in reasons.items()])
    body += '''## Detailed attribute fields

Detailed attributes use `available` or `unavailable`, rather than the scalar metric's three-state status. They preserve their own definition, input population and window. Scalar metric reason-code enums do not define an exhaustive reason-code list for detailed attributes.

'''
    fields = {
        'key': 'An exact published attribute key, including its applicable category, period or cross-system observation.',
        'value_type': 'Whether the decimal-string value represents a decimal or an integer.',
        'value / unit / currency': 'The supported observation and its unit; monetary values carry currency. An unavailable value is null.',
        'status': 'Available means a supported value is present; unavailable means its missing reason must be read.',
        'window_start / window_end': 'UTC calendar dates identifying the observation boundaries. The input manifest supplies exact timestamps, particularly for cross-system windows that end within a day.',
        'as_of': 'The knowledge cutoff for the saved observation.',
        'definition_version / calculation_version': 'The catalog definition and implementation pinned to the saved observation.',
        'input_resource_ids': 'Inline input references. An empty inline array does not mean there is no evidence; read the manifest.',
        'input_manifest_id': 'The complete frozen input population referenced in financial_attribute_inputs within the same package.',
        'coverage_ratio': 'The stated coverage measure. It is not a confidence score, and null does not imply complete coverage.',
        'missing_reason / reason_code': 'The explanation and structured reason the value cannot be supported.',
        'data_scope': 'observed_records describes supplied records; complete_account_history describes the declared account-history scope. Neither proves every external system or account is known.',
        'scope / coverage': 'The explicit population, observation limits, record counts and field-coverage information returned for the attribute.',
    }
    body += table(['Field', 'Meaning'], [('`' + k + '`', v) for k, v in fields.items()])
    body += '''The attribute summary's `definition_count` counts catalog definitions; `evaluated_count` counts observations assessed in this package; `available_count` and `unavailable_count` distinguish their availability. `input_manifest_count` counts frozen input populations, not unique borrowers or transactions. Read `coverage_statement` with these counts.

## Supporting analysis sections

These 14 sections hold structured supporting information. They are not additional scalar metric families. Read each section's status, reason, evidence and items.

'''
    body += table(['Section', 'What it represents'], [('`' + k + '`', v) for k, v in ANALYSES.items()])
    body += '''## Transaction classification fields

| Field or value | Meaning |
| --- | --- |
| `taxonomy_version` | The version of the purpose categories used for this record. |
| `category_id / category_path / category_label` | The stable leaf identifier, its hierarchy and its readable name. |
| `legacy_category` | The retained broad compatibility label, not a replacement for a supported detailed purpose. |
| Status `classified` | A category is supported by the available evidence. |
| Status `unclassified` | The purpose cannot be assigned with the available evidence. |
| Status `conflicting` | Classification evidence conflicts and remains unresolved. |
| `method` | How the classification was supported. It does not establish trained-model accuracy. |
| Confidence `high / medium / unknown` | Qualitative strength of classification evidence, not calibrated probabilities or a credit score. |
| `reason_codes` | Reasons supporting or limiting the classification. |
| `provider_category` | The original provider's category observation, retaining its source version and semantics. |

The normalized source field `financial_category_id` names the purpose category. Card brand and last four digits are descriptive card observations, not globally unique card identifiers or sufficient evidence by themselves that a card changed. Merchant sector, provider category, account context and purpose remain distinct.

## Transaction classification axes

The ten axes answer different questions about the same transaction. Their meanings are independent; for example, a card purchase is not automatically a bank cash outflow, and an online payment is not automatically operating revenue.

'''
    for key, (label, description, values) in AXES.items():
        body += '### ' + label + '\n\n`' + key + '` - ' + description + '\n\n' + table(['Value', 'Meaning'], [('`' + k + '`', v) for k, v in values.items()])
    body += '''## Continue reading

- [Underwriting dimensions and metrics](/api-reference/underwriting-dimensions)
- [Bank, card and cross-system attributes](/data-model/financial-attributes)
- [All transaction categories](/data-model/transaction-category-dictionary)
- [Normalized source-field dictionary](/data-model/field-dictionary)
- [Calculation and interpretation methodology](/api-reference/risk-package-methodology)
'''
    page('data-model/assessment-definitions.mdx', 'Assessment field glossary', 'Interpret financial result fields, availability states, evidence bases, supporting analyses and every value in the transaction classification axes.', body, 'Assessment glossary')


if __name__ == '__main__':
    write_guides()

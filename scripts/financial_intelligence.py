"""Versioned financial attributes and transaction purpose classification.

Extends the existing immutable result and its paged collection views. Catalogs
are published separately so configuration and API schemas remain bounded.
"""
from copy import deepcopy
import json
from product_api_review import ROOT, obj, ref, text, enum, array, nullable

VERSION = '2026-11-13.1'

def catalogs():
    return [json.loads((ROOT / 'downloads' / (name + '.json')).read_text()) for name in
            ['financial-attribute-catalog', 'cross-system-attribute-catalog', 'transaction-taxonomy']]

def catalog_metadata():
    bank, cross, taxonomy = catalogs()
    definitions = lambda c: c.get('definitions', c.get('attributes', []))
    return dict(version=VERSION, taxonomy_version=taxonomy['version'],
        attribute_definition_count=len(definitions(bank)) + len(definitions(cross)),
        transaction_category_count=len(taxonomy['categories']),
        scalar_metric_count=184,
        catalogs=[dict(kind=kind, version=c['version'], url='https://docs.amlok.io/downloads/'+name+'.json')
            for kind,name,c in [('bank_card_attributes','financial-attribute-catalog',bank),
                ('cross_system_attributes','cross-system-attribute-catalog',cross),
                ('transaction_categories','transaction-taxonomy',taxonomy)]])

def extend(spec, fixtures):
    s = spec['components']['schemas']
    decimal = text(pattern=r'^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$')
    count = {'type':'integer','minimum':0}
    strings = array(text())
    date = text(format='date')
    stamp = text(format='date-time')
    s['FinancialIntelligenceCatalog'] = obj({
        'version':text('Registry version for detailed financial attributes, independent of the scalar policy metric catalog.'),
        'taxonomy_version':text(), 'attribute_definition_count':count,
        'transaction_category_count':count, 'scalar_metric_count':count,
        'catalogs':array(obj({'kind':enum('bank_card_attributes','cross_system_attributes','transaction_categories'), 'version':text(),'url':text(format='uri')}))})
    s['FinancialAttribute'] = obj({
        'key':text('Stable attribute key in the published catalog; includes the applicable context, period and statistic.'),
        'value_type':enum('decimal','integer'), 'value':nullable(decimal),
        'unit':enum('currency','count','ratio','days'), 'currency':nullable(text(pattern='^[A-Z]{3}$')),
        'status':enum('available','unavailable'),
        'window_start':dict(date,description='UTC calendar date containing the observation start. Consult the input manifest for the exact timestamp.'), 'window_end':dict(date,description='UTC calendar date containing the exclusive observation end. Cross-system observations can end partway through this date; consult the manifest timestamp. Daily bank/card statistics use completed UTC days.'), 'as_of':stamp,
        'calculation_version':text(), 'definition_version':text(),
        'input_resource_ids':strings,
        'input_manifest_id':text('References financial_attribute_inputs[].id in this same immutable risk package. The manifest identifies the complete input scope; the catalog defines selection and formula. An empty inline ID array does not mean no evidence.'),
        'coverage_ratio':nullable(decimal),
        'missing_reason':nullable(text('Explicit reason a value is unavailable. Never interpret an unavailable value as zero.')),
        'reason_code':nullable(text()),
        'data_scope':enum('observed_records','complete_account_history'),
        'scope':{'type':'object','description':'Explicit source population and observational limitations.'},
        'coverage':{'type':'object','description':'Observed record counts and field coverage; does not establish that every external account or system is known.'},
    }, required=['key','value_type','value','unit','currency','status','window_start','window_end','as_of','calculation_version','definition_version','input_resource_ids','input_manifest_id','coverage_ratio','missing_reason','reason_code'],
        description='An explainable calculated observation over a declared input scope. Manifest timestamps define the exact UTC [start, end) input window; date fields identify its calendar dates. Bank cash movement and issuer-card activity are distinct contexts. Existing scalar policy keys remain in dimensions; these detailed attributes do not silently become policy rules.',
        allOf=[{'if':{'properties':{'status':{'const':'available'}}},'then':{'properties':{'value':decimal,'missing_reason':{'type':'null'},'reason_code':{'type':'null'}}},'else':{'properties':{'value':{'type':'null'},'missing_reason':text()}}}])
    s['FinancialAttributeInputManifest'] = obj({
        'id':text('Hash-derived identity of this immutable input set.'),
        'basis':text('bank_cashflow, card_activity or the cross-system input family. Never add cash movement and card activity without reconciliation.'),
        'window':ref('Window'), 'currency':text(pattern='^[A-Z]{3}$'),
        'account_ids':strings, 'resource_ids':strings, 'evidence_ids':strings,
        'coverage':{'type':'object','description':'Input population, complete-account-day coverage or observed-record counts. Missing dates and incomplete collections are not treated as zero activity.'},
        'as_of':stamp,
        'data_scope':text(), 'scope':{'type':'object'},
    }, required=['id','basis','window','currency','account_ids','resource_ids','evidence_ids','coverage','as_of'])
    s['FinancialAttributeSummary'] = obj({
        'catalog_version':text(), 'taxonomy_version':text(),
        'definition_count':count, 'evaluated_count':count, 'available_count':count, 'unavailable_count':count,
        'input_manifest_count':count, 'currency':text(pattern='^[A-Z]{3}$'), 'as_of':stamp,
        'coverage_statement':text('Explains the difference between attribute definitions and available observations.')})
    rp = s['RiskPackage']['properties']
    rp['financial_attributes'] = array(ref('FinancialAttribute'), description='Detailed calculated attributes. Use view=section&section=financial_attributes to page, or export the complete immutable package. Older saved packages may omit this collection.')
    rp['financial_attribute_inputs'] = array(ref('FinancialAttributeInputManifest'), description='Deduplicated provenance sets referenced by detailed attributes. Follow evidence_ids through the frozen evidence endpoints.')
    rp['financial_attribute_summary'] = ref('FinancialAttributeSummary')
    s['Configuration']['properties']['financial_intelligence'] = ref('FinancialIntelligenceCatalog')
    fixtures['Configuration']['financial_intelligence'] = catalog_metadata()
    # A small synthetic response illustrates transport; runtime evaluates the full catalog.
    bank = catalogs()[0]
    first = (bank.get('definitions') or bank.get('attributes'))[0]
    first = {**bank.get('statistics',{}).get(first.get('statistic'),{}), **first}
    p = fixtures['RiskPackage']
    p['financial_attributes'] = [{
        'key':first['key'], 'value_type':'decimal', 'value':None, 'unit':first['unit'],
        'currency':'CAD' if first['unit']=='currency' else None, 'status':'unavailable',
        'window_start':'2026-10-02','window_end':'2026-11-01','as_of':p['as_of'],
        'calculation_version':first.get('calculation_version',VERSION), 'definition_version':first.get('definition_version',VERSION),
        'input_resource_ids':[], 'input_manifest_id':'fai_synthetic', 'coverage_ratio':None,
        'missing_reason':'This abbreviated documentation example does not supply complete source history.', 'reason_code':'incomplete_coverage'}]
    p['financial_attribute_inputs'] = [dict(id='fai_synthetic',basis='bank_cashflow',window=dict(start='2026-10-02T00:00:00Z',end='2026-11-01T00:00:00Z'),currency='CAD',account_ids=[],resource_ids=[],evidence_ids=[],coverage=dict(expected_days=30,expected_account_days=0,covered_account_days=0,transaction_count=0,classified_transaction_count=0),as_of=p['as_of'])]
    p['financial_attribute_summary'] = dict(catalog_version=VERSION,taxonomy_version=VERSION,definition_count=catalog_metadata()['attribute_definition_count'],evaluated_count=1,available_count=0,unavailable_count=1,input_manifest_count=1,currency='CAD',as_of=p['as_of'],coverage_statement='Abbreviated synthetic documentation example. Retrieve all evaluated attributes through paged sections; definitions do not imply available inputs.')
    taxonomy = catalogs()[2]
    s['TransactionClassification'] = obj({
        'taxonomy_version':text(), 'status':enum('classified','unclassified','conflicting'),
        'category_id':nullable(text('Stable leaf identifier in the versioned transaction taxonomy.')),
        'category_path':strings, 'category_label':nullable(text()), 'legacy_category':nullable(text()),
        'method':text('Evidence-based classification method; no claim of trained-model accuracy.'),
        'confidence':enum('high','medium','unknown'),
        'cash_flow_role':text(), 'cash_effect':text(), 'balance_sheet_effect':text(), 'activity_basis':text(),
        'reason_codes':strings, 'provider_category':{'description':'Preserved provider classification observation. Provider version and semantics must be retained; a merchant industry code alone does not prove transaction purpose.'},
    }, description='Conservative transaction-purpose classification. Confidence labels describe evidence strength, not calibrated probabilities. No category implies tax deductibility, fraud, creditworthiness or a verified counterparty.')
    tx = s['NormalizedBankTransactionRead']['properties']
    tx['financial_category_id'] = nullable(text('Supported Amlok transaction-purpose category, pinned to classification.taxonomy_version. May be absent when only a broad source classification exists.'))
    tx['classification'] = ref('TransactionClassification')
    tx['provider_category'] = nullable(obj({'provider':text(), 'taxonomy_version':text(), 'primary':nullable(text()), 'detailed':nullable(text()), 'confidence_level':nullable(text()), 'raw_labels':strings}, required=['provider','taxonomy_version'], description='Original provider category identifiers and confidence labels, retained separately from Amlok classification. An unmapped version remains explicitly unclassified.'))
    tx['card_event_type'] = nullable(enum(*taxonomy['axes']['card_event_types']))
    tx['card_last4'] = nullable(text('Last four digits only; never a full PAN or security code.',pattern='^[0-9]{4}$'))
    tx['card_brand'] = nullable(text())
    tx['counterparty_role'] = nullable(enum(*taxonomy['axes']['counterparty_roles']))
    tx['classification']['description'] = 'Versioned economic-purpose classification, evidence strength and explicit uncertainty. Issuer card transactions represent card activity, not depository cash movement.'
    return spec

def extend_summary(spec, fixtures):
    schema = spec['components']['schemas']['RiskPackageSummary']
    schema['properties']['financial_attribute_summary'] = ref('FinancialAttributeSummary')
    operation = spec['paths']['/v1/risk-packages/{id}']['get']
    for name, description in [
        ('attribute_key','Exact detailed attribute key. Only with view=section and section=financial_attributes. Mutually exclusive with attribute_prefix.'),
        ('attribute_prefix','Literal attribute key prefix, not a regular expression. Only with view=section and section=financial_attributes; mutually exclusive with attribute_key.'),
        ('input_manifest_id','Exact input manifest ID referenced by an attribute. Only with view=section and section=financial_attribute_inputs.')]:
        operation['parameters'].append(dict(name=name, **{'in':'query'}, required=False, schema=text(maxLength=256),description=description))
    operation['description'] += ' Detailed financial attributes and their input manifests are available as paged sections. Attribute filters bind the cursor and total_items counts matching records. Invalid filter/section combinations return 400 validation_error. Historical packages may predate these optional sections.'
    def visit(value):
        if isinstance(value, dict):
            if value.get('view')=='summary' and 'catalog_version' in value:
                value['financial_attribute_summary'] = deepcopy(fixtures['RiskPackage']['financial_attribute_summary'])
            for child in value.values(): visit(child)
        elif isinstance(value,list):
            for child in value: visit(child)
    visit(spec)

def finalize(spec, fixtures):
    """Preserve additions after historical lifecycle patches replace whole schemas."""
    extend(spec, fixtures)
    extend_summary(spec, fixtures)
    schemas = spec['components']['schemas']
    operation = spec['paths']['/v1/risk-packages/{id}']['get']
    media = operation['responses']['200']['content']['application/json']
    views = media['x-response-views']
    section_names = ['financial_attributes', 'financial_attribute_inputs']
    section_parameter = next(p for p in operation['parameters'] if p['name']=='section')['schema']['enum']
    summary_sections = schemas['RiskPackageSummary']['properties']['sections']
    summary_enum = summary_sections['items']['properties']['section']['enum']
    for key in section_names:
        name = 'RiskSection'+''.join(v.title() for v in key.split('_'))
        spec['x-risk-package-sections'][key]={'items':deepcopy(schemas['RiskPackage']['properties'][key]['items']),'metadata_schema':None}
        if key not in section_parameter: section_parameter.append(key)
        if key not in summary_enum: summary_enum.append(key)
        union = schemas['RiskPackageSection']
        if ref(name) not in union['oneOf']: union['oneOf'].append(ref(name))
        union['discriminator']['mapping'][key] = '#/components/schemas/'+name
        views[key] = dict(title=key+' (view=section)',schema=obj({'data':ref(name),'meta':ref('Meta'),'page':ref('Page')}),example={
            'data':dict(view='section',risk_package_id=fixtures['RiskPackage']['id'],record_version=1,section=key,section_metadata=None,items=deepcopy(fixtures['RiskPackage'][key]),total_items=len(fixtures['RiskPackage'][key])),
            'meta':deepcopy(views['full']['example']['meta']),
            'page':dict(next_cursor=None,has_more=False,snapshot_id='risk_section_synthetic',expires_at='2026-11-06T13:00:00Z')})
    summary_sections['minItems']=len(summary_enum)
    summary_sections['maxItems']=len(summary_enum)
    for example in [media.get('example',{}),views['full']['example']]:
        if example.get('data',{}).get('product') in ['insights','signal']:
            for key in section_names+['financial_attribute_summary']: example['data'][key]=deepcopy(fixtures['RiskPackage'][key])
    summary_example=views['summary']['example']['data']
    summary_example['financial_attribute_summary']=deepcopy(fixtures['RiskPackage']['financial_attribute_summary'])
    for key in section_names:
        summary_example['sections']=[row for row in summary_example['sections'] if row['section']!=key]
        summary_example['sections'].append(dict(section=key,item_count=len(fixtures['RiskPackage'][key])))
    from scale_contract import section_value, section_definitions
    definitions=section_definitions(schemas)
    summary_example['sections']=[dict(section=key,item_count=len(section_value(fixtures['RiskPackage'],key))) for key in summary_enum]
    spec['paths']['/v1/exports']['post']['description'] += ' Risk-package JSON exports include every detailed financial attribute and input manifest. PDF is a human-readable report: it includes the assessment and financial-attribute summary, with an explicit notice that the detailed attribute and input-manifest arrays are available through JSON export or paged API sections.'
    spec['x-contract-revision']='2026-11-13.financial-intelligence.1'


def write_guides():
    meta = catalog_metadata()
    page = '''---
title: "Financial attributes"
description: "Use detailed bank, card, accounting and commerce attributes with explicit periods, source coverage, calculation definitions and frozen evidence."
sidebarTitle: "Financial attributes"
keywords: [financial attributes, cash flow, accounting, card transactions]
---

Financial attributes explain observed financial activity in detail. You receive category totals, timing and distribution measures, plus accounting, commerce, inventory and obligation observations in the existing Insights or Signal risk package.

## Understand what is counted

The current registry contains **ATTRIBUTE_COUNT attribute definitions**. Definitions include distinct account contexts, categories, periods and applicable statistics. They are not ATTRIBUTE_COUNT independent facts about every borrower. The separate [184 scalar underwriting metrics](/api-reference/underwriting-dimensions) remain the approved keys for risk-policy rules.

Bank cash movement and issuer-card activity are separate. An issuer-card purchase creates a liability; paying the card bill moves bank cash and reduces that liability. Do not add both as operating spending. Merchant card-processing payments are a third perspective, representing sales collection and settlement, not the merchant's own credit-card spending.

## Retrieve the results

Start with the summary so large collections do not block your integration:

```bash
curl --fail-with-body "$AMLOK_API_BASE_URL/v1/risk-packages/$RISK_PACKAGE_ID?view=summary" \\
  --header "Authorization: Bearer $AMLOK_API_KEY"
```

Read `financial_attribute_summary` for catalog versions, evaluated and available counts. Retrieve a page of observations:

```bash
curl --fail-with-body "$AMLOK_API_BASE_URL/v1/risk-packages/$RISK_PACKAGE_ID?view=section&section=financial_attributes&limit=25" \\
  --header "Authorization: Bearer $AMLOK_API_KEY"
```

Use `attribute_key` for an exact key or `attribute_prefix` for a literal prefix, such as `cross_system.ar.`. These filters are mutually exclusive and only apply to the `financial_attributes` section. Follow `page.next_cursor` with the same package, section and filters until `has_more` is false. `total_items` counts matching observations, including unavailable values. A missing key in an older package does not imply a zero value.

Daily bank/card attributes use completed UTC days; current-day activity does not establish a full day of coverage. Cross-system observations may end partway through a day. Use the input manifest timestamps for the exact start-inclusive, end-exclusive interval; attribute date fields identify those calendar dates.

Each observation references `input_manifest_id`. Retrieve that input set with `view=section&section=financial_attribute_inputs&input_manifest_id=<id>`. Its resource IDs, evidence IDs, observation window and coverage identify the frozen inputs. Follow evidence IDs through [Evidence](/api-reference/evidence-traceability). A manifest is shared by attributes with the same input population; the definition determines which records and fields enter each calculation.

Console record drawers also use a reading view that preserves the assessment and coverage. An explicit notice identifies the detailed collections retrieved separately and provides their paged API paths and complete JSON export request.

PDF reports retain the assessment and an attribute coverage summary. Their report notice explicitly identifies the detailed attributes and input manifests available through JSON or the paged API; those two large collections are not printed in the PDF.

For bulk processing, request the package's JSON [export](/api-reference/export-formats). Full responses above the configured response limit return an explicit recovery response; they are not silently truncated. Historical packages retain their saved definitions and may predate the detailed attribute collections.

## Interpret the value

| Field | Meaning |
| --- | --- |
| `key` | Stable key for the calculation and its applicable context/period. |
| `value` / `unit` | Exact decimal-string result and unit. Ratios use fractional units, not percentages. |
| `status` | `available` or `unavailable`; unavailable values are null. |
| `window_start` / `window_end` | UTC dates for the half-open observation interval. |
| `as_of` | Knowledge cutoff for the assessment. Later source versions do not alter it. |
| `definition_version` / `calculation_version` | Pinned meaning and calculation implementation. |
| `coverage_ratio` | Stated coverage measure, not confidence in creditworthiness. |
| `missing_reason` / `reason_code` | Why the input scope cannot support the calculation. |
| `input_manifest_id` | Exact input population in this same immutable package. |

Transaction periods are anchored to the stated source observation window, which may be older than collection time. Read source freshness separately. Rolling periods that extend beyond proven account coverage are unavailable. Missing days are not zero-activity days. Category-specific zero values require enough classification detail to rule out matching activity; a broad operating-expense label cannot prove there were no software purchases.

Cross-system results use `data_scope: observed_records`. They describe the supplied invoices, bills, orders, inventory or other records. They do not assert complete business-wide coverage. A missing collection is unavailable. Differences in currency, date basis, source versions or required fields remain explicit.

## Attribute families

| Family | Examples | Input requirements |
| --- | --- | --- |
| Banking | Directional/category totals, counts, shares, amount distribution, active days and recency | Posted records, account context, complete period coverage and supported categories |
| Issuer cards | Purchases, refunds, repayments, fees and category distributions | Credit-account context and normalized event direction |
| Receivables and payables | Aging buckets, overdue amounts and observed collection/payment timing | Dated invoices/bills, due balances, payment dates and currency |
| Payments and payouts | Observed capture/refund amounts, fees, failure shares and settlement delays | Captured amounts, supported status and actual timestamps |
| Commerce and subscriptions | Order cancellation/refund measures, fulfillment observations and recurring obligations | Order amounts/status, subscription terms and observation dates |
| Inventory | Owned/consigned value and expiry exposure | Carrying values, ownership and explicit expiry dates |
| Loans and installments | Maturity exposure, scheduled amounts and observed overdue installments | Loan balances, currencies, due dates and remaining amounts |
| Accounting and reconciliation | Journal/credit observations and matched-record coverage | Explicit ledger entries and reconciliation relationships |

A current subscription snapshot does not establish historical churn. Current inventory does not establish stock aging or liquidation value. Transaction descriptions and merchant codes do not independently verify business purpose. Default probabilities, expected loss and credit limits require their applicable validated models; this attribute library does not imply those outputs.

## Download and explore definitions

- [Bank and card attribute catalog](/downloads/financial-attribute-catalog.json)
- [Cross-system attribute catalog](/downloads/cross-system-attribute-catalog.json)
- [Transaction categorization](/data-model/transaction-categorization)

The bank/card download uses `financial-attribute-references-v1` encoding to avoid repeating definitions. Resolve `selector` in `selectors`, `period` in `periods`, `statistic` in `statistics` and `context` in `contexts`. Statistics supply formula, unit and value type; selectors supply required inputs; contexts explain accounting interpretation. `calculation_version` applies to every entry. This preserves all definitions while reducing download size.

In Console, open **Dev Tools → Data Lookup → Financial intelligence**. Search by key, category, period or source, then inspect the formula, required inputs and interpretation. This reference explains calculations; use Sandbox scenarios to execute them with fictional records.
'''.replace('ATTRIBUTE_COUNT',f"{meta['attribute_definition_count']:,}")
    (ROOT/'data-model/financial-attributes.mdx').write_text(page)
    classification = '''---
title: "Transaction categorization"
description: "Understand bank and card transaction purpose, payment context, classification evidence, uncertainty and the treatment of transfers and repayments."
sidebarTitle: "Transaction categories"
keywords: [transaction categories, banking, credit cards, financial taxonomy]
---

Transaction categorization identifies the supported economic purpose of bank and issuer-card activity. The versioned Amlok taxonomy contains CATEGORY_COUNT leaf categories with hierarchical groups. Payment method, merchant industry, business use and accounting effect remain separate observations.

## Read the classification

Read normalized `bank_transaction.classification` through [Data](/api-reference/data-access) or the frozen [Evidence](/api-reference/evidence-traceability) used by a risk package. The result retains its taxonomy version, category ID/path, method, evidence-strength label, cash-flow role, cash effect, balance-sheet effect and reason codes.

`classified` means the supplied evidence supports that category. `unclassified` means no supported classification is available at that specificity. `conflicting` means relevant observations disagree. A broad category maps to an explicitly unspecified leaf; it does not become a guessed detailed purpose.

Confidence labels describe evidence strength. They are not calibrated probabilities, approval signals or a guarantee that a transaction is legitimate. Original provider labels remain in `source_category`, optional `provider_category` and authorized source payloads. An unsupported provider taxonomy version remains unmapped.

## Keep the classification dimensions separate

| Dimension | Meaning |
| --- | --- |
| Economic purpose | Sales receipts, payroll, supplier purchases, software, rent, financing, taxes, fees, investments, refunds and other supported purposes |
| Account context | Depository cash movement versus issuer-card or loan-ledger activity |
| Direction | Normalized inflow or outflow from the account holder's perspective |
| Payment rail/channel | ACH, EFT, wire, card, cash and the reported channel; a rail does not establish purpose |
| Counterparty role | Customer, supplier, employee, creditor, owner, processor or another supported relationship |
| Merchant category code | Reported merchant-industry classification; it does not establish what was bought or whether it was a business expense |
| Economic role | Business, personal, mixed or unknown; mixed use requires supported allocation |
| Card event | Purchase, repayment, refund, cash advance, fee, interest, reversal or other supported event |

## Avoid counting the same economic activity twice

- Bank loan proceeds and owner contributions are not operating sales receipts.
- Transfers between included depository accounts do not create consolidated operating revenue.
- A supported payment from the bank to the business's own credit card is a liability settlement. Own-account status alone does not make it an asset-to-asset transfer to eliminate.
- Issuer-card purchases create card activity; the later bank settlement creates cash movement. Do not add them together as purchases.
- Merchant processor payouts, underlying card sales and accounting revenue can describe the same economic activity. Reconcile them rather than summing them.
- Refunds, reversals and chargebacks retain their own purposes and linkage. They are not automatically new sales or fraud.
- Pending authorizations are not finalized posted activity.

## Classification boundaries

The library uses explicit supported purpose, normalized categories, structural transaction facts and versioned provider mappings. Merchant-name keywords or an MCC alone do not establish a verified financial purpose. Unknowns and conflicting labels remain visible. Category definitions do not establish tax treatment, legal ownership, a completed fraud investigation or a credit decision.

Source availability depends on the provider, country, account, consent, modules and history. A category in the taxonomy does not imply that every integration supplies the evidence to assign it. See [provider coverage](/data-model/provider-coverage).

Download the [complete versioned taxonomy](/downloads/transaction-taxonomy.json), including category definitions, applicability, hierarchy, independent axes and source references. Explore the same definitions in **Dev Tools → Data Lookup → Financial intelligence → Transaction categories**. Use the [financial attribute guide](/data-model/financial-attributes) to retrieve calculated observations by category and period.
'''.replace('CATEGORY_COUNT',str(meta['transaction_category_count']))
    (ROOT/'data-model/transaction-categorization.mdx').write_text(classification)
    for name in ['data-model/derived-attributes.mdx','data-model/api-alignment.mdx','api-reference/risk-package-methodology.mdx','console/data-lookup.mdx']:
        path=ROOT/name
        marker='\n## Detailed financial intelligence\n'
        body=path.read_text().split(marker)[0]
        path.write_text(body+marker+'\nUse the [financial attribute library](/data-model/financial-attributes) for detailed calculated observations and [transaction categorization](/data-model/transaction-categorization) for versioned bank/card purpose classifications. The detailed collections extend the same risk package and its paged views; they do not replace the scalar policy metric catalog. In Console, open **Dev Tools → Data Lookup → Financial intelligence** to search the definitions, formulas and input requirements.\n')
    config=json.loads((ROOT/'docs.json').read_text())
    def nav(value):
        if isinstance(value,list):
            if 'data-model/derived-attributes' in value:
                for target in ['data-model/financial-attributes','data-model/transaction-categorization']:
                    if target not in value:value.insert(value.index('data-model/derived-attributes')+1,target)
            for child in value:nav(child)
        elif isinstance(value,dict):
            for child in value.values():nav(child)
    nav(config)
    (ROOT/'docs.json').write_text(json.dumps(config,indent=2)+'\n')


def write_export_note():
    path=ROOT/'api-reference/export-formats.mdx'
    if path.exists():
        text_value=path.read_text().split('\n{/* BEGIN FINANCIAL ATTRIBUTE EXPORTS */}')[0]
        path.write_text(text_value+"""
{/* BEGIN FINANCIAL ATTRIBUTE EXPORTS */}
## Detailed financial attribute exports

Choose JSON for the complete immutable risk package, including every `financial_attributes` observation and `financial_attribute_inputs` manifest. PDF is a human-readable assessment report. It preserves the assessment, scalar metrics, evidence references and financial attribute summary, and explicitly identifies the two detailed collections available through JSON export or paged API sections. These large arrays are not printed in PDF; the report states their counts and retrieval paths.

The formatted report still has a size limit. If its remaining assessment content exceeds that limit, the export fails with `export_too_large`; use JSON for lossless retrieval. No attribute values are silently removed from JSON.
{/* END FINANCIAL ATTRIBUTE EXPORTS */}
""")

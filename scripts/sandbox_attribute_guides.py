"""Document the additive, source-backed detailed attribute scenario."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEGIN = '{/* BEGIN DETAILED ATTRIBUTE SCENARIO */}'
END = '{/* END DETAILED ATTRIBUTE SCENARIO */}'

DETAIL = '''## Explore detailed financial attributes

Choose **Underwriting > Detailed financial attributes** (`detailed_attribute_coverage`) with any of the six existing fictional business profiles. This scenario creates a new borrower and linked records for that run. It does not replace existing sample businesses, change historical assessments or require a separate business for each attribute.

The history covers **36 calendar periods: 35 complete months plus the current partial month**. A run created on November 19, 2026 starts on December 1, 2023 and includes current-month observations through its frozen cutoff. Daily bank and issuer-card attributes use completed UTC days; current-day activity cannot establish a complete day. On the first day of a month, a month-to-date attribute can correctly remain unavailable because no complete day has elapsed. The ordinary sample pack and existing comprehensive scalar-metric scenarios retain their 36 complete-month histories.

The detailed scenario retains 35 complete months of individual orders and captured processor payments. Its current partial-month additions are bank/accounting activity and status observations on existing provider records, such as dispute inquiries and unsuccessful payout attempts. It does not invent new current-month Shopify orders or Stripe captures; direct customer receipts are identified separately and backed by accounting records.

Inspect the returned observation windows. Current-month transaction activity is an interim source ledger; it is not added to a completed annual income statement or represented as a complete month. Bank cash, issuer-card purchases and merchant-processing settlements remain separate. A card purchase and its later bank repayment must not be counted twice as operating spending. Annual financial statements, collateral valuations and annual debt metrics retain their source closing date; the current loan schedule and latest bank balances can have a later observation date. A calculation requiring the same date, such as net debt, remains unavailable when those observations cannot be aligned.

The registry has **12,955 detailed definitions**: **12,805 bank/card definitions** and **150 cross-system definitions**. These combine contexts, categories, periods and statistics, rather than represent independent facts that must all be nonzero. The existing **184 scalar underwriting metrics across 24 dimensions** remain a separate catalog with their own [example coverage](/sandbox/sample-package#exercise-every-underwriting-metric).

Read each attribute's status and reason before asserting a value:

| Result | How to interpret it |
| --- | --- |
| Available, nonzero | The disclosed observations support this result in the stated context and period. |
| Available, zero | Complete, sufficiently classified observations support no matching activity, or the calculated balance or difference is zero. |
| Unavailable, sparse observations | Some statistics need more observations. For example, `p90` requires at least ten values and standard deviation requires at least three. |
| Unavailable, missing or restricted source | The required input population is not available or authorized. This is not zero activity. |
| Unavailable, insufficient classification detail | A broad expense label cannot establish whether a specific category, such as software, is absent. |
| Unavailable, empty period | The frozen source window contains no completed day for that period. |

Source examples follow each business's operations. A business need not have payroll deposits, consumer benefits, gambling activity or every possible issuer-card category. Do not treat a coverage percentage as credit quality, or fill unsupported combinations with invented transactions.

### Run and retrieve the detailed results

Get the current version from `GET /v1/sandbox/catalog`, then create the run with that exact `catalog_version`:

```bash
curl --fail-with-body -X POST "$AMLOK_API_BASE_URL/v1/sandbox/runs" \\
  -H "Authorization: Bearer $AMLOK_API_KEY" \\
  -H 'Content-Type: application/json' \\
  -H 'Idempotency-Key: detailed-attributes-maple-001' \\
  -d '{"scenario_id":"detailed_attribute_coverage","fixture_id":"maple-retail","catalog_version":"CATALOG_VERSION"}'
```

Poll `GET /v1/sandbox/runs/{id}` until completion. Follow its linked risk package and retrieve `GET /v1/risk-packages/{id}?view=summary`. Read `financial_attribute_summary` for evaluated, available and unavailable counts; these counts refer to the particular assessment, not a promise that every definition has a usable value.

Page through `view=section&section=financial_attributes&limit=25`, following `page.next_cursor` until `page.has_more` is false. Filter by an exact `attribute_key` or a literal `attribute_prefix`; keep the same filter on every page. For each result, retrieve the matching `input_manifest_id` from `section=financial_attribute_inputs`, then follow its evidence references to the frozen source records. [Financial attributes](/data-model/financial-attributes) explains the fields and download catalogs.

In Console, use **Dev Tools > Data Lookup > Financial intelligence** for definitions, formulas and required inputs. Use **Sandbox scenarios > Run history** to inspect execution and linked records. Saved runs and packages retain their original catalog version; a new catalog does not rewrite them.
'''


def replace_block(path, content):
    target = ROOT / path
    text = target.read_text()
    if BEGIN in text:
        prefix, rest = text.split(BEGIN, 1)
        _, suffix = rest.split(END, 1)
        text = prefix.rstrip() + '\n\n' + BEGIN + '\n' + content.strip() + '\n' + END + suffix
    else:
        text = text.rstrip() + '\n\n' + BEGIN + '\n' + content.strip() + '\n' + END + '\n'
    target.write_text(text)


def write_guides():
    import json
    version = json.loads((ROOT / 'data/sandbox-catalog.json').read_text())['version']
    detail = DETAIL.replace('CATALOG_VERSION', version)
    report_path = ROOT / 'downloads/sandbox-attribute-coverage-summary.json'
    if report_path.exists():
        report = json.loads(report_path.read_text())
        counts = report['current']
        detail += f'''
### Measured example coverage

The [coverage snapshot](/downloads/sandbox-attribute-coverage-summary.json) uses catalog `{report['fixture_catalog_version']}` and frozen source observations at **{report['fixture_observation_at']}**. It checks actual returned risk packages across **{len(report['scenarios'])} cases**: the starter businesses, complete scalar-metric examples, detailed attribute examples, individual-income and comparable-monitoring cases. Counts are the union across those cases, not the result promised for one borrower.

| Definition outcome across the audited cases | Count |
| --- | ---: |
| At least one supported nonzero example | {counts['nonzero']:,} |
| Supported zero examples, with no nonzero example | {counts['zero_only']:,} |
| Unavailable in every audited case | {counts['unavailable_everywhere']:,} |
| Total definitions | {counts['definitions']:,} |

That is **{counts['numeric_including_zero']:,} definitions with a supported numeric example**, including legitimate zeros. All **150 cross-system definitions** have a nonzero example somewhere in the cases. Every amount, count, amount-share and active-days definition has a numeric example. The remaining 897 definitions are statistics: 383 percentile, 162 standard-deviation, and 88 each of mean, median, maximum and days-since-last. A category with no eligible activity has no meaningful mean or last-activity date; a sparse category may not support a percentile. These results remain unavailable rather than receiving invented observations.

Download the [per-attribute coverage manifest](/downloads/sandbox-attribute-coverage.json) to find the exact scenario, business, representative value, period and missingness reasons for each definition. The manifest explains its compact observation codes and case indices. This is a dated, reproducible example snapshot; new run dates can change calendar windows and date-sensitive results. It does not claim every definition is nonzero, or that any single business should exercise all categories.
'''
    for page in ['sandbox/sample-package.mdx', 'api-reference/sandbox-journeys.mdx']:
        replace_block(page, detail)
    replace_block('sandbox/businesses-and-scenarios.mdx', '''## Detailed financial attribute examples

Choose **Detailed financial attributes** (`detailed_attribute_coverage`) with any existing business profile. Each run contains 35 complete months plus the current partial month, within a total of 36 calendar periods. It exercises detailed bank, issuer-card and cross-system observations without changing your existing samples. The ordinary starter and scalar-metric cases retain their complete-month history.

Read the [detailed scenario guide](/sandbox/sample-package#explore-detailed-financial-attributes) for execution, source evidence and the distinction between nonzero values, supported zeros and unavailable attributes. A catalog definition is not a guarantee of applicable activity for every business.''')
    replace_block('console/sandbox.mdx', '''## Explore detailed financial attributes

Choose **Underwriting > Detailed financial attributes** and one of the six fictional businesses. The scenario creates its own linked history with 35 complete months plus the current partial month. Run history links to the resulting assessment and source records. **Dev Tools > Data Lookup > Financial intelligence** explains the detailed definitions and formulas.

Use the [detailed scenario guide](/sandbox/sample-package#explore-detailed-financial-attributes) to retrieve paged attributes and supporting input manifests. Check each status and observation window: a supported zero, a sparse sample and a missing source mean different things.''')
    replace_block('data-model/financial-attributes.mdx', '''## Test with coherent Sandbox records

Run `detailed_attribute_coverage` with any of the six fictional business profiles. Its history covers 35 complete months and the current partial month, totaling 36 calendar periods. The scenario supplies detailed category and cross-system records while preserving the distinction between bank cash, issuer-card activity and merchant settlements.

See the [detailed attribute scenario](/sandbox/sample-package#explore-detailed-financial-attributes) for requests, result traversal and interpretation. An available zero requires supported absence; missing coverage, restricted records, insufficient category specificity and sparse statistical samples remain unavailable. A business does not need every category in the registry to be populated.''')


if __name__ == '__main__':
    write_guides()

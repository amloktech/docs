"""Generate the narrative contract for the finalized enterprise behavior."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def write(slug, title, description, body):
    (ROOT/'api-reference'/f'{slug}.mdx').write_text('---\ntitle: '+json.dumps(title)+'\ndescription: '+json.dumps(description)+'\n---\n\n'+body.strip()+'\n')


def generate():
    write('products-and-endpoints','Products and endpoint scope','How Insights, Signal, and shared infrastructure fit together.', '''
AMLOK has two paid products. API categories organize financial data and technical capabilities; they are not additional products or separate charges.

| Capability | Product ownership | AMLOK charge |
| --- | --- | --- |
| New full underwriting for an application | Insights | One charge when the agreed output is completed and published |
| Portfolio monitoring and change-driven reassessment | Signal | One charge per active borrower/business per workspace per month |
| Verification, lien searches, attribute calculations and analytical investigation | Included stages within an authorized Insights or Signal workflow | No additional AMLOK product charge |
| Connections, consent, evidence uploads, normalized data reads and result downloads | Shared infrastructure | No additional product charge for the API call |
| Webhooks, synchronization, availability checks and reporting | Shared infrastructure | No additional product charge for the API call |

Provider data or verification charges, where applicable, follow the agreement. API access does not create a new standalone AMLOK service rate.

## Insights

Start a root `underwrite` workflow with the application and ready input manifest. AMLOK returns `product: insights`, the workflow ID, workload report, and eventually the completed risk snapshot and billing usage ID. A retry of that run does not create a second underwriting charge. A new full underwriting is a distinct authorized request.

## Signal

Create monitoring from an approved baseline. All monitors for a borrower/business share one monthly monitoring-period record. Signal uses existing evidence and new records to reassess risk without launching a separately billed Insights underwriting.

The full monthly rate is deducted at 00:00 UTC on the first day of each calendar month before monitoring proceeds. First activation during a month deducts the full monthly rate immediately, without proration. Repeated activation, pauses, resumes, checks and reassessments do not add another charge in an already paid period. See [Signal pricing](/pricing/signal).

## Included processing stages

Verification, lien-search and calculation requests require `processing_context`. Non-underwriting workflow requests also require it. Supply exactly one of:

```json
{"product":"insights","workflow_run_id":"wfr_example"}
```

```json
{"product":"signal","monitoring_period_id":"monitoring_period_example"}
```

The context must belong to the same workspace and subject. Insights must be an unfinished authorized underwriting; Signal must have an active paid period. The stage must be permitted by the agreed workflow and fit its workload limits. A context is not permission to run arbitrary additional analysis. AMLOK deduplicates equivalent stage work already requested by the orchestrator. Unrelated, finished, cancelled, unpaid or unentitled contexts are rejected with `409 invalid_state`.

These endpoints support integration steps within the complete product. They do not offer independently purchased verification, search, calculation or investigation services.

## Institution intervention

AMLOK supplies risk results, alerts and evidence. Your institution decides and performs outreach, collections, credit-limit changes and other intervention in its own systems. There are no servicing cases, tasks, borrower messages, payment promises or action-approval endpoints. Read-only loan and repayment records remain evidence supplied by lender systems.
''')
    write('credit-reporting','Credit reporting','Read available and spent credits without payment controls.', '''
Each workspace has one CAD credit balance shared by Insights and Signal. Paid and promotional top-ups join the same balance with no consumption priority.

## Available and spent credits

| Field | Meaning |
| --- | --- |
| `available_credits` | Credits available to spend now. Successful top-ups add credits; actual product charges and final refunds reduce them. |
| `spent_credits` | Cumulative product charges since the account opened, less corrections that reverse an erroneous charge. |

There are no reserved credits, held balances or separate posted-credit balances. A payment still in progress is visible in funding history, but it becomes credit only after successful completion. An unfinished underwriting has not spent credits. A final cancellation refund is a return of unused credits, not product spend.

`available credits = successful funding + corrections - product charges - cancellation refunds`

Read [the credit balance](/api-reference/endpoints/billing/retrieve-credit-balance) and [consumption reports](/api-reference/consumption-reporting). Transaction timestamps such as `posted_at` identify when a historical entry was recorded; they do not describe another kind of credit.

## Automatic top-ups

The trigger uses **available credits**. With auto-pay enabled, a balance strictly below the configured threshold triggers the selected payment. The threshold is at least **CAD 200.00** and the customer-funded top-up is at least **CAD 500.00**. At exactly the threshold, no below-threshold trigger has occurred.

The [billing account](/api-reference/endpoints/billing/retrieve-billing-account) reports the actual `auto_top_up_enabled`, `auto_top_up_threshold` and `auto_top_up_amount` settings. Only the portal changes them. Payment attempts are deduplicated while the same top-up is in progress; every usage debit must not launch another duplicate collection. Failed collections leave credits unchanged and follow the portal's payment handling, without allowing a negative balance.

Processing can use credits below CAD 200.00 if the balance covers its cost. Read-only reports remain accessible without a new product charge. See [processing lifecycle](/api-reference/processing-lifecycle) for insufficient-credit handling.

## Portal and API responsibilities

The client portal manages card/bank payment methods, top-ups, automatic-payment settings and cancellation. Enterprise clients can also request cancellation through their account manager. The public API provides reports and exports only. There are no wallet-management, payment, top-up, refund-request, transfer or cancellation commands.

## Cancellation

Cancellation immediately stops processing, deductions, and upcoming top-ups. Unfinished work creates no charge. Full account closure occurs at the end of the request month. AMLOK immediately refunds all remaining available credits, including promotional top-ups, to the saved portal bank account. Correctly spent credits are non-refundable. Bank receipt can take 7-10 business days after issuance.

Data is deleted after that month closes and necessary final information is generated. Export needed evidence before deletion. Necessary final billing and refund records are retained separately, without borrower data or continuing workspace API access. See [cancellation and refunds](/pricing/refunds-and-payouts).
''')
    write('consumption-reporting','Consumption reporting','Reconcile product charges, credit activity, historical rates and reproducible reports.', '''
Use one immutable billing snapshot to answer what was consumed, what it cost, and how available credits changed. Each API key is bound to one workspace.

## Billable usage

| Product | Unit | Standard | Advanced | Complex | Charge timing |
| --- | --- | ---: | ---: | ---: | --- |
| Insights | Completed underwriting | CAD 5.00 | CAD 15.00 | CAD 35.00 | Successful completion and publication of the agreed output |
| Signal | Active borrower/business per month | CAD 3.00 | CAD 5.00 | CAD 8.00 | Beginning of the UTC calendar month, or full charge at first activation during the month |

Signal includes monitoring and reassessment. Multiple monitors, checks or facilities do not create more account-month charges. Included verification, searches, calculations and investigations do not add another AMLOK charge. The monthly consumption unit does not change the monthly minimum's annual payment schedule.

Each usage record identifies its subject, product, tier, billable quantity, rate, amount, period, historical rate-card ID and ledger entry. Insights additionally links the workflow run, application, frozen input manifest and risk snapshot. Signal links the shared monitoring-period record and baseline. See [evidence traceability](/api-reference/evidence-traceability).

Custom quotes retain Standard, Advanced or Complex with negotiated rates and explicit workload limits. The rate card reports the product's counting basis, limits and charge timing. [Workload reports](/api-reference/workload-reporting) show processing counts separately from billable quantities.

## Amounts and corrections

Amounts are CAD decimal strings with two decimals. Round the effective discounted unit rate half up to two decimals first, multiply by the billable quantity, then round the line half up to two decimals. Totals sum those rounded lines. Never apply today's rate card to an earlier charge.

Usage records exist only for actual charges or corrections, with `status: posted`. There is no pending usage credit category. A charge correction creates a negative `reversal` linked by `reverses_usage_id`; the original remains immutable. The ledger reversal has a positive amount and references the original ledger entry. Cumulative reversals cannot exceed that original charge. A replacement charge, when appropriate, is separate.

## Reproduce a report

1. Read [the current billing snapshot](/api-reference/endpoints/billing/retrieve-current-billing-snapshot); save its ID, `as_of` and ledger sequence.
2. Reuse `snapshot_id` across credits, usage, consumption, funding, rate cards and ledger reads. The response header `X-Billing-Snapshot-ID` also supplies the selected snapshot, including for empty lists.
3. Preserve the same snapshot and filters across cursor pages and export requests.
4. Use a statement's own snapshot, exact period and revision to reproduce that statement.

Snapshots freeze financial resource versions and configuration at the cutoff. Later corrections appear only in newer snapshots. Conflicting cursor parameters return `400`; unknown snapshots return `404`. A financial snapshot does not freeze a source-data collection; use [synchronization checkpoints](/api-reference/synchronization) for that purpose.

## Filters and periods

Intervals are UTC and `[from, to)`, with an inclusive start and exclusive end. Usage supports event time (`occurred_at`) or ledger time (`posted_at`); consumption includes only recorded charges and reversals. Product, tier, source resource and historical rate-card filters are supported. Grouping by day or month preserves product, tier and billing unit; it never combines underwritings and account-months into one quantity.

Ledger entries sort by sequence. Other financial collections document their ordering. Default page size is 100, maximum 200. Payment source labels distinguish annual prepayments, top-ups and promotions for audit; they do not create separate credit balances or priorities.

## Reconciliation example

All endpoint examples using `billing_snapshot_example` share this dataset:

| Activity | CAD | Available credits |
| --- | ---: | ---: |
| Annual prepayment completed September 30 | +12,000.00 | 12,000.00 |
| One Standard Signal business charged October 1 | -3.00 | 11,997.00 |
| One Standard Insights underwriting completed October 23 | -5.00 | 11,992.00 |

October usage and consumption total **CAD 8.00**. The October statement opens at CAD 12,000.00 and closes at CAD 11,992.00. Cumulative spent credits are CAD 8.00. The unfiltered ledger includes all three entries; an October ledger export includes the two October charges. An October funding export is empty because the prepayment completed in September.

`closing = opening + funding - usage - final-cancellation refunds + adjustments`

Funding, usage and refund columns are nonnegative magnitudes. Adjustments are signed. Correcting ledger reversals are included in adjustments and are not counted again as negative statement usage. Consumption summaries, by contrast, expose gross charges, correcting adjustments and net usage explicitly.

## Export and finalize

Create an asynchronous report for `usage`, `ledger`, `statement` or `funding`. Usage supports event or posting time; ledger and statements use `posted_at`; funding uses `initiated_at`. Only usage exports accept usage filters. Poll until ready, then request a short-lived download link. These requests do not change credits.

[Export formats](/api-reference/export-formats) defines JSON schemas, CSV columns, empty results, decimal handling and downloadable examples. Verify the file's SHA-256 and retain its snapshot ID. A repeated export of the same snapshot and filters reproduces the same financial data; job metadata and delivery URLs can differ.

Final statement revisions are immutable. Later corrections create a new revision with `supersedes_id`. On cancellation, processing and deductions stop immediately; unused credits are refunded at month-end closure. No new product charge can post after the cancellation cutoff. Final documents and refund confirmations are supplied through the closure process. Workspace API access ends on deletion; minimal financial/refund records retained separately contain no borrower evidence. See [cancellation and refunds](/pricing/refunds-and-payouts).
''')
    write('processing-lifecycle','Processing lifecycle','Follow evidence collection, workload checks, credit deductions and terminal states.', '''
AMLOK coordinates assessment processing. It does not execute borrower outreach, servicing actions or credit-limit changes.

## Workflow states

| State | Meaning and next step |
| --- | --- |
| `queued` / `running` | Authorized work is accepted or executing. Poll with backoff or consume workflow events. |
| `waiting_for_data` | Required evidence is missing or not yet accepted. Read requirements and submit an authorized document with its `requirement_id`. |
| `blocked_by_limit` | The agreed workload cannot cover further work. AMLOK must agree expanded scope before it resumes. |
| `waiting_for_credits` | Available credits cannot cover final completion. Fund through the portal; AMLOK retries the same completion without duplicating processing or charges. |
| `completed` | Required output is published. For a root Insights run, its single charge and output publication complete atomically. |
| `failed` | Processing failed definitively. Inspect the reason and use support when needed. No completed-underwriting charge is created. |
| `cancelled` | Processing has stopped. No later output publication or charge is permitted. |

There is no workflow state for approving borrower communications or other servicing actions.

## Evidence requirements

Read the requirement to identify the missing evidence and parent workflow. Upload the requested document with `requirement_id`; the subject and workspace must match. Upload acceptance does not mean evidence acceptance. AMLOK's validation process or authorized evidence reviewer accepts, rejects or waives the requirement according to the agreed assessment rules. These review actions are managed in the platform, not public servicing endpoints. Accepted evidence resumes the waiting assessment automatically; rejected evidence includes a reason and remains unresolved. AMLOK does not contact the borrower to collect it.

## Credits and concurrent work

There is one spendable balance and no reservations. AMLOK checks funds before accepting a billable request. Acceptance alone does not spend Insights credits. At successful completion, the balance check, exact usage debit and final output publication are atomic and idempotent per root workflow. Concurrent completions cannot spend the same credits or make the balance negative.

If another operation consumes credits before completion, the run waits for funding without publishing the final output or charging. After funding, the same completion resumes. A pre-execution `402` creates neither an accepted job nor a debit, and may be retried with the same intended idempotency key. A job already accepted keeps its ID; do not create another run to resume it.

Signal deducts its monthly charge before monitoring starts for that period. Insufficient credits leave the period `unfunded` and monitors `blocked` with `blocked_reason: insufficient_credits`. Once funded, AMLOK activates only the current period after its one successful charge. No debt or charge for missed inactive months accumulates. A manually paused monitor stays paused until explicitly resumed.

## Monitoring and alerts

Monitor states are `active`, `paused`, `blocked` or `cancelled`. Customers can set active, paused or cancelled through the monitor update endpoint; blocked is system-controlled. `blocked_reason` distinguishes insufficient credits, workload limits, missing evidence and unavailable consent. Correct the underlying condition before processing resumes. Cancelling one monitor does not cancel other configurations for the borrower or create a refund of its already consumed monthly charge.

Alerts use `open` and `resolved`. AMLOK resolves a signal only when fresh, comparable evidence demonstrates the triggering condition has cleared. An outage, missing evidence or a client's acknowledgement is not resolution. Institution acknowledgements, assignments and follow-up stay in the institution's systems.

## Account cancellation

All processing, deductions and upcoming top-ups stop immediately. Pending workflows, calculations, lien searches, verification and document extraction become `cancelled`, with `stop_reason: account_cancellation` (or `parent_cancelled` for a child). A late provider response does not resume the workflow or create a charge. Read access continues only until workspace deletion under the month-end closure policy.
''')
    write('workload-reporting','Workload limits and reporting','Read measured workload and handle an agreed limit before additional processing.', '''
The rate card defines allowed workload; a [workload report](/api-reference/endpoints/billing/list-workload-reports) shows actual counts, limits, remaining capacity and blocking dimensions. Workload records are not extra billable units.

Insights counts its full frozen underwriting evidence, including at least 12 months of banking statements and transactions. Signal counts newly processed records and each updated source-record version within the UTC month. The same source record and version is counted once across all monitors for the borrower/business; retries and unchanged baseline reads do not count again.

Each report links the subject, product, tier, historical rate card and either the underwriting run or monitoring period. Bank accounts and non-banking business integrations are separate dimensions. All dimensions and analysis scope must fit the assigned tier. Custom rates use an existing tier with explicit negotiated limits.

## Limit handling

- At a limit, already-in-scope work can proceed. Only work that would exceed a dimension is blocked.
- Known over-limit requests return `422 workload_limit_exceeded` before excess processing.
- If additional records are discovered asynchronously, processing pauses before consuming records beyond the allowance. The parent workflow becomes `blocked_by_limit`, or a monitor becomes `blocked` with that reason.
- Counter updates and limit checks are atomic across concurrent processing, so parallel monitors cannot bypass the cap.
- AMLOK must agree a scope change and effective rate card before resuming. There is no automatic upgrade, additional fee or combination of different tier limits.
- A Signal month's record allowance resets at the next UTC calendar month. Historical reports retain the earlier counts and limits. Resetting capacity does not waive the next month's Signal charge or an unresolved source-count/scope limit.

Read `as_of` and keep a pagination cursor for a consistent progress snapshot. Start a fresh first-page read to see updated counts. This operational progress snapshot is separate from an immutable financial billing snapshot.

See [complexity tiers](/pricing/complexity-tiers), [processing lifecycle](/api-reference/processing-lifecycle) and [rate cards](/api-reference/endpoints/billing/retrieve-billing-rate-card).
''')
    write('evidence-traceability','Evidence and charge traceability','Follow exact inputs from a completed assessment to its usage charge.', '''
An underwriting is identified by its workflow-run ID. There is no separate opaque underwriting resource that clients must infer.

## Freeze inputs

1. Synchronize permitted sources and resolve the required evidence coverage.
2. Select a ready input manifest for the subject. Read its coverage, record count and [entries](/api-reference/endpoints/risk/list-input-manifest-entries).
3. Start the full underwriting with `application_id`, `input_manifest_id`, and input resource IDs present in that manifest. The server retains the initial ID as `initial_input_manifest_id`.
4. Any included attribute calculations use the same manifest and a window contained within its coverage. They require the parent product context.

The current `input_manifest_id` identifies the run's evidence set. The result's `evidence_manifest_id` and the usage record refer to the final set used at completion. A changed source record never rewrites an existing manifest or completed assessment.

If an unfinished run is waiting for required evidence, AMLOK can validate an uploaded document and attach a successor manifest within the same agreed scope. The run keeps its ID and one completion charge. Its record version increases, and an audit event identifies the old and new manifest IDs; `initial_input_manifest_id` remains unchanged. Recompute affected calculations against the successor before completion. Additional evidence must fit the agreed workload limits; expanded scope requires AMLOK agreement. After completion, a separately requested full underwriting is a new Insights run.

## Audit exact versions

Manifest entries contain the resource type, ID, normalized version, source ID/version and a content digest. Pagination stays bound to that immutable manifest. Retrieve a resource with `manifest_id` to read that exact normalized version. The document download request accepts the manifest ID for the exact original document bytes. Missing or deleted evidence returns an explicit error, never today's replacement version.

To verify the manifest digest, concatenate all entries in `(resource_type, resource_id, resource_version)` order. Serialize each entry as compact UTF-8 JSON with lexically sorted keys, no spaces and a final LF; hash the concatenated bytes with SHA-256. This verifies membership consistency. A digest alone does not prove source authenticity or legal sufficiency. Individual `content_sha256` values identify frozen evidence content; document file verification uses the document's `sha256` against the original downloaded bytes. Digests and evidence in examples are synthetic.

## Connect results and billing

| Record | References |
| --- | --- |
| Insights workflow | Application, input manifest, workload report, output resources and billing usage |
| Risk snapshot | Workflow, application, evidence manifest and billing usage |
| Insights usage | Subject, workflow-run ID, application, manifest, risk snapshot, historical rate card and ledger entry |
| Signal usage | Subject, monitoring-period ID, baseline snapshot, rate card and ledger entry |
| Monitoring period | One borrower/business/month, its charge and combined workload report |

A Signal reassessment is linked to its paid monitoring period and creates no additional Insights debit. Included child stages do not have independent charge records. All references must belong to the key-bound workspace and appropriate subject; report access never grants broader evidence access.

Export evidence before workspace deletion. Necessary financial records retained for final refunds do not retain borrower source data, documents or analysis outputs.
''')
    write('synchronization','Reliable synchronization','Bootstrap a consistent snapshot and resume normalized-data changes without gaps.', '''
Use a synchronization checkpoint for source-data replication. Billing snapshots serve a separate purpose: financial reconciliation.

## Bootstrap without a gap

1. [Create a checkpoint](/api-reference/endpoints/platform/create-synchronization-checkpoint) for the entitled resource types you need. Save its ID, `as_of`, `expires_at` and `resume_cursor`.
2. Read each selected collection with `snapshot_id` equal to the checkpoint ID. Follow each collection's cursor with unchanged filters. All bootstrap reads describe the same boundary.
3. After storing the snapshot, read `/v1/changes` using the checkpoint's `resume_cursor`. It begins strictly after that boundary.

Checkpoint creation is a read-only operation and does not start provider synchronization or spend credits. Collections not included in the checkpoint are rejected. Complete bootstrap before `expires_at`; otherwise start again with a new checkpoint.

## Apply and checkpoint changes

Changes are ordered by workspace `sequence`, with created, updated and deleted actions. Sequence gaps are valid for filtered resource types. Deduplicate by resource type, ID and version, and never overwrite a newer version with an older delivery.

Apply every item durably before committing the response's `resume_cursor`. Save data and cursor together transactionally where possible. A crash before committing the cursor may replay a page; idempotent application prevents duplicate effects. Do not advance past an item that failed to persist.

`page.next_cursor` continues a multi-page response. `resume_cursor` is the durable change-feed position after the delivered items and is returned even on the last or an empty page. When `has_more` is false, keep the resume cursor and poll it later with backoff. Never replace it with null or a collection cursor.

Each response supplies `cursor_expires_at`. Poll before expiry; do not assume an unspecified retention period. An expired cursor returns `410 cursor_expired`. Rebuild using a fresh checkpoint and replace the replicated snapshot only after the new bootstrap succeeds. Reconcile absent records during that replacement so deleted records do not survive locally.

The cursor binds workspace, institution, environment, resource types and filters. Attempts to change these return an error. Workspace deletion revokes access and checkpoints. Financial resources use their own billing snapshot and events, not this normalized-data feed.
''')

    exports=json.loads((ROOT/'data/report-export-contract.json').read_text())
    body='''Billing reports support `usage`, `ledger`, `statement` and `funding`. Exports are read-only. Their schema version is **1.4.2**. The selected immutable snapshot and filters determine the financial rows; there is no hidden truncation or maximum-row omission. Larger files are generated asynchronously.

## JSON

JSON files contain `schema_version`, `report_type`, `snapshot_id`, `as_of` and a `rows` array. The row schema matches the corresponding API resource. Empty results use `rows: []`. Amounts remain decimal strings with two digits after the decimal point, and nullable values remain JSON null. Resource IDs and record versions are preserved.

## CSV

CSV files use UTF-8 without a byte-order mark, comma delimiters, CRLF line endings and RFC 4180 quoting. The first row contains the exact ordered headers below. Empty results contain that header row only. Null is an empty cell; an actual empty text value is not permitted for these reporting fields. Dates use the API's UTC representation; amounts use a period decimal separator without currency symbols or thousands separators.

Every data row starts with `export_schema_version`, `export_snapshot_id` and `export_as_of`. Arrays or objects, if present in a future compatible row schema, use compact JSON in a quoted cell. Text beginning with a spreadsheet formula character (`=`, `+`, `-`, `@`, tab or carriage return) is prefixed with a single quote. Validated numeric decimal fields retain their minus sign without escaping. Consumers should treat text cells as data, not evaluate formulas.

## Schemas, samples and columns

The examples share the endpoint fixture: CAD 12,000.00 funded before October, then CAD 3.00 Signal and CAD 5.00 Insights consumption in October. October funding is therefore an empty export. The ledger export contains only the two movements in the selected October window.
'''
    for item in exports:
        kind=item['type']
        body+='\n### '+kind.capitalize()+'\n\n[JSON Schema](/downloads/report-schemas/'+kind+'.schema.json) · [JSON example](/downloads/report-examples/'+kind+'.json) · [CSV example](/downloads/report-examples/'+kind+'.csv)\n\n```text\n'+','.join(item['columns'])+'\n```\n'
    body+='''
## Delivery and verification

Download links require a ready, unexpired report. Verify SHA-256 over the exact downloaded bytes before parsing. Content types are `application/json` or `text/csv; charset=utf-8`; filenames identify report ID, type and extension. A failed generation returns `status: failed` and a safe `failure_code`, not a partial file marked ready.

An expired report requires a new export of the same saved snapshot and filters. Do not silently substitute today's data. File-delivery URLs and job timestamps can change; financial rows and schema remain reproducible. Workspace deletion removes access, so retain required exports before closure.
'''
    write('export-formats','Billing export formats','Versioned JSON schemas, CSV columns, file examples and integrity checks.',body)

    # Refine the original guide templates after generation, preserving unrelated narrative.
    replacements={
        'waiting_for_approval':'waiting_for_data',
        'Cancel pending work and release unused holds without capture.':'Pending work is cancelled without a usage debit.',
        'Retention, residency, legal holds, deletion, and permitted purposes.':'Retention during active use, residency, month-end workspace deletion, and permitted purposes.',
        'Confirm source permissions and your institution\'s approval before enabling consequential actions.':'Confirm source permissions and product scope before enabling assessment processing.',
        'Resource records inherit':'Canonical normalized financial-data records inherit',
        'GET endpoints use a dedicated `*Read` schema':'GET endpoints for canonical financial-data records use a dedicated `*Read` schema',
        'Response-only helper objects such as calculation jobs and signed links use their documented helper schemas inside `data`.':'Reporting, manifests, monitoring periods, checkpoints, workload reports, calculation jobs and signed links use their own documented schemas inside `data`.',
        'Bootstrap by reading the required collections; the cursor bootstrap, expiry, and retention windows remain deployment decisions.':'Create a synchronization checkpoint before collection bootstrap and resume changes from its cursor. Every change response includes a durable resume cursor and explicit expiry, including empty pages. See [reliable synchronization](/api-reference/synchronization).',
    }
    for path in (ROOT/'api-reference').glob('*.mdx'):
        content=path.read_text()
        for a,b in replacements.items():content=content.replace(a,b)
        path.write_text(content)
    p=ROOT/'api-reference/workflows.mdx';t=p.read_text()
    t=t.replace('with an approved workflow version.', 'as an included stage, with an approved workflow version and authorized `processing_context`.')
    t=t.replace('Use the returned manifest ID for [attribute calculations](/api-reference/endpoints/risk/calculate-attributes), with a calculation window contained in the frozen manifest window.', 'Use the returned manifest ID for the underwriting and its included calculations, with a calculation window contained in the frozen manifest window.')
    t=t.replace('with `workflow_type: underwrite`, an approved version, and input resource IDs.', 'with `workflow_type: underwrite`, an approved version, `application_id`, `input_manifest_id`, and input resource IDs present in that manifest. Included calculation requests identify this parent in `processing_context`.')
    t=t.replace('Use `workflow_type: investigate` to analyze', 'Use `workflow_type: investigate` with the existing product `processing_context` to analyze')
    t+='\nSee [product scope](/api-reference/products-and-endpoints), [processing lifecycle](/api-reference/processing-lifecycle), and [evidence traceability](/api-reference/evidence-traceability).\n';p.write_text(t)
    p=ROOT/'api-reference/errors.mdx';t=p.read_text();at='| `invalid_request` |'
    t=t.replace(at,'| `validation_error` | 400 | No | Correct the invalid field or projection. |\n| `cursor_expired` | 410 | No | Create a new synchronization checkpoint and rebuild the snapshot. |\n| `workload_limit_exceeded` | 422 | No, until scope is agreed | Inspect the workload report and agree expanded scope before processing. |\n'+at)
    t+='\nFor an accepted job that later runs short of credits, inspect `waiting_for_credits` rather than submitting a duplicate run. See [processing lifecycle](/api-reference/processing-lifecycle).\n';p.write_text(t)
    # Keep worked requests executable under the same contract as the endpoint examples.
    import re
    index={entry['id']:entry for entry in json.loads((ROOT/'data/api-reference-index.json').read_text())}
    p=ROOT/'api-reference/examples.mdx';t=p.read_text()
    block_number=-1
    def current_payload(match):
        nonlocal block_number
        block_number+=1
        mapping={0:('EP142','request'),1:('EP142','response'),4:('EP143','request'),5:('EP143','response'),9:('EP147','request'),10:('EP147','response')}
        if block_number not in mapping:return match[0]
        oid,key=mapping[block_number]
        return '```json\n'+json.dumps(index[oid][key],indent=2)+'\n```'
    t=re.sub(r'```json\n(.*?)\n```',current_payload,t,flags=re.S)
    t+='\nThe compact synthetic evidence examples demonstrate request shape and reference linkage. They are not a production underwriting dataset or a benchmark for the minimum twelve months of banking evidence.\n'
    p.write_text(t)
    import runpy
    runpy.run_path(str(ROOT/'scripts/sync-enterprise-data-model.py'))['sync']()


if __name__=='__main__':
    generate()

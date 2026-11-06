"""Guidance for the institution's Hub, data and financial reporting workflow."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent.parent


def write_guides(spec,f,index):
    from current_api_guides import page
    def write(name,title,body):
        page('api-reference/'+name,title,title+' using the AMLOK institution API.',body)
    def append(name,body):
        p=ROOT/('api-reference/'+name+'.mdx');p.write_text(p.read_text().rstrip()+'\n\n'+body.strip()+'\n')
    def sample(name):
        op=next(o for o in index if o['id']==name)
        return '```bash\n'+spec['paths'][op['path']][op['method'].lower()]['x-codeSamples'][0]['source']+'\n```'
    write('integration-hub','Embed a configured Integrations Hub','''
Configure available integrations, category steps and branding in the console, publish that Hub, and embed the borrower experience in your own application. Public connection endpoints launch and observe that experience; they do not configure provider adapters or make your team orchestrate ingestion.

## Configuration and execution

| Responsibility | Where it belongs |
| --- | --- |
| Select integrations, categories and branding | Published Hub configuration in the console |
| Associate the Hub with the correct borrower | Your authenticated backend and a short-lived embedding session |
| Provider authorization, consent and collection | AMLOK and the embedded Hub |
| Observe readiness, freshness and reconnect requirements | Connection API and notifications |
| Retrieve authorized collected and enriched data | Data API, independently of an assessment |
| Request underwriting | Origination API |

## Launch for one borrower

Your backend first verifies the person using your flow is allowed to connect data for the selected borrower. It creates a session with that borrower ID and the published embedding_version_id. A borrower-supplied ID alone is not proof of that association.

'''+sample('createEmbeddingSession')+'''

Use the returned launch_url as the source of the embedded Hub in your approved borrower flow. The session is short-lived and bound to the borrower, institution, workspace, environment and published Hub version. The API key stays on your backend. The session cannot add integrations disabled in that published version. Return URLs and embedding origins must be approved for the institution; the Hub must not accept arbitrary redirects or embedding origins. Provider authorization can require a provider-approved redirect or new window.

This contract specifies the session API and launch URL. It does not claim a distributed JavaScript SDK or invent a widget initialization method.

## Distinguish connection completion from data readiness

A session's completed state means the borrower finished the connection journey. A browser callback or return URL is not authoritative proof: confirm the session server-side or consume the signed embedding_session.completed event.

The session returns connection_ids and consent_ids. A connection has separate authorization status, data_status, last_successful_sync_at, source_as_of and coverage. A connected source can still be collecting or have incomplete data. Read the [data API](/api-reference/data-access) whenever records become available; a completed risk package is not required.

Use the returned connection IDs when submitting the origination or enrolling the funded deal. These select the authorized sources for that application; they do not instruct your team to run synchronization. Every source must match the borrower and allowed purpose. A prior underwriting consent does not automatically authorize post-funding monitoring.

## Recover access

Use the same session endpoint with purpose reauthorize and the affected connection_id to return the borrower to the Hub. AMLOK manages provider authorization and resumes permitted collection. Revoking consent stops future collection; access to retained historical information follows the configured authorization and retention policy.

Connections exist for visibility and recovery. Removing them would hide useful information about whether an institution can rely on the data; it is not necessary to call every connection endpoint in the happy path.
''')
    write('data-access','Retrieve collected and enriched borrower data','''
The Data API exposes authorized bank, payment, accounting and other integration records before and after underwriting. It includes the typed normalized representation, enrichment fields, field provenance, missing-value reasons, provider extensions, permitted source payloads and document references. AMLOK handles processing; you do not invoke its internal stages.

## Three read operations

| Operation | Purpose |
| --- | --- |
| [GET /v1/data/records](/api-reference/endpoints/data/list-data-records) | Page through all currently authorized records for a borrower at one consistent snapshot |
| [GET /v1/data/records/{id}](/api-reference/endpoints/data/get-data-record) | Retrieve an exact immutable record version |
| [GET /v1/data/changes](/api-reference/endpoints/data/list-data-changes) | Keep a downstream copy up to date without repeatedly downloading the full history |

The Data API requires data:read. It is independent of Insights and Signal execution. The underlying integration, borrower consent, purpose and provider entitlement must still authorize access. An empty result means no matching authorized records at that snapshot; inspect connection readiness and coverage before concluding there was no activity.

## Bootstrap without missing changes

'''+sample('listDataRecords')+'''

1. Supply borrower_id. Optionally filter by connection_id, integration_id or resource_type, such as bank_transaction, bank_account or invoice.
2. Persist page.snapshot_id, page.as_of and page.changes_cursor from the first page. The server captures the snapshot and its change-feed boundary atomically.
3. Fetch every page using next_cursor with the same borrower and filters. The snapshot freezes membership and record versions; current authorization is rechecked on each read.
4. After committing the complete snapshot, call the changes endpoint with the saved changes_cursor. It already binds borrower, filters and authorization.
5. Apply each batch idempotently using change ID and logical resource version. Follow next_cursor while has_more is true; after the final committed batch persist resume_cursor, including on empty results.

Changes cover upsert, removed and access_changed. An upsert points to the exact DataRecord version to retrieve. Removed or newly restricted content may expose permitted metadata only. Do not mistake a provider deletion or access withdrawal for zero activity, and handle local retained copies according to the applicable authorization/retention policy.

A stale or mismatched cursor fails explicitly. On 410, deliberately reconcile a new full snapshot; never silently skip the missing interval. Pagination never truncates the dataset. The data.updated notification identifies a connection with new committed data; use your cursor to collect the changes. Webhooks are a wake-up signal, not the record transport.

## Understand each record

- id identifies an immutable DataRecord version; resource_id identifies the logical normalized record, whose record_version increases on change.
- resource_type selects one of the existing typed normalized schemas. normalized.object, normalized.id and normalized.record_version match the envelope; the server rejects inconsistent representations.
- normalized includes all authorized populated fields. Financial enrichment can appear in those typed fields, while broader assessment dimensions and policy results are returned in the risk package.
- field_provenance, source_refs, missing_fields and namespaced extensions retain source attribution and provider details. Do not invent unavailable values.
- source_payload contains authorized provider-native business fields when retained and permitted. not_retained, restricted and not_applicable use a null value and an explicit reason. Credentials, secrets and unrelated borrower data are never part of the public data.
- document_ids link original files and reports. Discover and download them with the [document API](/api-reference/documents).

“All available data” means the complete authorized representation, including data not selected as evidence for a particular assessment. It does not override provider licensing or promise fields the provider did not supply. Restricted data is explicitly identified rather than silently represented as an empty successful result.

## Assessments and exports

The [risk package](/api-reference/risk-package) contains assessment-level enrichments, financial dimensions, policy results and limitations. [Evidence](/api-reference/evidence-traceability) freezes the exact inputs used for a particular result. EvidenceSummary.data_record_id connects that assessment input to its exact DataRecord version when applicable. A newer collected record never changes an older risk package.

For a bulk download, create an export with kind data, data_snapshot_id from the list response, and format json or csv. The snapshot preserves the selected borrower and filters. Expired snapshots return 410; do not substitute a newer snapshot without the caller requesting it. Export access requires data:read and source authorization at creation, retrieval and download in addition to export scope.

Data Lookup imports these same schemas. Choose Amlok API to explore the full contract, or a provider to view its applicable data/evidence schemas and the documented upstream field mappings.
''')
    append('quickstart','''
## Read the collected data and submitted documents

See [embedding the Hub](/api-reference/integration-hub) for the split between console configuration and secure borrower-specific sessions. Before or after underwriting, use [GET /v1/data/records](/api-reference/endpoints/data/list-data-records) with borrower_id to retrieve the authorized normalized and enriched data; no risk-package ID is required.

Upload supporting files with POST /v1/documents and include their IDs in the origination request. If Amlok requests a later document, upload it with the origination_id and open requirement_id. GET /v1/originations/{id} retains submitted_request even before completion. GET /v1/documents?origination_id=... lists associated files. See [documents](/api-reference/documents) for attachment states and download controls.
''')
    append('documents','''
## Discover and associate files

[GET /v1/documents](/api-reference/endpoints/evidence/list-documents) lists files by borrower_id, origination_id, context, document_type and status. Origin distinguishes institution_upload, borrower_upload, integration and amlok_generated. Pagination covers all matching authorized files.

For the initial request, upload files with borrower context and include returned IDs in CreateOrigination.document_ids. The server validates borrower/workspace/environment ownership and file readiness. Processing files keep the origination collecting; rejected or inaccessible files produce an explicit requirement or error, never silently disappear.

For an open document requirement, upload a new file with borrower_id, origination_id and requirement_id. All three must refer to the same authorized context. Association and the upload receipt are atomic and idempotent; inspection still completes asynchronously. requirement_id cannot be supplied without origination_id. Later association is permitted only while the origination is collecting or requires_action; other states return 409. Completed assessments and files are never overwritten.

The origination retains its immutable submitted_request and the accepted document associations. The completed risk package freezes document_ids and its evidence set. For changed application information after submission, create a new origination with a new command identity; do not modify the historical application. A document status notification identifies the file to retrieve without including file contents or a signed URL.
''')
    append('evidence-traceability','''
## All collected data versus assessment evidence

This evidence interface answers “what exact inputs support this result?” For the full authorized collected and enriched dataset, including records available before a result and records not used in that result, use the [Data API](/api-reference/data-access). EvidenceSummary.data_record_id links the exact data version when applicable. Retrieving that link separately requires data:read; an evidence grant does not expand other permissions.
''')
    append('credit-reporting','''
## Reconcile payments, credits and consumption

| Read operation | What it explains |
| --- | --- |
| [GET /v1/billing/payments](/api-reference/endpoints/billing/list-billing-payments) | Every initial funding, renewal and top-up payment attempt, including pending and failed attempts |
| [GET /v1/billing/payments/{id}](/api-reference/endpoints/billing/get-billing-payment) | Payment amount, masked method, settlement/failure/refund state and linked ledger entries |
| GET /v1/billing/transactions | Actual posted changes to the wallet, in sequence order |
| [GET /v1/billing/transactions/{id}](/api-reference/endpoints/billing/get-billing-transaction) | One movement with historical balance and payment/usage/correction links |
| [GET /v1/billing/usage](/api-reference/endpoints/billing/list-billing-usage) | Product charges with borrower, period, historical rate, tier and workload |
| [GET /v1/billing/usage/{id}](/api-reference/endpoints/billing/get-billing-usage) | One charge linked to its origination or monitored deals, result and wallet transaction |

Read billing summary first and pass its snapshot_id to related list/detail calls to reconcile one as-of state. Preserve filters across pages. New payments or charges after that snapshot belong to a later report; an expired snapshot returns 410 rather than silently changing the balance. Date filters use inclusive from and exclusive to UTC timestamps. Lists return all matching rows through pagination, not only the latest entries.

Available credits reconcile as:

```text
paid_funding_credits + promotional_credits + adjustment_credits
- spent_credits - refunded_credits = available_credits
```

All totals use posted CAD wallet entries. A payment attempt is not itself a credit. Pending/processing/failed/cancelled payments contribute no credits. Paid funding links payment_id; promotional funding has no payment. A settled payment's credited_amount records credits actually posted; subsequent returns/refunds have linked negative entries rather than modifying the original credit. Adjustments are signed, with related_transaction_id identifying the original entry. Use transaction sequence, not timestamps alone, to follow balance_after.

Usage amounts are positive costs; their ledger entries are negative. Historical unit_rate, quantity, tier, workload and rate_version explain the deduction. Example rates are synthetic and are not price quotations. Signal groups all monitored deals for one borrower/workspace/month, so do not sum one monthly charge per monitor.

The summary also reports actual auto_pay settings read-only. Payment collection, method updates and top-up settings remain console actions. Billing events and delivery/replay metadata require billing:read and current Owner authority; event scope alone must not reveal financial information. Use typed exports for statements, receipts of funding activity and full-period reports.
''')
    append('consumption-reporting','''
## Follow one deduction

List billing usage by product, borrower_id, origination_id, monitor_id or charged date window. Each result links transaction_id to the exact wallet deduction and provides the historical rate and workload behind it. GET /v1/billing/usage/{id} resolves the billing_usage_id on a risk package. Read payment history separately for top-ups; funding is not product consumption.
''')
    append('pagination','''
## Collected-data synchronization

Data records use DataPage: snapshot_id, as_of and changes_cursor alongside ordinary pagination. Finish that snapshot before consuming changes. Data changes use DataChangePage with a durable resume_cursor. This atomic snapshot boundary avoids gaps and is separate from the general resource-event feed. Follow the [data synchronization procedure](/api-reference/data-access).
''')
    append('authentication','''
Collected data requires data:read. Assessment evidence requires evidence:read. Export scopes alone grant neither: a data export additionally requires data:read; each other kind retains its documented source permission. Billing events, deliveries and replays require billing:read and Owner authority in addition to event scopes. Data notifications require data:read. Unauthorized event metadata must be filtered from feeds and denied on direct reads/replays.
''')
    append('export-formats','''
## Collected-data exports and lookup schemas

The data kind accepts data_snapshot_id and json/csv format. JSON uses DataExport: schema_version, snapshot_id and rows of DataRecord. CSV uses id,borrower_id,connection_id,integration_id,resource_type,resource_id,record_version,ingested_at,source_as_of,access,access_reason,normalized_json,source_payload_json,document_ids_json. Nested values are compact JSON; use the same quoting, null and formula-escaping rules as financial CSV. No silent truncation is permitted.

All export kinds and financial report schemas are declared in the canonical OpenAPI x-export-schemas map. The console's Data Lookup shows the typed downloaded content beneath the download-link response as reference material; these fields are not included inline in the HTTP download-link response.
''')
    append('event-catalog','''
## Data and billing notifications

- data.updated references a connection whose committed data changed. Continue the Data API cursor; the event does not carry records and is not a sync job to execute.
- document.status_changed references the document to inspect for availability or rejection.
- billing.payment_updated references a payment's current state. A successful delivery of this notification does not itself post credits.
- billing.transaction_posted references an immutable wallet entry. Use the billing snapshot APIs for reconciliation.

Only authorized destinations and event readers receive the corresponding resource metadata. Billing notification delivery, reads and replay require Owner authority and billing:read; data notifications require data:read. Losing access stops further delivery and does not permit replay of restricted events.
''')
    write('api-review','Institution API completeness review','''
The November 6, 2026 review follows the institution's full workflow: configure and embed an Integrations Hub, collect authorized borrower data, submit application information and documents, receive enriched data and risk packages, monitor funded deals, and reconcile deposits and consumption.

The contract has one public surface under /v1 with 54 operations. The prior 45-operation design covered product execution but did not completely expose the surrounding data and financial reporting. This revision adds nine read operations; it retains secure borrower sessions and connection visibility. Endpoint count is a consequence of supported client tasks, not a target.

| Requirement | Finding and resolution |
| --- | --- |
| Configure integrations in the console | Preserved; session creation launches a published Hub and cannot override enabled integrations |
| Securely embed it for a borrower | Preserved borrower-bound session; documented ownership checks, expiry, approved origins/return URLs and server-side completion checks |
| Inspect readiness and repair authorization | Preserved connections and consent controls; separate authorization status from data_status |
| Access all authorized collected/enriched data | Added list/get data records and incremental changes, independently of risk-package creation |
| Preserve provider detail and explain missing data | Typed normalized fields, source payload availability, extensions, provenance, document references and explicit access reasons |
| Submit and inspect application information | Origination accepts existing structured application/product/policy inputs and now returns the immutable submitted_request before completion |
| Upload and find supporting documents | Added document listing; documented initial and later requirement association with borrower ownership and immutable files |
| Retrieve assessment findings and source proof | Preserved risk packages/evidence, with document IDs and exact DataRecord version links |
| Monitor funded deals and inspect changes | Preserved monitors, per-run sources, packages and alerts; data changes expose updates between assessments |
| See deposits and failed/pending top-ups | Added payment list/detail, separating payment attempts from posted wallet credits |
| Explain consumption | Added usage list/detail with borrower/product references, actual historical rate, workload and ledger links |
| Reconcile balances and corrections | Added transaction detail, sequence/balance_after, payment and correction links, lifetime totals and shared snapshots |
| Download all authorized records and reports | Added data-snapshot export; preserved evidence/results and financial export formats with explicit schema links |
| Keep the console reference accurate | Generate Data Lookup, examples, scopes and event choices from the same OpenAPI contract; validate exact parity |

No provider sync, enrichment stage or underwriting engine is exposed as a client-managed workflow. Product data and financial history remain immutable. Billing mutations, payment-method configuration and Hub design remain console responsibilities. Source access is subject to actual borrower permission and provider entitlement; omitted/unavailable data must have explicit reasons.

## Implementation and validation boundary

This repository defines and validates the public contract and generated documentation. It does not deploy or certify the underwriting engine, integration adapters or payment processor. Synthetic schema/example tests and console reference checks are not production end-to-end execution tests. Runtime implementation must enforce the documented authorization, snapshot, reconciliation and idempotency invariants before these operations are enabled for a live institution.

## Design references

The separation between an embedded authorization experience and server-side data access is supported by [Plaid Link](https://plaid.com/docs/link/). Cursor-based incremental updates and explicit removal handling are described by [Plaid Transactions](https://plaid.com/docs/api/products/transactions/). Linking financial movements to their source records is illustrated by [Stripe balance transactions](https://docs.stripe.com/api/balance_transactions/object). AMLOK's endpoint names, CAD credit rules and institution boundaries follow its own contract; these references do not imply equivalent provider features or payment infrastructure.
''')

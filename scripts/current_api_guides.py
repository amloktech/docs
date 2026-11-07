"""Customer guides for the primary product API, generated with its reference."""
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent


def page(path,title,description,body):
    p=ROOT/(path+'.mdx');p.parent.mkdir(parents=True,exist_ok=True)
    short={'overview':'Overview','quickstart':'Quickstart','authentication':'Authentication','environments':'Environments','downloads':'Downloads','configuration':'Lending configuration','risk-package':'Risk packages','monitoring-design':'Signal monitoring','evidence-traceability':'Evidence','documents':'Documents','processing-lifecycle':'Product lifecycle','pagination':'Pagination','idempotency':'Idempotency','request-recovery':'Request recovery','connection-recovery':'Connection recovery','webhook-operations':'Delivery recovery','rate-limits':'Rate limits','sandbox-journeys':'Sandbox journeys','credit-reporting':'Wallet and billing','consumption-reporting':'Consumption','workload-reporting':'Workload','export-formats':'Export formats','product-api-migration':'Migration','api-review':'Simplification review'}.get(path.split('/')[-1],title)
    p.write_text('---\ntitle: '+json.dumps(title)+'\nsidebarTitle: '+json.dumps(short)+'\ndescription: '+json.dumps(description)+'\nkeywords: ["AMLOK", "API", "Insights", "Signal"]\n---\n\n'+body.strip()+'\n')


def write_guides(spec,f,index):
    def api(name,title,body,description=None):page('api-reference/'+name,title,description or title+' for the AMLOK product API.',body)
    def code(value):return '```json\n'+json.dumps(value,indent=2)+'\n```'
    def sample(oid):
        op=next(o for o in index if o['id']==oid)
        return '```bash\n'+spec['paths'][op['path']][op['method'].lower()]['x-codeSamples'][0]['source']+'\n```'
    api('overview','API overview','''
AMLOK helps financial institutions underwrite business and consumer borrowers with **Insights** and monitor funded deals with **Signal**. Borrowers connect their sources through an embedded Integrations Hub. Your institution submits its application, lending product and risk policy; AMLOK returns a risk package and the evidence behind it.

**One API covers the complete borrower-to-monitoring journey in 57 operations.** Use the [quickstart](/api-reference/quickstart), [endpoint reference](/api-reference/endpoints/insights/create-origination) and [OpenAPI download](/openapi/amlok.json).

## The integration flow

```mermaid
flowchart LR
    B[Borrower] --> H[Embedded Integrations Hub]
    H --> E[Authorized source data and files]
    A[Application + product version + policy version] --> I[Insights origination]
    E --> I
    I --> R[Risk package + evidence]
    R --> D[Institution decision and funding]
    D --> S[Signal monitor]
    E --> S
    S --> N[Monitoring runs + updated packages + alerts]
```

AMLOK handles collection, normalization, KYB/KYC, included checks and calculations. You do not orchestrate provider sync jobs, verification jobs, manifests or workflow runs. You can retrieve authorized normalized records, licensed reports and documents through the [Data API](/api-reference/data-access), evidence and download interfaces.

## Public resources

| Resource | What you use it for |
| --- | --- |
| Borrowers and embedding sessions | Identify the borrower and launch an authorized connection journey |
| Connections and consents | Inspect source access, freshness and required borrower actions |
| Lending-product and risk-policy versions | Supply the exact lending context for each assessment |
| Originations and risk packages | Request underwriting and retrieve dimensions, findings and evidence |
| Monitors, monitoring runs and alerts | Follow funded exposures, refreshed evidence and material changes |
| Data, evidence, documents and exports | Retrieve all collected/enriched data or inspect the exact inputs to an assessment |
| Events and webhook deliveries | Receive notifications, recover missed events and troubleshoot delivery |
| Billing summary, payments, usage and transactions | Reconcile top-ups, available credit and the exact product consumption behind each deduction |

The organization owns billing identity, payment methods and team roles. Each workspace has a shared CAD wallet and isolated Sandbox and Live environments. API keys are scoped to one workspace and environment. Product records cannot be edited or deleted; authorized configuration changes apply prospectively.

<Columns cols={2}>
<Card title="Start integrating" icon="terminal" href="/api-reference/quickstart">Connect a borrower and submit an Origination.</Card>
<Card title="Read a risk package" icon="file-search" href="/api-reference/risk-package">Understand financial dimensions and exact evidence versions.</Card>
<Card title="Monitor funded deals" icon="activity" href="/api-reference/monitoring-design">Inspect evaluations, alerts and connection health.</Card>
<Card title="Explore the evidence" icon="database" href="/api-reference/evidence-traceability">Retrieve normalized data and authorized source files.</Card>
</Columns>

Use the [OpenAPI specification](/overview/openapi-spec) as the authoritative API contract.
''')
    api('quickstart','Connect a borrower and request underwriting','''
Use your backend to create a borrower, launch an Integrations Hub session and submit an Origination. The examples use synthetic identifiers; replace them with returned values. Provisioned product, policy, application-schema and embedding-version IDs come from your workspace.

## 1. Configure server access

```bash
export AMLOK_API_BASE_URL="<your-institution-api-origin>"
export AMLOK_API_KEY="<your-workspace-api-key>"
```

The origin excludes `/v1`. Keep the key on your server. Retrieve [configuration](/api-reference/endpoints/configuration/get-configuration) to discover approved schemas and capabilities.

## 2. Register the borrower

'''+sample('createBorrower')+'''

Save `data.id` as your borrower ID. A business or person profile records supplied identity, not a completed KYB/KYC check.

## 3. Launch the connection journey

'''+sample('createEmbeddingSession')+'''

Use the returned `data.launch_url` in your borrower experience. Your institution API key must never enter the browser. The published embedding configuration determines enabled integrations and category steps. AMLOK captures consent, handles provider authorization and collects data.

A browser return does not prove completion. Read the session or consume `embedding_session.completed`, then retrieve its connections and inspect their status. A completed connection journey is not a completed underwriting.

## 4. Supply lending context

Create immutable [lending-product versions](/api-reference/endpoints/configuration/create-lending-product-version) and [risk-policy versions](/api-reference/endpoints/configuration/create-risk-policy-version) once for each approved catalog/policy revision. Reuse them across originations. [Configuration](/api-reference/configuration) explains approved pricing/application schemas and typed rules.

## 5. Submit an Origination

'''+sample('createOrigination')+'''

Expect `202 Accepted`, with an Origination ID and `status: accepted`. Retain the ID and the idempotency key. AMLOK resolves data coverage and runs included checks; do not start sync, verification or calculation jobs yourself.

## 6. Read the result

Retrieve `GET /v1/originations/{id}` or handle `origination.completed`. If `requires_action`, complete the returned connection or document requirements. `waiting_for_credits` is accepted work waiting for funding, not a reason to resubmit.

Once completed, use its `risk_package_id` with `GET /v1/risk-packages/{id}`. Read dimensions, policy results, source coverage and limitations. Use `GET /v1/evidence?evidence_set_id=...` for the supporting records and document references. Your institution makes the final decision.

After funding, [create a Signal monitor](/api-reference/monitoring-design) with the deal terms and the baseline risk package.
''')
    api('configuration','Lending products, policies and configuration','''
Use `GET /v1/configuration` to discover the schemas, integration IDs, embedding versions and monitoring cadences approved for your key. The catalog of supported providers does not itself grant access to every integration or field.

## Lending-product catalog

`POST /v1/lending-product-versions` records one immutable lending-product revision. It captures borrower type, market, currency, amount and term bounds, repayment frequency, pricing and source documents. `pricing` must validate against the returned `pricing_schema_id`. Include the fees, rate and amortization inputs required for repayment analysis; AMLOK does not infer missing economics.

'''+code(f['LendingProductInput'])+'''

Read or list versions using the same resource. Create a new version when terms change; previous originations keep their original version and hash. Catalog products here are lending products, not merchant inventory.

## Risk policies

`POST /v1/risk-policy-versions` records approved typed rules and supporting policy documents. The rule language supports scalar comparisons (`gt`, `gte`, `lt`, `lte`, `eq`) against configured metric keys with matching units. Missing data routes to review. Policy documents provide context and are not automatically executable rules.

'''+code(f['RiskPolicyInput'])+'''

The threshold above is synthetic and is not a recommended credit policy. Your institution supplies and approves its policy. Both rule definitions and evaluation results remain visible in the risk package.

## Application schemas

Every Origination supplies an `application_schema_id` and `declared_data`. Validate those fields against the matching JSON Schema from configuration. Compatibility checks also cover borrower type, market, currency, product and policy. Unsupported inputs produce a validation error rather than silently changing the assessment.

Owners manage organization/workspace settings and billing; Owners and Devs manage approved integration configuration. Versioned product and policy records are new records, never edits to prior assessment data.
''')
    api('risk-package','Read a risk package','''
A risk package is an immutable, complete assessment result from Insights or Signal. Retrieve it using `GET /v1/risk-packages/{id}`. It contains the institution's exact application context, product and policy versions, evaluated dimensions, source coverage and a frozen evidence set.

## What the response contains

| Field | Meaning |
| --- | --- |
| `product`, `origination_id`, `monitoring_run_id` | The product and assessment that produced the package |
| `application` | Submitted application context; may be null for an independently onboarded portfolio |
| `lending_product`, `risk_policy` | Immutable definitions and hashes used for this assessment |
| `assessment` | Advisory recommendation, reasons and a human-readable summary |
| `dimensions` | Financial and risk dimensions, typed metrics, windows and evidence links |
| `policy_results` | Each evaluated rule, threshold, actual value, result and explanation |
| `sources` | Per-integration retrieval time, source freshness, coverage and limitations |
| `evidence_set` | Stable evidence-set ID, hash and record count |
| `versions` | Schema, normalization, calculation and applicable model versions |
| `previous_package_id` | Prior package for a monitoring comparison |
| `billing_usage_id` | Link to the applicable usage record, when present |

## Dimensions

The contract supports identity, cash flow, liquidity, revenue quality, profitability, leverage, repayment capacity, concentration, collateral, fraud/consistency and consumer income/affordability. Which metrics are available depends on borrower type, approved calculations, source coverage and entitlement. [Derived attributes](/data-model/derived-attributes) explain retained definitions; [configuration](/api-reference/configuration) identifies authorized metric keys and versions.

A metric contains a decimal-string value, unit, observation window, calculation version and evidence IDs. Available values have `missing_reason: null`. Unavailable or not-applicable values are null with an explicit reason. Missing values are never converted into zero or a passing rule result.

Business DSCR needs eligible cash flow and complete comparable debt-service inputs. Consumer affordability needs verified income and obligations; deposits alone do not establish gross income. The API does not prescribe universal thresholds or claim an unvalidated probability of default.

## Decision and evidence

`assessment.is_institution_decision` is always false. Your institution makes and records the final lending decision. An unavailable policy input requires review.

Follow `evidence_set.id` to [list evidence](/api-reference/endpoints/evidence/list-evidence), then read a record or download an authorized source file. IDs, hashes and versions refer to the evidence used in this package, not a later replacement.

[Download a complete synthetic risk package](/downloads/risk-package-example.json). Its sample threshold, amounts, IDs and hashes illustrate the shape; they are not an observed assessment or a pricing commitment.
''')
    api('monitoring-design','Monitor funded deals with Signal','''
Signal refreshes authorized sources and reassesses funded deals against the institution's policy. You enroll the deal; AMLOK manages collection, normalization, baseline preparation and included calculations.

## Enroll a funded deal

'''+sample('createMonitor')+'''

The baseline is either an existing risk-package ID or typed baseline.portfolio inputs. Do not send both. Portfolio onboarding does not require purchasing a new Insights assessment. The server validates that the baseline, borrower, policy and connections belong to the same authorized context.

`202 Accepted` means enrollment is initializing. Retrieve the monitor to observe activation, action requirements or funding requirements. Cadences come from configuration; provider webhook support does not establish a universal refresh frequency or SLA.

## Inspect each evaluation

`GET /v1/monitoring-runs?monitor_id=...` returns the evaluation history. Each run exposes per-integration source freshness, coverage, limitations, its evidence set and the resulting risk-package ID. Drill into evidence for normalized records and authorized provider reports or original files.

A partial, failed or skipped sync does not mean the borrower passed a risk check. Read source coverage and package limitations before interpreting an alert or comparison. A Signal package links the previous package for traceable changes.

## Alerts, events and deliveries

- **Alert:** the system-derived risk condition with rule, severity, previous/current values and evidence.
- **Event:** a durable notification that an alert, run or other resource changed.
- **Delivery:** an HTTP attempt to send the event to your configured destination.

Read alerts through `GET /v1/alerts?monitor_id=...`, receive signed events and troubleshoot delivery attempts separately. Replaying a delivery does not rerun monitoring. Your institution performs outreach, collections and case management in its own systems.

## Change future configuration

Use `PATCH /v1/monitors/{id}` with the ETag returned by the monitor. You may change its future policy, cadence or active/paused/stopped state. A stale ETag returns `412`. A replacement risk policy must retain the existing policy's borrower type and market; an incompatible policy returns `422 validation_error` and leaves the monitor unchanged. Stopped is terminal. Neither a configuration change nor an alert resolution rewrites historical packages, evidence or charges.

Signal includes change-driven reassessment. A separately requested full underwriting is Insights. Signal counts a borrower/business once per workspace/month, using its combined workload; see [consumption reporting](/api-reference/consumption-reporting).
''')
    api('evidence-traceability','Retrieve records, reports and source files','''
Use an assessment's evidence set to inspect exactly which records and files support its conclusions. Risk packages supply `evidence_set.id`; monitoring runs supply `evidence_set_id`; metric and policy-result references identify individual evidence records.

1. Call `GET /v1/evidence?evidence_set_id=...`, optionally with `resource_type`.
2. Page through summaries using the returned cursor without changing filters.
3. Call `GET /v1/evidence/{id}` for the exact normalized record version and provenance.
4. Follow `document_id` or `provider_report_document_id` to retrieve file metadata and create a controlled download link.

Evidence retains the typed [normalized resource dictionary](/data-model/field-dictionary). Banks, payments, accounting, commerce, KYB/KYC, liens, lending records and other source families no longer require one collection API per table. Raw provider secrets, credentials and unrelated borrower records are not evidence outputs.

Each summary includes resource type and ID, record version, observation time, source, hash and access state. Restricted or deleted evidence returns metadata and a reason, with no hidden payload or provider download. A source license or consent restriction is not bypassed by an export.

Risk packages are immutable. Corrected source information becomes a new evidence version and a new assessment; old evidence is never silently replaced with the latest record. Retention and final cancellation rules still apply.

For large datasets, use a typed evidence export. Files and normalized records remain linked, so a human-readable package can be reconciled to the data used to calculate it.
''')
    api('documents','Upload and download documents','''
Upload documents with `POST /v1/documents` using multipart form data. Documents can support a borrower, a lending-product version or a risk-policy version. Every upload creates a new immutable record.

'''+sample('uploadDocument')+'''

Use `context: borrower` with `borrower_id`; add `origination_id` and `requirement_id` when satisfying an existing requirement. For `lending_product` or `risk_policy`, omit borrower/origination/requirement fields and reference the returned document ID in the new configuration version.

An upload returns `202` while inspection and processing occur. Retrieve its metadata until available or rejected. The filename, MIME type, byte length and SHA-256 describe the retained file. Metadata access does not imply download permission.

Create a short-lived link with `POST /v1/documents/{id}/download-links`, supplying an authorized purpose. The server checks workspace, environment, borrower authorization, consent and provider entitlement again. Do not log signed links, send them in webhooks or treat an expired link as a missing document. Request a new link when permitted.

Use the original files and provider reports referenced by [evidence](/api-reference/evidence-traceability). There is no update or delete operation for product documents.
''')
    scopes=sorted({o['scope'] for o in index if o['scope']!='public'})
    api('authentication','Authentication and access','''
Create scoped API keys through the authorized console administrator. Send the key as `Authorization: Bearer ...` from your backend. Each key belongs to exactly one institution, workspace and environment; callers cannot override that boundary with a workspace parameter.

```text
Authorization: Bearer <your-workspace-api-key>
```

An API key is never a browser embedding token or a webhook signing secret. Send borrowers only their short-lived embedding-session URL. Do not put keys in source control, browser storage, mobile applications, telemetry or support messages.

## Permissions

Every endpoint lists its required scope. Console roles and machine scopes work together: Owners manage organization/workspace identity, team permissions and billing; Owners and Devs manage integration configuration; Analysts read permitted reporting and product data. Analysts do not manage keys or Dev Tools. Billing reporting and billing exports require Owner authority and `billing:read`.

| Scope | Operations |
| --- | ---: |
'''+ '\n'.join('| `'+s+'` | '+str(sum(o['scope']==s for o in index))+' |' for s in scopes)+'''

Export access also checks the exported content: `exports:read` does not grant access to the underlying content. Risk-package exports also require `results:read`, billing exports require `billing:read` and Owner authority, and evidence exports require `evidence:read` and source entitlement. The same source entitlements apply on export creation, retrieval and download. All linked IDs and cursor state are checked against the authorized workspace/environment.

`401` means authentication failed; `403` means access was denied. A resource ID is not a permission. Product records have no edit or deletion operations, even for Owners. Creating new assessment inputs or changing future monitor configuration does not modify historical data.
''')
    api('environments','Sandbox and Live','''
Sandbox and Live use separate keys, records, connections and financial balances. Use the institution-issued origin in `AMLOK_API_BASE_URL`, without a version suffix. Do not infer API hostnames from the console or documentation domain.

`meta.environment` and event `environment` identify the context. Sandbox examples and simulated credits do not establish production funding or provider authorization. Never copy a Sandbox resource ID, embedding URL or cursor into Live.

Exercise the borrower connection journey, a completed Origination, missing inputs, expired consent, restricted evidence and monitoring failures. See [Sandbox journeys](/api-reference/sandbox-journeys).
''')
    api('response-format','Response format','''
Successful responses contain `data` and `meta`. Collections add `page`. Resource fields and schemas are documented on each endpoint.

'''+code({'data':f['Origination'],'meta':{'request_id':'req_synthetic','schema_version':'1.0.0','environment':'sandbox'}})+'''

Amounts and financial ratios use decimal strings. Do not convert money to binary floating point. Source ratios may retain more precision than two-decimal billing amounts. UTC timestamps use RFC 3339; date-only fields use `YYYY-MM-DD`.

Null explicitly means absent or unavailable according to that field's definition, not zero or an empty result. Metrics and restricted evidence include reasons. Mutable operational resources expose a monotonic record version; historical packages, records and accounting entries remain immutable.

Errors contain an `error` object with `code`, `message`, `retryable`, `request_id` and nullable `field`. Use the request ID when troubleshooting, without sending credentials or unredacted financial payloads.
''')
    api('pagination','Pagination and event recovery','''
Collection endpoints accept `limit` from 1 to 100 (default 25) and an opaque `cursor`. Follow `page.next_cursor` while `page.has_more` is true. Keep the original filters unchanged. Normal collection cursors bind authorization and a stable snapshot, identified by `page.snapshot_id`.

Never construct cursors, reuse them across workspaces or interpret a cursor-expiry error as end of data. `410 cursor_expired` requires a deliberate restart or reconciliation.

## Events

Events use a durable feed position instead of collection snapshot metadata. `page.resume_cursor` is present even on an empty page. Commit it only after processing and durably recording the batch.

For initial bootstrap, call `GET /v1/events?start=now` to capture a position before reading collections. Bootstrap collection snapshots, then resume the event feed using that position to reconcile changes that occurred during bootstrap. Do not combine `start` and `cursor`.

Webhook notifications may be duplicated or out of order. Deduplicate by event ID and compare resource versions when applying updates. A webhook destination failure does not erase the event or justify rerunning an assessment.
''')
    api('idempotency','Idempotency and accepted commands','''
Every POST requires `Idempotency-Key`, including uploads, downloads and delivery replays. Generate one key for each intended command, retain it with the exact request and reuse both for retries. Keys are scoped to the operation, workspace and environment. Reusing a key with a different payload returns `409 idempotency_conflict`. The fingerprint includes the resolved target path and payload; a key cannot be reused for a different target.

Full-response replay lasts 24 hours. After it expires, repeating an accepted command returns `409 idempotency_result_expired` without executing it again. Accepted-command receipts survive that response cache until workspace deletion. After a timeout, recover the original command with `GET /v1/request-receipts/lookup?operation_id=...&idempotency_key=...`, then retrieve its resource. Never use a fresh key merely because the cached response expired.

A rejected unfunded request does not produce a debit. An already accepted Origination can enter `waiting_for_credits`; continue following that ID rather than creating another assessment.

Monitor configuration updates use `If-Match` with the current ETag. On `412`, retrieve and reconcile the latest configuration before retrying. Do not blindly overwrite another administrator's change.
''')
    api('errors','Errors and safe retries','''
AMLOK returns structured errors. Inspect the HTTP status, error code, retryability and any field context. Keep the request ID for support.

| HTTP | Meaning | Action |
| --- | --- | --- |
| 400 / 422 | Invalid input or incompatible configuration | Correct the request; do not retry unchanged |
| 401 / 403 | Authentication or authorization failure | Check the key, environment, scope and source entitlement |
| 402 | Insufficient credits before acceptance | Resolve funding through the console; no debit is created |
| 404 | Resource not found in the authorized context | Check the returned ID and environment |
| 409 | Conflicting idempotency payload or invalid state | Recover the original command or reconcile state |
| 410 | Cursor expired | Reconcile from a new snapshot; do not silently skip data |
| 412 | Monitor ETag changed | Retrieve current configuration and review the intended change |
| 429 | Rate limited | Respect `Retry-After` and apply bounded jittered backoff |
| 503 | Temporarily unavailable | Retry when permitted, preserving command identity |

Network failure does not prove that a command failed. Recover accepted commands before attempting a new one. Do not automatically retry every error or repeat a chargeable assessment with a fresh idempotency key.

A successful HTTP response may contain incomplete source coverage, an action requirement or an asynchronous status. Inspect resource and metric states before treating the business operation as completed.
''')
    api('rate-limits','Rate limits and polling','''
Use bounded polling and exponential backoff with jitter. `429` and transient `503` responses may include `Retry-After` in seconds; wait at least that interval. Your institution's agreed limits determine capacity, not illustrative examples in this reference.

Prefer events to frequent polling for Origination completion, monitoring changes and export readiness. Keep a durable event cursor for recovery and a bounded fallback polling strategy. A collection page has at most 100 items; fetch pages rather than requesting an unlimited response.

Preserve an operation's idempotency key during transport retries. Rate limits do not change source-provider freshness, monitoring cadence or evidence completeness.
''')
    api('async-jobs','Asynchronous product operations','''
Origination, monitor enrollment, uploads, exports and event replay can return `202 Accepted`. Acceptance confirms a recorded command, not a completed business outcome. Persist the returned ID and idempotency key.

| Resource | Completion or follow-up |
| --- | --- |
| Origination | Read status and requirements; completed returns a risk-package ID |
| Monitor | Follow initializing, active, action-required or waiting-for-credits states |
| Document | Wait for available; inspect rejection or access restrictions |
| Export | Wait for completed, then request a download link |
| Replay receipt | Follow the separate webhook-delivery attempts |

AMLOK owns internal provider jobs, verification and calculation stages. You no longer create or retry those jobs. Operational failures expose useful status and requirements on the product resource. An accepted Origination awaiting credits remains the same resource and must not be resubmitted as a new command.
''')
    signature=(ROOT/'data/webhook-signature.md').read_text()
    api('webhooks','Webhooks and signatures','''
Configure HTTPS destinations and signing-secret rotation in **Dev Tools** in the console. Subscribe to the [event catalog](/api-reference/event-catalog). Store the signing secret in your server secret manager; it is different from your institution API key.

Events contain resource references, not source financial data or download URLs. Verify the exact raw request bytes, durably record the event and then acknowledge delivery. Retrieve authorized resource details separately.

'''+signature)
    api('event-catalog','Event catalog','''
AMLOK events notify you of product and connection changes. Each payload contains an event ID, type, occurrence time, resource type/ID/version, nullable borrower ID and environment. This is the same envelope used by signed webhooks and the durable event feed.

'''+code(f['Event'])+'''

| Event | Follow-up |
| --- | --- |
'''+ '\n'.join('| `'+e+'` | Retrieve the referenced resource and compare its version. |' for e in spec['components']['schemas']['Event']['properties']['type']['enum'])+'''

Delivery is at least once and may be out of order. Deduplicate by event ID. Resource versions are meaningful only within the same resource. An immutable package has version 1; mutable status resources increment their version. Fetching a newer resource than the event is expected.

A run failure and a risk alert describe different problems. Missing data must not be treated as a healthy risk result. Events never contain borrower credentials, complete financial payloads or signed download URLs.
''')
    api('webhook-operations','Troubleshoot and replay webhook delivery','''
Use `GET /v1/webhook-deliveries` to inspect attempts by `event_id` or `endpoint_id`. Each row has attempt number, delivery state, attempt time and HTTP status. New delivery records also include `delivery_id`, `replay_id`, `duration_ms`, `error_code`, `next_attempt_at` and `exhausted`. Historical records can omit these fields. Destination creation, subscriptions and secret rotation are [Console configuration](/console/webhooks).

## Diagnose a delivery

1. Confirm the event exists with `GET /v1/events`. Your key needs the event scope and the referenced resource's read scope. Billing events also require current Owner access.
2. Check the endpoint is enabled in the correct workspace and environment and subscribes to that exact event type. Events recorded before a subscription was created are not sent automatically.
3. Inspect the attempt's `error_code` and HTTP status. A recorded event is not a delivery acknowledgment; only a 2xx receiver response confirms acceptance.
4. Resolve the receiver, DNS, certificate, URL or subscription issue. Use the [delivery error catalog](/api-reference/errors#webhook-delivery-diagnostics). Never disable signature verification to fix a failed request.
5. If `next_attempt_at` is present, another automatic attempt is scheduled. If `exhausted` is true, fix the cause and request a replay while the event is retained.

Each delivery has one initial attempt and six automatic retries at successive delays of 1 minute, 5 minutes, 30 minutes, 2 hours, 8 hours and 24 hours. A manual replay starts a new delivery with its own retry budget. Delivery is at least once: an ambiguous acknowledgment or worker recovery can cause duplicates. Deduplicate the original event ID before applying any business side effect.

## Replay a retained event

'''+sample('replayEvent')+'''

A replay targets an existing authorized endpoint. It creates another delivery attempt for the same event, so receivers must deduplicate. It does not create another assessment, change an alert, refresh source data or deduct usage credits.

Use the durable `GET /v1/events` feed to reconcile gaps. Do not infer missing business events merely from failed webhook deliveries. Store the last processed resume cursor and each accepted event ID.
''')
    api('credit-reporting','Shared wallet and billing reports','''
Each workspace has one CAD wallet shared by Insights and Signal. The organization owns the billing profile, payment methods and Owner permissions. Sandbox credits are isolated from Live funds.

Use `GET /v1/billing/summary` for `available_credits`, cumulative `spent_credits` and a stable reporting snapshot. Read immutable movements with `GET /v1/billing/transactions`; filter by snapshot to reconcile related reads. An adjustment is a linked new entry, not an edit to history.

There are no held or reserved credit categories. In-progress funding is not available credit. Top-up controls, card/ACH methods and cancellation are managed by authorized Owners in the console; the public API provides reporting and exports only.

The default auto-pay trigger is CAD 200 and may be raised. Customer-funded top-ups are at least CAD 500. Processing may continue below the trigger while credits cover the cost. The agreed monthly minimum is at least CAD 1,000, funded for 12 months at signing and annual renewal; this is not a monthly funding schedule.

Cancellation immediately stops processing, new deductions and upcoming top-ups. Reconcile already-submitted funding without a new collection attempt. At month-end closure, all unused credits, including promotional credits, are refunded to the saved bank account; bank delivery takes 7-10 business days after issuance. Necessary final financial records are retained separately from deleted borrower data. Used credits are non-refundable. See [pricing and credits](/pricing/credits-and-billing).

For detailed usage, credit movements, statements, funding, rates or workload, create a typed billing export. Owner authority and `billing:read` are required at every access step.
''')
    api('consumption-reporting','Insights and Signal consumption','''
Only Insights and Signal are paid products. Verification, KYB/KYC, liens, calculations and investigations are included stages managed by AMLOK. Clients do not supply a processing context or buy those stages separately.

Insights checks available credits and deducts the charge atomically with risk-package publication. If concurrent activity leaves insufficient funds after acceptance, the Origination waits for credits without publishing or charging. Resume the accepted resource rather than submitting another underwriting.

Signal charges each active borrower/business once per workspace/month, using the combined workload across configurations, deals and sources. The full monthly rate is deducted at 00:00 UTC on the first calendar day, or on first mid-month activation without proration. A paid borrower/workspace/month is not charged twice. Unfunded monitoring pauses without debt; resume funds only the current period.

Signal includes change-driven reassessment. A separate full underwriting is a new Insights Origination. Monetary rates and amounts use two-decimal, half-up rounding: round the effective unit rate, then each quantity-times-rate line, and sum the rounded lines.

Read summary movements through billing transactions and create a `billing` export with `billing_report_type: usage` for detailed consumption. Historical rate versions, source IDs and correction links remain available in the report.
''')
    api('workload-reporting','Workload and complexity reporting','''
AMLOK determines a workload tier from the highest required dimension: connected bank accounts, business systems and processed records. The underwriting and monitoring APIs expose product outcomes; clients do not construct workload manifests or checkpoints.

| Tier | Bank accounts | Business systems | Records |
| --- | ---: | ---: | ---: |
| Standard | 2 | 5 | 75,000 |
| Advanced | 4 | 10 | 250,000 |
| Complex | 8 | 20 | 1,000,000 |

Insights counts the complete assessment and includes at least 12 months of banking history. Signal counts newly processed records during the month; unchanged baseline history is not counted again. Updated versions count as new records, while retries of the same unchanged version are deduplicated. Negotiated quotes retain an existing tier with explicit limits and rates.

Request `POST /v1/exports` with `kind: billing`, `billing_report_type: workload`, a UTC window and JSON or CSV format. Workload and billing reports preserve the evidence versions and financial reconciliation identifiers needed to explain the tier without requiring execution of internal stages.
''')
    api('export-formats','Exports and file formats','''
Create exports through `POST /v1/exports`. Use one typed source: a risk-package ID, an evidence-set ID, or a billing report type with a UTC window. Poll the export or consume `export.ready`, then call `POST /v1/exports/{id}/download-links` with a purpose.

| Kind | Formats | Content |
| --- | --- | --- |
| `risk_package` | JSON, PDF | The complete assessment or human-readable report with evidence references |
| `evidence` | JSON, CSV | Authorized frozen evidence records and file references |
| `billing` | JSON, CSV | `usage`, `credits`, `statements`, `funding`, `rates` or `workload` |

'''+code({'kind':'billing','billing_report_type':'usage','window':{'start':'2026-10-01T00:00:00Z','end':'2026-11-01T00:00:00Z'},'format':'csv'})+'''

JSON risk-package exports use the `RiskPackage` schema. Evidence JSON uses `schema_version: 1.0.0`, an `evidence_set_id` and an array of the same `Evidence` records returned by the API. Restricted records preserve metadata/reasons without exposing hidden content. CSV evidence has `evidence_set_id,id,resource_type,resource_id,record_version,kind,source_id,observed_at,sha256,access,access_reason,document_id,normalized_json,provider_report_document_id`; nested normalized values are compact JSON cells.

## Financial report compatibility

The simplified API retains the established financial report row schemas and monetary semantics. File schema versions are independent from API route versions. The existing `1.4.2` report schemas remain valid for usage, credit movements, statements and funding; internal reconciliation identifiers in these files are informational, not commands the client must execute.

| Report type | File schema / example |
| --- | --- |
| `usage` | [Usage schema](/downloads/report-schemas/usage.schema.json), [JSON](/downloads/report-examples/usage.json), [CSV](/downloads/report-examples/usage.csv) |
| `credits` | [Ledger row schema](/downloads/report-schemas/ledger.schema.json), [JSON](/downloads/report-examples/ledger.json), [CSV](/downloads/report-examples/ledger.csv) |
| `statements` | [Statement schema](/downloads/report-schemas/statement.schema.json), [JSON](/downloads/report-examples/statement.json), [CSV](/downloads/report-examples/statement.csv) |
| `funding` | [Funding schema](/downloads/report-schemas/funding.schema.json), [JSON](/downloads/report-examples/funding.json), [CSV](/downloads/report-examples/funding.csv) |
| `rates` | Versioned rate-card definitions and their effective periods; use the rate export schema in the OpenAPI contract |
| `workload` | Workload report records with versions, counts, tier and provenance; use the workload export schema in the OpenAPI contract |

JSON financial reports include schema version, report type, snapshot, as-of time and rows. Empty results use an empty array. CSV uses UTF-8, RFC 4180 quoting, CRLF line endings and a header even for no rows. Null is an empty cell; defined financial text fields do not use an empty string. Decimal strings retain their sign and precision. Formula-like text cells are escaped; consumers must never execute cell contents.

No export silently truncates records. Download metadata includes expiration and SHA-256; verify integrity before ingestion. Source entitlements, Owner billing access and workspace/environment checks apply during creation, retrieval and download.
''')
    api('connection-recovery','Recover source connections','''
Inspect `GET /v1/connections` for source status, consent, last successful sync, source-as-of time and coverage. Connection health and data freshness are different: a connected account can still have stale or incomplete evidence.

When a source requires authorization again, create an embedding session with `purpose: reauthorize` and the `connection_id`. Use the same borrower and a compatible published embedding version. Send the new short-lived launch URL to that borrower and verify completion server-side.

'''+code({**f['CreateEmbeddingSession'],'purpose':'reauthorize','connection_id':'con_synthetic'})+'''

Complete Origination requirements through the indicated connection or document action. AMLOK resumes collection and assessment when dependencies permit. Do not start a provider sync or retry an internal workflow.

Revoke authorization with `POST /v1/consents/{id}/revoke` when appropriate. Revocation stops future collection under that consent and does not rewrite previous assessments or bypass retention policy.
''')
    api('request-recovery','Recover a timed-out request','''
A timeout can occur after AMLOK accepted your command. Save the operation ID, exact payload and idempotency key before sending it. Use the same values during retries.

'''+sample('lookupRequestReceipt')+'''

A receipt identifies the accepted resource even after the 24-hour full-response cache expires. Retrieve that resource and continue following its state. Do not generate a new idempotency key to recover the same accepted action.

If lookup does not find acceptance, reconcile with your own request log before retrying the original command. A `404` is not permission to create duplicate work under a new key. Webhook replay and source reauthorization are separate actions with their own keys.
''')
    api('onboarding','Set up an institution integration','''
Your account manager provides the environment details and console access. An authorized Owner configures organization identity, billing and team roles. Owners and Devs create workspace/environment keys and manage integration tools.

Before submitting product requests, provision approved application/pricing schemas, integration entitlements, embedding versions, monitoring cadences and webhook destinations. Retrieve `GET /v1/configuration` to discover what your key can use. Create immutable lending-product and policy versions for your institution's approved underwriting context.

Keep institution credentials on your server. Borrowers interact only with short-lived embedding sessions. Register allowed return URLs, verify webhook signatures and test tenant isolation. Follow the [quickstart](/api-reference/quickstart) and [Sandbox journeys](/api-reference/sandbox-journeys) before Live enablement.
''')
    api('related-person-verification','Related people and borrower verification','''
A business Origination can reference related people using `application.related_borrower_ids`. Create the authorized person profiles through the borrower endpoint and include those IDs in the application context.

AMLOK validates the relationship and permitted purpose before running included KYC/KYB checks. Registration alone does not establish verified identity or authority. Required authorization and supporting evidence must be present, and failures surface as requirements or limitations.

Verification results, provenance and authorized reports appear in the risk package and evidence set. The parent business remains the product billing/workload subject. Do not start a separate verification job or assign a standalone verification charge.
''')
    api('synchronization','Source freshness and monitoring cadence','''
AMLOK collects and normalizes authorized integration data behind Origination and Signal. There is no public start-sync command in the public API. Use connections, package source coverage and monitoring runs to understand collection outcomes.

`last_successful_sync_at` describes the last successful collection. `source_as_of` describes the data's upstream freshness. Coverage windows describe the actual observation period; retrieval time does not establish that the source data is current.

Monitoring uses a provisioned `cadence_id`, subject to the provider's update capability and consent. See [integration refresh behavior](/integrations/data-refresh) for provider-specific constraints. Webhooks, daily synchronization or available APIs do not imply a universal AMLOK SLA.

A partial run retains its limitations and available evidence. Missing source data must not be presented as zero, a resolved risk condition or a passing policy check.
''')
    api('processing-lifecycle','Origination and monitoring lifecycle','''
Origination progresses from accepted through collection and processing to a completed risk package. Source or document dependencies may produce `requires_action`; insufficient funding after acceptance may produce `waiting_for_credits`. Terminal failure or cancellation does not produce a published successful package.

| Origination status | Client action |
| --- | --- |
| `accepted`, `collecting`, `processing` | Follow the existing ID or wait for events |
| `requires_action` | Complete the returned authorization/document requirement |
| `waiting_for_credits` | Resolve funding through the console and follow the same ID |
| `completed` | Retrieve the non-null risk-package ID |
| `failed` | Inspect failure and contact support when appropriate |
| `cancelled` | Retain the outcome; do not treat it as completed underwriting |

Signal has a long-lived monitor and separate evaluation runs. Monitor configuration can change prospectively with ETag protection. Every evaluation and resulting risk package preserves the inputs and versions used. Pausing or stopping a monitor does not erase historical data.

Insights charges and publication are atomic. Signal reassessments are included in its monthly product charge. See [consumption reporting](/api-reference/consumption-reporting).
''')
    api('security','API and evidence security','''
Use scoped server-side keys, borrower-bound sessions and HTTPS. Every resource, linked ID, cursor, export and download is authorized within one workspace and environment. A cross-workspace ID must not grant access, including when nested inside an Origination or export request.

Provider consent and source entitlements apply independently from API scope. Restricted reports return metadata and an explicit reason. Never return credentials, unrestricted signed URLs or unlicensed source files through evidence or events.

Owners manage organization identity, team permissions and billing. Devs manage authorized integration configuration; Analysts read permitted reporting and product data. All roles are prevented from editing or deleting historical product records. Monitor configuration and new catalog/policy versions affect future processing only.

Verify raw webhook bytes, deduplicate events durably and retain exact command identity during retries. Keep credentials and financial payloads out of logs. Follow the institution's retention and cancellation rules for evidence and final financial records.
''')
    api('sandbox-journeys','Validate a Sandbox integration','''
Use an enabled Sandbox environment to exercise the complete product journey with approved test data. Synthetic examples in this documentation validate contract shape; they do not establish that a backend operation ran successfully.

| Journey | Verify |
| --- | --- |
| Connect and underwrite | Borrower session completes; Origination publishes a traceable risk package |
| Missing authorization | Requires-action state; reauthorization resumes the existing request |
| Missing financial input | Null metric and explicit reason; policy routes to review |
| Restricted provider report | Metadata visible as permitted; content and downloads remain inaccessible |
| Timeout after acceptance | Receipt recovery returns the original resource without duplicate work |
| Insufficient credits | No unfunded debit; accepted work waits without another command |
| Monitoring | Runs expose source coverage; alerts link previous/current packages and evidence |
| Duplicate/out-of-order event | Receiver deduplicates and reconciles versions correctly |
| Export | Correct source permissions, complete rows and matching integrity hash |
| Tenant boundary | Other workspace/environment IDs and cursors are rejected |

Test controls are available through authorized Sandbox tooling. They are not public production API commands and cannot affect Live funds or real provider authorizations.
''')
    api('product-api-design','Product API structure','''
AMLOK exposes one product API for the complete customer journey. The [57-operation OpenAPI contract](/openapi/amlok.json) defines its requests, responses, errors and permissions.

Institutions supply borrowers, applications, lending-product versions and risk-policy versions. Embedding sessions collect borrower authorization and connections. Insights returns an immutable risk package. Signal follows funded deals with evaluation history, updated packages and risk alerts.

Evidence and file access preserve the depth of the normalized data model without requiring institutions to orchestrate backend stages or learn one API per source table. See the [overview](/api-reference/overview), [quickstart](/api-reference/quickstart) and [endpoint reference](/api-reference/endpoints/insights/create-origination).
''')
    api('products-and-endpoints','Products and endpoint responsibilities','''
Insights and Signal are the two paid products. Insights evaluates an Origination and returns its risk package. Signal monitors funded exposure and includes change-driven reassessment. Borrower verification, liens, calculations and other checks are included processing stages, not separate paid APIs.

| Capability | Primary endpoints |
| --- | --- |
| Borrower identity | `/v1/borrowers` |
| Borrower connection journey | `/v1/embedding-sessions`, `/v1/connections`, `/v1/consents/{id}` |
| Lending context | `/v1/lending-product-versions`, `/v1/risk-policy-versions`, `/v1/configuration` |
| Underwriting | `/v1/originations`, `/v1/risk-packages/{id}` |
| Monitoring | `/v1/monitors`, `/v1/monitoring-runs`, `/v1/alerts` |
| Data and files | `/v1/evidence`, `/v1/documents`, `/v1/exports` |
| Notifications | `/v1/events`, `/v1/webhook-deliveries`, `/v1/webhook-replays` |
| Financial reporting | `/v1/billing/summary`, `/v1/billing/transactions`, billing exports |

The API does not service loans, manage collection cases, contact borrowers, record payment promises or make the institution's final lending decision. Organization settings, user permissions, API keys, webhook destinations and payment settings are managed through the authorized console.
''')
    api('workflows','Integrate by product journey','''
AMLOK manages internal workflows. Your integration follows borrower-facing and product resources rather than choosing workflow versions or starting individual processing jobs.

For underwriting, create a borrower and embedding session, supply the institution's lending-product and policy versions, and submit the application with `POST /v1/originations`. Follow status and action requirements, then retrieve the completed risk package and evidence.

For continuous monitoring, enroll the funded deal with `POST /v1/monitors`. Inspect evaluation runs, package changes and alerts. Receive durable events and troubleshoot delivery attempts without triggering another assessment.

Use the [quickstart](/api-reference/quickstart), [risk-package guide](/api-reference/risk-package) and [Signal guide](/api-reference/monitoring-design) for the complete sequences.
''')
    api('examples','API request examples','''
These examples follow API 1.0.0 and use synthetic values. Configure your institution-issued origin and server-side key, then replace IDs with returned values. Each endpoint has cURL, Python and JavaScript examples generated from the same contract.

## Start underwriting

'''+sample('createOrigination')+'''

## Read the risk package

'''+sample('getRiskPackage')+'''

## Inspect supporting evidence

'''+sample('listEvidence')+'''

## Enroll a funded deal

'''+sample('createMonitor')+'''

## Export an assessment

'''+sample('createExport')+'''

Use [Postman](/downloads/amlok-api.postman_collection.json) for all 57 operations and the [complete risk-package example](/downloads/risk-package-example.json) for result structure. Requests are not a claim of live backend execution.
''')
    api('downloads','Specifications and integration downloads','''
Use these artifacts for the primary API 1.0.0 contract. Endpoint pages, request/response examples and Postman requests are generated from the same definitions.

- [OpenAPI 3.1 JSON](/openapi/amlok.json)
- [Postman collection: 57 operations](/downloads/amlok-api.postman_collection.json)
- [Operation index](/downloads/api-product-index.json)
- [Complete synthetic risk package](/downloads/risk-package-example.json)
- [Node.js webhook signature verifier](/downloads/verify-webhook.mjs)
- [Python webhook signature verifier](/downloads/verify_webhook.py)

Set your institution-issued origin and key in a private environment. Keys and secrets are not included. The [OpenAPI specification](/overview/openapi-spec) is the source of truth. [SDK guidance](/overview/sdks) covers client generation.
''')
    page('overview/openapi-spec','OpenAPI specification','Download the primary AMLOK API 1.0.0 contract.', '''
Use the [OpenAPI 3.1 specification](/openapi/amlok.json) as the authoritative machine-readable contract for AMLOK API **1.0.0**. It defines all 57 public operations, typed inputs and outputs, scopes, errors and examples.

API routes use `/v1`. The origin is supplied during institution onboarding; it is not the documentation or console hostname. Configure the origin explicitly when generating clients or running requests.

The specification contains the typed normalized evidence models so consolidating source-specific endpoints does not remove field definitions. JSON Schema conditionals remain authoritative even when a code generator cannot represent all constraints.

Use the [Postman collection](/downloads/amlok-api.postman_collection.json) and [quickstart](/api-reference/quickstart) to start integrating.
''')
    page('overview/sdks','SDKs and API clients','Build a client from the authoritative AMLOK contract.', '''
Generate a server-side client from the [current OpenAPI 3.1 contract](/openapi/amlok.json), or use the cURL, Python and JavaScript examples on each endpoint. The current contract contains 57 operations with typed request and response models.

Set your institution-issued API origin explicitly. Keep keys server-side, configure timeouts, reject cross-origin redirects and preserve idempotency keys during retries. Generated client types do not replace server authorization or JSON Schema conditional validation.

## Client generation

Generate your language's client from this OpenAPI file. The download contains the complete contract, including normalized evidence variants. Use the endpoint examples and Postman collection to check generated requests in your Sandbox. JSON Schema conditionals and source entitlements remain authoritative when a generator cannot express them as language types.

No packaged SDK is currently distributed. All published client examples and downloads use this same contract.
''')

    from institution_api_guides import write_guides as write_institution_guides
    write_institution_guides(spec,f,index)

def navigation(groups):
    path=ROOT/'docs.json';config=json.loads(path.read_text())
    tab=next(t for t in config['navigation']['tabs'] if t['tab'].lower()=='api reference')
    icons={'Sandbox':'flask-conical','Borrowers':'users','Connections':'plug','Configuration':'sliders-horizontal','Insights':'files','Results':'file-search','Data':'database','Evidence':'database','Signal':'activity','Events':'webhook','Exports':'download','Billing':'wallet','Reliability':'shield-check'}
    tab['groups']=[
        {'group':'Start here','pages':['api-reference/overview','api-reference/quickstart','api-reference/authentication','api-reference/environments','api-reference/downloads']},
        {'group':'Product guides','pages':['api-reference/integration-hub','api-reference/configuration','api-reference/data-access','api-reference/risk-package','api-reference/monitoring-design','api-reference/evidence-traceability','api-reference/documents']},
        {'group':'Endpoints','pages':[{'group':g,'icon':icons[g],'expanded':g=='Insights','pages':p} for g in ['Borrowers','Connections','Configuration','Insights','Results','Signal','Data','Evidence','Events','Exports','Billing','Reliability','Sandbox'] for p in [groups[g]]]},
        {'group':'Integration behavior','pages':['api-reference/response-format','api-reference/processing-lifecycle','api-reference/pagination','api-reference/idempotency','api-reference/request-recovery','api-reference/connection-recovery','api-reference/webhooks','api-reference/event-catalog','api-reference/webhook-operations','api-reference/errors','api-reference/rate-limits','api-reference/sandbox-journeys']},
        {'group':'Billing and exports','pages':['api-reference/credit-reporting','api-reference/consumption-reporting','api-reference/workload-reporting','api-reference/export-formats']},
    ]
    config['api']['playground']['display']='simple'
    config['api']['examples']['languages']=['bash','python','javascript']
    path.write_text(json.dumps(config,indent=2)+'\n')

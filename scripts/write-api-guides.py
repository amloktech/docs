"""Author the narrative companion to the generated API reference."""
from pathlib import Path
from wallet_contract import REPORTING_EVENTS
from public_api_scope import REMOVED_EVENTS, REMOVED_RESOURCES, public_example
import json

ROOT=Path(__file__).resolve().parent.parent
SOURCE=json.loads((ROOT/'data/api-contract-source.json').read_text())
INDEX=json.loads((ROOT/'data/api-reference-index.json').read_text())
OPS={r['id']:r for r in INDEX}
EVENT_ROWS=[r for r in SOURCE['Events']['values'][1:] if r[0] not in REMOVED_EVENTS]
EVENT_COUNT=len(EVENT_ROWS)+len(REPORTING_EVENTS)

def write(name,title,description,body):
    body=body.replace('67 financial-data resource types', '63 financial-data resource types')
    body=body.replace('164 operations', str(len(INDEX))+' operations').replace('28 event types',str(EVENT_COUNT)+' event types')
    for oid,op in OPS.items():body=body.replace('@@'+oid+'@@','/'+op['page'])
    text='---\ntitle: '+json.dumps(title)+'\ndescription: '+json.dumps(description)+'\n---\n\n'+body.strip()+'\n'
    (ROOT/'api-reference'/f'{name}.mdx').write_text(text.replace('0.1.0-draft','1.4.2').replace('\u2014','-').replace('\u2013','-'))

write('overview','API overview','Build workspace-scoped integrations with the AMLOK API 1.4.2.', '''
The AMLOK API organizes authorized financial evidence into a common data model and coordinates verification, underwriting, monitoring, and analytical investigation workflows. AMLOK identifies changes and risk signals so your institution can decide when to intervene. Borrower outreach and intervention take place in your institution's own systems.

This reference contains **164 operations**, **67 financial-data resource types plus credit and billing reporting resources**, **28 event types**, and schema-checked example payloads. Endpoint pages include cURL, Python, and Node.js request examples, response bodies, required scopes, and error definitions.

<CardGroup cols={2}>
  <Card title="Make your first request" icon="terminal" href="/api-reference/quickstart">Follow a complete connection and data-read flow.</Card>
  <Card title="Authentication and scopes" icon="key-round" href="/api-reference/authentication">Understand API keys, workspace boundaries, and permissions.</Card>
  <Card title="Webhooks" icon="webhook" href="/api-reference/webhooks">Verify signatures, deduplicate deliveries, and process changes.</Card>
  <Card title="OpenAPI and examples" icon="download" href="/api-reference/downloads">Download the specification, Postman collection, and verification code.</Card>
</CardGroup>

## How the API fits together

1. Create or identify a business or person under your institution tenant.
2. Record actual authorization and connect an enabled provider.
3. Synchronize evidence and read normalized records with their coverage and provenance.
4. Start approved workflows and retrieve asynchronous results.
5. Process signed events and keep your local records in sync.

Financial-data and reporting operations use a server-side bearer API key. The healthcheck and service-status endpoints are public and require no key. Each key authorizes exactly one workspace. Resources are workspace-scoped; a resource ID alone never grants access. Source capabilities, consent, scopes, and field entitlements all constrain the returned data.

## Explore the API

| Area | Start with |
| --- | --- |
| Connections and consent | [Create a connection](@@EP139@@), [record consent](@@EP137@@), [discover provider capabilities](@@EP163@@) |
| Identity and evidence | [Start verification](@@EP142@@), [upload a document](@@EP144@@) |
| Banking | [List accounts](@@EP021@@), [list transactions](@@EP025@@) |
| Payments, commerce, accounting, inventory | Browse the endpoint groups in the sidebar and the [data dictionary](/data-model/field-dictionary). |
| Lending and assessment | [Create an application](@@EP146@@), [run a workflow](@@EP147@@), [calculate attributes](@@EP148@@) |
| Monitoring and risk review | [Create a monitor](@@EP150@@), [review intervention signals](/api-reference/workflows#review-intervention-signals) |
| Reporting | [Credit reporting](/api-reference/credit-reporting), [consumption reporting](/api-reference/consumption-reporting), [cancellation and refunds](/pricing/refunds-and-payouts) |
| Delivery | [Register a webhook](@@EP158@@), [read changes](@@EP164@@) |
| Service availability | [Healthcheck](@@ST001@@), [service status](@@ST002@@) |

## Version and availability

Use the [integration status catalog](/integrations/status) to check provider availability and supported markets. Returned resources and fields depend on your enabled products, source permissions, and account entitlements.

This reference covers **AMLOK API 1.4.2**. Endpoint paths use the `/v1` major-version namespace. Configure `AMLOK_API_BASE_URL` with the environment URL issued to your institution.

See [integration onboarding](/api-reference/onboarding) for environment setup and [versioning](/api-reference/versioning) for compatibility rules.
''')

write('quickstart','Quickstart','Create a subject, capture authorization, connect a provider, and read normalized transactions.', '''
This walkthrough uses synthetic identifiers. Replace every returned ID with the value from your environment. Run requests from your server after receiving an AMLOK environment URL and scoped key.

## 1. Configure your environment

```bash
# Set these from your approved environment configuration and secret manager.
export AMLOK_API_BASE_URL="<your-institution-api-origin>"
export AMLOK_API_KEY="<institution-issued-key>"
```

The base URL excludes `/v1`. Do not store the key in source control, browser storage, or a mobile application. This flow needs `identity:write`, `documents:write`, `consent:write`, `connections:write`, `connections:read`, and `banking:read` as appropriate.

## 2. Create the business

```bash
curl --request POST --fail-with-body --max-time 30 \\
  "${AMLOK_API_BASE_URL}/v1/businesses" \\
  --header "Authorization: Bearer ${AMLOK_API_KEY}" \\
  --header "Content-Type: application/json" \\
  --header "Idempotency-Key: onboarding-business-1001" \\
  --data '{"legal_name":"Example Manufacturing Inc.","client_reference":"app-1029","incorporation_country":"CA"}'
```

Save `data.id`, illustrated below as `biz_example`. A created profile is client-asserted; it does not establish registry verification. [Request and response schema](@@EP135@@).

## 3. Capture real authorization

Obtain the subject's authorization through your institution's approved process. Upload the supporting evidence using [document upload](@@EP144@@), then record consent:

```json
{
  "subject_id": "biz_example",
  "subject_type": "business",
  "purposes": ["credit_assessment"],
  "scopes": ["banking:read"],
  "policy_version": "consent-v1",
  "evidence_document_id": "doc_consent"
}
```

Send this body to `POST /v1/consents` with a new idempotency key for this action. Save `data.id` as `con_example`. Recording consent is not a substitute for obtaining it. [Consent endpoint](@@EP137@@).

## 4. Connect an enabled provider

Use [provider capability discovery](@@EP163@@) to select a provider enabled for your institution, country, and resource needs. Then send this body to `POST /v1/connections`:

```json
{
  "subject_id": "biz_example",
  "provider_id": "BANK-02",
  "products": ["transactions"],
  "consent_id": "con_example",
  "redirect_uri": "https://client.example.com/connected"
}
```

Save `data.id` as `cnn_example`. Direct the authorized user through the short-lived `action.url`. The registered `redirect_uri` is a browser return location, not a webhook destination. Retrieve the connection or consume `connection.updated` before attempting a sync. [Connection endpoint](@@EP139@@).

## 5. Synchronize and wait for completion

Send this body to `POST /v1/connections/cnn_example/sync`:

```json
{
  "resources": ["bank_account", "bank_transaction"],
  "from": "2026-09-01",
  "to": "2026-10-01"
}
```

The response is `202 Accepted` with a sync-job ID. Poll `GET /v1/sync-jobs/{id}` with bounded backoff, or process `sync.completed` / `sync.failed`. Treat `partial` as incomplete coverage and inspect errors and actual date coverage. [Sync endpoint](@@EP140@@).

## 6. Read the transactions

```bash
curl --get --fail-with-body --max-time 30 \\
  "${AMLOK_API_BASE_URL}/v1/bank-transactions" \\
  --header "Authorization: Bearer ${AMLOK_API_KEY}" \\
  --data-urlencode "subject_id=biz_example" \\
  --data-urlencode "connection_id=cnn_example" \\
  --data-urlencode "posted_from=2026-09-01" \\
  --data-urlencode "posted_to=2026-10-01" \\
  --data-urlencode "limit=100"
```

Follow `page.next_cursor` until `page.has_more` is false. Keep the same filters for subsequent pages. Amounts are exact decimal strings; for bank transactions, `direction` carries the movement direction.

Next, implement [pagination](/api-reference/pagination), [safe retries](/api-reference/idempotency), and [webhook verification](/api-reference/webhooks).
''')

scope_rows=[]
for scope in sorted({op['scope'] for op in INDEX if op['scope']}):
    ops=[op for op in INDEX if op['scope']==scope]
    scope_rows.append('| `'+scope+'` | '+str(len(ops))+' | ['+ops[0]['title']+'](/'+ops[0]['page']+') |')
write('authentication','Authentication and authorization','Use workspace-scoped bearer keys and explicit resource permissions.', '''
## Bearer API keys

Financial-data and reporting operations use server-to-server API keys bound to exactly one workspace, institution tenant, and environment. [Healthcheck](@@ST001@@) and [service status](@@ST002@@) are public read-only exceptions and require no API key.

```http
Authorization: Bearer <AMLOK_API_KEY>
Accept: application/json
```

Use HTTPS. Keep credentials in your secret manager and load them on the server. Never put keys in a query string, browser bundle, analytics event, error report, or shared Postman export.

Manage key issuance, expiry, revocation, and rotation through the administration process agreed during onboarding. Authenticate requests with your institution-issued API key.

## Authorization has several layers

| Check | What it controls |
| --- | --- |
| Environment | A sandbox credential must not authorize production data. |
| Institution and workspace | Every resource and linked ID must belong to the one workspace bound to the key. |
| Endpoint scope | The operation requires its documented scope. |
| Product and provider entitlement | The institution must be entitled to the requested product and source. |
| Subject consent and purpose | Data collection and use must remain within recorded authorization. |
| Field entitlement | Sensitive fields can require additional permissions and purpose checks. |

Caller-supplied `tenant_id` or `workspace_id` values cannot select another workspace. The API derives the workspace and institution from the key. Every subject, document, manifest, baseline, and webhook destination must belong to that workspace. Use a separately provisioned key for another workspace.

Read access does not authorize borrower communications, funding, filings, or changes to credit limits. AMLOK provides assessment results and risk alerts to your institution. Borrower outreach, collections, and intervention remain in your institution's own systems. Credit access is reporting-only. No customer wallet or payment-setting endpoints are exposed. The client portal manages payment methods, top-up settings, and cancellation. Enterprise clients can also request cancellation through their dedicated account manager. Cancellation is available at any time without notice, with an immediate stop to processing, usage deductions, and upcoming top-ups. Full closure is at the end of the request month with an immediate refund of all unused credits to the saved portal bank account. Deletion follows month closure and generation of final information. Report generation and downloads do not change credits.

## Scope reference

Scopes are API permissions. They are not OAuth claims or evidence that a provider grants all requested data.

| Scope | Operations | Example |
| --- | ---: | --- |
'''+ '\n'.join(scope_rows)+'''

## Authentication failures

- **401 `unauthenticated`:** missing, invalid, expired, or incorrect-environment credential. Stop retrying until credentials are corrected.
- **403 `forbidden`:** the key is authenticated but lacks the necessary scope or entitlement.
- **404 `not_found`:** an ID is missing or not visible to this institution. Do not probe IDs from other tenants.

## Credential rotation

When your environment supports overlapping keys, provision a replacement, update consumers, verify traffic uses it, and revoke the old key through the agreed administration process. If overlap is unavailable, coordinate a cutover. Never infer a rotation endpoint from this guide.

Webhook signing secrets are separate from API keys. Store each secret with its destination and environment. The registration response returns a new signing secret only once; list responses omit it.
''')

write('environments','Environments and requests','Configure the correct API host, transport, and headers before making requests.', '''
## Base URL

Set `AMLOK_API_BASE_URL` to the HTTPS origin issued for your institution and environment. Use the matching environment-specific API key.

| Setting | Meaning |
| --- | --- |
| `AMLOK_API_BASE_URL` | Approved HTTPS origin, without `/v1` or a trailing slash. |
| `AMLOK_API_KEY` | Server-side key for that environment and institution. |
| Webhook destination and secret | Separate endpoint configuration for the same environment. |

Sandbox and production keys, subjects, provider connections, consent records, event destinations, and idempotency records must remain separate. Do not copy production evidence into a sandbox unless your approved data-handling process explicitly allows it.

## Request format

Paths begin `/v1`. JSON writes use `Content-Type: application/json`. JSON reads use `Accept: application/json`. Document uploads use multipart form data with a client-generated boundary.

| Header | When to send it |
| --- | --- |
| `Authorization` | Every authenticated financial-data or reporting request. |
| `Content-Type` | JSON body or multipart upload. Let the HTTP client set the multipart boundary. |
| `X-Request-ID` | Optional caller correlation ID. Record AMLOK's returned `request_id` separately. |
| `Idempotency-Key` | Every POST command, including download-link issuance and event replay. |
| `If-Match` | PATCH configuration with the current quoted ETag. |

Treat IDs as opaque case-sensitive strings. Do not trim leading zeros, infer information from a prefix, or reuse an ID across environments.

## Network behavior

The examples use a 30-second client timeout as an illustration, not a server SLA. Set explicit timeouts suited to your application. A timeout does not prove a command was rejected; retain its idempotency key when retrying.

Do not forward an API credential to a redirected host. Configure the correct origin and reject unexpected redirects. Long-running work returns a resource to poll instead of holding the HTTP connection open.

## Environment configuration

Onboarding must provide the production and sandbox origins, enabled scopes and providers, numeric quotas, network controls, support route, incident contacts, and any contractual service commitments. See [integration onboarding](/api-reference/onboarding).
''')

write('response-format','Responses and data conventions','Interpret envelopes, exact amounts, missing values, coverage, and record versions.', '''
## Envelopes

Financial-data and reporting operations use a consistent envelope. Single responses contain `data` and `meta`. Collection responses also contain `page`. Errors contain `error` and `meta`. The public healthcheck and service-status endpoints use their lightweight status schemas without a `data` / `meta` wrapper; see their individual response definitions.

```json
{
  "data": [],
  "page": {"next_cursor": null, "has_more": false, "limit": 100},
  "meta": {
    "request_id": "req_example",
    "schema_version": "1.4.2",
    "generated_at": "2026-10-23T14:00:00Z",
    "data_status": "complete"
  }
}
```

This example is a completed, known-empty collection. An unqueried source or a failed connection must not be represented as an empty successful result.

Resource records inherit `id`, `object`, `created_at`, `updated_at`, `record_version`, `source_refs`, `data_status`, `missing_fields`, and `schema_version`. Subject context, provenance, and other optional fields appear when relevant and authorized. Response-only helper objects such as calculation jobs and signed links use their documented helper schemas inside `data`.

## Missing, empty, and redacted values

| Value | Interpretation |
| --- | --- |
| `null` | A value is unavailable or unknown. Consult `missing_fields`. |
| `0` or `"0.00"` | A known numeric zero with evidence. |
| `false` | A known false condition. |
| `[]` | A collection was queried and is known to be empty. |
| Omitted field | Optional, not selected, or not authorized; inspect the contract and entitlements. |

Denied sensitive values are omitted. Missing-field explanations must not leak the hidden value. `data_status: partial` means you must inspect the available coverage before using the result.

## Money and time

```json
{"amount": {"amount": "1250.00", "currency": "CAD"}, "direction": "inflow"}
```

Monetary amounts and decimal ratios use strings. Preserve exact precision and currency. Bank-transaction amounts are absolute magnitudes with a separate direction; other resources can define signed values. Do not apply one sign rule to every domain or sum currencies without explicit FX inputs.

Dates preserve source calendar dates. Timestamps use RFC 3339 UTC. `generated_at` is response generation time, `retrieved_at` is collection time, and `as_of` / `observed_at` describe evidence timing when known. A retrieval timestamp is not proof that a balance is real time.

## Coverage and provenance

`source_refs` identifies the evidence origin. Optional field provenance records the source path and transformation. Coverage records the actual sources, time interval, and completed jurisdictions.

An observed zero lien count for one completed jurisdiction says nothing about an unqueried or failed jurisdiction. An unavailable DSCR is not zero and is not an approval. See [worked payloads](/api-reference/examples).

## Versions and projections

`record_version` tracks a particular resource. `schema_version` identifies the serialization contract. Use the quoted ETag with `If-Match` for supported mutable configuration.

The `fields` parameter selects comma-separated **top-level field names** while preserving required identity and metadata. For example, `fields=id,amount` returns the mandatory metadata and the complete `amount` object when authorized. Nested paths, wildcards, and unknown field names return `400 validation_error`.

GET endpoints use a dedicated `*Read` schema whose domain fields can be omitted by projection. Present fields retain their canonical types, nullability, and nested requirements. Full canonical schemas remain available for complete objects and mutation responses. Omitting `fields` returns the full authorized representation. This uses standard OpenAPI 3.1 Schema Objects, so generated clients must treat unselected properties as absent rather than null.

`include` permits `provenance` and `missing_fields`; it does not grant access or allow arbitrary relationship expansion. The [data dictionary](/data-model/field-dictionary) describes full objects. See the [OpenAPI Schema Object specification](https://spec.openapis.org/oas/v3.1.1.html#schema-object) for the schema vocabulary.
''')

write('pagination','Pagination and filtering','Read stable cursor pages and apply only the filters an endpoint supports.', '''
## Cursor pagination

Collection endpoints use opaque AMLOK cursors. The default page size is **100**, with a minimum of **1** and maximum of **200**.

```http
GET /v1/bank-transactions?subject_id=biz_example&posted_from=2026-09-01&posted_to=2026-10-01&limit=100
```

Read `page.next_cursor` and send it with the same filters on the next request. Finish when `page.has_more` is false and `page.next_cursor` is null. Do not decode a cursor or substitute an upstream provider cursor.

Resource collections use stable `updated_at`, then `id` ordering. The credit ledger instead uses ascending `sequence` with its documented `sequence_after` filter. Cursors bind the workspace, institution, filters, and snapshot. A cursor from a different query or environment must be rejected.

```javascript
// Node.js, using your institution-issued environment and key.
const baseUrl = process.env.AMLOK_API_BASE_URL;
const apiKey = process.env.AMLOK_API_KEY;
if (!baseUrl || !apiKey) throw new Error("Configure API environment and key");
const seen = new Set();
let cursor;
let finished = false;
for (let pageNumber = 0; pageNumber < 1000; pageNumber++) {
  const url = new URL("/v1/bank-transactions", baseUrl);
  url.search = new URLSearchParams({
    subject_id: "biz_example", posted_from: "2026-09-01",
    posted_to: "2026-10-01", limit: "100", ...(cursor ? { cursor } : {})
  }).toString();
  const response = await fetch(url, {
    headers: { Authorization: `Bearer ${apiKey}`, Accept: "application/json" },
    redirect: "error", signal: AbortSignal.timeout(30000)
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const result = await response.json();
  // Persist/process result.data; also inspect result.meta.data_status and coverage.
  if (!result.page.has_more) { finished = true; break; }
  cursor = result.page.next_cursor;
  if (!cursor || seen.has(cursor)) throw new Error("Invalid or repeated cursor");
  seen.add(cursor);
}
if (!finished) throw new Error("Client page budget reached; save progress for review");
```

The 1,000-page budget is an example client safeguard. It is not a server limit. Add your retry policy around each request and persist the continuation state if processing spans runs.

## Filters are endpoint-specific

Common resource filters include `subject_id`, `updated_from`, and `updated_to`. Source-backed collections can expose `connection_id`; resources with a status can expose a typed `status` filter. Each endpoint page lists the supported parameters.

Specialized filters include bank-account and posting-date filters, invoice due dates, loan days-past-due thresholds, lien jurisdiction, and attribute key. Unsupported or unknown parameters return `400` instead of silently broadening the result.

Intervals are start-inclusive and end-exclusive unless the individual field explicitly says otherwise. Unknown source dates do not match a dated filter.

## Historical reads and changes

`as_of` is supported only for stored point-in-time attribute or risk-snapshot results. It is not a universal historical-read parameter. Billing uses an immutable `snapshot_id` instead: obtain it from [the current billing snapshot](/api-reference/endpoints/billing/retrieve-current-billing-snapshot), then reuse it across financial reads and exports. Cursor pages remain bound to the same snapshot and filters.

Use [the change feed](@@EP164@@) for normalized created, updated, and deleted actions. Keep its cursor separate from collection cursors and source-adapter cursors. Bootstrap by reading the required collections; the cursor bootstrap, expiry, and retention windows remain deployment decisions.
''')

write('idempotency','Idempotency and concurrency','Retry intended actions safely and protect mutable configuration from stale writes.', '''
## Idempotency for POST commands

Every POST operation requires an `Idempotency-Key`. Generate it once for one intended action, store it with the payload, and reuse both for retries.

```http
Idempotency-Key: onboarding-connection-1001
```

The deduplication scope is **institution + workspace + environment + operation + key**, with **24-hour retention**. An identical replay returns the original result; a different intended payload with the same key returns `409 idempotency_conflict`.

| Situation | Client behavior |
| --- | --- |
| Network timeout after POST | Keep the same key and identical payload; the command may already have been accepted. |
| Transient 429/503 | Respect the retry delay and reuse the same key for that action. |
| 409 conflicting payload | Reconcile the original action. Use a new key only for a genuinely new intended action. |
| Retry beyond the retention window | Reconcile the existing resource/job before creating a new action. |
| Multipart upload | Reuse the same file bytes and logical fields. Keep the request content unchanged when retrying. |

Never generate a new idempotency key on every automatic retry. Do not assume a command is safe to replay indefinitely after deduplication retention expires.

## Optimistic concurrency for PATCH

Read the current [monitor](@@EP116@@), retain the quoted `ETag`, and send it in `If-Match`. The PATCH body changes only explicitly supplied fields.

```http
PATCH /v1/monitors/mon_example
Authorization: Bearer <AMLOK_API_KEY>
Content-Type: application/json
If-Match: "3"

{"status":"paused"}
```

In the synthetic success example the new record version is `4` and the ETag is `"4"`. A stale precondition returns `412 version_conflict`. Re-read, compare, and decide whether the change is still intended; do not blindly overwrite the newer record.

The PATCH schemas reject empty bodies, unknown properties, and null clearing. Omit fields you do not intend to change.

A pre-execution `402 insufficient_credits` rejection does not reserve an accepted operation or charge credits. After funding, retry the same intended request with the same key.

See [errors](/api-reference/errors) and [asynchronous jobs](/api-reference/async-jobs) for recovery behavior.
''')

error_table='\n'.join('| `'+r[0]+'` | '+r[1]+' | '+r[3]+' | '+r[4]+' |' for r in SOURCE['Error Codes']['values'][1:])
error_table+='\n| `insufficient_credits` | 402 | No, until funded | Fund the workspace in the portal, then retry the rejected workflow. Unprocessed work is not charged. |'
error_table+='\n| `invalid_state` | 409 | No, until state permits | Operational commands stop immediately on cancellation. Read-only reporting remains available until deletion; report downloads require a ready export. |'
write('errors','Errors','Handle stable error codes, correlation IDs, validation failures, and recoverable outages.', '''
Errors use a stable code and a safe explanation. Do not branch on human-readable message text.

```json
{
  "error": {
    "code": "invalid_search_scope",
    "message": "At least one supported jurisdiction is required.",
    "field": "jurisdictions",
    "retryable": false,
    "request_id": "req_example"
  },
  "meta": {
    "request_id": "req_example",
    "schema_version": "1.4.2",
    "generated_at": "2026-10-23T14:00:00Z",
    "data_status": "complete"
  }
}
```

The example has HTTP `422`. `meta.data_status: complete` describes the error response, not successful completion of the requested workflow.

## Error catalog

| Code | HTTP | Retryable | Client action |
| --- | ---: | --- | --- |
'''+error_table+'''

## Retry decisions

Honor `error.retryable` and `Retry-After` when provided. A source error or internal error can require investigation; its HTTP class alone does not establish that repeating a command is safe. Preserve the idempotency key for the same POST action.

Do not retry malformed input, invalid credentials, missing permissions, or stale resource versions without resolving the cause. Do not broaden subject IDs or permissions in response to an authorization error.

## Insufficient credits

A billable workflow returns `402 insufficient_credits` when available credits cannot cover its cost. CAD 200.00 is an automatic top-up trigger, not a processing floor. Requests may continue below it while funded. Pending payments are excluded from available credits. The rejection occurs before work is accepted, without a usage debit. After credits are available, retry the same intended request with the same idempotency key; a pre-execution insufficient-credit rejection does not reserve the key as an accepted operation.

Read-only reports and baseline retrieval do not require a new usage charge. Signal reassessment is included in Signal, not billed as another Insights underwriting.

## Partial results versus request errors

A valid request can return usable partial data with `meta.data_status: partial`. Job-level errors and resource `missing_fields` explain the missing scope. Do not treat a `200` as evidence that every provider succeeded, or an unavailable metric as zero.

## Diagnostics

Record the AMLOK `request_id`, operation, timestamp, environment, HTTP status, error code, and relevant resource/job IDs in your restricted operational logs. Redact keys, signing secrets, signed links, raw identity evidence, and full response bodies.

Provide sanitized request IDs through your agreed support channel. Your agreement defines support channels and response commitments.
''')

write('rate-limits','Rate limits and retries','Handle throttling and transient failures without duplicating work.', '''
The API applies workspace and provider-aware limits. Numeric quotas, burst allowances, concurrent-job limits, and per-provider refresh budgets are configured for your environment. Refer to your agreement and response headers for the applicable limits.

## Throttled responses

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 30
Content-Type: application/json
```

The value `30` illustrates a delay in seconds. Clients should also accept an HTTP-date form of `Retry-After`. The error body uses `rate_limited` and includes a request ID.

## Bounded retry policy

1. Retry only a transient condition and an operation you can safely repeat.
2. Respect the server's `Retry-After`; do not retry earlier than that time.
3. Otherwise use exponential backoff with jitter, a maximum attempt count, and an overall deadline.
4. Keep the same idempotency key and payload for a retried POST action.
5. Stop when the retry budget is exhausted and retain the request/job ID for reconciliation.

For example, a client might use a 1-second base delay, a 30-second exponential-delay cap, and five attempts. These are illustrative client settings. If `Retry-After` exceeds the overall client deadline, schedule a later attempt instead of shortening the server's delay.

## Manage load deliberately

- Bound concurrent requests per tenant and provider.
- Avoid starting overlapping syncs for the same connection and time window.
- Use pagination and narrow documented filters.
- Cache reference data according to your release agreement; no cache lifetime is asserted here.
- Prefer lifecycle events to tight polling loops, with reconciliation for missed or delayed events.

Do not retry `401`, `403`, `409`, `412`, or validation errors blindly. A network timeout leaves a command's outcome uncertain; [idempotency and reconciliation](/api-reference/idempotency) determine the next step.
''')

write('async-jobs','Asynchronous jobs','Distinguish acceptance, progress, partial results, and terminal outcomes.', '''
A successful HTTP response can indicate acceptance rather than completed work. The source contract uses `202` for most long-running commands and `201` for creation of a verification session whose result arrives later.

| Command | Acceptance | Observe the result |
| --- | --- | --- |
| [Start sync](@@EP140@@) | 202, sync job | `GET /v1/sync-jobs/{id}`; `sync.completed` or `sync.failed` |
| [Start verification](@@EP142@@) | 201, verification | `GET /v1/verifications/{id}`; verification events |
| [Search liens](@@EP143@@) | 202, search | `GET /v1/lien-searches/{id}`; lien-search events |
| [Upload document](@@EP144@@) | 202, document | `GET /v1/documents/{id}`; `document.processed` |
| [Run workflow](@@EP147@@) | 202, workflow run | `GET /v1/workflow-runs/{id}`; workflow events |
| [Calculate attributes](@@EP148@@) | 202, calculation job | `GET /v1/attribute-calculations/{id}`; `attributes.calculated` |

The event replay command returns a queued replay receipt. Monitor redelivery through your webhook receiver and the delivery controls configured during onboarding.

## Poll safely

Persist the returned resource or job ID. Poll the documented retrieval route with bounded backoff, respect throttling, and stop at the resource's terminal state or your application deadline. A client polling deadline does not cancel server work.

Sync-style jobs use `queued`, `running`, `completed`, `partial`, `failed`, and `cancelled`. Other resources have their own typed states. Do not assume every job uses the same enum or that a generic cancellation command exists.

## Interpret completion

- `partial` means some requested scope remains unavailable. Inspect errors, missing intervals, completed jurisdictions, and missing-field reasons.
- Verification completion means a result is available; it can be declined or require review.
- A completed lien search with no results applies only to the declared completed scope.
- Attribute calculation can complete with individual values marked `unavailable`.
- A completed assessment is not authorization to fund a loan or contact a borrower.
- Account cancellation immediately stops processing, usage deductions, and upcoming top-ups. Cancel pending work and release unused holds without capture. Full account closure is at the end of the request month. After that month closes and final information is generated, deletion removes all associated workspace data; there is no public deletion-command API.

Retrieve the authoritative resource after an event. Use `resource_version` to avoid overwriting a newer record with an older delivery. See [webhooks](/api-reference/webhooks).
''')

node_verifier=(ROOT/'downloads/verify-webhook.mjs').read_text()
python_verifier=(ROOT/'downloads/verify_webhook.py').read_text()
write('webhooks','Webhooks and signatures','Verify raw-body signatures and consume events with durable deduplication.', '''
## Register an event destination

Use [webhook endpoint registration](@@EP158@@) with an institution-approved HTTPS URL and event keys from the [event catalog](/api-reference/event-catalog).

```json
{
  "url": "https://client.example.com/amlok-events",
  "event_types": ["sync.completed", "sync.failed", "verification.completed"],
  "description": "Application evidence events"
}
```

The creation response includes a signing secret once. Store it immediately in a secret manager with the destination, workspace, institution, and environment. Destination list responses do not return it. Never use the API key as the webhook secret.

## Signature contract

```text
X-AMLOK-Signature: t=<unix_seconds>,v1=<hex_hmac>
signed_bytes = UTF8(timestamp + ".") + exact_raw_request_body
hex_hmac = HMAC-SHA256(webhook_secret, signed_bytes)
```

Verify the exact bytes before JSON parsing or reserialization. Compare the digest in constant time. The timestamp tolerance is five minutes in either direction; keep the receiver's clock synchronized.

The following helpers implement the signature format. They validate the signature and basic envelope, but your application must still enforce destination/tenant association, durable deduplication, payload validation, and processing rules.

<Tabs>
<Tab title="Node.js">

```javascript
'''+node_verifier+'''
```

</Tab>
<Tab title="Python">

```python
'''+python_verifier+'''
```

</Tab>
</Tabs>

## Receive, persist, acknowledge

1. Apply a configured body-size limit and capture the raw bytes. Use the payload limit configured for your environment.
2. Resolve the expected secret from the registered destination, not from an untrusted body field.
3. Verify the signature and timestamp, then validate the event against the contract.
4. Atomically insert the event into a durable inbox with a unique key of workspace/environment + event ID. Persist its processing job in the same transaction, or use a transactional outbox.
5. Return `2xx` after durable acceptance. A duplicate already accepted event can receive `2xx` without repeating its effects.
6. Process asynchronously. Fetch the authorized resource and apply only a newer resource version.

Do not mark an event complete before its effects are durably committed. A worker failure after acknowledgment must be recoverable from your inbox; the sender may not deliver again. An invalid signature should receive a non-2xx response and must not enter the business-processing queue.

## Delivery, retries, and replay

Delivery is at least once, and arrival order is not guaranteed. Keep deduplication records for the agreed replay window, not merely the five-minute signature tolerance.

The retry offsets after the first failed delivery are **1 minute, 5 minutes, 30 minutes, 2 hours, 8 hours, and 24 hours**. Terminal failures require delivery review and reconciliation.

[Replay](@@EP160@@) preserves the original event ID. It must use a fresh delivery timestamp/signature so delayed replay can pass timestamp verification. Secret rotation overlap, replay retention, delivery timeouts, and administrative controls are configured during onboarding.

Event bodies contain resource references and limited status changes. Retrieve sensitive evidence through authenticated API reads. Do not add provider credentials, identity media, or unrestricted raw payloads to event logs.
''')

event_table='\n'.join('| `'+r[0]+'` | `'+r[1]+'` | '+r[2]+' | '+r[3]+' |' for r in EVENT_ROWS)
event_table+='\n'+'\n'.join('| `'+event+'` | `'+resource+'` | '+trigger+' | Resource ID, version and status; retrieve full details. |' for event,resource,trigger in REPORTING_EVENTS)
write('event-catalog','Event catalog','Subscribe to '+str(EVENT_COUNT)+' lifecycle events.', '''
Every event uses the same envelope. The event ID is the deduplication key within the workspace and environment. `resource_version` identifies the version that triggered the event.

```json
{
  "id": "evt_example",
  "type": "verification.completed",
  "created_at": "2026-10-23T14:06:00Z",
  "schema_version": "1.4.2",
  "resource_type": "verification",
  "resource_id": "ver_example",
  "resource_version": 2,
  "data": {"status": "in_review"}
}
```

The example indicates that a verification result is ready for review. It is not an approval. The `data` object is deliberately limited; retrieve the referenced resource for authorized details.

| Event | Resource | Trigger | Minimal details |
| --- | --- | --- | --- |
'''+event_table+'''

The details column summarizes each event. The OpenAPI reference defines the shared envelope and event keys. Retrieve the referenced resource for its complete current representation.

`resource.deleted` can refer to any resource type. Preserve the deletion version and avoid treating an older event as a later recreation. Follow your institution's retention rules when applying tombstones.

See [webhook verification and delivery](/api-reference/webhooks) before subscribing or processing events.
''')

write('documents','Document uploads and downloads','Upload permitted evidence and retrieve short-lived authorized download links.', '''
## Upload evidence

[POST /v1/documents](@@EP144@@) accepts multipart form data with `file`, `subject_id`, and `document_type`. The response is `202` with a document resource.

```bash
curl --request POST --fail-with-body --max-time 30 \\
  "${AMLOK_API_BASE_URL}/v1/documents" \\
  --header "Authorization: Bearer ${AMLOK_API_KEY}" \\
  --header "Idempotency-Key: statement-upload-1001" \\
  --form "file=@statement-2026-09.pdf;type=application/pdf" \\
  --form "subject_id=biz_example" \\
  --form "document_type=bank_statement" \\
  --form "period_start=2026-09-01" \\
  --form "period_end=2026-09-30"
```

Let the HTTP client construct the multipart `Content-Type` boundary. Do not set `Content-Type: application/json` for this route.

The upload period records the document's stated evidence period. It is not the exclusive `to` filter used by transaction queries. Poll the document's `extraction_status` or consume `document.processed`; acceptance does not establish a completed or verified extraction.

## File controls

Document processing validates actual file content, allowed types, malware status, tenant ownership, and permitted purpose. Maximum size, page limits, accepted MIME types, scan timeouts, and residency are environment settings. The PDF above is illustrative and is not a universal file-acceptance promise.

Use only authorized evidence. The normalized default response excludes raw biometric media, card PAN/CVV, and provider credentials. Do not place credentials inside uploaded filenames or metadata.

## Authorized download

Send `{"purpose":"credit_assessment"}` to [POST /v1/documents/{id}/download](@@EP145@@) with `documents:read` and an idempotency key. The response contains `data.document_id`, `data.url`, and `data.expires_at`.

The URL is a temporary capability. Do not make it public, log it, put it in analytics, or persist it as a permanent asset address. Download it only within its authorized context and expiry. Do not attach an AMLOK API key to the signed storage URL.

Use the expiry and storage domain returned by your environment. Upload documents through the documented multipart endpoint.

## Retention and deletion

Retention is managed by authorized users through workspace configuration in the AMLOK platform and in accordance with applicable compliance frameworks. Consent revocation or connection disconnection stops future collection; it does not itself delete stored evidence. After the cancellation request month closes and final information is generated, workspace deletion removes all associated workspace data. Necessary final billing, refund, and bank-return records are retained separately without borrower source data, documents, analysis outputs, or active workspace access. This API does not expose deletion-request endpoints. See [privacy and data handling](/security/privacy).
''')

write('versioning','Versioning and compatibility','Track API paths, schema versions, record versions, and policy revisions separately.', '''
## Version layers

| Version | Purpose |
| --- | --- |
| `/v1` path | Major HTTP interface namespace. |
| `schema_version` | Serialization contract, currently `1.4.2`. |
| `record_version` / ETag | Concurrency and change order for one resource. |
| `workflow_version` / `ruleset_version` | Approved orchestration or policy revision. |
| `calculation_version` | Definition or model revision behind a derived value. |
| Provider API version | Upstream evidence schema recorded in provenance where available. |

Do not use one version as a substitute for another. A newer record can still follow the same schema; a recalculation under a new policy must retain its own provenance.

## Breaking changes

Changing a field's meaning, type, requiredness, units, sign convention, or calculation requires contract review and versioned client communication. Endpoint removal, changed authorization behavior, and changed idempotency or pagination semantics also require compatibility review.

New optional fields can be additive when existing meanings remain intact. Enum additions must be announced. Retain raw provider statuses and handle normalized `unknown` values where the resource defines them.

## Client guidance

Tolerate new optional response properties. Validate the fields your application relies on and fail safely when a critical contract assumption no longer holds. Do not fabricate a default score, currency, or approval state for an unknown value.

Reject invalid request properties according to the documented request schema. Store schema and calculation versions with evidence used for decisions. Preserve immutable risk snapshots instead of rewriting the original assessment.

## Release lifecycle

This reference documents API version **1.4.2**. Your service agreement defines support windows and deprecation notice periods; follow the migration guidance provided for a version transition.

Download and pin the [OpenAPI contract](/openapi/amlok-v1.json) used by your integration. Review a schema diff and rerun contract tests before adopting a new version.
''')

write('security','Security, privacy, and auditability','Design your integration around tenant isolation, least privilege, and controlled evidence access.', '''
Protect your integration with tenant-scoped access, least privilege, and controlled evidence handling. See [Security & Compliance](/security/overview) for AMLOK platform controls and privacy practices.

## Institution and subject boundaries

Bind requests to the tenant represented by the API key. Check ownership of every referenced subject, document, connection, manifest, and snapshot. A valid ID from another tenant must not become visible through a relationship, filter, download, or event.

Grant the smallest useful scopes. Separate service accounts by environment and workload. A read-only analytical service should not hold workflow-execution or configuration-write permissions.

## Evidence and consent

Record the authorized purpose, consent policy version, evidence, and relevant scope. Re-check these constraints when collecting, reading, exporting, or sending data. Revocation stops new collection but does not bypass an applicable retention or legal-hold policy.

Mask or tokenize restricted identifiers by default. Avoid storing unnecessary identity data in your own system. Raw biometric media, PAN, CVV, and provider secrets are not part of the normalized default response.

## Audit trails

Capture institution, service identity, purpose, operation, resource version, correlation ID, and outcome in your restricted audit system. Record the analysis configuration, input versions, and result reviewed. Preserve evidence manifests and immutable decision snapshots.

Redact keys, webhook secrets, signed URLs, raw documents, and sensitive payload fields. Do not rely on broad request/response logging as an audit strategy.

## Webhook and outbound destination controls

Register only institution-controlled HTTPS destinations. Deployment must validate destinations against SSRF, private-network targets, unsafe redirects, and tenant policy. Receivers verify signatures over raw bytes and durably deduplicate events.

## Retention and incident handling

Authorized users manage retention in the AMLOK platform according to applicable compliance frameworks. Completed workspace deletion removes all associated workspace data. Necessary final billing, refund, and bank-return records are retained separately without borrower source data, documents, analysis outputs, or active workspace access. Workspace deletion is managed in the platform, not through a public deletion-request API. Cancellation may be requested at any time without notice through the client portal or a dedicated enterprise account manager. Closure is at the end of the request month, with an immediate full unused-credit refund to the saved bank account. Deletion occurs after that month closes and final information is generated.

Before production, agree data locations, retention rules, encryption/key-management requirements, breach-reporting channels, access reviews, incident contacts, and support escalation. Record these settings during [integration onboarding](/api-reference/onboarding).
''')

write('workflows','Integration workflows','Connect the endpoint families into verification, underwriting, monitoring, and intervention signals.', '''
## Verify an applicant

Create a business/person, obtain authorization, and upload permitted evidence. [Start verification](@@EP142@@) with an approved workflow version. If a hosted URL is returned, route the applicant through it and wait for the result.

Retrieve checks and screening matches. `in_review`, unresolved identity, missing ownership evidence, and possible screening matches require explicit handling. Completion is not the same as a verified identity or institutional approval.

## Underwrite from frozen evidence

1. [Create the application](@@EP146@@) with exact amount and currency.
2. Connect and synchronize authorized sources, then inspect coverage and freshness.
3. [List ready input manifests](@@BM001@@) for the subject after synchronization. Use the returned manifest ID for [attribute calculations](@@EP148@@), with a calculation window contained in the frozen manifest window. Retrieve the manifest to confirm coverage; missing coverage is not a zero value.
4. [Start an underwriting run](@@EP147@@) with `workflow_type: underwrite`, an approved version, and input resource IDs.
5. Retrieve the decision and immutable risk snapshot. Distinguish an advisory recommendation from the institution's decision.

Missing inputs produce explicit unavailability. Do not replace an unavailable DSCR, credit score, PD, or income verification with an inferred value. Provider bank deposits alone do not establish gross income or employment.

## Observe funding

The API exposes lender-supplied loans, facilities, guarantees, collateral, and repayment schedules. [Credit reporting](/api-reference/credit-reporting) shows prepaid AMLOK service credits and consumption. It provides no payment controls. Borrower funding and filings remain in the institution's authorized systems.

## Monitor an existing exposure

1. [List ready monitoring baselines](@@BB001@@) for the borrower/business. AMLOK prepares these from a completed assessment or the agreed existing-portfolio onboarding process. If none is ready, complete that process before creating a monitor.
2. [Retrieve the baseline](@@BB002@@) and its linked risk snapshot. The response provides the frozen input-manifest ID and approved snapshot ID.
3. [Create a monitor](@@EP150@@) using the returned `snapshot_id` as `baseline_snapshot_id`, with resource types, attribute keys, cadence, and ruleset version. All linked IDs must belong to the same subject and key-bound workspace.
4. Consume alerts and retrieve supporting evidence. Baseline reads do not launch or charge an Insights underwriting.

Compare comparable time windows and coverage. A data outage is not an improvement in borrower risk. Refresh cadence depends on source capability and consent; a daily requested cadence is not a source freshness guarantee.

For a material change, Signal reassesses risk using existing baseline data and newly processed records. Each updated version counts as a new record; retries and repeated reads of the same unchanged version do not count again. This work is included in Signal and does not launch or charge another Insights underwriting. Preserve the original snapshot and the new evidence for audit. A separately requested full underwriting is a distinct Insights operation.

## Review intervention signals

Read alerts alongside the current risk snapshot, the monitoring baseline, and supporting source evidence. Review severity, the rule or threshold that triggered the alert, data freshness, and missing coverage before deciding whether intervention is needed.

Signed webhooks notify your institution's registered systems that results or alerts are available. They do not contact borrowers. Your institution decides whether and how to intervene using its own staff, policies, and systems.

Use `workflow_type: investigate` to analyze suspicious evidence or related-party signals. Its purpose is evidence review and risk assessment. AMLOK does not create servicing cases, assign follow-up tasks, send borrower messages, collect repayments, or manage payment promises.

## Four assessment workflow types

`verify`, `underwrite`, `monitor`, and `investigate` are the workflow enum values. Funding and re-underwriting are lifecycle journeys, not additional enum values.
''')

worked_parts=[]
for r in SOURCE['Examples']['values'][1:]:
    request=json.loads(r[3]);response=public_example(json.loads(r[4]))
    if r[0]=='Read partial balance':response['data']['date_basis']='unknown'
    if any('/'+segment in r[2] for segment in ['cases', 'tasks', 'communications', 'payment-promises']): continue
    worked_parts.append('## '+r[0]+'\n\n`'+r[1]+' '+r[2]+'`\n\n'+r[5]+'\n\n'+('### Request body\n\n```json\n'+json.dumps(request,indent=2)+'\n```\n\n' if request else '')+'### Response or event payload\n\n```json\n'+json.dumps(response,indent=2)+'\n```')
write('examples','Worked payloads','Inspect synthetic successful, partial, unavailable, and failed API outcomes.', '''
These scenarios expand the source workbook into readable JSON examples. Values and URLs are synthetic. Use the endpoint page for the request schema and HTTP status.

The invalid-search example is intentionally invalid input. The account-balance example includes the required `date_basis: unknown` because no source observation timestamp is available.

'''+ '\n\n'.join(worked_parts))

write('downloads','Downloads and developer tools','Use the machine-readable contract and runnable verification examples.', '''
<CardGroup cols={2}>
  <Card title="OpenAPI 3.1 contract" icon="file-json" href="/openapi/amlok-v1.json">164 operations, resource schemas, authentication, examples, and the webhook envelope.</Card>
  <Card title="Postman collection" icon="send" href="/downloads/amlok-api.postman_collection.json">Requests grouped by domain with synthetic saved responses.</Card>
  <Card title="Node.js webhook verifier" icon="file-code" href="https://raw.githubusercontent.com/amloktech/docs/main/downloads/verify-webhook.mjs">Verify raw-body HMAC signatures using built-in Node.js crypto.</Card>
  <Card title="Python webhook verifier" icon="file-code" href="https://raw.githubusercontent.com/amloktech/docs/main/downloads/verify_webhook.py">Verify the same signature format using the Python standard library.</Card>
</CardGroup>

The webhook helpers link to the maintained source files for this reference. Save the Node.js helper as `verify-webhook.mjs` and the Python helper as `verify_webhook.py`.

## Import the Postman collection

1. Import the downloaded JSON file.
2. Set `base_url` to your institution-issued environment URL. The exported `base_url` value is empty so you can configure the appropriate environment.
3. Store `api_key` locally in a protected environment or vault. The exported collection contains no credential.
4. Set `idempotency_key` once for one intended POST action. Use a new value for a new action and preserve it for retries of the same action.
5. Replace synthetic resource IDs and configure the current `record_etag` before a PATCH.
6. Select a local file before trying the multipart upload request.

Saved responses are examples, not captured production traffic. Do not run every POST as a bulk collection against production: some routes initiate processing or change a monitoring configuration.

## Language examples

Endpoint pages provide cURL, Python with `requests`, and Node.js using `fetch`. The examples use a 30-second client timeout and reject unexpected redirects. They are integration examples, not official AMLOK SDK packages.

The webhook helpers have no third-party runtime dependency. They verify signatures and envelope basics only; add durable inbox processing, tenant association, replay handling, and operational monitoring as described in the [webhook guide](/api-reference/webhooks).

## Contract validation

The reference has been checked for OpenAPI structure and generated request/response example validity against JSON Schema. Language samples have been syntax-checked, and both signature helpers have been tested using synthetic signed events, altered bodies, expired/future timestamps, and malformed headers.

Validate your integration with your enabled providers, environment settings, and representative test data before processing live requests.
''')

write('onboarding','Integration onboarding','Configure your institution, environments, access, and operational settings.', '''
Use this checklist to configure an integration with **AMLOK API 1.4.2**. Your AMLOK contact supplies the settings and access appropriate to your agreement.

## Configure your environment

| Area | Configuration |
| --- | --- |
| Environments | Production and sandbox origins, one workspace per API key, institution tenant, test-data policy, and network controls. |
| Credit reporting | Authorized access to credit balances, usage, statements and exports. The portal manages card/bank funding, top-up settings and cancellation. Each key belongs to one workspace. Its shared balance has a CAD 200.00 default auto-pay trigger and CAD 500.00 minimum top-up; requests can continue below the trigger while available credits cover the cost; enterprise clients can also use their account manager. |
| API keys | Issuance, expiry, rotation, revocation, scopes, and administrator access. |
| Provider capabilities | Enabled products, resources, markets, account permissions, and field coverage. |
| Limits | Request quotas, burst and concurrency budgets, job limits, and upload limits. |
| Support | Support channel, incident contacts, escalation, and service commitments. |
| Webhooks | Destination, event subscriptions, signing secret, replay retention, and delivery monitoring. |
| Documents | Allowed file types, size and page limits, storage location, and signed-link expiry. |
| Evidence and review | Read frozen input manifests and monitoring baselines through the API. Configure authorized reviewers and assessment workflows during onboarding. |
| Data handling | Retention, residency, legal holds, deletion, and permitted purposes. |

## Connect and verify

1. Store the environment URL and API key in your server-side configuration.
2. Grant the smallest set of scopes required by your workflow.
3. Follow the [quickstart](/api-reference/quickstart) using your environment's identifiers.
4. Validate response handling, pagination, and missing-data rules with representative records.
5. Exercise retries, idempotency, concurrency conflicts, asynchronous outcomes, and webhook verification.
6. Configure monitoring and the agreed support and incident channels.

Keep sandbox and production credentials and data separate. Confirm source permissions and your institution's approval before enabling consequential actions.

## Keep your integration current

Pin the [OpenAPI reference](/openapi/amlok-v1.json) used by your client. Review schema changes and rerun integration checks when adopting a new version or enabling a provider. See [versioning](/api-reference/versioning) and [Security & Compliance](/security/overview).
''')
from enterprise_guides import generate
generate()
from integration_guides import generate as generate_integration
generate_integration()
from sandbox_journeys import generate as generate_journeys
generate_journeys()
print('Wrote API guides and enterprise contract guides')

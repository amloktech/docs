"""Integration instructions and backend acceptance requirements from the same contract."""
import json
import re
from pathlib import Path
from readiness_contract import PROFILE, EVENT_RESOURCES
from current_api_guides import page
from product_api_review import ROOT


def write_guides(spec,f,index):
 descriptions={
  'integration-hub':'Embed the Integrations Hub, obtain borrower consent, validate session messages and connect authorized sources for underwriting and ongoing monitoring.',
  'deal-inputs':'Send immutable funded-deal snapshots to Signal, validate balances and terms, handle competing updates and retrieve the inputs used by each evaluation.',
  'operating-profile':'Discover upload sizes, supported file types, request budgets, polling intervals and resource expiry through your environment configuration.',
  'processing-lifecycle':'Handle Insights and Signal states, resolve missing inputs and authorization, recover accepted requests and reconcile completion or failure.',
  'sandbox-journeys':'Test underwriting, monitoring, consent recovery, document requests and billing with deterministic Sandbox scenarios and synthetic borrower data.',
  'event-catalog':'Find every AMLOK event type, its referenced resource and required permission, then reconcile versions and recover missed webhook notifications.'
 }
 def api(name,title,body):
  page('api-reference/'+name,title,descriptions[name],body)
 def append(name,text):
  p=ROOT/('api-reference/'+name+'.mdx');p.write_text(p.read_text().rstrip()+'\n\n'+text.strip()+'\n')
 def replace(name,old,new):
  p=ROOT/('api-reference/'+name+'.mdx');s=p.read_text();assert old in s,(name,old);p.write_text(s.replace(old,new))
 endpoints={x['id']:'/'+x['page'] for x in index}
 api('integration-hub','Embed the Integrations Hub','''
AMLOK's Integrations Hub collects borrower authorization and connects sources selected by the institution in the console. Your backend creates a borrower-bound session; your frontend displays its short-lived launch URL. AMLOK performs collection and normalization. The borrower selects one provider per category step. Selecting another provider replaces that step's previous choice; a session can include one provider from each of several categories.

## Publish and discover a Hub

In **Embeddings**, publish the integrations, branding and requested consent purposes. Approve exact HTTPS embedding origins and return URLs. AMLOK rejects wildcard origins, embedded URL credentials, fragments and unregistered destinations. Sandbox alone may permit explicitly registered loopback HTTP origins for development; Live requires HTTPS.

Read `GET /v1/configuration`. Each embedding_versions entry lists its ID, integrations, consent purposes, allowed origins, return URLs and hub_origin. Configure the customer-facing logo, colors, typography, controls and text in the [Console appearance panel](/console/embeddings#customize-the-appearance). The saved design belongs to that version. Existing sessions retain their version's integrations and appearance, including when a borrower returns to an in-progress session. Create new sessions with the new version ID to use a saved update. Use a version whose integration set and purposes fit the borrower flow.

## Create the session on your server

Authenticate your own customer and authorize their relationship to the borrower before calling `POST /v1/embedding-sessions`. Keep the API key on the server. Send borrower_id, embedding_version_id, purpose, return_url, consent_purposes and, for an iframe, embed_origin.

- Request credit_assessment for underwriting.
- Request continuous_monitoring for post-funding monitoring.
- Request both if the borrower is explicitly consenting to both. The Hub presents both purposes; neither implies the other.
- Requested purposes must be a subset of the published Hub's allowed purposes. Otherwise return 422 consent_purpose_missing.
- For reauthorization, use purpose reauthorize and the affected connection_id. Consent can be renewed only with a new affirmative borrower authorization.

The session expires at expires_at. Repeating the same idempotency key returns the same session, including its original expiry. After expiration create a new session with a fresh command identity. An abandoned session is never evidence of consent.

## Display the borrower experience

Use launch_url for either full-page navigation or an iframe. A session without embed_origin is redirect-only. The Hub uses a frame-ancestors policy allowing the approved parent origin; API endpoints do not enable browser CORS for secret keys. Allow the configured hub_origin in your application's frame-src policy.

```html
<iframe id="amlok-hub" title="Connect your financial accounts"
  sandbox="allow-scripts allow-forms allow-same-origin allow-popups allow-popups-to-escape-sandbox"
  referrerpolicy="no-referrer" style="width:100%;height:720px;border:0"></iframe>
```

Set the iframe source from your own authenticated backend response. Never put an API key into HTML. Providers that require a new window open it only after a borrower action. If browser restrictions prevent completion, offer a borrower-initiated full-page link to the same unexpired launch URL. The Hub persists the session's confirmed connections across these presentations.

The [browser example](/downloads/hub-embed.js) uses the typed HubMessage contract. Every message contains protocol_version, event_id, session_id and type. Types are amlok.hub.ready, amlok.hub.completed, amlok.hub.cancelled, amlok.hub.expired and amlok.hub.failed. The Hub sends messages only to the exact embed_origin, never `*`.

Validate event.origin against the configured hub_origin, event.source against the iframe's contentWindow, and session_id against the session your backend created. Deduplicate event_id. No message includes provider tokens, financial data or proof of consent. Your backend retrieves the session before trusting a terminal state.

For full-page presentation, terminal states return the browser to the approved return_url with amlok_session_id and amlok_state added as query parameters. These reserved parameters cannot be supplied in the configured URL. Treat them as untrusted hints; your authenticated backend verifies session ownership and retrieves its state. Cancelled and expired sessions require a new session. Already confirmed consent/connections are not revoked by closing the window.

## Confirm readiness

The completed state means the borrower finished the Hub journey, not that all sources have finished ingestion. Retrieve session.connection_ids and consent_ids. A connection exposes authorization status separately from data_status, freshness and coverage. Wait for required inputs or let an origination remain collecting; never interpret a stale or partial source as a clean result.

An underwriting-only connection cannot enroll in Signal. Create a new authorization session requesting continuous_monitoring, then use the resulting connection IDs. Reauthorization preserves the logical connection ID when the same source account is reconnected. A different source creates a different connection.

## Resolve a resource requirement

When an origination or monitor returns requires_action, use its typed requirements. Create a Hub session with that resource's origination_id or monitor_id and requirement_id. These IDs must match the borrower and an open connect/reauthorize requirement. On successful authorization, AMLOK atomically associates the connection, resolves that requirement, increments the resource version and schedules permitted continuation. The immutable submitted_request and historical results remain unchanged.

For an independently connected source on an existing monitor, replace connection_ids using the monitor's If-Match configuration update. This change is prospective. Hub configuration stays in the console; the API does not expose provider job orchestration.
''')
 api('deal-inputs','Send funded-deal updates','''
Signal needs the institution's current exposure as well as the borrower's integration data. Use immutable deal snapshots to submit balance, maturity, terms and lender-reported performance after enrollment. AMLOK does not service loans or initiate borrower payments.

## Initial enrollment and portfolio onboarding

`POST /v1/monitors` captures the initial deal as snapshot sequence 1 and returns latest_deal_snapshot_id. It validates borrower ownership, currency, funded amount, outstanding amount, policy, connection consent and baseline before accepting. funded_at cannot be in the future; amounts are nonnegative decimal strings and currencies must agree.

For an Insights-funded deal, pass baseline.risk_package_id. For an existing portfolio deal, pass baseline.portfolio with lending_product_version_id, application (or null when unavailable) and document_ids. AMLOK prepares the Signal baseline from those inputs and the authorized sources. Portfolio preparation is included in Signal; it does not purchase a separate Insights assessment. Missing evidence remains explicit in the baseline.

## Append a new snapshot

1. Retrieve the monitor and its latest_deal_snapshot_id.
2. Submit `POST /v1/monitors/{id}/deal-snapshots` with previous_snapshot_id, effective_at, the complete deal and performance (or null if unknown).
3. Save the returned immutable snapshot ID. Read its sequence and received_at to confirm acceptance.

previous_snapshot_id is compared atomically to the monitor's current pointer. A stale value returns 409 deal_snapshot_conflict without accepting or charging anything. Fetch the latest state and review the intended input before submitting a new command. Retrying an already accepted command with its original idempotency key returns its original snapshot even if the pointer has subsequently advanced.

The institution_reference, funded_at, funded_amount and currency identify the enrolled facility and cannot change. Submit a separate monitor for a refinanced or different facility. Outstanding balance, maturity, repayment frequency and referenced terms can change in a new snapshot. effective_at must be later than the previous snapshot and no later than server acceptance. Backdated corrections do not rewrite existing results; submit the corrected current state with a new as-of time and retain earlier records for audit.

The accepted write stores the snapshot, advances the monitor pointer/version and emits deal_snapshot.created atomically. Future evaluations capture that exact pointer at their start. A run already in progress retains its original snapshot. Each monitoring run and Signal risk package exposes deal_snapshot_id, and the package freezes its supporting evidence.

`GET /v1/monitors/{id}/deal-snapshots` lists versions by sequence ascending. `GET /v1/deal-snapshots/{id}` retrieves one exact version. There is no update/delete operation for snapshots. Stopped monitors reject new inputs with 409 invalid_state. Paused and action-required monitors may accept current inputs without starting processing until their blocking state resolves.

A paid_off performance status records lender information; explicitly stop monitoring with PATCH when monitoring should end. Snapshots and included change-driven reassessment add no Insights charge. Normal Signal borrower/month charging still applies.

## Currency and performance validation

All deal and performance amounts use the facility currency. days_past_due is a nonnegative integer. current and paid_off require zero days_past_due and zero amount_past_due; paid_off additionally requires zero outstanding_amount. Do not use zero to represent unknown performance: send performance null. A maturity amendment must still be compatible with the selected lending product. Unsupported amendments fail with field-specific 422 validation_error.
''')
 api('operating-profile','Discover operating limits','''
Read configuration.operational_profile to discover the effective limits for your workspace and environment. The response includes a profile ID and version, supported file types, request budgets and resource lifetimes. Use these values when configuring uploads, polling and recovery.

| Setting | Behavior |
| --- | --- |
| max_json_bytes | Reject larger JSON bodies with 413 before command acceptance |
| max_upload_bytes / max_document_pages | Reject oversized uploads with 413; inspection rejects over-limit pages without treating the file as available |
| allowed_document_mime_types / document_types | Validate detected content and declared type; do not trust a filename extension |
| session_ttl_seconds / download_ttl_seconds | Use the actual expires_at returned for each issued capability |
| snapshot_ttl_seconds | Stable collection and billing snapshot lifetime; expose expires_at or snapshot_expires_at |
| data_feed_retention_seconds / event_retention_seconds | Recover before the returned resume_expires_at; expired cursors return 410 |
| export_retention_seconds | Download a ready export before its retention expiry; do not assume URLs last as long as export metadata |
| poll_min_interval_seconds / poll_max_interval_seconds | Poll no faster than the minimum; back off with jitter up to the maximum |
| webhook_timeout_seconds / webhook_max_body_bytes | Receiver must durably accept and respond inside the deadline; oversized event production is forbidden |
| webhook_rotation_overlap_seconds | Old and new secrets verify during this overlap; rotate before disabling the previous secret |
| rate_limits | Rolling request budget shared across keys in the workspace/environment for reads, commands and uploads |

GETs use the reads budget, uploadDocument uses uploads, and other POST/PATCH requests use commands. A 429 carries Retry-After in whole seconds, which overrides local polling schedules. A 503 may include it as well. Caller timeouts do not cancel accepted work. Keep total waiting bounded in your application and hand unresolved requests to durable background reconciliation.

The [example profile](/downloads/development-profile.json) provides synthetic values for local tests. Use the profile returned by your environment for its effective limits. Source freshness and coverage remain provider-specific; polling frequency does not make sources refresh faster.

## Changes and expiration

Profiles apply prospectively. Existing issued capabilities and cursors keep their disclosed expiry unless authorization is revoked or the workspace closes. Save the profile ID/version with integration diagnostics. Key revocation and consent withdrawal take priority over unexpired links or retained snapshots.

Snapshots bind workspace, environment, caller authorization and filters. Cursor chains cannot change filters. Empty change/event batches still return a resumable cursor and expiry. On 410, establish a new checkpoint and reconcile a fresh complete snapshot, including deletions; never silently discard the gap.

## Upload inspection

The example profile accepts PDF, PNG, JPEG and WebP. Check allowed_document_mime_types for the types supported by your environment. Password-protected/encrypted files and archives are not accepted by this contract. Detected type mismatch returns 415 unsupported_media_type. If discovered after asynchronous acceptance, the document becomes rejected with failure.code document_rejected and a safe explanation. Infected, corrupt, empty or unreadable files never become available. Re-upload a corrected file as a new immutable record.

Client-side checks improve feedback; AMLOK validates size, content type and authorization for every upload. Uploads are not fetched from arbitrary customer URLs. Downloads use short-lived HTTPS capabilities with MIME type and SHA-256; verify integrity after transfer and avoid logging URLs.
''')
 api('processing-lifecycle','Processing states and recovery','''
AMLOK accepts long-running product commands with 202. Persist the returned ID before polling or processing events. HTTP acceptance does not mean authorization, data collection, underwriting or charging has completed.

## Insights origination

| State | Meaning | Permitted continuation |
| --- | --- | --- |
| accepted | Command and recovery receipt committed | AMLOK begins collecting |
| collecting | Waiting for permitted input processing | AMLOK advances to processing or requires_action |
| requires_action | One or more typed requirements are open | Resolve requirements through Hub or new document uploads |
| processing | Evaluation uses the captured source/input versions | AMLOK completes, waits for credits, requires action or fails |
| waiting_for_credits | Accepted work cannot publish an unfunded output | Funding posts through the console; AMLOK resumes automatically |
| completed | Immutable package and any Insights debit published atomically | Terminal; retrieve package/evidence |
| failed | Terminal failure, with structured failure | Reconcile failure; a fresh assessment is a deliberate new command |
| cancelled | Workspace cancellation ended unfinished work | Terminal; no further processing or debit |

No public operation overwrites a completed application. To correct institution application data, submit a new origination. Idempotent retry never means a new underwriting. An internal stage retry does not add another charge.

## Typed requirements

requirements is nonempty exactly when a product resource is requires_action. IDs remain stable while the same requirement is open. Resolving one requirement does not imply others are resolved. A later recurrence gets a new requirement ID.

| action | Required details | Resolution |
| --- | --- | --- |
| connect_source | integration_id, consent_purposes | Create a connect session bound to resource + requirement |
| reauthorize_source | connection_id, consent_purposes | Create a reauthorize session bound to resource + requirement |
| upload_document | document_type, accepted_mime_types | Upload with borrower_id, origination_id and requirement_id |
| contact_support | code and human explanation | Give support the resource ID and request ID; never credentials |

Document requirements apply to originations. A monitor needing a different term document receives it through a new deal snapshot; the monitor must not emit an upload_document requirement that has no upload resolution route. Validation errors use JSON-pointer field paths. Do not branch on message text.

## Signal monitor

initializing captures the first snapshot and prepares a baseline. It becomes active, requires_action, waiting_for_credits or failed. active schedules configured evaluations. paused suspends new work by institution configuration. stopped is terminal and rejects future changes or lender snapshot submissions. Work already running when paused or stopped must not publish a new package after the state change; keep its skipped/cancelled explanation without a new usage charge.

A monitor exposes current connection_ids, requirements, failure, latest_deal_snapshot_id, latest_package_id and next_evaluation_at. failure is non-null exactly when failed. A source or purpose problem produces a typed requirement; insufficient credits produces waiting_for_credits, not a fabricated source error.

Use PATCH with If-Match for future policy, cadence, connection set or active/paused/stopped state. Active is accepted only after server validation of consent, required inputs and funding; otherwise return 409 invalid_state with the unresolved reason and retain state. failed cannot be resumed: correct the cause and enroll a new monitor. Unchanged identical configuration does not increment version or emit an event.

Resolving a requirement resumes an eligible monitor automatically. Posting credits resumes only the current period; no missed-period backcharges or synthetic historical runs. Explicitly paused monitors stay paused when credits or consent change. An institution must explicitly set active to resume. Consent revocation during evaluation prevents publication of restricted results.

## Monitoring runs and exports

A run freezes deal_snapshot_id, policy and authorized source/evidence versions when evaluation starts. processing becomes completed, partial, failed or skipped. Terminal runs do not change. Partial results describe coverage and limitations; failed/skipped runs have no newly published risk package. An alert is a derived risk condition, not a run error. Resolution requires new comparable evidence.

An export moves queued to processing to completed or failed. completed means the file is ready and emits export.ready. Each read/download rechecks source permissions. The source snapshot is pinned at acceptance, so its later cursor expiry does not truncate an already accepted export. Export metadata includes availability expiry; download capability expiry is separate. Failed exports carry a structured failure. Export/replay commands never rerun underwriting.
''')
 api('sandbox-journeys','Run reproducible Sandbox scenarios','''
AMLOK Sandbox provides deterministic synthetic scenarios to validate your integration without real borrower credentials or funds. Each scenario covers a specific result, recovery path or billing event.

## Provision and run

1. Obtain a Sandbox key and read configuration.sandbox. Live returns null.
2. Publish a Hub containing the returned test_integration_id and both consent purposes. Register your local or test application's return URL and embedding origin.
3. Create the borrower normally. Use X-AMLOK-Sandbox-Scenario on the origination, monitor or export command whose outcome you want to simulate. The endpoint lists supported values; the identifier must also appear in configuration.sandbox.scenario_ids. Omit the header for happy_path. Unknown or inapplicable scenarios return 422 scenario_not_available; unsupported operations return 400 validation_error; Live returns 422 sandbox_only before command acceptance.
4. Launch the Hub. The synthetic integration offers a clearly labeled **Connect test institution** action; it needs no bank username, password or OTP. Explicit acceptance records test consent and connections.
5. Run the [downloadable journey](/api-reference/runnable-example). It sends the selected scenario on the affected command. A scenario header does not persist on the borrower or affect later commands automatically. For full business, monitoring and payment fixtures, use the named Sandbox scenario catalog.

Each run uses a new unique client_reference and command prefix. Old records remain immutable. Reset a scenario by creating a new synthetic borrower; no production-style reset/delete API is introduced.

| Scenario | Trigger and expected result |
| --- | --- |
| happy_path | Complete test consent, submit a valid origination; completed package, evidence and linked Insights usage appear |
| source_reauthorization | First origination returns requires_action with reauthorize_source; a requirement-bound Hub session resolves it and the same origination completes |
| document_required | First origination returns upload_document for financial_statement; upload a readable PDF with its requirement ID; the same origination completes |
| missing_financial_input | Complete package has an unavailable dscr metric with null value and explicit reason; policy result is unavailable and recommendation review_required |
| restricted_report | Package includes restricted report metadata with explanation; download is denied with 403 and no capability URL |
| provider_failure | First evaluation terminates failed with processing_failed; no package or Insights debit is published |
| insufficient_credits | First completion attempt waits for credits; console **Sandbox funding** adds a simulated top-up, then that same request completes with one debit |
| monitoring_alert | First Signal evaluation establishes baseline; the next configured evaluation publishes an adverse fixture and alert with previous/current values and evidence |
| payment_return | Console **Sandbox funding** posts a simulated payment, then **Simulate return** creates a linked reversal; earlier wallet entries remain unchanged |
| export_failure | The first export for that borrower's package fails with processing_failed; a new explicit export command succeeds without another product charge |

Sandbox funding controls are labeled as simulations, apply only to the selected Sandbox environment and require Owner authority. They do not invoke a payment processor. Sandbox prices and balances are test fixtures. Live rejects Sandbox headers and controls before creating resources or moving funds.

## Transport and security tests

- Simulate a client-side timeout after acceptance, then recover via request receipt and retry the original key. Assert one resource and one charge.
- Deliver the same signed event twice and deliver newer/older resource versions out of order. Assert one durable event inbox entry and no state rollback.
- Replay via the normal event replay endpoint. Assert the event ID is unchanged and signature timestamp is fresh.
- Use two independently provisioned workspaces. Cross-workspace IDs, snapshots, cursors, downloads and session associations must fail without leaking resource contents.
- Use the returned profile to test oversized documents, unsupported MIME types, stale If-Match, expired cursors and invalid purpose scopes.
- Advance only the Sandbox service's test clock through its authorized console tooling to force configured expiry and scheduled evaluations. Production clocks and real provider data are never affected.

The [scenario manifest](/downloads/sandbox-scenarios.json) supplies stable IDs and expected states for automated integration tests. Use the scenario IDs and test integration returned by your Sandbox configuration.
''')
 # Generate the only event catalog and replace the stale Data Model vocabulary.
 rows=[]
 for event,(resource,operation,scope) in EVENT_RESOURCES.items():
  rows.append('| `'+event+'` | `'+resource+'` | ['+operation+']('+endpoints[operation]+') | `'+scope+'` |')
 api('event-catalog','Public event catalog','''
AMLOK emits the same Event envelope through signed webhooks and the durable event feed. This is the complete public event vocabulary. Internal provider jobs, workflows and normalization stages are not separate public events.

| Event | resource_type | Retrieve details | Source permission |
| --- | --- | --- | --- |
'''+ '\n'.join(rows)+'''

Event reads and replay also require events access. Source permission applies in addition to that access; billing requires current Owner authority. data.updated can be consumed with data:read and a Data API checkpoint; reading connection details separately requires connections:read. Export events also retain the source permissions used by that export. Destinations cannot subscribe around these authorization checks.

## Ordering and versions

Every event carries id, type, occurred_at, resource_type, resource_id, resource_version, nullable borrower_id and environment. Event.resource_version refers to the resource in this table. Every mutable referenced representation exposes record_version; immutable packages, deal snapshots and wallet transactions always use 1. Version numbers are comparable only for the same resource ID/type.

Deduplicate event IDs. Fetch the current resource, not an assumed event-embedded payload. A fetched newer version is expected; a fetched older version must be retried and must not replace newer local state. Billing snapshot reads intentionally represent an older as-of time; use an unpinned payment read when reconciling a new payment event. Event arrival order does not define wallet posting order; use transaction.sequence.

A resource update and its event are recorded atomically. Several events may refer to one state change; for example origination.completed and risk_package.created. Their delivery order is not guaranteed. A completed monitoring event includes both completed and partial terminal runs; fetch status and limitations. Failed/skipped runs use monitoring_run.failed with a structured reason.

connection.status_changed also covers collection-state/freshness changes and consent withdrawal. Export readiness, document status changes, payment state changes and snapshot acceptance increment or reference the correct resource version. Events contain no provider credentials, financial records or download URLs.

## Recovery

Capture an events checkpoint with start=now before collection bootstrap, then consume the saved resume_cursor after the snapshots. Process and checkpoint batches atomically. Replaying a webhook preserves the event ID and uses a fresh signature; it never reruns product work or changes a charge. See [webhook verification](/api-reference/webhooks) and [delivery recovery](/api-reference/webhook-operations).
''')
 page('data-model/events','Events and normalized data changes','Use the single public AMLOK event catalog and Data API change feed to reconcile resource state and exact normalized record versions.','''
Use the [public event catalog](/api-reference/event-catalog) for webhook subscriptions and event consumers. Its event names and resource mappings are generated from the same contract as the API reference and console Data Lookup.

Normalized financial data changes use data.updated as a notification hint and [the Data API change feed](/api-reference/data-access) for exact version discovery. Consume upsert, removed and access_changed records from your checkpoint. Internal provider synchronization and enrichment stages are not customer commands or separate public webhook names.

A lender submits new loan/exposure information through [deal snapshots](/api-reference/deal-inputs). Signal evaluates those inputs and the authorized integration data, then publishes versioned results and alerts.
''')
 # Reconcile existing pages and count-sensitive generated prose.
 for directory in ['api-reference','overview']:
  for p in (ROOT/directory).glob('*.mdx'):
   s=p.read_text().replace('54 operations','57 operations').replace('54 public operations','57 public operations').replace('all 54','all 57').replace('54-operation','57-operation')
   s=s.replace('evidence_set_id supplied by a risk package','evidence_set.id supplied by a risk package')
   p.write_text(s)
 p=ROOT/'api-reference/monitoring-design.mdx';s=p.read_text();s=re.sub(r'The baseline is either.*?Do not send both\.', 'The baseline is either an existing risk-package ID or typed baseline.portfolio inputs with lending_product_version_id, nullable application and document_ids. Do not send both.',s)
 s+='\n\nCurrent lender balance and terms arrive through [immutable deal snapshots](/api-reference/deal-inputs). Read [processing states and recovery](/api-reference/processing-lifecycle) for typed requirements, consent renewal and funding resumption.\n';p.write_text(s)
 p=ROOT/'api-reference/evidence-traceability.mdx';s=p.read_text().replace('risk package supplies evidence_set_id','risk package supplies evidence_set.id').replace('Risk packages supply evidence_set_id','Risk packages supply evidence_set.id').replace('Risk packages and monitoring runs supply `evidence_set_id`', 'Risk packages supply `evidence_set.id`; monitoring runs supply `evidence_set_id`');p.write_text(s)
 append('overview','''<Tip>Follow the [runnable integration example](/api-reference/runnable-example) for a complete business or consumer journey, from borrower authorization to underwriting, monitoring and billing reconciliation.</Tip>''')
 append('documents','''## Validation and rejection

Read allowed_document_mime_types, document_types, max_upload_bytes and max_document_pages from configuration.operational_profile. [Operating limits](/api-reference/operating-profile) defines 413/415 behavior, asynchronous rejection, encrypted-file handling and integrity checks. Rejected documents expose structured failure; available documents have failure null. Every document exposes record_version for event reconciliation.''')
 append('configuration','''## Runtime discovery

embedding_versions exposes each published Hub's allowed origins, return URLs, integrations and consent purposes. operational_profile supplies required limits and lifetimes. sandbox is null in Live; in Sandbox it exposes deterministic scenario IDs and the synthetic integration ID. Read the [operating profile guide](/api-reference/operating-profile) before implementing uploads, polling or recovery.''')
 append('errors','''## Additional defined errors

| HTTP | Code | Action |
| --- | --- | --- |
| 422 | sandbox_only | Use the Sandbox environment for simulation controls; no command was accepted |
| 409 | deal_snapshot_conflict | Read the latest monitor snapshot and review the new input |
| 413 | payload_too_large | Reduce to the discovered size limit; the command was not accepted |
| 415 | unsupported_media_type | Submit supported detected file content or JSON media type |
| 422 | consent_purpose_missing | Obtain the explicit required borrower purpose through a permitted Hub version |
| 422 | scenario_not_available | Use a scenario returned by Sandbox configuration |

Asynchronous document_rejected and processing_failed appear in resource.failure; they are not successful business outcomes. Error.field is a JSON pointer into the submitted request (or null). Safe messages never contain provider credentials or full source payloads. 429 and 503 are retryable; validation, authorization, stale-state and terminal processing failures require corrective action.''')
 append('rate-limits','''Read configuration.operational_profile.rate_limits for effective shared workspace/environment budgets and the polling interval fields. The [profile guide](/api-reference/operating-profile) defines grouping, rolling windows and timeout handling. Use the returned values for your environment rather than the example profile.''')
 append('pagination','''Every snapshot page returns expires_at. Data-change and event pages return resume_expires_at, including empty pages. The billing summary returns snapshot_expires_at. Use these timestamps to schedule reconciliation before the effective retention window closes.''')
 append('downloads','''## Integration examples and test resources

- [Runnable client journey](/downloads/amlok-journey.mjs)
- [Validated browser embedding helper](/downloads/hub-embed.js)
- [Synthetic journey inputs](/downloads/journey-inputs.json)
- [Development operating profile](/downloads/development-profile.json)
- [Sandbox scenario manifest](/downloads/sandbox-scenarios.json)
- [Integration checklist](/api-reference/integration-acceptance)

Use these resources with the [runnable walkthrough](/api-reference/runnable-example) to connect your application and test recovery paths.''')
 nav=json.loads((ROOT/'docs.json').read_text());tab=next(t for t in nav['navigation']['tabs'] if t['tab'].lower()=='api reference')
 tab['groups'][0]['pages'].insert(2,'api-reference/runnable-example')
 tab['groups'][1]['pages'].insert(5,'api-reference/deal-inputs')
 tab['groups'][3]['pages']+=['api-reference/operating-profile','api-reference/integration-acceptance']
 for source in ['/api-reference/implementation-status','/api-reference/api-review','/api-reference/versioning','/api-reference/contract-changelog']:
  redirects=nav.setdefault('redirects',[])
  redirects[:]=[r for r in redirects if r['source']!=source]
  redirects.append({'source':source,'destination':'/api-reference/overview'})
  (ROOT/(source.lstrip('/')+'.mdx')).unlink(missing_ok=True)
 (ROOT/'docs.json').write_text(json.dumps(nav,indent=2)+'\n')
 (ROOT/'downloads/development-profile.json').write_text(json.dumps(PROFILE,indent=2)+'\n')
 scenarios={name:{'id':name,'environment':'sandbox','selected_on':'processing_command','header':'X-AMLOK-Sandbox-Scenario','expected':value} for name,value in {
  'happy_path':{'origination':'completed','insights_debits':1},'source_reauthorization':{'initial_origination':'requires_action','action':'reauthorize_source','after_resolution':'completed'},'document_required':{'initial_origination':'requires_action','action':'upload_document','document_type':'financial_statement','after_resolution':'completed'},'missing_financial_input':{'metric':'dscr','value':None,'recommendation':'review_required'},'restricted_report':{'evidence_access':'restricted','download_status':403},'provider_failure':{'origination':'failed','failure_code':'processing_failed','insights_debits':0},'insufficient_credits':{'initial_origination':'waiting_for_credits','after_simulated_funding':'completed','insights_debits':1},'monitoring_alert':{'subsequent_event':'alert.created'},'payment_return':{'historical_entries_unchanged':True,'new_linked_reversal':True},'export_failure':{'first_export':'failed','explicit_new_export':'ready'},}.items()}
 (ROOT/'downloads/sandbox-scenarios.json').write_text(json.dumps({'contract_version':'1.0.0','scenarios':list(scenarios.values())},indent=2)+'\n')
 inputs={k:deepcopy_value(f[k]) for k in ['CreateBorrower','LendingProductInput','RiskPolicyInput','CreateOrigination','CreateMonitor','DealSnapshotInput']}
 (ROOT/'downloads/journey-inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
 consumer=deepcopy_value(inputs)
 consumer['CreateBorrower']={'type':'person','person':{'given_name':'Synthetic','family_name':'Borrower','residence_country':'CA','client_reference':'CONSUMER-SYNTHETIC'}}
 consumer['LendingProductInput'].update(borrower_type='person',external_id='consumer-term',name='Synthetic consumer term loan')
 consumer['RiskPolicyInput'].update(borrower_type='person',external_id='consumer-policy',name='Synthetic consumer policy; not a recommended threshold',rules=[{'id':'dti-test','dimension_key':'debt_to_income','calculation_version':'amlok-debt_to_income-1','operator':'lte','threshold':'0.40','unit':'ratio','on_missing':'review','on_fail':'review'}])
 consumer['CreateOrigination']['application'].update(application_schema_id='consumer_app_schema_synthetic',declared_data={'gross_monthly_income':'6000.00','monthly_debt_payments':'1200.00'})
 (ROOT/'downloads/consumer-journey-inputs.json').write_text(json.dumps(consumer,indent=2)+'\n')



def deepcopy_value(v):
 return json.loads(json.dumps(v))

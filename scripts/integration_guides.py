"""Publish the integration contract runbooks and align existing guides."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent.parent

def write(name,title,description,body):
    (ROOT/'api-reference'/f'{name}.mdx').write_text('---\ntitle: '+json.dumps(title)+'\ndescription: '+json.dumps(description)+'\n---\n\n'+body.strip()+'\n')

def generate():
    write('connection-recovery','Connection authorization and recovery','Connect and renew provider access while preserving the original connection.',r'''
## Start an authorized connection

1. Read `GET /v1/providers`. Choose a product from that provider's `products[].id`; its `resources`, `consent_scopes` and `purposes` describe what it authorizes. A resource such as `bank_transaction` is not a product ID.
2. Record the borrower's valid consent. Create an unpredictable browser-session `state` with at least 32 characters. Store it server-side with the intended business and registered HTTPS return URL.
3. [Create the connection](/api-reference/endpoints/platform/create-connection) with that consent, product IDs, `redirect_uri` and `state`. Save its ID before opening `action.url`.
4. On return, validate `state`, its session binding and the expected `connection_id`, and consume that state once. Return parameters are `connection_id`, `state`, and `result` (`completed`, `cancelled`, or `failed`); a failed return also has a sanitized `error_code`.
5. Retrieve the connection from your server. A browser return does not prove authorization succeeded. Wait for `active` or inspect `error_code`; `connection.updated` can notify your server independently.

Never put API keys, source records or provider tokens in the browser return URL. Register return URLs through the client portal; the account manager provides portal access information.

## Renew access

For a `reauth_required` connection, or an expired/abandoned authorization action on a pending connection, call [Renew connection authorization](/api-reference/endpoints/platform/renew-connection-authorization):

```json
{
  "consent_id": "con_current",
  "redirect_uri": "https://client.example.com/connected",
  "state": "replace-with-cryptographically-random-session-state"
}
```

Use `POST /v1/connections/{id}/authorization` with the existing connection ID. Obtain and record fresh borrower consent first when the previous consent is expired or revoked. The replacement consent must cover the same subject, products and purposes. AMLOK updates the connection's consent reference only after successful authorization.

The connection ID, previously retrieved records and synchronization lineage remain stable. A replacement action invalidates the previous unused action. An identical idempotent retry returns the same action and original expiry. To replace an expired link intentionally, use a new key and fresh state. After the connection is active, synchronize and inspect actual coverage; authorization alone does not fill a data gap.

`revoked` or `disconnected` connections cannot be reopened. Obtain new consent and create a new connection; preserve the old records as evidence under the configured retention policy. Do not merge account identities or deduplicate cross-connection data using names alone.
''')
    write('related-person-verification','Verify business owners and related people','Include person KYC within the existing business underwriting or monitoring product.',r'''
The business remains the primary subject for its Insights underwriting or Signal monitoring period. An owner, director, guarantor or authorized signatory can have a person-level KYC check within that same product.

1. Create or retrieve the business and person in the same workspace. Obtain the required authorization and upload supporting evidence.
2. [Create a subject association](/api-reference/endpoints/identity/create-subject-association) using `business_id`, `person_id`, `role` and `evidence_document_ids`.
3. Poll the association until `active`. AMLOK validates permitted use and evidence; a record can remain `pending` for platform review or become `rejected` with a `reason_code`. Contact your account manager for unresolved review. A declared association is not a verified legal ownership determination.
4. Start or retrieve the unfinished business underwriting, or use its active paid Signal period. A full underwriting can wait for required KYC evidence; it does not require the owner check to be completed before the parent run exists.
5. Request person KYC with the active association in its processing context:

```json
{
  "subject_id": "per_owner",
  "verification_type": "kyc",
  "workflow_version": "kyc-ca-v1",
  "processing_context": {
    "product": "insights",
    "workflow_run_id": "wfr_business",
    "subject_association_id": "assoc_owner"
  }
}
```

Select the actual approved verification version from [environment configuration](/api-reference/configuration). For Signal, replace `workflow_run_id` with `monitoring_period_id` and set `product` to `signal`.

The association's person must match the verification subject and its business must match the parent subject. AMLOK validates current authorization on every attempt and records `subject_association_version` on the verification. Inactive or mismatched associations are rejected. Revocation stops unfinished related-person work without changing already completed audit evidence.

The association exception applies only to person verification. Other processing stages remain tied to their parent subject. All associated evidence and processing count toward that parent's agreed workload. The person check does not create a separate Insights charge or Signal account-month. Associations do not grant unrestricted access to the person's other data. Corrections, review and revocation are managed through the client portal; canonical verified relationships remain read-only evidence.
''')
    write('request-recovery','Recover interrupted requests','Find accepted work after a timeout without starting duplicate processing.',r'''
## Persist the intended action

Before sending a POST, persist its idempotency key, OpenAPI `operationId`, exact resolved target path, intended body and your correlation ID. Never store API credentials with that record. For example, an underwriting uses `EP147` and `/v1/workflow-runs`; a synchronization uses `EP140` and `/v1/connections/cnn_123/sync`.

Within 24 hours, retry the identical request and key after a timeout. An accepted command and its durable receipt are recorded atomically. Full response replay lasts 24 hours; the minimal receipt lasts until workspace deletion. An unchanged retry after the replay window returns `409 idempotency_result_expired` without executing again. Changed payloads or targets return `409 idempotency_conflict`.

## Find the original resource

```bash
curl --get --fail-with-body --max-time 30 \
  "${AMLOK_API_BASE_URL}/v1/request-receipts/lookup" \
  --header "Authorization: Bearer ${AMLOK_API_KEY}" \
  --header "Idempotency-Key: your-original-key" \
  --data-urlencode "operation_id=EP147" \
  --data-urlencode "target_path=/v1/workflow-runs"
```

The response identifies `resource_id`, `resource_type`, `resource_path`, `original_http_status`, `request_id` and receipt status. Retrieve the authorized relative `resource_path` with its read scope and continue polling or reconciliation. Receipt status is a record of command execution, not a replacement for the authoritative resource's current status. Lookup requires `platform:read` plus the original operation's scopes in the same workspace and environment; rotating the API key does not lose access to its receipts.

For a short-lived document/report download, the receipt points to its durable document/report parent. Generate a fresh link with a new key when the old link expires; this does not rerun paid processing. A webhook replay receipt points to the original event; match its `request_id` against delivery `replay_request_id`. A lost webhook-creation response does not make its one-time signing secret readable through lookup; rotate it through the portal.

If the resource has expired, `resource_unavailable` preserves its identity. It does not authorize a new billable request. A `404` may reflect an in-flight or never-accepted command, so it does not prove the operation never ran. Within the replay window, retry the original request; after that window, ask support to reconcile your saved key and caller correlation ID before generating a new key.

Pre-execution validation and insufficient-credit rejection create no accepted receipt. Correct the rejected request as directed; a known `402` can be retried with its original key after funding. Do not infer rejection from a timeout.

## Recover a failed workflow

`WorkflowRun.failure` is non-null for `failed` runs. It contains `code`, `message`, `retryable`, `recovery_action`, `retry_after_seconds`, `occurred_at` and `request_id`.

- `retry_same_run`: after the specified delay, call [Retry failed workflow](/api-reference/endpoints/operations/retry-failed-workflow). Save a new key for this retry action. The same run ID and evidence remain; `attempt` increments once and there is still only one eventual Insights charge.
- `correct_evidence`: inspect requirements and correct the rejected evidence through its authorized upload flow. If the run is already terminal and non-retryable, contact support to resolve it; do not start replacement billable work automatically.
- `contact_support`: provide the run and request IDs. Do not retry a non-retryable failure.

Retry rejects completed, cancelled or already-running work and rechecks product authorization, consent and limits. `waiting_for_credits` and `waiting_for_data` resume through funding and accepted evidence; they do not use the retry endpoint. Requirement `rejection` includes a machine-readable code, safe message, rejected document IDs and review time.
''')
    write('configuration','Discover your integration configuration','Read approved identifiers, provider products and runtime limits for your environment.',r'''
Your account manager provides client portal access information and the environment details. Authorized administrators **create API keys in the client portal**, selecting a workspace, environment and permitted scopes. Store keys on your server. One key identifies exactly one workspace and environment.

Call [Retrieve environment configuration](/api-reference/endpoints/platform/retrieve-environment-configuration) with `platform:read` before configuring processing:

| Response | How to use it |
| --- | --- |
| `workspace_id`, `environment`, `revision` | Confirm your intended tenant and sandbox/production environment; refresh cached settings when the revision changes. |
| `workflow_versions` | Select an allowed ID by workflow type, paid product and verification type. |
| `rulesets` | Use an approved `ruleset_version` and its allowed resource types and attribute keys. |
| `cadences` | Use its ID as `cadence`. It describes requested evaluation, not guaranteed source freshness. |
| `limits` | Actual request, burst, concurrent-job, upload-byte, page and MIME-type constraints. |
| `webhooks` | Retained history boundary, retention, delivery timeout and signing-secret overlap. |
| `idempotency_replay_seconds` | The 24-hour full-response replay window; durable request receipts remain until workspace deletion. |

Numeric values in saved examples are synthetic. The response for your environment is authoritative. The account manager communicates planned configuration changes before their effective time under your agreement. Accepted work retains its approved workflow revision.

Read `GET /v1/providers` separately for each provider's `products[].id`, resource mapping, consent scopes, purposes, markets and limitations. Unsupported identifiers return `422 validation_error`; refresh configuration before correcting your request. Rates and agreed workload limits remain available through billing rate cards and workload reports. Discovery does not alter your tier, rate or agreement.

## Evidence readiness

Read [subject readiness](/api-reference/endpoints/risk/retrieve-subject-readiness) with `product=insights` or `product=signal`.

- `preparing`: source synchronization or evidence validation is still running. Poll after `retry_after_seconds`.
- `blocked`: inspect every check and `next_action`; supply missing evidence or contact the account manager.
- `ready`: use `input_manifest_id` for Insights or `baseline_snapshot_id` for Signal.

AMLOK prepares the initial immutable manifest after synchronization and evidence acceptance. Insights banking evidence includes at least 12 months within the agreed record limit. The initial manifest can be ready while later-stage KYC evidence is still required by the underwriting; those requirements belong to the accepted run. Accepted later evidence creates an auditable successor manifest, not a second charge.

A Signal baseline becomes ready after the completed assessment is approved for monitoring, or after the existing-portfolio onboarding process arranged with the account manager. Baseline readiness does not silently run or bill Insights. An empty baseline list is not a readiness signal. Reading readiness never initiates paid processing.
''')
    write('webhook-operations','Operate and recover webhooks','Find missing events, inspect failed deliveries and rotate destinations safely.',r'''
## Reconcile missed events

1. Read `GET /v1/configuration` for `webhooks.retained_from` and retention.
2. [List webhook events](/api-reference/endpoints/webhooks/list-webhook-events) for an inclusive `created_from` and exclusive `created_to` interval. Events remain discoverable even if delivery never succeeded. Page with the returned cursor; the first page freezes its upper boundary.
3. [List webhook deliveries](/api-reference/endpoints/webhooks/list-webhook-deliveries) using `endpoint_id` or `event_id`. Each attempt reports status, safe failure code, HTTP status and the next scheduled attempt.
4. Fix your receiver. Replay the retained event to an enabled destination subscribed to its type. Observe the new attempt and acknowledge only after durable acceptance.

Replay preserves the original event ID and uses a fresh signature timestamp. Your consumer must deduplicate it. Delivery reports omit receiver bodies and credentials. Resource permissions still apply to event discovery and replay.

If your requested interval predates retained history, the API returns `410 event_history_expired`. It does not silently claim there were no events. Reconcile current state through [checkpoints and changes](/api-reference/synchronization). That restores current state, not the exact delivery history of expired events; use your own retained event audit for that history.

## Portal controls

Authorized administrators use the client portal to update a destination's registered HTTPS URL and subscriptions, enable or disable it, and rotate signing secrets. The account manager supplies portal access information and required administrator permissions. Disabling immediately prevents new attempts and cancels queued attempts; retained events remain available for later reconciliation. Re-enabling does not automatically replay the disabled interval. List and replay the needed retained events explicitly.

URL changes are validated before activation and audited. Confirm your new receiver is ready before changing a destination. Pending deliveries use the currently enabled registered destination; preserve its signing-secret configuration during cutover. Register separate destinations if simultaneous delivery is required.

## Rotate a signing secret

1. Generate a replacement through the portal and store it in your server's secret manager. The portal displays it once; never add it to documentation or logs.
2. The portal shows the overlap expiry; its duration comes from `webhooks.rotation_overlap_seconds`. During overlap, each delivery carries a `v1` signature for both current secrets.
3. Deploy the replacement secret to your receiver and verify a signed sandbox event or retained-event replay. The downloadable verifiers accept any matching `v1` signature.
4. Confirm migration before the announced cutoff. At cutoff, the old secret stops signing; only the new secret remains. Coordinate another rotation through the portal if migration fails.

Signing-secret rotation is separate from API-key rotation. Never expose a signing secret in event-list, delivery-list or endpoint-list responses.
''')
    write('sandbox-journeys','Test complete product journeys','Run Insights and Signal scenarios with provisioned synthetic data and test credits.',r'''
Your account manager provides the sandbox URL, client portal access and a synthetic fixture pack. Create a sandbox API key in the portal. Choose or reset the desired sandbox scenario there before a fresh run. Resetting discards only sandbox fixtures and test credits. No real funding, provider account or production data is required.

The runnable journeys need `platform:read`, `risk:read`, `billing:read`, `workflows:execute`, `workflows:read`, `monitoring:write`, and `monitoring:read`. Grant additional scopes only when running the connection, evidence or verification scenarios; each endpoint identifies its required scope. Keys remain restricted to one sandbox workspace.

Read [List sandbox scenarios](/api-reference/endpoints/platform/list-sandbox-scenarios) to obtain actual IDs provisioned for your workspace. These fixtures include authorized source evidence, applications and approved configuration. Insights success includes two bank accounts, five business systems and at least 12 months of banking history within Standard limits. The initial source-connect flow is covered by the [quickstart](/api-reference/quickstart).

## Runnable journeys

Download the [Python journey runner](https://raw.githubusercontent.com/amloktech/docs/main/downloads/run-sandbox-journey.py). It uses the Python standard library, rejects redirects and refuses a production configuration. Set `AMLOK_API_BASE_URL` and `AMLOK_API_KEY` locally, then run:

```bash
python3 run-sandbox-journey.py insights --state insights-state.json
python3 run-sandbox-journey.py signal --state signal-state.json
```

The state file stores resource IDs, intended bodies and stable action keys, never your API key. Protect it as workspace metadata. Reuse the same file after interruption; a fresh file represents a new test action. Reset the fixture in the portal before repeating a completely fresh journey. Run each state file in only one process at a time.

The runner checks configuration and fixture IDs, polls readiness, submits the product request, follows returned IDs, and checks evidence and usage. Insights verifies one completed run and its single usage record. Signal verifies activation, a subsequent snapshot and alert, one charge in its shared monitoring period, and no additional Insights charge for that fixture. A timeout preserves state for reconciliation and does not cancel processing. The runner stops on blocking conditions instead of silently creating replacement work.

Also download the [Postman product journeys](/downloads/amlok-journeys.postman_collection.json). Run one folder at a time with the Collection Runner after setting its protected local environment. Scripts save returned IDs and poll with a bounded attempt count. Standard collection requests remain available for manual debugging. Postman keys are generated once per intended action and retained across a rerun; clear the journey variables only when starting a deliberate new test after a fixture reset.

## Acceptance scenarios

| Scenario ID | Exercise | Expected result |
| --- | --- | --- |
| `insights_success` | Complete underwriting and reconcile its output. | One Standard Insights charge; completed snapshot, manifest and usage agree. |
| `signal_success` | Activate monitoring; observe the scheduled synthetic change. | Full Signal charge on activation; reassessment and alert without another Insights charge. |
| `insufficient_credits` | Submit work without enough test credits, fund through the sandbox portal and retry. | Initial `402` has no run or debit; funded retry uses the same intended key. |
| `authorization_expired` | Renew the seeded connection and complete hosted authorization. | Same connection ID, restored authorization and explicit sync coverage. |
| `rejected_evidence` | Read a rejected requirement and upload the supplied valid replacement. | Structured rejection reason; accepted replacement resumes the same run. |
| `workload_limit` | Submit an oversized workload. | `422 workload_limit_exceeded`, no automatic upgrade or debit. |
| `retryable_failure` | Read the structured failure and retry the same run. | Attempt increments once; successful completion produces only one Insights charge. |
| `owner_kyc` | Run person KYC using its active business association and unfinished parent. | Person result stays in the business product with no extra charge. |
| `duplicate_delivery` | Receive duplicates and replay the same event. | One application-side effect; delivery attempts remain observable. |

For cancellation and month-boundary tests, use the sandbox portal's scenario controls. Cancellation immediately stops processing, deductions and upcoming top-ups. Month advance tests the full Signal charge once per borrower/business/workspace/month. Simulated funds and time cannot affect production. Use the portal fixture pack's valid replacement document and hosted authorization flow; do not fabricate evidence or provider credentials.

Scenario `expected_http_status`, `expected_state` and `instructions` describe each fixture's expected result. General endpoint saved responses show schema shapes and are not those full datasets. A successful local contract test is not evidence that a live sandbox run completed; retain actual run IDs and results from your provisioned environment for acceptance.
''')
    # Regenerated base guides receive deterministic changes, so future rebuilds retain the runbooks.
    changes={
        'authentication': [('Manage key issuance, expiry, revocation, and rotation through the administration process agreed during onboarding. Authenticate requests with your institution-issued API key.', 'Your account manager provides client portal access information and environment details. Authorized administrators create API keys in the client portal, choosing the workspace, environment and permitted scopes. Manage expiry, revocation and rotation there. Authenticate server-side requests with your portal-created API key.')],
        'onboarding': [('Your AMLOK contact supplies the settings and access appropriate to your agreement.', 'Your account manager supplies client portal access information and the environment details appropriate to your agreement. Authorized administrators create API keys in the client portal. Read [environment configuration](/api-reference/configuration) for accepted values and limits, then run the [sandbox journeys](/api-reference/sandbox-journeys).')],
        'quickstart': [('Save `data.id` as `cnn_example`.', 'Generate and include a cryptographically random `state` of at least 32 characters in this request, bound to the initiating browser session. Save `data.id` as `cnn_example`.'),('Next, implement [pagination]', 'Continue with the [complete product journeys](/api-reference/sandbox-journeys) and [connection recovery](/api-reference/connection-recovery). Next, implement [pagination]')],
        'products-and-endpoints': [('The context must belong to the same workspace and subject.', 'The context must belong to the same workspace and primary subject. Person KYC may use an active `subject_association_id` linking the verified person to the parent business; see [related-person verification](/api-reference/related-person-verification). Other stage types remain same-subject.')],
        'processing-lifecycle': [('Processing failed definitively. Inspect the reason and use support when needed.', 'The attempt failed. Inspect structured `failure`; retry the same run only when permitted, otherwise correct evidence or contact support.'),('rejected evidence includes a reason', 'rejected evidence includes structured `rejection` with code, message, document IDs and review time')],
        'idempotency': [('**institution + workspace + environment + operation + key**', '**institution + workspace + environment + operation + key**, with the resolved target path and intended payload validated in its fingerprint'),('Never generate a new idempotency key on every automatic retry.', 'After full-response replay expires, a retained key returns `409 idempotency_result_expired` without executing again. Durable receipts remain until workspace deletion. [Look up the original accepted request](/api-reference/request-recovery) before taking another action.\n\nNever generate a new idempotency key on every automatic retry.')],
        'workflows': [('Create a business/person, obtain authorization, and upload permitted evidence.', 'Create a business/person, obtain authorization, and upload permitted evidence. An included stage needs an existing unfinished Insights run or active paid Signal period. For owner KYC in a business assessment, follow [related-person verification](/api-reference/related-person-verification).'),('## Underwrite from frozen evidence', 'See the [runnable product journeys](/api-reference/sandbox-journeys) for linked requests and billing assertions.\n\n## Underwrite from frozen evidence')],
        'webhooks': [('Terminal failures require delivery review and reconciliation.', 'Terminal failures require [delivery review and reconciliation](/api-reference/webhook-operations). List retained events to discover missing IDs and delivery attempts to inspect failures.'),('Secret rotation overlap, replay retention, delivery timeouts, and administrative controls are configured during onboarding.', 'Read configured overlap, retention and delivery timeouts from `GET /v1/configuration`. Authorized administrators manage URLs, subscriptions, enablement and secret rotation in the client portal; follow the [webhook operations procedure](/api-reference/webhook-operations).')],
    }
    for name,pairs in changes.items():
        p=ROOT/'api-reference'/f'{name}.mdx';t=p.read_text()
        for a,b in pairs:
            if a not in t: raise ValueError('Missing guide edit anchor: '+name+' '+a[:60])
            t=t.replace(a,b)
        p.write_text(t)
    p=ROOT/'api-reference/quickstart.mdx';t=p.read_text().replace('"redirect_uri": "https://client.example.com/connected"','"redirect_uri": "https://client.example.com/connected",\n  "state": "replace-with-random-session-state-at-least-32-characters"');p.write_text(t)
    p=ROOT/'api-reference/errors.mdx';t=p.read_text().replace('| `validation_error` |','| `idempotency_result_expired` | 409 | No re-execution | Look up the durable request receipt. |\n| `event_history_expired` | 410 | No | Reconcile current state through checkpoints and changes. |\n| `validation_error` |',1);p.write_text(t)
    p=ROOT/'api-reference/downloads.mdx';t=p.read_text().replace('180 operations',str(len(json.loads((ROOT/'data/api-reference-index.json').read_text())))+' operations');t+='\n## Complete product journeys\n\nUse the [sandbox journeys](/api-reference/sandbox-journeys), [Python runner](https://raw.githubusercontent.com/amloktech/docs/main/downloads/run-sandbox-journey.py), and [Postman journey collection](/downloads/amlok-journeys.postman_collection.json) to follow returned identifiers through complete Insights and Signal flows.\n';p.write_text(t)
    p=ROOT/'api-reference/overview.mdx';t=p.read_text();t+='\nYour account manager provides client portal access information. Authorized administrators create workspace-bound API keys in the portal. Start with [configuration discovery](/api-reference/configuration) and [sandbox journeys](/api-reference/sandbox-journeys).\n';p.write_text(t)

if __name__=='__main__':generate()

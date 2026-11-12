"""One canonical event/error catalog and webhook delivery contract."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EVENTS={
'embedding_session.completed':('The borrower finishes the Hub connection flow.','Fetch the session and its connection IDs. Completion does not mean underwriting is complete.'),
'connection.action_required':('A connection needs borrower action, such as renewed authorization.','Fetch the connection and start an authorized Hub reauthorization flow; do not retry credentials yourself.'),
'connection.status_changed':('Connection authorization, availability or collection status changes.','Reconcile status, data_status, freshness and consent before using source data.'),
'origination.action_required':('An assessment pauses for documents, consent or another explicit requirement.','Read requirements and supply the requested input; a submission receipt is not an approval.'),
'origination.status_changed':('Origination processing enters another nonterminal state, including waiting_for_credits.','Read current status and requirements. Follow the specific completion/failure events for terminal outcomes.'),
'origination.completed':('Underwriting processing finishes and a risk package is available.','Fetch the origination and risk package. Completed includes approve, decline and review recommendations; it is not a lending approval.'),
'origination.failed':('Underwriting ends without a successful result.','Read failure.code and request_id, correct the cause, and use a new command only for an intentional new assessment.'),
'risk_package.created':('A new immutable Insights or Signal risk package is committed.','Read the package, completeness, dimensions, evidence and policy results with results:read and the required product entitlement.'),
'monitor.status_changed':('Monitoring configuration or lifecycle changes, including active, paused, requires_action, waiting_for_credits, stopped or failed.','Fetch the monitor. Paused or blocked monitoring must not be interpreted as a clean risk evaluation.'),
'monitoring_run.completed':('A monitoring evaluation finishes as completed or partial.','Fetch the run, sources, limitations, deal snapshot and risk package. Partial coverage is explicit.'),
'monitoring_run.failed':('A monitoring evaluation terminates as failed or skipped without a new risk conclusion.','Inspect the run failure and current monitor. Preserve the previous result; do not treat this as an all-clear.'),
'alert.created':('A policy condition becomes an open monitoring alert.','Fetch severity, rule, evidence and package references. Start your own intervention workflow; this API does not manage lender cases.'),
'alert.updated':('An existing open alert receives a newer evaluation, value or evidence.','Fetch the same alert ID and its current package; this is a continuing condition, not another intervention case.'),
'alert.resolved':('Comparable evidence satisfies the old policy condition, or the old policy is superseded. Inspect the resolution explanation; policy replacement does not prove risk recovery.','Fetch the resolved alert and package. A delivery retry or manual acknowledgment does not resolve risk.'),
'export.ready':('An export finishes and can be downloaded.','Fetch the export and request a short-lived download link before expiry. The webhook contains no file or signed URL.'),
'export.failed':('Export generation fails.','Read failure and correct format, input or size constraints before requesting a new export.'),
'data.updated':('New normalized data is available for a connection.','Resume the normalized-data change feed. resource_version identifies the updated connection, not a count of rows.'),
'document.status_changed':('Document processing or access status changes.','Fetch the document and inspect available, rejected or restricted status and failure before using it.'),
'billing.payment_updated':('A funding payment changes state, for example pending, succeeded, failed or returned.','Owners with billing:read reconcile the payment; a pending payment is not spendable credit.'),
'billing.transaction_posted':('An immutable funding, usage, adjustment or refund ledger transaction is posted.','Read the transaction and billing summary. Reconcile by transaction ID, never by webhook arrival order.'),
'deal_snapshot.created':('A new immutable lender-supplied deal snapshot is accepted.','Read its sequence and effective time. This records lender input; it does not rerun historical underwriting.'),
}
ERRORS={
'validation_error':('400 / 422','Correct the named field, schema or incompatible input. Do not retry unchanged.'),
'unauthenticated':('401','Use an unexpired, unrevoked API key for this workspace environment.'),
'forbidden':('403','Check current membership, scopes, product access, Live activation and source consent.'),
'not_found':('404','Check the ID and workspace/environment; foreign records are not exposed.'),
'invalid_state':('409 / 422','Fetch current state and choose an allowed lifecycle action.'),
'idempotency_conflict':('409','Reuse the original payload for that key, or use a fresh key for a genuinely new command.'),
'insufficient_credits':('402','Top up through the Console. For an accepted resource, inspect waiting_for_credits before submitting more work.'),
'precondition_failed':('412','Fetch the current ETag, review the change and submit If-Match again.'),
'cursor_expired':('410','Start a new snapshot and reconcile; retain deduplication state. Expired event replays cannot be queued.'),
'rate_limited':('429','Respect Retry-After and use bounded jittered backoff with the same command identity.'),
 'temporarily_unavailable':('503','Respect retryable and Retry-After; recover an uncertain accepted command before repeating it.'),
'deal_snapshot_conflict':('409','Read the current deal snapshot and review previous_snapshot_id before appending.'),
'payload_too_large':('413','Reduce JSON or upload size to the operational profile limit; do not split a single document arbitrarily.'),
'unsupported_media_type':('415','Send the supported Content-Type and matching detected file content.'),
'document_rejected':('Resource failure','Inspect the rejected document and replace unsafe, corrupt or unsupported content.'),
'processing_failed':('Resource failure','Inspect the terminal origination, monitor, run or export failure and retain request_id for support.'),
'session_expired':('410','Create a new short-lived embedding session; do not reuse its launch URL.'),
'consent_purpose_missing':('422','Obtain the required borrower purpose through the approved Hub configuration.'),
'sandbox_only':('422','Remove simulation controls from Live; use the Sandbox environment to test scenarios.'),
'scenario_not_available':('422','For a command header, choose a scenario enabled in configuration.sandbox.scenario_ids and supported by that endpoint. Named scenario runs use the separate Sandbox catalog.'),
'idempotency_result_expired':('409','Look up the durable request receipt and resource; an expired cached response does not authorize duplicate work.'),
'capacity_exceeded':('429','Lower concurrency or resource fan-out and respect Retry-After.'),
'queue_full':('429','Apply bounded backoff; do not replace the idempotency key while retrying submission.'),
'queue_wait_exceeded':('Resource failure','Inspect the accepted resource failure; review capacity before an intentional new command.'),
'processing_deadline_exceeded':('Resource failure','Inspect partial evidence and the terminal failure; do not interpret a deadline as a completed result.'),
'response_too_large':('413','Use Error.recovery to choose a summary, section, smaller page or supported export.'),
'export_too_large':('Resource failure','Reduce the export scope or choose a supported partitioned format.'),
'export_expired':('410','Create a new export; expired downloads are not renewed indefinitely.'),
'invalid_export_part':('422','Read the export manifest and request an existing part number.'),
}
DELIVERY_ERRORS={
'http_error':'The receiver returned a non-2xx HTTP status. Inspect http_status and fix receiver authentication, validation or availability.',
'redirect_rejected':'The destination returned 3xx. Redirects are not followed; configure the final HTTPS URL.',
'dns_error':'The hostname could not be resolved. Check public DNS and retry after correcting it.',
'unsafe_destination':'The URL or a resolved address is not permitted. Use a public HTTPS hostname on port 443; private, local, metadata and mixed public/private DNS addresses are blocked. This delivery stops.',
'timeout':'DNS, TLS, connection or acknowledgment exceeded the total 10-second deadline. Persist and return 2xx before asynchronous processing.',
'tls_error':'TLS negotiation or certificate validation failed. Install a valid public certificate with the correct hostname and chain.',
'connection_error':'A network connection failed or closed before acknowledgment. Check reachability and receiver capacity.',
'destination_disabled':'The endpoint was disabled or unsubscribed before this attempt. This delivery stops; re-enable and explicitly replay retained events as needed.',
'signing_unavailable':'The service could not access the destination signing secret. Retain the attempt ID and contact support.',
'payload_too_large':'The notification exceeded the 64 KiB envelope limit. This delivery stops; reconcile the event feed and contact support.',
'demo_delivery_disabled':'Outbound delivery is suppressed in the demonstration deployment. Use a normal Sandbox workspace for receiver tests.',
}
def extend(spec):
 s=spec['components']['schemas']
 assert set(EVENTS)==set(s['Event']['properties']['type']['enum'])
 assert set(ERRORS)==set(s['Error']['properties']['code']['enum'])
 spec['x-event-catalog']={k:{'trigger':v[0],'action':v[1],**spec['x-event-resources'][k]} for k,v in EVENTS.items()}
 s['Event']['properties']['type']['description']='Event name. '+ ' '.join(k+': '+v[0] for k,v in EVENTS.items())
 s['Error']['properties']['code']['description']='Stable machine-readable code. '+ ' '.join(k+': '+v[1] for k,v in ERRORS.items())
 s['Delivery']['description']='One immutable HTTP attempt. Multiple attempts share delivery_id; replay creates a new delivery_id while preserving event_id. Diagnostic fields are optional on historical records. next_attempt_at is the schedule at the time of this attempt, not a guarantee of current queue state.'
 s['Delivery']['properties'].update({
 'delivery_id':{'type':'string','description':'Stable delivery group across automatic retries.'},
 'replay_id':{'type':['string','null'],'description':'Replay receipt ID, or null for original delivery.'},
 'duration_ms':{'type':'integer','minimum':0,'description':'Elapsed milliseconds, including DNS, connection, TLS and acknowledgment.'},
 'error_code':{'type':['string','null'],'enum':[None,*DELIVERY_ERRORS],'description':'Safe transport diagnostic; null for a 2xx acknowledgment. '+ ' '.join(k+': '+v for k,v in DELIVERY_ERRORS.items())},
 'next_attempt_at':{'type':['string','null'],'format':'date-time','description':'UTC retry schedule at attempt completion, or null when no retry is scheduled.'},
 'exhausted':{'type':'boolean','description':'True if unsuccessful and no more automatic attempts remain, including a terminal destination rejection.'},
 })
 hook=spec['webhooks']['resourceEvent']['post']
 hook['summary']='Receive a signed resource event'
 hook['description']='POST to your Console-configured destination, not an AMLOK API route. Authentication is HMAC-SHA256 using the destination secret, not a Bearer API key. Verify the exact raw body, enforce five-minute timestamp tolerance, durably deduplicate, then return 2xx within 10 seconds. Maximum body 65536 bytes. During a 24-hour rotation overlap the signature header contains two v1 values. No redirects, Basic authentication, custom authorization headers or mutual TLS are supported.'
 hook['parameters']=[{'name':name,'in':'header','required':True,'schema':{'type':'string'},'description':desc} for name,desc in [('X-AMLOK-Signature','t=<unix_seconds>,v1=<hex_hmac>[,v1=<overlap_hmac>]. HMAC-SHA256 over timestamp + dot + exact raw request bytes.'),('X-AMLOK-Event-ID','Matches the verified body id. Use workspace/environment + event ID for durable deduplication.')]]
 hook['responses']={str(code):{'description':desc} for code,desc in [(200,'Durably accepted, including a previously accepted duplicate.'),(204,'Durably accepted without a response body.'),(400,'Malformed payload; not acknowledged.'),(401,'Invalid signature; not acknowledged.'),(503,'Receiver unavailable; not acknowledged.') ]}
 for path in spec['paths'].values():
  for op in path.values():
   if isinstance(op,dict) and op.get('operationId') in ['listEvents','getEvent','listDeliveries','replayEvent']:
    op['description']+=' Requires the source resource read scope in addition to the event scope. Lists omit unauthorized events and attempts; direct access and replay reject them. Billing events require current Owner authority.'
 return spec

def write_guides(spec):
 def save(path,title,description,body):
  (ROOT/path).write_text('---\ntitle: '+json.dumps(title)+'\ndescription: '+json.dumps(description)+'\nkeywords: ["webhooks", "events", "errors", "recovery"]\n---\n\n'+body+'\n')
 body='Events are durable notifications of committed resource changes. They contain identifiers and versions, not full financial payloads. Fetch the resource with an authorized server-side key. Event recording, outbound delivery and your business processing are separate outcomes.\n\n## Envelope and permissions\n\nEvery notification uses the same [Event schema](/openapi/amlok.json): `id`, `type`, `occurred_at`, `resource_type`, `resource_id`, `resource_version`, nullable `borrower_id` and `environment` (`sandbox` or `live`). A resource without a direct borrower relationship can have `borrower_id: null`; fetch its parent to resolve the borrower.\n\nUse `events:read` to inspect events and deliveries, and `events:write` for replay, plus the read scope in each entry below. Lists omit unauthorized entries; direct reads/replays reject them. Billing requires Owner authority. Resource reads also enforce current consent and product access.\n\n'
 for name,(trigger,action) in EVENTS.items():
  m=spec['x-event-resources'][name]
  body+=f"## `{name}`\n\n{trigger}\n\n{action}\n\nResource: `{m['resource_type']}`. Read operation: `{m['read_operation_id']}`. Additional scope: `{m['scope']}`.\n\n"
 body+='## Delivery semantics\n\nAn origination decline is a completed assessment with a decline recommendation, not `origination.failed`. A risk alert is different from a processing failure. There is no webhook for every HTTP 4xx/5xx request: inspect request logs and the [error catalog](/api-reference/errors). Browser `amlok.hub.*` postMessage notifications are a separate channel; see [embedded Hub integration](/api-reference/integration-hub).\n\nDeduplicate by workspace/environment + event ID. Event IDs survive replay; delivery IDs do not. Arrival order is not guaranteed. Reconcile resource versions and use the event feed for gaps. Specific completion/action events can replace a generic status event; do not require both for the same version.\n\nSee [signatures and receivers](/api-reference/webhooks), [operations and retries](/api-reference/webhook-operations), and [Console configuration](/console/webhooks).'
 save('api-reference/event-catalog.mdx','Event catalog','Every event trigger, resource, required permission and consumer action.',body)
 body='An HTTP error reports request handling. A resource `failure` reports accepted asynchronous work that ended unsuccessfully. A delivery `error_code` reports the attempt to contact your webhook receiver. Keep these three channels separate.\n\n## API and asynchronous errors\n\nInspect `error.code`, `message`, `retryable`, `request_id`, nullable `field` and optional `recovery`. For a resource failure, inspect the same fields on `failure`. Preserve `meta.request_id` and the response request ID for support. `field` is a JSON pointer or header context, never a secret.\n\n| Code | Typical surface | Recovery |\n| --- | --- | --- |\n'
 for name,(surface,action) in ERRORS.items():body+=f'| `{name}` | {surface} | {action} |\n'
 body+='\nHTTP surfaces can vary with the operation; handle the actual status and `retryable` value. After an ambiguous network timeout, use the same idempotency key or look up the request receipt. Never retry an accepted assessment with a fresh key merely because its cached response expired. A partial result, decline, waiting state or alert is not an HTTP failure.\n\n## Webhook delivery diagnostics\n\nEach delivery attempt records `http_status`, `duration_ms`, `error_code`, `next_attempt_at`, `exhausted`, `delivery_id` and optional `replay_id`. Historical records may omit diagnostic fields. A failed attempt can still have a retry scheduled. A previously recorded retry time does not override the endpoint\'s current state.\n\n| Code | Meaning and recovery |\n| --- | --- |\n'
 for code,desc in DELIVERY_ERRORS.items():body+=f'| `{code}` | {desc} |\n'
 body+='\nA 2xx acknowledgment sets `error_code: null`. Receiver response bodies are not stored in public diagnostics. Disabling a destination or removing its subscription stops queued delivery when it is claimed; an already in-flight request may finish. [Replay](/api-reference/webhook-operations) redelivers an existing event, never repeats an assessment or a charge.'
 save('api-reference/errors.mdx','Errors and recovery','Complete API error codes, asynchronous failures and webhook transport diagnostics.',body)

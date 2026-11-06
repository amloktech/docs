# Backend implementation contract

Build the product backend against `openapi/amlok.json`, the published guides and the acceptance cases in this directory. This repository specifies behavior; it does not contain a deployed product backend. Keep one `/v1` surface. Do not implement an internal provider job as a new customer endpoint.

## Delivery order

1. Identity context and discovery: resolve the authenticated key to institution, workspace, environment, authority and scopes; publish effective configuration and immutable profile versions.
2. Durable command infrastructure: canonical request fingerprints, atomic acceptance receipts, 24-hour full-response replay, transactional resource/event outbox, optimistic concurrency and tenant-bound cursors.
3. Borrower and Hub: published Hub versions, exact URL allowlists, short-lived launch capabilities, explicit purpose consent, the browser protocol and idempotent source authorization associations.
4. Inputs and evidence: immutable product/policy versions, application validation, quarantined uploads, content inspection, authorized data snapshots/change feed, frozen evidence and controlled downloads.
5. Insights orchestration: the documented state machine and requirements. Treat normalization/enrichment/calculation as internal implementations behind the specified input/output boundary.
6. Signal: typed portfolio baselines, funded-deal snapshots, consent checks, cadence execution, immutable evaluations and versioned alerts.
7. Financial reporting: connect the organization payment system and shared workspace wallet to the read APIs and exports. Financial administration stays in the console.
8. Events, exports and operations: signed delivery, replay, retention discovery, recovery, Sandbox fixtures and acceptance evidence.

## Atomic boundaries

- Accept a command, create its resource and durable receipt in one transaction. Key scope is workspace/environment/operation/idempotency key. Fingerprint the canonical body, target path, semantic multipart fields/file digest, and any Sandbox scenario header. Same key plus different intent is 409; network failure cannot leave an undiscoverable accepted resource.
- A posted Insights debit and package publication commit together. With insufficient funds, retain waiting_for_credits and publish neither output nor debit. No reservations/held credits. Internal retries and Signal reassessments do not create new Insights charges.
- Signal charging has a unique borrower/workspace/calendar-month identity. Serialize competing facilities/activations. Full monthly charge on the first day or first mid-month activation; no proration and no historical-period debt when resuming.
- Deal snapshot acceptance compares previous_snapshot_id, stores the new immutable input, increments sequence and monitor record_version, updates the pointer and appends its event in one transaction. A run captures its pointer/policy/source versions at start; no mixed-version package.
- Every client-visible state mutation commits its event outbox row atomically. Event reads and delivery inspect current authority/source access. Durable receiver acknowledgments and sender delivery records are separate from domain processing.
- Snapshot creation and change-feed checkpoint acquisition share a consistency boundary. Clients must be able to finish all snapshot pages and then consume changes without losing updates between those phases.
- Upload metadata, binary acceptance and any open requirement association have a durable receipt. Inspection remains asynchronous. An uploaded file cannot be replaced at its existing ID.

## Security and integrity gates

Perform tenant/environment checks on all IDs, references, cursor tokens and source grants; never use a caller-supplied tenant override. For opaque cross-tenant IDs, return not_found without revealing membership. A valid key with insufficient scope receives forbidden. Recheck role authority on billing reads even if a key still carries billing:read.

Keys are issued only to authorized principals in the console. Record creator/service identity, workspace/environment and scopes; loss of required role or membership invalidates the affected authority. Owner and Dev may hold permitted product/developer scopes. Billing scope requires current Owner authority. Analysts have no key-administration or Dev Tools capability. Rotate keys by provisioning a second scoped key, updating the client, confirming traffic, then revoking the first. Revocation applies to new requests immediately, including downloads and exports where source authorization is checked.

Reject spoofed parent origins, return URLs, cross-borrower sessions, stale requirements and unconsented purposes. Hub message receipt is never authoritative consent proof. Bind capability URLs to immutable session/file context and short expiration; exclude them from logs/referrers. Real providers must never receive Sandbox test controls.

Validate dynamic application/pricing schemas and policy unit compatibility. Registry schema definitions are trusted, immutable, versioned and bounded; do not execute arbitrary client schema/code. Product market/type/currency/amount/term/pricing compatibility is checked before acceptance.

Append-only deal updates retain facility identity (borrower, reference, currency, funding time/amount). Validate chronological effective_at, amount currencies, performance consistency and document ownership. Changes to historical evidence are forbidden. A new snapshot cannot cause processing while paused, failed or stopped; stopped and failed monitors reject new snapshot commands.

## Lifecycle and concurrency

A monitor's explicit paused state persists across unrelated consent and funding changes. Keep the requested run state separately from effective blocking reasons internally, while exposing the documented public status. A user-set stop is terminal. Resolve all requirements and recheck funding/consent before returning to active. Never publish restricted outputs when consent is withdrawn during an evaluation.

Origination requirements have stable IDs until resolved. Hub completion and document association must recheck that the requirement remains open and targets the same borrower. Duplicate completion is harmless; if the requirement closed concurrently, return the existing outcome without attaching an unrelated connection. Submitted inputs remain inspectable separately from subsequent associations.

For Signal completed/partial runs, require an immutable package and exact deal snapshot. Failed/skipped runs expose structured failure and no new package. An alert resolution references fresh comparable evidence; it is not a customer dismissal. Versionless mutable resources are forbidden in the event map.

## Data and retention

Authorized data access is independent of underwriting. Preserve normalized fields, source payload availability and provenance. Snapshot filters/authorization bind the cursor. On expiry, return 410 rather than advancing to a new snapshot. Access revocation beats retention; changes expose permitted tombstones so clients can reconcile removed access.

An accepted export pins its snapshot until completion or failure even if the interactive cursor expires. Export source permissions are rechecked on read and download. Immutable resource references cannot be silently replaced by current data. SHA-256 refers to exact downloaded bytes.

## Billing and cancellation

Use decimal arithmetic and half-up rounding as defined in AGENTS.md. Payment attempts are not wallet credits. Only posted transactions change available credits; usage references its historical rate and corresponding negative transaction. Returns/refunds create new linked entries. A billing snapshot freezes summary, payment versions, usage and transaction sequence for reconciliation.

Payment returns and refunds are sourced from the organization payment system. Only actual posted wallet movements affect the API balance; unreconciled returns must not be disguised as spendable credits or erased from payment history. Carry the payment-system explanation in failure_reason and preserve every linked correction. Keep payment processing and accounting implementation behind the read-only API boundary.

Cancellation stops processing, future charges and new top-ups at submission. Follow the existing month-end closure and unused-credit refund policy; retain only permitted final financial records separately. Do not add a servicing, payout or withdrawal API.

## Verification and release evidence

Run `python scripts/current_api.py`, `python scripts/validate-api-reference.py`, `python scripts/test-product-api-review.py`, `python scripts/test-api-examples.py`, `python scripts/test-readiness-contract.py`, and `node --test scripts/test-integration-client.mjs`. Use the project's Python validation environment and Node 22+.

Offline tests validate schemas, semantics and client behavior against controlled fixtures. They are not backend acceptance. Implement each `acceptance-cases.json` scenario against a real test environment and retain observed request/resource IDs and redacted assertions. Complete all public acceptance checklist rows, including both business and consumer examples, before advertising availability.

Keep `artifacts/backend-readiness.json` as the evidence boundary: implemented-backend acceptance remains not_run until executed. Do not change it to passed based only on generated examples.

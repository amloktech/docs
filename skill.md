---
name: amlok-integration
description: Build AMLOK borrower connection, Insights origination, risk-package and Signal monitoring integrations from the authoritative product API.
metadata:
  author: AMLOK
  version: "1.1.0"
  api-version: "1.0.0"
---

# AMLOK integration

Read the [OpenAPI contract](https://docs.amlok.io/openapi/amlok.json), [quickstart](https://docs.amlok.io/api-reference/quickstart) and relevant endpoint schemas before implementing requests. AMLOK has one public API with 65 operations under `/v1`. Do not create provider sync jobs, input manifests or workflow executions from client code.

Inspect the customer's existing application, identity mapping and selected products. Use existing permissions, storage and event handling where possible. This skill provides guidance, not permission to access records, transmit messages or execute chargeable requests. Never request credentials in chat or invent hostnames, fields, endpoints, packages or successful results.

## Access

Set `AMLOK_API_BASE_URL=https://api.amlok.io`, without `/v1`, for both Sandbox and Live, and keep `AMLOK_API_KEY` on the server. Each key binds one workspace and environment. The customer Sandbox uses the same API origin as Live; staging-api.amlok.io is a separate deployment and requires separately issued staging credentials. Never send a workspace key to docs.amlok.io or console.amlok.io. A caller-supplied tenant identifier cannot override that scope. Owners manage organization and billing configuration; Owners and Devs manage integration configuration; Analysts read authorized product results. Product data cannot be modified or deleted.

Read `GET /v1/configuration` for approved application and pricing schemas, integration IDs, embedding versions and monitoring cadences. Catalog coverage does not grant provider entitlements.

## Connect and underwrite

1. Create a business or person with `POST /v1/borrowers`.
2. Create a borrower-bound session with `POST /v1/embedding-sessions`. Launch the returned URL without exposing the API key. Session completion means authorization completed, not underwriting completed.
3. Read connections for access and freshness. AMLOK handles consent capture, collection, normalization and included verification internally.
4. Create immutable lending-product and risk-policy versions using the matching version resources.
5. Submit `POST /v1/originations` with the application, borrower, product/policy version IDs, connection IDs and document IDs.
6. Follow the Origination state and action requirements. For `waiting_for_credits`, preserve the accepted request; do not submit another underwriting.
7. Retrieve the completed risk package, then its frozen evidence set and authorized documents. Preserve missing-data reasons, units, source coverage and policy explanations. The institution makes the credit decision.

## Monitor funded deals

Create `POST /v1/monitors` with funded terms, a risk-package or approved portfolio-onboarding baseline, policy, cadence and connections. Read monitoring runs, alerts and updated packages. Use `PATCH /v1/monitors/{id}` with `If-Match` only for prospective monitoring configuration. Never rewrite historical product evidence or charges.

Signal includes change-driven reassessment and counts each active borrower/business once per workspace/month. A separately requested full underwriting is Insights. Financial APIs expose billing summary, transactions and authorized exports; payment methods, automatic top-ups and cancellation stay in the console.

## Reliability and evidence

- Preserve one `Idempotency-Key` per intended POST command and its retries.
- Recover accepted requests using `/v1/request-receipts/lookup`; do not rerun after the response cache expires.
- Verify raw-body webhook signatures, persist before acknowledgement, deduplicate event IDs and reconcile resource versions.
- Use `/v1/events` with durable resume cursors to recover missed notifications.
- Retrieve evidence through `/v1/evidence` using its frozen set ID. Provider field definitions do not imply separate source-specific endpoints.
- Use document/export download-link commands for authorized short-lived access. Never log credentials or signed URLs.
- Treat missing, stale or restricted information explicitly; never turn it into zero or a passing policy result.

## Verification

Use synthetic fixtures to test request/response schemas, idempotency, null handling, scope isolation and event replay. Validate a provisioned Sandbox journey before enabling Live. Report local checks and actual backend execution separately. The [documentation MCP](https://docs.amlok.io/mcp) searches reference material; it does not access customer workspaces or execute this API.

"""Generate customer Sandbox guidance from the same versioned fixture catalog."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent

def write_guides(spec,index):
    catalog=json.loads((ROOT/'data/sandbox-catalog.json').read_text())
    table='\n'.join('| `'+s['id']+'` | '+s['name']+' | '+s['expected']+' |' for s in catalog['scenarios'])
    businesses='\n'.join('| `'+b['id']+'` | '+b['name']+' | '+b['market']+' | '+b['industry']+' | `'+b['scenario_id']+'` |' for b in catalog['businesses'])
    body='''---
title: "Run reproducible Sandbox scenarios"
sidebarTitle: "Sandbox scenarios"
description: "Run complete fictional business journeys, inspect API responses and logs, test monitoring events, and reconcile simulated credits and payment outcomes."
---

Use **Dev Tools > Sandbox scenarios** to create records through the same API your integration calls. Run a named scenario, inspect its requests and responses, then retrieve its borrowers, data, documents, results and billing records through their normal endpoints. Each execution creates a fresh set of linked resources.

For a guided introduction, start with the [Sandbox overview](/sandbox/overview), [first-use setup](/sandbox/getting-started) and [simulated billing](/sandbox/simulated-billing).

## Choose your starting point

On first use, an Owner or Developer can choose **Start with an empty workspace**. An Owner can choose **Explore sample businesses** to queue the complete six-business pack, including simulated billing. The choice applies to the workspace's Sandbox and is shared with teammates. Concurrent setup requests return the first saved choice.

Starting empty preserves any existing records. Every Sandbox receives CAD 5,000 in simulated promotional credits. **Decide later** postpones the choice in the current browser tab. You can load samples or run individual scenarios later. The Sandbox and Live switch remains unchanged; a separate Demo environment is not required.

The console shows persisted API records. API activity, request logs, source data, risk packages and consumption can be followed using returned resource IDs and request IDs. No sample is a real borrower, credit decision, verification or payment.

## Run from your integration

Create an **All products** Sandbox key in the Console for nonfinancial product scenarios. Set `AMLOK_API_BASE_URL=https://api.amlok.io` and `AMLOK_API_KEY` to that server-side key. Use the [Console scenario tools](/console/sandbox) as an Owner for the complete sample pack and financial simulations; standard Console key profiles do not combine billing permission with scenario commands.

```bash
curl --fail-with-body "$AMLOK_API_BASE_URL/v1/sandbox/catalog" \\
  -H "Authorization: Bearer $AMLOK_API_KEY"

curl --fail-with-body -X POST "$AMLOK_API_BASE_URL/v1/sandbox/runs" \\
  -H "Authorization: Bearer $AMLOK_API_KEY" \\
  -H 'Content-Type: application/json' \\
  -H 'Idempotency-Key: my-first-healthy-test-001' \\
  -d '{"scenario_id":"healthy","fixture_id":"maple-retail","catalog_version":"2026-11-07.1"}'
```

The command returns **202** with a queued run ID. Poll `GET /v1/sandbox/runs/{id}` until `status` is `completed` or `failed`. Inspect `assertions`, `steps`, and `resources`. An expected failed underwriting or declined payment can produce a **completed scenario** because the observed product outcome matched the expectation. A failed scenario means a step or assertion did not complete as expected; completed records remain retrievable.

Use the [runnable scenario client](/downloads/run-sandbox-scenario.mjs) with Node.js 22 or later:

```bash
AMLOK_SANDBOX_SCENARIO=healthy node run-sandbox-scenario.mjs healthy-run.json
```

Set `AMLOK_SANDBOX_FIXTURE` to another fixture ID if needed. The client obtains the catalog version, saves the intended command and idempotency key to a private state file, submits it and polls its result. If the connection drops or polling times out, rerun with the **same file and key** to resume the original run. A new filename starts a new run; changing environment variables does not replace a command already saved in a state file. Keep the file private; it contains request and resource IDs but no API key. For webhook scenarios, set `AMLOK_SANDBOX_ENDPOINT_ID` to your enabled Sandbox endpoint before the first run; this explicitly enables delivery.

## Permissions and isolation

- Catalog, setup and history reads require `sandbox:read`; commands require `sandbox:write`.
- Product journeys require `borrowers:read/write`, `configuration:read/write`, `connections:read/write`, `evidence:read/write`, `insights:read/write`, `signal:read/write`, `exports:read/write`, plus `data:read`, `results:read` and `events:read`.
- Billing scenarios and the full sample pack require current Owner authority with `billing:read`. Developers can run nonfinancial journeys; Analysts cannot execute scenarios.
- Detailed product traces require the product read scopes and enabled Insights and Signal. Billing-only traces require Owner billing authority. Revoking source authorization redacts saved trace payloads and assertions as well as the ordinary source-backed reads.
- Webhook scenarios also require `events:write`. The selected endpoint must belong to the same Sandbox and subscribe to `origination.status_changed` and `origination.completed`.
- The initiating key must remain valid while a run executes. Revoking it stops subsequent scenario API steps. At most three runs can be queued or running in one workspace environment. Honor `Retry-After` on 429 responses.
- Sandbox controls reject Live requests. Sandbox keys and resources cannot address another workspace or environment.

## Fictional business pack

Each business has bank, accounting, payment, commerce and verification fixtures; synthetic normalized records and provenance; a PDF financial statement; consent and connection records; a lending product and risk policy; and an Origination with its expected outcome. Completed assessments include evidence, results, exports and funded monitoring. Blocked and failed cases retain their requirements or failure details so you can test those states.

| Fixture | Business | Market | Industry | Initial outcome |
| --- | --- | --- | --- | --- |
'''+businesses+'''

The pack includes card success and decline, pending and settled ACH, ACH return, refund and simulated automatic top-up records, with linked immutable credit movements. Underwriting and monitoring use synthetic rates and generate usage/workload records. Billing amounts are CAD, including US business examples. Fixture banking covers twelve monthly periods; it is sparse synthetic history, not production-scale or complete daily coverage.

## Scenario catalog

The selected business determines the fictional identity and source data. The scenario controls the test condition and the supplied illustrative policy. A `healthy` run uses a passing policy; `outside_policy` uses a failing threshold, even when you select the same business. `manual_review` exercises unavailable policy inputs. These outcomes are assessments against a test policy; your institution makes the lending decision.

| Scenario ID | Journey | Expected result |
| --- | --- | --- |
'''+table+'''

## Webhooks and monitoring

Outbound delivery is **off by default**, including for the sample pack. Event records are still available through `/v1/events`. Set `send_webhooks: true` and `endpoint_id`, or enable delivery in the console, to send signed events only to that Sandbox destination.

Webhook-specific scenarios suppress automatic delivery during setup, then queue explicit replay attempts for the selected origination events. Duplicate delivery retains the event ID. Out-of-order replay queues newer resource versions before older ones. Delivery is asynchronous; inspect `/v1/webhook-deliveries` and your receiver to confirm actual arrival, status and attempt numbers. Concurrent workers and HTTP retries do not guarantee arrival order. Configure your receiver to return 503 and then 2xx to test the normal retry path. Only actual HTTP attempts appear in delivery history.

`monitoring_alert` publishes reduced synthetic receipts before evaluation. `monitoring_recovery` restores receipts and evaluates again, resolving the prior open alerts. **Evaluate monitoring now** or the `evaluate_monitor` action queues an immediate evaluation for a run-owned active monitor. This does not change server time, token expiry, date-based billing periods or another developer's records.

## Simulated billing

Funding actions require Owner billing authority and never contact a payment processor. Pending and declined payments do not credit the balance. Settled payments credit it; returns and refunds create linked reversals. Existing ledger entries are immutable.

The `autopay` scenario evaluates a fixed synthetic balance of CAD 199 against a CAD 200 trigger and posts a CAD 1,000 automatic top-up. It also checks that a balance equal to the trigger does not trigger that fixture. It does not change saved auto-pay settings or drain your workspace balance. The fixture tests the resulting payment and ledger lifecycle; configure real account auto-pay separately in the billing console.

`insufficient_credits` exercises the blocked underwriting state, funds with simulated credits, clears the explicit test condition and resumes the same origination. It does not drain other developers' test credits. Reconcile `/v1/billing/summary`, `/v1/billing/transactions`, `/v1/billing/payments` and `/v1/billing/usage` after execution.

## Repeat and build your own tests

Use **Repeat with fresh records** or `POST /v1/sandbox/runs/{id}/repeat` with an empty object and a new idempotency key. This creates a new run without deleting prior history, changing prior results, or resetting shared credits. Reuse the same idempotency key only when retrying the same intended command.

Run history lists the newest 25 runs by default, up to 100 with `limit`. Retrieve a known run directly to inspect older history. The list omits detailed steps and resources. Retain returned IDs in your test system.

Use **Data Lookup** for typed requests, responses and field explanations. Copy a run's request sequence to build your own integration tests. Test additional failure conditions with the ordinary endpoints: invalid credentials and scopes, a second workspace's IDs, stale `If-Match`, invalid files, pagination checkpoints, timeouts and accepted-command recovery. Production throughput and real provider behavior require separate verification; these fixtures do not establish those properties.
'''
    (ROOT/'api-reference/sandbox-journeys.mdx').write_text(body)
    (ROOT/'downloads/sandbox-scenarios.json').write_text(json.dumps(catalog,indent=2)+'\n')
    # Maintain compatibility with existing guide links without a duplicate public contract.
    for path in ['api-reference/environments.mdx','api-reference/downloads.mdx']:
        p=ROOT/path
        p.write_text(p.read_text()+'\n\nExplore the [Sandbox scenarios](/api-reference/sandbox-journeys) and download the [runnable scenario client](/downloads/run-sandbox-scenario.mjs).\n')

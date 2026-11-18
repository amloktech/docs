"""Keep the engineering feedback clarifications stable across regeneration."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def section(path, title, body):
    p=ROOT/(path+'.mdx')
    marker='\n## '+title+'\n'
    text=p.read_text().split(marker)[0]
    p.write_text(text.rstrip()+marker+'\n'+body.strip()+'\n')

def write_guides():
    section('api-reference/connection-recovery', 'What consent revocation changes', '''Send `POST /v1/consents/{id}/revoke` with a `reason`. The returned Consent records that value in `revocation_reason`, together with `revoked_at`. Repeating revocation preserves the original reason and timestamp; it does not replace the audit record. Older records can omit `revocation_reason`.

Revocation marks the affected connections `revoked` and immediately moves unfinished originations and running monitors that depend on them to `requires_action`. Inspect `requirements` for the source and required consent purpose. This includes sources belonging to related parties. Paused, stopped and failed monitors keep their current state. Source collection and publication cannot continue under the withdrawn consent.

Historical assessments, evidence references, runs and charges remain recorded. Retention does not grant access: source data and documents can become `restricted`, and a risk package containing unauthorized sources cannot be retrieved. Revocation is not a data-deletion request. See [data access](/api-reference/data-access).

Obtain a new affirmative borrower authorization through a reauthorization Hub session. Review the resulting connection and workflow state. Explicitly paused or stopped monitors need an explicit resume; consent renewal does not turn them on.''')
    section('api-reference/monitoring-design', 'Recover a failed evaluation without duplicating the facility', '''A failed evaluation does not require a new borrower or Monitor. Keep the Monitor ID and deal reference. Inspect its `failure`, source consent, documents and policy first. Obtain a fresh ETag with `GET /v1/monitors/{id}`, then request a new evaluation:

```bash
curl --request PATCH --fail-with-body "$AMLOK_API_BASE_URL/v1/monitors/$MONITOR_ID" \\
  --header "Authorization: Bearer $AMLOK_API_KEY" \\
  --header "If-Match: $MONITOR_ETAG" \\
  --header 'Content-Type: application/json' \\
  --data '{"status":"active"}'
```

`MONITOR_ETAG` is the exact ETag response header, including its quotes. The response confirms scheduling, not a completed evaluation. Poll the Monitor and read `GET /v1/monitoring-runs?monitor_id=...` for the new result. A stale version returns `412`; resolve it by reading again. Invalid or revoked sources must be corrected before activation.

The previous failed run remains in history. Institution-supplied application and deal inputs remain evidence, but are not counted as collected provider records or uploaded documents in the monitoring workload allowance. Resuming does not replay old periods or erase billing records. Do not repeatedly create new Monitors to work around a failure. If the same failure returns, send support the Monitor ID, environment and `failure.request_id`, without your API key.''')
    section('api-reference/configuration', 'Reuse product and policy versions across borrowers', '''A lending-product version describes your offering, not one borrower. Reuse its `id` as `lending_product_version_id` in multiple Origination requests or `baseline.portfolio` inputs. Reuse a compatible `risk_policy_version_id` in the same way. The borrower type, market, amount, currency and term must satisfy the referenced definitions.

For example, two Canadian business borrowers requesting CAD working capital can reference the same product version when both requests fit its limits. Their `borrower_id`, application, documents and authorized connections remain specific to each borrower. Use a different idempotency key for each intended origination.

Find a version using `GET /v1/lending-product-versions?external_id=working-capital&version=1`. Create a new version only when its definition changes. The sample pack deliberately creates separate named versions for its fictional businesses so each scenario can be inspected independently; that is not a requirement for your integration.''')
    section('console/security', 'How long sign-in lasts', '''A Console session lasts up to seven days from creation or its latest refresh. Using the Console can refresh it after at least 24 hours since its previous refresh, extending the expiry another seven days. A brief period of inactivity therefore does not automatically sign you out.

Signing out or revoking a session ends its access. Sensitive actions can still request a fresh identity check even while the main session remains valid. Use **Sign out other sessions** in account security when you need to remove access from another browser.''')
    section('console/webhooks', 'Understand a receiver error', '''In **Dev Tools > Deliveries & events**, **Latest receiver response** is the status returned by your webhook destination. It is separate from the response to your API request. A successful embedding-session request can generate an event whose delivery later fails.

For `405 Method Not Allowed`, check that the configured destination accepts **POST** at the exact path. Use your backend receiver URL, not a Console page or a GET-only route. Verify authentication, signature handling and the response your proxy returns. After correcting the receiver, replay the event and inspect the next attempt. A replay keeps the same event ID, so your receiver must deduplicate it. It does not repeat the original underwriting or source connection.''')
    section('console/quickstart', 'After sample setup finishes', '''The preparation dialog closes when the server finishes loading the records and opens **Home**. A completion notice remains available until you dismiss it, including after navigating or reloading the page. If setup fails, the notice points to the run for inspection; a temporary network error is not a confirmed setup failure.

Open **Origination** from the left navigation to inspect underwriting. Open **Portfolio** for continuous monitoring. Open **Dev Tools > Sandbox scenarios** to inspect setup results or run another example. Older walkthrough recordings can show Sandbox scenarios immediately after loading; the current flow returns to Home.''')
    section('api-reference/rate-limits', 'Test bounded bursts in Sandbox', '''Use an isolated Sandbox workspace and key. Start with a small request count and concurrency, and inspect `operational_profile` from `GET /v1/configuration` before increasing either. Basic compute capacity is not an unlimited load-test target.

In Postman or your test client, keep the method, URL, request body, response status, `X-Request-ID` and `Retry-After` for each attempt. Never record the Authorization header. Test reads first, then POSTs with synthetic data. For each retry of one intended POST, reuse the exact same body and `Idempotency-Key`; use a new key only for a different intended operation.

On `429`, honor `Retry-After`, reduce concurrency and add jitter before retrying. Check the error code: rate limits and a full workload queue are different conditions. Verify that retries do not duplicate records or simulated usage charges. If an accepted response was lost, use [request recovery](/api-reference/request-recovery). Seeing no 429 in a small run is not a failure; the run may remain below the current limit.''')

    section('console/origination', 'Find policy results', '''Open **Origination** in the left navigation, select the case, then open **Overview > Risk package > Policy results**. Each result identifies a rule, its comparison, outcome and supporting evidence. Missing evidence can route the result to review; a completed request does not mean every rule passed.

Developers retrieve the same results using `GET /v1/risk-packages/{id}` and inspect `data.policy_results`. The Origination provides `risk_package_id`; its API response is the workflow record, not the entire risk package. For Signal, use the risk-package ID on the latest monitoring run. See [risk packages](/api-reference/risk-package) for the complete contract.''')

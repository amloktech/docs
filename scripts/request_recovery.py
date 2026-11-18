"""Public request-recovery metadata, generated from the single endpoint catalog."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADER = 'X-Amlok-Operation-Id'

def extend(spec):
    for methods in spec['paths'].values():
        for entry in methods.values():
            for response in entry.get('responses', {}).values():
                response.setdefault('headers', {})[HEADER] = {
                    'schema': {'type': 'string'}, 'example': entry['operationId'],
                    'description': 'Stable OpenAPI operation name for this endpoint. For receipt lookup use the original POST operation name, not the lookup operation, request ID or resource ID. Available on responses handled by a documented route; transport failures may have no response.'}
    lookup = spec['paths']['/v1/request-receipts/lookup']['get']
    descriptions = {
        'operation_id': 'Exact, case-sensitive OpenAPI operationId of the original POST endpoint, for example createOrigination for POST /v1/originations. Find it on the endpoint reference page or in Console Data Lookup under Operation name. It is also returned in X-Amlok-Operation-Id. Save it before sending the original request; it is not a request ID or resource ID.',
        'idempotency_key': 'Exact Idempotency-Key header value sent with the original POST request. Use the same workspace and environment with reliability:read permission. Do not generate a new key for lookup. Keys contain 1 to 256 characters and must not be blank.'}
    for p in lookup['parameters']:
        p['description'] = descriptions[p['name']]
        p['example'] = 'createOrigination' if p['name'] == 'operation_id' else 'origination-synthetic-0042'
        p['schema']['example'] = p['example']
        if p['name'] == 'idempotency_key': p['schema']['maxLength'] = 256
    lookup['responses']['400']['description'] = 'validation_error: missing, blank or malformed lookup parameters, or operation_id does not name a supported POST operation. Inspect error.field.'
    lookup['responses']['404']['description'] = 'not_found: no accepted command matches this operation and key in the authorized workspace environment. The original request may still be in flight; a missing receipt is not permission to submit a duplicate with a new key.'
    schema = spec['components']['schemas']['RequestReceipt']
    schema['properties']['operation_id']['description'] = descriptions['operation_id']
    schema['properties']['idempotency_key']['description'] = descriptions['idempotency_key']

def write_guides(spec, index):
    for endpoint in index:
        path = ROOT / (endpoint['page'] + '.mdx')
        text = path.read_text()
        marker = '\n## Operation name\n'
        text = text.split(marker)[0]
        text += marker + '\n`' + endpoint['id'] + '`\n\n'
        if endpoint['method'] == 'POST':
            text += 'Save this operation name and your `Idempotency-Key` before sending the request. Use both to [recover accepted work](/api-reference/request-recovery) if the response is lost.\n'
        else:
            text += 'The `X-Amlok-Operation-Id` response header identifies this endpoint. Request receipts apply to accepted POST commands.\n'
        path.write_text(text)
    rows = '\n'.join('| `' + e['method'] + ' ' + e['path'] + '` | `' + e['id'] + '` |' for e in index if e['method'] == 'POST')
    guide = '''\n## Find the operation name\n\n`operation_id` is the original POST endpoint's stable, case-sensitive OpenAPI `operationId`. For `POST /v1/originations`, use `createOrigination`. Find it under **Operation name** on the endpoint reference page or in **Console > Dev Tools > Data Lookup**. Use the copy button in Data Lookup. `X-Amlok-Operation-Id` also returns it on responses handled by a documented route. Save the name before sending your request so recovery works when no response arrives.\n\n| Identifier | Meaning |\n| --- | --- |\n| `operation_id` | Fixed endpoint name, such as `createOrigination`. |\n| `idempotency_key` | Exact key you generated and sent for this intended POST command. |\n| `X-Request-ID` | Identifier for one HTTP attempt, useful for support and logs. |\n| `meta.request_id` | Request ID in the response body; an idempotent replay retains the original value. |\n| `resource_id` | Identifier of the accepted resource returned by a receipt. |\n\n## Recover an accepted command\n\n1. Keep the original operation name, Idempotency-Key and exact request in your integration. Use opaque keys without passwords, personal information or other secrets.\n2. Use an API key for the same workspace and environment, with `reliability:read`. Set `AMLOK_API_BASE_URL=https://api.amlok.io` for the customer API or `https://staging-api.amlok.io` when testing on staging with staging credentials.\n3. Look up the receipt with your original values:\n\n```bash\ncurl --get --fail-with-body "$AMLOK_API_BASE_URL/v1/request-receipts/lookup" \\\n  --header "Authorization: Bearer $AMLOK_API_KEY" \\\n  --data-urlencode 'operation_id=createOrigination' \\\n  --data-urlencode 'idempotency_key=origination-synthetic-0042'\n```\n\nThe synthetic key above only works if you previously sent and Amlok accepted that operation with that key. A successful receipt contains `resource_id`, `accepted_at` and `response_replay_available`. Retrieve the resource through its documented GET endpoint; a receipt confirms acceptance, not successful completion. The lookup itself never resubmits the original command.\n\nUnknown operation names and read-operation names return `400 validation_error` with `error.field=operation_id`. A valid operation with no matching accepted receipt returns `404 not_found`. A missing receipt may mean the original request is still in flight. Retry the original request with the same key and payload within the 24-hour replay window. After that window, escalate an unresolved acceptance state to support instead of inventing a new key.\n\nIn **Console > Dev Tools > Request logs**, open the request's **Overview > Request recovery** to copy its operation name and, for new POST logs with a recorded key, a complete lookup example. Supply your API key locally; Console never includes it in the example. Older logs may lack these fields, so keep your integration's own trace.\n\n## POST operation names\n\n| Endpoint | `operation_id` for receipt lookup |\n| --- | --- |\n''' + rows + '\n'
    for name in ['api-reference/idempotency.mdx', 'api-reference/request-recovery.mdx']:
        path = ROOT / name
        path.write_text(path.read_text().split('\n## Find the operation name\n')[0] + guide)

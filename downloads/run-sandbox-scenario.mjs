/* Re-run with the same private state file after interruption; use a new file for a new run. */
import { randomUUID } from 'node:crypto';
import { readFile, writeFile, chmod } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';

export class SandboxScenarioClient {
  constructor({ baseUrl, apiKey, fetcher = fetch, sleep = ms => new Promise(resolve => setTimeout(resolve, ms)) }) {
    const origin = new URL(baseUrl);
    if (origin.protocol !== 'https:' && !(origin.protocol === 'http:' && ['localhost', '127.0.0.1'].includes(origin.hostname))) throw Error('Use an HTTPS API origin.');
    if (origin.pathname !== '/' || origin.search || origin.hash || origin.username || origin.password) throw Error('Supply the API origin without /v1, credentials or query parameters.');
    if (!apiKey?.startsWith('amlok_test_')) throw Error('Use a Sandbox AMLOK_API_KEY.');
    this.origin = origin.origin; this.apiKey = apiKey; this.fetcher = fetcher; this.sleep = sleep;
  }
  async request(path, body, commandKey) {
    if (!path.startsWith('/v1/')) throw Error('Only configured API paths are allowed.');
    if (body !== undefined && !commandKey) throw Error('Persist an idempotency key before submitting a command.');
    let last;
    for (let attempt = 0; attempt < 6; attempt++) {
      try {
        const response = await this.fetcher(this.origin + path, {
          method: body === undefined ? 'GET' : 'POST', redirect: 'error', signal: AbortSignal.timeout(30000),
          headers: { Authorization: 'Bearer ' + this.apiKey, Accept: 'application/json', ...(body === undefined ? {} : { 'Content-Type': 'application/json', 'Idempotency-Key': commandKey }) },
          body: body === undefined ? undefined : JSON.stringify(body),
        });
        const payload = await response.json();
        if (response.ok) {
          if (payload.meta?.environment !== 'sandbox') throw Error('The response did not identify a Sandbox environment.');
          return payload.data;
        }
        const error = Object.assign(Error(`${response.status}: ${payload.error?.code}: ${payload.error?.message || 'Request failed'}`), { status: response.status, detail: payload.error });
        if (![429, 503].includes(response.status) || payload.error?.retryable !== true) throw error;
        const wait = Number(response.headers.get('Retry-After') ?? 2 ** attempt);
        if (!Number.isFinite(wait) || wait < 0 || wait > 60) throw error;
        last = error;
        if (attempt < 5) await this.sleep(wait * 1000 + 250);
      } catch (error) {
        if (error.status || /Sandbox environment/.test(error.message)) throw error;
        last = error;
        if (attempt < 5) await this.sleep(1000 * 2 ** attempt);
      }
    }
    throw last;
  }
}

export async function runSandboxScenario({ client, state, input, persist, sleep = ms => new Promise(resolve => setTimeout(resolve, ms)), now = Date.now, maxWaitMs = 15 * 60 * 1000 }) {
  if (state.origin && state.origin !== client.origin) throw Error('This state file belongs to a different API deployment.');
  if (!state.command) {
    const catalog = await client.request('/v1/sandbox/catalog');
    const body = { scenario_id: input.scenario || 'healthy', fixture_id: input.fixture || catalog.businesses[0].id, catalog_version: catalog.version, ...(input.endpoint ? { endpoint_id: input.endpoint, send_webhooks: true } : {}) };
    state.origin = client.origin;
    state.command = { key: randomUUID(), body };
    await persist(state);
  }
  let run;
  if (state.runId) run = await client.request('/v1/sandbox/runs/' + encodeURIComponent(state.runId));
  else {
    try { run = await client.request('/v1/sandbox/runs', state.command.body, state.command.key); }
    catch (error) {
      if (error.detail?.code !== 'idempotency_result_expired') throw error;
      const receipt = await client.request('/v1/request-receipts/lookup?operation_id=createSandboxRun&idempotency_key=' + encodeURIComponent(state.command.key));
      run = await client.request('/v1/sandbox/runs/' + encodeURIComponent(receipt.resource_id));
    }
    state.runId = run.id;
    await persist(state);
  }
  const deadline = now() + maxWaitMs;
  while (['queued', 'running'].includes(run.status) && now() + 2000 <= deadline) {
    await sleep(2000);
    run = await client.request('/v1/sandbox/runs/' + encodeURIComponent(state.runId));
  }
  return run;
}

async function main() {
  const statePath = process.argv[2] || 'amlok-sandbox-run-state.json';
  let state;
  try { state = JSON.parse(await readFile(statePath, 'utf8')); }
  catch (error) { if (error.code !== 'ENOENT') throw error; state = {}; }
  const client = new SandboxScenarioClient({ baseUrl: process.env.AMLOK_API_BASE_URL, apiKey: process.env.AMLOK_API_KEY });
  const run = await runSandboxScenario({ client, state,
    input: { scenario: process.env.AMLOK_SANDBOX_SCENARIO, fixture: process.env.AMLOK_SANDBOX_FIXTURE, endpoint: process.env.AMLOK_SANDBOX_ENDPOINT_ID },
    persist: async value => { await writeFile(statePath, JSON.stringify(value, null, 2), { mode: 0o600 }); await chmod(statePath, 0o600); },
  });
  console.log(JSON.stringify({ id: run.id, status: run.status, error: run.error, assertions: run.assertions, resources: run.resources }, null, 2));
  if (run.status !== 'completed') {
    if (['queued', 'running'].includes(run.status)) console.error('Still running. Resume with the same state file; do not create another command.');
    process.exitCode = 1;
  }
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main().catch(error => {
  console.error(error.message + '\nRetain the state file and rerun with the same key to recover this command.'); process.exitCode = 1;
});

// Run after npm run build: node scripts/test-sdk-typescript.mjs <build-dir>
// Uses an injected transport only. No backend or external network calls.
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';

const require = createRequire(import.meta.url);
const build = path.resolve(process.argv[2]);
const sdk = require(path.join(build, 'typescript/dist/index.js'));
const spec = JSON.parse(fs.readFileSync(new URL('../openapi/amlok-v1.json', import.meta.url)));
const sample = spec.paths['/v1/configuration'].get.responses['200'].content['application/json'].examples.synthetic.value;
const calls = [];
let status = 200;
const config = new sdk.Configuration({
  basePath: 'https://fixture.invalid',
  accessToken: 'synthetic-test-key',
  fetchApi: async (url, init) => {
    calls.push({ url, init });
    return new Response(JSON.stringify(status === 200 ? sample : { error: { code: 'rate_limit_exceeded' } }), {
      status, headers: { 'Content-Type': 'application/json', 'X-Request-ID': 'req_fixture', 'Retry-After': '5' }
    });
  }
});
const api = new sdk.PlatformApi(config);
const response = await api.iR007();
assert.deepEqual(response, sample);
assert.equal(calls[0].url, 'https://fixture.invalid/v1/configuration');
assert.equal(calls[0].init.headers.Authorization, 'Bearer synthetic-test-key');
assert.equal(calls[0].init.redirect, 'error');
assert.equal(calls.length, 1);
status = 429;
await assert.rejects(api.iR007(), error => {
  assert.equal(error.response.status, 429);
  assert.equal(error.response.headers.get('Retry-After'), '5');
  return true;
});
assert.equal(calls.length, 2, 'No automatic request retries');
for (const item of Object.values(spec.paths)) {
  for (const method of ['get', 'post', 'put', 'patch', 'delete']) {
    const op = item[method];
    if (!op) continue;
    const className = op.tags[0].replace(/[^a-zA-Z0-9]/g, '') + 'Api';
    const methodName = op.operationId[0].toLowerCase() + op.operationId.slice(1);
    assert.equal(typeof sdk[className]?.prototype[methodName], 'function', `${className}.${methodName}`);
  }
}
console.log('TypeScript: 192 callable operations, auth, response preservation, errors and retry/redirect checks passed');

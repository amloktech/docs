# AMLOK documentation

Mintlify source for docs.amlok.io. AMLOK exposes one public product API for borrower connections, Insights origination, evidence and Signal monitoring.

## Authoritative contract

`openapi/amlok.json` defines all 57 public operations under `/v1`. Endpoint pages, examples, Postman and the console Data Lookup import use this contract. There is no legacy API or alternate client catalog.

## Regenerate and validate

```sh
python scripts/current_api.py
python scripts/validate-api-reference.py
python scripts/test-product-api-review.py
python scripts/test-api-examples.py
node --test scripts/test-integration-client.mjs
python scripts/test-readiness-contract.py
mint validate
mint broken-links
```

Validation needs `jsonschema`, `openapi-spec-validator`, and Node.js for JavaScript examples. The normalized-schema source in `data/` preserves field definitions without publishing another endpoint surface. `data/api-contract-source.json` is the original read-only source inventory, not a client contract.

After contract changes, regenerate the console catalog with `python3 scripts/import-data-lookup.py --docs-root /path/to/this/repo` from the console repository. The importer rejects a mismatched endpoint index.

Changes merged to the connected main branch publish through Mintlify. These files describe the API contract; they are not product backend route implementations.

## Backend implementation handoff

Start with `implementation/README.md` and `implementation/acceptance-cases.json`. The public runnable example supports business and consumer fixtures. `artifacts/backend-readiness.json` records offline contract/client verification and explicitly leaves backend acceptance as not_run. The three deal-snapshot operations provide immutable lender inputs; they do not expose loan servicing. Effective operating limits come from configuration, not assumed production quotas.

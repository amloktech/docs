# AMLOK documentation

This Mintlify site publishes integration documentation, normalized data definitions, product research and the AMLOK API reference.

## Current API

API **2.0.0** is the primary documented contract: **45 operations** for borrower connections, Insights origination and risk packages, Signal monitoring, evidence, events and reporting. The previous 192-operation contract remains in `openapi/amlok-v1.json` and the labeled `legacy/v1` reference for migration.

Publishing this repository updates documentation. It does not deploy backend routes, migrate customer records or retire a running v1 environment. The original `data/api-contract-source.json` workbook snapshot is read-only.

## Generate and validate

```bash
python scripts/build-api-reference.py
python scripts/write-api-guides.py
python scripts/validate-api-reference.py
python scripts/test-product-api-review.py
python scripts/test-api-examples.py
mint validate
mint broken-links
```

Python validation requires `jsonschema` and `openapi-spec-validator`. Sample checks also need Node.js. `current_api.py`, `product_api_review.py` and `current_api_guides.py` own the current contract, examples and guides. Do not hand-edit generated endpoint pages or overwrite them with legacy modules.

The validator checks all 45 operations, request/response examples and primary navigation. Migration tests map every v1 operation, enforce immutable product data and exercise invalid payloads. Example tests check cURL/Python/JavaScript syntax and webhook signature handling. These are contract and controlled local checks, not live backend tests.

The current downloadable artifacts are `openapi/amlok-v2.json`, `downloads/amlok-api.postman_collection.json`, `downloads/api-product-index.json` and `downloads/risk-package-example.json`. Existing seven-language SDK archives and their build scripts target **v1.4.2 only**; their compatibility is explicit on the SDK page. Historical billing report schemas and normalized definition versions remain independent from the API route version.

## Preview and publication

```bash
mint dev --no-open
```

The GitHub-connected Mintlify deployment publishes changes merged to `main`. Verify the deployment check and the public page after merging. Follow `AGENTS.md` for billing, evidence, authorization and content boundaries.

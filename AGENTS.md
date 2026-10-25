> **First-time setup**: Customize this file for your project. Prompt the user to customize this file for their project.
> For Mintlify product knowledge (components, configuration, writing standards),
> install the Mintlify skill: `npx skills add https://mintlify.com/docs`

# Documentation project instructions

## About this project

- This is a documentation site built on [Mintlify](https://mintlify.com)
- Pages are MDX files with YAML frontmatter
- Configuration lives in `docs.json`
- Use the Mintlify MCP server, `https://mcp.mintlify.com`, to edit content and settings via MCP
- Use the Mintlify docs MCP server, `https://www.mintlify.com/docs/mcp`, to query information about using Mintlify via MCP

## Terminology

{/* Add product-specific terms and preferred usage */}
{/* Example: Use "workspace" not "project", "member" not "user" */}

## Style preferences

{/* Add any project-specific style rules below */}

- Use active voice and second person ("you")
- Keep sentences concise - one idea per sentence
- Use regular dashes (-), not em dashes, in all documentation titles, descriptions, and body text.
- Use sentence case for headings
- Bold for UI elements: Click **Settings**
- Code formatting for file names, commands, paths, and code references

## Integration status

- Maintain availability, beta labels, and documented markets in `data/integration-status.json`.
- After updating the catalog data or table template, run `node scripts/sync-integration-status.mjs` to synchronize the table, provider pages, and provider coverage.
- Use US and CA as the default markets, as confirmed by the AMLOK team. Keep country-specific providers and catalog editions scoped to their applicable country. Preserve provider-specific availability and entitlement limitations when editing field and resource mappings.

## Integration refresh guidance

- Maintain verified provider update capabilities and primary-source links in `data/integration-refresh.json`. Profiles must match the Active catalog entries exactly.
- Run `python scripts/sync-integration-refresh.py` after changing refresh profiles or Active membership. It updates provider sections and the shared guide.
- Distinguish upstream provider timing from the agreed AMLOK synchronization schedule. Do not infer an AMLOK SLA or universal interval from webhook support or API rate limits.

## Content boundaries

{/* Define what should and shouldn't be documented */}
{/* Example: Don't document internal admin features */}

## API reference

- The AMLOK team identifies the API as version 1.4.2 and requested removal of draft and release-readiness notices. Keep public reference versions and generated examples consistent; preserve operational resource states such as communication drafts.
- Source snapshot: `data/api-contract-source.json`. Keep the original Google workbook unchanged.
- Generate the OpenAPI contract, endpoint pages, Postman collection, and navigation with `python scripts/build-api-reference.py`, then regenerate the guides with `python scripts/write-api-guides.py`.
- Validate schemas and examples with `python scripts/validate-api-reference.py` (requires `jsonschema` and `openapi-spec-validator`). Run `python scripts/test-api-examples.py` with Node.js on PATH to check both webhook verifiers and code samples.
- Use `AMLOK_API_BASE_URL` for institution-issued origins in examples. Keep the playground in simple mode and do not invent a production or sandbox hostname.
- Preserve the read-only source snapshot and internal design refinements. Do not invent production quotas, service commitments, credentials, or verification results. Keep integration availability and Beta labels as explicitly approved by the AMLOK team.
- Billing and wallet extensions live in `scripts/wallet_contract.py`; the API build imports them without changing the source workbook. Preserve existing operation IDs when extending this module.
- Wallet policy: prepaid paid credits are consumed by AMLOK products; the full remaining paid balance is refunded only on final agreement cancellation after usage reconciliation. No on-demand withdrawals or wallet transfers. Cancellation notice and timing vary by agreement, but the remaining-balance refund is not discretionary. Do not deduct fees or remaining term obligations from that refund. Promotional benefits have no cash principal. Refund delivery and reconciliation remain an account-manager process linked to the final cancellation; no client-selected refund amount or payout API. Preserve stable API operation IDs.
- API boundaries: account managers handle agreements, final cancellation, closure and refunds. Publish only reporting, wallet reads, funding methods, top-ups and automatic top-up settings for customers. No customer refund, payout, transfer, wallet-approval, wallet-creation, closure, cancellation or privacy-deletion endpoints. Retention is configured in the platform; completed workspace deletion removes all associated workspace data. Healthcheck and service-status reads are public and contain no tenant data.
- Refund timing: reconcile usage and funding and verify refund instructions before account closure. Issue the full remaining paid-balance refund immediately after account closure. Funds may take 7-10 business days to reach the bank account, depending on the bank. Account closure does not wait for bank delivery; the refund obligation survives closure and any failed or returned payment.
- Run `python scripts/test-wallet-contract.py` after wallet changes. These checks validate the documentation contract and examples; they do not execute a backend or payment rail. Keep payment-provider enablement, custody, settlement expectations and regulatory disclosures tied to onboarding rather than inventing a production arrangement.

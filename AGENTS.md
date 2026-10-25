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

- The AMLOK team identifies the API as version 1.4.2 and requested removal of draft and release-readiness notices. Keep public reference versions and generated examples consistent; preserve valid operational resource states.
- Source snapshot: `data/api-contract-source.json`. Keep the original Google workbook unchanged.
- Generate the OpenAPI contract, endpoint pages, Postman collection, and navigation with `python scripts/build-api-reference.py`, then regenerate the guides with `python scripts/write-api-guides.py`.
- Validate schemas and examples with `python scripts/validate-api-reference.py` (requires `jsonschema` and `openapi-spec-validator`). Run `python scripts/test-api-examples.py` with Node.js on PATH to check both webhook verifiers and code samples.
- Use `AMLOK_API_BASE_URL` for institution-issued origins in examples. Keep the playground in simple mode and do not invent a production or sandbox hostname.
- Preserve the read-only source snapshot and internal design refinements. Do not invent production quotas, service commitments, credentials, or verification results. Keep integration availability and Beta labels as explicitly approved by the AMLOK team.
- Billing and wallet extensions live in `scripts/wallet_contract.py`; the API build imports them without changing the source workbook. Preserve existing operation IDs when extending this module.
- Credit policy: each workspace has one shared CAD credit balance across products. Paid and promotional top-ups have no consumption priority. Used credits are non-refundable; all unused credits, including promotional top-ups, are refunded on final cancellation. No on-demand withdrawals or transfers.
- Signal billing: count each active borrower/business once per workspace per month, regardless of monitoring configurations, checks, facilities, or data connections. The combined workload determines the tier. Cancellation immediately stops further processing and usage deductions; do not introduce post-cancellation charges.
- Client portal: customers manage card or bank-account payment methods, automatic top-up thresholds (minimum CAD 200), top-up amounts (minimum CAD 500 for customer-funded top-ups), and cancellation requests. Enterprise clients may also request cancellation through their dedicated account manager. At least one saved portal bank account is required for refunds, even when funding by card.
- Auto-pay: CAD 200 is the default trigger (customers can raise it), not a processing floor. Minimum customer-funded top-up is CAD 500. Processing continues below the trigger while available credits cover the cost; reject unfunded work without a debit. Holds reduce available credits and pending incoming funds are excluded. Keep active-account reporting accessible.
- API boundaries: publish credit and consumption reports and exports only. No public wallet, payment-method, top-up-setting, cancellation, refund-request, payout, transfer, wallet-approval, or privacy-deletion commands. Portal capabilities do not authorize new public API mutations. Preserve stable operation IDs. Reports identify the authorized workspace and do not allow an untrusted workspace override.
- Cancellation: customers can cancel at any time without notice, including before renewal. All processing, deductions and upcoming top-ups stop immediately when cancellation is submitted in the portal or set by the account manager. Release pending reservations without another debit. Reconcile already-submitted funding without starting new collection attempts. Full closure is at the end of the request month, with an immediate refund of all unused credits to the saved bank account. Data is deleted after that month closes and final information is generated. Retain only necessary final financial/refund/bank-return records separately, without borrower data or continuing workspace access. Bank delivery takes 7-10 business days after issuance, independently of closure. No refund fees or remaining-term deductions.
- Complexity: Standard 2 bank accounts / 5 business systems / 75,000 records; Advanced 4 / 10 / 250,000; Complex 8 / 20 / 1,000,000. Insights limits cover each complete underwriting including at least 12 months of banking history. Signal limits cover newly processed records in the month; unchanged baseline history is not counted again. Each updated version counts as a new record; retries of the same unchanged version are deduplicated. The highest required dimension determines the tier. Custom quotes retain an existing tier with negotiated rates and explicit limits.
- Funding: quote a monthly minimum (at least CAD 1,000), paid for 12 months at signing and each annual renewal. No scheduled monthly payment. Monthly Signal usage deductions are not monthly funding payments.
- Signal includes monitoring and change-driven reassessment, without another Insights charge. A separately requested full underwriting is Insights.
- Monetary billing amounts and rates have two decimals. Decimal half-up round the effective unit rate first, then each quantity-times-rate charge. Totals sum rounded lines; preserve higher precision for non-monetary source ratios.
- Each API key is bound to exactly one workspace, institution and environment, with no caller-controlled workspace override. Read-only baseline discovery lives in scripts/baseline_contract.py.
- Calculator volumes start at 50; deselect unused tiers. Monthly minimum starts at CAD 1,000, auto-pay trigger at CAD 200, and top-ups at CAD 500.
- Support retains the approved uptime and response targets, including 24/7 P1 coverage and a one-hour human response target. There is no standard compensation formula or automatic SLA credit; any remedy is discretionary and expressly agreed.
- Internal supplemental verification and registry providers are not customer integrations. Do not reintroduce their named pages, provider-coverage sections or field mappings. Preserve generic jurisdiction/regulatory terminology and the original source snapshot.

- Run `python scripts/test-wallet-contract.py` after wallet changes. These checks validate the documentation contract and examples; they do not execute a backend or payment rail. Keep payment-provider enablement, custody, settlement expectations and regulatory disclosures tied to onboarding rather than inventing a production arrangement.

- Assessment boundary: AMLOK identifies risk and intervention signals. Do not expose servicing cases, tasks, borrower communications, payment promises, or their approval/send workflows. Institution staff handle outreach and intervention in their own systems. Apply scripts/public_api_scope.py when generating from the original workbook. Preserve loan and repayment data as read-only evidence.

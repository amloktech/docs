"""Customer workflow review and explicitly separate replacement-API design."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DESIGN_GUIDES = ['api-review', 'product-api-design', 'risk-package', 'monitoring-design', 'product-api-migration']


def page(name, title, description, body):
    (ROOT/'api-reference'/f'{name}.mdx').write_text('---\ntitle: '+json.dumps(title)+'\ndescription: '+json.dumps(description)+'\nkeywords: ["Insights", "Signal", "risk package", "API design"]\n---\n\n'+body.strip()+'\n')


def generate():
    audit=json.loads((ROOT/'data/api-surface-review.json').read_text())
    target=json.loads((ROOT/'downloads/api-product-design-index.json').read_text())['operations']
    page('overview','API overview','Underwrite borrowers with Insights and monitor funded deals with Signal.', '''
AMLOK serves financial institutions that underwrite and fund businesses or consumers. Borrowers connect authorized data sources through an embedded Integrations Hub. AMLOK normalizes that evidence and uses it for two products:

- **Insights:** assess an origination using the institution's application, lending product and risk policy. Return the financial dimensions, findings and evidence needed for the institution's decision.
- **Signal:** monitor an existing exposure, identify meaningful changes and deliver risk signals with their supporting evidence.

AMLOK supplies risk intelligence. Your institution makes lending decisions, funds deals and performs servicing in its own systems.

## Choose the correct contract

| Reference | Status | Use |
| --- | --- | --- |
| [Current API 1.4.2](/openapi/amlok-v1.json) | Existing published contract, 192 operations | Existing integrations, endpoint pages, SDKs and runnable examples |
| [Product API design](/api-reference/product-api-design) | Proposed replacement, 45 operations | Implementation planning and contract review; these `/v2` routes are **not available** |

The [API review](/api-reference/api-review) explains the consolidation. Publishing this documentation does not deploy backend routes, remove current endpoints or change existing client behavior. No replacement release date or v1 retirement date is established here.

## The customer journey

```mermaid
flowchart LR
    B[Borrower connects sources] --> E[Authorized evidence]
    A[Application + product + policy] --> I[Insights]
    E --> I
    I --> R[Risk package + evidence]
    R --> D[Institution decision and funding]
    D --> S[Signal monitoring]
    E --> S
    S --> N[Changes + alerts + updated evidence]
```

The replacement design makes this journey the public boundary. Collection, normalization, KYB/KYC stages, calculations, evidence freezing and orchestration run behind it. Your institution can still inspect every authorized supporting record, licensed report and retained file through a common evidence interface.

<CardGroup cols={2}>
  <Card title="Integrate with the current API" icon="terminal" href="/api-reference/quickstart">Use v1 connection, workflow and monitoring operations.</Card>
  <Card title="Review the product API" icon="blocks" href="/api-reference/product-api-design">See borrower sessions, Origination inputs and the smaller proposed surface.</Card>
  <Card title="Understand a risk package" icon="file-search" href="/api-reference/risk-package">Review dimensions, policy results, source coverage and evidence.</Card>
  <Card title="Understand monitoring" icon="activity" href="/api-reference/monitoring-design">Follow evaluations, risk alerts and reliable delivery.</Card>
</CardGroup>

## Workspace and access

Each server-side key is bound to one institution, workspace and environment. Never place it in borrower-facing code. A resource ID grants no access by itself; all reads, linked records, exports and downloads must enforce the same boundary. Sandbox and Live data remain isolated.

The organization owns its billing profile and team permissions. A workspace has one credit balance shared by Insights and Signal. Billing APIs are read-only reporting; authorized Owners manage funding and payment settings in the console. See [authentication](/api-reference/authentication), [product scope](/api-reference/products-and-endpoints) and [credit reporting](/api-reference/credit-reporting).

## Availability and versions

The existing reference is **API 1.4.2**, using `/v1`. Configure `AMLOK_API_BASE_URL` with your institution-issued environment URL. The separate design uses `/v2` to make its breaking changes explicit; it does not imply that a v2 service exists.

Provider access and fields depend on the [integration status catalog](/integrations/status), consent, market, enabled products and source entitlements. Missing or restricted evidence must remain explicit. Neither a connection nor a completed assessment guarantees a particular score, approval or data field.
''')
    page('api-review','API surface review','Findings from the complete 192-operation contract and the proposed 45-operation replacement.', '''
Reviewed **November 6, 2026** against the complete generated OpenAPI contract, all 192 operations, request and response schemas, API guides, normalized resource dictionary, derived attributes, integration coverage, SDK generation and billing rules in the documentation repository. The original source workbook remains unchanged.

## Finding

The public boundary follows internal data collections and processing stages more closely than the customer's two product journeys. The problem is not that the underlying data model is too detailed. Financial institutions need that evidence. The problem is making every collection and execution stage a separate integration concern.

The proposed replacement has **45 operations**, 147 fewer than the current 192 (about **77% fewer**). This is a target contract, not a claim that backend endpoints have been retired.

## What needs to change

| Finding | Current evidence | Design change |
| --- | --- | --- |
| Underwriting requires orchestration knowledge | Create application, discover a manifest, choose workflow version and input IDs, start workflow, resolve separate decision, attributes and snapshot | One Origination submission; AMLOK owns orchestration and returns a risk package |
| No first-class risk package | `RiskSnapshot` links attributes, manifest and workflow; `Decision` is a separate artifact | One immutable result with dimensions, policy evaluations, versioned input context and evidence links |
| Lending product catalog is missing | `/v1/products` represents inventory items; application creation supplies only product type and limited requested terms | Explicit immutable lending-product versions, including pricing and repayment terms |
| Policy input is incomplete | Decisions report policy IDs, but the public contract has no complete policy ingestion/version resource | Versioned validated risk policies supplied or provisioned before underwriting; no arbitrary executable policy code |
| Borrower embedding lifecycle is missing | Connection authorization exists, but no institution-facing embedding-session resource is documented | Short-lived, borrower-bound sessions tied to a published Integrations Hub configuration |
| Data access is fragmented | 96 operations can be expressed as evidence reads without losing their typed records | One paginated evidence collection and exact-version record reads, plus exports and controlled file downloads |
| Internal processing leaks into client code | 26 operations expose job, manifest, baseline or included-stage responsibilities | Keep these internal; expose requirements, useful status, workload reporting and traceability |
| Monitoring is too technical at enrollment | Monitor creation needs a baseline snapshot, resource types, attribute keys, cadence and ruleset | Accept funded-deal context and approved policy; resolve the baseline and source scope internally |
| Events, risk conditions and delivery can be confused | Separate webhook, alert, change-feed and job families | Keep business alerts, durable events and HTTP delivery attempts distinct, with clear links |
| Financial reporting repeats retrieval patterns | 20 billing operations plus 2 workload reads | Read-only summary, immutable transactions and typed exports; preserve all financial detail |

## Disposition of every current operation

| Disposition | Operations | Meaning |
| --- | ---: | --- |
| Retain a customer capability | 13 | Monitoring controls, alerts, connection visibility, recovery and reliability |
| Consolidate | 52 | Combine related reads and inputs into product resources |
| Expose through evidence | 96 | Preserve normalized records and source versions behind unified retrieval |
| Internalize execution | 26 | AMLOK owns collection, included checks, calculations, manifests and orchestration |
| Manage in the console or test tooling | 5 | Webhook administration, organization audit logs and sandbox controls |

Download the [complete 192-operation migration inventory](/downloads/api-endpoint-migration.csv). Each row includes the stable v1 operation ID, method, path, disposition, destination and reason. No endpoint is dropped from the inventory.

## What should stay

- The typed normalized dictionary and field provenance. Fewer routes must not mean untyped financial blobs.
- Immutable assessment inputs, outputs and evidence versions; no product-data update or delete commands.
- Explicit missing, stale, restricted and not-applicable states. Missing values do not become zero or a passing policy result.
- Workspace and environment isolation, source entitlements, audited downloads, idempotency and accepted-command recovery.
- Included KYB/KYC, lien, calculation and investigation stages within Insights or Signal, without new standalone product charges.
- The existing shared-wallet, funding, cancellation, refund and Signal account-month rules. This review does not change pricing or commercial terms.

## Design basis

The report-oriented flow is consistent with [Plaid's Assets pattern](https://plaid.com/docs/assets/): request a report, receive completion notification and retrieve the result. That is an API design reference, not an assertion of equivalent product coverage or licensing. [Stripe's response expansion](https://docs.stripe.com/api/expanding_objects) also illustrates returning related context together instead of requiring a separate request for every object. AMLOK's design uses bounded summaries with paginated evidence rather than unbounded expansion.

For assessment content, [OCC small-business lending guidance](https://www.occ.gov/topics/supervision-and-examination/credit/commercial-credit/small-business-lending.html) emphasizes repayment capacity and current and expected cash flows. [OCC retail lending guidance](https://occ.gov/publications-and-resources/publications/comptrollers-handbook/files/retail-lending/pub-ch-retail-lending.pdf) discusses consumer capacity measures. These inform the dimension taxonomy; they do not establish universal thresholds or certify AMLOK compliance. Business and consumer methods, populations and permitted data must be validated separately.

## Delivery boundary

This repository deploys documentation. It does not contain the product processing backend. The changes publish a smaller, schema-defined design, a clearer entry point and a migration plan while keeping v1.4.2, its operation IDs, source snapshot, SDK inputs and examples intact.

The implementation gates and cutover sequence are in [Migration and release gates](/api-reference/product-api-migration). Backend behavior, live provider access, payment execution and production underwriting accuracy are not verified by documentation tests.
''')
    groups={}
    for op in target: groups.setdefault(op['group'],[]).append(op)
    catalog='\n\n'.join('### '+group+'\n\n| Method | Proposed route | Purpose |\n| --- | --- | --- |\n'+'\n'.join('| `'+o['method']+'` | `'+o['path']+'` | '+re.sub(r'(?<!^)([A-Z])',r' \1',o['id']).capitalize()+' |' for o in rows) for group,rows in groups.items())
    page('product-api-design','Product API design','A proposed API organized around borrower connections, Origination and monitoring.', '''
<Warning>
Design for implementation review only. The `/v2` routes on this page are not available. Existing integrations continue to use [API 1.4.2](/openapi/amlok-v1.json). Publishing this design does not deploy an API.
</Warning>

## Public boundary

Expose the customer inputs and outputs: borrower, connection session, lending product, risk policy, Origination, risk package, funded-deal monitor, evaluation, alert and evidence. AMLOK owns source collection, normalization, extraction, verification, calculations and orchestration.

An institution should not need a manifest ID, child workflow ID, calculation job or processing-context object to obtain an underwriting. Those records may remain internal for reproducibility and support.

Download the [proposed OpenAPI contract](/openapi/amlok-product-api-design.json) and [operation index](/downloads/api-product-design-index.json). The proposal has its own version, `2.0.0-design.1`, and is excluded from the current SDK and Postman generators.

## Ownership and configuration

| Object | Ownership and behavior |
| --- | --- |
| Organization | Legal customer, team permissions, billing profile and payment methods |
| Workspace + environment | API authorization boundary, product records, connection sessions and shared credit balance |
| Embedding configuration | Owner/Dev configures and publishes the Integrations Hub in the console; API sessions pin a published version |
| Lending product | Institution's financing offer and its repayment/pricing terms, not an AMLOK paid product or inventory item |
| Risk policy | Institution-approved, typed and versioned assessment rules |
| Origination | One request to assess a borrower for a particular application, lending product and policy |
| Risk package | Immutable assessment result and exact evidence references |
| Monitor | Prospective configuration for observing a funded exposure |

The API key's scopes do not replace console roles. Owners manage organization, workspace, team and billing controls. Owners and Devs manage integration configuration. Analysts read permitted product results and reporting without Dev Tools or billing access. Every export must enforce its underlying data permissions, including Owner authority for billing. Nobody edits or deletes historical product data through these routes.

## 1. Connect a borrower

Create a typed business or person borrower. The server then creates an embedding session using the borrower ID and published embedding version. Only the short-lived launch URL reaches the borrower browser. The institution key, provider credentials and provider routing remain server-side.

The session captures the actual borrower's authorization. Completion provides connection and consent references; it does not mean all data has arrived. Connection health explains missing access and reauthorization. For reauthorization, create a new session bound to the existing connection. Revoked or expired consent cannot be revived by changing a status value; obtain new authorization.

Return URLs must match approved destinations. Session binding, expiry, origin restrictions and callback validation must be enforced by the implementation. A browser success callback is never proof of consent or underwriting completion; verify server-side state or a signed event.

## 2. Supply the lending context

Create immutable versions of the institution's lending product and risk policy, or use versions already provisioned for the workspace. Retrieve approved application and pricing schemas through configuration.

The lending product must capture borrower type, market, currency, size and term bounds, repayment frequency and validated pricing economics. The submitted application carries the requested amount, term, purpose and institution-specific declared data. Validate that these inputs agree. A policy for a Canadian business cannot silently become a US consumer policy.

Policy rules refer to approved dimension keys, units, comparison operators and thresholds. Missing inputs require review. Policy documents are supporting context, not automatically executable rules. Free-text descriptions must not silently become credit decisions. Updating a policy or product means creating a new version; existing packages keep their original versions and hashes.

## 3. Request an Origination

The institution submits its application, borrower, product version, policy version and authorized connection/document IDs in one command. AMLOK gathers the necessary source data, identifies missing requirements, runs included verification and analysis, freezes the evidence and produces the risk package.

```json
{
  "borrower_id": "bor_synthetic",
  "application": {
    "institution_reference": "LOS-2026-0042",
    "requested_amount": {"amount": "50000.00", "currency": "CAD"},
    "requested_term_months": 12,
    "purpose": "Working capital",
    "application_schema_id": "app_schema_synthetic",
    "declared_data": {"annual_revenue": "600000.00"}
  },
  "lending_product_version_id": "lpv_synthetic",
  "risk_policy_version_id": "rpv_synthetic",
  "connection_ids": ["con_synthetic"],
  "document_ids": []
}
```

This is a synthetic design example. `declared_data` must validate against the institution-approved schema; it is not an unrestricted route around input validation. Submitted claims remain distinguishable from provider-observed or independently verified data.

An accepted request returns `202` and an Origination ID. Follow the resource or a signed event through `collecting`, `requires_action`, `processing`, `waiting_for_credits`, `completed`, `failed` or `cancelled`. Requirements point to source connection, reauthorization or document-upload actions. New accepted evidence can resume the same unfinished request within its agreed scope. Completed work is immutable; a new full underwriting is a separate authorized request.

Completion checks and deducts Insights credits atomically with package publication. Insufficient credits at that point leave the accepted request waiting without publication or a debit. No separate verification/calculation charges or reserved-credit model is introduced.

## 4. Retrieve the result and evidence

Read the [risk package](/api-reference/risk-package) by the ID returned on completion. It includes product/policy versions, application context, financial dimensions, rule outcomes, source coverage and limitations. Use its evidence-set ID to paginate exact normalized records, provider-report references and original documents.

Keep large transaction collections and files outside the main response. Exports support complete risk-package JSON or PDF, normalized evidence JSON/CSV and authorized billing reports. Recheck workspace, consent, retention and provider licensing when reading or downloading. A restricted original file remains restricted even if its derived result is available.

## 5. Monitor the funded deal

Create a monitor with the borrower, funded-deal terms, approved policy, cadence and either an existing risk package or an approved portfolio-onboarding reference. AMLOK resolves the baseline. Institutions do not need to create internal baseline snapshots or calculation manifests. See [Monitoring design](/api-reference/monitoring-design).

## Reliability and scale

- All list routes use opaque cursors and bounded pages. Cursors bind workspace, environment, filters and snapshot; a changed filter requires a new traversal.
- Every POST accepts a stable idempotency key. A reused key with different input fails. Accepted-command recovery must survive the 24-hour cached-response window.
- Monitor configuration changes require `If-Match`; stale changes fail with `412`. There are no edits or deletes for packages, alerts, source evidence or billing history.
- Event consumers verify raw-body signatures, persist before acknowledging, deduplicate by event ID and tolerate out-of-order delivery. Replay only repeats delivery.
- API origins, quotas, event retention and provider freshness are supplied through onboarding. This design does not invent production values or SLAs.

## Proposed operation catalog

All routes below belong to the replacement design, not the available v1 contract. Endpoint count is the number of method/path pairs.

'''+catalog)
    page('risk-package','Risk package design','Financial dimensions, policy evaluation and evidence in one immutable result.', '''
<Warning>
This page defines the replacement API design. The current API returns separate risk snapshots, attributes and decisions; follow [current evidence traceability](/api-reference/evidence-traceability) for those resources. The proposed `RiskPackage` is not yet a live endpoint.
</Warning>

## What the institution receives

A risk package is the completed assessment of a borrower in a specific lending context. It is not just a score, a provider response dump or an executed lending decision.

| Section | Contents and purpose |
| --- | --- |
| Identity and context | Borrower, Origination or monitoring-run ID, product, timestamps and previous-package link |
| Application | Submitted request and declared data; absent only where an existing-portfolio assessment has no origination |
| Lending product and policy | Exact immutable definitions, version IDs and content hashes used in this assessment |
| Assessment | Advisory result, plain-language summary and supported reasons; institution decision remains external |
| Dimensions | Financial measures grouped by the question they answer, with units, calculation versions and observation windows |
| Policy results | Each rule's pass, fail, unavailable or not-applicable result, threshold, actual value and evidence |
| Source coverage | Integration, source-as-of time, retrieval time, usable window, gaps and limitations |
| Evidence set | Immutable membership ID, count and digest; paginated access to exact normalized versions and files |
| Reproducibility | Normalization, calculation and applicable model versions; billing usage link when relevant |

Every meaningful conclusion must lead back to evidence. Preserve measured values and definitions separately from narrative interpretation. A fluent explanation is not a substitute for a calculable metric or licensed provider result.

## Assessment dimensions

| Dimension | Business assessment | Consumer assessment and boundaries |
| --- | --- | --- |
| Identity | KYB, registration, ownership and related-person checks where authorized | Authorized identity/KYC and applicant consistency; do not assume business ownership checks apply |
| Cash flow | Operating inflows/outflows, net cash flow, volatility, seasonality and overdraft patterns | Observed income deposits, spending, recurring obligations and cash buffers; deposits are not verified gross income |
| Liquidity | Available cash, liquidity ratios, runway and working-capital needs | Liquid resources and residual buffers, using permitted sources |
| Revenue quality | Customer/processor receipts, refunds, chargebacks, recurring revenue and reconciliation | Not applicable unless the consumer assessment legitimately includes self-employment/business income |
| Profitability | Margins and earnings using eligible statements and consistent periods | Not a generic consumer metric; assess applicable income and affordability instead |
| Leverage and obligations | Existing facilities, debt schedule, liens and debt-to-equity where supportable | Verified liabilities and complete debt obligations; do not infer missing debts from bank activity alone |
| Repayment capacity | Cash-flow DSCR, stress scenarios and proposed product payments | Verified-income debt-to-income, payment burden and residual income when the required inputs exist |
| Concentration | Customer, supplier, channel and related-party dependence | Income-source concentration only where meaningful and permitted |
| Collateral | Eligible asset valuations, encumbrances and supportable loan-to-value | Product-specific collateral; not applicable to every unsecured product |
| Fraud and consistency | Identity, document and cross-source inconsistencies with evidence | Applicable identity, document and source discrepancies; a signal is not a proven allegation |
| Income and affordability | Owner/guarantor support where explicitly in scope | Verified income, obligations and product-specific affordability |

These are assessment categories, not a promise that every integration supplies every field. Use the existing [56 derived-attribute definitions](/data-model/derived-attributes) where applicable. Any new metric needs an approved formula, units, eligible population, minimum coverage, evidence inputs and calculation version before implementation. There is no universal score, threshold or minimum ratio suitable for all products and markets.

## Availability is part of the answer

A dimension is `available`, `partial`, `unavailable` or `not_applicable`. Individual proposed scalar metrics are `available`, `unavailable` or `not_applicable`; a usable metric has a decimal-string value and an explicit unit/window. Unavailable metrics have a null value and a reason. Coverage limitations belong alongside the result, not only in a log.

Do not substitute zero for missing revenue, debt, DSCR, DTI, a credit score or probability of default. Do not manufacture a PD or provider score where the model is not validated, licensed and entitled. Actual cash-flow DSCR and EBITDA-based proxies must have different definitions. Do not combine currencies, legal entities or non-comparable periods without an explicit approved transformation.

Policy results use `unavailable` when inputs are missing. The overall recommendation must not become `within_policy` while a required rule remains unavailable. Institutions review the reasons and make their own final decision.

## Evidence and documents

1. Read the package's immutable `evidence_set.id`.
2. List evidence with that set ID and an optional normalized `resource_type` filter.
3. Retrieve a record using its evidence ID. The response contains the frozen normalized version, provenance and any document reference.
4. Request a controlled download for an authorized original file or provider report. Verify the returned digest against the downloaded bytes.
5. Use an asynchronous export for large normalized datasets or a complete risk-package report.

This preserves bank transactions, accounting records, payments, commerce, inventory, lender-supplied exposures, KYB/KYC results, liens, reconciliations and retained documents without one collection endpoint per table. Exact records may be restricted by source licensing, consent or retention. Return explicit unavailability; never silently substitute today's record for the one used in the assessment.

A content hash establishes byte consistency, not source authenticity or legal sufficiency. The package and evidence-set digest rules must reuse the canonical manifest serialization in [evidence traceability](/api-reference/evidence-traceability), and the implementation must verify member hashes before publishing an export.

## Historical integrity

Completed packages cannot be edited. A corrected source or changed policy produces a new package linked to its predecessor. Monitoring keeps the original baseline and each subsequent assessment. The prior facts, missing-data state, policy version and reasons remain auditable until the configured retention boundary.

The [synthetic package example](/downloads/risk-package-design-example.json) illustrates a case requiring review because repayment evidence is missing. Its values and hashes are illustrative and are not model-performance or verification claims.
''')
    page('monitoring-design','Monitoring design','Enroll a funded exposure and retrieve evaluations, changes, alerts and evidence.', '''
<Warning>
This is the replacement API design. Use [current monitoring workflows](/api-reference/workflows#monitor-an-existing-exposure) for the available v1 contract.
</Warning>

## Enroll the deal, not a collection of backend jobs

Submit the borrower, funded amount, outstanding exposure, funding/maturity dates, repayment terms, source connections and approved policy. Reference a completed risk package or an approved existing-portfolio onboarding process. A baseline must be ready before active monitoring; the server resolves and records it.

One borrower may have multiple monitored exposures. Signal's charge remains one borrower/business per workspace per month, with the combined workload determining the tier. Evaluations and included reassessments do not launch or charge a separate full Insights underwriting. The existing activation, monthly charge, insufficient-credit and cancellation rules remain unchanged.

## Keep four concepts separate

| Resource | Answers |
| --- | --- |
| Monitor | Which deal is observed, against which baseline, policy and requested cadence? |
| Monitoring run | What happened in this scheduled or change-driven evaluation, and which source data was available? |
| Risk package and alert | What changed in the assessment, which risk condition triggered, and what evidence supports it? |
| Event and delivery attempt | What notification was produced, and did the institution's endpoint receive it? |

## Evaluate each integration explicitly

Each monitoring run reports per-connection retrieval and source-as-of times, the evidence window, completeness, gaps and failure limitations. Its evidence-set ID opens normalized records or document references from that run. The console can render these as per-integration logs and payload drawers without exposing internal worker queues.

Daily monitoring is a requested evaluation schedule, not a guarantee that every provider has new daily data. Do not count unchanged source versions again, interpret a missing sync as zero revenue, or clear a risk condition because data disappeared. A partial run can publish supported findings only with explicit limitations; required unavailable checks remain unresolved.

An alert identifies its rule and policy version, metric, unit, previous/current values, threshold, severity, evidence and baseline/current package IDs. System resolution requires comparable fresh evidence. Institutions can store their own acknowledgements and case actions; they do not edit the historical alert in AMLOK.

## Configuration changes

Owners and Devs can pause, resume or stop future monitoring and change approved policy/cadence with `If-Match`. These are configuration changes, not edits to source data or past results. A stopped monitor is terminal; a new authorization is needed for a new enrollment. Pausing or creating another monitor does not generate duplicate monthly charges within an already paid borrower/workspace/month.

Consent revocation prevents further collection. Account cancellation stops processing and deductions immediately according to the existing policy. A late provider callback cannot reactivate cancelled work or publish a newly billed result.

## Notifications and recovery

The proposed event catalog covers connection actions, Origination progress, completed packages, monitor state, evaluation results, alert creation/resolution and export completion/failure. Notifications contain identifiers, event time and resource version. They contain no bank transactions, full reports, API credentials or download URLs.

1. Validate the raw-body signature using the existing webhook verification rules.
2. Persist the event before returning success; deduplicate using its event ID.
3. Fetch the referenced resource using the institution's authorized server-side key.
4. Do not let an older resource version overwrite newer state.
5. Use the durable event cursor to recover missed notifications. A webhook replay repeats delivery only.

For initial synchronization, capture a feed cursor with `start=now`, then traverse snapshot-bound collection pages and resume events from the captured cursor. Deduplicate overlap using resource ID and version. The event response returns a resume cursor even when no events are available. Invalid or expired cursors fail explicitly; resynchronize rather than silently skipping a gap. Retention duration remains an onboarding/release requirement, not an invented SLA.

`GET /events` is the durable notification log. `GET /webhook-deliveries` is the transport history. Alert state, processing state and an HTTP delivery failure must never be collapsed into one status.
''')
    page('product-api-migration','Migration and release gates','Move from the v1 resource API to the product API without breaking existing customers.', '''
## Current change

This documentation change introduces the product design, complete migration inventory and machine-readable proposed schemas. The published v1.4.2 specification, operation IDs, Postman collection, SDKs and existing endpoint URLs remain available. There is no declared sunset and no claim that any replacement route works in an institution's environment.

## Implementation sequence

1. **Build the product boundary.** Introduce borrower aliases, embedding sessions, immutable lending-product/policy versions, Origination orchestration and risk-package assembly on top of the existing normalized model. Keep stable source and evidence identifiers.
2. **Hide orchestration behind the boundary.** The server owns consent validation, collection, required KYB/KYC/lien stages, manifests, calculations, included-processing context and billing publication. Avoid requiring customers to coordinate child jobs.
3. **Complete monitoring.** Accept funded-deal context, resolve the baseline, expose each evaluation's source coverage, immutable package and risk alerts. Preserve account-month billing and historical policy/evidence versions.
4. **Provide evidence and exports.** Implement frozen-version queries, licensed document downloads and bounded exports. Reconcile result membership and hashes against the original manifest; preserve typed normalized schemas.
5. **Run parallel contract checks.** Compare v1 and replacement outputs for the same authorized evidence, product/policy and observation window. Shadow comparisons must not create extra paid processing or duplicate charges.
6. **Release per institution.** Confirm application/pricing schemas, supported policy operators, provider entitlements, sandbox fixtures, retention and quotas. Issue the correct environment configuration, publish supported replacement SDKs and enable the new API only after backend checks pass.
7. **Deprecate after adoption.** Measure actual v1 use, publish operation-specific migration instructions, agree notice periods and maintain v1 adapters during the transition. Remove routes only through an announced compatible migration, not by deleting documentation.

## Backend release gates

| Area | Required evidence before availability |
| --- | --- |
| Tenant isolation | Cross-workspace/environment references, cursors, associations and download IDs fail closed |
| Embedding sessions | Expired/replayed sessions, unapproved origins/return URLs and forged callbacks cannot authorize sources |
| Policy and product input | Schema/type/unit/currency/market mismatches rejected; unknown dimension keys cannot execute; accepted versions immutable |
| Evidence | Every metric/reason/policy result resolves to frozen authorized versions; restricted/deleted originals remain unavailable |
| Async behavior | Accepted, missing-evidence, retryable failure, permanent failure, cancellation and waiting-for-credits states have deterministic recovery |
| Money | Insights publication/debit atomic; same command never billed twice; Signal same borrower/month deduplicated; cancellation blocks late publication/charges |
| Monitoring | Existing-portfolio enrollment works without inventing an origination; source outages do not clear alerts; policy revisions preserve history |
| Delivery | Raw-body HMAC, duplicate/out-of-order events, cursor gaps, retries and replays tested; no borrower payloads in notifications |
| Scale | Bounded pages, consistent pagination, large evidence sets and exports verified under the intended workload; no made-up throughput claim |
| Data science | Metric formulas, coverage rules, population/market validation and model limitations approved separately from schema tests |

## Compatibility details

`/v1/products` contains merchant inventory. It must not be redirected to lending-product configuration. Business/person IDs can remain underlying subject IDs while a borrower resource supplies a simpler public identity. Existing applications map to Origination references, and historical workflow/decision/snapshot IDs remain traceable.

Do not rename existing routes simply because the console says **Origination**. Existing clients may use `/v1/applications`; the proposed `/v2/originations` has a different input and output contract, not just a different label.

The current SDK and Postman downloads stay pinned to v1.4.2. The proposed OpenAPI file is an independent design artifact. A backend release must supply its own tested examples, supported client generation and migration tests before those tools can switch contracts.

## Review artifacts

- [Current OpenAPI](/openapi/amlok-v1.json)
- [Proposed OpenAPI](/openapi/amlok-product-api-design.json)
- [Every existing operation and its destination](/downloads/api-endpoint-migration.csv)
- [Proposed operation index](/downloads/api-product-design-index.json)
- [Synthetic risk package](/downloads/risk-package-design-example.json)

The generator preserves the source workbook and regenerates this inventory from every current operation. Validation covers schema structure, positive and negative examples, complete endpoint mapping and preservation of the existing contract. These checks do not execute a production backend.
''')


def apply_navigation(api_tab, groups, essentials, icons):
    api_tab['groups'] = [
        {'group':'Start here','pages':['api-reference/overview','api-reference/api-review','api-reference/authentication','api-reference/environments']},
        {'group':'Product API design','icon':'blocks','pages':['api-reference/product-api-design','api-reference/risk-package','api-reference/monitoring-design','api-reference/product-api-migration']},
        {'group':'Current v1 integration','pages':['api-reference/quickstart','api-reference/workflows','api-reference/downloads']},
        {'group':'Current v1 endpoints','expanded':False,'pages':[{'group':g,'icon':icons[g],'expanded':False,'pages':pages} for g,pages in groups.items()]},
        {'group':'Current v1 guides','expanded':False,'pages':[{'group':name,'icon':icon,'expanded':False,'pages':['api-reference/'+p for p in pages if p not in ['workflows','downloads']]} for name,icon,pages in essentials]},
    ]

# Risk-package coverage review - 6 November 2026

## Decision and scope

Expand the existing single product API result rather than add calculation endpoints. Keep 57 operations under `/v1`. The contract includes 24 dimension families, 149 uniquely named scalar definitions and 14 typed analysis sections. Period variants are series, not additional metric-count claims. Business and consumer applicability, market/provider entitlement and data completeness are explicit.

This is a review of published product capabilities and a contract design. It does not demonstrate production accuracy, connector completeness, regulatory fitness or industry superiority. Backend execution and predictive model validation have not been performed. Public customer documentation describes the specified behavior in present tense; this internal review is excluded from the documentation site.

## Published benchmark

| Provider / primary source | Published coverage used in the review | Contract response |
| --- | --- | --- |
| [Plaid Underwriting](https://plaid.com/docs/underwriting/), [Plaid Check API](https://plaid.com/docs/api/products/check/) | Income, employment/assets/cash flow, transaction behavior and eligible credit insights. US Check coverage must not be generalized to Canada. | Independent gross/net income, affordability, verified income streams, payment behavior, source coverage, eligible credit/model output with population and market. |
| [Codat lending](https://docs.codat.io/lending/overview/), [financial statements](https://docs.codat.io/lending/features/financial-statements-overview/) | Standardized accounting, banking and commerce information, financial statements and ratios. | Source-backed P&L/balance/cash-flow statements, working capital, profitability, reporting quality and bank/accounting reconciliation. |
| [Ocrolus Analyze](https://docs.ocrolus.com/docs/analyze), [Detect](https://docs.ocrolus.com/docs/detect), [post-funding analytics](https://docs.ocrolus.com/docs/post-funding-analytics) | Document/bank financial analytics, balances, recurring cash flows, debt/payment behavior, document integrity and post-funding analysis. | Original documents and page-level evidence, contradiction findings, explained debt schedules, daily balances and comparable Signal changes. No imitation of proprietary scoring. |
| [Mastercard cash-flow analytics report](https://static.developer.mastercard.com/content/open-banking-us/uploads/Cash-Flow-Analytics-annotated-report.pdf), [balance analytics](https://static.developer.mastercard.com/content/open-banking-us/uploads/Balance-Analytics-Report.pdf) | Account and aggregate transaction/balance analytics and historical trends. | Explicit account consolidation, observation coverage, dated series, transfers/financing exclusions and cash-buffer/payment metrics. |
| [Flinks Enrich](https://www.flinks.com/products/enrich), [attributes overview](https://help.flinks.com/support/solutions/articles/43000765794-flinks-attributes-transforming-transactional-data-into-actionable-insights) | Broad categorized transaction attributes, income, cash flow, liabilities and risk signals. | Versioned calculations, classification basis, unclassified share, complete-obligation requirements and explicit missingness. Attribute counts are not comparable to unique conceptual dimensions. |
| [ForwardAI lenders](https://www.forwardai.com/lenders), [Precise API description](https://www.forwardai.com/knowledge-center/press/forwardai-debuts-forwardai-precise-a-new-lender-first-api-that-delivers-real-time-robust-accounting-and-financial-data-suite-for-reduced-risk-small-business-lending/) | Accounting/bank information, cross-reference analysis and financial forecasting for lending. | Evidence-backed reconciliation bridges, financial metrics and conditional forecasts/stress scenarios with assumptions, horizons and model identifiers. |

These sources establish useful breadth targets. They do not prove that a competitor lacks an undocumented feature. Provider marketing counts, sample reports, countries, products and time-window variants are not interchangeable comparison units.

## Acceptance requirements for implementation

1. Resolve only authorized borrower sources and frozen input versions. Account for every catalog metric and every analysis section, including unsupported, missing, stale and inapplicable results.
2. Implement and version calculations with replayable reference datasets. Validate source-to-normalized transformations, transfers, refunds, duplicate transactions, FX, accounting basis, document extraction, ownership scope and incomplete histories independently.
3. Validate numerical results against independently produced bank/accounting/payroll/debt records. Compare cross-source sums, period boundaries and precision; exercise genuine zero and invalid-denominator cases.
4. Reconcile every decision-support reason to immutable evidence and the actual policy comparison. Confirm partial evidence never becomes a policy pass or automatic financial-institution decision.
5. Establish separate business/consumer and US/Canada eligibility matrices. Map source permissions and licensed redistribution constraints. Do not expose restricted raw reports just because derived output is permitted.
6. Produce a provider-by-provider coverage report on matched data populations before making comparative claims. Compare feature completeness, evidence coverage, missingness, calculation agreement, freshness and failure recovery; measure operating performance separately.
7. Validate any PD/LGD/expected-loss model on representative held-out cohorts with a defined target, horizon, calibration, stability and governance. No such calibrated model is supplied by this documentation change.
8. Test supported Signal cadence against immutable deal snapshots and comparable baseline metrics. Verify failure/staleness does not resolve alerts. Financial history and charges stay immutable.

## Artifacts and checks

- `scripts/risk_package_catalog.py`: source definitions and applicability.
- `scripts/risk_package_contract.py`: schemas, fixtures and cross-field acceptance rules.
- `scripts/risk_package_guides.py`: public dictionary, methodology and business/consumer/Signal examples.
- `scripts/test-risk-package.py`: negative schema and semantic checks; results in `artifacts/risk-package-validation.json`.
- Console importer consumes the same generated catalog and OpenAPI, with a parity check and searchable individual metric definitions.

Contract checks cannot prove the performance or completeness of an implementation that has not been exercised with real provider data. “Most comprehensive in the industry” remains a goal to demonstrate, not a published claim.

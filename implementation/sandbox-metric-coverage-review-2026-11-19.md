# Sandbox metric examples: documentation validation

## Scope

Catalog `2026-11-19.3` provides positive fictional examples for all 184 scalar underwriting metrics across 24 dimensions. This is coverage across applicable scenarios, not 184 numeric results for one borrower. The separate financial attribute registry contains 12,955 context/period/category/statistic definitions; this review does not claim positive coverage of every definition or validate live provider performance.

The recommended customer path uses comprehensive business scenarios for Maple and Cedar, the individual-income scenario, and the monitoring-comparison scenario. The downloaded manifest also includes the other four business fixtures and the first monitoring baseline. The four recommended runs cover every metric. Business activity and personal income evidence retain 36 complete months; metrics use their declared periods, generally the latest twelve months. The first comparable monitoring example reuses frozen observations and therefore has zero change. It must not be presented as a deterioration example.

The starter missing-source and manual-review cases retain their intentional gaps. Unsupported denominators, subscription cohorts, inventory, consumer applicability and baseline comparisons remain null with a reason. Optional model probabilities, benchmark percentiles and real credit-bureau results are not fabricated.

## Download and evidence

`downloads/sandbox-metric-coverage.json` was regenerated from the current backend's public sample builders using `apps/product-api/scripts/audit-metric-coverage.mjs`. Its observation timestamp is explicitly frozen at `2026-11-19T12:00:00.000Z`. It contains only allowlisted fictional fixture/scenario IDs, metric metadata, numeric examples, dates and counts. It contains no workspace IDs, users, credentials, customer records, source payloads or download capabilities.

The backend audit inspected 9 assessment cases and checked every metric's type/status, numeric input, frozen evidence membership, source field path, document reference, dimension status and completeness totals. All 184 definitions had an available example. Cases using the same metric can legitimately have different numbers or missingness. These values are a dated snapshot, not assertions for a future run.

## Local verification

| Verification | Result |
| --- | --- |
| Canonical API reference generation | Passed; 67 operations; no drift across 260 fingerprinted generated targets. |
| Console Data Lookup importer parity | Passed; 67 endpoints, 1,841 fields, 238 providers and 71 mappings. |
| API reference validation | Passed; 20 request examples, 704 response examples and 67 Python samples. |
| Product contract review | Passed; 57 positive examples, negative validation cases, institution completeness, negotiated rates and borrower lifecycle checks. |
| Risk package contract | Passed; 24 dimensions, 184 metrics and 36 contract checks. |
| Verification contract | Passed; 936 checks, 25 sections, 860 dictionary fields and 44 mapping groups. |
| Downloaded metric coverage | Passed; all 184 metric keys match the contract/catalog; 9 scenario counts reconcile; the four documented runs cover every metric. |
| Download URLs | Passed; 16 source-hosted downloads and 42 same-host JSON targets. |
| Data model alignment | Passed; 7,541 checks, 981 source fields and 2,036 provider-resource associations. |
| Executable example checks | Passed; 68 JavaScript examples, 90 shell examples and 36 guide blocks. |
| Sandbox/integration client tests | Passed; 12 tests including retries, resumable commands, origin boundaries and pagination. |
| Readiness contract | Passed; 196 schema/client checks, 21 event types and 110 offline client calls. |
| Enterprise transport contract | Passed; 199 checks and 52 paged risk-package sections. |

The Mintlify renderer was not available in the local tool installation, so no visual Mintlify build is claimed. This review covers local generation, links, schemas and executable examples. Hosted staging acceptance and release deployment are tracked separately by the application release; this document makes no production-publication claim. Offline contract checks do not demonstrate live integrations, predictive accuracy or production load capacity.

## Canonical-generation compatibility correction

Local integration subsequently caught a pre-existing mismatch between the documentation generator and the checked-in runtime contract: generation omitted the optional Hub session `created_at`, `first_opened_at`, `completed_at` and `cancelled_at` fields. Internal docs/Data Lookup parity alone did not detect this because both had been regenerated from the same incomplete source. The canonical lifecycle patch now preserves all four existing definitions and both create/get response examples. Both Hub operations and the `EmbeddingSession` schema match the prior runtime HEAD exactly; the remaining schema changes are the intended scenario enum and the derived paged-metric view described below. A second canonical generation retained the repaired contract digest, and all five runtime contract/semantic tests passed. Documentation readiness checks now explicitly require the timestamp properties/examples, reject invalid timestamps and permit omission on older sessions.

## Bounded metric retrieval

Integration testing also demonstrated that one complete dimension could exceed the response byte limit even with a page size of one, because its metrics contain complete evidence references. The additive `section=metrics` representation returns `RiskMetricEntry` objects with the parent dimension key/status and one unchanged metric. It flattens the existing immutable dimensions rather than adding a field to stored packages or exports. The summary indexes 184 metric entries and the contract exposes 52 total sections. Clients start at `limit=1` and follow cursors; individually oversized metrics still use explicit export recovery. New contract checks reject incorrect parent dimension keys, missing wrapper fields and invalid statuses. This preserves evidence instead of truncating it to meet the byte limit.

## Reproduction

Run the backend metric audit to regenerate the source report, then preserve the download's allowlisted fields. Run `python scripts/test-sandbox-metric-coverage.py`, `python scripts/test-download-links.py` and the existing contract workflow checks. The new coverage test is included in the documentation contract workflow. Keep both the generated guide and `scripts/sandbox_guides.py` updated so later regeneration preserves the explanation and download link.

## Hosted staging acceptance — 20 November 2026 UTC

The final public-API verifier and combined Console browser checks passed. Four hosted cases (comprehensive Atlas/Cedar, personal income and comparable monitoring) collectively covered 184 of 184 scalar metrics. Each assessment retained all 184 entries with explicit applicability/missingness. The verifier made 1,357 validated requests across 10 operations, with observed statuses 200, 202, 401 and 413. Zero transport/backoff retries were recorded; bounded metric-page resizing after documented 413 responses is counted separately. These are verifier-only requests, excluding scenario-internal traffic, setup, cleanup and browser calls; they are not a throughput benchmark.

Every referenced evidence ID in the four assessed packages was checked against the frozen manifests. The hosted verifier fetched 898 evidence details and checked at least one source field for every populated metric. This is deliberately bounded source-field verification; the local nine-case audit remains the exhaustive all-input-path check. The linked monitoring baseline and unchanged-observation zero deltas were verified. The browser completed 12 unique checks across selectors, history, underwriting, personal PDFs, Data Lookup, Portfolio and verification-key cleanup with no unexpected server errors.

Local results were 214 product tests, a subsequent focused seven-test verifier run that overlaps the product suite, 30 Console tests, and passed local API journeys. Do not sum the overlapping suites. The initial functional job terminated only during cleanup because its monitor update used a stale If-Match and returned 412. A separate cleanup job fetched the current monitor version, completed successfully, and confirmed one paused synthetic monitor plus three revoked verification keys with zero active. The Console independently confirmed all verification keys were revoked.

The webapp release artifact `docs/releases/sandbox-complete-metric-verification.json` contains exact operation counts, observed status sets, case-level availability and evidence counters, immutable staging image references, cleanup proof and source snapshots. It excludes private fixture/user/workspace/run/package/evidence identifiers and credentials. Deployment was directly through Azure. This release has not been deployed or published to production. No claim is made that unrelated production branches stayed unchanged. No Mintlify visual build, live-provider validation, production load or predictive-accuracy acceptance is implied.

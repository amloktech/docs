# Normalized KYC/KYB response review

Reviewed November 6, 2026. This is internal implementation guidance, excluded from the public site by `.mintignore`.

The approved change extends the existing risk package and Data/Evidence records. It does not create a second API, standalone paid verification product, or lender-managed provider workflow. The original borrower/integration, origination, document, monitoring and billing contracts remain in place.

## Sources and limits

Reviewed Didit's public data-model dictionary and session decision OpenAPI, Baselayer's full published OpenAPI (including search, enhanced international records, watchlists, liens, dockets and consortium results), and all five user-supplied Canadian JSON/PDF files. The machine-readable [source mapping](./verification-source-mapping.json) records 44 mapping groups, canonical schema targets, transformations and limits.

Current's sample demonstrates search and business verification, corporate/individual shareholders, municipal licence detail and document-only corporate structure. Empty regulatory arrays and null sanctions/website results do not establish those branches' non-empty field schema or no-hit semantics. Obtain their provider schemas or authorized populated fixtures before implementing those adapters. The contract already provides typed destinations for these capabilities without pretending the sample proved them.

The supplied PDF distinguishes registered/records offices and the agent for service, while summary material can collapse roles or addresses. Preserve conflicting observations and authoritative document/page evidence. An active company with overdue returns or missing required people is not a completed verified outcome. Voting shares do not establish economic ownership or a resolved ultimate owner.

No supplied customer identities, registration numbers, addresses, report URLs or report contents are published. Public examples are synthetic and illustrate incomplete KYB and an unreviewed screening candidate.

## Contract and disclosure decisions

- All 25 observation sections are present. Their availability, check execution, check outcome and entity legal status are independent.
- Each item carries source identity, observation/retrieval times, evidence or exact data-record references, field overrides and missing-field reasons.
- Stable canonical fields cover common meaning. Reviewed typed supplemental facts and authorized native source payloads preserve material source-specific detail. Neither is an unrestricted passthrough.
- Documents retain AMLOK IDs and page references. Reauthorize downloads; never return provider console/session URLs, credentials or expiring source links.
- Default responses exclude raw biometric templates/capture media, precise tracking identifiers, unrelated identities, private personal social data and unnecessary protected attributes. Identity attributes used for an authorized compliance purpose must not silently become lending score inputs. Full identifier/document disclosure requires appropriate entitlement and purpose in every representation, including exports and native payloads.
- Subscription state, configurable provider admin fields, workflow layout, internal user/assignee metadata, provider billing, lien-filing mutations and provider-console actions are not underwriting observations. Age estimation and authentication telemetry unrelated to the requested identity/compliance purpose are not promoted into lending output. Verified age/identity facts can use permitted person facts with evidence, without raw face imagery.
- Provider and registry availability varies by purchased product, consent, country and source entitlement. Do not advertise universal successful KYC or KYB from feature availability.

## Backend implementation acceptance

This change supplies the contract, documentation, field dictionary, fixtures and semantic validators; it does not execute provider adapters. Implement each mapping with real licensed fixtures before production acceptance.

1. Pin source versions and replay normalized adapter fixtures against `VerificationAssessment` and `semantic_errors`. Cover all completed, rejected, pending, skipped, unavailable and unrecognized provider statuses.
2. Resolve authorized borrower/associated-party identities. Keep every attempt and immutable assessment version, exact source snapshots and provenance without cross-workspace leakage.
3. Enforce disclosure before writing any normalized value, source payload, document or export. Test masking, licence restrictions, consent withdrawal, document expiry, unsupported countries and redaction of prohibited facts in every representation.
4. Validate currency, dates, country codes, ownership basis/ranges, complete chains, matching-policy thresholds and screening reported/returned counts. Never infer missing/clean/zero values.
5. Emit ordinary data changes and updated Signal risk packages through the existing event contract when new verification observations arrive. Frozen underwriting packages and evidence remain unchanged.
6. Keep `risk_package.verification`, `normalized.assessment`, downloadable examples, public field anchors and console Data Lookup generated from the same schemas.

## Checks

Run `scripts/build-api-reference.py`, `scripts/validate-api-reference.py`, `scripts/test-product-api-review.py`, `scripts/test-risk-package.py`, `scripts/test-verification.py`, and `scripts/test-api-examples.py`. Validate Mintlify navigation/links. Regenerate the console using `scripts/import-data-lookup.py`, then run its Data Lookup tests and type checks. These validate contracts/examples and UI reference behavior; they do not establish live source coverage or backend deployment.

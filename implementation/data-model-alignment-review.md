# Data model alignment review - November 6, 2026

## Scope and evidence

Reviewed the published main tree after PR 15 against the sole 57-operation OpenAPI contract, all Data Model pages, 238 integration guide/catalog entries, 2,036 provider/resource associations, 71 upstream mappings, 149 metric definitions, 860 detailed verification definitions and the research/product boundary. Console Data Lookup imports the same contract and now the generated source-field catalog.

This is a specification and cross-reference audit. It does not execute upstream adapters, borrower processing or enterprise load tests. Existing provider source citations and mapping evidence/test statuses remain unchanged. It does not recertify every third-party API field or refresh the empirical research corpus.

## Findings corrected

- The source dictionary had 957 entries but the current source read schemas contain 961. Added verification.subject_association_version, requirement.rejection, workflow_run.attempt and workflow_run.failure to the reference.
- Required/optional labels came from a fuller resource definition rather than the public partial read representation. The generated dictionary now follows exact containing-object requiredness and nullability. Optional read fields no longer carry a contradictory required-when-resource-exists availability annotation.
- Restored field IDs on refined schema properties. Corrected reconciliation_link.review_status to its actual F0987 identifier rather than the stale F0941 reference.
- Normalized source enums and public product-state enums were insufficiently distinguished. The current enum page is schema-generated and removes five source-only enum headings that have no corresponding public normalized enum schema.
- Shared source helper structures were not listed after the earlier shared-types rewrite. The page now includes the helper properties and their exact types/presence.
- Domain counts and the model entry point now reflect the source catalog, detailed verification aggregate and 149 metrics separately. The 56 supporting derived attributes are explicitly distinguished from selectable risk-package metric keys.
- Research pages previously linked only generally to the data model. Added direct product correspondence, including record revisions, provenance, reconciliation, metrics, verification and monitoring, while preserving proposed/observed research boundaries.
- Provider lookup now carries the catalog's Active/In Review, Beta and market metadata. Full-inventory capability references do not imply that every connector is Active or every upstream field is mapped.

## Validation

The alignment test checks every published source field against its exact schema pointer and field identifier, presence and nullability; matches Data/Evidence variants; validates provider guide status and resource membership; resolves all upstream mapping targets (including common metadata and resource routing); compares enum values; and resolves the API fields referenced by research correspondence. 7,461 checks pass.

OpenAPI/example validation, product, risk, verification and enterprise contract checks pass. Deterministic regeneration passes. Mintlify build and link validation pass. Console Data Lookup passes 13 tests and contract/web type checks. Wire schemas, endpoints and accepted JSON shapes are unchanged; this change corrects metadata and reference material.

## Remaining evidence boundary

22 catalog integrations are Active and 216 are In Review. The 71 field mappings are a documented subset, not full upstream conformance for all catalog entries. The API schema can represent an observation without every provider supplying it. An empty collection, missing input, candidate identity or research benchmark must not be represented as completed verification or a production-calibrated borrower outcome.

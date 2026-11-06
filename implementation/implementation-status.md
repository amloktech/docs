The AMLOK API reference is the specification for the product backend to be built. It defines one API under `/v1`. Publishing a specification, example or console Data Lookup entry does not establish that its backend operation is available.

The current contract covers borrower authorization, application and document submission, Insights risk packages, direct data access, Signal monitoring, funded-deal input updates, events, exports and billing reads. All implementations must conform to the same OpenAPI, lifecycle rules and acceptance criteria.

## Before calling an environment

Your account manager provides portal access and the API origin. An Owner creates a workspace/environment key, publishes a Hub and approves the application's exact return URLs and embedding origins. Retrieve configuration to discover supported inputs and the effective operating profile. A successful configuration response is required before an environment is considered provisioned.

An environment is ready for integration only after the [acceptance checklist](/api-reference/integration-acceptance) passes against that environment. The downloadable development profile and examples are synthetic fixtures, not production credentials, quotas, prices, measured latency or uptime promises.

## Source of truth

The [OpenAPI document](/openapi/amlok.json) defines wire types, constraints, operation IDs and events. The product guides define cross-resource authorization, atomicity and lifecycle behavior that JSON Schema cannot express. Endpoint pages, Postman and console Data Lookup are generated from that contract. There is no parallel API or legacy endpoint set.

The [operational profile](/api-reference/operating-profile) contains effective environment-specific limits. Source-specific coverage, licensing and retention remain constrained by each integration's documented entitlements; a field in the schema is not a promise that every provider populates it.

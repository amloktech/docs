An AMLOK environment is ready for institution integration when these checks pass against that environment. Contract validation and offline client tests are prerequisites; they do not establish backend availability.

| Area | Required observable result |
| --- | --- |
| Provisioning | An Owner obtains scoped keys, publishes a Hub, registers origins/return URLs and reads complete configuration |
| Authentication | Missing/invalid/revoked keys fail; wrong workspace/environment IDs and cursor chains disclose no resources |
| Permissions | Each operation enforces its documented scope; billing requires Owner authority; export and event reads recheck source access |
| Hub | Approved iframe and redirects work; unapproved origins/URLs fail; spoofed messages cannot complete sessions |
| Consent | Underwriting and monitoring purposes are explicit; missing/revoked monitoring consent blocks Signal and ongoing restricted collection |
| Inputs | Application/product/policy schemas and units are validated; document MIME, size, malware and ownership checks run server-side |
| Insights | One accepted command publishes one immutable package and its debit atomically, or exposes a typed blocking/terminal state |
| Recovery | Timeout after acceptance, 24-hour replay expiry, duplicate commands and mismatched payloads do not create duplicate work/charges |
| Data | All snapshot pages plus changes contain authorized records without gaps; revoked access and removals reconcile local copies |
| Evidence | Metric/policy references resolve to the exact versions used; restricted files stay restricted; downloads match SHA-256 |
| Signal | Explicit portfolio baseline works; scheduled/changed-source evaluations preserve source coverage and prior package links |
| Deal inputs | Competing snapshot submissions accept exactly one current version; prior snapshots/results remain unchanged |
| Actions | Every requires_action state has a typed, usable resolution; failed states expose safe structured reasons |
| Events | Every event type maps to its documented retrievable resource/version; signatures, duplicate delivery and out-of-order processing are safe |
| Exports | Complete authorized snapshot contents, format/schema and integrity match; source permission is rechecked on download |
| Billing | Pending payments do not create spendable credits; one snapshot reconciles deposits, product usage, corrections and returns |
| Signal billing | One charge per borrower/workspace/month, including multiple facilities; no duplicate charge for included reassessment |
| Limits | Effective configured upload/rate/expiry boundaries produce the documented errors; clients can discover all values |
| Cancellation | Processing and future deductions/top-ups stop immediately; closure/refund follow the documented credit policy |
| Sandbox isolation | All test controls are rejected in Live before side effects; synthetic funding never calls a payment processor |

## Evidence to retain

Record the environment, contract SHA-256/revision, operational profile ID/version, test scenario, request IDs, resource IDs and observed results. Retain redacted assertions and counts; do not store API keys, provider credentials, full identity files or signed capability URLs in test logs.

## Client recovery exercise

Run the example to completion, interrupt it after command acceptance, and resume it with the same state. Independently reconcile its package, evidence, monitor, deal snapshot and billing entries. Verify both a business and a consumer fixture; applicability and missing values must remain explicit rather than forcing a business metric into consumer underwriting.

Use two distinct workspaces and both Sandbox/Live test contexts for isolation tests. Use separate Owner, Dev and Analyst users for console permission checks, and independently scoped API keys for programmatic checks. UI visibility never substitutes for server authorization.

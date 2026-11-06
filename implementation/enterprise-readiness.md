# Enterprise implementation acceptance

The single `/v1` API now specifies discoverable admission/processing limits, byte-bounded result views, complete multipart exports, client compatibility and the complete source/verification/financial data model. These are implementation requirements. Public pages describe the intended product behavior; this internal file records what must be demonstrated before runtime sign-off.

## Source of truth and changes

`scale_contract.py` extends the canonical generator without adding endpoints. `scale_guides.py` derives matching guides, navigation, profiles and fixtures. Run the existing generator before importing console Data Lookup. `x-response-views` carries the exact typed summary/section examples used by Data Lookup; it is documentation metadata, not an additional wire field.

The new export-link request uses `ExportDownloadPurpose`, retaining the original required purpose and adding optional part_number. The original DownloadPurpose used by document downloads remains unchanged. Completed Export.artifact and new configuration properties are part of this approved specification update. The previous contract is not served as a second API. Future changes must pass the compatibility review, with semantically disruptive changes explicitly coordinated.

## Required implementation invariants

- Atomically resolve accepted idempotent commands before new admission limits. Atomically reserve capacity, store receipt and enqueue new work. No receipt/resource/debit on pre-admission rejection.
- Share HTTP and workload budgets across all keys and replicas. Scheduled monitoring capacity failure creates an observable skipped run; no successful refresh timestamp changes.
- Persist cumulative queue and running time across restarts; pause only explicit credit/action waits. Capture the admission profile. Deadline termination cannot race with a successful package/debit publication.
- Freeze each package's collection ordering. A section cursor binds package, section, authorization and expiry. Check UTF-8 envelope bytes before sending headers; never send a partially serialized successful JSON response.
- Capture a data bootstrap checkpoint even if its first record cannot fit. Its snapshot ID, feed cursor, as-of and expiry must refer to one atomic boundary. Preserve source access and original payload through exact-record/snapshot exports.
- Materialize exports using streaming serialization with a frozen authorized snapshot and a fixed part size. Atomically publish a complete artifact only when part count, total bytes, rows and hashes reconcile. Part boundaries are arbitrary bytes. No multipart-upload-style financial commands are exposed.
- Check permissions at creation, publication, link issuance and download. An access change fails an unfinished export instead of silently omitting rows. Expired artifacts cannot issue links. A renewed link never changes immutable artifact bytes.
- Serve byte ranges with correct strong ETag, Content-Range, Content-Length and identity encoding. Never forward institution credentials to a storage host.
- Retain original source precision in normalized financial fields. Money and billing semantics remain distinct. Preserve missingness, licensing and KYC/KYB evidence provenance in all representations.

## Runtime evidence gate

Use `enterprise-acceptance.json` to agree the representative workload and required cases before running an environment. At minimum, exercise one million source records, high-fan-out corporate ownership/screening observations, simultaneous institution workers, worker crashes and database failover. Use synthetic or specifically authorized fixtures and a controlled non-production environment. Record target volume and burst duration separately from observed throughput. Preserve contract/profile hashes and redacted request IDs with every result.

Run long enough to cover normal processing, provider delays, retry windows, cursor expiry, export interruption and monitoring recovery. Measure throughput, p95/p99 latency, backlog age, CPU/memory, errors and recovery time. Compare with the agreed allocation and recovery objectives. Verify zero missing records, duplicate charges and cross-tenant disclosures. Complete the provider mappings against licensed fixtures; the Current sample still does not establish non-empty regulatory branches.

`validate-enterprise-evidence.py` rejects missing cases, failed cases, unrun evidence, invalid measurements and missing artifacts. It validates evidence completeness, not the truth of externally supplied measurements. A reviewer must inspect the actual logs and reconcile counts. The current status is **not run** because no product backend or provisioned performance environment is being exercised in this documentation task.

## Automated checks

Run the OpenAPI/example, product, risk-package, verification, client and enterprise-scale tests. `test-enterprise-scale.py` executes interrupted/resumed byte transfers, corrupt-part recovery, cursor errors and compatibility changes against the public helpers. Check generated output for drift and reimport the console catalog with `--check`. Mintlify validation and broken-link checks must pass. These automated checks are contract/client evidence only.

"""Publish enterprise client behavior and a unified model index from the contract."""
import json
import re
from pathlib import Path
from current_api_guides import page
from product_api_review import ROOT
from scale_contract import REVISION

CAPACITY_GUIDE='''Read `GET /v1/configuration` before starting workers. Its `operational_profile` contains the effective request, concurrency, queue, payload, export and retention limits for your workspace and environment. All keys share those limits. The [downloadable profile](/downloads/development-profile.json) contains synthetic test values; it is not your production allocation.

## Separate HTTP requests from background processing

| Limit | What it controls | At capacity |
| --- | --- | --- |
| `rate_limits` | Requests per rolling window, grouped into reads, commands and uploads | `429 rate_limited` |
| `capacity.max_in_flight_requests` | Simultaneous HTTP requests across all keys | `429 capacity_exceeded` |
| `capacity.workloads[].max_running` | Executing Origination, monitoring or export work | Ready work enters the bounded queue |
| `capacity.workloads[].max_queued` | Accepted ready jobs waiting for execution in that group | New commands receive `429 queue_full` before acceptance |
| `max_queue_wait_seconds` | Cumulative time an admitted job spends ready but waiting | That job fails with `queue_wait_exceeded` |
| `max_processing_seconds` | Cumulative running wall time including provider waits and internal retries | That job fails with `processing_deadline_exceeded` |

Every `429` includes `Retry-After` in whole seconds. Capacity errors also identify the group, reason, effective limit and profile revision. Back off for at least that delay, add jitter, and retain the same payload and idempotency key. Do not increase concurrency in response to throttling. Global service overload returns retryable `503` and does not establish acceptance.

Admission, durable command receipt and queue reservation are atomic. Resolve an existing idempotent receipt before applying fresh admission limits: an already accepted command remains the same resource during saturation. A rejected new command creates no resource, receipt or debit. A timeout is ambiguous; follow [request recovery](/api-reference/request-recovery) before submitting anything else.

Queue and running timers pause only while the resource is explicitly waiting for borrower action or credits. They do not restart on internal retry. On resumption, work re-enters the ready queue under its original accepted profile and remaining timer budgets. Existing ready work is not displaced by a later capacity reduction. No partial risk package is published as a successful result after a processing timeout. Insights charges only on atomic result publication. Signal's existing monthly charge is not a per-run charge and its billing rules remain unchanged.

For scheduled Signal work, record a monitoring run even when admission fails. A capacity-blocked scheduled evaluation is a `skipped` run with a structured capacity failure and a normal run notification; it cannot silently advance successful-sync timestamps. Future permitted evaluations continue on the configured cadence. Monitor enrollment uses the monitoring capacity group; source collection required by an Origination is part of its Origination job. Export work uses the export group. Limits apply independently to each group.

## Plan a portfolio import

1. Read the profile and choose a shared, bounded worker pool. Coordinate workers across application replicas and API keys.
2. Persist a durable institution work queue before sending commands. One intended action has one stable idempotency key.
3. Keep HTTP concurrency below `max_in_flight_requests` and request rates below each rolling budget. Leave capacity for status, receipt, event and billing reconciliation reads.
4. Consume completion events and periodically reconcile the durable feed. Poll only within the configured intervals.
5. Use snapshot exports for history and incremental data changes for ongoing updates. Do not repeatedly redownload a borrower's complete history.
6. Track throttled requests, queue failures, oldest unfinished work, cursor expiry and source freshness independently.

For a page size of 100, one million records require at least 10,000 collection reads before any detail fetches. This is arithmetic, not a throughput promise. Exports reduce HTTP request volume and [byte-part downloads](/api-reference/large-results) bound transfer memory.

## Processing targets and changes

`capacity.targets` supplies environment-specific p95 and/or p99 elapsed-time targets and the measurement window. Exactly one capacity entry exists for each workload group; target pairs of group and percentile are unique. Targets cover admitted ready work from first queue entry to terminal state, excluding explicit credit/action pauses and including provider waiting while running. Timeouts and processing failures count as misses; they are never removed to improve a percentile. These are configured objectives, not observed latency measurements or guarantees that every provider completes.

Capture profile ID/version when commands are accepted. Queue deadlines and artifact part sizes remain bound to that profile. Request budgets use the currently effective profile. An administrator coordinates disruptive allocation changes through your registered technical contacts using the notice period returned in `configuration.contract`. Immediate authorization revocation and security containment take precedence. The [SLA](/support/sla) defines availability and support obligations separately.
'''

LARGE_GUIDE='''Use `GET /v1/risk-packages/{id}` with the representation that fits your task. These views are part of the same endpoint and describe the same immutable package.

| Request | Response |
| --- | --- |
| No `view`, or `view=full` | Complete `RiskPackage` under `data`, subject to the JSON byte limit |
| `view=summary` | `RiskPackageSummary`: IDs, completeness, evidence-set ID, section names/counts and export source |
| `view=section&section=verification.screenings&limit=100` | Typed section items, complete section metadata and ordinary `page` metadata |

`section`, `cursor` and `limit` are valid only with `view=section`; section is required in that view. Unsupported names or parameter combinations return `400 validation_error`. Use the section names returned in the summary. The OpenAPI declares the exact item schema for every section, including financial analyses, policy results, sources and KYC/KYB observations.

```bash
curl --fail-with-body --max-time 30 \\
  "${AMLOK_API_BASE_URL}/v1/risk-packages/${RISK_PACKAGE_ID}?view=section&section=verification.screenings&limit=100" \\
  --header "Authorization: Bearer ${AMLOK_API_KEY}"
```

Persist `page.next_cursor` only after committing that page. Keep the package and section unchanged. `page.has_more` determines completion; a short page does not. Cursors expire at `page.expires_at`, bind authorization and freeze array order at package publication. After `410`, restart that section and deduplicate by package/section and original item identity or array position. No item is added, replaced or omitted because a newer assessment exists.

For structured sections, `section_metadata` contains the original status, coverage and limitations with only `items` separated for pagination. For plain arrays it is null. `total_items` is the complete section count. An empty array is not a successful verification: read its status and coverage. A summary does not contain a lending recommendation or substitute for reviewing required actions and limitations. Full-only objects such as submitted application/product/policy definitions remain in the complete package or export.

## Byte limits and exact oversized records

`max_response_bytes` limits uncompressed UTF-8 JSON, including its envelope. Collection and section pages may contain fewer items than requested to fit that limit. They must make progress or fail explicitly. The server does not replace populated fields with null, truncate arrays, or skip an oversized record.

If a full package or one indivisible record cannot fit, the response is `413 response_too_large`. Its `error.recovery.export_request` is a typed request for `POST /v1/exports`. The recovery object identifies an exact immutable package/record, evidence set or frozen data snapshot. `snapshot_expires_at` tells you when to submit a snapshot-based export; null means the source is an immutable record/package rather than a collection cursor. Exporting requires the existing export scopes and underlying source permissions. A large response never grants broader access.

For collected-data bootstrapping, begin with `limit=1` to capture the snapshot and its change cursor, then export that snapshot and consume changes after ingestion. If even the first record exceeds the limit, the 413 recovery also supplies `data_checkpoint` with snapshot ID, as-of time, changes cursor and expiry. Persist it before exporting. The change cursor represents the same atomic snapshot boundary, so no changes are missed.

The API also accepts `kind: data` with `data_record_id` instead of `data_snapshot_id` for an exact oversized record. Use exactly one. JSON retains the DataExport envelope with one row; `snapshot_id` identifies the immutable export snapshot. No request reruns underwriting or recollects data.

## Complete, resumable exports

After export completion, `Export.artifact` identifies one complete immutable file:

- `total_bytes`, `sha256`, `mime_type` and `schema_version` describe the full file.
- `part_size_bytes` and `part_count` define its byte layout. `part_count = ceil(total_bytes / part_size_bytes)`.
- `row_count` counts top-level exported records; it is one for a risk package.
- `source_snapshot_id` identifies a pinned collection/report snapshot, or is null for a single immutable package/record.

Request `POST /v1/exports/{id}/download-links` with `purpose` and a one-based `part_number`. Omit the number only to retrieve part 1. The response adds artifact ID, part number, byte offset, byte length and a strong ETag. Its SHA-256 covers that part. Every non-final part has `part_size_bytes`; the final part contains the remaining bytes.

Download parts in order to a file or streaming parser and verify each hash and the complete artifact hash. Parts are byte segments, not independently parseable JSON/CSV/PDF files. Boundaries can split Unicode sequences or CSV rows. Preserve decoder/parser state across parts; never load the complete export into memory just to join it.

Each signed HTTPS URL supports a single `Range: bytes=<offset>-` within that part and `If-Match` with the returned ETag. Expect `206`, validate `Content-Range`, and append only matching bytes. A full `200` must restart that part rather than append. `412` means the ETag does not match; `416` means the requested range is outside the part. Use `Accept-Encoding: identity` so offsets and hashes describe the transferred bytes. Do not send the AMLOK API key to signed download URLs or follow redirects to another host.

Renew expired links using the same export and part number with a new idempotency key for each intentional link issuance. Retrying one issuance keeps its key. The artifact ID, layout and hashes remain unchanged. Authorization is rechecked for every link and transfer; revocation can invalidate previously issued links. After export retention ends, link issuance returns `410 export_expired`. An out-of-range part returns `422 invalid_export_part`.

The server freezes authorized source membership at acceptance and retains that snapshot through export construction. An access change before publication fails the export instead of silently changing its row count. Download authorization still applies to completed files. `max_export_bytes` caps the complete file; larger jobs fail with `export_too_large` and never report a partial artifact as completed. Reduce scope using connection/resource filters on a new data snapshot, a narrower billing window, or exact-record exports. No export failure incurs an additional product charge.

The [reference transfer helper](/downloads/enterprise-client.py) validates page progress, resume state, offsets and file integrity. Its [synthetic fixtures](/downloads/enterprise-examples.json) illustrate summary, section, capacity and multipart responses.
'''

COMPATIBILITY='''AMLOK exposes one public API under `/v1`. `configuration.contract.revision` identifies the published contract; `meta.schema_version` identifies a response's schema revision. These values are diagnostic and do not select a second API or a legacy endpoint set. File-format, normalized-definition, metric-catalog, calculation and record versions have separate meanings.

## Safe client behavior

Parse fields you use, preserve exact decimal strings and opaque IDs, and ignore additional response object fields. Validate known fields and their documented types. Do not reject an otherwise valid response merely because an additive field appears. An older schema's `additionalProperties: false` describes that exact published revision, not a rule to reject future additive response fields in a long-lived client. Use the current OpenAPI for strict conformance checks in CI.

Requests remain strict. Send only documented fields; unknown request properties produce validation errors. New request fields are optional and retain existing behavior when omitted. New response fields do not change the meanings of existing fields or make an old request invalid.

Enums are closed within this contract. New enum values, new union/discriminator variants, changed units, removed fields, new required request fields, changed null semantics and altered existing calculations are not additive changes. They require explicit institution coordination before activation. In particular, do not silently add a verification outcome, event type or new section value and assume generated clients will accept it. Keep unknown values in diagnostic storage and route them to review; never coerce an unknown state to approved, complete or no-hit.

## Change communication

Compatible field additions are published in the canonical OpenAPI and reflected in Data Lookup and examples together. Record the contract revision in integration diagnostics and compare the current contract during your release checks. The [contract compatibility check](/downloads/check-contract-compatibility.py) detects wire removals, changed constraints and enum/union changes. It deliberately requires review of semantic changes; a passing structural diff is not proof that field meaning stayed the same.

Disruptive behavior, schema or operational allocation changes require notice to registered technical contacts at least `configuration.contract.change_notice_days` before their agreed activation. Use the actual configured agreement value; the example value is synthetic. Never replace an institution's active incompatible contract without coordinated acceptance. Credential revocation, consent withdrawal and urgent security containment can take effect immediately. This policy does not weaken authorization or extend retained data past cancellation.

Historical risk packages, source records, pinned policies/calculations and export artifacts remain immutable. Corrections create new versions or linked records; they never rewrite an older result. Adding a new calculated metric requires a new catalog/calculation definition, applicability rules, evidence, and coordinated client acceptance if it changes a closed key set.

## Version responsibilities

| Value | Meaning |
| --- | --- |
| `/v1` | Single public routing contract |
| `configuration.contract.revision` | Published contract identity for diagnostics and release review |
| `meta.schema_version` | Response-envelope schema revision |
| `operational_profile.id/version` | Effective allocation, deadlines and retention interpretation |
| `record_version` | Resource state or immutable source-record revision |
| `catalog_version` / calculation version | Exact metric definitions and computations used |
| Verification `definition_version` | Normalized KYC/KYB field definitions |
| Export `schema_version` and artifact hash | Downloaded file interpretation and integrity |

The institution remains responsible for testing its client against changed fields and the [integration checklist](/api-reference/integration-acceptance) before enabling new behavior.
'''

MODEL='''The API exposes one model through three related representations: current collected data, frozen assessment evidence, and the underwriting or monitoring risk package. The [OpenAPI contract](/openapi/amlok.json) defines wire types; the references below explain meaning and provenance.

| Reference | What you retrieve | Dictionary |
| --- | --- | --- |
| Collected integration records | `DataRecord.normalized`, selected by `resource_type` and `normalized.object` | [Source field dictionary](/data-model/field-dictionary): 957 field definitions |
| Detailed KYC/KYB assessment | `RiskPackage.verification` or `normalized.assessment` for `verification_assessment` | [Verification field dictionary](/api-reference/verification-fields): 860 field definitions across 25 observation sections |
| Financial assessment | `RiskPackage.dimensions`, `analyses`, policies, findings and required actions | [Underwriting dimensions](/api-reference/underwriting-dimensions): 24 families and 184 metrics |
| Frozen assessment input | `Evidence.normalized` and exact data-record/document references | [Evidence traceability](/api-reference/evidence-traceability) |
| Shared transport and monetary types | Envelopes, errors, cursor pages, amounts and exports | [Shared types](/data-model/shared-types) |

The source and verification dictionaries contain **1,817 separately identified field definitions**. This is a dictionary count, not a count of populated fields on every borrower. Shared structures, optional observations and source entitlements determine each response. The 860 verification definitions supplement the original source dictionary; they are not another API. Console **Data Lookup** uses these same definitions and the same operation schemas.

## Follow the relationships

A borrower identifies a business or person subject. Each authorized connection supplies immutable DataRecord versions. An Origination binds the submitted application, document IDs, exact lending-product/risk-policy versions and effective connections. Its RiskPackage records computed dimensions, detailed verification and an evidence set referencing the precise inputs. Signal creates later packages linked to monitoring runs and lender deal snapshots; earlier packages remain unchanged.

`DataRecord.id` identifies one immutable version; `resource_id` identifies the logical normalized record and `record_version` its sequence. Evidence links to the exact data-record version used. Related people have their own subject IDs and must remain associated with the authorized parent business. A provider search candidate is an observation, not automatically the resolved borrower entity.

[Entities](/data-model/entities) describes the source resource families and the detailed verification assessment. [Relationships](/data-model/relationships) describes joins and integrity. [Data access](/api-reference/data-access) explains snapshot/bootstrap/change-feed synchronization.

## Interpret values correctly

- Required means required for a valid resource when it exists; it does not promise that every provider supplies every field.
- Null is not zero, false or no-hit. Read missing reasons and section coverage. An empty collection must be interpreted with its source/query state.
- `Money` uses two decimals for application/deal and billing contracts. Source-normalized amounts retain documented source precision and currency; see [normalization rules](/data-model/normalization-rules).
- Source-provided, institution-declared, document-extracted and derived facts retain distinct provenance. See [field mappings](/data-model/field-mappings) and [derived attributes](/data-model/derived-attributes).
- Coverage is conditional on country, source product, consent and licensing. [Provider coverage](/data-model/provider-coverage) and [resource coverage](/data-model/resource-coverage) describe catalog capabilities, not proof that a particular check ran.

## Build for large datasets

Use [bounded result views and resumable exports](/api-reference/large-results), [capacity discovery](/api-reference/enterprise-operation), [client compatibility](/api-reference/client-compatibility) and the [integration checklist](/api-reference/integration-acceptance). Complete authorized data remains accessible without exposing internal enrichment jobs.
'''

def write_guides(spec,f,index):
 pages=[('enterprise-operation','Operate at enterprise volume',CAPACITY_GUIDE),('large-results','Retrieve large results and exports',LARGE_GUIDE),('client-compatibility','Maintain client compatibility',COMPATIBILITY)]
 for name,title,body in pages:page('api-reference/'+name,title,title+' with bounded capacity, explicit contracts and recoverable client behavior.',body)
 page('data-model/start-here','Data model','Find the complete source, financial and KYC/KYB model and understand its API representations.',MODEL)
 nav=json.loads((ROOT/'docs.json').read_text());tab=next(t for t in nav['navigation']['tabs'] if t['tab'].lower()=='api reference')
 group=next(g for g in tab['groups'] if 'api-reference/operating-profile' in g.get('pages',[]))
 for name,_,_ in pages:
  path='api-reference/'+name
  if path not in group['pages']:group['pages'].append(path)
 (ROOT/'docs.json').write_text(json.dumps(nav,indent=2)+'\n')
 (ROOT/'downloads/development-profile.json').write_text(json.dumps(f['Configuration']['operational_profile'],indent=2)+'\n')
 additions={
 'api-reference/operating-profile.mdx':'## Concurrency, deadlines and transfer limits\n\n`capacity` defines shared HTTP concurrency, bounded workload queues and processing targets. `max_response_bytes`, `max_export_bytes`, `export_part_bytes` and `max_page_items` define transport limits. Follow [enterprise operation](/api-reference/enterprise-operation) and [large results](/api-reference/large-results).',
 'api-reference/rate-limits.mdx':'## Admission pressure\n\nEvery 429 includes Retry-After. `capacity_exceeded` and `queue_full` include typed capacity details. All keys share the allocation. See [capacity and queue behavior](/api-reference/enterprise-operation).',
 'api-reference/risk-package.mdx':'## Bounded representations\n\nUse `view=summary` for a compact section index and `view=section` with section/cursor/limit for typed paged observations on the same endpoint. Complete packages remain available through full reads and exports. See [large results](/api-reference/large-results).',
 'api-reference/export-formats.mdx':'## Transfer layout\n\nCompleted exports expose `artifact` metadata. Request a link for each `part_number` and concatenate verified bytes in order; individual parts are not standalone JSON or CSV. See [resumable transfers](/api-reference/large-results) for hashes, Range handling, renewal, access changes and byte limits.',
 'api-reference/data-access.mdx':'## Large-record recovery\n\nCollections are bounded by both items and bytes. An oversized indivisible record returns a typed export source; it is never skipped. Bootstrap errors preserve an atomic data checkpoint. See [large results](/api-reference/large-results).',
 'api-reference/response-format.mdx':'## Evolving clients\n\nIgnore additional response object fields while validating known fields and types. Request objects remain strict and enums remain closed. See [client compatibility](/api-reference/client-compatibility).',
 'api-reference/downloads.mdx':'## Enterprise clients\n\n- [Bounded paging and export-transfer helper](/downloads/enterprise-client.py)\n- [Contract compatibility checker](/downloads/check-contract-compatibility.py)\n- [Synthetic enterprise responses](/downloads/enterprise-examples.json)\n- [Enterprise operation](/api-reference/enterprise-operation)\n- [Large-result retrieval](/api-reference/large-results)',
 'api-reference/runnable-example.mdx':'## Large datasets\n\nThis journey exercises a small synthetic package and obtains the first export-part capability. A completed export can contain multiple parts; use artifact.part_count and the [enterprise transfer helper](/downloads/enterprise-client.py) for the complete file. For large datasets, use [summary/section views and oversized-response recovery](/api-reference/large-results).',
 'api-reference/integration-acceptance.mdx':'## Volume and compatibility exercises\n\nRun your agreed sustained and burst workload with representative business/consumer data. Verify bounded workers, 429 admission recovery, queue deadlines, every risk-section cursor, oversized records, multipart transfer interruption and authorization revocation. Reconcile exact input/output counts, hashes and charges. Record achieved throughput, p95/p99 latency and recovery time against your effective profile. Test additive response fields and explicit handling of unknown states. Keep source-provider latency separate from AMLOK queue/processing time. The [enterprise guide](/api-reference/enterprise-operation) defines these behaviors.',
 'data-model/shared-types.mdx':'## Source precision and large results\n\n`Money` is the two-decimal application/deal type. `NormalizedMoney` and source-normalized amount fields retain the precision allowed by their field schema; these are different types. Billing values use the billing rounding policy. `RiskPackageSummary`, typed `RiskPackageSection` variants, `ExportArtifact` and `ExportDownloadLink` support [bounded retrieval](/api-reference/large-results). Detailed KYC/KYB fields use the [verification dictionary](/api-reference/verification-fields).',
 'data-model/field-dictionary.mdx':'## Complete model references\n\nThis page documents the original 957 source-field definitions. The additional 860 detailed KYC/KYB fields are in the [verification dictionary](/api-reference/verification-fields). Read the [model index](/data-model/start-here) for their relationship to DataRecord, Evidence and RiskPackage. Resource prefixes identify the normalized object: a bank transaction amount is `data.normalized.amount.amount` on Get data record, or `data[].normalized.amount.amount` on List data records.',
 'data-model/entities.mdx':'## Detailed verification assessment\n\n`verification_assessment` is the additional normalized resource for complete KYC/KYB results. `DataRecord.normalized.assessment` and `RiskPackage.verification` share `VerificationAssessment`. Its 25 observation sections preserve individual subjects, sources, coverage and documents. The earlier `verification` and `verification_check` resource definitions describe source-level summaries/checks; they do not replace this aggregate. See the [complete model index](/data-model/start-here).',
 'data-model/relationships.mdx':'## Assessment and verification links\n\nBorrower `subject_id` identifies its business/person. `RiskPackage.verification` aggregates authorized observations for that subject and related subjects. `EvidenceSummary.data_record_id` resolves an immutable DataRecord version, while `resource_id` plus `record_version` identifies the underlying logical record revision. Verification source references preserve exact evidence/data-record IDs and document/page locations. These links never authorize cross-workspace or unrelated-person access. See [KYC/KYB results](/api-reference/verification).',
 }
 for file,body in additions.items():
  p=ROOT/file;content=p.read_text();heading=body.split('\n')[0]
  if heading in content:content=content[:content.index(heading)].rstrip()+'\n'
  p.write_text(content.rstrip()+'\n\n'+body+'\n')
 # Correct a pre-existing envelope shorthand without changing source definitions.
 p=ROOT/'data-model/field-dictionary.mdx';p.write_text(p.read_text().replace('`data.amount.amount` in a bank transaction record','`data.normalized.amount.amount` in a Get data record response'))
 examples={'contract_revision':REVISION,'synthetic':True,'profile':f['Configuration']['operational_profile'],'views':{}}
 for path,methods in spec['paths'].items():
  for op in methods.values():
   for response in op['responses'].values():
    for media in response.get('content',{}).values():
     for name,v in media.get('x-response-views',{}).items():examples['views'][op['operationId']+':'+name]=v['example']
 (ROOT/'downloads/enterprise-examples.json').write_text(json.dumps(examples,indent=2)+'\n')

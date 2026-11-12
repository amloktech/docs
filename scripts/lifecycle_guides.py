"""Final customer-guide alignment for shared identity and independent product journeys.

Run after the contract and all existing guide writers. Targeted replacements preserve
unrelated guidance; marked additions are idempotent for hand-maintained Console pages.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARK = 'BORROWER LIFECYCLE'


def replace(path, old, new):
    p = ROOT / (path + '.mdx')
    if not p.exists():
        return
    body = p.read_text()
    if old in body:
        p.write_text(body.replace(old, new))


def section(path, body):
    p = ROOT / (path + '.mdx')
    if not p.exists():
        return
    current = p.read_text()
    block = '{/* BEGIN ' + MARK + ' */}\n' + body.strip() + '\n{/* END ' + MARK + ' */}'
    pattern = r'\{/\* BEGIN ' + MARK + r' \*/\}.*?\{/\* END ' + MARK + r' \*/\}'
    current = re.sub(pattern, lambda _: block, current, flags=re.S) if re.search(pattern, current, re.S) else current.rstrip() + '\n\n' + block + '\n'
    p.write_text(current)


def page(path, title, description, body, short=None):
    p = ROOT / (path + '.mdx')
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text('---\ntitle: ' + json.dumps(title) + '\nsidebarTitle: ' + json.dumps(short or title) + '\ndescription: ' + json.dumps(description) + '\nkeywords: ["borrowers", "lifecycle", "Insights", "Signal", "identity"]\n---\n\n' + body.strip() + '\n')


def write_guides(spec, f, index):
    catalog = json.loads((ROOT / 'data/sandbox-catalog.json').read_text())
    page('api-reference/borrower-lifecycle', 'Manage borrower identity and product journeys',
         'Register and reuse borrower profiles, correct identity safely, start underwriting or portfolio monitoring, and preserve assessment history.', '''
A borrower is the shared business or person profile you use to collect authorized inputs and associate product work. Register it before opening the Integrations Hub or uploading its documents. Registration does not verify identity, submit an application, start monitoring or create a product usage charge.

## Choose the product journey

| Goal | Sequence | Result |
| --- | --- | --- |
| Underwrite a new application | Register or reuse borrower, collect credit-assessment inputs, submit Origination | An Insights risk package and its frozen evidence |
| Monitor an existing funded portfolio | Register or reuse borrower, collect continuous-monitoring inputs, submit Monitor with `baseline.portfolio` | Signal evaluations, risk packages and alerts, without an Insights Origination |
| Monitor a deal underwritten by AMLOK | Reuse borrower and completed package, confirm continuous-monitoring authority, submit Monitor | Signal evaluations linked to the chosen baseline |
| Assess a business's owner or guarantor | Register the related person and include a typed participant with authorized evidence in the parent product request | Participant coverage and findings inside the parent result |

A borrower can have no product activity yet, several applications, and several monitored facilities. Its profile state cannot represent all those product states. The Console's [shared Borrowers directory](/console/borrowers) is accessible from both Origination and Portfolio.

## Register once and reuse the ID

Use [Create borrower](/api-reference/endpoints/borrowers/create-borrower), supplying your stable `client_reference` when available. Save both returned identifiers:

| Identifier | Use |
| --- | --- |
| `Borrower.id` (`bor_…`) | `borrower_id` on Hub sessions, documents, applications, monitors, data queries and billing usage |
| `Borrower.subject_id` (`biz_…` or `person_…`) | The canonical business/person identity in verification and billing `subject_id` fields |
| `DataRecord.id` | One immutable collected-data version |
| `DataRecord.resource_id` / `normalized.id` | A logical source-normalized record, identified together with its resource type and version |
| `application.institution_reference` | Your stable application identity across explicit assessment attempts |
| `deal.institution_reference` | Your stable funded-facility identity for a Monitor |

Use `GET /v1/borrowers?client_reference=...` to find an existing profile before creating another. Client-reference uniqueness is within the selected environment and borrower type. Names are not unique and are never sufficient to merge profiles. A new reference creates a separate identity, even if its name matches another record.

There is no public merge or delete operation. Correct the existing profile when it represents the same legal identity. If duplicate IDs already have financial or assessment history, contact support to resolve them without rewriting that history. Do not create duplicates to restart an application or monitoring service.

## Correct current identity

Retrieve the borrower and retain its `ETag`. Call `PATCH /v1/borrowers/{id}` with `borrowers:write` and the returned `If-Match` value. The body can contain a full replacement `profile`, a `lifecycle_status`, or both.

The profile uses the same business/person shape as Create borrower. Keep its type and stable client reference. Omitting the client reference from a replacement retains the current reference; it does not erase it. A stale ETag returns `412 precondition_failed`. Read the latest representation, reconcile the change, and retry with its new ETag.

`record_version` changes when the resource changes. `profile_version` identifies changes to identity content. `updated_at` records the latest update. Archival alone does not create a new identity revision.

An accepted Origination keeps `borrower_snapshot` and `borrower_profile_version`; editing today's profile does not change that assessment. A Monitor retains enrollment identity, while each new evaluation pins the current authorized identity into its resulting package. Previously published risk packages and evidence remain immutable.

## Separate retries from new assessments

A timeout retry uses the original payload and `Idempotency-Key`. Recover accepted work through [request receipts](/api-reference/request-recovery) and continue following the existing Origination ID.

To reassess the same application after its latest attempt is `completed`, `failed` or `cancelled`, send a new `POST /v1/originations` with:

- The same primary borrower and `application.institution_reference`.
- `supersedes_origination_id` identifying the latest terminal attempt.
- The intended current application, configuration and evidence inputs.
- A new idempotency key for this new assessment command.

The response has a new Origination ID and incremented `attempt_number`. A prior attempt still in progress returns `409 invalid_state`; cancel it first if the application is withdrawn. Each successfully completed Insights attempt is priced independently. A new idempotency key alone does not authorize a duplicate or reassessment.

To withdraw unfinished underwriting, call `PATCH /v1/originations/{id}` with its current `If-Match` and `{"status":"cancelled"}`. Completed or failed results cannot be cancelled. Cancellation stops pending processing; it does not erase history or reverse a completed charge. An unfinished cancelled assessment creates no assessment charge.

## Archive abandoned intake

Set `lifecycle_status` to `archived` through the borrower PATCH. Every associated Origination must be terminal and every associated Monitor must be stopped, including associations as a participant. Otherwise the API returns `409 invalid_state`.

Archival cancels unfinished Hub sessions, stops pending source collection and rejects new Hub sessions, borrower document uploads, originations and monitors. Historical records remain available subject to current access authorization. Archiving is neither consent revocation nor deletion.

Restore with `{"lifecycle_status":"active"}` and the latest ETag. Restoration does not restart cancelled sessions or stopped products. Create a fresh Hub session for any needed collection or reauthorization, then explicitly resume monitoring or submit the intended new assessment attempt.

Collection starts only through an authorized source journey; a saved profile alone does not schedule collection. Hub intake is bounded collection, not a perpetual refresh subscription. Signal handles configured recurring evaluations while active. Registering a profile or completing intake does not create an Insights or Signal consumption entry. See your agreement for any provider-specific commercial terms; [usage records](/api-reference/consumption-reporting) identify actual product charges.

## Consent, history and retention

Use the [consent revocation endpoint](/api-reference/endpoints/connections/revoke-consent) to withdraw source authorization. Current consent and source access are checked again for source-backed results, data, evidence and exports, including historical records. An immutable result is not a promise of indefinite access to restricted source content.

Archive, revoke consent and remove retained data are distinct actions. The public API does not promise an automatic deletion schedule or expose a purge command. Retention and any authorized removal follow your applicable agreement and support process; do not infer a retention period from an archived state.

Test both product paths with the [independent Sandbox scenarios](/api-reference/sandbox-journeys), and use [Data Lookup](/console/data-lookup) for the fields and exact endpoint contracts.
''', 'Borrower lifecycle')

    # Keep the overview honest about two independent products and mutable identity.
    p = ROOT / 'api-reference/overview.mdx'
    body = p.read_text()
    diagram = '''```mermaid
flowchart LR
    B[Shared borrower profile] --> H[Authorized Hub collection and documents]
    H --> I[New application: Insights Origination]
    H --> S[Funded portfolio: Signal Monitor]
    I --> R[Underwriting risk package]
    R --> D[Institution decision and funding]
    D --> S
    P[Existing funded deal and portfolio baseline] --> S
    S --> M[Monitoring runs, packages and alerts]
```'''
    body = re.sub(r'```mermaid\n.*?```', lambda _: diagram, body, count=1, flags=re.S)
    body = body.replace('Product records cannot be edited or deleted; authorized configuration changes apply prospectively.', 'Historical assessments and evidence are immutable. Current borrower identity and monitoring configuration have explicit, versioned updates; see [borrower lifecycle](/api-reference/borrower-lifecycle).')
    p.write_text(body)
    section('api-reference/quickstart', '''
## Reuse identity and choose the next product

Before registering another borrower, look up its stable `client_reference`. One identity can support multiple application attempts and monitored deals. [Borrower lifecycle](/api-reference/borrower-lifecycle) explains corrections, reassessment, withdrawal and archival.

For an existing funded portfolio, skip the Origination step and [enroll Signal directly](/api-reference/monitoring-design) with `baseline.portfolio`. Use a **Monitoring integration** key and continuous-monitoring source authorization. You do not need an Insights purchase or its scopes for this path.
''')

    page('api-reference/related-person-verification', 'Submit related parties and authorized evidence',
         'Include owners, controllers and guarantors in a business assessment with declared roles, permitted purposes and separately authorized supporting evidence.', '''
Use typed participants to include a related business or person in the primary borrower's assessment. Register each identity through the borrower endpoint, collect its own authorized sources and documents, then associate it with the parent request. A related profile is not a separate paid underwriting.

## Submit a participant

For Insights, include `application.participants`. For Signal, prefer top-level `participants`. When onboarding a portfolio, omitted top-level participants uses `baseline.portfolio.application.participants` if supplied. If both lists are supplied, their participant definitions must agree; conflicting lists are rejected rather than silently selecting one. The portfolio application's nonempty `related_borrower_ids` must match the admitted participant IDs. Every participant supplies:

| Field | Meaning |
| --- | --- |
| `borrower_id` | Its distinct active profile in the same workspace and environment |
| `roles` | One or more of `owner`, `controller`, `guarantor`, `related_party` |
| `ownership_share` | Declared decimal-string percentage from 0 to 100, or null; not a verified ownership conclusion |
| `authority` | `basis: institution_attested`, a nonfuture `attested_at`, and the permitted `purposes` |
| `connection_ids` | This participant's sources with active consent for the product purpose |
| `document_ids` | Available borrower-context documents owned by this participant |

Insights requires `credit_assessment`; Signal requires `continuous_monitoring`. Institution attestation does not replace provider consent and does not prove the declared relationship. Cross-borrower sources, inaccessible documents, duplicate participants and the primary borrower repeated as a participant are rejected.

The optional `application.related_borrower_ids` is a correlation list. If nonempty, it must exactly match the typed participant IDs. An ID by itself cannot request verification or establish authority. Put participant sources and files inside that participant, not the primary borrower's `connection_ids` or `document_ids`.

### Example participant list

Use this array as `application.participants` for Insights or top-level `participants` for Signal. All identifiers are synthetic: replace them with the registered guarantor's borrower ID and that same person's authorized connection and available document IDs. Supply your actual attestation time and only the purposes for which you hold authority. This example includes both purposes to illustrate reuse across products; each source still needs active consent for the product being requested.

```json
[
  {
    "borrower_id": "bor_guarantor_synthetic",
    "roles": ["guarantor"],
    "ownership_share": null,
    "authority": {
      "basis": "institution_attested",
      "attested_at": "2026-10-15T12:00:00Z",
      "purposes": ["credit_assessment", "continuous_monitoring"]
    },
    "connection_ids": ["con_guarantor_synthetic"],
    "document_ids": ["doc_guarantor_synthetic"]
  }
]
```

Use an empty `connection_ids` or `document_ids` array when you are supplying no sources or files of that kind. Empty evidence does not imply successful verification; inspect the returned coverage, outcome and limitations. `institution_attested` records your institution's assertion of authority, not proof of the relationship or a provider-verified identity.

## Inspect the outcome

The accepted product resource pins each participant's `borrower_snapshot` and `borrower_profile_version`. The risk package's `participants` array carries roles, declared ownership, authority, `subject_id`, `verification_status`, `verification_outcome`, `evidence_ids` and limitations. Retrieve the bounded `participants` risk-package section when you need that part alone.

Read coverage and outcome separately. Missing evidence can yield `unavailable` and `not_performed`; incomplete evidence must not be presented as successful identity verification. Source observations and provenance support the finding. A declared percentage remains a declaration unless supported by authorized evidence.

The parent business remains the product's billing borrower and subject. Related-party checks are included in that assessment, with no standalone participant-verification charge.

## Continue into monitoring

When creating a Monitor from a baseline risk package, omitted `participants` reuses the baseline participants but validates continuous-monitoring authority and source consent again. Use `[]` to explicitly select no participants, or supply a complete participant list authorized for monitoring. Prior credit-assessment consent alone is insufficient.

A Monitor PATCH can replace the future participant list with ETag protection. New evaluations pin their current authorized identity and evidence; previous packages remain unchanged. See [borrower lifecycle](/api-reference/borrower-lifecycle) and [Signal monitoring](/api-reference/monitoring-design).
''', 'Related parties')

    replace('api-reference/monitoring-design', 'Stopped is terminal.', 'A stopped Monitor can be explicitly reactivated with `status: active` after current prerequisites pass; reuse its ID and facility reference.')
    replace('api-reference/processing-lifecycle', 'stopped is terminal and rejects future changes or lender snapshot submissions.', 'stopped halts scheduling. Explicitly set it active to re-enroll the same facility after validating current prerequisites.')
    section('api-reference/monitoring-design', '''
## Start without a previous underwriting

A Signal-only integration registers or reuses the borrower, obtains `continuous_monitoring` consent, uploads the funded facility's documents, and creates the required product and policy versions. Submit `POST /v1/monitors` with `baseline.portfolio`, containing `lending_product_version_id`, `application` (the supplied application or null when unavailable), and `document_ids`. Supply the funded `deal`, `risk_policy_version_id`, `cadence_id` and authorized `connection_ids` as usual.

This path creates monitoring and its baseline result without creating an Origination or an Insights charge. A Monitor can instead use `baseline.risk_package_id`; the two baseline forms are mutually exclusive. Only choose a package your current key and product entitlement can access.

Supply related parties through top-level `participants`, or through `baseline.portfolio.application.participants` when the top-level list is omitted. If both are present, they must describe the same participants; a conflicting empty list does not silently discard submitted parties. Nonempty application `related_borrower_ids` must match those participants. Every admitted party needs continuous-monitoring authority and authorized evidence. See [related parties](/api-reference/related-person-verification).

## Recover and re-enroll the same facility

Retrieve the Monitor, resolve its `requirements` or `failure`, and obtain the latest ETag. Use `PATCH /v1/monitors/{id}` with `If-Match` and `{"status":"active"}` to resume `paused`, `requires_action`, `waiting_for_credits` or `failed`, or re-enroll `stopped`. Activation validates the active borrower, current product access, documents, policy and continuous-monitoring consent, then schedules evaluation durably. It does not invent a successful result or bypass missing prerequisites.

For changed sources, replace `connection_ids` with the full desired future source set. Reauthorize through the Hub first when consent is absent or revoked. Restore an archived borrower before resuming. Pausing or stopping fences pending publication; subsequent work cannot publish a package or charge against that suspended evaluation. Prior completed packages and charges remain unchanged.

## Find the same activity across resources

Use `GET /v1/monitors?institution_reference=...` with the facility's `deal.institution_reference`. Filter monitoring runs using `borrower_id` or `monitor_id`; each run returns its primary `borrower_id`. The corresponding events carry that borrower reference, so `GET /v1/events?borrower_id=...` can correlate product activity. Keep pagination filters unchanged while following a cursor.
''')
    replace('api-reference/processing-lifecycle', 'Use PATCH with If-Match for future policy, cadence, connection set or active/paused/stopped state. Active is accepted only after server validation of consent, required inputs and funding; otherwise return 409 invalid_state with the unresolved reason and retain state. failed cannot be resumed: correct the cause and enroll a new monitor. Unchanged identical configuration does not increment version or emit an event.', 'Use PATCH with If-Match for future policy, cadence, connections, participants or active/paused/stopped state. Activation validates current identity, consent and required inputs, then schedules an evaluation on the same Monitor. Invalid inputs, revoked authorization or unresolved requirements reject the change. Funding is checked before publication; insufficient credits leave evaluation waiting without an unfunded charge. A successful update returns the current resource version; use that version for later updates.')
    replace('api-reference/processing-lifecycle', '| cancelled | Workspace cancellation ended unfinished work |', '| cancelled | An authorized cancellation ended unfinished work |')
    section('api-reference/processing-lifecycle', '''
## Identity and assessment attempts

The borrower profile, Origination attempt and Monitor are separate resources. Read [borrower lifecycle](/api-reference/borrower-lifecycle) for identity revisions and archive/restore behavior.

An unfinished Origination can be withdrawn using its ETag and `PATCH /v1/originations/{id}` with `status: cancelled`. To reassess after the latest completed, failed or cancelled attempt, reuse the application reference and borrower, provide `supersedes_origination_id`, and send a new command key. The new attempt is independently priced on successful completion. Transport retries and open `requires_action` / `waiting_for_credits` states continue the existing attempt.

A failed or blocked Monitor resumes through `PATCH` to `active` after the cause is resolved. A stopped Monitor can also be explicitly re-enrolled on the same ID and facility reference. Activation schedules recovery; its response is not itself a completed evaluation. Read the [Signal recovery sequence](/api-reference/monitoring-design#recover-and-re-enroll-the-same-facility).
''')
    replace('api-reference/documents', 'For changed application information after submission, create a new origination with a new command identity; do not modify the historical application.', 'For changed application information, finish or cancel the existing attempt, then create a new Origination using the same application reference, `supersedes_origination_id` and a new command key; do not modify the historical application.')
    section('api-reference/documents', '''
## Identity, participants and archived intake

Upload initial borrower documents before submitting the assessment and associate returned IDs with the correct identity. Related-party files use that participant's own `borrower_id` and appear in its typed `participants[].document_ids`. The primary borrower's document list cannot borrow another person's files. Participant files must be available when submitted.

An archived borrower rejects new uploads. Restoration permits new intake but does not alter previous files or assessment evidence. Archival is not file deletion; no automatic purge period is implied. Follow your agreement and support process for retained-data requests.
''')
    section('api-reference/integration-hub', '''
## Prepare inputs without starting a product

A registered profile can collect authorized intake before underwriting or portfolio enrollment. Hub completion starts bounded collection; it does not submit an Origination, enroll a Monitor or create product consumption. Recurring monitoring requires an active Signal enrollment and appropriate `continuous_monitoring` consent.

Archiving the borrower cancels unfinished Hub sessions and stops pending ingestion. A restored profile needs a fresh session for further collection. Closing or archiving intake does not itself revoke existing consent. Use explicit revocation when authorization must be withdrawn. [Borrower lifecycle](/api-reference/borrower-lifecycle) separates these actions.
''')
    section('api-reference/data-access', '''
## Shared identity and ongoing access

Use the primary or participant's `bor_…` ID when a query requires `borrower_id`; `subject_id` and normalized source resource IDs are different namespaces. Data access does not require a completed Origination or a Monitor, but it still requires currently authorized sources, purposes and entitlements.

An archived profile has no ongoing intake collection. Archival does not erase retained records or grant continued source access after consent withdrawal. Use [borrower lifecycle](/api-reference/borrower-lifecycle) for restore, revocation and retention boundaries.
''')
    section('api-reference/connection-recovery', '''
## Restart collection and monitoring

If the source is failed or needs renewed authorization, complete a fresh borrower-bound reauthorization session and confirm the source's returned state. That completion schedules source collection again. An archived borrower must be restored first; cancelled old Hub sessions are not reused.

For a failed, paused, blocked or stopped Monitor, resolve the source issue and then explicitly PATCH the Monitor to `active` using its current ETag. Updating the connection alone must not be interpreted as a completed monitoring evaluation.
''')

    section('api-reference/export-formats', '''
## Match permissions to the export source

In addition to `exports:write` to create an export, or `exports:read` to inspect it and request a download, the same key needs the source permission below:

| Export kind | Required source permission |
| --- | --- |
| `risk_package` | `results:read`, and access to the package's Insights or Signal product |
| `evidence` | `evidence:read` |
| `data` | `data:read` |
| `billing` | `billing:read` with current Owner billing authority |

Source authorization is checked when creating, preparing, retrieving and downloading the export. Losing a required permission, product entitlement or source authorization prevents subsequent access. A saved export ID or download link is not an access bypass. Risk-package access does not require `evidence:read` as a substitute for `results:read`.
''')
    section('api-reference/consumption-reporting', '''
## Correlate identity and assessment attempts

Billing usage and workload expose both `borrower_id` (the product's `bor_…` profile) and canonical `subject_id` (`biz_…` or `person_…`). Join product activity through `borrower_id`; use `subject_id` for the underlying identity. Historical entries retain their original rates and charges.

Each successfully completed Insights attempt is separate consumption, even when it supersedes an earlier attempt of the same institution application. Signal-only portfolio enrollment does not create an Insights charge. Signal retains its documented borrower/workspace/month billing rule; stopping and resuming a Monitor does not create a second charge for an already paid period. Related participants are included under the primary product borrower, not separately priced checks.

Profile registration and identity edits do not create product charges. Keep duplicate resolution separate from billing reconciliation; neither an edit nor archival rewrites an existing ledger entry.
''')
    section('data-model/api-alignment', '''
## Product identity and lifecycle

`Borrower.id` (`bor_…`) is the shared product identity used for intake, applications, monitors and billing `borrower_id`. Its canonical `subject_id` (`biz_…` / `person_…`) is the business or person used in verification and billing `subject_id`. Source-normalized business/person observations keep their own record identities and provenance.

The current profile has `lifecycle_status`, `profile_version`, `record_version` and update/archive timestamps. Origination identity is pinned at acceptance; monitoring packages pin identity at evaluation. Risk-package `participants` reports the submitted related parties, their authorized evidence, coverage and limitations. This does not turn declared roles or ownership percentages into verified facts.

See [borrower lifecycle](/api-reference/borrower-lifecycle) for reuse, corrections, explicit assessment attempts and archive/restore, and [related parties](/api-reference/related-person-verification) for the association contract.
''')
    section('api-reference/risk-package', '''
## Identity and related-party coverage

Read `borrower_snapshot` and `borrower_profile_version` for the primary identity actually used by this assessment. Current profile corrections do not rewrite that snapshot. `participants` reports each included related party's roles, declared ownership, canonical subject ID, accepted authority, verification availability/outcome, evidence and limitations. Use `view=section&section=participants` for that bounded section. Missing or unavailable party evidence is explicit, never an implied successful check.
''')
    section('api-reference/security', '''
## Versioned maintenance versus historical results

Authorized `borrowers:write` keys can correct or archive current identity with ETag protection. `insights:write` can cancel unfinished underwriting, and `signal:write` can change future monitoring configuration or resume eligible monitoring. These actions do not edit published packages, evidence or ledger history. Related-party authority is checked independently from the primary borrower; see [related parties](/api-reference/related-person-verification).
''')

    # Scenario guidance comes from the runtime catalog, including minimum per-journey scopes.
    sandbox = ROOT / 'api-reference/sandbox-journeys.mdx'
    text = sandbox.read_text().replace('2026-11-09.1', catalog['version'])
    text = text.replace('- Product journeys require `borrowers:read/write`, `configuration:read/write`, `connections:read/write`, `evidence:read/write`, `insights:read/write`, `signal:read/write`, `exports:read/write`, plus `data:read`, `results:read` and `events:read`.', '- Each catalog scenario declares `required_scopes`, `inspection_scopes` and `required_products`. Grant the scopes for the selected journey; a scenario does not require the other product unless it actually uses it.')
    text = text.replace('- Detailed product traces require the product read scopes and enabled Insights and Signal. Billing-only traces require Owner billing authority.', '- Detailed traces require the selected scenario\'s `inspection_scopes` and `required_products`. Underwriting-only traces do not require Signal; monitoring-only traces do not require Insights. Billing-only traces require Owner billing authority.')
    sandbox.write_text(text)
    selected = [s for s in catalog['scenarios'] if s['id'] in ('underwriting_only', 'monitoring_only', 'sample_pack')]
    table = '\n'.join('| `' + s['id'] + '` | ' + ', '.join('`' + p + '`' for p in s['required_products']) + ' | ' + s['expected'] + ' |' for s in selected)
    section('api-reference/sandbox-journeys', '''
## Test each product independently

Use **Origination integration** for `underwriting_only`: it creates the identity, authorized credit-assessment sources, documents, an Origination and result, without creating a Monitor. Use **Monitoring integration** for `monitoring_only`: it creates a funded-portfolio baseline, Signal Monitor and result, without creating an Origination. Each works with only its own product enabled.

| Scenario | Required products | Expected result |
| --- | --- | --- |
''' + table + '''

The complete `sample_pack` remains available with both products and Owner billing authority. It exercises six businesses plus simulated funding and consumption. Ordinary underwriting scenarios do not silently enroll Signal; monitoring scenarios use portfolio baselines. Export creation is exercised by the export scenarios and complete sample pack.

Read the catalog's `required_scopes` before executing or repeating a scenario. A key limited to `inspection_scopes` can inspect that completed trace but cannot initiate the run. The Console displays the same product and scope requirements under the selected scenario. Source revocation continues to restrict trace content.
''')
    replace('api-reference/authentication', 'Product scenarios may need both Insights and Signal scopes and enabled products.', 'The selected scenario declares its exact required scopes and products in the catalog. Underwriting-only and monitoring-only scenarios need only their own product; the full sample pack needs both.')
    section('console/sandbox', '''
## Choose one product or the complete pack

Choose **Underwriting only** to exercise Insights without monitoring, or **Monitor an existing funded business** to enroll an existing funded portfolio without underwriting. The selected case shows **Products used**, required API scopes and the scopes needed to inspect its run. Use those requirements when choosing an API key.

The complete sample pack includes both products and simulated billing. For independent API tests, use **Origination integration** or **Monitoring integration** as appropriate. Running a single-product scenario does not require enabling the other product. See the [scenario catalog and permissions](/api-reference/sandbox-journeys#test-each-product-independently).
''')
    replace('sandbox/businesses-and-scenarios', 'six fictional businesses and 30 executable scenarios', 'six fictional businesses and ' + str(len(catalog['scenarios'])) + ' executable scenarios')
    section('sandbox/businesses-and-scenarios', '''
## Verify independent product integration

The `underwriting_only` scenario stops after its Insights assessment. The `monitoring_only` scenario uses a funded portfolio baseline and creates Signal results without an Origination. These cases verify the minimum product access your integration needs. The complete `sample_pack` still demonstrates both products and billing across all six fictional businesses.

The catalog and Console show each scenario's required products, execution scopes and trace-inspection scopes. See [run reproducible Sandbox scenarios](/api-reference/sandbox-journeys).
''')

    # Console directory remains shared; update wording without discarding its troubleshooting.
    replace('console/borrowers', 'The table shows **Borrower**, **Type**, **Client reference**, **Registration number**, **Incorporation country** and **Created (UTC)**.', 'The table includes identity fields, **Profile status**, **Identity revision**, **Underwriting requests**, **Monitored deals** and **Created (UTC)**.')
    replace('console/borrowers', 'The borrower ID, subject ID, type, client reference, creation time, submitted profile and available linked records.', 'The borrower ID, subject ID, type, stable client reference, current profile, lifecycle state, identity revision, timestamps, underwriting count, monitored-deal count and active monitors.')
    section('console/borrowers', '''
## Correct or archive the profile

Owners and Developers can select **Edit profile** in the borrower drawer to correct current business or person details. The stable client reference and borrower type do not change. Saving creates a new identity revision; earlier accepted underwriting and published results retain their original identity snapshot. Analysts can review profiles but cannot change them.

Select **Archive profile** to close unused intake after all associated underwriting is terminal and all monitors are stopped. This also applies when the identity participates in another borrower's assessment. Archival stops new intake and cancels unfinished Hub sessions; it does not delete history or revoke consent. Select **Restore profile** to permit new intake again. Restoration does not restart old sessions or products.

If another teammate changes the record first, refresh and review the latest profile before saving again. The Console uses the same version checks and lifecycle rules as the [borrower API](/api-reference/borrower-lifecycle).

## Read activity separately from identity

**Active** means the profile can accept intake; it does not mean the borrower is approved or currently monitored. Underwriting and monitored-deal counts include primary-borrower and related-party participation, restricted to the products you can access. The drawer separately identifies activity as a related party, such as a guarantor. **Related records** links those applications and monitors and their participant roles. A new profile can have zero of both.

Use **View shared borrower profiles** from Origination or Portfolio to open this same directory in your selected workspace and environment. A monitoring-only borrower belongs here even when it has never had an underwriting request.
''')
    for name in ['origination', 'portfolio']:
        section('console/' + name, '''
## Open the shared identity profile

Select **View shared borrower profiles** to open [Borrowers](/console/borrowers) for the same workspace and environment. Registered profiles appear there before an application or monitored facility exists. The profile drawer separates current identity and lifecycle from underwriting requests and monitored deals. Owners and Developers can correct, archive or restore the profile without changing historical results.
''')

    # Navigation is patched last, after current_api_guides.navigation rewrites its groups.
    path = ROOT / 'docs.json'
    config = json.loads(path.read_text())
    tab = next(t for t in config['navigation']['tabs'] if t['tab'].lower() == 'api reference')
    group = next(g for g in tab['groups'] if g['group'] == 'Product guides')
    for entry in reversed(['api-reference/borrower-lifecycle', 'api-reference/related-person-verification']):
        if entry not in group['pages']:
            group['pages'].insert(0, entry)
    path.write_text(json.dumps(config, indent=2) + '\n')

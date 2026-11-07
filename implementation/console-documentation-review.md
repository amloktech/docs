# Console documentation review

Reviewed 2026-11-07. Customer-facing content is under `console/`; this file is excluded by `.mintignore`.

## Scope

Twenty task-based guides in a new Console tab, positioned after Documentation. Existing API Reference, Research and Documentation sections retain their content. The home card, introduction and Sandbox setup guide link into the new section. No application, API contract, infrastructure, production-data or email changes.

## Evidence

- Actual browser review of the isolated `demo.amlok.io` console, Demo Organization / Demo Workspace B / Sandbox.
- Twenty-six native 1280 x 720 JPEG screenshots in `images/console/`, without resizing, compositing or fabricated UI. Existing `images/sandbox/choose-starting-data.png` reused for the first-use choice.
- Source review in `amloktech/webapp`: identity settings, environment settings, billing settings, account security, invitation form, navigation, workspace catalog, tables, record drawers, case views, Hub builder, Data Lookup, Sandbox scenarios, resources and shared role policy.
- Existing Sandbox guides, API contracts and pricing rules remain the authorities for fixtures, operation semantics and commercial terms.

## Coverage

- Account invitation and self-registration, first-session sample/empty choice, preparation progress and first result.
- Organization/workspace/environment boundaries, Live activation, compact tables and drawers.
- Origination processing versus underwriting recommendation, monitoring, documents, verification and source evidence. Every primary drawer tab is documented individually: five in Origination and four in Portfolio, with screenshots, role boundaries, actions and empty/missing-data interpretation.
- Integrations Hub draft selection, markets, filtered category selection and API handoff.
- Scoped keys, incoming requests, outgoing events, Data Lookup and executable scenarios.
- Organization identity, product access, audit activity, scoped team invitations, personal and organization security.
- Simulated autopay and methods, funding/ledger/consumption/statement reconciliation, reports and complete-export boundaries.
- Troubleshooting and support trace information.

## Screenshots and data

Existing demo records were sufficient; no extra data needed to be seeded. No real customer records, new credentials, invitations, email messages or financial actions were created. Screenshots intentionally exclude secrets, authenticator setup and recovery codes. Financial images clearly identify simulation.

## Boundaries

Do not infer publication from Save draft in the Hub, retry from opening a request, or replay from opening a delivery. The guides use confirmed controls and link to API operations where execution is outside the UI. Table CSV export is not documented as a complete enterprise dataset. Customer guides exclude the internal admin app and infrastructure setup. Personal notification delivery, referral rewards, live assistant answers and unconnected service-health controls are not advertised as working features.

## Validation

- Mintlify validate: build and validation passed.
- Mintlify broken-links: no broken links.
- Navigation/page/image references: all new targets exist.
- Browser review: Console navigation, overview, onboarding steps, billing screenshot expansion and Data Lookup rendering. Follow-up covers all nine Origination/Portfolio tabs and their documentation sections.
- Git diff whitespace check: passed.

Changes are prepared on `codex/console-guides` for review; live deployment requires publication approval.

## Drawer guide follow-up

Captured seven additional native screenshots. Inspected all five Origination and four Portfolio tabs and the corresponding case-workspace source. Technical request/response tabs are Owner/Developer only. Captured origination JSON can wrap submitted inputs in `submitted_request`; it is not documented as a ready-to-submit POST body. Sparse metadata remains explicitly absent, and a connected source or generated event does not imply fresh data or successful delivery. No application or dataset changes.

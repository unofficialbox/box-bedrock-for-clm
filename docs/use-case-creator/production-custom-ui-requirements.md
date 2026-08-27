# Production Custom UI Requirements (CLM Use Case)

## 1) Purpose
Build a production-grade custom operator and business UI that operationalizes the CLM demo flows:
- Contract intake
- Automated extraction + clause comparison
- Human-governed AI recommendations
- Review and approval routing
- Salesforce record lifecycle orchestration
- Auditability, evidence, and operational visibility

The UI should make the demo flow usable in customer environments without requiring manual Box/Agentforce navigation.

## 2) Scope

### In Scope
- Operator and business workflows for one customer tenant.
- Two runtime modes:
  - **Mode A (Box-centric):** Box Automate-led orchestration with Box Forms, Extract, Hubs, Doc Gen/Sign, Salesforce handoff.
  - **Mode B (Cross-platform):** AgentCore-led orchestration coordinating Box + Agentforce + Databricks signals.
- Full task visibility with human-in-the-loop gates and structured audit trail.

### Out of Scope
- Replacing Box or Salesforce core UI.
- Core AI model development.
- Signature provider integration beyond delegated existing calls.
- Multi-tenant customer switching in first release (single-tenant first).

## 3) Users and Personas
- **Contract Requester (Sales/Procurement):** submit requests, upload redlines, review status.
- **Legal Reviewer:** validates AI risk recommendations, assigns legal reviewers, approves/rejects decisions.
- **Finance Reviewer:** validates commercial/compliance terms and pricing thresholds.
- **Operations Manager:** monitors workload, SLA, escalations, and throughput.
- **System Operator/Admin:** configures integrations, maps IDs and metadata, monitors health, manages roles.
- **Compliance/Audit:** validates policy enforcement, provenance, and approvals.

## 4) Core Functional Requirements by Workflow

### 4.1 Intake and Contract Creation
- Launch a **New Contract Request** flow from the home UI.
- Capture requester metadata, counterparty, opportunity, priority, contract type, effective/expiry dates, and attachments.
- Validate required fields before submit and prevent invalid submissions.
- Persist request in draft and submit states with request id.
- Persist supporting artifacts into target Box folders.

### 4.2 Workbench and Dashboard
- Role-aware dashboard with active requests, SLA status, high-risk queue, and approval backlog.
- Quick action tiles for start request, approvals, clause review, clause library, and executed contracts.
- Persistent filters and saved views by owner, status, risk, and aging.

### 4.3 Extraction and Clause Lifecycle
- Auto-synchronize clause library and show version context.
- Present AI-assisted clause extraction and redline difference candidates.
- Route high-risk clauses to required reviewer domains (Legal, Finance, Privacy, Security).
- Support side-by-side review and inline comments with escalation paths.

### 4.4 Approvals and Routing
- Human confirmation gates at each critical action:
  - post-extraction,
  - pre-document generation,
  - pre-signature.
- Approval actions: `Approve`, `Reject`, `Request Change`, `Escalate`, `Reassign`.
- Record reason, reviewer notes, and policy check result per action.

### 4.5 Salesforce Integration View
- Surface linked `CLM_Contract__c` state and related account/opportunity context.
- Expose sync state (`pending`, `synced`, `retrying`, `failed`) per object and per action.
- Enable deterministic retry actions and failure surfacing without direct destructive edits to governed records.

### 4.6 Evidence, Traceability, and Audit
- Show immutable activity history per contract.
- Attach AI recommendations to evidence (model, inputs, citations, timestamps).
- Provide one-click audit exports (JSON/CSV/PDF).
- Maintain evidence-only view for compliance review and legal hold as required.

### 4.7 Operator Configuration
- Configure tenant ids, approval rules, role mappings, policy thresholds.
- Dry-run mode for non-mutating config validation.
- Confirm-before-apply pattern for policy/model/permission changes.
- Display environment health and last successful validation timestamps.

### 4.8 Monitoring and Operations
- Health cards for queue depth, API quota usage, failures, and retries.
- Incident feed and alerting for degraded workflows.
- One-click manual recovery actions with audit logging.

## 5) Security, Reliability, and Compliance Requirements
- SSO + RBAC with least-privilege service accounts.
- No secrets visible in UI state, logs, or browser devtools.
- Tenant isolation for all persisted identifiers and tokens.
- Correlation IDs across UI, workflow calls, and downstream systems.
- Idempotent actions and bounded retries.
- P95 response time targets:
  - dashboard 2s,
  - record views 3s,
  - list/filter 2s.
- Accessibility baseline: WCAG 2.1 AA and keyboard-first paths.

## 6) Data and API Requirements

### UI-facing entities
- `ContractRequest` (id, status, type, counterparty, owner, priority, due date)
- `ContractArtifact` (folder, version, extracted clauses, redline payload)
- `Recommendation` (model source, rationale, risk score, required reviewers)
- `ApprovalRecord` (reviewer, decision, timestamp, notes, evidence)
- `AuditEvent` (actor, action, before/after, correlation id)

### Core endpoints
- `POST /contracts/requests`
- `GET /contracts/{id}`
- `POST /contracts/{id}/actions`
- `GET /contracts/{id}/audit`
- `GET /contracts/{id}/recommendations`
- `GET /contracts/{id}/events`

### Integration requirements
- Box folder + document operations + event callbacks.
- Salesforce record read/update operations and metadata mapping.
- Databricks/analytics signal retrieval (optional).
- AI output normalization into one recommendation schema.

## 7) UI Component Requirements by Section

| Section | Required Component Types | Why It Is Needed |
|---|---|---|
| Intake & Contract Creation | Multi-step wizard, form inputs, file upload, inline validation, confirmation modal, toast, breadcrumbs | Validate and capture complete intake with low friction. |
| Intake Workbench | Dashboard grid, KPI cards, charts, filter/search, paginated table, quick actions, drawers, alerts | Makes workflow state obvious and reduces click-depth. |
| Clause Lifecycle | Tabbed panels, diff viewer, expandable clause cards, risk summary panel, assignment modal, evidence links, exception table | Makes clause decisions transparent and governable. |
| Approval Queue | Queue table, inline action buttons, decision modal, policy status panel, timeline, filter menu | Keeps human governance enforceable and fast. |
| Salesforce Record Integration | Record cards, tabbed sections, sync badges, retry/open actions, sync-error modal, compact sync log | Keeps structured commercial truth visible without direct overwrite risk. |
| Evidence and Audit | Append-only timeline, evidence panels, event table, export actions, preview modal, version chips, audit search | Supports compliance and post-hoc review. |
| Operator Config | Sectioned forms, config tabs, masked secrets, policy builder, toggles, verify/apply/rollback buttons, logs table | Enables safe environment setup and change management. |
| Monitoring & Operations | Health cards, throughput/latency charts, failure charts, incident table, control actions, notification settings | Provides production-grade operational readiness. |
| Global Layout | Scenario switcher, role-aware nav, global search, command bar, version footer, loading and error states | Supports operators using one interface for both scenarios. |

### 7.1 Intake & Contract Creation Components
- Multi-step form shell
- Text/select/date/currency inputs
- Drag-and-drop uploader
- Inline validation and required-field banners
- Submit/save/draft action buttons
- Submit confirmation modal
- Change/discard modal
- Toast + confirmation panel

### 7.2 Workbench Components
- Sticky sidebar + two-column shell
- KPI cards
- Funnel/kanban chart, bar/line chart, status distribution chart
- Search + chip filters + date-range
- Sortable/paginated table with row actions
- Quick-action button grid
- Detail drawer/modal
- System alert banner

### 7.3 Clause Lifecycle Components
- Tabs for docs/extract/review
- Side-by-side diff viewer
- Expandable clause cards
- Risk badges and reviewer chips
- Collapsible AI summary area
- Assign-reviewer modal
- Exception table

### 7.4 Approval Components
- Queue table with SLA timers
- Decision button group
- Decision modal with reason code + comment
- Policy status panel
- Event timeline
- Filters by risk, owner, and age
- Status/priority badges

### 7.5 Salesforce Integration Components
- Record summary cards
- Read-only record tabs (Commercials, Terms, Approval, History)
- Sync status badges
- Retry + Open-in-Salesforce actions
- Failure details modal
- Sync attempt list

### 7.6 Evidence and Audit Components
- Append-only activity timeline
- Evidence cards and links
- Correlation/event table
- Export toolbar
- Evidence preview modal
- Schema/version badges
- Audit search and filters

### 7.7 Operator/Administration Components
- Config forms by domain
- Tabbed config sections
- Secret status cards (masked)
- Rule-builder grid
- Toggle controls
- Verify/Generate Report/Reload/Rollback controls
- Read-only config viewer (copy/download)
- Apply/Rollback confirmation modals
- Filterable logs table

### 7.8 Monitoring Components
- Health metric cards
- Trend charts
- Failure-by-category chart
- Incident list/table
- Pause/retry/escalate controls
- Notifications modal

### 7.9 Global Navigation and UX Components
- Scenario mode switcher
- Role-aware sidebar
- Global search with suggestions
- Command quick actions
- Environment/version footer
- Empty-state templates
- Skeleton/loading placeholders
- Error boundary fallbacks

## 8) Delivery Phases

1. **MVP:** intake + dashboard + approval + audit baseline.
2. **M1:** clause comparison, routing, and evidence visibility.
3. **M2:** cross-platform orchestration mode and operational analytics.
4. **M3:** hardened operations controls and production observability.

## 9) Acceptance Criteria
- Request can be submitted end-to-end with clear status visibility.
- Every recommendation is linked to evidence and assigned reviewer ownership.
- No high-risk action executes without human confirmation.
- Failed actions are recoverable without data loss.
- Audit export can be generated in one action.
- Operators can validate environment health with a documented runbook in a bounded workflow.

# Box App Blueprint: Contract Lifecycle Management

## App Name

`Contract Lifecycle Management`

## Live Build Inputs

| Input | Value |
|-------|-------|
| Workspace | `CLM-2026-Northstar` |
| Workspace folder ID | `399081692991` |
| Shared link | `https://kadams.ent.box.com/folder/399081692991` |
| Live spec | `config/box/box-app-dashboard-live-spec.json` |
| Builder checklist | `config/box/box-app-builder-checklist.md` |
| Metadata templates | `clmContract`, `clmDocument`, `clmObligation`, `clmClause` |

## Sections

### 1. Quick Actions & Portfolio

| Block | Source |
|-------|--------|
| Document Approval Status donut | `clmDocument.approvalStatus` |
| Document Risk Profile donut | `clmDocument.clauseRisk` |
| Documents by Type bar | `clmDocument.documentType` |
| Contract Package Status bar | `clmDocument.versionStatus` |
| Approved Clause Hub shortcut | `https://kadams.ent.box.com/hubs/1312630996` |
| Start a New Contract form | Published `New Contract Request` form, open in a new tab |
| Executed Agreements shortcut | Folder `399080706253` |

Use two equal chart columns. Keep approval and risk in the first row, document type and package status in the second row, and the Hub, Form, and executed-agreement actions together in the same top dashboard section.

### 2. Northstar Deal Room

| Card | Target |
|------|--------|
| Contract Workspace | `CLM-2026-Northstar` root folder `399081692991` |
| Redline Risk Review | `northstar-msa-redline-v3.pdf` file `2342633195167`, task `42899891150` |
| Commercial Mismatch | `northstar-order-form.pdf` file `2342633259967`, task `42899881417` |
| Privacy and Security Review | `northstar-dpa.pdf` file `2342633156726`, task `42899893550`; `northstar-security-exhibit.pdf` file `2342636075017` |
| Obligation Register | `07 - Obligations` folder `399081567921` |

### 3. Intake and Actions

| Block | Purpose |
|-------|---------|
| Pending approvals table | Filter `approvalStatus = Pending` |
| Critical risk view | Filter `clauseRisk = Critical` |

The Form is intentionally not repeated here. `Start a New Contract` in the top section is the single intake entry point.

### 4. Executed Agreements and Renewals

| Block | Purpose |
|-------|---------|
| Executed agreements table | Filter `status = Executed` |
| Renewal calendar | Sort by `noticeDeadline` |
| Insurance reminders | Filter `obligationType = Insurance` |

### 5. Clause Library Page

| Block | Purpose |
|-------|---------|
| Approved Standards | Metadata-backed view of approved standard clauses |
| Clause Source Files | Open governed Markdown source folder `399419341582` |
| Open Approved Clause Hub | Open Hub `1312630996` |
| Standard vs Fallback | Donut from `clmClause.position` |
| Clauses by Family | Donut from `clmClause.clauseFamily` |
| Clause Approval Status | Donut from `clmClause.approvalStatus` |

## Dashboard Tone

Make the Box App feel like an operational dashboard, not a sparse file browser. Use status/risk charts, workstream cards, and action blocks so the low-maturity demo feels complete without custom code.

## Manual Build Boundary

The live Box workspace, metadata, uploaded files, tags, descriptions, review tasks, Form, Hub, and dashboard are published. The Box App builder remains a browser-only maintenance boundary; the CLI does not expose a dashboard-builder command. Use `config/box/box-app-builder-checklist.md` when rebuilding or changing the live layout.

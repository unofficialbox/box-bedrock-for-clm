# Box App Blueprint: Contract Lifecycle Management

This is a portable layout specification. Bind it to the folders, files, metadata templates, Form, and Hub created in the target environment. Do not record target-environment App, page, folder, or file identifiers here; keep those in runtime state or audit receipts.

**Structure verified:** 2026-07-22, by read-only browser inspection of the live Home and Clause Library pages.

The App uses two pages. Page order and block order below match the verified live layout.

## Page 1 - Home

### 1. Quick Actions & Portfolio

Section header: `Quick Actions & Portfolio`. Place the action row above the charts.

| Order | Block | Type | Subtitle | Source |
|---:|---|---|---|---|
| 1 | Start a New Contract | Form action | Submit a governed intake request and contract package | Published `New Contract Request` Form |
| 2 | Clause Hub | Link | Standards, approved fallbacks, owners, and review cadence | Target environment's published Clause Hub |
| 3 | Executed Agreements | Link | Signed contracts, obligations, and renewal-ready records | Generated `06 - Executed Agreement` folder |
| 4 | Document Approval Status | Donut | - | `clmDocument.approvalStatus` |
| 5 | Document Risk Profile | Donut | - | `clmDocument.clauseRisk` |
| 6 | Documents by Type | Bar | - | `clmDocument.documentType` |
| 7 | Contract Package Status | Bar | - | `clmDocument.versionStatus` |

Use three action cards in one row, then two equal chart columns. Do not add a second Form block.

The action block is named `Clause Hub`, not `Approved Clause Hub`. The Clause Library page uses the longer `Open Approved Clause Hub` for the equivalent link.

### 2. Northstar Deal Room

Section header: `Northstar Deal Room`. One full-width card list, in this order:

1. Generated contract workspace folder
2. Order form PDF
3. MSA redline PDF
4. DPA PDF
5. Security exhibit PDF
6. Generated obligations folder

### 3. Intake and Actions

Section header: `Intake and Actions`.

| Block | Type | Filter |
|---|---|---|
| Pending High-Risk Reviews | Table | `clmDocument.approvalStatus = Pending` and `clmDocument.clauseRisk in (High, Critical)` |

Columns: Name, Document Type, Version Status, Clause Risk, AI Summary Status, Approval Status, Signature Status, Location, Content Modified, Updated.

This is one combined table. Earlier revisions of this blueprint specified a separate pending-approvals table and critical-risk view; the live App merges both into this single block. Keep the merged form unless the owner asks to split it.

### 4. Executed Agreements and Renewals

Section header: `Executed Agreements and Renewals`.

| Block | Type | Source |
|---|---|---|
| Executed agreements folder card | Card | Generated `06 - Executed Agreement` folder |
| Open Obligations | Table | `clmObligation.status = Open` |

Columns: Name, Obligation Type, Owner, Due Date, Source Clause, Status, Reminder Window Days, Location, Content Modified, Updated.

No renewal-calendar block exists in the live App. Add one sorted by `noticeDeadline` only on owner request; do not treat its absence as a defect.

## Page 2 - Clause Library

Section header: `Approved Clause Library`

Description: `Governed standard and fallback language, ownership, review cadence, and usage signals for deal teams.`

| Order | Block | Type | Subtitle | Source |
|---:|---|---|---|---|
| 1 | Approved Standards | Metric card | Approved language with current owners and review dates. | Approved `clmClause` standard positions |
| 2 | Clause Source Files | Folder card | Standards, fallbacks, and governance notes in governed Box folders. | Generated Approved Clauses folder |
| 3 | Open Approved Clause Hub | Link | Published standards, approved fallbacks, owners, and review cadence | Target environment's Hub |
| 4 | Standard vs Fallback | Donut | - | `clmClause.position` |
| 5 | Clauses by Family | Donut | - | `clmClause.clauseFamily` |
| 6 | Clause Approval Status | Donut | - | `clmClause.approvalStatus` |

Three action cards in one row, then two equal chart columns. `Approved Standards` displays the approved clause count as its metric.

## Chart consistency invariants

These must hold in any bound environment. They are structural, not fixture-specific.

- Every Home document chart resolves to the same document total: `Document Approval Status`, `Document Risk Profile`, `Documents by Type`, and `Contract Package Status`.
- `Pending High-Risk Reviews` row count equals the High plus Critical slices of `Document Risk Profile` that are also Pending.
- Every Clause Library chart resolves to the same clause total: `Standard vs Fallback`, `Clauses by Family`, and `Clause Approval Status`.

## Known presentation defects

Open items observed in the live App on 2026-07-22. None are layout errors; all affect presenter quality.

| Defect | Detail | Suggested fix |
|---|---|---|
| App name carries build scaffolding | Live title is `Contract Lifecycle Management` plus a `-<timestamp>` suffix | Rename to `Contract Lifecycle Management` before presenting |
| Single-category donut | `Clause Approval Status` renders 100 percent Approved as a solid ring | Seed one non-approved clause, or drop the block |
| Flat bar chart | `Documents by Type` renders every type at 1, so all bars are identical | Seed a second document of one type, or drop the block |
| Truncated labels | `Documents by Type` clips `Order For...` and `Security E...`; action card subtitles and the executed-agreements card title clip at desktop width | Shorten labels or widen the blocks |
| Obligation naming | `Open Obligations` shows the folder name in its Name column rather than an obligation title | Give obligation records a descriptive name |

## Tone and boundary

Make the App feel operational: representative metadata, clear ownership, visible work, useful charts, and convenient actions. Box Apps construction remains browser-only; obtain approval immediately before publishing.

## Build and validation

1. Create **Contract Lifecycle Management** from the generated workspace. Do not leave a build timestamp in the App name.
2. Put the three quick actions first and keep them visible without scrolling.
3. Use two equal chart columns; drag and resize blocks instead of building a long single column.
4. Set the description to `Operational CLM cockpit for governed intake, document risk, approvals, approved clauses, execution, and renewal readiness.`
5. Preview at desktop width, save, and obtain owner approval immediately before publishing.
6. Verify exactly one Form action, working Hub and folder links, non-empty charts, generated deal-room items, filtered pending work, and all Clause Library blocks.
7. Verify the chart consistency invariants above and confirm no chart renders a single category or all-equal bars.
8. Confirm the deal-room and review tables reference the intended MSA sample file version.

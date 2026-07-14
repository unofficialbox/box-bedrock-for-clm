# Box App Blueprint: Contract Lifecycle Management

This is a portable layout specification. Bind it to the folders, files, metadata templates, Form, and Hub created in the target environment.

## 1. Quick actions and portfolio

Place the action row above the charts.

| Block | Source |
|---|---|
| Start a New Contract | Published `New Contract Request` Form |
| Approved Clause Hub | Target environment's published Clause Hub |
| Executed Agreements | Generated `06 - Executed Agreement` folder |
| Document Approval Status | Donut, `clmDocument.approvalStatus` |
| Document Risk Profile | Donut, `clmDocument.clauseRisk` |
| Documents by Type | Bar, `clmDocument.documentType` |
| Contract Package Status | Bar, `clmDocument.versionStatus` |

Use two equal chart columns. Do not add a second Form block.

## 2. Northstar Deal Room

Add cards for the generated workspace, MSA redline, order form, DPA, security exhibit, and obligations folder.

## 3. Intake and review

- Pending approvals table: `clmDocument.approvalStatus = Pending`.
- Critical risk view: `clmDocument.clauseRisk = Critical or High`.
- Task-bearing documents represent Legal, Finance, Privacy, and Security work when a task-specific block is unavailable.

## 4. Executed agreements and renewals

- Executed content: generated `06 - Executed Agreement` folder.
- Renewal calendar: sort contract metadata by `noticeDeadline`.
- Obligations: `clmObligation.status = Open`.

## 5. Clause Library page

| Block | Source |
|---|---|
| Approved Standards | Approved `clmClause` standard positions |
| Clause Source Files | Generated Approved Clauses folder |
| Open Approved Clause Hub | Target environment's Hub |
| Standard vs Fallback | Donut, `clmClause.position` |
| Clauses by Family | Donut, `clmClause.clauseFamily` |
| Clause Approval Status | Donut, `clmClause.approvalStatus` |

## Tone and boundary

Make the App feel operational: representative metadata, clear ownership, visible work, useful charts, and convenient actions. Box Apps construction remains browser-only; obtain approval immediately before publishing.

## Build and validation

1. Create **Contract Lifecycle Management** from the generated workspace.
2. Put the three quick actions first and keep them visible without scrolling.
3. Use two equal chart columns; drag and resize blocks instead of building a long single column.
4. Set the description to `Operational CLM cockpit for governed intake, document risk, approvals, approved clauses, execution, and renewal readiness.`
5. Preview at desktop width, save, and obtain owner approval immediately before publishing.
6. Verify exactly one Form action, working Hub and folder links, non-empty charts, generated deal-room items, filtered pending work, and all Clause Library blocks.

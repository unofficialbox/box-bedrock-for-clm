# CLM Box Web UI Build Queue

Use this file when the Codex task must run from this subdirectory:

`/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm`

The Box CLI and browser-only Box UI builds are complete. The Box Form and Box App dashboard are published, and their URLs are recorded in `config/box/live-box-surface.json`. Retain this queue as the live build specification and validation checklist.

## Open These Pages

| Surface | URL |
|---------|-----|
| Box Apps | https://kadams.ent.box.com/app |
| Box Forms | https://kadams.ent.box.com/automate/forms |
| CLM workspace | https://kadams.ent.box.com/folder/399081692991 |

If the Box Apps or Box Forms URLs redirect, use the Box left navigation or Admin Console search to open `Apps` and `Forms`.

## URL Update Helper

After publishing the App and Form, update the live manifest from this directory:

```bash
python3 update-box-web-urls.py --app-url '<published-clm-app-url>' --form-url '<published-clm-form-url>'
```

## Build Order

1. Build the CLM Box Form.
2. Build the CLM Box App dashboard.
3. Publish both.
4. Update `config/box/live-box-surface.json` with the published URLs.
5. Re-run the primary demo from `docs/runbooks/04-box-agentforce-react-demo.md`.

## New Contract Request Form

| Item | Value |
|------|-------|
| Form name | `New Contract Request` |
| Destination folder | `CLM-2026-Northstar / 01 - Intake` |
| Destination folder ID | `399082115646` |
| Root workspace | `399081692991` |
| Published URL target | `config/box/live-box-surface.json -> boxFormUrl` |

Fields:

| Label | Type | Required | Options / Notes |
|-------|------|----------|-----------------|
| Requester name | Short text | Yes | Demo default: `Jordan Lee` |
| Requester email | Email | Yes | Demo default: `jordan.lee@acmerobotics.example` |
| Counterparty | Short text | Yes | Demo default: `Northstar Health System` |
| Contract type | Dropdown | Yes | `MSA Package`, `DPA`, `SOW`, `Order Form`, `Procurement Agreement` |
| Deal value | Number | Yes | Demo default: `2400000` |
| Region | Dropdown | Yes | `US`, `EU`, `APAC`, `Global` |
| Data category | Dropdown | Yes | `None`, `Personal Data`, `PHI`, `Financial Data`, `Confidential` |
| Target signature date | Date | Yes | Demo default: `2026-07-31` |
| Business owner | Short text | Yes | Demo default: `Account Executive` |
| Upload contract package | File upload | Yes | Destination: intake folder |
| Special terms / risk notes | Long text | No | Use for redline and approval triggers |

## Contract Lifecycle Management App

| Item | Value |
|------|-------|
| App name | `Contract Lifecycle Management` |
| Primary workspace | `CLM-2026-Northstar` |
| Workspace folder ID | `399081692991` |
| Workspace URL | `https://kadams.ent.box.com/folder/399081692991` |
| Published URL target | `config/box/live-box-surface.json -> boxAppUrl` |

Sections:

| Section | Blocks |
|---------|--------|
| Quick Actions & Portfolio | Two-column chart rows: `Document Approval Status` donut from `clmDocument.approvalStatus`; `Document Risk Profile` donut from `clmDocument.clauseRisk`; `Documents by Type` bar from `clmDocument.documentType`; `Contract Package Status` bar from `clmDocument.versionStatus`. The same top dashboard section includes `Approved Clause Hub`, the single `Start a New Contract` Form block, and `Executed Agreements` shortcut. |
| Northstar Deal Room | Folder/file cards for workspace `399081692991`, MSA redline `2342633195167`, order form `2342633259967`, DPA `2342633156726`, security exhibit `2342636075017`, obligation folder `399081567921` |
| Intake and Actions | Document table from `clmDocument` filtered to pending high/critical risk. Do not add a second Form block; `Start a New Contract` is the sole dashboard intake action. Live UI note: this Box Apps builder exposes no task-specific block, so the task-bearing review documents represent tasks `42899891150`, `42899881417`, and `42899893550`. |
| Executed Agreements and Renewals | Folder view for `399080706253`; obligations table from `clmObligation` filtered to `status = Open` |

Clause Library page:

| Block | Source |
|-------|--------|
| Approved Standards | `clmClause`, filtered to approved standard positions |
| Clause Source Files | Folder `399419341582` |
| Open Approved Clause Hub | Hub `1312630996` |
| Standard vs Fallback | Donut from `clmClause.position` |
| Clauses by Family | Donut from `clmClause.clauseFamily` |
| Clause Approval Status | Donut from `clmClause.approvalStatus` |

## Live IDs

| Object | ID |
|--------|----|
| Workspace | `399081692991` |
| Intake folder | `399082115646` |
| Executed agreement folder | `399080706253` |
| Obligations folder | `399081567921` |
| MSA redline | `2342633195167` |
| DPA | `2342633156726` |
| Order form | `2342633259967` |
| Security exhibit | `2342636075017` |
| Legal review task | `42899891150` |
| Finance review task | `42899881417` |
| Privacy/security review task | `42899893550` |

## Validation Checklist

| Check | Expected Result |
|-------|-----------------|
| App opens | Dashboard loads without custom code |
| Form submits | New request lands in folder `399082115646` |
| Deal room cards | Cards open live folders/files and review artifacts |
| Pending reviews | Shows legal, finance, and privacy/security tasks |
| Portfolio charts | Shows approval, clause-risk, document-type, and version-status breakdowns from live `clmDocument` metadata |
| Action row | Opens the single published intake Form, Hub `1312630996`, and executed-agreement folder `399080706253` |
| Clause Library page | Shows the approved view, source folder, Hub shortcut, and three live clause-metadata charts |
| URL manifest | `boxAppUrl` and `boxFormUrl` are populated in `config/box/live-box-surface.json` |

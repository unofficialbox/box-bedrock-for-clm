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
| Metadata templates | `clmContract`, `clmDocument`, `clmObligation` |

## Sections

### 1. Contract Overview

| Block | Source |
|-------|--------|
| Contract pipeline table | `clmContract` metadata |
| Risk status donut | `riskLevel` |
| Status chart | `status` |
| Target signature date view | `targetSignatureDate` |

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
| New Contract Request form | Launch intake form |
| Pending approvals table | Filter `approvalStatus = Pending` |
| Critical risk view | Filter `clauseRisk = Critical` |

### 4. Executed Agreements and Renewals

| Block | Purpose |
|-------|---------|
| Executed agreements table | Filter `status = Executed` |
| Renewal calendar | Sort by `noticeDeadline` |
| Insurance reminders | Filter `obligationType = Insurance` |

## Dashboard Tone

Make the Box App feel like an operational dashboard, not a sparse file browser. Use status/risk charts, workstream cards, and action blocks so the low-maturity demo feels complete without custom code.

## Manual Build Boundary

The live Box workspace, metadata, uploaded files, tags, descriptions, and review tasks are already created. The Box App dashboard itself still needs to be assembled in Box Apps through the Box web UI; the CLI does not expose a dashboard-builder command. Use `config/box/box-app-builder-checklist.md` as the click-by-click build checklist.

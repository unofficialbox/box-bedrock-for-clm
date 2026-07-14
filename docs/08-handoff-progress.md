# Progress Handoff: Box + Agentforce + React CLM Demo

## Demo Scenario

**CLM-2026-Northstar** | Acme Robotics, Inc. + Northstar Health System | $2.4M ARR | 36-month term.

Contract package:
- Master Services Agreement
- Data Processing Addendum
- Statement of Work
- Order Form
- Security Exhibit
- Insurance Certificate

---

## Current Status

| Area | Status | Notes |
|------|--------|-------|
| CLM directory | Created | `/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm` |
| README | Current | Defines separate Governed Workflow and Agentic Orchestration presenter tracks |
| Core docs | Current | Each scenario has one ordered guide containing architecture, flow, presenter script, screenshots, readiness, and setup; shared assets remain single-source |
| Runbooks | Separated | Governed Workflow leads with Box; Agentic Orchestration uses the AgentCore/Strands runbook and React presenter surface |
| Sample data | Generated | Synthetic PDFs, JSON records, playbook, and analytics CSV in `output/` |
| Generation script | Created | `scripts/generate_sample_contract_assets.py` |
| Box config | Drafted | Metadata templates, folder template, and Box App blueprint under `config/box/` |
| AgentCore config | Demo-ready | AgentCore Strands orchestration, tool contracts, handoff payloads, and local mock over Box, Salesforce, and Databricks under `config/agentcore/` |
| Architecture diagram | Created | Mermaid source and rendered SVG in `docs/diagrams/` |
| Live Box workspace | Created | Kyle-owned `CLM-2026-Northstar` folder `399081692991` at the Box root in enterprise `5105484` |
| Box App | Published | `Contract Lifecycle Management` is live at the URL recorded in `config/box/live-box-surface.json` |
| Box App rich dashboard additions | Live | Home uses `Quick Actions & Portfolio` with approval, risk, document-type, and package-status charts plus the sole intake Form, Hub, and executed-agreement actions; the duplicate intake Form was removed. Clause Library includes the approved view, source folder, Hub shortcut, and position, family, and approval-status charts. |
| Box metadata | Four live, one specified | `clmContract`, `clmDocument`, `clmObligation`, and `clmClause` are live; `clmRedlineReview` is specified but not created |
| Box tasks | Created | Legal, finance, and privacy/security review tasks assigned to `kadams@boxdemo.com` |
| Box Form | Published | `New Contract Request` is live at the URL recorded in `config/box/live-box-surface.json` |
| Box Form smoke test | Box intake passed; downstream activation pending | On 2026-07-14 the published Form created intake file `2346653850589` in folder `399082115646`; Salesforce returned zero matching `CLM_Contract__c` records because Automate workflow `399436615012` remains inactive |
| Box AI / AI Studio | Staged in Automate | Box Agent instructions review the live MSA against the approved clause library and require human validation |
| Box DocGen | Created | Approval memo, order-form summary, and renewal notice are marked as live DocGen templates in folder `399363530207` |
| Box Automate | Saved draft, inactive; OAuth credential blocked | Workflow `399436615012` now uses the correct `Agentforce Dev` My Domain, OAuth 2.0, JSON header, and a deterministic standard REST `PATCH` smoke request. Box test attempts fail before Salesforce login because the supplied secret came from the legacy `Box Automate` app rather than `Box_Automate_CLM`; the GET lookup and dynamic field bindings remain after the CLM-specific secret is corrected. |
| Clause library | Live content | Eight governed Markdown clauses plus README are uploaded under live folder `399419341582` with `clmClause` metadata |
| Box Hub | Live | `Acme Contract Clause Library` Hub `1312630996` contains the live clause folder, current-standard operations callout, intake/App/executed-agreement cards, and governance content |
| Experience galleries | Complete | Separate Governed Workflow and Agentic Orchestration HTML galleries embed only their scenario screenshots with no browser tabs or external references |
| Box Sign | Not started | Needs execution packet flow |
| Box + Agentforce + React supporting flow | Local implementation complete | React UI Bundle, Agentforce action contract, architecture diagram, and supporting split runbook are ready; live Salesforce deployment and runtime IDs remain |
| Redline expert router | Local specification complete | Structured finding schema, deterministic expert directory, triage controls, domain-grouped React queues, and Agentforce/HTTPS contracts are ready; named Box collaborators and live workflow activation remain |
| Presentation package | Complete | Two ordered single-page scenario guides; optional executive, Legal Operations, and technical React appendices; reusable Form entry module; rendered diagrams; JSON manifests |
| Operator documentation | Complete | `docs/runbooks/05-demo-setup-and-activation.md` covers end-to-end bring-up; `docs/manual-task-register.md` inventories all known manual and confirmation-gated tasks |
| Salesforce CLM record | Object and metadata-managed External Client App deployed; REST upsert verified in `agentforce` | `CLM_Contract__c`, permission set `0PSgL00000IR6zpWAD`, External Client App `0xIgL000000Ok89UAC`, OAuth policy `0yOgL000000coILUAY`, and dedicated Run As user `005gL00000KmN8TQAV` are live in org `00DgL000003D0LRUA0`; external-ID create/update/lookup passed with record `a7IgL000000WYWPUA4`, exactly one matching record, and `DataStorageMB remaining = 1`; only the consumer-secret handoff and Box OAuth test remain |
| AWS AgentCore | Future | High-complexity tier uses AgentCore Strands agents with Box, Salesforce, and Databricks |

### Salesforce storage cleanup audit — 2026-07-13

- Removed 433 sequential `Sponsor_Product__c` import rows, 51 legacy Cases, 22 stock Leads, 17 stock Products, 34 stock Pricebook Entries, and 14 stock Contacts. Case deletion also removed 24 Email Messages and 20 dependent Tasks. Salesforce marks the soft-deleted rows non-restorable while its background physical purge completes.
- Permanently hard-deleted 452 pre-2026 `box__FRUP__c` staging-history rows with bulk job `750gL00000dQsMTQA0`; retained the two 2026 rows. Folder metadata, Box Sign data, and the DocGen template were not changed.
- Retained two row-locked stock Contacts, four Campaigns that this admin cannot delete, all Accounts and Contracts, and the CLM smoke record `a7IgL000000WYWPUA4`.
- Temporary Bulk API Hard Delete permission set `0PSgL00000IQypRWAT` and assignment `0PagL00000b1A4zSAE` were deleted after use. Final storage is `DataStorageMB remaining = 1` and `FileStorageMB remaining = 7`.

### Salesforce OAuth automation — 2026-07-14

- Added and deployed the metadata-managed `Box_Automate_CLM` External Client App (`0xIgL000000Ok89UAC`) with client credentials enabled, `Api` as its only OAuth scope, admin-preauthorized access, and OAuth policy `0yOgL000000coILUAY`.
- Created dedicated Salesforce Integration user `box.automate.clm+00dgl000003d0lrua0@boxdemo.com` (`005gL00000KmN8TQAV`) on the minimum-access API-only profile and assigned only `CLM_Box_Automate_Integration` (`0PagL00000b40CHSAY`, plus the platform-generated integration-license permission set).
- Added idempotent reconciliation script `clm-react-app/scripts/configure-clm-oauth.sh`; repeated execution completed successfully without creating duplicate users, permission assignments, or apps.
- Pinned the generated consumer key in metadata with key and secret rotation disabled for repeat deployments. The consumer secret is intentionally not retrievable through Metadata API and must be transferred directly into the Box-managed OAuth connection.
- Deployed OAuth IP policy `Bypass` for the trusted Box server-to-server client (deployment `0AfgL00000R9BXmSAN`). Tooling verification confirms client credentials, the API scope, dedicated Run As user, preauthorized permission set, and OAuth plugin are enabled.
- Saved the inactive Box workflow with connector `Agentforce Dev`, API v67.0 external-ID `PATCH`, `Content-Type: application/json`, and a deterministic smoke payload. Repeated tests return Box `Request Failed` with no Salesforce login-history event, isolating the remaining failure to the consumer secret. Salesforce Setup currently exposes only the older `Box Automate` app, whose secret does not match the pinned `Box_Automate_CLM` consumer key.

---

## Recommended Build Order

1. **Review live Box workspace**
   - Root folder: `399081692991`.
   - Workspace URL: `https://kadams.ent.box.com/folder/399081692991`.
   - Live ID manifest: `config/box/live-box-surface.json`.

2. **Regenerate or review sample-data package**
   - Run `python3 scripts/generate_sample_contract_assets.py`.
   - Review generated PDFs in `output/pdf/`.
   - Review JSON/CSV context in `output/json/` and `output/csv/`.

3. **Create Box metadata templates**
   - Source: `config/box/metadata-templates.json`.
   - Templates: `clmContract`, `clmDocument`, `clmObligation`.
   - Current live IDs:
     - `clmContract`: `fe4e6fdb-659f-4931-9718-d03b624affdb`
     - `clmDocument`: `8a6cc4c2-8425-48fa-b4f0-01711b777d4a`
     - `clmObligation`: `964802ab-7da2-444e-9422-1b52fd4f5489`

4. **Create Box folder template**
   - Source: `config/box/folder-template.md`.
   - Current live folders:
     - `01 - Intake`: `399082115646`
     - `02 - Drafts and Redlines`: `399080778184`
     - `03 - Review Packets`: `399082148957`
     - `04 - Approvals`: `399082072259`
     - `05 - Signature`: `399081939679`
     - `06 - Executed Agreement`: `399080706253`
     - `07 - Obligations`: `399081567921`

5. **Create Box Form**
   - New Contract Request (single dashboard Form entry point: `Start a New Contract`)
   - Fields: requester, counterparty, contract type, deal value, region, data category, target signature date, package upload.

6. **Create Box App dashboard**
   - Source: `config/box/box-app-blueprint.md`.
   - Live implementation spec: `config/box/box-app-dashboard-live-spec.json`.
   - UI build checklist: `config/box/box-app-builder-checklist.md`.
   - Manual boundary: create and publish the dashboard in Box Apps through the Box web UI, then add the published URL to `config/box/live-box-surface.json`.
   - Current live layout: `Quick Actions & Portfolio`; charts plus `Approved Clause Hub`, `Start a New Contract`, and `Executed Agreements`; no repeated Form in `Intake and Actions`; Clause Library adds Hub access and three metadata charts.

7. **Activate the Box + Agentforce + React demo**
   - React project: `clm-react-app/`.
   - Presenter runbook: `docs/runbooks/04-box-agentforce-react-demo.md`.
   - Agentforce contract: `config/agentforce/clm-react-agentforce-spec.json`.
   - Remaining live work: deploy the Salesforce UI Bundle plus remaining layout/tab metadata, transfer the ECA consumer secret into Box and test the already-verified standard REST intake through Box OAuth 2.0, provide Agentforce runtime IDs, and implement the same-origin downscoped Box token endpoint.

8. **Optional: evaluate the AgentCore prototype**
   - Source: `docs/runbooks/03-agentcore-demo.md`.
   - Orchestration spec: `config/agentcore/agentcore-orchestration-spec.json`.
   - Tool contracts: `config/agentcore/tool-contracts.json`.
   - Handoff payloads: `config/agentcore/agent-handoff-payloads.json`.
   - Local trace mock: `python3 scripts/run_agentcore_mock.py`.

---

## Generated Sample Artifacts

| Artifact | Path | Demo Use |
|----------|------|----------|
| MSA redline | `output/pdf/northstar-msa-redline-v3.pdf` / Box `2342633195167` | Unlimited liability, renewal ambiguity, termination issue |
| DPA | `output/pdf/northstar-dpa.pdf` / Box `2342633156726` | PHI/privacy/security approval trigger |
| SOW | `output/pdf/northstar-sow-implementation.pdf` / Box `2342622013520` | SLA credits and delivery obligations |
| Order form | `output/pdf/northstar-order-form.pdf` / Box `2342633259967` | Net 90 vs Net 45 mismatch |
| Security exhibit | `output/pdf/northstar-security-exhibit.pdf` / Box `2342636075017` | SOC 2 and incident notice obligations |
| Insurance certificate | `output/pdf/northstar-insurance-certificate.pdf` / Box `2342619758153` | Insurance renewal reminder |
| Structured records | `output/json/northstar-clm-records.json` / Box `2342634498103` | Salesforce-style opportunity, contract, approval matrix |
| Clause playbook | `output/json/clause-playbook.json` / Box `2342635779827` | Approved standard and fallback positions |
| Analytics context | `output/csv/historical-clause-outcomes.csv` / Box `2342621008641` | Databricks analytics mock |

---

## Live Box Review Tasks

| Task | Task ID | File | Assignment ID | Assignee |
|------|---------|------|---------------|----------|
| Legal review | `42899891150` | `northstar-msa-redline-v3.pdf` / Box `2342633195167` | `92573629417` | `kadams@boxdemo.com` |
| Finance review | `42899881417` | `northstar-order-form.pdf` / Box `2342633259967` | `92573683142` | `kadams@boxdemo.com` |
| Privacy/security review | `42899893550` | `northstar-dpa.pdf` / Box `2342633156726` | `92573685345` | `kadams@boxdemo.com` |

These live tasks remain the safe demo-triage assignments. Intended expert personas are configured in `config/clm/expert-routing.json`, but their Box logins are deliberately unset until real collaborators are provided.

---

## Metadata Draft

### `clmContract`

| Field | Type | Example |
|-------|------|---------|
| contractId | string | CLM-2026-0042 |
| counterparty | string | Northstar Health System |
| contractType | enum | MSA, DPA, SOW, Order Form, Procurement Agreement |
| status | enum | Intake, Legal Review, Business Review, Approved, Signature, Executed, Obligations Active |
| dealValue | number | 2400000 |
| termMonths | number | 36 |
| region | enum | US, EU, APAC, Global |
| dataCategory | enum | None, Personal Data, PHI, Financial Data, Confidential |
| owner | string | Account Executive |
| legalReviewer | string | Commercial Counsel |
| riskLevel | enum | Low, Medium, High, Critical |
| targetSignatureDate | date | 2026-07-31 |
| renewalDate | date | 2029-06-30 |
| noticeDeadline | date | 2029-03-31 |

### `clmDocument`

| Field | Type | Example |
|-------|------|---------|
| documentType | enum | MSA, DPA, SOW, Order Form, Security Exhibit, Insurance |
| versionStatus | enum | Draft, Redline, Approved, Executed |
| clauseRisk | enum | Low, Medium, High, Critical |
| aiSummaryStatus | enum | Not Started, Complete, Needs Review |
| approvalStatus | enum | Not Required, Pending, Approved, Rejected |
| signatureStatus | enum | Not Required, Pending, Signed |

### `clmObligation`

| Field | Type | Example |
|-------|------|---------|
| obligationType | enum | Renewal Notice, SLA Report, Security Evidence, Data Deletion, Insurance, Billing |
| owner | string | Customer Success Manager |
| dueDate | date | 2029-03-31 |
| sourceClause | string | MSA Section 7.3 |
| status | enum | Open, In Progress, Complete, Escalated |
| reminderWindowDays | number | 90 |

---

## Demo-Ready Issues to Build Into Sample Data

| Issue | Document | Demo Purpose |
|-------|----------|--------------|
| Unlimited liability | `northstar-msa-redline-v3.pdf` | Clause Risk Agent critical finding |
| Net 90 payment terms | `northstar-order-form.pdf` | Finance approval trigger and Salesforce mismatch |
| PHI processing language | `northstar-dpa.pdf` | Privacy/security approval trigger |
| Auto-renewal with unclear notice | `northstar-msa-redline-v3.pdf` | Obligation extraction and legal review |
| SLA credits uncapped | `northstar-sow-implementation.pdf` | Business owner escalation |
| Insurance expiration | `northstar-insurance-certificate.pdf` | Renewal reminder extraction |

---

## Future Reuse Checklist

For the next use-case demo, copy this directory and update:

| Artifact | Replace With |
|----------|--------------|
| Scenario | New persona, business object, and business stakes |
| Sample data | Domain-specific files and structured JSON |
| Metadata templates | Domain-specific schema |
| Agent names | Domain-specific roles |
| Demo script | Same three levels, new acts |
| ROI | Domain-specific metrics |
| Competitive landscape | Relevant software category |
| Handoff | Live build state and IDs |

# Legal Operations Demo: Review to Approval Readiness

## Demo card

| Item | Value |
|---|---|
| Duration | 20-25 minutes |
| Audience | Legal Ops, commercial counsel, Sales Ops, Finance, Privacy, Security |
| Objective | Demonstrate package review, clause analysis, approval routing, DocGen, and post-signature readiness |
| Contract | `CLM-2026-0017` — Northstar Health MSA |

## Live anchors

| Component | Target-environment value |
|---|---|
| Box workspace | Generated `CLM-2026-Northstar` folder |
| MSA redline | Generated `northstar-msa-redline-v3.pdf` |
| DPA | Generated `northstar-dpa.pdf` |
| Order form | Generated `northstar-order-form.pdf` |
| Clause playbook | Target environment's approved clause folder and Hub |
| Legal task | Human-owned Legal review task |
| Finance task | Human-owned Finance review task |
| Privacy/Security task | Human-owned Privacy/Security review task |
| Approval memo template | Generated approval memo template |
| Renewal notice template | Generated renewal notice template |

## Script

### Act 1 — Establish the contract record (3 minutes)

**Show**

- Review the validated Box intake and approved Automate branch.
- Create the Salesforce CLM record through the configured HTTPS operation and capture the returned record ID.
- Open React with `recordId=<returned-salesforce-id>&contractId=<contract-id>&folderId=<generated-workspace-folder-id>`.
- Review counterparty, contract type, value, term, risk, and status.
- Open the Box workspace panel.

**Explain**

- The React UI carries context and orchestration.
- Box carries files, versions, metadata, tasks, DocGen, Sign, and audit history.
- Agentforce receives explicit contract and Box folder context.
- The Salesforce record stores structured deal context and the Box workspace reference; it does not duplicate contract files.

### Act 2 — Review the package with citations (4 minutes)

**Prompt**

> Summarize the Northstar package by document. Identify missing or conflicting information and cite the exact Box file used for each conclusion.

**Verify**

- MSA, DPA, SOW, and order form appear.
- Findings are separated by source document.
- Agentforce does not invent missing terms or policies.

### Act 3 — Compare and route the redline (6 minutes)

**Prompt**

> Compare `northstar-msa-redline-v3.pdf` with the approved clause playbook. For each deviation, show the proposed language, approved position, available fallback, risk, and source citation.

Then open **Redline reviews** in React.

- Show four cited findings consolidated into Commercial Legal, Finance, and Privacy expert queues.
- Open the Commercial Legal group to show the removed liability cap and shortened renewal notice together.
- Point out the intended named expert, target environment's Box task ID, classification confidence, and triage assignee.
- Explain that production assignment requires a configured Box collaborator login; low-confidence or unclassified findings go to Legal Operations triage.

**Expected findings**

- Unlimited liability is outside the approved position.
- Auto-renewal/notice language needs clarification.
- Termination language requires Legal review.

**Control statement**

Agentforce may show fallback options and recommend a routing domain. The configured expert selects or rejects the position; the agent never invents a person or login.

### Act 4 — Reconcile commercial and privacy issues (4 minutes)

**Prompt**

> Check the order form and DPA for approval triggers. Explain the commercial mismatch and the privacy/security review requirement.

**Expected findings**

- Order form contains Net 90 while the expected structured term is Net 45.
- DPA includes PHI-processing language and security obligations.
- Finance and Privacy/Security reviews remain required.

### Act 5 — Show the expert approval gate (3 minutes)

**Show**

- Select **Redline reviews**.
- Confirm the three Box task IDs and Pending state.
- Confirm **Signature blocked**.

**Prompt**

> Explain the minimum evidence required for each reviewer to complete their decision. Do not approve or complete any task.

### Act 6 — Generate the review packet (3 minutes)

**Prompt**

> Prepare an approval memo using the Box DocGen approval memo template. Include the deal summary, material deviations, reviewer owners, unresolved decisions, and Box source citations.

**Presenter action**

- Pause at the mutation confirmation.
- Explain that file creation is the only requested action; task completion is not included.
- If running against a configured org, confirm draft generation only when the demo environment is ready.

### Act 7 — Signature and obligations (3 minutes)

**Show**

- Generated `05 - Signature` folder.
- Generated `07 - Obligations` folder.
- Generated renewal notice template.

**Explain**

- Box Sign begins only after human approvals.
- Agentforce may extract candidate obligations with file citations.
- A human validates owners, dates, notice periods, and final communications.

## Objection handling

| Question | Response |
|---|---|
| Can Agentforce approve the contract? | No. The agent may prepare and route work; humans complete the Box tasks and authorize signature. |
| Is the React app another repository? | No. It renders context and embeds Box capabilities; Box remains authoritative for content. |
| Where is the AI audit trail? | Agentforce conversation/action history and Box file versions, tasks, and events provide the relevant traces. |
| Does this require AWS or Databricks? | No. Those systems are explicitly excluded from this variation. |

## Pass criteria

- All material findings cite Box files.
- Validated intake creates one Salesforce CLM record and the React workspace uses the returned record ID.
- The MSA, order-form, and DPA issues match the seeded scenario.
- Live task IDs and owners remain unchanged.
- DocGen requires confirmation.
- Signature remains blocked until human approval completion.

# Executive Demo: Governed Contract Decisions

## Demo card

| Item | Value |
|---|---|
| Duration | 10-12 minutes |
| Audience | General counsel, CRO, CIO, legal and sales leadership |
| Scenario | Acme Robotics negotiates a $2.4M ARR MSA package with Northstar Health |
| Experience | Salesforce Multi-Framework React app with Box content and Agentforce |
| Core message | AI compresses review time while Box preserves evidence and humans retain decision rights |

## Pre-demo state

- Prepare a validated New Contract Request and the Salesforce standard REST OAuth 2.0 connection.
- Open the React workspace with the test contract and generated Box workspace folder.
- Keep the **Workspace** view selected.
- Confirm the Northstar banner shows **Critical** risk and **Approval blocked** status.
- Do not complete any of the three Box review tasks before the demo.

## Script

### Act 0 — Create the contract record (2 minutes)

**Show**

- Submit or open the validated Box intake.
- Show the Automate approval gate, then the approved HTTPS branch.
- Show the newly created Salesforce CLM record and returned record ID.
- Open React with `recordId`, `contractId`, and `folderId=<returned boxFolderId>`.

**Land**

The structured Salesforce record is created only after a human validates the Extract and Box Agent output. Box remains the source for contract content.

### Act 1 — One contract workspace (2 minutes)

**Say**

> Contract teams should not have to reconstruct deal context from email, CRM notes, and local copies. This workspace combines the commercial context with the governed contract package in Box.

**Show**

- Northstar Health MSA, `$2.4M ARR`, 36-month term.
- The live Box workspace and the MSA, DPA, SOW, and order form.
- Critical and high-risk labels.

**Land**

Box remains the content system of record. The React app is the work surface, not another document repository.

### Act 2 — Ask Agentforce for a cited briefing (3 minutes)

**Prompt**

> Summarize the Northstar contract package, identify the three most material risks, and cite the Box source file for each finding.

**Expected response**

- Unlimited liability and renewal ambiguity from the MSA redline.
- PHI and security obligations from the DPA/security exhibit.
- Net 90 versus expected Net 45 from the order form.
- File-level citations for every material claim.

**Land**

Agentforce accelerates comprehension without moving the source content into a separate AI platform.

### Act 3 — Route redlines to the right experts (3 minutes)

**Show**

- Select **Redline reviews**.
- Point to the cited differences grouped under Commercial Legal, Finance, and Privacy.
- Show the named domain expert, Box task ID, confidence, and before/after clause position.
- Point to **Signature blocked**.

**Prompt**

> Explain why signature is blocked, who owns each decision, and what evidence each reviewer should inspect.

**Land**

Agentforce explains and classifies the work. The maintained expert directory controls assignment, uncertain findings go to Legal Operations triage, and only humans complete approvals.

### Act 4 — Prepare, do not decide (2 minutes)

**Say**

> Once the reviewers are ready, Agentforce can prepare the approval memo using the governed Box DocGen template. Creating that draft still requires confirmation.

**Show**

- The generated approval memo Doc Gen template.
- Explain that Box Sign remains blocked until the live Box tasks are complete.

## Close

> This is a focused CLM experience: Box governs the contract record, Agentforce helps people understand and prepare the work, and the React app makes the process visible. There is no separate agent runtime, analytics platform, or shadow content store in this variation.

## Pass criteria

- The audience sees the Salesforce CLM record created from validated intake, then one contract workspace with the live Box package.
- Agentforce produces source-cited findings.
- Three named domain experts and their human-owned task queues remain visible.
- No automated approval or signature action is shown.

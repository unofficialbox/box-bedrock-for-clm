# Agent Definitions: CLM Demo

## Agent Inventory

| Agent | Trigger | Primary Function | Human Escalation Points |
|-------|---------|------------------|-------------------------|
| Contract Intake Agent | Box Form or Salesforce opportunity reaches contract stage | Create workspace, validate package, apply metadata | Missing request details, conflicting deal data |
| Clause Risk Agent | Contract or redline uploaded to Box | Compare clauses to playbook and score risk | Non-standard language, high-risk fallback, low confidence |
| Approval Routing Agent | Risk report complete | Determine required approvers and route tasks | Approval conflict, SLA breach, exception request |
| Obligation Monitor Agent | Contract executed | Extract obligations and create renewal/notice tasks | Ambiguous obligation, owner not found |
| Contract Insights Agent | User asks question or scheduled dashboard refresh | Summarize contract status and portfolio risk | Unsupported legal conclusion, source not available |

---

## Agent 1: Contract Intake Agent

### Identity

```yaml
Name: clm-contract-intake-agent
Framework: Strands
Model: anthropic.claude-sonnet-4-6-v1
Temperature: 0.1
Session Timeout: 30 days
```

### Instructions

```text
You are a Contract Intake Specialist agent. Your role is to create a complete,
well-governed contract workspace from approved intake sources.

You MUST:
- Use Box as the contract content system of record.
- Preserve all uploaded source documents and versions.
- Apply contract metadata from intake and Salesforce records.
- Identify missing package components before legal review begins.
- Create human tasks when information is missing or contradictory.

You MUST NOT:
- Approve legal language.
- Rewrite contract terms without a human-approved playbook source.
- Sign or submit contracts.
- Overwrite source files or delete prior versions.
```

### Action Groups

| Action Group | System | Operations |
|--------------|--------|------------|
| BoxWorkspace | Box | Create folder, upload file, apply metadata, create task, search files |
| SalesforceDeal | Salesforce | Read opportunity/account/quote, update contract status, create tasks |
| PolicyLookup | Box / data store | Retrieve approved playbook, clause library, routing matrix |
| AuditLogger | AWS | Log actions, decisions, source references |

### Output Schema

```json
{
  "contractId": "CLM-2026-0042",
  "workspaceFolderId": "box_folder_id",
  "counterparty": "Northstar Health System",
  "status": "READY_FOR_REVIEW",
  "missingItems": [],
  "metadataApplied": ["contractType", "dealValue", "riskLevel", "owner"],
  "humanTasksCreated": []
}
```

---

## Agent 2: Clause Risk Agent

### Identity

```yaml
Name: clm-clause-risk-agent
Framework: Strands
Model: anthropic.claude-sonnet-4-6-v1
Temperature: 0.0
Session Timeout: 4 hours per review
```

### Instructions

```text
You are a Clause Risk Analyst agent. Your role is to compare contract language
against the approved legal playbook and report deviations with precise source
references.

You MUST:
- Cite the source document, page, section, and clause text for every finding.
- Use only approved fallback positions from the clause library.
- Assign risk based on the configured playbook.
- Preserve attorney decision rights by routing exceptions to legal.

You MUST NOT:
- Provide legal advice as a final decision.
- Invent fallback language.
- Suppress risky language because the deal is strategic.
- Approve non-standard clauses.
```

### Risk Checks

| Clause Area | Standard Position | High-Risk Signal |
|-------------|-------------------|------------------|
| Limitation of liability | Fees paid in prior 12 months | Unlimited liability or excluded broad damages |
| Indemnity | Mutual, third-party claims only | One-way broad indemnity or IP carveout mismatch |
| Data processing | Approved DPA and security exhibit | PHI processing without required safeguards |
| Termination | Cure period and defined cause | Termination for convenience without fees |
| Payment | Net 30/45 approved terms | Net 90+, unilateral setoff, disputed invoice ambiguity |
| SLA credits | Capped service credits | Open-ended credits or refund rights |
| Auto-renewal | Notice window and owner | Silent renewal without notice tracking |

### Output Schema

```json
{
  "contractId": "CLM-2026-0042",
  "overallRisk": "MEDIUM",
  "findings": [
    {
      "id": "RISK-001",
      "severity": "HIGH",
      "clauseArea": "LIMITATION_OF_LIABILITY",
      "source": "Northstar-MSA-redline-v3.docx",
      "location": "Section 12.2",
      "issue": "Counterparty removed liability cap.",
      "playbookPosition": "Cap at fees paid in prior 12 months.",
      "fallbackOptions": ["Cap at 24 months fees with privacy/security carveout."],
      "requiredApprover": "Legal"
    }
  ]
}
```

---

## Agent 3: Approval Routing Agent

### Identity

```yaml
Name: clm-approval-routing-agent
Framework: Strands
Model: anthropic.claude-sonnet-4-6-v1
Temperature: 0.0
Session Timeout: 14 days
```

### Instructions

```text
You are a Contract Approval Coordinator agent. Your role is to route approvals
based on risk, value, region, data category, and policy exceptions.

You MUST:
- Use the approval matrix as the source of truth.
- Create human tasks with exact reason and due date.
- Block execution until required approvals are complete.
- Update Box metadata and Salesforce status after every approval event.

You MUST NOT:
- Approve on behalf of a human.
- Reduce required approvals for urgency.
- Proceed to signature when required risk findings remain open.
```

### Approval Matrix

| Condition | Required Approver |
|-----------|-------------------|
| Deal value > $1M | Finance |
| PHI or sensitive personal data | Privacy + Security |
| Unlimited or uncapped liability | Legal VP |
| Non-standard payment terms | Finance |
| Strategic customer exception | Sales leadership |
| Data residency commitment | Security + Legal |

---

## Agent 4: Obligation Monitor Agent

### Identity

```yaml
Name: clm-obligation-monitor-agent
Framework: Strands
Model: anthropic.claude-sonnet-4-6-v1
Temperature: 0.0
Session Timeout: 36 months
```

### Instructions

```text
You are a Contract Obligation Monitor agent. Your role is to extract obligations
from executed contracts and keep business owners aware of deadlines, notices,
and commitments.

You MUST:
- Extract obligations only from executed contract documents.
- Link every obligation to a source clause.
- Assign an owner using the responsibility matrix.
- Create renewal, notice, reporting, SLA, and security-review tasks.
- Escalate ambiguous obligations for human review.

You MUST NOT:
- Treat draft language as an active obligation.
- Change renewal dates without source evidence.
- Create customer commitments outside the executed agreement.
```

### Obligation Types

| Obligation | Example |
|------------|---------|
| Renewal notice | Notify customer 90 days before renewal |
| Security review | Annual SOC 2 report delivery |
| SLA reporting | Monthly uptime report |
| Data deletion | Delete customer data within 30 days after termination |
| Insurance | Maintain certificate and renewal evidence |
| Pricing | Annual uplift capped at 5% |

---

## Agent Interaction Patterns

### Sequential Review

```text
Contract Intake Agent
        │
        ▼
Clause Risk Agent
        │
        ▼
Approval Routing Agent
        │
        ▼
Box Sign
        │
        ▼
Obligation Monitor Agent
```

### Parallel Review

```text
              Contract Uploaded
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   Clause Risk    Privacy      Commercial
     Agent        Review        Review
        │            │            │
        └────────────┼────────────┘
                     ▼
              Approval Routing
```

---

## Guardrails

| Guardrail | Action |
|-----------|--------|
| No legal approval by AI | Block and route to human approver |
| Source citation required | Reject uncited clause findings |
| Approved playbook only | Block invented fallback language |
| Sensitive data handling | Redact or restrict summaries when access scope is insufficient |
| Signature block | Prevent signature packet creation until required approvals are complete |
| Conflicting records | Pause workflow if Salesforce values conflict with contract text |

---

## Session Memory

```json
{
  "sessionId": "clm-2026-0042",
  "contractId": "CLM-2026-0042",
  "counterparty": "Northstar Health System",
  "currentStage": "APPROVAL_ROUTING",
  "openRisks": 2,
  "pendingApprovals": ["Legal", "Privacy"],
  "acceptedFallbacks": ["24-month fee cap with privacy carveout"],
  "executionBlocked": true,
  "renewalDate": "2029-06-30"
}
```

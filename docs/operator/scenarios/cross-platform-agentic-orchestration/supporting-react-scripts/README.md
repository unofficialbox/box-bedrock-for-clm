# Supporting Box + Agentforce + React Scripts

These supporting scripts present the React portion of Cross-Platform Agentic Orchestration at three depths. They intentionally stop short of AgentCore, Strands, and Databricks; use the parent [Cross-Platform Agentic Orchestration guide](../README.md#4-presenter-script) for the complete scenario.

| Script | Duration | Audience | Primary outcome |
|---|---:|---|---|
| [Executive walkthrough](01-executive-walkthrough.md) | 10-12 minutes | Executives, business sponsors, first meetings | Show the value and human-control model quickly |
| [Legal operations walkthrough](02-legal-operations-walkthrough.md) | 20-25 minutes | Legal Ops, Sales Ops, Finance, Privacy, Security | Demonstrate the complete contract-review and approval workflow |
| [Technical validation](03-technical-validation.md) | 20-30 minutes | Architects, Salesforce teams, security, developers | Prove runtime boundaries, token handling, actions, and guardrails |
| [Box Form entry-point variation](04-box-form-automate-entry.md) | 5-7 minutes | Any audience | Start with Form submission, Automate enrichment, human validation, and HTTPS Connector record creation |

Supporting artifacts:

- [Demo flow diagram](../../../../diagrams/clm-box-agentforce-react-demo-flow.svg)
- [Box Form entry-point diagram](../../../../diagrams/clm-box-form-automate-entry.svg)
- [Machine-readable scenario manifest](../../../../../config/demo/cross-platform-agentic-orchestration-demo-manifest.json)
- [Agentforce action contract](../../../../../config/agentforce/clm-react-agentforce-spec.json)

## Experience boundary

| Layer | Responsibility |
|---|---|
| React UI Bundle | Contract context, governed Box content, cited findings, expert queues, and Agentforce conversation |
| Box | Files, versions, metadata, review tasks, Doc Gen, Sign, and audit history |
| Salesforce | `CLM_Contract__c` structured context and approval state |
| Agentforce | Cited retrieval, comparison, explanation, draft preparation, and confirmed actions |
| Human reviewers | Legal positions, commercial concessions, task completion, generation, and signature authorization |

## Activation and pass criteria

1. Deploy the UI Bundle, `CLM_Contract__c`, and least-privilege permission set.
2. Configure standard REST external-ID upsert and lookup for validated intake fields.
3. Provide Agentforce IDs and downscoped Box-token behavior only through the documented runtime boundary.
4. Confirm the application resolves `recordId`, `contractId`, and `folderId` without browser secrets.
5. Confirm material answers cite Box files and approval state matches human-owned tasks.
6. Confirm one open task is reused per contract, redline file, and review domain.
7. Confirm document generation requires presenter confirmation and signature remains blocked while reviews are incomplete.
8. Keep managed AgentCore and Databricks claims outside these supporting scripts; the parent scenario owns that evidence.

## Shared presenter rule

Never describe Agentforce as approving a contract. It may retrieve, summarize, compare, explain, draft, and route. Named humans complete approval tasks and authorize signature.

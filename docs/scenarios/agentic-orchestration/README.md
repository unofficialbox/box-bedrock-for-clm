# Agentic Orchestration

Supervisor-led CLM execution across the complete platform stack. AWS Bedrock AgentCore and Strands coordinate specialist agents across Box, Salesforce Agentforce, the Salesforce Multi-Framework React workspace, and Databricks while humans retain approval and signature authority.

## Read this guide in order

[1. Orientation](#1-orientation) → [2. Architecture](#2-architecture) → [3. Flow](#3-flow) → [4. Presenter script](#4-presenter-script) → [5. Visual walkthrough](#5-visual-walkthrough) → [6. Components and readiness](#6-components-and-readiness) → [7. Setup and validation](#7-setup-and-validation)

Everything required for the main presentation is on this page. Links in **References** and the supporting React scripts are optional technical depth.

## 1. Orientation

Use this track when dynamic planning, specialist delegation, memory, traces, and cross-system reasoning are central and the Salesforce React workspace is the presenter surface.

| Boundary | Included |
|---|---|
| Presenter surface | Salesforce Multi-Framework React CLM workspace |
| Orchestration | AWS Bedrock AgentCore supervisor and Strands specialists |
| Systems | Box, Salesforce Agentforce, Databricks |
| Shared asset | Box Automate intake exists but remains inactive and is not executed in this presenter path |
| Human authority | Legal positions, approvals, concessions, signature, final obligations |

Repository truth: the React experience and Box specifications are available; the AgentCore flow includes a deterministic local trace. Each operator must validate their own Box surfaces, Salesforce Agentforce configuration, and managed integrations. Do not present AWS or Databricks as live until that environment passes deployment tests.

[Continue to architecture](#2-architecture)

## 2. Architecture

![Agentic Orchestration architecture](../../diagrams/clm-agentcore-architecture.svg)

AgentCore/Strands owns planning and specialist delegation. Box governs content, Salesforce Agentforce provides structured commercial context plus Salesforce-native assistance and actions, Databricks supplies analytical context, and React presents the joined workspace.

- [Architecture source](../../diagrams/clm-agentcore-architecture.mmd)
- [Shared architecture and control detail](../../01-architecture.md)

[Continue to flow](#3-flow)

## 3. Flow

![Agentic Orchestration flow](../../diagrams/agentic-orchestration-flow.svg)

1. A Box or Salesforce event starts an AgentCore session.
2. The supervisor selects Box, Salesforce Agentforce, and Databricks specialists.
3. Specialists return governed evidence, structured commercial truth, and historical benchmarks.
4. React presents the combined context, citations, findings, and ownership.
5. A human gate blocks signature and routes missing approvals.
6. Approved work proceeds to Doc Gen, Box Sign, obligations, and audit evidence.

- [Flow source](../../diagrams/agentic-orchestration-flow.mmd)

[Continue to presenter script](#4-presenter-script)

## 4. Presenter script

**Duration:** 20–25 minutes

**Audience:** Executives, enterprise architects, AI platform teams, and technical buyers

| Step | Tell | Show | Tell |
|---|---|---|---|
| 1. Context | “The supervisor starts with a contract, workspace, and business request.” | Open the Northstar record in the Salesforce React workspace. | “The session begins with governed identifiers, not an unbounded prompt.” |
| 2. Plan | “AgentCore/Strands selects specialists for the evidence it needs.” | Open the trace and highlight the delegated work. | “The plan is observable and each handoff has a defined contract.” |
| 3. Content | “Box remains authoritative for files, versions, metadata, and clauses.” | Show the governed package and cited missing-evidence result. | “Specialists reason over governed content without replacing it.” |
| 4. Commercial truth | “Salesforce Agentforce contributes record context and native actions.” | Show Net 90 in the order form versus Net 45 on the record. | “The discrepancy is explicit and sourced; Agentforce and Salesforce are one platform role.” |
| 5. Redlines | “Specialists turn document differences into reviewable findings.” | Show cited liability, PHI, SLA, renewal, and termination findings. | “Each finding has a domain, risk, confidence, approved position, and source.” |
| 6. Intelligence | “Portfolio history can inform—but not decide—the negotiation.” | Show Databricks outcome and cycle-time context. | “Analytics never overwrites authoritative contract state.” |
| 7. Ownership | “Material findings must reach qualified people.” | Show Legal, Finance, Privacy, and Security assignments. | “Low-confidence or unmapped work returns to Legal Operations triage.” |
| 8. Workspace | “The operator should not have to chase six systems.” | Show Box context, findings, queue, and Contract Copilot together in React. | “The unified view preserves each system's authority while reducing clicks.” |
| 9. Guardrail | “Autonomy stops at legal approval and signature.” | Attempt the premature signature path and show it blocked. | “Incomplete human approvals are a hard control, not a suggestion.” |
| 10. Close | “After confirmation, the platform completes the governed lifecycle.” | Show generation, Sign, obligations, and returned state. | “The result is end-to-end orchestration with human authority and an auditable trace.” |

Required language: AgentCore/Strands coordinates; Salesforce Agentforce supplies structured commercial context and Salesforce-native capabilities; Box governs content; Databricks supplies analytics, not authority; humans approve concessions, signatures, and final obligations.

[Continue to the visual walkthrough](#5-visual-walkthrough)

## 5. Visual walkthrough

The Box screenshots below reference the Governed Workflow source files. Only the React screenshots are scenario-specific.

### Unified React workspace

![Northstar React workspace](../../../output/screenshots/agentic-orchestration/clm-react-workspace.png)

![React domain-expert review queue](../../../output/screenshots/agentic-orchestration/clm-react-redline-reviews.png)

### Shared governed Box context

![Box App portfolio dashboard](../../../output/screenshots/governed-workflow/box-app-dashboard-live.png)

![Box App Clause Library](../../../output/screenshots/governed-workflow/box-app-clause-library-live.png)

![Approved Clause Hub](../../../output/screenshots/governed-workflow/box-hub-clause-library-live.png)

![Human approval branch](../../../output/screenshots/governed-workflow/automate-approval-flow.png)

Optional offline presentation: [self-contained visual gallery](../../../output/html/04-agentic-orchestration-gallery.html). For the complete narrative, use the [portable guide](../../../output/html/03-agentic-orchestration-guide.html). No live Databricks or AWS console screenshots are claimed; use the architecture, flow, and [local trace](../../../output/agentcore/northstar-agentcore-trace.json) until managed deployment is verified.

[Continue to components and readiness](#6-components-and-readiness)

## 6. Components and readiness

| Layer | Components | Status |
|---|---|---|
| Experience | Salesforce Multi-Framework React CLM workspace | Local tests/build verified; deploy per environment |
| Salesforce Agentforce | `CLM_Contract__c`, Contract Copilot, approval context | Portable object/spec provided; configure per environment |
| Box | Apps, Forms, content, metadata, tasks, Hub, Doc Gen, Sign | Foundation automation and browser specifications provided |
| Orchestration | AWS Bedrock AgentCore supervisor and Strands specialists | Specification and deterministic local mock |
| Analytics | Databricks historical outcomes and cycle-time benchmarks | Synthetic dataset/tool contract only |
| Controls | Citations, deterministic expert directory, human approvals, signature block | Specified; Box tasks seeded |
| Observability | Handoffs, tool calls, guardrail events, final trace | Local trace generated |

[Continue to setup and validation](#7-setup-and-validation)

## 7. Setup and validation

1. Complete [Operator Start Here](../../operator/00-start-here.md) and the Governed Workflow foundation first.
2. Run `python3 scripts/run_agentcore_mock.py` and validate `output/agentcore/northstar-agentcore-trace.json`.
3. Start the React workspace with this environment's Salesforce record ID, contract ID, and generated Box workspace folder ID.
4. Confirm Box content and the safe Salesforce Agentforce fallback render without browser secrets.
5. Confirm the trace shows Box, Salesforce Agentforce, and Databricks specialist work plus a signature-block guardrail.
6. Confirm every finding has a Box citation and every approval remains human-owned.
7. Describe AgentCore and Databricks as local/specification-backed until managed deployment tests pass.

### References

- [Detailed AgentCore runbook](../../runbooks/03-agentcore-demo.md)
- [Operator setup and activation](../../operator/00-start-here.md)
- [Manual-task register](../../manual-task-register.md)
- [Machine-readable scenario manifest](../../../config/demo/agentic-orchestration-demo-manifest.json)
- [Supporting React scripts](supporting-react-scripts/README.md)

[Back to the scenario selector](../README.md)

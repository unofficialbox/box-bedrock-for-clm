# Runbook: Agentic Orchestration

## Goal

Show the end-state multi-agent path: AWS Bedrock AgentCore and Strands coordinate Box agents for unstructured data, Salesforce Agentforce specialists for structured work, Databricks agents for governed analytics, and the Salesforce Multi-Framework React workspace as the presenter surface.

Scenario package: [Agentic Orchestration](../scenarios/agentic-orchestration/README.md)

Readiness boundary: the orchestration trace is locally executable; do not represent AgentCore, Strands, or Databricks as deployed until their managed integrations and screenshots are verified.

## Agent Layers

| Layer | Agent Type | Systems |
|-------|------------|---------|
| Orchestration | Bedrock AgentCore supervisor | Agent routing, memory, guardrails, traces |
| Unstructured data | Box agents | Box files, metadata, tasks, Sign, Forms, Apps |
| Structured data | Salesforce agents | Salesforce opportunity, account, quote, approval, renewal records |
| Analytics | Databricks agents | Historical clause outcomes, pricing benchmarks, cycle-time analytics |

## Demo Agents

| Agent | Role |
|-------|------|
| CLM Supervisor Agent | Routes requests and coordinates workflow state |
| Box Contract Package Agent | Reads files, applies metadata, creates tasks, manages content workspace |
| Clause Risk Agent | Compares documents to playbook and creates cited findings |
| Salesforce Commercial Agent | Compares order form to Salesforce opportunity/quote records |
| Salesforce Approval Agent | Determines required Legal, Privacy, Security, Finance approvals |
| Databricks Analytics Agent | Queries historical clause outcomes and cycle-time benchmarks |
| Obligation Monitor Agent | Extracts renewal, SLA, security, data deletion, and insurance obligations |

## Demo Flow

| Act | Agent Action | Expected Result |
|-----|--------------|-----------------|
| 1 | Supervisor receives contract intake event | Workflow session starts |
| 2 | Box Contract Package Agent validates package | Missing/complete documents are identified |
| 3 | Salesforce Commercial Agent compares order form to structured record | Net 90 vs Net 45 mismatch is flagged |
| 4 | Clause Risk Agent reviews MSA/DPA/SOW | Unlimited liability, PHI, SLA credit, renewal findings created |
| 5 | Databricks Analytics Agent queries clause outcomes | Negotiation benchmarks enrich risk report |
| 6 | Salesforce Approval Agent routes approvals | Legal VP, Finance, Privacy, Security tasks created |
| 7 | Supervisor blocks signature until approvals complete | Guardrail event is visible |
| 8 | Obligation Monitor Agent extracts follow-up tasks | Renewal, SOC 2, data deletion, insurance reminders assigned |

## Config Files

| File | Purpose |
|------|---------|
| `config/agentcore/agentcore-orchestration-spec.json` | Agent inventory, tools, routing, guardrails |
| `config/agentcore/tool-contracts.json` | Box, Salesforce, and Databricks tool contracts |
| `config/agentcore/agent-handoff-payloads.json` | Expected payloads between supervisor and specialized agents |
| `scripts/run_agentcore_mock.py` | Local deterministic orchestration mock |
| `output/agentcore/northstar-agentcore-trace.json` | Generated local supervisor trace |
| `output/json/northstar-clm-records.json` | Mock structured system data |
| `output/csv/historical-clause-outcomes.csv` | Mock analytics query source |

## Local Mock

Run this before building live AWS infrastructure:

```bash
python3 scripts/run_agentcore_mock.py
python3 -m json.tool output/agentcore/northstar-agentcore-trace.json >/dev/null
```

The mock produces a deterministic trace showing:

| Step | Expected Trace Event |
|------|----------------------|
| 1 | AgentCore Strands supervisor starts the workflow |
| 2 | Box package agent validates the live Box file package |
| 3 | Salesforce commercial agent flags Net 90 versus Net 45 |
| 4 | Clause risk agent creates source-cited findings |
| 5 | Databricks analytics agent returns clause benchmarks |
| 6 | Salesforce approval agent routes Finance, Privacy, Security, and Legal VP approvals |
| 7 | Supervisor blocks signature until required human approvals complete |
| 8 | Obligation monitor creates draft-only candidate obligations |

## Guardrail Moments

| Moment | Expected Behavior |
|--------|-------------------|
| Signature requested before approvals | Block and route to Approval Agent |
| Agent recommends uncited legal position | Block and request source citation |
| PHI terms appear without approval | Require Privacy + Security approval |
| Order form conflicts with Salesforce quote data | Require Finance review |

## Manual Verification

| Check | Pass Criteria |
|-------|---------------|
| Supervisor trace | Shows routing across Box, Salesforce, and Databricks agents |
| Source citations | Findings reference source file and section |
| Structured comparison | Net 90 / Net 45 mismatch appears |
| Analytics enrichment | Clause benchmark appears in risk output |
| Human approvals | Required approvers are explicit |
| Finalization block | Signature is blocked until approvals complete |

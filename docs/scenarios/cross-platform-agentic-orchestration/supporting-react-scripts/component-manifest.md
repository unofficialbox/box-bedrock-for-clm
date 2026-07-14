# Cross-Platform Agentic Orchestration Component Manifest

This human-readable manifest uses logical names only. Target-environment IDs belong in the gitignored runtime configuration and bootstrap state.

## Required platform components

| Component | Role | Readiness evidence |
|---|---|---|
| Box CLM workspace | Authoritative contracts, versions, metadata, tasks, Doc Gen, Sign, audit | Generated workspace opens for intended users |
| Contract Lifecycle Management App | Portfolio, actions, risk/status views, Clause Library | Published App passes the UI checklist |
| New Contract Request | Intake entry point | Submission reaches generated intake folder |
| Approved Contract Clause Library | Governed approved and fallback clause Markdown | Hub shows ownership and review cadence |
| Box Automate intake | Form → Extract → cited review → human gate → Salesforce REST | Duplicate-safe test passes before activation |
| `CLM_Contract__c` | Structured commercial record and Box references | Portable metadata deploy succeeds |
| Salesforce Agentforce Contract Copilot | Salesforce-native cited assistance and actions | Topics/actions pass positive and negative tests |
| Salesforce Multi-Framework React UI Bundle | Joined contract, Box, findings, queues, and conversation | Bundle tests/build pass; live page resolves context |
| AWS Bedrock AgentCore + Strands | Supervisor and specialist delegation | Managed trace or disclosed deterministic local trace |
| Databricks | Historical outcome and cycle-time analytics | Read-only governed query evidence |

## Record creation contract

| Item | Value |
|---|---|
| Trigger | Validated New Contract Request |
| Human gate | Box Automate approval task |
| Operations | Salesforce standard REST external-ID upsert, then lookup |
| Object | `CLM_Contract__c` |
| External ID | `Contract_ID__c` |
| Output | Salesforce record ID, contract ID, Box workspace folder ID |

No custom Apex intake service is required. Apex remains necessary for redline routing, lifecycle-event ingestion, and authorized downscoped Box-token issuance if those features are presented live.

## Human authority

Agents may retrieve, summarize, compare, explain, recommend, and draft. A human must approve legal positions, complete review tasks, authorize Doc Gen output, and send for signature.

## Generated Box structure

- `01 - Intake`
- `02 - Drafts and Redlines`
- `03 - Review Packets`
- `04 - Approvals`
- `05 - Signature`
- `06 - Executed Agreement`
- `07 - Obligations`
- `08 - DocGen Templates`
- Approved clause source folder and published Hub

## Contract evidence

- `northstar-msa-redline-v3.pdf`
- `northstar-dpa.pdf`
- `northstar-sow-implementation.pdf`
- `northstar-order-form.pdf`
- `northstar-security-exhibit.pdf`
- `northstar-insurance-certificate.pdf`
- three generated Doc Gen templates
- approved and fallback clause Markdown files

## Controls

- All material claims cite Box content.
- `Contract_ID__c` prevents duplicate Salesforce intake records.
- One open task is reused per contract, file, and review domain.
- Low-confidence, unclassified, missing-owner, and inaccessible work routes to Legal Operations triage.
- Databricks provides analytics, not authority.
- Incomplete required reviews block signature.
- Secrets never enter browser source, runtime JSON committed to Git, chat, screenshots, or logs.

## Operator references

- [Start Here](../../../operator/00-start-here.md)
- [Browser configuration](../../../operator/01-browser-configuration.md)
- [Smoke test](../../../operator/02-smoke-test.md)
- [Technical validation](03-technical-validation.md)

# CLM Control Matrix

## Runtime Responsibilities

| Control Area | Box | Agentforce | React UI Bundle | Human Owner |
|---|---|---|---|---|
| Intake | Files, `clmContract` metadata, Automate | Explain extracted values and package gaps | Show request and contract context | Validate Extract and AI output |
| Clause review | Versioned contracts and approved clause Hub | Compare redlines with source citations and emit structured findings | Present before/after language and fallback position | Select or approve legal position |
| Expert routing | Review tasks and collaborator permissions | Classify domains; resolve experts only from the maintained directory | Group findings into one review queue item per domain | Legal Operations owns exceptions; named experts own decisions |
| Approvals | Tasks, due dates, decision history | Explain blockers and prepare drafts | Show expert, task, risk, and approval readiness | Complete assigned review tasks |
| Signature | Governed Box Sign packet | Explain prerequisites | Keep execution blocked while tasks remain open | Authorize and sign |
| Obligations | Metadata, tasks, renewal files | Extract candidate obligations with citations | Present owners and dates | Validate obligations and ownership |
| Audit | Versions, events, metadata, workflow history | Source references and action context | Visible state and confirmation prompts | Decision rationale |

## Contract Intake Controls

| Requirement | Implementation | System |
|---|---|---|
| Capture required fields | Apply the `clmContract` metadata template (contractId, contractType, counterparty, requesterEmail) when uploading to `01 - Intake` | Box metadata / Automate |
| Preserve source files | Upload into intake folder without overwriting | Box |
| Extract candidate values | Enhanced Extract Agent fields: contract type, risk level, key issues | Box Automate |
| Review AI output | Approval task before the HTTPS branch | Box Automate / Human reviewer |
| Prevent premature integration | Keep workflow inactive until the Salesforce origin, API version, OAuth 2.0 connection, and standard REST mappings are confirmed | Box Automate |

## Clause Review Controls

| Requirement | Implementation | System |
|---|---|---|
| Use governed language | Individual Markdown clauses with `clmClause` metadata | Box |
| Publish approved positions | Acme Contract Clause Library Hub | Box Hubs |
| Cite source clauses | Include file, section, and page references | Agentforce |
| Preserve redline history | Versioned files and comments | Box |
| Prevent task spam | One open task per contract, redline file, and expert domain | Automate / Agentforce action |
| Fail closed on routing | Low-confidence, unclassified, inaccessible, or unconfigured assignments go to Legal Operations triage | Automate / Human reviewer |
| Keep legal decisions human-owned | Agentforce recommends; Legal approves | Agentforce / Human reviewer |

## Approval and Execution Controls

| Requirement | Implementation | System |
|---|---|---|
| Segregation of duties | Assigned legal, finance, and privacy tasks | Box Tasks |
| Approval visibility | Live task identifiers and readiness state | React UI Bundle |
| Block execution | Do not create the Sign packet while required tasks remain open | React / Box Sign |
| Confirm mutations | Doc Gen actions require presenter confirmation | Agentforce / React |
| Retain final packet | Executed agreement and audit history remain in Box | Box Sign / Box |

## Security and Privacy Controls

| Control | Implementation |
|---|---|
| Least privilege | Short-lived downscoped Box token from a same-origin Salesforce endpoint |
| No browser secrets | React receives no long-lived Box or Salesforce credential |
| Connector minimization | HTTPS payload allowlist excludes file bytes, tokens, and unreviewed AI output |
| Human review | Required for legal positions, privacy decisions, approvals, and signature |
| Source grounding | Material Agentforce claims cite governed Box files |
| Retention and audit | Box Governance, versions, tasks, and events retain the system record |

## Validation

| Surface | Pass Criteria |
|---|---|
| React | Workspace and approval views load with the live Box identifiers |
| Agentforce | Responses cite Box sources and cannot approve or sign |
| Box | App, Hub, metadata, tasks, clauses, and Doc Gen templates resolve |
| Automate | Saved inactive workflow contains Extract, Box Agent, approval gate, and HTTPS stage |
| End to end | Signature remains blocked until named human tasks are complete |

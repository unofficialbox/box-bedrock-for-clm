# Box + Agentforce + React: Contract Lifecycle Management

## Overview

This repository contains one primary CLM demo: a Salesforce Multi-Framework React contract workspace with embedded Agentforce and governed Box content.

| Runtime | Responsibility |
|---|---|
| Box | Contracts, metadata, tasks, Forms, Apps, Automate, Hub, Doc Gen, Sign, and audit history |
| Agentforce | Source-cited contract analysis, explanations, drafting, and routing |
| React UI Bundle | Presenter-facing Salesforce contract record, Box workspace, redline findings, and domain-expert review experience |

Start with [setup and activation](docs/runbooks/05-demo-setup-and-activation.md), then use [the demo runbook](docs/runbooks/04-box-agentforce-react-demo.md). Every browser/admin/approval task is tracked in the [manual-task register](docs/manual-task-register.md). AWS AgentCore assets remain as an optional future architecture experiment; they are not a separate presenter demo.

Scenario presentation package:

- [Executive demo script](docs/demo-scripts/box-agentforce-react/01-executive-walkthrough.md)
- [Legal Operations demo script](docs/demo-scripts/box-agentforce-react/02-legal-operations-walkthrough.md)
- [Technical validation script](docs/demo-scripts/box-agentforce-react/03-technical-validation.md)
- [Box Form entry-point variation](docs/demo-scripts/box-agentforce-react/04-box-form-automate-entry.md)
- [Rendered demo flow](docs/diagrams/clm-box-agentforce-react-demo-flow.svg)
- [Rendered Box Form entry flow](docs/diagrams/clm-box-form-automate-entry.svg)
- [Demo component manifest](docs/demo-scripts/box-agentforce-react/component-manifest.md)
- [Machine-readable manifest](config/demo/box-agentforce-react-demo-manifest.json)

The scenario is an enterprise commercial contract workflow for **Acme Robotics** negotiating a master services agreement (MSA), data processing addendum (DPA), statement of work (SOW), and order form with **Northstar Health**.

---

## Demo Thesis

CLM teams lose time because contract content, structured deal data, obligations, risk positions, and approvals are split across systems. Validated Box intake creates the structured Salesforce CLM record, Box remains the governed content and workflow layer, Agentforce provides source-cited assistance, and the React UI Bundle presents one coherent contract workspace. Humans retain approval and signature authority.

---

## Documentation Index

| # | Document | Description |
|---|----------|-------------|
| 1 | [Architecture](docs/01-architecture.md) | Primary Box + Agentforce + React architecture and optional AgentCore expansion |
| 2 | [Agent Definitions](docs/02-agent-definitions.md) | CLM agent specifications, prompts, action groups, guardrails, and outputs |
| 3 | [Legal and Commercial References](docs/03-legal-commercial-references.md) | Demo-safe legal, privacy, revenue, and procurement reference model |
| 4 | [Control Matrix](docs/04-control-matrix.md) | Contract controls mapped to Box, Agentforce, React, and human reviewers |
| 5 | [ROI Analysis](docs/05-roi-analysis.md) | CLM value drivers, time compression model, and executive metrics |
| 6 | [Competitive Landscape](docs/06-competitive-landscape.md) | CLM market positioning and Box + AWS differentiation |
| 7 | [Handoff Progress](docs/08-handoff-progress.md) | Build checklist, sample-data plan, metadata model, and next actions |
| 8 | [Demo Runbook](docs/runbooks/04-box-agentforce-react-demo.md) | Primary CLM walkthrough with no AgentCore, Strands, or Databricks dependency |
| 9 | [Setup and Activation](docs/runbooks/05-demo-setup-and-activation.md) | End-to-end prerequisites, local rehearsal, Box verification, Salesforce/Agentforce deployment, activation, smoke test, and teardown |
| 10 | [Manual-Task Register](docs/manual-task-register.md) | Complete inventory of human decisions, administrator work, confirmation gates, live validation, and per-demo reset tasks |
| 11 | [Salesforce CLM Record Contract](docs/salesforce-clm-record-contract.md) | `CLM_Contract__c` schema, ownership, private sharing, idempotency, Box references, and intake mapping |

Repository organization recommendations: [Cleanup plan](docs/cleanup-plan.md).

### Runbooks

| Status | Runbook | Purpose |
|---|---|---|
| Primary | [Box + Agentforce + React](docs/runbooks/04-box-agentforce-react-demo.md) | Run the live Box surfaces and Salesforce UI Bundle as one CLM demo |
| Operator setup | [Setup and Activation](docs/runbooks/05-demo-setup-and-activation.md) | Bring the demo from local rehearsal through full integrated activation |
| Optional experiment | [AgentCore Prototype](docs/runbooks/03-agentcore-demo.md) | Evaluate a future multi-agent architecture outside the presenter flow |

---

## Contract Scenario

| Dimension | Detail |
|-----------|--------|
| Selling company | Acme Robotics, Inc. |
| Customer | Northstar Health System |
| Contract package | MSA, DPA, SOW, order form, security exhibit, insurance certificate |
| Value | $2.4M ARR, 36-month term |
| Risk themes | Limitation of liability, indemnity, PHI/data processing, SLA credits, auto-renewal, termination for convenience |
| Teams | Sales, Legal, Privacy, Security, Finance, Procurement, Customer Success |
| Outcome | Signed contract package, extracted obligations, renewal calendar, account handoff |

---

## Demo Components

| Component | Role in the primary demo |
|----------------|----------|
| Box Apps | CLM dashboard with deal pipeline, risk status, pending approvals, and contract workstreams |
| Box Forms | New contract request intake with requester, counterparty, value, contract type, and upload fields |
| Box Metadata | Contract record fields, risk scoring, clause status, business owner, renewal dates |
| Box AI | Summarize contract package, identify risky clauses, compare versions |
| Box Sign | Execute approved agreement |
| Box DocGen | Generate cover memo, approval packet, order-form summary, renewal notice |
| Box Automate | Form-triggered intake, Extract enrichment, Box AI Agent review, human approval, and HTTPS connector handoff |
| Box Hubs | Published, maintained library of approved standard and fallback clause Markdown files |
| Agentforce | Contract summary, structured redline comparison, domain routing explanation, approval readiness, and confirmed draft actions |
| React UI Bundle | Contract context, governed Box content, domain-grouped redline reviews, and Agentforce conversation in one workspace |

---

## Generated Demo Assets

Run the generator from this directory:

```bash
python3 scripts/generate_sample_contract_assets.py
```

Generated artifacts:

| Path | Purpose |
|------|---------|
| `output/pdf/northstar-msa-redline-v3.pdf` | Redline risk review with intentional issues |
| `output/pdf/northstar-dpa.pdf` | Privacy/security review with PHI trigger |
| `output/pdf/northstar-sow-implementation.pdf` | SLA and delivery obligations |
| `output/pdf/northstar-order-form.pdf` | Commercial mismatch against Salesforce-style record |
| `output/pdf/northstar-security-exhibit.pdf` | Security evidence obligations |
| `output/pdf/northstar-insurance-certificate.pdf` | Insurance renewal obligation |
| `output/json/northstar-clm-records.json` | Mock Salesforce/approval context |
| `output/json/clause-playbook.json` | Approved clause positions and fallback language |
| `output/csv/historical-clause-outcomes.csv` | Mock Databricks analytics context |
| `output/agentcore/northstar-agentcore-trace.json` | Generated AgentCore Strands supervisor trace |
| `output/docgen/clm-approval-memo-template.docx` | Live Box DocGen approval memo template |
| `output/docgen/clm-order-summary-template.docx` | Live Box DocGen commercial order summary template |
| `output/docgen/clm-renewal-notice-template.docx` | Live Box DocGen renewal notice template |
| `output/html/clm-experience-gallery.html` | Self-contained visual walkthrough using screenshots from the real Box and React demo experiences |

Config artifacts:

| Path | Purpose |
|------|---------|
| `config/box/metadata-templates.json` | Box metadata template definitions |
| `config/box/folder-template.md` | Workspace folder template |
| `config/box/box-app-blueprint.md` | Box App dashboard blueprint |
| `config/box/box-app-builder-checklist.md` | Click-by-click Box App web UI build checklist |
| `config/box/box-app-dashboard-live-spec.json` | Live Box App dashboard block spec with folder, file, and task IDs |
| `config/box/live-box-surface.json` | Live Box IDs for the created workspace, metadata templates, folders, and files |
| `config/box/docgen-template-data.json` | Sample merge payloads for the three live DocGen templates |
| `config/box/automate-workflows.json` | Automate workflow stages, guardrails, and live object bindings |
| `config/box/extract-field-prompts.json` | Field-level Extract prompts and validation expectations |
| `config/box/ai-agent-specs.json` | Box AI Agent instructions and human-review boundary |
| `config/box/https-connectors.json` | Salesforce standard REST external-ID upsert/lookup, deployed External Client App IDs, live REST verification, and the remaining Box-managed consumer-secret/OAuth test |
| `config/clm/redline-finding.schema.json` | Structured contract for cited, risk-classified redline findings |
| `config/clm/expert-routing.json` | Deterministic domain-to-expert directory with Legal Operations fallback |
| `config/box/hub-blueprint.md` | Lived-in approved clause Hub content and governance blueprint |
| `config/agentcore/agentcore-orchestration-spec.json` | Multi-agent orchestration spec |
| `config/agentcore/tool-contracts.json` | Box, Salesforce, and Databricks tool contracts |
| `config/agentcore/agent-handoff-payloads.json` | Supervisor-to-agent handoff payload examples |
| `config/agentforce/clm-react-agentforce-spec.json` | Agentforce topics, actions, mutation confirmations, and guardrails for the primary demo |
| `config/salesforce/clm-contract-record.json` | `CLM_Contract__c` ownership, idempotency, field mapping, Box references, and intake contract |
| `config/demo/box-agentforce-react-demo-manifest.json` | Complete machine-readable inventory of included runtime, React, Box, Agentforce, and presenter components |

React application:

```bash
cd clm-react-app/force-app/main/default/uiBundles/clmreactapp
npm install
npm test -- --run
npm run build -- --mode standalone
```

Rebuild the offline experience gallery after replacing any screenshot:

```bash
python3 scripts/build_clm_experience_gallery.py
```

Capture screenshots from the real Box or React page viewport only. Do not include browser tabs, the address bar, or unrelated desktop content.

Run the high-complexity local mock from this directory:

```bash
python3 scripts/run_agentcore_mock.py
python3 -m json.tool output/agentcore/northstar-agentcore-trace.json >/dev/null
```

---

## Reuse Pattern

This CLM variation is intentionally structured as a template for later use-case demos.

| Reusable Layer | How to Reuse for DAM / Government / Media / Insurance / Banking / Wealth |
|----------------|------------------------------------------------------------------------|
| Runtime boundary | Keep Box + Agentforce + React as one coherent presenter flow |
| Content model | Swap CLM contract package for asset package, case file, policy packet, loan file, or portfolio packet |
| Metadata model | Replace contract fields with the domain-specific record fields |
| Agent inventory | Keep intake, review, risk, approval, obligation/follow-up agents; rename for domain |
| Dashboard pattern | Keep KPI, pipeline, risk, workstream, and action cards |
| Sample-data generator | Produce realistic PDFs and JSON records per domain |
| Handoff doc | Track live Box/Salesforce/AWS build state for each variation |

---

## File Structure

```text
box-bedrock-for-clm/
├── README.md
├── clm-react-app/
│   └── force-app/main/default/
│       ├── objects/CLM_Contract__c/
│       ├── externalClientApps/Box_Automate_CLM.eca-meta.xml
│       ├── extlClntAppGlobalOauthSets/
│       ├── extlClntAppOauthSettings/
│       ├── extlClntAppOauthPolicies/
│       ├── permissionsets/
│       └── uiBundles/clmreactapp/
├── config/
│   ├── agentcore/
│   ├── agentforce/
│   ├── demo/
│   ├── salesforce/
│   └── box/
├── docs/
│   ├── 01-architecture.md
│   ├── 02-agent-definitions.md
│   ├── 03-legal-commercial-references.md
│   ├── 04-control-matrix.md
│   ├── 05-roi-analysis.md
│   ├── 06-competitive-landscape.md
│   ├── 08-handoff-progress.md
│   ├── demo-scripts/
│   │   └── box-agentforce-react/
│   ├── diagrams/
│   └── runbooks/
├── output/
│   ├── csv/
│   ├── agentcore/
│   ├── json/
│   └── pdf/
├── sample-data/
│   └── README.md
└── scripts/
    ├── README.md
    ├── generate_sample_contract_assets.py
    └── run_agentcore_mock.py
```

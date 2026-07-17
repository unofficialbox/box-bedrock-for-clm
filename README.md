# Contract Lifecycle Management Demo Scenarios

## Overview

This repository contains two presenter-ready CLM scenario packages built on the same Northstar contract data and governance model.

| Scenario | Model | Primary surface | Scope |
|---|---|---|---|
| [Box Automate–Led Agentic Orchestration](docs/scenarios/box-automate-agentic-orchestration/README.md) | Workflow-directed agents inside Box Automate | Box | Forms, Apps, Automate, Extract, Box and Agentforce agents, approvals, Hubs, Doc Gen, Sign, and governed Salesforce REST handoff |
| [Cross-Platform Agentic Orchestration](docs/scenarios/cross-platform-agentic-orchestration/README.md) | Supervisor-directed agents across platforms | Salesforce Multi-Framework React | Shared governed assets plus the React workspace, Databricks, AWS Bedrock AgentCore, Strands, memory, traces, and dynamic delegation; Box Automate remains inactive |

**New environment:** start with [CLM Demo Operator Start Here](docs/operator/00-start-here.md). It generates new Box and Salesforce bindings and never requires IDs from another environment.

**Presenting the demo:** choose a track in the [scenario selector](docs/scenarios/README.md). Every browser/admin/approval task is tracked in the [manual-task register](docs/manual-task-register.md).

Scenario presentation packages:

- [00 portable operator setup guide](output/html/00-operator-setup-guide.html)
- [Box Automate–Led Agentic Orchestration Markdown guide](docs/scenarios/box-automate-agentic-orchestration/README.md) · [01 portable guide](output/html/01-box-automate-agentic-orchestration-guide.html) · [02 visual gallery](output/html/02-box-automate-agentic-orchestration-gallery.html) · [manifest](config/demo/box-automate-agentic-orchestration-demo-manifest.json)
- [Cross-Platform Agentic Orchestration Markdown guide](docs/scenarios/cross-platform-agentic-orchestration/README.md) · [03 portable guide](output/html/03-cross-platform-agentic-orchestration-guide.html) · [04 visual gallery](output/html/04-cross-platform-agentic-orchestration-gallery.html) · [manifest](config/demo/cross-platform-agentic-orchestration-demo-manifest.json)
- [05 executive marketecture](output/html/05-executive-marketecture.html) — business value, governance, phased delivery, target architecture, and real-product proof for IT decision makers
- [06 coordinated contract-work marketecture](output/html/06-agentcore-agent-experience-marketecture.html) — Amazon Bedrock AgentCore coordinates specialized agents across Box, Salesforce Agentforce, and Databricks with evidence, controls, and human approvals
- [07 customer solution datasheet](output/html/07-customer-solution-datasheet.html) — nontechnical tell/show/tell overview for generalists, sales teams, customers, and IT decision makers
- [08 contract lifecycle readiness marketecture](output/html/08-contract-lifecycle-readiness-marketecture.html) — lifecycle swimlane view of persistent platform contributions, expert review, and approved execution
- [Marketecture design concepts](docs/design/marketecture-concepts/README.md) — committed visual references, explicitly separated from real-demo screenshot evidence
- [Agent orchestration messaging](docs/design/agent-orchestration-messaging.md) — researched messaging principles, approved headline system, and retired phrases for generated collateral

Review the numbered HTML files in order. Each **guide** contains the complete narrative, architecture, flow, presenter script, screenshots, readiness, and setup. Each **visual gallery** is the shorter screenshot-only companion.
- Existing detailed Box + Agentforce + React scripts remain inside `docs/scenarios/cross-platform-agentic-orchestration/supporting-react-scripts/` as supporting deep dives.

## Validate the repository

Install the declared Python and React validation dependencies once, then run the complete matrix:

```bash
python3 -m pip install -r requirements-dev.txt
npm install --global @mermaid-js/mermaid-cli@11.12.0
npm ci --prefix clm-salesforce-project/force-app/main/default/uiBundles/clmreactapp
python3 scripts/validate_clm.py
```

The command checks secrets and live-ID isolation, JSON and schemas, local links, Mermaid/SVG drift, Python and React tests, lint, build, Playwright, deterministic fixtures and presenter output, scenario and screenshot manifests, portability, and reset/idempotency contracts. Repository mode intentionally skips live-environment receipts.

After completing the integrated live tests, copy `config/runtime/validation-receipts.example.json` to the gitignored `config/runtime/validation-receipts.json`, replace every example value with current evidence, and run:

```bash
python3 scripts/validate_clm.py --presenter-ready
```

This stricter mode fails closed unless Box, Salesforce, AgentCore, and Databricks have current passed receipts. It does not treat repository tests as proof of live deployment.

The scenario is an enterprise commercial contract workflow for **Acme Robotics** negotiating a master services agreement (MSA), data processing addendum (DPA), statement of work (SOW), and order form with **Northstar Health**.

---

## Demo Thesis

CLM teams lose time because contract content, structured deal data, obligations, risk positions, and approvals are split across systems. Box Automate–Led Agentic Orchestration shows agents working inside a designed business process; Cross-Platform Agentic Orchestration shows a supervisor dynamically coordinating specialists across systems. In both, Box remains authoritative for contract content and humans retain approval and signature authority.

---

## Documentation Index

| # | Document | Description |
|---|----------|-------------|
| 1 | [Architecture](docs/01-architecture.md) | Shared foundations plus Box Automate–Led Agentic Orchestration and Cross-Platform Agentic Orchestration architecture |
| 2 | [Agent Definitions](docs/02-agent-definitions.md) | CLM agent specifications, prompts, action groups, guardrails, and outputs |
| 3 | [Legal and Commercial References](docs/03-legal-commercial-references.md) | Demo-safe legal, privacy, revenue, and procurement reference model |
| 4 | [Control Matrix](docs/04-control-matrix.md) | Contract controls mapped to Box, Agentforce, React, and human reviewers |
| 5 | [ROI Analysis](docs/05-roi-analysis.md) | CLM value drivers, time compression model, and executive metrics |
| 6 | [Competitive Landscape](docs/06-competitive-landscape.md) | CLM market positioning and Box + AWS differentiation |
| 7 | [Operator Start Here](docs/operator/00-start-here.md) | Fresh-environment bootstrap, automation, browser tasks, and validation |
| 8 | [Scenario Packages](docs/scenarios/README.md) | Two ordered single-page guides referencing shared manifests, diagrams, galleries, and screenshots |
| 9 | [Manual-Task Register](docs/manual-task-register.md) | Complete inventory of human decisions, administrator work, confirmation gates, live validation, and per-demo reset tasks |
| 10 | [Salesforce CLM Record Contract](docs/salesforce-clm-record-contract.md) | `CLM_Contract__c` schema, ownership, private sharing, idempotency, Box references, and intake mapping |

### Runbooks

| Status | Runbook | Purpose |
|---|---|---|
| Box Automate–Led deep dive | [Box + Agentforce + React](docs/runbooks/04-box-agentforce-react-demo.md) | Supporting details for the workflow-directed Box/Agentforce path and React handoff |
| Cross-Platform deep dive | [AgentCore runbook](docs/runbooks/03-agentcore-demo.md) | Run or evaluate the supervisor-led multi-agent path |

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

| Component | Role across the two scenarios |
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
| `output/html/00-operator-setup-guide.html` | Complete, self-contained fresh-environment operator guide |
| `output/html/01-box-automate-agentic-orchestration-guide.html` | Complete, self-contained Box Automate–Led Agentic Orchestration narrative |
| `output/html/02-box-automate-agentic-orchestration-gallery.html` | Visual-only Box Automate–Led Agentic Orchestration gallery using real Box screens |
| `output/html/03-cross-platform-agentic-orchestration-guide.html` | Complete, self-contained Cross-Platform Agentic Orchestration narrative |
| `output/html/04-cross-platform-agentic-orchestration-gallery.html` | Visual-only Cross-Platform Agentic Orchestration gallery using real Box and React screens |
| `output/html/05-executive-marketecture.html` | Executive, non-technical marketecture for IT and business decision makers |
| `output/html/06-agentcore-agent-experience-marketecture.html` | Executive variation showing coordinated contract work across content, business data, analytics, and accountable teams |
| `output/html/07-customer-solution-datasheet.html` | Customer-facing Box Solutions datasheet centered on experience, outcomes, and the CLM starting point |
| `output/html/08-contract-lifecycle-readiness-marketecture.html` | Executive lifecycle marketecture showing persistent platform responsibilities and human decision authority |

Config artifacts:

| Path | Purpose |
|------|---------|
| `config/box/metadata-templates.json` | Box metadata template definitions |
| `config/box/folder-template.md` | Workspace folder template |
| `config/box/form-blueprint.md` | Canonical Form fields, options, confirmation, and validation |
| `config/box/box-app-blueprint.md` | Box App dashboard blueprint |
| `config/box/docgen-template-data.json` | Portable sample merge payloads for the three Doc Gen templates |
| `config/box/automate-workflows.json` | Portable workflow stages and guardrails; resolve bindings with `demo_operator.py` |
| `config/box/extract-field-prompts.json` | Field-level Extract prompts and validation expectations |
| `config/box/ai-agent-specs.json` | Box AI Agent instructions and human-review boundary |
| `config/box/https-connectors.json` | Portable standard REST external-ID operations with runtime binding tokens |
| `config/clm/redline-finding.schema.json` | Structured contract for cited, risk-classified redline findings |
| `config/clm/expert-routing.json` | Deterministic domain-to-expert directory with Legal Operations fallback |
| `config/box/hub-blueprint.md` | Lived-in approved clause Hub content and governance blueprint |
| `config/agentcore/agentcore-orchestration-spec.json` | Multi-agent orchestration spec |
| `config/agentcore/tool-contracts.json` | Box, Salesforce, and Databricks tool contracts |
| `config/agentcore/agent-handoff-payloads.json` | Supervisor-to-agent handoff payload examples |
| `config/agentforce/clm-react-agentforce-spec.json` | Shared Agentforce topics, actions, mutation confirmations, and guardrails used by both scenarios |
| `config/salesforce/clm-contract-record.json` | `CLM_Contract__c` ownership, idempotency, field mapping, Box references, and intake contract |
| `config/demo/box-automate-agentic-orchestration-demo-manifest.json` | Box Automate–Led Agentic Orchestration runtime, readiness, documentation, and screenshot inventory |
| `config/demo/cross-platform-agentic-orchestration-demo-manifest.json` | Cross-Platform Agentic Orchestration runtime, readiness, documentation, trace, and screenshot inventory |
| `config/operator/operator-workflow.json` | Machine-readable phase, authority, confirmation, and completion contract for human or AI-assisted setup |
| `config/runtime/demo-environment.example.json` | Secret-free per-environment input template; copy to the gitignored runtime file |

Salesforce project UI Bundle:

```bash
cd clm-salesforce-project/force-app/main/default/uiBundles/clmreactapp
npm install
npm test -- --run
npm run build -- --mode standalone
```

Rebuild the offline experience gallery after replacing any screenshot:

```bash
python3 scripts/build_clm_experience_gallery.py
```

Capture screenshots from the real Box or React page viewport only. Store them under the matching scenario directory. Do not include browser tabs, the address bar, or unrelated desktop content. Do not create simulated AWS or Databricks screenshots.

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
| Runtime state | Record each operator's generated Box/Salesforce bindings in ignored runtime files |

---

## File Structure

```text
box-bedrock-for-clm/
├── README.md
├── clm-salesforce-project/
│   └── force-app/main/default/
│       ├── objects/CLM_Contract__c/
│       ├── permissionsets/
│       └── uiBundles/clmreactapp/
├── config/
│   ├── agentcore/
│   ├── agentforce/
│   ├── demo/
│   ├── operator/
│   ├── runtime/                 # example plus gitignored environment bindings
│   ├── salesforce/
│   └── box/
├── docs/
│   ├── 01-architecture.md
│   ├── 02-agent-definitions.md
│   ├── 03-legal-commercial-references.md
│   ├── 04-control-matrix.md
│   ├── 05-roi-analysis.md
│   ├── 06-competitive-landscape.md
│   ├── operator/                # canonical fresh-environment path
│   ├── scenarios/
│   │   ├── box-automate-agentic-orchestration/
│   │   └── cross-platform-agentic-orchestration/
│   ├── diagrams/
│   └── runbooks/
├── output/
│   ├── csv/
│   ├── agentcore/
│   ├── html/
│   ├── json/
│   ├── pdf/
│   └── screenshots/
│       ├── box-automate-agentic-orchestration/
│       └── cross-platform-agentic-orchestration/
├── sample-data/
│   └── README.md
└── scripts/
    ├── README.md
    ├── demo_operator.py
    ├── build_clm_experience_gallery.py
    ├── generate_sample_contract_assets.py
    └── run_agentcore_mock.py
```

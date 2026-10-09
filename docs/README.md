# Documentation

One topic per file. Read the one you need; the guides link onward where a path genuinely
crosses roles.

## By role

| Role | Start here |
|---|---|
| Operating a demo | [OPERATING.md](OPERATING.md) — the ordered run, from environment to rehearsal |
| Understanding or tailoring CLM | [USE-CASE.md](USE-CASE.md) — what the use case is and what it decides |
| Changing the repository | [MAINTAINING.md](MAINTAINING.md) — source precedence, workflow, release gates |

## Topics

| File | What it covers |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Box, Salesforce and the governed actions between them |
| [SETUP.md](SETUP.md) | Bringing a fresh environment up |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Every value bound to one org or Box enterprise, and what breaks without it |
| [CLIENT-SETUP.md](CLIENT-SETUP.md) | Browser and administrator configuration |
| [DOCUMENTS-SETUP.md](DOCUMENTS-SETUP.md) | Governed Box content and the downscoped-token preview path |
| [MANUAL-TASKS.md](MANUAL-TASKS.md) | The work no script can safely do, by ID |
| [SMOKE-TEST.md](SMOKE-TEST.md) | The integrated check before rehearsing |
| [SCENARIO-GUIDE.md](SCENARIO-GUIDE.md) | The Box + Salesforce Contract Lifecycle scenario |
| [PRESENTING.md](PRESENTING.md) | Presenter deliverables |
| [FINALIZATION.md](FINALIZATION.md) | The end-to-end completion gate |
| [EMAIL-INTAKE.md](EMAIL-INTAKE.md) | The inbound email intake service |
| [SALESFORCE-RECORD.md](SALESFORCE-RECORD.md) | The `CLM_Contract__c` record contract |
| [CONSTRAINTS.md](CONSTRAINTS.md) | What bites: Box, Salesforce and box-ui-elements behaviour this repo has already paid for |
| [CONVENTIONS.md](CONVENTIONS.md) | Readiness vocabulary, the safety contract, and the config model |

The beats themselves live in [DEMO-STORYBOARD.html](../DEMO-STORYBOARD.html) at the
repository root, and the presenter rules an assistant follows live in
[skills/clm-contract-lifecycle/SKILL.md](../skills/clm-contract-lifecycle/SKILL.md).

## Collections

| Directory | Contents |
|---|---|
| [alternate-scripts/](alternate-scripts/) | Other ways to run the same assets: executive, technical, Box-metadata entry |
| [diagrams/](diagrams/) | Mermaid sources and their synchronized SVG renders |
| [design/](design/) | Brand assets and marketecture concepts |

[CONVENTIONS.md](CONVENTIONS.md) — the readiness vocabulary and the safety contract —
applies to every path. All durable links and commands are repository-relative; run commands
from the repository root unless a guide explicitly changes directories.

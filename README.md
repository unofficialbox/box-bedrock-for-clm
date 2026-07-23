# Contract Lifecycle Management Demo

This repository contains a mature Contract Lifecycle Management demo with two orchestration scenarios, deterministic local fixtures, portable configuration, real-product screenshots, and self-contained presenter output.

## Choose one path

| Goal | Start here |
|---|---|
| Configure, deploy, validate, or present the demo | [Operator guide](docs/operator/README.md) |
| Understand or tailor the CLM domain, controls, agents, and value story | [Use-case creator guide](docs/use-case-creator/README.md) |
| Change code, configuration, tests, generated assets, or release state | [Maintainer guide](docs/maintainers/README.md) |

The complete persona index is in [docs/README.md](docs/README.md). AI assistants must read this file and exactly one matching persona instruction before exploring further.

## Scenarios

| Scenario | Primary surface | Coordination model |
|---|---|---|
| [Box Automate Agentic Orchestration](docs/operator/scenarios/box-automate-agentic-orchestration/README.md) | Box | Box Automate coordinates Forms, Extract, Box and Agentforce agents, human approvals, Hubs, Doc Gen, Sign, and a governed Salesforce REST handoff. |
| [Cross-Platform Agentic Orchestration](docs/operator/scenarios/cross-platform-agentic-orchestration/README.md) | Salesforce Multi-Framework React | Amazon Bedrock AgentCore coordinates Box, Salesforce Agentforce, and Databricks specialists while humans retain decision authority. |

Both scenarios use the same Northstar contract package and governance model. Box remains authoritative for contract content; Salesforce `CLM_Contract__c` remains authoritative for structured commercial truth.

## Readiness vocabulary

Use these exact terms in documentation, configuration, and presenter claims:

| State | Meaning |
|---|---|
| **Portable specification** | Secret-free architecture, contracts, manifests, prompts, and setup instructions exist. |
| **Local deterministic fixture** | Repeatable local data, traces, documents, UI tests, or presenter output demonstrate the contract without claiming a live integration. |
| **Deployed integration** | The capability has passed current tests in the named target environment with secret-free evidence. |
| **Presenter-ready live** | The complete scenario has current receipts, screenshots, reset evidence, and a rehearsed human-operated path. |

Never promote a capability based only on configuration files or local fixtures.

## Validate

Before running validation commands, complete operator prerequisites:

- Authenticate the CLIs used by demo setup:
  - `box login -d` (or your standard Box auth flow)
  - `sf org login web` (or org auth flow you already use)
- Confirm you are in the CLM repo root.

Run the onboarding smoke check first. It only probes CLI sessions and prints a safe, simulated install plan:

```bash
python3 scripts/setup_clm_dev.py --smoke
```

Install dependencies and create the runtime config in one command:

```bash
python3 scripts/setup_clm_dev.py
```

What setup command variants do:

- `--automated`: runs without prompts for CI or scripted setup.
- `--from-current-clis`: preloads Box/Salesforce IDs and login values from the authenticated CLIs into `config/runtime/demo-environment.json`.

```bash
python3 scripts/setup_clm_dev.py --automated --from-current-clis
```

Run the full non-live validation gate (unit/lint/tests/build/schema checks, local presenter artifacts, and safety contracts):

```bash
python3 scripts/validate_clm.py
```

It checks secrets and runtime-ID isolation, JSON schemas, Markdown links, Mermaid/SVG drift, Python and React tests, lint, build, Playwright, deterministic fixtures, presenter output, screenshot manifests, reset behavior, and idempotency contracts. Repository mode intentionally skips live receipts.

After integrated testing and smoke verification, create the gitignored `config/runtime/validation-receipts.json` from its example and run presenter-readiness validation:

```bash
python3 scripts/validate_clm.py --presenter-ready
```

This fails closed unless Box, Salesforce, AgentCore, and Databricks have current secret-free passed receipts.

## Portable presenter output

Start with the [presenter library](output/html/index.html). It routes to each standalone file and to the [complete self-contained edition](output/html/09-complete-presenter-edition.html).

Review the standalone files in order:

1. [Operator setup guide](output/html/00-operator-setup-guide.html)
2. [Box Automate scenario guide](output/html/01-box-automate-agentic-orchestration-guide.html)
3. [Box Automate visual gallery](output/html/02-box-automate-agentic-orchestration-gallery.html)
4. [Cross-platform scenario guide](output/html/03-cross-platform-agentic-orchestration-guide.html)
5. [Cross-platform visual gallery](output/html/04-cross-platform-agentic-orchestration-gallery.html)
6. [Executive marketecture](output/html/05-executive-marketecture.html)
7. [Coordinated contract-work marketecture](output/html/06-agentcore-agent-experience-marketecture.html)
8. [Customer solution datasheet](output/html/07-customer-solution-datasheet.html)
9. [Contract lifecycle readiness marketecture](output/html/08-contract-lifecycle-readiness-marketecture.html)

The combined edition embeds all nine chapters and requires no sibling files or network access. The Markdown source remains authoritative. Generated HTML is the portable sharing layer.

## Safety contract

- Keep credentials and target-environment identifiers in ignored runtime files.
- Use external IDs for duplicate-safe Salesforce and Box operations.
- Separate dry-run planning from explicit apply operations.
- Confirm the exact enterprise, org, folder, and record before external writes.
- Require human approval for legal positions, document generation, signature, publishing, sharing, and destructive reset actions.
- Preserve citations for material contract findings.
- Record partial failures and reconcile before retrying.
- Reset only resources owned by the current demo run and retain evidence.

## Source map

| Path | Purpose |
|---|---|
| `config/` | Portable platform, scenario, operator, and runtime contracts |
| `docs/use-case-creator/` | CLM architecture, agents, controls, references, value, and marketecture |
| `docs/operator/` | Ordered environment setup, deployment, validation, and presentation path |
| `docs/maintainers/` | Source precedence, development workflow, validation, and release rules |
| `docs/diagrams/` | Mermaid sources and synchronized SVG renders |
| `sample-data/` | Synthetic CLM inputs and governed clause Markdown |
| `scripts/` | Deterministic generators, operator automation, mocks, and validation |
| `tests/` | Repository, safety, fixture, presenter, and navigation checks |
| `clm-salesforce-project/` | Salesforce metadata and Multi-Framework React UI Bundle |
| `output/` | Generated fixtures, traces, screenshots, and portable presenter deliverables |

Run commands from the repository root unless a guide explicitly changes directories. Use repository-relative paths in every durable file.

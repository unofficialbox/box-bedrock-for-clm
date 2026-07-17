# CLM Demo vs. Box Bedrock Template

## Comparison and reconciliation plan

**Reviewed:** 2026-07-17  
**Demo:** `box-bedrock-for-clm/` at `04600d9`  
**Template baseline reviewed read-only:** `../box-bedrock-template/` branch `codex/life-sciences-template-reconciliation` at `5e99aa2`  
**Baseline document:** [`box-bedrock-template-clm-comparison-and-reconciliation.md` at `5e99aa2`](https://github.com/unofficialbox/box-bedrock-template/blob/5e99aa2935567460133d542db1ccb244a537d9be/box-bedrock-template-clm-comparison-and-reconciliation.md)

## Executive decision

CLM is the current **maturity benchmark** for Box Bedrock solution demos. It has the strongest combined evidence across live Box and Salesforce surfaces, two clearly separated orchestration scenarios, operator guidance, portable configuration, real screenshots, self-contained presenter output, executive messaging, and automated regression checks.

Use CLM to improve the template's reusable operating system. Do not turn the template into a CLM clone. Contract-specific objects, clauses, prompts, screenshots, and legal workflows remain vertical assets.

The template's description of Life Sciences as the forward-looking reference vertical is compatible with this assessment: Life Sciences is the next portability proof, while CLM remains the most mature implementation and presentation benchmark. Use this hierarchy:

1. **Template** — portable scaffold and validation contract.
2. **CLM** — most mature implementation and presenter-quality benchmark.
3. **Life Sciences** — forward-looking portability proof and domain specialization.
4. **Citizen Services** — additional domain specialization reconciled against the same contracts.

No template files were changed during this review.

## Evidence reviewed

- Full CLM Git history from the initial import through PR #12.
- Current documentation, configuration, scripts, tests, sample data, generated output, diagrams, and screenshots.
- Template phase model, profiles, validation matrix, and current Life Sciences reconciliation branch.
- Repository status and ownership boundaries.

This is a repository-evidence assessment. A committed contract is not proof that its external service is currently deployed or authenticated.

## Maturity summary

| Area | CLM assessment | Evidence | Template action |
|---|---|---|---|
| Git ownership | Reference-ready | Clean `main`, tracked PR history, no wrapper ambiguity | Preserve as the expected generated-demo ownership model |
| Scenario model | Reference-ready | Box Automate–Led and Cross-Platform Agentic Orchestration have separate start pages and manifests | Keep exactly two canonical scenarios |
| Operator experience | Strong | Start-here, entitlement, browser, smoke, deployment, AI-operator, and manual-task guides | Promote the concise navigation and human/AI operator split |
| Box surface contracts | Strong | Forms, Apps, Automate, Extract, agents, HTTPS connector, Hub, DocGen, folders, and metadata | Keep portable specs; add UI build verification as environment evidence |
| Salesforce and Agentforce | Strong | `CLM_Contract__c`, metadata, permissions, React UI Bundle, OAuth/connector path | Preserve standard REST and external-ID defaults |
| AgentCore and Databricks | Partial live readiness | Contracts and local fixtures exist; presenter material explicitly treats managed deployment as a readiness gate | Keep the truthful portable/local/deployed vocabulary |
| Fixtures and reset | Strong portable layer | Clauses, contracts, redlines, expected outputs, manifests, and operator reset planning | Promote manifest-driven fixtures and stable business keys |
| Diagrams | Strong | Maintained Mermaid and SVG architecture, flow, operator, form-entry, and React integration views | Add drift validation consistently across demos |
| Presenter output | Benchmark | Numbered operator/scenario HTML, marketecture, datasheet, lifecycle-responsibility view, and real screenshots | Keep CLM as the content-quality benchmark; the template now owns the reusable lifecycle generator |
| Automated verification | Reconciled | `scripts/validate_clm.py` reports repository and fail-closed presenter-readiness matrices | Keep the command aligned with new artifacts and live receipt contracts |

## What the Git history teaches

The CLM history records a useful maturation sequence:

1. **Live foundation:** Box surfaces, Salesforce integration, OAuth, and handoff evidence.
2. **Experience correction:** Apps and Hub refinements based on browser-visible review.
3. **Scenario separation:** one Box-led scenario and one cross-platform supervisor-led scenario.
4. **Documentation consolidation:** ordered guides with shared assets referenced instead of duplicated.
5. **Portability:** live IDs moved behind configuration and new-environment instructions.
6. **Operator readiness:** manual tasks, safe setup, validation, and human decision boundaries.
7. **Presenter quality:** screenshots, offline HTML, marketecture, official logos, message testing, and a cross-vertical lifecycle-responsibility benchmark.

That order should inform template evolution. It also shows why feature inventory alone is not a maturity measure: the most reusable work came from consolidation, portability, verification, and presentation after the live implementation existed.

The Git history begins with an imported implementation on 2026-07-14, so it does not prove the chronology of every earlier external-system build step.

## Template phase reconciliation

| Phase | CLM status | Reconciliation |
|---|---|---|
| 0. Ownership and safety | Complete | Use clean root ownership, ignored secrets, and environment-bound IDs as the standard |
| 1. Scenario and documentation scaffold | Complete | Promote ordered navigation and shared-reference rules |
| 2. Box and environment bootstrap | Strong | Retain safe plan/apply/confirm behavior; strengthen machine-readable live evidence |
| 3. Salesforce experience | Strong | Preserve profile choice, standard REST default, stable external IDs, and server-side credential boundaries |
| 4. Fixtures and presenter assets | Complete at portable level | The template now has numbered HTML and a reusable lifecycle generator; continue promoting official brand assets, screenshot freshness checks, and deterministic generators |
| 5. Verification and rehearsal | Reconciled at repository level | One command now covers tests, links, diagram drift, generators, manifests, screenshots, browser checks, and portable reset/idempotency contracts; live receipts remain environment-specific |
| 6. Managed orchestration | Contract-ready, not fully proven live | Require deployed AgentCore and Databricks traces before presenter-ready live claims |

## Reconciliation actions

### P0 — maturity language and navigation

- Make CLM the implementation maturity benchmark in maintainer documentation.
- Keep the four readiness labels: portable specification, local deterministic fixture, deployed integration, and presenter-ready live.
- Retain the template's ordered operator start page and one ordered path for each scenario.
- Retain shared architecture, setup, and platform documents in one location and reference them from scenario pages.

### P1 — presenter and brand system

- Retain the numbered offline-output convention now present in both repositories.
- Port the remaining reusable layouts for executive marketecture, AgentCore experience, and customer datasheets; the template already owns operator, scenario, gallery, and lifecycle layouts.
- Treat the template's lifecycle-responsibility generator as the reusable source and CLM's `08-contract-lifecycle-readiness-marketecture.html` as a domain-content benchmark, not a second generic implementation.
- Port official-logo handling and the regression rules in `tests/test_html_branding.py`.
- Port the messaging principles in `docs/design/agent-orchestration-messaging.md` without copying CLM-specific claims.
- Add a screenshot manifest with capture date, source surface, scenario, crop requirements, and freshness state.

### P1 — unified validation

Add one root command that reports:

- placeholder and secret scans;
- JSON and schema validity;
- Markdown links;
- Mermaid/SVG drift;
- unit, lint, build, and browser tests for the selected Salesforce profile;
- deterministic fixture and presenter generation;
- scenario-manifest and screenshot-manifest completeness;
- absence of live IDs outside ignored runtime state;
- clean reset and idempotent rerun evidence.

### P2 — live-evidence receipts

- Define machine-readable receipts for Box, Salesforce, Databricks, and AgentCore deployment and smoke tests.
- Record environment identity, timestamp, action mode, object type, stable business key, result, and cleanup owner without storing secrets.
- Make presenter-ready live fail closed when required receipts or current screenshots are absent.

## CLM-specific assets that must not enter the generic scaffold

- `CLM_Contract__c`, legal metadata fields, clause taxonomies, redline domains, and reviewer assignments.
- Approved clause Markdown, contract request fields, legal prompts, and contract fixture content.
- CLM App, Hub, Form, Automate workflow, folder, task, template, and record identifiers.
- Acme/Northstar presenter content and CLM screenshots.
- Contract-specific Salesforce UI, DocGen templates, and approval language.

These belong in a CLM example pack or generated vertical, not in template defaults.

## CLM gaps to close without waiting on the template

| Priority | Gap | Done when |
|---|---|---|
| Complete | Single top-level verification command | `python3 scripts/validate_clm.py` produces the repository matrix; `--presenter-ready` additionally requires live receipts |
| P0 | Managed AgentCore and Databricks remain readiness gates | Current deployed traces and bounded-query evidence exist, or all output remains explicitly labelled illustrative/local |
| Complete | Screenshot freshness is explicit | `config/demo/screenshot-manifest.json` maps every screenshot to its source, capture date, crop rule, scenario, and readiness state |
| Complete | Diagram synchronization is visible | Every maintained `.mmd`/`.svg` pair is drift-checked by the root validator |
| P1 | Versioned release state is weak | Add a small `VERSION`/`CHANGELOG` convention or an equivalent release manifest |
| P2 | External-system reset evidence is mostly procedural | Repeated setup/run/reset produces idempotent receipts for owned demo objects |

## Copy contract for other template repositories

When copying this document into another template repository:

1. Preserve the maturity criteria and phase vocabulary.
2. Replace CLM evidence paths with that template's generated-project evidence.
3. Keep CLM as a comparative benchmark, not a dependency.
4. Separate reusable platform contracts from vertical content.
5. Do not copy live IDs, screenshots, credentials, tenant names, or customer fixtures.
6. Keep this reconciliation maintainer-only and exclude it from generated demos unless explicitly requested.

## Definition of reconciled

The template and CLM are reconciled when:

- a new operator can generate a demo, select one of the two scenarios, and follow one ordered path;
- an AI operator can validate the same steps from machine-readable contracts;
- no maintained source depends on CLM's live environment identifiers;
- local validation is deterministic and live actions require explicit confirmation;
- current screenshots and receipts distinguish configured, deployed, and presenter-ready states;
- CLM-specific legal content remains isolated from the portable scaffold.

## Recommended next step

Execute the Cross-Platform Agentic Orchestration path in current managed environments and populate secret-free Box, Salesforce, AgentCore, and Databricks validation receipts. The repository contract is now reconciled; current bounded live evidence is the remaining requirement before the full scenario can pass `python3 scripts/validate_clm.py --presenter-ready`.

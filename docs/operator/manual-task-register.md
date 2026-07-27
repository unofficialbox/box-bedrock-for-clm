# CLM Demo Manual-Task Register

This register lists only work that cannot be completed safely by `scripts/demo_operator.py`. Complete it for each new environment.

Status values: **Required**, **Per run**, **Optional**, and **Confirmation required**.

## Environment and access

| ID | Task | Owner | Status | Complete when |
|---|---|---|---|---|
| MT-001 | Confirm the target Box enterprise and Salesforce org | Demo owner | Required | Hostname, org alias, and safe test scope are recorded locally |
| MT-002 | Confirm required Box and Salesforce licenses/features | Administrators | Required | Every selected product surface opens for its operator |
| MT-003 | Name workflow, legal, privacy, security, finance, publishing, and signing owners | Demo owner | Required | Owners and escalation path are recorded |
| MT-004 | Store credentials outside source control | Administrators | Required | Secrets exist only in managed connections or protected secret stores |
| MT-005 | Sign in to the intended Box web application before browser-agent configuration | Box operator | Required for Apps, Automate, and Hub composition | An authenticated tab is open on the exact configured hostname under the intended builder account; no browser credentials are exported |

## Box browser work

| ID | Task | Owner | Status | Complete when |
|---|---|---|---|---|
| MT-010 | Review deterministic metadata applied by `seed-metadata` | Content owner | Required | Values are appropriate and App views/charts contain useful data |
| MT-011 | Mark the three Word files as Doc Gen templates | Doc Gen admin | Required | Templates appear in the Doc Gen catalog |
| MT-012 | Verify the `clmContract` metadata trigger entry point for intake | Content owner | Required | The generated `01 - Intake` folder and the `clmContract` metadata template exist, and applying `clmContract` metadata to a test file uploaded there starts **CLM - Contract Intake Enrichment** |
| MT-013 | Build **Contract Lifecycle Management** | Apps builder | Required | Actions are first; status, risk, type, region, and clause charts are useful |
| MT-014 | Build **Approved Contract Clause Library** | Hub owner | Required | Approved clauses, fallbacks, ownership, and review cadence are visible |
| MT-015 | Build and save the Automate workflows | Workflow builder | Required | Bindings use only this environment's generated IDs |
| MT-016 | Publish or republish an App or Hub | Surface owner | Confirmation required | Owner approves immediately before the consequential action |
| MT-017 | Activate an Automate workflow | Workflow owner | Confirmation required | Trigger, scope, destination, idempotency, rollback, and test plan are reviewed |
| MT-018 | Generate a Doc Gen output | Authorized reviewer | Confirmation required | One intended file is created after approval |
| MT-019 | Send a Box Sign request | Signatory coordinator | Confirmation required | Required approvals are complete and send is separately approved |
| MT-020 | Share externally or change collaborators | Content owner | Confirmation required | Exact users, items, and access are approved |

## Salesforce and Agentforce

| ID | Task | Owner | Status | Complete when |
|---|---|---|---|---|
| MT-030 | Authenticate Salesforce CLI and review the target org | Salesforce operator | Required | `sf org display` matches the intended org |
| MT-031 | Create a dedicated API-only integration user | Salesforce admin | Required | User has `CLM_Box_Automate_Integration` and no broad business access |
| MT-032 | Create/configure the environment-specific External Client App | Salesforce admin | Required | Client credentials, `api` scope, Run As user, and admin preauthorization are set |
| MT-033 | Configure the Box-managed OAuth connection | Box/Salesforce admins | Required | Token test succeeds without exposing the token |
| MT-034 | Add the UI Bundle to a Lightning or Experience page | Salesforce admin | Required for Cross-Platform Agentic Orchestration | Intended users can open it with record and Box context |
| MT-035 | Configure Contract Copilot topics, actions, and guardrails | Agentforce admin | Required for live Agentforce | Cited reads work; mutations require confirmation |
| MT-036 | Configure the Salesforce origin in the Box application | Box app admin | Required for live embedded Box | Only approved origins can load content |

## Review routing and testing

| ID | Task | Owner | Status | Complete when |
|---|---|---|---|---|
| MT-050 | Select real domain experts or managed groups | Legal Operations | Required | Every active domain has an owner and triage fallback |
| MT-051 | Grant least-privilege Box access to reviewers | Content owner | Required | Each reviewer can access only required items |
| MT-052 | Validate low-confidence and missing-owner triage | Legal Operations | Required | Exceptions route to the named triage owner |
| MT-053 | Submit a labeled test intake | Demo operator | Per run | File, workflow run, and one Salesforce record are visible |
| MT-054 | Validate duplicate-safe Salesforce behavior | Salesforce operator | Per run | Repeated contract ID updates the same record |
| MT-055 | Inspect citations and human task ownership | Human validator | Per run | Unsupported output is corrected; people retain approval authority |
| MT-056 | Confirm signature is blocked | Legal Operations | Per run | Incomplete required work prevents execution |

## Presenter and reset

| ID | Task | Owner | Status | Complete when |
|---|---|---|---|---|
| MT-070 | Rehearse the selected tell/show/tell script | Presenter | Per run | Script completes inside its time box without hidden setup |
| MT-071 | Pre-open only the selected scenario's surfaces | Presenter | Per run | Every page loads under the intended account |
| MT-072 | Capture screenshots from the real page viewport and update `config/demo/screenshot-manifest.json` | Maintainer | After UI changes | No browser chrome, documentation pages, or unrelated content appears; source, date, scenario, and readiness are current |
| MT-073 | Record test artifacts and restore demo state | Operator | Per run | Workflows/tasks are ready for the next session |
| MT-074 | Delete data or remove collaborators | System owner | Confirmation required | Impact is reviewed and exact objects are approved |

Use the run log in [Integrated Smoke Test](smoke-test.md). Store environment-specific IDs and completion evidence only in the gitignored runtime files or the operator's external run log.

For fail-closed readiness, copy `config/runtime/validation-receipts.example.json` to the gitignored `config/runtime/validation-receipts.json`, record only secret-free references to the current external run log, and run `python3 scripts/validate_clm.py --presenter-ready`.

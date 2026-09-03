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
| MT-031 | Create a dedicated API-only integration user | Salesforce admin | Required | User is assigned `CLM_Contract_Internal` and nothing else. That set is shared with the presenter and the agent user, so an API-only user now carries the same internal grants they do. That is the price of one internal permission set instead of four; split it back out if an environment needs the integration user narrower than its operators |
| MT-032 | Create/configure the environment-specific External Client App | Salesforce admin | Required | Client credentials, `api` scope, Run As user, and admin preauthorization are set |
| MT-033 | Configure the Box-managed OAuth connection | Box/Salesforce admins | Required | Token test succeeds without exposing the token |
| MT-034 | Add the UI Bundle to a Lightning or Experience page (requires MT-041) | Salesforce admin | Required for Box + Salesforce Contract Lifecycle | Intended users can open it with record and Box context |
| MT-035 | Configure Contract Copilot topics, actions, and guardrails | Agentforce admin | Required for live Agentforce | Cited reads work; mutations require confirmation |
| MT-036 | Configure the Salesforce origin in the Box application | Box app admin | Required for live embedded Box | Only approved origins can load content |
| MT-037 | Create and authorize the Box platform app **in the same enterprise the Box for Salesforce package writes to** | Box admin | Required for live Box preview | A Client Credentials Grant app is authorized in that enterprise's Admin Console. An app authorized elsewhere fails with `invalid_grant: App is not yet authorized for use`, and one authorized in a *different* enterprise from the package mints tokens fine but cannot see the folders the package creates -- the downscope then fails with `invalid_resource` |
| MT-038 | Set the Box client id and secret with `configure-clm-box-credential.sh` | Salesforce admin | Required for live Box preview | `ClientId` and `ClientSecret` are set on `CLM_Box_Principal`; values stay encrypted in the org and never reach source |
| MT-039 | Set the Box CCG subject and folder allowlist with `configure-clm-box-settings.sh` | Salesforce admin | Required for live Box preview | `CLM_Box_Config__c` has `Box_User_Id__c` (or `Enterprise_Id__c`), and `Allowed_Folder_Ids__c` restricts the endpoint to the demo workspace |
| MT-040 | Switch to per-user Box OAuth for production | Box/Salesforce admins | Optional; production hardening | The `CLM_Box` auth provider holds real consumer credentials, the Box app carries its callback URL, and the external credential uses a per-user principal |
| MT-041 | Enable Salesforce Multi-Framework in the target org | Salesforce admin | Required before any UI Bundle deploy | **Setup → React Development with Salesforce Multi-Framework** is on, and `UIBundle` appears in the org's metadata types |
| MT-042 | Grant the Experience Cloud site user access to the token endpoint | Salesforce admin | Required for live Box preview from a site | `CLM_Contract_External` is assigned to the site's guest user (or community profile), including read on `UserExternalCredential` |
| MT-043 | Deploy the `CLM_Box_App` trusted site so previews can frame | Salesforce admin | Required for in-app document preview | **Setup → Trusted URLs** lists `https://*.app.box.com` with frame-src active; selecting a file in the workspace renders the document instead of an empty frame |
| MT-044 | Confirm the Box for Salesforce package can provision contract folders | Box + Salesforce admins | Required for live Box content | The workspace asks the package for a record's folder and provisions one when it has none, so no seeding is needed. Confirm the object root folder and the service account's rights allow `createFolderForRecordId` to succeed; a failure surfaces as `box_folder_not_provisioned` |
| MT-045 | Decide whether site visitors may read contract records, and create a guest user sharing rule if so | Demo owner + Salesforce admin | Required for the live contract dashboard | `CLM_Contract__c` is Private/Private, so the guest user sees no records and the dashboard shows its synthetic fixture. A guest user sharing rule makes real contracts readable by **unauthenticated** visitors — approve that exposure before creating it |
| MT-046 | Publish Contract Copilot as a service agent and record its agent id | Salesforce admin | Required for live Agentforce | `sf agent publish authoring-bundle --api-name CLM_Contract_Copilot` creates a **service** agent. In an org where a mis-typed agent already exists, delete it in Agent Builder first — the Metadata API refuses with "setup object in use" |
| MT-047 | Create a Lightning Out 2.0 app for the site and record its 18-digit id | Salesforce admin | Required for live Agentforce | Without a `LightningOutApp` record the conversation panel mounts empty, because the client loads through Lightning Out. Scriptable via the **Tooling API** — see `docs/operator/box-preview-setup.md` — or **Setup → Lightning Out 2.0 App Manager**. `IsEnabled` must be true, and the site origin must be added as a `LightningOutAppHost`. Supply the id as `VITE_AGENTFORCE_APP_ID` at build, or `agentforceAppId` in runtime config |
| MT-048 | Give the workspace an authenticated Salesforce user | Demo owner + Salesforce admin | Required for live data | The GraphQL UI API and the conversation client both return 401 for the Experience Cloud guest user |
| MT-075 | Complete Box Sign setup in the Box for Salesforce package | Salesforce admin | Required for live Box Sign | The package's Box Sign setup schedules the job that refreshes `box__BoxSign__c` from Box. Skip it and rows are written once and never updated: the contract's related list sits at `converting` for a request Box already reports as `sent`. Confirm with `SELECT CronJobDetail.Name, State FROM CronTrigger` returning a Box Sign refresh job in `WAITING`. If setup leaves none, schedule `box.UpdateSignRecordsSchedulable` directly -- Salesforce rejects a minute list in one cron expression, so quarter-hourly is four jobs |

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

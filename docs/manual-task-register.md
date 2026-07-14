# CLM Demo Manual-Task Register

This register contains every known task that requires a human decision, browser/admin UI, credentialed deployment, confirmation, or per-demo operation. Automated repository checks are included in the setup guide, not duplicated here.

Status values:

- **Complete** — verified in the current `kadams.ent.box.com` demo.
- **Required** — must be completed for the integrated demo.
- **Confirmation required** — prepare the action, then obtain explicit approval immediately before the final click.
- **Per run** — repeat for every integrated smoke test or presentation.
- **Optional** — not required for the core presenter flow.

## A. Environment and authority

| ID | Manual task | Owner | Status | Evidence / completion condition |
|---|---|---|---|---|
| MT-001 | Confirm work is scoped to `box-bedrock-for-clm`; do not touch DAM | Demo owner/operator | Per run | Current working directory matches this repository |
| MT-002 | Confirm Box hostname is `kadams.ent.box.com` and enterprise is `5105484` | Box operator | Per run | Account menu and workspace URL match |
| MT-003 | Confirm the target Salesforce org and whether it is safe for test records | Salesforce admin | Required | `sf org display` output reviewed |
| MT-004 | Confirm licenses/features for Apps, Forms, Automate, AI/Extract, Hubs, DocGen, Sign, Agentforce, and UI Bundles | Box and Salesforce admins | Required | Each named product surface opens for the operator |
| MT-005 | Establish who may approve workflow activation, publishing/sharing, DocGen generation, and Box Sign submission | Demo owner | Required | Named approver recorded in the handoff |
| MT-006 | Store Box, Salesforce, and connector secrets outside the repository | Security/admin | Required | Protected configuration exists; repository contains no secret |

## B. Box foundation

| ID | Manual task | Owner | Status | Evidence / completion condition |
|---|---|---|---|---|
| MT-010 | Create/verify `CLM-2026-Northstar` and its workstream folders | Box admin | Complete | Folder IDs match `config/box/live-box-surface.json` |
| MT-011 | Create/verify `clmContract`, `clmDocument`, `clmObligation`, and `clmClause` templates | Box metadata admin | Complete | Four live template IDs match the manifest |
| MT-012 | Create `clmRedlineReview` from `config/box/metadata-templates.json` | Box metadata admin | Required | New template ID recorded after creation |
| MT-013 | Upload/verify the Northstar package, clause playbook, records, and clause Markdown files | Box content owner | Complete | File IDs match the manifest |
| MT-014 | Apply and verify contract, document, obligation, and clause metadata | Box content owner | Complete | App tables and file metadata show expected values |
| MT-015 | Create/verify the three seeded review tasks | Legal Operations | Complete | Tasks `42899891150`, `42899881417`, `42899893550` remain human-owned |
| MT-016 | Build/verify the **New Contract Request** Form and destination folder | Box Forms builder | Complete | Published Form opens and targets folder `399082115646` |
| MT-017 | Build/verify the **Contract Lifecycle Management** App | Box Apps builder | Complete | Published Home shows charts plus one Form, Hub, and executed-agreement actions; Clause Library shows its view, folder, Hub shortcut, and three charts |
| MT-018 | Publish or republish the App/Form after changes | Box Apps/Forms owner | Confirmation required | Owner confirms immediately before publish; URLs are recorded afterward |
| MT-019 | Maintain the approved clause folders, README, ownership, review cadence, and Hub composition | Clause-library owner | Complete / ongoing | Hub `1312630996` shows eight clauses, current-standard status, three operational cards, and governance content |
| MT-020 | Publish new or revised approved clauses to the Hub | Clause-library owner | Confirmation required | Legal approval exists and final publish click is confirmed |
| MT-021 | Verify the three DocGen templates are marked as templates | Box DocGen admin | Complete | IDs `2344242775119`, `2344233767713`, `2344244747613` open in the catalog |
| MT-022 | Generate an approval memo, order summary, or renewal notice | Authorized reviewer | Confirmation required | User confirms immediately before DocGen creates the file |
| MT-023 | Create and send a Box Sign request | Authorized signatory coordinator | Confirmation required | All approvals are complete and the owner confirms immediately before send |
| MT-024 | Change sharing or add external collaborators | Box content owner | Confirmation required | Exact people, files/folders, and access level are confirmed before change |

## C. Salesforce application and integration

| ID | Manual task | Owner | Status | Evidence / completion condition |
|---|---|---|---|---|
| MT-030 | Choose the Salesforce CLM object API name and field mapping | Salesforce admin + CLM owner | Complete locally | `CLM_Contract__c` and `config/salesforce/clm-contract-record.json` contain no schema placeholder |
| MT-031 | Choose the record owner, sharing model, external ID, and Box folder-reference fields | Salesforce admin | Complete locally | Private sharing, standard `OwnerId`, unique `Contract_ID__c`, business-owner fallback, and Box references are specified |
| MT-032 | Configure Salesforce standard REST external-ID upsert and lookup in the Box HTTPS Connector | Box/Salesforce integration admin | Salesforce REST verified; Box OAuth test remains | External-ID `PATCH` created and then updated record `a7IgL000000WYWPUA4`; follow-up `GET` returned the same record, count remained one, and `agentforce` reports `DataStorageMB remaining = 1` |
| MT-033 | Implement `routeRedlineFindings` with schema validation and task idempotency | Salesforce developer | Required | Tests cover success, duplicate, triage, authorization, and Box failure |
| MT-034 | Implement the same-origin downscoped Box-token endpoint | Salesforce + Box developers | Required | Authorized folder succeeds; arbitrary/unauthorized folder fails |
| MT-035 | Implement approval-ready and executed-agreement event endpoints | Salesforce developer | Required for full lifecycle | Allowlisted payload tests pass |
| MT-036 | Retrieve the `Box_Automate_CLM` consumer secret and store it in the Box-managed OAuth connection | Salesforce/Box admins | Required | Salesforce metadata is complete: ECA `0xIgL000000Ok89UAC`, policy `0yOgL000000coILUAY`, user `005gL00000KmN8TQAV`, and assignment `0PagL00000b40CHSAY`; copy the secret directly from Salesforce Setup into Box without putting it in chat, source, screenshots, or shell history |
| MT-037 | Authenticate the Salesforce CLI and verify the target org | Salesforce operator | Required / per deploy | Alias and org ID reviewed before deployment |
| MT-038 | Deploy `CLM_Contract__c`, its layout, tab, and `CLM_Demo_Operator`; assign the permission set | Salesforce operator | Required | Object is private, fields/layout exist, and the intended operator has access |
| MT-039 | Deploy `clmreactapp` | Salesforce operator | Required | UI Bundle deployment succeeds in the intended org |
| MT-040 | Add the UI Bundle to the intended Lightning or Experience page | Salesforce admin | Required | Authorized user can open the deployed workspace |
| MT-041 | Confirm the page passes `recordId`, `contractId`, and `folderId` | Salesforce developer | Required | React banner and Box workspace resolve returned values |
| MT-042 | Allowlist the deployed Salesforce/Experience origin in the Box application CORS settings | Box app admin | Required | Live Box Explorer loads from the Salesforce page |

## D. Agentforce

| ID | Manual task | Owner | Status | Evidence / completion condition |
|---|---|---|---|---|
| MT-050 | Create/select the **Contract Copilot** Agentforce agent | Agentforce admin | Required | Agent exists in the target org |
| MT-051 | Create topics and register actions from the Agentforce spec | Agentforce admin/developer | Required | All specified actions are available |
| MT-052 | Apply source-citation, human-approval, expert-directory, DocGen, and Sign guardrails | Agentforce admin | Required | Negative tests cannot approve, complete tasks, or sign |
| MT-053 | Configure the agent and application IDs for React | Salesforce developer | Required | Live conversation replaces prompt-card fallback |
| MT-054 | Validate multi-file redline comparison against the finding schema | Agentforce developer + Legal Ops | Required | Results include citations, risk, domain, confidence, and approved position |
| MT-055 | Validate `get_redline_review_queue` is read-only | Agentforce developer | Required | Action returns assignments without mutation |
| MT-056 | Review and accept any prompt/agent changes that can affect legal routing | Legal Operations | Confirmation required | Change owner approves before production-like use |

## E. Expert directory and redline routing

| ID | Manual task | Owner | Status | Evidence / completion condition |
|---|---|---|---|---|
| MT-060 | Select real experts or managed groups for active domains | Legal Operations | Required | Commercial Legal, Finance, Privacy, and any active domains have owners |
| MT-061 | Replace applicable `null` `boxLogin` values in `config/clm/expert-routing.json` | Demo maintainer | Required | Active routes contain verified Box identities |
| MT-062 | Add each expert/group as a collaborator with least privilege | Box content owner | Required | Access test succeeds for each active route |
| MT-063 | Verify the `0.85` confidence threshold and allowed domains | Legal Operations | Required | Threshold/domain decision documented |
| MT-064 | Verify unclassified, low-confidence, missing-expert, and inaccessible cases route to `kadams@boxdemo.com` triage | Legal Operations | Required | Four negative tests create/reuse triage work |
| MT-065 | Verify repeated findings reuse one task per contract, file, and domain | Salesforce/Box developer | Required | Second request returns existing task ID |
| MT-066 | Reassign the current seeded tasks from demo triage to real experts | Legal Operations | Confirmation required | Exact tasks and assignees confirmed before reassignment |

## F. Box Automate and HTTPS connectors

| ID | Manual task | Owner | Status | Evidence / completion condition |
|---|---|---|---|---|
| MT-070 | Update and verify **CLM - Contract Intake Enrichment** against the standard REST specification | Box Automate builder | Required update to saved draft | Workflow `399436615012` uses OAuth 2.0 external-ID upsert and lookup and remains inactive |
| MT-071 | Build **CLM - Redline Domain Review Routing** | Box Automate builder | Required | Inactive workflow matches the spec and folder `399080778184` |
| MT-072 | Build **CLM - Approval Packet Readiness** | Box Automate builder | Optional / full lifecycle | Inactive workflow matches task and DocGen gates |
| MT-073 | Build **CLM - Executed Agreement Obligations** | Box Automate builder | Optional / full lifecycle | Inactive workflow matches Sign, Extract, review, and reminder gates |
| MT-074 | Test the Box-managed OAuth 2.0 connection and bind the saved workflow to standard REST `PATCH` + `GET` | Box/Salesforce admins | Blocked on CLM-specific consumer secret | The inactive `PATCH` request is saved on connector `Agentforce Dev`, but 2026-07-14 tests failed before Salesforce login because the UI-visible legacy `Box Automate` secret does not match `Box_Automate_CLM`. Retrieve or rotate the secret for consumer key `3MVG9dAEux2v1sLvqwMv.uh.fDj5.dT8YnFSByxksfuDj98cOZNQ_wZR2AVRszo9bAJ0cpGPaJu4xAJyBmoUL`, update Box, rerun `PATCH` twice, then add and test the `GET` lookup. |
| MT-075 | Validate connector payload allowlist and prohibited fields | Security + integration owner | Required | Test proves file bytes, tokens, signer details, and unreviewed output are rejected |
| MT-076 | Review trigger scope, test plan, rollback, and idempotency for each workflow | Workflow owner | Required before activation | Review evidence recorded |
| MT-077 | Activate any Box Automate workflow | Demo owner + Box Automate admin | Confirmation required | Explicit approval obtained immediately before the final activation click |
| MT-078 | Disable a workflow after testing or when unexpected behavior occurs | Box Automate admin | Per run / incident | Workflow is inactive and run IDs are recorded |

## G. Integrated smoke test

Latest verified run: 2026-07-14. The published Form created Box intake file `2346653850589` in folder `399082115646`. The Salesforce lookup returned zero matching `CLM_Contract__c` records, confirming the current boundary at the inactive Automate workflow.

| ID | Manual task | Owner | Status | Evidence / completion condition |
|---|---|---|---|---|
| MT-080 | Submit a labeled non-production New Contract Request | Demo operator | Per run | File appears in folder `399082115646` |
| MT-081 | Review Extract and AI Agent output for unsupported values | Human validator | Per run | Corrections or acceptance recorded |
| MT-082 | Approve or reject the intake validation task | Human validator | Per run | Decision history exists in Box |
| MT-083 | Verify one Salesforce record is created and retry is idempotent | Salesforce operator | Per run | Record ID is stable across retry |
| MT-084 | Launch React with returned context | Demo operator | Per run | Salesforce ID and Box folder appear in React |
| MT-085 | Verify live Box Explorer and downscoped access | Demo operator | Per run | Authorized folder loads; unrelated folder is not accessible |
| MT-086 | Ask Agentforce for a cited package summary | Demo operator | Per run | Material claims cite live Box files |
| MT-087 | Run redline comparison and inspect every structured finding | Legal Operations | Per run | Required finding fields and citations are present |
| MT-088 | Verify task grouping, expert assignment, and triage behavior | Legal Operations | Per run | One task per domain; exceptions use triage |
| MT-089 | Verify React **Redline reviews** matches Box task state | Demo operator | Per run | Expert, task ID, risk, confidence, and status agree |
| MT-090 | Confirm signature is blocked while reviews are incomplete | Legal Operations | Per run | No premature Sign action is available |
| MT-091 | Confirm before generating the approval memo | Authorized reviewer | Confirmation required | DocGen creates one file only after confirmation |
| MT-092 | Confirm before sending a Box Sign request | Demo owner/signatory coordinator | Confirmation required | Final send occurs only after completed approvals |
| MT-093 | Validate extracted obligations, owners, dates, and reminders | Contract owner | Per full-lifecycle run | Human-reviewed obligation records exist |

## H. Presenter preparation and reset

| ID | Manual task | Owner | Status | Evidence / completion condition |
|---|---|---|---|---|
| MT-100 | Choose and rehearse the executive, Legal Operations, or technical script | Presenter | Per presentation | Selected script completes within its time box |
| MT-101 | Pre-open Box workspace, App, Hub, Salesforce record, and React page | Presenter | Per presentation | All surfaces load under the correct accounts |
| MT-102 | Confirm task states support the intended **Signature blocked** story | Legal Operations | Per presentation | Required tasks are incomplete at demo start |
| MT-103 | Confirm named experts are available or disclose use of demo triage | Presenter | Per presentation | Routing story matches live state |
| MT-104 | Capture new screenshots only from the real demo surfaces and page viewport | Demo maintainer | After material UI change | Screenshot shows the actual Box or React demo, not documentation, browser tabs, the address bar, or unrelated desktop content |
| MT-105 | Rebuild and inspect the self-contained gallery after screenshot changes | Demo maintainer | After screenshot change | `output/html/clm-experience-gallery.html` opens offline |
| MT-106 | Record test files, records, tasks, workflow runs, and generated outputs | Demo operator | Per run | Run log supports cleanup and audit |
| MT-107 | Disable temporary workflows and restore intended task states | Box/Salesforce operators | Per run | Next rehearsal begins from the documented state |
| MT-108 | Delete records/files/tasks or remove collaborators | Content/system owner | Confirmation required | Exact objects and downstream impact confirmed before deletion |
| MT-109 | Update the live manifest and handoff after verified live changes | Demo maintainer | After live change | IDs, URLs, statuses, and blockers match the live systems |

## Remaining blockers for Level C

At the time this register was written:

1. `CLM_Contract__c` and the integration permission set are deployed to `agentforce`; the layout, tab, `CLM_Demo_Operator`, and React UI Bundle remain undeployed.
2. Standard REST create/update/lookup is verified directly against Salesforce, and the External Client App Run As policy is deployed. Retrieve the ECA consumer secret, configure the Box OAuth connection, and test through Box Automate. The redline-routing, event, and downscoped-token Apex endpoints are not implemented.
3. Agentforce agent/application IDs and registered live actions are not available.
4. The Salesforce/Experience origin is not set in the Box CORS or connector configuration.
5. Named expert Box logins remain unset; current live tasks use `kadams@boxdemo.com` demo triage.
6. `clmRedlineReview` is specified but not created live.
7. Redline routing and downstream lifecycle workflows are not built/activated live.
8. The saved intake workflow remains inactive and must be updated from the prior connector selection to the standard REST upsert/lookup steps before validation and explicit activation confirmation.

## Completion-log template

```text
Run date/time:
Operator:
Demo owner / confirmation authority:
Box hostname and enterprise:
Salesforce alias, org ID, and origin:
Readiness level attempted: A / B / C
Manual-task IDs completed:
Manual-task IDs skipped and reason:
Confirmation-gated actions approved:
Salesforce record ID:
Box Form submission / workflow run ID:
Created or reused Box task IDs:
DocGen output IDs:
Box Sign request ID, if separately approved:
Corrections made during human validation:
Cleanup/reset performed:
Remaining blockers:
```

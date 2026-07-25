# CLM Box Surface and Automate Takeover Handoff

**Updated:** 2026-07-22  
**Active package:** `/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm`  
**Target Box host:** `kadams.ent.box.com`

## Objective

Bring the tracked CLM package into alignment with the reorganized live Box App and the latest Box Automate workflows. The highest-priority work is to inspect the two live Automate drafts, capture the tested HTTPS outcome schema, and update the first packaged workflow with the exact Box merge variables used by the Salesforce record-creation POST body.

Do not infer the private API graph or merge-token syntax. Read it from the authenticated Box Automate page and its in-page GraphQL requests.

## Start here

Read these files before making changes:

| Purpose | File |
|---|---|
| Repository rules | `AGENTS.md` |
| Scenario presenter source | `docs/operator/scenarios/box-automate-agentic-orchestration/README.md` |
| Automate workflow source of truth | `config/box/automate-workflows.json` |
| HTTPS connector contract | `config/box/https-connectors.json` |
| `clmContract` metadata template source of truth | `config/box/metadata-templates.bcl` |
| Box App portable layout | `config/box/box-app-blueprint.md` |
| Box private API operator notes | `docs/box-private-api-labs.md` in the box-capture repository |
| Box private API research index | `docs/research/box-web-private-api/README.md` |
| Guarded Automate executor | `box-capture/automate.py` |

## Live Box targets

| Surface | URL | Required work |
|---|---|---|
| Primary Contract Intake workflow | `https://kadams.ent.box.com/automate/workflow/edit/399436615012` | Review the user's reorganized graph, shortened names, trigger, step order, edges, and variable bindings. Update the first packaged workflow to match. |
| HTTPS outcome test workflow | `https://kadams.ent.box.com/automate/workflow/edit/402235479966` | Inspect the configured HTTPS Connector outcome and capture its request/response and GraphQL workflow representation. |
| CLM Box App | `https://kadams.ent.box.com/app/tyC9bQaEzWXFGg8AT#p=sngzAsJ7yoTdzonKe` | Review the Home and Clause Library layouts, reordered content, shortened names, actions, charts, filters, and links. Reconcile the portable App blueprint. |

## Browser requirement

This task could not inspect the authenticated pages because the Browser and Chrome plugins were recognized but no callable browser controller was injected. Before doing any live work, confirm the new task has an authenticated Chrome controller, such as the browser-client `mcp__node_repl__js` runtime.

If the controller is absent, stop and request screenshots or a browser-enabled task. Do not claim the live surfaces were reviewed.

Use the authenticated page's existing Apollo client for Automate GraphQL inspection. Do not export or persist cookies, access tokens, anti-forgery values, or browser credentials.

## Current package state

### Contract Intake workflow

`config/box/automate-workflows.json` currently defines **CLM - Contract Intake Enrichment** as:

| Order | Step |
|---:|---|
| Trigger | `clmContract` metadata applied to a file in generated `01 - Intake` |
| 1 | Extract Agent: Contract Intake Extract |
| 2 | Box Agent: CLM Contract Risk Triage |
| 3 | Approval Task: validate extracted terms and approval brief |
| 4 | Conditional Split on approval outcome |
| 5 | HTTPS Request: `salesforceContractUpsert` |
| 6 | HTTPS Request: `salesforceContractLookup` |

The live workflow may now differ. Treat workflow `399436615012` as the live reference and the tracked JSON as stale until compared.

### Connector mismatch requiring resolution

`config/box/https-connectors.json` currently defines `salesforceContractUpsert` as:

- Method: `PATCH`
- Endpoint: `/services/data/v67.0/sobjects/CLM_Contract__c/Contract_ID__c/{urlEncodedContractId}`
- Behavior: external-ID upsert followed by a lookup

The latest user requirement explicitly asks for the tested HTTPS **POST** request that creates a Salesforce record. Inspect workflow `402235479966` and reconcile this difference deliberately. Do not silently retain the old `PATCH` contract or guess that the test uses the same endpoint.

The POST payload must use Box Automate merge variables, not literal placeholder names. Capture the exact expression syntax used by the editor for each value.

### Intended Salesforce payload fields

The current connector contract contains these fields. Keep only fields supported by the verified workflow inputs and current Salesforce schema:

| Salesforce field | Intended source |
|---|---|
| `Name` | Counterparty plus contract type |
| `Requester_Name__c` | Metadata requester name |
| `Requester_Email__c` | Metadata `requesterEmail` |
| `Counterparty__c` | Metadata `counterparty` or Extract counterparty |
| `Contract_Type__c` | Metadata `contractType` or Extract contract type |
| `Deal_Value__c` | Metadata or Extract deal value |
| `Term_Months__c` | Metadata or Extract term |
| `Region__c` | Metadata region |
| `Data_Category__c` | Metadata or Extract data category |
| `Target_Signature_Date__c` | Metadata target signature date |
| `Business_Owner_Name__c` | Metadata business owner |
| `Risk_Level__c` | Box Agent risk level |
| `Special_Terms_Risk_Notes__c` | Metadata notes or reviewed agent summary |
| `Record_Source__c` | Literal `Box Automate` |
| `Counterparty_Account__c` | Resolved counterparty Account |
| `Opportunity__c` | Resolved opportunity |

The `clmContract` metadata template supplies the required inputs (`contractId`, `contractType`, `counterparty`, `requesterEmail`). Any optional value must be safe when blank or must be sourced from the Extract or Box Agent outcome before the HTTPS step.

## Recent local changes

### Metadata trigger replaces the Form

The Box Form ("New Contract Request") has been removed entirely. Intake now fires from a `clmContract` metadata trigger: the workflow starts when `clmContract` metadata is applied to a file uploaded into generated `01 - Intake`. The trigger yields `static.trigger.fileId` and `static.trigger.metadata.<key>`.

`config/box/metadata-templates.bcl` defines the `clmContract` template. `requesterEmail` was added so the Salesforce-required `Requester_Email__c` can be sourced from metadata alongside `contractId`, `contractType`, and `counterparty`.

The live Box Automate workflow must be rebound from the removed form-trigger tokens to the metadata-trigger tokens before it can run. This metadata-triggered variant is designed but has not been re-verified live.

### Realistic MSA fixture

A new seven-page realistic agreement was added without replacing v3:

- Generated artifact: `output/pdf/northstar-msa-redline-v4.pdf`
- Generator: `scripts/generate_sample_contract_assets.py`
- Generator function: `build_realistic_msa()`

The v4 agreement includes realistic commercial, privacy, security, IP, indemnity, liability, termination, and signature provisions plus negotiated Northstar redlines and an issue register. It was rendered and visually reviewed across all seven pages.

The `clmContract` metadata sample and presenter README still refer to `northstar-msa-redline-v3.pdf`. Switch them to v4 if the user confirms v4 should become the canonical intake sample.

## Existing private API evidence

The repository currently proves only an empty Automate draft and a Manual Start graph:

- `config/box/private-api-lab-automate-definition.json`
- `config/box/private-api-lab-automate-manual-start-definition.json`
- `docs/research/box-web-private-api/2026-07-20-automate-lab-request.redacted.json`
- `docs/research/box-web-private-api/2026-07-20-automate-manual-start-request.redacted.json`

Known Automate transport:

- Endpoint: `/app-api/graphql`
- Read operations observed: `GetCombinedWorkflows`, `LoadWorkflowAndEnsureCascadeRole`
- Write operations observed: `CreateItemV2`, `UpdateItemV2`
- Workflow graph fields observed: `trigger`, `outcomes`, `gateways`, and `edges`

No repository fixture currently contains the HTTPS Connector outcome graph. Add a new redacted, versioned fixture after inspecting workflow `402235479966`.

## Required execution order

1. Verify the active repository, Box hostname, logged-in Box operator, and enterprise before reading or changing live state.
2. Confirm both Automate workflows are inactive.
3. Read workflow `399436615012` and record its title, trigger, outcomes, gateways, edges, names, descriptions, variables, and IDs.
4. Read workflow `402235479966` and capture the HTTPS outcome configuration plus the GraphQL request/response shape.
5. Sanitize the capture. Preserve schema and non-secret identifiers needed for implementation; remove credentials and anti-forgery data.
6. Update `config/box/automate-workflows.json` to match the primary workflow's verified organization.
7. Update `config/box/https-connectors.json` with the verified POST endpoint, headers, merge-variable body, expected statuses, and response outputs.
8. Add a versioned HTTPS outcome fixture under `config/box/` and matching redacted evidence under `docs/research/box-web-private-api/`.
9. Extend `box-capture/automate.py` only after the graph shape is known. Preserve exact-title, inactive-status, and no-publish guards.
10. Inspect the live Box App Home and Clause Library, then update `config/box/box-app-blueprint.md` to match the revised layout and names.
11. Rebind the workflow trigger to the `clmContract` metadata template and decide whether v4 becomes the canonical presenter upload.
12. Run the repository's narrow configuration validation only after the package changes are complete.

## Safety boundaries

- Do not publish or activate an Automate workflow.
- Do not publish or republish the Box App without immediate owner confirmation.
- Do not delete, share, submit, or run live Box resources during schema capture.
- Do not export browser cookies, OAuth tokens, connector secrets, or anti-forgery values.
- Do not send contract bytes through the Salesforce HTTPS Connector.
- Do not treat unreviewed AI output as an approved Salesforce value.
- Keep target-environment IDs in runtime state or audit receipts, not portable template defaults.

## Acceptance criteria

- The primary packaged Automate workflow matches the verified organization of workflow `399436615012`.
- The HTTPS outcome fixture reproduces the verified structure from workflow `402235479966`.
- The Salesforce POST body contains valid Box Automate merge variables for all included dynamic values.
- Optional metadata values cannot break the POST when omitted.
- The response captures the Salesforce record ID when the tested outcome exposes it.
- The package does not store credentials or browser anti-forgery state.
- The App blueprint matches the live Home and Clause Library structure and shortened names.
- The presenter script names the exact MSA file used for intake.
- No workflow or App is published or activated without explicit confirmation.

## Outcome, 2026-07-22 into 2026-07-23

**The objective above was completed and the form-triggered scenario was proven end to end on 2026-07-22.** At that time a Form submission ran trigger, workspace copy, workspace rename, Box Agent, human approval, and an HTTPS POST that created a real Salesforce record. This section is history: the Box Form has since been removed, and intake is now designed to fire from a `clmContract` metadata trigger on the `01 - Intake` folder. That metadata-triggered variant has not been re-verified live and must be re-tested before activation.

Config now lives in `.bcl`, not `.json`. BCL is the only supported import format; the paths in the table above should be read with a `.bcl` extension.

### Capture method that worked

The Automate editor holds the server-provided workflow definition in client application state once the page finishes loading. That is the definition before any local edit, and it is more reliable than reading the rendered editor. GraphQL request and response bodies stayed unreadable throughout, so this is the practical read path. `box-capture/automate.py --write-inspector` packages it.

### Live workflow, as reconciled

Order is trigger, copy workspace folder, rename workspace folder, Box Agent, approval task, exclusive split, connector call on the Approved branch. There is no Extract Agent and no Salesforce lookup step. The Rejected branch has no outcome, so a rejected submission is silently dropped.

### Three failures, three distinct causes

Each one is worth keeping, because none was visible from Box's error reporting.

1. **Unresolved variables become the literal string `Variable unavailable`.** Not empty, not null. `Deal_Value__c` (Currency) and `Term_Months__c` (Number) received that text and Salesforce could not parse it. The same substitution produced a folder named `CLM-2026-Variable unavailable`. Reconstructing the body with empty strings had "proved" blank-safety, but Box never emits empty, so the test measured the wrong thing. **Rule: only bind values whose Form field is mandatory.**
2. **The Form and the Salesforce schema disagreed on what is mandatory.** `CLM_Contract__c` requires `Contract_ID__c`, `Contract_Type__c`, `Counterparty__c`, `Requester_Email__c`. Three had been made optional on the Form. `Contract_Type__c` is a restricted picklist, so the substituted text could not satisfy it either. The Form now requires five fields.
3. **The connector pointed at the wrong Salesforce org.** Two similarly named connectors existed; only one org holds `CLM_Contract__c`. A valid payload sent to the other org fails as a bare `UNKNOWN_ERROR`. Switching the connector also normalised the endpoint to the leading-slash-free form.

### Diagnosing connector faults on this surface

Box never exposes the Salesforce error body. The run event carries `errorCode: UNKNOWN_ERROR` with an empty payload, Run Test says only "Something went wrong", and the underlying `/app-api/graphql` call returns HTTP 200 because the failure is inside Box's server-side connector call. The method that worked:

1. Read the fully resolved request body from the `CALL_CONNECTOR` run event.
2. Validate it field by field against the object metadata in `clm-salesforce-project`.
3. Confirm the connector's base URL is the org that actually holds the object.
4. If all three pass, replay the request from Workbench or curl, which returns the real error.

### Verified result

The created record carried all ten mapped fields correctly, confirmed on the Salesforce record itself rather than only from Box: contract name, contract ID, counterparty, contract type, requester email, intake file ID, workspace folder ID, record source, routing status, task count. `Deal Value`, `Term Months`, `Target Signature Date` and `Risk Level` are intentionally absent, because their Form fields are optional and would have carried `Variable unavailable` into typed Salesforce fields.

### Editing cautions learned the hard way

- **The workflow is Active.** Any further edit saves as a draft and does nothing until Activate is pressed again. The editor showing your change is not evidence that it runs. Confirm `lastPublishedAt` moved, or check the Status column on the Automate list.
- **The endpoint control is a segmented editor, not a text input.** Text typed after a `/` is held as a pending variable lookup and is silently dropped from the model while still displayed. `Escape`, blur and `Enter` all discard it; a following `/` commits a segment. Select-all does not clear committed segments, so retyping appends. The reliable edit is cursor-to-end and delete backwards. Verify the model, not the rendered text.
- **In the body editor, search variables by form element ID, not by label.** Several labels, `Counterparty` among them, match both a Form field and a metadata attribute, and picking the wrong one binds silently.
- **A date variable has no `YYYY-MM-DD` preset.** Only a full ISO datetime or single components, which persist as a distinct `DATE_FORMAT` operand. A Salesforce Date field needs three of them joined by literal hyphens.

## Repository boundary

This repository is a **golden copy** of the finished CLM scenario. Anything needed to *create* that copy lives elsewhere.

The Box surface authoring tooling has already moved to `unofficialbox/box-capture`: the guarded Forms, Apps and Automate executors, the Automate graph inspector, the `CLM Surface API Lab - *` specifications, and the lab operator guide. Nothing here depends on it at runtime. Reach for it when rebuilding a Box surface in a new environment or capturing a live workflow definition, not when running or presenting the demo.

Live environment values did not move. `config/runtime/*` stays here and is passed to that tooling per run with `--config`, `--bootstrap`, and `--form-runtime`. No live identifier crosses the boundary in either direction.

`scripts/` has **not** been sorted against this rule yet, and a cleanup is planned. See `scripts/README.md` for the current classification, the four scripts still holding stale `.json` config paths, and the three candidate resolutions. Treat its present layout as unsorted rather than decided.

## Still open

1. **Duplicate safety.** A plain POST to the sobject collection creates a new record every submission. The `PATCH` upsert it replaced was idempotent against a `Contract_ID__c` external ID.
2. **The created record ID is not captured.** The outcome defines no output variable; `$.id` is available.
3. **The presenter script is wrong at step 5.** `docs/operator/scenarios/box-automate-agentic-orchestration/README.md` still says "upsert and lookup" and "the external ID prevents duplicates". Neither is true.
4. **Rejected branch is terminal**, with no notification or return-for-correction.
5. **No Extract Agent** in the live workflow, though the packaged design once specified one.
6. **v3 versus v4 MSA** as the canonical intake sample is still undecided.
7. **Repository Python tooling still expects `.json` config paths** after the BCL cutover, so `validate_clm.py` and several tests error. Tooling migration is owned by the box-dispatch effort.

## Immediate next action

Fix step 5 of the presenter script so it matches the live behaviour, then decide the duplicate-safety question before the scenario is presented.

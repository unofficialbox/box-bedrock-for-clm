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
| Box Form source of truth | `config/box/form-definition.json` |
| Box App portable layout | `config/box/box-app-blueprint.md` |
| Box private API operator notes | `docs/operator/box-private-api-labs.md` |
| Box private API research index | `docs/research/box-web-private-api/README.md` |
| Guarded Automate executor | `scripts/experimental_box_automate_private_api.py` |

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
| Trigger | Box Forms submission from **New Contract Request** |
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
| `Requester_Name__c` | Form requester name |
| `Requester_Email__c` | Form requester email |
| `Counterparty__c` | Form or Extract counterparty |
| `Contract_Type__c` | Form or Extract contract type |
| `Deal_Value__c` | Form deal value |
| `Term_Months__c` | Form or Extract term |
| `Region__c` | Form region |
| `Data_Category__c` | Form or Extract data category |
| `Target_Signature_Date__c` | Form target signature date |
| `Business_Owner_Name__c` | Form business owner |
| `Risk_Level__c` | Box Agent risk level |
| `Special_Terms_Risk_Notes__c` | Form notes or reviewed agent summary |
| `Box_Workspace_Folder_ID__c` | Resolved Box workspace folder ID |
| `Box_Workspace_URL__c` | Resolved Box workspace URL |
| `Box_Intake_File_ID__c` | Submitted Form file ID |
| `Box_Redline_File_ID__c` | Submitted Form file ID |
| `Intake_Workflow_Run_ID__c` | Current Automate workflow run ID |
| `Record_Source__c` | Literal `Box Form` |
| `Latest_Routing_Status__c` | Initial routing status |
| `Open_Review_Task_Count__c` | Initial task count |
| `Last_Box_Sync__c` | Current workflow timestamp |

The new Form has only two required inputs. Any optional value must be safe when blank or must be sourced from the Extract or Box Agent outcome before the HTTPS step.

## Recent local changes

### Form simplification

`config/box/form-definition.json` now requires only:

- `requesterEmail`
- `contractPackage`

All other Form fields remain available but optional. The live Box Form still needs reconciliation before its required states change.

`config/box/automate-workflows.json` still lists all Form variables under `requiredFormVariables`. This is inconsistent with the new Form definition and must be corrected after reviewing the live primary workflow.

### Realistic MSA fixture

A new seven-page realistic agreement was added without replacing v3:

- Generated artifact: `output/pdf/northstar-msa-redline-v4.pdf`
- Generator: `scripts/generate_sample_contract_assets.py`
- Generator function: `build_realistic_msa()`

The v4 agreement includes realistic commercial, privacy, security, IP, indemnity, liability, termination, and signature provisions plus negotiated Northstar redlines and an issue register. It was rendered and visually reviewed across all seven pages.

The Form definition and presenter README still refer to `northstar-msa-redline-v3.pdf`. Switch them to v4 if the user confirms v4 should become the canonical intake sample.

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
9. Extend `scripts/experimental_box_automate_private_api.py` only after the graph shape is known. Preserve exact-title, inactive-status, and no-publish guards.
10. Inspect the live Box App Home and Clause Library, then update `config/box/box-app-blueprint.md` to match the revised layout and names.
11. Reconcile the Form's two required fields and decide whether v4 becomes the canonical presenter upload.
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
- Optional Form values cannot break the POST when omitted.
- The response captures the Salesforce record ID when the tested outcome exposes it.
- The package does not store credentials or browser anti-forgery state.
- The App blueprint matches the live Home and Clause Library structure and shortened names.
- The presenter script names the exact MSA file used for intake.
- No workflow or App is published or activated without explicit confirmation.

## Immediate next action

Start a browser-enabled task, open workflow `399436615012` read-only, and compare its graph with `config/box/automate-workflows.json`. Then use workflow `402235479966` to capture the HTTPS outcome and merge-variable payload before editing either JSON source of truth.

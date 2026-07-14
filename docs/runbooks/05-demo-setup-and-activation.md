# CLM Demo Setup and Activation

This is the operator guide for bringing up the **Box + Agentforce + Salesforce Multi-Framework React** CLM demo. Use it with the [manual-task register](../manual-task-register.md), which records every browser, administrator, deployment, approval, and per-run human task.

## 1. Choose the target readiness level

| Level | Result | Current state |
|---|---|---|
| A. Local rehearsal | React workspace, Box-safe fallback, redline review queues, and Agentforce prompt cards | Ready |
| B. Live Box rehearsal | Level A plus the live Box workspace, App, Form, Hub, clauses, tasks, and DocGen templates | Ready; Automate remains inactive |
| C. Integrated demo | Validated Form intake creates a Salesforce record; React receives live record context; Agentforce runs registered actions; redlines route to real Box collaborators | Not ready; complete sections 6–9 |

Do not present Level C as live until the final smoke test in section 10 passes.

## 2. Fixed scope and live anchors

Run commands from:

```text
/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm
```

Use only the `kadams.ent.box.com` enterprise for this demo.

| Surface | Live value |
|---|---|
| Box enterprise | `5105484` |
| Box login / demo triage | `kadams@boxdemo.com` |
| Workspace | [CLM-2026-Northstar](https://kadams.ent.box.com/folder/399081692991) |
| Box App | [Contract Lifecycle Management](https://kadams.ent.box.com/app/KyZohNNwCy6Y6ccmn) |
| Box Form | [New Contract Request](https://kadams.ent.box.com/f/c83f2ab35ee74a519b5fbc2859e2a858) |
| Approved clause Hub | [Acme Contract Clause Library](https://kadams.ent.box.com/hubs/1312630996) |
| Saved Automate workflow | [CLM - Contract Intake Enrichment](https://kadams.ent.box.com/automate/workflow/edit/399436615012) |
| Live-ID manifest | `config/box/live-box-surface.json` |

Stop if the browser shows another Box hostname or enterprise. Do not recreate CLM content in an ANZ or Agentforce Box tenant.

## 3. Prerequisites

### Accounts and product access

- Box account in enterprise `5105484` with access to Files, Apps, Forms, Automate, Hubs, AI/Extract, metadata, DocGen, Tasks, and Sign.
- Salesforce org with Agentforce, Apex/API access, and Salesforce Multi-Framework UI Bundle support.
- Permission to deploy metadata and add the UI Bundle to the intended Lightning or Experience surface.
- A Box Platform application or managed-package configuration capable of issuing short-lived downscoped tokens.
- Real Box users or managed groups for each expert domain that will be activated.

### Local tools

```bash
node --version       # 22 or newer
npm --version
python3 --version
sf --version
```

Install the Python package used by the schema-validation command:

```bash
python3 -m pip install jsonschema
```

Only when regenerating the sample PDFs or DocGen templates, also install `reportlab` and `python-docx`.

Install project dependencies:

```bash
cd /Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/clm-react-app/force-app/main/default/uiBundles/clmreactapp
npm install
cd /Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm
```

Do not commit Box tokens, Salesforce tokens, connector secrets, or client secrets. Put credentials in Salesforce protected configuration, Box admin configuration, or local ignored environment files.

## 4. Validate the repository and local demo

From the CLM root:

```bash
python3 -m py_compile update-box-web-urls.py
python3 -m json.tool config/box/live-box-surface.json >/dev/null

for f in config/clm/*.json config/box/*.json config/agentforce/*.json config/demo/*.json; do
  python3 -m json.tool "$f" >/dev/null || exit 1
done
```

Validate the redline schema:

```bash
python3 - <<'PY'
import json
from pathlib import Path
from jsonschema import Draft202012Validator

schema = json.loads(Path("config/clm/redline-finding.schema.json").read_text())
Draft202012Validator.check_schema(schema)
print("redline finding schema valid")
PY
```

Run the React gates:

```bash
cd clm-react-app/force-app/main/default/uiBundles/clmreactapp
npm test -- --run
npm run lint
npm run build -- --mode standalone
npm run test:e2e
```

Start the local demo:

```bash
npm run dev
```

Open the URL printed by Vite with the seeded context:

```text
?recordId=a01xx0000001234&contractId=CLM-2026-0017&folderId=399081692991
```

Expected local behavior:

- The Northstar contract banner renders.
- Workspace shows a safe file-list fallback when no downscoped token is available.
- **Redline reviews** shows four findings grouped into three expert domains.
- Agentforce shows prompt cards until live runtime IDs are configured.
- No control can approve a contract or bypass signature gating.

Level A is ready when all checks above pass.

## 5. Verify or recreate the Box foundation

The current `kadams.ent.box.com` foundation is already live. Verify it rather than rebuilding it.

### 5.1 Verify the workspace

Open folder `399081692991` and confirm these workstreams exist:

| Workstream | Folder ID |
|---|---|
| Intake | `399082115646` |
| Drafts and Redlines | `399080778184` |
| Review Packets | `399082148957` |
| Approvals | `399082072259` |
| Signature | `399081939679` |
| Executed Agreement | `399080706253` |
| Obligations | `399081567921` |
| DocGen Templates | `399363530207` |
| Clause Library | `399419341582` |

Confirm the sample contract package and IDs against `config/box/live-box-surface.json`.

### 5.2 Verify metadata

These templates are live:

| Template | ID |
|---|---|
| `clmContract` | `fe4e6fdb-659f-4931-9718-d03b624affdb` |
| `clmDocument` | `8a6cc4c2-8425-48fa-b4f0-01711b777d4a` |
| `clmObligation` | `964802ab-7da2-444e-9422-1b52fd4f5489` |
| `clmClause` | `9ca0de81-5f96-4158-82f7-1251b28a9c6e` |

Create `clmRedlineReview` manually before activating redline automation. Its fields are defined in `config/box/metadata-templates.json`. Record the returned template ID in `config/box/live-box-surface.json` only after the template exists.

### 5.3 Verify human review tasks

| Review | Task ID | Current assignee |
|---|---|---|
| Commercial Legal | `42899891150` | `kadams@boxdemo.com` |
| Finance | `42899881417` | `kadams@boxdemo.com` |
| Privacy/Security | `42899893550` | `kadams@boxdemo.com` |

These are demo-triage assignments. Do not claim named expert routing is live until section 8 is complete.

### 5.4 Verify App, Form, Hub, and DocGen

- Follow `box-web-ui-build-queue.md` if the Form or App must be recreated.
- Follow `config/box/box-app-builder-checklist.md` for the App blocks and filters.
- Follow `config/box/hub-blueprint.md` for clause-library composition and governance.
- Confirm the App Home page uses `Quick Actions & Portfolio`, with portfolio charts and exactly one intake Form block labeled `Start a New Contract`, plus `Approved Clause Hub` and `Executed Agreements` actions.
- Confirm the App Clause Library page shows the approved view, source folder, Hub shortcut, and clause-position, family, and approval-status charts.
- Confirm the Hub shows the governed clause source, the current-standard operations callout, and working links for intake, the CLM dashboard, and executed agreements.
- Confirm the DocGen template folder contains:
  - Approval memo: `2344242775119`
  - Order summary: `2344233767713`
  - Renewal notice: `2344244747613`
- If App or Form URLs change, run:

```bash
python3 update-box-web-urls.py \
  --app-url '<published-clm-app-url>' \
  --form-url '<published-clm-form-url>'
python3 -m json.tool config/box/live-box-surface.json >/dev/null
```

Publishing, sharing, workflow activation, and Box Sign submission are confirmation-gated manual actions.

Level B is ready when the live surfaces open, the files and tasks match the manifest, and local React verification still passes.

## 6. Prepare Salesforce

### 6.1 Authenticate and verify the org

```bash
sf org login web --alias <clm-org-alias> --set-default
sf org display --target-org <clm-org-alias>
```

Record the Salesforce origin and confirm the intended non-production org before deployment.

### 6.2 Decide the structured record contract

The repository contract is now explicit:

| Decision | Value |
|---|---|
| Object | `CLM_Contract__c` |
| Sharing | Private internal and external sharing |
| Record owner | Standard `OwnerId`; authenticated integration user unless an approved assignment rule changes it |
| Business owner | Optional `Business_Owner__c` User lookup plus required `Business_Owner_Name__c` fallback |
| External ID / idempotency | Required unique `Contract_ID__c`; intake uses upsert |
| Box references | Folder ID, folder URL, intake file ID, redline file ID, and workflow run ID |
| Intake integration | Standard REST external-ID `PATCH`, followed by external-ID `GET` |

Review `docs/salesforce-clm-record-contract.md` and `config/salesforce/clm-contract-record.json`, then deploy the metadata under `clm-react-app/force-app/main/default/objects/CLM_Contract__c/`. Do not substitute a managed-package object without intentionally updating the contract, mappings, connector configuration, tests, and documentation.

### 6.3 Configure standard REST intake and implement the remaining custom endpoints

Contract intake uses Salesforce standard REST and requires no custom Apex service:

| Method and path | Responsibility |
|---|---|
| `PATCH /services/data/{apiVersion}/sobjects/CLM_Contract__c/Contract_ID__c/{urlEncodedContractId}` | Create or update the contract idempotently |
| `GET /services/data/{apiVersion}/sobjects/CLM_Contract__c/Contract_ID__c/{urlEncodedContractId}?fields=Id,Contract_ID__c,Box_Workspace_Folder_ID__c` | Return stable React launch context after create or retry |

Configure both operations through the Box Automate OAuth 2.0 HTTPS connection defined in `config/box/https-connectors.json`. Use a dedicated Salesforce integration user and assign only the required object and field permissions.

From `clm-react-app`, run `./scripts/configure-clm-oauth.sh <clm-org-alias>`. The script creates or reuses the dedicated Salesforce Integration-licensed user, assigns `CLM_Box_Automate_Integration`, and deploys the `Box_Automate_CLM` External Client App plus its global OAuth settings, local OAuth settings, and OAuth policy. Metadata enables client credentials, selects the dedicated **Run As** user, requests only the `Api` scope, and enforces the admin-preauthorized permission-set policy. Store the consumer secret only in the Box Automate managed connection; it is intentionally absent from source.

The repository still specifies but does not implement these custom server-side endpoints:

| Method and path | Responsibility |
|---|---|
| `POST /services/apexrest/clm/redline-routing` | Validate findings, group by domain, resolve experts, create/reuse Box tasks, and return assignments |
| `GET /services/apexrest/clm/box-token?folderId=<id>` | Authenticate the Salesforce user and return a short-lived downscoped Box token as `{ "accessToken": "..." }` |
| `POST /services/apexrest/clm/contract-events/approval` | Accept the allowlisted approval-ready event |
| `POST /services/apexrest/clm/contract-events/executed` | Accept the allowlisted executed-agreement event |

Required controls:

- Authenticate and authorize every request, including standard REST through OAuth 2.0.
- Validate `folderId` against the Salesforce record; never downscope arbitrary folders supplied by the browser.
- Enforce the payload allowlist and prohibited fields from `config/box/https-connectors.json`.
- Keep Box credentials server-side.
- Use `Contract_ID__c` as the standard REST external ID for intake idempotency.
- Use `contractId:redlineFileId:domain` for task-routing idempotency.
- Return non-success responses for invalid findings, missing collaborators, or unauthorized folders.
- Add Apex tests for success, duplicate/idempotent requests, authorization failure, invalid payloads, and downstream Box failure.

### 6.4 Deploy the data model and React UI Bundle

```bash
cd clm-react-app
sf project deploy start \
  --source-dir force-app/main/default/objects/CLM_Contract__c \
  --source-dir 'force-app/main/default/layouts/CLM_Contract__c-CLM Contract Layout.layout-meta.xml' \
  --source-dir force-app/main/default/permissionsets/CLM_Box_Automate_Integration.permissionset-meta.xml \
  --source-dir force-app/main/default/permissionsets/CLM_Demo_Operator.permissionset-meta.xml \
  --source-dir force-app/main/default/tabs/CLM_Contract__c.tab-meta.xml \
  --target-org <clm-org-alias>

sf org assign permset \
  --name CLM_Demo_Operator \
  --target-org <clm-org-alias>

./scripts/configure-clm-oauth.sh <clm-org-alias>

sf project deploy start \
  --source-dir force-app/main/default/uiBundles \
  --target-org <clm-org-alias>
```

Then add `clmreactapp` to the intended Lightning record page or Experience surface. Launch it with:

```text
recordId=<returned-salesforce-id>&contractId=<contract-id>&folderId=<box-folder-id>
```

## 7. Configure Agentforce

Use `config/agentforce/clm-react-agentforce-spec.json` as the source contract.

1. Create or select the **Contract Copilot** agent.
2. Create the topics in the spec.
3. Register every read-only and mutation action against the deployed Apex implementation.
4. Apply the guardrails verbatim or with stricter org policy.
5. Confirm `compare_redline_to_clause_playbook` returns findings that validate against `config/clm/redline-finding.schema.json`.
6. Confirm `get_redline_review_queue` is read-only.
7. Require confirmation before either DocGen action.
8. Record the Agentforce agent and application IDs.
9. Provide the IDs through protected runtime configuration or the supported `VITE_AGENTFORCE_*` build variables.
10. Rebuild and redeploy the UI Bundle if build-time variables are used.

Expected behavior:

- Material answers cite Box files.
- The agent cannot approve language, complete human tasks, or start Box Sign.
- Named experts come only from the maintained routing directory.
- Missing or low-confidence routing returns Legal Operations triage.

## 8. Activate redline expert routing

1. Choose the approved baseline Box item for each redline comparison.
2. Replace the required `null` `boxLogin` values in `config/clm/expert-routing.json` with real Box users or managed groups.
3. Add those users/groups as collaborators on the contract workspace or relevant redline files.
4. Verify least-privilege access by signing in as, or testing with, each target expert.
5. Create the `clmRedlineReview` metadata template from the repository specification.
6. Deploy and test `POST /services/apexrest/clm/redline-routing`.
7. Test confidence below `0.85`, `Unclassified`, missing-expert, and missing-file-access cases; all must route to Legal Operations triage.
8. Test the same domain twice; the second call must reuse the open task rather than create task spam.
9. Build **CLM - Redline Domain Review Routing** in Box Automate from `config/box/automate-workflows.json`.
10. Leave it inactive until section 9 is complete and a human explicitly approves activation.

## 9. Bind and activate Box Automate

### 9.1 Configure the HTTPS connector

In `config/box/https-connectors.json`, replace only confirmed deployment values:

- `allowedDomain`
- `apiVersion`
- OAuth 2.0 External Client App and integration-user connection

External Client App source:

- `clm-react-app/force-app/main/default/externalClientApps/Box_Automate_CLM.eca-meta.xml`
- `clm-react-app/force-app/main/default/extlClntAppGlobalOauthSets/Box_Automate_CLM_glbloauth.ecaGlblOauth-meta.xml`
- `clm-react-app/force-app/main/default/extlClntAppOauthSettings/Box_Automate_CLM_oauth.ecaOauth-meta.xml`
- `clm-react-app/force-app/main/default/extlClntAppOauthPolicies/Box_Automate_CLM_oauthPlcy.ecaOauthPlcy-meta.xml`
- OAuth scope: `Api` only
- Metadata-managed preauthorized permission set: `CLM_Box_Automate_Integration`
- Metadata-managed Run As user: `box.automate.clm+00dgl000003d0lrua0@boxdemo.com`
- Idempotent reconciliation: `clm-react-app/scripts/configure-clm-oauth.sh <clm-org-alias>`
- Manual secret boundary: retrieve the ECA consumer secret and store it only in the Box-managed connection

The object, external ID, upsert path template, and lookup path template are already fixed to `CLM_Contract__c` and `Contract_ID__c`. Do not add a custom Apex intake endpoint.

Store OAuth client material and tokens in Box/Salesforce administrator-managed connection storage, never in this repository.

#### Remaining administrator steps

1. In Salesforce Setup, open **External Client App Manager** and select **Box Automate CLM Integration** (`Box_Automate_CLM`).
2. Open **Settings**, then **Consumer Key and Secret**. Complete Salesforce identity verification if prompted.
3. Copy the **Consumer Secret**. Do not paste it into chat, a terminal command, a repository file, or a screenshot.
4. Open Box Automate workflow [CLM - Contract Intake Enrichment](https://kadams.ent.box.com/automate/workflow/edit/399436615012).
5. Create or update the administrator-managed OAuth 2.0 connection with these values:

   | Setting | Value |
   |---|---|
   | Grant type | Client Credentials |
   | Token URL | `https://kadams-dev-ed.develop.my.salesforce.com/services/oauth2/token` |
   | Client ID | `3MVG9dAEux2v1sLvqwMv.uh.fDj5.dT8YnFSByxksfuDj98cOZNQ_wZR2AVRszo9bAJ0cpGPaJu4xAJyBmoUL` |
   | Client secret | The secret copied directly from Salesforce |
   | Scope | `api` only if Box requires a value; otherwise leave the optional field empty |

6. Test the managed connection. A successful token test is the only acceptable credential check; do not expose the returned access token.
7. Configure the approved branch to call the existing `salesforceContractUpsert` `PATCH`, followed by `salesforceContractLookup` `GET`, from `config/box/https-connectors.json`.
8. Run the duplicate-safe test with a clearly labeled demo `contractId`: the first `PATCH` creates one record, the second updates it, and both `GET` requests return the same Salesforce ID.
9. Leave the workflow inactive. Obtain the confirmation in section 9.3 immediately before the final activation click.

Do not select the similarly named legacy **Box Automate** app. Its consumer secret does not match the pinned `Box_Automate_CLM` client ID. The dedicated Run As user is already set by deployed metadata; it does not need to be selected again in Box.

If Salesforce rotates the secret later, update only the Box-managed connection and retest it. The consumer key is pinned in metadata; do not generate a new key unless rotation is intentional.

### 9.2 Validate inactive workflows

For each workflow, confirm trigger scope, test folder, assignees, branches, connector payload, rollback behavior, and idempotency before activation:

- `CLM - Contract Intake Enrichment`
- `CLM - Redline Domain Review Routing`
- `CLM - Approval Packet Readiness`
- `CLM - Executed Agreement Obligations`

### 9.3 Obtain activation confirmation

Activation is an external-state change. Immediately before clicking **Enable**, **Activate**, **Publish**, or equivalent:

1. State the exact workflow name.
2. State its trigger and affected folder.
3. State the external Salesforce destination.
4. State the test/rollback plan.
5. Ask the demo owner for explicit confirmation.

Do not activate on implied approval from earlier setup work.

## 10. Run the integrated smoke test

Use a clearly labeled non-production request. This test is also the activation gate for the [Box Form entry-point variation](../scenarios/agentic-orchestration/supporting-react-scripts/04-box-form-automate-entry.md).

1. Submit the published **New Contract Request** Form with the Northstar defaults from `box-web-ui-build-queue.md`.
2. Confirm the upload lands in intake folder `399082115646`.
3. Confirm Extract returns reviewable values and the AI Agent returns cited issues.
4. Inspect the human validation task. Reject and correct any invented or unsupported value.
5. Approve the validation task manually.
6. Confirm the standard REST `PATCH` creates exactly one Salesforce record and the follow-up `GET` returns its ID.
7. Retry the same request and confirm `PATCH` updates and `GET` returns the same record.
8. Launch React with the returned `recordId`, `contractId`, and `boxFolderId`.
9. Confirm live Box content loads through the downscoped token endpoint.
10. Ask Agentforce for a cited package summary.
11. Trigger or invoke the redline comparison.
12. Confirm every finding contains section, change type, domain, risk, confidence, approved position, and Box citation.
13. Confirm findings are grouped into one task per domain.
14. Confirm low-confidence findings go to Legal Operations triage.
15. Confirm React **Redline reviews** matches the live assignments.
16. Confirm signature remains blocked while required tasks are incomplete.
17. Ask to draft the approval memo and verify a human confirmation appears before DocGen creates a file.
18. Stop before sending a Box Sign request unless the demo owner separately confirms that action.

Record the Salesforce record ID, Box workflow run ID, created/reused task IDs, timestamps, and any correction made during validation.

## 11. Presenter preparation

- Choose [Governed Workflow](../scenarios/governed-workflow/README.md) or [Agentic Orchestration](../scenarios/agentic-orchestration/README.md) before opening presenter surfaces.
- Follow the selected scenario's single-page guide in order; use the audience-specific scripts under `docs/scenarios/agentic-orchestration/supporting-react-scripts/` only as optional supporting detail.
- Open only the surfaces required by the selected guide. Governed Workflow stays in Box; open the Salesforce record and React page only for Agentic Orchestration.
- Verify all named experts are available or use the documented demo-triage fallback.
- Keep live tasks incomplete if the story requires **Signature blocked**.
- Do not publish, share, approve, generate, sign, or send without the applicable confirmation.

## 12. Reset and teardown

After a smoke test or demo:

1. Disable test workflows if they were enabled only for the session.
2. Record, do not silently delete, test records, files, tasks, workflow runs, and DocGen outputs.
3. Remove temporary collaborators only after confirming they are not used by another demo.
4. Re-establish the intended task states for the next rehearsal.
5. Confirm no Box Sign request or external notification remains pending unintentionally.
6. Update `config/box/live-box-surface.json` only when live IDs or URLs actually changed.
7. Update `docs/08-handoff-progress.md` with the verified state and remaining blockers.

Copy the completion-log template from the bottom of `docs/manual-task-register.md` into the handoff or demo-run notes.

## 13. Troubleshooting

| Symptom | Check |
|---|---|
| Box page is empty or wrong | Confirm hostname is `kadams.ent.box.com` and IDs match `live-box-surface.json` |
| React shows fallback files | Downscoped token endpoint is missing, rejected, or returned no token |
| Agentforce shows prompt cards | Agent/application IDs are missing or the agent is not available to the current Salesforce user |
| Form does not trigger Automate | Workflow is inactive, trigger folder differs, or the Form destination changed |
| Salesforce duplicate records | Intake idempotency is not enforced on `contractId` |
| Duplicate Box tasks | Routing idempotency is not enforced on `contractId:redlineFileId:domain` |
| Expert assignment fails | User/group is not configured or lacks file collaboration |
| Redline goes to triage | Domain is unclassified, confidence is below `0.85`, expert is missing, or access validation failed |
| Box Explorer fails in Salesforce | Check same-origin endpoint authorization, Box application scopes, CORS, and folder downscope |
| DocGen or Sign appears too early | Guardrail or approval-state check is missing; stop the flow and correct it before continuing |

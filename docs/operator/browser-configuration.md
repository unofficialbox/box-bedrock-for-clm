# Browser and Administrator Configuration

Complete these steps after `box-foundation` and `salesforce-deploy`. Read IDs from the local, gitignored `config/runtime/bootstrap-state.json`.

Before any browser-agent step, sign in to the intended Box web application with the intended builder account and keep that tab open. Confirm its hostname exactly matches `config/runtime/demo-environment.json`. Browser plans and private-lab executors use that existing web session; they do not perform login or contain credentials.

## 1. Box content and metadata

1. Open the generated `CLM-2026-Northstar` workspace.
2. Mark the three Word files in `08 - DocGen Templates` as Box Doc Gen templates.
3. Confirm `seed-metadata` applied the `clmContract`, `clmDocument`, `clmObligation`, and `clmClause` values recorded in `bootstrap-state.json`.
4. Confirm the generated **Approved Clauses** folder contains the README plus eight standard/fallback Markdown clauses.
5. Assign real owners and collaborators from this environment; do not copy demo usernames.

## 2. Box Form

Prepare the guarded [Box Form Browser Plan](box-form-provisioner.md), then have an authenticated browser agent apply it. It builds one Form named **New Contract Request** from the portable definition and binds its destination to generated folder `01 - Intake`.

Verify the title, fields, required states, defaults, destination, and Box-default confirmation behavior. Box lists a saved Form as **Active**; obtain approval before copying, enabling, or distributing its link, then record the approved URL in `demo-environment.json`.

## 3. Box App

Build **Contract Lifecycle Management** from `config/box/box-app-blueprint.md`.

Use the generated folder/template IDs only when the builder asks for a binding. Put the high-frequency actions first: **Start a New Contract**, **Approved Clause Hub**, and **Executed Agreements**. Add charts by status, risk, contract type, region, and clause family so the dashboard appears operational rather than empty.

Obtain approval before publishing. Record the published URL in `demo-environment.json`.

## 4. Clause Library Hub

Create **Approved Contract Clause Library** from `config/box/hub-blueprint.md`.

Include the clause README, standard clauses, approved fallbacks, governance notes, ownership, and review cadence. Add enough usage metadata and recently reviewed content to demonstrate an actively maintained library. Obtain approval before publishing and record the URL.

## 5. Salesforce OAuth connection

1. Create a dedicated API-only integration user in the target org.
2. Assign `CLM_Box_Automate_Integration`.
3. In **Setup → External Client App Manager**, create **Box Automate CLM Integration**.
4. Enable OAuth and client-credentials flow; use `api` scope only.
5. Require administrator preauthorization and allow only `CLM_Box_Automate_Integration`.
6. Set the dedicated integration user as the client-credentials Run As user.
7. Keep refresh-token, device, JWT, and token-exchange flows disabled.
8. If Box requires a callback URL, use the target environment's saved workflow URL; the client-credentials flow does not otherwise use it.
9. Store the consumer secret only in the Box-managed OAuth connection.
10. Use the target org's My Domain token URL: `<my-domain>/services/oauth2/token`.
11. Test the connection without copying the returned token.

The repository intentionally contains no tenant-specific External Client App metadata. Create it in the target org using the settings above.

## 6. Box Automate

Build the workflows from `config/box/automate-workflows.json`. Start with **CLM - Contract Intake Enrichment**:

1. Trigger: **New Contract Request** submitted.
2. Extract: use the uploaded contract file and `config/box/extract-field-prompts.json`.
3. Agent review: use `config/box/ai-agent-specs.json` and require citations.
4. Human validation: assign a real reviewer in this environment.
5. Approved branch: Salesforce standard REST record creation, using `config/box/https-connectors.bcl`. Point the connector at the org that holds `CLM_Contract__c`; two similarly named connectors can target different orgs, and the wrong one fails as an opaque `UNKNOWN_ERROR`.
6. Rejected branch: return for correction; do not invoke Salesforce. The live workflow currently leaves this branch empty, so a rejected submission ends the run silently.

Save and test the workflow while inactive. Obtain explicit approval immediately before activation.

### HTTPS Request settings

Use the resolved file `config/runtime/generated/box/https-connectors.json`.

| Request | Setting | Value |
|---|---|---|
| Upsert | Method | `PATCH` |
| Upsert | Endpoint | `/services/data/v67.0/sobjects/CLM_Contract__c/Contract_ID__c/{urlEncodedContractId}` |
| Upsert | Header | `Content-Type: application/json` |
| Upsert | Body | Copy the allowlisted field mapping from `salesforceContractUpsert.body` |
| Lookup | Method | `GET` |
| Lookup | Endpoint | `/services/data/v67.0/sobjects/CLM_Contract__c/Contract_ID__c/{urlEncodedContractId}?fields=Id,Contract_ID__c,Box_Workspace_Folder_ID__c` |
| Lookup | Output | `recordId=$.Id`, `contractId=$.Contract_ID__c`, `boxFolderId=$.Box_Workspace_Folder_ID__c` |

Do not place the OAuth token in a header manually; select the Box-managed OAuth connection. If a Box variable picker uses different display labels, bind by the logical field named in the resolved JSON and verify the test preview before saving.

## 7. Agentforce and optional orchestration

For Box Automate Agentic Orchestration, configure only the Agentforce actions used by the Box-led path. For Cross-Platform Agentic Orchestration, follow [Cross-Platform Agentic Orchestration deployment boundary](cross-platform-deployment.md). The repository provides a local deterministic trace; it does not yet automate managed AgentCore or Databricks provisioning.

Record the new environment's IDs in `demo-environment.json`; never write secrets there.

## 8. Completion gate

Proceed only when:

- The App, Form, and Hub open for the intended operator.
- The Form targets the generated intake folder.
- The workflow is saved and remains inactive until approval.
- OAuth succeeds as the dedicated integration user.
- One record creation succeeds in a labeled test, and the created record is opened and checked field by field in Salesforce rather than trusted from the Box run events.
- Every bound value is sourced from a **required** Form field. An unresolved variable is sent as the literal string `Variable unavailable`, not as an empty value, so an optional source corrupts any typed Salesforce field.
- Duplicate behaviour is understood and accepted: the current create path is not idempotent, so a duplicate submission creates a second record. Restore the external-ID upsert if duplicate safety is required.

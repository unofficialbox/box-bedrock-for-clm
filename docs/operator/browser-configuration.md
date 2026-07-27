# Browser and Administrator Configuration

Complete these steps after `box-foundation` and `salesforce-deploy`. Read IDs from the local, gitignored `config/runtime/bootstrap-state.bcl`.

Before any browser-agent step, sign in to the intended Box web application with the intended builder account and keep that tab open. Confirm its hostname exactly matches `config/runtime/demo-environment.bcl`. Browser plans and private-lab executors use that existing web session; they do not perform login or contain credentials.

## 1. Box content and metadata

1. Open the generated `CLM-2026-Northstar` workspace.
2. Mark the three Word files in `08 - DocGen Templates` as Box Doc Gen templates.
3. Confirm `seed-metadata` applied the `clmContract`, `clmDocument`, `clmObligation`, and `clmClause` values recorded in `bootstrap-state.bcl`.
4. Confirm the generated **Approved Clauses** folder contains the README plus eight standard/fallback Markdown clauses.
5. Assign real owners and collaborators from this environment; do not copy demo usernames.

## 2. Box intake entry point

Intake no longer uses a Box Form. A contract enters the pipeline when it is uploaded into generated folder `01 - Intake` and the `clmContract` metadata template is applied to it, with `contractId`, `contractType`, `counterparty`, and `requesterEmail` populated. Applying that metadata is the trigger for the **CLM - Contract Intake Enrichment** workflow.

Confirm the `01 - Intake` folder exists and that the `clmContract` template is available in this environment (section 1). No Form is built, enabled, or distributed.

## 3. Box App

Build **Contract Lifecycle Management** from `config/box/box-app-blueprint.md`.

Use the generated folder/template IDs only when the builder asks for a binding. Put high-frequency actions first: **Start a New Contract**, **Approved Clause Hub**, and **Executed Agreements**. Add charts by status, risk, contract type, region, and clause family.

Obtain approval before publishing. Record the published URL in `demo-environment.bcl`.

## 4. Clause Library Hub

Create **Approved Contract Clause Library** from `config/box/hub-blueprint.md`.

Include the clause README, standard clauses, approved fallbacks, governance notes, ownership, and review cadence. Add usage metadata and recently reviewed content. Obtain approval before publishing and record the URL.

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

Build the workflows from `config/box/automate-workflows.bcl`. Start with **CLM - Contract Intake Enrichment**:

1. Trigger: `clmContract` metadata applied to a file in generated `01 - Intake`. The trigger yields `static.trigger.fileId` and `static.trigger.metadata.<key>`.
2. Extract: use the uploaded contract file and `config/box/extract-field-prompts.bcl`.
3. Agent review: use `config/box/ai-agent-specs.bcl` and require citations.
4. Human validation: assign a real reviewer in this environment.
5. Approved branch: Salesforce standard REST record creation, using `config/box/https-connectors.bcl`. Point the connector at the org that holds `CLM_Contract__c`; two similarly named connectors can target different orgs, and the wrong one fails as an opaque `UNKNOWN_ERROR`.
6. Rejected branch: return for correction; do not invoke Salesforce. The live workflow currently leaves this branch empty, so a rejected submission ends the run silently.

Save and test the workflow while inactive. Obtain explicit approval immediately before activation.

### HTTPS Request settings

Use the resolved file `config/runtime/generated/box/https-connectors.bcl`.

The intended live path is a plain **POST** record create, not an upsert. This is the configuration that created a real `CLM_Contract__c` record end to end on 2026-07-22, when intake was triggered by the now-removed Box Form. The connector endpoint and body are unchanged, but the trigger is now the `clmContract` metadata event and every dynamic value is re-sourced from `static.trigger.metadata.<key>`. That metadata-triggered path has not been re-verified live and must be re-tested before activation.

| Request | Setting | Value |
|---|---|---|
| Create | Method | `POST` |
| Create | Endpoint | `services/data/v67.0/sobjects/CLM_Contract__c` (no leading slash; resolved against the connector base URL. Plain sobject collection, not an external-ID upsert path.) |
| Create | Headers | None. The verified outcome enables no headers and no query parameters; authorization is handled entirely by the Box-managed OAuth connection. |
| Create | Body | Copy the field mapping from `salesforceContractCreate.body`. Every bound value must be sourced from a populated `clmContract` metadata key (`static.trigger.metadata.<key>`) or another mandatory source, or Box sends the literal `Variable unavailable`. |
| Create | Output | `id=$.id` |

Do not place the OAuth token in a header manually; select the Box-managed OAuth connection. If a Box variable picker uses different display labels, bind by the logical field named in the resolved BCL and verify the test preview before saving.

This POST is **not idempotent** (`idempotency.safe = false`): resubmitting the same contract creates a second record. The connector also carries `salesforceContractUpsert` (a `PATCH` on `Contract_ID__c`) and `salesforceContractLookup` (a `GET`) as the duplicate-safe alternative, but that upsert path is not the proven live path — `salesforceContractUpsert` is marked `supersededForCreate = "salesforceContractCreate"`. Restore it only if duplicate safety is required, and re-verify against a live run before relying on it.

## 7. Agentforce and optional orchestration

For Box Automate Agentic Orchestration, configure only the Agentforce actions used by the Box-led path. For Cross-Platform Agentic Orchestration, follow [Cross-Platform Agentic Orchestration deployment boundary](cross-platform-deployment.md). The repository provides a local deterministic trace; it does not yet automate managed AgentCore or Databricks provisioning.

Record the new environment's IDs in `demo-environment.bcl`; never write secrets there.

## 8. Completion gate

Proceed only when:

- The App and Hub open for the intended operator.
- The `01 - Intake` folder accepts uploads and the `clmContract` metadata trigger starts the workflow.
- The workflow is saved and remains inactive until approval.
- OAuth succeeds as the dedicated integration user.
- One record creation succeeds in a labeled test, and the created record is opened and checked field by field in Salesforce rather than trusted from the Box run events.
- Every bound value is sourced from a populated `clmContract` metadata key (`static.trigger.metadata.<key>`) or another mandatory source. An unresolved variable is sent as the literal string `Variable unavailable`, not as an empty value, so an optional source corrupts any typed Salesforce field.
- Duplicate behaviour is understood and accepted: the current create path is not idempotent, so a duplicate submission creates a second record. Restore the external-ID upsert if duplicate safety is required.

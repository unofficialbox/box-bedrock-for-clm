# CLM Salesforce Project

This Salesforce DX project contains the portable `CLM_Contract__c` data model, layout, permission sets, tab, and Salesforce Multi-Framework React UI Bundle.

Start with [CLM Demo Operator Start Here](../docs/operator/start-here.md). The root automation deploys the portable components and deliberately excludes tenant-specific OAuth metadata.

## Local UI development

```bash
cd force-app/main/default/uiBundles/clmreactapp
npm install
npm run dev
```

The local experience uses synthetic Northstar data and a safe Box fallback. It contains no credentials.

The fallback contains no tenant hostname, Box IDs, task IDs, or usernames. Supply new-environment bindings at build time when needed:

- `VITE_BOX_HOSTNAME`, `VITE_BOX_FOLDER_ID`, and the optional `VITE_BOX_*_FOLDER_ID` values;
- `VITE_BOX_APP_URL` and `VITE_BOX_FORM_URL`;
- `VITE_AGENTFORCE_AGENT_ID`, `VITE_AGENTFORCE_APP_ID`, and `VITE_SALESFORCE_ORIGIN`.

The Salesforce page must pass `recordId`, `contractId`, and `folderId` in its launch context. Without a downscoped Box token, the fallback deliberately shows inert synthetic file rows rather than links to another tenant.

## Verification

```bash
cd force-app/main/default/uiBundles/clmreactapp
npm test -- --run
npm run build
npm run test:e2e
```

## Portable deployment

From the repository root:

```bash
python3 scripts/demo_operator.py salesforce-deploy --dry-run
python3 scripts/demo_operator.py salesforce-deploy
```
This deploys the object, fields, layout, operator and integration permission sets, tab, and UI Bundle. It then assigns `CLM_Demo_Operator` to the authenticated operator. Environment-specific OAuth metadata is intentionally not included.

## Salesforce sample data (packageable)

The `sample-data/` folder captures a deterministic CLM dataset (Accounts, Contacts, Opportunities, Contracts) plus an idempotent Apex seed and a BCL manifest.

- Idempotent Apex seed (source of truth):
  - `./scripts/seed-clm-sample-data.sh <orgAlias>`
- BCL manifest (descriptive; not read at seed time):
  - `sample-data/clm-sample-records.bcl`

This lets each environment load the same contract relationships and record shape before demo setup.

## Integration user

After reviewing the target org shown by `sf org display`:

```bash
CLM_INTEGRATION_USERNAME='unique-user@your-domain.example' \
CLM_INTEGRATION_EMAIL='your-admin@your-domain.example' \
./scripts/configure-clm-oauth.sh <org-alias>
```

The script creates or reuses an API-only integration user and assigns only `CLM_Box_Automate_Integration`.

## External Client App

Create the External Client App in the target org because these values are environment-specific:

- org scope;
- consumer key and secret;
- callback URL;
- dedicated Run As username;
- Salesforce My Domain token URL.

Use client credentials, `api` scope only, administrator preauthorization, and the dedicated integration user as Run As. Store the consumer secret only in the Box-managed OAuth connection.

## Runtime integration

1. Set Agentforce IDs through protected runtime configuration or supported `VITE_AGENTFORCE_*` build variables.
2. Implement the same-origin, authorized, downscoped Box-token endpoint before claiming live embedded Box content.
3. Add the UI Bundle to the intended Lightning/Experience page.
4. Pass this environment's `recordId`, `contractId`, and `folderId`.
5. Use Salesforce standard REST external-ID upsert and lookup for intake record creation; no custom Apex intake service is required.

The repository does not yet include the Apex implementations for redline routing, lifecycle-event ingestion, or downscoped Box-token issuance. Implement and test those endpoints before presenting the full integration as live.

# CLM Multi-Framework React App

This Salesforce UI Bundle is the presentation layer for the **Box + Agentforce + React** CLM demo variation. It reuses the Salesforce Multi-Framework React shape from the citizen-services demo while keeping the CLM path limited to:

- Box for contract files, metadata, tasks, DocGen, Sign, and governance
- Agentforce for conversational orchestration and human-in-the-loop recommendations
- This React UI Bundle for the contract workspace

AWS Bedrock AgentCore, Strands, Databricks, and separate custom middleware are not part of this variation.

## Local development

Full operator prerequisites and deployment steps: [`../docs/runbooks/05-demo-setup-and-activation.md`](../docs/runbooks/05-demo-setup-and-activation.md). Manual administrator and confirmation-gated work: [`../docs/manual-task-register.md`](../docs/manual-task-register.md).

```bash
cd force-app/main/default/uiBundles/clmreactapp
npm install
npm run dev
```

The local experience uses the Northstar demo record and a safe Box fallback view. It does not require or embed credentials.

## Verification

```bash
cd force-app/main/default/uiBundles/clmreactapp
npm test -- --run
npm run build
npm run test:e2e
```

## Live configuration

Before Salesforce deployment:

1. Run `./scripts/configure-clm-oauth.sh <org-alias>` to reconcile the dedicated integration user, permission assignment, and metadata-managed `Box_Automate_CLM` External Client App.
2. Set the Agentforce agent and application IDs in runtime configuration or `VITE_AGENTFORCE_*` build variables.
3. Implement `GET /services/apexrest/clm/box-token?folderId=<id>` in Salesforce. It must return a short-lived, downscoped token as `{ "accessToken": "..." }`.
4. Deploy the UI Bundle, then add the resulting surface to the intended Lightning or Experience site.

Never put Box or Salesforce client secrets in browser-delivered source.

## Deploy

```bash
sf project deploy start \
  --source-dir force-app/main/default/objects/CLM_Contract__c \
  --source-dir 'force-app/main/default/layouts/CLM_Contract__c-CLM Contract Layout.layout-meta.xml' \
  --source-dir force-app/main/default/permissionsets/CLM_Box_Automate_Integration.permissionset-meta.xml \
  --source-dir force-app/main/default/permissionsets/CLM_Demo_Operator.permissionset-meta.xml \
  --source-dir force-app/main/default/tabs/CLM_Contract__c.tab-meta.xml \
  --target-org <alias>

sf org assign permset --name CLM_Demo_Operator --target-org <alias>
./scripts/configure-clm-oauth.sh <alias>

sf project deploy start \
  --source-dir force-app/main/default/uiBundles \
  --target-org <alias>
```

## External Client App activation

The source project contains the complete non-secret OAuth configuration:

- `force-app/main/default/externalClientApps/Box_Automate_CLM.eca-meta.xml`
- `force-app/main/default/extlClntAppGlobalOauthSets/Box_Automate_CLM_glbloauth.ecaGlblOauth-meta.xml`
- `force-app/main/default/extlClntAppOauthSettings/Box_Automate_CLM_oauth.ecaOauth-meta.xml`
- `force-app/main/default/extlClntAppOauthPolicies/Box_Automate_CLM_oauthPlcy.ecaOauthPlcy-meta.xml`
- `force-app/main/default/permissionsets/CLM_Box_Automate_Integration.permissionset-meta.xml`
- `scripts/configure-clm-oauth.sh`

The app requests only the Salesforce `Api` OAuth scope. Metadata enables client credentials, requires a consumer secret, uses the admin-preauthorized permission-set policy, relaxes IP restrictions for the trusted Box server-to-server client, and binds the dedicated `box.automate.clm+00dgl000003d0lrua0@boxdemo.com` Run As user. The consumer key is safe to version and is pinned to prevent accidental rotation. The consumer secret and access tokens must never be stored in this repository.

Box Automate does not provide a stable, verified egress IP set for this connector, so the OAuth policy cannot use an IP allowlist without making the integration unreliable. The explicit compensating controls are:

- a dedicated Salesforce Integration user on the minimum-access API-only profile;
- only the `CLM_Box_Automate_Integration` permission set;
- only the Salesforce `Api` OAuth scope;
- administrator-preauthorized client credentials with a pinned consumer key;
- administrator-managed secret storage in Box; and
- workflow-level allowlisting of the CLM external-ID upsert and lookup operations, with the workflow inactive until idempotency testing passes.

For org `00DgL000003D0LRUA0`, the automation script is idempotent and:

1. Refuses to run against a different org ID.
2. Creates or reuses the Salesforce Integration-licensed user with the minimum-access API profile.
3. Assigns only `CLM_Box_Automate_Integration`.
4. Deploys the External Client App, global OAuth settings, local OAuth settings, and OAuth policy in dependency order.
5. Verifies the user, assignment, and app.

The only remaining secret-bearing step is to retrieve the External Client App consumer secret and store it with the recorded consumer key in the Box Automate managed OAuth 2.0 connection. Then test the token and standard REST external-ID upsert/lookup before activating the workflow.

Operator values for that Box-managed connection:

- Salesforce External Client App: `Box Automate CLM Integration`
- Client ID / consumer key: `3MVG9dAEux2v1sLvqwMv.uh.fDj5.dT8YnFSByxksfuDj98cOZNQ_wZR2AVRszo9bAJ0cpGPaJu4xAJyBmoUL`
- Token URL: `https://kadams-dev-ed.develop.my.salesforce.com/services/oauth2/token`
- Grant type: OAuth 2.0 client credentials
- Scope: `api` if Box requires a scope value; otherwise leave the optional scope field empty
- Secret: retrieve it in Salesforce Setup and paste it directly into Box; never place it in chat, source, screenshots, or shell history

Do not use the similarly named legacy **Box Automate** app. Its consumer secret does not match the pinned `Box_Automate_CLM` client ID. If the CLM app is not visible in External Client App Manager, retrieve or rotate its OAuth consumer secret through Salesforce's supported External Client App credentials administration path before retrying Box.

Use Box workflow `399436615012` for the connection test. Keep the workflow inactive until its REST steps and idempotency test pass and the demo owner explicitly approves activation.

The legacy `Box_Automate_CLM_Integration` Connected App metadata remains in source as a fallback for older orgs; it is not the primary configuration.

The Agentforce action contract and presenter flow live in:

- `../config/agentforce/clm-react-agentforce-spec.json`
- `../docs/runbooks/04-box-agentforce-react-demo.md`

Contract record creation uses Salesforce standard REST external-ID upsert and lookup through Box Automate; it does not require Apex. The repository does not currently include the Apex implementations for redline routing, lifecycle-event ingestion, or downscoped Box-token issuance. Implement and test those remaining endpoints before presenting the full integrated flow as live.

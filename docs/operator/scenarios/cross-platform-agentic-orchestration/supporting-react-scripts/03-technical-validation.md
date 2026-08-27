# Technical Demo: Runtime, Security, and Guardrails

## Demo card

| Item | Value |
|---|---|
| Duration | 20-30 minutes |
| Audience | Enterprise architects, Salesforce developers, Box platform teams, security reviewers |
| Goal | Validate that the focused CLM variation contains only the approved runtime participants and preserves human control |

## Architecture statement

The runtime path is:

1. Box metadata and Automate capture and enrich the contract request: applying the `clmContract` metadata to a file in `01 - Intake` triggers the workflow.
2. A human validates Extract and Box Agent output.
3. The approved HTTPS branch uses Salesforce standard REST to upsert one CLM record by external ID, then looks it up for a stable record ID.
4. Salesforce hosts the Multi-Framework React UI Bundle.
5. The React app passes the Salesforce record, contract, and Box folder context to Agentforce.
6. The React app and Agentforce use Box APIs/capabilities for content operations.
7. Salesforce provides a short-lived, downscoped Box token through a same-origin endpoint.
8. Structured redline findings are validated against a schema and grouped into one Box task per expert domain.
9. Human reviewers complete approval decisions before Box Sign.

There is no call to AgentCore, Strands, Databricks, or external custom middleware.

## Script

### Act 0 — Validate Salesforce record creation (4 minutes)

**Show**

- `config/box/automate-workflows.json` and the target environment's saved workflow.
- The approval task before the standard REST upsert and lookup stages.
- The `CLM_Contract__c` object, private sharing, unique `Contract_ID__c`, and mapping in `config/salesforce/clm-contract-record.json`.
- The upsert status and external-ID lookup response mapped to `recordId`, `contractId`, and `boxFolderId`.

**Verify**

- Replaying the same approved request does not create a duplicate record.
- No contract file bytes, access tokens, or unreviewed AI output are sent.
- A failed upsert or lookup keeps the Box request available for connector retry.

### Act 1 — Inspect the deployable UI Bundle (4 minutes)

**Show**

- `clm-salesforce-project/force-app/main/default/uiBundles/clmreactapp/`.
- `clmreactapp.uibundle-meta.xml` with target `Experience`.
- `settings/Communities.settings-meta.xml` and `settings/ExperienceBundle.settings-meta.xml` enabling deployable Digital Experiences metadata.
- `sites/CLM_Experience.site-meta.xml`, `networks/CLM Experience.network-meta.xml`, and the `CLM_Experience1` Digital Experience bundle/config mounting `c__clmreactapp` at `/clm`.
- `src/Workspace.tsx`, `src/components/BoxWorkspace.tsx`, and `src/components/AgentforcePanel.tsx`.

**Explain**

- React owns layout and interaction state.
- Box Workspace owns content rendering/token acquisition.
- Agentforce Panel owns the embedded conversation client.
- The app is external-facing through Experience Cloud, but the packaged site requires authenticated access and disables self-registration.
- Dispatch publishes the Experience after metadata deployment and waits for the Salesforce background operation to complete before reporting the external application as ready.

### Act 2 — Prove the credential boundary (4 minutes)

**Show**

- `fetchDownscopedBoxToken()` in `src/lib/box.ts`.
- Request path: `/services/apexrest/clm/box-token?folderId=<id>`.
- The source scan that rejects `CLIENT_SECRET` and `client_secret` in browser code.

**Explain**

- The browser receives only a short-lived token scoped to the requested Box folder.
- Box and Salesforce client secrets remain server-side.
- Local mode renders a safe file-link fallback without credentials.

### Act 3 — Validate context and source authority (4 minutes)

**Show**

- `getClmPageContext()` accepts the returned Salesforce record ID, contract ID, and generated Box folder ID.
- `getAgentContextPrompt()` instructs Agentforce to use Box as source of truth and cite files.
- The gitignored `config/runtime/bootstrap-state.json` as the target environment's generated-ID authority.

**Test prompt**

> Identify the current contract and Box workspace. Then summarize the MSA risk with a file citation.

### Act 4 — Inspect Agentforce actions (5 minutes)

**Show**

- `config/agentforce/clm-react-agentforce-spec.json`.
- Read-only actions for context, listing, summarization, playbook comparison, tasks, and blockers.
- Mutating DocGen actions marked `confirmationRequired: true`.

**Call out**

- No action completes an approval task.
- No action creates a Box Sign request before approvals.
- `compare_redline_to_clause_playbook` emits `config/clm/redline-finding.schema.json` findings.
- `get_redline_review_queue` is read-only and exposes domain groups, assignments, triage exceptions, and Box tasks.
- `routeRedlineFindings` uses `contractId:redlineFileId:domain` as its idempotency key.
- Expert identities come only from `config/clm/expert-routing.json`; missing collaborators fail to Legal Operations triage.
- No action sends data to an external agent/analytics runtime.

### Act 5 — Exercise the human gate (4 minutes)

**Show**

- Open **Approvals** in the rendered app.
- Confirm three Pending tasks and **Signature blocked**.
- Confirm that no **Approve** button exists.

**Explain**

The UI, action contract, and presenter script all enforce the same decision boundary.

### Act 6 — Run the verification gate (4 minutes)

```bash
cd clm-salesforce-project/force-app/main/default/uiBundles/clmreactapp
npm run lint
npm test -- --run
npm run build -- --mode standalone
npm run test:e2e
npm audit --omit=dev
```

From the CLM root:

```bash
python3 -m json.tool config/demo/cross-platform-agentic-orchestration-demo-manifest.json >/dev/null
python3 -m json.tool config/agentforce/clm-react-agentforce-spec.json >/dev/null
python3 -m json.tool config/runtime/demo-environment.json >/dev/null
```

## Technical pass criteria

- UI Bundle builds without a Salesforce org in standalone mode.
- Unit and end-to-end tests pass.
- Production dependency audit reports zero vulnerabilities.
- Browser code contains no client secret.
- Runtime actions match the manifest and Agentforce spec.
- Salesforce record creation is idempotent, occurs after human validation, and returns the context consumed by React.
- Approval and signature mutations remain human-controlled.

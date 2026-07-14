# Technical Demo: Runtime, Security, and Guardrails

## Demo card

| Item | Value |
|---|---|
| Duration | 20-30 minutes |
| Audience | Enterprise architects, Salesforce developers, Box platform teams, security reviewers |
| Goal | Validate that the focused CLM variation contains only the approved runtime participants and preserves human control |

## Architecture statement

The runtime path is:

1. Box Forms and Automate capture and enrich the contract request.
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

- `config/box/automate-workflows.json` and the saved workflow ID `399436615012`.
- The approval task before the standard REST upsert and lookup stages.
- The `CLM_Contract__c` object, private sharing, unique `Contract_ID__c`, and mapping in `config/salesforce/clm-contract-record.json`.
- The upsert status and external-ID lookup response mapped to `recordId`, `contractId`, and `boxFolderId`.

**Verify**

- Replaying the same approved request does not create a duplicate record.
- No contract file bytes, access tokens, or unreviewed AI output are sent.
- A failed upsert or lookup keeps the Box request available for connector retry.

### Act 1 — Inspect the deployable UI Bundle (4 minutes)

**Show**

- `clm-react-app/force-app/main/default/uiBundles/clmreactapp/`.
- `clmreactapp.uibundle-meta.xml` with target `Experience`.
- `src/Workspace.tsx`, `src/components/BoxWorkspace.tsx`, and `src/components/AgentforcePanel.tsx`.

**Explain**

- React owns layout and interaction state.
- Box Workspace owns content rendering/token acquisition.
- Agentforce Panel owns the embedded conversation client.

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

- `getClmPageContext()` accepts the returned Salesforce `recordId` with contract `CLM-2026-0017` and folder `399081692991`.
- `getAgentContextPrompt()` instructs Agentforce to use Box as source of truth and cite files.
- `config/box/live-box-surface.json` as the live-ID authority.

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
cd clm-react-app/force-app/main/default/uiBundles/clmreactapp
npm run lint
npm test -- --run
npm run build -- --mode standalone
npm run test:e2e
npm audit --omit=dev
```

From the CLM root:

```bash
python3 -m json.tool config/demo/box-agentforce-react-demo-manifest.json >/dev/null
python3 -m json.tool config/agentforce/clm-react-agentforce-spec.json >/dev/null
python3 -m json.tool config/box/live-box-surface.json >/dev/null
```

## Technical pass criteria

- UI Bundle builds without a Salesforce org in standalone mode.
- Unit and end-to-end tests pass.
- Production dependency audit reports zero vulnerabilities.
- Browser code contains no client secret.
- Runtime actions match the manifest and Agentforce spec.
- Salesforce record creation is idempotent, occurs after human validation, and returns the context consumed by React.
- Approval and signature mutations remain human-controlled.

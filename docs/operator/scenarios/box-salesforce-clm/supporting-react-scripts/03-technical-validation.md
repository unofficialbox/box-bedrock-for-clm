# Technical Demo: Runtime, Security, and Guardrails

## Demo card

| Item | Value |
|---|---|
| Duration | 15-20 minutes |
| Audience | Enterprise architects, Salesforce developers, Box platform teams, security reviewers |
| Goal | Show where each credential lives, what bounds each surface, and which boundaries are enforced by the platform rather than by the prompt |

## Architecture statement

1. Applying `clmContract` metadata to a file in `01 - Intake` triggers a Box Automate workflow.
2. A human validates the Extract and Box AI output.
3. The approved branch calls Salesforce standard REST and creates one `CLM_Contract__c` record.
4. Salesforce hosts the Multi-Framework React UI Bundle on an Experience Cloud site.
5. The site's workspace reads Box content with a short-lived token downscoped to one folder.
6. The internal persona reaches the same governed Apex through a hosted MCP server.
7. The counterparty's record access is enforced by a Salesforce sharing set.

There is no call to an external agent runtime or middleware in this variation.

## Script

### Act 0 — Record creation, and what it does not yet guarantee (2 minutes)

**Show**

- The Automate approval task standing before the connector call.
- `config/box/https-connectors.bcl` and the `CLM_Contract__c` object with its unique `Contract_ID__c`.

**Say this exactly**

> The proven connector is a plain `POST` create. It is **not** idempotent: re-triggering the
> same contract creates a second record. The duplicate-safe design is a `PATCH` upsert against
> the `Contract_ID__c` external ID, and it is not the path that runs today.

Do not claim duplicate safety unless the org on screen actually runs the upsert path.

**Verify**

- No contract bytes, Box tokens, connector secrets, or unreviewed AI output appear in the request.

### Act 1 — The deployable UI Bundle (2 minutes)

**Show**

- `clm-salesforce-project/force-app/main/default/uiBundles/clmreactapp/` and `clmreactapp.uibundle-meta.xml` with target `Experience`.
- `sites/CLM_Experience.site-meta.xml` and `networks/CLM Experience.network-meta.xml` mounting `c__clmreactapp` at `/clm`.
- `src/Workspace.tsx`, `src/components/BoxWorkspace.tsx`, `src/components/AgentforcePanel.tsx`.

**Explain**

The site requires authenticated access and disables self-registration. This app is the
**counterparty's** surface; the internal persona does not use it.

### Act 2 — The credential boundary (4 minutes)

**Show**

- `fetchDownscopedBoxToken()` in `src/lib/box.ts`, calling `/services/apexrest/clm/box-token?folderId=<id>`.
- `ClmBoxTokenService.cls`: a client-credentials grant, then an exchange scoped to one folder.
- The requested scope string, which is wider than a read-only demo implies:

  ```
  base_explorer item_preview item_read item_upload item_download item_delete item_rename item_share
  ```

- The merge fields in the grant body. Apex holds `{!$Credential.Username}` and
  `{!$Credential.Password}` and never a secret; Salesforce substitutes the encrypted values
  from the `CLM_Box` external credential at callout time.
- The repository secret scan that rejects `client_secret` in browser code.

**Explain**

- The browser receives only a short-lived token bound to one folder. The enterprise parent
  token is exchanged, never returned.
- Non-numeric folder ids are rejected before any call reaches Box.
- **A folder needs a direct collaboration to downscope.** Inherited access returns
  `invalid_resource` from the exchange while `GET /2.0/folders/<id>` still answers 200 with
  `can_upload: true`. The tell is `GET /2.0/folders/<id>/collaborations`.

**Credential model:** a Client Credentials Grant app, so any authorized viewer of the site
gets a preview with no per-user consent. Moving to per-user Box OAuth gives per-person
attribution in Box's audit log and removes the enterprise-wide token, at the cost of one
consent per user. That is MT-040 and it is not done.

### Act 3 — Why the preview is bundled, not fetched (3 minutes)

This is the most Salesforce-specific constraint in the build and it is worth the time.

**Show**

- `src/lib/boxPreviewRuntime.ts` and the `BundledPreview` subclass.
- The site's live CSP header: the Box trusted sites reach `style-src`, `media-src`,
  `font-src`, `connect-src` and `frame-src` -- and only `script-src` is missing them.

**Explain**

> Box Content Preview normally injects a `<script>` from the Box CDN. On an Experience Cloud
> site that script never loads, and there is no setting to change it: `CspTrustedSite` has
> **no script-src field at all**. Querying `IsApplicableToScriptSrc` fails with "No such
> column". The Strict/Relaxed CSP switch lives in Experience Builder, which refuses to open a
> React-framework site.

So the renderer is an npm dependency the bundler puts on the page. `boxPreviewRuntime.ts`
assigns `global.Box.Preview` unconditionally -- importing the package already registers a
plain `Preview` there, so a "only if missing" guard silently wins and drops the subclass.

**Verify on the deployed site:** a 7-page redline renders, with zero script requests to
`cdn01.boxcdn.net`.

### Act 4 — The agent's real actions (3 minutes)

**Show**

`clm-salesforce-project/force-app/main/default/aiAuthoringBundles/CLM_Contract_Copilot/`.
Two actions exist:

| Action | Target | Purpose |
|---|---|---|
| `get_contract_package` | `apex://ClmContractPackage` | Resolves the contract, its Box folder, and every document's Box file ID |
| `ask_box_ai` | `apex://ClmBoxAskDocument` | Asks Box AI about one file id, or the clause-library Hub |

**Call out**

- `ask_box_ai` carries `available when @variables.contractPackageLoaded == True`. Prose
  ordering was ignored five times in a row; the hard guard is what fixed it, because the wrong
  order is never offered.
- `ClmBoxAskDocument` forces the Hub id from configuration, so a caller cannot name which
  library to check itself against.
- The managed-package Box AI invocable authenticates as the *Salesforce user*, and an agent
  user has no linked Box account. That is why this is custom Apex on the org's own
  client-credentials grant.

**The lesson worth stating:** when an action never appears in the trace at all, suspect
permissions before prompting. An unavailable action is invisible, not failed.

`config/agentforce/clm-react-agentforce-spec.bcl` still describes redline-routing actions.
Those are a **design spec, not deployed behaviour** -- say so if anyone opens it.

### Act 5 — Two boundaries, one of them incomplete (4 minutes)

Show both. The second is the honest half.

**The workspace is bounded, and it is checkable.**

- `CLM_Counterparty_Access` maps `CLM_Contract__c.Counterparty_Account__c` to the signed-in
  user's Contact Account.
- `ClmContractListService.ContractReader` runs **`with sharing`**, so the platform filters it.
- Verify with `UserRecordAccess` rather than the share tables, which show zero rows for
  sharing-set access:

  ```sql
  SELECT RecordId, HasReadAccess FROM UserRecordAccess
  WHERE UserId = '<counterparty user>' AND RecordId IN (<contract ids>)
  ```

  The counterparty reads their own contracts and has no access to the others.

**The agent is not bounded, because of what kind of agent it is.**

- The Copilot is a Service Agent -- `BotDefinition.Type = ExternalCopilot`,
  `AgentType = EinsteinServiceAgent` -- and a Service Agent runs as the agent user named in
  `BotUserId`, not as the signed-in person. So `UserInfo.getUserId()` returns the agent, its
  Contact is null, and an identity-scoped action is useless inside it. The org confirms the
  binding directly:

  ```sql
  SELECT DeveloperName, Type, BotUserId, BotUser.Name FROM BotDefinition
  ```

- **An Employee Agent behaves the other way.** It inherits the permissions of the logged-in
  user and its `default_agent_user` is optional. The limitation below is a property of the
  agent type, not of Agentforce.
- `get_contract_package` binds `with inputContract = ...`, meaning the model fills it from the
  conversation. **A counterparty can therefore ask the Copilot about another company's
  contract by naming it.**
- The downscoped Box token bounds the workspace UI. It does not bound the agent, which reaches
  Box through Apex under the app's own credentials.

State this plainly to a security audience, and state its edges honestly. What is verified is
that this agent runs as its bot user: its actions failed until that user was granted access,
observed in the Agentforce Builder preview. What is **not** verified is how a Service Agent
behaves for an authenticated Experience Cloud user on the live site -- there are claims that
an authenticated session changes the effective permissions, and this repository has not
tested it. Until it does, the executive script keeps the Copilot out of the counterparty
demo.

### Act 6 — The MCP boundary (2 minutes)

**Show**

- `McpServerDefinition:CLMContractTools` exposing `listContracts`, `getContractPackage`, and
  `askContractDocument`.
- `CLM_MCP_Client`, an empty permission set that exists only to gate who may authenticate.

**Explain**

The Box credential never leaves Apex. A client holding an MCP token holds no Box token, and
reads contract content only through the same governed Apex the site uses.

Two constraints worth naming: `McpServerDefinition` is **Metadata API and source-tracking
only** -- not packages, not change sets -- and activation is not in the metadata at all. It is
a `McpServerAccess` Tooling API record whose `DeveloperName` must equal the server's. Without
it a client authenticates and sees no tools.

### Act 7 — Run the gate (1 minute)

```bash
python3 scripts/validate_clm.py
```

Thirteen checks, including a secret and runtime-ID scan across every tracked text file, the
React unit, lint, build, and Playwright suites, and local Markdown link resolution.

## Technical pass criteria

- The UI Bundle builds without a Salesforce org.
- Unit, lint, build, and end-to-end suites pass.
- Browser code contains no client secret; no runtime environment ID is committed.
- The downscoped token is bound to one folder and the parent token is never returned.
- Preview renders with no script request to the Box CDN.
- The counterparty's record access is confirmed by `UserRecordAccess`.
- The agent's inability to scope by identity is stated, not omitted.
- Record creation is **not** claimed to be idempotent.

## References

- [Executive walkthrough](01-executive-walkthrough.md)
- [Box metadata entry-point variation](04-box-metadata-automate-entry.md)
- [Cross-platform agentic orchestration scenario](../README.md)
- [Operator setup and activation](../../../start-here.md)

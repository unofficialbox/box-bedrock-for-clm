# Constraints that will bite you

Compressed from the debugging that found them. Each is a property of Box, Salesforce or
box-ui-elements that this repository has already paid for once, and none of them names
itself when it fails. The blow-by-blow is in `git log`.

## A Box folder needs a *direct* collaboration before it can be downscoped

Inherited access is not enough, and the failure is disguised: `GET /2.0/folders/<id>`
returns 200 with `can_upload = true`, and the token exchange still returns
`{"error":"invalid_resource"}`. You will look at scopes, at the enterprise, at caching —
all fine. The tell is `GET /2.0/folders/<id>/collaborations`: a folder that downscopes
lists `CLM_Box_Config__c.Box_User_Id__c` **directly**.

It is wider than the downscope. The Box for Salesforce Toolkit and the CLM Box app
authenticate as different Box identities, and only the Toolkit's owns what the Toolkit
creates — folders made by calling `box.Toolkit.createFolderForRecordId` directly returned
404 `not_found` to the app *and* to an admin's own Box session.

`ClmBoxFolderService.grantWorkspaceAccess` now makes the `POST /2.0/collaborations` call
immediately after creating the folder and deliberately **before** `commitChanges()` — the
Toolkit has only staged the association at that point, so a callout is still legal, and
would not be after the DML. A 409 counts as success. **Provision through
`ClmBoxFolderService`, or grant the collaboration yourself.**

It is wider still than the downscope and the 404. **Box's metadata search returns only what
the querying user can reach**, so a folder with no collaborators contributes nothing to a
portfolio query while looking entirely healthy: `GET` on it succeeds, its documents list,
their metadata is intact, and the search simply omits them. That presents as indexing lag
and survives any amount of waiting. Check `GET /2.0/folders/<id>/collaborations` before
believing a delay.

## Content Preview: four things must be true at once

Verified live. Any one missing gives a blank frame or the "Sad Box Cloud", and none of
them names itself:

- **`box-annotations` installed and passed as `boxAnnotations`.** ContentPreview expects an
  instance and does not construct one. Pinned `5.2.1-beta.18`; `5.3.0` fails the build.
- **A react-router `Router` above it.** The annotations layer is wrapped in `withRouter`.
  box-ui-elements supplies a router only when a sidebar is mounted, which this view is not,
  so `BoxElements` wraps the preview in its own `MemoryRouter`. This invariant, not CSP,
  was the real cause of the long preview outage.
- **The token passed as a function, not a string.** Preview 3.x asserts
  `typeof annotatorToken === "function"` and the throw aborts the viewer *silently* — empty
  frame, nothing in `onError`.
- **`item_preview` scope**, plus the `CLM_Box_App` (frame-src `*.app.box.com`) and
  `CLM_Box_Content_Delivery` (connect-src `*.boxcloud.com`) trusted sites. Preview fetches
  bytes from a per-request `dl.boxcloud.com` host; only `public.boxcloud.com` is allowed by
  default.

**The renderer is bundled from npm, not fetched from the Box CDN**, because Experience
Cloud sends `script-src 'self'` and `CspTrustedSite` has **no script-src field at all** —
confirmed against both REST and Tooling describes. There is no security-level switch to
flip: an app-container React site cannot be opened in Experience Builder, which is where
that setting lives. `src/lib/boxPreviewRuntime.ts` owns the seam; read its comments before
touching it. `PREVIEW_LIBRARY_VERSION` selects only the **stylesheet** and is pinned to
3.83.0 because that is the newest release the CDN actually serves (3.84/3.85 404 there
even though npm ships them, and the CDN's version list is sparse — probe before bumping).

Content Explorer was dropped: it never emitted a file activation in this embedding, so the
workspace lists the folder itself and owns the row click.

## Every counterparty permission gap fails without saying "permission"

Four grants were needed to get a counterparty to a Box document, and each failed
differently. None of the failures named the missing thing:

| Missing | What you see |
|---|---|
| Field-level security on **any** selected field | UI API rejects the whole query — the list reads as "this counterparty has no contracts" |
| `API Enabled` | Apex REST refuses with a bare 403, while GraphQL keeps working through the site's own bridge |
| Read on `UserExternalCredential` + the `CLM_Box-CLM_Box_Principal` external credential | The endpoint runs and throws `System.CalloutException` |
| A **sharing set** (`CLM_Counterparty_Access`) | Zero rows, with no error |

When a counterparty surface half-works, diff its permission set against
`CLM_Contract_External`, which is the one known to reach Box end to end.

Two verification traps: `CLM_Contract__Share` shows **zero rows** for a community user —
sharing sets compute access rather than materialise shares, so an empty share table is a
false negative; use `UserRecordAccess`. And most of this metadata caps `description` at
**255 characters**.

`Counterparty_Account__c` is the anchor, not the `Counterparty__c` text, which holds both
"Northstar Health" and "Northstar Health System" for one customer.

**Signing in as the counterparty.** Dana Whitfield
(`dana.whitfield@northstarhealth.clm.demo`, Customer Community User on Northstar Health)
exists for this. Two org gates had to open first and neither announces itself:
`CommunitiesSettings.enableOotbProfExtUserOpsEnable` was off, so creating a user on a
standard external profile failed outright; and the site's `networkMemberGroups` listed only
`admin`, so she could not log in even though the user was valid and the sharing set already
granted her records — **a non-member's login failure looks like bad credentials**. Confirm
membership with a `NetworkMember` query rather than by trying to log in.

**"Log in as" is not available for her Customer Community licence**, so she needs a real
password (Setup → Users → Reset Password; the mail goes to the address on the user record,
not yours). The login page is **not** under the app path: `/clm/` serves the React app for
every URL beneath it, so `/clm/login` and `/clm/s/login/` both render the workspace and a
signed-out visitor is never redirected. Sign in at
`https://<your-site>.my.site.com/clmvforcesite/login?startURL=%2Fclm%2F`.

## Guest users enforce field-level security *inside SOQL*

Apex ignores FLS in SOQL for authenticated users but **not for guests**, and it reports a
field the guest cannot read as `No such column '<field>' on entity` — a `QueryException`,
so the whole request 500s naming no field rather than one column coming back blank. Adding
a field to a REST projection therefore breaks the site for signed-out visitors while
working perfectly for an administrator.

`validate_clm.py` now checks offline that every `CLM_Contract__c` field
`ClmContractListService` selects is readable by both permission sets that serve the site.

The mirror-image trap: because Apex does *not* enforce FLS for authenticated users, a field
in the projection reaches the browser whatever the permission set says. `Risk_Level__c` was
withheld from the counterparty and still shipped in the JSON until it was removed from the
projection itself.

## The external agent is scoped by nothing, which is why there isn't one

The workspace runs as the signed-in user, so `ClmCounterpartyContracts` can resolve their
Contact → Account and filter. An **ACC Service Agent runs as its own user**
(`BotDefinition.Type = ExternalCopilot`, `AgentType = EinsteinServiceAgent`), so identity
is not available to it and `UserInfo.getUserId()` is the bot. Its action bindings take the
contract from the conversation, so a counterparty could name another company's contract.
The downscoped token bounds the workspace UI; it does not bound the agent, which reaches
Box through Apex under the app's credentials.

The Copilot was therefore **removed from the counterparty app** rather than scoped. Tests
assert its absence so the decision does not drift back. An **Employee Agent** inherits the
signed-in user's permissions and is the surface where "same agent, different access" holds.

Related: ACC offers no way to pass context to the agent — checked three ways
(`embedAgentforceClient` has no such option, the mounted element exposes no methods, and
`lightning/accApi` is importable only from an LWC). The agent bundle declares `contractId`
and `boxFolderId` variables that nothing on the client can set.

## Agent Script and publishing

- **`subagents:` is not a field on `start_agent`.** A subagent is a top-level block with
  its own `actions:`; routing is `@utils.transition to @subagent.<name>`.
- **`with x = ...` (a literal `...`) lets the model fill an argument.** Binding to a
  variable instead *overrides* the model, and an unset variable is an empty string — which
  surfaces as a platform `REQUIRED_FIELD_MISSING` and a 500, never reaching the class's own
  error handling. This cost two publish cycles.
- **An action output must be declared in `outputs:` before any binding may reference it.**
  That compile check is the only structural verification available: the retrieved
  `agentGraph` JSON serializes no variable bindings, so grepping it proves nothing.
- **Ordering is enforced with guards, not prose.** Told five times to call one action
  first, the planner ignored it; `available when @variables.x == True` fixed it.
- **Nothing reaches the site until a version is activated.** `sf agent publish
  authoring-bundle` then `sf agent activate --version <n>`. Publish outputs land in
  `bots/` and `genAiPlannerBundles/`, both gitignored.
- **When an action never appears in a trace, suspect permissions before prompting** — an
  unavailable action is invisible, not failed. A `TraceFlag` on the agent user named every
  such failure in one line.

## Box metadata is the index, and it must be scoped

`search_files_metadata` over `clmDocument` replaces a folder listing plus a per-file AI
read — but metadata search is **enterprise-wide**, and this enterprise still holds
documents from earlier demo environments with the same file names and different ids.
Unscoped, the query returns files that are not in a contract folder at all. Always pass
`ancestor_folder_id`.

Request metadata inline on a listing as `metadata.enterprise.<templateKey>` — the
shorthand for the caller's own enterprise, so no enterprise id reaches the browser. That is
how the counterparty's redline filter works: it matches on `versionStatus`, not on the file
name, because a redline named `v5-final.pdf` is still a redline. Untagged files are shown —
an unclassified upload is a tagging gap, not a document to hide.

**The tagging is still manual.** A metadata cascade policy on the contract folder is what
would make it survive the next contract.

## Doc Gen and Sign

`ClmGenerateCounterProposal` → `/2.0/docgen_batches`; `ClmSendForSignature` →
`/2.0/sign_requests`. Both go through `ClmBoxAuth`, so an MCP client holds no Box token.
Neither is on the counterparty surface.

- **Doc Gen is versioned**: `box-version: 2025.0` required; Sign wants 2024.0 or no header.
- **Doc Gen is asynchronous**: a 202 means accepted, not written. Poll
  `GET /2.0/docgen_batch_jobs/<id>`.
- **Sign sends.** `is_document_preparation_needed` is false, so Box mails the signer.
  Left true it returns a `prepare_url` and parks a `created` draft that never reaches the
  sent list and notifies nobody. It refuses unless `Status__c` is Approved or Signature.
  All three states verified live.
- **`@InvocableVariable` attributes are space-separated** — `(label='x', required=true)` is
  a parse error with a misleading cascade.
- **`documentIdsFor` returns nothing in a test context** because the Toolkit does, so
  bounded callers can only be tested on their refusal path.
- **`pushFileToBox` appends the extension**, so a `.docx` title becomes `.docx.docx`.

## Hosted MCP metadata is undocumented

`McpServerDefinition` is **not in the Metadata API Developer Guide**. Shape learned from a
deployed example and two org errors: an Apex tool is `aa:apex-<ClassName>` with `apiSource`
`API_CATALOG` and `operation` set to the **class** name (not `apex://ClassName`, which is
what the *agent* bundle uses for the same classes); the developer name is **alphanumeric
only**; only `global` `@InvocableMethod` methods can be exposed. Activation is not in the
metadata at all — it is a `McpServerAccess` Tooling API record whose `DeveloperName` must
equal the server's. It exists from **API v66.0** and is **source-deploy only** (no
packaging, no change sets). **Never retrieve `ExtlClntAppGlobalOauthSettings`** — it brings
back the consumer secret.

## Dependency pins that are load-bearing

- **`.npmrc` sets `legacy-peer-deps=true`.** Without it `npm ci` fails ERESOLVE and four
  validation checks go red. It changes no resolved version.
- **`react-router` must be pinned to `^5.3.4`**, matching `react-router-dom@5`.
  box-ui-elements imports `MemoryRouter`/`Router` from `react-router` directly, so it has to
  be a top-level dependency — and it was pinned to `^7` for a while, putting two
  incompatible majors in one bundle.
- **`o11y` and `o11y_schema` must be declared explicitly.** `@salesforce/platform-sdk`
  imports `o11y/client` without installing it; the build fails to resolve otherwise.
- **box-ui-elements declares 68 peer dependencies.** Almost every unfamiliar entry in
  `package.json` is one of them. Check the peer list before assuming a dep is unused.
- **Never share a CSS class name with box-ui-elements.** Its stylesheets are unscoped and
  load after ours as lazy chunks, so at equal specificity they win: its `.modal-backdrop`
  carries `z-index: -1` and painted our upload dialog behind the page. `styles.test.ts`
  guards this.


## The generate and sign tail of the Automate workflow is specification only

`config/box/automate-workflows.bcl` orders 8 to 10 are designed, not built, and
`seed-clm-contract-files.apex` has never been run against the `agentforce` org. Treat both
as **Portable specification** in the sense [CONVENTIONS.md](CONVENTIONS.md) gives the term.

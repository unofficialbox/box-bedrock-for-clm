# CLM Demo — Agent Handoff

Snapshot of `box-bedrock-for-clm` for an agent picking up this repo cold. Written 2026-08-27, refreshed 2026-08-31. Verify anything time-sensitive against current `git log` / `validate_clm.py` before relying on it.

## 1. What this repo is

A mature Contract Lifecycle Management (CLM) demo built on **Box + Salesforce**. It ships deterministic local fixtures, portable configuration, real-product screenshots, and self-contained presenter HTML. Nothing here requires a live org to validate — "repository mode" is fully green offline; live presenter-readiness is a separate opt-in gate.

**One scenario** since `62f9678`: **Box + Salesforce Contract Lifecycle**. Primary surface is the Salesforce Multi-Framework React app; governed Apex actions are the only path between Box and Salesforce, and humans keep decision authority. The standalone Box Automate scenario was removed, but **Box intake stays** — the metadata-triggered Automate entry point is still how a contract reaches the React workspace, so `config/box/*.bcl`, the 04 entry-point module, the shared Box screenshots, and the `CLM_Box_Automate_Integration` permission set are all retained.

**Governance invariant:** Box is authoritative for contract *content*; Salesforce `CLM_Contract__c` is authoritative for structured *commercial truth*; the Opportunity is the Box-mapped object. Contract bytes never flow to Salesforce. Human gates precede any generation, signature, or Salesforce write.

## 2. Working rules (from project CLAUDE.md — read before acting)

- Work from the Git root; use repository-relative paths in durable files.
- Read `README.md` + **exactly one** persona instruction before exploring: `.claude/personas/{maintainer,operator,use-case-creator}.md`. Don't load the whole doc tree.
- Search with `rg`, open only linked evidence, summarize large outputs.
- **External deploy / publish / share / sign / delete / any live-org mutation requires explicit approval and a confirmed target.** Keep secrets, environment IDs, live record IDs, and machine-specific paths out of committed files.
- Box Sign / signature sends are human-gated — never fired by an agent.

## 3. Current state

- Branch `main`, pushed to `origin`.
- Validation: **14 passed, 0 failed, 1 skipped** (the skip is live receipts, expected in repository mode), **62 Python unit tests OK**, and **60 React tests**. Four of the fourteen checks shell out to the UI bundle, so `npm ci` in `clm-salesforce-project/force-app/main/default/uiBundles/clmreactapp` has to run first.
- **Live Box works end to end against a real folder**, and so do Doc Gen, Box Sign preparation, the MCP server, and the counterparty-scoped workspace.
- The Contract Copilot is an internal surface only. Active version **v16**.

Getting live Box working took two waves of stacked failures, each masking the next, and the
repo no longer narrates them: every constraint they discovered that still governs the code
is in §6, and the commits are in `git log`. The one habit worth carrying forward is why
they were so slow to find — the workspace used to answer *any* Box failure with synthetic
fixtures, so a CORS rejection, a dead endpoint and a crashed component all rendered the
same plausible screen. That fallback is gone; every failure now names itself on the page.

## 4. Config model (important — two formats on purpose)

- **Authored specs = BCL** (`config/**/*.bcl`): HCL2-subset envelope `locals { "bcl" = { resources = [{ "config" = {...} }] } }`. The real payload is `resources[0].config`. Parsed by external Go tooling; also by this repo's `scripts/bcl.py`.
- **Runtime files = JSON** (`config/runtime/*.json`, gitignored): written back by `setup_clm_dev.py` and round-tripped by tooling. Deliberately NOT BCL (no external tool imports them; a BCL emitter would be lossy).
- `scripts/bcl.py` is a **dependency-free** recursive-descent reader (`load_bcl`, `parse_bcl`, `load_artifact`, `BCLError`). `demo_operator.py` dispatches via `load_config()` (`.bcl` → `bcl.load_bcl`, else JSON). Consumers: `demo_operator.py`, `validate_clm.py`.
- Generated per-operator specs land in `config/runtime/generated/` as resolved `.json` (with parallel `.bcl` for the Go side).
- `config/runtime/*.example.json` are the committed templates; the real `demo-environment.json`, `bootstrap-state.json`, `validation-receipts.json`, and `generated/` are gitignored.

## 5. Key paths

| Path | Purpose |
|---|---|
| `scripts/demo_operator.py` | Operator automation: bootstrap, provision, seed, resolve-config, validate, teardown |
| `scripts/validate_clm.py` | The offline validation matrix (secrets, JSON/BCL, links, drift, tests, fixtures, presenters, manifests, idempotency) |
| `scripts/bcl.py` | Dependency-free BCL reader |
| `scripts/setup_clm_dev.py` | One-command dev setup; writes runtime JSON |
| `scripts/generate_sample_contract_assets.py` | reportlab PDFs (incl. executed MSAs) |
| `scripts/generate_docgen_templates.py` | python-docx Doc Gen templates (incl. 2026 redline) |
| `config/box/automate-workflows.bcl` | Intake workflow incl. the Generate Document → Request Signature tail |
| `clm-salesforce-project/.forceignore` | Keeps `node_modules` out of the UI bundle deploy — do not delete |
| `.../classes/ClmBoxTokenService.cls` | Downscoped Box token endpoint; reads the `CLM_Box` external credential |
| `.../externalCredentials/CLM_Box.externalCredential-meta.xml` | Where the Box client id/secret live (encrypted in the org, never in source) |
| `.../objects/CLM_Box_Config__c/` | `Box_User_Id__c` / `Enterprise_Id__c` + `Allowed_Folder_Ids__c` folder allowlist |
| `.../permissionsets/CLM_Box_Preview_Guest.permissionset-meta.xml` | Least-privilege grant letting the site guest user mint a token (MT-042) |
| `clm-salesforce-project/scripts/configure-clm-box-*.sh` | Set the Box credential (MT-038) and CCG subject + folder allowlist (MT-039) |
| `.../clmreactapp/src/components/BoxWorkspace.tsx` | Token, then folder listing; either failure renders `DataError` with the reason, and no fixture stands in |
| `.../clmreactapp/src/components/BoxElements.tsx` | Folder table + lazy Content Preview; needs `react-intl` and `MemoryRouter` providers |
| `.../clmreactapp/src/components/BoxDocumentTable.tsx` | The file table itself — name, modified, size |
| `.../cspTrustedSites/CLM_Box_App.cspTrustedSite-meta.xml` | frame-src grant for `*.app.box.com`, without which the preview frame is blank (MT-043) |
| `.../clmreactapp/vite.live-box.ts` | Dev-only plugin serving a real downscoped token locally (`npm run preview:live`) |
| `.../clmreactapp/src/lib/loaded.ts` | `Loaded<T>` — every remote read returns a value or the reason there is none |
| `.../clmreactapp/src/styles.test.ts` | Guards against sharing a CSS class name with box-ui-elements |
| `.../clmreactapp/.npmrc` | `legacy-peer-deps=true`, without which `npm ci` cannot reproduce the lockfile — do not delete |
| `clm-salesforce-project/sample-data/clm-sample-records.bcl` | Sample Salesforce records (Northstar history) |
| `clm-salesforce-project/scripts/seed-clm-*.apex` / `.sh` | Anonymous-apex seeders (records; per-record Box file uploads) |
| `docs/operator/box-preview-setup.md` | Box app, credential, CORS, folder-id gotcha, error→cause table |
| `docs/maintainers/README.md` | The local live-Box harness: `preview:live` vs `dev:live`, and why |
| `docs/operator/manual-task-register.md` | MT register; MT-036–MT-042 are the live-Box tasks |
| `docs/use-case-creator/production-custom-ui-requirements.md` | Forward-looking spec for a production operator/business UI (aspirational, not built) |
| `tests/` | `test_bcl.py`, `test_demo_operator.py`, `test_validate_clm.py`, presenter/branding/navigation tests |
| `docs/conventions.md` | Readiness vocabulary (4 states) + safety contract |

## 6. Constraints that will bite you

Compressed from the debugging that found them. Each is a property of Box, Salesforce or
box-ui-elements that this repo has already paid for once. The blow-by-blow is in `git log`.

### 6.1 A Box folder needs a *direct* collaboration before it can be downscoped

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

### 6.2 Content Preview: four things must be true at once

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

### 6.3 Every counterparty permission gap fails without saying "permission"

Four grants were needed to get a counterparty to a Box document, and each failed
differently. None of the failures named the missing thing:

| Missing | What you see |
|---|---|
| Field-level security on **any** selected field | UI API rejects the whole query — the list reads as "this counterparty has no contracts" |
| `API Enabled` | Apex REST refuses with a bare 403, while GraphQL keeps working through the site's own bridge |
| Read on `UserExternalCredential` + the `CLM_Box-CLM_Box_Principal` external credential | The endpoint runs and throws `System.CalloutException` |
| A **sharing set** (`CLM_Counterparty_Access`) | Zero rows, with no error |

When a counterparty surface half-works, diff its permission set against
`CLM_Box_Preview_Guest`, which is the one known to reach Box end to end.

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

### 6.4 Guest users enforce field-level security *inside SOQL*

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

### 6.5 The external agent is scoped by nothing, which is why there isn't one

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

### 6.6 Agent Script and publishing

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

### 6.7 Box metadata is the index, and it must be scoped

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

### 6.8 Doc Gen and Sign

`ClmGenerateCounterProposal` → `/2.0/docgen_batches`; `ClmSendForSignature` →
`/2.0/sign_requests`. Both go through `ClmBoxAuth`, so an MCP client holds no Box token.
Neither is on the counterparty surface.

- **Doc Gen is versioned**: `box-version: 2025.0` required; Sign wants 2024.0 or no header.
- **Doc Gen is asynchronous**: a 202 means accepted, not written. Poll
  `GET /2.0/docgen_batch_jobs/<id>`.
- **Sign prepares and does not send.** `is_document_preparation_needed` returns a
  `prepare_url`; no mail leaves. It also refuses unless `Status__c` is Approved or
  Signature. All three states verified live.
- **`@InvocableVariable` attributes are space-separated** — `(label='x', required=true)` is
  a parse error with a misleading cascade.
- **`documentIdsFor` returns nothing in a test context** because the Toolkit does, so
  bounded callers can only be tested on their refusal path.
- **`pushFileToBox` appends the extension**, so a `.docx` title becomes `.docx.docx`.

### 6.9 Hosted MCP metadata is undocumented

`McpServerDefinition` is **not in the Metadata API Developer Guide**. Shape learned from a
deployed example and two org errors: an Apex tool is `aa:apex-<ClassName>` with `apiSource`
`API_CATALOG` and `operation` set to the **class** name (not `apex://ClassName`, which is
what the *agent* bundle uses for the same classes); the developer name is **alphanumeric
only**; only `global` `@InvocableMethod` methods can be exposed. Activation is not in the
metadata at all — it is a `McpServerAccess` Tooling API record whose `DeveloperName` must
equal the server's. It exists from **API v66.0** and is **source-deploy only** (no
packaging, no change sets). **Never retrieve `ExtlClntAppGlobalOauthSettings`** — it brings
back the consumer secret.

### 6.10 Dependency pins that are load-bearing

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

## 7. What is still open

1. **MT-045 — guest sharing decision.** `CLM_Contract__c` is Private/Private and the
   Experience Cloud guest has no record access. The endpoint returns `200 []` for a
   signed-out visitor, correctly. Granting a guest sharing rule would make contract records
   readable by anyone who can open the site: a deliberate exposure, not a bug to fix.
2. **MT-040 — per-user Box OAuth** (optional production hardening). The `CLM_Box` auth
   provider is committed with placeholder credentials so the path is scaffolded.
3. **`ClmBoxAuth` has 0 of 47 lines covered.** Fine in a dev org; blocks any production
   deploy or packaging.
4. **MT-072 — workspace screenshots are stale.** `clm-react-workspace.png` is marked
   `readiness = "real-demo"` but predates the folder table, Content Preview and the charts.
   `validate_clm.py` checks the manifest structurally and cannot detect this.
5. **The generate/sign tail of the Automate workflow is spec-only.**
   `config/box/automate-workflows.bcl` orders 8–10 are designed, not built.
   `seed-clm-contract-files.apex` has never been run against the `agentforce` org.
6. **`production-custom-ui-requirements.md` predates the scenario reduction.** It frames
   Mode A / Mode B as parallel runtime modes. Treat it as a wish-list.
7. **Sibling-repo propagation is deferred.** Self-contained per-repo prompts are at
   `../propagation-prompts/*.md`; background in `../BCL-CLEANUP-PROPAGATION.md`. Don't
   start unless asked.
8. **No live-org state in commits.** Any org mutation needs explicit approval and a
   confirmed target, and is the user's call to fire.

## 8. How to verify you're in a good state

```bash
npm ci --prefix clm-salesforce-project/force-app/main/default/uiBundles/clmreactapp
python3 scripts/validate_clm.py            # expect 14 passed / 0 failed / 1 skipped
python3 -m unittest discover -s tests -p 'test_*.py'   # expect 62 tests OK
```

Requires Python 3.11+ (`validate_clm.py` imports `datetime.UTC`). The `npm ci` is not optional
on a fresh clone: four of the thirteen checks are React lint/test/build/Playwright, and they
fail closed without `node_modules`.

If validation is red, the first suspects are: a BCL file that doesn't parse (`scripts/bcl.py`), a stale set-comparison contract in `validate_clm.py` (`EXPECTED_SCENARIOS`, `EXPECTED_PRESENTERS`, screenshot/PDF/docx manifests), a runtime JSON drifted from its `.example`, or a new Markdown file with a relative link that doesn't resolve — `check_local_links` walks every non-excluded `.md` in the tree, tracked or not.

One failure mode is worth naming because it only appears on a **fresh** clone or worktree: `.gitattributes` normalizes text to LF, so anything a generator writes with CRLF reads back as `Deterministic fixture drift` even though the content is identical. A checkout that predates the generator keeps its CRLF copy on disk and passes, which is why this can be green locally and red everywhere else. Writers must pin LF explicitly — see `write_csv` in `scripts/generate_sample_contract_assets.py`.

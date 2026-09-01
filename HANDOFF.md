# CLM Demo — Agent Handoff

Snapshot of `box-bedrock-for-clm` for an agent picking up this repo cold. Written 2026-08-27, refreshed 2026-08-31. Verify anything time-sensitive against current `git log` / `validate_clm.py` before relying on it.

## 1. What this repo is

A mature Contract Lifecycle Management (CLM) demo built on **Box + Salesforce + Databricks + Amazon Bedrock AgentCore**. It ships deterministic local fixtures, portable configuration, real-product screenshots, and self-contained presenter HTML. Nothing here requires a live org to validate — "repository mode" is fully green offline; live presenter-readiness is a separate opt-in gate.

**One scenario** since `62f9678`: **Cross-Platform Agentic Orchestration**. Primary surface is the Salesforce Multi-Framework React app; Amazon Bedrock AgentCore coordinates Box, Agentforce, and Databricks specialists while humans keep decision authority. The standalone Box Automate scenario was removed, but **Box intake stays** — the metadata-triggered Automate entry point is still how a contract reaches the React workspace, so `config/box/*.bcl`, the 04 entry-point module, the shared Box screenshots, and the `CLM_Box_Automate_Integration` permission set are all retained.

**Governance invariant:** Box is authoritative for contract *content*; Salesforce `CLM_Contract__c` is authoritative for structured *commercial truth*; the Opportunity is the Box-mapped object. Contract bytes never flow to Salesforce. Human gates precede any generation, signature, or Salesforce write.

## 2. Working rules (from project CLAUDE.md — read before acting)

- Work from the Git root; use repository-relative paths in durable files.
- Read `README.md` + **exactly one** persona instruction before exploring: `.claude/personas/{maintainer,operator,use-case-creator}.md`. Don't load the whole doc tree.
- Search with `rg`, open only linked evidence, summarize large outputs.
- **External deploy / publish / share / sign / delete / any live-org mutation requires explicit approval and a confirmed target.** Keep secrets, environment IDs, live record IDs, and machine-specific paths out of committed files.
- Box Sign / signature sends are human-gated — never fired by an agent.

## 3. Current state

- Branch `main`, pushed to `origin`. **No open PRs and no open issues.**
- Validation: **13 passed, 0 failed, 1 skipped** (the skip is live receipts, expected in repository mode) and **62 Python unit tests OK**. Four of the thirteen checks shell out to the UI bundle, so `npm ci` in `clm-salesforce-project/force-app/main/default/uiBundles/clmreactapp` has to run first.
- **Live Box works end to end and has been verified against a real folder.** That was this repo's longest-standing untested claim; it took two waves.

### Wave 1 — the preview scaffolding (through `9b18a35`)

- `62f9678` reduced the demo to the cross-platform scenario; presenter chapters renumbered 00–07, and the counts `validate_clm.py` used to assert are now derived from `EXPECTED_PRESENTERS` and the discovered manifests instead of bare numbers.
- `c2f6861` added `.forceignore` so the UI bundle actually deploys (the `UIBundle` type packages its whole directory, `node_modules` included, which blew the 50 MB Metadata API request limit).
- `38d954d` added the downscoped Box token endpoint (`ClmBoxTokenService`) and the live preview path in `BoxWorkspace.tsx`.
- `0d4668c` moved Box credentials into a Salesforce **external credential**, so no Box secret exists in Apex, metadata, or source control.
- `354d677` recorded the credential model: Client Credentials Grant is the demo default (one-time admin setup, no per-user consent screen); the `CLM_Box` auth provider is committed with placeholder consumer credentials so per-user OAuth is scaffolded for production rather than rediscovered.
- `cf3b54a` vendored Box Content Preview 2.106.0 into the bundle. **Superseded — reverted in wave 2**; it vendored the entry file rather than the distribution and never worked in any environment. The CSP finding it recorded still holds: the Experience Cloud `script-src` omits `cdn01.boxcdn.net` and `CspTrustedSite` has no field that can grant `script-src`, so a CDN path is not available.
- `9b18a35` added the Box preview setup guide as step 8 of the operator run order.

### Wave 2 — making it actually work (PRs #31–#38, 2026-08-28)

Nothing in wave 1 had ever run against Box. Every layer failed, each one masking the next, because the workspace falls back to synthetic fixtures on *any* Box failure — a CORS rejection, a dead endpoint, and a crashed component all rendered the same screen.

- **#31, #32** scripted the `CLM_Box_Config__c` org default (MT-039) and recorded the Multi-Framework feature gate as MT-041.
- **#33, #35** embedded Content Explorer and Content Uploader, granted the token as a user rather than the service account, and moved credential setup into `configure-clm-box-credential.sh` (MT-038), dropping the Basic username/password.
- **#36** — *the token endpoint had never once succeeded.* `DOWNSCOPE_SCOPE` was a comma-separated list and Box reads that as one scope name. OAuth 2.0 separates scopes with spaces. Each scope was individually valid, so the failure only appeared when more than one was requested. A unit test now pins the delimiter.
- **#37** fixed three more stacked defects: the vendored Content Preview was incomplete and is now removed entirely; `box-ui-elements` needs a `react-intl` provider or `ContentExplorer` takes the React tree with it; and Apex REST discards the body of some status codes, so a 502 reached the caller as `INTERNAL_SERVER_ERROR` with the real cause lost — upstream failures now return 500 with the cause in the body. Added the `CLM_Box_Preview_Guest` permission set (MT-042): the workspace calls the endpoint from the browser, so the request runs as the Experience Cloud **site guest user**, which had been granted nothing. Both Box failure paths now log.
- **#38** added a local live-Box harness. `npm run preview:live` serves a real downscoped token at the Apex path via a dev-only Vite plugin, minted through the Salesforce CLI as the current user and held in memory only. Live defects no longer need a deploy cycle to diagnose. See `docs/maintainers/README.md`.

Wave 2 also **retired both concessions** wave 1's vendoring forced: `validate_clm.py` no longer exempts directories named `vendor` from the secret scan, and eslint no longer ignores `src/vendor`. `BoxElements` is lazy-loaded, dropping the entry chunk from ~3 MB to 236 KB.

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
| `.../clmreactapp/src/components/BoxWorkspace.tsx` | Live branch (token + folder listing) with synthetic-fixture fallback; both failure paths log |
| `.../clmreactapp/src/components/BoxElements.tsx` | Folder table + lazy Content Preview; needs `react-intl` and `MemoryRouter` providers |
| `.../clmreactapp/src/components/BoxDocumentTable.tsx` | The file table itself — name, modified, size |
| `.../clmreactapp/src/components/BoxDocumentPreview.tsx` | Inline document preview: Box's expiring embed URL in an iframe, no preview library |
| `.../cspTrustedSites/CLM_Box_App.cspTrustedSite-meta.xml` | frame-src grant for `*.app.box.com`, without which the preview frame is blank (MT-043) |
| `.../clmreactapp/vite.live-box.ts` | Dev-only plugin serving a real downscoped token locally (`npm run preview:live`) |
| `.../clmreactapp/.npmrc` | `legacy-peer-deps=true`, without which `npm ci` cannot reproduce the lockfile — do not delete |
| `clm-salesforce-project/sample-data/clm-sample-records.bcl` | Sample Salesforce records (Northstar history) |
| `clm-salesforce-project/scripts/seed-clm-*.apex` / `.sh` | Anonymous-apex seeders (records; per-record Box file uploads) |
| `docs/operator/box-preview-setup.md` | Box app, credential, CORS, folder-id gotcha, error→cause table |
| `docs/maintainers/README.md` | The local live-Box harness: `preview:live` vs `dev:live`, and why |
| `docs/operator/manual-task-register.md` | MT register; MT-036–MT-042 are the live-Box tasks |
| `docs/use-case-creator/production-custom-ui-requirements.md` | Forward-looking spec for a production operator/business UI (aspirational, not built) |
| `tests/` | `test_bcl.py`, `test_demo_operator.py`, `test_validate_clm.py`, presenter/branding/navigation tests |
| `docs/conventions.md` | Readiness vocabulary (4 states) + safety contract |

## 6. Open threads / caveats

1. **Live Box is verified; MT-036–MT-039, MT-041, and MT-042 are effectively done.** **MT-043** (the `CLM_Box_App` trusted site that lets the preview iframe render) was deployed to the `agentforce` org on 2026-08-31 and verified: `https://*.app.box.com`, active, frame-src true — the wildcard is accepted, so no tenant subdomain is hardcoded. Any other environment still needs it. Worth noting the org itself confirms the constraint this design works around: querying `IsApplicableToScriptSrc` on `CspTrustedSite` fails with "No such column". `http://localhost:4173` was added to the Box app's CORS domains on 2026-08-31, so the local harness reaches live Box. Otherwise only **MT-040** remains (optional: move to per-user Box OAuth for production hardening). If preview breaks in a new environment, check the CORS domains on the Box app first — the browser calls `api.box.com` directly, so a missing origin fails the folder listing and the workspace silently falls back to fixtures. Check the browser console: both failure paths log now.
2. **The contract dashboard needs a sharing decision before it shows real data.**
   `ClmContractListService` works — verified as an admin against the org, returning 13
   records through its fixed projection — but `CLM_Contract__c` is Private/Private and
   Salesforce's guest-user hardening means the endpoint's `without sharing` query does
   not give the Experience Cloud guest record access. Object and field read are granted
   on `CLM_Box_Preview_Guest`; what is missing is a **guest user sharing rule**, and
   creating one makes contract records readable by unauthenticated visitors. That is a
   deliberate exposure, tracked as **MT-045**, not a bug to fix. Until it exists the
   dashboard renders its synthetic fixture and says so.
3. **Folder-id gotcha.** The workspace still defaults to the non-numeric string `demo-workspace` (`src/config.ts`), which the endpoint rejects as `invalid_folder_id` before any Box call. Pass `?folderId=` or rebuild with `VITE_BOX_FOLDER_ID`; locally, `CLM_BOX_FOLDER_ID` for `preview:live`.
4. **Document preview works, and it is not the Content Explorer.** The workspace lists
   the governed folder itself (`BoxWorkspace` already fetched that listing to decide live
   vs fixtures) and renders it as a plain table; clicking a row mounts
   `box-ui-elements/es/elements/content-preview` on that file id. Verified against live
   Box on 2026-08-31 through the local harness, in both the dev server and the production
   bundle: a 7-page redline renders.

   Four things had to be true at once before it rendered at all, each independently a
   blocker:
   - **`box-annotations` must be installed and an instance passed as `boxAnnotations`.**
     ContentPreview expects one and does not construct it. Pinned to `5.2.1-beta.18`;
     `5.3.0` fails the build (`parseMessageMarkdown` is not exported).
   - **The preview needs a react-router `Router` above it.** The annotations layer is
     wrapped in `withRouter`, so without one React throws `Invariant failed: You should
     not use <withRouter(WithAnnotations(Component)) /> outside a <Router>` and the
     error boundary paints the "Sad Box Cloud". box-ui-elements supplies a router only
     when a sidebar is mounted, which this view does not use, so `BoxElements` wraps the
     preview in its own `MemoryRouter` (memory history — the workspace owns the URL).
     This invariant, not CSP, was the real cause of the long-running preview failure.
   - **The token must be passed as a function, not a string.** ContentPreview forwards
     its `token` prop straight through as preview's `annotatorToken`, and Box Content
     Preview 3.x asserts `typeof annotatorToken === "function"` or throws
     `Bad annotatorToken!`. That throw aborts the viewer silently: an empty frame, no
     error UI, nothing in `onError`. `BoxElements` memoizes a `() => token` provider.
     (3.0.0 has no such assertion, which is why the element's own default appeared to
     work and every newer version did not.)
   - **`item_preview` scope** on the downscoped token, and the `CLM_Box_App` frame-src
     trusted site.

   **Version is pinned to 3.83.0** (`PREVIEW_LIBRARY_VERSION` in `BoxElements.tsx`).
   box-ui-elements defaults to **3.0.0**, years stale. 3.83.0 is the newest release on
   `cdn01.boxcdn.net/platform/preview/` — the npm package reaches 3.85.0 and its README
   documents that exact CDN URL, but 3.84.0 and 3.85.0 both 404 there. The CDN's version
   list is sparse (3.80–3.82 are absent, 3.83.0 is present), so probe before bumping.

   **The renderer is bundled from npm, not fetched from the Box CDN.** ContentPreview
   normally injects `<script src="cdn01.boxcdn.net/platform/preview/<version>/en-US/
   preview.js">`. On an Experience Cloud site that script never loads: the page sends
   `script-src 'self' …` and `CspTrustedSite` has **no script-src directive at all** --
   verified against both the REST and Tooling describes at the org's API version, which
   expose only connect/frame/img/style/font/media. That asymmetry is visible in the live
   header: the Box trusted sites reach style-src, media-src, font-src, connect-src and
   frame-src, and only script-src is missing them. There is also no security-level switch
   to flip -- this is an app-container React site, and the org refuses to open it in
   Experience Builder ("You can't edit this site in Experience Builder because it's based
   on the React framework"), which is where the Strict/Relaxed CSP setting lives.

   So `box-content-preview@3.85.0` is a dependency and the bundler puts it on the page.
   `src/lib/boxPreviewRuntime.ts` owns that seam:
   - It assigns `global.Box.Preview` **unconditionally**. Importing the package already
     registers the plain `Preview` there as a side effect, so a "only if missing" guard
     silently keeps that one and drops everything below.
   - It installs a `BundledPreview` subclass rather than passing props, because a bundled
     copy cannot infer two things and one of them cannot travel as a prop. `location:
     { staticBaseURI }` is the package's documented npm-consumer hook -- without it
     preview requests `undefinedexif/exif.min.js` -- but `location` is also the prop
     react-router's `withRouter` injects into the annotations wrapper, which overwrites
     it before ContentPreview ever sees it. `pdfjs: { workerSrc }` rides along.
   - `vite.box-preview-assets.ts` serves the side-car assets from `assets/box-preview/`:
     copied into `dist` on build, served out of `node_modules` in dev and `vite preview`.
     Only `exif/` is copied. pdf.js is bundled into the npm build (unlike the CDN build,
     which pulls it from `third-party/doc/`), and the rest are for viewers this workspace
     does not use -- `third-party/` is 20MB of Shaka players and 3D geometry, `cmaps/` is
     1.6MB of CJK encodings across ~330 files that would become ~330 more components on
     every UI bundle deploy. A CJK PDF would lose its glyph mapping; nothing else does.
   - `previewLibraryVersion` now selects **only the stylesheet**. `loadScript` is
     short-circuited but `loadStylesheet` has no such guard and always appends a `<link>`,
     and style-src does allow the Box CDN. It is pinned to 3.83.0 because that is the
     newest release the CDN actually serves; the matching 3.85.0 stylesheet is bundled
     too, so preview stays styled if the CDN is unreachable.

   **One trusted site had to be added.** `CLM_Box_Content_Delivery`
   (`https://*.boxcloud.com`, connect-src) -- preview fetches the file bytes from a
   per-request `dl.boxcloud.com` host, and only `public.boxcloud.com` is allowed by
   default, so the renderer would load and then fail on connect-src.

   Verified on the deployed site on 2026-08-31: a 7-page redline renders, zero requests
   to `cdn01.boxcdn.net` for script, and no failed resource requests.

   **Content Explorer was dropped for this.** It never emitted a file activation in this
   embedding: `ItemList` fires only when `type === FOLDER || !isTouch && (type === WEBLINK
   || canPreview)`, and the element stayed in its small/touch layout regardless of
   container width, so a file click went nowhere however `canPreview` was set. Folder
   clicks worked, which is why the coupling was easy to miss until a file was clicked
   against live Box. Owning the row click removes the guesswork. The npm package
   `box-content-preview` remains unusable and unused — it declares peers on React 18 and
   box-ui-elements 20 (this app is React 19 and 27), and its `dist/lib` is a bundler input
   with unresolved bare specifiers rather than the standalone artifact the CDN serves.
5. **The Contract Copilot cannot be told which contract is on screen.** ACC offers no way
   to pass context, and this was checked three ways rather than assumed:
   `embedAgentforceClient` takes no context or variables option (`container`,
   `salesforceOrigin`, `appId`, `frontdoorUrl`, `sitePrefix`, `agentforceClientConfig`,
   `onError`, `onReady` — that is the whole surface); the mounted
   `runtime_copilot-acc-sdk-wrapper` element exposes no methods, only the Lightning Out
   proxy's `_uuid`/`_ready`/`configuration`; and the `open`/`close`/`execute` API is the
   `lightning/accApi` module, importable only from an LWC running inside Lightning, which
   a UI-bundle React app is not. The agent bundle does declare `contractId`,
   `contractRecordId` and `boxFolderId` as variables — nothing on this side can set them.
   Hence **"Copy agent context"** in the top bar: the person pastes what the client cannot
   send. `AgentforcePanel` puts the contract reference in `agentLabel` and
   `messageInputPlaceholderText`, which is the only contract awareness available.


   **The agent now has actions, which it previously did not.** Its Agent Script carried
   instructions and nothing else, so it could only promise to "gather the details" and
   then answer from nothing -- a conversation would loop through several turns of
   clarifying questions and never retrieve a thing. Two actions fix that, on the
   `contract_review` start agent and a `document_answers` subagent:
   - `get_contract_package` -> `apex://ClmContractPackage`. Resolves a contract from the
     reference a person typed (or its name, or a record id), finds the governed Box folder,
     and lists every document **with its Box file ID**. Nothing else supplies those ids,
     and the Box AI action addresses a file by id, so without this the agent had no way to
     read anything.
   - `ask_box_ai` -> `apex://box__BoxAIAskByItemId`, the Box for Salesforce managed-package
     invocable. No custom Box AI code is needed.

   Two Agent Script details cost a compile cycle each and are easy to get wrong:
   `subagents:` is not a field on `start_agent` -- a subagent is a top-level block that
   also declares its own `actions:`, and routing between them is
   `@utils.transition to @subagent.<name>`. And `with x = ...` (a literal `...`) is what
   lets the model fill an argument from the conversation; binding it to a variable instead
   ignores the reference the person just typed. `@utils.setVariables` is how a reference
   gets captured into a variable in the first place.

   `ClmContractPackage` lists through `box.Toolkit.getFolderContents(folderId)`, which
   returns `box.Folder` with `List<box.Entry>` and needs no `commitChanges()`. The Toolkit
   already holds the org's Box credentials, so the action needs no token grant and no named
   credential of its own. It reads `box__FRUP__c` with SOQL rather than using the Toolkit's
   folder lookup, because the provisioning call beside that one commits DML and Apex forbids
   a callout after DML.

   **The agent answers end to end, verified in the Agentforce Builder preview on
   2026-09-01.** "Summarize the insurance certificate for CLM-SAMPLE-NST-2024: dollar
   amounts and expiration dates" returns the three coverages with their limits and
   2027-06-30 expiries, citing `northstar-insurance-certificate.pdf`, in one turn. The
   trace reads Contract Router -> document answers -> get contract package -> ask box ai ->
   GROUNDED. Test it there (Studio -> Agents -> Contract Copilot -> Preview), not in the
   workspace: the ACC composer sits behind a closed shadow root and no browser tool can
   type into it, and `sf agent preview` needs a TTY and crashes rendering.

   Getting there took five distinct blockers, and only the first is about prompting:

   - **The planner ignored prose ordering.** Told five times to call get_contract_package
     first, it called ask_box_ai five times instead. What fixed it was
     `available when @variables.contractPackageLoaded == True` on the ask_box_ai binding --
     a hard guard, so the wrong order is not offered. Interpolating
     `{!@variables.contractPackage}` into the instructions actively hurt: the agent read
     the empty variable as fact and reported "the package has no visible document listing".
   - **The agent user could not execute the Apex.** `ClmContractPackage` was granted to
     System Administrator only, so the action was never *offered* to the planner -- it was
     never attempted and never failed, which reads exactly like the model choosing not to
     use it. `CLM_Contract_Agent` grants it.
   - **Then it found no contract.** The agent owns none and CLM_Contract__c is
     Private/Private, so the read returned nothing and the reply was "I could not find that
     contract" -- a permission boundary wearing the costume of a bad reference. Fixed with
     `viewAllRecords` on that one object.
   - **Then `box__FRUP__c` threw.** Apex raises "sObject type box__FRUP__c is not
     supported" when the user cannot see a managed-package object. Granted, and the lookup
     now catches so a gap costs the folder rather than the answer.
   - **Then Box AI 401'd.** `box__BoxAIAskByItemId` authenticates as the *Salesforce user*,
     and an agent user has no linked Box account -- an authorization error nobody can act
     on. Replaced with `ClmBoxAskDocument`, which calls `/2.0/ai/ask` with the same Client
     Credentials Grant the workspace already uses. That needed two more grants the error
     messages name precisely: the `CLM_Box-CLM_Box_Principal` external credential, and read
     on `UserExternalCredential`.

   When an action never appears in the trace at all, suspect permissions before prompting:
   an unavailable action is invisible, not failed. The Apex debug log on the agent user
   (`TraceFlag` on 005NS00000ybncIYAQ) named every one of these in a single line.

   **Version 1 is still the Active version**, so the workspace continues to serve the
   original agent -- the one with no actions and the stale `CLM-2026-0017` welcome. Every
   publish creates a new numbered bundle (`CLM_Contract_Copilot_N`) and a new project
   version; none of it reaches the site until a version is activated. That is why
   republishing appeared to change nothing there for so long.

   Both Apex legs were also verified directly against the live org and live Box:
6. **A Box folder needs a *direct* collaboration before it can be downscoped.** Inherited
   access is not enough, and the failure is badly disguised: `GET /2.0/folders/<id>`
   returns 200 with `permissions.can_upload = true`, and the token exchange still comes
   back `{"error":"invalid_resource"}`. Reading that error you will look at scopes, at the
   enterprise, at token caching -- all of which are fine.

   The tell is `GET /2.0/folders/<id>/collaborations`. A folder that downscopes has the
   configured Box user (`CLM_Box_Config__c.Box_User_Id__c`) listed on it *directly*; one
   that does not, does not. Northstar's folder carried `385982796:editor` from a manual
   grant made months ago. Calder's, freshly provisioned by
   `box.Toolkit.createFolderForRecordId`, carried only the owner's own collaboration and
   inherited the rest -- and no amount of collaborating the parent `CLM Root` changes it.

   **It is wider than the downscope, and wider than the REST endpoint.** Seeding the two
   Calder precedent contracts on 2026-09-01 hit it again from a different direction. Calling
   `box.Toolkit.createFolderForRecordId` directly -- rather than through
   `ClmBoxFolderService`, which grants the collaboration -- produced folders that *nothing*
   else could read: `ClmBoxAuth.parentToken()` returned 404 `not_found` on the files inside,
   and so did an admin's own Box session. The Toolkit and the CLM Box app authenticate as
   different Box identities, and only the Toolkit's owns what the Toolkit creates. One
   `POST /2.0/collaborations` granting `Box_User_Id__c` editor on each folder fixed every
   symptom at once. If you provision a folder any way other than through
   `ClmBoxFolderService`, grant that collaboration yourself.

   **This affects every contract whose folder the package provisions.** The workspace
   requests `item_upload item_delete item_rename item_share`, so the token mint fails
   outright and the panel falls back to fixtures. It has gone unnoticed only because the
   demo has always pointed at Northstar. Until `ClmBoxFolderService` grants the
   collaboration itself, provisioning a contract folder is a two-step operation:

   ```
   POST /2.0/collaborations
   {"item":{"id":"<folderId>","type":"folder"},
    "accessible_by":{"id":"<Box_User_Id__c>","type":"user"},"role":"editor"}
   ```

   **Fixed on 2026-09-01.** `ClmBoxFolderService.grantWorkspaceAccess` now makes that call
   immediately after `createFolderForRecordId`, and deliberately *before* the `finally`
   block runs `commitChanges()`: the Toolkit has only staged the association at that point,
   so a callout is still legal, and would not be once the DML has run. A 409 is treated as
   success -- the grant is already there. With no `Box_User_Id__c` configured the grant is
   skipped, because an enterprise subject already owns what it creates.

   End-to-end check, on a contract created for the purpose and then deleted: provision
   through the endpoint, then mint a workspace token, with no manual Box step in between.
   Both succeeded.

7. **The internal persona reaches Salesforce over MCP, and the metadata is half-undocumented.**
   `McpServerDefinition:CLMContractTools` exposes the two governed actions --
   `ClmContractPackage` and `ClmBoxAskDocument` -- as MCP tools, so Claude Desktop reads
   contract content through the same Apex the Experience Cloud agent uses. The Box
   credential never leaves Apex: a client holding an MCP token holds no Box token.

   Hosted MCP Servers are GA (April 2026). `McpServerDefinition` is **not in the Metadata
   API Developer Guide** -- no reference page, no field table -- so the shape below came
   from a deployed example and two org errors:
   - An Apex tool is `aa:apex-<ClassName>` with `apiSource` `API_CATALOG` and `operation`
     set to the **class** name. It is not `apex://ClassName`, which is what the agent
     authoring bundle uses for the very same classes.
   - `description` and `descriptionOverride` cap at **255 characters**.
   - The server's developer name is **alphanumeric only** -- no underscores, 2-40 chars.
     `CLM_Contract_Tools` is rejected; `CLMContractTools` is not. Every other API name in
     this repo uses underscores, so this one reads like a typo and is not.
   - Only `global` methods annotated `@InvocableMethod` can be exposed.

   Activation is not in the metadata. It is a `McpServerAccess` Tooling API record whose
   `DeveloperName` **must equal the server's**, with `Active = true` and `McpServerId`
   pointing at the definition. Without it a client authenticates and sees no tools.

   The client side is four metadata types deployed together --
   `ExternalClientApplication`, `ExtlClntAppOauthSettings`,
   `ExtlClntAppGlobalOauthSettings`, `ExtlClntAppOauthConfigurablePolicies` -- as
   `CLM_Claude_MCP`. Scopes are spelled `MCP, RefreshToken` in metadata and shown as
   `mcp_api` / `refresh_token` in Setup. The callback is Claude's:
   `https://claude.ai/api/mcp/auth_callback`. `CLM_MCP_Client` is an empty permission set
   that exists only to gate who may authenticate, since the default is any user in the org.

   **Never retrieve `ExtlClntAppGlobalOauthSettings` into the repo.** A retrieve brings back
   `consumerKey` and `consumerSecret`; the committed file is authored and holds neither.

   Two constraints for anyone propagating this: `McpServerDefinition` exists from **API
   v66.0** and the Metadata Coverage Report marks it **Metadata API and source tracking
   only** -- not unlocked packages, not 2GP or 1GP, not change sets. It has to be deployed
   as source. And there is **no named user permission** for hosted MCP; Salesforce's own
   guidance is to author an empty permission set and use it for pre-authorization, which is
   what `CLM_MCP_Client` is. The endpoint format is confirmed by the connection-issues
   page: `.../mcp/v1/custom/<Name>` for a Developer or Enterprise org, and
   `.../mcp/v1/sandbox/custom/<Name>` for a sandbox or scratch org.

8. **Box metadata is the index; listing a folder is the fallback.** The enterprise already
   carries `clmContract`, `clmDocument`, `clmClause`, `clmObligation` and `clmRedlineReview`
   templates (scope `enterprise_5105484`). `clmDocument` was applied by hand on 2026-09-01
   to all nine Northstar documents and the Calder draft, which is what makes
   `search_files_metadata` usable:

   ```
   from: enterprise_5105484.clmDocument
   query: clauseRisk = :risk        params: {risk: Critical}
   -> northstar-msa-redline-v4.pdf, calder-msa-customer-paper-v2.pdf
   ```

   One query, across two contracts on two different papers, replacing a folder listing plus
   nine Box AI reads. `documentType` (MSA, DPA, SOW, Order Form, Security Exhibit,
   Insurance, Approval Memo) makes "find the insurance certificate" deterministic instead of
   a filename guess.

   **The tagging is manual and will not survive the next contract.** `clmContract` is not
   applied to the folders at all yet, so contract-level facts -- `contractRecordId`,
   `noticeDeadline`, `riskLevel` -- cannot be searched. A metadata cascade policy on the
   folder is what would give every document its contract's facts by inheritance, and that
   is the piece that turns a portfolio question into a single query.

9. **The external persona is not scoped through the agent, only through the UI -- and the
   reason is the agent type.** The
   Experience Cloud workspace and the Contract Copilot are governed differently, and the
   difference is not a choice:

   - The **workspace** runs as the signed-in Experience Cloud user, so identity is
     available. `ClmCounterpartyContracts` resolves that user's Contact, takes its Account,
     and returns only contracts whose `Counterparty_Account__c` matches. It has no usable
     reference input: naming somebody else's contract returns a refusal that does not even
     leak the contract's name.
   - The **ACC agent** runs as its own user -- `access.default_agent_user` in the authoring
     bundle -- not as the person typing. That is not a guess: the agent's actions returned
     "could not find that contract" until `CLM_Contract_Agent` granted **the agent user**
     View All. Had they run as the signed-in admin they would have worked immediately.

     The org names the type: `BotDefinition.Type = ExternalCopilot`,
     `AgentType = EinsteinServiceAgent`, `BotUserId = 005NS00000ybncIYAQ`. A **Service Agent**
     runs as that bot user. An **Employee Agent** does the opposite -- it inherits the
     permissions of the logged-in user, and its `default_agent_user` is optional. So this is a
     property of the agent type, not a limit of Agentforce, and an internal Employee Agent is
     the surface on which "same agent, different access" would hold.

     One edge is **untested**: what a Service Agent does for an *authenticated* Experience
     Cloud user on the live site. The evidence above comes from the Agentforce Builder
     preview, where there is no site user at all. There are claims that an authenticated
     session changes the effective permissions; do not repeat them until this repo tests it.

   So an identity-scoped action is useless inside the agent: `UserInfo.getUserId()` is the
   agent, whose Contact is null. And the agent's `get_contract_package` binding is
   `with inputContract = ...`, meaning the model fills it from the conversation. **A
   counterparty in the portal can therefore ask the Copilot about another company's
   contract by naming it.** The downscoped Box token bounds the workspace UI to one folder;
   it does not bound the agent, which reaches Box through Apex under the app's credentials.

   This is the ACC context limitation from thread 5 wearing a different hat: the client
   cannot pass identity any more than it can pass a record. Until it can, the external agent
   is demo-grade and should be described that way. The workspace itself is defensible.

   `Counterparty_Account__c` is the anchor rather than the `Counterparty__c` text, which
   holds both "Northstar Health" and "Northstar Health System" for one customer -- matching
   on it would show a counterparty half their contracts.

   **Record visibility comes from a sharing set, and it is deployed.**
   `CLM_Counterparty_Access` maps `CLM_Contract__c.Counterparty_Account__c` to the signed-in
   user's `Contact.Account` with Read for the Customer Community User profile. Verified on
   2026-09-01 via `UserRecordAccess` for Dana: read on all four Northstar contracts, no
   access to Calder or Acme Cloudworks. That boundary is the platform's, not the Apex
   filter's -- which means it holds even if someone queries the object directly.

   Two things to know when checking this. `CLM_Contract__Share` shows **zero rows** for a
   community user: sharing sets compute access rather than materialise share records, so an
   empty share table is a false negative. `UserRecordAccess` is the honest check. And the
   sharing set's `description` caps at 255 characters, like most of this metadata.

   **The permission set still withholds `viewAllRecords`.** `CLM_Counterparty_Portal` grants object
   read and the class, deliberately not `viewAllRecords` -- a Customer Community user with
   View All could query every contract straight through the REST API with their own session,
   which is the hole this class exists to close. A Customer Community licence reaches its own
   account's rows through a **sharing set** on `CLM_Contract__c` keyed to
   `Counterparty_Account__c`, configured under Digital Experiences settings. Without it the
   action returns "no contracts on file" for a real portal user. The tests pin the bound
   account rather than granting View All, because a test that grants the permission the
   class exists to avoid proves nothing.

   Dana Whitfield (`dana.whitfield@northstarhealth.clm.demo`, Customer Community User on
   Northstar Health) exists for this. Two org-level gates had to open before she was usable,
   and neither announces itself:

   - `CommunitiesSettings.enableOotbProfExtUserOpsEnable` was off, so creating a user on a
     standard external profile failed outright.
   - The site's `networkMemberGroups` listed only the `admin` profile, so she could not log
     in even though the user was valid and active and the sharing set already granted her
     records. **A non-member's login failure looks like bad credentials**, which sends you
     hunting for a password problem that does not exist. `Customer Community User` is now a
     member group; confirm with a `NetworkMember` query rather than by trying to log in.

   To see the site as her, use **Log in as** from her user record in Setup. She has no
   password, and setting one is not needed to test.

10. **One dependency concession.** `clmreactapp/.npmrc` sets `legacy-peer-deps=true`. `box-ui-elements@27` pins `@box/activity-feed@^2.3.12`, but `activity-feed@2.4.2` declares peer `@box/user-selector@^3.0.0` while the tree resolves `2.2.23`. The committed lockfile already encodes that resolution, so without the `.npmrc` a clean `npm ci` fails ERESOLVE and four validation checks go red. It changes no resolved version. (The two *vendoring* concessions this section used to record — the `vendor` secret-scan exemption and the eslint ignore — were retired when the vendored preview was removed.)
11. **Generate/sign tail is spec-only.** `config/box/automate-workflows.bcl` (see the note near line 44) states orders 8–10 (Human Confirmation → Generate Document → Request Signature) are **added to the design, not built or verified in the live Automate workflow**. No live signer email is stored. `clm-salesforce-project/scripts/seed-clm-contract-files.apex` (per-record Box file uploads) exists but has **not been run against the `agentforce` org** — the user runs live seed/upload/deploy themselves.
12. **Workspace screenshots are stale.** `output/screenshots/cross-platform-agentic-orchestration/clm-react-workspace.png` is marked `readiness = "real-demo"` but was captured **2026-07-14**, before the workspace gained its folder table and working Content Preview. `validate_clm.py` checks the manifest structurally and cannot detect this. Recapture per **MT-072**.
13. **`production-custom-ui-requirements.md` predates the scenario reduction.** It still frames Mode A (Box-centric) and Mode B (cross-platform) as parallel runtime modes. Treat it as a requirements wish-list, not a description of what exists.
14. **Sibling-repo propagation is deferred to separate sessions.** The plan: propagate CLM's Tier-1 cleanup (gitignore hardening, validate-robustness set comparisons, doc/persona alignment) to the other demos. Siblings stay pure JSON (BCL is opt-in). Copy-paste, self-contained per-repo prompts already exist at the **workspace root**: `../propagation-prompts/*.md` (one per repo + `README.md` index), with background in `../BCL-CLEANUP-PROPAGATION.md`. DAM is greenfield (not git-init'd) and needs a scope decision first. Don't start propagation unless the user asks.
15. **No live-org state in commits.** Any request touching the org (deploy static resources, run seeders, send a signature) needs explicit approval + confirmed target and is the user's call to fire.

## 7. How to verify you're in a good state

```bash
npm ci --prefix clm-salesforce-project/force-app/main/default/uiBundles/clmreactapp
python3 scripts/validate_clm.py            # expect 13 passed / 0 failed / 1 skipped
python3 -m unittest discover -s tests -p 'test_*.py'   # expect 62 tests OK
```

Requires Python 3.11+ (`validate_clm.py` imports `datetime.UTC`). The `npm ci` is not optional
on a fresh clone: four of the thirteen checks are React lint/test/build/Playwright, and they
fail closed without `node_modules`.

If validation is red, the first suspects are: a BCL file that doesn't parse (`scripts/bcl.py`), a stale set-comparison contract in `validate_clm.py` (`EXPECTED_SCENARIOS`, `EXPECTED_PRESENTERS`, screenshot/PDF/docx manifests), a runtime JSON drifted from its `.example`, or a new Markdown file with a relative link that doesn't resolve — `check_local_links` walks every non-excluded `.md` in the tree, tracked or not.

One failure mode is worth naming because it only appears on a **fresh** clone or worktree: `.gitattributes` normalizes text to LF, so anything a generator writes with CRLF reads back as `Deterministic fixture drift` even though the content is identical. A checkout that predates the generator keeps its CRLF copy on disk and passes, which is why this can be green locally and red everywhere else. Writers must pin LF explicitly — see `write_csv` in `scripts/generate_sample_contract_assets.py`.

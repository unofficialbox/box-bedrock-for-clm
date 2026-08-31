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
| `.../clmreactapp/src/components/BoxElements.tsx` | Lazy-loaded Content Explorer + Content Uploader; needs a `react-intl` provider |
| `.../clmreactapp/src/components/BoxDocumentPreview.tsx` | Inline document preview: Box's expiring embed URL in an iframe, no preview library |
| ... opened from the toolbar picker in `BoxElements.tsx` | ContentExplorer will not emit a file click unless its own broken preview is enabled — see thread 3 |
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

1. **Live Box is verified; MT-036–MT-039, MT-041, and MT-042 are effectively done.** Newly required is **MT-043**, the `CLM_Box_App` trusted site that lets the preview iframe render; it is committed but not deployed. `http://localhost:4173` was added to the Box app's CORS domains on 2026-08-31, so the local harness reaches live Box. Otherwise only **MT-040** remains (optional: move to per-user Box OAuth for production hardening). If preview breaks in a new environment, check the CORS domains on the Box app first — the browser calls `api.box.com` directly, so a missing origin fails the folder listing and the workspace silently falls back to fixtures. Check the browser console: both failure paths log now.
2. **Folder-id gotcha.** The workspace still defaults to the non-numeric string `demo-workspace` (`src/config.ts`), which the endpoint rejects as `invalid_folder_id` before any Box call. Pass `?folderId=` or rebuild with `VITE_BOX_FOLDER_ID`; locally, `CLM_BOX_FOLDER_ID` for `preview:live`.
3. **Document preview deliberately avoids the Box Content Preview library.** The npm
   package `box-content-preview` cannot be used here: it declares peers on React 18 and
   box-ui-elements 20 (this app is React 19 and 27), requires `box-annotations` which is
   not installed, and its `dist/lib` is a bundler input with unresolved bare specifiers
   rather than the standalone artifact the CDN serves — importing it in the browser
   fails on `box-ui-elements/es/utils/keys`. Self-hosting it is a dead end, the same wall
   cf3b54a hit from a different side. The workspace requests `expiring_embed_link`
   instead and frames Box's own rendering, which needs only `item_preview` scope
   (already granted) and a frame-src trusted site.

   **The trigger cannot live on an explorer row.** `ContentExplorer` delegates rows to
   `ItemList`, whose handler is `if (type === FOLDER || !isTouch && (type === WEBLINK ||
   canPreview)) onItemClick(item)` — a file click is emitted only when `canPreview` is
   on, and turning it on also mounts the built-in preview dialog, which has no library
   to load and renders a "Sad Box Cloud" error over the workspace. No prop separates
   the two. So `canPreview` stays `false` and the preview is opened from a picker in the
   toolbar, fed by `onNavigate` so it lists the folder currently on screen. Folder
   navigation still works because folders short-circuit that condition — which is why
   the coupling is easy to miss until a file is clicked against live Box.
4. **One dependency concession.** `clmreactapp/.npmrc` sets `legacy-peer-deps=true`. `box-ui-elements@27` pins `@box/activity-feed@^2.3.12`, but `activity-feed@2.4.2` declares peer `@box/user-selector@^3.0.0` while the tree resolves `2.2.23`. The committed lockfile already encodes that resolution, so without the `.npmrc` a clean `npm ci` fails ERESOLVE and four validation checks go red. It changes no resolved version. (The two *vendoring* concessions this section used to record — the `vendor` secret-scan exemption and the eslint ignore — were retired when the vendored preview was removed.)
5. **Generate/sign tail is spec-only.** `config/box/automate-workflows.bcl` (see the note near line 44) states orders 8–10 (Human Confirmation → Generate Document → Request Signature) are **added to the design, not built or verified in the live Automate workflow**. No live signer email is stored. `clm-salesforce-project/scripts/seed-clm-contract-files.apex` (per-record Box file uploads) exists but has **not been run against the `agentforce` org** — the user runs live seed/upload/deploy themselves.
6. **Workspace screenshots are stale.** `output/screenshots/cross-platform-agentic-orchestration/clm-react-workspace.png` is marked `readiness = "real-demo"` but was captured **2026-07-14**, before PR #37 replaced the hand-rolled file rail and preview mount with Content Explorer. `validate_clm.py` checks the manifest structurally and cannot detect this. Recapture per **MT-072**.
7. **`production-custom-ui-requirements.md` predates the scenario reduction.** It still frames Mode A (Box-centric) and Mode B (cross-platform) as parallel runtime modes. Treat it as a requirements wish-list, not a description of what exists.
8. **Sibling-repo propagation is deferred to separate sessions.** The plan: propagate CLM's Tier-1 cleanup (gitignore hardening, validate-robustness set comparisons, doc/persona alignment) to the other demos. Siblings stay pure JSON (BCL is opt-in). Copy-paste, self-contained per-repo prompts already exist at the **workspace root**: `../propagation-prompts/*.md` (one per repo + `README.md` index), with background in `../BCL-CLEANUP-PROPAGATION.md`. DAM is greenfield (not git-init'd) and needs a scope decision first. Don't start propagation unless the user asks.
9. **No live-org state in commits.** Any request touching the org (deploy static resources, run seeders, send a signature) needs explicit approval + confirmed target and is the user's call to fire.

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

# CLM Demo — Agent Handoff

Snapshot of `box-bedrock-for-clm` for an agent picking up this repo cold. Written 2026-08-27. Verify anything time-sensitive against current `git log` / `validate_clm.py` before relying on it.

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

- Branch `main`, pushed to `origin`. Validation as last recorded by the commits below: **13 passed, 0 failed, 1 skipped** (the skip is live receipts, expected in repository mode) and **62 unit tests OK**.
- The last work stream was **live Box preview inside the React workspace**, landed across seven commits:
  - `62f9678` reduced the demo to the cross-platform scenario; presenter chapters renumbered 00–07, and the counts `validate_clm.py` used to assert are now derived from `EXPECTED_PRESENTERS` and the discovered manifests instead of bare numbers.
  - `c2f6861` added `.forceignore` so the UI bundle actually deploys (the `UIBundle` type packages its whole directory, `node_modules` included, which blew the 50 MB Metadata API request limit).
  - `38d954d` added the downscoped Box token endpoint (`ClmBoxTokenService`) and the live preview path in `BoxWorkspace.tsx`.
  - `0d4668c` moved Box credentials into a Salesforce **external credential**, so no Box secret exists in Apex, metadata, or source control.
  - `354d677` recorded the credential model: Client Credentials Grant is the demo default (one-time admin setup, no per-user consent screen); the `CLM_Box` auth provider is committed with placeholder consumer credentials so per-user OAuth is scaffolded for production rather than rediscovered.
  - `cf3b54a` vendored Box Content Preview 2.106.0 into the bundle. The CDN path could never work: the Experience Cloud CSP `script-src` omits `cdn01.boxcdn.net`, and `CspTrustedSite` has no field that can grant `script-src`. Serving from `'self'` does work. Bundle goes ~248 KB → 1.3 MB.
  - `9b18a35` added the Box preview setup guide as step 8 of the operator run order.

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
| `.../objects/CLM_Box_Config__c/` | `Enterprise_Id__c` + `Allowed_Folder_Ids__c` folder allowlist |
| `.../clmreactapp/src/vendor/box-preview/` | Vendored Box Content Preview 2.106.0 (served from `'self'`) |
| `.../clmreactapp/src/components/BoxWorkspace.tsx` | Live preview with synthetic-fixture fallback |
| `clm-salesforce-project/sample-data/clm-sample-records.bcl` | Sample Salesforce records (Northstar history) |
| `clm-salesforce-project/scripts/seed-clm-*.apex` / `.sh` | Anonymous-apex seeders (records; per-record Box file uploads) |
| `docs/operator/box-preview-setup.md` | Box app, credential, CORS, folder-id gotcha, error→cause table |
| `docs/operator/manual-task-register.md` | MT register; MT-036–MT-040 are the live-Box tasks |
| `docs/use-case-creator/production-custom-ui-requirements.md` | Forward-looking spec for a production operator/business UI (aspirational, not built) |
| `tests/` | `test_bcl.py`, `test_demo_operator.py`, `test_validate_clm.py`, presenter/branding/navigation tests |
| `docs/conventions.md` | Readiness vocabulary (4 states) + safety contract |

## 6. Open threads / caveats

1. **Live Box preview is untested end to end.** No Box credentials exist yet, so the token exchange and an actual document render have never run. Tracked as **MT-037** (create the Client Credentials Grant app and authorize it in the Box Admin Console), **MT-038** (set client id/secret on the `CLM_Box` external credential), **MT-039** (enterprise id + folder allowlist on `CLM_Box_Config__c`), **MT-040** (optional move to per-user OAuth for production). **MT-036** is the Salesforce origin in the Box app's CORS domains — the browser calls `api.box.com` directly, so without it preview fails.
2. **Folder-id gotcha.** The workspace defaults to the non-numeric string `demo-workspace`, which the endpoint rejects as `invalid_folder_id` before any Box call. Pass `?folderId=` or rebuild with `VITE_BOX_FOLDER_ID`.
3. **Two narrow concessions from vendoring the preview:** eslint ignores `src/vendor/**`, and `validate_clm.py` adds `vendor` to `EXCLUDED_PARTS` because minified third-party output trips the committed-password heuristic. Any directory named `vendor` is now exempt from the secret scan, same as `node_modules`.
4. **Generate/sign tail is spec-only.** `config/box/automate-workflows.bcl` (see the note near line 44) states orders 8–10 (Human Confirmation → Generate Document → Request Signature) are **added to the design, not built or verified in the live Automate workflow**. No live signer email is stored. `clm-salesforce-project/scripts/seed-clm-contract-files.apex` (per-record Box file uploads) exists but has **not been run against the `agentforce` org** — the user runs live seed/upload/deploy themselves.
5. **`production-custom-ui-requirements.md` predates the scenario reduction.** It still frames Mode A (Box-centric) and Mode B (cross-platform) as parallel runtime modes. Treat it as a requirements wish-list, not a description of what exists.
6. **Sibling-repo propagation is deferred to separate sessions.** The plan: propagate CLM's Tier-1 cleanup (gitignore hardening, validate-robustness set comparisons, doc/persona alignment) to the other demos. Siblings stay pure JSON (BCL is opt-in). Copy-paste, self-contained per-repo prompts already exist at the **workspace root**: `../propagation-prompts/*.md` (one per repo + `README.md` index), with background in `../BCL-CLEANUP-PROPAGATION.md`. DAM is greenfield (not git-init'd) and needs a scope decision first. Don't start propagation unless the user asks.
7. **No live-org state in commits.** Any request touching the org (deploy static resources, run seeders, send a signature) needs explicit approval + confirmed target and is the user's call to fire.

## 7. How to verify you're in a good state

```bash
python3 scripts/validate_clm.py            # expect 13 passed / 0 failed / 1 skipped
python3 -m unittest discover -s tests -p 'test_*.py'
```

Requires Python 3.11+ (`validate_clm.py` imports `datetime.UTC`).

If validation is red, the first suspects are: a BCL file that doesn't parse (`scripts/bcl.py`), a stale set-comparison contract in `validate_clm.py` (`EXPECTED_SCENARIOS`, `EXPECTED_PRESENTERS`, screenshot/PDF/docx manifests), a runtime JSON drifted from its `.example`, or a new Markdown file with a relative link that doesn't resolve — `check_local_links` walks every non-excluded `.md` in the tree, tracked or not.

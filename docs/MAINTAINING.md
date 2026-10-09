# Maintaining the repository

Use this path when changing code, configuration, tests, documentation structure, generated artifacts, or release state.

## Source-of-truth order

1. `AGENTS.md` and the selected assistant persona
2. `README.md` and `docs/README.md`
3. Machine-readable contracts under `config/`
4. Source Markdown under `docs/` and `sample-data/`
5. Generators under `scripts/`
6. Tests under `tests/`

Files under `output/` and rendered `docs/diagrams/*.svg` are derived evidence. Update their source and regenerate them instead of editing them directly.

## Maintainer workflow

1. Confirm the Git root, branch, remote, and working-tree state.
2. Read only the source contract, nearest documentation, generator, and tests relevant to the change.
3. Update configuration and Markdown sources before derived output.
4. Preserve Box content authority, Salesforce structured authority, citations, human decision gates, external-ID idempotency, dry-run/apply separation, target confirmation, partial-failure reconciliation, and owned-resource reset evidence.
5. Run the narrowest relevant tests first.
6. Regenerate affected fixtures, diagrams, screenshots indexes, or presenter HTML.
7. Run `python3 scripts/validate_clm.py` without skip flags.
8. Review the diff for secrets, live IDs, absolute local paths, stale readiness claims, and unexplained generated drift.
9. Commit one coherent change and open a pull request.

## Testing the live Box workspace locally

The Box token endpoint is Apex, so it does not exist off-platform: by default a local run
can only ever exercise the failure path, where the workspace reports that it could not
mint a token. `--mode live` closes that gap by serving a **real** downscoped token at the
Apex path, minted through the Salesforce CLI as the current user and held in memory only.

```bash
cd clm-salesforce-project/force-app/main/default/uiBundles/clmreactapp
export CLM_BOX_FOLDER_ID=<box-folder-id>   # required
export CLM_ORG_ALIAS=agentforce            # optional, this is the default
npm run preview:live
```

Add the localhost origin (for example `http://localhost:4173`) to the Box application's
**CORS Domains**. The browser calls `api.box.com` directly, so Box rejects the folder
listing without it, and the workspace reports the rejection with Box's own
`cors_origin_not_whitelisted` in the message.

**Use `preview:live`, not `dev:live`, for anything involving Box UI Elements.**
`preview:live` builds and serves the production bundle; `dev:live` runs the Vite dev
server, where a box-ui-elements dependency throws `Dynamic require of "react" is not
supported` from esbuild's CJS interop and the elements never mount. The two also diverge
in ways that matter: a broken vendored Content Preview reproduced only in the production
bundle. `dev:live` remains useful for the rest of the app, where hot reload is worth more.

This exists because the Box paths cannot be exercised at all without a real token, and a
deploy cycle per attempt is slow. The workspace no longer hides a failure -- a CORS
rejection, a dead token endpoint and a refused folder each name themselves on screen --
but seeing them locally still beats reading them out of a deployed org. Check the message
on the page and the browser console before assuming the demo simply
has no content.

## Release readiness

Repository release evidence requires:

- all persona entry points and local links resolve;
- configuration and schemas validate;
- Mermaid sources match their SVG renders;
- deterministic fixtures and presenter HTML regenerate cleanly;
- screenshot manifests describe current real-product evidence;
- React tests, lint, build, and Playwright pass;
- Python tests pass;
- no secret, live environment identifier, or machine-specific absolute path is committed.

`python3 scripts/validate_clm.py --presenter-ready` is a separate live gate requiring current secret-free receipts for Box and Salesforce. Repository tests never substitute for those receipts.

## Current maturity boundary

The repository provides **Portable specification** and **Local deterministic fixture** evidence for both scenarios. A capability is a **Deployed integration** only when current receipts prove the named target. The complete cross-platform scenario is **Presenter-ready live** only when all platform receipts, screenshots, reset evidence, and presenter rehearsal are current.

## Historical decisions retained

- CLM is a mature vertical implementation, not the reusable neutral template.
- The two orchestration scenarios remain separate and share governed CLM assets without sharing runtime claims.
- Box owns governed contract content; Salesforce `CLM_Contract__c` owns structured commercial truth.
- Standard Salesforce external-ID upsert and lookup is the default intake path. Custom Apex is reserved for genuinely custom multi-record, authorization, routing, lifecycle-event, or downscoped-token behavior.
- Portable Markdown remains authoritative; self-contained HTML remains a derived sharing layer.

## Forward priority

Run the Box + Salesforce Contract Lifecycle path in confirmed target environments and populate `config/runtime/validation-receipts.json`. That is the remaining evidence boundary for full presenter readiness.

## Verifying a clean state

```bash
npm ci --prefix clm-salesforce-project/force-app/main/default/uiBundles/clmreactapp
python3 scripts/validate_clm.py            # expect 15 passed / 0 failed / 1 skipped
python3 -m unittest discover -s tests -p 'test_*.py'   # expect 72 tests OK
```

Requires Python 3.11+ (`validate_clm.py` imports `datetime.UTC`). The `npm ci` is not optional
on a fresh clone: four of the fifteen checks are React lint/test/build/Playwright, and they
fail closed without `node_modules`.

If validation is red, the first suspects are: a BCL file that doesn't parse (`scripts/bcl.py`), a stale set-comparison contract in `validate_clm.py` (`EXPECTED_SCENARIOS`, `EXPECTED_PRESENTERS`, screenshot/PDF/docx manifests), a runtime JSON drifted from its `.example`, or a new Markdown file with a relative link that doesn't resolve — `check_local_links` walks every non-excluded `.md` in the tree, tracked or not.

One failure mode is worth naming because it only appears on a **fresh** clone or worktree: `.gitattributes` normalizes text to LF, so anything a generator writes with CRLF reads back as `Deterministic fixture drift` even though the content is identical. A checkout that predates the generator keeps its CRLF copy on disk and passes, which is why this can be green locally and red everywhere else. Writers must pin LF explicitly — see `write_csv` in `scripts/generate_sample_contract_assets.py`.

# Repository Maintainer

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

`python3 scripts/validate_clm.py --presenter-ready` is a separate live gate requiring current secret-free receipts for Box, Salesforce, AgentCore, and Databricks. Repository tests never substitute for those receipts.

## Current maturity boundary

The repository provides **Portable specification** and **Local deterministic fixture** evidence for both scenarios. A capability is a **Deployed integration** only when current receipts prove the named target. The complete cross-platform scenario is **Presenter-ready live** only when all platform receipts, screenshots, reset evidence, and presenter rehearsal are current.

## Historical decisions retained

- CLM is a mature vertical implementation, not the reusable neutral template.
- The two orchestration scenarios remain separate and share governed CLM assets without sharing runtime claims.
- Box owns governed contract content; Salesforce `CLM_Contract__c` owns structured commercial truth.
- Standard Salesforce external-ID upsert and lookup is the default intake path. Custom Apex is reserved for genuinely custom multi-record, authorization, routing, lifecycle-event, or downscoped-token behavior.
- Portable Markdown remains authoritative; self-contained HTML remains a derived sharing layer.
- Managed AgentCore and Databricks evidence must remain disclosed as local or illustrative until current deployed receipts exist.

## Forward priority

Run the Cross-Platform Agentic Orchestration path in confirmed target environments and populate `config/runtime/validation-receipts.json`. That is the remaining evidence boundary for full presenter readiness.

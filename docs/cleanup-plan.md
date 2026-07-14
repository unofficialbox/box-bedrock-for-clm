# CLM Repository Cleanup Plan

## Goal

Keep the Governed Workflow and Agentic Orchestration presenter packages obvious while preserving shared live Box identifiers.

## Recommended Target Structure

```text
box-agentforce-clm-demo/
├── README.md
├── app/                         # current clm-react-app
├── demo/
│   ├── runbook.md
│   ├── scripts/
│   ├── flow.mmd
│   ├── flow.svg
│   └── manifest.json
├── box/
│   ├── live.json                # only canonical live Box IDs and URLs
│   ├── app/
│   ├── automate/
│   ├── content-model/
│   ├── docgen/
│   └── hub/
├── sample-data/
│   ├── source/
│   └── clauses/
├── artifacts/                   # generated and reproducible outputs
│   ├── documents/
│   ├── screenshots/
│   └── experience-gallery.html
├── experiments/
│   └── agentcore/               # Agentic Orchestration runtime assets
├── docs/
│   ├── architecture.md
│   ├── controls.md
│   ├── references.md
│   ├── roi.md
│   └── competitive-landscape.md
└── scripts/
```

## Consolidation Recommendations

### 1. Keep AgentCore bounded to Agentic Orchestration

Move the following into `experiments/agentcore/` as one bounded unit:

- `config/agentcore/`
- `docs/02-agent-definitions.md`
- `docs/runbooks/03-agentcore-demo.md`
- `docs/diagrams/clm-agentcore-architecture.*`
- `scripts/run_agentcore_mock.py`
- `output/agentcore/`
- AgentCore-only analytics fixtures after confirming they are not used by the React demo

The scenario index now provides this boundary without hiding AgentCore as an unowned experiment.

### 2. Consolidate Presenter Material

Complete for the core presenter path. Each scenario now has one ordered guide containing architecture, flow, script, screenshots, readiness, and setup. The numbered `04-` runbook and audience scripts under `docs/scenarios/agentic-orchestration/supporting-react-scripts/` remain optional deep dives rather than required navigation.

Keep shared diagrams, screenshots, galleries, runbooks, and JSON manifests single-source; scenario guides should embed or reference them rather than create copies.

### 3. Organize Box Configuration by Product Surface

Split the current flat `config/box/` directory into product-oriented folders:

- `app/`: blueprint, build checklist, live dashboard spec
- `automate/`: workflow, Extract prompts, AI Agent specs, HTTPS connector
- `content-model/`: metadata templates and folder template
- `docgen/`: template data
- `hub/`: Hub blueprint

Keep `live-box-surface.json` at the Box root and treat it as the only source of live IDs and URLs. Other manifests should reference it rather than repeat mutable IDs where possible.

### 4. Separate Sources from Generated Artifacts

Keep authored clause Markdown and generator inputs under `sample-data/`. Move generated PDFs, DOCX files, screenshots, JSON traces, and the gallery under `artifacts/`.

Use one command to rebuild generated artifacts and document which files are intentionally checked in.

### 5. Archive One-Time Operational Notes

Move these out of the main project root after their work is complete:

- `anz-box-cleanup-inventory.md`
- `box-web-ui-build-queue.md`
- temporary Doc Gen screenshots under `.tmp/`

Recommended destination: `docs/archive/2026-07-box-build/`.

### 6. Remove Local Noise

Delete `.DS_Store`, Python `__pycache__`, obsolete `*-draft` screenshots, and the gallery QA screenshot after confirming the live replacements. Add repo-level ignore rules so they do not return.

### 7. Rename the Repository Last

The current `box-bedrock-for-clm` name now accommodates both tracks. Defer any repository rename until the managed Agentic Orchestration runtime is deployed and the long-term product emphasis is clear.

Renaming should be the final step because it affects scripts, local links, Salesforce project references, and any future Git remote.

## Suggested Execution Order

1. Remove local noise and obsolete screenshots.
2. Move AgentCore into `experiments/agentcore/`.
3. Consolidate presenter material under `demo/`.
4. Reorganize Box configuration by surface.
5. Separate generated artifacts from source data.
6. Archive completed operational notes.
7. Update links, run verification, then rename the repository if desired.

## Guardrails

- Do not change live Box IDs or URLs during file moves.
- Keep `config/box/live-box-surface.json` readable until every consumer is migrated.
- Use mechanical moves with link validation; do not combine them with React behavior changes.
- Run JSON validation, React unit tests, production build, and E2E tests after each phase.

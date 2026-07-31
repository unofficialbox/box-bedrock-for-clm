# CLM Scripts

> **Status: transitional. A cleanup is planned.** Read the two sections below before adding to or depending on anything here.

## The boundary this directory has not yet been sorted against

This repository is a **golden copy** of the finished CLM scenario. Machinery that *creates* that copy belongs elsewhere — the Box surface authoring tooling already moved to `unofficialbox/box-capture`.

`scripts/` predates that rule and still mixes both kinds. Roughly:

| Kind | Scripts | Belongs |
|---|---|---|
| **Golden-copy verification** — proves the committed artifact is internally consistent | `validate_clm.py` | Here |
| **Golden-copy generation** — builds committed presenter and diagram assets | the `build_*.py` family, `generate_*.py` | Here, arguably; they produce tracked output |
| **Environment provisioning** — creates or mutates live Box and Salesforce state | `demo_operator.py`, `setup_clm_dev.py` | Elsewhere, by the rule above |

Nothing has been moved on this basis yet. Do not treat the current layout as a decision.

## Config formats: authored BCL, runtime JSON

Authored spec config under `config/` is `.bcl` — BCL is the only supported admin-facing import format, and the canonical inventory matches what `box-dispatch` reads in `internal/bcl`. `scripts/bcl.py` is a dependency-free reader that parses the `locals { "bcl" = { … } }` envelope and returns the `resources[0].config` payload. `demo_operator.py` and `validate_clm.py` load authored config through it (`load_config` dispatches `.bcl` → BCL, `.json` → JSON).

The `config/runtime/*` files are the exception and stay JSON: they are per-operator, gitignored, and round-tripped by the tooling (`setup_clm_dev.py` writes `demo-environment.json`, `demo_operator.py` writes `bootstrap-state.json`, and `resolve-config` emits resolved specs as JSON under `config/runtime/generated/`). Only the `*.example.json` templates are committed. No external tool imports these runtime files, so BCL would add a lossy emitter for no gain.

## Available scripts

| Script | Purpose |
|--------|---------|
| `validate_clm.py` | Run the complete repository matrix or fail-closed presenter-readiness validation from one command |
| `demo_operator.py` | Check prerequisites, generate assets, create the Box foundation, deploy portable Salesforce metadata, and validate a new environment |
| `setup_clm_dev.py` | Install repository dependencies and optionally sync Box/Salesforce context into `config/runtime/demo-environment.json` |
| `bcl.py` | Dependency-free reader for authored `.bcl` config artifacts; returns the config payload from the `locals.bcl` envelope |
| `build_clm_experience_gallery.py` | Build separate self-contained Box Automate Agentic Orchestration and Cross-Platform Agentic Orchestration galleries from their scenario screenshot directories |
| `build_scenario_guides.py` | Build complete portable scenario guides with embedded assets and full-size diagram dialogs |
| `build_executive_marketecture.py` | Build the self-contained executive marketecture with business outcomes, platform roles, phased delivery, and real-demo proof |
| `build_presenter_portal.py` | Build the presenter landing page plus a single self-contained edition that embeds all nine standalone chapters |
| `build_agentcore_primary_marketecture.py` | Build the coordinated contract-work variation across Box, Salesforce Agentforce, Databricks, specialized agents, and accountable teams |
| `build_customer_datasheet.py` | Build the nontechnical Box Solutions datasheet for generalists, sales teams, customers, and IT decision makers |
| `build_contract_lifecycle_readiness_marketecture.py` | Build the lifecycle swimlane marketecture showing persistent platform responsibilities and human decision authority |
| `generate_sample_contract_assets.py` | Create synthetic MSA, DPA, SOW, order form, exhibits, JSON records, and analytics CSV |
| `generate_docgen_templates.py` | Create Box DocGen-ready Word templates for approval memo, order summary, and renewal notice |

For a fresh environment, start with:

```bash
cp config/runtime/demo-environment.example.json config/runtime/demo-environment.json
python3 scripts/demo_operator.py doctor
```

For repository verification, run the setup script (it also installs all dependency prerequisites):

```bash
python3 scripts/setup_clm_dev.py
python3 scripts/validate_clm.py
```

You can enable CLI context capture in setup:

```bash
python3 scripts/setup_clm_dev.py --automated --from-current-clis --pet off
```

Run a safe pre-flight check before full setup:

```bash
python3 scripts/setup_clm_dev.py --smoke
```

Use `--skip-react` only for a narrow Python/content diagnostic. Use `--skip-playwright` only when browser binaries are unavailable and report the omitted gate. For a live presenter-readiness decision, populate the gitignored receipt file from `config/runtime/validation-receipts.example.json` and run `python3 scripts/validate_clm.py --presenter-ready`.

The operator command sequence is:

```bash
python3 scripts/demo_operator.py generate-assets
python3 scripts/demo_operator.py box-foundation --dry-run
python3 scripts/demo_operator.py box-foundation
python3 scripts/demo_operator.py seed-metadata --dry-run
python3 scripts/demo_operator.py seed-metadata
python3 scripts/demo_operator.py salesforce-deploy --dry-run
python3 scripts/demo_operator.py salesforce-deploy
python3 scripts/demo_operator.py resolve-config --allow-unresolved
# Complete browser/admin configuration and record published URLs.
python3 scripts/demo_operator.py resolve-config
python3 scripts/demo_operator.py validate --scenario box-automate-agentic-orchestration
```

For a clean single-shot operator flow that checks and creates what is missing:

```bash
python3 scripts/demo_operator.py bootstrap --scenario box-automate-agentic-orchestration --dry-run
python3 scripts/demo_operator.py bootstrap --scenario box-automate-agentic-orchestration --yes
python3 scripts/demo_operator.py status --scenario box-automate-agentic-orchestration
```

`provision` remains as a legacy alias for backward compatibility.

Use `--offline` with `doctor` or `validate` only for repository/CI checks. Normal operator runs perform read-only verification against the configured Box enterprise and Salesforce org.

Run the sample asset generator from the CLM demo root:

```bash
python3 scripts/generate_sample_contract_assets.py
```

Generate the DocGen templates from the CLM demo root:

```bash
python3 scripts/generate_docgen_templates.py
```

The generated `.docx` files are written to `output/docgen/`. Sample merge data is in `config/box/docgen-template-data.bcl`.

Rebuild both screenshot galleries from the CLM demo root:

```bash
python3 scripts/build_clm_experience_gallery.py
```

Rebuild the complete portable guides:

```bash
python3 scripts/build_scenario_guides.py
```

Rebuild the executive marketecture:

```bash
python3 scripts/build_executive_marketecture.py
```

Build the coordinated contract-work variation:

```bash
python3 scripts/build_agentcore_primary_marketecture.py
```

Build the customer-facing Box Solutions datasheet:

```bash
python3 scripts/build_customer_datasheet.py
```

Build the contract lifecycle contribution marketecture:

```bash
python3 scripts/build_contract_lifecycle_readiness_marketecture.py
```

Build the presenter landing page and complete embedded edition after the nine standalone chapters exist:

```bash
python3 scripts/build_presenter_portal.py
```

Review outputs in this order:

- `output/html/index.html` — landing page and table of contents for the presenter library.

1. `output/html/00-operator-setup-guide.html` — fresh-environment setup and validation.
2. `output/html/01-box-automate-agentic-orchestration-guide.html` — complete narrative.
3. `output/html/02-box-automate-agentic-orchestration-gallery.html` — visual-only companion.
4. `output/html/03-cross-platform-agentic-orchestration-guide.html` — complete narrative.
5. `output/html/04-cross-platform-agentic-orchestration-gallery.html` — visual-only companion.
6. `output/html/05-executive-marketecture.html` — executive marketecture for IT and business decision makers.
7. `output/html/06-agentcore-agent-experience-marketecture.html` — coordinated contract work across content, business data, analytics, and accountable teams.
8. `output/html/07-customer-solution-datasheet.html` — high-level customer and sales datasheet focused on experience and outcomes.
9. `output/html/08-contract-lifecycle-readiness-marketecture.html` — executive lifecycle view showing how each platform contributes from intake through lifecycle management.

For one-file sharing, use `output/html/09-complete-presenter-edition.html`. It embeds all nine chapters and supports desktop navigation, a mobile chapter picker, previous/next controls, and `Alt` + arrow-key navigation.

Guide diagrams and screenshots open in a full-size dialog. All eleven files remain portable with no external assets; the combined edition has no sibling-file dependency.

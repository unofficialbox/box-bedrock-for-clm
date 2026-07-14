# CLM Scripts

This directory is reserved for helper scripts.

Available scripts:

| Script | Purpose |
|--------|---------|
| `demo_operator.py` | Check prerequisites, generate assets, create the Box foundation, deploy portable Salesforce metadata, and validate a new environment |
| `build_clm_experience_gallery.py` | Build separate self-contained Governed Workflow and Agentic Orchestration galleries from their scenario screenshot directories |
| `build_scenario_guides.py` | Build complete portable scenario guides with embedded assets and full-size diagram dialogs |
| `generate_sample_contract_assets.py` | Create synthetic MSA, DPA, SOW, order form, exhibits, JSON records, and analytics CSV |
| `generate_docgen_templates.py` | Create Box DocGen-ready Word templates for approval memo, order summary, and renewal notice |

For a fresh environment, start with:

```bash
cp config/runtime/demo-environment.example.json config/runtime/demo-environment.json
python3 scripts/demo_operator.py doctor
```

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
python3 scripts/demo_operator.py validate --scenario governed
```

Use `--offline` with `doctor` or `validate` only for repository/CI checks. Normal operator runs perform read-only verification against the configured Box enterprise and Salesforce org.

Run the sample asset generator from the CLM demo root:

```bash
python3 scripts/generate_sample_contract_assets.py
```

Generate the DocGen templates from the CLM demo root:

```bash
python3 scripts/generate_docgen_templates.py
```

The generated `.docx` files are written to `output/docgen/`. Sample merge data is in `config/box/docgen-template-data.json`.

Rebuild both screenshot galleries from the CLM demo root:

```bash
python3 scripts/build_clm_experience_gallery.py
```

Rebuild the complete portable guides:

```bash
python3 scripts/build_scenario_guides.py
```

Review outputs in this order:

1. `output/html/00-operator-setup-guide.html` — fresh-environment setup and validation.
2. `output/html/01-governed-workflow-guide.html` — complete narrative.
3. `output/html/02-governed-workflow-gallery.html` — visual-only companion.
4. `output/html/03-agentic-orchestration-guide.html` — complete narrative.
5. `output/html/04-agentic-orchestration-gallery.html` — visual-only companion.

Guide diagrams and screenshots open in a full-size dialog. All five files remain self-contained with no external assets.

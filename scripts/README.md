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

## Known breakage: the BCL cutover is half-applied

Config under `config/` is now `.bcl`; BCL is the only supported import format and every `.json` config was removed. Several scripts still expect the JSON paths and therefore fail:

| Script | Stale references |
|---|---|
| `demo_operator.py` | 10 config paths |
| `setup_clm_dev.py` | 1 |
| `validate_clm.py` | 1 (`validation-receipts.json`) |

Some tests error as a result, and `validate_clm.py` reports fewer passing rows than it did before the cutover. This is understood and accepted for now; it is not a regression to chase in isolation.

A working Python BCL reader exists in `unofficialbox/box-capture/bcl.py` and parses the same inventory that `box-dispatch` reads in `internal/bcl`. It is deliberately **not** vendored back into this repository, because doing so would recreate the dependency the extraction just removed.

Three ways out, in the order they should be considered:

1. **Move the provisioning scripts out**, so the question disappears with them. Preferred if the boundary rule holds.
2. **Let `box-dispatch` own config resolution** and delete the Python that duplicates it.
3. **Vendor a shared BCL reader here** — cheapest, but keeps machinery in the golden copy.

## Available scripts

| Script | Purpose |
|--------|---------|
| `validate_clm.py` | Run the complete repository matrix or fail-closed presenter-readiness validation from one command |
| `demo_operator.py` | Check prerequisites, generate assets, create the Box foundation, deploy portable Salesforce metadata, and validate a new environment |
| `setup_clm_dev.py` | Install repository dependencies and optionally sync Box/Salesforce context into `config/runtime/demo-environment.bcl` |
| `build_clm_experience_gallery.py` | Build separate self-contained Box Automate Agentic Orchestration and Cross-Platform Agentic Orchestration galleries from their scenario screenshot directories |
| `build_scenario_guides.py` | Build complete portable scenario guides with embedded assets and full-size diagram dialogs |
| `build_executive_marketecture.py` | Build the self-contained executive marketecture with business outcomes, platform roles, phased delivery, and real-demo proof |
| `build_presenter_portal.py` | Build the presenter landing page plus a single self-contained edition that embeds all nine standalone chapters |
| `build_agentcore_primary_marketecture.py` | Build the coordinated contract-work variation across Box, Salesforce Agentforce, Databricks, specialized agents, and accountable teams |
| `build_customer_datasheet.py` | Build the nontechnical Box Solutions datasheet for generalists, sales teams, customers, and IT decision makers |
| `build_contract_lifecycle_readiness_marketecture.py` | Build the lifecycle swimlane marketecture showing persistent platform responsibilities and human decision authority |
| `generate_sample_contract_assets.py` | Create synthetic MSA, DPA, SOW, order form, exhibits, JSON records, and analytics CSV |
| `generate_docgen_templates.py` | Create Box DocGen-ready Word templates for approval memo, order summary, and renewal notice, plus the in-redline Northstar MSA contract |

For a fresh environment, start with:

```bash
cp config/runtime/demo-environment.example.bcl config/runtime/demo-environment.bcl
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

Use `--skip-react` only for a narrow Python/content diagnostic. Use `--skip-playwright` only when browser binaries are unavailable and report the omitted gate. For a live presenter-readiness decision, populate the gitignored receipt file from `config/runtime/validation-receipts.example.bcl` and run `python3 scripts/validate_clm.py --presenter-ready`.

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

Three of the four files are merge templates. `northstar-msa-2026-redline.docx` is not: it is a real MSA draft still in redline, uploaded against the `CLM-SAMPLE-NST-001` sample record. It reads as an agreement would — recitals, defined terms, numbered clauses in legal prose, tracked-changes markup on the six contested clauses, counsel comments, an unsigned signature block, and an Exhibit A order form.

Every value the Salesforce intake connector binds is stated the way a contract states it, never as a labelled extraction field. Box Extract has to normalise real prose: `Two Hundred Fifty Thousand Dollars ($250,000.00)` → `250000.00`, `thirty-six (36) months` → `36`, a United States territory clause → `US`. That is deliberate — it exercises the extraction and human-validation path instead of short-circuiting it. Prompts live in `config/box/extract-field-prompts.bcl`.

Two bound fields are **not** in the document, because they are assessments rather than contract terms: `riskLevel` and `specialTermsRiskNotes` both come from the reviewer at the approval task. Keep the contract values aligned with `clm-salesforce-project/scripts/seed-clm-salesforce-sample-data.apex`.

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

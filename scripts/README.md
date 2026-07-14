# CLM Scripts

This directory is reserved for helper scripts.

Available scripts:

| Script | Purpose |
|--------|---------|
| `generate_sample_contract_assets.py` | Create synthetic MSA, DPA, SOW, order form, exhibits, JSON records, and analytics CSV |
| `generate_docgen_templates.py` | Create Box DocGen-ready Word templates for approval memo, order summary, and renewal notice |
| `generate_mock_records.py` | Create Salesforce opportunity, quote, approval matrix, and clause playbook JSON |

Follow the life-sciences demo pattern: generate reproducible artifacts into `output/pdf/` and keep source scripts in this directory.

Run the sample asset generator from the CLM demo root:

```bash
python3 scripts/generate_sample_contract_assets.py
```

Generate the DocGen templates from the CLM demo root:

```bash
python3 scripts/generate_docgen_templates.py
```

The generated `.docx` files are written to `output/docgen/`. Sample merge data is in `config/box/docgen-template-data.json`.

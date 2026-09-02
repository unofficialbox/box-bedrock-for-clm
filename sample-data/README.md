# CLM Sample Data Plan

This directory is reserved for synthetic CLM demo artifacts. The generated artifacts currently live under `output/` so they are clearly separated from source notes and can be regenerated.

Recommended files:

| File | Purpose |
|------|---------|
| `output/pdf/northstar-msa-redline-v3.pdf` | Redline with intentional high-risk clauses |
| `output/pdf/northstar-dpa.pdf` | Data processing addendum with PHI-related review trigger |
| `output/pdf/northstar-sow-implementation.pdf` | Statement of work with SLA and delivery obligations |
| `output/pdf/northstar-order-form.pdf` | Commercial terms for Salesforce quote comparison |
| `output/pdf/northstar-security-exhibit.pdf` | Security controls and annual evidence obligations |
| `output/pdf/northstar-insurance-certificate.pdf` | Insurance expiration tracking |
| `output/json/northstar-clm-records.json` | Mock opportunity/account/quote/approval data |
| `output/json/clause-playbook.json` | Approved standard and fallback positions |

Use the PDFs, Box metadata, structured records, and approved clause Markdown across the scenario packages. These are **Local deterministic fixture** evidence for Box + Salesforce Contract Lifecycle; they are not proof of a **Deployed integration**.

Regenerate all sample assets from the CLM demo root:

```bash
python3 scripts/generate_sample_contract_assets.py
```

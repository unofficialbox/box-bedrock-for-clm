# Presenter Deliverables

Complete this after the smoke test and before rehearsal.

## Build

```bash
python3 scripts/build_scenario_guides.py
python3 scripts/build_clm_experience_gallery.py
python3 scripts/build_executive_marketecture.py
python3 scripts/build_agentcore_primary_marketecture.py
python3 scripts/build_customer_datasheet.py
python3 scripts/build_contract_lifecycle_readiness_marketecture.py
```

`python3 scripts/validate_clm.py` rebuilds and compares all nine self-contained HTML files in temporary directories, so it remains the final deterministic check.

## Screenshot requirements

- Capture the real Box, Salesforce, or React page viewport.
- Exclude browser tabs, address bars, desktop content, notifications, and unrelated records.
- Use the target scenario directory under `output/screenshots/`.
- Update `config/demo/screenshot-manifest.json` with source, capture date, crop rule, scenario, and readiness state.
- Do not simulate AWS or Databricks console evidence.
- Rebuild affected HTML after replacing a screenshot.

## Rehearsal package

1. Open `output/html/00-operator-setup-guide.html` and verify offline navigation.
2. Select one scenario in [Scenario Guides](scenarios/README.md).
3. Review its complete guide before using the shorter visual gallery.
4. Verify every claim against the current readiness state.
5. Complete every relevant item in the [Manual-Task Register](manual-task-register.md).
6. Record reset ownership and the post-demo reconciliation path.

The Markdown source remains authoritative. HTML is a portable, self-contained sharing layer.

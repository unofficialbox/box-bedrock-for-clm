# CLM Operator Handoff: Build a Separate CLI (for Another AI Coding Agent)

This document is a **build spec** for a separate CLI that orchestrates CLM demo environment setup, validation, and handoff tasks.

## 1) Intent and non-negotiable requirements

The CLI must:

1. Reuse this repository’s existing script logic and contracts.
2. Keep destructive/production-impacting actions behind explicit confirmation.
3. Preserve idempotency and dry-run behavior.
4. Surface manual/browser steps clearly and fail closed when they are required.
5. Produce deterministic outputs and validation artifacts.
6. Expose machine-friendly output for automation and a human-readable mode for operators.

### Hard requirements

- Scope: support both scenarios supported by this repo:
  - `box-automate-agentic-orchestration`
  - `cross-platform-agentic-orchestration`
- Required commands:
  - `setup`, `doctor`, `bootstrap`, `status`, `validate`, `resolve`, `present`, `smoke`, `publish-check`
- Required flags:
  - `--scenario`, `--dry-run`, `--yes/--confirm`, `--offline`, `--skip-validate`, `--from-current-clis`, `--allow-unresolved`, `--json`
- Safety gates:
  - no publish/share/activate/send/secret material changes without explicit confirmation and configured evidence
  - never hardcode tenant/org IDs; use `config/runtime/demo-environment.json`
- Success criteria:
  - pass `validate_clm.py --presenter-ready` path with receipts when requested
  - run local validation matrix cleanly when in repository mode

## 2) CLI command spec (must map to existing repo primitives)

### `clm-cli setup`

Wraps `scripts/setup_clm_dev.py` and `setup_clm_dev.py` arguments.

- `clm-cli setup --automated` -> `python3 scripts/setup_clm_dev.py --automated`
- `clm-cli setup --automated --from-current-clis` -> `python3 scripts/setup_clm_dev.py --automated --from-current-clis`
- `clm-cli setup --smoke` -> `python3 scripts/setup_clm_dev.py --smoke`
- `clm-cli setup --json` emits machine-readable summary of planned/applied install steps.

### `clm-cli doctor`

Wraps `scripts/demo_operator.py doctor`.

- `clm-cli doctor --platform box|salesforce|all [--offline]`
- Outputs: required checks, failures, and recommended fix for each missing precondition.

### `clm-cli bootstrap`

Primary one-shot flow wrapper for:

1. `generate-assets`
2. `box-foundation`
3. `seed-metadata`
4. `salesforce-deploy`
5. `resolve-config`

Behavior:

- `--dry-run` prints planned steps only.
- `--yes/--confirm` allows mutating execution.
- default requires explicit confirmation.
- `--allow-unresolved` only allows unresolved browser/manual bindings.
- `--skip-validate` for bootstrap-only mode.
- `--scenario` determines validation breadth.

### `clm-cli status`

Wraps `scripts/demo_operator.py status`.

- Must show: bootstrap state, required folders/files/templates, generated specs presence, unresolved tokens, and remaining manual fields.
- Includes expected blocker list (form/app/hub/workflow URLs if missing).

### `clm-cli validate`

Wraps `scripts/demo_operator.py validate` for scenario checks and `scripts/validate_clm.py` for repository checks.

- `clm-cli validate --scenario <scenario> [--offline]`
- `clm-cli validate --repo [--skip-react] [--skip-playwright]`
- `clm-cli validate --presenter-ready`

### `clm-cli resolve`

Wraps `scripts/demo_operator.py resolve-config`.

- `--allow-unresolved` is supported for pre-browser validation.
- writes generated specs under `config/runtime/generated`.

### `clm-cli present`

Orchestrates presenter-build path used by `README.md`.

- `clm-cli present --build`
- Runs generators for all 11 HTML outputs and confirms checksums match tracked outputs if required.

### `clm-cli smoke`

Wraps and prints `docs/operator/smoke-test.md` gate items.

- `--scenario` required
- Accepts `--record-path` for external run log handoff file path.

### `clm-cli publish-check`

Pre-flight confirmation command for manual gates (publish/share/activate/send).

- Loads `docs/operator/manual-task-register.md` and required runtime fields before allowing operator to proceed with UI actions.

## 3) Reference inventory of scripts to reuse (absolute links)

### Core scripts

1. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/scripts/setup_clm_dev.py](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/scripts/setup_clm_dev.py)
2. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/scripts/demo_operator.py](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/scripts/demo_operator.py)
3. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/scripts/validate_clm.py](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/scripts/validate_clm.py)
4. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/scripts/prepare_box_form_browser_plan.py](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/scripts/prepare_box_form_browser_plan.py)
5. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/scripts/generate_sample_contract_assets.py](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/scripts/generate_sample_contract_assets.py)
6. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/scripts/generate_docgen_templates.py](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/scripts/generate_docgen_templates.py)
7. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/scripts/run_agentcore_mock.py](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/scripts/run_agentcore_mock.py)

### Presenter/build scripts

8. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/scripts/build_scenario_guides.py](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/scripts/build_scenario_guides.py)
9. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/scripts/build_clm_experience_gallery.py](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/scripts/build_clm_experience_gallery.py)
10. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/scripts/build_presenter_portal.py](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/scripts/build_presenter_portal.py)

### Auxiliary/browser/experimentation scripts

11. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/scripts/box_form_provisioner.py](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/scripts/box_form_provisioner.py)
12. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/tools/box-capture/forms.py](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/tools/box-capture/forms.py)
13. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/tools/box-capture/apps.py](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/tools/box-capture/apps.py)
14. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/tools/box-capture/automate.py](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/tools/box-capture/automate.py)

## 4) Reference inventory of config/assets/docs for the new CLI

### Runtime and generated state

1. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/config/runtime/demo-environment.example.json](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/config/runtime/demo-environment.example.bcl)
2. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/config/runtime/demo-environment.json](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/config/runtime/demo-environment.bcl)
3. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/config/runtime/bootstrap-state.json](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/config/runtime/bootstrap-state.bcl)
4. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/config/runtime/generated/box/form-definition.json](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/config/runtime/generated/box/form-definition.bcl)
5. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/config/runtime/validation-receipts.example.json](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/config/runtime/validation-receipts.example.bcl)
6. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/config/runtime/validation-receipts.example.json](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/config/runtime/validation-receipts.example.bcl) (copy to `config/runtime/validation-receipts.json` for presenter-ready runs)
7. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/config/operator/operator-workflow.json](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/config/operator/operator-workflow.bcl)
8. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/config/demo/box-automate-agentic-orchestration-demo-manifest.json](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/config/demo/box-automate-agentic-orchestration-demo-manifest.bcl)
9. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/config/demo/cross-platform-agentic-orchestration-demo-manifest.json](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/config/demo/cross-platform-agentic-orchestration-demo-manifest.bcl)
10. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/config/demo/screenshot-manifest.json](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/config/demo/screenshot-manifest.bcl)

### Operator/docs entry points

11. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/docs/operator/README.md](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/docs/operator/README.md)
12. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/docs/operator/start-here.md](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/docs/operator/start-here.md)
13. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/docs/operator/browser-configuration.md](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/docs/operator/browser-configuration.md)
14. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/docs/operator/final-phase.md](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/docs/operator/final-phase.md)
15. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/docs/operator/smoke-test.md](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/docs/operator/smoke-test.md)
16. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/docs/operator/manual-task-register.md](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/docs/operator/manual-task-register.md)
17. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/docs/operator/manual-box-configuration.md](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/docs/operator/manual-box-configuration.md)
18. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/docs/operator/scenarios/box-automate-agentic-orchestration/README.md](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/docs/operator/scenarios/box-automate-agentic-orchestration/README.md)
19. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/docs/operator/scenarios/cross-platform-agentic-orchestration/README.md](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/docs/operator/scenarios/cross-platform-agentic-orchestration/README.md)

### Public bootstrap/reuse tests

20. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/tests/test_demo_operator.py](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/tests/test_demo_operator.py)
21. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/tests/test_setup_clm_dev.py](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/tests/test_setup_clm_dev.py)
22. [/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/tests/test_box_form_provisioner.py](/Users/massnerder/Developer/Code/box-bedrock-agentcore-demos/box-bedrock-for-clm/tests/test_box_form_provisioner.py)

## 5) CLI implementation constraints

The new CLI should avoid hardcoding environment IDs, tenant names, usernames, or secrets.

It must use existing runtime boundaries:

- Read/write runtime state only in `config/runtime` and tracked generated artifacts.
- Reuse `demo_operator` for operational decisions when possible.
- Reuse `validate_clm.py` for matrix checks.
- Treat `bootstrap-state.json` and `demo-environment.json` as single source of truth for environment reconciliation.

## 6) Acceptance test matrix for the new CLI

The implementing AI should run:

1. `python3 scripts/setup_clm_dev.py --smoke`
2. `python3 scripts/demo_operator.py bootstrap --scenario box-automate-agentic-orchestration --dry-run`
3. `python3 scripts/demo_operator.py bootstrap --scenario box-automate-agentic-orchestration --yes`
4. manual/browser steps from `docs/operator/browser-configuration.md` executed in target environment
5. `python3 scripts/demo_operator.py resolve-config`
6. `python3 scripts/demo_operator.py status --scenario box-automate-agentic-orchestration`
7. `python3 scripts/demo_operator.py validate --scenario box-automate-agentic-orchestration`
8. `python3 scripts/validate_clm.py --presenter-ready` (only after receipts)
9. Re-run the same for cross-platform scenario.

## 7) Minimal handoff outputs for AI-agent ownership

At each run, the CLI should emit:

- phase results (`phase`, `status`, `duration_ms`, `error`)
- unresolved required tokens if any
- blocked actions with explicit action item IDs
- validation summary and next command
- reproducible machine-readable artifact path (JSON)

## 8) Output contract example

```json
{
  "command": "bootstrap",
  "scenario": "box-automate-agentic-orchestration",
  "dryRun": false,
  "confirmRequired": true,
  "phases": [
    {
      "name": "generate-assets",
      "status": "passed",
      "durationMs": 1210
    }
  ],
  "manual": [
    "box.formUrl",
    "box.appUrl"
  ],
  "validation": {
    "demo_operator_status": "blocked",
    "repo_status": "passed"
  }
}
```

---

If you want the next handoff to be even more implementation-ready, I can add:

1. a proposed command schema (`typer` / `click` interface),
2. exact return codes per command,
3. a minimal test harness spec with fake Box/Salesforce adapters.

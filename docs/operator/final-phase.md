# CLM Finalization Phase (End-to-End Completion)

Use this phase after:

1. `box-foundation`
2. `seed-metadata`
3. `salesforce-deploy`
4. Browser-admin configuration (Form/App/Hub/Automate + OAuth)
5. Scenario-specific smoke test

## 0) Scope and safety guardrails

- Do not proceed if the target runtime differs from:
  - `box.enterpriseId`
  - `box.operatorLogin`
  - `salesforce.orgId`
- Never export credentials or browser session state.
- Keep all new URLs and IDs in `config/runtime/demo-environment.json` only.
- Do not publish/share/activate/send until owner confirmation has been recorded in the manual task register.

## 1) Resolve final runtime bindings

```bash
python3 scripts/demo_operator.py resolve-config
```

Expected output:
- `config/runtime/generated` contains resolved specs for all portable manifests.
- No unresolved `${...}` tokens remain for required fields.

## 2) Validate end-to-end automation boundary

```bash
python3 scripts/demo_operator.py validate --scenario cross-platform-agentic-orchestration
python3 scripts/validate_clm.py
```

For Cross-Platform demos, run the additional check:

```bash
python3 scripts/demo_operator.py validate --scenario cross-platform-agentic-orchestration
```

## 3) Capture proof and evidence locks

1. Record the latest:
   - published URLs in `config/runtime/demo-environment.json`
   - test artifacts, workflow run IDs, and Salesforce record IDs in your external run log
   - screenshot set and manifest updates (`config/demo/screenshot-manifest.json`)
2. Copy and fill the receipt file:

```bash
cp config/runtime/validation-receipts.example.json config/runtime/validation-receipts.json
```

Populate with current external evidence references only:

- scenario name
- presenter readiness date
- screenshot manifest entry IDs used
- smoke-test log IDs
- Salesforce record IDs used in labeled validation
3. Run:

```bash
python3 scripts/validate_clm.py --presenter-ready
```

This must fail closed if any required receipt is missing.

## 4) Manual confirmation gates (must be explicit in writing)

Before opening/using any external UI button action or destructive step, confirm with owner and record intent:

- Publish Form
- Publish App
- Publish Hub
- Activate workflow
- Generate document
- Send signature request
- Delete/reset data
- Share content or collaborators

Only execute these after `validate_clm.py` and operator sign-off.

## 5) Final evidence review checklist

Declare final readiness only when:

- `validate_clm.py --presenter-ready` passes
- one labeled smoke intake creates/updates a Salesforce record end-to-end
- Box/CLI IDs and links are consistent in `demo-environment.json`
- no unresolved runtime tokens remain in generated specs
- screenshot and run evidence is stored and versioned in this environment

Capture this in `manual-task-register.md` as complete:

- MT-053 (per-run validation submission)
- MT-054 (duplicate-safe behavior)
- MT-072 (screenshot capture)
- MT-073 (post-run reset readiness)

## 6) Optional private-API lab closure (non-production only)

Keep private-lab executors separate from production setup:

```bash
python3 ../../unofficialbox/box-capture/forms.py --dry-run
python3 ../../unofficialbox/box-capture/apps.py --dry-run
python3 ../../unofficialbox/box-capture/automate.py --dry-run
```

Then run each generated executor only in an authenticated Box web-app tab and never as production dependency.

# Demo Operator

Use this path to configure, deploy, validate, rehearse, or reset the CLM demo in a confirmed target environment.

## Run order

Use [Demo Operator Handoff](./demo-operator-handoff.md) as the single consolidated script and validation reference.

1. Confirm the repository, selected scenario, exact Box enterprise, Salesforce org, AWS account and region, Databricks workspace, and ignored runtime file.
2. Run `python3 scripts/demo_operator.py status`.
3. Run `python3 scripts/demo_operator.py doctor --offline --platform box`.
4. For a one-shot idempotent operator path, run:

   ```bash
   python3 scripts/demo_operator.py bootstrap --scenario <scenario> --dry-run
   ```

5. Complete the [Entitlement Checklist](entitlement-checklist.md).
6. Follow [Start Here](start-here.md).
7. Complete [Browser Configuration](browser-configuration.md).
8. Complete [Cross-Platform Deployment](cross-platform-deployment.md) when that scenario is selected.
9. Run the [Smoke Test](smoke-test.md).
10. Rehearse one [Scenario Guide](scenarios/README.md).
11. Build [Presenter Deliverables](presenter-deliverables.md) and finish the [Manual-Task Register](manual-task-register.md).
12. Complete [Finalization](final-phase.md) before declaring presenter readiness.

Use [Manual Box Configuration and Automation Feasibility](manual-box-configuration.md) to distinguish supported API automation from browser-only product setup and private-API research.

Use the [Box Form Browser Plan](box-form-provisioner.md) only for the unsupported Forms-authoring gap. It prepares a guarded Browser Use task; it does not change Box by itself.

Use [Box Private-API Labs](box-private-api-labs.md) for isolated research on Forms, Apps, Automate, and Hub composition. Every executor requires an already-authenticated Box web-app tab on the exact configured hostname.

For assistant-driven execution, read [AI-Assisted Operator Protocol](ai-operator.md). Planning, generation, validation, and dry runs may proceed without external approval. Every external write requires the guide's explicit apply option, confirmation of the exact target, and any documented human decision gate.

## Live claim boundary

Use the four readiness terms in `README.md`. Do not describe a **Portable specification** or **Local deterministic fixture** as a **Deployed integration**. Do not describe a scenario as **Presenter-ready live** until `python3 scripts/validate_clm.py --presenter-ready` passes with current receipts.

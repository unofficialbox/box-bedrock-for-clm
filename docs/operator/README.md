# Demo Operator

Use this path to configure, deploy, validate, rehearse, or reset the CLM demo in a confirmed target environment.

## Run order

1. Confirm the repository, selected scenario, exact Box enterprise, Salesforce org, AWS account and region, Databricks workspace, and ignored runtime file.
2. Run `python3 scripts/demo_operator.py status`.
3. Run `python3 scripts/demo_operator.py doctor --offline --platform box`.
4. Complete the [Entitlement Checklist](entitlement-checklist.md).
5. Follow [Start Here](start-here.md).
6. Complete [Browser Configuration](browser-configuration.md).
7. Complete [Cross-Platform Deployment](cross-platform-deployment.md) when that scenario is selected.
8. Run the [Smoke Test](smoke-test.md).
9. Rehearse one [Scenario Guide](scenarios/README.md).
10. Build [Presenter Deliverables](presenter-deliverables.md) and finish the [Manual-Task Register](manual-task-register.md).

For assistant-driven execution, read [AI-Assisted Operator Protocol](ai-operator.md). Planning, generation, validation, and dry runs may proceed without external approval. Every external write requires the guide's explicit apply option, confirmation of the exact target, and any documented human decision gate.

## Live claim boundary

Use the four readiness terms in `README.md`. Do not describe a **Portable specification** or **Local deterministic fixture** as a **Deployed integration**. Do not describe a scenario as **Presenter-ready live** until `python3 scripts/validate_clm.py --presenter-ready` passes with current receipts.

# Operating the demo

Configure, deploy, validate, rehearse, or reset the CLM demo in a confirmed target environment.

## Run order

See [`scripts/README.md`](../scripts/README.md) for the operator scripts and validation commands.

1. Confirm the repository, selected scenario, exact Box enterprise, Salesforce org, and ignored runtime file.
2. Run `python3 scripts/demo_operator.py status`.
3. Run `python3 scripts/demo_operator.py doctor --offline --platform box`.
4. For a one-shot idempotent operator path, run:

   ```bash
   python3 scripts/demo_operator.py bootstrap --scenario <scenario> --dry-run
   ```

5. Bind the environment: [Deployment](DEPLOYMENT.md) lists every value tied to one
   Salesforce org or Box enterprise, and what breaks when one is missing.
6. Follow [Setup](SETUP.md).
7. Complete [Client Setup](CLIENT-SETUP.md).
8. Complete [Documents Setup](DOCUMENTS-SETUP.md) to bring up governed Box content; until it is done the workspace reports that it cannot be opened.
9. Run the [Smoke Test](SMOKE-TEST.md).
10. Rehearse the [scenario guide](SCENARIO-GUIDE.md).
11. Build [Presenter Deliverables](PRESENTING.md) and finish the [Manual-Task Register](MANUAL-TASKS.md).
12. Complete [Finalization](FINALIZATION.md) before declaring presenter readiness.

[Inbound Email Intake Service](EMAIL-INTAKE.md): Salesforce email service that captures a counterparty's emailed contract onto the matching Opportunity and stages the attachment for Box intake.

Box Private-API Labs (box-capture repository): isolated research on Apps, Automate, and Hub composition. Every executor requires an already-authenticated Box web-app tab on the exact configured hostname.

## Live claim boundary

Use the four readiness terms in `docs/CONVENTIONS.md`. Do not describe a **Portable specification** or **Local deterministic fixture** as a **Deployed integration**. Do not describe a scenario as **Presenter-ready live** until `python3 scripts/validate_clm.py --presenter-ready` passes with current receipts.

## Box surface authoring tooling

This repository is a **golden copy** of the finished CLM scenario. The tooling that authors Box surfaces without a supported API — guarded Forms, Apps, and Automate executors, their lab specifications, and the Automate graph inspector — lives in a separate repository:

    unofficialbox/box-capture

Nothing here depends on it at runtime. Use it to rebuild a Box surface in a new environment or capture a live workflow definition, not to run or present the demo.

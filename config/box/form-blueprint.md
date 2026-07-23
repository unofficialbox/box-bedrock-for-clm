# Box Form Blueprint: New Contract Request

Build this Form after `python3 scripts/demo_operator.py box-foundation`. Bind its destination to the generated `CLM-2026-Northstar / 01 - Intake` folder from `config/runtime/bootstrap-state.json`.

The machine-readable [Form definition](form-definition.bcl) is the sole source for the title, ordered fields, options, required states, rehearsal values, destination binding, default confirmation behavior, and automation safety policy. Do not maintain a second field list here.

Prepare and apply it through the [Box Form Browser Plan](../../docs/operator/box-form-provisioner.md).

## Build and validation

1. Build and save the Form with Browser Use. Box lists a saved Form as **Active**.
2. Verify the exact title, field order, field types, required states, options, destination, and Box-default confirmation behavior.
3. Obtain owner approval before copying, enabling, or distributing the Form link.
4. Record the approved link in gitignored `config/runtime/demo-environment.json`.
5. Submit the smoke-test values and confirm the upload lands in this environment's generated intake folder.

Do not create a second intake Form. The Box App must reference this published Form as its sole intake action.

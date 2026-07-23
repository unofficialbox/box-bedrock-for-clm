# Box Form Browser Plan

Box Forms has no supported public authoring API. This is the controlled Browser Use fallback; it is not API provisioning. The tracked [Form definition](../../config/box/form-definition.bcl) is the source of truth.

## Prepare

Before preparing or applying the plan, sign in to the intended Box web application and keep that authenticated tab open. The browser agent uses the existing Box web session; neither the plan nor the experimental executor performs login or contains credentials.

Run after `box-foundation` has created the target environment's intake folder:

```bash
python3 scripts/prepare_box_form_browser_plan.py --dry-run
python3 scripts/prepare_box_form_browser_plan.py
```

The second command reads the gitignored environment and bootstrap files, verifies the hostname and target guards, resolves the destination folder, and writes:

`config/runtime/generated/box/form-browser-plan.json`

**This command does not open Box or change external state.** It only validates the portable definition, resolves the generated intake-folder binding, and writes a Browser Use plan.

## Apply with an authenticated browser agent

Give the agent this concise instruction:

> Apply `config/runtime/generated/box/form-browser-plan.json` in the authenticated Box browser. Confirm the configured hostname, enterprise, and operator before making changes. Reconcile exactly one Form with the exact title. Save it, verify every supported property, and stop before copying, enabling, or distributing its link or submitting a response.

That instruction authorizes creation or modification of the single Form described by the packet. It does not authorize link distribution or a test submission. In the current Box UI, **Save Form** immediately lists the Form as **Active**; there is no separate saved-draft status.

The browser agent must:

1. Open the packet's Forms URL and confirm the active hostname and signed-in identity.
2. Search for an exact title match before creating anything.
3. Create one draft when there is no match; reconcile the existing Form when there is one match.
4. Stop and report when there are multiple exact matches.
5. Apply the ordered fields, types, required states, dropdown options, and destination.
6. Save and re-open the Form to verify the complete configuration.
7. Accept Box's default submission confirmation. The current builder and public API do not expose a custom confirmation-message setting.
8. Stop before copying, enabling, or distributing the link and request separate owner approval.

## Safety boundary

The provisioner does not call the private REST endpoints directly, export browser credentials, or persist headers, cookies, tokens, or anti-forgery values. The generated plan is environment-specific and gitignored. Delete it when the environment is retired.

## Unsupported private API lab

The repository also contains separate, opt-in research executors documented in [Box Private-API Labs](box-private-api-labs.md). The Forms executor targets only the retained **CLM Forms API Lab - Contract Intake** Form. It is not the production provisioning path and cannot target **New Contract Request**.

```bash
python3 tools/box-capture/forms.py --dry-run
python3 tools/box-capture/forms.py \
  --write-executor \
  --acknowledge 'I understand this uses an unsupported Box private API'
```

The second command writes a credential-free, gitignored browser-automation executor to:

`config/runtime/generated/box/private-api-lab-provisioner.js`

Do **not** paste this file into the JavaScript console. Give an authenticated browser agent this instruction:

> Apply `config/runtime/generated/box/private-api-lab-provisioner.js` through browser automation in the existing authenticated Box tab. Confirm the exact configured hostname, run the executor in the page origin without opening DevTools, and report only the sanitized result. Do not export browser credentials.

The browser automation attaches to the authenticated Box tab and executes the guarded request within that page's origin. It lists Forms, matches the exact lab title, and performs one of three outcomes: `created`, `updated`, or `unchanged`. It stops on duplicate exact-title matches. It contains no delete, publish, share, link-copy, or submission call and never stores browser credentials.

The lab definition exercises the seven private component schemas observed in the real builder: short text, long text, email, number, single-select dropdown, date, and file upload. The upload destination is resolved from the gitignored generated Form runtime, so run the normal Form-plan preparation first when rebuilding a new environment.

This remains unsupported research. Do not use it to provision production Forms or as a dependency for a customer deployment. It still requires a browser-automation surface capable of attaching to an authenticated tab; a normal Box OAuth client is not sufficient. The redacted request and response evidence is in [Box Forms private API experiments](../research/box-forms-private-api/README.md).

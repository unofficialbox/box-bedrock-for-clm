# Box Private-API Labs

These labs investigate unsupported Box web APIs for surfaces that do not have complete public authoring APIs. They are research tools, not production provisioning.

## Required operator state

Before running any lab executor, the operator must:

1. Sign in to the intended Box enterprise in a normal Box web-app tab.
2. Confirm the tab hostname exactly matches `config/runtime/demo-environment.json`.
3. Use the intended builder account and confirm it has access to the target product.
4. Keep that authenticated tab open while the browser agent runs the executor in the same page origin.

The executors do not contain credentials and cannot authenticate by themselves. Do not export cookies, tokens, local storage, or anti-forgery values. A Box Platform OAuth token is not a substitute for the authenticated Box web-app session used by these unsupported endpoints.

## Current coverage

| Surface | Public authoring boundary | Private lab status | Allowed lab operations | Blocked operations |
|---|---|---|---|---|
| Forms | No supported Form definition CRUD | Proven | Exact-title create, update, read-back, unchanged | Delete, publish/link distribution, share, submit |
| Apps | No complete supported page/section/block/layout CRUD | Proven for shell plus section-aware reconciliation | Exact-title create, lock, update description + sections, unlock, read-back, unchanged | Delete, publish, share; production titles |
| Automate | No supported workflow-definition CRUD | Proven for an empty inactive draft and a separate Manual Start-only graph draft | Exact-title create/update/read-back/unchanged; the graph lab permits one scoped Manual Start trigger and one dangling edge | Delete, publish, activate, share, run; outcomes, gateways, additional triggers, and connected actions |
| Hub page composition | Core Hub CRUD is public; the composed page document is not fully authorable publicly | Read-only schema captured | Read Hub document/version envelope | Private document writes, publish, share |

Use supported APIs for Hub creation/items/collaborators, AI Agents, Doc Gen templates, content, metadata, tasks, and other documented surfaces.

## Forms lab

```bash
python3 scripts/experimental_box_forms_private_api.py --dry-run
python3 scripts/experimental_box_forms_private_api.py \
  --write-executor \
  --acknowledge 'I understand this uses an unsupported Box private API'
```

## Apps lab

```bash
python3 scripts/experimental_box_apps_private_api.py --dry-run
python3 scripts/experimental_box_apps_private_api.py \
  --write-executor \
  --acknowledge 'I understand this uses an unsupported Box private API'
```

## Automate empty-draft lab

Open Box Automate in the authenticated web-app tab before applying this executor.

```bash
python3 scripts/experimental_box_automate_private_api.py --dry-run
python3 scripts/experimental_box_automate_private_api.py \
  --write-executor \
  --acknowledge 'I understand this uses an unsupported Box private API'
```

## Automate Manual Start graph lab

This separate lab resolves the `workspace` folder alias from the gitignored
`config/runtime/bootstrap-state.json`. It never writes a live Box ID to the portable specification.

```bash
python3 scripts/experimental_box_automate_private_api.py \
  --spec config/box/private-api-lab-automate-manual-start-definition.json \
  --bootstrap config/runtime/bootstrap-state.json \
  --dry-run

python3 scripts/experimental_box_automate_private_api.py \
  --spec config/box/private-api-lab-automate-manual-start-definition.json \
  --bootstrap config/runtime/bootstrap-state.json \
  --output config/runtime/generated/box/private-api-lab-automate-manual-start-provisioner.js \
  --write-executor \
  --acknowledge 'I understand this uses an unsupported Box private API'
```

The executor accepts only an inactive exact-title lab with either no graph or one Manual Start
trigger, one dangling basic edge, and no outcomes or gateways. Run it a second time and require
`"outcome": "unchanged"` before treating the lab as reconciled.

The Apps lab can also reconcile a portable `pages` section schema when provided in
`config/box/private-api-lab-app-definition.json`. Keep sections to basic metadata only; `items` is still blocked until a stable block schema capture exists.

After generating an executor, give the authenticated browser agent this instruction:

> In the already-authenticated Box web-app tab on the configured hostname, apply the generated private-API lab executor in the page origin without opening DevTools. Reconcile only the exact lab title, report a sanitized result, and do not export credentials or invoke delete, publish, share, activate, or submission actions.

## Next guarded experiments

1. Add one inert, non-notifying outcome to a separate Automate graph lab and extend the schema one element at a time. Keep `PublishWorkflow`, activation, and execution blocked.
2. Create a disposable Hub through the supported Hubs API, edit one simple lab-only page block in the UI, and characterize the versioned binary document update. Do not publish or share it.
3. Expand the Apps lab from shell/description reconciliation to portable block payloads only after each block schema has been captured and sanitized.

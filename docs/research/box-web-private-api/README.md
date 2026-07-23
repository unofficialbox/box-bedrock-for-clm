# Box web private-API surface discovery

Captured on **2026-07-20** in the authenticated `kadams.ent.box.com` web application. The operator must already be signed in to the intended Box web-app session; these requests do not establish authentication and no browser credentials were exported.

## Findings

| Surface | Observed transport | Read contract | Write contracts observed in the client | Live lab result |
|---|---|---|---|---|
| Box Apps | Crooze private REST-like method calls | `app.list`, `app.get`, `app.status` | `app.create`, `app.lock`, `app.update.all`, `app.cancelEdit`, `app.delete` | Created and updated **CLM Surface API Lab - Apps Workspace**; second reconcile was unchanged. Delete/publish/share were not called. |
| Box Automate | Private GraphQL through the authenticated in-page Apollo client | `GetCombinedWorkflows`, `LoadWorkflowAndEnsureCascadeRole` | `CreateItemV2`, `UpdateItemV2`, `PublishWorkflow`, `ActivateWorkflow`, and related operations | Preserved the empty lab and created a separate **CLM Surface API Lab - Automate Manual Start Graph** with one folder-scoped Manual Start trigger and one dangling edge. The generated executor updated it once and returned unchanged on the second run. Both stayed inactive and unpublished. |
| Box Hub composition | Private GraphQL | `GetHub` returns a versioned, base64-encoded binary `document` envelope | Client composition mutations require a separate isolated capture | Read-only capture only. No Hub content, publication, or sharing state changed. |

## Interpretation

- Apps configuration is represented as pages containing sections and items/blocks with positions, sizes, themes, and block-specific data.
- Automate definitions expose trigger, outcomes, gateways, edges, enterprise-feature gates, and publication timestamps separately from the workflow item identity.
- A direct same-origin Automate mutation without the web application's anti-forgery context returned `403`. The guarded executor instead uses the authenticated page's existing Apollo client. It never reads, returns, or stores the anti-forgery token.
- The Manual Start graph uses `triggerType: MANUAL`, `triggerSubtype: START`, a runtime-resolved `parentFolderId`, string-valued `includeSubfolders`, and one `BASIC` edge with no target. Portable configuration stores only the logical `workspace` folder alias.
- Hub page composition is not ordinary JSON in the read response; the document is a versioned binary payload. Core Hub creation and item management should remain on the supported Hubs API.
- Private web APIs remain unsupported and may change without notice. Preserve exact-host, exact-title, duplicate, and consequential-action guards.

Sanitized request and response shapes are stored beside this file, including the Apps lab create/update sequence, the empty and Manual Start Automate labs, and the read-only Hub probe. They contain no live IDs, user identities, enterprise identifiers, cookies, tokens, anti-forgery values, or customer content.

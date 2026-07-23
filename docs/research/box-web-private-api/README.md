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

## 2026-07-22 follow-up: reading and writing an existing workflow

Two existing drafts were read without mutation, and one connector outcome was then authored through the editor. The definitions were taken from the editor's loaded workflow graph in client application state, which is the server-provided definition before any local edit. GraphQL request and response bodies remained unreadable, so this is the practical read path for an existing workflow. `tools/box-capture/automate.py --write-inspector` packages the read path with hostname, surface, exact-title and never-published guards.

Additional interpretation:

- Variable tokens are namespaced by trigger type. A form trigger yields `static.trigger.form.<formFieldId>`; a metadata trigger yields `trigger.fileId` and `trigger.metadata.<field>`. Bindings are by element ID, not label, so rebuilding a Form breaks them.
- Free-text fields interpolate a token as `${token}`. Structured fields store `{"type":"variable","value":"<token>"}`.
- An HTTPS body is stored as an ordered `CONCAT` of operands rather than a template string. Literal JSON sits in `VALUE` operands and each dynamic value is a separate operand spliced between them.
- Operand types observed: `VALUE`, `VARIABLE`, `DYNAMIC_VARIABLE`, `GET_FILE_METADATA_FIELD`, and `DATE_FORMAT`. Metadata reads carry the file variable, template key, field GUID and template scope; the GUID is per-template and per-enterprise and is not portable.
- A date variable offers a full ISO datetime or single components but no `YYYY-MM-DD` preset, so a date-only value is three `DATE_FORMAT` operands joined by literal hyphens. Component formats are encoded as a `__YYYY__` style suffix on the token name, the same convention seen in folder-rename expressions.
- The body editor opens an inline variable search on `/`, and the picked variable becomes a ProseMirror `variable` node whose `name` attribute carries the token. On save the whole body converts from a single `VALUE` to a `CONCAT` operand list. Searching by form element ID is the only unambiguous selection method, because several labels match both a Form field and a metadata attribute.
- HTTPS response captures are stored as a `jsonPathCustomVariableList`. The editor exposes no expected-status configuration, so status gating cannot be claimed for this surface.
- **An unresolved variable renders as the literal string `Variable unavailable`.** It is not empty and not null. Any downstream system receiving that text into a typed field will reject it. This was observed in a live run, not inferred.
- Connector faults surface only as `errorCode: UNKNOWN_ERROR` with an empty payload. The underlying `/app-api/graphql` call still returns HTTP 200 because the failure happens inside Box's server-side connector call, so the external system's error text is never exposed. Diagnose from the fully resolved request body recorded in the `CALL_CONNECTOR` run event instead.

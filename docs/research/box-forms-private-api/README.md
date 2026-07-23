# Box Forms private API experiments

Captured on **2026-07-20** in a confirmed test enterprise. This experiment created, updated, and deleted one disposable Form through the Box web builder. It did not click **Publish**, copy a share link, or retain submitted content.

## Result

| Operation | Observed private REST call | Result |
|---|---|---|
| Create | `POST /app-api/file-request-web/form` | `200` |
| Update | `POST /app-api/file-request-web/form-version/${FORM_VERSION_ID}` | `200` |
| Delete | `DELETE /app-api/file-request-web/file-request/${FORM_ID}` | `204` |

The traffic was REST, not GraphQL. Create and update used `multipart/form-data`; the Form definition was a JSON value in the `content` field. The delete response had no body.

The create response reported `status: ACTIVE` and `visibility: OPEN` before the separate **Publish** UI action. Do not interpret an unpublished-looking editor state as proof that the backing object is inactive or private.

## Can this run without Browser Use?

Only in a narrow, unsupported sense. A browserless HTTP client could reproduce the request shape if it also reproduced Box's authenticated web session, anti-forgery controls, and current internal schema. This probe did **not** establish that a Box Platform OAuth token can call these endpoints, and it intentionally did not export or replay browser credentials.

Therefore:

- Private API Form creation is technically demonstrated.
- Supported, durable, browserless Form provisioning is **not** demonstrated.
- These endpoints are undocumented, may change without notice, and should not be a production dependency.
- Keep Form creation manual or controlled through UI automation until Box publishes a supported Forms API.

## Evidence handling

The adjacent JSON files are normalized, redacted representations of the observed calls. They preserve methods, endpoint patterns, multipart field names, payload structure, response shape, and status codes. They deliberately omit request headers, cookies, tokens, CSRF material, user details, enterprise identifiers, live object IDs, URL keys, and timestamps.

The disposable Form was deleted after capture, and its title no longer appeared in the Forms list.

## Retained CLM lab Form

On **2026-07-20**, a second isolated experiment created **CLM Forms API Lab - Contract Intake** in `kadams.ent.box.com`. It was intentionally retained at the operator's request. No delete, share-link distribution, or test submission was performed.

The first request in this experiment returned `400 Invalid form` because its component key was an unprefixed generated identifier. Reading the existing builder payload showed that field component keys use the `element-` prefix. Repeating the request with an `element-${FIELD_ID}` key returned `200`; the response again reported `status: ACTIVE` and `visibility: OPEN`.

Evidence for this retained experiment is stored in the `2026-07-20-clm-forms-api-lab-*.redacted.json` files. All live identifiers and authenticated browser material are replaced with placeholders.

The guarded reconciliation was then repeated through authenticated browser automation without opening or pasting into the JavaScript console. The initial one-field executor found exactly one matching lab Form and returned `outcome: unchanged`, `status: ACTIVE`, and `visibility: OPEN`. No browser credential was exported.

## Field-schema capture

A subsequent authenticated, read-only request captured the normalized component shapes for short text, long text, email, number, single-select dropdown, date, and file upload fields. The sanitized shapes are in `2026-07-20-box-form-component-schemas.redacted.json`.

The guarded lab provisioner now supports those seven observed types. Upload fields receive their destination folder from the gitignored generated Form runtime (`config/runtime/generated/box/form-definition.json`); no live folder ID is stored in the committed definition or evidence.

The seven-field executor updated only the exact-title lab Form. An immediate second run returned `outcome: unchanged` with `fieldCount: 7`, demonstrating idempotent reconciliation. The redacted request and both sanitized results are stored in the adjacent `2026-07-20-clm-forms-api-lab-update-*.redacted.json` files. No production Form, delete, publish, share, or submission endpoint was targeted.

# Box Preview Setup

Configure the governed Box preview in the CLM React workspace: a Box platform app, the
Salesforce credential that holds it, and the settings that scope it to one folder.

Until this is complete the workspace renders its synthetic file fixtures. That fallback is
intentional and safe — nothing breaks, you just do not see real Box content.

Related manual tasks: MT-037 through MT-040 in the [Manual-Task Register](manual-task-register.md).

## What this builds

```
Browser ──GET /services/apexrest/clm/box-token?folderId=<id>──▶ ClmBoxTokenService (Apex)
                                                                  │
                                        1. client credentials grant│ (Box app -> enterprise token)
                                        2. token exchange          │ (downscope to one folder)
                                                                  ▼
Browser ◀────────── short-lived token, scoped to that folder only ─┘
   │
   ├── GET api.box.com/2.0/folders/<id>/items      (list files)
   └── Box Content Preview renders the selected file
```

The browser never receives a client secret and never receives the enterprise token. Apex
never holds a credential either: Salesforce substitutes the encrypted values into the
request body at callout time.

## Prerequisites

- Box admin access to the target enterprise.
- Salesforce admin access to the target org.
- The CLM metadata deployed, including `ClmBoxTokenService`, the `CLM_Box` external
  credential, `CLM_Box_Config__c`, and the CSP trusted sites.

## Part 1 — Box platform app

1. In the Box Developer Console, create a **Custom App** with **Server Authentication
   (Client Credentials Grant)**.
2. Set **App Access Level** to **App + Enterprise Access**. The service identity must be
   able to see the contract folder.
3. Under **Application Scopes**, enable reading all files and folders. Write, delete, and
   share scopes are not required — the endpoint only ever mints read-only preview tokens.
4. Under **CORS Domains**, add the Experience Cloud origin, for example
   `https://<your-site>.my.site.com`. The browser calls `api.box.com` directly with the
   downscoped token, so Box refuses the folder listing without this.
5. Save, then have a Box admin **authorize the app** in the Admin Console under
   **Apps → Custom Apps Manager**, using the app's Client ID. A Client Credentials Grant
   app returns `unauthorized` until this is done.
6. Record the **Client ID**, **Client Secret**, and **Enterprise ID**.

## Part 2 — Salesforce credential

Secrets go in the external credential, never in a file.

1. **Setup → Named Credentials → External Credentials → CLM Box**.
2. Under **Principals**, edit `CLM_Box_Principal` and set the two authentication
   parameters:
   - **Username** — the Box **Client ID**
   - **Password** — the Box **Client Secret**
3. Save. Salesforce stores both encrypted; they cannot be retrieved back into source, and
   Apex only ever holds `{!$Credential.Username}` and `{!$Credential.Password}` placeholders.

## Part 3 — Non-secret settings

Two values go on the `CLM_Box_Config__c` org-default record:

- **Enterprise Id** — the Box enterprise ID from Part 1. The endpoint returns
  `box_not_configured` until this is set.
- **Allowed Folder Ids** — a comma-separated list of Box folder IDs the endpoint may mint
  tokens for. Leave blank to allow **any** folder; populate it to restrict the endpoint to
  the demo workspace.

Apply them with the script, which validates both values, upserts the org default, and
prints a masked summary. Rerunning it updates the same record rather than adding one:

```bash
BOX_ENTERPRISE_ID=<id> BOX_ALLOWED_FOLDER_IDS=<id,id> \
  clm-salesforce-project/scripts/configure-clm-box-settings.sh <alias>
```

The values are substituted into a temporary copy at run time, so no live identifier is
written into the working tree. Retrieve them with `box users:get --fields=enterprise` and
`box folders:items 0 --fields=id,name,type`.

The equivalent by hand is **Setup → Custom Settings → CLM Box Config → Manage → New** (the
org default record), setting the same two fields.

Then assign the `CLM_Demo_Operator` permission set to anyone who will open the workspace. It
grants both the Apex class and access to the credential principal.
`python3 scripts/demo_operator.py salesforce-deploy` assigns it automatically.

## Part 4 — Point the workspace at a real folder

The app's default workspace folder is the placeholder string `demo-workspace`, which is not
numeric. The endpoint rejects it with `invalid_folder_id` before any Box call, so choose one:

- Open the page with an explicit folder: `/clm?folderId=<box-folder-id>`, or
- Rebuild the UI bundle with the folder baked in:

  ```bash
  VITE_BOX_FOLDER_ID=<box-folder-id> npm run build
  ```

  then redeploy the bundle.

## Part 5 — Verify

Check the endpoint before opening the page. From `clm-salesforce-project`:

```bash
sf api request rest "/services/apexrest/clm/box-token?folderId=<box-folder-id>" --target-org <alias>
```

A working setup returns `accessToken`, `expiresIn`, `folderId`, and `scope`. Anything else
is diagnosable from the table below.

Then open the workspace and confirm the redlined contract renders in place of the file list.

## Troubleshooting

| Response | Meaning | Fix |
|---|---|---|
| `missing_folder_id` (400) | No `folderId` parameter | Call with `?folderId=<box-folder-id>` |
| `invalid_folder_id` (400) | `folderId` is not numeric | Usually the `demo-workspace` default; see Part 4 |
| `box_not_configured` (503) | `Enterprise_Id__c` is blank | Complete Part 3 |
| `folder_not_allowed` (403) | Folder is not in `Allowed_Folder_Ids__c` | Add the folder ID, or clear the field to allow any |
| `box_auth_failed` (502) | Box rejected the client credentials | Check Part 2 values; confirm the app is authorized in the Admin Console (Part 1 step 5) |
| `box_downscope_failed` (502) | Box refused the token exchange | Confirm App + Enterprise Access and that the service identity can see the folder |
| `box_request_failed` (502) | The callout itself failed | Check the named credential is enabled and the permission set grants principal access |
| 200, but the file list still shows | Preview script or listing blocked | Check the browser console; confirm the Box app's CORS domains include the site origin |

## Production variant: per-user OAuth

The demo uses a Client Credentials Grant because it needs no per-user step: one-time admin
setup, no consent screen, and any authorized viewer of the site gets a preview.

For production, the committed `CLM_Box` auth provider supports moving to per-user Box OAuth.
Each person authenticates to Box themselves, so access is bounded by what they can already
see and Box's audit log shows the actual person rather than a service identity. The costs
are a callback-URL round trip during setup and a one-time Box consent per user — which is
why it is not the demo default. Tracked as MT-040.

## Notes

- Box Content Preview is served from the UI bundle, not `cdn01.boxcdn.net`. The Experience
  Cloud CSP allows the Box CDN under `style-src`, `connect-src`, and `frame-src`, but
  `script-src` permits only `'self'` and a Salesforce allowlist, and `CspTrustedSite` has no
  field to change that.
- Keep every value from this guide out of committed files. Client IDs, secrets, enterprise
  IDs, and folder IDs belong in the org, and `python3 scripts/validate_clm.py` fails the
  build if they appear in source.

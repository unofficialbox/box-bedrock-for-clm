# Manual Box Configuration and Automation Feasibility

Assessment date: **2026-07-20**. “No public API” means no supported create/update operation was found in the [Box API reference](https://developer.box.com/reference) or the official [Box OpenAPI specification](https://github.com/box/box-openapi). Recheck before each new deployment because the platform is evolving.

## Public API gaps

All browser-agent and private-lab paths require the operator to be signed in to the intended Box web application first. The authenticated tab hostname must match the gitignored runtime environment. Generated executors do not log in, contain credentials, or make a Box Platform OAuth token equivalent to a Box web session. See [Box Private-API Labs](box-private-api-labs.md).

| Box component | CLM use case | Why it matters | Manual configuration needed | What would remove the manual work |
|---|---|---|---|---|
| **Box Forms** | Capture `New Contract Request`, upload the package, and trigger intake | Provides the governed business entry point and consistent fields | Have an authenticated browser agent apply the [Box Form Browser Plan](box-form-provisioner.md); a human approves link access and distribution | A supported Forms CRUD/publish API. None is present in the current public API contract. |
| **Box Apps** | Present intake actions, contract views, charts, clause access, and executed agreements | Gives operators one production-like contract workspace | Have an authenticated browser agent build pages, sections, blocks, views, filters, columns, charts, layout, sizing, themes, and App sharing in the [Apps builder](https://docs.box.com/en/box-apps/using-box-apps/apps/creating-an-app.md). Experimental private-API support now updates only sections for a fixed, exact-title lab app. | A supported Box Apps definition API. A guarded private lab now proves shell creation and section reconciliation, but not block-level provisioning. |
| **Box Automate authoring** | Run Form → Extract → agent review → approval → Salesforce HTTPS handoff | Makes the sequence inspectable, repeatable, and governed | Build the production graph, bind variables and target IDs, configure connector credentials, test, save, publish, and activate in the [Automate builder](https://docs.box.com/en/box-automate/creating-workflows-in-box-automate.md) | A supported workflow-definition CRUD API. Guarded private labs now prove inactive draft creation plus one folder-scoped Manual Start trigger; outcomes, variable binding, connectors, publication, and activation remain manual. |
| **Box Hub page composition** | Make the approved-clause library navigable and visibly maintained | Gives reviewers a governed source for standard and fallback clauses | Design Hub pages/blocks, navigation, visual hierarchy, and final presentation | Public [Hubs APIs](https://developer.box.com/guides/hubs-api/hubs/create-hub) can create Hubs and manage items/collaborations, but the current contract exposes page/block retrieval rather than full page/block authoring. Copying an approved same-enterprise Hub may reduce this work. |
| **Enterprise enablement and delegated builder access** | Enable Forms, Apps, Automate, AI, Hubs, Doc Gen, and appropriate builders | Prevents deployment failures and preserves least privilege | An administrator enables products and assigns environment-specific users/groups | Supported entitlement-management APIs for these product controls, or an approved enterprise configuration-as-code mechanism. |

Final publish, share, activate, signature, and destructive actions remain human-confirmed governance gates even if an API becomes available.

## Manual tasks that can move to supported APIs

| Component | Supported browserless path | Repository opportunity |
|---|---|---|
| **Box Hubs core setup** | `POST /2.0/hubs`, Hub update/copy, item, and collaboration APIs with `box-version: 2025.0` | Automate Hub creation, content population, and collaborators; leave only visual composition and approval manual. |
| **Box AI Studio agents** | `POST/GET/PUT/DELETE /2.0/ai_agents` with `ai.readwrite` | Create or reconcile CLM agent definitions from portable configuration. |
| **Box Doc Gen templates** | `POST /2.0/docgen_templates` with `box-version: 2025.0` | Replace manual template marking with an idempotent API step after upload. |
| **Content, metadata, tasks, Sign, and shared links** | Existing Box Platform APIs | Continue using supported APIs with dry-run/apply separation, external IDs, and explicit confirmation for consequential actions. |

## Private REST and GraphQL feasibility

| Question | Finding | Decision |
|---|---|---|
| Can setup run without Browser Use? | **Yes** for supported API rows above. **No supported browserless path is currently documented** for Form creation, Apps composition, or Automate authoring. | Automate supported surfaces first; retain UI steps for the remaining gaps. |
| Can private Box web APIs be interrogated? | **Technically yes**, through a one-time, read-only network capture and a separately approved disposable draft save in a confirmed test enterprise. Prior internal Apps evidence used REST-like Crooze methods such as `app.get` and `savedSearch.get`; GraphQL primarily hydrated collections rather than App definitions. | Treat endpoint names and payloads as research evidence, never as a stable contract. Do not guess write methods. |
| Can a private API create this Form? | **Technically yes.** A live disposable-Form probe observed private REST create, update, and delete calls. Create and update used multipart payloads containing the Form definition; delete returned `204`. See the [redacted probe evidence](../research/box-forms-private-api/README.md). | Treat this as research evidence, not a supported provisioning interface. The endpoints, schemas, and security requirements may change without notice. |
| Could a standalone script replay the private call? | Only if it reproduces Box's authenticated web session, anti-forgery controls, and current internal schema. The probe did not establish support for a Box Platform OAuth token and intentionally did not export or replay browser credentials. | Do not persist or replay browser credentials. Keep Form creation manual or under controlled UI automation until Box publishes a supported API. |
| What other private authoring paths were observed? | Apps uses private Crooze method calls; Automate uses private GraphQL workflow-item mutations through the authenticated page client; Hub composition returns a versioned binary document through private GraphQL. | See the [cross-surface discovery evidence](../research/box-web-private-api/README.md). Keep each surface in a separate exact-title lab and preserve publish/share/activate gates. |
| Best path to less manual work | Use public APIs immediately; request supported Forms, Apps-definition, and Automate-definition APIs from Box; use UI automation only as a controlled interim option. | Keep private API work as an isolated experiment with no production dependency. |

## Completed investigation controls

The 2026-07-20 probe used a confirmed test enterprise and explicit authorization to create and delete one disposable Form. It captured only endpoint patterns, redacted payload shapes, status codes, and response schemas. It retained no cookies, bearer tokens, CSRF values, user identifiers, tenant-specific IDs, or live Form identifiers. The Form was deleted after capture and was not published or shared through the UI.

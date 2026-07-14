# Demo Component Manifest

Machine-readable source: [`config/demo/box-agentforce-react-demo-manifest.json`](../../../config/demo/box-agentforce-react-demo-manifest.json)

## Runtime scope

| Included | Role |
|---|---|
| Box | Governed contracts, versions, metadata, tasks, DocGen, Sign, and audit history |
| Agentforce | Source-cited retrieval, analysis, explanation, drafting, and routing |
| Salesforce Multi-Framework React UI Bundle | Contract workspace and embedded Box/Agentforce presentation surface |

Explicitly excluded: AWS Bedrock AgentCore, Strands, Databricks, and external custom middleware.

## Experience components

| Component | Status | Primary flow | Path / live surface |
|---|---|---:|---|
| React CLM workspace | Local verified | Yes | Contract, Box content, cited redline findings, and domain-grouped expert queues in `clm-react-app/force-app/main/default/uiBundles/clmreactapp` |
| Agentforce Contract Copilot | Specified, not deployed | Yes | `config/agentforce/clm-react-agentforce-spec.json` |
| Box CLM workspace | Live | Yes | Folder `399081692991` |
| Box CLM app | Live | Yes, supporting dashboard | `https://kadams.ent.box.com/app/KyZohNNwCy6Y6ccmn`; production-style portfolio charts, one intake Form entry point, Hub and executed-agreement actions, and a metadata-rich Clause Library page |
| New Contract Request form | Live | Box Form entry variation | `https://kadams.ent.box.com/f/c83f2ab35ee74a519b5fbc2859e2a858` |
| Approved clause library | Live content | Yes | Folder `399419341582`; eight Markdown clauses plus governance README |
| Box Automate intake workflow | Saved draft, inactive | Yes | Workflow `399436615012`: Form trigger → Extract → Box Agent → human approval → HTTPS connector |
| Salesforce CLM record creation | Object and metadata-managed External Client App deployed; direct REST upsert verified | Yes | `CLM_Contract__c` uses private sharing and unique `Contract_ID__c`; create/update/lookup passed against record `a7IgL000000WYWPUA4`; only the Box consumer-secret handoff and OAuth test remain |
| Acme Contract Clause Library Hub | Live | Yes | Hub `1312630996`: live clause folder, current-standard operating context, intake/App/executed-agreement action cards, and governance content |
| Offline experience gallery | Local verified | Presenter support | `output/html/clm-experience-gallery.html` |

## React components

| Component | Responsibility |
|---|---|
| `Workspace.tsx` | Contract banner, workspace/approval navigation, deal metrics, and Agentforce context |
| `BoxWorkspace.tsx` | Downscoped Box access, live Explorer, and safe local fallback |
| `AgentforcePanel.tsx` | Embedded Contract Copilot or local prompt cards |
| `lib/box.ts` | Salesforce record, contract, and Box folder context; guarded agent prompt; same-origin token request |

## Salesforce Record Creation

| Contract | Value |
|---|---|
| Trigger | Validated New Contract Request |
| Human gate | Box Automate approval task |
| Connector operations | `salesforceContractUpsert`, then `salesforceContractLookup` |
| Object API name | `CLM_Contract__c` |
| Record contract | `config/salesforce/clm-contract-record.json` |
| Standard REST paths | `/services/data/{apiVersion}/sobjects/CLM_Contract__c/Contract_ID__c/{urlEncodedContractId}` |
| Idempotency key | `contractId` |
| Required response | `recordId`, `contractId`, `boxFolderId` |
| React launch context | `recordId=<returned-salesforce-id>&contractId=<contract-id>&folderId=<box-folder-id>` |

The Salesforce record stores structured deal context and the Box workspace reference. Contract documents remain in Box.

The [Box Form entry-point variation](04-box-form-automate-entry.md) replaces the pre-created-record opening with the complete Form → Automate → human validation → standard REST upsert and lookup sequence. After Salesforce returns the record, every walkthrough continues in the same React workspace.

## Box folders in the flow

| Folder | ID |
|---|---|
| Drafts and Redlines | `399080778184` |
| Approvals | `399082072259` |
| Signature | `399081939679` |
| Executed Agreement | `399080706253` |
| Obligations | `399081567921` |
| DocGen Templates | `399363530207` |
| Clause Library | `399419341582` |

## Box capability status

| Capability | Status | Components |
|---|---|---|
| Metadata | Four live, one specified | `clmContract`, `clmDocument`, `clmObligation`, `clmClause`; `clmRedlineReview` is specified but not live |
| Tasks | Live | Legal, Finance, Privacy and Security reviews |
| DocGen | Live | Approval memo, order summary, renewal notice |
| Automate | Saved draft, inactive; update required | Enhanced Extract Agent, Box Agent, approval branch, Salesforce standard REST upsert and lookup |
| Hubs | Live | Approved Markdown clause publication and governance guidance |
| Sign | Packet not created | Execution packet begins after completed approvals |

## Contract evidence

| Artifact | Box file ID | Demo role |
|---|---|---|
| MSA redline | `2342633195167` | Unlimited liability, renewal, and termination deviations |
| DPA | `2342633156726` | PHI, privacy, and security approval triggers |
| SOW | `2342622013520` | SLA and delivery obligations |
| Order form | `2342633259967` | Net 90 versus expected Net 45 mismatch |
| Security exhibit | `2342636075017` | Security evidence requirements |
| Insurance certificate | `2342619758153` | Renewal obligation |
| Clause playbook | `2342635779827` | Approved positions and fallback language |

## Human approval tasks

| Review | Task ID | Source file | Status |
|---|---|---|---|
| Legal | `42899891150` | MSA redline | Incomplete |
| Finance | `42899881417` | Order form | Incomplete |
| Privacy and Security | `42899893550` | DPA | Incomplete |

All three tasks are human-owned. The demo includes no automated approval action.

The existing live tasks remain assigned to `kadams@boxdemo.com` as demo triage. Named expert personas and production collaborator logins are governed by `config/clm/expert-routing.json`; task creation must fail to triage when a domain expert is unconfigured or lacks file access.

## Redline routing components

| Component | Role |
|---|---|
| `config/clm/redline-finding.schema.json` | Validates cited differences, domain, risk, confidence, routing, and review status |
| `config/clm/expert-routing.json` | Maps domains to maintained expert identities and the Legal Operations fallback |
| `CLM Redline Difference Router` | Compares redline, baseline, and approved clauses without inventing users or approvals |
| `routeRedlineFindings` | Idempotently groups findings and creates or reuses one Box task per domain |
| React **Redline reviews** | Shows before/after language, fallback clause, risk, confidence, expert, and live task |

## Box DocGen templates

| Template | File ID | Used in flow |
|---|---|---|
| Approval memo | `2344242775119` | Yes, after confirmation |
| Order summary | `2344233767713` | Available, not in the primary flow |
| Renewal notice | `2344244747613` | Yes, after confirmation |

## Agentforce action boundary

Read-only actions:

- Resolve contract context and list Box files.
- Summarize the package with source citations.
- Compare the MSA redline to the clause playbook.
- Read Box review tasks and explain signature blockers.
- Extract candidate obligations.

Confirmation-required actions:

- Draft a Box DocGen approval memo.
- Draft a Box DocGen renewal notice.

Not included:

- Approving a contract.
- Completing a Box review task for a human.
- Sending for signature before required approvals are complete.

## Demo artifacts

| Artifact | Path |
|---|---|
| Setup and activation guide | `docs/runbooks/05-demo-setup-and-activation.md` |
| Manual-task register | `docs/manual-task-register.md` |
| Executive script | `docs/demo-scripts/box-agentforce-react/01-executive-walkthrough.md` |
| Legal Operations script | `docs/demo-scripts/box-agentforce-react/02-legal-operations-walkthrough.md` |
| Technical validation script | `docs/demo-scripts/box-agentforce-react/03-technical-validation.md` |
| Demo-flow source | `docs/diagrams/clm-box-agentforce-react-demo-flow.mmd` |
| Rendered demo flow | `docs/diagrams/clm-box-agentforce-react-demo-flow.svg` |
| Self-contained experience gallery | `output/html/clm-experience-gallery.html` |

## Remaining live activation components

- Deployed `clmreactapp` UI Bundle.
- Agentforce agent and application IDs.
- Same-origin Salesforce endpoint returning a short-lived, downscoped Box token.
- Box CORS allowlist for the deployed Salesforce/Experience domain.
- Registered Agentforce actions from the action contract.
- Deployed Salesforce CLM object plus configured standard REST origin, API version, OAuth 2.0 connection, and field mapping.
- Idempotent record-creation test returning `recordId`, `contractId`, and `boxFolderId`.

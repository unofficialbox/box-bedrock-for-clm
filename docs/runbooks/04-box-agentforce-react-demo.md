# Box + Agentforce + React CLM Demo

## Purpose

This is the primary CLM demo. It uses only Box, Agentforce, and the Salesforce-hosted Multi-Framework React app. It does not call AWS Bedrock AgentCore, Strands, Databricks, or external custom middleware.

Before running this script, complete [CLM Demo Setup and Activation](05-demo-setup-and-activation.md) and review the [manual-task register](../manual-task-register.md). Do not claim the integrated path is live unless the Level C smoke test passes.

Source diagram: [Box + Agentforce + React architecture](../diagrams/clm-box-agentforce-react.mmd)

Presentation package:

- [Executive walkthrough](../demo-scripts/box-agentforce-react/01-executive-walkthrough.md)
- [Legal Operations walkthrough](../demo-scripts/box-agentforce-react/02-legal-operations-walkthrough.md)
- [Technical validation](../demo-scripts/box-agentforce-react/03-technical-validation.md)
- [Box Form entry-point variation](../demo-scripts/box-agentforce-react/04-box-form-automate-entry.md)
- [Rendered demo flow](../diagrams/clm-box-agentforce-react-demo-flow.svg)
- [Rendered Box Form entry flow](../diagrams/clm-box-form-automate-entry.svg)
- [Component manifest](../demo-scripts/box-agentforce-react/component-manifest.md)
- [Machine-readable manifest](../../config/demo/box-agentforce-react-demo-manifest.json)

## Experience boundary

| Layer | Responsibility |
|---|---|
| React UI Bundle | Contract workspace, record context, cited redline findings, domain-expert routing, Box and Agentforce surfaces |
| Box | Contract files, versions, metadata, review tasks, DocGen templates, Sign, audit trail |
| Agentforce | Source-cited Q&A, structured clause/playbook comparison, domain routing explanation, readiness, and draft generation orchestration |
| Human reviewers | Legal positions, commercial concessions, task completion, signature authorization |
| Salesforce record | `CLM_Contract__c` structured context created from validated Box intake; live record ID is a runtime value |

## Live anchors

| Asset | Value |
|---|---|
| Box workspace | [CLM-2026-Northstar](https://kadams.ent.box.com/folder/399081692991) |
| Box CLM app | [Contract Lifecycle Management](https://kadams.ent.box.com/app/KyZohNNwCy6Y6ccmn) |
| New Contract Request form | [Published form](https://kadams.ent.box.com/f/c83f2ab35ee74a519b5fbc2859e2a858) |
| MSA redline | File `2342633195167` |
| Legal / Finance / Privacy tasks | `42899891150` / `42899881417` / `42899893550` |
| Approval memo DocGen template | File `2344242775119` |
| Renewal notice DocGen template | File `2344244747613` |
| Approved clause library | Folder `399419341582`; metadata template `9ca0de81-5f96-4158-82f7-1251b28a9c6e` |
| Offline experience gallery | `output/html/clm-experience-gallery.html` |
| Salesforce CLM record | `CLM_Contract__c` and metadata-managed External Client App are deployed to `agentforce`; direct REST create/update/lookup passed with record `a7IgL000000WYWPUA4`; only the Box consumer-secret handoff and OAuth test remain |

## Presenter flow

Choose one entry point before the session:

- **Existing-record entry:** open React with a prepared Salesforce record for a shorter, repeatable walkthrough.
- **Box Form entry variation:** run [Box Form to Salesforce Record](../demo-scripts/box-agentforce-react/04-box-form-automate-entry.md), then continue in the React workspace. This variation requires the deployed object, configured Salesforce OAuth 2.0 REST connection, and an explicitly activated Automate workflow.

| Act | Show | Agentforce moment | Control |
|---|---|---|---|
| 0. Intake | Submit the published Box Form, then show Automate through Extract, Box Agent, and human validation. | Explain the candidate enrichment prepared for the structured record. | The HTTPS connector remains downstream of human approval. |
| 1. Create Salesforce record | Run the approved HTTPS branch and show the newly created Salesforce CLM record plus returned record ID. | Resolve the new record with its Box workspace context. | Record creation is idempotent and uses only validated, allowlisted fields. |
| 2. Open contract | Launch the React workspace with `recordId`, `contractId=CLM-2026-0017`, and `folderId=399081692991`. | Ask for a package summary with Box file citations. | Salesforce holds structured context; Box remains authoritative for content. |
| 3. Inspect and route redlines | Open the MSA redline and approved-clause Hub/View, then switch to **Redline reviews**. | Compare the redline to the governed Markdown clauses; return cited findings, domain, risk, confidence, and fallback. | Expert selection comes only from the configured directory; uncertain findings go to Legal Operations triage. |
| 4. Explain blockers | Show the Commercial Legal, Finance, and Privacy queues with their named experts. | Ask why signature is blocked and who owns each decision. | Findings are consolidated into one human-owned Box task per domain. |
| 5. Prepare packet | Return to the workspace. | Draft an approval memo with Box DocGen after presenter confirmation. | File creation requires confirmation; approval does not occur automatically. |
| 6. Execute | Show the signature folder. | Explain that Box Sign remains unavailable until reviewers complete tasks. | No agent can bypass approval sequencing. |
| 7. Operationalize | Show the obligations folder and renewal template. | Extract candidate obligations with citations and draft a renewal notice after confirmation. | A human validates owners, dates, and notices. |

## Local rehearsal

```bash
cd clm-react-app/force-app/main/default/uiBundles/clmreactapp
npm install
npm test -- --run
npm run build
npm run test:e2e
```

Local mode intentionally shows a safe fallback file list and Agentforce prompt cards when runtime credentials/IDs are absent.

## Redline routing activation

1. Confirm the redline file, approved baseline item, and approved clause library.
2. Configure real collaborator logins in `config/clm/expert-routing.json`.
3. Deploy the `routeRedlineFindings` Agentforce/Apex action defined in `config/box/https-connectors.json`.
4. Validate `config/clm/redline-finding.schema.json` responses and the `0.85` triage threshold.
5. Confirm idempotency: one open Box task per contract, redline file, and domain.
6. Keep the Automate workflow inactive until a presenter approves activation.

## Salesforce activation checklist

- Deploy the `clmreactapp` UI Bundle.
- Review and deploy `CLM_Contract__c` and the `CLM_Demo_Operator` permission set.
- Configure the standard Salesforce REST external-ID upsert and lookup operations for validated, allowlisted Box intake values.
- Use `Contract_ID__c` for standard REST idempotency, then map the external-ID lookup response to `recordId`, `contractId`, and `boxFolderId`.
- Configure the Agentforce agent/application IDs at runtime or with `VITE_AGENTFORCE_*` build variables.
- Implement the same-origin downscoped token endpoint documented in `clm-react-app/README.md`.
- Register the actions and guardrails from `config/agentforce/clm-react-agentforce-spec.json`.
- Verify Box application CORS for the deployed Salesforce/Experience domain.
- Rehearse with `recordId=<returned-salesforce-id>&contractId=CLM-2026-0017&folderId=399081692991`.

## Pass criteria

- The React app displays Northstar deal context and the live Box workspace.
- A validated intake creates exactly one Salesforce CLM record and returns its record ID.
- The React app and Agentforce receive the returned Salesforce record ID with the Box workspace context.
- Agentforce receives explicit contract and Box folder context.
- Answers cite Box files for material contract claims.
- Approval state matches the three live Box tasks.
- No action allows Agentforce to approve a clause or send for signature.
- DocGen mutations require presenter confirmation.
- No network path to AWS, Strands, or Databricks is present in this variation.
- The experience gallery loads offline with 12 current, embedded screenshots from real demo surfaces, no browser tabs, and no external references.

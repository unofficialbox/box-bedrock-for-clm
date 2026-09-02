# Supporting Box + Agentforce + React Scripts

These scripts present the React portion of Box + Salesforce Contract Lifecycle at three depths. For the full scenario, use the parent [Box + Salesforce Contract Lifecycle guide](../README.md#4-presenter-script) for the complete scenario.

| Script | Duration | Audience | Primary outcome |
|---|---:|---|---|
| [Executive walkthrough](01-executive-walkthrough.md) | 5-6 minutes | Executives, business sponsors, first meetings | Read customer paper against the governed clause library, and show the counterparty boundary |
| [Technical validation](03-technical-validation.md) | 15-20 minutes | Architects, Salesforce teams, security, developers | Prove credential, CSP, sharing, and MCP boundaries -- and name the one that is not enforceable |
| [Box metadata entry-point variation](04-box-metadata-automate-entry.md) | 5-7 minutes | Any audience | Start with a contract uploaded to `01 - Intake` and `clmContract` metadata applied, then Automate enrichment, human validation, and HTTPS Connector record creation |

Supporting artifacts:

- [Calder demo storyboard](../../../../../DEMO-STORYBOARD.html) -- the executive walkthrough as a single presenter page: preflight checks, every prompt as copy-paste, and what each beat should return. Open it in a browser. Site URL and counterparty login are placeholders; bind them to your environment first.
- [Demo flow diagram](../../../../diagrams/clm-box-agentforce-react-demo-flow.svg)
- [Box metadata entry-point diagram](../../../../diagrams/clm-box-metadata-automate-entry.svg)
- [Machine-readable scenario manifest](../../../../../config/demo/box-salesforce-clm-demo-manifest.bcl)
- [Agentforce action contract](../../../../../config/agentforce/clm-react-agentforce-spec.bcl)

## Experience boundary

| Layer | Responsibility |
|---|---|
| React UI Bundle | The counterparty's surface: their contracts, governed Box content, and the Copilot |
| Box | Files, versions, metadata, the approved clause library Hub, and audit history |
| Salesforce | `CLM_Contract__c` structured context and approval state |
| Agentforce | Cited retrieval, comparison, explanation, draft preparation, and confirmed actions |
| Human reviewers | Legal positions, commercial concessions, task completion, generation, and signature authorization |

## Activation and pass criteria

1. Deploy the UI Bundle, `CLM_Contract__c`, and least-privilege permission set.
2. Configure standard REST external-ID upsert and lookup for validated intake fields.
3. Provide Agentforce IDs and downscoped Box-token behavior only through the documented runtime boundary.
4. Confirm the application resolves `recordId`, `contractId`, and `folderId` without browser secrets.
5. Confirm material answers cite Box files and approval state matches human-owned tasks.
6. Confirm one open task is reused per contract, redline file, and review domain.
7. Doc Gen generates into the contract's own folder; Box Sign only ever *prepares* a request and refuses an unapproved contract. Never describe a signature request as sent.
8. Keep unverified platform claims outside these supporting scripts; the parent scenario owns that evidence.

## Shared presenter rule

Never describe Agentforce as approving a contract. It may retrieve, summarize, compare, explain, draft, and route. Named humans complete approval tasks and authorize signature.

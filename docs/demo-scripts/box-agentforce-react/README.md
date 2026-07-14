# Box + Agentforce + React CLM Demo Scripts

These scripts present the same Northstar CLM scenario at three depths. All three use only Box, Agentforce, and the Salesforce Multi-Framework React app. The optional Form-led entry module can replace the opening of any walkthrough.

| Script | Duration | Audience | Primary outcome |
|---|---:|---|---|
| [Executive walkthrough](01-executive-walkthrough.md) | 10-12 minutes | Executives, business sponsors, first meetings | Show the value and human-control model quickly |
| [Legal operations walkthrough](02-legal-operations-walkthrough.md) | 20-25 minutes | Legal Ops, Sales Ops, Finance, Privacy, Security | Demonstrate the complete contract-review and approval workflow |
| [Technical validation](03-technical-validation.md) | 20-30 minutes | Architects, Salesforce teams, security, developers | Prove runtime boundaries, token handling, actions, and guardrails |
| [Box Form entry-point variation](04-box-form-automate-entry.md) | 5-7 minutes | Any audience | Start with Form submission, Automate enrichment, human validation, and HTTPS Connector record creation |

Supporting artifacts:

- [Demo flow diagram](../../diagrams/clm-box-agentforce-react-demo-flow.svg)
- [Box Form entry-point diagram](../../diagrams/clm-box-form-automate-entry.svg)
- [Human-readable component manifest](component-manifest.md)
- [Machine-readable component manifest](../../../config/demo/box-agentforce-react-demo-manifest.json)
- [Agentforce action contract](../../../config/agentforce/clm-react-agentforce-spec.json)

## Shared presenter rule

Never describe Agentforce as approving a contract. It may retrieve, summarize, compare, explain, draft, and route. Named humans complete approval tasks and authorize signature.

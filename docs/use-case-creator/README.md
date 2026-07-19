# CLM Use-Case Creator

Use this path to understand or intentionally tailor the existing Contract Lifecycle Management use case. This repository is already a generated vertical; do not run a template generator or replace it with a generic scaffold.

## Review order

1. [Architecture](architecture.md)
2. [Agent Definitions](agent-definitions.md)
3. [Domain References](domain-references.md)
4. [Control Matrix](control-matrix.md)
5. [ROI Analysis](roi-analysis.md)
6. [Competitive Landscape](competitive-landscape.md)
7. [Salesforce Experience Selection](salesforce-profile-selection.md)
8. [Salesforce Record Contract](salesforce-record-contract.md)
9. [Lifecycle Marketecture](marketecture.md)

## Definition of the use case

| Dimension | CLM decision |
|---|---|
| Business process | Commercial contract intake, review, approval, execution, and lifecycle management |
| Primary user | Legal Operations and accountable contract reviewers |
| Business object | Salesforce `CLM_Contract__c` |
| Governed content package | MSA, DPA, SOW, order form, security exhibit, insurance certificate, redlines, approved clauses, evidence, and executed agreement |
| Content authority | Box |
| Structured authority | Salesforce |
| Human authority | Legal, Finance, Privacy, Security, and designated business owners |
| Entry points | Box Form or prepared Salesforce record, depending on the scenario |
| Failure path | Triage missing evidence, low confidence, unresolved owners, partial writes, and blocked approvals before retry |
| Reset path | Remove or archive only resources owned by the confirmed demo run and retain reset evidence |

Every material claim must use the readiness vocabulary in `README.md`. Keep credentials, tenant IDs, org IDs, live record IDs, and machine-specific paths out of committed files.

After changing domain behavior, hand the result to the [operator](../operator/README.md) for environment binding and live validation.
